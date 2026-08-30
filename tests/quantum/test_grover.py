from backend.quantum.algorithms.grover import build_grover_circuit

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