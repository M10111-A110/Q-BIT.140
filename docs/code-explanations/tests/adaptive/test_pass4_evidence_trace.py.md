# Explanation: `tests/adaptive/test_pass4_evidence_trace.py`

## Purpose

This page explains the meaningful behavior in `tests/adaptive/test_pass4_evidence_trace.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
import json
import pytest
from fastapi.testclient import TestClient

from backend.adaptive import (
    AdaptiveRecommendation,
    GapInference,
    InMemoryLearnerRepository,
    LearnerEvidence,
    LearnerModel,
    LearnerState,
    evaluate_conceptual_response,
    evaluate_quantum_prediction,
)
from backend.ai import MockLLMProvider, build_experiment_explanation_prompt
from backend.api.dependencies import (
    reset_dependencies,
    set_learner_repository,
    set_llm_provider,
)
from backend.api.main import app


@pytest.fixture(autouse=True)
def setup_clean_env():
    """Ensure every test runs in an isolated environment."""
    repo = InMemoryLearnerRepository()
    set_learner_repository(repo)
    set_llm_provider(MockLLMProvider())
    yield
    reset_dependencies()


# ===========================================================================
# 1. EVIDENCE SEMANTICS & JSON SERIALIZATION
# ===========================================================================

def test_evidence_id_generation_and_uniqueness():
    """Requirement 1 & 2: Evidence IDs are generated, unique per attempt, and JSON-serializable."""
    ev1 = evaluate_quantum_prediction(
        learner_id="u_trace_1",
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="01",
        simulation_result={"target_state": "10", "most_likely_state": "10", "target_probability": 0.938},
        attempt_number=1,
    )
    assert ev1.evidence_id.startswith("ev_act_grover_2q_predict_att1")
    assert ev1.evidence_type == "quantum_prediction"
    assert ev1.evidence_source == "learner_and_quantum_execution"

    ev2 = evaluate_quantum_prediction(
        learner_id="u_trace_1",
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="00",
        simulation_result={"target_state": "10", "most_likely_state": "10", "target_probability": 0.938},
        attempt_number=2,
    )
    assert ev2.evidence_id.startswith("ev_act_grover_2q_predict_att2")
    assert ev1.evidence_id != ev2.evidence_id

    # Verify JSON serialization
    serialized = json.dumps(ev1.to_dict())
    reconstructed = json.loads(serialized)
    assert reconstructed["evidence_id"] == ev1.evidence_id
    assert reconstructed["evidence_type"] == "quantum_prediction"


def test_evidence_backward_compatibility():
    """Requirement 3: Existing persisted evidence without evidence_id is handled safely."""
    legacy_dict = {
        "learner_id": "u_legacy",
        "activity_id": "act_grover_2q_predict",
        "concept_id": "grover.search_problem",
        "learner_response": "10",
        "is_correct": True,
        "attempt_number": 1,
    }
    reconstructed = LearnerEvidence.from_dict(legacy_dict)
    assert reconstructed.evidence_id != ""
    assert reconstructed.evidence_type == "derived_evaluation"
    assert reconstructed.evidence_source == "learner"


# ===========================================================================
# 2. EVIDENCE SUFFICIENCY & DECISION TRACE (4 CORE SCENARIOS)
# ===========================================================================

def test_single_incorrect_attempt_trace():
    """Requirement 4: Single incorrect attempt -> insufficient evidence, gather_evidence."""
    model = LearnerModel()
    state = LearnerState(user_id="u_trace_a")

    ev = evaluate_quantum_prediction(
        learner_id="u_trace_a",
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="01",
        simulation_result={"target_state": "10", "most_likely_state": "10", "target_probability": 0.938},
        attempt_number=1,
    )
    rec = model.record_evidence(ev, state)

    # 1. Gap Inference audit
    inf = state.gap_inferences["grover.search_problem"]
    assert inf["evidence_sufficiency"] == "insufficient"
    assert "preliminary_difficulty_observation" in inf["hypothesis"]
    assert inf["supporting_evidence_ids"] == [ev.evidence_id]
    assert inf["confidence"] == 0.35

    # 2. Adaptive Recommendation Trace audit
    assert rec.action == "gather_evidence"
    assert rec.trigger == "single_prediction_mismatch"
    assert rec.evidence_sufficiency == "insufficient"
    assert rec.supporting_evidence_ids == [ev.evidence_id]
    assert rec.decision_id.startswith("dec_grover_search_problem_gather_evidence")


def test_repeated_incorrect_attempt_trace():
    """Requirement 5: Repeated incorrect attempts -> sufficient for targeted inference, targeted_remediation."""
    model = LearnerModel()
    state = LearnerState(user_id="u_trace_b")

    ev1 = evaluate_quantum_prediction(
        learner_id="u_trace_b",
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="01",
        simulation_result={"target_state": "10", "most_likely_state": "10", "target_probability": 0.938},
        attempt_number=1,
    )
    model.record_evidence(ev1, state)

    ev2 = evaluate_quantum_prediction(
        learner_id="u_trace_b",
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="00",
        simulation_result={"target_state": "10", "most_likely_state": "10", "target_probability": 0.938},
        attempt_number=2,
    )
    rec = model.record_evidence(ev2, state)

    # 1. Gap Inference audit
    inf = state.gap_inferences["grover.search_problem"]
    assert inf["evidence_sufficiency"] == "sufficient_for_targeted_inference"
    assert "possible_grover_search_problem_difficulty" in inf["hypothesis"]
    assert inf["supporting_evidence_ids"] == [ev1.evidence_id, ev2.evidence_id]
    assert inf["confidence"] == 0.90

    # 2. Adaptive Recommendation Trace audit
    assert rec.action == "targeted_remediation"
    assert rec.trigger == "repeated_prediction_error"
    assert rec.evidence_sufficiency == "sufficient_for_targeted_inference"
    assert rec.supporting_evidence_ids == [ev1.evidence_id, ev2.evidence_id]


def test_remediation_and_retry_recovery_trace():
    """Requirement 6: Error -> Remediation -> Retry Success -> post_intervention_improvement, advance."""
    model = LearnerModel()
    state = LearnerState(user_id="u_trace_c")

    # 1. Failed prediction on Grover
    ev1 = evaluate_quantum_prediction(
        learner_id="u_trace_c",
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="01",
        simulation_result={"target_state": "10", "most_likely_state": "10", "target_probability": 0.938},
        attempt_number=1,
    )
    model.record_evidence(ev1, state)

    # 2. Successful retry on Grover
    ev2 = evaluate_quantum_prediction(
        learner_id="u_trace_c",
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="10",
        simulation_result={"target_state": "10", "most_likely_state": "10", "target_probability": 0.938},
        attempt_number=2,
    )
    rec = model.record_evidence(ev2, state)

    # Gap Inference audit
    inf = state.gap_inferences["grover.search_problem"]
    assert inf["evidence_sufficiency"] == "sufficient_for_improvement_observation"
    assert "post_intervention_improvement" in inf["hypothesis"]
    assert inf["supporting_evidence_ids"] == [ev1.evidence_id, ev2.evidence_id]
    assert inf["confidence"] == 0.15

    # Adaptive Recommendation Trace audit
    assert rec.action == "advance"
    assert rec.trigger == "post_intervention_recovery"
    assert rec.evidence_sufficiency == "sufficient_for_improvement_observation"
    assert rec.supporting_evidence_ids == [ev1.evidence_id, ev2.evidence_id]


def test_stable_mastery_trace():
    """Requirement 7: Consecutive successes -> sufficient for mastery, stable_mastery, advance."""
    model = LearnerModel()
    state = LearnerState(user_id="u_trace_d")

    ev1 = evaluate_conceptual_response(
        learner_id="u_trace_d",
        activity_id="act_grover_iteration_reasoning",
        concept_id="grover.amplitude_amplification",
        selected_option="B",
        expected_option="B",
        attempt_number=1,
    )
    model.record_evidence(ev1, state)

    ev2 = evaluate_conceptual_response(
        learner_id="u_trace_d",
        activity_id="act_grover_iteration_reasoning",
        concept_id="grover.amplitude_amplification",
        selected_option="B",
        expected_option="B",
        attempt_number=2,
    )
    rec = model.record_evidence(ev2, state)

    # Gap Inference audit
    inf = state.gap_inferences["grover.amplitude_amplification"]
    assert inf["evidence_sufficiency"] == "sufficient_for_mastery"
    assert "consistent_mastery" in inf["hypothesis"]
    assert inf["supporting_evidence_ids"] == [ev1.evidence_id, ev2.evidence_id]
    assert inf["confidence"] == 0.0

    # Recommendation Trace audit
    assert rec.action == "advance"
    assert rec.trigger == "consecutive_mastery_success"
    assert rec.evidence_sufficiency == "sufficient_for_mastery"
    assert rec.supporting_evidence_ids == [ev1.evidence_id, ev2.evidence_id]


# ===========================================================================
# 3. ADVERSARIAL TRACE ISOLATION & API BOUNDARY
# ===========================================================================

def test_adversarial_irrelevant_evidence_isolation():
    """
    Requirement 13: Irrelevant historical evidence from another concept/activity
    is NEVER cited as supporting evidence for a decision on a different concept.
    """
    model = LearnerModel()
    state = LearnerState(user_id="u_trace_adv")

    # 1. Unrelated activity on Measurement probability
    ev_unrelated = evaluate_conceptual_response(
        learner_id="u_trace_adv",
        activity_id="act_measurement_prob_diagnostic",
        concept_id="quantum.measurement",
        selected_option="A",
        expected_option="B",
        attempt_number=1,
    )
    model.record_evidence(ev_unrelated, state)

    # 2. Activity on Grover Search Problem
    ev_grover = evaluate_quantum_prediction(
        learner_id="u_trace_adv",
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="01",
        simulation_result={"target_state": "10", "most_likely_state": "10", "target_probability": 0.938},
        attempt_number=1,
    )
    rec = model.record_evidence(ev_grover, state)

    # Ensure supporting_evidence_ids only contains Grover evidence, NOT the measurement evidence
    assert ev_unrelated.evidence_id not in rec.supporting_evidence_ids
    assert rec.supporting_evidence_ids == [ev_grover.evidence_id]


def test_api_submission_exposes_trace_contract():
    """Requirement 10: POST /api/activity/{id}/submit cleanly exposes trace fields."""
    client = TestClient(app)
    res = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_api_trace", "response": "01"},
    )
    assert res.status_code == 200
    data = res.json()

    # Evidence audit
    ev = data["evidence"]
    assert "evidence_id" in ev
    assert ev["evidence_type"] == "quantum_prediction"
    assert ev["evidence_source"] == "learner_and_quantum_execution"

    # Decision trace audit
    dec = data["adaptive_decision"]
    assert "decision_id" in dec
    assert dec["action"] == "gather_evidence"
    assert dec["trigger"] == "single_prediction_mismatch"
    assert dec["evidence_sufficiency"] == "insufficient"
    assert dec["supporting_evidence_ids"] == [ev["evidence_id"]]

    # Pure JSON verification
    json.dumps(data)


def test_m5_prompt_and_explanation_receives_trace():
    """Requirement 11: M5 prompt includes decision trace and MockLLMProvider outputs trace."""
    client = TestClient(app)
    sub_res = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_m5_trace", "response": "01"},
    )
    sub_data = sub_res.json()

    # Request AI explanation
    ai_res = client.post(
        "/api/ai/explain_experiment",
        json={
            "learner_response": sub_data["learner_response"],
            "verified_result": sub_data["verified_result"],
            "evidence": sub_data["evidence"],
            "adaptive_decision": sub_data["adaptive_decision"],
        },
    )
    assert ai_res.status_code == 200
    ai_data = ai_res.json()
    explanation = ai_data["explanation"]

    # Verify decision trace is referenced in explanation
    assert "Evidence & Decision Trace" in explanation
    assert sub_data["evidence"]["evidence_id"] in explanation
    assert "insufficient" in explanation
    assert "single_prediction_mismatch" in explanation

```

