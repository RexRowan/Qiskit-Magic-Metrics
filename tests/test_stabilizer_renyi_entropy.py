import math

from qiskit import QuantumCircuit

from qiskit_magic_metrics import StabilizerRenyiEntropy


def test_stabilizer_states_have_zero_magic():
    # Any Clifford-only circuit is a stabilizer state and must read exactly zero, via the fast
    # path -- check a few structurally different examples.
    circuits = []

    ghz = QuantumCircuit(3)
    ghz.h(0)
    ghz.cx(0, 1)
    ghz.cx(1, 2)
    circuits.append(ghz)

    bell = QuantumCircuit(2)
    bell.h(0)
    bell.cx(0, 1)
    circuits.append(bell)

    plus = QuantumCircuit(1)
    plus.h(0)
    circuits.append(plus)

    zero = QuantumCircuit(2)  # |00>
    circuits.append(zero)

    magic = StabilizerRenyiEntropy(alpha=2)
    for qc in circuits:
        assert magic.compute(qc) == 0.0


def test_t_gate_state_has_nonzero_magic():
    # A single T gate on |+> is the canonical non-stabilizer ("magic") state.
    qc = QuantumCircuit(1)
    qc.h(0)
    qc.t(0)
    magic = StabilizerRenyiEntropy(alpha=2)
    m = magic.compute(qc)
    assert m > 1e-9


def test_stabilizer_fast_path_agrees_with_statevector_path_on_a_stabilizer_state():
    from qiskit.quantum_info import Clifford, Statevector

    qc = QuantumCircuit(3)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(1, 2)

    magic = StabilizerRenyiEntropy(alpha=2)
    fast = magic._compute_stabilizer(Clifford.from_circuit(qc))
    general = magic._compute_statevector(Statevector.from_instruction(qc))
    assert math.isclose(fast, general, abs_tol=1e-9)


def test_alpha_equals_one_is_rejected():
    try:
        StabilizerRenyiEntropy(alpha=1)
        assert False, "expected ValueError for alpha=1"
    except ValueError:
        pass


def test_nonpositive_alpha_is_rejected():
    for bad_alpha in (0, -1, -0.5):
        try:
            StabilizerRenyiEntropy(alpha=bad_alpha)
            assert False, f"expected ValueError for alpha={bad_alpha}"
        except ValueError:
            pass


def test_repr_includes_alpha():
    assert repr(StabilizerRenyiEntropy(alpha=3)) == "StabilizerRenyiEntropy(alpha=3)"
