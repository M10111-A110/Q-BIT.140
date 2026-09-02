# Explanation: `tests/api/test_m6_adapter.py`

## Purpose

This page explains the meaningful behavior in `tests/api/test_m6_adapter.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

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


def test_m4_response_provides_all_fields_for_m6_adapter():
    """
    Verify that the M4 submission response contains 100% of the fields
    required by the M6 frontend visualization adapter.
    """
    res = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "usr_m6_test", "response": "01"},
    )
    assert res.status_code == 200
    data = res.json()

    # 1. Quantum Result fields
    verified = data.get("verified_result")
    assert verified is not None
    assert "target_state" in verified
    assert "most_likely_state" in verified
    assert "target_probability" in verified
    assert "shots" in verified
    assert "counts" in verified
    assert "probabilities" in verified
    assert "circuit" in verified

    # Probability distribution verification
    probabilities = verified["probabilities"]
    assert isinstance(probabilities, dict)
    assert "10" in probabilities
    assert sum(probabilities.values()) == pytest.approx(1.0, rel=1e-2)

    # Circuit metadata verification
    circuit = verified["circuit"]
    assert circuit["num_qubits"] == 2
    assert circuit["depth"] > 0
    assert "diagram" in circuit
    assert isinstance(circuit["diagram"], str)

    # 2. Learner & Evidence fields
    evidence = data.get("evidence")
    assert evidence is not None
    assert evidence["learner_id"] == "usr_m6_test"
    assert evidence["is_correct"] is False
    assert "evaluation_details" in evidence

    # 3. Adaptive Decision fields
    decision = data.get("adaptive_decision")
    assert decision is not None
    assert decision["action"] == "gather_evidence"
    assert "reason" in decision
    assert decision["target"] == "act_grover_2q_predict"


def test_m6_histogram_data_pass_through():
    """
    Verify that probabilities and counts pass directly from M3 through M4
    without alteration or loss of resolution.
    """
    res = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "usr_hist_test", "response": "10"},
    )
    assert res.status_code == 200
    data = res.json()
    verified = data["verified_result"]

    # Target state |10> must have the highest count and probability >= 0.90
    target_state = verified["target_state"]
    assert target_state == "10"
    assert verified["most_likely_state"] == "10"

    probs = verified["probabilities"]
    assert probs["10"] >= 0.90
    assert verified["target_probability"] >= 0.90

    counts = verified["counts"]
    assert counts["10"] >= 900
    assert sum(counts.values()) == verified["shots"]


def test_m6_explanation_hook_connected():
    """
    Verify that M6 can take the exact submit output and invoke POST /api/ai/explain_experiment.
    """
    submit_res = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "usr_explain_test", "response": "01"},
    )
    assert submit_res.status_code == 200
    submit_data = submit_res.json()

    explain_res = client.post(
        "/api/ai/explain_experiment",
        json={
            "learner_response": submit_data["learner_response"],
            "verified_result": submit_data["verified_result"],
            "evidence": submit_data["evidence"],
            "adaptive_decision": submit_data["adaptive_decision"],
        },
    )
    assert explain_res.status_code == 200
    explain_data = explain_res.json()
    assert "Quantum Execution Analysis" in explain_data["explanation"]
    assert explain_data["adaptive_decision"]["action"] == "gather_evidence"

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

`def test_m4_response_provides_all_fields_for_m6_adapter():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 19

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 20

`Verify that the M4 submission response contains 100% of the fields`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 21

`required by the M6 frontend visualization adapter.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 22

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 23

`res = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 24

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 25

`json={"learner_id": "usr_m6_test", "response": "01"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 26

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 27

`assert res.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 28

`data = res.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 29

`(blank)`

Blank line used to separate nearby statements.
### Line 30

`# 1. Quantum Result fields`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 31

`verified = data.get("verified_result")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 32

`assert verified is not None`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 33

`assert "target_state" in verified`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 34

`assert "most_likely_state" in verified`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 35

`assert "target_probability" in verified`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 36

`assert "shots" in verified`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 37

`assert "counts" in verified`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 38

`assert "probabilities" in verified`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 39

`assert "circuit" in verified`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 40

`(blank)`

Blank line used to separate nearby statements.
### Line 41

`# Probability distribution verification`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 42

