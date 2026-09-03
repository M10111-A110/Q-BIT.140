from __future__ import annotations

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status

from backend.adaptive import (
    LearnerEvidence,
    LearnerModel,
    LearnerRepository,
    PersistenceError,
    evaluate_conceptual_response,
    evaluate_quantum_prediction,
    get_activity,
    list_activities,
)
from backend.adaptive.diagnostics import Diagnostic
from backend.quantum import QuantumExperiment, run_experiment

from ..dependencies import get_learner_model, get_learner_repository
from ..schemas import (
    ActivityDetailResponse,
    ActivitySummary,
    DiagnosticQuestionItem,
    DiagnosticQuestionResult,
    DiagnosticReadinessResponse,
    DiagnosticSubmitRequest,
    DiagnosticSubmitResponse,
    LearnerStateResponse,
    SubmissionRequest,
    SubmissionResponse,
)

router = APIRouter(tags=["activities"])



@router.get("/activities", response_model=list[ActivitySummary])
def get_all_activities() -> list[ActivitySummary]:
    """List all registered MVP activities."""
    activities = list_activities()
    return [
        ActivitySummary(
            activity_id=act.activity_id,
            concept_id=act.concept_id,
            title=act.title,
            description=act.description,
            task_type=act.task_type,
            prerequisites=act.prerequisites,
        )
        for act in activities
    ]


@router.get("/activity/{activity_id}", response_model=ActivityDetailResponse)
def get_activity_detail(activity_id: str) -> ActivityDetailResponse:
    """Retrieve detailed specification for a single activity."""
    try:
        act = get_activity(activity_id)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity '{activity_id}' not found",
        )

    return ActivityDetailResponse(
        activity_id=act.activity_id,
        concept_id=act.concept_id,
        title=act.title,
        description=act.description,
        task_type=act.task_type,
        prerequisites=act.prerequisites,
        prompt=act.prompt,
        options=act.options,
        quantum_experiment=act.quantum_experiment,
        remediation_activity_id=act.remediation_activity_id,
        next_activity_id=act.next_activity_id,
    )


@router.post("/activity/{activity_id}/submit", response_model=SubmissionResponse)
def submit_activity_attempt(
    activity_id: str,
    req: SubmissionRequest,
    repo: LearnerRepository = Depends(get_learner_repository),
    model: LearnerModel = Depends(get_learner_model),
) -> SubmissionResponse:
    """
    Process a learner activity attempt through the complete vertical slice:
      1. Resolve activity definition
      2. Load persistent learner state from repository (raises 503 on persistence failure)
      3. If quantum prediction, execute REAL M3 quantum engine experiment (raises 500 on quantum failure)
      4. Construct empirical LearnerEvidence
      5. Accumulate evidence into persistent LearnerState in repository
      6. Compute M2 deterministic adaptive routing decision
      7. Persist updated state (raises 503 on persistence failure)
      8. Return structured response contract for UI and AI explanation
    """
    try:
        activity = get_activity(activity_id)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity '{activity_id}' not found",
        )

    # 1. Load persistent learner state from repository
    try:
        state = repo.get(req.learner_id)
    except PersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Learner state persistence service is currently unavailable",
        ) from exc

    prior_attempts = [
        e for e in state.evidence_history
        if e.get("activity_id") == activity_id
    ]
    attempt_num = len(prior_attempts) + 1

    verified_dict: dict[str, Any] | None = None

    # 2. Execution & Evidence Construction
    if activity.task_type == "quantum_prediction":
        if not activity.quantum_experiment:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Activity '{activity_id}' missing quantum_experiment specification",
            )
        
        # Real M3 Quantum Engine Execution
        try:
            experiment = QuantumExperiment(**activity.quantum_experiment)
            sim_result = run_experiment(experiment)
            verified_dict = sim_result.to_dict()
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Quantum execution engine failed: {exc}",
            ) from exc

        evidence = evaluate_quantum_prediction(
            learner_id=req.learner_id,
            activity_id=activity.activity_id,
            concept_id=activity.concept_id,
            prediction=req.response,
            simulation_result=verified_dict,
            attempt_number=attempt_num,
        )
    else:
        # Conceptual Choice Activity
        evidence = evaluate_conceptual_response(
            learner_id=req.learner_id,
            activity_id=activity.activity_id,
            concept_id=activity.concept_id,
            selected_option=req.response,
            expected_option=activity.expected_answer or "",
            attempt_number=attempt_num,
        )

    # 3. M2 Ingestion & State Accumulation
    decision = model.record_evidence(evidence, state)

    # 4. Save updated state back to repository (do not pretend save succeeded on error)
    try:
        repo.save(state)
    except PersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to persist updated learner state to storage",
        ) from exc

    # 5. Return complete response contract
    return SubmissionResponse(
        activity={
            "activity_id": activity.activity_id,
            "title": activity.title,
            "concept_id": activity.concept_id,
            "task_type": activity.task_type,
        },
        learner_response=req.response,
        verified_result=verified_dict,
        evidence=evidence.to_dict(),
        learner_state=state.to_dict(),
        adaptive_decision=decision.to_dict(),
    )


