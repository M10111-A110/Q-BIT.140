# Explanation: `tests/api/test_activities.py`

## Purpose

This page explains the meaningful behavior in `tests/api/test_activities.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
from fastapi.testclient import TestClient
from backend.api.main import app

client = TestClient(app)


def test_get_all_activities():
    response = client.get("/api/activities")
    assert response.status_code == 200
    activities = response.json()
    assert len(activities) == 4
    act_ids = [a["activity_id"] for a in activities]
    assert "act_grover_2q_predict" in act_ids
    assert "act_measurement_prob_diagnostic" in act_ids


def test_get_activity_detail():
    response = client.get("/api/activity/act_grover_2q_predict")
    assert response.status_code == 200
    data = response.json()
    assert data["activity_id"] == "act_grover_2q_predict"
    assert data["concept_id"] == "grover.search_problem"
    assert data["task_type"] == "quantum_prediction"
    assert data["quantum_experiment"] is not None
    assert data["quantum_experiment"]["algorithm"] == "grover"
    assert data["quantum_experiment"]["num_qubits"] == 2
    assert data["remediation_activity_id"] == "act_measurement_prob_diagnostic"


def test_get_activity_unknown_returns_404():
    response = client.get("/api/activity/non_existent_activity")
    assert response.status_code == 404
    assert "Activity 'non_existent_activity' not found" in response.json()["detail"]

```

## Line Notes

### Line 1

`from fastapi.testclient import TestClient`

Imports a dependency or project symbol so later code can use it by name.
### Line 2

`from backend.api.main import app`

Imports a dependency or project symbol so later code can use it by name.
### Line 3

`(blank)`

Blank line used to separate nearby statements.
### Line 4

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 5

`(blank)`

Blank line used to separate nearby statements.
### Line 7

`def test_get_all_activities():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 8

`response = client.get("/api/activities")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 9

`assert response.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 10

`activities = response.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 11

`assert len(activities) == 4`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 12

`act_ids = [a["activity_id"] for a in activities]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 13

`assert "act_grover_2q_predict" in act_ids`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 14

`assert "act_measurement_prob_diagnostic" in act_ids`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 15

`(blank)`

Blank line used to separate nearby statements.
### Line 17

`def test_get_activity_detail():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 18

`response = client.get("/api/activity/act_grover_2q_predict")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 19

`assert response.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 20

`data = response.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 21

`assert data["activity_id"] == "act_grover_2q_predict"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 22

`assert data["concept_id"] == "grover.search_problem"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 23

`assert data["task_type"] == "quantum_prediction"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 24

`assert data["quantum_experiment"] is not None`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 25

`assert data["quantum_experiment"]["algorithm"] == "grover"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 26

`assert data["quantum_experiment"]["num_qubits"] == 2`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 27

`assert data["remediation_activity_id"] == "act_measurement_prob_diagnostic"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 28

`(blank)`

Blank line used to separate nearby statements.
### Line 30

`def test_get_activity_unknown_returns_404():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 31

`response = client.get("/api/activity/non_existent_activity")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 32

`assert response.status_code == 404`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 33

`assert "Activity 'non_existent_activity' not found" in response.json()["detail"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.

## Nearby Files

[tests/api/__init__.py](__init__.py.md), [tests/api/test_adaptive_vertical_slice.py](test_adaptive_vertical_slice.py.md), [tests/api/test_ai.py](test_ai.py.md), [tests/api/test_frontend_adapter_and_binding.py](test_frontend_adapter_and_binding.py.md), [tests/api/test_health.py](test_health.py.md), [tests/api/test_json_contracts.py](test_json_contracts.py.md), [tests/api/test_m1_m6_integration.py](test_m1_m6_integration.py.md), [tests/api/test_m6_adapter.py](test_m6_adapter.py.md)
