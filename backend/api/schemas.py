from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check status response schema."""
    status: str = "ok"
    service: str = "qbit-api"


class ActivitySummary(BaseModel):
    """Concise activity summary for listing."""
    activity_id: str
    concept_id: str
    title: str
    description: str
    task_type: str
    prerequisites: list[str] = Field(default_factory=list)


class ActivityDetailResponse(BaseModel):
    """Detailed activity response for frontend rendering."""
    activity_id: str
    concept_id: str
    title: str
    description: str
    task_type: str
    prerequisites: list[str] = Field(default_factory=list)
    prompt: str
    options: Optional[dict[str, str]] = None
    quantum_experiment: Optional[dict[str, Any]] = None
    remediation_activity_id: Optional[str] = None
    next_activity_id: Optional[str] = None


class SubmissionRequest(BaseModel):
    """Learner activity submission request payload."""
    learner_id: str = Field(..., min_length=1, description="Unique identifier for the learner")
    response: str = Field(..., min_length=1, description="Learner prediction or chosen answer option")


class AdaptiveDecisionResponse(BaseModel):
    """Structured adaptive decision resulting from evidence evaluation."""
    action: str
    target: Optional[Any] = None
    reason: str
    concept_id: Optional[str] = None


class SubmissionResponse(BaseModel):
    """Complete response contract for an activity submission."""
    activity: dict[str, Any]
    learner_response: str
    verified_result: Optional[dict[str, Any]] = None
    evidence: dict[str, Any]
    learner_state: dict[str, Any]
    adaptive_decision: dict[str, Any]


class AskRequest(BaseModel):
    """Payload for conceptual quantum question inquiry."""
    question: str = Field(..., min_length=1, description="Learner question about quantum concepts")
    learner_context: Optional[dict[str, Any]] = Field(default=None, description="Optional snapshot of learner mastery")
    concept_id: Optional[str] = Field(default=None, description="Optional canonical concept ID")


class AskResponse(BaseModel):
    """Response containing grounded AI guidance answer."""
    question: str
    answer: str
    concept_id: Optional[str] = None


class ExplainExperimentRequest(BaseModel):
    """Payload requesting an AI explanation of an empirical experiment attempt."""
    learner_response: str = Field(..., min_length=1, description="What the learner predicted or selected")
    verified_result: Optional[dict[str, Any]] = Field(default=None, description="M3 verified simulation result dictionary")
    evidence: dict[str, Any] = Field(..., description="LearnerEvidence dictionary")
    adaptive_decision: dict[str, Any] = Field(..., description="M2 adaptive recommendation dictionary")
    user_question: Optional[str] = Field(default=None, description="Optional specific inquiry from learner about outcome")


class ExplainExperimentResponse(BaseModel):
    """Response containing grounded explanation of the experiment attempt."""
    explanation: str
    learner_response: str
    adaptive_decision: dict[str, Any]
