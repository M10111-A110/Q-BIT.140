# Explanation: `backend/adaptive/engine.py`

## Purpose

This page explains the meaningful behavior in `backend/adaptive/engine.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
from __future__ import annotations

import time
from typing import Any, Optional

from .activities import MVP_ACTIVITIES, get_activities_for_concept, get_activity
from .concepts import (
    CONCEPT_GRAPH,
    get_concept,
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
    Implements a strict 4-tier separation:
      1. Observed Performance (LearnerEvidence from latest attempt)
      2. Accumulated Evidence (evidence_history, score trajectories, attempts)
      3. Inferred Learner State (continuous mastery scores, calibrated GapInferences)
      4. Adaptive Decisions (explainable, deterministic next pedagogical actions)
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
        [TIER 3: INFERRED CONTINUOUS MASTERY]
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

    def find_unmastered_prerequisite(
        self,
        concept_id: str,
        state: LearnerState,
    ) -> Optional[str]:
        """
        [TIER 3: PREREQUISITE BOTTLENECK INFERENCE]
        Traverse concept dependencies (via concept DAG or registered activities)
        to find the earliest unsatisfied prerequisite with active errors or low mastery.
        Returns the canonical concept ID of the unmastered prerequisite, or None.
        """
        canonical = resolve_concept_id(concept_id)
        prereqs: list[str] = []

        concept_obj = get_concept(canonical)
        if concept_obj and concept_obj.prerequisites:
            prereqs.extend(concept_obj.prerequisites)

        # Also inspect prerequisite links from mapped activities
        activities = get_activities_for_concept(canonical)
        for act in activities:
            for p in act.prerequisites:
                if p not in prereqs:
                    prereqs.append(p)

        # Priority 1: Check if any prerequisite has explicit active errors
        for prereq_id in prereqs:
            prereq_canonical = resolve_concept_id(prereq_id)
            prereq_name = get_concept_display_name(prereq_canonical)
            if len(state.errors.get(prereq_name, [])) > 0:
                return prereq_canonical

        # Priority 2: Check if any prerequisite has low mastery
        for prereq_id in prereqs:
            prereq_canonical = resolve_concept_id(prereq_id)
            prereq_name = get_concept_display_name(prereq_canonical)
            prereq_mastery = self.compute_mastery(prereq_name, state)
            if prereq_name in state.concept_scores and prereq_mastery < self.threshold:
                return prereq_canonical

        return None

    def recommend_next(self, topic: str, state: LearnerState) -> AdaptiveRecommendation:
        """
        [TIER 4: GENERAL TOPIC ROUTING]
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

        canonical = resolve_concept_id(topic)

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
                    confidence=0.85,
                    trigger="prerequisite_mastery_check",
                    evidence_sufficiency="sufficient_for_targeted_inference",
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
                concept_id=canonical,
                confidence=0.90,
                trigger="repeated_concept_error_streak",
                evidence_sufficiency="sufficient_for_targeted_inference",
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
                concept_id=canonical,
                confidence=0.0,
                trigger="mastery_threshold_passed",
                evidence_sufficiency="sufficient_for_mastery",
            )

        # 4. Default: not mastered yet, no glaring error pattern -> reinforce
        return AdaptiveRecommendation(
            action="reinforce_current_concept",
            target=topic,
            reason=(
                f"{topic} mastery is {mastery} (< {self.threshold}) — "
                f"needs more practice before moving on."
            ),
            concept_id=canonical,
            confidence=0.35,
            trigger="reinforce_baseline",
            evidence_sufficiency="insufficient",
        )

    def record_evidence(
        self,
        evidence: LearnerEvidence | dict[str, Any],
        state: LearnerState,
    ) -> AdaptiveRecommendation:
        """
        Closed evidence-driven loop executing the 4-tier semantic flow:
          Tier 1: Ingest empirical LearnerEvidence (Observed Performance of latest attempt)
          Tier 2: Accumulate into persistent LearnerState (history trajectories)
          Tier 3: Derive deterministic GapInference (Inferred cognitive state without false certainty)
          Tier 4: Return explainable AdaptiveRecommendation (Next pedagogical action)
        """
        if isinstance(evidence, dict):
            evidence = LearnerEvidence.from_dict(evidence)

        canonical_concept = resolve_concept_id(evidence.concept_id)
        display_name = get_concept_display_name(canonical_concept)
        concept_tag = canonical_concept.replace(".", "_")

        # ===================================================================
        # TIER 2: ACCUMULATED EVIDENCE UPDATE
        # ===================================================================
        # 1. Append structured empirical observation to immutable history
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
            # If successful after prior errors, clear active unresolved error list for this concept
            if display_name in state.errors and len(state.errors[display_name]) > 0:
                state.errors[display_name] = []

        # ===================================================================
        # TIER 3: DETERMINISTIC GAP INFERENCE & TRAJECTORY CLASSIFICATION
        # ===================================================================
        concept_evidence = [
            e for e in state.evidence_history
            if resolve_concept_id(e.get("concept_id", "")) == canonical_concept
        ]
        recent = concept_evidence[-5:]
        recent_errors = [e for e in recent if not e.get("is_correct", False)]
        recent_successes = [e for e in recent if e.get("is_correct", False)]

        prereq_gap: Optional[str] = None
        supporting_evidence_ids: list[str] = []
        hypothesis: str = "unassessed"
        evidence_sufficiency: str = "insufficient"
        trigger: str = "default_routing"

        if len(recent) >= 2 and recent[-1].get("is_correct", False) and recent[-2].get("is_correct", False):
            # 2 consecutive recent successes -> stable mastery
            confidence = 0.0
            status = "mastered"
            trend = "stable_mastery"
            hypothesis = f"consistent_mastery_in_{concept_tag}"
            evidence_sufficiency = "sufficient_for_mastery"
            supporting_evidence_ids = [e.get("evidence_id", "") for e in [recent[-2], recent[-1]] if e.get("evidence_id")]
            trigger = "consecutive_mastery_success"
            desc = f"Evidence demonstrates consistent understanding of {display_name} across multiple attempts."
        elif len(recent_errors) == 0 and len(recent_successes) >= 1:
            # 1 initial success -> observed mastery
            confidence = 0.0
            status = "mastered"
            trend = "mastered"
            hypothesis = f"demonstrated_understanding_in_{concept_tag}"
            evidence_sufficiency = "sufficient_for_observation"
            supporting_evidence_ids = [e.get("evidence_id", "") for e in [recent[-1]] if e.get("evidence_id")]
            trigger = "correct_prediction_advancement"
            desc = f"Evidence demonstrates consistent understanding of {display_name}."
        elif evidence.is_correct and len(concept_evidence) >= 2 and not concept_evidence[-2].get("is_correct", False):
            # Success after error -> post-intervention improvement
            confidence = 0.15
            status = "improving"
            trend = "improving"
            hypothesis = f"post_intervention_improvement_in_{concept_tag}"
            evidence_sufficiency = "sufficient_for_improvement_observation"
            supporting_evidence_ids = [e.get("evidence_id", "") for e in [concept_evidence[-2], concept_evidence[-1]] if e.get("evidence_id")]
            trigger = "post_intervention_recovery"
            desc = f"Evidence indicates post-intervention improvement in {display_name}."
        elif len(recent_errors) == 1:
            # Single error -> low confidence, no false certainty of misconception
            confidence = 0.35
            status = "observing"
            trend = "preliminary_observation"
            hypothesis = f"preliminary_difficulty_observation_in_{concept_tag}"
            evidence_sufficiency = "insufficient"
            supporting_evidence_ids = [e.get("evidence_id", "") for e in [recent_errors[-1]] if e.get("evidence_id")]
            trigger = "single_prediction_mismatch"
            desc = f"Evidence is consistent with possible difficulty in {display_name} (preliminary observation from 1 incorrect attempt)."
        else:
            # 2 or more recent errors -> persistent difficulty
            confidence = min(0.40 + len(recent_errors) * 0.25, 0.90)
            status = "remediation_needed"
            trend = "persistent_difficulty"
            prereq_gap = self.find_unmastered_prerequisite(canonical_concept, state)
            hypothesis = f"possible_{concept_tag}_difficulty"
            evidence_sufficiency = "sufficient_for_targeted_inference"
            supporting_evidence_ids = [e.get("evidence_id", "") for e in recent_errors if e.get("evidence_id")]
            trigger = "prerequisite_bottleneck_error" if prereq_gap else "repeated_prediction_error"
            desc = f"Evidence is consistent with possible difficulty in {display_name} supported by {len(recent_errors)} repeated incorrect attempts."

        inference = GapInference(
            concept_id=canonical_concept,
            confidence=round(confidence, 2),
            status=status,
            supporting_evidence_count=len(recent_errors),
            description=desc,
            trend=trend,
            prerequisite_concept_id=prereq_gap,
            hypothesis=hypothesis,
            supporting_evidence_ids=supporting_evidence_ids,
            evidence_sufficiency=evidence_sufficiency,
        )
        state.gap_inferences[canonical_concept] = inference.to_dict()

        # ===================================================================
        # TIER 4: DETERMINISTIC ADAPTIVE DECISION
        # ===================================================================
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
                        confidence=round(confidence, 2),
                        supporting_evidence_ids=supporting_evidence_ids,
                        trigger=trigger,
                        evidence_sufficiency=evidence_sufficiency,
                    )
                return AdaptiveRecommendation(
                    action="advance",
                    target=None,
                    reason=f"Learner demonstrated correct understanding in '{activity.title}' (end of activity sequence).",
                    concept_id=canonical_concept,
                    confidence=round(confidence, 2),
                    supporting_evidence_ids=supporting_evidence_ids,
                    trigger=trigger,
                    evidence_sufficiency=evidence_sufficiency,
                )

            # Not correct:
            if len(recent_errors) == 1:
                # Case B: Single error -> gather more evidence
                return AdaptiveRecommendation(
                    action="gather_evidence",
                    target=activity.activity_id,
                    reason=f"Initial prediction mismatch on '{activity.title}'. Gathering additional evidence before selecting remediation.",
                    concept_id=canonical_concept,
                    confidence=0.35,
                    supporting_evidence_ids=supporting_evidence_ids,
                    trigger="single_prediction_mismatch",
                    evidence_sufficiency="insufficient",
                )

            # Case C: Repeated errors (>= 2) -> targeted remediation
            # Default to activity's configured remediation
            remediation_target = activity.remediation_activity_id

            # If an explicit prerequisite gap was identified with active errors, route to that prerequisite
            if prereq_gap:
                prereq_name = get_concept_display_name(prereq_gap)
                if len(state.errors.get(prereq_name, [])) > 0:
                    prereq_activities = get_activities_for_concept(prereq_gap)
                    if prereq_activities:
                        remediation_target = prereq_activities[0].activity_id

            if remediation_target and remediation_target in MVP_ACTIVITIES:
                remed_act = get_activity(remediation_target)
                return AdaptiveRecommendation(
                    action="targeted_remediation",
                    target=remediation_target,
                    reason=f"Repeated prediction errors provide evidence consistent with possible difficulty in {display_name}. Recommending targeted remediation in '{remed_act.title}'.",
                    concept_id=canonical_concept,
                    confidence=round(confidence, 2),
                    supporting_evidence_ids=supporting_evidence_ids,
                    trigger=trigger,
                    evidence_sufficiency=evidence_sufficiency,
                )

            return AdaptiveRecommendation(
                action="targeted_remediation",
                target=activity.activity_id,
                reason=f"Repeated errors provide evidence consistent with possible difficulty in {display_name}. Reviewing current concept.",
                concept_id=canonical_concept,
                confidence=round(confidence, 2),
                supporting_evidence_ids=supporting_evidence_ids,
                trigger=trigger,
                evidence_sufficiency=evidence_sufficiency,
            )

        # Fallback to general topic routing if activity is not registered
        if display_name in self.graph:
            return self.recommend_next(display_name, state)

        return AdaptiveRecommendation(
            action="reinforce_current_concept",
            target=display_name,
            reason=f"Recorded evidence for {display_name}.",
            concept_id=canonical_concept,
            confidence=round(confidence, 2),
            supporting_evidence_ids=supporting_evidence_ids,
            trigger=trigger,
            evidence_sufficiency=evidence_sufficiency,
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
        [TIER 3: DOMAIN-LEVEL COGNITIVE STATE SNAPSHOT]
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

```

