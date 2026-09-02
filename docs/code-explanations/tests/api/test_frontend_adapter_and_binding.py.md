# Explanation: `tests/api/test_frontend_adapter_and_binding.py`

## Purpose

This page explains the meaningful behavior in `tests/api/test_frontend_adapter_and_binding.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
import json
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from backend.adaptive import (
    InMemoryLearnerRepository,
    StorageUnavailableError,
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
# 1. FRONTEND CONTRACT TESTS (M1/M6 CONSUMPTION VIA FASTAPI GATEWAY)
# ===========================================================================

def test_frontend_loads_activities_list():
    """Requirement 1: Frontend GET /api/activities loads registered activities."""
    client = TestClient(app)
    res = client.get("/api/activities")
    assert res.status_code == 200
    activities = res.json()
    assert len(activities) == 4
    assert activities[0]["activity_id"] == "act_grover_2q_predict"
    assert activities[0]["task_type"] == "quantum_prediction"


def test_frontend_loads_activity_detail():
    """Requirement 2: Frontend GET /api/activity/{id} loads specification."""
    client = TestClient(app)
    res = client.get("/api/activity/act_grover_2q_predict")
    assert res.status_code == 200
    act = res.json()
    assert act["activity_id"] == "act_grover_2q_predict"
    assert act["quantum_experiment"] is not None
    assert act["quantum_experiment"]["algorithm"] == "grover"


def test_frontend_submission_renders_3_distinct_states():
    """
    Requirements 4 & 5: Submission preserves the 3 distinct quantum states:
      1. Learner Predicted State ("01")
      2. Theoretical Target State ("10")
      3. Empirical Most-Likely Measured State ("10")
    """
    client = TestClient(app)
    res = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_frontend_demo", "response": "01"},
    )
    assert res.status_code == 200
    data = res.json()

    # Distinct states
    assert data["learner_response"] == "01"
    assert data["verified_result"]["target_state"] == "10"
    assert data["verified_result"]["most_likely_state"] == "10"
    assert data["verified_result"]["target_probability"] > 0.90
    assert data["evidence"]["is_correct"] is False


def test_frontend_renders_gather_evidence_state():
    """Requirement 7: Case A Single error -> gather_evidence, confidence 0.35, observing."""
    client = TestClient(app)
    res = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_case_a", "response": "01"},
    )
    data = res.json()
    inf = data["learner_state"]["gap_inferences"]["grover.search_problem"]
    assert inf["status"] == "observing"
    assert inf["trend"] == "preliminary_observation"
    assert inf["confidence"] == 0.35
    assert data["adaptive_decision"]["action"] == "gather_evidence"
    assert data["adaptive_decision"]["target"] == "act_grover_2q_predict"


def test_frontend_renders_targeted_remediation_state():
    """Requirement 8: Case B Repeated errors -> targeted_remediation, confidence 0.90."""
    client = TestClient(app)
    client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_case_b", "response": "01"},
    )
    res2 = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_case_b", "response": "00"},
    )
    data = res2.json()
    inf = data["learner_state"]["gap_inferences"]["grover.search_problem"]
    assert inf["status"] == "remediation_needed"
    assert inf["trend"] == "persistent_difficulty"
    assert inf["confidence"] == 0.90
    assert data["adaptive_decision"]["action"] == "targeted_remediation"
    assert data["adaptive_decision"]["target"] == "act_measurement_prob_diagnostic"


def test_frontend_renders_improving_state():
    """Requirement 9: Case C Wrong -> Remediation -> Correct -> improving, advance."""
    client = TestClient(app)
    # Attempt 1: Error on Grover
    client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_case_c", "response": "01"},
    )
    # Attempt 2: Success on Remediation
    client.post(
        "/api/activity/act_measurement_prob_diagnostic/submit",
        json={"learner_id": "u_case_c", "response": "B"},
    )
    # Attempt 3: Success on Retry Grover
    res3 = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_case_c", "response": "10"},
    )
    data = res3.json()
    inf = data["learner_state"]["gap_inferences"]["grover.search_problem"]
    assert inf["status"] == "improving"
    assert inf["trend"] == "improving"
    assert inf["confidence"] == 0.15
    assert data["adaptive_decision"]["action"] == "advance"


def test_frontend_renders_stable_mastery_state():
    """Requirement 10: Case D Correct -> Correct -> stable_mastery, advance."""
    client = TestClient(app)
    client.post(
        "/api/activity/act_grover_iteration_reasoning/submit",
        json={"learner_id": "u_case_d", "response": "B"},
    )
    res2 = client.post(
        "/api/activity/act_grover_iteration_reasoning/submit",
        json={"learner_id": "u_case_d", "response": "B"},
    )
    data = res2.json()
    inf = data["learner_state"]["gap_inferences"]["grover.amplitude_amplification"]
    assert inf["status"] == "mastered"
    assert inf["trend"] == "stable_mastery"
    assert inf["confidence"] == 0.0


def test_frontend_handles_404_activity_not_found():
    """Requirement 11: 404 for unknown activity ID."""
    client = TestClient(app)
    res = client.get("/api/activity/act_unknown_xyz")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_frontend_handles_500_quantum_failure():
    """Requirement 12: 500 when quantum execution fails."""
    client = TestClient(app)
    with patch("backend.api.routes.activities.run_experiment", side_effect=RuntimeError("Aer simulator failure")):
        res = client.post(
            "/api/activity/act_grover_2q_predict/submit",
            json={"learner_id": "u_err_q", "response": "10"},
        )
        assert res.status_code == 500
        assert "Quantum execution engine failed" in res.json()["detail"]


def test_frontend_handles_503_persistence_failure():
    """Requirement 13: 503 when persistence is unavailable."""
    client = TestClient(app)
    class BrokenRepo(InMemoryLearnerRepository):
        def save(self, state):
            raise StorageUnavailableError("Supabase network partition")

    set_learner_repository(BrokenRepo())
    res = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_err_p", "response": "10"},
    )
    assert res.status_code == 503
    assert "Failed to persist updated learner state" in res.json()["detail"]


def test_frontend_ai_failure_does_not_erase_submission():
    """Requirement 14: AI failure returns 503 but does not alter successful submission."""
    client = TestClient(app)
    repo = InMemoryLearnerRepository()
    set_learner_repository(repo)

    # 1. Submission succeeds
    sub_res = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_ai_fail", "response": "10"},
    )
    assert sub_res.status_code == 200
    sub_data = sub_res.json()

    # 2. AI fails
    class FailingProvider(LLMProvider):
        def generate(self, messages, model=None):
            raise RuntimeError("API timeout")

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

    # 3. State in repository remains intact
    assert repo.exists("u_ai_fail") is True
    persisted = repo.get("u_ai_fail")
    assert len(persisted.evidence_history) == 1


def test_frontend_static_serving():
    """Verify that FastAPI mounts and serves the enhanced hybrid frontend index.html."""
    client = TestClient(app)
    res = client.get("/")
    assert res.status_code == 200
    html = res.text
    # Core brand & structure
    assert "Q-BIT.140" in html
    assert "Interactive Quantum Circuit Studio" in html
    # Hybrid visual enhancements
    assert '<canvas id="fx"></canvas>' in html
    assert 'class="atom"' in html
    # Topbar Mastery
    assert 'id="chipMastery"' in html
    assert 'id="badgeMastery"' in html
    # Profile modal & subviews
    assert 'id="profileModal"' in html
    assert 'id="profileView-menu"' in html
    assert 'id="profileView-edit"' in html
    assert 'id="profileView-settings"' in html
    # Core quantum & adaptive IDs
    assert 'id="circuitWireGrid"' in html
    assert 'id="quantumResultsCard"' in html
    assert 'id="stateTriadContainer"' in html
    assert 'id="histogramContainer"' in html
    assert 'id="adaptiveDecisionCard"' in html
    assert 'id="aiGuidanceCard"' in html
    assert 'id="askModal"' in html

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

`StorageUnavailableError,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 9

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 10

