# Explanation: `tests/api/test_pass5_why_this_next_ux.py`

## Purpose

This page explains the meaningful behavior in `tests/api/test_pass5_why_this_next_ux.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
import json
import pytest
from fastapi.testclient import TestClient

from backend.adaptive import (
    InMemoryLearnerRepository,
    LearnerModel,
    LearnerState,
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
# 1. LEARNER-STATE & "WHY THIS NEXT?" PRESENTATION PARITY
# ===========================================================================

def test_single_error_learner_state_and_why_this_next():
    """
    Evaluator Step 1:
      - Prediction mismatch on Attempt 1
      - Evidence sufficiency = insufficient
      - Hypothesis = preliminary observation
      - Action = gather_evidence
      - Supporting evidence references Attempt 1
    """
    client = TestClient(app)
    res = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_evaluator_step1", "response": "01"},
    )
    assert res.status_code == 200
    data = res.json()

    # Distinct states
    assert data["learner_response"] == "01"
    assert data["verified_result"]["target_state"] == "10"
    assert data["verified_result"]["most_likely_state"] == "10"

    # Learner-state & evidence
    ev = data["evidence"]
    assert ev["evidence_id"].startswith("ev_act_grover_2q_predict_att1")
    assert ev["is_correct"] is False

    gap = data["learner_state"]["gap_inferences"]["grover.search_problem"]
    assert gap["status"] == "observing"
    assert gap["trend"] == "preliminary_observation"
    assert gap["confidence"] == 0.35
    assert gap["evidence_sufficiency"] == "insufficient"
    assert "preliminary_difficulty_observation" in gap["hypothesis"]
    assert gap["supporting_evidence_ids"] == [ev["evidence_id"]]

    # "Why this next?" decision trace
    dec = data["adaptive_decision"]
    assert dec["action"] == "gather_evidence"
    assert dec["trigger"] == "single_prediction_mismatch"
    assert dec["evidence_sufficiency"] == "insufficient"
    assert dec["supporting_evidence_ids"] == [ev["evidence_id"]]
    assert dec["target"] == "act_grover_2q_predict"


def test_repeated_error_targeted_remediation_trace():
    """
    Evaluator Step 2:
      - Repeated prediction mismatch on Attempt 2
      - Evidence sufficiency = sufficient_for_targeted_inference
      - Hypothesis = possible difficulty
      - Action = targeted_remediation
      - Supporting evidence = Attempt 1 + Attempt 2
    """
    client = TestClient(app)
    # Attempt 1
    r1 = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_evaluator_step2", "response": "01"},
    )
    ev1_id = r1.json()["evidence"]["evidence_id"]

    # Attempt 2
    r2 = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_evaluator_step2", "response": "00"},
    )
    assert r2.status_code == 200
    data = r2.json()
    ev2_id = data["evidence"]["evidence_id"]

    # Learner-state
    gap = data["learner_state"]["gap_inferences"]["grover.search_problem"]
    assert gap["status"] == "remediation_needed"
    assert gap["trend"] == "persistent_difficulty"
    assert gap["confidence"] == 0.90
    assert gap["evidence_sufficiency"] == "sufficient_for_targeted_inference"
    assert "possible_grover_search_problem_difficulty" in gap["hypothesis"]
    assert gap["supporting_evidence_ids"] == [ev1_id, ev2_id]

    # "Why this next?"
    dec = data["adaptive_decision"]
    assert dec["action"] == "targeted_remediation"
    assert dec["trigger"] == "repeated_prediction_error"
    assert dec["evidence_sufficiency"] == "sufficient_for_targeted_inference"
    assert dec["supporting_evidence_ids"] == [ev1_id, ev2_id]
    assert dec["target"] == "act_measurement_prob_diagnostic"


def test_remediation_success_and_retry_recovery():
    """
    Evaluator Step 3 & 4:
      - Step 3: Learner completes remediation diagnostic correctly.
      - Step 4: Learner retries Grover and succeeds -> post-intervention improvement -> advance.
    """
    client = TestClient(app)
    # 1. Error on Grover
    client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_evaluator_recovery", "response": "01"},
    )
    # 2. Success on Remediation
    r_remed = client.post(
        "/api/activity/act_measurement_prob_diagnostic/submit",
        json={"learner_id": "u_evaluator_recovery", "response": "B"},
    )
    assert r_remed.json()["evidence"]["is_correct"] is True
    assert r_remed.json()["adaptive_decision"]["action"] == "advance"

    # 3. Retry Grover Success
    r_retry = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_evaluator_recovery", "response": "10"},
    )
    data = r_retry.json()

    # Verification
    assert data["evidence"]["is_correct"] is True
    gap = data["learner_state"]["gap_inferences"]["grover.search_problem"]
    assert gap["status"] == "improving"
    assert gap["trend"] == "improving"
    assert gap["confidence"] == 0.15
    assert gap["evidence_sufficiency"] == "sufficient_for_improvement_observation"

    dec = data["adaptive_decision"]
    assert dec["action"] == "advance"
    assert dec["trigger"] == "post_intervention_recovery"
    assert dec["target"] == "act_grover_iteration_reasoning"


def test_ai_explanation_cites_m2_decision_without_overriding():
    """
    Evaluator Step 5:
      - M5 AI explanation grounds its output in M3 evidence and M2 decision trace.
      - If M5 fails, M2 decision and M3 result remain untouched.
    """
    client = TestClient(app)
    sub = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_m5_grounding_eval", "response": "01"},
    )
    sub_data = sub.json()

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
    assert "Evidence Record" in ai_data["explanation"]
    assert "single_prediction_mismatch" in ai_data["explanation"]

    # AI failure isolation
    class FailingLLM(LLMProvider):
        def generate(self, messages, model=None):
            raise RuntimeError("LLM offline")

    set_llm_provider(FailingLLM())
    fail_res = client.post(
        "/api/ai/explain_experiment",
        json={
            "learner_response": sub_data["learner_response"],
            "verified_result": sub_data["verified_result"],
            "evidence": sub_data["evidence"],
            "adaptive_decision": sub_data["adaptive_decision"],
        },
    )
    assert fail_res.status_code == 503
    # Submission result in client session is untouched
    assert sub_data["adaptive_decision"]["action"] == "gather_evidence"

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

`InMemoryLearnerRepository,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 7