## Line Notes

### Line 1

`import json`

Imports a dependency or project symbol so later code can use it by name.
### Line 2

`import pytest`

Imports a dependency or project symbol so later code can use it by name.
### Line 3

`from fastapi.testclient import TestClient`

Imports a dependency or project symbol so later code can use it by name.
### Line 4

`(blank)`

Blank line used to separate nearby statements.
### Line 5

`from backend.adaptive import (`

Imports a dependency or project symbol so later code can use it by name.
### Line 6

`AdaptiveRecommendation,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 7

`GapInference,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 8

`InMemoryLearnerRepository,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 9

`LearnerEvidence,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 10

`LearnerModel,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 11

`LearnerState,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 12

`evaluate_conceptual_response,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 13

`evaluate_quantum_prediction,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 14

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 15

`from backend.ai import MockLLMProvider, build_experiment_explanation_prompt`

Imports a dependency or project symbol so later code can use it by name.
### Line 16

`from backend.api.dependencies import (`

Imports a dependency or project symbol so later code can use it by name.
### Line 17

`reset_dependencies,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 18

`set_learner_repository,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 19

`set_llm_provider,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 20

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 21

`from backend.api.main import app`

Imports a dependency or project symbol so later code can use it by name.
### Line 22

`(blank)`

Blank line used to separate nearby statements.
### Line 24

`@pytest.fixture(autouse=True)`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 25

`def setup_clean_env():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 26

