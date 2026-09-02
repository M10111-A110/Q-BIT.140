# Explanation: `tests/api/test_m1_m6_integration.py`

## Purpose

This page explains the meaningful behavior in `tests/api/test_m1_m6_integration.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
import json
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


def test_curriculum_journey_activities_contract():
    """
    Verify that GET /api/activities returns all registered MVP activities
    with canonical concept mapping and prerequisites for any client journey track.
    """
    res = client.get("/api/activities")
    assert res.status_code == 200
    activities = res.json()
    assert len(activities) == 4

    act_ids = [a["activity_id"] for a in activities]
    assert "act_grover_2q_predict" in act_ids
    assert "act_measurement_prob_diagnostic" in act_ids
    assert "act_superposition_remediation" in act_ids
    assert "act_grover_iteration_reasoning" in act_ids


def test_quantum_prediction_submission_and_adapter_flow():
    """
    Test end-to-end quantum prediction flow:
      1. Submit prediction '01' to Grover 2Q predict.
      2. M3 executes Aer simulator.
      3. M2 records evidence and sets adaptive decision 'gather_evidence'.
      4. M4 returns verified JSON structure without Qiskit leaks.
    """
    res = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "test_m1_m6_user", "response": "01"},
    )
    assert res.status_code == 200
    data = res.json()

    # Quantum result (for M6 visualization)
    verified = data["verified_result"]
    assert verified["algorithm"] == "grover"
    assert verified["target_state"] == "10"
    assert verified["most_likely_state"] == "10"
    assert verified["target_probability"] >= 0.90
    assert "counts" in verified
    assert "probabilities" in verified
    assert "circuit" in verified
    assert verified["circuit"]["num_qubits"] == 2
    assert "diagram" in verified["circuit"]

    # Evidence & Cognition (for M1 dashboard)
    evidence = data["evidence"]
    assert evidence["is_correct"] is False
    assert evidence["attempt_number"] == 1

    state = data["learner_state"]
    inf = state["gap_inferences"]["grover.search_problem"]
    assert inf["status"] == "observing"
    assert inf["trend"] == "preliminary_observation"
    assert inf["confidence"] == 0.35

    # Adaptive decision (for M1 progression)
    dec = data["adaptive_decision"]
    assert dec["action"] == "gather_evidence"
    assert dec["target"] == "act_grover_2q_predict"


def test_conceptual_choice_submission_and_explanation_flow():
    """
    Test conceptual choice task submission and subsequent M5 explanation request.
    """
    # 1. Submit answer to measurement diagnostic
    sub_res = client.post(
        "/api/activity/act_measurement_prob_diagnostic/submit",
        json={"learner_id": "test_mcq_user", "response": "B"},
    )
    assert sub_res.status_code == 200
    sub_data = sub_res.json()
    assert sub_data["evidence"]["is_correct"] is True
    assert sub_data["adaptive_decision"]["action"] == "advance"

    # 2. Request AI explanation from M5
    exp_res = client.post(
        "/api/ai/explain_experiment",
        json={
            "learner_response": sub_data["learner_response"],
            "verified_result": sub_data.get("verified_result"),
            "evidence": sub_data["evidence"],
            "adaptive_decision": sub_data["adaptive_decision"],
        },
    )
    assert exp_res.status_code == 200
    exp_data = exp_res.json()
    assert "Concept Explanation" in exp_data["explanation"]
    assert "Quantum Execution Analysis" not in exp_data["explanation"]
    assert "Born's rule" in exp_data["explanation"] or "Born" in exp_data["explanation"]
    assert "|B⟩" not in exp_data["explanation"]
    assert "|B\\rangle" not in exp_data["explanation"]



def test_conceptual_ask_inquiry_flow():
    """Test conceptual question inquiry to M5 knowledge base."""
    res = client.post(
        "/api/ai/ask",
        json={
            "question": "What is quantum superposition?",
            "concept_id": "quantum.superposition",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert "question" in data
    assert "answer" in data
    assert "$" in data["answer"]  # KaTeX math present


def test_submission_response_json_schema_completeness():
    """
    Verify that the submission response contains all required fields
    for any arbitrary frontend client to render without missing metadata.
    """
    res = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "schema_test_user", "response": "10"},
    )
    assert res.status_code == 200
    payload = res.json()

    # Verify top-level contract keys
    assert set(payload.keys()) == {
        "activity",
        "learner_response",
        "verified_result",
        "evidence",
        "learner_state",
        "adaptive_decision",
    }

    # Verify JSON serializability
    json_str = json.dumps(payload)
    reconstituted = json.loads(json_str)
    assert reconstituted["activity"]["activity_id"] == "act_grover_2q_predict"
    assert reconstituted["learner_response"] == "10"
    assert reconstituted["adaptive_decision"]["action"] == "advance"

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

`from backend.ai.providers import MockLLMProvider`

Imports a dependency or project symbol so later code can use it by name.
### Line 5

`from backend.api.dependencies import reset_dependencies, set_llm_provider`

Imports a dependency or project symbol so later code can use it by name.
### Line 6

`from backend.api.main import app`

Imports a dependency or project symbol so later code can use it by name.
### Line 7

`(blank)`

Blank line used to separate nearby statements.
### Line 8

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 9

`(blank)`

Blank line used to separate nearby statements.
### Line 11

`@pytest.fixture(autouse=True)`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 12

`def setup_test_environment():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 13

