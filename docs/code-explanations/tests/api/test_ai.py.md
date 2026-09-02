# Explanation: `tests/api/test_ai.py`

## Purpose

This page explains the meaningful behavior in `tests/api/test_ai.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
import pytest
from fastapi.testclient import TestClient
from backend.ai.providers import MockLLMProvider
from backend.api.dependencies import reset_dependencies, set_llm_provider
from backend.api.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_environment():
    reset_dependencies()
    set_llm_provider(MockLLMProvider())
    yield


def test_ai_ask_valid_question():
    response = client.post(
        "/api/ai/ask",
        json={
            "question": "What is the role of the oracle in Grover's algorithm?",
            "concept_id": "grover.search_problem",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == "What is the role of the oracle in Grover's algorithm?"
    assert "Grover" in data["answer"]
    assert "$" in data["answer"]


def test_ai_ask_validation_failure():
    # Empty question
    response = client.post("/api/ai/ask", json={"question": ""})
    assert response.status_code == 422


def test_ai_explain_experiment_valid():
    response = client.post(
        "/api/ai/explain_experiment",
        json={
            "learner_response": "01",
            "verified_result": {
                "algorithm": "grover",
                "target_state": "10",
                "shots": 1024,
                "most_likely_state": "10",
                "target_probability": 0.934,
            },
            "evidence": {
                "concept_id": "grover.search_problem",
                "is_correct": False,
                "evaluation_details": {
                    "predicted_state": "01",
                    "most_likely_state": "10",
                    "match": False,
                },
            },
            "adaptive_decision": {
                "action": "gather_evidence",
                "target": "act_grover_2q_predict",
                "reason": "Initial prediction mismatch. Gathering additional evidence.",
            },
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "Quantum Execution Analysis" in data["explanation"]
    assert data["learner_response"] == "01"
    assert data["adaptive_decision"]["action"] == "gather_evidence"


def test_full_connected_loop_with_m3_m2_m4_m5():
    """
    Full End-to-End Workflow Verification:
      1. Fetch Activity via GET /api/activity/act_grover_2q_predict
      2. Submit attempt via POST /api/activity/act_grover_2q_predict/submit
         - Triggers REAL M3 Aer quantum execution
         - Produces verified SimulationResult
         - Ingests into M2 LearnerModel
         - Computes deterministic AdaptiveRecommendation
      3. Pass verified output into POST /api/ai/explain_experiment
         - M5 retrieves grounded knowledge
         - Explains experiment without modifying quantum result or adaptive decision!
    """
    # 1. Get Activity
    act_resp = client.get("/api/activity/act_grover_2q_predict")
    assert act_resp.status_code == 200
    act_data = act_resp.json()

    # 2. Submit Learner Attempt (Incorrect prediction "01")
    submit_resp = client.post(
        f"/api/activity/{act_data['activity_id']}/submit",
        json={"learner_id": "integration_user_01", "response": "01"},
    )
    assert submit_resp.status_code == 200
    submit_data = submit_resp.json()

    verified = submit_data["verified_result"]
    assert verified["most_likely_state"] == "10"
    assert verified["algorithm"] == "grover"

    evidence = submit_data["evidence"]
    assert evidence["is_correct"] is False

    decision = submit_data["adaptive_decision"]
    assert decision["action"] == "gather_evidence"

    # 3. Request M5 Grounded Explanation of the Attempt
    ai_resp = client.post(
        "/api/ai/explain_experiment",
        json={
            "learner_response": submit_data["learner_response"],
            "verified_result": verified,
            "evidence": evidence,
            "adaptive_decision": decision,
            "user_question": "Why did |10> have the highest probability?",
        },
    )
    assert ai_resp.status_code == 200
    ai_data = ai_resp.json()

    assert "Quantum Execution Analysis" in ai_data["explanation"]
    assert ai_data["learner_response"] == "01"
    # M5 preserved M2's decision exactly
    assert ai_data["adaptive_decision"]["action"] == "gather_evidence"

```

## Line Notes

### Line 1

`import pytest`

Imports a dependency or project symbol so later code can use it by name.
### Line 2

`from fastapi.testclient import TestClient`

Imports a dependency or project symbol so later code can use it by name.
### Line 3

`from backend.ai.providers import MockLLMProvider`

Imports a dependency or project symbol so later code can use it by name.
### Line 4

`from backend.api.dependencies import reset_dependencies, set_llm_provider`

Imports a dependency or project symbol so later code can use it by name.
### Line 5

`from backend.api.main import app`

Imports a dependency or project symbol so later code can use it by name.
### Line 6

`(blank)`

Blank line used to separate nearby statements.
### Line 7

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 8

`(blank)`

Blank line used to separate nearby statements.
### Line 10

`@pytest.fixture(autouse=True)`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 11

`def setup_test_environment():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 12

`reset_dependencies()`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 13

`set_llm_provider(MockLLMProvider())`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 14

`yield`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 15

`(blank)`

Blank line used to separate nearby statements.
### Line 17

`def test_ai_ask_valid_question():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 18

`response = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 19

`"/api/ai/ask",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 20

`json={`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 21

`"question": "What is the role of the oracle in Grover's algorithm?",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 22

`"concept_id": "grover.search_problem",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 23

