from unittest.mock import MagicMock, patch
import pytest

from backend.quantum.engine import run_experiment
from backend.quantum.results import SimulationResult
from backend.quantum.schemas import QuantumExperiment


def test_run_experiment_success():
    experiment = QuantumExperiment(
        algorithm="grover",
        num_qubits=2,
        target_state="11",
        iterations=1,
        shots=1024,
    )

    result = run_experiment(experiment)

    assert isinstance(result, SimulationResult)
    assert result.algorithm == "grover"
    assert result.target_state == "11"
    assert result.shots == 1024
    assert result.counts == {"11": 1024}
    assert result.probabilities == {"11": 1.0}


def test_run_experiment_custom_shots():
    experiment = QuantumExperiment(
        algorithm="grover",
        num_qubits=2,
        target_state="01",
        iterations=1,
        shots=500,
    )

    result = run_experiment(experiment)

    assert result.shots == 500
    assert sum(result.counts.values()) == 500
    assert result.counts.get("01") == 500


@pytest.mark.parametrize(
    "num_qubits,target_state,iterations",
    [
        (3, "101", 2),
        (4, "0110", 3),
        (5, "10101", 4),
    ],
)
def test_run_experiment_multi_qubits(num_qubits, target_state, iterations):
    experiment = QuantumExperiment(
        algorithm="grover",
        num_qubits=num_qubits,
        target_state=target_state,
        iterations=iterations,
        shots=1024,
    )

    result = run_experiment(experiment)

    assert isinstance(result, SimulationResult)
    assert result.algorithm == "grover"
    assert result.target_state == target_state
    assert result.shots == 1024
    top_state = max(result.counts, key=result.counts.get)
    assert top_state == target_state
    assert result.probabilities[target_state] > 0.8



def test_run_experiment_validation_error():
    experiment = QuantumExperiment(
        algorithm="grover",
        num_qubits=2,
        target_state="101",  # target_state length (3) != num_qubits (2)
        iterations=1,
        shots=1024,
    )

    with pytest.raises(ValueError):
        run_experiment(experiment)


def test_run_experiment_orchestration_isolated():
    # Tests the orchestration pipeline independently from simulator execution
    experiment = QuantumExperiment(
        algorithm="grover",
        num_qubits=2,
        target_state="10",
        iterations=1,
        shots=256,
    )

    fake_circuit = MagicMock()
    fake_counts = {"10": 256}
    fake_builder = MagicMock(return_value=fake_circuit)

    with patch("backend.quantum.engine.validate_experiment") as mock_validate, \
         patch("backend.quantum.engine.get_algorithm", return_value=fake_builder) as mock_get_algorithm, \
         patch("backend.quantum.engine.execute_circuit", return_value=fake_counts) as mock_exec:

        result = run_experiment(experiment)

    mock_validate.assert_called_once_with(experiment)
    mock_get_algorithm.assert_called_once_with("grover")
    fake_builder.assert_called_once_with(
        num_qubits=2,
        target_state="10",
        iterations=1,
    )
    mock_exec.assert_called_once_with(
        fake_circuit,
        shots=256,
    )

    assert result.algorithm == "grover"
    assert result.target_state == "10"
    assert result.shots == 256
    assert result.counts == fake_counts


# ---------------------------------------------------------------------------
# Circuit metadata integration tests
# ---------------------------------------------------------------------------

def test_run_experiment_result_has_circuit_metadata():
    """run_experiment() must return a result with populated CircuitMetadata."""
    from backend.quantum.results import CircuitMetadata

    experiment = QuantumExperiment(
        algorithm="grover",
        num_qubits=2,
        target_state="11",
        iterations=1,
        shots=1024,
    )

    result = run_experiment(experiment)

    assert result.circuit is not None
    assert isinstance(result.circuit, CircuitMetadata)
    assert result.circuit.num_qubits == 2
    assert result.circuit.num_clbits == 2
    assert result.circuit.depth > 0
    assert "measure" in result.circuit.gate_counts
    assert result.circuit.gate_counts["measure"] == 2
    assert isinstance(result.circuit.diagram, str)
    assert len(result.circuit.diagram.strip()) > 0


@pytest.mark.parametrize(
    "num_qubits,target_state,iterations",
    [
        (2, "11", 1),
        (3, "101", 2),
        (4, "0110", 3),
        (5, "10101", 4),
    ],
)
def test_run_experiment_circuit_metadata_qubit_count_matches(
    num_qubits, target_state, iterations
):
    """CircuitMetadata.num_qubits must match the experiment's num_qubits."""
    experiment = QuantumExperiment(
        algorithm="grover",
        num_qubits=num_qubits,
        target_state=target_state,
        iterations=iterations,
        shots=1024,
    )

    result = run_experiment(experiment)

    assert result.circuit is not None
    assert result.circuit.num_qubits == num_qubits


def test_run_experiment_result_is_json_serializable():
    """run_experiment() result must be fully serializable via to_dict()."""
    import json

    experiment = QuantumExperiment(
        algorithm="grover",
        num_qubits=2,
        target_state="11",
        iterations=1,
        shots=1024,
    )

    result = run_experiment(experiment)

    # Must not raise
    serialized = json.dumps(result.to_dict())
    reloaded = json.loads(serialized)

    assert reloaded["algorithm"] == "grover"
    assert reloaded["target_state"] == "11"
    assert reloaded["shots"] == 1024
    assert "counts" in reloaded
    assert "probabilities" in reloaded
    assert "target_probability" in reloaded
    assert "most_likely_state" in reloaded
    assert reloaded["circuit"]["num_qubits"] == 2
    assert reloaded["circuit"]["depth"] > 0