"""Placeholder test confirming the package imports.

Replace/expand once passes/ has real implementations — see ROADMAP.md v0.1.
"""

import qiskit_magic_metrics


def test_package_imports():
    assert hasattr(qiskit_magic_metrics, "__version__")


def test_base_class_raises_not_implemented():
    from qiskit_magic_metrics import ResourceMetric

    metric = ResourceMetric()
    try:
        metric.compute(None)
        assert False, "expected NotImplementedError from scaffold stub"
    except NotImplementedError:
        pass
