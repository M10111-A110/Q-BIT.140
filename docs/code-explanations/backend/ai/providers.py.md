# Explanation: `backend/ai/providers.py`

## Purpose

This page explains the meaningful behavior in `backend/ai/providers.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
from __future__ import annotations

import json
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
    Inspects structured message content and evidence types to generate curriculum-grounded
    KaTeX markdown without requiring external network calls or API keys.
    """

    def generate(self, messages: list[dict[str, str]], model: Optional[str] = None) -> str:
        user_msg = next((m["content"] for m in messages if m.get("role") == "user"), "")

        # 1. Structured Evidence Attempt Explanation Handling
        if any(marker in user_msg for marker in [
            "LEARNER EVIDENCE:",
            "VERIFIED EXPERIMENT EVIDENCE:",
            "VERIFIED SIMULATION RESULT:",
            "QUANTUM EXECUTION EVIDENCE:",
            "EVIDENCE CONTEXT:",
        ]):
            return self._generate_evidence_grounded_explanation(user_msg)

        # 2. General Concept / Inquirer Q&A Handling
        return self._generate_qa_explanation(user_msg)

    def _generate_evidence_grounded_explanation(self, user_msg: str) -> str:
        # Extract evidence type and core metadata
        ev_type_match = re.search(r"Evidence Type:\s*([^\n\(\)]+)", user_msg)
        evidence_type = ev_type_match.group(1).strip() if ev_type_match else ""

        concept_match = re.search(r"- Concept ID:\s*([^\n]+)", user_msg) or re.search(r"\* Concept:\s*([^\n]+)", user_msg)
        concept_id = concept_match.group(1).strip() if concept_match else ""

        activity_match = re.search(r"- Activity ID:\s*([^\n]+)", user_msg)
        activity_id = activity_match.group(1).strip() if activity_match else ""

        ev_id_match = re.search(r"- Evidence ID:\s*([^\n\s]+)", user_msg)
        evidence_id = ev_id_match.group(1).strip() if ev_id_match else None
        if evidence_id == "N/A":
            evidence_id = None

        # Extract learner response
        learner_resp_match = (
            re.search(r"- Learner Response / Selection:\s*([^\n]+)", user_msg)
            or re.search(r"- Learner Predicted State / Response:\s*([^\n]+)", user_msg)
            or re.search(r"prediction was\s*([^\n,\.]+)", user_msg, re.IGNORECASE)
        )
        learner_response = learner_resp_match.group(1).strip() if learner_resp_match else ""

        # Extract correctness
        outcome_match = re.search(r"- Evaluation Outcome:\s*([^\n]+)", user_msg) or re.search(r"- Empirical Evaluation Outcome:\s*([^\n]+)", user_msg)
        outcome_str = outcome_match.group(1).strip() if outcome_match else ""
        is_correct = ("INCORRECT" not in outcome_str.upper()) and ("CORRECT" in outcome_str.upper() or "MATCH (Correct" in outcome_str)


        # Extract evaluation details
        eval_details = {}
        eval_details_match = re.search(r"- Evaluation Details:\s*([^\n]+)", user_msg)
        if eval_details_match:
            try:
                eval_details = json.loads(eval_details_match.group(1).strip())
            except Exception:
                pass

        # Extract quantum execution fields
        target_match = re.search(r"- Theoretical Target State:\s*([^\n]+)", user_msg) or re.search(r"Target state\s*\|?([0-9a-zA-Z]+)⟩?", user_msg, re.IGNORECASE)
        target_state = target_match.group(1).strip() if target_match else None
        if target_state == "N/A":
            target_state = None

        most_likely_match = re.search(r"- Empirical Most-Likely Measured State:\s*([^\n]+)", user_msg)
        most_likely = most_likely_match.group(1).strip() if most_likely_match else None
        if most_likely == "N/A":
            most_likely = None

        prob_match = re.search(r"- Target State Probability:\s*([^\n]+)", user_msg)
        target_prob = prob_match.group(1).strip() if prob_match else None
        if target_prob == "N/A":
            target_prob = None

        shots_match = re.search(r"- Total Shots Sampled:\s*([^\n]+)", user_msg)
        shots = shots_match.group(1).strip() if shots_match else None
        if shots == "N/A":
            shots = None

        # Extract adaptive decision fields
        action_match = re.search(r"- Action:\s*([^\n]+)", user_msg) or re.search(r"\* Action:\s*([^\n]+)", user_msg)
        action = action_match.group(1).strip() if action_match else "advance"

        target_act_match = re.search(r"- Target Activity:\s*([^\n]+)", user_msg) or re.search(r"\* Target:\s*([^\n]+)", user_msg)
        target_activity = target_act_match.group(1).strip() if target_act_match else None
        if target_activity == "N/A":
            target_activity = None

        reason_match = re.search(r"- Pedagogical Rationale:\s*([^\n]+)", user_msg) or re.search(r"\* Rationale:\s*([^\n]+)", user_msg)
        reason = reason_match.group(1).strip() if reason_match else "Continuing learning sequence."

        hyp_match = re.search(r"- Learner-State Hypothesis:\s*([^\n]+)", user_msg) or re.search(r"\* Hypothesis:\s*([^\n]+)", user_msg)
        hypothesis = hyp_match.group(1).strip() if hyp_match else None

        suff_match = re.search(r"- Evidence Sufficiency:\s*([^\n]+)", user_msg)
        sufficiency = suff_match.group(1).strip() if suff_match else None

        trigger_match = re.search(r"- Decision Trigger:\s*([^\n]+)", user_msg) or re.search(r"\* Trigger:\s*([^\n]+)", user_msg)
        trigger = trigger_match.group(1).strip() if trigger_match else None

        supp_match = re.search(r"- Supporting Evidence IDs:\s*([^\n]+)", user_msg) or re.search(r"\* Supporting Evidence IDs:\s*([^\n]+)", user_msg)
        supporting_ids = supp_match.group(1).strip() if supp_match else None

        # Determine if genuine quantum execution evidence is present
        has_execution_evidence = (
            (most_likely is not None)
            or (evidence_type == "quantum_prediction" and (target_state is not None or most_likely is not None))
            or ("VERIFIED EXPERIMENT EVIDENCE: Target state" in user_msg)
        ) and (evidence_type != "conceptual_response")

        if has_execution_evidence:
            return self._generate_quantum_execution_explanation(
                pred_state=learner_response,
                target_state=target_state,
                most_likely=most_likely or target_state or "10",
                target_prob=target_prob,
                shots=shots,
                is_correct=is_correct,
                action=action,
                target_activity=target_activity,
                reason=reason,
                hypothesis=hypothesis,
                evidence_id=evidence_id,
                sufficiency=sufficiency,
                trigger=trigger,
                supporting_ids=supporting_ids,
            )
        else:
            return self._generate_conceptual_explanation(
                learner_resp=learner_response,
                is_correct=is_correct,
                concept_id=concept_id,
                activity_id=activity_id,
                eval_details=eval_details,
                action=action,
                target_activity=target_activity,
                reason=reason,
                hypothesis=hypothesis,
                evidence_id=evidence_id,
                sufficiency=sufficiency,
                trigger=trigger,
                supporting_ids=supporting_ids,
            )

    def _generate_conceptual_explanation(
        self,
        learner_resp: str,
        is_correct: bool,
        concept_id: str,
        activity_id: str,
        eval_details: dict[str, Any],
        action: str,
        target_activity: Optional[str],
        reason: str,
        hypothesis: Optional[str] = None,
        evidence_id: Optional[str] = None,
        sufficiency: Optional[str] = None,
        trigger: Optional[str] = None,
        supporting_ids: Optional[str] = None,
    ) -> str:
        # 1. Assessment of choice
        expected_opt = eval_details.get("expected_option")
        if is_correct:
            assessment = "Your selection demonstrated correct conceptual understanding."
        elif expected_opt:
            assessment = f"Your selection was Option **{learner_resp}**, whereas the expected concept answer was Option **{expected_opt}**."
        else:
            assessment = f"Your selection was Option **{learner_resp}**, which did not match the expected conceptual response."

        # 2. Concept-specific explanation grounded in curriculum
        lower_concept = f"{concept_id} {activity_id}".lower()
        if "measurement" in lower_concept or "prob" in lower_concept:
            what_it_tests = (
                "This diagnostic evaluates understanding of **Born's rule** ($P(x) = |\\alpha_x|^2$) and wavefunction collapse. "
                "In quantum mechanics, state amplitudes $\\alpha_x \\in \\mathbb{C}$ are complex weighting coefficients that can interfere, "
                "whereas measurement probabilities $P(x)$ represent physical observation frequencies that sum to 1 ($\\sum P(x) = 1$). "
                "A high-probability state represents a statistical likelihood across repeated observations rather than a classical certainty."
            )
            takeaway = "Distinguishing probability amplitudes from physical measurement probabilities is essential before analyzing quantum interference."
        elif "superposition" in lower_concept or "hadamard" in lower_concept:
            what_it_tests = (
                "This task evaluates understanding of **equal quantum superposition** created by Hadamard gates ($H^{\\otimes n}$). "
                "Applying $H^{\\otimes 2}$ to ground state $|00\\rangle$ produces state $|s\\rangle = \\frac{1}{2}(|00\\rangle + |01\\rangle + |10\\rangle + |11\\rangle)$, "
                "where each of the 4 computational basis states has an identical amplitude of $\\frac{1}{2}$ and equal measurement probability "
                "$P(x) = \\left|\\frac{1}{2}\\right|^2 = \\frac{1}{4} = 25\\%$."
            )
            takeaway = "Equal superposition provides the uniform baseline required for amplitude amplification algorithms."
        elif "iteration" in lower_concept or "over-rotation" in lower_concept or "amplitude_amplification" in lower_concept:
            what_it_tests = (
                "This task evaluates the geometric mechanism of **Grover amplitude amplification**. "
                "Each Grover iteration rotates the quantum state vector in the 2D search subspace toward the target state. "
                "Because this unitary transformation is oscillatory rather than monotonic, applying too many iterations rotates the state "
                "vector past the target state, reducing its measurement probability."
            )
            takeaway = "Optimal query complexity in Grover's algorithm requires stopping after $\\approx \\frac{\\pi}{4}\\sqrt{N}$ iterations to maximize target probability."
        elif "qubit" in lower_concept or "state" in lower_concept:
            what_it_tests = (
                "This diagnostic assesses understanding of a **qubit state** represented as a normalized linear combination "
                "$|\\psi\\rangle = \\alpha|0\\rangle + \\beta|1\\rangle$ satisfying $|\\alpha|^2 + |\\beta|^2 = 1$. "
                "Measurement collapses the continuous state vector into a discrete classical outcome ($0$ or $1$)."
            )
            takeaway = "Qubits maintain superposition only prior to measurement; observation always yields a single definite classical state."
        else:
            what_it_tests = (
                f"This diagnostic tests core conceptual principles for concept `{concept_id or 'quantum foundations'}`. "
                "It validates mathematical understanding of quantum state transformations and measurement postulates."
            )
            takeaway = "Mastering prerequisite mathematical and physical principles ensures strong conceptual foundations."

        next_line = f"\n- **Next Activity**: `{target_activity}`" if target_activity else ""
        hyp_line = f"\n- **Learner-State Hypothesis**: `{hypothesis}`" if hypothesis else ""

        trace_section = (
            f"\n\n### Evidence & Decision Trace\n\n"
            f"- **Evidence Record**: `{evidence_id}`\n"
            f"- **Evidence Sufficiency**: `{sufficiency or 'insufficient'}`\n"
            f"- **Decision Trigger**: `{trigger or 'default_routing'}`\n"
            f"- **Supporting Evidence IDs**: `{supporting_ids or '[]'}`"
        ) if evidence_id else ""

        return (
            f"### Concept Explanation\n\n"
            f"- **Your Response**: Selected Option **{learner_resp}**\n"
            f"- **Assessment**: {assessment}\n"
            f"- **What This Tests**: {what_it_tests}\n"
            f"- **Learning Takeaway**: {takeaway}\n\n"
            f"### Adaptive Learning Path\n\n"
            f"- **Action**: `{action}`"
            f"{next_line}\n"
            f"- **Pedagogical Rationale**: {reason}"
            f"{hyp_line}"
            f"{trace_section}"
        )

    def _generate_quantum_execution_explanation(
        self,
        pred_state: str,
        target_state: Optional[str],
        most_likely: str,
        target_prob: Optional[str],
        shots: Optional[str],
        is_correct: bool,
        action: str,
        target_activity: Optional[str],
        reason: str,
        hypothesis: Optional[str] = None,
        evidence_id: Optional[str] = None,
        sufficiency: Optional[str] = None,
        trigger: Optional[str] = None,
        supporting_ids: Optional[str] = None,
    ) -> str:
        # Format states in Dirac ket notation
        pred_label = f"|{pred_state}\\rangle" if pred_state and not pred_state.startswith("|") else (pred_state or "|?⟩")
        most_likely_label = f"|{most_likely}\\rangle" if most_likely and not most_likely.startswith("|") else (most_likely or "|?⟩")

        is_match = is_correct or (pred_state == most_likely)
        if is_match:
            outcome_analysis = f"Your prediction of state ${pred_label}$ correctly matched the empirical simulation outcome ${most_likely_label}$."
        else:
            outcome_analysis = f"Your prediction was ${pred_label}$, while the empirical simulation resulted in target state ${most_likely_label}$."

        target_line = f"\n- **Target State**: Theoretical target is $|{target_state}\\rangle$." if target_state else ""
        next_line = f"\n- **Next Activity**: `{target_activity}`" if target_activity else ""
        hyp_line = f"\n- **Learner-State Hypothesis**: `{hypothesis}`" if hypothesis else ""

        # Build measurement probability line if data is present
        prob_details = []
        if target_prob:
            try:
                prob_flt = float(target_prob)
                prob_details.append(f"a target state amplitude yielding theoretical probability ~{prob_flt * 100:.1f}%")
            except ValueError:
                prob_details.append(f"target probability {target_prob}")
        if shots:
            prob_details.append(f"finite-shot sampling ({shots} shots on Qiskit Aer) produced empirical counts reflecting this distribution")

        if prob_details:
            prob_str = f" In this scenario, {'; '.join(prob_details)}."
        else:
            prob_str = " Finite-shot sampling on Qiskit Aer produces empirical counts reflecting Born's rule."

        trace_section = (
            f"\n\n### Evidence & Decision Trace\n\n"
            f"- **Evidence Record**: `{evidence_id}`\n"
            f"- **Evidence Sufficiency**: `{sufficiency or 'insufficient'}`\n"
            f"- **Decision Trigger**: `{trigger or 'default_routing'}`\n"
            f"- **Supporting Evidence IDs**: `{supporting_ids or '[]'}`"
        ) if evidence_id else ""

        return (
            f"### Quantum Execution Analysis\n\n"
            f"- **Prediction vs Outcome**: {outcome_analysis}"
            f"{target_line}\n"
            f"- **Mechanism**: The phase oracle flipped the sign of the marked target state ($O|w\\rangle = -|w\\rangle$), "
            f"and the diffusion operator ($D = 2|s\\rangle\\langle s| - I$) performed inversion-about-the-mean, "
            f"amplifying the target state amplitude.\n"
            f"- **Amplitude vs Probability**: Measurement probabilities follow Born's rule: "
            f"$P(x) = |\\alpha_x|^2.{prob_str}\n\n"
            f"### Adaptive Learning Path\n\n"
            f"- **Action**: `{action}`"
            f"{next_line}\n"
            f"- **Pedagogical Rationale**: {reason}"
            f"{hyp_line}"
            f"{trace_section}"
        )

    def _generate_qa_explanation(self, user_msg: str) -> str:
        # Extract the actual learner question from the prompt
        q_match = re.search(r"LEARNER QUESTION:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\nPlease answer|\Z)", user_msg, re.IGNORECASE)
        question_text = q_match.group(1).strip() if q_match else user_msg.strip()
        lower_q = question_text.lower()

        # Check if structured learner state context or execution evidence is present in prompt
        has_execution_context = ("most_likely_state" in user_msg) or ("counts" in user_msg and "{" in user_msg)

        # Intent 1: Prediction Mismatch / Verified Outcome inquiry
        if any(k in lower_q for k in ["prediction", "differ", "mismatch", "incorrect", "wrong", "verified result", "actual result", "outcome"]):
            if has_execution_context:
                return (
                    "### Prediction vs Quantum Execution\n\n"
                    "A prediction mismatch occurs when the learner's hypothesized basis state does not match "
                    "the high-probability state produced by the physical quantum circuit.\n\n"
                    "In Grover's search, the phase oracle flips the amplitude sign of the target state ($O|w\\rangle = -|w\\rangle$), "
                    "and the diffusion operator inverts amplitudes about the mean ($D = 2|s\\rangle\\langle s| - I$). "
                    "The empirical simulation reflects the actual amplified target state rather than the hypothesized prediction."
                )
            else:
                return (
                    "### Prediction vs Quantum Execution\n\n"
                    "The available evidence does not include a quantum execution result, so there is no measurement outcome to compare here.\n\n"
                    "In general quantum computing experiments, a prediction mismatch occurs when a learner's hypothesized basis state differs "
                    "from the high-probability computational basis state produced by the physical circuit. In Grover's algorithm, the phase oracle "
                    "inverts the target state amplitude ($O|w\\rangle = -|w\\rangle$) and the diffusion operator ($D = 2|s\\rangle\\langle s| - I$) "
                    "inverts all amplitudes about their mean, amplifying the marked state measurement probability ($P(x) = |\\alpha_x|^2$)."
                )

        # Intent 2: Diagnostic inquiry (e.g. "What does this measurement diagnostic test?")
        elif "diagnostic" in lower_q or ("test" in lower_q and ("measurement" in lower_q or "superposition" in lower_q or "grover" in lower_q)):
            if "measurement" in lower_q or "prob" in lower_concept_helper(lower_q):
                return (
                    "### Measurement Diagnostic Purpose\n\n"
                    "This diagnostic assesses your understanding of **quantum measurement** and **Born's Rule** ($P(x) = |\\alpha_x|^2$):\n\n"
                    "- **Amplitudes vs Probabilities**: State amplitudes $\\alpha_x$ are complex weighting coefficients that undergo quantum interference, whereas measurement probabilities $P(x)$ represent physical observation frequencies.\n"
                    "- **Wavefunction Collapse**: Measurement projects a superposition into a single discrete computational basis state.\n"
                    "- **Finite-Shot Sampling**: Sampling across finite shots (such as 1024 shots) produces empirical counts approximating the underlying probability distribution."
                )
            elif "superposition" in lower_q:
                return (
                    "### Superposition Diagnostic Purpose\n\n"
                    "This diagnostic assesses your understanding of **equal quantum superposition** created by Hadamard gates ($H^{\\otimes n}$):\n\n"
                    "- **Equal Amplitudes**: Applying Hadamard gates to $|00\\rangle$ creates state $|s\\rangle = \\frac{1}{2}(|00\\rangle + |01\\rangle + |10\\rangle + |11\\rangle)$.\n"
                    "- **Equal Probabilities**: Each basis state has equal measurement probability $P(x) = |1/2|^2 = 25\\%$.\n"
                    "- **Interference Foundation**: Equal superposition provides the baseline for subsequent oracle phase marking."
                )
            else:
                return (
                    "### Diagnostic Purpose\n\n"
                    "Diagnostic activities assess specific prerequisite concepts before advancing to quantum circuit construction. "
                    "They identify whether conceptual difficulties originate in linear algebra, probability, superposition, or circuit mechanics."
                )

        # Intent 3: Adaptive Recommendation / "Why This Next?"
        elif any(k in lower_q for k in ["next", "recommend", "why this", "selected", "activity", "remediation", "advance", "routing"]):
            # Check if learner context with recommendation / gap inference was provided in prompt
            ctx_match = re.search(r"LEARNER STATE CONTEXT:\s*\n(\{[\s\S]*?\})\s*\nLEARNER QUESTION:", user_msg) or re.search(r"LEARNER STATE CONTEXT:\s*\n(\{[\s\S]*\})", user_msg)
            if ctx_match:
                try:
                    learner_ctx = json.loads(ctx_match.group(1).strip())
                    rec_dict = learner_ctx.get("recommendation")
                    if rec_dict and isinstance(rec_dict, dict):
                        rec_action = rec_dict.get("action", "advance")
                        rec_target = rec_dict.get("target") or "Next curriculum activity"
                        rec_reason = rec_dict.get("reason", "Continuing learning progression.")
                        rec_trigger = rec_dict.get("trigger", "default_routing")
                        rec_suff = rec_dict.get("evidence_sufficiency", "insufficient")
                        rec_supp = json.dumps(rec_dict.get("supporting_evidence_ids", []))

                        # Extract hypothesis from gap_inferences if available
                        rec_hyp = "preliminary_observation"
                        gap_inferences = learner_ctx.get("gap_inferences", {})
                        if isinstance(gap_inferences, dict):
                            for _, gap_data in gap_inferences.items():
                                if isinstance(gap_data, dict) and "hypothesis" in gap_data:
                                    rec_hyp = gap_data["hypothesis"]
                                    break

                        return (
                            "### Adaptive Decision Explanation\n\n"
                            f"- **Selected Pedagogical Action**: `{rec_action}`\n"
                            f"- **Next Recommended Activity**: `{rec_target}`\n"
                            f"- **Pedagogical Rationale**: {rec_reason}\n"
                            f"- **Decision Trigger**: `{rec_trigger}`\n"
                            f"- **Evidence Sufficiency**: `{rec_suff}`\n"
                            f"- **Inferred Learner-State Hypothesis**: `{rec_hyp}`\n"
                            f"- **Supporting Evidence Used**: `{rec_supp}`"
                        )
                except Exception as exc:
                    logger.warning("Error parsing adaptive context: %s", exc)


            return (
                "### Adaptive Learning Path (\"Why This Next?\")\n\n"
                "Q-BIT's M2 Cognitive Engine determines the next pedagogical activity deterministically based on accumulated empirical evidence:\n\n"
                "- **Single Error**: Triggers `gather_evidence` to confirm whether a difficulty is persistent before intervening.\n"
                "- **Repeated Errors**: Triggers `targeted_remediation` by citing historical attempt records and routing to prerequisite concept diagnostics.\n"
                "- **Mastery / Recovery**: Triggers `advance` to progress along the curriculum DAG once understanding is demonstrated."
            )


        # Intent 4: Learner State / Progress
        elif any(k in lower_q for k in ["learner state", "progress", "mastery", "score", "trajectory", "gap", "inference"]):
            return (
                "### Learner State & Cognitive Tracking\n\n"
                "Q-BIT tracks your conceptual understanding across a 4-tier cognitive architecture:\n\n"
                "- **Tier 1 (Evidence)**: Empirical attempt records pairing your responses with Qiskit Aer simulation counts.\n"
                "- **Tier 2 (Accumulated State)**: Chronological attempt counts, error sequences, and score trajectories.\n"
                "- **Tier 3 (Cognitive Gaps)**: Calibrated Bayesian mastery probabilities and gap hypotheses (e.g. `observing`, `remediation_needed`, `improving`, `mastered`).\n"
                "- **Tier 4 (Pedagogical Action)**: Deterministic routing decisions grounded in evidence sufficiency."
            )

        # Intent 5: Qubit Concept (explicitly distinct from Superposition)
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

        # Intent 6: Quantum Superposition
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

        # Intent 7: Measurement / Probability / Born Rule / Amplitude
        elif any(k in lower_q for k in ["measurement", "probability", "born", "collapse", "shots", "distribution", "amplitude"]):
            return (
                "### Quantum Measurement & Born's Rule\n\n"
                "In quantum mechanics, quantum state amplitudes $\\alpha_x$ are complex numbers, "
                "while measurement probabilities $P(x)$ represent physical observation frequencies:\n\n"
                "**Born's Rule**:\n"
                "$$P(x) = |\\alpha_x|^2$$\n\n"
                "- **Amplitude vs Probability**: A quantum state with amplitude $\\alpha$ has measurement probability $P = |\\alpha|^2$. Probabilities across all computational basis states sum to 1 ($\\sum P(x) = 1$).\n"
                "- **Wavefunction Collapse**: Measurement projects the continuous state vector into a single discrete computational basis state $|x\\rangle$.\n"
                "- **Finite-Shot Sampling**: Empirical finite-shot executions produce sampled frequency counts that approximate $N_{\\text{shots}} \\times P(x)$."
            )

        # Intent 8: Grover / Oracle / Diffusion
        elif any(k in lower_q for k in ["grover", "oracle", "diffusion", "amplification", "inversion"]):
            return (
                "### Grover's Algorithm Overview\n\n"
                "Grover's algorithm searches an unstructured database of $N = 2^n$ items in $\\mathcal{O}(\\sqrt{N})$ oracle queries.\n\n"
                "**Core Steps**:\n"
                "1. **Superposition Initialization**: $|s\\rangle = H^{\\otimes n}|0\\rangle^{\\otimes n} = \\frac{1}{\\sqrt{N}}\\sum_{x=0}^{N-1}|x\\rangle$.\n"
                "2. **Phase Oracle**: Inverts the sign of the marked target state: $O|x\\rangle = (-1)^{f(x)}|x\\rangle$.\n"
                "3. **Diffusion Operator**: Inverts amplitudes about the mean: $D = 2|s\\rangle\\langle s| - I$, amplifying the marked state amplitude.\n"
                "4. **Measurement**: Collapses the quantum state according to Born's rule ($P(x) = |\\alpha_x|^2$). "
                "Empirical outcomes from finite-shot execution statistically sample this amplified distribution."
            )

        # Intent 9: Honest fallback for unknown questions
        return (
            "### Q-BIT AI Guidance\n\n"
            "I can explain what a qubit is, quantum superposition, measurement probability (Born's rule), Grover's algorithm, "
            "experiment predictions, adaptive recommendations, and your cognitive learner state. Please ask a question related to these topics."
        )


def lower_concept_helper(text: str) -> str:
    """Helper to check concept keywords in text."""
    return text.lower()


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

```

