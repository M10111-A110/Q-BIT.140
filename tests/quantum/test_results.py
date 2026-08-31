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


# ---------------------------------------------------------------------------
# to_dict() serialization tests
# ---------------------------------------------------------------------------

def test_to_dict_includes_all_fields():
    import json
    result = SimulationResult(
        algorithm="grover",
        target_state="11",
        shots=1000,
        counts={"11": 800, "00": 200},
    )

    d = result.to_dict()

    assert d["algorithm"] == "grover"
    assert d["target_state"] == "11"
    assert d["shots"] == 1000
    assert d["counts"] == {"11": 800, "00": 200}
    assert d["probabilities"] == {"11": 0.8, "00": 0.2}
    assert d["target_probability"] == 0.8
    assert d["most_likely_state"] == "11"
    assert "circuit" in d


def test_to_dict_without_circuit_is_json_serializable():
    import json
    result = SimulationResult(
        algorithm="grover",
        target_state="11",
        shots=100,
        counts={"11": 100},
    )

    # Must not raise
    serialized = json.dumps(result.to_dict())
    assert len(serialized) > 0


def test_to_dict_circuit_is_none_when_not_set():
    result = SimulationResult(
        algorithm="grover",
        target_state="11",
        shots=100,
        counts={"11": 100},
    )

    d = result.to_dict()
    assert d["circuit"] is None


def test_simulation_result_circuit_defaults_to_none():
    """Backward compatibility: existing call sites that don't pass circuit still work."""
    result = SimulationResult(
        algorithm="grover",
        target_state="11",
        shots=100,
        counts={"11": 100},
    )

    assert result.circuit is None


def test_to_dict_with_circuit_metadata_is_json_serializable():
    import json
    from backend.quantum.results import CircuitMetadata

    meta = CircuitMetadata(
        num_qubits=2,
        num_clbits=2,
        depth=5,
        gate_counts={"h": 4, "cz": 1, "measure": 2},
        diagram="     ┌───┐\nq_0: ┤ H ├\n     └───┘",
    )
    result = SimulationResult(
        algorithm="grover",
        target_state="11",
        shots=1000,
        counts={"11": 900, "00": 100},
        circuit=meta,
    )

    serialized = json.dumps(result.to_dict())
    reloaded = json.loads(serialized)

    assert reloaded["circuit"]["num_qubits"] == 2
    assert reloaded["circuit"]["depth"] == 5
    assert reloaded["circuit"]["gate_counts"] == {"h": 4, "cz": 1, "measure": 2}
    assert "diagram" in reloaded["circuit"]