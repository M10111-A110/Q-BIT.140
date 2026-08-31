from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.ai import LLMProvider, ask_question, explain_experiment

from ..dependencies import get_llm_provider
from ..schemas import (
    AskRequest,
    AskResponse,
    ExplainExperimentRequest,
    ExplainExperimentResponse,
)

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/ask", response_model=AskResponse)
def handle_ai_ask(
    req: AskRequest,
    provider: LLMProvider = Depends(get_llm_provider),
) -> AskResponse:
    """
    Answer a learner's conceptual quantum question grounded strictly in curriculum knowledge.
    """
    answer = ask_question(
        question=req.question,
        learner_context=req.learner_context,
        concept_id=req.concept_id,
        provider=provider,
    )
    return AskResponse(
        question=req.question,
        answer=answer,
        concept_id=req.concept_id,
    )


@router.post("/explain_experiment", response_model=ExplainExperimentResponse)
def handle_explain_experiment(
    req: ExplainExperimentRequest,
    provider: LLMProvider = Depends(get_llm_provider),
) -> ExplainExperimentResponse:
    """
    Generate an AI explanation of an empirical experiment attempt, explaining the relationship
    between the learner's prediction, the verified quantum result, and M2's adaptive decision.
    """
    explanation = explain_experiment(
        learner_response=req.learner_response,
        verified_result=req.verified_result,
        evidence=req.evidence,
        adaptive_decision=req.adaptive_decision,
        user_question=req.user_question,
        provider=provider,
    )

    return ExplainExperimentResponse(
        explanation=explanation,
        learner_response=req.learner_response,
        adaptive_decision=req.adaptive_decision,
    )
