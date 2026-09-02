"""Stabilizer Renyi entropy — a magic (nonstabilizerness) monotone.

Reference: L. Leone, S. F. E. Oliviero, A. Hamma, "Stabilizer Rényi Entropy",
Phys. Rev. Lett. 128, 050402 (2022).

Define, for an n-qubit pure state |psi> with d = 2^n, the probability distribution over the
4^n n-qubit Pauli strings P:

    Xi(P) = <psi|P|psi>^2 / d

(this is a valid probability distribution because sum_P <psi|P|psi>^2 = d for any pure state —
a standard identity of the Pauli basis expansion of a density matrix). The stabilizer Renyi
entropy of order alpha (alpha != 1) is:

    M_alpha(psi) = 1/(1-alpha) * log2( sum_P Xi(P)^alpha ) - log2(d)

M_alpha = 0 for every stabilizer state (Xi is uniform over exactly d Pauli strings, each with
value 1/d, and zero elsewhere — the sum collapses to d^(1-alpha), making M_alpha vanish
identically), which is exactly the stabilizer fast path implemented here: no enumeration
needed, the answer is always 0.0 for a genuine Clifford circuit.
"""

from __future__ import annotations

from itertools import product

import numpy as np
from qiskit.quantum_info import Clifford, Pauli, Statevector
from qiskit.transpiler.basepasses import AnalysisPass

from qiskit_magic_metrics.base import ResourceMetric


class StabilizerRenyiEntropy(ResourceMetric, AnalysisPass):
    """Compute the stabilizer Renyi entropy M_alpha(psi) of a pure state.

    The statevector path is exact but enumerates all 4^n Pauli strings, so it is intended for
    small-to-medium circuits (ansatz design, magic-state characterization) rather than
    large-scale simulation. Clifford circuits take the O(1) fast path instead: the answer is
    exactly zero by construction, regardless of qubit count.

    Args:
        alpha: Renyi order. Must be strictly positive and not equal to 1 (Xi(P)^alpha is
            undefined/divergent for alpha <= 0 whenever some Pauli has zero expectation value,
            which is the common case; the alpha -> 1 limit is a different, more expensive
            quantity not implemented here).

    Raises:
        ValueError: if `alpha <= 0` or `alpha == 1`.

    Usage:
        magic = StabilizerRenyiEntropy(alpha=2)
        magic.compute(circuit)  # standalone

        pm = PassManager([StabilizerRenyiEntropy(alpha=2)])
        pm.run(circuit)
        pm.property_set["stabilizer_renyi_entropy"]
    """

    property_set_key = "stabilizer_renyi_entropy"

    def __init__(self, alpha: float = 2):
        if alpha <= 0 or alpha == 1:
            raise ValueError(f"alpha must be > 0 and != 1 (the von Neumann limit); got {alpha!r}")
        AnalysisPass.__init__(self)
        self.alpha = alpha

    def __repr__(self) -> str:
        return f"{type(self).__name__}(alpha={self.alpha!r})"

    def _compute_statevector(self, statevector: Statevector) -> float:
        """General path: enumerate all 4^n Pauli strings, compute Xi(P) = <psi|P|psi>^2 / d for
        each, and evaluate M_alpha from the resulting distribution. See module docstring.
        """
        n = statevector.num_qubits
        d = 2**n
        alpha = self.alpha

        xi_values = []
        for labels in product("IXYZ", repeat=n):
            pauli = Pauli("".join(labels))
            exp_val = np.real(statevector.expectation_value(pauli))
            xi_values.append((exp_val**2) / d)

        xi_values = np.array(xi_values)
        sum_xi_alpha = np.sum(xi_values**alpha)
        # sum_xi_alpha should be > 0 for any valid pure state (Xi(I) = 1/d alone guarantees
        # this), so no zero-guard needed before the log.
        m_alpha = (1 / (1 - alpha)) * np.log2(sum_xi_alpha) - np.log2(d)
        return float(m_alpha)

    def _compute_stabilizer(self, clifford: Clifford) -> float:
        """Exact fast path: every stabilizer state has zero stabilizer Renyi entropy by
        definition (see module docstring) — no enumeration required, O(1) regardless of `n`.
        """
        return 0.0

    def run(self, dag):
        """`AnalysisPass` entry point: compute M_alpha(psi) for `dag` and store it under
        `property_set["stabilizer_renyi_entropy"]`. Called by `PassManager.run`, not directly.
        """
        from qiskit.converters import dag_to_circuit

        circuit = dag_to_circuit(dag)
        self.property_set[self.property_set_key] = self.compute(circuit)
