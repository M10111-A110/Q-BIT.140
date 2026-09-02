# Explanation: `tests/ai/test_m5_grounded_guidance.py`

## Purpose

This page explains the meaningful behavior in `tests/ai/test_m5_grounded_guidance.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
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

```

## Line Notes

### Line 1

`import json`

Imports a dependency or project symbol so later code can use it by name.
### Line 2

`import pytest`

Imports a dependency or project symbol so later code can use it by name.
### Line 3

`from unittest.mock import MagicMock`

Imports a dependency or project symbol so later code can use it by name.
### Line 4

`from fastapi.testclient import TestClient`

Imports a dependency or project symbol so later code can use it by name.
### Line 5

`(blank)`

Blank line used to separate nearby statements.
### Line 6

`from backend.adaptive import (`

Imports a dependency or project symbol so later code can use it by name.
### Line 7

`InMemoryLearnerRepository,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 8

`LearnerModel,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 9

`LearnerState,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 10

`evaluate_quantum_prediction,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 11

`get_activity,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 12

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 13

`from backend.ai import (`

Imports a dependency or project symbol so later code can use it by name.
### Line 14

`LLMProvider,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 15

`MockLLMProvider,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 16

`ask_question,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 17

`explain_experiment,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 18

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 19

`from backend.ai.prompts import build_ask_prompt, build_experiment_explanation_prompt`

Imports a dependency or project symbol so later code can use it by name.
### Line 20

`from backend.ai.retrieval import find_relevant_knowledge`

Imports a dependency or project symbol so later code can use it by name.
### Line 21

`from backend.api.dependencies import reset_dependencies, set_learner_repository, set_llm_provider`

Imports a dependency or project symbol so later code can use it by name.
### Line 22

`from backend.api.main import app`

Imports a dependency or project symbol so later code can use it by name.
### Line 23

`from backend.quantum import QuantumExperiment, run_experiment`

Imports a dependency or project symbol so later code can use it by name.
### Line 24

`(blank)`

Blank line used to separate nearby statements.
### Line 26

`def test_complete_m3_m2_m5_context_propagation():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 27

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 28

`Verify complete vertical flow:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 29

`M3 Simulation -> M2 Evidence Evaluation -> M2 Adaptive Decision -> M5 Grounded Prompt & Explanation.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 30

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 31

`# 1. Real M3 Execution`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 32

`act = get_activity("act_grover_2q_predict")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 33

`assert act.quantum_experiment is not None`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 34

`exp = QuantumExperiment(**act.quantum_experiment)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 35

`sim_result = run_experiment(exp)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 36

`verified_dict = sim_result.to_dict()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 37

`(blank)`

Blank line used to separate nearby statements.
### Line 38

`# 2. M2 Evaluation & State Update`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 39

`model = LearnerModel()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 40

`state = LearnerState(user_id="learner_m5_flow")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 41

`ev = evaluate_quantum_prediction(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 42

`learner_id=state.user_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 43

`activity_id=act.activity_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 44

`concept_id=act.concept_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 45

`prediction="01",  # mismatch with target "10"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 46

`simulation_result=verified_dict,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 47

`attempt_number=1,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 48

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 49

`decision = model.record_evidence(ev, state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 50

`(blank)`

Blank line used to separate nearby statements.
### Line 51

`# 3. M5 Grounded Explanation`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 52

`provider = MockLLMProvider()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 53

`explanation = explain_experiment(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 54

`learner_response="01",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 55

`verified_result=verified_dict,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 56

`evidence=ev.to_dict(),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 57

`adaptive_decision=decision.to_dict(),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 58

`provider=provider,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 59

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 60

`(blank)`

Blank line used to separate nearby statements.
### Line 61

`assert "Quantum Execution Analysis" in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 62

`assert "Adaptive Learning Path" in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 63

`assert "gather_evidence" in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 64

`assert "$|01\\rangle$" in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 65

`assert "$|10\\rangle$" in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 66

`(blank)`

Blank line used to separate nearby statements.
### Line 68

`def test_explicit_distinction_between_prediction_target_and_empirical_states():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 69

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 70

`Verify prompt builder separates:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 71

`1. Learner Predicted State`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 72

`2. Theoretical Target State`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 73

`3. Empirical Most-Likely Measured State`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 74

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 75

`verified_result = {`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 76

`"target_state": "10",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 77

`"most_likely_state": "10",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 78

`"target_probability": 0.9375,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 79

`"counts": {"00": 10, "01": 15, "10": 950, "11": 25},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 80

`"shots": 1000,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 81

`"circuit": {"qubits": 2, "gates": 12},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 82

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 83

`evidence = {`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 84

`"concept_id": "grover.search_problem",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 85

`"is_correct": False,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 86

`"evaluation_details": {"predicted_state": "00", "most_likely_state": "10", "match": False},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 87

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 88

`adaptive_decision = {`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 89

`"action": "gather_evidence",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 90

`"target": "act_grover_2q_predict",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 91

`"reason": "Initial prediction mismatch.",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 92

`"concept_id": "grover.search_problem",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 93

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 94

`(blank)`

Blank line used to separate nearby statements.
### Line 95

`messages = build_experiment_explanation_prompt(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 96

`learner_response="00",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 97

`verified_result=verified_result,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 98

`evidence=evidence,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 99

`adaptive_decision=adaptive_decision,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 100

`curriculum_context="Sample curriculum text",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 101

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 102

`(blank)`

Blank line used to separate nearby statements.
### Line 103

`user_content = messages[1]["content"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 104

`assert "- Learner Predicted State / Response: 00" in user_content`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 105

`assert "- Theoretical Target State: 10" in user_content`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 106

`assert "- Empirical Most-Likely Measured State: 10" in user_content`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 107

`assert "- Target State Probability: 0.9375" in user_content`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 108

`assert "- Empirical Measurement Counts: {\"00\": 10, \"01\": 15, \"10\": 950, \"11\": 25}" in user_content`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 109

`(blank)`

Blank line used to separate nearby statements.
### Line 111

`def test_relevant_concept_aware_retrieval():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 112

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 113

`Verify that query on probability/shots retrieves probability docs,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 114

`and query on Grover retrieves Grover docs.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 115

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 116

`prob_result = find_relevant_knowledge("amplitudes probabilities counts shots frequency", top_n=1)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 117

`assert "02_math_probability.md" in prob_result`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 118

`(blank)`

Blank line used to separate nearby statements.
### Line 119

`grover_result = find_relevant_knowledge("Grover oracle phase marking diffusion amplitude amplification", top_n=1)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 120

`assert "07_grovers_algorithm.md" in grover_result`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 121

`(blank)`

Blank line used to separate nearby statements.
### Line 123

`def test_irrelevant_retrieval_not_blindly_concatenated():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 124

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 125

`Verify that queries with non-matching terms do not blindly concatenate`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 126

`unrelated documents.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 127

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 128

`result = find_relevant_knowledge("xyzxyz12345 nonmatchinggibberishquery", top_n=2)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 129

`# Should return fallback rather than multiple irrelevant files`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 130

`assert "07_grovers_algorithm.md" in result or "foundations" in result.lower()`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 131

`assert "--- From 01_math_linear_algebra.md ---" not in result`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 132

`(blank)`

Blank line used to separate nearby statements.
### Line 134

`def test_m5_explains_adaptive_decision_faithfully():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 135

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 136

`Verify M5 prompt and mock provider faithfully describe the M2 decision action and reason.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 137

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 138

`provider = MockLLMProvider()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 139

`explanation = explain_experiment(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 140

`learner_response="00",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 141

`verified_result={"target_state": "10", "most_likely_state": "10"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 142

`evidence={"concept_id": "grover.search_problem", "is_correct": False},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 143

`adaptive_decision={`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 144

`"action": "targeted_remediation",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 145

`"target": "act_measurement_prob_diagnostic",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 146

`"reason": "Repeated errors indicate prerequisite gap in measurement.",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 147

`"concept_id": "grover.search_problem",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 148

`},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 149

`provider=provider,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 150

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 151

`(blank)`

Blank line used to separate nearby statements.
### Line 152

`assert "targeted_remediation" in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 153

`assert "Repeated errors indicate prerequisite gap in measurement" in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 154

`(blank)`

Blank line used to separate nearby statements.
### Line 156

`def test_m5_failure_does_not_corrupt_m2_or_m3_state():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 157

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 158

`Verify that if the AI provider fails (e.g. raises exception),`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 159

`the repository and learner state remain intact and uncorrupted.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 160

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 161

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 162

`repo = InMemoryLearnerRepository()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 163

`set_learner_repository(repo)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 164

`(blank)`

Blank line used to separate nearby statements.
### Line 165

`# 1. Successful submission updates M3 and persists M2 state`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 166

`sub_res = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 167

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 168

`json={"learner_id": "u_safe_test", "response": "10"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 169

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 170

`assert sub_res.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 171

`sub_data = sub_res.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 172

`assert repo.exists("u_safe_test") is True`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 173

`(blank)`

Blank line used to separate nearby statements.
### Line 174

`# 2. Inject a failing LLM provider`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 175

`class FailingLLMProvider(LLMProvider):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 176

`def generate(self, messages, model=None):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 177

`raise RuntimeError("Groq API rate limit exceeded")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 178

`(blank)`

Blank line used to separate nearby statements.
### Line 179

`set_llm_provider(FailingLLMProvider())`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 180

`(blank)`

Blank line used to separate nearby statements.
### Line 181

`# 3. Call AI explanation endpoint -> returns 503`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 182

`ai_res = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 183

`"/api/ai/explain_experiment",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 184

`json={`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 185

`"learner_response": "10",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 186

`"verified_result": sub_data["verified_result"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 187

`"evidence": sub_data["evidence"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 188

`"adaptive_decision": sub_data["adaptive_decision"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 189

`},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 190

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 191

`assert ai_res.status_code == 503`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 192

`assert "AI guidance service is currently unavailable" in ai_res.json()["detail"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 193

`(blank)`

Blank line used to separate nearby statements.
### Line 194

`# 4. Verify M2 learner state in repository is completely intact and unchanged`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 195

`persisted_state = repo.get("u_safe_test")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 196

`assert len(persisted_state.evidence_history) == 1`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 197

`assert persisted_state.evidence_history[0]["is_correct"] is True`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 198

`(blank)`

Blank line used to separate nearby statements.
### Line 199

`reset_dependencies()`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 200

`(blank)`

Blank line used to separate nearby statements.
### Line 202

`def test_katex_math_formula_formatting():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 203

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 204

`Verify all generated guidance contains valid KaTeX math markers ($ or $$).`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 205

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 206

`provider = MockLLMProvider()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 207

`(blank)`

Blank line used to separate nearby statements.
### Line 208

`# QA Output`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 209

`ans1 = ask_question("Tell me about quantum gates and Hadamard", provider=provider)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 210

`assert "$" in ans1`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 211

`(blank)`

Blank line used to separate nearby statements.
### Line 212

`# Experiment Explanation Output`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 213

`exp1 = explain_experiment(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 214

`learner_response="10",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 215

`verified_result={"target_state": "10", "most_likely_state": "10"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 216

`evidence={"is_correct": True},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 217

`adaptive_decision={"action": "advance", "reason": "Good job"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 218

`provider=provider,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 219

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 220

`assert "$" in exp1`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 221

`assert "O|w\\rangle = -|w\\rangle" in exp1`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 222

`assert "P(x) = |\\alpha_x|^2" in exp1`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 223

`(blank)`

Blank line used to separate nearby statements.
### Line 225

`def test_json_safe_ai_request_response_contracts():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 226

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 227

`Verify that AI requests and responses serialize cleanly with strict JSON compliance.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 228

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 229

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 230

`set_llm_provider(MockLLMProvider())`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 231

`(blank)`

Blank line used to separate nearby statements.
### Line 232

`# 1. Ask endpoint`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 233

`ask_req = {`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 234

`"question": "What is superposition?",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 235

`"concept_id": "quantum.superposition",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 236

`"learner_context": {"concept_mastery": {"quantum.superposition": 0.8}},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 237

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 238

`ask_res = client.post("/api/ai/ask", json=ask_req)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 239

`assert ask_res.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 240

`data = ask_res.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 241

`assert "answer" in data`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 242

`assert isinstance(data["answer"], str)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 243

`assert json.dumps(data)  # Valid JSON`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 244

`(blank)`

Blank line used to separate nearby statements.
### Line 245

`# 2. Explain experiment endpoint`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 246

`exp_req = {`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 247

`"learner_response": "10",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 248

`"verified_result": {"algorithm": "grover", "target_state": "10"},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 249

`"evidence": {"concept_id": "grover.search_problem", "is_correct": True},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 250

`"adaptive_decision": {"action": "advance", "target": "act_grover_iteration_reasoning"},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 251

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 252

`exp_res = client.post("/api/ai/explain_experiment", json=exp_req)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 253

`assert exp_res.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 254

`exp_data = exp_res.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 255

`assert "explanation" in exp_data`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 256

`assert json.dumps(exp_data)  # Valid JSON`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 257

`(blank)`

Blank line used to separate nearby statements.
### Line 258

`reset_dependencies()`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 259

`(blank)`

Blank line used to separate nearby statements.
### Line 261

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 262

`# GENERAL M5 GROUNDED GUIDANCE REGRESSION SUITE (TESTS A - G & CONSTRAINTS)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 263

`# ===========================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 264

`(blank)`

Blank line used to separate nearby statements.
### Line 265

`def test_a_conceptual_response_grounding_no_execution_fabrication():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 266

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 267

`Requirement A: conceptual_response attempt produces a grounded Concept Explanation`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 268

`and strictly omits quantum execution claims, fake Dirac kets (|B⟩), fake outcomes (|N/A⟩),`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 269

`and 1024-shot counts.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 270

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 271

`provider = MockLLMProvider()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 272

`evidence = {`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 273

`"evidence_id": "ev_diag_born_01",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 274

`"evidence_type": "conceptual_response",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 275

`"evidence_source": "learner",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 276

`"concept_id": "quantum.measurement",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 277

`"activity_id": "act_measurement_prob_diagnostic",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 278

`"learner_response": "B",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 279

`"is_correct": True,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 280

`"evaluation_details": {"selected_option": "B", "expected_option": "B", "match": True},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 281

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 282

`adaptive_decision = {`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 283

`"decision_id": "dec_meas_adv_01",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 284

`"action": "advance",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 285

`"target": "act_grover_2q_predict",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 286

`"reason": "Demonstrated understanding of measurement probabilities.",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 287

`"concept_id": "quantum.measurement",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 288

`"trigger": "correct_prediction_advancement",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 289

`"evidence_sufficiency": "sufficient_for_observation",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 290

`"supporting_evidence_ids": ["ev_diag_born_01"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 291

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 292

`(blank)`

Blank line used to separate nearby statements.
### Line 293

`explanation = explain_experiment(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 294

`learner_response="B",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 295

`verified_result=None,  # NO quantum execution`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 296

`evidence=evidence,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 297

`adaptive_decision=adaptive_decision,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 298

`provider=provider,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 299

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 300

`(blank)`

Blank line used to separate nearby statements.
### Line 301

`# 1. Heading and structure are evidence-appropriate`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 302

`assert "### Concept Explanation" in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 303

`assert "### Quantum Execution Analysis" not in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 304

`(blank)`

Blank line used to separate nearby statements.
### Line 305

`# 2. No fabricated Dirac kets for MCQ option letters`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 306

`assert "|B⟩" not in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 307

`assert "|B\\rangle" not in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 308

`assert "Option **B**" in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 309

`(blank)`

Blank line used to separate nearby statements.
### Line 310

`# 3. No fabricated N/A states or shot counts`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 311

`assert "|N/A⟩" not in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 312

`assert "|N/A\\rangle" not in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 313

`assert "Theoretical target is" not in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 314

`assert "1024 shots" not in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 315

`(blank)`

Blank line used to separate nearby statements.
### Line 316

`# 4. Correct conceptual explanation for Born's rule`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 317

`assert "Born's rule" in explanation or "Born" in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 318

`assert "$P(x) = |\\alpha_x|^2$" in explanation or "P(x)" in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 319

`assert "advance" in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 320

`assert "ev_diag_born_01" in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 321

`(blank)`

Blank line used to separate nearby statements.
### Line 323

`def test_b_quantum_execution_grounding_preserves_verified_facts():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 324

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 325

`Requirement B: quantum_prediction attempt with real execution data produces`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 326

`Quantum Execution Analysis and compares prediction vs empirical outcome accurately.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 327

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 328

`provider = MockLLMProvider()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 329

`evidence = {`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 330

`"evidence_id": "ev_grover_exec_01",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 331

`"evidence_type": "quantum_prediction",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 332

`"evidence_source": "learner_and_quantum_execution",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 333

`"concept_id": "grover.search_problem",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 334

`"activity_id": "act_grover_2q_predict",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 335

`"learner_response": "01",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 336

`"is_correct": False,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 337

`"evaluation_details": {"predicted_state": "01", "most_likely_state": "10", "match": False},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 338

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 339

`verified_result = {`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 340

`"algorithm": "grover",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 341

`"target_state": "10",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 342

`"most_likely_state": "10",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 343

`"target_probability": 0.9375,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 344

`"counts": {"00": 10, "01": 15, "10": 950, "11": 25},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 345

`"shots": 1024,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 346

`"circuit": {"num_qubits": 2, "depth": 8},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 347

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 348

`adaptive_decision = {`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 349

`"decision_id": "dec_grover_gather_01",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 350

`"action": "gather_evidence",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 351

`"target": "act_grover_2q_predict",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 352

`"reason": "Single prediction mismatch.",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 353

`"concept_id": "grover.search_problem",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 354

`"trigger": "single_prediction_mismatch",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 355

`"evidence_sufficiency": "insufficient",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 356

`"supporting_evidence_ids": ["ev_grover_exec_01"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 357

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 358

`(blank)`

Blank line used to separate nearby statements.
### Line 359

`explanation = explain_experiment(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 360

`learner_response="01",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 361

`verified_result=verified_result,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 362

`evidence=evidence,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 363

`adaptive_decision=adaptive_decision,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 364

`provider=provider,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 365

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 366

`(blank)`

Blank line used to separate nearby statements.
### Line 367

`# 1. Execution analysis is present`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 368

`assert "### Quantum Execution Analysis" in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 369

`assert "$|01\\rangle$" in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 370

`assert "$|10\\rangle$" in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 371

`assert "Theoretical target is $|10\\rangle$" in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 372

`(blank)`

Blank line used to separate nearby statements.
### Line 373

`# 2. Physical mechanism is explained`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 374

`assert "phase oracle" in explanation.lower() or "oracle" in explanation.lower()`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 375

`assert "diffusion operator" in explanation.lower() or "diffusion" in explanation.lower()`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 376

`(blank)`

Blank line used to separate nearby statements.
### Line 377

`# 3. Adaptive decision is preserved`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 378

`assert "gather_evidence" in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 379

`assert "single_prediction_mismatch" in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 380

`(blank)`

Blank line used to separate nearby statements.
### Line 382

`def test_c_adaptive_decision_grounding_references_supplied_facts():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 383

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 384

`Requirement C: M5 explanation references M2 decision facts (sufficiency, trigger,`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 385

`hypothesis, target) without manufacturing fake quantum execution results.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 386

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 387

`provider = MockLLMProvider()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 388

`evidence = {`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 389

`"evidence_id": "ev_superposition_01",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 390

`"evidence_type": "conceptual_response",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 391

`"concept_id": "quantum.superposition",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 392

`"activity_id": "act_superposition_remediation",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 393

`"learner_response": "B",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 394

`"is_correct": True,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 395

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 396

`adaptive_decision = {`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 397

`"decision_id": "dec_remed_adv_01",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 398

`"action": "advance",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 399

`"target": "act_measurement_prob_diagnostic",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 400

`"reason": "Successfully reinforced equal superposition prerequisite.",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 401

`"concept_id": "quantum.superposition",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 402

`"trigger": "post_intervention_recovery",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 403

`"evidence_sufficiency": "sufficient_for_improvement_observation",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 404

`"supporting_evidence_ids": ["ev_superposition_01"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 405

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 406

`(blank)`

Blank line used to separate nearby statements.
### Line 407

`explanation = explain_experiment(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 408

`learner_response="B",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 409

`verified_result=None,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 410

`evidence=evidence,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 411

`adaptive_decision=adaptive_decision,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 412

`provider=provider,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 413

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 414

`(blank)`

Blank line used to separate nearby statements.
### Line 415

`# References supplied adaptive facts`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 416

`assert "advance" in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 417

`assert "Successfully reinforced equal superposition prerequisite" in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 418

`assert "post_intervention_recovery" in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 419

`assert "sufficient_for_improvement_observation" in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 420

`assert "ev_superposition_01" in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 421

`assert "Quantum Execution Analysis" not in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 422

`(blank)`

Blank line used to separate nearby statements.
### Line 424

`def test_c2_adaptive_decision_qa_inquiry_explains_decision_specifically():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 425

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 426

`Requirement C2: Standalone QA inquiry about next activity recommendation`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 427

`explains supplied action, target, reason, trigger, sufficiency, hypothesis, and evidence IDs.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 428

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 429

`provider = MockLLMProvider()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 430

`learner_context = {`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 431

`"recommendation": {`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 432

`"action": "targeted_remediation",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 433

`"target": "act_measurement_prob_diagnostic",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 434

`"reason": "Repeated prediction errors indicate prerequisite bottleneck in measurement.",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 435

`"trigger": "repeated_prediction_error",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 436

`"evidence_sufficiency": "sufficient_for_targeted_inference",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 437

`"supporting_evidence_ids": ["ev_01", "ev_02"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 438

`},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 439

`"gap_inferences": {`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 440

`"grover.search_problem": {`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 441

`"hypothesis": "possible_grover_search_problem_difficulty",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 442

`"status": "remediation_needed",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 443

`"trend": "persistent_difficulty",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 444

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 445

`},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 446

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 447

`(blank)`

Blank line used to separate nearby statements.
### Line 448

`ans = ask_question(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 449

`question="Why was this next activity selected for remediation?",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 450

`learner_context=learner_context,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 451

`provider=provider,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 452

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 453

`(blank)`

Blank line used to separate nearby statements.
### Line 454

`assert "### Adaptive Decision Explanation" in ans`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 455

`assert "targeted_remediation" in ans`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 456

`assert "act_measurement_prob_diagnostic" in ans`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 457

`assert "Repeated prediction errors indicate prerequisite bottleneck in measurement" in ans`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 458

`assert "repeated_prediction_error" in ans`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 459

`assert "sufficient_for_targeted_inference" in ans`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 460

`assert "possible_grover_search_problem_difficulty" in ans`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 461

`assert '["ev_01", "ev_02"]' in ans`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 462

`assert "Quantum Execution Analysis" not in ans`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 463

`assert "Selected Option" not in ans`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 464

`(blank)`

Blank line used to separate nearby statements.
### Line 466

`def test_d_missing_execution_fields_omitted_not_rendered_as_fake_observed_values():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 467

`(blank)`

Blank line used to separate nearby statements.
### Line 468

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 469

`Requirement D: When verified_result has missing fields (e.g. target_state omitted),`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 470

`the explanation omits that claim rather than rendering '|N/A>' or fake values.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 471

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 472

`provider = MockLLMProvider()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 473

`evidence = {`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 474

`"evidence_id": "ev_partial_01",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 475

`"evidence_type": "quantum_prediction",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 476

`"concept_id": "grover.search_problem",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 477

`"learner_response": "10",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 478

`"is_correct": True,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 479

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 480

`# verified_result without target_state and without shots`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 481

`verified_result = {`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 482

`"algorithm": "grover",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 483

`"most_likely_state": "10",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 484

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 485

`adaptive_decision = {`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 486

`"action": "advance",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 487

`"reason": "Correct prediction.",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 488

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 489

`(blank)`

Blank line used to separate nearby statements.
### Line 490

`explanation = explain_experiment(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 491

`learner_response="10",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 492

`verified_result=verified_result,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 493

`evidence=evidence,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 494

`adaptive_decision=adaptive_decision,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 495

`provider=provider,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 496

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 497

`(blank)`

Blank line used to separate nearby statements.
### Line 498

`assert "Quantum Execution Analysis" in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 499

`assert "$|10\\rangle$" in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 500

`assert "|N/A⟩" not in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 501

`assert "|N/A\\rangle" not in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 502

`assert "Theoretical target is |N/A⟩" not in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 503

`assert "N/A shots" not in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 504

`(blank)`

Blank line used to separate nearby statements.
### Line 506

`def test_e_compound_question_prediction_execution_requires_actual_evidence():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 507

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 508

`Requirement E: 'Why did my Grover prediction differ from the verified result?'`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 509

`produces honest notice when NO execution evidence is in context, and produces`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 510

`prediction/result explanation when execution evidence IS present.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 511

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 512

`provider = MockLLMProvider()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 513

`(blank)`

Blank line used to separate nearby statements.
### Line 514

`# Case 1: No execution context provided in prompt`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 515

`ans_no_evidence = ask_question(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 516

`question="Why did my Grover prediction differ from the verified result?",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 517

`learner_context=None,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 518

`provider=provider,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 519

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 520

`assert "The available evidence does not include a quantum execution result, so there is no measurement outcome to compare here." in ans_no_evidence`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 521

`assert "Your prediction was" not in ans_no_evidence`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 522

`(blank)`

Blank line used to separate nearby statements.
### Line 523

`# Case 2: Execution context IS provided in learner_context`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 524

`ans_with_evidence = ask_question(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 525

`question="Why did my Grover prediction differ from the verified result?",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 526

`learner_context={"most_likely_state": "10", "counts": {"00": 10, "10": 950}},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 527

`provider=provider,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 528

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 529

`assert "Prediction vs Quantum Execution" in ans_with_evidence`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 530

`assert "The available evidence does not include a quantum execution result" not in ans_with_evidence`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 531

`(blank)`

Blank line used to separate nearby statements.
### Line 533

`def test_f_generic_concept_question_no_learner_execution_claims():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 534

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 535

`Requirement F: 'What is Grover's algorithm?' produces conceptual explanation`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 536

`without fabricating learner-specific execution claims.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 537

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 538

`provider = MockLLMProvider()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 539

`ans = ask_question("What is Grover's algorithm?", provider=provider)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 540

`(blank)`

Blank line used to separate nearby statements.
### Line 541

`assert "Grover's Algorithm Overview" in ans`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 542

`assert "Your prediction was" not in ans`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 543

`assert "empirical 1024-shot" not in ans`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 544

`assert "$" in ans`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 545

`(blank)`

Blank line used to separate nearby statements.
### Line 547

`def test_g_unknown_question_honest_fallback():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 548

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 549

`Requirement G: Out-of-scope question returns honest guidance fallback.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 550

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 551

`provider = MockLLMProvider()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 552

`ans = ask_question("How do I bake sourdough bread with olive oil?", provider=provider)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 553

`(blank)`

Blank line used to separate nearby statements.
### Line 554

`assert "Q-BIT AI Guidance" in ans`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 555

`assert "I can explain what a qubit is, quantum superposition, measurement probability" in ans`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 556

`(blank)`

Blank line used to separate nearby statements.
### Line 558

`def test_constraint15_conceptual_response_with_grover_curriculum_does_not_produce_execution_analysis():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 559

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 560

`Constraint 15: An activity with conceptual_response on a Grover topic (e.g. over-rotation)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 561

`with Grover curriculum context MUST NOT produce a Quantum Execution Analysis.`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 562

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 563

`provider = MockLLMProvider()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 564

`evidence = {`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 565

`"evidence_id": "ev_grover_iter_01",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 566

`"evidence_type": "conceptual_response",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 567

`"concept_id": "grover.amplitude_amplification",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 568

`"activity_id": "act_grover_iteration_reasoning",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 569

`"learner_response": "B",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 570

`"is_correct": True,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 571

`"evaluation_details": {"selected_option": "B", "expected_option": "B", "match": True},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 572

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 573

`adaptive_decision = {`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 574

`"decision_id": "dec_grover_iter_01",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 575

`"action": "advance",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 576

`"reason": "Demonstrated mastery of Grover iteration oscillation.",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 577

`"concept_id": "grover.amplitude_amplification",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 578

`"trigger": "consecutive_mastery_success",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 579

`"evidence_sufficiency": "sufficient_for_mastery",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 580

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 581

`(blank)`

Blank line used to separate nearby statements.
### Line 582

`explanation = explain_experiment(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 583

`learner_response="B",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 584

`verified_result=None,  # Conceptual interaction, no simulation run`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 585

`evidence=evidence,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 586

`adaptive_decision=adaptive_decision,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 587

`provider=provider,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 588

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 589

`(blank)`

Blank line used to separate nearby statements.
### Line 590

`assert "### Concept Explanation" in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 591

`assert "### Quantum Execution Analysis" not in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 592

`assert "1024 shots" not in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 593

`assert "Theoretical target is" not in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 594

`assert "|B⟩" not in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 595

`assert "|B\\rangle" not in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 596

`assert "oscillatory" in explanation.lower() or "rotation" in explanation.lower() or "over-rotation" in explanation.lower()`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 597

`(blank)`

Blank line used to separate nearby statements.
### Line 599

`def test_constraint16_quantum_execution_with_prediction_produces_execution_analysis():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 600

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 601

`Constraint 16: An activity with quantum_prediction and verified simulation`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 602

`DOES produce the Quantum Execution Analysis.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 603

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 604

`provider = MockLLMProvider()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 605

`evidence = {`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 606

`"evidence_id": "ev_grover_pred_success",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 607

`"evidence_type": "quantum_prediction",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 608

`"concept_id": "grover.search_problem",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 609

`"activity_id": "act_grover_2q_predict",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 610

`"learner_response": "10",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 611

`"is_correct": True,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 612

`"evaluation_details": {"predicted_state": "10", "most_likely_state": "10", "match": True},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 613

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 614

`verified_result = {`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 615

`"algorithm": "grover",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 616

`"target_state": "10",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 617

`"most_likely_state": "10",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 618

`"target_probability": 0.938,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 619

`"shots": 1024,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 620

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 621

`adaptive_decision = {`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 622

`"action": "advance",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 623

`"target": "act_grover_iteration_reasoning",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 624

`"reason": "Correct prediction demonstrating search problem understanding.",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 625

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 626

`(blank)`

Blank line used to separate nearby statements.
### Line 627

`explanation = explain_experiment(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 628

`learner_response="10",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 629

`verified_result=verified_result,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 630

`evidence=evidence,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 631

`adaptive_decision=adaptive_decision,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 632

`provider=provider,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 633

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 634

`(blank)`

Blank line used to separate nearby statements.
### Line 635

`assert "### Quantum Execution Analysis" in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 636

`assert "Your prediction of state $|10\\rangle$ correctly matched the empirical simulation outcome $|10\\rangle$" in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 637

`assert "Theoretical target is $|10\\rangle$" in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.

## Nearby Files

[tests/ai/__init__.py](__init__.py.md), [tests/ai/test_providers.py](test_providers.py.md), [tests/ai/test_retrieval.py](test_retrieval.py.md), [tests/ai/test_service.py](test_service.py.md)
