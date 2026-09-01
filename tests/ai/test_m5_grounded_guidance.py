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
