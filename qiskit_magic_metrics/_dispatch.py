"""Dispatch logic for choosing between the stabilizer fast path and the general statevector path.

See docs/ARCHITECTURE.md, "Stabilizer detection and the fast path".
"""

from __future__ import annotations

from qiskit import QuantumCircuit


def is_clifford_circuit(circuit: QuantumCircuit) -> bool:
    """Return True if `circuit` consists entirely of Clifford gates.

    Implementation plan: attempt `Clifford.from_circuit(circuit)` and return False if it raises
    (Qiskit raises on encountering a non-Clifford gate). Not yet implemented.
    """
    raise NotImplementedError("see ROADMAP.md v0.1")
