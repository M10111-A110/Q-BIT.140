# Explanation: `tests/adaptive/test_evidence_progression.py`

## Purpose

This page explains the meaningful behavior in `tests/adaptive/test_evidence_progression.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
import json
import pytest
from backend.adaptive.activities import get_activity
from backend.adaptive.engine import LearnerModel
from backend.adaptive.evidence import (
    GapInference,
    evaluate_conceptual_response,
    evaluate_quantum_prediction,
)
from backend.adaptive.models import LearnerState


def test_evidence_trend_progression():
    """
    Verify full deterministic trajectory progression:
      preliminary_observation -> persistent_difficulty -> improving -> stable_mastery
    """
    model = LearnerModel()
    state = LearnerState(user_id="learner_trend_test")
    mock_sim = {"most_likely_state": "10", "target_probability": 0.93}

    # 1. Attempt 1: Error -> preliminary_observation (confidence 0.35)
    ev1 = evaluate_quantum_prediction(
        learner_id=state.user_id,
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="01",
        simulation_result=mock_sim,
        attempt_number=1,
    )
    dec1 = model.record_evidence(ev1, state)
    assert dec1.action == "gather_evidence"
    inf1 = state.gap_inferences["grover.search_problem"]
    assert inf1["status"] == "observing"
    assert inf1["trend"] == "preliminary_observation"
    assert inf1["confidence"] == 0.35

    # 2. Attempt 2: Second Error -> persistent_difficulty (confidence 0.90)
    ev2 = evaluate_quantum_prediction(
        learner_id=state.user_id,
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="00",
        simulation_result=mock_sim,
        attempt_number=2,
    )
    dec2 = model.record_evidence(ev2, state)
    assert dec2.action == "targeted_remediation"
    inf2 = state.gap_inferences["grover.search_problem"]
    assert inf2["status"] == "remediation_needed"
    assert inf2["trend"] == "persistent_difficulty"
    assert inf2["confidence"] == 0.90

    # 3. Attempt 3: Success on same concept -> improving (confidence 0.15)
    ev3 = evaluate_quantum_prediction(
        learner_id=state.user_id,
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="10",
        simulation_result=mock_sim,
        attempt_number=3,
    )
    dec3 = model.record_evidence(ev3, state)
    assert dec3.action == "advance"
    inf3 = state.gap_inferences["grover.search_problem"]
    assert inf3["status"] == "improving"
    assert inf3["trend"] == "improving"
    assert inf3["confidence"] == 0.15

    # 4. Attempt 4: Second consecutive success -> stable_mastery (confidence 0.0)
    ev4 = evaluate_quantum_prediction(
        learner_id=state.user_id,
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="10",
        simulation_result=mock_sim,
        attempt_number=4,
    )
    dec4 = model.record_evidence(ev4, state)
    assert dec4.action == "advance"
    inf4 = state.gap_inferences["grover.search_problem"]
    assert inf4["status"] == "mastered"
    assert inf4["trend"] == "stable_mastery"
    assert inf4["confidence"] == 0.0


def test_prerequisite_gap_identification_via_dag():
    """
    Verify that when an unmastered prerequisite exists in the DAG,
    repeated errors record prerequisite_concept_id in the gap inference.
    """
    model = LearnerModel()
    state = LearnerState(user_id="learner_prereq_test")
    mock_sim = {"most_likely_state": "10", "target_probability": 0.93}

    # Record error on prerequisite "Superposition"
    state.record_attempt("Superposition", 0.4, ["Wrong question 1"])

    # Attempt 1: Error on Grover
    ev1 = evaluate_quantum_prediction(
        learner_id=state.user_id,
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="01",
        simulation_result=mock_sim,
        attempt_number=1,
    )
    model.record_evidence(ev1, state)

    # Attempt 2: Error on Grover
    ev2 = evaluate_quantum_prediction(
        learner_id=state.user_id,
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="00",
        simulation_result=mock_sim,
        attempt_number=2,
    )
    dec2 = model.record_evidence(ev2, state)

    inf2 = state.gap_inferences["grover.search_problem"]
    assert inf2["status"] == "remediation_needed"
    assert inf2["trend"] == "persistent_difficulty"
    # Prerequisite gap was identified via DAG
    assert inf2["prerequisite_concept_id"] == "quantum.superposition"
    assert dec2.action == "targeted_remediation"
    assert dec2.target == "act_superposition_remediation"


def test_gap_inference_round_trip_with_trend_and_prereq():
    """
    Verify that GapInference serialization/deserialization with trend
    and prerequisite_concept_id is completely lossless and JSON-safe.
    """
    inf = GapInference(
        concept_id="grover.search_problem",
        confidence=0.90,
        status="remediation_needed",
        supporting_evidence_count=2,
        description="Persistent difficulty.",
        trend="persistent_difficulty",
        prerequisite_concept_id="quantum.measurement",
    )

    d = inf.to_dict()
    json_str = json.dumps(d)
    data = json.loads(json_str)

    reconstituted = GapInference.from_dict(data)
    assert reconstituted.concept_id == "grover.search_problem"
    assert reconstituted.confidence == 0.90
    assert reconstituted.status == "remediation_needed"
    assert reconstituted.trend == "persistent_difficulty"
    assert reconstituted.prerequisite_concept_id == "quantum.measurement"


def test_gap_inference_from_dict_backwards_compatible():
    """
    Verify that older dictionaries missing 'trend' or 'prerequisite_concept_id'
    deserialize without errors.
    """
    old_data = {
        "concept_id": "quantum.superposition",
        "confidence": 0.35,
        "status": "observing",
        "supporting_evidence_count": 1,
        "description": "Observing single error.",
    }
    inf = GapInference.from_dict(old_data)
    assert inf.trend == "unassessed"
    assert inf.prerequisite_concept_id is None

```

