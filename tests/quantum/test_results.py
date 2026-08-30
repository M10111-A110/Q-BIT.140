import pytest

from backend.quantum.results import SimulationResult

def test_simulation_result_stores_values():
    result = SimulationResult(
        algorithm="grover",
        target_state="11",
        shots=100,
        counts={
            "11":90,
            "00":10
        }
    )

    assert result.algorithm == "grover"
    assert result.target_state == "11"
    assert result.shots == 100
    assert result.counts == {"11":90, "00":10}

def test_simulation_result_rejects_non_positive_shots():
    with pytest.raises(ValueError):
        SimulationResult(
            algorithm="grover",
            target_state="11",
            shots=0,
            counts={},
        )


def test_simulation_result_rejects_negative_counts():
    with pytest.raises(ValueError):
        SimulationResult(
            algorithm="grover",
            target_state="11",
            shots=100,
            counts={"11": -1, "00": 101},
        )


def test_simulation_result_rejects_counts_not_matching_shots():
    with pytest.raises(ValueError):
        SimulationResult(
            algorithm="grover",
            target_state="11",
            shots=100,
            counts={"11": 80, "00": 10},
        )


def test_simulation_result_calculates_probabilities():
    result = SimulationResult(
        algorithm="grover",
        target_state="11",
        shots=1000,
        counts={"00": 250, "11": 750},
    )

    assert result.probabilities == {"00": 0.25, "11": 0.75}
    assert sum(result.probabilities.values()) == 1.0