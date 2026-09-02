# Explanation: `tests/api/test_adaptive_vertical_slice.py`

## Purpose

This page explains the meaningful behavior in `tests/api/test_adaptive_vertical_slice.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
import json
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from backend.adaptive import (
    InMemoryLearnerRepository,
    MVP_ACTIVITIES,
    PersistenceError,
    StorageUnavailableError,
    get_activity,
    list_activities,
    resolve_concept_id,
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
    """Ensure every test runs with an isolated in-memory repository and mock provider."""
    repo = InMemoryLearnerRepository()
    set_learner_repository(repo)
    set_llm_provider(MockLLMProvider())
    yield
    reset_dependencies()


# ===========================================================================
# PHASE 2: CANONICAL MULTI-ATTEMPT LEARNER JOURNEY (CASES A - D)
# ===========================================================================

def test_canonical_learner_journey_full_vertical_slice():
    """
    Execute the complete canonical multi-attempt learner journey through the real HTTP API:
      Case A: Attempt 1 on Grover (Wrong) -> preliminary_observation (confidence 0.35) -> gather_evidence
      Case B: Attempt 2 on Grover (Wrong) -> persistent_difficulty (confidence 0.90) -> targeted_remediation
      Case C: Remediation on Measurement (Correct) -> Retry Grover (Correct) -> improving -> advance
      Case D: Second correct attempt on Grover Reasoning -> stable_mastery -> advance
    """
    client = TestClient(app)
    learner_id = "learner_canonical_journey"

    # -----------------------------------------------------------------------
    # CASE A: First Incorrect Attempt
    # -----------------------------------------------------------------------
    res_a = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": learner_id, "response": "01"},  # Target is "10"
    )
    assert res_a.status_code == 200
    data_a = res_a.json()

    # 1. State preservation
    assert data_a["learner_response"] == "01"
    assert data_a["evidence"]["attempt_number"] == 1
    assert data_a["evidence"]["is_correct"] is False
    assert data_a["evidence"]["concept_id"] == "grover.search_problem"
    assert data_a["verified_result"]["target_state"] == "10"
    assert data_a["verified_result"]["most_likely_state"] == "10"
    assert data_a["verified_result"]["target_probability"] > 0.90
    assert "counts" in data_a["verified_result"]

    # 2. Inferred state (no false certainty)
    inf_a = data_a["learner_state"]["gap_inferences"]["grover.search_problem"]
    assert inf_a["status"] == "observing"
    assert inf_a["trend"] == "preliminary_observation"
    assert inf_a["confidence"] == 0.35
    assert inf_a["supporting_evidence_count"] == 1

    # 3. Adaptive decision
    dec_a = data_a["adaptive_decision"]
    assert dec_a["action"] == "gather_evidence"
    assert dec_a["target"] == "act_grover_2q_predict"
    assert "Initial prediction mismatch" in dec_a["reason"]

    # -----------------------------------------------------------------------
    # CASE B: Second Incorrect Attempt (Same Activity, Same Learner)
    # -----------------------------------------------------------------------
    res_b = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": learner_id, "response": "00"},  # Wrong again
    )
    assert res_b.status_code == 200
    data_b = res_b.json()

    # 1. State accumulation
    assert data_b["evidence"]["attempt_number"] == 2
    assert len(data_b["learner_state"]["evidence_history"]) == 2

    # 2. Inferred state (persistent difficulty with higher confidence)
    inf_b = data_b["learner_state"]["gap_inferences"]["grover.search_problem"]
    assert inf_b["status"] == "remediation_needed"
    assert inf_b["trend"] == "persistent_difficulty"
    assert inf_b["confidence"] == 0.90
    assert inf_b["supporting_evidence_count"] == 2

    # 3. Adaptive decision: Targeted remediation
    dec_b = data_b["adaptive_decision"]
    assert dec_b["action"] == "targeted_remediation"
    assert dec_b["target"] == "act_measurement_prob_diagnostic"

    # -----------------------------------------------------------------------
    # CASE C: Remediation + Post-Intervention Improvement
    # -----------------------------------------------------------------------
    # Step 1: Complete remediation activity
    res_remed = client.post(
        "/api/activity/act_measurement_prob_diagnostic/submit",
        json={"learner_id": learner_id, "response": "B"},  # Correct answer
    )
    assert res_remed.status_code == 200
    data_remed = res_remed.json()
    assert data_remed["evidence"]["attempt_number"] == 1  # 1st attempt on this diagnostic
    assert data_remed["evidence"]["is_correct"] is True
    assert len(data_remed["learner_state"]["evidence_history"]) == 3

    # Step 2: Retry Grover prediction activity -> Succeeds
    res_c = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": learner_id, "response": "10"},  # Correct target prediction
    )
    assert res_c.status_code == 200
    data_c = res_c.json()

    assert data_c["evidence"]["attempt_number"] == 3  # 3rd attempt on Grover
    assert data_c["evidence"]["is_correct"] is True
    assert len(data_c["learner_state"]["evidence_history"]) == 4

    # Trend becomes improving; confidence drops to 0.15
    inf_c = data_c["learner_state"]["gap_inferences"]["grover.search_problem"]
    assert inf_c["status"] == "improving"
    assert inf_c["trend"] == "improving"
    assert inf_c["confidence"] == 0.15

    # Adaptive decision advances
    assert data_c["adaptive_decision"]["action"] == "advance"
    assert data_c["adaptive_decision"]["target"] == "act_grover_iteration_reasoning"

    # -----------------------------------------------------------------------
    # CASE D: Second Consecutive Success on Target Concept -> Stable Mastery
    # -----------------------------------------------------------------------
    res_d1 = client.post(
        "/api/activity/act_grover_iteration_reasoning/submit",
        json={"learner_id": learner_id, "response": "B"},  # Correct
    )
    assert res_d1.status_code == 200

    # Repeat second success on Grover reasoning
    res_d2 = client.post(
        "/api/activity/act_grover_iteration_reasoning/submit",
        json={"learner_id": learner_id, "response": "B"},  # Correct again
    )
    assert res_d2.status_code == 200
    data_d2 = res_d2.json()

    inf_d2 = data_d2["learner_state"]["gap_inferences"]["grover.amplitude_amplification"]
    assert inf_d2["status"] == "mastered"
    assert inf_d2["trend"] == "stable_mastery"
    assert inf_d2["confidence"] == 0.0


# ===========================================================================
# CASE E: CONCEPTUAL DIAGNOSTIC FAILURE & PREREQUISITE ROUTING
# ===========================================================================

def test_conceptual_diagnostic_failure_routes_to_superposition_prerequisite():
    """
    Case E: Submit failed conceptual diagnostic and verify DAG prerequisite routing.
    """
    client = TestClient(app)
    res = client.post(
        "/api/activity/act_measurement_prob_diagnostic/submit",
        json={"learner_id": "u_concept_fail", "response": "A"},  # Wrong option (expected "B")
    )
    assert res.status_code == 200
    data = res.json()

    assert data["activity"]["task_type"] == "conceptual_choice"
    assert data["evidence"]["is_correct"] is False
    assert data["verified_result"] is None  # Pure conceptual choice has no quantum simulation
    assert data["adaptive_decision"]["action"] == "gather_evidence"
    assert data["adaptive_decision"]["target"] == "act_measurement_prob_diagnostic"


# ===========================================================================
# CASE F: PERSISTENCE FAILURE RESILIENCE
# ===========================================================================

def test_persistence_failure_on_get_and_save_returns_503():
    """
    Case F: Injected storage failure returns HTTP 503 and never returns false 200.
    """
    client = TestClient(app)

    # 1. Failure during get()
    class BrokenGetRepo(InMemoryLearnerRepository):
        def get(self, user_id: str):
            raise StorageUnavailableError("Supabase connection timeout")

    set_learner_repository(BrokenGetRepo())
    res_get = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_err", "response": "10"},
    )
    assert res_get.status_code == 503
    assert "Learner state persistence service is currently unavailable" in res_get.json()["detail"]

    # 2. Failure during save()
    class BrokenSaveRepo(InMemoryLearnerRepository):
        def save(self, state):
            raise StorageUnavailableError("Disk quota exceeded")

    set_learner_repository(BrokenSaveRepo())
    res_save = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_err", "response": "10"},
    )
    assert res_save.status_code == 503
    assert "Failed to persist updated learner state" in res_save.json()["detail"]


# ===========================================================================
# CASE G: QUANTUM SIMULATOR ENGINE FAILURE
# ===========================================================================

def test_quantum_engine_failure_returns_500_without_mutating_state():
    """
    Case G: Mocked M3 quantum execution failure returns HTTP 500 without corrupting learner state.
    """
    client = TestClient(app)
    repo = InMemoryLearnerRepository()
    set_learner_repository(repo)

    with patch("backend.api.routes.activities.run_experiment", side_effect=RuntimeError("Qiskit Aer backend error")):
        res = client.post(
            "/api/activity/act_grover_2q_predict/submit",
            json={"learner_id": "u_q_err", "response": "10"},
        )
        assert res.status_code == 500
        assert "Quantum execution engine failed" in res.json()["detail"]

    # Verify no state was created or mutated in the repository
    assert repo.exists("u_q_err") is False


# ===========================================================================
# CASE H: M5 AI GUIDANCE FAILURE RESILIENCE
# ===========================================================================

def test_m5_guidance_failure_does_not_corrupt_persisted_state():
    """
    Case H: AI provider failure during explanation leaves persisted M2/M3 state intact.
    """
    client = TestClient(app)
    repo = InMemoryLearnerRepository()
    set_learner_repository(repo)

    # 1. Normal submission succeeds
    sub_res = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_m5_test", "response": "10"},
    )
    assert sub_res.status_code == 200
    sub_data = sub_res.json()

    # 2. Inject failing LLM provider
    class FailingProvider(LLMProvider):
        def generate(self, messages, model=None):
            raise RuntimeError("LLM provider rate limit")

    set_llm_provider(FailingProvider())

    # 3. Call explanation endpoint -> returns 503
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

    # 4. Verified state in repository is untampered
    state = repo.get("u_m5_test")
    assert len(state.evidence_history) == 1
    assert state.evidence_history[0]["is_correct"] is True


# ===========================================================================
# PHASE 3: ATTEMPT NUMBERING INTEGRITY
# ===========================================================================

def test_attempt_numbering_monotonic_and_isolated_per_activity():
    """
    Phase 3: Verify attempt numbers increment monotonically (1 -> 2 -> 3)
    and do not collide across different activities.
    """
    client = TestClient(app)
    learner_id = "learner_attempt_numbering"

    # Grover Attempt 1
    res1 = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": learner_id, "response": "01"},
    )
    assert res1.json()["evidence"]["attempt_number"] == 1

    # Grover Attempt 2
    res2 = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": learner_id, "response": "00"},
    )
    assert res2.json()["evidence"]["attempt_number"] == 2

    # Measurement Attempt 1 (Different activity starts at 1)
    res_meas1 = client.post(
        "/api/activity/act_measurement_prob_diagnostic/submit",
        json={"learner_id": learner_id, "response": "B"},
    )
    assert res_meas1.json()["evidence"]["attempt_number"] == 1

    # Grover Attempt 3 (Resumes at 3)
    res3 = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": learner_id, "response": "10"},
    )
    assert res3.json()["evidence"]["attempt_number"] == 3


# ===========================================================================
# PHASE 4: ACTIVITY GRAPH & DAG AUDIT
# ===========================================================================

def test_activity_graph_completeness_and_termination():
    """
    Phase 4: Audit bounded MVP activities:
      - All referenced activity IDs and concepts exist
      - No dangling IDs
      - Remediation paths terminate
    """
    activities = list_activities()
    assert len(activities) == 4

    known_activity_ids = set(MVP_ACTIVITIES.keys())

    for act in activities:
        # Check concept resolution
        canonical_concept = resolve_concept_id(act.concept_id)
        assert canonical_concept != ""

        # Check next activity references
        if act.next_activity_id is not None:
            assert act.next_activity_id in known_activity_ids

        # Check remediation references
        if act.remediation_activity_id is not None:
            assert act.remediation_activity_id in known_activity_ids

        # Ensure task type is valid
        assert act.task_type in {"quantum_prediction", "conceptual_choice"}

        # Ensure prompts are non-empty
        assert len(act.prompt) > 20


# ===========================================================================
# PHASE 5 & 8: M3 -> M2 -> API SERIALIZATION INTEGRITY (NO QISKIT OBJECTS)
# ===========================================================================

def test_response_is_strictly_json_serializable_and_contains_no_raw_qiskit_objects():
    """
    Phase 5 & 8: Verify full response contract converts cleanly with json.dumps
    and contains no raw Qiskit objects, non-primitive types, or unhandled objects.
    """
    client = TestClient(app)
    res = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_json_check", "response": "10"},
    )
    assert res.status_code == 200
    data = res.json()

    # Must be valid pure JSON string
    json_str = json.dumps(data)
    parsed = json.loads(json_str)

    # Key fields present
    assert "activity" in parsed
    assert "learner_response" in parsed
    assert "verified_result" in parsed
    assert "evidence" in parsed
    assert "learner_state" in parsed
    assert "adaptive_decision" in parsed

    # Check verified result primitives
    vr = parsed["verified_result"]
    assert isinstance(vr["target_state"], str)
    assert isinstance(vr["most_likely_state"], str)
    assert isinstance(vr["target_probability"], float)
    assert isinstance(vr["counts"], dict)
    assert isinstance(vr["shots"], int)

```