`reset_dependencies()`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 14

`set_llm_provider(MockLLMProvider())`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 15

`yield`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 16

`(blank)`

Blank line used to separate nearby statements.
### Line 18

`def test_curriculum_journey_activities_contract():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 19

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 20

`Verify that GET /api/activities returns all registered MVP activities`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 21

`with canonical concept mapping and prerequisites for any client journey track.`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 22

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 23

`res = client.get("/api/activities")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 24

`assert res.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 25

`activities = res.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 26

`assert len(activities) == 4`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 27

`(blank)`

Blank line used to separate nearby statements.
### Line 28

`act_ids = [a["activity_id"] for a in activities]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 29

`assert "act_grover_2q_predict" in act_ids`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 30

`assert "act_measurement_prob_diagnostic" in act_ids`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 31

`assert "act_superposition_remediation" in act_ids`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 32

`assert "act_grover_iteration_reasoning" in act_ids`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 33

`(blank)`

Blank line used to separate nearby statements.
### Line 35

`def test_quantum_prediction_submission_and_adapter_flow():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 36

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 37

`Test end-to-end quantum prediction flow:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 38

`1. Submit prediction '01' to Grover 2Q predict.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 39

`2. M3 executes Aer simulator.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 40

`3. M2 records evidence and sets adaptive decision 'gather_evidence'.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 41

`4. M4 returns verified JSON structure without Qiskit leaks.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 42

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 43

`res = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 44

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 45

`json={"learner_id": "test_m1_m6_user", "response": "01"},`

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

