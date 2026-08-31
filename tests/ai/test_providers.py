import pytest
from backend.ai.providers import MockLLMProvider, get_default_provider


def test_mock_provider_generates_grounded_qa_response():
    provider = MockLLMProvider()
    messages = [
        {"role": "system", "content": "You are Q-BIT AI."},
        {"role": "user", "content": "Explain Grover's algorithm and the oracle."},
    ]
    response = provider.generate(messages)
    assert "Grover's Algorithm" in response
    assert "Oracle" in response or "diffusion" in response.lower()
    assert "$" in response  # Contains KaTeX math formatting


def test_mock_provider_generates_experiment_explanation():
    provider = MockLLMProvider()
    messages = [
        {"role": "system", "content": "You are Q-BIT AI."},
        {
            "role": "user",
            "content": "VERIFIED EXPERIMENT EVIDENCE: Target state |10>, prediction was 01.",
        },
    ]
    response = provider.generate(messages)
    assert "Quantum Execution Analysis" in response
    assert "Adaptive Learning Path" in response
    assert "$" in response


def test_get_default_provider_returns_mock_when_no_api_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    provider = get_default_provider()
    assert isinstance(provider, MockLLMProvider)
