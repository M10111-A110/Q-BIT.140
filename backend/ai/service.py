from __future__ import annotations

from typing import Any, Optional

from .prompts import build_ask_prompt, build_experiment_explanation_prompt
from .providers import LLMProvider, get_default_provider
from .retrieval import find_relevant_knowledge


def ask_question(
    question: str,
    learner_context: Optional[dict[str, Any]] = None,
    concept_id: Optional[str] = None,
    provider: Optional[LLMProvider] = None,
) -> str:
    """
    Answer a learner's conceptual inquiry grounded in curriculum knowledge.
    """
    active_provider = provider or get_default_provider()

    # Retrieve relevant curriculum content
    search_query = f"{question} {concept_id or ''}".strip()
    curriculum_context = find_relevant_knowledge(search_query, top_n=2)

    # Build prompt and generate response
    messages = build_ask_prompt(
        question=question,
        curriculum_context=curriculum_context,
        learner_context=learner_context,
    )

    return active_provider.generate(messages)


def explain_experiment(
    learner_response: str,
    verified_result: Optional[dict[str, Any]],
    evidence: dict[str, Any],
    adaptive_decision: dict[str, Any],
    user_question: Optional[str] = None,
    provider: Optional[LLMProvider] = None,
) -> str:
    """
    Generate a grounded explanation of a completed quantum experiment attempt,
    correlating learner prediction, verified execution evidence, and M2 adaptive decision.
    """
    active_provider = provider or get_default_provider()

    concept_id = evidence.get("concept_id", "")
    search_query = f"grover oracle diffusion measurement probability {concept_id} {user_question or ''}".strip()
    curriculum_context = find_relevant_knowledge(search_query, top_n=2)

    messages = build_experiment_explanation_prompt(
        learner_response=learner_response,
        verified_result=verified_result,
        evidence=evidence,
        adaptive_decision=adaptive_decision,
        curriculum_context=curriculum_context,
        user_question=user_question,
    )

    return active_provider.generate(messages)
