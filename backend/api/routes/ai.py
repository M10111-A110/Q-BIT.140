from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

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
    try:
        answer = ask_question(
            question=req.question,
            learner_context=req.learner_context,
            concept_id=req.concept_id,
            provider=provider,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI guidance service is currently unavailable: {exc}",
        ) from exc

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
    try:
        explanation = explain_experiment(
            learner_response=req.learner_response,
            verified_result=req.verified_result,
            evidence=req.evidence,
            adaptive_decision=req.adaptive_decision,
            user_question=req.user_question,
            provider=provider,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI guidance service is currently unavailable: {exc}",
        ) from exc

    return ExplainExperimentResponse(
        explanation=explanation,
        learner_response=req.learner_response,
        adaptive_decision=req.adaptive_decision,
    )
