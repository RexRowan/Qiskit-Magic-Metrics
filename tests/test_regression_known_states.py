"""Cross-metric regression checks against known closed-form states, and PassManager
integration -- confirming each metric works both standalone and wired into a pipeline, per
docs/ARCHITECTURE.md.
"""

import math

from qiskit import QuantumCircuit
from qiskit.transpiler import PassManager

from qiskit_magic_metrics import EntanglementEntropy, MeyerWallachMeasure, StabilizerRenyiEntropy


def bell_pair():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    return qc


def test_bell_pair_known_values_across_all_three_metrics():
    qc = bell_pair()

    assert StabilizerRenyiEntropy(alpha=2).compute(qc) == 0.0
    assert math.isclose(MeyerWallachMeasure().compute(qc), 1.0, abs_tol=1e-9)
    assert math.isclose(EntanglementEntropy(partition=[0]).compute(qc), 1.0, abs_tol=1e-9)


def test_product_state_known_values_across_all_three_metrics():
    qc = QuantumCircuit(2)  # |00>, no gates at all

    assert StabilizerRenyiEntropy(alpha=2).compute(qc) == 0.0
    assert MeyerWallachMeasure().compute(qc) == 0.0
    assert EntanglementEntropy(partition=[0]).compute(qc) == 0.0


def test_passmanager_runs_all_three_metrics_together():
    qc = bell_pair()
    pm = PassManager(
        [
            StabilizerRenyiEntropy(alpha=2),
            MeyerWallachMeasure(),
            EntanglementEntropy(partition=[0]),
        ]
    )
    pm.run(qc)

    assert pm.property_set["stabilizer_renyi_entropy"] == 0.0
    assert math.isclose(pm.property_set["meyer_wallach_measure"], 1.0, abs_tol=1e-9)
    assert math.isclose(pm.property_set["entanglement_entropy"], 1.0, abs_tol=1e-9)
