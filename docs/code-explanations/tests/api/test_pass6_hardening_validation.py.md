# Explanation: `tests/api/test_pass6_hardening_validation.py`

## Purpose

This page explains the meaningful behavior in `tests/api/test_pass6_hardening_validation.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
import json
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from backend.adaptive import (
    InMemoryLearnerRepository,
    LearnerEvidence,
    LearnerModel,
    LearnerState,
    StorageUnavailableError,
    evaluate_conceptual_response,
    evaluate_quantum_prediction,
)
from backend.ai import LLMProvider, MockLLMProvider
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
# 1. MULTI-LEARNER & MULTI-ACTIVITY ISOLATION (PHASE 3)
# ===========================================================================

def test_multi_learner_complete_isolation():
    """
    Adversarial isolation test:
      - Learner Alice makes 2 errors -> targeted_remediation.
      - Learner Bob makes 1 correct prediction -> advance.
      - Alice's state must not contain Bob's evidence, and Bob's state must not contain Alice's errors.
    """
    client = TestClient(app)

    # Alice Attempt 1 & 2 (Errors)
    client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "alice", "response": "01"},
    )
    r_alice = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "alice", "response": "00"},
    )
    alice_data = r_alice.json()
    assert alice_data["adaptive_decision"]["action"] == "targeted_remediation"
    assert len(alice_data["learner_state"]["evidence_history"]) == 2

    # Bob Attempt 1 (Correct)
    r_bob = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "bob", "response": "10"},
    )
    bob_data = r_bob.json()
    assert bob_data["adaptive_decision"]["action"] == "advance"
    assert len(bob_data["learner_state"]["evidence_history"]) == 1
    assert bob_data["evidence"]["attempt_number"] == 1
    assert bob_data["evidence"]["is_correct"] is True

    # Alice's supporting evidence only references Alice's IDs
    alice_ev_ids = [e["evidence_id"] for e in alice_data["learner_state"]["evidence_history"]]
    assert alice_data["adaptive_decision"]["supporting_evidence_ids"] == alice_ev_ids
    assert bob_data["evidence"]["evidence_id"] not in alice_data["adaptive_decision"]["supporting_evidence_ids"]


def test_multi_activity_attempt_number_isolation():
    """
    Attempt numbers must be strictly calculated per-activity:
      - Act A: 1, 2
      - Act B: 1
      - Interleaving does not contaminate counts or supporting evidence.
    """
    client = TestClient(app)
    uid = "interleaved_learner"

    # Act A - Att 1
    r_a1 = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": uid, "response": "01"},
    )
    assert r_a1.json()["evidence"]["attempt_number"] == 1

    # Act B - Att 1
    r_b1 = client.post(
        "/api/activity/act_measurement_prob_diagnostic/submit",
        json={"learner_id": uid, "response": "B"},
    )
    assert r_b1.json()["evidence"]["attempt_number"] == 1

    # Act A - Att 2
    r_a2 = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": uid, "response": "10"},
    )
    assert r_a2.json()["evidence"]["attempt_number"] == 2


# ===========================================================================
# 2. DETERMINISM AUDIT (PHASE 6)
# ===========================================================================

def test_m2_decision_trace_pure_determinism():
    """
    Identical evidence sequences submitted to distinct learner instances
    must produce mathematically identical inferences and decisions.
    """
    model = LearnerModel()

    # Sequence for Learner 1
    state1 = LearnerState(user_id="det_user_1")
    ev1_a = evaluate_quantum_prediction("det_user_1", "act_grover_2q_predict", "grover.search_problem", "01", {"target_state": "10", "most_likely_state": "10", "target_probability": 0.938}, 1)
    ev1_b = evaluate_quantum_prediction("det_user_1", "act_grover_2q_predict", "grover.search_problem", "00", {"target_state": "10", "most_likely_state": "10", "target_probability": 0.938}, 2)
    model.record_evidence(ev1_a, state1)
    rec1 = model.record_evidence(ev1_b, state1)

    # Sequence for Learner 2
    state2 = LearnerState(user_id="det_user_2")
    ev2_a = evaluate_quantum_prediction("det_user_2", "act_grover_2q_predict", "grover.search_problem", "01", {"target_state": "10", "most_likely_state": "10", "target_probability": 0.938}, 1)
    ev2_b = evaluate_quantum_prediction("det_user_2", "act_grover_2q_predict", "grover.search_problem", "00", {"target_state": "10", "most_likely_state": "10", "target_probability": 0.938}, 2)
    model.record_evidence(ev2_a, state2)
    rec2 = model.record_evidence(ev2_b, state2)

    # Assert invariant equivalence
    assert rec1.action == rec2.action == "targeted_remediation"
    assert rec1.target == rec2.target == "act_measurement_prob_diagnostic"
    assert rec1.confidence == rec2.confidence == 0.90
    assert rec1.trigger == rec2.trigger == "repeated_prediction_error"
    assert rec1.evidence_sufficiency == rec2.evidence_sufficiency == "sufficient_for_targeted_inference"


# ===========================================================================
# 3. API CONTRACT & FAILURE HARDENING (PHASE 4 & PHASE 7)
# ===========================================================================

def test_api_validation_and_malformed_input_rejection():
    """Verify clean 422/404 responses without internal stack traces."""
    client = TestClient(app)

    # Empty learner_id -> 422
    r_empty_id = client.post("/api/activity/act_grover_2q_predict/submit", json={"learner_id": "", "response": "10"})
    assert r_empty_id.status_code == 422

    # Empty response -> 422
    r_empty_resp = client.post("/api/activity/act_grover_2q_predict/submit", json={"learner_id": "u1", "response": ""})
    assert r_empty_resp.status_code == 422

    # Unknown activity -> 404
    r_unknown = client.post("/api/activity/act_nonexistent_99/submit", json={"learner_id": "u1", "response": "10"})
    assert r_unknown.status_code == 404
    assert "not found" in r_unknown.json()["detail"].lower()


def test_simulation_failure_prevents_evidence_fabrication():
    """M3 failure (HTTP 500) must not record evidence or mutate learner state."""
    client = TestClient(app)
    repo = InMemoryLearnerRepository()
    set_learner_repository(repo)

    with patch("backend.api.routes.activities.run_experiment", side_effect=RuntimeError("Simulator internal error")):
        res = client.post(
            "/api/activity/act_grover_2q_predict/submit",
            json={"learner_id": "u_fail_sim", "response": "10"},
        )
        assert res.status_code == 500
        assert "Quantum execution engine failed" in res.json()["detail"]

    # State must not exist
    assert repo.exists("u_fail_sim") is False


def test_persistence_failure_prevents_false_submission_success():
    """Persistence save failure (HTTP 503) must not return 200 OK."""
    client = TestClient(app)
    class BrokenSaveRepo(InMemoryLearnerRepository):
        def save(self, state):
            raise StorageUnavailableError("Database connection timed out")

    set_learner_repository(BrokenSaveRepo())
    res = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_fail_db", "response": "10"},
    )
    assert res.status_code == 503
    assert "Failed to persist updated learner state" in res.json()["detail"]


def test_ai_explanation_failure_preserves_m2_m3_state():
    """AI explanation failure (HTTP 503) must preserve verified quantum results and M2 recommendations."""
    client = TestClient(app)
    repo = InMemoryLearnerRepository()
    set_learner_repository(repo)

    # 1. Submission succeeds
    sub = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_ai_preserve", "response": "10"},
    )
    assert sub.status_code == 200
    sub_data = sub.json()

    # 2. AI fails
    class FailingProvider(LLMProvider):
        def generate(self, messages, model=None):
            raise RuntimeError("Rate limit exceeded")

    set_llm_provider(FailingProvider())
    ai_res = client.post(
        "/api/ai/explain_experiment",
        json={
            "learner_response": "10",
            "verified_result": sub_data["verified_result"],
            "evidence": sub_data["evidence"],
            "adaptive_decision": sub_data["adaptive_decision"],
        },
    )
    assert ai_res.status_code == 503

    # 3. Client's submission payload remains intact
    assert sub_data["verified_result"]["target_state"] == "10"
    assert sub_data["adaptive_decision"]["action"] == "advance"


# ===========================================================================
# 4. COMPLETE EVALUATOR JOURNEY END-TO-END VALIDATION (PHASE 1)
# ===========================================================================

def test_evaluator_journey_end_to_end_complete_trace():
    """
    End-to-end trace of all 6 evaluator steps through the live FastAPI gateway:
      Step 1: Fresh learner loads activity
      Step 2: Error 1 -> gather_evidence, confidence 0.35, insufficient
      Step 3: Error 2 -> targeted_remediation, confidence 0.90, sufficient_for_targeted_inference
      Step 4: Remediation success -> advance
      Step 5: Retry Grover success -> post_intervention_improvement, advance
      Step 6: AI explanation cites oracle, diffusion, and M2 decision trace
    """
    client = TestClient(app)
    learner_id = "evaluator_master_journey"

    # Step 1: Load activity
    r_act = client.get("/api/activity/act_grover_2q_predict")
    assert r_act.status_code == 200

    # Step 2: Error 1
    r_step2 = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": learner_id, "response": "01"},
    )
    s2 = r_step2.json()
    assert s2["evidence"]["attempt_number"] == 1
    assert s2["adaptive_decision"]["action"] == "gather_evidence"
    assert s2["adaptive_decision"]["evidence_sufficiency"] == "insufficient"
    assert s2["adaptive_decision"]["trigger"] == "single_prediction_mismatch"
    ev1_id = s2["evidence"]["evidence_id"]

    # Step 3: Error 2
    r_step3 = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": learner_id, "response": "00"},
    )
    s3 = r_step3.json()
    assert s3["evidence"]["attempt_number"] == 2
    assert s3["adaptive_decision"]["action"] == "targeted_remediation"
    assert s3["adaptive_decision"]["target"] == "act_measurement_prob_diagnostic"
    assert s3["adaptive_decision"]["evidence_sufficiency"] == "sufficient_for_targeted_inference"
    assert s3["adaptive_decision"]["trigger"] == "repeated_prediction_error"
    ev2_id = s3["evidence"]["evidence_id"]
    assert s3["adaptive_decision"]["supporting_evidence_ids"] == [ev1_id, ev2_id]

    # Step 4: Remediation
    r_step4 = client.post(
        "/api/activity/act_measurement_prob_diagnostic/submit",
        json={"learner_id": learner_id, "response": "B"},
    )
    s4 = r_step4.json()
    assert s4["evidence"]["is_correct"] is True
    assert s4["adaptive_decision"]["action"] == "advance"
    assert s4["adaptive_decision"]["target"] == "act_grover_2q_predict"

    # Step 5: Grover Retry
    r_step5 = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": learner_id, "response": "10"},
    )
    s5 = r_step5.json()
    assert s5["evidence"]["attempt_number"] == 3
    assert s5["evidence"]["is_correct"] is True
    assert s5["adaptive_decision"]["action"] == "advance"
    assert s5["adaptive_decision"]["target"] == "act_grover_iteration_reasoning"
    assert s5["adaptive_decision"]["trigger"] == "post_intervention_recovery"
    assert s5["learner_state"]["gap_inferences"]["grover.search_problem"]["status"] == "improving"

    # Step 6: M5 Explanation
    r_step6 = client.post(
        "/api/ai/explain_experiment",
        json={
            "learner_response": "10",
            "verified_result": s5["verified_result"],
            "evidence": s5["evidence"],
            "adaptive_decision": s5["adaptive_decision"],
        },
    )
    s6 = r_step6.json()
    assert "Evidence Record" in s6["explanation"]
    assert "post_intervention_recovery" in s6["explanation"]
    assert "advance" in s6["explanation"]

```