`"""Ensure every test runs in an isolated environment."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 27

`repo = InMemoryLearnerRepository()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 28

`set_learner_repository(repo)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 29

`set_llm_provider(MockLLMProvider())`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 30

`yield`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 31

`reset_dependencies()`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 32

`(blank)`

Blank line used to separate nearby statements.
### Line 34

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 35

`# 1. EVIDENCE SEMANTICS & JSON SERIALIZATION`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 36

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 37

`(blank)`

Blank line used to separate nearby statements.
### Line 38

`def test_evidence_id_generation_and_uniqueness():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 39

`"""Requirement 1 & 2: Evidence IDs are generated, unique per attempt, and JSON-serializable."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 40

`ev1 = evaluate_quantum_prediction(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 41

`learner_id="u_trace_1",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 42

`activity_id="act_grover_2q_predict",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 43

`concept_id="grover.search_problem",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 44

`prediction="01",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 45

`simulation_result={"target_state": "10", "most_likely_state": "10", "target_probability": 0.938},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 46

`attempt_number=1,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 47

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 48

`assert ev1.evidence_id.startswith("ev_act_grover_2q_predict_att1")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 49

`assert ev1.evidence_type == "quantum_prediction"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 50

`assert ev1.evidence_source == "learner_and_quantum_execution"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 51

`(blank)`

Blank line used to separate nearby statements.
### Line 52

`ev2 = evaluate_quantum_prediction(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 53

`learner_id="u_trace_1",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 54

`activity_id="act_grover_2q_predict",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 55

`concept_id="grover.search_problem",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 56

`prediction="00",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 57

`simulation_result={"target_state": "10", "most_likely_state": "10", "target_probability": 0.938},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 58

`attempt_number=2,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 59

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 60

`assert ev2.evidence_id.startswith("ev_act_grover_2q_predict_att2")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 61

`assert ev1.evidence_id != ev2.evidence_id`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 62

`(blank)`

Blank line used to separate nearby statements.
### Line 63

`# Verify JSON serialization`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 64

`serialized = json.dumps(ev1.to_dict())`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 65

`reconstructed = json.loads(serialized)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 66

`assert reconstructed["evidence_id"] == ev1.evidence_id`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 67

`assert reconstructed["evidence_type"] == "quantum_prediction"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 68

`(blank)`

Blank line used to separate nearby statements.
### Line 70

`def test_evidence_backward_compatibility():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 71

`"""Requirement 3: Existing persisted evidence without evidence_id is handled safely."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 72

