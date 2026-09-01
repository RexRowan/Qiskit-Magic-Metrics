"""Qiskit Magic Metrics: exact, stabilizer-accelerated resource and entanglement metrics.

See README.md for scope and docs/PRIOR_ART.md for how this relates to Qurrium and qLEET.
"""

__version__ = "0.0.0.dev0"

# NOTE: these are not yet implemented — see ROADMAP.md. Imports are declared here ahead of
# implementation so the public API shape is fixed early; each raises NotImplementedError until
# its corresponding pass module is filled in.
from qiskit_magic_metrics.base import ResourceMetric

__all__ = [
    "ResourceMetric",
    "__version__",
]
