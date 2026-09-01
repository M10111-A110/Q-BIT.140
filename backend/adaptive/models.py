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
    """
    [TIER 4: ADAPTIVE DECISION]
    Actionable next pedagogical recommendation produced deterministically by M2,
    grounded in accumulated evidence and inferred cognitive state.
    """
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
    [TIER 2: ACCUMULATED EVIDENCE & PERSISTENT REPOSITORY STATE]
    Tracks empirical attempt records, chronological evidence history, score trajectories,
    and derived gap inferences across time for an individual learner.
    """
    user_id: str
    concept_scores: dict[str, float] = field(default_factory=dict)       # Latest observed attempt score per concept (Tier 1)
    attempts: dict[str, int] = field(default_factory=dict)               # Total attempt counts per concept (Tier 2)
    errors: dict[str, list[str]] = field(default_factory=dict)           # Recorded error representations per concept (Tier 2)
    score_history: dict[str, list[float]] = field(default_factory=dict)  # Chronological attempt scores per concept (Tier 2)
    last_updated: dict[str, float] = field(default_factory=dict)         # Timestamps of latest attempt per concept
    evidence_history: list[dict[str, Any]] = field(default_factory=list) # Immutable chronological array of LearnerEvidence dicts (Tier 2)
    gap_inferences: dict[str, dict[str, Any]] = field(default_factory=dict) # Inferred conceptual gap/trend states (Tier 3)

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
    [TIER 3: INFERRED LEARNER STATE SNAPSHOT]
    Structured cognitive state snapshot bridging M2 evidence to M4 (API Gateway),
    M5 (AI Guidance), and M1 (Learner Dashboards).
    """
    user_id: str
    concept_mastery: dict[str, float] = field(default_factory=dict)      # Inferred continuous mastery [0.0, 1.0] (Tier 3)
    concept_scores: dict[str, float] = field(default_factory=dict)       # Latest attempt score (Tier 1)
    attempts: dict[str, int] = field(default_factory=dict)               # Attempt counts (Tier 2)
    errors: dict[str, list[str]] = field(default_factory=dict)           # Error counts/items (Tier 2)
    score_history: dict[str, list[float]] = field(default_factory=dict)  # Score trajectories (Tier 2)
    gap_inferences: dict[str, dict[str, Any]] = field(default_factory=dict) # Gap inferences & trends (Tier 3)
    current_concept: Optional[str] = None
    recommendation: Optional[AdaptiveRecommendation] = None              # Next pedagogical action (Tier 4)

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
