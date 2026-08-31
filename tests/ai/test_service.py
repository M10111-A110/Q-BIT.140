from backend.ai.providers import MockLLMProvider
from backend.ai.service import ask_question, explain_experiment


def test_ask_question_service_with_mock_provider():
    provider = MockLLMProvider()
    ans = ask_question(
        question="How does superposition work with qubits?",
        concept_id="quantum.superposition",
        provider=provider,
    )
    assert "Superposition" in ans or "qubit" in ans.lower()
    assert "$" in ans


def test_explain_experiment_service_with_mock_provider():
    provider = MockLLMProvider()
    explanation = explain_experiment(
        learner_response="01",
        verified_result={
            "algorithm": "grover",
            "target_state": "10",
            "most_likely_state": "10",
            "target_probability": 0.934,
        },
        evidence={
            "concept_id": "grover.search_problem",
            "is_correct": False,
            "evaluation_details": {"match": False},
        },
        adaptive_decision={
            "action": "gather_evidence",
            "target": "act_grover_2q_predict",
            "reason": "Initial mismatch.",
        },
        provider=provider,
    )
    assert "Quantum Execution Analysis" in explanation
    assert "Adaptive Learning Path" in explanation
