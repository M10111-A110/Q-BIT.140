import pytest
from backend.adaptive.activities import (
    MVP_ACTIVITIES,
    Activity,
    get_activities_for_concept,
    get_activity,
    list_activities,
)


def test_activities_registry_contains_expected_core_activities():
    activities = list_activities()
    assert len(activities) == 4

    ids = [a.activity_id for a in activities]
    assert "act_grover_2q_predict" in ids
    assert "act_measurement_prob_diagnostic" in ids
    assert "act_superposition_remediation" in ids
    assert "act_grover_iteration_reasoning" in ids


def test_get_activity_by_id():
    act = get_activity("act_grover_2q_predict")
    assert act.activity_id == "act_grover_2q_predict"
    assert act.task_type == "quantum_prediction"
    assert act.concept_id == "grover.search_problem"
    assert act.quantum_experiment is not None
    assert act.quantum_experiment["algorithm"] == "grover"
    assert act.quantum_experiment["num_qubits"] == 2
    assert act.quantum_experiment["target_state"] == "10"
    assert act.remediation_activity_id == "act_measurement_prob_diagnostic"
    assert act.next_activity_id == "act_grover_iteration_reasoning"


def test_get_activity_unknown_raises_key_error():
    with pytest.raises(KeyError):
        get_activity("unknown_activity_xyz")


def test_get_activities_for_concept():
    acts = get_activities_for_concept("quantum.measurement")
    assert len(acts) == 1
    assert acts[0].activity_id == "act_measurement_prob_diagnostic"


def test_activity_to_dict():
    act = get_activity("act_superposition_remediation")
    d = act.to_dict()
    assert d["activity_id"] == "act_superposition_remediation"
    assert d["expected_answer"] == "B"
    assert "options" in d
    assert "B" in d["options"]
