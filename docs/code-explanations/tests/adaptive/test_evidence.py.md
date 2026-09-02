# Explanation: `tests/adaptive/test_evidence.py`

## Purpose

This page explains the meaningful behavior in `tests/adaptive/test_evidence.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
import json
import pytest
from backend.adaptive.activities import get_activity
from backend.adaptive.engine import LearnerModel
from backend.adaptive.evidence import (
    GapInference,
    LearnerEvidence,
    evaluate_conceptual_response,
    evaluate_quantum_prediction,
)
from backend.adaptive.models import LearnerState


def test_evidence_construction_and_serialization():
    mock_sim_result = {
        "algorithm": "grover",
        "target_state": "10",
        "shots": 1024,
        "counts": {"00": 20, "01": 20, "10": 960, "11": 24},
        "probabilities": {"00": 0.0195, "01": 0.0195, "10": 0.9375, "11": 0.0234},
        "target_probability": 0.9375,
        "most_likely_state": "10",
        "circuit": {"num_qubits": 2, "depth": 5},
    }

    evidence = evaluate_quantum_prediction(
        learner_id="user_123",
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="10",
        simulation_result=mock_sim_result,
        attempt_number=1,
    )

    assert evidence.learner_id == "user_123"
    assert evidence.activity_id == "act_grover_2q_predict"
    assert evidence.concept_id == "grover.search_problem"
    assert evidence.learner_response == "10"
    assert evidence.is_correct is True
    assert evidence.evaluation_details["match"] is True
    assert evidence.evaluation_details["predicted_probability"] == 0.9375
    assert evidence.verified_result == mock_sim_result

    d = evidence.to_dict()
    assert d["learner_id"] == "user_123"
    assert d["verified_result"]["algorithm"] == "grover"


def test_learner_evidence_round_trip_serialization():
    mock_sim_result = {
        "algorithm": "grover",
        "target_state": "10",
        "shots": 1024,
        "counts": {"00": 20, "01": 20, "10": 960, "11": 24},
        "probabilities": {"00": 0.0195, "01": 0.0195, "10": 0.9375, "11": 0.0234},
        "target_probability": 0.9375,
        "most_likely_state": "10",
    }

    original = evaluate_quantum_prediction(
        learner_id="user_roundtrip",
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="10",
        simulation_result=mock_sim_result,
        attempt_number=2,
        metadata={"session_id": "sess_abc"},
    )

    # Serialize to dict and JSON string
    serialized_dict = original.to_dict()
    json_str = json.dumps(serialized_dict)

    # Deserialize back
    deserialized_dict = json.loads(json_str)
    reconstituted = LearnerEvidence.from_dict(deserialized_dict)

    assert reconstituted.learner_id == original.learner_id
    assert reconstituted.activity_id == original.activity_id
    assert reconstituted.concept_id == original.concept_id
    assert reconstituted.learner_response == original.learner_response
    assert reconstituted.is_correct == original.is_correct
    assert reconstituted.attempt_number == original.attempt_number
    assert reconstituted.verified_result == original.verified_result
    assert reconstituted.evaluation_details == original.evaluation_details
    assert reconstituted.metadata == original.metadata


def test_learner_evidence_from_dict_validation():
    # Missing learner_id
    with pytest.raises(ValueError, match="learner_id"):
        LearnerEvidence.from_dict({"activity_id": "act1", "concept_id": "grover"})

    # Missing activity_id
    with pytest.raises(ValueError, match="activity_id"):
        LearnerEvidence.from_dict({"learner_id": "u1", "concept_id": "grover"})

    # Missing concept_id
    with pytest.raises(ValueError, match="concept_id"):
        LearnerEvidence.from_dict({"learner_id": "u1", "activity_id": "act1"})

    # Not a dictionary
    with pytest.raises(TypeError):
        LearnerEvidence.from_dict("not_a_dict")  # type: ignore


def test_non_json_serializable_evidence_rejected():
    class NonSerializableClass:
        pass

    with pytest.raises(ValueError, match="non-JSON-serializable"):
        LearnerEvidence(
            learner_id="u1",
            activity_id="act1",
            concept_id="grover.search_problem",
            learner_response="01",
            is_correct=False,
            verified_result={"invalid_obj": NonSerializableClass()},
        )


def test_learner_state_round_trip_serialization():
    state = LearnerState(user_id="usr_state_test")
    state.record_attempt("Superposition", 0.8, ["Q3"])
    state.gap_inferences["quantum.superposition"] = {
        "concept_id": "quantum.superposition",
        "confidence": 0.15,
        "status": "improving",
        "supporting_evidence_count": 1,
        "description": "Improving.",
    }

    raw = state.to_dict()
    json_str = json.dumps(raw)
    loaded = LearnerState.from_dict(json.loads(json_str))

    assert loaded.user_id == "usr_state_test"
    assert loaded.concept_scores["Superposition"] == 0.8
    assert loaded.gap_inferences["quantum.superposition"]["status"] == "improving"


def test_record_evidence_accepts_dictionary():
    model = LearnerModel()
    state = LearnerState(user_id="u1")

    evidence_dict = {
        "learner_id": "u1",
        "activity_id": "act_grover_2q_predict",
        "concept_id": "grover.search_problem",
        "learner_response": "10",
        "is_correct": True,
        "attempt_number": 1,
        "verified_result": {"most_likely_state": "10"},
        "evaluation_details": {"match": True},
    }

    # Pass raw dictionary instead of object
    decision = model.record_evidence(evidence_dict, state)
    assert decision.action == "advance"
    assert len(state.evidence_history) == 1


def test_prediction_mismatch_evaluation():
    mock_sim_result = {
        "algorithm": "grover",
        "target_state": "10",
        "shots": 1024,
        "counts": {"00": 20, "01": 20, "10": 960, "11": 24},
        "probabilities": {"00": 0.0195, "01": 0.0195, "10": 0.9375, "11": 0.0234},
        "target_probability": 0.9375,
        "most_likely_state": "10",
    }

    evidence = evaluate_quantum_prediction(
        learner_id="user_123",
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="01",  # incorrect prediction
        simulation_result=mock_sim_result,
    )

    assert evidence.is_correct is False
    assert evidence.evaluation_details["match"] is False
    assert evidence.evaluation_details["predicted_state"] == "01"
    assert evidence.evaluation_details["most_likely_state"] == "10"


def test_conceptual_response_evaluation():
    ev_correct = evaluate_conceptual_response(
        learner_id="u1",
        activity_id="act_measurement_prob_diagnostic",
        concept_id="quantum.measurement",
        selected_option="b",
        expected_option="B",
    )
    assert ev_correct.is_correct is True
    assert ev_correct.learner_response == "B"

    ev_wrong = evaluate_conceptual_response(
        learner_id="u1",
        activity_id="act_measurement_prob_diagnostic",
        concept_id="quantum.measurement",
        selected_option="A",
        expected_option="B",
    )
    assert ev_wrong.is_correct is False


def test_single_error_does_not_infer_strong_gap():
    model = LearnerModel()
    state = LearnerState(user_id="u1")
    mock_sim = {"most_likely_state": "10", "target_probability": 0.93}

    # Attempt 1: Incorrect
    ev1 = evaluate_quantum_prediction(
        learner_id="u1",
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="01",
        simulation_result=mock_sim,
    )

    decision = model.record_evidence(ev1, state)

    # 1. Action should gather more evidence, not jump to remediation immediately
    assert decision.action == "gather_evidence"
    assert decision.target == "act_grover_2q_predict"

    # 2. Confidence in conceptual gap is low (0.35) and status is "observing"
    inference = state.gap_inferences.get("grover.search_problem")
    assert inference is not None
    assert inference["confidence"] == 0.35
    assert inference["status"] == "observing"
    assert "preliminary observation" in inference["description"]


def test_repeated_errors_increase_confidence_and_trigger_remediation():
    model = LearnerModel()
    state = LearnerState(user_id="u1")
    mock_sim = {"most_likely_state": "10", "target_probability": 0.93}

    # Attempt 1: Incorrect
    ev1 = evaluate_quantum_prediction(
        learner_id="u1",
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="01",
        simulation_result=mock_sim,
    )
    model.record_evidence(ev1, state)

    # Attempt 2: Incorrect again on same activity
    ev2 = evaluate_quantum_prediction(
        learner_id="u1",
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="00",
        simulation_result=mock_sim,
        attempt_number=2,
    )
    decision = model.record_evidence(ev2, state)

    # Action should now be targeted remediation pointing to measurement diagnostic
    assert decision.action == "targeted_remediation"
    assert decision.target == "act_measurement_prob_diagnostic"

    # Confidence should be elevated (0.90) and status "remediation_needed"
    inference = state.gap_inferences.get("grover.search_problem")
    assert inference["confidence"] == 0.90
    assert inference["status"] == "remediation_needed"
    assert "repeated incorrect attempts" in inference["description"]


def test_post_intervention_improvement():
    model = LearnerModel()
    state = LearnerState(user_id="u1")
    mock_sim = {"most_likely_state": "10", "target_probability": 0.93}

    # First attempt: incorrect
    ev1 = evaluate_quantum_prediction(
        learner_id="u1",
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="01",
        simulation_result=mock_sim,
    )
    model.record_evidence(ev1, state)

    # Second attempt after intervention: correct
    ev2 = evaluate_quantum_prediction(
        learner_id="u1",
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="10",
        simulation_result=mock_sim,
        attempt_number=2,
    )
    decision = model.record_evidence(ev2, state)

    assert decision.action == "advance"
    assert decision.target == "act_grover_iteration_reasoning"

    inference = state.gap_inferences.get("grover.search_problem")
    assert inference["status"] == "improving"
    assert inference["confidence"] == 0.15
    assert "post-intervention improvement" in inference["description"]


def test_invalid_simulation_result_type_rejected():
    with pytest.raises(TypeError):
        evaluate_quantum_prediction(
            learner_id="u1",
            activity_id="act_grover_2q_predict",
            concept_id="grover.search_problem",
            prediction="10",
            simulation_result="not_a_dictionary",  # invalid
        )

```

