"""Qiskit Magic Metrics: exact, stabilizer-accelerated resource and entanglement metrics.

See README.md for scope and docs/PRIOR_ART.md for how this relates to Qurrium and qLEET.

Public API:
    ResourceMetric        — base class; subclass to add a new metric.
    StabilizerRenyiEntropy — magic (nonstabilizerness) measure; alpha-parameterized.
    MeyerWallachMeasure    — global multipartite entanglement measure.
    EntanglementEntropy    — von Neumann entropy across a user-specified bipartition.

Each of the three concrete metrics is both a plain callable (`.compute(circuit)`) and a Qiskit
`AnalysisPass`, so it composes into a `PassManager` pipeline. See each class's docstring for a
usage example.
"""

__version__ = "0.1.0.dev0"

from qiskit_magic_metrics.base import ResourceMetric
from qiskit_magic_metrics.passes.entanglement_entropy import EntanglementEntropy
from qiskit_magic_metrics.passes.meyer_wallach import MeyerWallachMeasure
from qiskit_magic_metrics.passes.stabilizer_renyi_entropy import StabilizerRenyiEntropy

__all__ = [
    "EntanglementEntropy",
    "MeyerWallachMeasure",
    "ResourceMetric",
    "StabilizerRenyiEntropy",
    "__version__",
]
