# Explanation: `tests/api/test_pass2_contracts_dataflow_graph.py`

## Purpose

This page explains the meaningful behavior in `tests/api/test_pass2_contracts_dataflow_graph.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
import json
import pytest
from fastapi.testclient import TestClient

from backend.adaptive import (
    Activity,
    AdaptiveRecommendation,
    CONCEPT_GRAPH,
    Concept,
    GapInference,
    InMemoryLearnerRepository,
    JSONFileLearnerRepository,
    LearnerContext,
    LearnerEvidence,
    LearnerModel,
    LearnerState,
    MVP_ACTIVITIES,
    Question,
    QuizResult,
    QuizSubmission,
    get_activity,
    get_concept,
    get_concept_display_name,
    get_concept_graph,
    list_activities,
    resolve_concept_id,
)
from backend.adaptive.concepts import CANONICAL_CONCEPTS
from backend.ai import MockLLMProvider, ask_question, explain_experiment
from backend.api.dependencies import (
    reset_dependencies,
    set_learner_repository,
    set_llm_provider,
)
from backend.api.main import app
from backend.api.schemas import (
    ActivityDetailResponse,
    ActivitySummary,
    AskRequest,
    AskResponse,
    ExplainExperimentRequest,
    ExplainExperimentResponse,
    HealthResponse,
    SubmissionRequest,
    SubmissionResponse,
)


@pytest.fixture(autouse=True)
def setup_clean_env():
    """Ensure every test runs in an isolated environment."""
    repo = InMemoryLearnerRepository()
    set_learner_repository(repo)
    set_llm_provider(MockLLMProvider())
    yield
    reset_dependencies()


# ===========================================================================
# 1. API ↔ DOMAIN MODEL CONTRACTS & SCHEMA VALIDATION
# ===========================================================================

def test_pydantic_to_domain_schema_parity():
    """Verify all Pydantic schemas map cleanly to domain dataclasses without data loss."""
    # 1. Health schema
    health = HealthResponse(status="ok", service="qbit-api")
    assert health.model_dump() == {"status": "ok", "service": "qbit-api"}

    # 2. ActivitySummary schema
    act = get_activity("act_grover_2q_predict")
    summary = ActivitySummary(
        activity_id=act.activity_id,
        concept_id=act.concept_id,
        title=act.title,
        description=act.description,
        task_type=act.task_type,
        prerequisites=act.prerequisites,
    )
    assert summary.activity_id == "act_grover_2q_predict"
    assert summary.task_type == "quantum_prediction"

    # 3. SubmissionRequest schema validation
    with pytest.raises(ValueError):
        SubmissionRequest(learner_id="", response="10")  # Empty learner_id rejected

    with pytest.raises(ValueError):
        SubmissionRequest(learner_id="u1", response="")  # Empty response rejected


def test_domain_dataclasses_lossless_json_round_trips():
    """Verify domain dataclasses serialize to/from dicts losslessly."""
    # LearnerEvidence
    ev = LearnerEvidence(
        learner_id="u_rt",
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        learner_response="10",
        is_correct=True,
        attempt_number=2,
        verified_result={"target_state": "10", "shots": 1024},
        evaluation_details={"match": True},
    )
    ev_dict = ev.to_dict()
    ev_recon = LearnerEvidence.from_dict(ev_dict)
    assert ev_recon.learner_id == ev.learner_id
    assert ev_recon.is_correct is True
    assert ev_recon.verified_result["target_state"] == "10"

    # GapInference
    gap = GapInference(
        concept_id="grover.search_problem",
        confidence=0.35,
        status="observing",
        supporting_evidence_count=1,
        description="Preliminary observation.",
        trend="preliminary_observation",
    )
    gap_dict = gap.to_dict()
    gap_recon = GapInference.from_dict(gap_dict)
    assert gap_recon.confidence == 0.35
    assert gap_recon.trend == "preliminary_observation"

    # AdaptiveRecommendation
    rec = AdaptiveRecommendation(
        action="gather_evidence",
        target="act_grover_2q_predict",
        reason="Observation required.",
        concept_id="grover.search_problem",
    )
    rec_dict = rec.to_dict()
    rec_recon = AdaptiveRecommendation.from_dict(rec_dict)
    assert rec_recon.action == "gather_evidence"
    assert rec_recon.target == "act_grover_2q_predict"


# ===========================================================================
# 2. ACTIVITY GRAPH AUDIT & REACHABILITY
# ===========================================================================

def test_activity_graph_completeness_reachability_and_termination():
    """
    Programmatic graph audit:
      - 4 MVP activities
      - No dangling IDs
      - Terminating forward progression
      - Terminating remediation path
      - All concepts and prerequisites exist in CANONICAL_CONCEPTS
    """
    activities = list_activities()
    assert len(activities) == 4

    activity_ids = {a.activity_id for a in activities}

    for a in activities:
        # Check concept ID
        canonical_concept = resolve_concept_id(a.concept_id)
        assert canonical_concept in CANONICAL_CONCEPTS or canonical_concept.startswith("grover.")

        # Check prerequisites
        for p in a.prerequisites:
            p_canonical = resolve_concept_id(p)
            assert p_canonical in CANONICAL_CONCEPTS or p_canonical.startswith("grover.")

        # Check next activity
        if a.next_activity_id is not None:
            assert a.next_activity_id in activity_ids, f"Dangling next_activity_id: {a.next_activity_id}"

        # Check remediation activity
        if a.remediation_activity_id is not None:
            assert a.remediation_activity_id in activity_ids, f"Dangling remediation_activity_id: {a.remediation_activity_id}"

    # Trace forward path from entry
    visited_forward = set()
    current = "act_grover_2q_predict"
    while current:
        assert current not in visited_forward, f"Accidental cycle in forward progression: {current}"
        visited_forward.add(current)
        current = MVP_ACTIVITIES[current].next_activity_id

    # Normal progression terminates at act_grover_iteration_reasoning
    assert "act_grover_iteration_reasoning" in visited_forward
    assert MVP_ACTIVITIES["act_grover_iteration_reasoning"].next_activity_id is None

    # Trace remediation path from entry
    visited_remed = set()
    current_remed = "act_grover_2q_predict"
    while current_remed:
        assert current_remed not in visited_remed, f"Accidental cycle in remediation progression: {current_remed}"
        visited_remed.add(current_remed)
        current_remed = MVP_ACTIVITIES[current_remed].remediation_activity_id

    # Remediation path terminates cleanly at act_superposition_remediation
    assert "act_superposition_remediation" in visited_remed
    assert MVP_ACTIVITIES["act_superposition_remediation"].remediation_activity_id is None


# ===========================================================================
# 3. ATTEMPT NUMBERING & MULTI-ACTIVITY ISOLATION
# ===========================================================================

def test_attempt_numbering_multi_activity_isolation():
    """
    Verify attempt numbering is strictly monotonic and isolated across activities:
      - Act A: 1, 2, 3
      - Act B: 1, 2
      - Interleaving does not reset or corrupt counts.
    """
    client = TestClient(app)
    learner_id = "learner_interleaved_test"

    # Act A - Attempt 1
    r1 = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": learner_id, "response": "01"},
    )
    assert r1.json()["evidence"]["attempt_number"] == 1

    # Act B - Attempt 1 (Different activity)
    r2 = client.post(
        "/api/activity/act_measurement_prob_diagnostic/submit",
        json={"learner_id": learner_id, "response": "B"},
    )
    assert r2.json()["evidence"]["attempt_number"] == 1

    # Act A - Attempt 2
    r3 = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": learner_id, "response": "00"},
    )
    assert r3.json()["evidence"]["attempt_number"] == 2

    # Act B - Attempt 2
    r4 = client.post(
        "/api/activity/act_measurement_prob_diagnostic/submit",
        json={"learner_id": learner_id, "response": "B"},
    )
    assert r4.json()["evidence"]["attempt_number"] == 2

    # Act A - Attempt 3
    r5 = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": learner_id, "response": "10"},
    )
    assert r5.json()["evidence"]["attempt_number"] == 3

    # Total accumulated history has all 5 attempts preserved
    state_history = r5.json()["learner_state"]["evidence_history"]
    assert len(state_history) == 5
    assert [e["activity_id"] for e in state_history] == [
        "act_grover_2q_predict",
        "act_measurement_prob_diagnostic",
        "act_grover_2q_predict",
        "act_measurement_prob_diagnostic",
        "act_grover_2q_predict",
    ]


# ===========================================================================
# 4. JSON SERIALIZATION & INTERNAL OBJECT PURITY
# ===========================================================================

def test_api_response_pure_json_without_internal_objects():
    """
    Verify complete absence of raw Python/Qiskit internal objects across all API responses.
    """
    client = TestClient(app)

    # 1. Activities list
    res_list = client.get("/api/activities")
    assert res_list.status_code == 200
    json.dumps(res_list.json())  # Pure JSON

    # 2. Activity detail
    res_detail = client.get("/api/activity/act_grover_2q_predict")
    assert res_detail.status_code == 200
    json.dumps(res_detail.json())  # Pure JSON

    # 3. Submission response
    res_sub = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_json_pure", "response": "10"},
    )
    assert res_sub.status_code == 200
    sub_data = res_sub.json()
    json.dumps(sub_data)  # Pure JSON

    # Confirm verified result types
    vr = sub_data["verified_result"]
    assert type(vr["target_state"]) is str
    assert type(vr["shots"]) is int
    assert type(vr["target_probability"]) is float
    assert type(vr["counts"]) is dict

    # 4. AI Explanation
    res_ai = client.post(
        "/api/ai/explain_experiment",
        json={
            "learner_response": "10",
            "verified_result": sub_data["verified_result"],
            "evidence": sub_data["evidence"],
            "adaptive_decision": sub_data["adaptive_decision"],
        },
    )
    assert res_ai.status_code == 200
    json.dumps(res_ai.json())  # Pure JSON


# ===========================================================================
# 5. M2 EXCLUSIVE ADAPTIVE DECISION SOURCE
# ===========================================================================

def test_m2_exclusive_deterministic_adaptive_decisions():
    """
    Verify M2 remains the exclusive deterministic source of decisions:
      - Decisions are deterministic across identical state
      - M5 explanation does not mutate recommendation
      - Valid actions only from defined vocabulary
    """
    model = LearnerModel()
    state = LearnerState(user_id="u_det")

    valid_actions = {
        "advance",
        "gather_evidence",
        "targeted_remediation",
        "recommend_prerequisite",
        "recommend_targeted_review",
        "reinforce_current_concept",
    }

    # Initial single error -> gather_evidence
    ev1 = LearnerEvidence(
        learner_id="u_det",
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        learner_response="01",
        is_correct=False,
    )
    rec1 = model.record_evidence(ev1, state)
    assert rec1.action in valid_actions
    assert rec1.action == "gather_evidence"

    # Repeated error -> targeted_remediation
    ev2 = LearnerEvidence(
        learner_id="u_det",
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        learner_response="00",
        is_correct=False,
        attempt_number=2,
    )
    rec2 = model.record_evidence(ev2, state)
    assert rec2.action in valid_actions
    assert rec2.action == "targeted_remediation"
    assert rec2.target == "act_measurement_prob_diagnostic"

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

`Activity,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 7