## Line Notes

### Line 1

`from __future__ import annotations`

Imports a dependency or project symbol so later code can use it by name.
### Line 2

`(blank)`

Blank line used to separate nearby statements.
### Line 3

`import json`

Imports a dependency or project symbol so later code can use it by name.
### Line 4

`import logging`

Imports a dependency or project symbol so later code can use it by name.
### Line 5

`import os`

Imports a dependency or project symbol so later code can use it by name.
### Line 6

`import re`

Imports a dependency or project symbol so later code can use it by name.
### Line 7

`from abc import ABC, abstractmethod`

Imports a dependency or project symbol so later code can use it by name.
### Line 8

`from typing import Any, Optional`

Imports a dependency or project symbol so later code can use it by name.
### Line 9

`(blank)`

Blank line used to separate nearby statements.
### Line 10

`logger = logging.getLogger(__name__)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 11

`(blank)`

Blank line used to separate nearby statements.
### Line 13

`class LLMProvider(ABC):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 14

`"""Abstract interface for LLM completion providers."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 15

`(blank)`

Blank line used to separate nearby statements.
### Line 16

`@abstractmethod`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 17

`def generate(self, messages: list[dict[str, str]], model: Optional[str] = None) -> str:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 18

`"""Generate an AI completion string given a list of chat messages."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 19

`pass`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 20

`(blank)`

Blank line used to separate nearby statements.
### Line 22

`class MockLLMProvider(LLMProvider):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 23

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 24

