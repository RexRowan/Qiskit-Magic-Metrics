"""Placeholder test confirming the package imports and base-class dispatch behaves.

The three real metrics now have their own test files; this file just guards the package's
import surface and the base class's type-checking, so it stays intentionally thin.
"""

import qiskit_magic_metrics


def test_package_imports():
    assert hasattr(qiskit_magic_metrics, "__version__")


def test_base_class_rejects_unrecognized_input():
    from qiskit_magic_metrics import ResourceMetric

    metric = ResourceMetric()
    try:
        metric.compute(None)
        assert False, "expected TypeError for unrecognized input type"
    except TypeError:
        pass
