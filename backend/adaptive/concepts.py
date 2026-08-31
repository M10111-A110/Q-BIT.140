from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ConceptType = Literal["prerequisite", "core", "algorithm"]


@dataclass(frozen=True)
class Concept:
    """Canonical representation of a curriculum concept."""
    id: str
    name: str
    prerequisites: tuple[str, ...]
    concept_type: ConceptType
    description: str = ""


# ---------------------------------------------------------------------------
# Canonical Concept Definitions & DAG
# ---------------------------------------------------------------------------
# Order matches the prerequisite chain:
#   Qubits -> Quantum States -> Superposition -> Quantum Gates -> Measurement
# Canonical IDs align with M5 knowledge base taxonomy (11_concept_ids.md).

CANONICAL_CONCEPTS: dict[str, Concept] = {
    "quantum.qubit": Concept(
        id="quantum.qubit",
        name="Qubits",
        prerequisites=(),
        concept_type="prerequisite",
        description="Foundational definition of a qubit as the basic unit of quantum information.",
    ),
    "quantum.state": Concept(
        id="quantum.state",
        name="Quantum States",
        prerequisites=("quantum.qubit",),
        concept_type="prerequisite",
        description="State vectors, amplitudes, and basis representation in Hilbert space.",
    ),
    "quantum.superposition": Concept(
        id="quantum.superposition",
        name="Superposition",
        prerequisites=("quantum.state",),
        concept_type="core",
        description="Linear combinations of basis states and Hadamard gate transformations.",
    ),
    "quantum.gates": Concept(
        id="quantum.gates",
        name="Quantum Gates",
        prerequisites=("quantum.superposition",),
        concept_type="core",
        description="Unitary operations manipulating single and multiple qubits (Pauli, H, CNOT).",
    ),
    "quantum.measurement": Concept(
        id="quantum.measurement",
        name="Measurement",
        prerequisites=("quantum.gates",),
        concept_type="core",
        description="Projective measurement, Born's rule probabilities, and state collapse.",
    ),
}

# Display name <-> Canonical ID lookup tables
_NAME_TO_ID: dict[str, str] = {c.name: c.id for c in CANONICAL_CONCEPTS.values()}
_ID_TO_NAME: dict[str, str] = {c.id: c.name for c in CANONICAL_CONCEPTS.values()}

# Additional aliases for robustness
_NAME_TO_ID.update({
    "qubit": "quantum.qubit",
    "qubits": "quantum.qubit",
    "state": "quantum.state",
    "states": "quantum.state",
    "quantum states": "quantum.state",
    "superposition": "quantum.superposition",
    "gates": "quantum.gates",
    "quantum gates": "quantum.gates",
    "measurement": "quantum.measurement",
})


def resolve_concept_id(name_or_id: str) -> str:
    """
    Resolve a human-readable display name or concept ID to its canonical ID.
    If already a canonical ID or unrecognized, returns it normalized.
    """
    cleaned = name_or_id.strip()
    if cleaned in CANONICAL_CONCEPTS:
        return cleaned
    cleaned_lower = cleaned.lower()
    if cleaned_lower in _NAME_TO_ID:
        return _NAME_TO_ID[cleaned_lower]
    if cleaned in _NAME_TO_ID:
        return _NAME_TO_ID[cleaned]
    return cleaned


def get_concept_display_name(concept_id: str) -> str:
    """Return the display name for a concept ID, falling back to the ID itself."""
    return _ID_TO_NAME.get(concept_id, concept_id)


def get_concept(concept_id_or_name: str) -> Concept | None:
    """Retrieve a Concept dataclass by canonical ID or display name."""
    canonical_id = resolve_concept_id(concept_id_or_name)
    return CANONICAL_CONCEPTS.get(canonical_id)


def get_concept_graph() -> dict[str, dict]:
    """
    Return the concept graph dictionary keyed by canonical ID with display
    name and prerequisites for consumption by adaptive engine and UI.
    """
    return {
        c_id: {
            "name": c.name,
            "prereqs": list(c.prerequisites),
            "type": c.concept_type,
            "description": c.description,
        }
        for c_id, c in CANONICAL_CONCEPTS.items()
    }


# Backward-compatible dictionary matching the original M2 CONCEPT_GRAPH structure
# Keyed by display name with display name prereqs, so existing call sites work seamlessly.
CONCEPT_GRAPH: dict[str, dict] = {
    "Qubits": {"prereqs": [], "type": "prerequisite", "concept_id": "quantum.qubit"},
    "Quantum States": {"prereqs": ["Qubits"], "type": "prerequisite", "concept_id": "quantum.state"},
    "Superposition": {"prereqs": ["Quantum States"], "type": "core", "concept_id": "quantum.superposition"},
    "Quantum Gates": {"prereqs": ["Superposition"], "type": "core", "concept_id": "quantum.gates"},
    "Measurement": {"prereqs": ["Quantum Gates"], "type": "core", "concept_id": "quantum.measurement"},
}
