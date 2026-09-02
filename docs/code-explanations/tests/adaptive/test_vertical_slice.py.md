# Explanation: `tests/adaptive/test_vertical_slice.py`

## Purpose

This page explains the meaningful behavior in `tests/adaptive/test_vertical_slice.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
from backend.adaptive.activities import get_activity
from backend.adaptive.engine import LearnerModel
from backend.adaptive.evidence import (
    evaluate_conceptual_response,
    evaluate_quantum_prediction,
)
from backend.adaptive.models import LearnerState
from backend.quantum import QuantumExperiment, run_experiment


def test_complete_vertical_slice_integration():
    """
    Vertical Slice Integration Test:
      1. Retrieve Activity (Grover 2-Qubit Target Prediction).
      2. Execute real M3 Quantum Engine simulation.
      3. Capture verified quantum result without Qiskit leaks.
      4. Learner makes incorrect prediction -> generates empirical LearnerEvidence.
      5. M2 processes evidence (Case B: single error -> gathers evidence).
      6. Learner makes second incorrect prediction -> M2 updates confidence & selects remediation.
      7. Learner completes remediation activity successfully.
      8. M2 records improvement and routes back to main sequence.
      9. Learner makes correct prediction on Grover task -> M2 advances to next activity.
    """
    model = LearnerModel()
    state = LearnerState(user_id="learner_demo_01")

    # Step 1: Get initial activity
    activity = get_activity("act_grover_2q_predict")
    assert activity.quantum_experiment is not None

    # Step 2 & 3: Real M3 execution (unmodified M3 engine)
    experiment = QuantumExperiment(**activity.quantum_experiment)
    sim_result = run_experiment(experiment)

    assert sim_result.algorithm == "grover"
    assert sim_result.target_state == "10"
    assert sim_result.most_likely_state == "10"
    assert sim_result.target_probability > 0.90
    assert sim_result.circuit is not None
    assert sim_result.circuit.num_qubits == 2

    # Step 4 & 5: Learner makes 1st incorrect prediction "01"
    evidence_1 = evaluate_quantum_prediction(
        learner_id=state.user_id,
        activity_id=activity.activity_id,
        concept_id=activity.concept_id,
        prediction="01",
        simulation_result=sim_result.to_dict(),
        attempt_number=1,
    )
    assert evidence_1.is_correct is False
    assert evidence_1.verified_result["most_likely_state"] == "10"

    # Step 6: M2 ingestion of Attempt 1 -> Single error does not jump to remediation
    decision_1 = model.record_evidence(evidence_1, state)
    assert decision_1.action == "gather_evidence"
    assert decision_1.target == "act_grover_2q_predict"

    inference_1 = state.gap_inferences["grover.search_problem"]
    assert inference_1["confidence"] == 0.35
    assert inference_1["status"] == "observing"

    # Step 7: Learner makes 2nd incorrect prediction "00"
    evidence_2 = evaluate_quantum_prediction(
        learner_id=state.user_id,
        activity_id=activity.activity_id,
        concept_id=activity.concept_id,
        prediction="00",
        simulation_result=sim_result.to_dict(),
        attempt_number=2,
    )
    decision_2 = model.record_evidence(evidence_2, state)

    # Repeated error elevates confidence and triggers targeted remediation
    assert decision_2.action == "targeted_remediation"
    assert decision_2.target == "act_measurement_prob_diagnostic"

    inference_2 = state.gap_inferences["grover.search_problem"]
    assert inference_2["confidence"] == 0.90
    assert inference_2["status"] == "remediation_needed"

    # Step 8: Learner takes remediation activity "act_measurement_prob_diagnostic"
    remed_act = get_activity("act_measurement_prob_diagnostic")
    evidence_remed = evaluate_conceptual_response(
        learner_id=state.user_id,
        activity_id=remed_act.activity_id,
        concept_id=remed_act.concept_id,
        selected_option="B",
        expected_option=remed_act.expected_answer,
    )
    assert evidence_remed.is_correct is True

    decision_3 = model.record_evidence(evidence_remed, state)
    assert decision_3.action == "advance"
    assert decision_3.target == "act_grover_2q_predict"

    # Step 9: Learner re-attempts Grover prediction with correct state "10"
    evidence_success = evaluate_quantum_prediction(
        learner_id=state.user_id,
        activity_id=activity.activity_id,
        concept_id=activity.concept_id,
        prediction="10",
        simulation_result=sim_result.to_dict(),
        attempt_number=3,
    )
    assert evidence_success.is_correct is True

    decision_4 = model.record_evidence(evidence_success, state)
    assert decision_4.action == "advance"
    assert decision_4.target == "act_grover_iteration_reasoning"

    inference_4 = state.gap_inferences["grover.search_problem"]
    assert inference_4["status"] == "improving"
    assert inference_4["confidence"] == 0.15

    # Step 10: Verify complete learner context summary
    context = model.get_learner_context(state, current_topic="Superposition")
    assert context.user_id == state.user_id
    assert "grover.search_problem" in context.gap_inferences
    assert len(state.evidence_history) == 4

```

