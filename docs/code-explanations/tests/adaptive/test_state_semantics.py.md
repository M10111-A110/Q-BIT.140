# Explanation: `tests/adaptive/test_state_semantics.py`

## Purpose

This page explains the meaningful behavior in `tests/adaptive/test_state_semantics.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
import pytest
from backend.adaptive.activities import get_activity
from backend.adaptive.engine import LearnerModel
from backend.adaptive.evidence import (
    GapInference,
    evaluate_conceptual_response,
    evaluate_quantum_prediction,
)
from backend.adaptive.models import LearnerState


def test_scenario_a_single_incorrect_attempt_no_false_certainty():
    """
    Scenario A: Single incorrect attempt
      - Evidence is recorded in history.
      - Inferred state remains preliminary/observing with low confidence (0.35).
      - No false certainty of deep misconception.
      - Adaptive decision is gather_evidence on current activity.
    """
    model = LearnerModel()
    state = LearnerState(user_id="learner_a")
    mock_sim = {"most_likely_state": "10", "target_probability": 0.93}

    ev = evaluate_quantum_prediction(
        learner_id=state.user_id,
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="01",
        simulation_result=mock_sim,
        attempt_number=1,
    )
    decision = model.record_evidence(ev, state)

    # 1. Observed Performance
    assert ev.is_correct is False
    assert ev.attempt_number == 1
    assert ev.evaluation_details["match"] is False

    # 2. Accumulated Evidence
    assert len(state.evidence_history) == 1
    assert state.evidence_history[0]["learner_response"] == "01"
    assert state.attempts["grover.search_problem"] == 1
    assert state.score_history["grover.search_problem"] == [0.0]

    # 3. Inferred Learner State (No false certainty)
    inf = state.gap_inferences["grover.search_problem"]
    assert inf["status"] == "observing"
    assert inf["trend"] == "preliminary_observation"
    assert inf["confidence"] == 0.35
    assert inf["supporting_evidence_count"] == 1
    assert "preliminary observation" in inf["description"]

    # 4. Adaptive Decision (Traceable to single observation)
    assert decision.action == "gather_evidence"
    assert decision.target == "act_grover_2q_predict"
    assert "Initial prediction mismatch" in decision.reason
    assert decision.concept_id == "grover.search_problem"


def test_scenario_b_repeated_incorrect_attempts_justifies_difficulty():
    """
    Scenario B: Repeated incorrect attempts
      - Accumulated evidence increases confidence (0.90).
      - Inferred state status becomes remediation_needed and trend persistent_difficulty.
      - Prerequisite gap is evaluated against DAG.
      - Adaptive decision triggers targeted remediation.
    """
    model = LearnerModel()
    state = LearnerState(user_id="learner_b")
    mock_sim = {"most_likely_state": "10", "target_probability": 0.93}

    # Attempt 1
    ev1 = evaluate_quantum_prediction(
        learner_id=state.user_id,
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="01",
        simulation_result=mock_sim,
        attempt_number=1,
    )
    model.record_evidence(ev1, state)

    # Attempt 2
    ev2 = evaluate_quantum_prediction(
        learner_id=state.user_id,
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="00",
        simulation_result=mock_sim,
        attempt_number=2,
    )
    decision = model.record_evidence(ev2, state)

    # 1. Observed Performance
    assert ev2.is_correct is False
    assert ev2.attempt_number == 2

    # 2. Accumulated Evidence
    assert len(state.evidence_history) == 2
    assert state.score_history["grover.search_problem"] == [0.0, 0.0]
    assert state.attempts["grover.search_problem"] == 2

    # 3. Inferred Learner State (High confidence based on converging evidence)
    inf = state.gap_inferences["grover.search_problem"]
    assert inf["status"] == "remediation_needed"
    assert inf["trend"] == "persistent_difficulty"
    assert inf["confidence"] == 0.90
    assert inf["supporting_evidence_count"] == 2
    assert "repeated incorrect attempts" in inf["description"]

    # 4. Adaptive Decision (Traceable to repeated errors)
    assert decision.action == "targeted_remediation"
    assert decision.target == "act_measurement_prob_diagnostic"
    assert "Repeated prediction errors" in decision.reason
    assert decision.concept_id == "grover.search_problem"


def test_scenario_c_wrong_then_correct_tracks_improvement():
    """
    Scenario C: Wrong -> Correct
      - Complete evidence history is preserved (both error and success).
      - Inferred state changes to improving with low gap confidence (0.15).
      - Adaptive decision advances to next activity.
    """
    model = LearnerModel()
    state = LearnerState(user_id="learner_c")
    mock_sim = {"most_likely_state": "10", "target_probability": 0.93}

    # Attempt 1: Wrong
    ev1 = evaluate_quantum_prediction(
        learner_id=state.user_id,
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="01",
        simulation_result=mock_sim,
        attempt_number=1,
    )
    model.record_evidence(ev1, state)

    # Attempt 2: Correct
    ev2 = evaluate_quantum_prediction(
        learner_id=state.user_id,
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="10",
        simulation_result=mock_sim,
        attempt_number=2,
    )
    decision = model.record_evidence(ev2, state)

    # 1. Observed Performance
    assert ev2.is_correct is True

    # 2. Accumulated Evidence (Both attempts intact)
    assert len(state.evidence_history) == 2
    assert state.evidence_history[0]["is_correct"] is False
    assert state.evidence_history[1]["is_correct"] is True
    assert state.score_history["grover.search_problem"] == [0.0, 1.0]

    # 3. Inferred Learner State (Improving)
    inf = state.gap_inferences["grover.search_problem"]
    assert inf["status"] == "improving"
    assert inf["trend"] == "improving"
    assert inf["confidence"] == 0.15
    assert "post-intervention improvement" in inf["description"]

    # 4. Adaptive Decision
    assert decision.action == "advance"
    assert decision.target == "act_grover_iteration_reasoning"
    assert "demonstrated correct understanding" in decision.reason
    assert decision.concept_id == "grover.search_problem"


def test_scenario_d_correct_then_correct_supports_stable_mastery():
    """
    Scenario D: Correct -> Correct
      - Stable mastery is confirmed by multiple successful observations.
      - Gap confidence is 0.0.
      - Inferred state trend is stable_mastery.
    """
    model = LearnerModel()
    state = LearnerState(user_id="learner_d")
    mock_sim = {"most_likely_state": "10", "target_probability": 0.93}

    # Attempt 1: Correct
    ev1 = evaluate_quantum_prediction(
        learner_id=state.user_id,
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="10",
        simulation_result=mock_sim,
        attempt_number=1,
    )
    model.record_evidence(ev1, state)

    # Attempt 2: Correct again
    ev2 = evaluate_quantum_prediction(
        learner_id=state.user_id,
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="10",
        simulation_result=mock_sim,
        attempt_number=2,
    )
    decision = model.record_evidence(ev2, state)

    # 1. Observed Performance
    assert ev2.is_correct is True

    # 2. Accumulated Evidence
    assert len(state.evidence_history) == 2
    assert state.score_history["grover.search_problem"] == [1.0, 1.0]

    # 3. Inferred Learner State
    inf = state.gap_inferences["grover.search_problem"]
    assert inf["status"] == "mastered"
    assert inf["trend"] == "stable_mastery"
    assert inf["confidence"] == 0.0
    assert "multiple attempts" in inf["description"]

    # 4. Adaptive Decision
    assert decision.action == "advance"
    assert decision.concept_id == "grover.search_problem"


def test_scenario_e_latest_attempt_never_erases_historical_evidence():
    """
    Scenario E: Latest attempt must not erase historical evidence.
      - Multiple attempts across activities accumulate in evidence_history.
      - Prior timestamps, predictions, and verification results remain accessible.
    """
    model = LearnerModel()
    state = LearnerState(user_id="learner_e")
    mock_sim = {"most_likely_state": "10", "target_probability": 0.93}

    # 1. Initial error on Grover
    ev1 = evaluate_quantum_prediction(
        learner_id=state.user_id,
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="01",
        simulation_result=mock_sim,
        attempt_number=1,
    )
    model.record_evidence(ev1, state)

    # 2. Success on Remediation Diagnostic
    ev2 = evaluate_conceptual_response(
        learner_id=state.user_id,
        activity_id="act_measurement_prob_diagnostic",
        concept_id="quantum.measurement",
        selected_option="B",
        expected_option="B",
        attempt_number=1,
    )
    model.record_evidence(ev2, state)

    # 3. Subsequent success on Grover
    ev3 = evaluate_quantum_prediction(
        learner_id=state.user_id,
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="10",
        simulation_result=mock_sim,
        attempt_number=2,
    )
    model.record_evidence(ev3, state)

    # Verify history integrity:
    assert len(state.evidence_history) == 3
    assert state.evidence_history[0]["activity_id"] == "act_grover_2q_predict"
    assert state.evidence_history[0]["is_correct"] is False
    assert state.evidence_history[1]["activity_id"] == "act_measurement_prob_diagnostic"
    assert state.evidence_history[1]["is_correct"] is True
    assert state.evidence_history[2]["activity_id"] == "act_grover_2q_predict"
    assert state.evidence_history[2]["is_correct"] is True

    # Both concept inferences exist independently:
    assert "grover.search_problem" in state.gap_inferences
    assert "quantum.measurement" in state.gap_inferences


def test_scenario_f_adaptive_decision_is_deterministic_and_explainable():
    """
    Scenario F: Every adaptive decision is deterministic and verifiable.
      - Action, target, reason, and concept_id are fully populated and explainable.
    """
    model = LearnerModel()
    state = LearnerState(user_id="learner_f")
    mock_sim = {"most_likely_state": "10", "target_probability": 0.93}

    ev = evaluate_quantum_prediction(
        learner_id=state.user_id,
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="10",
        simulation_result=mock_sim,
        attempt_number=1,
    )
    rec = model.record_evidence(ev, state)

    assert isinstance(rec.action, str)
    assert rec.action == "advance"
    assert rec.target == "act_grover_iteration_reasoning"
    assert isinstance(rec.reason, str)
    assert len(rec.reason) > 10
    assert rec.concept_id == "grover.search_problem"

    # Context snapshot serialization
    ctx = model.get_learner_context(state, current_topic="Superposition")
    assert ctx.user_id == "learner_f"
    assert ctx.concept_scores["grover.search_problem"] == 1.0
    assert ctx.gap_inferences["grover.search_problem"]["status"] == "mastered"

```

