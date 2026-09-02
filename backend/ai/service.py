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

    # Dynamic, evidence-aware search query based on actual concept, activity, algorithm, and question
    query_parts = []
    concept_id = evidence.get("concept_id", "")
    if concept_id:
        query_parts.append(concept_id.replace(".", " "))
    activity_id = evidence.get("activity_id", "")
    if activity_id:
        query_parts.append(activity_id.replace("_", " "))
    if user_question:
        query_parts.append(user_question)
    if verified_result and isinstance(verified_result, dict):
        algo = verified_result.get("algorithm")
        if algo:
            query_parts.append(str(algo))

    search_query = " ".join(query_parts).strip() or "quantum computing foundations"
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