`Deterministic, offline mock provider for automated testing and standalone execution.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 25

`Inspects structured message content and evidence types to generate curriculum-grounded`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 26

`KaTeX markdown without requiring external network calls or API keys.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 27

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 28

`(blank)`

Blank line used to separate nearby statements.
### Line 29

`def generate(self, messages: list[dict[str, str]], model: Optional[str] = None) -> str:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 30

`user_msg = next((m["content"] for m in messages if m.get("role") == "user"), "")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 31

`(blank)`

Blank line used to separate nearby statements.
### Line 32

`# 1. Structured Evidence Attempt Explanation Handling`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 33

`if any(marker in user_msg for marker in [`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 34

`"LEARNER EVIDENCE:",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 35

`"VERIFIED EXPERIMENT EVIDENCE:",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 36

`"VERIFIED SIMULATION RESULT:",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 37

`"QUANTUM EXECUTION EVIDENCE:",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 38

`"EVIDENCE CONTEXT:",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 39

`]):`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 40

`return self._generate_evidence_grounded_explanation(user_msg)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 41

`(blank)`

Blank line used to separate nearby statements.
### Line 42

`# 2. General Concept / Inquirer Q&A Handling`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 43

`return self._generate_qa_explanation(user_msg)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 44

`(blank)`

Blank line used to separate nearby statements.
### Line 45

`def _generate_evidence_grounded_explanation(self, user_msg: str) -> str:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 46

