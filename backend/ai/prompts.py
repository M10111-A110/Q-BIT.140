from __future__ import annotations

import json
from typing import Any, Optional

SYSTEM_PROMPT = """You are the Q-BIT AI Guidance assistant for a quantum computing learning platform.
You help learners understand Grover's Algorithm and its prerequisites (linear algebra, probability, qubits, gates, circuits).

Rules:
- Base your answers strictly on the CURRICULUM CONTEXT and VERIFIED EXPERIMENT EVIDENCE provided below.
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
    """Build messages list for explaining an empirical quantum experiment attempt."""
    user_q_section = f"\nLEARNER ADDITIONAL QUESTION:\n{user_question}\n" if user_question else ""

    user_content = f"""CURRICULUM CONTEXT:
{curriculum_context}

VERIFIED EXPERIMENT EVIDENCE:
- Learner Prediction / Response: {learner_response}
- Verified Simulation Result: {json.dumps(verified_result, indent=2) if verified_result else "N/A (Conceptual task)"}
- Evaluation Details: {json.dumps(evidence.get('evaluation_details', {}), indent=2)}
- Adaptive Decision from M2: {json.dumps(adaptive_decision, indent=2)}
{user_q_section}
Explain the relationship between the learner's prediction, the verified quantum result (oracle marking and amplitude amplification), and why M2 recommended this adaptive decision. Format all equations using KaTeX ($...$ or $$...$$)."""

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]
