# Explanation: `tests/adaptive/test_mastery.py`

## Purpose

This page explains the meaningful behavior in `tests/adaptive/test_mastery.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
from backend.adaptive.engine import LearnerModel
from backend.adaptive.models import LearnerState


def test_mastery_initial_single_attempt():
    model = LearnerModel()
    state = LearnerState(user_id="u1")

    # 1 attempt: score 0.8, 1 error -> mastery = 0.8 + 0.0 - 0.05 = 0.75
    state.record_attempt("Qubits", 0.8, ["Question 1"])
    mastery = model.compute_mastery("Qubits", state)
    assert mastery == 0.75


def test_mastery_with_improvement_bonus():
    model = LearnerModel()
    state = LearnerState(user_id="u1")

    # Attempt 1: score 0.4
    state.record_attempt("Superposition", 0.4, ["Q1", "Q2", "Q3"])
    # Attempt 2: score 0.8, 1 error
    # improvement = (0.8 - 0.4) * 0.2 = +0.08
    # error penalty = 1 * 0.05 = 0.05
    # mastery = 0.8 + 0.08 - 0.05 = 0.83
    state.record_attempt("Superposition", 0.8, ["Q1"])
    mastery = model.compute_mastery("Superposition", state)
    assert mastery == 0.83


def test_mastery_improvement_bonus_cap():
    model = LearnerModel()
    state = LearnerState(user_id="u1")

    # Jump from 0.0 to 1.0 -> improvement = 1.0 * 0.2 = 0.2 (max bonus)
    state.record_attempt("Measurement", 0.0, ["Q1", "Q2", "Q3", "Q4", "Q5"])
    state.record_attempt("Measurement", 1.0, [])
    # mastery = 1.0 + 0.2 - 0 = 1.2 -> clamped to 1.0
    mastery = model.compute_mastery("Measurement", state)
    assert mastery == 1.0


def test_mastery_no_bonus_on_score_drop():
    model = LearnerModel()
    state = LearnerState(user_id="u1")

    # Attempt 1: 0.8, Attempt 2: 0.6 -> score drop gives 0 bonus
    state.record_attempt("Quantum Gates", 0.8, ["Q1"])
    state.record_attempt("Quantum Gates", 0.6, ["Q1", "Q2"])
    # mastery = 0.6 + 0.0 - (2 * 0.05) = 0.50
    mastery = model.compute_mastery("Quantum Gates", state)
    assert mastery == 0.5


def test_mastery_error_penalty_cap():
    model = LearnerModel()
    state = LearnerState(user_id="u1")

    # 10 errors -> 10 * 0.05 = 0.50, but penalty is capped at 0.30
    many_errors = [f"Err {i}" for i in range(10)]
    state.record_attempt("Quantum States", 0.4, many_errors)
    # mastery = 0.4 + 0.0 - 0.3 = 0.10
    mastery = model.compute_mastery("Quantum States", state)
    assert mastery == 0.1


def test_mastery_bounds_and_rounding():
    model = LearnerModel()
    state = LearnerState(user_id="u1")

    # Lower bound clamp
    state.record_attempt("Qubits", 0.0, ["Q1", "Q2", "Q3", "Q4", "Q5"])
    mastery_low = model.compute_mastery("Qubits", state)
    assert mastery_low == 0.0

    # Upper bound clamp
    state.record_attempt("Measurement", 1.0, [])
    mastery_high = model.compute_mastery("Measurement", state)
    assert mastery_high == 1.0


def test_get_mastery_profile():
    model = LearnerModel()
    state = LearnerState(user_id="u1")
    state.record_attempt("Qubits", 1.0, [])
    state.record_attempt("Quantum States", 0.8, ["Q1"])

    profile = model.get_mastery_profile(state)
    assert len(profile) == 5
    assert profile["Qubits"] == 1.0
    assert profile["Quantum States"] == 0.75
    assert profile["Superposition"] == 0.0
    assert profile["Quantum Gates"] == 0.0
    assert profile["Measurement"] == 0.0

```

## Line Notes

### Line 1

`from backend.adaptive.engine import LearnerModel`

Imports a dependency or project symbol so later code can use it by name.
### Line 2

`from backend.adaptive.models import LearnerState`

Imports a dependency or project symbol so later code can use it by name.
### Line 3

`(blank)`

Blank line used to separate nearby statements.
### Line 5

`def test_mastery_initial_single_attempt():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 6

`model = LearnerModel()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 7

`state = LearnerState(user_id="u1")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 8

`(blank)`

Blank line used to separate nearby statements.
### Line 9

`# 1 attempt: score 0.8, 1 error -> mastery = 0.8 + 0.0 - 0.05 = 0.75`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 10

`state.record_attempt("Qubits", 0.8, ["Question 1"])`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 11

`mastery = model.compute_mastery("Qubits", state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 12

`assert mastery == 0.75`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 13

`(blank)`

Blank line used to separate nearby statements.
### Line 15

`def test_mastery_with_improvement_bonus():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 16

`model = LearnerModel()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 17

`state = LearnerState(user_id="u1")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 18

`(blank)`

Blank line used to separate nearby statements.
### Line 19