`# Extract evidence type and core metadata`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 47

`ev_type_match = re.search(r"Evidence Type:\s*([^\n\(\)]+)", user_msg)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 48

`evidence_type = ev_type_match.group(1).strip() if ev_type_match else ""`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 49

`(blank)`

Blank line used to separate nearby statements.
### Line 50

`concept_match = re.search(r"- Concept ID:\s*([^\n]+)", user_msg) or re.search(r"\* Concept:\s*([^\n]+)", user_msg)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 51

`concept_id = concept_match.group(1).strip() if concept_match else ""`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 52

`(blank)`

Blank line used to separate nearby statements.
### Line 53

`activity_match = re.search(r"- Activity ID:\s*([^\n]+)", user_msg)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 54

`activity_id = activity_match.group(1).strip() if activity_match else ""`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 55

`(blank)`

Blank line used to separate nearby statements.
### Line 56

`ev_id_match = re.search(r"- Evidence ID:\s*([^\n\s]+)", user_msg)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 57

`evidence_id = ev_id_match.group(1).strip() if ev_id_match else None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 58

`if evidence_id == "N/A":`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 59

`evidence_id = None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 60

`(blank)`

Blank line used to separate nearby statements.
### Line 61

`# Extract learner response`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 62

`learner_resp_match = (`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 63

`re.search(r"- Learner Response / Selection:\s*([^\n]+)", user_msg)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 64

`or re.search(r"- Learner Predicted State / Response:\s*([^\n]+)", user_msg)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 65

`or re.search(r"prediction was\s*([^\n,\.]+)", user_msg, re.IGNORECASE)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 66

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 67

`learner_response = learner_resp_match.group(1).strip() if learner_resp_match else ""`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 68

`(blank)`

Blank line used to separate nearby statements.
### Line 69

`# Extract correctness`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 70

`outcome_match = re.search(r"- Evaluation Outcome:\s*([^\n]+)", user_msg) or re.search(r"- Empirical Evaluation Outcome:\s*([^\n]+)", user_msg)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 71

`outcome_str = outcome_match.group(1).strip() if outcome_match else ""`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 72

`is_correct = ("INCORRECT" not in outcome_str.upper()) and ("CORRECT" in outcome_str.upper() or "MATCH (Correct" in outcome_str)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 73

`(blank)`

Blank line used to separate nearby statements.
### Line 75

`# Extract evaluation details`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 76

`eval_details = {}`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 77

`eval_details_match = re.search(r"- Evaluation Details:\s*([^\n]+)", user_msg)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 78

`if eval_details_match:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 79

`try:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 80

`eval_details = json.loads(eval_details_match.group(1).strip())`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 81

`except Exception:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 82

`pass`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 83

`(blank)`

Blank line used to separate nearby statements.
### Line 84

`# Extract quantum execution fields`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 85

`target_match = re.search(r"- Theoretical Target State:\s*([^\n]+)", user_msg) or re.search(r"Target state\s*\|?([0-9a-zA-Z]+)⟩?", user_msg, re.IGNORECASE)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 86

`target_state = target_match.group(1).strip() if target_match else None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 87

`if target_state == "N/A":`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 88

`target_state = None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 89

`(blank)`

Blank line used to separate nearby statements.
### Line 90

`most_likely_match = re.search(r"- Empirical Most-Likely Measured State:\s*([^\n]+)", user_msg)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 91