## Line Notes

### Line 1

`import json`

Imports a dependency or project symbol so later code can use it by name.
### Line 2

`import pytest`

Imports a dependency or project symbol so later code can use it by name.
### Line 3

`from unittest.mock import patch`

Imports a dependency or project symbol so later code can use it by name.
### Line 4

`from fastapi.testclient import TestClient`

Imports a dependency or project symbol so later code can use it by name.
### Line 5

`(blank)`

Blank line used to separate nearby statements.
### Line 6

`from backend.adaptive import (`

Imports a dependency or project symbol so later code can use it by name.
### Line 7

`InMemoryLearnerRepository,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 8

`LearnerEvidence,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 9

`LearnerModel,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 10

`LearnerState,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 11

`StorageUnavailableError,`

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

`from backend.ai import LLMProvider, MockLLMProvider`

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

`# 1. MULTI-LEARNER & MULTI-ACTIVITY ISOLATION (PHASE 3)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 36

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 37

`(blank)`

Blank line used to separate nearby statements.
### Line 38

`def test_multi_learner_complete_isolation():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 39

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 40

`Adversarial isolation test:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 41

`- Learner Alice makes 2 errors -> targeted_remediation.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 42

`- Learner Bob makes 1 correct prediction -> advance.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 43

`- Alice's state must not contain Bob's evidence, and Bob's state must not contain Alice's errors.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 44

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 45

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 46

