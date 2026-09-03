import pytest
from backend.quantum.algorithms.grover import build_grover_circuit


@pytest.mark.parametrize(
    "num_qubits,target_state",
    [
        (2, "00"),
        (2, "11"),
        (3, "000"),
        (3, "101"),
        (4, "0110"),
        (4, "1111"),
        (5, "00000"),
        (5, "10101"),
        (5, "11111"),
    ],
)
def test_grover_circuit_structure_for_supported_qubit_counts(num_qubits, target_state):
    circuit = build_grover_circuit(
        num_qubits=num_qubits,
        target_state=target_state,
        iterations=1,
    )

    assert circuit.num_qubits == num_qubits
    assert circuit.num_clbits == num_qubits
    assert circuit.count_ops()["measure"] == num_qubits


def test_grover_circuit_has_expected_qubits():
    circuit = build_grover_circuit(
        num_qubits=2,
        target_state="11",
        iterations=1,
    )

    assert circuit.num_qubits == 2
    assert circuit.num_clbits == 2


def test_grover_circuit_contains_measurement():
    circuit = build_grover_circuit(
        num_qubits=2,
        target_state="11",
        iterations=1,
    )

    assert circuit.num_clbits == 2
    assert circuit.count_ops()["measure"] == 2


def test_grover_circuit_validates_target_state_length():
    with pytest.raises(ValueError, match="length"):
        build_grover_circuit(num_qubits=3, target_state="11")


def test_grover_circuit_validates_target_state_characters():
    with pytest.raises(ValueError, match="binary"):
        build_grover_circuit(num_qubits=2, target_state="12")


def test_grover_circuit_validates_min_qubits():
    with pytest.raises(ValueError, match="qubits"):
        build_grover_circuit(num_qubits=1, target_state="1")


def test_canonical_grover_2q_target_10_exactness_and_aer_simulation():
    """
    Regression Test for Canonical 2-Qubit Grover Search (Target |10>):
      1. Ideal statevector probability for |10> is exactly 1.0 (100.0%)
      2. Ideal probabilities for all other states (|00>, |01>, |11>) are strictly 0.0
      3. AerSimulator 1024-shot empirical counts concentrate completely on '10' (1024/1024)
      4. Verifies Qiskit bit ordering/endianness: '10' maps to q1=1, q0=0
    """
    from qiskit.quantum_info import Statevector
    from backend.quantum.execution import execute_circuit

    circ = build_grover_circuit(num_qubits=2, target_state="10", iterations=1)

    # 1. Statevector exactness (ideal quantum mechanics)
    circ_no_meas = circ.remove_final_measurements(inplace=False)
    sv = Statevector.from_instruction(circ_no_meas)
    probs = sv.probabilities_dict()

    assert pytest.approx(probs.get("10", 0.0), abs=1e-7) == 1.0
    assert pytest.approx(probs.get("00", 0.0), abs=1e-7) == 0.0
    assert pytest.approx(probs.get("01", 0.0), abs=1e-7) == 0.0
    assert pytest.approx(probs.get("11", 0.0), abs=1e-7) == 0.0

    # 2. Qiskit Aer simulation with 1024 shots
    counts = execute_circuit(circ, shots=1024)
    assert counts == {"10": 1024}
    assert counts.get("10") == 1024