`legacy_dict = {`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 73

`"learner_id": "u_legacy",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 74

`"activity_id": "act_grover_2q_predict",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 75

`"concept_id": "grover.search_problem",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 76

`"learner_response": "10",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 77

`"is_correct": True,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 78

`"attempt_number": 1,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 79

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 80

`reconstructed = LearnerEvidence.from_dict(legacy_dict)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 81

`assert reconstructed.evidence_id != ""`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 82

`assert reconstructed.evidence_type == "derived_evaluation"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 83

`assert reconstructed.evidence_source == "learner"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 84

`(blank)`

Blank line used to separate nearby statements.
### Line 86

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 87

`# 2. EVIDENCE SUFFICIENCY & DECISION TRACE (4 CORE SCENARIOS)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 88

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 89

`(blank)`

Blank line used to separate nearby statements.
### Line 90

`def test_single_incorrect_attempt_trace():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 91

`"""Requirement 4: Single incorrect attempt -> insufficient evidence, gather_evidence."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 92

`model = LearnerModel()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 93

`state = LearnerState(user_id="u_trace_a")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 94

`(blank)`

Blank line used to separate nearby statements.
### Line 95

`ev = evaluate_quantum_prediction(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 96

`learner_id="u_trace_a",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 97

`activity_id="act_grover_2q_predict",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 98

`concept_id="grover.search_problem",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 99

`prediction="01",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 100

`simulation_result={"target_state": "10", "most_likely_state": "10", "target_probability": 0.938},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 101

`attempt_number=1,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 102

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 103

`rec = model.record_evidence(ev, state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 104

`(blank)`

Blank line used to separate nearby statements.
### Line 105

`# 1. Gap Inference audit`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 106

`inf = state.gap_inferences["grover.search_problem"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 107

`assert inf["evidence_sufficiency"] == "insufficient"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 108

`assert "preliminary_difficulty_observation" in inf["hypothesis"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 109

`assert inf["supporting_evidence_ids"] == [ev.evidence_id]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 110

`assert inf["confidence"] == 0.35`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 111

`(blank)`

Blank line used to separate nearby statements.
### Line 112

`# 2. Adaptive Recommendation Trace audit`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 113

`assert rec.action == "gather_evidence"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 114

`assert rec.trigger == "single_prediction_mismatch"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 115

`assert rec.evidence_sufficiency == "insufficient"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 116

`assert rec.supporting_evidence_ids == [ev.evidence_id]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 117

`assert rec.decision_id.startswith("dec_grover_search_problem_gather_evidence")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 118

`(blank)`

Blank line used to separate nearby statements.
### Line 120

`def test_repeated_incorrect_attempt_trace():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 121

`"""Requirement 5: Repeated incorrect attempts -> sufficient for targeted inference, targeted_remediation."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 122

