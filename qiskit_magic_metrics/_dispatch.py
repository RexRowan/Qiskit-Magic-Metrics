"""Dispatch logic for choosing between the stabilizer fast path and the general statevector path.

See docs/ARCHITECTURE.md, "Stabilizer detection and the fast path".
"""

from __future__ import annotations

from qiskit import QuantumCircuit
from qiskit.exceptions import QiskitError
from qiskit.quantum_info import Clifford, Statevector


def is_clifford_circuit(circuit: QuantumCircuit) -> bool:
    """Return True if `circuit` consists entirely of Clifford gates.

    Qiskit's `Clifford.from_circuit` raises `QiskitError` on encountering a non-Clifford
    instruction, which we use as the detection mechanism rather than maintaining our own gate
    allowlist (avoids drifting out of sync with Qiskit's own definition of "Clifford").

    Args:
        circuit: the circuit to classify.

    Returns:
        True if every instruction in `circuit` is Clifford, False otherwise.
    """
    try:
        Clifford.from_circuit(circuit)
    except QiskitError:
        return False
    return True


def to_clifford_or_statevector(circuit_or_state):
    """Normalize an input to a `(kind, obj)` pair.

    `kind` is `"clifford"` or `"statevector"`. Accepts a `QuantumCircuit`, an existing
    `Clifford`, or an existing `Statevector` — circuits are classified via `is_clifford_circuit`
    and converted to whichever representation is cheaper to work with.

    Args:
        circuit_or_state: a `QuantumCircuit`, `Clifford`, or `Statevector`.

    Returns:
        A `(kind, obj)` tuple, where `obj` is a `Clifford` when `kind == "clifford"` and a
        `Statevector` when `kind == "statevector"`.

    Raises:
        TypeError: if `circuit_or_state` is none of the three accepted types.
    """
    if isinstance(circuit_or_state, Clifford):
        return "clifford", circuit_or_state
    if isinstance(circuit_or_state, Statevector):
        return "statevector", circuit_or_state
    if isinstance(circuit_or_state, QuantumCircuit):
        if is_clifford_circuit(circuit_or_state):
            return "clifford", Clifford.from_circuit(circuit_or_state)
        return "statevector", Statevector.from_instruction(circuit_or_state)
    raise TypeError(
        f"expected a QuantumCircuit, Clifford, or Statevector, got {type(circuit_or_state)!r}"
    )
