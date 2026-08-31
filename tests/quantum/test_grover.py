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