## Line Notes

### Line 1

`from __future__ import annotations`

Imports a dependency or project symbol so later code can use it by name.
### Line 2

`(blank)`

Blank line used to separate nearby statements.
### Line 3

`import time`

Imports a dependency or project symbol so later code can use it by name.
### Line 4

`from typing import Any, Optional`

Imports a dependency or project symbol so later code can use it by name.
### Line 5

`(blank)`

Blank line used to separate nearby statements.
### Line 6

`from .activities import MVP_ACTIVITIES, get_activities_for_concept, get_activity`

Imports a dependency or project symbol so later code can use it by name.
### Line 7

`from .concepts import (`

Imports a dependency or project symbol so later code can use it by name.
### Line 8

`CONCEPT_GRAPH,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 9

`get_concept,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 10

`get_concept_display_name,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 11

`resolve_concept_id,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 12

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 13

`from .evidence import GapInference, LearnerEvidence`

Imports a dependency or project symbol so later code can use it by name.
### Line 14

`from .models import (`

Imports a dependency or project symbol so later code can use it by name.
### Line 15

`AdaptiveRecommendation,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 16

`LearnerContext,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 17

`LearnerState,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 18

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 19

`(blank)`

Blank line used to separate nearby statements.
### Line 20

`MASTERY_THRESHOLD: float = 0.6  # Score below which concept counts as not mastered`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 21