`probabilities = verified["probabilities"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 43

`assert isinstance(probabilities, dict)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 44

`assert "10" in probabilities`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 45

`assert sum(probabilities.values()) == pytest.approx(1.0, rel=1e-2)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 46

`(blank)`

Blank line used to separate nearby statements.
### Line 47

`# Circuit metadata verification`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 48

`circuit = verified["circuit"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 49

`assert circuit["num_qubits"] == 2`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 50

`assert circuit["depth"] > 0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 51

`assert "diagram" in circuit`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 52

`assert isinstance(circuit["diagram"], str)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 53

`(blank)`

Blank line used to separate nearby statements.
### Line 54

`# 2. Learner & Evidence fields`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 55

`evidence = data.get("evidence")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 56

`assert evidence is not None`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 57

`assert evidence["learner_id"] == "usr_m6_test"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 58

`assert evidence["is_correct"] is False`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 59

`assert "evaluation_details" in evidence`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 60

`(blank)`

Blank line used to separate nearby statements.
### Line 61

`# 3. Adaptive Decision fields`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 62

`decision = data.get("adaptive_decision")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 63

`assert decision is not None`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 64

`assert decision["action"] == "gather_evidence"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 65

`assert "reason" in decision`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 66

`assert decision["target"] == "act_grover_2q_predict"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 67

`(blank)`

Blank line used to separate nearby statements.
### Line 69

`def test_m6_histogram_data_pass_through():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 70

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 71

`Verify that probabilities and counts pass directly from M3 through M4`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 72

`without alteration or loss of resolution.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 73

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 74

`res = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 75

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 76

`json={"learner_id": "usr_hist_test", "response": "10"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 77

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 78

`assert res.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 79

`data = res.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 80

`verified = data["verified_result"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 81

`(blank)`

Blank line used to separate nearby statements.
### Line 82

`# Target state |10> must have the highest count and probability >= 0.90`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 83

`target_state = verified["target_state"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 84

`assert target_state == "10"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 85

`assert verified["most_likely_state"] == "10"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 86

`(blank)`

Blank line used to separate nearby statements.
### Line 87

`probs = verified["probabilities"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 88

`assert probs["10"] >= 0.90`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 89

`assert verified["target_probability"] >= 0.90`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 90

`(blank)`

Blank line used to separate nearby statements.
### Line 91

`counts = verified["counts"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 92

`assert counts["10"] >= 900`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 93

`assert sum(counts.values()) == verified["shots"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 94

`(blank)`

Blank line used to separate nearby statements.
### Line 96

`def test_m6_explanation_hook_connected():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 97

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 98

`Verify that M6 can take the exact submit output and invoke POST /api/ai/explain_experiment.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 99

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 100

`submit_res = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 101

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 102

`json={"learner_id": "usr_explain_test", "response": "01"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 103

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 104

`assert submit_res.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 105

`submit_data = submit_res.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 106

`(blank)`

Blank line used to separate nearby statements.
### Line 107

`explain_res = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 108

`"/api/ai/explain_experiment",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 109

`json={`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 110

`"learner_response": submit_data["learner_response"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 111

`"verified_result": submit_data["verified_result"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 112

`"evidence": submit_data["evidence"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 113

`"adaptive_decision": submit_data["adaptive_decision"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 114

`},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 115

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 116

`assert explain_res.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 117

`explain_data = explain_res.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 118

`assert "Quantum Execution Analysis" in explain_data["explanation"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 119

`assert explain_data["adaptive_decision"]["action"] == "gather_evidence"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.

## Nearby Files

[tests/api/__init__.py](__init__.py.md), [tests/api/test_activities.py](test_activities.py.md), [tests/api/test_adaptive_vertical_slice.py](test_adaptive_vertical_slice.py.md), [tests/api/test_ai.py](test_ai.py.md), [tests/api/test_frontend_adapter_and_binding.py](test_frontend_adapter_and_binding.py.md), [tests/api/test_health.py](test_health.py.md), [tests/api/test_json_contracts.py](test_json_contracts.py.md), [tests/api/test_m1_m6_integration.py](test_m1_m6_integration.py.md)