`most_likely = most_likely_match.group(1).strip() if most_likely_match else None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 92

`if most_likely == "N/A":`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 93

`most_likely = None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 94

`(blank)`

Blank line used to separate nearby statements.
### Line 95

`prob_match = re.search(r"- Target State Probability:\s*([^\n]+)", user_msg)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 96

`target_prob = prob_match.group(1).strip() if prob_match else None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 97

`if target_prob == "N/A":`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 98

`target_prob = None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 99

`(blank)`

Blank line used to separate nearby statements.
### Line 100

`shots_match = re.search(r"- Total Shots Sampled:\s*([^\n]+)", user_msg)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 101

`shots = shots_match.group(1).strip() if shots_match else None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 102

`if shots == "N/A":`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 103

`shots = None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 104

`(blank)`

Blank line used to separate nearby statements.
### Line 105

`# Extract adaptive decision fields`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 106

`action_match = re.search(r"- Action:\s*([^\n]+)", user_msg) or re.search(r"\* Action:\s*([^\n]+)", user_msg)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 107

`action = action_match.group(1).strip() if action_match else "advance"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 108

`(blank)`

Blank line used to separate nearby statements.
### Line 109

`target_act_match = re.search(r"- Target Activity:\s*([^\n]+)", user_msg) or re.search(r"\* Target:\s*([^\n]+)", user_msg)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 110

`target_activity = target_act_match.group(1).strip() if target_act_match else None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 111

`if target_activity == "N/A":`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 112

`target_activity = None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 113

`(blank)`

Blank line used to separate nearby statements.
### Line 114

`reason_match = re.search(r"- Pedagogical Rationale:\s*([^\n]+)", user_msg) or re.search(r"\* Rationale:\s*([^\n]+)", user_msg)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 115

`reason = reason_match.group(1).strip() if reason_match else "Continuing learning sequence."`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 116

`(blank)`

Blank line used to separate nearby statements.
### Line 117

`hyp_match = re.search(r"- Learner-State Hypothesis:\s*([^\n]+)", user_msg) or re.search(r"\* Hypothesis:\s*([^\n]+)", user_msg)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 118

`hypothesis = hyp_match.group(1).strip() if hyp_match else None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 119

`(blank)`

Blank line used to separate nearby statements.
### Line 120

`suff_match = re.search(r"- Evidence Sufficiency:\s*([^\n]+)", user_msg)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 121

`sufficiency = suff_match.group(1).strip() if suff_match else None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 122

`(blank)`

Blank line used to separate nearby statements.
### Line 123

`trigger_match = re.search(r"- Decision Trigger:\s*([^\n]+)", user_msg) or re.search(r"\* Trigger:\s*([^\n]+)", user_msg)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 124

`trigger = trigger_match.group(1).strip() if trigger_match else None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 125

`(blank)`

Blank line used to separate nearby statements.
### Line 126

`supp_match = re.search(r"- Supporting Evidence IDs:\s*([^\n]+)", user_msg) or re.search(r"\* Supporting Evidence IDs:\s*([^\n]+)", user_msg)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 127

`supporting_ids = supp_match.group(1).strip() if supp_match else None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 128

`(blank)`

Blank line used to separate nearby statements.
### Line 129

`# Determine if genuine quantum execution evidence is present`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 130

`has_execution_evidence = (`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 131

`(most_likely is not None)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 132

`or (evidence_type == "quantum_prediction" and (target_state is not None or most_likely is not None))`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 133

`or ("VERIFIED EXPERIMENT EVIDENCE: Target state" in user_msg)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 134

`) and (evidence_type != "conceptual_response")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 135

`(blank)`

Blank line used to separate nearby statements.
### Line 136

`if has_execution_evidence:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 137

`return self._generate_quantum_execution_explanation(`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 138

`pred_state=learner_response,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 139

`target_state=target_state,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 140

`most_likely=most_likely or target_state or "10",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 141

`target_prob=target_prob,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 142

`shots=shots,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 143

`is_correct=is_correct,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 144

`action=action,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 145

`target_activity=target_activity,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 146

`reason=reason,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 147

`hypothesis=hypothesis,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 148

`evidence_id=evidence_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 149

`sufficiency=sufficiency,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 150

`trigger=trigger,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 151

`supporting_ids=supporting_ids,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 152

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 153

