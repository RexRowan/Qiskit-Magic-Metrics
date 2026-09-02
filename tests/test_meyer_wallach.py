import math

from qiskit import QuantumCircuit

from qiskit_magic_metrics import MeyerWallachMeasure


def ghz(n):
    qc = QuantumCircuit(n)
    qc.h(0)
    for i in range(n - 1):
        qc.cx(i, i + 1)
    return qc


def product_state(n):
    qc = QuantumCircuit(n)
    qc.h(0)  # local rotation only, no entangling gates
    return qc


def w_state_3():
    # 3-qubit W state, not a stabilizer state — exercises the general statevector path.
    qc = QuantumCircuit(3)
    qc.ry(2 * math.acos(1 / math.sqrt(3)), 0)
    qc.ch(0, 1)
    qc.cx(1, 2)
    qc.cx(0, 1)
    qc.x(0)
    return qc


def test_product_state_zero_entanglement():
    mw = MeyerWallachMeasure()
    assert mw.compute(product_state(3)) == 0.0


def test_ghz_is_maximally_entangled():
    mw = MeyerWallachMeasure()
    for n in (2, 3, 4):
        assert math.isclose(mw.compute(ghz(n)), 1.0, abs_tol=1e-9)


def test_bell_pair():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    mw = MeyerWallachMeasure()
    assert math.isclose(mw.compute(qc), 1.0, abs_tol=1e-9)


def test_stabilizer_fast_path_matches_statevector_path():
    mw = MeyerWallachMeasure()
    circuit = ghz(4)
    from qiskit.quantum_info import Clifford, Statevector

    fast = mw._compute_stabilizer(Clifford.from_circuit(circuit))
    general = mw._compute_statevector(Statevector.from_instruction(circuit))
    assert math.isclose(fast, general, abs_tol=1e-9)


def test_w_state_uses_general_path_and_is_between_zero_and_one():
    # W-state is entangled but not a stabilizer state, so this exercises _compute_statevector
    # via the automatic Clifford-detection fallback, not the fast path.
    mw = MeyerWallachMeasure()
    q = mw.compute(w_state_3())
    assert 0.0 < q < 1.0