## Line Notes

### Line 1

`import json`

Imports a dependency or project symbol so later code can use it by name.
### Line 2

`import pytest`

Imports a dependency or project symbol so later code can use it by name.
### Line 3

`from backend.adaptive.activities import get_activity`

Imports a dependency or project symbol so later code can use it by name.
### Line 4

`from backend.adaptive.engine import LearnerModel`

Imports a dependency or project symbol so later code can use it by name.
### Line 5

`from backend.adaptive.evidence import (`

Imports a dependency or project symbol so later code can use it by name.
### Line 6

`GapInference,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 7

`evaluate_conceptual_response,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 8

`evaluate_quantum_prediction,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 9

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 10

`from backend.adaptive.models import LearnerState`

Imports a dependency or project symbol so later code can use it by name.
### Line 11

`(blank)`

Blank line used to separate nearby statements.
### Line 13

`def test_evidence_trend_progression():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 14

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 15

`Verify full deterministic trajectory progression:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 16

`preliminary_observation -> persistent_difficulty -> improving -> stable_mastery`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 17

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 18

`model = LearnerModel()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 19

`state = LearnerState(user_id="learner_trend_test")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 20

`mock_sim = {"most_likely_state": "10", "target_probability": 0.93}`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 21

`(blank)`

Blank line used to separate nearby statements.
### Line 22

`# 1. Attempt 1: Error -> preliminary_observation (confidence 0.35)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 23

`ev1 = evaluate_quantum_prediction(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 24

`learner_id=state.user_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 25

`activity_id="act_grover_2q_predict",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 26

`concept_id="grover.search_problem",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 27

`prediction="01",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 28

`simulation_result=mock_sim,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 29