`ERROR_STREAK_LIMIT: int = 2     # Consecutive errors triggering targeted review`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 22

`(blank)`

Blank line used to separate nearby statements.
### Line 24

`class LearnerModel:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 25

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 26

`Cognitive mastery model and adaptive decision engine.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 27

`Implements a strict 4-tier separation:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 28

`1. Observed Performance (LearnerEvidence from latest attempt)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 29

`2. Accumulated Evidence (evidence_history, score trajectories, attempts)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 30

`3. Inferred Learner State (continuous mastery scores, calibrated GapInferences)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 31

`4. Adaptive Decisions (explainable, deterministic next pedagogical actions)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 32

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 33

`(blank)`

Blank line used to separate nearby statements.
### Line 34

`def __init__(`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 35

`self,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 36

`concept_graph: Optional[dict] = None,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 37

`threshold: float = MASTERY_THRESHOLD,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 38

`) -> None:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 39

`self.graph = concept_graph if concept_graph is not None else CONCEPT_GRAPH`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 40

`self.threshold = threshold`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 41

`(blank)`

Blank line used to separate nearby statements.
### Line 42

`def compute_mastery(self, topic: str, state: LearnerState) -> float:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 43

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 44

`[TIER 3: INFERRED CONTINUOUS MASTERY]`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 45

`Compute transparent mastery score for a topic given learner history:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 46

`mastery = diagnostic_score + improvement_bonus - error_penalty`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 47

`Clamped within [0.0, 1.0] and rounded to 3 decimal places.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 48

`Preserves exact original M2 mathematical behavior.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 49

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 50

`diag_score = state.concept_scores.get(topic, 0.0)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 51

`(blank)`

Blank line used to separate nearby statements.
### Line 52

`history = state.score_history.get(topic, [])`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 53

`improvement = 0.0`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 54

`if len(history) >= 2:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 55

`improvement = max(0.0, history[-1] - history[-2]) * 0.2  # up to +0.2 bonus`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 56

`(blank)`

Blank line used to separate nearby statements.
### Line 57

`error_count = len(state.errors.get(topic, []))`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 58

`error_penalty = min(error_count * 0.05, 0.3)  # capped at 0.3`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 59

`(blank)`

Blank line used to separate nearby statements.
### Line 60

`mastery = diag_score + improvement - error_penalty`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 61

`return round(max(0.0, min(1.0, mastery)), 3)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 62

`(blank)`

Blank line used to separate nearby statements.
### Line 63

`def find_unmastered_prerequisite(`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 64

`self,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 65

`concept_id: str,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 66

`state: LearnerState,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 67

`) -> Optional[str]:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 68

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 69

`[TIER 3: PREREQUISITE BOTTLENECK INFERENCE]`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 70

`Traverse concept dependencies (via concept DAG or registered activities)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 71

`to find the earliest unsatisfied prerequisite with active errors or low mastery.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 72

`Returns the canonical concept ID of the unmastered prerequisite, or None.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 73

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 74

`canonical = resolve_concept_id(concept_id)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 75

`prereqs: list[str] = []`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 76

`(blank)`

Blank line used to separate nearby statements.
### Line 77

`concept_obj = get_concept(canonical)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 78

`if concept_obj and concept_obj.prerequisites:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 79

`prereqs.extend(concept_obj.prerequisites)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 80

`(blank)`

Blank line used to separate nearby statements.
### Line 81

`# Also inspect prerequisite links from mapped activities`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 82

`activities = get_activities_for_concept(canonical)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 83

`for act in activities:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 84

`for p in act.prerequisites:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 85

`if p not in prereqs:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 86

`prereqs.append(p)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 87

`(blank)`

Blank line used to separate nearby statements.
### Line 88

`# Priority 1: Check if any prerequisite has explicit active errors`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 89

`for prereq_id in prereqs:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 90

`prereq_canonical = resolve_concept_id(prereq_id)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 91

`prereq_name = get_concept_display_name(prereq_canonical)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 92

`if len(state.errors.get(prereq_name, [])) > 0:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 93

`return prereq_canonical`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 94

`(blank)`

Blank line used to separate nearby statements.
### Line 95

`# Priority 2: Check if any prerequisite has low mastery`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 96

`for prereq_id in prereqs:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 97

`prereq_canonical = resolve_concept_id(prereq_id)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 98

`prereq_name = get_concept_display_name(prereq_canonical)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 99

`prereq_mastery = self.compute_mastery(prereq_name, state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 100

`if prereq_name in state.concept_scores and prereq_mastery < self.threshold:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 101

`return prereq_canonical`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 102

`(blank)`

Blank line used to separate nearby statements.
### Line 103

`return None`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 104

`(blank)`

Blank line used to separate nearby statements.
### Line 105

`def recommend_next(self, topic: str, state: LearnerState) -> AdaptiveRecommendation:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 106

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 107

`[TIER 4: GENERAL TOPIC ROUTING]`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 108

`Determine the next pedagogical recommendation for the learner given their state.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 109

`Evaluation order:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 110

`1. Prerequisite mastery check`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 111

`2. Error streak check -> targeted review`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 112

`3. Mastery pass check -> advance to dependent concepts`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 113

`4. Default -> reinforce current concept`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 114

`(blank)`

Blank line used to separate nearby statements.
### Line 115

`Preserves exact original M2 routing logic and explanations.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 116

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 117

`if topic not in self.graph:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 118

`raise KeyError(f"Unknown topic '{topic}'. Known graph topics: {list(self.graph.keys())}")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 119

`(blank)`

Blank line used to separate nearby statements.
### Line 120

`canonical = resolve_concept_id(topic)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 121

`(blank)`

Blank line used to separate nearby statements.
### Line 122

`# 1. Prerequisite verification`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 123

`for prereq in self.graph[topic]["prereqs"]:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 124

`prereq_mastery = self.compute_mastery(prereq, state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 125

`if prereq_mastery < self.threshold:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 126

`return AdaptiveRecommendation(`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 127

`action="recommend_prerequisite",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 128

`target=prereq,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 129

`reason=(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 130

`f"{prereq} mastery is {prereq_mastery} (< {self.threshold}), "`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 131

`f"so {topic} isn't safe to build on yet."`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 132

`),`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 133

`concept_id=resolve_concept_id(prereq),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 134

`confidence=0.85,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 135

`trigger="prerequisite_mastery_check",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 136

`evidence_sufficiency="sufficient_for_targeted_inference",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 137

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 138

`(blank)`

Blank line used to separate nearby statements.
### Line 139

`mastery = self.compute_mastery(topic, state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 140

`error_count = len(state.errors.get(topic, []))`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 141

`(blank)`

Blank line used to separate nearby statements.
### Line 142

`# 2. Repeated errors on this exact concept -> targeted review`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 143

`if error_count >= ERROR_STREAK_LIMIT and mastery < self.threshold:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 144

`return AdaptiveRecommendation(`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 145

`action="recommend_targeted_review",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 146

`target=topic,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 147

`reason=(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 148

`f"{error_count} wrong answers on {topic} and mastery is only "`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 149

`f"{mastery} — needs focused review, not just repetition."`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 150

`),`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 151

`concept_id=canonical,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 152

`confidence=0.90,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 153

`trigger="repeated_concept_error_streak",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 154

`evidence_sufficiency="sufficient_for_targeted_inference",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 155

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 156

`(blank)`

Blank line used to separate nearby statements.
### Line 157

`# 3. Mastered -> unlock dependent concepts`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 158

`if mastery >= self.threshold:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 159

`next_topics = [c for c, v in self.graph.items() if topic in v["prereqs"]]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 160

`target = next_topics if next_topics else None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 161

`next_str = f" to {', '.join(next_topics)}" if next_topics else " (end of chain)"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 162

`return AdaptiveRecommendation(`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 163

`action="advance",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 164

`target=target,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 165

`reason=f"{topic} mastery is {mastery} (>= {self.threshold}) — ready to move on{next_str}.",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 166

`concept_id=canonical,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 167

`confidence=0.0,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 168

`trigger="mastery_threshold_passed",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 169

`evidence_sufficiency="sufficient_for_mastery",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 170

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 171

`(blank)`

Blank line used to separate nearby statements.
### Line 172

`# 4. Default: not mastered yet, no glaring error pattern -> reinforce`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 173

`return AdaptiveRecommendation(`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 174

`action="reinforce_current_concept",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 175

`target=topic,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 176

`reason=(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 177

`f"{topic} mastery is {mastery} (< {self.threshold}) — "`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 178

`f"needs more practice before moving on."`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 179

`),`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 180

`concept_id=canonical,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 181

`confidence=0.35,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 182

`trigger="reinforce_baseline",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 183

`evidence_sufficiency="insufficient",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 184

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 185

`(blank)`

Blank line used to separate nearby statements.
### Line 186

`def record_evidence(`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 187

`self,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 188

`evidence: LearnerEvidence | dict[str, Any],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 189

`state: LearnerState,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 190

`) -> AdaptiveRecommendation:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 191

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 192

`Closed evidence-driven loop executing the 4-tier semantic flow:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 193

`Tier 1: Ingest empirical LearnerEvidence (Observed Performance of latest attempt)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 194

`Tier 2: Accumulate into persistent LearnerState (history trajectories)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 195

`Tier 3: Derive deterministic GapInference (Inferred cognitive state without false certainty)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 196

`Tier 4: Return explainable AdaptiveRecommendation (Next pedagogical action)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 197

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 198

`if isinstance(evidence, dict):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 199

`evidence = LearnerEvidence.from_dict(evidence)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 200

`(blank)`

Blank line used to separate nearby statements.
### Line 201

`canonical_concept = resolve_concept_id(evidence.concept_id)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 202

`display_name = get_concept_display_name(canonical_concept)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 203

`concept_tag = canonical_concept.replace(".", "_")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 204

`(blank)`

Blank line used to separate nearby statements.
### Line 205

`# ===================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 206

`# TIER 2: ACCUMULATED EVIDENCE UPDATE`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 207

`# ===================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 208

`# 1. Append structured empirical observation to immutable history`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 209

`state.evidence_history.append(evidence.to_dict())`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 210

`(blank)`

Blank line used to separate nearby statements.
### Line 211

`# 2. Update basic state counters`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 212

`state.attempts[display_name] = state.attempts.get(display_name, 0) + 1`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 213

`state.last_updated[display_name] = time.time()`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 214

`(blank)`

Blank line used to separate nearby statements.
### Line 215

`# 3. Update score trajectory based on outcome`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 216

`attempt_score = 1.0 if evidence.is_correct else 0.0`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 217

`state.concept_scores[display_name] = attempt_score`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 218

`state.score_history.setdefault(display_name, []).append(attempt_score)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 219

`(blank)`

Blank line used to separate nearby statements.
### Line 220

`if not evidence.is_correct:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 221

`err_repr = str(evidence.learner_response)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 222

`state.errors.setdefault(display_name, []).append(err_repr)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 223

`else:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 224

`# If successful after prior errors, clear active unresolved error list for this concept`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 225

`if display_name in state.errors and len(state.errors[display_name]) > 0:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 226

`state.errors[display_name] = []`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 227

`(blank)`

Blank line used to separate nearby statements.
### Line 228

`# ===================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 229

`# TIER 3: DETERMINISTIC GAP INFERENCE & TRAJECTORY CLASSIFICATION`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 230

`# ===================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 231

`concept_evidence = [`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 232

`e for e in state.evidence_history`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 233

`if resolve_concept_id(e.get("concept_id", "")) == canonical_concept`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 234

`]`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 235

`recent = concept_evidence[-5:]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 236

`recent_errors = [e for e in recent if not e.get("is_correct", False)]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 237

`recent_successes = [e for e in recent if e.get("is_correct", False)]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 238

`(blank)`

Blank line used to separate nearby statements.
### Line 239

`prereq_gap: Optional[str] = None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 240

`supporting_evidence_ids: list[str] = []`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 241

`hypothesis: str = "unassessed"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 242

`evidence_sufficiency: str = "insufficient"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 243

`trigger: str = "default_routing"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 244

`(blank)`

Blank line used to separate nearby statements.
### Line 245

`if len(recent) >= 2 and recent[-1].get("is_correct", False) and recent[-2].get("is_correct", False):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 246

`# 2 consecutive recent successes -> stable mastery`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 247

`confidence = 0.0`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 248

`status = "mastered"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 249

`trend = "stable_mastery"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 250

`hypothesis = f"consistent_mastery_in_{concept_tag}"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 251

`evidence_sufficiency = "sufficient_for_mastery"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 252

`supporting_evidence_ids = [e.get("evidence_id", "") for e in [recent[-2], recent[-1]] if e.get("evidence_id")]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 253

`trigger = "consecutive_mastery_success"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 254

`desc = f"Evidence demonstrates consistent understanding of {display_name} across multiple attempts."`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 255

`elif len(recent_errors) == 0 and len(recent_successes) >= 1:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 256

`# 1 initial success -> observed mastery`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 257

`confidence = 0.0`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 258

`status = "mastered"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 259

`trend = "mastered"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 260

`hypothesis = f"demonstrated_understanding_in_{concept_tag}"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 261

`evidence_sufficiency = "sufficient_for_observation"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 262

`supporting_evidence_ids = [e.get("evidence_id", "") for e in [recent[-1]] if e.get("evidence_id")]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 263

`trigger = "correct_prediction_advancement"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 264

`desc = f"Evidence demonstrates consistent understanding of {display_name}."`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 265

`elif evidence.is_correct and len(concept_evidence) >= 2 and not concept_evidence[-2].get("is_correct", False):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 266

`# Success after error -> post-intervention improvement`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 267

`confidence = 0.15`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 268

`status = "improving"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 269

`trend = "improving"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 270

`hypothesis = f"post_intervention_improvement_in_{concept_tag}"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 271

`evidence_sufficiency = "sufficient_for_improvement_observation"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 272

`supporting_evidence_ids = [e.get("evidence_id", "") for e in [concept_evidence[-2], concept_evidence[-1]] if e.get("evidence_id")]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 273

`trigger = "post_intervention_recovery"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 274

`desc = f"Evidence indicates post-intervention improvement in {display_name}."`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 275

`elif len(recent_errors) == 1:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 276

`# Single error -> low confidence, no false certainty of misconception`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 277

`confidence = 0.35`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 278

`status = "observing"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 279

`trend = "preliminary_observation"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 280

`hypothesis = f"preliminary_difficulty_observation_in_{concept_tag}"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 281

`evidence_sufficiency = "insufficient"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 282

`supporting_evidence_ids = [e.get("evidence_id", "") for e in [recent_errors[-1]] if e.get("evidence_id")]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 283

`trigger = "single_prediction_mismatch"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 284

`desc = f"Evidence is consistent with possible difficulty in {display_name} (preliminary observation from 1 incorrect attempt)."`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 285

`else:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 286

`# 2 or more recent errors -> persistent difficulty`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 287

`confidence = min(0.40 + len(recent_errors) * 0.25, 0.90)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 288

`status = "remediation_needed"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 289

`trend = "persistent_difficulty"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 290

`prereq_gap = self.find_unmastered_prerequisite(canonical_concept, state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 291

`hypothesis = f"possible_{concept_tag}_difficulty"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 292

`evidence_sufficiency = "sufficient_for_targeted_inference"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 293

`supporting_evidence_ids = [e.get("evidence_id", "") for e in recent_errors if e.get("evidence_id")]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 294

`trigger = "prerequisite_bottleneck_error" if prereq_gap else "repeated_prediction_error"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 295

`desc = f"Evidence is consistent with possible difficulty in {display_name} supported by {len(recent_errors)} repeated incorrect attempts."`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 296

`(blank)`

Blank line used to separate nearby statements.
### Line 297

`inference = GapInference(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 298

`concept_id=canonical_concept,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 299

`confidence=round(confidence, 2),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 300

`status=status,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 301

`supporting_evidence_count=len(recent_errors),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 302

`description=desc,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 303

`trend=trend,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 304

`prerequisite_concept_id=prereq_gap,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 305

`hypothesis=hypothesis,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 306

`supporting_evidence_ids=supporting_evidence_ids,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 307

`evidence_sufficiency=evidence_sufficiency,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 308

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 309

`state.gap_inferences[canonical_concept] = inference.to_dict()`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 310

`(blank)`

Blank line used to separate nearby statements.
### Line 311

`# ===================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 312

`# TIER 4: DETERMINISTIC ADAPTIVE DECISION`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 313

`# ===================================================================`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 314

`if evidence.activity_id in MVP_ACTIVITIES:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 315

`activity = get_activity(evidence.activity_id)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 316

`(blank)`

Blank line used to separate nearby statements.
### Line 317

`if evidence.is_correct:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 318

`if activity.next_activity_id:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 319

`next_act = get_activity(activity.next_activity_id)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 320

`return AdaptiveRecommendation(`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 321

`action="advance",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 322

`target=activity.next_activity_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 323

`reason=f"Learner demonstrated correct understanding in '{activity.title}'. Ready to advance to '{next_act.title}'.",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 324

`concept_id=canonical_concept,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 325

`confidence=round(confidence, 2),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 326

`supporting_evidence_ids=supporting_evidence_ids,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 327

`trigger=trigger,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 328

`evidence_sufficiency=evidence_sufficiency,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 329

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 330

`return AdaptiveRecommendation(`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 331

`action="advance",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 332

`target=None,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 333

`reason=f"Learner demonstrated correct understanding in '{activity.title}' (end of activity sequence).",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 334

`concept_id=canonical_concept,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 335

`confidence=round(confidence, 2),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 336

`supporting_evidence_ids=supporting_evidence_ids,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 337

`trigger=trigger,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 338

`evidence_sufficiency=evidence_sufficiency,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 339

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 340

`(blank)`

Blank line used to separate nearby statements.
### Line 341

`# Not correct:`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 342

`if len(recent_errors) == 1:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 343

`# Case B: Single error -> gather more evidence`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 344

`return AdaptiveRecommendation(`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 345

`action="gather_evidence",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 346

`target=activity.activity_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 347

`reason=f"Initial prediction mismatch on '{activity.title}'. Gathering additional evidence before selecting remediation.",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 348

`concept_id=canonical_concept,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 349

`confidence=0.35,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 350

`supporting_evidence_ids=supporting_evidence_ids,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 351

`trigger="single_prediction_mismatch",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 352

`evidence_sufficiency="insufficient",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 353

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 354

`(blank)`

Blank line used to separate nearby statements.
### Line 355

`# Case C: Repeated errors (>= 2) -> targeted remediation`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 356

`# Default to activity's configured remediation`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 357

`remediation_target = activity.remediation_activity_id`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 358

`(blank)`

Blank line used to separate nearby statements.
### Line 359

`# If an explicit prerequisite gap was identified with active errors, route to that prerequisite`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 360

`if prereq_gap:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 361

`prereq_name = get_concept_display_name(prereq_gap)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 362

`if len(state.errors.get(prereq_name, [])) > 0:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 363

`prereq_activities = get_activities_for_concept(prereq_gap)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 364

`if prereq_activities:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 365

`remediation_target = prereq_activities[0].activity_id`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 366

`(blank)`

Blank line used to separate nearby statements.
### Line 367

`if remediation_target and remediation_target in MVP_ACTIVITIES:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 368

`remed_act = get_activity(remediation_target)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 369

`return AdaptiveRecommendation(`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 370

`action="targeted_remediation",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 371

`target=remediation_target,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 372

`reason=f"Repeated prediction errors provide evidence consistent with possible difficulty in {display_name}. Recommending targeted remediation in '{remed_act.title}'.",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 373

`concept_id=canonical_concept,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 374

`confidence=round(confidence, 2),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 375

`supporting_evidence_ids=supporting_evidence_ids,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 376

`trigger=trigger,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 377

`evidence_sufficiency=evidence_sufficiency,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 378

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 379

`(blank)`

Blank line used to separate nearby statements.
### Line 380

`return AdaptiveRecommendation(`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 381

`action="targeted_remediation",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 382

`target=activity.activity_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 383

`reason=f"Repeated errors provide evidence consistent with possible difficulty in {display_name}. Reviewing current concept.",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 384

`concept_id=canonical_concept,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 385

`confidence=round(confidence, 2),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 386

`supporting_evidence_ids=supporting_evidence_ids,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 387

`trigger=trigger,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 388

`evidence_sufficiency=evidence_sufficiency,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 389

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 390

`(blank)`

Blank line used to separate nearby statements.
### Line 391

`# Fallback to general topic routing if activity is not registered`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 392

`if display_name in self.graph:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 393

`return self.recommend_next(display_name, state)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 394

`(blank)`

Blank line used to separate nearby statements.
### Line 395

`return AdaptiveRecommendation(`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 396

`action="reinforce_current_concept",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 397

`target=display_name,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 398

`reason=f"Recorded evidence for {display_name}.",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 399

`concept_id=canonical_concept,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 400

`confidence=round(confidence, 2),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 401

`supporting_evidence_ids=supporting_evidence_ids,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 402

`trigger=trigger,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 403

`evidence_sufficiency=evidence_sufficiency,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 404

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 405

`(blank)`

Blank line used to separate nearby statements.
### Line 406

`def get_mastery_profile(self, state: LearnerState) -> dict[str, float]:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 407

`"""Compute mastery for all concepts in the DAG."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 408

`return {`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 409

`topic: self.compute_mastery(topic, state)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 410

`for topic in self.graph`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 411

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 412

`(blank)`

Blank line used to separate nearby statements.
### Line 413

`def get_learner_context(`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 414

`self,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 415

`state: LearnerState,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 416

`current_topic: Optional[str] = None,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 417

`) -> LearnerContext:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 418

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 419

`[TIER 3: DOMAIN-LEVEL COGNITIVE STATE SNAPSHOT]`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 420

`Build a complete LearnerContext domain snapshot summarizing mastery,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 421

`attempts, errors, gap inferences, and current recommendation.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 422

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 423

`mastery_by_canonical = {`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 424

`resolve_concept_id(topic): self.compute_mastery(topic, state)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 425

`for topic in self.graph`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 426

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 427

`(blank)`

Blank line used to separate nearby statements.
### Line 428

`rec = None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 429

`if current_topic and current_topic in self.graph:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 430

`rec = self.recommend_next(current_topic, state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 431

`(blank)`

Blank line used to separate nearby statements.
### Line 432

`return LearnerContext(`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 433

`user_id=state.user_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 434

`concept_mastery=mastery_by_canonical,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 435

`concept_scores=dict(state.concept_scores),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 436

`attempts=dict(state.attempts),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 437

`errors=dict(state.errors),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 438

`score_history=dict(state.score_history),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 439

`gap_inferences=dict(state.gap_inferences),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 440

`current_concept=current_topic,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 441

`recommendation=rec,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 442

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.

## Nearby Files

[backend/adaptive/__init__.py](__init__.py.md), [backend/adaptive/activities.py](activities.py.md), [backend/adaptive/concepts.py](concepts.py.md), [backend/adaptive/diagnostics.py](diagnostics.py.md), [backend/adaptive/evidence.py](evidence.py.md), [backend/adaptive/models.py](models.py.md), [backend/adaptive/repository.py](repository.py.md)