`else:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 154

`return self._generate_conceptual_explanation(`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 155

`learner_resp=learner_response,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 156

`is_correct=is_correct,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 157

`concept_id=concept_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 158

`activity_id=activity_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 159

`eval_details=eval_details,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 160

`action=action,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 161

`target_activity=target_activity,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 162

`reason=reason,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 163

`hypothesis=hypothesis,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 164

`evidence_id=evidence_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 165

`sufficiency=sufficiency,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 166

`trigger=trigger,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 167

`supporting_ids=supporting_ids,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 168

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 169

`(blank)`

Blank line used to separate nearby statements.
### Line 170

`def _generate_conceptual_explanation(`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 171

`self,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 172

`learner_resp: str,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 173

`is_correct: bool,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 174

`concept_id: str,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 175

`activity_id: str,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 176

`eval_details: dict[str, Any],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 177

`action: str,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 178

`target_activity: Optional[str],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 179

`reason: str,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 180

`hypothesis: Optional[str] = None,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 181

`evidence_id: Optional[str] = None,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 182

`sufficiency: Optional[str] = None,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 183

`trigger: Optional[str] = None,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 184

`supporting_ids: Optional[str] = None,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 185

`) -> str:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 186

`# 1. Assessment of choice`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 187

`expected_opt = eval_details.get("expected_option")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 188

`if is_correct:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 189

`assessment = "Your selection demonstrated correct conceptual understanding."`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 190

`elif expected_opt:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 191

`assessment = f"Your selection was Option **{learner_resp}**, whereas the expected concept answer was Option **{expected_opt}**."`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 192

`else:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 193

`assessment = f"Your selection was Option **{learner_resp}**, which did not match the expected conceptual response."`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 194

`(blank)`

Blank line used to separate nearby statements.
### Line 195

`# 2. Concept-specific explanation grounded in curriculum`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 196

`lower_concept = f"{concept_id} {activity_id}".lower()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 197

`if "measurement" in lower_concept or "prob" in lower_concept:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 198

`what_it_tests = (`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 199

`"This diagnostic evaluates understanding of **Born's rule** ($P(x) = |\\alpha_x|^2$) and wavefunction collapse. "`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 200

`"In quantum mechanics, state amplitudes $\\alpha_x \\in \\mathbb{C}$ are complex weighting coefficients that can interfere, "`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 201

`"whereas measurement probabilities $P(x)$ represent physical observation frequencies that sum to 1 ($\\sum P(x) = 1$). "`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 202

`"A high-probability state represents a statistical likelihood across repeated observations rather than a classical certainty."`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 203

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 204

`takeaway = "Distinguishing probability amplitudes from physical measurement probabilities is essential before analyzing quantum interference."`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 205

`elif "superposition" in lower_concept or "hadamard" in lower_concept:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 206

`what_it_tests = (`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 207

`"This task evaluates understanding of **equal quantum superposition** created by Hadamard gates ($H^{\\otimes n}$). "`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 208

`"Applying $H^{\\otimes 2}$ to ground state $|00\\rangle$ produces state $|s\\rangle = \\frac{1}{2}(|00\\rangle + |01\\rangle + |10\\rangle + |11\\rangle)$, "`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 209

`"where each of the 4 computational basis states has an identical amplitude of $\\frac{1}{2}$ and equal measurement probability "`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 210

`"$P(x) = \\left|\\frac{1}{2}\\right|^2 = \\frac{1}{4} = 25\\%$."`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 211

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 212

`takeaway = "Equal superposition provides the uniform baseline required for amplitude amplification algorithms."`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 213

`elif "iteration" in lower_concept or "over-rotation" in lower_concept or "amplitude_amplification" in lower_concept:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 214

`what_it_tests = (`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 215

`"This task evaluates the geometric mechanism of **Grover amplitude amplification**. "`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 216

`"Each Grover iteration rotates the quantum state vector in the 2D search subspace toward the target state. "`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 217

`"Because this unitary transformation is oscillatory rather than monotonic, applying too many iterations rotates the state "`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 218

`"vector past the target state, reducing its measurement probability."`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 219

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 220

`takeaway = "Optimal query complexity in Grover's algorithm requires stopping after $\\approx \\frac{\\pi}{4}\\sqrt{N}$ iterations to maximize target probability."`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 221

`elif "qubit" in lower_concept or "state" in lower_concept:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 222

`what_it_tests = (`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 223

`"This diagnostic assesses understanding of a **qubit state** represented as a normalized linear combination "`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 224

`"$|\\psi\\rangle = \\alpha|0\\rangle + \\beta|1\\rangle$ satisfying $|\\alpha|^2 + |\\beta|^2 = 1$. "`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 225

`"Measurement collapses the continuous state vector into a discrete classical outcome ($0$ or $1$)."`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 226

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 227

`takeaway = "Qubits maintain superposition only prior to measurement; observation always yields a single definite classical state."`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 228

`else:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 229

`what_it_tests = (`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 230

`f"This diagnostic tests core conceptual principles for concept \`{concept_id or 'quantum foundations'}\`. "`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 231

`"It validates mathematical understanding of quantum state transformations and measurement postulates."`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 232

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 233

`takeaway = "Mastering prerequisite mathematical and physical principles ensures strong conceptual foundations."`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 234

`(blank)`

Blank line used to separate nearby statements.
### Line 235

`next_line = f"\n- **Next Activity**: \`{target_activity}\`" if target_activity else ""`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 236

`hyp_line = f"\n- **Learner-State Hypothesis**: \`{hypothesis}\`" if hypothesis else ""`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 237

`(blank)`

Blank line used to separate nearby statements.
### Line 238

`trace_section = (`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 239

`f"\n\n### Evidence & Decision Trace\n\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 240

`f"- **Evidence Record**: \`{evidence_id}\`\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 241

`f"- **Evidence Sufficiency**: \`{sufficiency or 'insufficient'}\`\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 242

`f"- **Decision Trigger**: \`{trigger or 'default_routing'}\`\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 243

`f"- **Supporting Evidence IDs**: \`{supporting_ids or '[]'}\`"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 244

`) if evidence_id else ""`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 245

`(blank)`

Blank line used to separate nearby statements.
### Line 246

`return (`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 247

`f"### Concept Explanation\n\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 248

`f"- **Your Response**: Selected Option **{learner_resp}**\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 249

`f"- **Assessment**: {assessment}\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 250

`f"- **What This Tests**: {what_it_tests}\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 251

`f"- **Learning Takeaway**: {takeaway}\n\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 252

`f"### Adaptive Learning Path\n\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 253

`f"- **Action**: \`{action}\`"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 254

`f"{next_line}\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 255

`f"- **Pedagogical Rationale**: {reason}"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 256

`f"{hyp_line}"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 257

`f"{trace_section}"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 258

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 259

`(blank)`

Blank line used to separate nearby statements.
### Line 260

`def _generate_quantum_execution_explanation(`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 261

`self,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 262

`pred_state: str,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 263

`target_state: Optional[str],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 264

`most_likely: str,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 265

`target_prob: Optional[str],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 266

`shots: Optional[str],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 267

`is_correct: bool,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 268

`action: str,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 269

`target_activity: Optional[str],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 270

`reason: str,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 271

`hypothesis: Optional[str] = None,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 272

`evidence_id: Optional[str] = None,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 273

`sufficiency: Optional[str] = None,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 274

`trigger: Optional[str] = None,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 275

`supporting_ids: Optional[str] = None,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 276

`) -> str:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 277

`# Format states in Dirac ket notation`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 278

`pred_label = f"|{pred_state}\\rangle" if pred_state and not pred_state.startswith("|") else (pred_state or "|?⟩")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 279

`most_likely_label = f"|{most_likely}\\rangle" if most_likely and not most_likely.startswith("|") else (most_likely or "|?⟩")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 280

`(blank)`

Blank line used to separate nearby statements.
### Line 281

`is_match = is_correct or (pred_state == most_likely)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 282

`if is_match:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 283

`outcome_analysis = f"Your prediction of state ${pred_label}$ correctly matched the empirical simulation outcome ${most_likely_label}$."`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 284

`else:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 285

`outcome_analysis = f"Your prediction was ${pred_label}$, while the empirical simulation resulted in target state ${most_likely_label}$."`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 286

`(blank)`

Blank line used to separate nearby statements.
### Line 287

`target_line = f"\n- **Target State**: Theoretical target is $|{target_state}\\rangle$." if target_state else ""`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 288

`next_line = f"\n- **Next Activity**: \`{target_activity}\`" if target_activity else ""`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 289

`hyp_line = f"\n- **Learner-State Hypothesis**: \`{hypothesis}\`" if hypothesis else ""`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 290

`(blank)`

Blank line used to separate nearby statements.
### Line 291

`# Build measurement probability line if data is present`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 292

`prob_details = []`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 293

`if target_prob:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 294

`try:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 295

`prob_flt = float(target_prob)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 296

`prob_details.append(f"a target state amplitude yielding theoretical probability ~{prob_flt * 100:.1f}%")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 297

`except ValueError:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 298

`prob_details.append(f"target probability {target_prob}")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 299

`if shots:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 300

`prob_details.append(f"finite-shot sampling ({shots} shots on Qiskit Aer) produced empirical counts reflecting this distribution")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 301

`(blank)`

Blank line used to separate nearby statements.
### Line 302

`if prob_details:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 303

`prob_str = f" In this scenario, {'; '.join(prob_details)}."`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 304

`else:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 305

`prob_str = " Finite-shot sampling on Qiskit Aer produces empirical counts reflecting Born's rule."`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 306

`(blank)`

Blank line used to separate nearby statements.
### Line 307

`trace_section = (`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 308

`f"\n\n### Evidence & Decision Trace\n\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 309

`f"- **Evidence Record**: \`{evidence_id}\`\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 310

`f"- **Evidence Sufficiency**: \`{sufficiency or 'insufficient'}\`\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 311

`f"- **Decision Trigger**: \`{trigger or 'default_routing'}\`\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 312

`f"- **Supporting Evidence IDs**: \`{supporting_ids or '[]'}\`"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 313

`) if evidence_id else ""`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 314

`(blank)`

Blank line used to separate nearby statements.
### Line 315

`return (`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 316

`f"### Quantum Execution Analysis\n\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 317

`f"- **Prediction vs Outcome**: {outcome_analysis}"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 318

`f"{target_line}\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 319

`f"- **Mechanism**: The phase oracle flipped the sign of the marked target state ($O|w\\rangle = -|w\\rangle$), "`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 320

`f"and the diffusion operator ($D = 2|s\\rangle\\langle s| - I$) performed inversion-about-the-mean, "`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 321

`f"amplifying the target state amplitude.\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 322

`f"- **Amplitude vs Probability**: Measurement probabilities follow Born's rule: "`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 323

`f"$P(x) = |\\alpha_x|^2.{prob_str}\n\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 324

`f"### Adaptive Learning Path\n\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 325

`f"- **Action**: \`{action}\`"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 326

`f"{next_line}\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 327

`f"- **Pedagogical Rationale**: {reason}"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 328

`f"{hyp_line}"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 329

`f"{trace_section}"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 330

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 331

`(blank)`

Blank line used to separate nearby statements.
### Line 332

`def _generate_qa_explanation(self, user_msg: str) -> str:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 333

`# Extract the actual learner question from the prompt`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 334

`q_match = re.search(r"LEARNER QUESTION:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\nPlease answer|\Z)", user_msg, re.IGNORECASE)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 335

`question_text = q_match.group(1).strip() if q_match else user_msg.strip()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 336

`lower_q = question_text.lower()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 337

`(blank)`

Blank line used to separate nearby statements.
### Line 338

`# Check if structured learner state context or execution evidence is present in prompt`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 339

`has_execution_context = ("most_likely_state" in user_msg) or ("counts" in user_msg and "{" in user_msg)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 340

`(blank)`

Blank line used to separate nearby statements.
### Line 341

`# Intent 1: Prediction Mismatch / Verified Outcome inquiry`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 342

`if any(k in lower_q for k in ["prediction", "differ", "mismatch", "incorrect", "wrong", "verified result", "actual result", "outcome"]):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 343

`if has_execution_context:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 344

`return (`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 345

`"### Prediction vs Quantum Execution\n\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 346

`"A prediction mismatch occurs when the learner's hypothesized basis state does not match "`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 347

`"the high-probability state produced by the physical quantum circuit.\n\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 348

`"In Grover's search, the phase oracle flips the amplitude sign of the target state ($O|w\\rangle = -|w\\rangle$), "`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 349

`"and the diffusion operator inverts amplitudes about the mean ($D = 2|s\\rangle\\langle s| - I$). "`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 350

`"The empirical simulation reflects the actual amplified target state rather than the hypothesized prediction."`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 351

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 352

`else:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 353

`return (`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 354

`"### Prediction vs Quantum Execution\n\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 355

`"The available evidence does not include a quantum execution result, so there is no measurement outcome to compare here.\n\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 356

`"In general quantum computing experiments, a prediction mismatch occurs when a learner's hypothesized basis state differs "`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 357

`"from the high-probability computational basis state produced by the physical circuit. In Grover's algorithm, the phase oracle "`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 358

`"inverts the target state amplitude ($O|w\\rangle = -|w\\rangle$) and the diffusion operator ($D = 2|s\\rangle\\langle s| - I$) "`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 359

`"inverts all amplitudes about their mean, amplifying the marked state measurement probability ($P(x) = |\\alpha_x|^2$)."`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 360

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 361

`(blank)`

Blank line used to separate nearby statements.
### Line 362

`# Intent 2: Diagnostic inquiry (e.g. "What does this measurement diagnostic test?")`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 363

`elif "diagnostic" in lower_q or ("test" in lower_q and ("measurement" in lower_q or "superposition" in lower_q or "grover" in lower_q)):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 364

`if "measurement" in lower_q or "prob" in lower_concept_helper(lower_q):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 365

`return (`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 366

`"### Measurement Diagnostic Purpose\n\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 367

`"This diagnostic assesses your understanding of **quantum measurement** and **Born's Rule** ($P(x) = |\\alpha_x|^2$):\n\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 368

`"- **Amplitudes vs Probabilities**: State amplitudes $\\alpha_x$ are complex weighting coefficients that undergo quantum interference, whereas measurement probabilities $P(x)$ represent physical observation frequencies.\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 369

`"- **Wavefunction Collapse**: Measurement projects a superposition into a single discrete computational basis state.\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 370

`"- **Finite-Shot Sampling**: Sampling across finite shots (such as 1024 shots) produces empirical counts approximating the underlying probability distribution."`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 371

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 372

`elif "superposition" in lower_q:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 373

`return (`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 374

`"### Superposition Diagnostic Purpose\n\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 375

`"This diagnostic assesses your understanding of **equal quantum superposition** created by Hadamard gates ($H^{\\otimes n}$):\n\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 376

`"- **Equal Amplitudes**: Applying Hadamard gates to $|00\\rangle$ creates state $|s\\rangle = \\frac{1}{2}(|00\\rangle + |01\\rangle + |10\\rangle + |11\\rangle)$.\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 377

`"- **Equal Probabilities**: Each basis state has equal measurement probability $P(x) = |1/2|^2 = 25\\%$.\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 378

`"- **Interference Foundation**: Equal superposition provides the baseline for subsequent oracle phase marking."`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 379

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 380

`else:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 381

`return (`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 382

`"### Diagnostic Purpose\n\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 383

`"Diagnostic activities assess specific prerequisite concepts before advancing to quantum circuit construction. "`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 384

`"They identify whether conceptual difficulties originate in linear algebra, probability, superposition, or circuit mechanics."`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 385

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 386

`(blank)`

Blank line used to separate nearby statements.
### Line 387

`# Intent 3: Adaptive Recommendation / "Why This Next?"`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 388

`elif any(k in lower_q for k in ["next", "recommend", "why this", "selected", "activity", "remediation", "advance", "routing"]):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 389

`# Check if learner context with recommendation / gap inference was provided in prompt`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 390

`ctx_match = re.search(r"LEARNER STATE CONTEXT:\s*\n(\{[\s\S]*?\})\s*\nLEARNER QUESTION:", user_msg) or re.search(r"LEARNER STATE CONTEXT:\s*\n(\{[\s\S]*\})", user_msg)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 391

`if ctx_match:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 392

`try:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 393

`learner_ctx = json.loads(ctx_match.group(1).strip())`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 394

`rec_dict = learner_ctx.get("recommendation")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 395

`if rec_dict and isinstance(rec_dict, dict):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 396

`rec_action = rec_dict.get("action", "advance")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 397

`rec_target = rec_dict.get("target") or "Next curriculum activity"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 398

`rec_reason = rec_dict.get("reason", "Continuing learning progression.")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 399

`rec_trigger = rec_dict.get("trigger", "default_routing")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 400

`rec_suff = rec_dict.get("evidence_sufficiency", "insufficient")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 401

`rec_supp = json.dumps(rec_dict.get("supporting_evidence_ids", []))`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 402

`(blank)`

Blank line used to separate nearby statements.
### Line 403

`# Extract hypothesis from gap_inferences if available`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 404

`rec_hyp = "preliminary_observation"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 405

`gap_inferences = learner_ctx.get("gap_inferences", {})`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 406

`if isinstance(gap_inferences, dict):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 407

`for _, gap_data in gap_inferences.items():`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 408

`if isinstance(gap_data, dict) and "hypothesis" in gap_data:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 409

`rec_hyp = gap_data["hypothesis"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 410

`break`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 411

`(blank)`

Blank line used to separate nearby statements.
### Line 412

`return (`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 413

`"### Adaptive Decision Explanation\n\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 414

`f"- **Selected Pedagogical Action**: \`{rec_action}\`\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 415

`f"- **Next Recommended Activity**: \`{rec_target}\`\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 416

`f"- **Pedagogical Rationale**: {rec_reason}\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 417

`f"- **Decision Trigger**: \`{rec_trigger}\`\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 418

`f"- **Evidence Sufficiency**: \`{rec_suff}\`\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 419

`f"- **Inferred Learner-State Hypothesis**: \`{rec_hyp}\`\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 420

`f"- **Supporting Evidence Used**: \`{rec_supp}\`"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 421

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 422

`except Exception as exc:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 423

`logger.warning("Error parsing adaptive context: %s", exc)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 424

`(blank)`

Blank line used to separate nearby statements.
### Line 426

`return (`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 427

`"### Adaptive Learning Path (\"Why This Next?\")\n\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 428

`"Q-BIT's M2 Cognitive Engine determines the next pedagogical activity deterministically based on accumulated empirical evidence:\n\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 429

`"- **Single Error**: Triggers \`gather_evidence\` to confirm whether a difficulty is persistent before intervening.\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 430

`"- **Repeated Errors**: Triggers \`targeted_remediation\` by citing historical attempt records and routing to prerequisite concept diagnostics.\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 431

`"- **Mastery / Recovery**: Triggers \`advance\` to progress along the curriculum DAG once understanding is demonstrated."`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 432

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 433

`(blank)`

Blank line used to separate nearby statements.
### Line 435

`# Intent 4: Learner State / Progress`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 436

`elif any(k in lower_q for k in ["learner state", "progress", "mastery", "score", "trajectory", "gap", "inference"]):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 437

`return (`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 438

`"### Learner State & Cognitive Tracking\n\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 439

`"Q-BIT tracks your conceptual understanding across a 4-tier cognitive architecture:\n\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 440

`"- **Tier 1 (Evidence)**: Empirical attempt records pairing your responses with Qiskit Aer simulation counts.\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 441

`"- **Tier 2 (Accumulated State)**: Chronological attempt counts, error sequences, and score trajectories.\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 442

`"- **Tier 3 (Cognitive Gaps)**: Calibrated Bayesian mastery probabilities and gap hypotheses (e.g. \`observing\`, \`remediation_needed\`, \`improving\`, \`mastered\`).\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 443

`"- **Tier 4 (Pedagogical Action)**: Deterministic routing decisions grounded in evidence sufficiency."`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 444

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 445

`(blank)`

Blank line used to separate nearby statements.
### Line 446

`# Intent 5: Qubit Concept (explicitly distinct from Superposition)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 447

`elif ("qubit" in lower_q or "quantum bit" in lower_q) and ("superposition" not in lower_q):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 448

`return (`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 449

`"### Understanding the Qubit\n\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 450

`"A **qubit** (quantum bit) is the fundamental unit of quantum information, analogous to a classical bit (0 or 1):\n\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 451

`"- **State Representation**: A qubit state $|\\psi\\rangle$ is represented as a linear combination of orthonormal basis states:\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 452

`"$$|\\psi\\rangle = \\alpha|0\\rangle + \\beta|1\\rangle$$\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 453

`"- **Probability Amplitudes**: $\\alpha, \\beta \\in \\mathbb{C}$ are complex probability amplitudes normalized such that:\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 454

`"$$|\\alpha|^2 + |\\beta|^2 = 1$$\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 455

`"- **Measurement & Probabilities**: Measuring the qubit collapses the state, yielding outcome $0$ with probability $P(0) = |\\alpha|^2$ or outcome $1$ with probability $P(1) = |\\beta|^2$.\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 456

`"- **Key Distinction**: While superposition allows simultaneous amplitude weights before observation, measurement always produces a single classical outcome. A qubit is not simply 'a bit that is both 0 and 1 at the same time'."`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 457

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 458

`(blank)`

Blank line used to separate nearby statements.
### Line 459

`# Intent 6: Quantum Superposition`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 460

`elif any(k in lower_q for k in ["superposition", "hadamard", "basis state", "|+⟩", "|-⟩", "bloch"]):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 461

`return (`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 462

`"### Quantum Superposition\n\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 463

`"**Superposition** is the physical principle that allows a quantum state to exist as a linear combination of basis states simultaneously:\n\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 464

`"$$|\\psi\\rangle = \\alpha|0\\rangle + \\beta|1\\rangle$$\n\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 465

`"- **Equal Superposition via Hadamard Gate**: Applying an $H$ gate to basis state $|0\\rangle$ yields:\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 466

`"$$H|0\\rangle = \\frac{|0\\rangle + |1\\rangle}{\\sqrt{2}}$$\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 467

`"- **Probabilistic Symmetry**: Both basis states have equal amplitude $\\frac{1}{\\sqrt{2}}$, yielding equal measurement probabilities:\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 468

`"$$P(0) = \\left|\\frac{1}{\\sqrt{2}}\\right|^2 = 0.5 \\quad (50\\%), \\quad P(1) = \\left|\\frac{1}{\\sqrt{2}}\\right|^2 = 0.5 \\quad (50\\%)$$\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 469

`"- **Phase & Interference**: Unlike classical probabilities, amplitudes can have relative phases (e.g. negative signs) that enable constructive and destructive quantum interference."`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 470

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 471

`(blank)`

Blank line used to separate nearby statements.
### Line 472

`# Intent 7: Measurement / Probability / Born Rule / Amplitude`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 473

`elif any(k in lower_q for k in ["measurement", "probability", "born", "collapse", "shots", "distribution", "amplitude"]):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 474

`return (`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 475

`"### Quantum Measurement & Born's Rule\n\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 476

`"In quantum mechanics, quantum state amplitudes $\\alpha_x$ are complex numbers, "`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 477

`"while measurement probabilities $P(x)$ represent physical observation frequencies:\n\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 478

`"**Born's Rule**:\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 479

`"$$P(x) = |\\alpha_x|^2$$\n\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 480

`"- **Amplitude vs Probability**: A quantum state with amplitude $\\alpha$ has measurement probability $P = |\\alpha|^2$. Probabilities across all computational basis states sum to 1 ($\\sum P(x) = 1$).\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 481

`"- **Wavefunction Collapse**: Measurement projects the continuous state vector into a single discrete computational basis state $|x\\rangle$.\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 482

`"- **Finite-Shot Sampling**: Empirical finite-shot executions produce sampled frequency counts that approximate $N_{\\text{shots}} \\times P(x)$."`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 483

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 484

`(blank)`

Blank line used to separate nearby statements.
### Line 485

`# Intent 8: Grover / Oracle / Diffusion`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 486

`elif any(k in lower_q for k in ["grover", "oracle", "diffusion", "amplification", "inversion"]):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 487

`return (`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 488

`"### Grover's Algorithm Overview\n\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 489

`"Grover's algorithm searches an unstructured database of $N = 2^n$ items in $\\mathcal{O}(\\sqrt{N})$ oracle queries.\n\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 490

`"**Core Steps**:\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 491

`"1. **Superposition Initialization**: $|s\\rangle = H^{\\otimes n}|0\\rangle^{\\otimes n} = \\frac{1}{\\sqrt{N}}\\sum_{x=0}^{N-1}|x\\rangle$.\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 492

`"2. **Phase Oracle**: Inverts the sign of the marked target state: $O|x\\rangle = (-1)^{f(x)}|x\\rangle$.\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 493

`"3. **Diffusion Operator**: Inverts amplitudes about the mean: $D = 2|s\\rangle\\langle s| - I$, amplifying the marked state amplitude.\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 494

`"4. **Measurement**: Collapses the quantum state according to Born's rule ($P(x) = |\\alpha_x|^2$). "`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 495

`"Empirical outcomes from finite-shot execution statistically sample this amplified distribution."`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 496

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 497

`(blank)`

Blank line used to separate nearby statements.
### Line 498

`# Intent 9: Honest fallback for unknown questions`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 499

`return (`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 500

`"### Q-BIT AI Guidance\n\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 501

`"I can explain what a qubit is, quantum superposition, measurement probability (Born's rule), Grover's algorithm, "`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 502

`"experiment predictions, adaptive recommendations, and your cognitive learner state. Please ask a question related to these topics."`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 503

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 504

`(blank)`

Blank line used to separate nearby statements.
### Line 506

`def lower_concept_helper(text: str) -> str:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 507

`"""Helper to check concept keywords in text."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 508

`return text.lower()`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 509

`(blank)`

Blank line used to separate nearby statements.
### Line 511

`class GroqLLMProvider(LLMProvider):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 512

`"""Production provider using Groq API completions."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 513

`(blank)`

Blank line used to separate nearby statements.
### Line 514

`def __init__(self, api_key: Optional[str] = None) -> None:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 515

`self.api_key = api_key or os.getenv("GROQ_API_KEY")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 516

`if not self.api_key:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 517

`raise ValueError("GROQ_API_KEY must be set in environment or passed to GroqLLMProvider.")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 518

`try:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 519

`from groq import Groq`

Imports a dependency or project symbol so later code can use it by name.
### Line 520

`self.client = Groq(api_key=self.api_key)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 521

`except ImportError:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 522

`raise ImportError("The 'groq' Python package is required to use GroqLLMProvider. Install with 'pip install groq'.")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 523

`(blank)`

Blank line used to separate nearby statements.
### Line 524

`def generate(self, messages: list[dict[str, str]], model: Optional[str] = None) -> str:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 525

`chosen_model = model or os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 526

`response = self.client.chat.completions.create(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 527

`model=chosen_model,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 528

`messages=messages,  # type: ignore`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 529

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 530

`return response.choices[0].message.content or ""`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 531

`(blank)`

Blank line used to separate nearby statements.
### Line 533

`def get_default_provider() -> LLMProvider:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 534

`"""Factory returning GroqLLMProvider if GROQ_API_KEY is present, else MockLLMProvider."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 535

`if os.getenv("GROQ_API_KEY"):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 536

`try:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 537

`return GroqLLMProvider()`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 538

`except Exception as exc:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 539

`logger.warning("Failed to initialize GroqLLMProvider; falling back to MockLLMProvider: %s", exc)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 540

`return MockLLMProvider()`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 541

`return MockLLMProvider()`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.

## Nearby Files

[backend/ai/__init__.py](__init__.py.md), [backend/ai/prompts.py](prompts.py.md), [backend/ai/retrieval.py](retrieval.py.md), [backend/ai/service.py](service.py.md)