`from backend.ai import LLMProvider, MockLLMProvider`

Imports a dependency or project symbol so later code can use it by name.
### Line 11

`from backend.api.dependencies import (`

Imports a dependency or project symbol so later code can use it by name.
### Line 12

`reset_dependencies,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 13

`set_learner_repository,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 14

`set_llm_provider,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 15

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 16

`from backend.api.main import app`

Imports a dependency or project symbol so later code can use it by name.
### Line 17

`(blank)`

Blank line used to separate nearby statements.
### Line 19

`@pytest.fixture(autouse=True)`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 20

`def setup_clean_env():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 21

`"""Ensure every test runs in an isolated environment."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 22

`repo = InMemoryLearnerRepository()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 23

`set_learner_repository(repo)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 24

`set_llm_provider(MockLLMProvider())`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 25

`yield`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 26

`reset_dependencies()`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 27

`(blank)`

Blank line used to separate nearby statements.
### Line 29

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 30

`# 1. FRONTEND CONTRACT TESTS (M1/M6 CONSUMPTION VIA FASTAPI GATEWAY)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 31

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 32

`(blank)`

Blank line used to separate nearby statements.
### Line 33

`def test_frontend_loads_activities_list():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 34

`"""Requirement 1: Frontend GET /api/activities loads registered activities."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 35

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 36

`res = client.get("/api/activities")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 37

`assert res.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 38

`activities = res.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 39

`assert len(activities) == 4`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 40

`assert activities[0]["activity_id"] == "act_grover_2q_predict"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 41

`assert activities[0]["task_type"] == "quantum_prediction"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 42

`(blank)`

Blank line used to separate nearby statements.
### Line 44

`def test_frontend_loads_activity_detail():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 45

`"""Requirement 2: Frontend GET /api/activity/{id} loads specification."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 46

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 47

