# Explanation: `tests/api/test_submissions.py`

## Purpose

This page explains the meaningful behavior in `tests/api/test_submissions.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
import pytest
from fastapi.testclient import TestClient
from backend.api.dependencies import reset_dependencies
from backend.api.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_state():
    """Reset in-memory repository before each test to ensure test isolation."""
    reset_dependencies()
    yield


def test_submit_unknown_activity_returns_404():
    response = client.post(
        "/api/activity/non_existent_activity/submit",
        json={"learner_id": "u1", "response": "01"},
    )
    assert response.status_code == 404
    assert "Activity 'non_existent_activity' not found" in response.json()["detail"]


def test_submit_invalid_payload_returns_422():
    # Empty learner_id
    response = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "", "response": "01"},
    )
    assert response.status_code == 422

    # Missing response field
    response2 = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u1"},
    )
    assert response2.status_code == 422


def test_successful_quantum_prediction_executes_real_m3():
    response = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "learner_test_01", "response": "10"},
    )
    assert response.status_code == 200
    data = response.json()

    # 1. Activity metadata
    assert data["activity"]["activity_id"] == "act_grover_2q_predict"
    assert data["learner_response"] == "10"

    # 2. Verified M3 simulation result
    verified = data["verified_result"]
    assert verified is not None
    assert verified["algorithm"] == "grover"
    assert verified["target_state"] == "10"
    assert verified["most_likely_state"] == "10"
    assert verified["target_probability"] > 0.90
    assert "counts" in verified
    assert "probabilities" in verified
    assert "circuit" in verified
    assert verified["circuit"]["num_qubits"] == 2

    # 3. Learner Evidence
    evidence = data["evidence"]
    assert evidence["learner_id"] == "learner_test_01"
    assert evidence["is_correct"] is True
    assert evidence["evaluation_details"]["match"] is True

    # 4. Adaptive Decision
    decision = data["adaptive_decision"]
    assert decision["action"] == "advance"
    assert decision["target"] == "act_grover_iteration_reasoning"


def test_multi_request_evidence_accumulation_and_remediation_loop():
    """
    Test the full multi-request learner workflow across HTTP API:
      Request 1: Submit incorrect prediction "01" -> gathers evidence (low confidence)
      Request 2: Submit 2nd incorrect prediction "00" -> triggers targeted remediation
      Request 3: Submit correct remediation option "B" -> routes back to Grover task
      Request 4: Submit correct prediction "10" -> advances to next activity
    """
    learner_id = "learner_loop_user"

    # Request 1: 1st incorrect prediction
    r1 = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": learner_id, "response": "01"},
    )
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1["evidence"]["is_correct"] is False
    assert d1["adaptive_decision"]["action"] == "gather_evidence"
    assert d1["adaptive_decision"]["target"] == "act_grover_2q_predict"
    assert len(d1["learner_state"]["evidence_history"]) == 1

    # Request 2: 2nd incorrect prediction on same activity (same learner_id)
    r2 = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": learner_id, "response": "00"},
    )
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["evidence"]["is_correct"] is False
    assert d2["adaptive_decision"]["action"] == "targeted_remediation"
    assert d2["adaptive_decision"]["target"] == "act_measurement_prob_diagnostic"
    assert len(d2["learner_state"]["evidence_history"]) == 2
    assert d2["learner_state"]["gap_inferences"]["grover.search_problem"]["confidence"] == 0.90

    # Request 3: Submit remediation activity with correct answer "B"
    r3 = client.post(
        "/api/activity/act_measurement_prob_diagnostic/submit",
        json={"learner_id": learner_id, "response": "B"},
    )
    assert r3.status_code == 200
    d3 = r3.json()
    assert d3["evidence"]["is_correct"] is True
    assert d3["adaptive_decision"]["action"] == "advance"
    assert d3["adaptive_decision"]["target"] == "act_grover_2q_predict"
    assert len(d3["learner_state"]["evidence_history"]) == 3

    # Request 4: Re-attempt Grover prediction with correct state "10"
    r4 = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": learner_id, "response": "10"},
    )
    assert r4.status_code == 200
    d4 = r4.json()
    assert d4["evidence"]["is_correct"] is True
    assert d4["adaptive_decision"]["action"] == "advance"
    assert d4["adaptive_decision"]["target"] == "act_grover_iteration_reasoning"
    assert len(d4["learner_state"]["evidence_history"]) == 4
    assert d4["learner_state"]["gap_inferences"]["grover.search_problem"]["status"] == "improving"

```