`# Attempt 1: score 0.4`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 20

`state.record_attempt("Superposition", 0.4, ["Q1", "Q2", "Q3"])`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 21

`# Attempt 2: score 0.8, 1 error`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 22

`# improvement = (0.8 - 0.4) * 0.2 = +0.08`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 23

`# error penalty = 1 * 0.05 = 0.05`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 24

`# mastery = 0.8 + 0.08 - 0.05 = 0.83`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 25

`state.record_attempt("Superposition", 0.8, ["Q1"])`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 26

`mastery = model.compute_mastery("Superposition", state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 27

`assert mastery == 0.83`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 28

`(blank)`

Blank line used to separate nearby statements.
### Line 30

`def test_mastery_improvement_bonus_cap():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 31

`model = LearnerModel()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 32

`state = LearnerState(user_id="u1")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 33

`(blank)`

Blank line used to separate nearby statements.
### Line 34

`# Jump from 0.0 to 1.0 -> improvement = 1.0 * 0.2 = 0.2 (max bonus)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 35

`state.record_attempt("Measurement", 0.0, ["Q1", "Q2", "Q3", "Q4", "Q5"])`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 36

`state.record_attempt("Measurement", 1.0, [])`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 37

`# mastery = 1.0 + 0.2 - 0 = 1.2 -> clamped to 1.0`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 38

`mastery = model.compute_mastery("Measurement", state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 39

`assert mastery == 1.0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 40

`(blank)`

Blank line used to separate nearby statements.
### Line 42

`def test_mastery_no_bonus_on_score_drop():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 43

`model = LearnerModel()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 44

`state = LearnerState(user_id="u1")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 45

`(blank)`

Blank line used to separate nearby statements.
### Line 46

`# Attempt 1: 0.8, Attempt 2: 0.6 -> score drop gives 0 bonus`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 47

`state.record_attempt("Quantum Gates", 0.8, ["Q1"])`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 48

`state.record_attempt("Quantum Gates", 0.6, ["Q1", "Q2"])`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 49

`# mastery = 0.6 + 0.0 - (2 * 0.05) = 0.50`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 50

`mastery = model.compute_mastery("Quantum Gates", state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 51

`assert mastery == 0.5`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 52

`(blank)`

Blank line used to separate nearby statements.
### Line 54

`def test_mastery_error_penalty_cap():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 55

`model = LearnerModel()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 56

`state = LearnerState(user_id="u1")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 57

`(blank)`

Blank line used to separate nearby statements.
### Line 58

`# 10 errors -> 10 * 0.05 = 0.50, but penalty is capped at 0.30`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 59

`many_errors = [f"Err {i}" for i in range(10)]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 60

`state.record_attempt("Quantum States", 0.4, many_errors)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 61

`# mastery = 0.4 + 0.0 - 0.3 = 0.10`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 62

`mastery = model.compute_mastery("Quantum States", state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 63

`assert mastery == 0.1`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 64

`(blank)`

Blank line used to separate nearby statements.
### Line 66

`def test_mastery_bounds_and_rounding():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 67

`model = LearnerModel()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 68

`state = LearnerState(user_id="u1")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 69

`(blank)`

Blank line used to separate nearby statements.
### Line 70

`# Lower bound clamp`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 71

`state.record_attempt("Qubits", 0.0, ["Q1", "Q2", "Q3", "Q4", "Q5"])`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 72

`mastery_low = model.compute_mastery("Qubits", state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 73

`assert mastery_low == 0.0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 74

`(blank)`

Blank line used to separate nearby statements.
### Line 75

`# Upper bound clamp`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 76

`state.record_attempt("Measurement", 1.0, [])`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 77

`mastery_high = model.compute_mastery("Measurement", state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 78

`assert mastery_high == 1.0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 79

`(blank)`

Blank line used to separate nearby statements.
### Line 81

`def test_get_mastery_profile():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 82

`model = LearnerModel()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 83

`state = LearnerState(user_id="u1")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 84

`state.record_attempt("Qubits", 1.0, [])`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 85

`state.record_attempt("Quantum States", 0.8, ["Q1"])`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 86

`(blank)`

Blank line used to separate nearby statements.
### Line 87

`profile = model.get_mastery_profile(state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 88

`assert len(profile) == 5`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 89

`assert profile["Qubits"] == 1.0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 90

`assert profile["Quantum States"] == 0.75`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 91

`assert profile["Superposition"] == 0.0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 92

`assert profile["Quantum Gates"] == 0.0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 93

`assert profile["Measurement"] == 0.0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.

## Nearby Files

[tests/adaptive/__init__.py](__init__.py.md), [tests/adaptive/test_activities.py](test_activities.py.md), [tests/adaptive/test_diagnostics.py](test_diagnostics.py.md), [tests/adaptive/test_evidence.py](test_evidence.py.md), [tests/adaptive/test_evidence_progression.py](test_evidence_progression.py.md), [tests/adaptive/test_models.py](test_models.py.md), [tests/adaptive/test_pass4_evidence_trace.py](test_pass4_evidence_trace.py.md), [tests/adaptive/test_persistence_hardening.py](test_persistence_hardening.py.md)
