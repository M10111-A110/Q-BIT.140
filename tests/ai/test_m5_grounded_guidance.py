import json
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from backend.adaptive import (
    InMemoryLearnerRepository,
    LearnerModel,
    LearnerState,
    evaluate_quantum_prediction,
    get_activity,
)
from backend.ai import (
    LLMProvider,
    MockLLMProvider,
    ask_question,
    explain_experiment,
)
from backend.ai.prompts import build_ask_prompt, build_experiment_explanation_prompt
from backend.ai.retrieval import find_relevant_knowledge
from backend.api.dependencies import reset_dependencies, set_learner_repository, set_llm_provider
from backend.api.main import app
from backend.quantum import QuantumExperiment, run_experiment


def test_complete_m3_m2_m5_context_propagation():
    """
    Verify complete vertical flow:
      M3 Simulation -> M2 Evidence Evaluation -> M2 Adaptive Decision -> M5 Grounded Prompt & Explanation.
    """
    # 1. Real M3 Execution
    act = get_activity("act_grover_2q_predict")
    assert act.quantum_experiment is not None
    exp = QuantumExperiment(**act.quantum_experiment)
    sim_result = run_experiment(exp)
    verified_dict = sim_result.to_dict()

    # 2. M2 Evaluation & State Update
    model = LearnerModel()
    state = LearnerState(user_id="learner_m5_flow")
    ev = evaluate_quantum_prediction(
        learner_id=state.user_id,
        activity_id=act.activity_id,
        concept_id=act.concept_id,
        prediction="01",  # mismatch with target "10"
        simulation_result=verified_dict,
        attempt_number=1,
    )
    decision = model.record_evidence(ev, state)

    # 3. M5 Grounded Explanation
    provider = MockLLMProvider()
    explanation = explain_experiment(
        learner_response="01",
        verified_result=verified_dict,
        evidence=ev.to_dict(),
        adaptive_decision=decision.to_dict(),
        provider=provider,
    )

    assert "Quantum Execution Analysis" in explanation
    assert "Adaptive Learning Path" in explanation
    assert "gather_evidence" in explanation
    assert "$|01\\rangle$" in explanation
    assert "$|10\\rangle$" in explanation


def test_explicit_distinction_between_prediction_target_and_empirical_states():
    """
    Verify prompt builder separates:
      1. Learner Predicted State
      2. Theoretical Target State
      3. Empirical Most-Likely Measured State
    """
    verified_result = {
        "target_state": "10",
        "most_likely_state": "10",
        "target_probability": 0.9375,
        "counts": {"00": 10, "01": 15, "10": 950, "11": 25},
        "shots": 1000,
        "circuit": {"qubits": 2, "gates": 12},
    }
    evidence = {
        "concept_id": "grover.search_problem",
        "is_correct": False,
        "evaluation_details": {"predicted_state": "00", "most_likely_state": "10", "match": False},
    }
    adaptive_decision = {
        "action": "gather_evidence",
        "target": "act_grover_2q_predict",
        "reason": "Initial prediction mismatch.",
        "concept_id": "grover.search_problem",
    }

    messages = build_experiment_explanation_prompt(
        learner_response="00",
        verified_result=verified_result,
        evidence=evidence,
        adaptive_decision=adaptive_decision,
        curriculum_context="Sample curriculum text",
    )

    user_content = messages[1]["content"]
    assert "- Learner Predicted State / Response: 00" in user_content
    assert "- Theoretical Target State: 10" in user_content
    assert "- Empirical Most-Likely Measured State: 10" in user_content
    assert "- Target State Probability: 0.9375" in user_content
    assert "- Empirical Measurement Counts: {\"00\": 10, \"01\": 15, \"10\": 950, \"11\": 25}" in user_content


def test_relevant_concept_aware_retrieval():
    """
    Verify that query on probability/shots retrieves probability docs,
    and query on Grover retrieves Grover docs.
    """
    prob_result = find_relevant_knowledge("amplitudes probabilities counts shots frequency", top_n=1)
    assert "02_math_probability.md" in prob_result

    grover_result = find_relevant_knowledge("Grover oracle phase marking diffusion amplitude amplification", top_n=1)
    assert "07_grovers_algorithm.md" in grover_result


def test_irrelevant_retrieval_not_blindly_concatenated():
    """
    Verify that queries with non-matching terms do not blindly concatenate
    unrelated documents.
    """
    result = find_relevant_knowledge("xyzxyz12345 nonmatchinggibberishquery", top_n=2)
    # Should return fallback rather than multiple irrelevant files
    assert "07_grovers_algorithm.md" in result or "foundations" in result.lower()
    assert "--- From 01_math_linear_algebra.md ---" not in result


