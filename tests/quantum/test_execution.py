import pytest

from backend.quantum.grover import build_grover_circuit
from backend.quantum.execution import execute_circuit

@pytest.mark.parametrize("target_state", ["00", "01", "10", "11"])
def test_grover_finds_target_state(target_state):
    circuit = build_grover_circuit(
        num_qubits=2,
        target_state=target_state,
        iterations=1,
    )

    counts = execute_circuit(circuit, shots=1024)

    assert counts[target_state] == 1024