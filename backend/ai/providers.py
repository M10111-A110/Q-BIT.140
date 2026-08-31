from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Any, Optional


class LLMProvider(ABC):
    """Abstract interface for LLM completion providers."""

    @abstractmethod
    def generate(self, messages: list[dict[str, str]], model: Optional[str] = None) -> str:
        """Generate an AI completion string given a list of chat messages."""
        pass


class MockLLMProvider(LLMProvider):
    """
    Deterministic, offline LLM provider for automated testing and standalone execution.
    Inspects message content to generate structured, curriculum-grounded KaTeX markdown
    without requiring external network calls or API keys.
    """

    def generate(self, messages: list[dict[str, str]], model: Optional[str] = None) -> str:
        user_msg = next((m["content"] for m in messages if m.get("role") == "user"), "")

        # 1. Experiment Explanation Handling
        if "VERIFIED EXPERIMENT EVIDENCE" in user_msg or "VERIFIED SIMULATION RESULT" in user_msg:
            return self._generate_experiment_explanation(user_msg)

        # 2. General Concept Q&A Handling
        return self._generate_qa_explanation(user_msg)

    def _generate_experiment_explanation(self, user_msg: str) -> str:
        return (
            "### Quantum Execution Analysis\n\n"
            "- **Observation**: The verified Qiskit simulation executed Grover's Algorithm.\n"
            "- **Mechanism**: The phase oracle flipped the sign of the marked target state ($O|w\\rangle = -|w\\rangle$), "
            "and the diffusion operator ($D = 2|s\\rangle\\langle s| - I$) performed inversion-about-the-mean, "
            "amplifying the target state's measurement amplitude.\n"
            "- **Measurement Probability**: In a quantum circuit, measurement probabilities follow Born's rule: "
            "$P(x) = |\\alpha_x|^2$. Finite-shot sampling produces empirical counts approximating this distribution.\n\n"
            "### Adaptive Learning Path\n\n"
            "The adaptive learner model (M2) evaluated the accumulated evidence and determined the next recommended activity. "
            "Follow the recommended activity to reinforce foundational prerequisites before moving to advanced multi-qubit search."
        )

    def _generate_qa_explanation(self, user_msg: str) -> str:
        lower = user_msg.lower()
        if "grover" in lower or "algorithm" in lower:
            return (
                "### Grover's Algorithm Overview\n\n"
                "Grover's algorithm searches an unstructured database of $N = 2^n$ items in $\\mathcal{O}(\\sqrt{N})$ oracle queries.\n\n"
                "**Core Steps**:\n"
                "1. Initialize qubits in equal superposition: $|s\\rangle = H^{\\otimes n}|0\\rangle^{\\otimes n} = \\frac{1}{\\sqrt{N}}\\sum_{x=0}^{N-1}|x\\rangle$.\n"
                "2. Apply Phase Oracle: $O|x\\rangle = (-1)^{f(x)}|x\\rangle$.\n"
                "3. Apply Diffusion Operator: $D = 2|s\\rangle\\langle s| - I$.\n"
                "4. Measure the computational basis state after $\\approx \\frac{\\pi}{4}\\sqrt{N}$ iterations."
            )
        elif "superposition" in lower or "qubit" in lower:
            return (
                "### Quantum Superposition\n\n"
                "A qubit can exist in a superposition state $|\\psi\\rangle = \\alpha|0\\rangle + \\beta|1\\rangle$, "
                "where $\\alpha, \\beta \\in \\mathbb{C}$ and $|\\alpha|^2 + |\\beta|^2 = 1$.\n\n"
                "Applying a Hadamard gate $H$ to $|0\\rangle$ yields:\n"
                "$$H|0\\rangle = \\frac{|0\\rangle + |1\\rangle}{\\sqrt{2}}$$\n"
                "This produces equal measurement probabilities of $50\\%$ ($P(0) = P(1) = 0.5$)."
            )
        elif "measurement" in lower or "probability" in lower:
            return (
                "### Quantum Measurement & Probability\n\n"
                "In quantum mechanics, measurement collapses the wavefunction according to the state's complex amplitudes. "
                "For a state $|\\psi\\rangle = \\sum_x \\alpha_x |x\\rangle$, the probability of observing outcome $x$ is given by Born's rule: "
                "$$P(x) = |\\alpha_x|^2$$\n"
                "Counts from a finite number of shots approximate this underlying probability distribution."
            )

        return (
            "### Q-BIT AI Guidance\n\n"
            "Grounded explanation based on curriculum knowledge:\n"
            "Quantum algorithms utilize superposition, unitary phase operations, and constructive interference to amplify target solution amplitudes prior to measurement."
        )


class GroqLLMProvider(LLMProvider):
    """Production provider using Groq API completions."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY must be set in environment or passed to GroqLLMProvider.")
        try:
            from groq import Groq
            self.client = Groq(api_key=self.api_key)
        except ImportError:
            raise ImportError("The 'groq' Python package is required to use GroqLLMProvider. Install with 'pip install groq'.")

    def generate(self, messages: list[dict[str, str]], model: Optional[str] = None) -> str:
        chosen_model = model or os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
        response = self.client.chat.completions.create(
            model=chosen_model,
            messages=messages,  # type: ignore
        )
        return response.choices[0].message.content or ""


def get_default_provider() -> LLMProvider:
    """Factory returning GroqLLMProvider if GROQ_API_KEY is present, else MockLLMProvider."""
    if os.getenv("GROQ_API_KEY"):
        try:
            return GroqLLMProvider()
        except Exception:
            return MockLLMProvider()
    return MockLLMProvider()
