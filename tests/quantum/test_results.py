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


def test_target_probability():
    result = SimulationResult(
            algorithm="grover",
            target_state="11",
            shots=1000,
            counts={"00": 100, "11": 900},
        )

    assert result.target_probability == 0.9

def test_most_likely_state():
    result = SimulationResult(
            algorithm="grover",
            target_state="11",
            shots=1000,
            counts={"00": 100, "11": 900},
        )

    assert result.most_likely_state == "11"

def test_target_probability_when_not_most_likely():
    result = SimulationResult(
            algorithm="grover",
            target_state="11",
            shots=1000,
            counts={"00": 800, "11": 200},
        )

    assert result.target_probability == 0.2
    assert result.most_likely_state == "00"