## Line Notes

### Line 1

`import pytest`

Imports a dependency or project symbol so later code can use it by name.
### Line 2

`from backend.adaptive.activities import get_activity`

Imports a dependency or project symbol so later code can use it by name.
### Line 3

`from backend.adaptive.engine import LearnerModel`

Imports a dependency or project symbol so later code can use it by name.
### Line 4

`from backend.adaptive.evidence import (`

Imports a dependency or project symbol so later code can use it by name.
### Line 5

`GapInference,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 6

`evaluate_conceptual_response,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 7

`evaluate_quantum_prediction,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 8

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 9

`from backend.adaptive.models import LearnerState`

Imports a dependency or project symbol so later code can use it by name.
### Line 10

`(blank)`

Blank line used to separate nearby statements.
### Line 12

`def test_scenario_a_single_incorrect_attempt_no_false_certainty():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 13

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 14

`Scenario A: Single incorrect attempt`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 15

`- Evidence is recorded in history.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 16

`- Inferred state remains preliminary/observing with low confidence (0.35).`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 17

`- No false certainty of deep misconception.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 18

`- Adaptive decision is gather_evidence on current activity.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 19

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 20

`model = LearnerModel()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 21

`state = LearnerState(user_id="learner_a")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 22

`mock_sim = {"most_likely_state": "10", "target_probability": 0.93}`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 23

`(blank)`

Blank line used to separate nearby statements.
### Line 24

`ev = evaluate_quantum_prediction(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 25

`learner_id=state.user_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 26

`activity_id="act_grover_2q_predict",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 27

`concept_id="grover.search_problem",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 28

`prediction="01",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 29

`simulation_result=mock_sim,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 30

`attempt_number=1,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 31

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 32

`decision = model.record_evidence(ev, state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 33

`(blank)`

Blank line used to separate nearby statements.
### Line 34

`# 1. Observed Performance`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 35

`assert ev.is_correct is False`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 36

`assert ev.attempt_number == 1`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 37

`assert ev.evaluation_details["match"] is False`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 38

`(blank)`

Blank line used to separate nearby statements.
### Line 39

`# 2. Accumulated Evidence`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 40

`assert len(state.evidence_history) == 1`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 41

`assert state.evidence_history[0]["learner_response"] == "01"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 42

`assert state.attempts["grover.search_problem"] == 1`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 43

`assert state.score_history["grover.search_problem"] == [0.0]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 44

`(blank)`

Blank line used to separate nearby statements.
### Line 45

`# 3. Inferred Learner State (No false certainty)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 46

`inf = state.gap_inferences["grover.search_problem"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 47

`assert inf["status"] == "observing"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 48

`assert inf["trend"] == "preliminary_observation"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 49

`assert inf["confidence"] == 0.35`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 50

`assert inf["supporting_evidence_count"] == 1`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 51

`assert "preliminary observation" in inf["description"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 52

`(blank)`

Blank line used to separate nearby statements.
### Line 53

`# 4. Adaptive Decision (Traceable to single observation)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 54

`assert decision.action == "gather_evidence"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 55

`assert decision.target == "act_grover_2q_predict"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 56

`assert "Initial prediction mismatch" in decision.reason`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 57

`assert decision.concept_id == "grover.search_problem"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 58

`(blank)`

Blank line used to separate nearby statements.
### Line 60

`def test_scenario_b_repeated_incorrect_attempts_justifies_difficulty():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 61

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 62

`Scenario B: Repeated incorrect attempts`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 63

`- Accumulated evidence increases confidence (0.90).`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 64

`- Inferred state status becomes remediation_needed and trend persistent_difficulty.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 65

`- Prerequisite gap is evaluated against DAG.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 66

`- Adaptive decision triggers targeted remediation.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 67

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 68

`model = LearnerModel()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 69

`state = LearnerState(user_id="learner_b")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 70

`mock_sim = {"most_likely_state": "10", "target_probability": 0.93}`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 71

`(blank)`

Blank line used to separate nearby statements.
### Line 72

`# Attempt 1`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 73

`ev1 = evaluate_quantum_prediction(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 74

`learner_id=state.user_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 75

`activity_id="act_grover_2q_predict",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 76

`concept_id="grover.search_problem",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 77

`prediction="01",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 78

`simulation_result=mock_sim,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 79

`attempt_number=1,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 80

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 81

`model.record_evidence(ev1, state)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 82

`(blank)`

Blank line used to separate nearby statements.
### Line 83

`# Attempt 2`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 84

`ev2 = evaluate_quantum_prediction(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 85

`learner_id=state.user_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 86

`activity_id="act_grover_2q_predict",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 87

`concept_id="grover.search_problem",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 88

`prediction="00",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 89

`simulation_result=mock_sim,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 90

`attempt_number=2,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 91

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 92

`decision = model.record_evidence(ev2, state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 93

`(blank)`

Blank line used to separate nearby statements.
### Line 94

`# 1. Observed Performance`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 95

`assert ev2.is_correct is False`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 96

`assert ev2.attempt_number == 2`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 97

`(blank)`

Blank line used to separate nearby statements.
### Line 98

`# 2. Accumulated Evidence`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 99

`assert len(state.evidence_history) == 2`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 100

`assert state.score_history["grover.search_problem"] == [0.0, 0.0]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 101

`assert state.attempts["grover.search_problem"] == 2`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 102

`(blank)`

Blank line used to separate nearby statements.
### Line 103

`# 3. Inferred Learner State (High confidence based on converging evidence)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 104

`inf = state.gap_inferences["grover.search_problem"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 105

`assert inf["status"] == "remediation_needed"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 106

`assert inf["trend"] == "persistent_difficulty"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 107

`assert inf["confidence"] == 0.90`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 108

`assert inf["supporting_evidence_count"] == 2`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 109

`assert "repeated incorrect attempts" in inf["description"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 110

`(blank)`

Blank line used to separate nearby statements.
### Line 111

`# 4. Adaptive Decision (Traceable to repeated errors)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 112

`assert decision.action == "targeted_remediation"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 113

`assert decision.target == "act_measurement_prob_diagnostic"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 114

`assert "Repeated prediction errors" in decision.reason`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 115

`assert decision.concept_id == "grover.search_problem"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 116

`(blank)`

Blank line used to separate nearby statements.
### Line 118

`def test_scenario_c_wrong_then_correct_tracks_improvement():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 119

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 120

`Scenario C: Wrong -> Correct`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 121

`- Complete evidence history is preserved (both error and success).`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 122

`- Inferred state changes to improving with low gap confidence (0.15).`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 123

`- Adaptive decision advances to next activity.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 124

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 125

`model = LearnerModel()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 126

`state = LearnerState(user_id="learner_c")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 127

`mock_sim = {"most_likely_state": "10", "target_probability": 0.93}`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 128

`(blank)`

Blank line used to separate nearby statements.
### Line 129

`# Attempt 1: Wrong`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 130

`ev1 = evaluate_quantum_prediction(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 131

`learner_id=state.user_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 132

`activity_id="act_grover_2q_predict",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 133

`concept_id="grover.search_problem",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 134

`prediction="01",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 135

`simulation_result=mock_sim,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 136

`attempt_number=1,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 137

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 138

`model.record_evidence(ev1, state)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 139

`(blank)`

Blank line used to separate nearby statements.
### Line 140

`# Attempt 2: Correct`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 141

`ev2 = evaluate_quantum_prediction(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 142

`learner_id=state.user_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 143

`activity_id="act_grover_2q_predict",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 144

`concept_id="grover.search_problem",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 145

`prediction="10",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 146

`simulation_result=mock_sim,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 147

`attempt_number=2,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 148

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 149

`decision = model.record_evidence(ev2, state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 150

`(blank)`

Blank line used to separate nearby statements.
### Line 151

`# 1. Observed Performance`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 152

`assert ev2.is_correct is True`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 153

`(blank)`

Blank line used to separate nearby statements.
### Line 154

`# 2. Accumulated Evidence (Both attempts intact)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 155

`assert len(state.evidence_history) == 2`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 156

`assert state.evidence_history[0]["is_correct"] is False`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 157

`assert state.evidence_history[1]["is_correct"] is True`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 158

`assert state.score_history["grover.search_problem"] == [0.0, 1.0]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 159

`(blank)`

Blank line used to separate nearby statements.
### Line 160

`# 3. Inferred Learner State (Improving)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 161

`inf = state.gap_inferences["grover.search_problem"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 162

`assert inf["status"] == "improving"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 163

`assert inf["trend"] == "improving"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 164

`assert inf["confidence"] == 0.15`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 165

`assert "post-intervention improvement" in inf["description"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 166

`(blank)`

Blank line used to separate nearby statements.
### Line 167

`# 4. Adaptive Decision`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 168

`assert decision.action == "advance"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 169

`assert decision.target == "act_grover_iteration_reasoning"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 170

`assert "demonstrated correct understanding" in decision.reason`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 171

`assert decision.concept_id == "grover.search_problem"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 172

`(blank)`

Blank line used to separate nearby statements.
### Line 174

`def test_scenario_d_correct_then_correct_supports_stable_mastery():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 175

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 176

`Scenario D: Correct -> Correct`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 177

`- Stable mastery is confirmed by multiple successful observations.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 178

`- Gap confidence is 0.0.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 179

`- Inferred state trend is stable_mastery.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 180

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 181

`model = LearnerModel()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 182

`state = LearnerState(user_id="learner_d")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 183

`mock_sim = {"most_likely_state": "10", "target_probability": 0.93}`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 184

`(blank)`

Blank line used to separate nearby statements.
### Line 185

`# Attempt 1: Correct`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 186

`ev1 = evaluate_quantum_prediction(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 187

`learner_id=state.user_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 188

`activity_id="act_grover_2q_predict",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 189

`concept_id="grover.search_problem",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 190

`prediction="10",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 191

`simulation_result=mock_sim,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 192

`attempt_number=1,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 193

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 194

`model.record_evidence(ev1, state)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 195

`(blank)`

Blank line used to separate nearby statements.
### Line 196

`# Attempt 2: Correct again`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 197

`ev2 = evaluate_quantum_prediction(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 198

`learner_id=state.user_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 199

`activity_id="act_grover_2q_predict",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 200

`concept_id="grover.search_problem",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 201

`prediction="10",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 202

`simulation_result=mock_sim,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 203

`attempt_number=2,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 204

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 205

`decision = model.record_evidence(ev2, state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 206

`(blank)`

Blank line used to separate nearby statements.
### Line 207

`# 1. Observed Performance`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 208

`assert ev2.is_correct is True`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 209

`(blank)`

Blank line used to separate nearby statements.
### Line 210

`# 2. Accumulated Evidence`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 211

`assert len(state.evidence_history) == 2`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 212

`assert state.score_history["grover.search_problem"] == [1.0, 1.0]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 213

`(blank)`

Blank line used to separate nearby statements.
### Line 214

`# 3. Inferred Learner State`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 215

`inf = state.gap_inferences["grover.search_problem"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 216

`assert inf["status"] == "mastered"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 217

`assert inf["trend"] == "stable_mastery"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 218

`assert inf["confidence"] == 0.0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 219

`assert "multiple attempts" in inf["description"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 220

`(blank)`

Blank line used to separate nearby statements.
### Line 221

`# 4. Adaptive Decision`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 222

`assert decision.action == "advance"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 223

`assert decision.concept_id == "grover.search_problem"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 224

`(blank)`

Blank line used to separate nearby statements.
### Line 226

`def test_scenario_e_latest_attempt_never_erases_historical_evidence():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 227

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 228

`Scenario E: Latest attempt must not erase historical evidence.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 229

`- Multiple attempts across activities accumulate in evidence_history.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 230

`- Prior timestamps, predictions, and verification results remain accessible.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 231

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 232

`model = LearnerModel()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 233

`state = LearnerState(user_id="learner_e")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 234

`mock_sim = {"most_likely_state": "10", "target_probability": 0.93}`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 235

`(blank)`

Blank line used to separate nearby statements.
### Line 236

`# 1. Initial error on Grover`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 237

`ev1 = evaluate_quantum_prediction(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 238

`learner_id=state.user_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 239

`activity_id="act_grover_2q_predict",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 240

`concept_id="grover.search_problem",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 241

`prediction="01",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 242

`simulation_result=mock_sim,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 243

`attempt_number=1,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 244

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 245

`model.record_evidence(ev1, state)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 246

`(blank)`

Blank line used to separate nearby statements.
### Line 247

`# 2. Success on Remediation Diagnostic`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 248

`ev2 = evaluate_conceptual_response(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 249

`learner_id=state.user_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 250

`activity_id="act_measurement_prob_diagnostic",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 251

`concept_id="quantum.measurement",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 252

`selected_option="B",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 253

`expected_option="B",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 254

`attempt_number=1,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 255

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 256

`model.record_evidence(ev2, state)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 257

`(blank)`

Blank line used to separate nearby statements.
### Line 258

`# 3. Subsequent success on Grover`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 259

`ev3 = evaluate_quantum_prediction(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 260

`learner_id=state.user_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 261

`activity_id="act_grover_2q_predict",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 262

`concept_id="grover.search_problem",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 263

`prediction="10",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 264

`simulation_result=mock_sim,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 265

`attempt_number=2,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 266

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 267

`model.record_evidence(ev3, state)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 268

`(blank)`

Blank line used to separate nearby statements.
### Line 269

`# Verify history integrity:`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 270

`assert len(state.evidence_history) == 3`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 271

`assert state.evidence_history[0]["activity_id"] == "act_grover_2q_predict"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 272

`assert state.evidence_history[0]["is_correct"] is False`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 273

`assert state.evidence_history[1]["activity_id"] == "act_measurement_prob_diagnostic"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 274

`assert state.evidence_history[1]["is_correct"] is True`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 275

`assert state.evidence_history[2]["activity_id"] == "act_grover_2q_predict"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 276

`assert state.evidence_history[2]["is_correct"] is True`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 277

`(blank)`

Blank line used to separate nearby statements.
### Line 278

`# Both concept inferences exist independently:`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 279

`assert "grover.search_problem" in state.gap_inferences`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 280

`assert "quantum.measurement" in state.gap_inferences`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 281

`(blank)`

Blank line used to separate nearby statements.
### Line 283

`def test_scenario_f_adaptive_decision_is_deterministic_and_explainable():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 284

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 285

`Scenario F: Every adaptive decision is deterministic and verifiable.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 286

`- Action, target, reason, and concept_id are fully populated and explainable.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 287

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 288

`model = LearnerModel()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 289

`state = LearnerState(user_id="learner_f")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 290

`mock_sim = {"most_likely_state": "10", "target_probability": 0.93}`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 291

`(blank)`

Blank line used to separate nearby statements.
### Line 292

`ev = evaluate_quantum_prediction(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 293

`learner_id=state.user_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 294

`activity_id="act_grover_2q_predict",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 295

`concept_id="grover.search_problem",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 296

`prediction="10",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 297

`simulation_result=mock_sim,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 298

`attempt_number=1,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 299

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 300

`rec = model.record_evidence(ev, state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 301

`(blank)`

Blank line used to separate nearby statements.
### Line 302

`assert isinstance(rec.action, str)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 303

`assert rec.action == "advance"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 304

`assert rec.target == "act_grover_iteration_reasoning"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 305

`assert isinstance(rec.reason, str)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 306

`assert len(rec.reason) > 10`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 307

`assert rec.concept_id == "grover.search_problem"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 308

`(blank)`

Blank line used to separate nearby statements.
### Line 309

`# Context snapshot serialization`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 310

`ctx = model.get_learner_context(state, current_topic="Superposition")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 311

`assert ctx.user_id == "learner_f"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 312

`assert ctx.concept_scores["grover.search_problem"] == 1.0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 313

`assert ctx.gap_inferences["grover.search_problem"]["status"] == "mastered"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.

## Nearby Files

[tests/adaptive/__init__.py](__init__.py.md), [tests/adaptive/test_activities.py](test_activities.py.md), [tests/adaptive/test_diagnostics.py](test_diagnostics.py.md), [tests/adaptive/test_evidence.py](test_evidence.py.md), [tests/adaptive/test_evidence_progression.py](test_evidence_progression.py.md), [tests/adaptive/test_mastery.py](test_mastery.py.md), [tests/adaptive/test_models.py](test_models.py.md), [tests/adaptive/test_pass4_evidence_trace.py](test_pass4_evidence_trace.py.md)