`res = client.get("/api/activity/act_grover_2q_predict")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 48

`assert res.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 49

`act = res.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 50

`assert act["activity_id"] == "act_grover_2q_predict"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 51

`assert act["quantum_experiment"] is not None`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 52

`assert act["quantum_experiment"]["algorithm"] == "grover"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 53

`(blank)`

Blank line used to separate nearby statements.
### Line 55

`def test_frontend_submission_renders_3_distinct_states():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 56

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 57

`Requirements 4 & 5: Submission preserves the 3 distinct quantum states:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 58

`1. Learner Predicted State ("01")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 59

`2. Theoretical Target State ("10")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 60

`3. Empirical Most-Likely Measured State ("10")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 61

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 62

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 63

`res = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 64

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 65

`json={"learner_id": "u_frontend_demo", "response": "01"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 66

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 67

`assert res.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 68

`data = res.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 69

`(blank)`

Blank line used to separate nearby statements.
### Line 70

`# Distinct states`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 71

`assert data["learner_response"] == "01"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 72

`assert data["verified_result"]["target_state"] == "10"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 73

`assert data["verified_result"]["most_likely_state"] == "10"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 74

`assert data["verified_result"]["target_probability"] > 0.90`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 75

`assert data["evidence"]["is_correct"] is False`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 76

`(blank)`

Blank line used to separate nearby statements.
### Line 78

`def test_frontend_renders_gather_evidence_state():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 79

`"""Requirement 7: Case A Single error -> gather_evidence, confidence 0.35, observing."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 80

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 81

`res = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 82

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 83

`json={"learner_id": "u_case_a", "response": "01"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 84

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 85

`data = res.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 86

`inf = data["learner_state"]["gap_inferences"]["grover.search_problem"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 87

`assert inf["status"] == "observing"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 88

`assert inf["trend"] == "preliminary_observation"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 89

`assert inf["confidence"] == 0.35`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 90

`assert data["adaptive_decision"]["action"] == "gather_evidence"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 91

`assert data["adaptive_decision"]["target"] == "act_grover_2q_predict"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 92

`(blank)`

Blank line used to separate nearby statements.
### Line 94

`def test_frontend_renders_targeted_remediation_state():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 95

`"""Requirement 8: Case B Repeated errors -> targeted_remediation, confidence 0.90."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 96

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 97

`client.post(`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 98

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 99

`json={"learner_id": "u_case_b", "response": "01"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 100

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 101

`res2 = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 102

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 103

`json={"learner_id": "u_case_b", "response": "00"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 104

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 105

`data = res2.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 106

`inf = data["learner_state"]["gap_inferences"]["grover.search_problem"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 107

`assert inf["status"] == "remediation_needed"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 108

`assert inf["trend"] == "persistent_difficulty"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 109

`assert inf["confidence"] == 0.90`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 110

`assert data["adaptive_decision"]["action"] == "targeted_remediation"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 111

`assert data["adaptive_decision"]["target"] == "act_measurement_prob_diagnostic"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 112

`(blank)`

Blank line used to separate nearby statements.
### Line 114

`def test_frontend_renders_improving_state():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 115

`"""Requirement 9: Case C Wrong -> Remediation -> Correct -> improving, advance."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 116

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 117

`# Attempt 1: Error on Grover`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 118

`client.post(`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 119

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 120

`json={"learner_id": "u_case_c", "response": "01"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 121

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 122

`# Attempt 2: Success on Remediation`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 123

`client.post(`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 124

`"/api/activity/act_measurement_prob_diagnostic/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 125

`json={"learner_id": "u_case_c", "response": "B"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 126

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 127

`# Attempt 3: Success on Retry Grover`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 128

`res3 = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 129

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 130

`json={"learner_id": "u_case_c", "response": "10"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 131

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 132

`data = res3.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 133

`inf = data["learner_state"]["gap_inferences"]["grover.search_problem"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 134

`assert inf["status"] == "improving"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 135

`assert inf["trend"] == "improving"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 136

`assert inf["confidence"] == 0.15`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 137

`assert data["adaptive_decision"]["action"] == "advance"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 138

`(blank)`

Blank line used to separate nearby statements.
### Line 140

`def test_frontend_renders_stable_mastery_state():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 141

`"""Requirement 10: Case D Correct -> Correct -> stable_mastery, advance."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 142

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 143

`client.post(`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 144

`"/api/activity/act_grover_iteration_reasoning/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 145

`json={"learner_id": "u_case_d", "response": "B"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 146

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 147

`res2 = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 148

`"/api/activity/act_grover_iteration_reasoning/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 149

`json={"learner_id": "u_case_d", "response": "B"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 150

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 151

`data = res2.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 152

`inf = data["learner_state"]["gap_inferences"]["grover.amplitude_amplification"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 153

`assert inf["status"] == "mastered"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 154

`assert inf["trend"] == "stable_mastery"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 155

`assert inf["confidence"] == 0.0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 156

`(blank)`

Blank line used to separate nearby statements.
### Line 158

`def test_frontend_handles_404_activity_not_found():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 159

`"""Requirement 11: 404 for unknown activity ID."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 160

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 161

`res = client.get("/api/activity/act_unknown_xyz")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 162

`assert res.status_code == 404`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 163

`assert "not found" in res.json()["detail"].lower()`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 164

`(blank)`

Blank line used to separate nearby statements.
### Line 166

`def test_frontend_handles_500_quantum_failure():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 167

`"""Requirement 12: 500 when quantum execution fails."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 168

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 169

`with patch("backend.api.routes.activities.run_experiment", side_effect=RuntimeError("Aer simulator failure")):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 170

`res = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 171

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 172

`json={"learner_id": "u_err_q", "response": "10"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 173

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 174

`assert res.status_code == 500`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 175

`assert "Quantum execution engine failed" in res.json()["detail"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 176

`(blank)`

Blank line used to separate nearby statements.
### Line 178

`def test_frontend_handles_503_persistence_failure():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 179

`"""Requirement 13: 503 when persistence is unavailable."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 180

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 181

`class BrokenRepo(InMemoryLearnerRepository):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 182

`def save(self, state):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 183

`raise StorageUnavailableError("Supabase network partition")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 184

`(blank)`

Blank line used to separate nearby statements.
### Line 185

`set_learner_repository(BrokenRepo())`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 186

`res = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 187

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 188

`json={"learner_id": "u_err_p", "response": "10"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 189

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 190

`assert res.status_code == 503`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 191

`assert "Failed to persist updated learner state" in res.json()["detail"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 192

`(blank)`

Blank line used to separate nearby statements.
### Line 194

`def test_frontend_ai_failure_does_not_erase_submission():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 195

`"""Requirement 14: AI failure returns 503 but does not alter successful submission."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 196

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 197

`repo = InMemoryLearnerRepository()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 198

`set_learner_repository(repo)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 199

`(blank)`

Blank line used to separate nearby statements.
### Line 200

`# 1. Submission succeeds`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 201

`sub_res = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 202

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 203

`json={"learner_id": "u_ai_fail", "response": "10"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 204

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 205

`assert sub_res.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 206

`sub_data = sub_res.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 207

`(blank)`

Blank line used to separate nearby statements.
### Line 208

`# 2. AI fails`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 209

`class FailingProvider(LLMProvider):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 210

`def generate(self, messages, model=None):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 211

`raise RuntimeError("API timeout")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 212

`(blank)`

Blank line used to separate nearby statements.
### Line 213

`set_llm_provider(FailingProvider())`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 214

`ai_res = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 215

`"/api/ai/explain_experiment",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 216

`json={`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 217

`"learner_response": "10",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 218

`"verified_result": sub_data["verified_result"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 219

`"evidence": sub_data["evidence"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 220

`"adaptive_decision": sub_data["adaptive_decision"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 221

`},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 222

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 223

`assert ai_res.status_code == 503`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 224

`(blank)`

Blank line used to separate nearby statements.
### Line 225

`# 3. State in repository remains intact`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 226

`assert repo.exists("u_ai_fail") is True`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 227

`persisted = repo.get("u_ai_fail")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 228

`assert len(persisted.evidence_history) == 1`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 229

`(blank)`

Blank line used to separate nearby statements.
### Line 231

`def test_frontend_static_serving():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 232

`"""Verify that FastAPI mounts and serves the enhanced hybrid frontend index.html."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 233

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 234

`res = client.get("/")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 235

`assert res.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 236

`html = res.text`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 237

`# Core brand & structure`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 238

`assert "Q-BIT.140" in html`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 239

`assert "Interactive Quantum Circuit Studio" in html`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 240

`# Hybrid visual enhancements`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 241

`assert '<canvas id="fx"></canvas>' in html`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 242

`assert 'class="atom"' in html`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 243

`# Topbar Mastery`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 244

`assert 'id="chipMastery"' in html`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 245

`assert 'id="badgeMastery"' in html`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 246

`# Profile modal & subviews`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 247

`assert 'id="profileModal"' in html`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 248

`assert 'id="profileView-menu"' in html`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 249

`assert 'id="profileView-edit"' in html`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 250

`assert 'id="profileView-settings"' in html`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 251

`# Core quantum & adaptive IDs`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 252

`assert 'id="circuitWireGrid"' in html`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 253

`assert 'id="quantumResultsCard"' in html`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 254

`assert 'id="stateTriadContainer"' in html`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 255

`assert 'id="histogramContainer"' in html`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 256

`assert 'id="adaptiveDecisionCard"' in html`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 257

`assert 'id="aiGuidanceCard"' in html`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 258

`assert 'id="askModal"' in html`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.

## Nearby Files

[tests/api/__init__.py](__init__.py.md), [tests/api/test_activities.py](test_activities.py.md), [tests/api/test_adaptive_vertical_slice.py](test_adaptive_vertical_slice.py.md), [tests/api/test_ai.py](test_ai.py.md), [tests/api/test_health.py](test_health.py.md), [tests/api/test_json_contracts.py](test_json_contracts.py.md), [tests/api/test_m1_m6_integration.py](test_m1_m6_integration.py.md), [tests/api/test_m6_adapter.py](test_m6_adapter.py.md)
