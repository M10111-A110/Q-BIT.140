from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any, Optional

from .concepts import resolve_concept_id


@dataclass
class Question:
    """Diagnostic quiz question domain model."""
    topic: str
    question: str
    options: dict[str, str]
    correct_answer: str
    explanation: str
    difficulty: str
    concept_id: str = field(default="")

    def __post_init__(self) -> None:
        if not self.concept_id:
            self.concept_id = resolve_concept_id(self.topic)
        self.correct_answer = self.correct_answer.strip().upper()
        self.difficulty = self.difficulty.strip().lower()


@dataclass
class QuizSubmission:
    """Inbound quiz answer submission from a learner."""
    user_id: str
    topic: str
    answers: dict[str, str]  # {question_text: chosen_letter}


@dataclass
class QuizResult:
    """Evaluated outcome of a diagnostic quiz attempt."""
    topic: str
    concept_id: str
    score: float
    total_questions: int
    correct_count: int
    wrong_questions: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "topic": self.topic,
            "concept_id": self.concept_id,
            "score": self.score,
            "total_questions": self.total_questions,
            "correct_count": self.correct_count,
            "wrong_questions": self.wrong_questions,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> QuizResult:
        return cls(
            topic=str(d.get("topic", "")),
            concept_id=resolve_concept_id(d.get("concept_id", "")),
            score=float(d.get("score", 0.0)),
            total_questions=int(d.get("total_questions", 0)),
            correct_count=int(d.get("correct_count", 0)),
            wrong_questions=list(d.get("wrong_questions", [])),
        )


@dataclass
class AdaptiveRecommendation:
    """Actionable recommendation produced by the adaptive learner model."""
    action: str  # advance | gather_evidence | targeted_remediation | recommend_prerequisite | recommend_targeted_review | reinforce_current_concept
    target: str | list[str] | None
    reason: str
    concept_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "target": self.target,
            "reason": self.reason,
            "concept_id": self.concept_id,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> AdaptiveRecommendation:
        return cls(
            action=str(d.get("action", "reinforce_current_concept")),
            target=d.get("target"),
            reason=str(d.get("reason", "")),
            concept_id=d.get("concept_id"),
        )


@dataclass
class LearnerState:
    """
    Persistent state of an individual learner tracking concept performance,
    history trajectories, error records, empirical evidence history, and
    derived gap inferences.
    """
    user_id: str
    concept_scores: dict[str, float] = field(default_factory=dict)
    attempts: dict[str, int] = field(default_factory=dict)
    errors: dict[str, list[str]] = field(default_factory=dict)
    score_history: dict[str, list[float]] = field(default_factory=dict)
    last_updated: dict[str, float] = field(default_factory=dict)
    evidence_history: list[dict[str, Any]] = field(default_factory=list)
    gap_inferences: dict[str, dict[str, Any]] = field(default_factory=dict)

    def record_attempt(self, topic: str, score: float, wrong_questions: list[str]) -> None:
        """Record the outcome of a quiz attempt, updating history and timestamps."""
        self.concept_scores[topic] = score
        self.attempts[topic] = self.attempts.get(topic, 0) + 1
        self.errors[topic] = wrong_questions
        self.score_history.setdefault(topic, []).append(score)
        self.last_updated[topic] = time.time()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> LearnerState:
        return cls(
            user_id=str(d.get("user_id", "")),
            concept_scores=dict(d.get("concept_scores", {})),
            attempts=dict(d.get("attempts", {})),
            errors=dict(d.get("errors", {})),
            score_history=dict(d.get("score_history", {})),
            last_updated=dict(d.get("last_updated", {})),
            evidence_history=list(d.get("evidence_history", [])),
            gap_inferences=dict(d.get("gap_inferences", {})),
        )


@dataclass
class LearnerContext:
    """
    Domain-level summary snapshot representing the learner's cognitive state,
    used to bridge M2 evidence to M4 (API), M5 (AI Guidance), and UI dashboards.
    """
    user_id: str
    concept_mastery: dict[str, float] = field(default_factory=dict)
    concept_scores: dict[str, float] = field(default_factory=dict)
    attempts: dict[str, int] = field(default_factory=dict)
    errors: dict[str, list[str]] = field(default_factory=dict)
    score_history: dict[str, list[float]] = field(default_factory=dict)
    gap_inferences: dict[str, dict[str, Any]] = field(default_factory=dict)
    current_concept: Optional[str] = None
    recommendation: Optional[AdaptiveRecommendation] = None

    def to_dict(self) -> dict[str, Any]:
        rec_dict = self.recommendation.to_dict() if self.recommendation else None
        return {
            "user_id": self.user_id,
            "concept_mastery": self.concept_mastery,
            "concept_scores": self.concept_scores,
            "attempts": self.attempts,
            "errors": self.errors,
            "score_history": self.score_history,
            "gap_inferences": self.gap_inferences,
            "current_concept": self.current_concept,
            "recommendation": rec_dict,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> LearnerContext:
        rec_raw = d.get("recommendation")
        rec = AdaptiveRecommendation.from_dict(rec_raw) if rec_raw else None
        return cls(
            user_id=str(d.get("user_id", "")),
            concept_mastery=dict(d.get("concept_mastery", {})),
            concept_scores=dict(d.get("concept_scores", {})),
            attempts=dict(d.get("attempts", {})),
            errors=dict(d.get("errors", {})),
            score_history=dict(d.get("score_history", {})),
            gap_inferences=dict(d.get("gap_inferences", {})),
            current_concept=d.get("current_concept"),
            recommendation=rec,
        )