## Line Notes

### Line 1

`from backend.adaptive.activities import get_activity`

Imports a dependency or project symbol so later code can use it by name.
### Line 2

`from backend.adaptive.engine import LearnerModel`

Imports a dependency or project symbol so later code can use it by name.
### Line 3

`from backend.adaptive.evidence import (`

Imports a dependency or project symbol so later code can use it by name.
### Line 4

`evaluate_conceptual_response,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 5

`evaluate_quantum_prediction,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 6

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 7

`from backend.adaptive.models import LearnerState`

Imports a dependency or project symbol so later code can use it by name.
### Line 8

`from backend.quantum import QuantumExperiment, run_experiment`

Imports a dependency or project symbol so later code can use it by name.
### Line 9

`(blank)`

Blank line used to separate nearby statements.
### Line 11

`def test_complete_vertical_slice_integration():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 12

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 13

`Vertical Slice Integration Test:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 14

`1. Retrieve Activity (Grover 2-Qubit Target Prediction).`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 15

`2. Execute real M3 Quantum Engine simulation.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 16

`3. Capture verified quantum result without Qiskit leaks.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 17

`4. Learner makes incorrect prediction -> generates empirical LearnerEvidence.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 18

`5. M2 processes evidence (Case B: single error -> gathers evidence).`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 19

`6. Learner makes second incorrect prediction -> M2 updates confidence & selects remediation.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 20

`7. Learner completes remediation activity successfully.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 21

`8. M2 records improvement and routes back to main sequence.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 22

`9. Learner makes correct prediction on Grover task -> M2 advances to next activity.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 23

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 24

`model = LearnerModel()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 25

`state = LearnerState(user_id="learner_demo_01")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 26

`(blank)`

Blank line used to separate nearby statements.
### Line 27

`# Step 1: Get initial activity`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 28

`activity = get_activity("act_grover_2q_predict")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 29

`assert activity.quantum_experiment is not None`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 30

`(blank)`

Blank line used to separate nearby statements.
### Line 31

`# Step 2 & 3: Real M3 execution (unmodified M3 engine)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 32

`experiment = QuantumExperiment(**activity.quantum_experiment)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 33

`sim_result = run_experiment(experiment)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 34

`(blank)`

Blank line used to separate nearby statements.
### Line 35

`assert sim_result.algorithm == "grover"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 36

`assert sim_result.target_state == "10"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 37

`assert sim_result.most_likely_state == "10"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 38

`assert sim_result.target_probability > 0.90`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 39

`assert sim_result.circuit is not None`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 40

`assert sim_result.circuit.num_qubits == 2`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 41

`(blank)`

Blank line used to separate nearby statements.
### Line 42

`# Step 4 & 5: Learner makes 1st incorrect prediction "01"`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 43

`evidence_1 = evaluate_quantum_prediction(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 44

`learner_id=state.user_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 45

`activity_id=activity.activity_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 46

`concept_id=activity.concept_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 47

`prediction="01",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 48

`simulation_result=sim_result.to_dict(),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 49

`attempt_number=1,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 50

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 51

`assert evidence_1.is_correct is False`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 52

`assert evidence_1.verified_result["most_likely_state"] == "10"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 53

`(blank)`

Blank line used to separate nearby statements.
### Line 54

`# Step 6: M2 ingestion of Attempt 1 -> Single error does not jump to remediation`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 55

