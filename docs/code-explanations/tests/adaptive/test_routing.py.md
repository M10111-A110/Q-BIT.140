# Explanation: `tests/adaptive/test_routing.py`

## Purpose

This page explains the meaningful behavior in `tests/adaptive/test_routing.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
import pytest
from backend.adaptive.engine import LearnerModel
from backend.adaptive.models import LearnerState


def test_rule_1_prerequisite_enforcement():
    model = LearnerModel()
    state = LearnerState(user_id="u1")

    # Prerequisite "Qubits" not mastered (mastery 0.0 < 0.6)
    # Trying to take "Quantum States"
    rec = model.recommend_next("Quantum States", state)
    assert rec.action == "recommend_prerequisite"
    assert rec.target == "Qubits"
    assert "Qubits mastery is 0.0" in rec.reason
    assert rec.concept_id == "quantum.qubit"

    # Prerequisite "Quantum States" not mastered
    # Trying to take "Superposition"
    state.record_attempt("Qubits", 1.0, [])  # Qubits mastered
    rec = model.recommend_next("Superposition", state)
    assert rec.action == "recommend_prerequisite"
    assert rec.target == "Quantum States"
    assert rec.concept_id == "quantum.state"


def test_rule_2_targeted_review_on_error_streak():
    model = LearnerModel()
    state = LearnerState(user_id="u1")

    # 2 errors on Qubits and mastery < 0.6 (score 0.4 - 0.1 = 0.3)
    state.record_attempt("Qubits", 0.4, ["Wrong 1", "Wrong 2"])
    rec = model.recommend_next("Qubits", state)
    assert rec.action == "recommend_targeted_review"
    assert rec.target == "Qubits"
    assert "2 wrong answers on Qubits" in rec.reason
    assert rec.concept_id == "quantum.qubit"


def test_rule_3_advance_on_mastery():
    model = LearnerModel()
    state = LearnerState(user_id="u1")

    # Qubits mastered (score 1.0 >= 0.6) -> unlocks Quantum States
    state.record_attempt("Qubits", 1.0, [])
    rec = model.recommend_next("Qubits", state)
    assert rec.action == "advance"
    assert rec.target == ["Quantum States"]
    assert "ready to move on to Quantum States" in rec.reason
    assert rec.concept_id == "quantum.qubit"

    # Superposition mastered -> unlocks Quantum Gates
    state.record_attempt("Quantum States", 1.0, [])
    state.record_attempt("Superposition", 1.0, [])
    rec_sup = model.recommend_next("Superposition", state)
    assert rec_sup.action == "advance"
    assert rec_sup.target == ["Quantum Gates"]

    # Measurement (end of chain) mastered -> target None, (end of chain) in reason
    state.record_attempt("Quantum Gates", 1.0, [])
    state.record_attempt("Measurement", 1.0, [])
    rec_meas = model.recommend_next("Measurement", state)
    assert rec_meas.action == "advance"
    assert rec_meas.target is None
    assert "(end of chain)" in rec_meas.reason


def test_rule_4_reinforce_current_concept():
    model = LearnerModel()
    state = LearnerState(user_id="u1")

    # Qubits: 1 error (below error streak limit 2), score 0.4 -> mastery 0.35 (< 0.6)
    state.record_attempt("Qubits", 0.4, ["Wrong 1"])
    rec = model.recommend_next("Qubits", state)
    assert rec.action == "reinforce_current_concept"
    assert rec.target == "Qubits"
    assert "needs more practice" in rec.reason
    assert rec.concept_id == "quantum.qubit"


def test_unknown_topic_raises_key_error():
    model = LearnerModel()
    state = LearnerState(user_id="u1")
    with pytest.raises(KeyError):
        model.recommend_next("UnknownTopic", state)


def test_get_learner_context():
    model = LearnerModel()
    state = LearnerState(user_id="learner_abc")
    state.record_attempt("Qubits", 1.0, [])

    context = model.get_learner_context(state, current_topic="Qubits")
    assert context.user_id == "learner_abc"
    assert context.concept_mastery["quantum.qubit"] == 1.0
    assert context.concept_scores["Qubits"] == 1.0
    assert context.current_concept == "Qubits"
    assert context.recommendation is not None
    assert context.recommendation.action == "advance"
    assert context.recommendation.target == ["Quantum States"]

    context_dict = context.to_dict()
    assert context_dict["user_id"] == "learner_abc"
    assert context_dict["recommendation"]["action"] == "advance"

```

## Line Notes

### Line 1

`import pytest`

Imports a dependency or project symbol so later code can use it by name.
### Line 2

`from backend.adaptive.engine import LearnerModel`

Imports a dependency or project symbol so later code can use it by name.
### Line 3

`from backend.adaptive.models import LearnerState`

Imports a dependency or project symbol so later code can use it by name.
### Line 4

`(blank)`

Blank line used to separate nearby statements.
### Line 6

`def test_rule_1_prerequisite_enforcement():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 7

`model = LearnerModel()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 8

`state = LearnerState(user_id="u1")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 9

`(blank)`

Blank line used to separate nearby statements.
### Line 10

`# Prerequisite "Qubits" not mastered (mastery 0.0 < 0.6)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 11

`# Trying to take "Quantum States"`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 12

`rec = model.recommend_next("Quantum States", state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 13

`assert rec.action == "recommend_prerequisite"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 14

`assert rec.target == "Qubits"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 15

`assert "Qubits mastery is 0.0" in rec.reason`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 16

`assert rec.concept_id == "quantum.qubit"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 17

`(blank)`

Blank line used to separate nearby statements.
### Line 18

