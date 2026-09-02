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