`model = LearnerModel()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 123

`state = LearnerState(user_id="u_trace_b")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 124

`(blank)`

Blank line used to separate nearby statements.
### Line 125

`ev1 = evaluate_quantum_prediction(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 126

`learner_id="u_trace_b",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 127

`activity_id="act_grover_2q_predict",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 128

`concept_id="grover.search_problem",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 129

`prediction="01",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 130

`simulation_result={"target_state": "10", "most_likely_state": "10", "target_probability": 0.938},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 131

`attempt_number=1,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 132

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 133

`model.record_evidence(ev1, state)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 134

`(blank)`

Blank line used to separate nearby statements.
### Line 135

`ev2 = evaluate_quantum_prediction(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 136

`learner_id="u_trace_b",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 137

`activity_id="act_grover_2q_predict",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 138

`concept_id="grover.search_problem",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 139

`prediction="00",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 140

`simulation_result={"target_state": "10", "most_likely_state": "10", "target_probability": 0.938},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 141

`attempt_number=2,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 142

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 143

`rec = model.record_evidence(ev2, state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 144

`(blank)`

Blank line used to separate nearby statements.
### Line 145

`# 1. Gap Inference audit`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 146

`inf = state.gap_inferences["grover.search_problem"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 147

`assert inf["evidence_sufficiency"] == "sufficient_for_targeted_inference"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 148

`assert "possible_grover_search_problem_difficulty" in inf["hypothesis"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 149

`assert inf["supporting_evidence_ids"] == [ev1.evidence_id, ev2.evidence_id]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 150

`assert inf["confidence"] == 0.90`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 151

`(blank)`

Blank line used to separate nearby statements.
### Line 152

`# 2. Adaptive Recommendation Trace audit`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 153

`assert rec.action == "targeted_remediation"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 154

`assert rec.trigger == "repeated_prediction_error"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 155

`assert rec.evidence_sufficiency == "sufficient_for_targeted_inference"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 156

`assert rec.supporting_evidence_ids == [ev1.evidence_id, ev2.evidence_id]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 157

`(blank)`

Blank line used to separate nearby statements.
### Line 159

`def test_remediation_and_retry_recovery_trace():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 160

`"""Requirement 6: Error -> Remediation -> Retry Success -> post_intervention_improvement, advance."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 161

`model = LearnerModel()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 162

`state = LearnerState(user_id="u_trace_c")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 163

`(blank)`

Blank line used to separate nearby statements.
### Line 164

`# 1. Failed prediction on Grover`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 165

`ev1 = evaluate_quantum_prediction(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 166

`learner_id="u_trace_c",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 167

`activity_id="act_grover_2q_predict",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 168

`concept_id="grover.search_problem",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 169

`prediction="01",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 170

`simulation_result={"target_state": "10", "most_likely_state": "10", "target_probability": 0.938},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 171

`attempt_number=1,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 172

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 173

`model.record_evidence(ev1, state)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 174

`(blank)`

Blank line used to separate nearby statements.
### Line 175

`# 2. Successful retry on Grover`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 176

`ev2 = evaluate_quantum_prediction(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 177

`learner_id="u_trace_c",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 178

`activity_id="act_grover_2q_predict",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 179

`concept_id="grover.search_problem",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 180

`prediction="10",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 181

`simulation_result={"target_state": "10", "most_likely_state": "10", "target_probability": 0.938},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 182

`attempt_number=2,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 183

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 184

`rec = model.record_evidence(ev2, state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 185

`(blank)`

Blank line used to separate nearby statements.
### Line 186

`# Gap Inference audit`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 187

`inf = state.gap_inferences["grover.search_problem"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 188

`assert inf["evidence_sufficiency"] == "sufficient_for_improvement_observation"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 189

`assert "post_intervention_improvement" in inf["hypothesis"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 190

`assert inf["supporting_evidence_ids"] == [ev1.evidence_id, ev2.evidence_id]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 191

`assert inf["confidence"] == 0.15`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 192

`(blank)`

Blank line used to separate nearby statements.
### Line 193

`# Adaptive Recommendation Trace audit`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 194

`assert rec.action == "advance"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 195

`assert rec.trigger == "post_intervention_recovery"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 196

`assert rec.evidence_sufficiency == "sufficient_for_improvement_observation"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 197

`assert rec.supporting_evidence_ids == [ev1.evidence_id, ev2.evidence_id]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 198

`(blank)`

Blank line used to separate nearby statements.
### Line 200

`def test_stable_mastery_trace():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 201

`"""Requirement 7: Consecutive successes -> sufficient for mastery, stable_mastery, advance."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 202

`model = LearnerModel()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 203

`state = LearnerState(user_id="u_trace_d")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 204

`(blank)`

Blank line used to separate nearby statements.
### Line 205

`ev1 = evaluate_conceptual_response(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 206

`learner_id="u_trace_d",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 207

`activity_id="act_grover_iteration_reasoning",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 208

`concept_id="grover.amplitude_amplification",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 209

`selected_option="B",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 210

`expected_option="B",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 211

`attempt_number=1,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 212

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 213

`model.record_evidence(ev1, state)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 214

`(blank)`

Blank line used to separate nearby statements.
### Line 215

`ev2 = evaluate_conceptual_response(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 216

`learner_id="u_trace_d",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 217

`activity_id="act_grover_iteration_reasoning",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 218

`concept_id="grover.amplitude_amplification",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 219

`selected_option="B",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 220

`expected_option="B",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 221

`attempt_number=2,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 222

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 223

`rec = model.record_evidence(ev2, state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 224

`(blank)`

Blank line used to separate nearby statements.
### Line 225

`# Gap Inference audit`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 226

`inf = state.gap_inferences["grover.amplitude_amplification"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 227

`assert inf["evidence_sufficiency"] == "sufficient_for_mastery"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 228

`assert "consistent_mastery" in inf["hypothesis"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 229

`assert inf["supporting_evidence_ids"] == [ev1.evidence_id, ev2.evidence_id]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 230

`assert inf["confidence"] == 0.0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 231

`(blank)`

Blank line used to separate nearby statements.
### Line 232

`# Recommendation Trace audit`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 233

`assert rec.action == "advance"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 234

`assert rec.trigger == "consecutive_mastery_success"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 235

`assert rec.evidence_sufficiency == "sufficient_for_mastery"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 236

`assert rec.supporting_evidence_ids == [ev1.evidence_id, ev2.evidence_id]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 237

`(blank)`

Blank line used to separate nearby statements.
### Line 239

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 240

`# 3. ADVERSARIAL TRACE ISOLATION & API BOUNDARY`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 241

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 242

`(blank)`

Blank line used to separate nearby statements.
### Line 243

`def test_adversarial_irrelevant_evidence_isolation():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 244

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 245

`Requirement 13: Irrelevant historical evidence from another concept/activity`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 246

`is NEVER cited as supporting evidence for a decision on a different concept.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 247

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 248

`model = LearnerModel()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 249

`state = LearnerState(user_id="u_trace_adv")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 250

`(blank)`

Blank line used to separate nearby statements.
### Line 251

`# 1. Unrelated activity on Measurement probability`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 252

`ev_unrelated = evaluate_conceptual_response(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 253

`learner_id="u_trace_adv",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 254

`activity_id="act_measurement_prob_diagnostic",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 255

`concept_id="quantum.measurement",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 256

`selected_option="A",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 257

`expected_option="B",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 258

`attempt_number=1,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 259

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 260

`model.record_evidence(ev_unrelated, state)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 261

`(blank)`

Blank line used to separate nearby statements.
### Line 262

`# 2. Activity on Grover Search Problem`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 263

`ev_grover = evaluate_quantum_prediction(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 264

`learner_id="u_trace_adv",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 265

`activity_id="act_grover_2q_predict",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 266

`concept_id="grover.search_problem",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 267

`prediction="01",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 268

`simulation_result={"target_state": "10", "most_likely_state": "10", "target_probability": 0.938},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 269

`attempt_number=1,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 270

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 271

`rec = model.record_evidence(ev_grover, state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 272

`(blank)`

Blank line used to separate nearby statements.
### Line 273

`# Ensure supporting_evidence_ids only contains Grover evidence, NOT the measurement evidence`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 274

`assert ev_unrelated.evidence_id not in rec.supporting_evidence_ids`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 275

`assert rec.supporting_evidence_ids == [ev_grover.evidence_id]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 276

`(blank)`

Blank line used to separate nearby statements.
### Line 278

`def test_api_submission_exposes_trace_contract():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 279

`"""Requirement 10: POST /api/activity/{id}/submit cleanly exposes trace fields."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 280

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 281

`res = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 282

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 283

`json={"learner_id": "u_api_trace", "response": "01"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 284

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 285

`assert res.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 286

`data = res.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 287

`(blank)`

Blank line used to separate nearby statements.
### Line 288

`# Evidence audit`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 289

`ev = data["evidence"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 290

`assert "evidence_id" in ev`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 291

`assert ev["evidence_type"] == "quantum_prediction"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 292

`assert ev["evidence_source"] == "learner_and_quantum_execution"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 293

`(blank)`

Blank line used to separate nearby statements.
### Line 294

`# Decision trace audit`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 295

`dec = data["adaptive_decision"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 296

`assert "decision_id" in dec`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 297

`assert dec["action"] == "gather_evidence"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 298

`assert dec["trigger"] == "single_prediction_mismatch"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 299

`assert dec["evidence_sufficiency"] == "insufficient"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 300

`assert dec["supporting_evidence_ids"] == [ev["evidence_id"]]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 301

`(blank)`

Blank line used to separate nearby statements.
### Line 302

`# Pure JSON verification`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 303

`json.dumps(data)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 304

`(blank)`

Blank line used to separate nearby statements.
### Line 306

`def test_m5_prompt_and_explanation_receives_trace():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 307

`"""Requirement 11: M5 prompt includes decision trace and MockLLMProvider outputs trace."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 308

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 309

`sub_res = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 310

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 311

`json={"learner_id": "u_m5_trace", "response": "01"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 312

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 313

`sub_data = sub_res.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 314

`(blank)`

Blank line used to separate nearby statements.
### Line 315

`# Request AI explanation`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 316

`ai_res = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 317

`"/api/ai/explain_experiment",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 318

`json={`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 319

`"learner_response": sub_data["learner_response"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 320

`"verified_result": sub_data["verified_result"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 321

`"evidence": sub_data["evidence"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 322

`"adaptive_decision": sub_data["adaptive_decision"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 323

`},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 324

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 325

`assert ai_res.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 326

`ai_data = ai_res.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 327

`explanation = ai_data["explanation"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 328

`(blank)`

Blank line used to separate nearby statements.
### Line 329

`# Verify decision trace is referenced in explanation`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 330

`assert "Evidence & Decision Trace" in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 331

`assert sub_data["evidence"]["evidence_id"] in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 332

`assert "insufficient" in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 333

`assert "single_prediction_mismatch" in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.

## Nearby Files

[tests/adaptive/__init__.py](__init__.py.md), [tests/adaptive/test_activities.py](test_activities.py.md), [tests/adaptive/test_diagnostics.py](test_diagnostics.py.md), [tests/adaptive/test_evidence.py](test_evidence.py.md), [tests/adaptive/test_evidence_progression.py](test_evidence_progression.py.md), [tests/adaptive/test_mastery.py](test_mastery.py.md), [tests/adaptive/test_models.py](test_models.py.md), [tests/adaptive/test_persistence_hardening.py](test_persistence_hardening.py.md)
