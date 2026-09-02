import math

from qiskit import QuantumCircuit

from qiskit_magic_metrics import EntanglementEntropy


def test_product_state_zero_entropy():
    qc = QuantumCircuit(2)
    qc.h(0)  # local only
    ee = EntanglementEntropy(partition=[0])
    assert ee.compute(qc) == 0.0


def test_bell_pair_one_ebit():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    ee = EntanglementEntropy(partition=[0])
    assert math.isclose(ee.compute(qc), 1.0, abs_tol=1e-9)


def test_ghz_any_single_qubit_cut_is_one_ebit():
    qc = QuantumCircuit(4)
    qc.h(0)
    for i in range(3):
        qc.cx(i, i + 1)
    for k in range(4):
        ee = EntanglementEntropy(partition=[k])
        assert math.isclose(ee.compute(qc), 1.0, abs_tol=1e-9)


def test_ghz_two_qubit_cut_is_still_one_ebit():
    # For a GHZ state, any nontrivial bipartition has entanglement entropy exactly 1 ebit --
    # it's a single long-range correlation, not one that grows with the size of either side.
    qc = QuantumCircuit(4)
    qc.h(0)
    for i in range(3):
        qc.cx(i, i + 1)
    ee = EntanglementEntropy(partition=[0, 1])
    assert math.isclose(ee.compute(qc), 1.0, abs_tol=1e-9)


def test_stabilizer_fast_path_agrees_with_statevector_path():
    from qiskit.quantum_info import Clifford, Statevector

    qc = QuantumCircuit(4)
    qc.h(0)
    for i in range(3):
        qc.cx(i, i + 1)

    ee = EntanglementEntropy(partition=[1, 2])
    fast = ee._compute_stabilizer(Clifford.from_circuit(qc))
    general = ee._compute_statevector(Statevector.from_instruction(qc))
    assert math.isclose(fast, general, abs_tol=1e-9)


def test_invalid_partition_rejected():
    qc = QuantumCircuit(2)
    try:
        EntanglementEntropy(partition=[]).compute(qc)
        assert False, "expected ValueError for empty partition"
    except ValueError:
        pass

    try:
        EntanglementEntropy(partition=[0, 1]).compute(qc)
        assert False, "expected ValueError for full-system partition"
    except ValueError:
        pass


def test_repr_includes_partition():
    assert repr(EntanglementEntropy(partition=[0, 2])) == "EntanglementEntropy(partition=[0, 2])"