`# Quantum result (for M6 visualization)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 51

`verified = data["verified_result"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 52

`assert verified["algorithm"] == "grover"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 53

`assert verified["target_state"] == "10"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 54

`assert verified["most_likely_state"] == "10"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 55

`assert verified["target_probability"] >= 0.90`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 56

`assert "counts" in verified`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 57

`assert "probabilities" in verified`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 58

`assert "circuit" in verified`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 59

`assert verified["circuit"]["num_qubits"] == 2`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 60

`assert "diagram" in verified["circuit"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 61

`(blank)`

Blank line used to separate nearby statements.
### Line 62

`# Evidence & Cognition (for M1 dashboard)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 63

`evidence = data["evidence"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 64

`assert evidence["is_correct"] is False`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 65

`assert evidence["attempt_number"] == 1`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 66

`(blank)`

Blank line used to separate nearby statements.
### Line 67

`state = data["learner_state"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 68

`inf = state["gap_inferences"]["grover.search_problem"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 69

`assert inf["status"] == "observing"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 70

`assert inf["trend"] == "preliminary_observation"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 71

`assert inf["confidence"] == 0.35`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 72

`(blank)`

Blank line used to separate nearby statements.
### Line 73

`# Adaptive decision (for M1 progression)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 74

`dec = data["adaptive_decision"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 75

`assert dec["action"] == "gather_evidence"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 76

`assert dec["target"] == "act_grover_2q_predict"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 77

`(blank)`

Blank line used to separate nearby statements.
### Line 79

`def test_conceptual_choice_submission_and_explanation_flow():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 80

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 81

`Test conceptual choice task submission and subsequent M5 explanation request.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 82

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 83

`# 1. Submit answer to measurement diagnostic`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 84

`sub_res = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 85

`"/api/activity/act_measurement_prob_diagnostic/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 86

`json={"learner_id": "test_mcq_user", "response": "B"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 87

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 88

`assert sub_res.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 89

`sub_data = sub_res.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 90

`assert sub_data["evidence"]["is_correct"] is True`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 91

`assert sub_data["adaptive_decision"]["action"] == "advance"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 92

`(blank)`

Blank line used to separate nearby statements.
### Line 93

`# 2. Request AI explanation from M5`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 94

`exp_res = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 95

`"/api/ai/explain_experiment",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 96

`json={`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 97

`"learner_response": sub_data["learner_response"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 98

`"verified_result": sub_data.get("verified_result"),`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 99

`"evidence": sub_data["evidence"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 100

`"adaptive_decision": sub_data["adaptive_decision"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 101

`},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 102

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 103

`assert exp_res.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 104

`exp_data = exp_res.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 105

`assert "Concept Explanation" in exp_data["explanation"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 106

`assert "Quantum Execution Analysis" not in exp_data["explanation"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 107

`assert "Born's rule" in exp_data["explanation"] or "Born" in exp_data["explanation"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 108

`assert "|B⟩" not in exp_data["explanation"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 109

`assert "|B\\rangle" not in exp_data["explanation"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 110

`(blank)`

Blank line used to separate nearby statements.
### Line 113

`def test_conceptual_ask_inquiry_flow():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 114

`"""Test conceptual question inquiry to M5 knowledge base."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 115

`res = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 116

`"/api/ai/ask",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 117

`json={`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 118

`"question": "What is quantum superposition?",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 119

`"concept_id": "quantum.superposition",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 120

`},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 121

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 122

`assert res.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 123

`data = res.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 124

`assert "question" in data`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 125

`assert "answer" in data`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 126

`assert "$" in data["answer"]  # KaTeX math present`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 127

`(blank)`

Blank line used to separate nearby statements.
### Line 129

`def test_submission_response_json_schema_completeness():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 130

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 131

`Verify that the submission response contains all required fields`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 132

`for any arbitrary frontend client to render without missing metadata.`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 133

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 134

`res = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 135

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 136

`json={"learner_id": "schema_test_user", "response": "10"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 137

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 138

`assert res.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 139

`payload = res.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 140

`(blank)`

Blank line used to separate nearby statements.
### Line 141

`# Verify top-level contract keys`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 142

`assert set(payload.keys()) == {`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 143

`"activity",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 144

`"learner_response",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 145

`"verified_result",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 146

`"evidence",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 147

`"learner_state",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 148

`"adaptive_decision",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 149

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 150

`(blank)`

Blank line used to separate nearby statements.
### Line 151

`# Verify JSON serializability`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 152

`json_str = json.dumps(payload)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 153

`reconstituted = json.loads(json_str)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 154

`assert reconstituted["activity"]["activity_id"] == "act_grover_2q_predict"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 155

`assert reconstituted["learner_response"] == "10"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 156

`assert reconstituted["adaptive_decision"]["action"] == "advance"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.

## Nearby Files

[tests/api/__init__.py](__init__.py.md), [tests/api/test_activities.py](test_activities.py.md), [tests/api/test_adaptive_vertical_slice.py](test_adaptive_vertical_slice.py.md), [tests/api/test_ai.py](test_ai.py.md), [tests/api/test_frontend_adapter_and_binding.py](test_frontend_adapter_and_binding.py.md), [tests/api/test_health.py](test_health.py.md), [tests/api/test_json_contracts.py](test_json_contracts.py.md), [tests/api/test_m6_adapter.py](test_m6_adapter.py.md)