def test_m5_explains_adaptive_decision_faithfully():
    """
    Verify M5 prompt and mock provider faithfully describe the M2 decision action and reason.
    """
    provider = MockLLMProvider()
    explanation = explain_experiment(
        learner_response="00",
        verified_result={"target_state": "10", "most_likely_state": "10"},
        evidence={"concept_id": "grover.search_problem", "is_correct": False},
        adaptive_decision={
            "action": "targeted_remediation",
            "target": "act_measurement_prob_diagnostic",
            "reason": "Repeated errors indicate prerequisite gap in measurement.",
            "concept_id": "grover.search_problem",
        },
        provider=provider,
    )

    assert "targeted_remediation" in explanation
    assert "Repeated errors indicate prerequisite gap in measurement" in explanation


def test_m5_failure_does_not_corrupt_m2_or_m3_state():
    """
    Verify that if the AI provider fails (e.g. raises exception),
    the repository and learner state remain intact and uncorrupted.
    """
    client = TestClient(app)
    repo = InMemoryLearnerRepository()
    set_learner_repository(repo)

    # 1. Successful submission updates M3 and persists M2 state
    sub_res = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_safe_test", "response": "10"},
    )
    assert sub_res.status_code == 200
    sub_data = sub_res.json()
    assert repo.exists("u_safe_test") is True

    # 2. Inject a failing LLM provider
    class FailingLLMProvider(LLMProvider):
        def generate(self, messages, model=None):
            raise RuntimeError("Groq API rate limit exceeded")

    set_llm_provider(FailingLLMProvider())

    # 3. Call AI explanation endpoint -> returns 503
    ai_res = client.post(
        "/api/ai/explain_experiment",
        json={
            "learner_response": "10",
            "verified_result": sub_data["verified_result"],
            "evidence": sub_data["evidence"],
            "adaptive_decision": sub_data["adaptive_decision"],
        },
    )
    assert ai_res.status_code == 503
    assert "AI guidance service is currently unavailable" in ai_res.json()["detail"]

    # 4. Verify M2 learner state in repository is completely intact and unchanged
    persisted_state = repo.get("u_safe_test")
    assert len(persisted_state.evidence_history) == 1
    assert persisted_state.evidence_history[0]["is_correct"] is True

    reset_dependencies()


def test_katex_math_formula_formatting():
    """
    Verify all generated guidance contains valid KaTeX math markers ($ or $$).
    """
    provider = MockLLMProvider()

    # QA Output
    ans1 = ask_question("Tell me about quantum gates and Hadamard", provider=provider)
    assert "$" in ans1

    # Experiment Explanation Output
    exp1 = explain_experiment(
        learner_response="10",
        verified_result={"target_state": "10", "most_likely_state": "10"},
        evidence={"is_correct": True},
        adaptive_decision={"action": "advance", "reason": "Good job"},
        provider=provider,
    )
    assert "$" in exp1
    assert "O|w\\rangle = -|w\\rangle" in exp1
    assert "P(x) = |\\alpha_x|^2" in exp1


def test_json_safe_ai_request_response_contracts():
    """
    Verify that AI requests and responses serialize cleanly with strict JSON compliance.
    """
    client = TestClient(app)
    set_llm_provider(MockLLMProvider())

    # 1. Ask endpoint
    ask_req = {
        "question": "What is superposition?",
        "concept_id": "quantum.superposition",
        "learner_context": {"concept_mastery": {"quantum.superposition": 0.8}},
    }
    ask_res = client.post("/api/ai/ask", json=ask_req)
    assert ask_res.status_code == 200
    data = ask_res.json()
    assert "answer" in data
    assert isinstance(data["answer"], str)
    assert json.dumps(data)  # Valid JSON

    # 2. Explain experiment endpoint
    exp_req = {
        "learner_response": "10",
        "verified_result": {"algorithm": "grover", "target_state": "10"},
        "evidence": {"concept_id": "grover.search_problem", "is_correct": True},
        "adaptive_decision": {"action": "advance", "target": "act_grover_iteration_reasoning"},
    }
    exp_res = client.post("/api/ai/explain_experiment", json=exp_req)
    assert exp_res.status_code == 200
    exp_data = exp_res.json()
    assert "explanation" in exp_data
    assert json.dumps(exp_data)  # Valid JSON

    reset_dependencies()


# ===========================================================================
# GENERAL M5 GROUNDED GUIDANCE REGRESSION SUITE (TESTS A - G & CONSTRAINTS)
# ===========================================================================