`# Prerequisite "Quantum States" not mastered`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 19

`# Trying to take "Superposition"`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 20

`state.record_attempt("Qubits", 1.0, [])  # Qubits mastered`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 21

`rec = model.recommend_next("Superposition", state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 22

`assert rec.action == "recommend_prerequisite"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 23

`assert rec.target == "Quantum States"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 24

`assert rec.concept_id == "quantum.state"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 25

`(blank)`

Blank line used to separate nearby statements.
### Line 27

`def test_rule_2_targeted_review_on_error_streak():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 28

`model = LearnerModel()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 29

`state = LearnerState(user_id="u1")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 30

`(blank)`

Blank line used to separate nearby statements.
### Line 31

`# 2 errors on Qubits and mastery < 0.6 (score 0.4 - 0.1 = 0.3)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 32

`state.record_attempt("Qubits", 0.4, ["Wrong 1", "Wrong 2"])`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 33

`rec = model.recommend_next("Qubits", state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 34

`assert rec.action == "recommend_targeted_review"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 35

`assert rec.target == "Qubits"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 36

`assert "2 wrong answers on Qubits" in rec.reason`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 37

`assert rec.concept_id == "quantum.qubit"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 38

`(blank)`

Blank line used to separate nearby statements.
### Line 40

`def test_rule_3_advance_on_mastery():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 41

`model = LearnerModel()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 42

`state = LearnerState(user_id="u1")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 43

`(blank)`

Blank line used to separate nearby statements.
### Line 44

`# Qubits mastered (score 1.0 >= 0.6) -> unlocks Quantum States`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 45

`state.record_attempt("Qubits", 1.0, [])`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 46

`rec = model.recommend_next("Qubits", state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 47

`assert rec.action == "advance"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 48

`assert rec.target == ["Quantum States"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 49

`assert "ready to move on to Quantum States" in rec.reason`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 50

`assert rec.concept_id == "quantum.qubit"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 51

`(blank)`

Blank line used to separate nearby statements.
### Line 52

`# Superposition mastered -> unlocks Quantum Gates`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 53

`state.record_attempt("Quantum States", 1.0, [])`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 54

`state.record_attempt("Superposition", 1.0, [])`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 55

`rec_sup = model.recommend_next("Superposition", state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 56

`assert rec_sup.action == "advance"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 57

`assert rec_sup.target == ["Quantum Gates"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 58

`(blank)`

Blank line used to separate nearby statements.
### Line 59

`# Measurement (end of chain) mastered -> target None, (end of chain) in reason`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 60

`state.record_attempt("Quantum Gates", 1.0, [])`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 61

`state.record_attempt("Measurement", 1.0, [])`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 62

`rec_meas = model.recommend_next("Measurement", state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 63

`assert rec_meas.action == "advance"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 64

`assert rec_meas.target is None`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 65

`assert "(end of chain)" in rec_meas.reason`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 66

`(blank)`

Blank line used to separate nearby statements.
### Line 68

`def test_rule_4_reinforce_current_concept():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 69

`model = LearnerModel()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 70

`state = LearnerState(user_id="u1")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 71

`(blank)`

Blank line used to separate nearby statements.
### Line 72

`# Qubits: 1 error (below error streak limit 2), score 0.4 -> mastery 0.35 (< 0.6)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 73

`state.record_attempt("Qubits", 0.4, ["Wrong 1"])`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 74

`rec = model.recommend_next("Qubits", state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 75

`assert rec.action == "reinforce_current_concept"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 76

`assert rec.target == "Qubits"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 77

`assert "needs more practice" in rec.reason`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 78

`assert rec.concept_id == "quantum.qubit"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 79

`(blank)`

Blank line used to separate nearby statements.
### Line 81

`def test_unknown_topic_raises_key_error():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 82

`model = LearnerModel()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 83

`state = LearnerState(user_id="u1")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 84

`with pytest.raises(KeyError):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 85

`model.recommend_next("UnknownTopic", state)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 86

`(blank)`

Blank line used to separate nearby statements.
### Line 88

`def test_get_learner_context():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 89

`model = LearnerModel()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 90

`state = LearnerState(user_id="learner_abc")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 91

`state.record_attempt("Qubits", 1.0, [])`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 92

`(blank)`

Blank line used to separate nearby statements.
### Line 93

`context = model.get_learner_context(state, current_topic="Qubits")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 94

`assert context.user_id == "learner_abc"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 95

`assert context.concept_mastery["quantum.qubit"] == 1.0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 96

`assert context.concept_scores["Qubits"] == 1.0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 97

`assert context.current_concept == "Qubits"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 98

`assert context.recommendation is not None`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 99

`assert context.recommendation.action == "advance"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 100

`assert context.recommendation.target == ["Quantum States"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 101

`(blank)`

Blank line used to separate nearby statements.
### Line 102

`context_dict = context.to_dict()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 103

`assert context_dict["user_id"] == "learner_abc"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 104

`assert context_dict["recommendation"]["action"] == "advance"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.

## Nearby Files

[tests/adaptive/__init__.py](__init__.py.md), [tests/adaptive/test_activities.py](test_activities.py.md), [tests/adaptive/test_diagnostics.py](test_diagnostics.py.md), [tests/adaptive/test_evidence.py](test_evidence.py.md), [tests/adaptive/test_evidence_progression.py](test_evidence_progression.py.md), [tests/adaptive/test_mastery.py](test_mastery.py.md), [tests/adaptive/test_models.py](test_models.py.md), [tests/adaptive/test_pass4_evidence_trace.py](test_pass4_evidence_trace.py.md)