`(blank)`

Blank line used to separate nearby statements.
### Line 47

`# Alice Attempt 1 & 2 (Errors)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 48

`client.post(`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 49

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 50

`json={"learner_id": "alice", "response": "01"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 51

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 52

`r_alice = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 53

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 54

`json={"learner_id": "alice", "response": "00"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 55

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 56

`alice_data = r_alice.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 57

`assert alice_data["adaptive_decision"]["action"] == "targeted_remediation"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 58

`assert len(alice_data["learner_state"]["evidence_history"]) == 2`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 59

`(blank)`

Blank line used to separate nearby statements.
### Line 60

`# Bob Attempt 1 (Correct)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 61

`r_bob = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 62

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 63

`json={"learner_id": "bob", "response": "10"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 64

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 65

`bob_data = r_bob.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 66

`assert bob_data["adaptive_decision"]["action"] == "advance"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 67

`assert len(bob_data["learner_state"]["evidence_history"]) == 1`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 68

`assert bob_data["evidence"]["attempt_number"] == 1`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 69

`assert bob_data["evidence"]["is_correct"] is True`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 70

`(blank)`

Blank line used to separate nearby statements.
### Line 71

`# Alice's supporting evidence only references Alice's IDs`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 72

`alice_ev_ids = [e["evidence_id"] for e in alice_data["learner_state"]["evidence_history"]]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 73

`assert alice_data["adaptive_decision"]["supporting_evidence_ids"] == alice_ev_ids`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 74

`assert bob_data["evidence"]["evidence_id"] not in alice_data["adaptive_decision"]["supporting_evidence_ids"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 75

`(blank)`

Blank line used to separate nearby statements.
### Line 77

`def test_multi_activity_attempt_number_isolation():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 78

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 79

`Attempt numbers must be strictly calculated per-activity:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 80

`- Act A: 1, 2`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 81

`- Act B: 1`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 82

`- Interleaving does not contaminate counts or supporting evidence.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 83

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 84

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 85

`uid = "interleaved_learner"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 86

`(blank)`

Blank line used to separate nearby statements.
### Line 87

`# Act A - Att 1`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 88

`r_a1 = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 89

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 90

`json={"learner_id": uid, "response": "01"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 91

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 92

`assert r_a1.json()["evidence"]["attempt_number"] == 1`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 93

`(blank)`

Blank line used to separate nearby statements.
### Line 94

`# Act B - Att 1`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 95

`r_b1 = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 96

`"/api/activity/act_measurement_prob_diagnostic/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 97

`json={"learner_id": uid, "response": "B"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 98

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 99

`assert r_b1.json()["evidence"]["attempt_number"] == 1`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 100

`(blank)`

Blank line used to separate nearby statements.
### Line 101

`# Act A - Att 2`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 102

`r_a2 = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 103

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 104

`json={"learner_id": uid, "response": "10"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 105

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 106

`assert r_a2.json()["evidence"]["attempt_number"] == 2`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 107

`(blank)`

Blank line used to separate nearby statements.
### Line 109

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 110

`# 2. DETERMINISM AUDIT (PHASE 6)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 111

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 112

`(blank)`

Blank line used to separate nearby statements.
### Line 113

`def test_m2_decision_trace_pure_determinism():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 114

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 115

`Identical evidence sequences submitted to distinct learner instances`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 116

`must produce mathematically identical inferences and decisions.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 117

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 118

`model = LearnerModel()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 119

`(blank)`

Blank line used to separate nearby statements.
### Line 120

`# Sequence for Learner 1`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 121

`state1 = LearnerState(user_id="det_user_1")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 122

`ev1_a = evaluate_quantum_prediction("det_user_1", "act_grover_2q_predict", "grover.search_problem", "01", {"target_state": "10", "most_likely_state": "10", "target_probability": 0.938}, 1)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 123

`ev1_b = evaluate_quantum_prediction("det_user_1", "act_grover_2q_predict", "grover.search_problem", "00", {"target_state": "10", "most_likely_state": "10", "target_probability": 0.938}, 2)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 124

`model.record_evidence(ev1_a, state1)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 125

`rec1 = model.record_evidence(ev1_b, state1)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 126

`(blank)`

Blank line used to separate nearby statements.
### Line 127

`# Sequence for Learner 2`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 128

`state2 = LearnerState(user_id="det_user_2")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 129

`ev2_a = evaluate_quantum_prediction("det_user_2", "act_grover_2q_predict", "grover.search_problem", "01", {"target_state": "10", "most_likely_state": "10", "target_probability": 0.938}, 1)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 130

`ev2_b = evaluate_quantum_prediction("det_user_2", "act_grover_2q_predict", "grover.search_problem", "00", {"target_state": "10", "most_likely_state": "10", "target_probability": 0.938}, 2)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 131

`model.record_evidence(ev2_a, state2)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 132

`rec2 = model.record_evidence(ev2_b, state2)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 133

`(blank)`

Blank line used to separate nearby statements.
### Line 134

`# Assert invariant equivalence`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 135

`assert rec1.action == rec2.action == "targeted_remediation"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 136

`assert rec1.target == rec2.target == "act_measurement_prob_diagnostic"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 137

`assert rec1.confidence == rec2.confidence == 0.90`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 138

`assert rec1.trigger == rec2.trigger == "repeated_prediction_error"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 139

`assert rec1.evidence_sufficiency == rec2.evidence_sufficiency == "sufficient_for_targeted_inference"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 140

`(blank)`

Blank line used to separate nearby statements.
### Line 142

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 143

`# 3. API CONTRACT & FAILURE HARDENING (PHASE 4 & PHASE 7)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 144

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 145

`(blank)`

Blank line used to separate nearby statements.
### Line 146

`def test_api_validation_and_malformed_input_rejection():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 147

`"""Verify clean 422/404 responses without internal stack traces."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 148

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 149

`(blank)`

Blank line used to separate nearby statements.
### Line 150

`# Empty learner_id -> 422`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 151

`r_empty_id = client.post("/api/activity/act_grover_2q_predict/submit", json={"learner_id": "", "response": "10"})`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 152

`assert r_empty_id.status_code == 422`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 153

`(blank)`

Blank line used to separate nearby statements.
### Line 154

`# Empty response -> 422`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 155

`r_empty_resp = client.post("/api/activity/act_grover_2q_predict/submit", json={"learner_id": "u1", "response": ""})`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 156

`assert r_empty_resp.status_code == 422`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 157

`(blank)`

Blank line used to separate nearby statements.
### Line 158

`# Unknown activity -> 404`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 159

`r_unknown = client.post("/api/activity/act_nonexistent_99/submit", json={"learner_id": "u1", "response": "10"})`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 160

`assert r_unknown.status_code == 404`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 161

`assert "not found" in r_unknown.json()["detail"].lower()`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 162

`(blank)`

Blank line used to separate nearby statements.
### Line 164

`def test_simulation_failure_prevents_evidence_fabrication():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 165

`"""M3 failure (HTTP 500) must not record evidence or mutate learner state."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 166

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 167

`repo = InMemoryLearnerRepository()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 168

`set_learner_repository(repo)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 169

`(blank)`

Blank line used to separate nearby statements.
### Line 170

`with patch("backend.api.routes.activities.run_experiment", side_effect=RuntimeError("Simulator internal error")):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 171

`res = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 172

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 173

`json={"learner_id": "u_fail_sim", "response": "10"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 174

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 175

`assert res.status_code == 500`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 176

`assert "Quantum execution engine failed" in res.json()["detail"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 177

`(blank)`

Blank line used to separate nearby statements.
### Line 178

`# State must not exist`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 179

`assert repo.exists("u_fail_sim") is False`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 180

`(blank)`

Blank line used to separate nearby statements.
### Line 182

`def test_persistence_failure_prevents_false_submission_success():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 183

`"""Persistence save failure (HTTP 503) must not return 200 OK."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 184

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 185

`class BrokenSaveRepo(InMemoryLearnerRepository):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 186

`def save(self, state):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 187

`raise StorageUnavailableError("Database connection timed out")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 188

`(blank)`

Blank line used to separate nearby statements.
### Line 189

`set_learner_repository(BrokenSaveRepo())`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 190

`res = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 191

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 192

`json={"learner_id": "u_fail_db", "response": "10"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 193

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 194

`assert res.status_code == 503`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 195

`assert "Failed to persist updated learner state" in res.json()["detail"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 196

`(blank)`

Blank line used to separate nearby statements.
### Line 198

`def test_ai_explanation_failure_preserves_m2_m3_state():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 199

`"""AI explanation failure (HTTP 503) must preserve verified quantum results and M2 recommendations."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 200

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 201

`repo = InMemoryLearnerRepository()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 202

`set_learner_repository(repo)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 203

`(blank)`

Blank line used to separate nearby statements.
### Line 204

`# 1. Submission succeeds`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 205

`sub = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 206

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 207

`json={"learner_id": "u_ai_preserve", "response": "10"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 208

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 209

`assert sub.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 210

`sub_data = sub.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 211

`(blank)`

Blank line used to separate nearby statements.
### Line 212

`# 2. AI fails`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 213

`class FailingProvider(LLMProvider):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 214

`def generate(self, messages, model=None):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 215

`raise RuntimeError("Rate limit exceeded")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 216

`(blank)`

Blank line used to separate nearby statements.
### Line 217

`set_llm_provider(FailingProvider())`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 218

`ai_res = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 219

`"/api/ai/explain_experiment",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 220

`json={`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 221

`"learner_response": "10",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 222

`"verified_result": sub_data["verified_result"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 223

`"evidence": sub_data["evidence"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 224

`"adaptive_decision": sub_data["adaptive_decision"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 225

`},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 226

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 227

`assert ai_res.status_code == 503`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 228

`(blank)`

Blank line used to separate nearby statements.
### Line 229

`# 3. Client's submission payload remains intact`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 230

`assert sub_data["verified_result"]["target_state"] == "10"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 231

`assert sub_data["adaptive_decision"]["action"] == "advance"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 232

`(blank)`

Blank line used to separate nearby statements.
### Line 234

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 235

`# 4. COMPLETE EVALUATOR JOURNEY END-TO-END VALIDATION (PHASE 1)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 236

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 237

`(blank)`

Blank line used to separate nearby statements.
### Line 238

`def test_evaluator_journey_end_to_end_complete_trace():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 239

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 240

`End-to-end trace of all 6 evaluator steps through the live FastAPI gateway:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 241

`Step 1: Fresh learner loads activity`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 242

`Step 2: Error 1 -> gather_evidence, confidence 0.35, insufficient`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 243

`Step 3: Error 2 -> targeted_remediation, confidence 0.90, sufficient_for_targeted_inference`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 244

`Step 4: Remediation success -> advance`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 245

`Step 5: Retry Grover success -> post_intervention_improvement, advance`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 246

`Step 6: AI explanation cites oracle, diffusion, and M2 decision trace`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 247

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 248

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 249

`learner_id = "evaluator_master_journey"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 250

`(blank)`

Blank line used to separate nearby statements.
### Line 251

`# Step 1: Load activity`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 252

`r_act = client.get("/api/activity/act_grover_2q_predict")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 253

`assert r_act.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 254

`(blank)`

Blank line used to separate nearby statements.
### Line 255

`# Step 2: Error 1`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 256

`r_step2 = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 257

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 258

`json={"learner_id": learner_id, "response": "01"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 259

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 260

`s2 = r_step2.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 261

`assert s2["evidence"]["attempt_number"] == 1`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 262

`assert s2["adaptive_decision"]["action"] == "gather_evidence"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 263

`assert s2["adaptive_decision"]["evidence_sufficiency"] == "insufficient"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 264

`assert s2["adaptive_decision"]["trigger"] == "single_prediction_mismatch"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 265

`ev1_id = s2["evidence"]["evidence_id"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 266

`(blank)`

Blank line used to separate nearby statements.
### Line 267

`# Step 3: Error 2`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 268

`r_step3 = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 269

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 270

`json={"learner_id": learner_id, "response": "00"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 271

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 272

`s3 = r_step3.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 273

`assert s3["evidence"]["attempt_number"] == 2`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 274

`assert s3["adaptive_decision"]["action"] == "targeted_remediation"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 275

`assert s3["adaptive_decision"]["target"] == "act_measurement_prob_diagnostic"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 276

`assert s3["adaptive_decision"]["evidence_sufficiency"] == "sufficient_for_targeted_inference"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 277

`assert s3["adaptive_decision"]["trigger"] == "repeated_prediction_error"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 278

`ev2_id = s3["evidence"]["evidence_id"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 279

`assert s3["adaptive_decision"]["supporting_evidence_ids"] == [ev1_id, ev2_id]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 280

`(blank)`

Blank line used to separate nearby statements.
### Line 281

`# Step 4: Remediation`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 282

`r_step4 = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 283

`"/api/activity/act_measurement_prob_diagnostic/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 284

`json={"learner_id": learner_id, "response": "B"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 285

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 286

`s4 = r_step4.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 287

`assert s4["evidence"]["is_correct"] is True`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 288

`assert s4["adaptive_decision"]["action"] == "advance"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 289

`assert s4["adaptive_decision"]["target"] == "act_grover_2q_predict"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 290

`(blank)`

Blank line used to separate nearby statements.
### Line 291

`# Step 5: Grover Retry`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 292

`r_step5 = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 293

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 294

`json={"learner_id": learner_id, "response": "10"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 295

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 296

`s5 = r_step5.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 297

`assert s5["evidence"]["attempt_number"] == 3`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 298

`assert s5["evidence"]["is_correct"] is True`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 299

`assert s5["adaptive_decision"]["action"] == "advance"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 300

`assert s5["adaptive_decision"]["target"] == "act_grover_iteration_reasoning"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 301

`assert s5["adaptive_decision"]["trigger"] == "post_intervention_recovery"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 302

`assert s5["learner_state"]["gap_inferences"]["grover.search_problem"]["status"] == "improving"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 303

`(blank)`

Blank line used to separate nearby statements.
### Line 304

`# Step 6: M5 Explanation`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 305

`r_step6 = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 306

`"/api/ai/explain_experiment",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 307

`json={`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 308

`"learner_response": "10",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 309

`"verified_result": s5["verified_result"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 310

`"evidence": s5["evidence"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 311

`"adaptive_decision": s5["adaptive_decision"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 312

`},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 313

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 314

`s6 = r_step6.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 315

`assert "Evidence Record" in s6["explanation"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 316

`assert "post_intervention_recovery" in s6["explanation"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 317

`assert "advance" in s6["explanation"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.

## Nearby Files

[tests/api/__init__.py](__init__.py.md), [tests/api/test_activities.py](test_activities.py.md), [tests/api/test_adaptive_vertical_slice.py](test_adaptive_vertical_slice.py.md), [tests/api/test_ai.py](test_ai.py.md), [tests/api/test_frontend_adapter_and_binding.py](test_frontend_adapter_and_binding.py.md), [tests/api/test_health.py](test_health.py.md), [tests/api/test_json_contracts.py](test_json_contracts.py.md), [tests/api/test_m1_m6_integration.py](test_m1_m6_integration.py.md)
