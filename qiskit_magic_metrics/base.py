"""Base class for exact resource/entanglement metrics.

See docs/ARCHITECTURE.md for the design rationale.
"""

from __future__ import annotations

from qiskit import QuantumCircuit
from qiskit.quantum_info import Clifford, Statevector


class ResourceMetric:
    """Base class for a metric computable exactly from a circuit or state, with an optional
    stabilizer fast path for Clifford circuits.

    Subclasses must set `property_set_key` and implement `_compute_statevector`. Implementing
    `_compute_stabilizer` is optional — metrics without a known closed form for the stabilizer
    case should omit it, and `compute()` will fall back to the statevector path for all inputs.
    """

    property_set_key: str = ""

    def compute(self, circuit_or_state: QuantumCircuit | Statevector | Clifford) -> float:
        """Compute the metric, dispatching to the stabilizer fast path when possible.

        Raises:
            NotImplementedError: always, in this scaffold. See ROADMAP.md.
        """
        raise NotImplementedError(
            f"{type(self).__name__}.compute is not yet implemented — see ROADMAP.md"
        )

    def _compute_stabilizer(self, clifford: Clifford) -> float:
        raise NotImplementedError("no stabilizer fast path implemented for this metric")

    def _compute_statevector(self, statevector: Statevector) -> float:
        raise NotImplementedError(
            f"{type(self).__name__}._compute_statevector is not yet implemented"
        )
