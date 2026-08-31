import pytest

from backend.quantum.algorithms.grover import build_grover_circuit
from backend.quantum.execution import execute_circuit


@pytest.mark.parametrize("target_state", ["00", "01", "10", "11"])
def test_grover_2qubit_finds_target_state(target_state):
    circuit = build_grover_circuit(
        num_qubits=2,
        target_state=target_state,
        iterations=1,
    )

    counts = execute_circuit(circuit, shots=1024)

    assert counts[target_state] == 1024


@pytest.mark.parametrize("target_state", ["000", "010", "101", "110", "111"])
def test_grover_3qubit_amplifies_target_state(target_state):
    circuit = build_grover_circuit(
        num_qubits=3,
        target_state=target_state,
        iterations=2,
    )

    counts = execute_circuit(circuit, shots=1024)
    top_state = max(counts, key=counts.get)

    assert top_state == target_state
    # 2 iterations on 3 qubits yields ~94.5% theoretical probability
    assert counts[target_state] > 850


@pytest.mark.parametrize("target_state", ["0000", "0110", "1001", "1111"])
def test_grover_4qubit_amplifies_target_state(target_state):
    circuit = build_grover_circuit(
        num_qubits=4,
        target_state=target_state,
        iterations=3,
    )

    counts = execute_circuit(circuit, shots=1024)
    top_state = max(counts, key=counts.get)

    assert top_state == target_state
    # 3 iterations on 4 qubits yields ~96% theoretical probability
    assert counts[target_state] > 850


@pytest.mark.parametrize("target_state", ["00000", "01010", "10101", "11111"])
def test_grover_5qubit_amplifies_target_state(target_state):
    circuit = build_grover_circuit(
        num_qubits=5,
        target_state=target_state,
        iterations=4,
    )

    counts = execute_circuit(circuit, shots=1024)
    top_state = max(counts, key=counts.get)

    assert top_state == target_state
    # 4 iterations on 5 qubits yields ~99.9% theoretical probability
    assert counts[target_state] > 900