## Line Notes

### Line 1

`import json`

Imports a dependency or project symbol so later code can use it by name.
### Line 2

`import pytest`

Imports a dependency or project symbol so later code can use it by name.
### Line 3

`from unittest.mock import patch, MagicMock`

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

`MVP_ACTIVITIES,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 9

`PersistenceError,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 10

`StorageUnavailableError,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 11

`get_activity,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 12

`list_activities,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 13

`resolve_concept_id,`

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

`"""Ensure every test runs with an isolated in-memory repository and mock provider."""`

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

`# PHASE 2: CANONICAL MULTI-ATTEMPT LEARNER JOURNEY (CASES A - D)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 36

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 37

`(blank)`

Blank line used to separate nearby statements.
### Line 38

`def test_canonical_learner_journey_full_vertical_slice():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 39

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 40

`Execute the complete canonical multi-attempt learner journey through the real HTTP API:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 41

`Case A: Attempt 1 on Grover (Wrong) -> preliminary_observation (confidence 0.35) -> gather_evidence`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 42

`Case B: Attempt 2 on Grover (Wrong) -> persistent_difficulty (confidence 0.90) -> targeted_remediation`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 43

`Case C: Remediation on Measurement (Correct) -> Retry Grover (Correct) -> improving -> advance`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 44