## Line Notes

### Line 1

`import pytest`

Imports a dependency or project symbol so later code can use it by name.
### Line 2

`from fastapi.testclient import TestClient`

Imports a dependency or project symbol so later code can use it by name.
### Line 3

`from backend.api.dependencies import reset_dependencies`

Imports a dependency or project symbol so later code can use it by name.
### Line 4

`from backend.api.main import app`

Imports a dependency or project symbol so later code can use it by name.
### Line 5

`(blank)`

Blank line used to separate nearby statements.
### Line 6

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 7

`(blank)`

Blank line used to separate nearby statements.
### Line 9

`@pytest.fixture(autouse=True)`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 10

`def clean_state():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 11

`"""Reset in-memory repository before each test to ensure test isolation."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 12

`reset_dependencies()`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 13

`yield`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 14

`(blank)`

Blank line used to separate nearby statements.
### Line 16

`def test_submit_unknown_activity_returns_404():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 17

`response = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 18

`"/api/activity/non_existent_activity/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 19

`json={"learner_id": "u1", "response": "01"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 20

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 21

`assert response.status_code == 404`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 22

`assert "Activity 'non_existent_activity' not found" in response.json()["detail"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 23

`(blank)`

Blank line used to separate nearby statements.
### Line 25

`def test_submit_invalid_payload_returns_422():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 26

`# Empty learner_id`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 27

`response = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 28

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 29

`json={"learner_id": "", "response": "01"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 30

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 31

`assert response.status_code == 422`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 32

`(blank)`

Blank line used to separate nearby statements.
### Line 33

`# Missing response field`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 34

`response2 = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 35

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 36

`json={"learner_id": "u1"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 37

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 38

`assert response2.status_code == 422`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 39

`(blank)`

Blank line used to separate nearby statements.
### Line 41

`def test_successful_quantum_prediction_executes_real_m3():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 42

`response = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 43

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 44

`json={"learner_id": "learner_test_01", "response": "10"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 45

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 46

`assert response.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 47

`data = response.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 48

`(blank)`

Blank line used to separate nearby statements.
### Line 49

`# 1. Activity metadata`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 50

`assert data["activity"]["activity_id"] == "act_grover_2q_predict"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 51

`assert data["learner_response"] == "10"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 52

`(blank)`

Blank line used to separate nearby statements.
### Line 53

`# 2. Verified M3 simulation result`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 54

`verified = data["verified_result"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 55

`assert verified is not None`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 56

`assert verified["algorithm"] == "grover"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 57

`assert verified["target_state"] == "10"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 58

`assert verified["most_likely_state"] == "10"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 59

`assert verified["target_probability"] > 0.90`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 60

`assert "counts" in verified`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 61

`assert "probabilities" in verified`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 62

`assert "circuit" in verified`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 63

`assert verified["circuit"]["num_qubits"] == 2`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 64

`(blank)`

Blank line used to separate nearby statements.
### Line 65

`# 3. Learner Evidence`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 66

`evidence = data["evidence"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 67

`assert evidence["learner_id"] == "learner_test_01"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 68

`assert evidence["is_correct"] is True`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 69

`assert evidence["evaluation_details"]["match"] is True`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 70

`(blank)`

Blank line used to separate nearby statements.
### Line 71

`# 4. Adaptive Decision`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 72

`decision = data["adaptive_decision"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 73

`assert decision["action"] == "advance"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 74

`assert decision["target"] == "act_grover_iteration_reasoning"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 75

`(blank)`

Blank line used to separate nearby statements.
### Line 77

`def test_multi_request_evidence_accumulation_and_remediation_loop():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 78

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 79

`Test the full multi-request learner workflow across HTTP API:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 80

`Request 1: Submit incorrect prediction "01" -> gathers evidence (low confidence)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 81

`Request 2: Submit 2nd incorrect prediction "00" -> triggers targeted remediation`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 82

`Request 3: Submit correct remediation option "B" -> routes back to Grover task`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 83

`Request 4: Submit correct prediction "10" -> advances to next activity`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 84

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 85

`learner_id = "learner_loop_user"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 86

`(blank)`

Blank line used to separate nearby statements.
### Line 87

`# Request 1: 1st incorrect prediction`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 88

`r1 = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 89

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 90

`json={"learner_id": learner_id, "response": "01"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 91

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 92

`assert r1.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 93

`d1 = r1.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 94

`assert d1["evidence"]["is_correct"] is False`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 95

`assert d1["adaptive_decision"]["action"] == "gather_evidence"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 96

`assert d1["adaptive_decision"]["target"] == "act_grover_2q_predict"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 97

`assert len(d1["learner_state"]["evidence_history"]) == 1`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 98

`(blank)`

Blank line used to separate nearby statements.
### Line 99

`# Request 2: 2nd incorrect prediction on same activity (same learner_id)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 100

`r2 = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 101

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 102

`json={"learner_id": learner_id, "response": "00"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 103

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 104

`assert r2.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 105

`d2 = r2.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 106

`assert d2["evidence"]["is_correct"] is False`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 107

`assert d2["adaptive_decision"]["action"] == "targeted_remediation"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 108

`assert d2["adaptive_decision"]["target"] == "act_measurement_prob_diagnostic"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 109

`assert len(d2["learner_state"]["evidence_history"]) == 2`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 110

`assert d2["learner_state"]["gap_inferences"]["grover.search_problem"]["confidence"] == 0.90`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 111

`(blank)`

Blank line used to separate nearby statements.
### Line 112

`# Request 3: Submit remediation activity with correct answer "B"`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 113

`r3 = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 114

`"/api/activity/act_measurement_prob_diagnostic/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 115

`json={"learner_id": learner_id, "response": "B"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 116

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 117

`assert r3.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 118

`d3 = r3.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 119

`assert d3["evidence"]["is_correct"] is True`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 120

`assert d3["adaptive_decision"]["action"] == "advance"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 121

`assert d3["adaptive_decision"]["target"] == "act_grover_2q_predict"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 122

`assert len(d3["learner_state"]["evidence_history"]) == 3`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 123

`(blank)`

Blank line used to separate nearby statements.
### Line 124

`# Request 4: Re-attempt Grover prediction with correct state "10"`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 125

`r4 = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 126

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 127

`json={"learner_id": learner_id, "response": "10"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 128

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 129

`assert r4.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 130

`d4 = r4.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 131

`assert d4["evidence"]["is_correct"] is True`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 132

`assert d4["adaptive_decision"]["action"] == "advance"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 133

`assert d4["adaptive_decision"]["target"] == "act_grover_iteration_reasoning"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 134

`assert len(d4["learner_state"]["evidence_history"]) == 4`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 135

`assert d4["learner_state"]["gap_inferences"]["grover.search_problem"]["status"] == "improving"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.

## Nearby Files

[tests/api/__init__.py](__init__.py.md), [tests/api/test_activities.py](test_activities.py.md), [tests/api/test_adaptive_vertical_slice.py](test_adaptive_vertical_slice.py.md), [tests/api/test_ai.py](test_ai.py.md), [tests/api/test_frontend_adapter_and_binding.py](test_frontend_adapter_and_binding.py.md), [tests/api/test_health.py](test_health.py.md), [tests/api/test_json_contracts.py](test_json_contracts.py.md), [tests/api/test_m1_m6_integration.py](test_m1_m6_integration.py.md)