def test_a_conceptual_response_grounding_no_execution_fabrication():
    """
    Requirement A: conceptual_response attempt produces a grounded Concept Explanation
    and strictly omits quantum execution claims, fake Dirac kets (|B⟩), fake outcomes (|N/A⟩),
    and 1024-shot counts.
    """
    provider = MockLLMProvider()
    evidence = {
        "evidence_id": "ev_diag_born_01",
        "evidence_type": "conceptual_response",
        "evidence_source": "learner",
        "concept_id": "quantum.measurement",
        "activity_id": "act_measurement_prob_diagnostic",
        "learner_response": "B",
        "is_correct": True,
        "evaluation_details": {"selected_option": "B", "expected_option": "B", "match": True},
    }
    adaptive_decision = {
        "decision_id": "dec_meas_adv_01",
        "action": "advance",
        "target": "act_grover_2q_predict",
        "reason": "Demonstrated understanding of measurement probabilities.",
        "concept_id": "quantum.measurement",
        "trigger": "correct_prediction_advancement",
        "evidence_sufficiency": "sufficient_for_observation",
        "supporting_evidence_ids": ["ev_diag_born_01"],
    }

    explanation = explain_experiment(
        learner_response="B",
        verified_result=None,  # NO quantum execution
        evidence=evidence,
        adaptive_decision=adaptive_decision,
        provider=provider,
    )

    # 1. Heading and structure are evidence-appropriate
    assert "### Concept Explanation" in explanation
    assert "### Quantum Execution Analysis" not in explanation

    # 2. No fabricated Dirac kets for MCQ option letters
    assert "|B⟩" not in explanation
    assert "|B\\rangle" not in explanation
    assert "Option **B**" in explanation

    # 3. No fabricated N/A states or shot counts
    assert "|N/A⟩" not in explanation
    assert "|N/A\\rangle" not in explanation
    assert "Theoretical target is" not in explanation
    assert "1024 shots" not in explanation

    # 4. Correct conceptual explanation for Born's rule
    assert "Born's rule" in explanation or "Born" in explanation
    assert "$P(x) = |\\alpha_x|^2$" in explanation or "P(x)" in explanation
    assert "advance" in explanation
    assert "ev_diag_born_01" in explanation


def test_b_quantum_execution_grounding_preserves_verified_facts():
    """
    Requirement B: quantum_prediction attempt with real execution data produces
    Quantum Execution Analysis and compares prediction vs empirical outcome accurately.
    """
    provider = MockLLMProvider()
    evidence = {
        "evidence_id": "ev_grover_exec_01",
        "evidence_type": "quantum_prediction",
        "evidence_source": "learner_and_quantum_execution",
        "concept_id": "grover.search_problem",
        "activity_id": "act_grover_2q_predict",
        "learner_response": "01",
        "is_correct": False,
        "evaluation_details": {"predicted_state": "01", "most_likely_state": "10", "match": False},
    }
    verified_result = {
        "algorithm": "grover",
        "target_state": "10",
        "most_likely_state": "10",
        "target_probability": 0.9375,
        "counts": {"00": 10, "01": 15, "10": 950, "11": 25},
        "shots": 1024,
        "circuit": {"num_qubits": 2, "depth": 8},
    }
    adaptive_decision = {
        "decision_id": "dec_grover_gather_01",
        "action": "gather_evidence",
        "target": "act_grover_2q_predict",
        "reason": "Single prediction mismatch.",
        "concept_id": "grover.search_problem",
        "trigger": "single_prediction_mismatch",
        "evidence_sufficiency": "insufficient",
        "supporting_evidence_ids": ["ev_grover_exec_01"],
    }

    explanation = explain_experiment(
        learner_response="01",
        verified_result=verified_result,
        evidence=evidence,
        adaptive_decision=adaptive_decision,
        provider=provider,
    )

    # 1. Execution analysis is present
    assert "### Quantum Execution Analysis" in explanation
    assert "$|01\\rangle$" in explanation
    assert "$|10\\rangle$" in explanation
    assert "Theoretical target is $|10\\rangle$" in explanation

    # 2. Physical mechanism is explained
    assert "phase oracle" in explanation.lower() or "oracle" in explanation.lower()
    assert "diffusion operator" in explanation.lower() or "diffusion" in explanation.lower()

    # 3. Adaptive decision is preserved
    assert "gather_evidence" in explanation
    assert "single_prediction_mismatch" in explanation