# ---------------------------------------------------------------------------
# Diagnostic Readiness Check & Learner State Endpoints (Phase 8 & 4)
# ---------------------------------------------------------------------------

_diagnostic = Diagnostic()

DIAGNOSTIC_ITEMS = [
    ("diag_qubits", "Qubits", 0),
    ("diag_superposition", "Superposition", 0),
    ("diag_measurement", "Measurement", 0),
    ("diag_quantum_gates", "Quantum Gates", 0),
]


@router.get("/diagnostic/readiness_check", response_model=DiagnosticReadinessResponse)
def get_diagnostic_readiness_check() -> DiagnosticReadinessResponse:
    """
    Retrieve concise diagnostic questions across foundational quantum concepts
    (Qubits, Superposition, Measurement, Gates) from the authoritative dataset.
    """
    items: list[DiagnosticQuestionItem] = []
    for q_id, topic, q_idx in DIAGNOSTIC_ITEMS:
        qs = _diagnostic.get_questions(topic)
        q = qs[q_idx]
        items.append(
            DiagnosticQuestionItem(
                id=q_id,
                question_id=q_id,
                topic=q.topic,
                concept_id=q.concept_id,
                question=q.question,
                prompt=q.question,
                options=q.options,
                difficulty=q.difficulty,
            )
        )


    return DiagnosticReadinessResponse(questions=items)


@router.post("/diagnostic/submit", response_model=DiagnosticSubmitResponse)
def submit_diagnostic_readiness_check(
    req: DiagnosticSubmitRequest,
    repo: LearnerRepository = Depends(get_learner_repository),
    model: LearnerModel = Depends(get_learner_model),
) -> DiagnosticSubmitResponse:
    """
    Evaluate diagnostic readiness check responses:
      1. Compares learner answers against authoritative answer keys.
      2. Generates real LearnerEvidence with evidence_type='diagnostic_response'.
      3. Ingests evidence into persistent LearnerState via authoritative M2 model.
      4. Saves updated state to repository.
      5. Returns evaluated outcome, question breakdown, and M2 adaptive recommendation.
    """
    try:
        state = repo.get(req.learner_id)
    except PersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Learner state persistence service is currently unavailable",
        ) from exc

    results: list[DiagnosticQuestionResult] = []
    correct_count = 0
    last_decision = None

    for q_id, topic, q_idx in DIAGNOSTIC_ITEMS:
        qs = _diagnostic.get_questions(topic)
        q = qs[q_idx]

        chosen = str(req.answers.get(q_id, "")).strip().upper()
        is_correct = chosen == q.correct_answer
        if is_correct:
            correct_count += 1

        prior_attempts = [e for e in state.evidence_history if e.get("activity_id") == q_id]
        attempt_num = len(prior_attempts) + 1

        evidence = LearnerEvidence(
            learner_id=req.learner_id,
            activity_id=q_id,
            concept_id=q.concept_id,
            learner_response=chosen or "unanswered",
            is_correct=is_correct,
            attempt_number=attempt_num,
            evidence_type="diagnostic_response",
            evidence_source="learner",
            evaluation_details={
                "question": q.question,
                "chosen": chosen,
                "correct_answer": q.correct_answer,
                "explanation": q.explanation,
                "topic": q.topic,
            },
        )

        last_decision = model.record_evidence(evidence, state)

        results.append(
            DiagnosticQuestionResult(
                question_id=q_id,
                topic=q.topic,
                concept_id=q.concept_id,
                question=q.question,
                chosen=chosen,
                correct_answer=q.correct_answer,
                is_correct=is_correct,
                explanation=q.explanation,
                evidence_id=evidence.evidence_id,
            )
        )

    try:
        repo.save(state)
    except PersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to persist updated learner state to storage",
        ) from exc

    score = round(correct_count / len(DIAGNOSTIC_ITEMS), 4) if DIAGNOSTIC_ITEMS else 0.0

    return DiagnosticSubmitResponse(
        learner_id=req.learner_id,
        score=score,
        total_questions=len(DIAGNOSTIC_ITEMS),
        correct_count=correct_count,
        results=results,
        learner_state=state.to_dict(),
        adaptive_decision=last_decision.to_dict() if last_decision else {},
    )


@router.get("/learner/{learner_id}/state", response_model=LearnerStateResponse)
def get_learner_state(
    learner_id: str,
    repo: LearnerRepository = Depends(get_learner_repository),
) -> LearnerStateResponse:
    """
    Retrieve authoritative persistent learner state and complete evidence history.
    """
    try:
        state = repo.get(learner_id)
    except PersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Learner state persistence service is currently unavailable",
        ) from exc

    return LearnerStateResponse(
        user_id=state.user_id,
        concept_scores=state.concept_scores,
        attempts=state.attempts,
        errors=state.errors,
        score_history=state.score_history,
        evidence_history=state.evidence_history,
        gap_inferences=state.gap_inferences,
    )
