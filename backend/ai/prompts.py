from __future__ import annotations

import json
from typing import Any, Optional

SYSTEM_PROMPT = """You are the Q-BIT AI Guidance assistant for a quantum computing learning platform.
You help learners understand Grover's Algorithm and its prerequisites (linear algebra, probability, qubits, gates, circuits).

Rules:
- Base your answers strictly on the CURRICULUM CONTEXT and VERIFIED EXPERIMENT EVIDENCE provided below.
- Explicitly distinguish between:
  1. The learner's predicted state / choice.
  2. The theoretical / target state.
  3. The empirical most-likely measured state from simulation counts.
- Never invent or alter quantum execution counts, target states, or measured probabilities.
- Never override or change the adaptive decision made by the learner model (M2).
- Distinguish observed empirical simulation results from ideal theoretical calculations.
- Correct common misconceptions gently when relevant (e.g. amplitude vs probability, single-shot vs distribution).
- Format equations using standard KaTeX: inline as $formula$ and block display as $$formula$$.
"""


def build_ask_prompt(
    question: str,
    curriculum_context: str,
    learner_context: Optional[dict[str, Any]] = None,
) -> list[dict[str, str]]:
    """Build messages list for conceptual question answering."""
    learner_context_str = ""
    if learner_context:
        learner_context_str = f"\nLEARNER STATE CONTEXT:\n{json.dumps(learner_context, indent=2)}\n"

    user_content = f"""CURRICULUM CONTEXT:
{curriculum_context}
{learner_context_str}
LEARNER QUESTION:
{question}

Please answer the learner's question using the curriculum context above. Format all math with KaTeX ($...$ or $$...$$)."""

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]


def build_experiment_explanation_prompt(
    learner_response: str,
    verified_result: Optional[dict[str, Any]],
    evidence: dict[str, Any],
    adaptive_decision: dict[str, Any],
    curriculum_context: str,
    user_question: Optional[str] = None,
) -> list[dict[str, str]]:
    """
    Build messages list for explaining an empirical quantum experiment attempt.
    Explicitly structures the 3 distinct states:
      1. Learner Predicted State / Response
      2. Theoretical Target State
      3. Empirical Most-Likely Measured State
    """
    user_q_section = f"\nLEARNER ADDITIONAL QUESTION:\n{user_question}\n" if user_question else ""

    target_state = verified_result.get("target_state", "N/A") if verified_result else "N/A"
    most_likely_state = verified_result.get("most_likely_state", "N/A") if verified_result else "N/A"
    target_prob = verified_result.get("target_probability", "N/A") if verified_result else "N/A"
    counts = verified_result.get("counts", {}) if verified_result else "N/A"
    shots = verified_result.get("shots", "N/A") if verified_result else "N/A"
    circuit_info = verified_result.get("circuit", {}) if verified_result else "N/A"

    is_correct = evidence.get("is_correct", False)
    outcome_str = "MATCH (Correct Prediction)" if is_correct else "MISMATCH (Incorrect Prediction)"
    evidence_id = evidence.get("evidence_id", "N/A")
    evidence_type = evidence.get("evidence_type", "N/A")
    evidence_sufficiency = adaptive_decision.get("evidence_sufficiency", "insufficient")
    decision_id = adaptive_decision.get("decision_id", "N/A")
    trigger = adaptive_decision.get("trigger", "N/A")
    supporting_ids = adaptive_decision.get("supporting_evidence_ids", [])

    user_content = f"""CURRICULUM CONTEXT:
{curriculum_context}

VERIFIED EXPERIMENT EVIDENCE:
- Evidence ID: {evidence_id} (Type: {evidence_type})
- Learner Predicted State / Response: {learner_response}
- Theoretical Target State: {target_state}
- Empirical Most-Likely Measured State: {most_likely_state}
- Target State Probability: {target_prob}
- Empirical Measurement Counts: {json.dumps(counts)}
- Total Shots Sampled: {shots}
- Circuit Metadata: {json.dumps(circuit_info)}
- Empirical Evaluation Outcome: {outcome_str}
- Evidence Sufficiency: {evidence_sufficiency}
- Adaptive Recommendation from M2:
  * Decision ID: {decision_id}
  * Action: {adaptive_decision.get('action', 'N/A')}
  * Target: {adaptive_decision.get('target', 'N/A')}
  * Rationale: {adaptive_decision.get('reason', 'N/A')}
  * Concept: {adaptive_decision.get('concept_id', 'N/A')}
  * Trigger: {trigger}
  * Supporting Evidence IDs: {json.dumps(supporting_ids)}
{user_q_section}
Explain the relationship between the learner's prediction, the verified quantum result (oracle marking and amplitude amplification), and why M2 recommended this adaptive decision. Format all equations using KaTeX ($...$ or $$...$$)."""

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]
