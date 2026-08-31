from __future__ import annotations

import time
from typing import Any, Optional

from .activities import MVP_ACTIVITIES, get_activity
from .concepts import (
    CONCEPT_GRAPH,
    get_concept_display_name,
    resolve_concept_id,
)
from .evidence import GapInference, LearnerEvidence
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

    def record_evidence(
        self,
        evidence: LearnerEvidence,
        state: LearnerState,
    ) -> AdaptiveRecommendation:
        """
        Ingest an empirical LearnerEvidence observation, accumulate historical evidence,
        derive calibrated gap inferences, and return a deterministic adaptive recommendation.
        """
        canonical_concept = resolve_concept_id(evidence.concept_id)
        display_name = get_concept_display_name(canonical_concept)

        # 1. Append to evidence history
        state.evidence_history.append(evidence.to_dict())

        # 2. Update basic state counters
        state.attempts[display_name] = state.attempts.get(display_name, 0) + 1
        state.last_updated[display_name] = time.time()

        # 3. Update score trajectory based on outcome
        attempt_score = 1.0 if evidence.is_correct else 0.0
        state.concept_scores[display_name] = attempt_score
        state.score_history.setdefault(display_name, []).append(attempt_score)

        if not evidence.is_correct:
            err_repr = str(evidence.learner_response)
            state.errors.setdefault(display_name, []).append(err_repr)
        else:
            # If successful after prior errors, clear active error list for this concept
            if display_name in state.errors and len(state.errors[display_name]) > 0:
                state.errors[display_name] = []

        # 4. Deterministic Gap Inference from Accumulated Evidence
        concept_evidence = [
            e for e in state.evidence_history
            if resolve_concept_id(e.get("concept_id", "")) == canonical_concept
        ]
        recent = concept_evidence[-5:]
        recent_errors = [e for e in recent if not e.get("is_correct", False)]
        recent_successes = [e for e in recent if e.get("is_correct", False)]

        if len(recent_errors) == 0 and len(recent_successes) >= 1:
            confidence = 0.0
            status = "mastered"
            desc = f"Evidence demonstrates consistent understanding of {display_name}."
        elif evidence.is_correct and len(concept_evidence) >= 2 and not concept_evidence[-2].get("is_correct", False):
            confidence = 0.15
            status = "improving"
            desc = f"Evidence indicates post-intervention improvement in {display_name}."
        elif len(recent_errors) == 1:
            confidence = 0.35  # Low confidence: single error is not proof of misconception
            status = "observing"
            desc = f"Evidence is consistent with possible difficulty in {display_name} (preliminary observation from 1 incorrect attempt)."
        else:
            # 2 or more recent errors
            confidence = min(0.40 + len(recent_errors) * 0.25, 0.90)
            status = "remediation_needed"
            desc = f"Evidence is consistent with possible difficulty in {display_name} supported by {len(recent_errors)} repeated incorrect attempts."

        inference = GapInference(
            concept_id=canonical_concept,
            confidence=round(confidence, 2),
            status=status,
            supporting_evidence_count=len(recent_errors),
            description=desc,
        )
        state.gap_inferences[canonical_concept] = inference.to_dict()

        # 5. Adaptive Routing Selection
        if evidence.activity_id in MVP_ACTIVITIES:
            activity = get_activity(evidence.activity_id)

            if evidence.is_correct:
                if activity.next_activity_id:
                    next_act = get_activity(activity.next_activity_id)
                    return AdaptiveRecommendation(
                        action="advance",
                        target=activity.next_activity_id,
                        reason=f"Learner demonstrated correct understanding in '{activity.title}'. Ready to advance to '{next_act.title}'.",
                        concept_id=canonical_concept,
                    )
                return AdaptiveRecommendation(
                    action="advance",
                    target=None,
                    reason=f"Learner demonstrated correct understanding in '{activity.title}' (end of activity sequence).",
                    concept_id=canonical_concept,
                )

            # Not correct:
            if len(recent_errors) == 1:
                # Case B: Single error -> gather more evidence
                return AdaptiveRecommendation(
                    action="gather_evidence",
                    target=activity.activity_id,
                    reason=f"Initial prediction mismatch on '{activity.title}'. Gathering additional evidence before selecting remediation.",
                    concept_id=canonical_concept,
                )

            # Case C: Repeated errors (>= 2) -> targeted remediation
            if activity.remediation_activity_id:
                remed_act = get_activity(activity.remediation_activity_id)
                return AdaptiveRecommendation(
                    action="targeted_remediation",
                    target=activity.remediation_activity_id,
                    reason=f"Repeated prediction errors provide evidence consistent with possible difficulty in {display_name}. Recommending targeted remediation in '{remed_act.title}'.",
                    concept_id=canonical_concept,
                )

            return AdaptiveRecommendation(
                action="targeted_remediation",
                target=activity.activity_id,
                reason=f"Repeated errors provide evidence consistent with possible difficulty in {display_name}. Reviewing current concept.",
                concept_id=canonical_concept,
            )

        # Fallback to general topic routing if activity is not registered
        if display_name in self.graph:
            return self.recommend_next(display_name, state)

        return AdaptiveRecommendation(
            action="reinforce_current_concept",
            target=display_name,
            reason=f"Recorded evidence for {display_name}.",
            concept_id=canonical_concept,
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
        attempts, errors, gap inferences, and current recommendation.
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
            gap_inferences=dict(state.gap_inferences),
            current_concept=current_topic,
            recommendation=rec,
        )
