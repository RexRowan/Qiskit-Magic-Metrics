"""Meyer-Wallach global multipartite entanglement measure.

Reference: D. A. Meyer and N. R. Wallach, "Global entanglement in multiparticle systems",
J. Math. Phys. 43, 4273 (2002). Closed-form reduction to average single-qubit purity per
G. K. Brennen, "An observable measure of entanglement for pure states of multi-qubit systems"
(2003):

    Q(psi) = 2 * (1 - (1/n) * sum_k tr(rho_k^2))

where rho_k is the reduced density matrix of qubit k. Q ranges from 0 (product states) to 1
(e.g. GHZ states).
"""

from __future__ import annotations

import numpy as np
from qiskit.quantum_info import Clifford, Statevector, partial_trace
from qiskit.transpiler.basepasses import AnalysisPass

from qiskit_magic_metrics._gf2 import gf2_nullspace
from qiskit_magic_metrics.base import ResourceMetric


class MeyerWallachMeasure(ResourceMetric, AnalysisPass):
    """Compute the Meyer-Wallach measure Q(psi) of a pure state, with a stabilizer fast path.

    Q(psi) ranges from 0 (product states) to 1 (e.g. GHZ states). Undefined below n=2 qubits by
    convention; `compute()` returns 0.0 for a single-qubit state rather than raising.

    Usage:
        mw = MeyerWallachMeasure()
        mw.compute(circuit)  # standalone

        pm = PassManager([MeyerWallachMeasure()])
        pm.run(circuit)
        pm.property_set["meyer_wallach_measure"]
    """

    property_set_key = "meyer_wallach_measure"

    def __init__(self):
        """MeyerWallachMeasure takes no configuration — it is well-defined for any pure state."""
        AnalysisPass.__init__(self)

    def _compute_statevector(self, statevector: Statevector) -> float:
        """General path: average single-qubit reduced-density-matrix purity, per qubit."""
        n = statevector.num_qubits
        if n < 2:
            return 0.0
        purities = []
        for k in range(n):
            other_qubits = [q for q in range(n) if q != k]
            rho_k = partial_trace(statevector, other_qubits)
            purities.append(np.real(np.trace(rho_k.data @ rho_k.data)))
        return float(2 * (1 - sum(purities) / n))

    def _compute_stabilizer(self, clifford: Clifford) -> float:
        """Exact fast path: for a stabilizer state, tr(rho_k^2) is either 1 (qubit k unentangled
        with the rest) or 1/2 (qubit k maximally mixed) — no intermediate purity is possible.

        Qubit k has a pure single-qubit marginal iff some combination of stabilizer generators
        is supported entirely on qubit k (i.e. acts as the identity on every other qubit). Any
        nontrivial combination of independent stabilizer generators is a non-identity Pauli
        string (the stabilizer group never contains -I, and the identity only arises from the
        empty combination), so finding such a combination is equivalent to finding a nonzero
        vector in the null space of the generator matrix restricted to the "other qubits"
        columns — computed here over GF(2) via `gf2_nullspace`.

        Args:
            clifford: the Clifford object for a stabilizer circuit.

        Returns:
            Q(psi), computed in O(n^4) via `n` GF(2) null-space computations rather than
            O(2^n) statevector construction.
        """
        n = clifford.num_qubits
        if n < 2:
            return 0.0

        # Symplectic (X|Z) representation of the n stabilizer generators: shape (n, 2n).
        stab_table = np.concatenate(
            [clifford.stab_x.astype(np.uint8), clifford.stab_z.astype(np.uint8)], axis=1
        )

        purities = []
        for k in range(n):
            other_cols = [q for q in range(n) if q != k] + [n + q for q in range(n) if q != k]
            restricted = stab_table[:, other_cols]
            nullspace = gf2_nullspace(restricted)
            purities.append(1.0 if nullspace.shape[0] > 0 else 0.5)

        return float(2 * (1 - sum(purities) / n))

    def run(self, dag):
        """`AnalysisPass` entry point: compute Q(psi) for `dag` and store it under
        `property_set["meyer_wallach_measure"]`. Called by `PassManager.run`, not directly.
        """
        from qiskit.converters import dag_to_circuit

        circuit = dag_to_circuit(dag)
        self.property_set[self.property_set_key] = self.compute(circuit)