`Case D: Second correct attempt on Grover Reasoning -> stable_mastery -> advance`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 45

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 46

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 47

`learner_id = "learner_canonical_journey"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 48

`(blank)`

Blank line used to separate nearby statements.
### Line 49

`# -----------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 50

`# CASE A: First Incorrect Attempt`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 51

`# -----------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 52

`res_a = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 53

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 54

`json={"learner_id": learner_id, "response": "01"},  # Target is "10"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 55

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 56

`assert res_a.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 57

`data_a = res_a.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 58

`(blank)`

Blank line used to separate nearby statements.
### Line 59

`# 1. State preservation`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 60

`assert data_a["learner_response"] == "01"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 61

`assert data_a["evidence"]["attempt_number"] == 1`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 62

`assert data_a["evidence"]["is_correct"] is False`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 63

`assert data_a["evidence"]["concept_id"] == "grover.search_problem"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 64

`assert data_a["verified_result"]["target_state"] == "10"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 65

`assert data_a["verified_result"]["most_likely_state"] == "10"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 66

`assert data_a["verified_result"]["target_probability"] > 0.90`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 67

`assert "counts" in data_a["verified_result"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 68

`(blank)`

Blank line used to separate nearby statements.
### Line 69

`# 2. Inferred state (no false certainty)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 70

