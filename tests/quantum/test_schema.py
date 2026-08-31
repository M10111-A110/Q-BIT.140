from backend.quantum.schemas import QuantumExperiment as qe

def test_valid_exp():
    exp = qe(
        algorithm="grover",
        num_qubits=2,
        target_state="11",
        iterations=1,
        shots=1024
    )

    assert exp.algorithm == "grover"
    assert exp.num_qubits == 2
    assert exp.target_state == "11"
    assert exp.iterations == 1
    assert exp.shots == 1024