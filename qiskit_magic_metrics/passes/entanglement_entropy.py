"""Von Neumann entanglement entropy across an arbitrary user-specified bipartition.

Generalizes `qiskit.quantum_info.mutual_information`, which only handles a fixed bipartite
(2-party, whole-system) split. Here the caller specifies which qubits belong to subsystem A;
subsystem B is everything else.

Stabilizer fast path reference: B. Fattal, T. J. Cubitt, Y. Yamamoto, S. Bravyi, I. L. Chuang,
"Entanglement in the stabilizer formalism" (arXiv:quant-ph/0406168). For a stabilizer state with
generator matrix M (n x 2n binary, X|Z symplectic representation), let M_B be the submatrix
restricted to the 2|B| columns corresponding to subsystem B's qubits. The entanglement entropy
of subsystem A, in bits (log2), is:

    S(A) = rank_GF2(M_B) - |B|
"""

from __future__ import annotations

import numpy as np
from qiskit.quantum_info import Clifford, Statevector, entropy, partial_trace
from qiskit.transpiler.basepasses import AnalysisPass

from qiskit_magic_metrics._gf2 import gf2_rank
from qiskit_magic_metrics.base import ResourceMetric


class EntanglementEntropy(ResourceMetric, AnalysisPass):
    """Compute the von Neumann entanglement entropy S(A) for a chosen subsystem A.

    Args:
        partition: qubit indices (referring to the circuit's own qubit indices, not physical or
            transpiled indices) making up subsystem A. Subsystem B is every other qubit in the
            circuit/state. Must be a non-empty, proper subset of the qubits — for an n-qubit
            circuit, `len(partition)` must be between 1 and n-1 inclusive.

    Raises:
        ValueError: at construction, if `partition` is empty; at `compute()` time, once the
            qubit count `n` is known, if any index in `partition` is out of range for `n`, or
            if `partition` covers all `n` qubits (leaving subsystem B empty).

    Usage:
        ee = EntanglementEntropy(partition=[0])
        ee.compute(circuit)  # standalone

        pm = PassManager([EntanglementEntropy(partition=[0])])
        pm.run(circuit)
        pm.property_set["entanglement_entropy"]
    """

    property_set_key = "entanglement_entropy"

    def __init__(self, partition: list[int]):
        AnalysisPass.__init__(self)
        if not partition:
            raise ValueError("partition must be non-empty")
        self.partition = list(partition)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(partition={self.partition!r})"

    def _validate(self, n: int) -> list[int]:
        """Check `self.partition` against a circuit/state of `n` qubits and return the
        complementary qubit list (subsystem B). Called by both compute paths since each is
        entered independently depending on the input's Clifford status.
        """
        if any(q < 0 or q >= n for q in self.partition):
            raise ValueError(f"partition {self.partition} out of range for a {n}-qubit state")
        if len(self.partition) >= n:
            raise ValueError("partition must be a proper subset — subsystem B cannot be empty")
        return [q for q in range(n) if q not in self.partition]

    def _compute_statevector(self, statevector: Statevector) -> float:
        """General path: partial-trace out subsystem B and take the von Neumann entropy of the
        remaining reduced density matrix on subsystem A.
        """
        n = statevector.num_qubits
        complement = self._validate(n)
        rho_a = partial_trace(statevector, complement)
        return float(entropy(rho_a, base=2))

    def _compute_stabilizer(self, clifford: Clifford) -> float:
        """Exact fast path via the Fattal et al. rank formula — see module docstring.

        Args:
            clifford: the Clifford object for a stabilizer circuit.

        Returns:
            S(A) in bits, computed via a single GF(2) rank computation rather than
            reduced-density-matrix construction.
        """
        n = clifford.num_qubits
        complement_b = self._validate(n)

        stab_table = np.concatenate(
            [clifford.stab_x.astype(np.uint8), clifford.stab_z.astype(np.uint8)], axis=1
        )
        b_cols = complement_b + [n + q for q in complement_b]
        m_b = stab_table[:, b_cols]
        rank_b = gf2_rank(m_b)
        return float(rank_b - len(complement_b))

    def run(self, dag):
        """`AnalysisPass` entry point: compute S(A) for `dag` and store it under
        `property_set["entanglement_entropy"]`. Called by `PassManager.run`, not directly.
        """
        from qiskit.converters import dag_to_circuit

        circuit = dag_to_circuit(dag)
        self.property_set[self.property_set_key] = self.compute(circuit)
