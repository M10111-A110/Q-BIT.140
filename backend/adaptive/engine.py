from __future__ import annotations

from typing import Any, Optional

from .concepts import CONCEPT_GRAPH, resolve_concept_id
from .models import (
    AdaptiveRecommendation,
    LearnerContext,
    LearnerState,
)

MASTERY_THRESHOLD: float = 0.6  # Score below which concept counts as not mastered
ERROR_STREAK_LIMIT: int = 2     # Consecutive errors triggering targeted review


class LearnerModel:
    """
    Cognitive mastery model and adaptive decision engine.
    Ties together concept prerequisite dependencies, diagnostic evidence,
    historical improvement, error penalties, and deterministic explainable routing.
    """

    def __init__(
        self,
        concept_graph: Optional[dict] = None,
        threshold: float = MASTERY_THRESHOLD,
    ) -> None:
        self.graph = concept_graph if concept_graph is not None else CONCEPT_GRAPH
        self.threshold = threshold

    def compute_mastery(self, topic: str, state: LearnerState) -> float:
        """
        Compute transparent mastery score for a topic given learner history:
          mastery = diagnostic_score + improvement_bonus - error_penalty
        Clamped within [0.0, 1.0] and rounded to 3 decimal places.
        Preserves exact original M2 mathematical behavior.
        """
        diag_score = state.concept_scores.get(topic, 0.0)

        history = state.score_history.get(topic, [])
        improvement = 0.0
        if len(history) >= 2:
            improvement = max(0.0, history[-1] - history[-2]) * 0.2  # up to +0.2 bonus

        error_count = len(state.errors.get(topic, []))
        error_penalty = min(error_count * 0.05, 0.3)  # capped at 0.3

        mastery = diag_score + improvement - error_penalty
        return round(max(0.0, min(1.0, mastery)), 3)

    def recommend_next(self, topic: str, state: LearnerState) -> AdaptiveRecommendation:
        """
        Determine the next pedagogical recommendation for the learner given their state.
        Evaluation order:
          1. Prerequisite mastery check
          2. Error streak check -> targeted review
          3. Mastery pass check -> advance to dependent concepts
          4. Default -> reinforce current concept

        Preserves exact original M2 routing logic and explanations.
        """
        if topic not in self.graph:
            raise KeyError(f"Unknown topic '{topic}'. Known graph topics: {list(self.graph.keys())}")

        # 1. Prerequisite verification
        for prereq in self.graph[topic]["prereqs"]:
            prereq_mastery = self.compute_mastery(prereq, state)
            if prereq_mastery < self.threshold:
                return AdaptiveRecommendation(
                    action="recommend_prerequisite",
                    target=prereq,
                    reason=(
                        f"{prereq} mastery is {prereq_mastery} (< {self.threshold}), "
                        f"so {topic} isn't safe to build on yet."
                    ),
                    concept_id=resolve_concept_id(prereq),
                )

        mastery = self.compute_mastery(topic, state)
        error_count = len(state.errors.get(topic, []))

        # 2. Repeated errors on this exact concept -> targeted review
        if error_count >= ERROR_STREAK_LIMIT and mastery < self.threshold:
            return AdaptiveRecommendation(
                action="recommend_targeted_review",
                target=topic,
                reason=(
                    f"{error_count} wrong answers on {topic} and mastery is only "
                    f"{mastery} — needs focused review, not just repetition."
                ),
                concept_id=resolve_concept_id(topic),
            )

        # 3. Mastered -> unlock dependent concepts
        if mastery >= self.threshold:
            next_topics = [c for c, v in self.graph.items() if topic in v["prereqs"]]
            target = next_topics if next_topics else None
            next_str = f" to {', '.join(next_topics)}" if next_topics else " (end of chain)"
            return AdaptiveRecommendation(
                action="advance",
                target=target,
                reason=f"{topic} mastery is {mastery} (>= {self.threshold}) — ready to move on{next_str}.",
                concept_id=resolve_concept_id(topic),
            )

        # 4. Default: not mastered yet, no glaring error pattern -> reinforce
        return AdaptiveRecommendation(
            action="reinforce_current_concept",
            target=topic,
            reason=(
                f"{topic} mastery is {mastery} (< {self.threshold}) — "
                f"needs more practice before moving on."
            ),
            concept_id=resolve_concept_id(topic),
        )

    def get_mastery_profile(self, state: LearnerState) -> dict[str, float]:
        """Compute mastery for all concepts in the DAG."""
        return {
            topic: self.compute_mastery(topic, state)
            for topic in self.graph
        }

    def get_learner_context(
        self,
        state: LearnerState,
        current_topic: Optional[str] = None,
    ) -> LearnerContext:
        """
        Build a complete LearnerContext domain snapshot summarizing mastery,
        attempts, errors, and current recommendation.
        """
        mastery_by_canonical = {
            resolve_concept_id(topic): self.compute_mastery(topic, state)
            for topic in self.graph
        }

        rec = None
        if current_topic and current_topic in self.graph:
            rec = self.recommend_next(current_topic, state)

        return LearnerContext(
            user_id=state.user_id,
            concept_mastery=mastery_by_canonical,
            concept_scores=dict(state.concept_scores),
            attempts=dict(state.attempts),
            errors=dict(state.errors),
            score_history=dict(state.score_history),
            current_concept=current_topic,
            recommendation=rec,
        )