def test_c_adaptive_decision_grounding_references_supplied_facts():
    """
    Requirement C: M5 explanation references M2 decision facts (sufficiency, trigger,
    hypothesis, target) without manufacturing fake quantum execution results.
    """
    provider = MockLLMProvider()
    evidence = {
        "evidence_id": "ev_superposition_01",
        "evidence_type": "conceptual_response",
        "concept_id": "quantum.superposition",
        "activity_id": "act_superposition_remediation",
        "learner_response": "B",
        "is_correct": True,
    }
    adaptive_decision = {
        "decision_id": "dec_remed_adv_01",
        "action": "advance",
        "target": "act_measurement_prob_diagnostic",
        "reason": "Successfully reinforced equal superposition prerequisite.",
        "concept_id": "quantum.superposition",
        "trigger": "post_intervention_recovery",
        "evidence_sufficiency": "sufficient_for_improvement_observation",
        "supporting_evidence_ids": ["ev_superposition_01"],
    }

    explanation = explain_experiment(
        learner_response="B",
        verified_result=None,
        evidence=evidence,
        adaptive_decision=adaptive_decision,
        provider=provider,
    )

    # References supplied adaptive facts
    assert "advance" in explanation
    assert "Successfully reinforced equal superposition prerequisite" in explanation
    assert "post_intervention_recovery" in explanation
    assert "sufficient_for_improvement_observation" in explanation
    assert "ev_superposition_01" in explanation
    assert "Quantum Execution Analysis" not in explanation


def test_c2_adaptive_decision_qa_inquiry_explains_decision_specifically():
    """
    Requirement C2: Standalone QA inquiry about next activity recommendation
    explains supplied action, target, reason, trigger, sufficiency, hypothesis, and evidence IDs.
    """
    provider = MockLLMProvider()
    learner_context = {
        "recommendation": {
            "action": "targeted_remediation",
            "target": "act_measurement_prob_diagnostic",
            "reason": "Repeated prediction errors indicate prerequisite bottleneck in measurement.",
            "trigger": "repeated_prediction_error",
            "evidence_sufficiency": "sufficient_for_targeted_inference",
            "supporting_evidence_ids": ["ev_01", "ev_02"],
        },
        "gap_inferences": {
            "grover.search_problem": {
                "hypothesis": "possible_grover_search_problem_difficulty",
                "status": "remediation_needed",
                "trend": "persistent_difficulty",
            }
        },
    }

    ans = ask_question(
        question="Why was this next activity selected for remediation?",
        learner_context=learner_context,
        provider=provider,
    )

    assert "### Adaptive Decision Explanation" in ans
    assert "targeted_remediation" in ans
    assert "act_measurement_prob_diagnostic" in ans
    assert "Repeated prediction errors indicate prerequisite bottleneck in measurement" in ans
    assert "repeated_prediction_error" in ans
    assert "sufficient_for_targeted_inference" in ans
    assert "possible_grover_search_problem_difficulty" in ans
    assert '["ev_01", "ev_02"]' in ans
    assert "Quantum Execution Analysis" not in ans
    assert "Selected Option" not in ans


def test_d_missing_execution_fields_omitted_not_rendered_as_fake_observed_values():

    """
    Requirement D: When verified_result has missing fields (e.g. target_state omitted),
    the explanation omits that claim rather than rendering '|N/A>' or fake values.
    """
    provider = MockLLMProvider()
    evidence = {
        "evidence_id": "ev_partial_01",
        "evidence_type": "quantum_prediction",
        "concept_id": "grover.search_problem",
        "learner_response": "10",
        "is_correct": True,
    }
    # verified_result without target_state and without shots
    verified_result = {
        "algorithm": "grover",
        "most_likely_state": "10",
    }
    adaptive_decision = {
        "action": "advance",
        "reason": "Correct prediction.",
    }

    explanation = explain_experiment(
        learner_response="10",
        verified_result=verified_result,
        evidence=evidence,
        adaptive_decision=adaptive_decision,
        provider=provider,
    )

    assert "Quantum Execution Analysis" in explanation
    assert "$|10\\rangle$" in explanation
    assert "|N/A⟩" not in explanation
    assert "|N/A\\rangle" not in explanation
    assert "Theoretical target is |N/A⟩" not in explanation
    assert "N/A shots" not in explanation


