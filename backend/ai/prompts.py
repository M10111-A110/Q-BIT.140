from __future__ import annotations

import json
from typing import Any, Optional

SYSTEM_PROMPT = """You are the Q-BIT AI Guidance assistant for an evidence-driven adaptive quantum computing learning platform.
You help learners understand quantum concepts, algorithms (including Grover's algorithm), and their mathematical foundations.

Grounding Contract & Strict Rules:
- Base your answers strictly on the supplied EVIDENCE and CURRICULUM CONTEXT.
- Maintain a strict distinction between:
  1. CURRICULUM KNOWLEDGE: General educational principles (used strictly for conceptual explanations, never as learner evidence).
  2. LEARNER EVIDENCE: The learner's actual response/choice, correctness, and task metadata.
  3. QUANTUM EXECUTION EVIDENCE: Authoritative simulation outputs (counts, probabilities, measured states, circuits) from verified quantum executions.
  4. ADAPTIVE DECISION: Deterministic pedagogical actions, hypotheses, and rationales from M2.
- NEVER claim an interaction was a quantum execution or simulation unless QUANTUM EXECUTION EVIDENCE is explicitly provided in the prompt.
- NEVER format non-state choices (e.g. MCQ option letters A, B, C, D) as Dirac quantum state kets like |A⟩ or |B⟩.
- NEVER fabricate missing values, target states, predictions, measurement counts, or shot statistics.
- If a field is missing or not applicable, omit that claim completely. Never output placeholder tokens like "N/A" or "|N/A⟩" as observed facts.
- For conceptual responses without execution evidence: explain what was asked, the learner's response, correctness, the underlying quantum concept, and learning takeaways.
- For quantum executions: explain the prediction vs verified outcome, target state (if present), measurement probabilities/counts (if present), and circuit mechanism.
- For adaptive decisions: explain why M2 selected the action based on the supplied evidence sufficiency and trigger.
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

    user_content = f"""CURRICULUM KNOWLEDGE CONTEXT:
{curriculum_context}
{learner_context_str}
LEARNER QUESTION:
{question}