## Line Notes

### Line 1

`import json`

Imports a dependency or project symbol so later code can use it by name.
### Line 2

`import pytest`

Imports a dependency or project symbol so later code can use it by name.
### Line 3

`from backend.adaptive.activities import get_activity`

Imports a dependency or project symbol so later code can use it by name.
### Line 4

`from backend.adaptive.engine import LearnerModel`

Imports a dependency or project symbol so later code can use it by name.
### Line 5

`from backend.adaptive.evidence import (`

Imports a dependency or project symbol so later code can use it by name.
### Line 6

`GapInference,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 7

`LearnerEvidence,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 8

`evaluate_conceptual_response,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 9

`evaluate_quantum_prediction,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 10

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 11

`from backend.adaptive.models import LearnerState`

Imports a dependency or project symbol so later code can use it by name.
### Line 12

`(blank)`

Blank line used to separate nearby statements.
### Line 14

`def test_evidence_construction_and_serialization():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 15

`mock_sim_result = {`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 16

`"algorithm": "grover",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 17

`"target_state": "10",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 18

`"shots": 1024,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 19

`"counts": {"00": 20, "01": 20, "10": 960, "11": 24},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 20

`"probabilities": {"00": 0.0195, "01": 0.0195, "10": 0.9375, "11": 0.0234},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 21

`"target_probability": 0.9375,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 22

`"most_likely_state": "10",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 23

`"circuit": {"num_qubits": 2, "depth": 5},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 24

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 25

`(blank)`

Blank line used to separate nearby statements.
### Line 26

`evidence = evaluate_quantum_prediction(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 27

`learner_id="user_123",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 28

`activity_id="act_grover_2q_predict",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 29

`concept_id="grover.search_problem",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 30

`prediction="10",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 31

`simulation_result=mock_sim_result,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 32

`attempt_number=1,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 33

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 34

`(blank)`

Blank line used to separate nearby statements.
### Line 35

`assert evidence.learner_id == "user_123"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 36

`assert evidence.activity_id == "act_grover_2q_predict"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 37

`assert evidence.concept_id == "grover.search_problem"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 38

`assert evidence.learner_response == "10"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 39

`assert evidence.is_correct is True`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 40

`assert evidence.evaluation_details["match"] is True`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 41

`assert evidence.evaluation_details["predicted_probability"] == 0.9375`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 42

`assert evidence.verified_result == mock_sim_result`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 43

`(blank)`

Blank line used to separate nearby statements.
### Line 44

`d = evidence.to_dict()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 45

`assert d["learner_id"] == "user_123"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 46

`assert d["verified_result"]["algorithm"] == "grover"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 47

`(blank)`

Blank line used to separate nearby statements.
### Line 49

`def test_learner_evidence_round_trip_serialization():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 50

`mock_sim_result = {`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 51

`"algorithm": "grover",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 52

`"target_state": "10",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 53

`"shots": 1024,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 54

`"counts": {"00": 20, "01": 20, "10": 960, "11": 24},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 55

`"probabilities": {"00": 0.0195, "01": 0.0195, "10": 0.9375, "11": 0.0234},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 56

`"target_probability": 0.9375,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 57

`"most_likely_state": "10",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 58

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 59

`(blank)`

Blank line used to separate nearby statements.
### Line 60

`original = evaluate_quantum_prediction(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 61

`learner_id="user_roundtrip",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 62

`activity_id="act_grover_2q_predict",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 63

`concept_id="grover.search_problem",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 64

`prediction="10",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 65

`simulation_result=mock_sim_result,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 66

`attempt_number=2,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 67

`metadata={"session_id": "sess_abc"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 68

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 69

`(blank)`

Blank line used to separate nearby statements.
### Line 70

`# Serialize to dict and JSON string`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 71

`serialized_dict = original.to_dict()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 72

`json_str = json.dumps(serialized_dict)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 73

`(blank)`

Blank line used to separate nearby statements.
### Line 74

`# Deserialize back`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 75

`deserialized_dict = json.loads(json_str)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 76

`reconstituted = LearnerEvidence.from_dict(deserialized_dict)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 77

`(blank)`

Blank line used to separate nearby statements.
### Line 78

`assert reconstituted.learner_id == original.learner_id`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 79

`assert reconstituted.activity_id == original.activity_id`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 80

`assert reconstituted.concept_id == original.concept_id`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 81

`assert reconstituted.learner_response == original.learner_response`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 82

`assert reconstituted.is_correct == original.is_correct`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 83

`assert reconstituted.attempt_number == original.attempt_number`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 84

`assert reconstituted.verified_result == original.verified_result`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 85

`assert reconstituted.evaluation_details == original.evaluation_details`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 86

`assert reconstituted.metadata == original.metadata`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 87

`(blank)`

Blank line used to separate nearby statements.
### Line 89

`def test_learner_evidence_from_dict_validation():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 90

`# Missing learner_id`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 91

`with pytest.raises(ValueError, match="learner_id"):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 92

`LearnerEvidence.from_dict({"activity_id": "act1", "concept_id": "grover"})`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 93

`(blank)`

Blank line used to separate nearby statements.
### Line 94

`# Missing activity_id`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 95

`with pytest.raises(ValueError, match="activity_id"):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 96

`LearnerEvidence.from_dict({"learner_id": "u1", "concept_id": "grover"})`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 97

`(blank)`

Blank line used to separate nearby statements.
### Line 98

`# Missing concept_id`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 99

`with pytest.raises(ValueError, match="concept_id"):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 100

`LearnerEvidence.from_dict({"learner_id": "u1", "activity_id": "act1"})`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 101

`(blank)`

Blank line used to separate nearby statements.
### Line 102

`# Not a dictionary`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 103

`with pytest.raises(TypeError):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 104

`LearnerEvidence.from_dict("not_a_dict")  # type: ignore`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 105

`(blank)`

Blank line used to separate nearby statements.
### Line 107

`def test_non_json_serializable_evidence_rejected():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 108

`class NonSerializableClass:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 109

`pass`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 110

`(blank)`

Blank line used to separate nearby statements.
### Line 111

`with pytest.raises(ValueError, match="non-JSON-serializable"):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 112

`LearnerEvidence(`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 113

`learner_id="u1",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 114

`activity_id="act1",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 115

`concept_id="grover.search_problem",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 116

`learner_response="01",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 117

`is_correct=False,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 118

`verified_result={"invalid_obj": NonSerializableClass()},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 119

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 120

`(blank)`

Blank line used to separate nearby statements.
### Line 122

`def test_learner_state_round_trip_serialization():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 123

`state = LearnerState(user_id="usr_state_test")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 124

`state.record_attempt("Superposition", 0.8, ["Q3"])`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 125

`state.gap_inferences["quantum.superposition"] = {`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 126

`"concept_id": "quantum.superposition",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 127

`"confidence": 0.15,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 128

`"status": "improving",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 129

`"supporting_evidence_count": 1,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 130

`"description": "Improving.",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 131

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 132

`(blank)`

Blank line used to separate nearby statements.
### Line 133

`raw = state.to_dict()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 134

`json_str = json.dumps(raw)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 135

`loaded = LearnerState.from_dict(json.loads(json_str))`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 136

`(blank)`

Blank line used to separate nearby statements.
### Line 137

`assert loaded.user_id == "usr_state_test"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 138

`assert loaded.concept_scores["Superposition"] == 0.8`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 139

`assert loaded.gap_inferences["quantum.superposition"]["status"] == "improving"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 140

`(blank)`

Blank line used to separate nearby statements.
### Line 142

`def test_record_evidence_accepts_dictionary():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 143

`model = LearnerModel()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 144

`state = LearnerState(user_id="u1")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 145

`(blank)`

Blank line used to separate nearby statements.
### Line 146

`evidence_dict = {`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 147

`"learner_id": "u1",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 148

`"activity_id": "act_grover_2q_predict",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 149

`"concept_id": "grover.search_problem",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 150

`"learner_response": "10",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 151

`"is_correct": True,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 152

`"attempt_number": 1,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 153

`"verified_result": {"most_likely_state": "10"},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 154

`"evaluation_details": {"match": True},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 155

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 156

`(blank)`

Blank line used to separate nearby statements.
### Line 157

`# Pass raw dictionary instead of object`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 158

`decision = model.record_evidence(evidence_dict, state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 159

`assert decision.action == "advance"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 160

`assert len(state.evidence_history) == 1`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 161

`(blank)`

Blank line used to separate nearby statements.
### Line 163

`def test_prediction_mismatch_evaluation():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 164

`mock_sim_result = {`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 165

`"algorithm": "grover",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 166

`"target_state": "10",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 167

`"shots": 1024,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 168

`"counts": {"00": 20, "01": 20, "10": 960, "11": 24},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 169

`"probabilities": {"00": 0.0195, "01": 0.0195, "10": 0.9375, "11": 0.0234},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 170

`"target_probability": 0.9375,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 171

`"most_likely_state": "10",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 172

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 173

`(blank)`

Blank line used to separate nearby statements.
### Line 174

`evidence = evaluate_quantum_prediction(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 175

`learner_id="user_123",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 176

`activity_id="act_grover_2q_predict",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 177

`concept_id="grover.search_problem",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 178

`prediction="01",  # incorrect prediction`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 179

`simulation_result=mock_sim_result,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 180

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 181

`(blank)`

Blank line used to separate nearby statements.
### Line 182

`assert evidence.is_correct is False`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 183

`assert evidence.evaluation_details["match"] is False`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 184

`assert evidence.evaluation_details["predicted_state"] == "01"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 185

`assert evidence.evaluation_details["most_likely_state"] == "10"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 186

`(blank)`

Blank line used to separate nearby statements.
### Line 188

`def test_conceptual_response_evaluation():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 189

`ev_correct = evaluate_conceptual_response(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 190

`learner_id="u1",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 191

`activity_id="act_measurement_prob_diagnostic",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 192

`concept_id="quantum.measurement",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 193

`selected_option="b",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 194

`expected_option="B",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 195

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 196

`assert ev_correct.is_correct is True`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 197

`assert ev_correct.learner_response == "B"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 198

`(blank)`

Blank line used to separate nearby statements.
### Line 199

`ev_wrong = evaluate_conceptual_response(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 200

`learner_id="u1",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 201

`activity_id="act_measurement_prob_diagnostic",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 202

`concept_id="quantum.measurement",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 203

`selected_option="A",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 204

`expected_option="B",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 205

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 206

`assert ev_wrong.is_correct is False`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 207

`(blank)`

Blank line used to separate nearby statements.
### Line 209

`def test_single_error_does_not_infer_strong_gap():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 210

`model = LearnerModel()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 211

`state = LearnerState(user_id="u1")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 212

`mock_sim = {"most_likely_state": "10", "target_probability": 0.93}`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 213

`(blank)`

Blank line used to separate nearby statements.
### Line 214

`# Attempt 1: Incorrect`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 215

`ev1 = evaluate_quantum_prediction(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 216

`learner_id="u1",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 217

`activity_id="act_grover_2q_predict",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 218

`concept_id="grover.search_problem",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 219

`prediction="01",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 220

`simulation_result=mock_sim,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 221

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 222

`(blank)`

Blank line used to separate nearby statements.
### Line 223

`decision = model.record_evidence(ev1, state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 224

`(blank)`

Blank line used to separate nearby statements.
### Line 225

`# 1. Action should gather more evidence, not jump to remediation immediately`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 226

`assert decision.action == "gather_evidence"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 227

`assert decision.target == "act_grover_2q_predict"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 228

`(blank)`

Blank line used to separate nearby statements.
### Line 229

`# 2. Confidence in conceptual gap is low (0.35) and status is "observing"`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 230

`inference = state.gap_inferences.get("grover.search_problem")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 231

`assert inference is not None`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 232

`assert inference["confidence"] == 0.35`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 233

`assert inference["status"] == "observing"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 234

`assert "preliminary observation" in inference["description"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 235

`(blank)`

Blank line used to separate nearby statements.
### Line 237

`def test_repeated_errors_increase_confidence_and_trigger_remediation():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 238

`model = LearnerModel()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 239

`state = LearnerState(user_id="u1")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 240

`mock_sim = {"most_likely_state": "10", "target_probability": 0.93}`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 241

`(blank)`

Blank line used to separate nearby statements.
### Line 242

`# Attempt 1: Incorrect`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 243

`ev1 = evaluate_quantum_prediction(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 244

`learner_id="u1",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 245

`activity_id="act_grover_2q_predict",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 246

`concept_id="grover.search_problem",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 247

`prediction="01",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 248

`simulation_result=mock_sim,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 249

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 250

`model.record_evidence(ev1, state)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 251

`(blank)`

Blank line used to separate nearby statements.
### Line 252

`# Attempt 2: Incorrect again on same activity`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 253

`ev2 = evaluate_quantum_prediction(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 254

`learner_id="u1",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 255

`activity_id="act_grover_2q_predict",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 256

`concept_id="grover.search_problem",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 257

`prediction="00",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 258

`simulation_result=mock_sim,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 259

`attempt_number=2,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 260

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 261

`decision = model.record_evidence(ev2, state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 262

`(blank)`

Blank line used to separate nearby statements.
### Line 263

`# Action should now be targeted remediation pointing to measurement diagnostic`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 264

`assert decision.action == "targeted_remediation"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 265

`assert decision.target == "act_measurement_prob_diagnostic"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 266

`(blank)`

Blank line used to separate nearby statements.
### Line 267

`# Confidence should be elevated (0.90) and status "remediation_needed"`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 268

`inference = state.gap_inferences.get("grover.search_problem")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 269

`assert inference["confidence"] == 0.90`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 270

`assert inference["status"] == "remediation_needed"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 271

`assert "repeated incorrect attempts" in inference["description"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 272

`(blank)`

Blank line used to separate nearby statements.
### Line 274

`def test_post_intervention_improvement():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 275

`model = LearnerModel()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 276

`state = LearnerState(user_id="u1")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 277

`mock_sim = {"most_likely_state": "10", "target_probability": 0.93}`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 278

`(blank)`

Blank line used to separate nearby statements.
### Line 279

`# First attempt: incorrect`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 280

`ev1 = evaluate_quantum_prediction(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 281

`learner_id="u1",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 282

`activity_id="act_grover_2q_predict",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 283

`concept_id="grover.search_problem",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 284

`prediction="01",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 285

`simulation_result=mock_sim,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 286

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 287

`model.record_evidence(ev1, state)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 288

`(blank)`

Blank line used to separate nearby statements.
### Line 289

`# Second attempt after intervention: correct`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 290

`ev2 = evaluate_quantum_prediction(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 291

`learner_id="u1",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 292

`activity_id="act_grover_2q_predict",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 293

`concept_id="grover.search_problem",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 294

`prediction="10",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 295

`simulation_result=mock_sim,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 296

`attempt_number=2,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 297

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 298

`decision = model.record_evidence(ev2, state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 299

`(blank)`

Blank line used to separate nearby statements.
### Line 300

`assert decision.action == "advance"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 301

`assert decision.target == "act_grover_iteration_reasoning"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 302

`(blank)`

Blank line used to separate nearby statements.
### Line 303

`inference = state.gap_inferences.get("grover.search_problem")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 304

`assert inference["status"] == "improving"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 305

`assert inference["confidence"] == 0.15`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 306

`assert "post-intervention improvement" in inference["description"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 307

`(blank)`

Blank line used to separate nearby statements.
### Line 309

`def test_invalid_simulation_result_type_rejected():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 310

`with pytest.raises(TypeError):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 311

`evaluate_quantum_prediction(`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 312

`learner_id="u1",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 313

`activity_id="act_grover_2q_predict",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 314

`concept_id="grover.search_problem",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 315

`prediction="10",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 316

`simulation_result="not_a_dictionary",  # invalid`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 317

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.

## Nearby Files

[tests/adaptive/__init__.py](__init__.py.md), [tests/adaptive/test_activities.py](test_activities.py.md), [tests/adaptive/test_diagnostics.py](test_diagnostics.py.md), [tests/adaptive/test_evidence_progression.py](test_evidence_progression.py.md), [tests/adaptive/test_mastery.py](test_mastery.py.md), [tests/adaptive/test_models.py](test_models.py.md), [tests/adaptive/test_pass4_evidence_trace.py](test_pass4_evidence_trace.py.md), [tests/adaptive/test_persistence_hardening.py](test_persistence_hardening.py.md)