`attempt_number=1,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 30

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 31

`dec1 = model.record_evidence(ev1, state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 32

`assert dec1.action == "gather_evidence"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 33

`inf1 = state.gap_inferences["grover.search_problem"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 34

`assert inf1["status"] == "observing"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 35

`assert inf1["trend"] == "preliminary_observation"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 36

`assert inf1["confidence"] == 0.35`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 37

`(blank)`

Blank line used to separate nearby statements.
### Line 38

`# 2. Attempt 2: Second Error -> persistent_difficulty (confidence 0.90)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 39

`ev2 = evaluate_quantum_prediction(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 40

`learner_id=state.user_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 41

`activity_id="act_grover_2q_predict",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 42

`concept_id="grover.search_problem",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 43

`prediction="00",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 44

`simulation_result=mock_sim,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 45

`attempt_number=2,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 46

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 47

`dec2 = model.record_evidence(ev2, state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 48

`assert dec2.action == "targeted_remediation"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 49

`inf2 = state.gap_inferences["grover.search_problem"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 50

`assert inf2["status"] == "remediation_needed"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 51

`assert inf2["trend"] == "persistent_difficulty"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 52

`assert inf2["confidence"] == 0.90`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 53

`(blank)`

Blank line used to separate nearby statements.
### Line 54

`# 3. Attempt 3: Success on same concept -> improving (confidence 0.15)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 55

`ev3 = evaluate_quantum_prediction(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 56

`learner_id=state.user_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 57

`activity_id="act_grover_2q_predict",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 58

`concept_id="grover.search_problem",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 59

`prediction="10",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 60

`simulation_result=mock_sim,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 61

`attempt_number=3,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 62

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 63

`dec3 = model.record_evidence(ev3, state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 64

`assert dec3.action == "advance"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 65

`inf3 = state.gap_inferences["grover.search_problem"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 66

`assert inf3["status"] == "improving"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 67

`assert inf3["trend"] == "improving"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 68

`assert inf3["confidence"] == 0.15`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 69

`(blank)`

Blank line used to separate nearby statements.
### Line 70

`# 4. Attempt 4: Second consecutive success -> stable_mastery (confidence 0.0)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 71

`ev4 = evaluate_quantum_prediction(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 72

`learner_id=state.user_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 73

`activity_id="act_grover_2q_predict",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 74

`concept_id="grover.search_problem",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 75

`prediction="10",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 76

`simulation_result=mock_sim,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 77

`attempt_number=4,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 78

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 79

`dec4 = model.record_evidence(ev4, state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 80

`assert dec4.action == "advance"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 81

`inf4 = state.gap_inferences["grover.search_problem"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 82

`assert inf4["status"] == "mastered"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 83

`assert inf4["trend"] == "stable_mastery"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 84

`assert inf4["confidence"] == 0.0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 85

`(blank)`

Blank line used to separate nearby statements.
### Line 87

`def test_prerequisite_gap_identification_via_dag():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 88

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 89

`Verify that when an unmastered prerequisite exists in the DAG,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 90

`repeated errors record prerequisite_concept_id in the gap inference.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 91

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 92

`model = LearnerModel()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 93

`state = LearnerState(user_id="learner_prereq_test")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 94

`mock_sim = {"most_likely_state": "10", "target_probability": 0.93}`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 95

`(blank)`

Blank line used to separate nearby statements.
### Line 96

`# Record error on prerequisite "Superposition"`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 97

`state.record_attempt("Superposition", 0.4, ["Wrong question 1"])`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 98

`(blank)`

Blank line used to separate nearby statements.
### Line 99

`# Attempt 1: Error on Grover`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 100

`ev1 = evaluate_quantum_prediction(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 101

`learner_id=state.user_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 102

`activity_id="act_grover_2q_predict",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 103

`concept_id="grover.search_problem",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 104

`prediction="01",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 105

`simulation_result=mock_sim,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 106

`attempt_number=1,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 107

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 108

`model.record_evidence(ev1, state)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 109

`(blank)`

Blank line used to separate nearby statements.
### Line 110

`# Attempt 2: Error on Grover`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 111

`ev2 = evaluate_quantum_prediction(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 112

`learner_id=state.user_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 113

`activity_id="act_grover_2q_predict",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 114

`concept_id="grover.search_problem",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 115

`prediction="00",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 116

`simulation_result=mock_sim,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 117

`attempt_number=2,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 118

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 119

`dec2 = model.record_evidence(ev2, state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 120

`(blank)`

Blank line used to separate nearby statements.
### Line 121

`inf2 = state.gap_inferences["grover.search_problem"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 122

`assert inf2["status"] == "remediation_needed"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 123

`assert inf2["trend"] == "persistent_difficulty"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 124

`# Prerequisite gap was identified via DAG`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 125

`assert inf2["prerequisite_concept_id"] == "quantum.superposition"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 126

`assert dec2.action == "targeted_remediation"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 127

`assert dec2.target == "act_superposition_remediation"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 128

`(blank)`

Blank line used to separate nearby statements.
### Line 130

`def test_gap_inference_round_trip_with_trend_and_prereq():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 131

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 132

`Verify that GapInference serialization/deserialization with trend`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 133

`and prerequisite_concept_id is completely lossless and JSON-safe.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 134

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 135

`inf = GapInference(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 136

`concept_id="grover.search_problem",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 137

`confidence=0.90,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 138

`status="remediation_needed",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 139

`supporting_evidence_count=2,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 140

`description="Persistent difficulty.",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 141

`trend="persistent_difficulty",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 142

`prerequisite_concept_id="quantum.measurement",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 143

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 144

`(blank)`

Blank line used to separate nearby statements.
### Line 145

`d = inf.to_dict()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 146

`json_str = json.dumps(d)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 147

`data = json.loads(json_str)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 148

`(blank)`

Blank line used to separate nearby statements.
### Line 149

`reconstituted = GapInference.from_dict(data)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 150

`assert reconstituted.concept_id == "grover.search_problem"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 151

`assert reconstituted.confidence == 0.90`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 152

`assert reconstituted.status == "remediation_needed"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 153

`assert reconstituted.trend == "persistent_difficulty"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 154

`assert reconstituted.prerequisite_concept_id == "quantum.measurement"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 155

`(blank)`

Blank line used to separate nearby statements.
### Line 157

`def test_gap_inference_from_dict_backwards_compatible():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 158

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 159

`Verify that older dictionaries missing 'trend' or 'prerequisite_concept_id'`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 160

`deserialize without errors.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 161

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 162

`old_data = {`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 163

`"concept_id": "quantum.superposition",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 164

`"confidence": 0.35,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 165

`"status": "observing",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 166

`"supporting_evidence_count": 1,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 167

`"description": "Observing single error.",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 168

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 169

`inf = GapInference.from_dict(old_data)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 170

`assert inf.trend == "unassessed"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 171

`assert inf.prerequisite_concept_id is None`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.

## Nearby Files

[tests/adaptive/__init__.py](__init__.py.md), [tests/adaptive/test_activities.py](test_activities.py.md), [tests/adaptive/test_diagnostics.py](test_diagnostics.py.md), [tests/adaptive/test_evidence.py](test_evidence.py.md), [tests/adaptive/test_mastery.py](test_mastery.py.md), [tests/adaptive/test_models.py](test_models.py.md), [tests/adaptive/test_pass4_evidence_trace.py](test_pass4_evidence_trace.py.md), [tests/adaptive/test_persistence_hardening.py](test_persistence_hardening.py.md)
