from __future__ import annotations

import logging
import os
import re
from abc import ABC, abstractmethod
from typing import Any, Optional

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract interface for LLM completion providers."""

    @abstractmethod
    def generate(self, messages: list[dict[str, str]], model: Optional[str] = None) -> str:
        """Generate an AI completion string given a list of chat messages."""
        pass


class MockLLMProvider(LLMProvider):
    """
    Deterministic, offline mock provider for automated testing and standalone execution.
    Inspects structured message content to generate curriculum-grounded KaTeX markdown
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
        # Extract structured evidence items from prompt if available
        pred_match = re.search(r"Learner Predicted State / Response:\s*([^\n]+)", user_msg)
        target_match = re.search(r"Theoretical Target State:\s*([^\n]+)", user_msg)
        most_likely_match = re.search(r"Empirical Most-Likely Measured State:\s*([^\n]+)", user_msg)
        action_match = re.search(r"\* Action:\s*([^\n]+)", user_msg)
        reason_match = re.search(r"\* Rationale:\s*([^\n]+)", user_msg)
        ev_id_match = re.search(r"- Evidence ID:\s*([^\n]+)", user_msg)
        suff_match = re.search(r"- Evidence Sufficiency:\s*([^\n]+)", user_msg)
        trigger_match = re.search(r"\* Trigger:\s*([^\n]+)", user_msg)
        supp_match = re.search(r"\* Supporting Evidence IDs:\s*([^\n]+)", user_msg)

        pred_state = pred_match.group(1).strip() if pred_match else "N/A"
        target_state = target_match.group(1).strip() if target_match else "N/A"
        most_likely = most_likely_match.group(1).strip() if most_likely_match else "N/A"
        action = action_match.group(1).strip() if action_match else "advance"
        reason = reason_match.group(1).strip() if reason_match else "Continuing learning sequence."
        evidence_id = ev_id_match.group(1).strip() if ev_id_match else "N/A"
        sufficiency = suff_match.group(1).strip() if suff_match else "insufficient"
        trigger = trigger_match.group(1).strip() if trigger_match else "default_routing"
        supporting_ids = supp_match.group(1).strip() if supp_match else "[]"

        is_match = (pred_state == most_likely) and (most_likely != "N/A")

        outcome_analysis = (
            f"Your prediction of state $|{pred_state}\\rangle$ correctly matched the empirical simulation outcome $|{most_likely}\\rangle$."
            if is_match else
            f"Your prediction was $|{pred_state}\\rangle$, while the empirical simulation resulted in target state $|{most_likely}\\rangle$."
        )

        trace_section = (
            f"\n\n### Evidence & Decision Trace\n\n"
            f"- **Evidence Record**: `{evidence_id}`\n"
            f"- **Evidence Sufficiency**: `{sufficiency}`\n"
            f"- **Decision Trigger**: `{trigger}`\n"
            f"- **Supporting Evidence IDs**: `{supporting_ids}`"
        ) if evidence_id != "N/A" else ""

        return (
            f"### Quantum Execution Analysis\n\n"
            f"- **Prediction vs Outcome**: {outcome_analysis}\n"
            f"- **Target State**: Theoretical target is $|{target_state}\\rangle$.\n"
            f"- **Mechanism**: The phase oracle flipped the sign of the marked target state ($O|w\\rangle = -|w\\rangle$), "
            f"and the diffusion operator ($D = 2|s\\rangle\\langle s| - I$) performed inversion-about-the-mean, "
            f"amplifying the target state amplitude.\n"
            f"- **Measurement Probability**: Measurement probabilities follow Born's rule: "
            f"$P(x) = |\\alpha_x|^2$. Finite-shot sampling produces counts reflecting this distribution.\n\n"
            f"### Adaptive Learning Path\n\n"
            f"- **Action**: `{action}`\n"
            f"- **Pedagogical Rationale**: {reason}"
            f"{trace_section}"
        )

    def _generate_qa_explanation(self, user_msg: str) -> str:
        # Extract the actual learner question from the prompt
        q_match = re.search(r"LEARNER QUESTION:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\nPlease answer|\Z)", user_msg, re.IGNORECASE)
        question_text = q_match.group(1).strip() if q_match else user_msg.strip()
        lower_q = question_text.lower()

        # Intent a: Superposition / Qubit
        if any(k in lower_q for k in ["superposition", "qubit", "hadamard", "basis state", "|+⟩", "|-⟩", "bloch"]):
            return (
                "### Quantum Superposition\n\n"
                "A qubit can exist in a superposition state $|\\psi\\rangle = \\alpha|0\\rangle + \\beta|1\\rangle$, "
                "where $\\alpha, \\beta \\in \\mathbb{C}$ and $|\\alpha|^2 + |\\beta|^2 = 1$.\n\n"
                "Applying a Hadamard gate $H$ to $|0\\rangle$ yields:\n"
                "$$H|0\\rangle = \\frac{|0\\rangle + |1\\rangle}{\\sqrt{2}}$$\n"
                "This produces equal measurement probabilities of $50\\%$ ($P(0) = P(1) = 0.5$)."
            )

        # Intent b: Measurement / Probability / Born Rule
        elif any(k in lower_q for k in ["measurement", "probability", "born", "collapse", "shots", "distribution"]):
            return (
                "### Quantum Measurement & Probability\n\n"
                "In quantum mechanics, measurement collapses the wavefunction according to the state's complex amplitudes. "
                "For a state $|\\psi\\rangle = \\sum_x \\alpha_x |x\\rangle$, the probability of observing outcome $x$ is given by Born's rule: "
                "$$P(x) = |\\alpha_x|^2$$\n"
                "Counts from a finite number of shots approximate this underlying probability distribution."
            )

        # Intent c: Grover / Oracle / Diffusion
        elif any(k in lower_q for k in ["grover", "oracle", "diffusion", "amplification", "inversion"]):
            return (
                "### Grover's Algorithm Overview\n\n"
                "Grover's algorithm searches an unstructured database of $N = 2^n$ items in $\\mathcal{O}(\\sqrt{N})$ oracle queries.\n\n"
                "**Core Steps**:\n"
                "1. Initialize qubits in equal superposition: $|s\\rangle = H^{\\otimes n}|0\\rangle^{\\otimes n} = \\frac{1}{\\sqrt{N}}\\sum_{x=0}^{N-1}|x\\rangle$.\n"
                "2. Apply Phase Oracle: $O|x\\rangle = (-1)^{f(x)}|x\\rangle$.\n"
                "3. Apply Diffusion Operator: $D = 2|s\\rangle\\langle s| - I$.\n"
                "4. Measure the computational basis state after $\\approx \\frac{\\pi}{4}\\sqrt{N}$ iterations."
            )

        # Intent d: Prediction Mismatch / Verified Outcome
        elif any(k in lower_q for k in ["prediction", "differ", "mismatch", "incorrect", "wrong", "verified result", "actual result", "outcome"]):
            return (
                "### Prediction vs Quantum Execution\n\n"
                "A prediction mismatch occurs when the learner's hypothesized basis state does not match "
                "the high-probability state produced by the physical quantum circuit.\n\n"
                "In Grover's search, the phase oracle flips the amplitude sign of the target state ($O|w\\rangle = -|w\\rangle$), "
                "and the diffusion operator inverts amplitudes about the mean ($D = 2|s\\rangle\\langle s| - I$). "
                "If an incorrect state was predicted, the empirical 1024-shot simulation reflects the actual amplified target state rather than the guess."
            )

        # Intent e: Adaptive Recommendation / "Why This Next?"
        elif any(k in lower_q for k in ["next", "recommend", "why this", "selected", "activity", "remediation", "advance", "routing"]):
            return (
                "### Adaptive Learning Path (\"Why This Next?\")\n\n"
                "Q-BIT's M2 Cognitive Engine determines the next pedagogical activity deterministically based on accumulated empirical evidence:\n\n"
                "- **Single Error**: Triggers `gather_evidence` to confirm whether a difficulty is persistent before intervening.\n"
                "- **Repeated Errors**: Triggers `targeted_remediation` by citing historical attempt records and routing to prerequisite concept diagnostics.\n"
                "- **Mastery / Recovery**: Triggers `advance` to progress along the curriculum DAG once understanding is demonstrated."
            )

        # Intent f: Learner State / Progress
        elif any(k in lower_q for k in ["learner state", "progress", "mastery", "score", "trajectory", "gap", "inference"]):
            return (
                "### Learner State & Cognitive Tracking\n\n"
                "Q-BIT tracks your conceptual understanding across a 4-tier cognitive architecture:\n\n"
                "- **Tier 1 (Evidence)**: Empirical attempt records pairing your responses with Qiskit Aer simulation counts.\n"
                "- **Tier 2 (Accumulated State)**: Chronological attempt counts, error sequences, and score trajectories.\n"
                "- **Tier 3 (Cognitive Gaps)**: Calibrated Bayesian mastery probabilities and gap hypotheses (e.g. `observing`, `remediation_needed`, `improving`, `mastered`).\n"
                "- **Tier 4 (Pedagogical Action)**: Deterministic routing decisions grounded in evidence sufficiency."
            )

        # Intent g: Honest fallback for unknown questions
        return (
            "### Q-BIT AI Guidance\n\n"
            "I can explain quantum superposition, measurement probability, Grover's algorithm, experiment predictions, "
            "adaptive recommendations, and your cognitive learner state. Please ask a question related to these topics."
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
        except Exception as exc:
            logger.warning("Failed to initialize GroqLLMProvider; falling back to MockLLMProvider: %s", exc)
            return MockLLMProvider()
    return MockLLMProvider()
