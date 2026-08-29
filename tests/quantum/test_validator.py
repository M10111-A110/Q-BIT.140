import pytest

from backend.quantum.schemas import QuantumExperiment
from backend.quantum.validator import validate_experiment

def test_valid_experiment():
    experiment = QuantumExperiment(
        algorithm="grover",
        num_qubits=2,
        target_state="11",
        iterations=1,
        shots=1024,
    )

    validate_experiment(experiment)

def test_target_state_must_match_qubit_count():
    experiment = QuantumExperiment(
            algorithm="grover",
            num_qubits=2,
            target_state="101",
            iterations=1,
            shots=1024,
    )

    with pytest.raises(ValueError):
        validate_experiment(experiment)

def test_target_state_must_be_binary():
    experiment = QuantumExperiment(
            algorithm="grover",
            num_qubits=2,
            target_state="1A",
            iterations=1,
            shots=1024,
    )

    with pytest.raises(ValueError):
        validate_experiment(experiment)

def test_only_grover_is_supported():
    experiment = QuantumExperiment(
            algorithm="qft",
            num_qubits=2,
            target_state="11",
            iterations=1,
            shots=1024,
    )

    with pytest.raises(ValueError):
        validate_experiment(experiment)
    