`AdaptiveRecommendation,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 8

`CONCEPT_GRAPH,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 9

`Concept,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 10

`GapInference,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 11

`InMemoryLearnerRepository,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 12

`JSONFileLearnerRepository,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 13

`LearnerContext,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 14

`LearnerEvidence,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 15

`LearnerModel,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 16

`LearnerState,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 17

`MVP_ACTIVITIES,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 18

`Question,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 19

`QuizResult,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 20

`QuizSubmission,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 21

`get_activity,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 22

`get_concept,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 23

`get_concept_display_name,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 24

`get_concept_graph,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 25

`list_activities,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 26

`resolve_concept_id,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 27

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 28

`from backend.adaptive.concepts import CANONICAL_CONCEPTS`

Imports a dependency or project symbol so later code can use it by name.
### Line 29

`from backend.ai import MockLLMProvider, ask_question, explain_experiment`

Imports a dependency or project symbol so later code can use it by name.
### Line 30

`from backend.api.dependencies import (`

Imports a dependency or project symbol so later code can use it by name.
### Line 31

`reset_dependencies,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 32

`set_learner_repository,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 33

`set_llm_provider,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 34

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 35

`from backend.api.main import app`

Imports a dependency or project symbol so later code can use it by name.
### Line 36

`from backend.api.schemas import (`

Imports a dependency or project symbol so later code can use it by name.
### Line 37

`ActivityDetailResponse,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 38

`ActivitySummary,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 39

`AskRequest,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 40

`AskResponse,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 41

`ExplainExperimentRequest,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 42

`ExplainExperimentResponse,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 43

`HealthResponse,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 44

`SubmissionRequest,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 45

`SubmissionResponse,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 46

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 47

`(blank)`

Blank line used to separate nearby statements.
### Line 49

`@pytest.fixture(autouse=True)`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 50

`def setup_clean_env():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 51

`"""Ensure every test runs in an isolated environment."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 52

`repo = InMemoryLearnerRepository()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 53

`set_learner_repository(repo)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 54

`set_llm_provider(MockLLMProvider())`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 55

`yield`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 56

`reset_dependencies()`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 57

`(blank)`

Blank line used to separate nearby statements.
### Line 59

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 60

`# 1. API ↔ DOMAIN MODEL CONTRACTS & SCHEMA VALIDATION`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 61

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 62

`(blank)`

Blank line used to separate nearby statements.
### Line 63

`def test_pydantic_to_domain_schema_parity():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 64

`"""Verify all Pydantic schemas map cleanly to domain dataclasses without data loss."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 65

`# 1. Health schema`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 66

`health = HealthResponse(status="ok", service="qbit-api")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 67

`assert health.model_dump() == {"status": "ok", "service": "qbit-api"}`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 68

`(blank)`

Blank line used to separate nearby statements.
### Line 69

`# 2. ActivitySummary schema`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 70

`act = get_activity("act_grover_2q_predict")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 71

`summary = ActivitySummary(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 72

`activity_id=act.activity_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 73

`concept_id=act.concept_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 74

`title=act.title,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 75

`description=act.description,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 76

`task_type=act.task_type,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 77

`prerequisites=act.prerequisites,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 78

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 79

`assert summary.activity_id == "act_grover_2q_predict"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 80

`assert summary.task_type == "quantum_prediction"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 81

`(blank)`

Blank line used to separate nearby statements.
### Line 82

`# 3. SubmissionRequest schema validation`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 83

`with pytest.raises(ValueError):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 84

`SubmissionRequest(learner_id="", response="10")  # Empty learner_id rejected`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 85

`(blank)`

Blank line used to separate nearby statements.
### Line 86

`with pytest.raises(ValueError):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 87

`SubmissionRequest(learner_id="u1", response="")  # Empty response rejected`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 88

`(blank)`

Blank line used to separate nearby statements.
### Line 90

`def test_domain_dataclasses_lossless_json_round_trips():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 91

`"""Verify domain dataclasses serialize to/from dicts losslessly."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 92

`# LearnerEvidence`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 93

`ev = LearnerEvidence(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 94

`learner_id="u_rt",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 95

`activity_id="act_grover_2q_predict",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 96

`concept_id="grover.search_problem",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 97

`learner_response="10",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 98

`is_correct=True,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 99

`attempt_number=2,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 100

`verified_result={"target_state": "10", "shots": 1024},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 101

`evaluation_details={"match": True},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 102

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 103

`ev_dict = ev.to_dict()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 104

`ev_recon = LearnerEvidence.from_dict(ev_dict)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 105

`assert ev_recon.learner_id == ev.learner_id`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 106

`assert ev_recon.is_correct is True`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 107

`assert ev_recon.verified_result["target_state"] == "10"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 108

`(blank)`

Blank line used to separate nearby statements.
### Line 109

`# GapInference`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 110

`gap = GapInference(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 111

`concept_id="grover.search_problem",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 112

`confidence=0.35,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 113

`status="observing",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 114

`supporting_evidence_count=1,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 115

`description="Preliminary observation.",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 116

`trend="preliminary_observation",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 117

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 118

`gap_dict = gap.to_dict()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 119

`gap_recon = GapInference.from_dict(gap_dict)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 120

`assert gap_recon.confidence == 0.35`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 121

`assert gap_recon.trend == "preliminary_observation"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 122

`(blank)`

Blank line used to separate nearby statements.
### Line 123

`# AdaptiveRecommendation`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 124

`rec = AdaptiveRecommendation(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 125

`action="gather_evidence",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 126

`target="act_grover_2q_predict",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 127

`reason="Observation required.",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 128

`concept_id="grover.search_problem",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 129

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 130

`rec_dict = rec.to_dict()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 131

`rec_recon = AdaptiveRecommendation.from_dict(rec_dict)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 132

`assert rec_recon.action == "gather_evidence"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 133

`assert rec_recon.target == "act_grover_2q_predict"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 134

`(blank)`

Blank line used to separate nearby statements.
### Line 136

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 137

`# 2. ACTIVITY GRAPH AUDIT & REACHABILITY`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 138

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 139

`(blank)`

Blank line used to separate nearby statements.
### Line 140

`def test_activity_graph_completeness_reachability_and_termination():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 141

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 142

`Programmatic graph audit:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 143

`- 4 MVP activities`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 144

`- No dangling IDs`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 145

`- Terminating forward progression`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 146

`- Terminating remediation path`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 147

`- All concepts and prerequisites exist in CANONICAL_CONCEPTS`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 148

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 149

`activities = list_activities()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 150

`assert len(activities) == 4`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 151

`(blank)`

Blank line used to separate nearby statements.
### Line 152

`activity_ids = {a.activity_id for a in activities}`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 153

`(blank)`

Blank line used to separate nearby statements.
### Line 154

`for a in activities:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 155

`# Check concept ID`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 156

`canonical_concept = resolve_concept_id(a.concept_id)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 157

`assert canonical_concept in CANONICAL_CONCEPTS or canonical_concept.startswith("grover.")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 158

`(blank)`

Blank line used to separate nearby statements.
### Line 159

`# Check prerequisites`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 160

`for p in a.prerequisites:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 161

`p_canonical = resolve_concept_id(p)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 162

`assert p_canonical in CANONICAL_CONCEPTS or p_canonical.startswith("grover.")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 163

`(blank)`

Blank line used to separate nearby statements.
### Line 164

`# Check next activity`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 165

`if a.next_activity_id is not None:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 166

`assert a.next_activity_id in activity_ids, f"Dangling next_activity_id: {a.next_activity_id}"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 167

`(blank)`

Blank line used to separate nearby statements.
### Line 168

`# Check remediation activity`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 169

`if a.remediation_activity_id is not None:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 170

`assert a.remediation_activity_id in activity_ids, f"Dangling remediation_activity_id: {a.remediation_activity_id}"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 171

`(blank)`

Blank line used to separate nearby statements.
### Line 172

`# Trace forward path from entry`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 173

`visited_forward = set()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 174

`current = "act_grover_2q_predict"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 175

`while current:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 176

`assert current not in visited_forward, f"Accidental cycle in forward progression: {current}"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 177

`visited_forward.add(current)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 178

`current = MVP_ACTIVITIES[current].next_activity_id`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 179

`(blank)`

Blank line used to separate nearby statements.
### Line 180

`# Normal progression terminates at act_grover_iteration_reasoning`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 181

`assert "act_grover_iteration_reasoning" in visited_forward`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 182

`assert MVP_ACTIVITIES["act_grover_iteration_reasoning"].next_activity_id is None`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 183

`(blank)`

Blank line used to separate nearby statements.
### Line 184

`# Trace remediation path from entry`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 185

`visited_remed = set()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 186

`current_remed = "act_grover_2q_predict"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 187

`while current_remed:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 188

`assert current_remed not in visited_remed, f"Accidental cycle in remediation progression: {current_remed}"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 189

`visited_remed.add(current_remed)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 190

`current_remed = MVP_ACTIVITIES[current_remed].remediation_activity_id`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 191

`(blank)`

Blank line used to separate nearby statements.
### Line 192

`# Remediation path terminates cleanly at act_superposition_remediation`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 193

`assert "act_superposition_remediation" in visited_remed`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 194

`assert MVP_ACTIVITIES["act_superposition_remediation"].remediation_activity_id is None`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 195

`(blank)`

Blank line used to separate nearby statements.
### Line 197

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 198

`# 3. ATTEMPT NUMBERING & MULTI-ACTIVITY ISOLATION`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 199

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 200

`(blank)`

Blank line used to separate nearby statements.
### Line 201

`def test_attempt_numbering_multi_activity_isolation():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 202

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 203

`Verify attempt numbering is strictly monotonic and isolated across activities:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 204

`- Act A: 1, 2, 3`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 205

`- Act B: 1, 2`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 206

`- Interleaving does not reset or corrupt counts.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 207

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 208

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 209

`learner_id = "learner_interleaved_test"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 210

`(blank)`

Blank line used to separate nearby statements.
### Line 211

`# Act A - Attempt 1`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 212

`r1 = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 213

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 214

`json={"learner_id": learner_id, "response": "01"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 215

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 216

`assert r1.json()["evidence"]["attempt_number"] == 1`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 217

`(blank)`

Blank line used to separate nearby statements.
### Line 218

`# Act B - Attempt 1 (Different activity)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 219

`r2 = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 220

`"/api/activity/act_measurement_prob_diagnostic/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 221

`json={"learner_id": learner_id, "response": "B"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 222

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 223

`assert r2.json()["evidence"]["attempt_number"] == 1`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 224

`(blank)`

Blank line used to separate nearby statements.
### Line 225

`# Act A - Attempt 2`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 226

`r3 = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 227

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 228

`json={"learner_id": learner_id, "response": "00"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 229

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 230

`assert r3.json()["evidence"]["attempt_number"] == 2`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 231

`(blank)`

Blank line used to separate nearby statements.
### Line 232

`# Act B - Attempt 2`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 233

`r4 = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 234

`"/api/activity/act_measurement_prob_diagnostic/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 235

`json={"learner_id": learner_id, "response": "B"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 236

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 237

`assert r4.json()["evidence"]["attempt_number"] == 2`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 238

`(blank)`

Blank line used to separate nearby statements.
### Line 239

`# Act A - Attempt 3`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 240

`r5 = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 241

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 242

`json={"learner_id": learner_id, "response": "10"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 243

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 244

`assert r5.json()["evidence"]["attempt_number"] == 3`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 245

`(blank)`

Blank line used to separate nearby statements.
### Line 246

`# Total accumulated history has all 5 attempts preserved`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 247

`state_history = r5.json()["learner_state"]["evidence_history"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 248

`assert len(state_history) == 5`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 249

`assert [e["activity_id"] for e in state_history] == [`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 250

`"act_grover_2q_predict",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 251

`"act_measurement_prob_diagnostic",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 252

`"act_grover_2q_predict",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 253

`"act_measurement_prob_diagnostic",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 254

`"act_grover_2q_predict",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 255

`]`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 256

`(blank)`

Blank line used to separate nearby statements.
### Line 258

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 259

`# 4. JSON SERIALIZATION & INTERNAL OBJECT PURITY`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 260

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 261

`(blank)`

Blank line used to separate nearby statements.
### Line 262

`def test_api_response_pure_json_without_internal_objects():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 263

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 264

`Verify complete absence of raw Python/Qiskit internal objects across all API responses.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 265

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 266

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 267

`(blank)`

Blank line used to separate nearby statements.
### Line 268

`# 1. Activities list`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 269

`res_list = client.get("/api/activities")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 270

`assert res_list.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 271

`json.dumps(res_list.json())  # Pure JSON`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 272

`(blank)`

Blank line used to separate nearby statements.
### Line 273

`# 2. Activity detail`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 274

`res_detail = client.get("/api/activity/act_grover_2q_predict")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 275

`assert res_detail.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 276

`json.dumps(res_detail.json())  # Pure JSON`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 277

`(blank)`

Blank line used to separate nearby statements.
### Line 278

`# 3. Submission response`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 279

`res_sub = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 280

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 281

`json={"learner_id": "u_json_pure", "response": "10"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 282

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 283

`assert res_sub.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 284

`sub_data = res_sub.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 285

`json.dumps(sub_data)  # Pure JSON`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 286

`(blank)`

Blank line used to separate nearby statements.
### Line 287

`# Confirm verified result types`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 288

`vr = sub_data["verified_result"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 289

`assert type(vr["target_state"]) is str`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 290

`assert type(vr["shots"]) is int`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 291

`assert type(vr["target_probability"]) is float`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 292

`assert type(vr["counts"]) is dict`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 293

`(blank)`

Blank line used to separate nearby statements.
### Line 294

`# 4. AI Explanation`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 295

`res_ai = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 296

`"/api/ai/explain_experiment",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 297

`json={`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 298

`"learner_response": "10",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 299

`"verified_result": sub_data["verified_result"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 300

`"evidence": sub_data["evidence"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 301

`"adaptive_decision": sub_data["adaptive_decision"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 302

`},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 303

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 304

`assert res_ai.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 305

`json.dumps(res_ai.json())  # Pure JSON`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 306

`(blank)`

Blank line used to separate nearby statements.
### Line 308

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 309

`# 5. M2 EXCLUSIVE ADAPTIVE DECISION SOURCE`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 310

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 311

`(blank)`

Blank line used to separate nearby statements.
### Line 312

`def test_m2_exclusive_deterministic_adaptive_decisions():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 313

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 314

`Verify M2 remains the exclusive deterministic source of decisions:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 315

`- Decisions are deterministic across identical state`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 316

`- M5 explanation does not mutate recommendation`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 317

`- Valid actions only from defined vocabulary`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 318

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 319

`model = LearnerModel()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 320

`state = LearnerState(user_id="u_det")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 321

`(blank)`

Blank line used to separate nearby statements.
### Line 322

`valid_actions = {`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 323

`"advance",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 324

`"gather_evidence",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 325

`"targeted_remediation",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 326

`"recommend_prerequisite",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 327

`"recommend_targeted_review",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 328

`"reinforce_current_concept",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 329

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 330

`(blank)`

Blank line used to separate nearby statements.
### Line 331

`# Initial single error -> gather_evidence`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 332

`ev1 = LearnerEvidence(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 333

`learner_id="u_det",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 334

`activity_id="act_grover_2q_predict",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 335

`concept_id="grover.search_problem",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 336

`learner_response="01",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 337

`is_correct=False,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 338

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 339

`rec1 = model.record_evidence(ev1, state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 340

`assert rec1.action in valid_actions`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 341

`assert rec1.action == "gather_evidence"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 342

`(blank)`

Blank line used to separate nearby statements.
### Line 343

`# Repeated error -> targeted_remediation`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 344

`ev2 = LearnerEvidence(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 345

`learner_id="u_det",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 346

`activity_id="act_grover_2q_predict",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 347

`concept_id="grover.search_problem",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 348

`learner_response="00",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 349

`is_correct=False,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 350

`attempt_number=2,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 351

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 352

`rec2 = model.record_evidence(ev2, state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 353

`assert rec2.action in valid_actions`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 354

`assert rec2.action == "targeted_remediation"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 355

`assert rec2.target == "act_measurement_prob_diagnostic"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.

## Nearby Files

[tests/api/__init__.py](__init__.py.md), [tests/api/test_activities.py](test_activities.py.md), [tests/api/test_adaptive_vertical_slice.py](test_adaptive_vertical_slice.py.md), [tests/api/test_ai.py](test_ai.py.md), [tests/api/test_frontend_adapter_and_binding.py](test_frontend_adapter_and_binding.py.md), [tests/api/test_health.py](test_health.py.md), [tests/api/test_json_contracts.py](test_json_contracts.py.md), [tests/api/test_m1_m6_integration.py](test_m1_m6_integration.py.md)