`inf_a = data_a["learner_state"]["gap_inferences"]["grover.search_problem"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 71

`assert inf_a["status"] == "observing"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 72

`assert inf_a["trend"] == "preliminary_observation"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 73

`assert inf_a["confidence"] == 0.35`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 74

`assert inf_a["supporting_evidence_count"] == 1`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 75

`(blank)`

Blank line used to separate nearby statements.
### Line 76

`# 3. Adaptive decision`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 77

`dec_a = data_a["adaptive_decision"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 78

`assert dec_a["action"] == "gather_evidence"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 79

`assert dec_a["target"] == "act_grover_2q_predict"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 80

`assert "Initial prediction mismatch" in dec_a["reason"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 81

`(blank)`

Blank line used to separate nearby statements.
### Line 82

`# -----------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 83

`# CASE B: Second Incorrect Attempt (Same Activity, Same Learner)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 84

`# -----------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 85

`res_b = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 86

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 87

`json={"learner_id": learner_id, "response": "00"},  # Wrong again`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 88

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 89

`assert res_b.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 90

`data_b = res_b.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 91

`(blank)`

Blank line used to separate nearby statements.
### Line 92

`# 1. State accumulation`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 93

`assert data_b["evidence"]["attempt_number"] == 2`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 94

`assert len(data_b["learner_state"]["evidence_history"]) == 2`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 95

`(blank)`

Blank line used to separate nearby statements.
### Line 96

`# 2. Inferred state (persistent difficulty with higher confidence)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 97

`inf_b = data_b["learner_state"]["gap_inferences"]["grover.search_problem"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 98

`assert inf_b["status"] == "remediation_needed"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 99

`assert inf_b["trend"] == "persistent_difficulty"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 100

`assert inf_b["confidence"] == 0.90`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 101

`assert inf_b["supporting_evidence_count"] == 2`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 102

`(blank)`

Blank line used to separate nearby statements.
### Line 103

`# 3. Adaptive decision: Targeted remediation`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 104

`dec_b = data_b["adaptive_decision"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 105

`assert dec_b["action"] == "targeted_remediation"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 106

`assert dec_b["target"] == "act_measurement_prob_diagnostic"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 107

`(blank)`

Blank line used to separate nearby statements.
### Line 108

`# -----------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 109

`# CASE C: Remediation + Post-Intervention Improvement`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 110

`# -----------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 111

`# Step 1: Complete remediation activity`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 112

`res_remed = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 113

`"/api/activity/act_measurement_prob_diagnostic/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 114

`json={"learner_id": learner_id, "response": "B"},  # Correct answer`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 115

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 116

`assert res_remed.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 117

`data_remed = res_remed.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 118

`assert data_remed["evidence"]["attempt_number"] == 1  # 1st attempt on this diagnostic`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 119

`assert data_remed["evidence"]["is_correct"] is True`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 120

`assert len(data_remed["learner_state"]["evidence_history"]) == 3`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 121

`(blank)`

Blank line used to separate nearby statements.
### Line 122

`# Step 2: Retry Grover prediction activity -> Succeeds`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 123

`res_c = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 124

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 125

`json={"learner_id": learner_id, "response": "10"},  # Correct target prediction`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 126

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 127

`assert res_c.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 128

`data_c = res_c.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 129

`(blank)`

Blank line used to separate nearby statements.
### Line 130

`assert data_c["evidence"]["attempt_number"] == 3  # 3rd attempt on Grover`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 131

`assert data_c["evidence"]["is_correct"] is True`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 132

`assert len(data_c["learner_state"]["evidence_history"]) == 4`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 133

`(blank)`

Blank line used to separate nearby statements.
### Line 134

`# Trend becomes improving; confidence drops to 0.15`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 135

`inf_c = data_c["learner_state"]["gap_inferences"]["grover.search_problem"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 136

`assert inf_c["status"] == "improving"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 137

`assert inf_c["trend"] == "improving"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 138

`assert inf_c["confidence"] == 0.15`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 139

`(blank)`

Blank line used to separate nearby statements.
### Line 140

`# Adaptive decision advances`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 141

`assert data_c["adaptive_decision"]["action"] == "advance"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 142

`assert data_c["adaptive_decision"]["target"] == "act_grover_iteration_reasoning"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 143

`(blank)`

Blank line used to separate nearby statements.
### Line 144

`# -----------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 145

`# CASE D: Second Consecutive Success on Target Concept -> Stable Mastery`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 146

`# -----------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 147

`res_d1 = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 148

`"/api/activity/act_grover_iteration_reasoning/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 149

`json={"learner_id": learner_id, "response": "B"},  # Correct`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 150

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 151

`assert res_d1.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 152

`(blank)`

Blank line used to separate nearby statements.
### Line 153

`# Repeat second success on Grover reasoning`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 154

`res_d2 = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 155

`"/api/activity/act_grover_iteration_reasoning/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 156

`json={"learner_id": learner_id, "response": "B"},  # Correct again`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 157

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 158

`assert res_d2.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 159

`data_d2 = res_d2.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 160

`(blank)`

Blank line used to separate nearby statements.
### Line 161

`inf_d2 = data_d2["learner_state"]["gap_inferences"]["grover.amplitude_amplification"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 162

`assert inf_d2["status"] == "mastered"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 163

`assert inf_d2["trend"] == "stable_mastery"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 164

`assert inf_d2["confidence"] == 0.0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 165

`(blank)`

Blank line used to separate nearby statements.
### Line 167

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 168

`# CASE E: CONCEPTUAL DIAGNOSTIC FAILURE & PREREQUISITE ROUTING`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 169

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 170

`(blank)`

Blank line used to separate nearby statements.
### Line 171

`def test_conceptual_diagnostic_failure_routes_to_superposition_prerequisite():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 172

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 173

`Case E: Submit failed conceptual diagnostic and verify DAG prerequisite routing.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 174

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 175

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 176

`res = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 177

`"/api/activity/act_measurement_prob_diagnostic/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 178

`json={"learner_id": "u_concept_fail", "response": "A"},  # Wrong option (expected "B")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 179

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 180

`assert res.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 181

`data = res.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 182

`(blank)`

Blank line used to separate nearby statements.
### Line 183

`assert data["activity"]["task_type"] == "conceptual_choice"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 184

`assert data["evidence"]["is_correct"] is False`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 185

`assert data["verified_result"] is None  # Pure conceptual choice has no quantum simulation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 186

`assert data["adaptive_decision"]["action"] == "gather_evidence"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 187

`assert data["adaptive_decision"]["target"] == "act_measurement_prob_diagnostic"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 188

`(blank)`

Blank line used to separate nearby statements.
### Line 190

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 191

`# CASE F: PERSISTENCE FAILURE RESILIENCE`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 192

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 193

`(blank)`

Blank line used to separate nearby statements.
### Line 194

`def test_persistence_failure_on_get_and_save_returns_503():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 195

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 196

`Case F: Injected storage failure returns HTTP 503 and never returns false 200.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 197

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 198

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 199

`(blank)`

Blank line used to separate nearby statements.
### Line 200

`# 1. Failure during get()`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 201

`class BrokenGetRepo(InMemoryLearnerRepository):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 202

`def get(self, user_id: str):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 203

`raise StorageUnavailableError("Supabase connection timeout")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 204

`(blank)`

Blank line used to separate nearby statements.
### Line 205

`set_learner_repository(BrokenGetRepo())`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 206

`res_get = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 207

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 208

`json={"learner_id": "u_err", "response": "10"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 209

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 210

`assert res_get.status_code == 503`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 211

`assert "Learner state persistence service is currently unavailable" in res_get.json()["detail"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 212

`(blank)`

Blank line used to separate nearby statements.
### Line 213

`# 2. Failure during save()`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 214

`class BrokenSaveRepo(InMemoryLearnerRepository):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 215

`def save(self, state):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 216

`raise StorageUnavailableError("Disk quota exceeded")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 217

`(blank)`

Blank line used to separate nearby statements.
### Line 218

`set_learner_repository(BrokenSaveRepo())`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 219

`res_save = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 220

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 221

`json={"learner_id": "u_err", "response": "10"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 222

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 223

`assert res_save.status_code == 503`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 224

`assert "Failed to persist updated learner state" in res_save.json()["detail"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 225

`(blank)`

Blank line used to separate nearby statements.
### Line 227

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 228

`# CASE G: QUANTUM SIMULATOR ENGINE FAILURE`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 229

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 230

`(blank)`

Blank line used to separate nearby statements.
### Line 231

`def test_quantum_engine_failure_returns_500_without_mutating_state():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 232

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 233

`Case G: Mocked M3 quantum execution failure returns HTTP 500 without corrupting learner state.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 234

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 235

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 236

`repo = InMemoryLearnerRepository()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 237

`set_learner_repository(repo)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 238

`(blank)`

Blank line used to separate nearby statements.
### Line 239

`with patch("backend.api.routes.activities.run_experiment", side_effect=RuntimeError("Qiskit Aer backend error")):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 240

`res = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 241

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 242

`json={"learner_id": "u_q_err", "response": "10"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 243

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 244

`assert res.status_code == 500`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 245

`assert "Quantum execution engine failed" in res.json()["detail"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 246

`(blank)`

Blank line used to separate nearby statements.
### Line 247

`# Verify no state was created or mutated in the repository`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 248

`assert repo.exists("u_q_err") is False`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 249

`(blank)`

Blank line used to separate nearby statements.
### Line 251

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 252

`# CASE H: M5 AI GUIDANCE FAILURE RESILIENCE`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 253

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 254

`(blank)`

Blank line used to separate nearby statements.
### Line 255

`def test_m5_guidance_failure_does_not_corrupt_persisted_state():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 256

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 257

`Case H: AI provider failure during explanation leaves persisted M2/M3 state intact.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 258

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 259

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 260

`repo = InMemoryLearnerRepository()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 261

`set_learner_repository(repo)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 262

`(blank)`

Blank line used to separate nearby statements.
### Line 263

`# 1. Normal submission succeeds`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 264

`sub_res = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 265

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 266

`json={"learner_id": "u_m5_test", "response": "10"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 267

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 268

`assert sub_res.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 269

`sub_data = sub_res.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 270

`(blank)`

Blank line used to separate nearby statements.
### Line 271

`# 2. Inject failing LLM provider`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 272

`class FailingProvider(LLMProvider):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 273

`def generate(self, messages, model=None):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 274

`raise RuntimeError("LLM provider rate limit")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 275

`(blank)`

Blank line used to separate nearby statements.
### Line 276

`set_llm_provider(FailingProvider())`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 277

`(blank)`

Blank line used to separate nearby statements.
### Line 278

`# 3. Call explanation endpoint -> returns 503`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 279

`ai_res = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 280

`"/api/ai/explain_experiment",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 281

`json={`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 282

`"learner_response": "10",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 283

`"verified_result": sub_data["verified_result"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 284

`"evidence": sub_data["evidence"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 285

`"adaptive_decision": sub_data["adaptive_decision"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 286

`},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 287

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 288

`assert ai_res.status_code == 503`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 289

`(blank)`

Blank line used to separate nearby statements.
### Line 290

`# 4. Verified state in repository is untampered`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 291

`state = repo.get("u_m5_test")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 292

`assert len(state.evidence_history) == 1`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 293

`assert state.evidence_history[0]["is_correct"] is True`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 294

`(blank)`

Blank line used to separate nearby statements.
### Line 296

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 297

`# PHASE 3: ATTEMPT NUMBERING INTEGRITY`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 298

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 299

`(blank)`

Blank line used to separate nearby statements.
### Line 300

`def test_attempt_numbering_monotonic_and_isolated_per_activity():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 301

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 302

`Phase 3: Verify attempt numbers increment monotonically (1 -> 2 -> 3)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 303

`and do not collide across different activities.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 304

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 305

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 306

`learner_id = "learner_attempt_numbering"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 307

`(blank)`

Blank line used to separate nearby statements.
### Line 308

`# Grover Attempt 1`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 309

`res1 = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 310

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 311

`json={"learner_id": learner_id, "response": "01"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 312

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 313

`assert res1.json()["evidence"]["attempt_number"] == 1`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 314

`(blank)`

Blank line used to separate nearby statements.
### Line 315

`# Grover Attempt 2`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 316

`res2 = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 317

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 318

`json={"learner_id": learner_id, "response": "00"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 319

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 320

`assert res2.json()["evidence"]["attempt_number"] == 2`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 321

`(blank)`

Blank line used to separate nearby statements.
### Line 322

`# Measurement Attempt 1 (Different activity starts at 1)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 323

`res_meas1 = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 324

`"/api/activity/act_measurement_prob_diagnostic/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 325

`json={"learner_id": learner_id, "response": "B"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 326

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 327

`assert res_meas1.json()["evidence"]["attempt_number"] == 1`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 328

`(blank)`

Blank line used to separate nearby statements.
### Line 329

`# Grover Attempt 3 (Resumes at 3)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 330

`res3 = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 331

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 332

`json={"learner_id": learner_id, "response": "10"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 333

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 334

`assert res3.json()["evidence"]["attempt_number"] == 3`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 335

`(blank)`

Blank line used to separate nearby statements.
### Line 337

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 338

`# PHASE 4: ACTIVITY GRAPH & DAG AUDIT`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 339

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 340

`(blank)`

Blank line used to separate nearby statements.
### Line 341

`def test_activity_graph_completeness_and_termination():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 342

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 343

`Phase 4: Audit bounded MVP activities:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 344

`- All referenced activity IDs and concepts exist`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 345

`- No dangling IDs`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 346

`- Remediation paths terminate`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 347

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 348

`activities = list_activities()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 349

`assert len(activities) == 4`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 350

`(blank)`

Blank line used to separate nearby statements.
### Line 351

`known_activity_ids = set(MVP_ACTIVITIES.keys())`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 352

`(blank)`

Blank line used to separate nearby statements.
### Line 353

`for act in activities:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 354

`# Check concept resolution`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 355

`canonical_concept = resolve_concept_id(act.concept_id)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 356

`assert canonical_concept != ""`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 357

`(blank)`

Blank line used to separate nearby statements.
### Line 358

`# Check next activity references`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 359

`if act.next_activity_id is not None:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 360

`assert act.next_activity_id in known_activity_ids`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 361

`(blank)`

Blank line used to separate nearby statements.
### Line 362

`# Check remediation references`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 363

`if act.remediation_activity_id is not None:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 364

`assert act.remediation_activity_id in known_activity_ids`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 365

`(blank)`

Blank line used to separate nearby statements.
### Line 366

`# Ensure task type is valid`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 367

`assert act.task_type in {"quantum_prediction", "conceptual_choice"}`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 368

`(blank)`

Blank line used to separate nearby statements.
### Line 369

`# Ensure prompts are non-empty`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 370

`assert len(act.prompt) > 20`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 371

`(blank)`

Blank line used to separate nearby statements.
### Line 373

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 374

`# PHASE 5 & 8: M3 -> M2 -> API SERIALIZATION INTEGRITY (NO QISKIT OBJECTS)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 375

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 376

`(blank)`

Blank line used to separate nearby statements.
### Line 377

`def test_response_is_strictly_json_serializable_and_contains_no_raw_qiskit_objects():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 378

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 379

`Phase 5 & 8: Verify full response contract converts cleanly with json.dumps`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 380

`and contains no raw Qiskit objects, non-primitive types, or unhandled objects.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 381

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 382

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 383

`res = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 384

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 385

`json={"learner_id": "u_json_check", "response": "10"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 386

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 387

`assert res.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 388

`data = res.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 389

`(blank)`

Blank line used to separate nearby statements.
### Line 390

`# Must be valid pure JSON string`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 391

`json_str = json.dumps(data)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 392

`parsed = json.loads(json_str)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 393

`(blank)`

Blank line used to separate nearby statements.
### Line 394

`# Key fields present`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 395

`assert "activity" in parsed`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 396

`assert "learner_response" in parsed`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 397

`assert "verified_result" in parsed`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 398

`assert "evidence" in parsed`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 399

`assert "learner_state" in parsed`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 400

`assert "adaptive_decision" in parsed`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 401

`(blank)`

Blank line used to separate nearby statements.
### Line 402

`# Check verified result primitives`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 403

`vr = parsed["verified_result"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 404

`assert isinstance(vr["target_state"], str)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 405

`assert isinstance(vr["most_likely_state"], str)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 406

`assert isinstance(vr["target_probability"], float)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 407

`assert isinstance(vr["counts"], dict)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 408

`assert isinstance(vr["shots"], int)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.

## Nearby Files

[tests/api/__init__.py](__init__.py.md), [tests/api/test_activities.py](test_activities.py.md), [tests/api/test_ai.py](test_ai.py.md), [tests/api/test_frontend_adapter_and_binding.py](test_frontend_adapter_and_binding.py.md), [tests/api/test_health.py](test_health.py.md), [tests/api/test_json_contracts.py](test_json_contracts.py.md), [tests/api/test_m1_m6_integration.py](test_m1_m6_integration.py.md), [tests/api/test_m6_adapter.py](test_m6_adapter.py.md)
