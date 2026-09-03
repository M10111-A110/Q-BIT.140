from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Optional

from .concepts import resolve_concept_id


@dataclass
class Activity:
    """
    Structured definition of a diagnostic or learning activity in the MVP.
    Binds conceptual tasks, prerequisite dependencies, optional quantum experiment configurations,
    and deterministic remediation/progression routes.
    """
    activity_id: str
    concept_id: str
    title: str
    description: str
    task_type: str  # "quantum_prediction" | "conceptual_choice"
    prerequisites: list[str]
    prompt: str
    options: Optional[dict[str, str]] = None
    expected_answer: Optional[str] = None
    quantum_experiment: Optional[dict[str, Any]] = None
    remediation_activity_id: Optional[str] = None
    next_activity_id: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# MVP Explicit Activity Registry (4 Core Activities)
# ---------------------------------------------------------------------------

MVP_ACTIVITIES: dict[str, Activity] = {
    "act_grover_2q_predict": Activity(
        activity_id="act_grover_2q_predict",
        concept_id=resolve_concept_id("grover.search_problem"),
        title="Grover 2-Qubit Target State Prediction",
        description="Predict the measurement outcome of a 2-qubit Grover search circuit configured for target state |10⟩.",
        task_type="quantum_prediction",
        prerequisites=["quantum.superposition", "quantum.measurement"],
        prompt=(
            "A 2-qubit Grover search circuit has been initialized with equal superposition "
            "and executed with 1 Grover iteration marking target state |10⟩. "
            "Predict the basis state with the highest measurement count (e.g. '00', '01', '10', '11')."
        ),
        expected_answer="10",
        quantum_experiment={
            "algorithm": "grover",
            "num_qubits": 2,
            "target_state": "10",
            "iterations": 1,
            "shots": 1024,
        },
        remediation_activity_id="act_measurement_prob_diagnostic",
        next_activity_id="act_grover_iteration_reasoning",
    ),
    "act_measurement_prob_diagnostic": Activity(
        activity_id="act_measurement_prob_diagnostic",
        concept_id=resolve_concept_id("quantum.measurement"),
        title="Measurement Probability Diagnostic",
        description="Diagnostic task assessing understanding of quantum measurement and Born's rule probabilities.",
        task_type="conceptual_choice",
        prerequisites=["quantum.state"],
        prompt=(
            "In a general quantum search experiment where a target state |10⟩ has an amplitude of approximately 0.968 "
            "(such as with rotation errors or in higher-qubit search spaces), what does the final measurement distribution represent?"
        ),
        options={
            "A": "A deterministic certainty that never produces any other state in finite shots",
            "B": "A probabilistic outcome where |10⟩ has ~93.7% probability of being measured across shots (since P = |0.968|² ≈ 0.937)",
            "C": "The circuit destroying quantum information and returning classical 00 always",
            "D": "Two classical bits existing simultaneously without state collapse",
        },
        expected_answer="B",

        remediation_activity_id="act_superposition_remediation",
        next_activity_id="act_grover_2q_predict",
    ),
    "act_superposition_remediation": Activity(
        activity_id="act_superposition_remediation",
        concept_id=resolve_concept_id("quantum.superposition"),
        title="Equal Superposition Foundation",
        description="Remediation task reviewing equal superposition before oracle interference.",
        task_type="conceptual_choice",
        prerequisites=["quantum.qubit"],
        prompt=(
            "Applying Hadamard gates H^⊗2 to ground state |00⟩ creates an equal superposition of all 4 basis states. "
            "What is the theoretical measurement probability for each basis state before the oracle is applied?"
        ),
        options={
            "A": "100% for |00⟩, 0% for all others",
            "B": "25% (1/4) for each of |00⟩, |01⟩, |10⟩, and |11⟩",
            "C": "50% for |00⟩ and 50% for |11⟩",
            "D": "0% because qubits cannot be measured in superposition",
        },
        expected_answer="B",
        remediation_activity_id=None,
        next_activity_id="act_measurement_prob_diagnostic",
    ),
    "act_grover_iteration_reasoning": Activity(
        activity_id="act_grover_iteration_reasoning",
        concept_id=resolve_concept_id("grover.amplitude_amplification"),
        title="Grover Iteration and Over-Rotation",
        description="Reasoning about the oscillatory nature of Grover amplitude amplification.",
        task_type="conceptual_choice",
        prerequisites=["grover.search_problem"],
        prompt=(
            "Why does applying too many Grover iterations (e.g. 5 iterations on a 2-qubit system) "
            "decrease the target state measurement probability?"
        ),
        options={
            "A": "Because the quantum simulator runs out of memory registers",
            "B": "Because amplitude amplification is oscillatory and rotates the state vector past the target state",
            "C": "Because the oracle deletes the marked state permanently after 2 queries",
            "D": "Because measurement counts can never exceed 100 shots",
        },
        expected_answer="B",
        remediation_activity_id="act_grover_2q_predict",
        next_activity_id=None,
    ),
}


def get_activity(activity_id: str) -> Activity:
    """Retrieve an Activity definition by ID or raise KeyError."""
    if activity_id not in MVP_ACTIVITIES:
        raise KeyError(f"Unknown activity ID: '{activity_id}'. Available: {list(MVP_ACTIVITIES.keys())}")
    return MVP_ACTIVITIES[activity_id]


def list_activities() -> list[Activity]:
    """Return all registered MVP activities in default sequence."""
    return list(MVP_ACTIVITIES.values())


def get_activities_for_concept(concept_id: str) -> list[Activity]:
    """Retrieve all activities mapped to a canonical concept ID."""
    canonical = resolve_concept_id(concept_id)
    return [act for act in MVP_ACTIVITIES.values() if act.concept_id == canonical]