Please answer the learner's question using the curriculum knowledge context above. If the question asks about a specific learner attempt or execution outcome that is not present in the supplied learner state context, state honestly that no execution evidence is present. Format all math with KaTeX ($...$ or $$...$$)."""

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
    Build messages list for explaining a learner attempt.
    Strictly structures:
      1. Curriculum Knowledge Context (Educational background)
      2. Learner Evidence (Observed response and evaluation)
      3. Quantum Execution Evidence (Actual simulation output if present, or explicitly None)
      4. Adaptive Recommendation from M2 (Deterministic pedagogical routing)
    """
    user_q_section = f"\nLEARNER ADDITIONAL QUESTION:\n{user_question}\n" if user_question else ""

    evidence_id = evidence.get("evidence_id", "N/A")
    evidence_type = evidence.get("evidence_type", "derived_evaluation")
    evidence_source = evidence.get("evidence_source", "learner")
    concept_id = evidence.get("concept_id", "")
    activity_id = evidence.get("activity_id", "")
    is_correct = evidence.get("is_correct", False)
    outcome_str = "CORRECT" if is_correct else "INCORRECT / MISMATCH"
    eval_details = evidence.get("evaluation_details", {})

    # 1. Learner Evidence block
    learner_ev_lines = [
        f"- Evidence ID: {evidence_id}",
        f"- Evidence Type: {evidence_type}",
        f"- Evidence Source: {evidence_source}",
    ]
    if concept_id:
        learner_ev_lines.append(f"- Concept ID: {concept_id}")
    if activity_id:
        learner_ev_lines.append(f"- Activity ID: {activity_id}")
    learner_ev_lines.append(f"- Learner Predicted State / Response: {learner_response}")
    learner_ev_lines.append(f"- Evaluation Outcome: {outcome_str}")
    if eval_details:
        learner_ev_lines.append(f"- Evaluation Details: {json.dumps(eval_details)}")
    learner_evidence_block = "\n".join(learner_ev_lines)

    # 2. Quantum Execution Evidence block (strictly omit if no execution occurred)
    has_execution = bool(verified_result and isinstance(verified_result, dict))
    if has_execution:
        exec_lines = [
            f"- Algorithm: {verified_result.get('algorithm', 'Quantum Circuit')}",
        ]
        if "target_state" in verified_result:
            exec_lines.append(f"- Theoretical Target State: {verified_result['target_state']}")
        if "most_likely_state" in verified_result:
            exec_lines.append(f"- Empirical Most-Likely Measured State: {verified_result['most_likely_state']}")
        if "target_probability" in verified_result:
            exec_lines.append(f"- Target State Probability: {verified_result['target_probability']}")
        if "counts" in verified_result:
            exec_lines.append(f"- Empirical Measurement Counts: {json.dumps(verified_result['counts'])}")
        if "shots" in verified_result:
            exec_lines.append(f"- Total Shots Sampled: {verified_result['shots']}")
        if "circuit" in verified_result:
            exec_lines.append(f"- Circuit Metadata: {json.dumps(verified_result['circuit'])}")
        quantum_execution_block = "\n".join(exec_lines)
    else:
        quantum_execution_block = "None (This interaction was a conceptual/diagnostic task without quantum circuit execution.)"

    # 3. Adaptive Decision block
    decision_lines = []
    if adaptive_decision and isinstance(adaptive_decision, dict):
        if "decision_id" in adaptive_decision:
            decision_lines.append(f"- Decision ID: {adaptive_decision['decision_id']}")
        if "action" in adaptive_decision:
            decision_lines.append(f"- Action: {adaptive_decision['action']}")
        if "target" in adaptive_decision and adaptive_decision["target"] is not None:
            decision_lines.append(f"- Target Activity: {adaptive_decision['target']}")
        if "reason" in adaptive_decision:
            decision_lines.append(f"- Pedagogical Rationale: {adaptive_decision['reason']}")
        if "hypothesis" in adaptive_decision:
            decision_lines.append(f"- Learner-State Hypothesis: {adaptive_decision['hypothesis']}")
        if "trigger" in adaptive_decision:
            decision_lines.append(f"- Decision Trigger: {adaptive_decision['trigger']}")
        if "evidence_sufficiency" in adaptive_decision:
            decision_lines.append(f"- Evidence Sufficiency: {adaptive_decision['evidence_sufficiency']}")
        if "supporting_evidence_ids" in adaptive_decision:
            decision_lines.append(f"- Supporting Evidence IDs: {json.dumps(adaptive_decision['supporting_evidence_ids'])}")

    adaptive_decision_block = "\n".join(decision_lines) if decision_lines else "None"

    # Tailor guidance instruction to the available evidence type
    if has_execution:
        instruction = (
            "Provide a Grounded Quantum Execution Analysis comparing the learner's prediction with the verified empirical outcome, "
            "explaining the physical circuit mechanism and Born's rule measurement probabilities, and explain why M2 recommended this adaptive decision. "
            "Format all equations using KaTeX ($...$ or $$...$$)."
        )
    else:
        instruction = (
            "Provide a Grounded Concept Explanation for the learner's response, explaining what was tested, whether the selection was correct, "
            "the underlying quantum concept, and why M2 recommended this adaptive decision. "
            "DO NOT include a quantum execution analysis or discuss simulator shot counts because no circuit execution occurred. "
            "Format all equations using KaTeX ($...$ or $$...$$)."
        )

    user_content = f"""CURRICULUM KNOWLEDGE CONTEXT:
{curriculum_context}

LEARNER EVIDENCE:
{learner_evidence_block}

QUANTUM EXECUTION EVIDENCE:
{quantum_execution_block}

ADAPTIVE RECOMMENDATION (M2):
{adaptive_decision_block}
{user_q_section}
{instruction}"""

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]
