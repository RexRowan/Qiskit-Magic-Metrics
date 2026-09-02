"""Base class for exact resource/entanglement metrics.

See docs/ARCHITECTURE.md for the design rationale.
"""

from __future__ import annotations

from qiskit import QuantumCircuit
from qiskit.quantum_info import Clifford, Statevector

from qiskit_magic_metrics._dispatch import to_clifford_or_statevector


class ResourceMetric:
    """Base class for a metric computable exactly from a circuit or state, with an optional
    stabilizer fast path for Clifford circuits.

    Subclasses must set `property_set_key` and implement `_compute_statevector`. Implementing
    `_compute_stabilizer` is optional — metrics without a known closed form for the stabilizer
    case should omit it (the default implementation raises `NotImplementedError`, which
    `compute()` catches and falls back to the statevector path for that call).
    """

    property_set_key: str = ""
    """`PassManager.property_set` key this metric writes to when run as an `AnalysisPass`."""

    def compute(self, circuit_or_state: QuantumCircuit | Statevector | Clifford) -> float:
        """Compute the metric, dispatching to the stabilizer fast path when possible.

        Args:
            circuit_or_state: the circuit or state to evaluate. A `QuantumCircuit` is classified
                as Clifford or general and converted accordingly; a `Clifford` or `Statevector`
                passed directly is used as-is without re-classification.

        Returns:
            The metric's value for this circuit or state.

        Raises:
            TypeError: if `circuit_or_state` is not a `QuantumCircuit`, `Clifford`, or
                `Statevector`.
        """
        kind, obj = to_clifford_or_statevector(circuit_or_state)
        if kind == "clifford":
            try:
                return self._compute_stabilizer(obj)
            except NotImplementedError:
                # No fast path implemented for this metric — fall back to the general path.
                # Note: this reconstructs a Statevector from the Clifford, which is exponential;
                # a metric that wants to avoid this for large Clifford circuits should implement
                # _compute_stabilizer rather than relying on this fallback.
                obj = Statevector(obj.to_circuit())
        return self._compute_statevector(obj)

    def _compute_stabilizer(self, clifford: Clifford) -> float:
        """Stabilizer fast path. Override in subclasses that have a closed form for the
        Clifford case; the default raises `NotImplementedError`, signaling `compute()` to fall
        back to `_compute_statevector` instead.
        """
        raise NotImplementedError("no stabilizer fast path implemented for this metric")

    def _compute_statevector(self, statevector: Statevector) -> float:
        """General exact path, used for non-Clifford input and as the fallback when no
        stabilizer fast path is implemented. Must be overridden by every concrete subclass.
        """
        raise NotImplementedError(
            f"{type(self).__name__}._compute_statevector is not yet implemented"
        )
