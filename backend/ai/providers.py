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
            f"- **Amplitude vs Probability**: Measurement probabilities follow Born's rule: "
            f"$P(x) = |\\alpha_x|^2$. In this MVP's specific 2-qubit diagnostic scenario, a target state amplitude of $\\alpha \\approx 0.968$ yields a theoretical measurement probability of $|0.968|^2 \\approx 0.937$ ($93.7\\%$). Finite-shot sampling ($1024$ shots on Qiskit Aer) produces empirical counts reflecting this distribution.\n\n"
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

        # Intent 1: Prediction Mismatch / Verified Outcome
        if any(k in lower_q for k in ["prediction", "differ", "mismatch", "incorrect", "wrong", "verified result", "actual result", "outcome"]):
            return (
                "### Prediction vs Quantum Execution\n\n"
                "A prediction mismatch occurs when the learner's hypothesized basis state does not match "
                "the high-probability state produced by the physical quantum circuit.\n\n"
                "In Grover's search, the phase oracle flips the amplitude sign of the target state ($O|w\\rangle = -|w\\rangle$), "
                "and the diffusion operator inverts amplitudes about the mean ($D = 2|s\\rangle\\langle s| - I$). "
                "If an incorrect state was predicted, the empirical 1024-shot simulation reflects the actual amplified target state rather than the guess."
            )

        # Intent 2: Adaptive Recommendation / "Why This Next?"
        elif any(k in lower_q for k in ["next", "recommend", "why this", "selected", "activity", "remediation", "advance", "routing"]):
            return (
                "### Adaptive Learning Path (\"Why This Next?\")\n\n"
                "Q-BIT's M2 Cognitive Engine determines the next pedagogical activity deterministically based on accumulated empirical evidence:\n\n"
                "- **Single Error**: Triggers `gather_evidence` to confirm whether a difficulty is persistent before intervening.\n"
                "- **Repeated Errors**: Triggers `targeted_remediation` by citing historical attempt records and routing to prerequisite concept diagnostics.\n"
                "- **Mastery / Recovery**: Triggers `advance` to progress along the curriculum DAG once understanding is demonstrated."
            )

        # Intent 3: Learner State / Progress
        elif any(k in lower_q for k in ["learner state", "progress", "mastery", "score", "trajectory", "gap", "inference"]):
            return (
                "### Learner State & Cognitive Tracking\n\n"
                "Q-BIT tracks your conceptual understanding across a 4-tier cognitive architecture:\n\n"
                "- **Tier 1 (Evidence)**: Empirical attempt records pairing your responses with Qiskit Aer simulation counts.\n"
                "- **Tier 2 (Accumulated State)**: Chronological attempt counts, error sequences, and score trajectories.\n"
                "- **Tier 3 (Cognitive Gaps)**: Calibrated Bayesian mastery probabilities and gap hypotheses (e.g. `observing`, `remediation_needed`, `improving`, `mastered`).\n"
                "- **Tier 4 (Pedagogical Action)**: Deterministic routing decisions grounded in evidence sufficiency."
            )

        # Intent 4: Qubit Concept (explicitly distinct from Superposition)
        elif ("qubit" in lower_q or "quantum bit" in lower_q) and ("superposition" not in lower_q):
            return (
                "### Understanding the Qubit\n\n"
                "A **qubit** (quantum bit) is the fundamental unit of quantum information, analogous to a classical bit (0 or 1):\n\n"
                "- **State Representation**: A qubit state $|\\psi\\rangle$ is represented as a linear combination of orthonormal basis states:\n"
                "$$|\\psi\\rangle = \\alpha|0\\rangle + \\beta|1\\rangle$$\n"
                "- **Probability Amplitudes**: $\\alpha, \\beta \\in \\mathbb{C}$ are complex probability amplitudes normalized such that:\n"
                "$$|\\alpha|^2 + |\\beta|^2 = 1$$\n"
                "- **Measurement & Probabilities**: Measuring the qubit collapses the state, yielding outcome $0$ with probability $P(0) = |\\alpha|^2$ or outcome $1$ with probability $P(1) = |\\beta|^2$.\n"
                "- **Key Distinction**: While superposition allows simultaneous amplitude weights before observation, measurement always produces a single classical outcome. A qubit is not simply 'a bit that is both 0 and 1 at the same time'."
            )

        # Intent 5: Quantum Superposition
        elif any(k in lower_q for k in ["superposition", "hadamard", "basis state", "|+⟩", "|-⟩", "bloch"]):
            return (
                "### Quantum Superposition\n\n"
                "**Superposition** is the physical principle that allows a quantum state to exist as a linear combination of basis states simultaneously:\n\n"
                "$$|\\psi\\rangle = \\alpha|0\\rangle + \\beta|1\\rangle$$\n\n"
                "- **Equal Superposition via Hadamard Gate**: Applying an $H$ gate to basis state $|0\\rangle$ yields:\n"
                "$$H|0\\rangle = \\frac{|0\\rangle + |1\\rangle}{\\sqrt{2}}$$\n"
                "- **Probabilistic Symmetry**: Both basis states have equal amplitude $\\frac{1}{\\sqrt{2}}$, yielding equal measurement probabilities:\n"
                "$$P(0) = \\left|\\frac{1}{\\sqrt{2}}\\right|^2 = 0.5 \\quad (50\\%), \\quad P(1) = \\left|\\frac{1}{\\sqrt{2}}\\right|^2 = 0.5 \\quad (50\\%)$$\n"
                "- **Phase & Interference**: Unlike classical probabilities, amplitudes can have relative phases (e.g. negative signs) that enable constructive and destructive quantum interference."
            )

        # Intent 6: Measurement / Probability / Born Rule / Amplitude
        elif any(k in lower_q for k in ["measurement", "probability", "born", "collapse", "shots", "distribution", "amplitude"]):
            return (
                "### Quantum Measurement & Born's Rule\n\n"
                "In quantum mechanics, quantum state amplitudes $\\alpha_x$ are complex numbers, "
                "while measurement probabilities $P(x)$ represent physical observation frequencies:\n\n"
                "**Born's Rule**:\n"
                "$$P(x) = |\\alpha_x|^2$$\n\n"
                "- **Amplitude vs Probability**: In this MVP's specific 2-qubit diagnostic scenario, a target state amplitude of $\\alpha \\approx 0.968$ yields a theoretical measurement probability of:\n"
                "$$P(10) = |0.968|^2 \\approx 0.937 \\quad (93.7\\%)$$\n"
                "- **Wavefunction Collapse**: Measurement projects the continuous state vector into a single discrete computational basis state $|x\\rangle$.\n"
                "- **Finite-Shot Sampling**: Empirical finite-shot executions (e.g. 1024 shots) produce sampled frequency counts that approximate $N_{\\text{shots}} \\times P(x)$, with empirical results depending on the executed circuit and sampling."
            )

        # Intent 7: Grover / Oracle / Diffusion
        elif any(k in lower_q for k in ["grover", "oracle", "diffusion", "amplification", "inversion"]):
            return (
                "### Grover's Algorithm Overview\n\n"
                "Grover's algorithm searches an unstructured database of $N = 2^n$ items in $\\mathcal{O}(\\sqrt{N})$ oracle queries.\n\n"
                "**Core Steps**:\n"
                "1. **Superposition Initialization**: $|s\\rangle = H^{\\otimes n}|0\\rangle^{\\otimes n} = \\frac{1}{\\sqrt{N}}\\sum_{x=0}^{N-1}|x\\rangle$.\n"
                "2. **Phase Oracle**: Inverts the sign of the marked target state: $O|x\\rangle = (-1)^{f(x)}|x\\rangle$.\n"
                "3. **Diffusion Operator**: Inverts amplitudes about the mean: $D = 2|s\\rangle\\langle s| - I$, amplifying the marked state amplitude.\n"
                "4. **Measurement**: Collapses the quantum state according to Born's rule ($P(x) = |\\alpha_x|^2$). "
                "In this MVP's specific 2-qubit diagnostic scenario ($|10\\rangle$ target with $\\alpha \\approx 0.968$), the theoretical success probability is $P(|10\\rangle) = |0.968|^2 \\approx 93.7\\%$. "
                "Empirical outcomes from finite-shot execution (such as 1024 shots on Qiskit Aer) statistically sample this distribution and depend on the specific circuit executed rather than being universal across all Grover configurations."
            )

        # Intent 8: Honest fallback for unknown questions
        return (
            "### Q-BIT AI Guidance\n\n"
            "I can explain what a qubit is, quantum superposition, measurement probability (Born's rule), Grover's algorithm, "
            "experiment predictions, adaptive recommendations, and your cognitive learner state. Please ask a question related to these topics."
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