`},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 24

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 25

`assert response.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 26

`data = response.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 27

`assert data["question"] == "What is the role of the oracle in Grover's algorithm?"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 28

`assert "Grover" in data["answer"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 29

`assert "$" in data["answer"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 30

`(blank)`

Blank line used to separate nearby statements.
### Line 32

`def test_ai_ask_validation_failure():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 33

`# Empty question`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 34

`response = client.post("/api/ai/ask", json={"question": ""})`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 35

`assert response.status_code == 422`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 36

`(blank)`

Blank line used to separate nearby statements.
### Line 38

`def test_ai_explain_experiment_valid():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 39

`response = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 40

`"/api/ai/explain_experiment",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 41

`json={`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 42

`"learner_response": "01",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 43

`"verified_result": {`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 44

`"algorithm": "grover",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 45

`"target_state": "10",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 46

`"shots": 1024,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 47

`"most_likely_state": "10",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 48

`"target_probability": 0.934,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 49

`},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 50

`"evidence": {`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 51

`"concept_id": "grover.search_problem",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 52

`"is_correct": False,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 53

`"evaluation_details": {`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 54

`"predicted_state": "01",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 55

`"most_likely_state": "10",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 56

`"match": False,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 57

`},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 58

`},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 59

`"adaptive_decision": {`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 60

`"action": "gather_evidence",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 61

`"target": "act_grover_2q_predict",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 62

`"reason": "Initial prediction mismatch. Gathering additional evidence.",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 63

`},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 64

`},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 65

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 66

`assert response.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 67

`data = response.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 68

`assert "Quantum Execution Analysis" in data["explanation"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 69

`assert data["learner_response"] == "01"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 70

`assert data["adaptive_decision"]["action"] == "gather_evidence"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 71

`(blank)`

Blank line used to separate nearby statements.
### Line 73

`def test_full_connected_loop_with_m3_m2_m4_m5():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 74

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 75

`Full End-to-End Workflow Verification:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 76

`1. Fetch Activity via GET /api/activity/act_grover_2q_predict`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 77

`2. Submit attempt via POST /api/activity/act_grover_2q_predict/submit`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 78

`- Triggers REAL M3 Aer quantum execution`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 79

`- Produces verified SimulationResult`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 80

`- Ingests into M2 LearnerModel`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 81

`- Computes deterministic AdaptiveRecommendation`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 82

`3. Pass verified output into POST /api/ai/explain_experiment`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 83

`- M5 retrieves grounded knowledge`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 84

`- Explains experiment without modifying quantum result or adaptive decision!`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 85

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 86

`# 1. Get Activity`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 87

`act_resp = client.get("/api/activity/act_grover_2q_predict")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 88

`assert act_resp.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 89

`act_data = act_resp.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 90

`(blank)`

Blank line used to separate nearby statements.
### Line 91

`# 2. Submit Learner Attempt (Incorrect prediction "01")`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 92

`submit_resp = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 93

`f"/api/activity/{act_data['activity_id']}/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 94

`json={"learner_id": "integration_user_01", "response": "01"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 95

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 96

`assert submit_resp.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 97

`submit_data = submit_resp.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 98

`(blank)`

Blank line used to separate nearby statements.
### Line 99

`verified = submit_data["verified_result"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 100

`assert verified["most_likely_state"] == "10"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 101

`assert verified["algorithm"] == "grover"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 102

`(blank)`

Blank line used to separate nearby statements.
### Line 103

`evidence = submit_data["evidence"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 104

`assert evidence["is_correct"] is False`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 105

`(blank)`

Blank line used to separate nearby statements.
### Line 106

`decision = submit_data["adaptive_decision"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 107

`assert decision["action"] == "gather_evidence"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 108

`(blank)`

Blank line used to separate nearby statements.
### Line 109

`# 3. Request M5 Grounded Explanation of the Attempt`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 110

`ai_resp = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 111

`"/api/ai/explain_experiment",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 112

`json={`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 113

`"learner_response": submit_data["learner_response"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 114

`"verified_result": verified,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 115

`"evidence": evidence,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 116

`"adaptive_decision": decision,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 117

`"user_question": "Why did |10> have the highest probability?",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 118

`},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 119

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 120

`assert ai_resp.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 121

`ai_data = ai_resp.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 122

`(blank)`

Blank line used to separate nearby statements.
### Line 123

`assert "Quantum Execution Analysis" in ai_data["explanation"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 124

`assert ai_data["learner_response"] == "01"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 125

`# M5 preserved M2's decision exactly`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 126

`assert ai_data["adaptive_decision"]["action"] == "gather_evidence"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.

## Nearby Files

[tests/api/__init__.py](__init__.py.md), [tests/api/test_activities.py](test_activities.py.md), [tests/api/test_adaptive_vertical_slice.py](test_adaptive_vertical_slice.py.md), [tests/api/test_frontend_adapter_and_binding.py](test_frontend_adapter_and_binding.py.md), [tests/api/test_health.py](test_health.py.md), [tests/api/test_json_contracts.py](test_json_contracts.py.md), [tests/api/test_m1_m6_integration.py](test_m1_m6_integration.py.md), [tests/api/test_m6_adapter.py](test_m6_adapter.py.md)