def test_e_compound_question_prediction_execution_requires_actual_evidence():
    """
    Requirement E: 'Why did my Grover prediction differ from the verified result?'
    produces honest notice when NO execution evidence is in context, and produces
    prediction/result explanation when execution evidence IS present.
    """
    provider = MockLLMProvider()

    # Case 1: No execution context provided in prompt
    ans_no_evidence = ask_question(
        question="Why did my Grover prediction differ from the verified result?",
        learner_context=None,
        provider=provider,
    )
    assert "The available evidence does not include a quantum execution result, so there is no measurement outcome to compare here." in ans_no_evidence
    assert "Your prediction was" not in ans_no_evidence

    # Case 2: Execution context IS provided in learner_context
    ans_with_evidence = ask_question(
        question="Why did my Grover prediction differ from the verified result?",
        learner_context={"most_likely_state": "10", "counts": {"00": 10, "10": 950}},
        provider=provider,
    )
    assert "Prediction vs Quantum Execution" in ans_with_evidence
    assert "The available evidence does not include a quantum execution result" not in ans_with_evidence


def test_f_generic_concept_question_no_learner_execution_claims():
    """
    Requirement F: 'What is Grover's algorithm?' produces conceptual explanation
    without fabricating learner-specific execution claims.
    """
    provider = MockLLMProvider()
    ans = ask_question("What is Grover's algorithm?", provider=provider)

    assert "Grover's Algorithm Overview" in ans
    assert "Your prediction was" not in ans
    assert "empirical 1024-shot" not in ans
    assert "$" in ans


def test_g_unknown_question_honest_fallback():
    """
    Requirement G: Out-of-scope question returns honest guidance fallback.
    """
    provider = MockLLMProvider()
    ans = ask_question("How do I bake sourdough bread with olive oil?", provider=provider)

    assert "Q-BIT AI Guidance" in ans
    assert "I can explain what a qubit is, quantum superposition, measurement probability" in ans


def test_constraint15_conceptual_response_with_grover_curriculum_does_not_produce_execution_analysis():
    """
    Constraint 15: An activity with conceptual_response on a Grover topic (e.g. over-rotation)
    with Grover curriculum context MUST NOT produce a Quantum Execution Analysis.
    """
    provider = MockLLMProvider()
    evidence = {
        "evidence_id": "ev_grover_iter_01",
        "evidence_type": "conceptual_response",
        "concept_id": "grover.amplitude_amplification",
        "activity_id": "act_grover_iteration_reasoning",
        "learner_response": "B",
        "is_correct": True,
        "evaluation_details": {"selected_option": "B", "expected_option": "B", "match": True},
    }
    adaptive_decision = {
        "decision_id": "dec_grover_iter_01",
        "action": "advance",
        "reason": "Demonstrated mastery of Grover iteration oscillation.",
        "concept_id": "grover.amplitude_amplification",
        "trigger": "consecutive_mastery_success",
        "evidence_sufficiency": "sufficient_for_mastery",
    }

    explanation = explain_experiment(
        learner_response="B",
        verified_result=None,  # Conceptual interaction, no simulation run
        evidence=evidence,
        adaptive_decision=adaptive_decision,
        provider=provider,
    )

    assert "### Concept Explanation" in explanation
    assert "### Quantum Execution Analysis" not in explanation
    assert "1024 shots" not in explanation
    assert "Theoretical target is" not in explanation
    assert "|B⟩" not in explanation
    assert "|B\\rangle" not in explanation
    assert "oscillatory" in explanation.lower() or "rotation" in explanation.lower() or "over-rotation" in explanation.lower()


def test_constraint16_quantum_execution_with_prediction_produces_execution_analysis():
    """
    Constraint 16: An activity with quantum_prediction and verified simulation
    DOES produce the Quantum Execution Analysis.
    """
    provider = MockLLMProvider()
    evidence = {
        "evidence_id": "ev_grover_pred_success",
        "evidence_type": "quantum_prediction",
        "concept_id": "grover.search_problem",
        "activity_id": "act_grover_2q_predict",
        "learner_response": "10",
        "is_correct": True,
        "evaluation_details": {"predicted_state": "10", "most_likely_state": "10", "match": True},
    }
    verified_result = {
        "algorithm": "grover",
        "target_state": "10",
        "most_likely_state": "10",
        "target_probability": 0.938,
        "shots": 1024,
    }
    adaptive_decision = {
        "action": "advance",
        "target": "act_grover_iteration_reasoning",
        "reason": "Correct prediction demonstrating search problem understanding.",
    }

    explanation = explain_experiment(
        learner_response="10",
        verified_result=verified_result,
        evidence=evidence,
        adaptive_decision=adaptive_decision,
        provider=provider,
    )

    assert "### Quantum Execution Analysis" in explanation
    assert "Your prediction of state $|10\\rangle$ correctly matched the empirical simulation outcome $|10\\rangle$" in explanation
    assert "Theoretical target is $|10\\rangle$" in explanation