`decision_1 = model.record_evidence(evidence_1, state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 56

`assert decision_1.action == "gather_evidence"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 57

`assert decision_1.target == "act_grover_2q_predict"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 58

`(blank)`

Blank line used to separate nearby statements.
### Line 59

`inference_1 = state.gap_inferences["grover.search_problem"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 60

`assert inference_1["confidence"] == 0.35`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 61

`assert inference_1["status"] == "observing"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 62

`(blank)`

Blank line used to separate nearby statements.
### Line 63

`# Step 7: Learner makes 2nd incorrect prediction "00"`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 64

`evidence_2 = evaluate_quantum_prediction(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 65

`learner_id=state.user_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 66

`activity_id=activity.activity_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 67

`concept_id=activity.concept_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 68

`prediction="00",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 69

`simulation_result=sim_result.to_dict(),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 70

`attempt_number=2,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 71

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 72

`decision_2 = model.record_evidence(evidence_2, state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 73

`(blank)`

Blank line used to separate nearby statements.
### Line 74

`# Repeated error elevates confidence and triggers targeted remediation`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 75

`assert decision_2.action == "targeted_remediation"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 76

`assert decision_2.target == "act_measurement_prob_diagnostic"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 77

`(blank)`

Blank line used to separate nearby statements.
### Line 78

`inference_2 = state.gap_inferences["grover.search_problem"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 79

`assert inference_2["confidence"] == 0.90`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 80

`assert inference_2["status"] == "remediation_needed"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 81

`(blank)`

Blank line used to separate nearby statements.
### Line 82

`# Step 8: Learner takes remediation activity "act_measurement_prob_diagnostic"`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 83

`remed_act = get_activity("act_measurement_prob_diagnostic")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 84

`evidence_remed = evaluate_conceptual_response(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 85

`learner_id=state.user_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 86

`activity_id=remed_act.activity_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 87

`concept_id=remed_act.concept_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 88

`selected_option="B",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 89

`expected_option=remed_act.expected_answer,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 90

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 91

`assert evidence_remed.is_correct is True`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 92

`(blank)`

Blank line used to separate nearby statements.
### Line 93

`decision_3 = model.record_evidence(evidence_remed, state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 94

`assert decision_3.action == "advance"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 95

`assert decision_3.target == "act_grover_2q_predict"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 96

`(blank)`

Blank line used to separate nearby statements.
### Line 97

`# Step 9: Learner re-attempts Grover prediction with correct state "10"`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 98

`evidence_success = evaluate_quantum_prediction(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 99

`learner_id=state.user_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 100

`activity_id=activity.activity_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 101

`concept_id=activity.concept_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 102

`prediction="10",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 103

`simulation_result=sim_result.to_dict(),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 104

`attempt_number=3,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 105

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 106

`assert evidence_success.is_correct is True`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 107

`(blank)`

Blank line used to separate nearby statements.
### Line 108

`decision_4 = model.record_evidence(evidence_success, state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 109

`assert decision_4.action == "advance"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 110

`assert decision_4.target == "act_grover_iteration_reasoning"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 111

`(blank)`

Blank line used to separate nearby statements.
### Line 112

`inference_4 = state.gap_inferences["grover.search_problem"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 113

`assert inference_4["status"] == "improving"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 114

`assert inference_4["confidence"] == 0.15`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 115

`(blank)`

Blank line used to separate nearby statements.
### Line 116

`# Step 10: Verify complete learner context summary`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 117

`context = model.get_learner_context(state, current_topic="Superposition")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 118

`assert context.user_id == state.user_id`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 119

`assert "grover.search_problem" in context.gap_inferences`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 120

`assert len(state.evidence_history) == 4`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.

## Nearby Files

[tests/adaptive/__init__.py](__init__.py.md), [tests/adaptive/test_activities.py](test_activities.py.md), [tests/adaptive/test_diagnostics.py](test_diagnostics.py.md), [tests/adaptive/test_evidence.py](test_evidence.py.md), [tests/adaptive/test_evidence_progression.py](test_evidence_progression.py.md), [tests/adaptive/test_mastery.py](test_mastery.py.md), [tests/adaptive/test_models.py](test_models.py.md), [tests/adaptive/test_pass4_evidence_trace.py](test_pass4_evidence_trace.py.md)
