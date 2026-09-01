from __future__ import annotations

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status

from backend.adaptive import (
    LearnerModel,
    LearnerRepository,
    PersistenceError,
    evaluate_conceptual_response,
    evaluate_quantum_prediction,
    get_activity,
    list_activities,
)
from backend.quantum import QuantumExperiment, run_experiment

from ..dependencies import get_learner_model, get_learner_repository
from ..schemas import (
    ActivityDetailResponse,
    ActivitySummary,
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
