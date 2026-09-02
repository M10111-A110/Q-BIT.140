# Explanation: `tests/adaptive/test_activities.py`

## Purpose

This page explains the meaningful behavior in `tests/adaptive/test_activities.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
import pytest
from backend.adaptive.activities import (
    MVP_ACTIVITIES,
    Activity,
    get_activities_for_concept,
    get_activity,
    list_activities,
)


def test_activities_registry_contains_expected_core_activities():
    activities = list_activities()
    assert len(activities) == 4

    ids = [a.activity_id for a in activities]
    assert "act_grover_2q_predict" in ids
    assert "act_measurement_prob_diagnostic" in ids
    assert "act_superposition_remediation" in ids
    assert "act_grover_iteration_reasoning" in ids


def test_get_activity_by_id():
    act = get_activity("act_grover_2q_predict")
    assert act.activity_id == "act_grover_2q_predict"
    assert act.task_type == "quantum_prediction"
    assert act.concept_id == "grover.search_problem"
    assert act.quantum_experiment is not None
    assert act.quantum_experiment["algorithm"] == "grover"
    assert act.quantum_experiment["num_qubits"] == 2
    assert act.quantum_experiment["target_state"] == "10"
    assert act.remediation_activity_id == "act_measurement_prob_diagnostic"
    assert act.next_activity_id == "act_grover_iteration_reasoning"


def test_get_activity_unknown_raises_key_error():
    with pytest.raises(KeyError):
        get_activity("unknown_activity_xyz")


def test_get_activities_for_concept():
    acts = get_activities_for_concept("quantum.measurement")
    assert len(acts) == 1
    assert acts[0].activity_id == "act_measurement_prob_diagnostic"


def test_activity_to_dict():
    act = get_activity("act_superposition_remediation")
    d = act.to_dict()
    assert d["activity_id"] == "act_superposition_remediation"
    assert d["expected_answer"] == "B"
    assert "options" in d
    assert "B" in d["options"]

```

## Line Notes

### Line 1

`import pytest`

Imports a dependency or project symbol so later code can use it by name.
### Line 2

`from backend.adaptive.activities import (`

Imports a dependency or project symbol so later code can use it by name.
### Line 3

`MVP_ACTIVITIES,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 4

`Activity,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 5

`get_activities_for_concept,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 6

`get_activity,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 7

`list_activities,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 8

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 9

`(blank)`

Blank line used to separate nearby statements.
### Line 11

`def test_activities_registry_contains_expected_core_activities():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 12

`activities = list_activities()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 13

`assert len(activities) == 4`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 14

`(blank)`

Blank line used to separate nearby statements.
### Line 15

`ids = [a.activity_id for a in activities]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 16

`assert "act_grover_2q_predict" in ids`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 17

`assert "act_measurement_prob_diagnostic" in ids`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 18

`assert "act_superposition_remediation" in ids`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 19

`assert "act_grover_iteration_reasoning" in ids`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 20

`(blank)`

Blank line used to separate nearby statements.
### Line 22

`def test_get_activity_by_id():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 23

`act = get_activity("act_grover_2q_predict")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 24

`assert act.activity_id == "act_grover_2q_predict"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 25

`assert act.task_type == "quantum_prediction"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 26

`assert act.concept_id == "grover.search_problem"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 27

`assert act.quantum_experiment is not None`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 28

`assert act.quantum_experiment["algorithm"] == "grover"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 29

`assert act.quantum_experiment["num_qubits"] == 2`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 30

`assert act.quantum_experiment["target_state"] == "10"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 31

`assert act.remediation_activity_id == "act_measurement_prob_diagnostic"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 32

`assert act.next_activity_id == "act_grover_iteration_reasoning"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 33

`(blank)`

Blank line used to separate nearby statements.
### Line 35

`def test_get_activity_unknown_raises_key_error():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 36

`with pytest.raises(KeyError):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 37

`get_activity("unknown_activity_xyz")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 38

`(blank)`

Blank line used to separate nearby statements.
### Line 40

`def test_get_activities_for_concept():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 41

`acts = get_activities_for_concept("quantum.measurement")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 42

`assert len(acts) == 1`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 43

`assert acts[0].activity_id == "act_measurement_prob_diagnostic"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 44

`(blank)`

Blank line used to separate nearby statements.
### Line 46

`def test_activity_to_dict():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 47

`act = get_activity("act_superposition_remediation")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 48

`d = act.to_dict()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 49

`assert d["activity_id"] == "act_superposition_remediation"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 50

`assert d["expected_answer"] == "B"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 51

`assert "options" in d`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 52

`assert "B" in d["options"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.

## Nearby Files

[tests/adaptive/__init__.py](__init__.py.md), [tests/adaptive/test_diagnostics.py](test_diagnostics.py.md), [tests/adaptive/test_evidence.py](test_evidence.py.md), [tests/adaptive/test_evidence_progression.py](test_evidence_progression.py.md), [tests/adaptive/test_mastery.py](test_mastery.py.md), [tests/adaptive/test_models.py](test_models.py.md), [tests/adaptive/test_pass4_evidence_trace.py](test_pass4_evidence_trace.py.md), [tests/adaptive/test_persistence_hardening.py](test_persistence_hardening.py.md)
