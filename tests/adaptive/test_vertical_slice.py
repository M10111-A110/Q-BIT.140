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