`LearnerModel,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 8

`LearnerState,`

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

`# 1. LEARNER-STATE & "WHY THIS NEXT?" PRESENTATION PARITY`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 31

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 32

`(blank)`

Blank line used to separate nearby statements.
### Line 33

`def test_single_error_learner_state_and_why_this_next():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 34

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 35

`Evaluator Step 1:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 36

`- Prediction mismatch on Attempt 1`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 37

`- Evidence sufficiency = insufficient`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 38

`- Hypothesis = preliminary observation`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 39

`- Action = gather_evidence`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 40

`- Supporting evidence references Attempt 1`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 41

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 42

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 43

`res = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 44

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 45

`json={"learner_id": "u_evaluator_step1", "response": "01"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 46

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 47

`assert res.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 48

`data = res.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 49

`(blank)`

Blank line used to separate nearby statements.
### Line 50

`# Distinct states`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 51

`assert data["learner_response"] == "01"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 52

`assert data["verified_result"]["target_state"] == "10"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 53

`assert data["verified_result"]["most_likely_state"] == "10"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 54

`(blank)`

Blank line used to separate nearby statements.
### Line 55

`# Learner-state & evidence`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 56

`ev = data["evidence"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 57

`assert ev["evidence_id"].startswith("ev_act_grover_2q_predict_att1")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 58

`assert ev["is_correct"] is False`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 59

`(blank)`

Blank line used to separate nearby statements.
### Line 60

`gap = data["learner_state"]["gap_inferences"]["grover.search_problem"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 61

`assert gap["status"] == "observing"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 62

`assert gap["trend"] == "preliminary_observation"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 63

`assert gap["confidence"] == 0.35`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 64

`assert gap["evidence_sufficiency"] == "insufficient"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 65

`assert "preliminary_difficulty_observation" in gap["hypothesis"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 66

`assert gap["supporting_evidence_ids"] == [ev["evidence_id"]]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 67

`(blank)`

Blank line used to separate nearby statements.
### Line 68

`# "Why this next?" decision trace`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 69

`dec = data["adaptive_decision"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 70

`assert dec["action"] == "gather_evidence"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 71

`assert dec["trigger"] == "single_prediction_mismatch"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 72

`assert dec["evidence_sufficiency"] == "insufficient"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 73

`assert dec["supporting_evidence_ids"] == [ev["evidence_id"]]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 74

`assert dec["target"] == "act_grover_2q_predict"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 75

`(blank)`

Blank line used to separate nearby statements.
### Line 77

`def test_repeated_error_targeted_remediation_trace():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 78

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 79

`Evaluator Step 2:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 80

`- Repeated prediction mismatch on Attempt 2`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 81

`- Evidence sufficiency = sufficient_for_targeted_inference`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 82

`- Hypothesis = possible difficulty`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 83

`- Action = targeted_remediation`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 84

`- Supporting evidence = Attempt 1 + Attempt 2`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 85

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 86

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 87

`# Attempt 1`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 88

`r1 = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 89

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 90

`json={"learner_id": "u_evaluator_step2", "response": "01"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 91

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 92

`ev1_id = r1.json()["evidence"]["evidence_id"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 93

`(blank)`

Blank line used to separate nearby statements.
### Line 94

`# Attempt 2`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 95

`r2 = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 96

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 97

`json={"learner_id": "u_evaluator_step2", "response": "00"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 98

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 99

`assert r2.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 100

`data = r2.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 101

`ev2_id = data["evidence"]["evidence_id"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 102

`(blank)`

Blank line used to separate nearby statements.
### Line 103

`# Learner-state`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 104

`gap = data["learner_state"]["gap_inferences"]["grover.search_problem"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 105

`assert gap["status"] == "remediation_needed"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 106

`assert gap["trend"] == "persistent_difficulty"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 107

`assert gap["confidence"] == 0.90`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 108

`assert gap["evidence_sufficiency"] == "sufficient_for_targeted_inference"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 109

`assert "possible_grover_search_problem_difficulty" in gap["hypothesis"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 110

`assert gap["supporting_evidence_ids"] == [ev1_id, ev2_id]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 111

`(blank)`

Blank line used to separate nearby statements.
### Line 112

`# "Why this next?"`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 113

`dec = data["adaptive_decision"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 114

`assert dec["action"] == "targeted_remediation"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 115

`assert dec["trigger"] == "repeated_prediction_error"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 116

`assert dec["evidence_sufficiency"] == "sufficient_for_targeted_inference"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 117

`assert dec["supporting_evidence_ids"] == [ev1_id, ev2_id]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 118

`assert dec["target"] == "act_measurement_prob_diagnostic"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 119

`(blank)`

Blank line used to separate nearby statements.
### Line 121

`def test_remediation_success_and_retry_recovery():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 122

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 123

`Evaluator Step 3 & 4:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 124

`- Step 3: Learner completes remediation diagnostic correctly.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 125

`- Step 4: Learner retries Grover and succeeds -> post-intervention improvement -> advance.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 126

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 127

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 128

`# 1. Error on Grover`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 129

`client.post(`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 130

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 131

`json={"learner_id": "u_evaluator_recovery", "response": "01"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 132

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 133

`# 2. Success on Remediation`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 134

`r_remed = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 135

`"/api/activity/act_measurement_prob_diagnostic/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 136

`json={"learner_id": "u_evaluator_recovery", "response": "B"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 137

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 138

`assert r_remed.json()["evidence"]["is_correct"] is True`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 139

`assert r_remed.json()["adaptive_decision"]["action"] == "advance"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 140

`(blank)`

Blank line used to separate nearby statements.
### Line 141

`# 3. Retry Grover Success`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 142

`r_retry = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 143

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 144

`json={"learner_id": "u_evaluator_recovery", "response": "10"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 145

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 146

`data = r_retry.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 147

`(blank)`

Blank line used to separate nearby statements.
### Line 148

`# Verification`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 149

`assert data["evidence"]["is_correct"] is True`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 150

`gap = data["learner_state"]["gap_inferences"]["grover.search_problem"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 151

`assert gap["status"] == "improving"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 152

`assert gap["trend"] == "improving"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 153

`assert gap["confidence"] == 0.15`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 154

`assert gap["evidence_sufficiency"] == "sufficient_for_improvement_observation"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 155

`(blank)`

Blank line used to separate nearby statements.
### Line 156

`dec = data["adaptive_decision"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 157

`assert dec["action"] == "advance"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 158

`assert dec["trigger"] == "post_intervention_recovery"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 159

`assert dec["target"] == "act_grover_iteration_reasoning"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 160

`(blank)`

Blank line used to separate nearby statements.
### Line 162

`def test_ai_explanation_cites_m2_decision_without_overriding():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 163

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 164

`Evaluator Step 5:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 165

`- M5 AI explanation grounds its output in M3 evidence and M2 decision trace.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 166

`- If M5 fails, M2 decision and M3 result remain untouched.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 167

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 168

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 169

`sub = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 170

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 171

`json={"learner_id": "u_m5_grounding_eval", "response": "01"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 172

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 173

`sub_data = sub.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 174

`(blank)`

Blank line used to separate nearby statements.
### Line 175

`ai_res = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 176

`"/api/ai/explain_experiment",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 177

`json={`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 178

`"learner_response": sub_data["learner_response"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 179

`"verified_result": sub_data["verified_result"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 180

`"evidence": sub_data["evidence"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 181

`"adaptive_decision": sub_data["adaptive_decision"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 182

`},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 183

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 184

`assert ai_res.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 185

`ai_data = ai_res.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 186

`assert "Evidence Record" in ai_data["explanation"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 187

`assert "single_prediction_mismatch" in ai_data["explanation"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 188

`(blank)`

Blank line used to separate nearby statements.
### Line 189

`# AI failure isolation`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 190

`class FailingLLM(LLMProvider):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 191

`def generate(self, messages, model=None):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 192

`raise RuntimeError("LLM offline")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 193

`(blank)`

Blank line used to separate nearby statements.
### Line 194

`set_llm_provider(FailingLLM())`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 195

`fail_res = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 196

`"/api/ai/explain_experiment",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 197

`json={`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 198

`"learner_response": sub_data["learner_response"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 199

`"verified_result": sub_data["verified_result"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 200

`"evidence": sub_data["evidence"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 201

`"adaptive_decision": sub_data["adaptive_decision"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 202

`},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 203

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 204

`assert fail_res.status_code == 503`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 205

`# Submission result in client session is untouched`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 206

`assert sub_data["adaptive_decision"]["action"] == "gather_evidence"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.

## Nearby Files

[tests/api/__init__.py](__init__.py.md), [tests/api/test_activities.py](test_activities.py.md), [tests/api/test_adaptive_vertical_slice.py](test_adaptive_vertical_slice.py.md), [tests/api/test_ai.py](test_ai.py.md), [tests/api/test_frontend_adapter_and_binding.py](test_frontend_adapter_and_binding.py.md), [tests/api/test_health.py](test_health.py.md), [tests/api/test_json_contracts.py](test_json_contracts.py.md), [tests/api/test_m1_m6_integration.py](test_m1_m6_integration.py.md)
