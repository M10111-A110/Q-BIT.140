# Explanation: `backend/adaptive/concepts.py`

## Purpose

This page explains the meaningful behavior in `backend/adaptive/concepts.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
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

```

## Line Notes

### Line 1

`from __future__ import annotations`

Imports a dependency or project symbol so later code can use it by name.
### Line 2

`(blank)`

Blank line used to separate nearby statements.
### Line 3

`from dataclasses import dataclass`

Imports a dependency or project symbol so later code can use it by name.
### Line 4

`from typing import Literal`

Imports a dependency or project symbol so later code can use it by name.
### Line 5

`(blank)`

Blank line used to separate nearby statements.
### Line 6

`ConceptType = Literal["prerequisite", "core", "algorithm"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 7

`(blank)`

Blank line used to separate nearby statements.
### Line 9

`@dataclass(frozen=True)`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 10

`class Concept:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 11

`"""Canonical representation of a curriculum concept."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 12

`id: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 13

`name: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 14

`prerequisites: tuple[str, ...]`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 15

`concept_type: ConceptType`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 16

`description: str = ""`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 17

`(blank)`

Blank line used to separate nearby statements.
### Line 19

`# ---------------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 20

`# Canonical Concept Definitions & DAG`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 21

`# ---------------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 22

`# Order matches the prerequisite chain:`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 23

`#   Qubits -> Quantum States -> Superposition -> Quantum Gates -> Measurement`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 24

`# Canonical IDs align with M5 knowledge base taxonomy (11_concept_ids.md).`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 25

`(blank)`

Blank line used to separate nearby statements.
### Line 26

`CANONICAL_CONCEPTS: dict[str, Concept] = {`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 27

`"quantum.qubit": Concept(`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 28

`id="quantum.qubit",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 29

`name="Qubits",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 30

`prerequisites=(),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 31

`concept_type="prerequisite",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 32

`description="Foundational definition of a qubit as the basic unit of quantum information.",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 33

`),`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 34

`"quantum.state": Concept(`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 35

`id="quantum.state",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 36

`name="Quantum States",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 37

`prerequisites=("quantum.qubit",),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 38

`concept_type="prerequisite",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 39

`description="State vectors, amplitudes, and basis representation in Hilbert space.",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 40

`),`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 41

`"quantum.superposition": Concept(`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 42

`id="quantum.superposition",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 43

`name="Superposition",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 44

`prerequisites=("quantum.state",),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 45

`concept_type="core",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 46

`description="Linear combinations of basis states and Hadamard gate transformations.",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 47

`),`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 48

`"quantum.gates": Concept(`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 49

`id="quantum.gates",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 50

`name="Quantum Gates",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 51

`prerequisites=("quantum.superposition",),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 52

`concept_type="core",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 53

`description="Unitary operations manipulating single and multiple qubits (Pauli, H, CNOT).",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 54

`),`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 55

`"quantum.measurement": Concept(`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 56

`id="quantum.measurement",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 57

`name="Measurement",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 58

`prerequisites=("quantum.gates",),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 59

`concept_type="core",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 60

`description="Projective measurement, Born's rule probabilities, and state collapse.",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 61

`),`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 62

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 63

`(blank)`

Blank line used to separate nearby statements.
### Line 64

`# Display name <-> Canonical ID lookup tables`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 65

`_NAME_TO_ID: dict[str, str] = {c.name: c.id for c in CANONICAL_CONCEPTS.values()}`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 66

`_ID_TO_NAME: dict[str, str] = {c.id: c.name for c in CANONICAL_CONCEPTS.values()}`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 67

`(blank)`

Blank line used to separate nearby statements.
### Line 68

`# Additional aliases for robustness`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 69

`_NAME_TO_ID.update({`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 70

`"qubit": "quantum.qubit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 71

`"qubits": "quantum.qubit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 72

`"state": "quantum.state",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 73

`"states": "quantum.state",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 74

`"quantum states": "quantum.state",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 75

`"superposition": "quantum.superposition",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 76

`"gates": "quantum.gates",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 77

`"quantum gates": "quantum.gates",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 78

`"measurement": "quantum.measurement",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 79

`})`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 80

`(blank)`

Blank line used to separate nearby statements.
### Line 82

`def resolve_concept_id(name_or_id: str) -> str:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 83

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 84

`Resolve a human-readable display name or concept ID to its canonical ID.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 85

`If already a canonical ID or unrecognized, returns it normalized.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 86

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 87

`cleaned = name_or_id.strip()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 88

`if cleaned in CANONICAL_CONCEPTS:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 89

`return cleaned`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 90

`cleaned_lower = cleaned.lower()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 91

`if cleaned_lower in _NAME_TO_ID:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 92

`return _NAME_TO_ID[cleaned_lower]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 93

`if cleaned in _NAME_TO_ID:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 94

`return _NAME_TO_ID[cleaned]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 95

`return cleaned`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 96

`(blank)`

Blank line used to separate nearby statements.
### Line 98

`def get_concept_display_name(concept_id: str) -> str:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 99

`"""Return the display name for a concept ID, falling back to the ID itself."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 100

`return _ID_TO_NAME.get(concept_id, concept_id)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 101

`(blank)`

Blank line used to separate nearby statements.
### Line 103

`def get_concept(concept_id_or_name: str) -> Concept | None:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 104

`"""Retrieve a Concept dataclass by canonical ID or display name."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 105

`canonical_id = resolve_concept_id(concept_id_or_name)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 106

`return CANONICAL_CONCEPTS.get(canonical_id)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 107

`(blank)`

Blank line used to separate nearby statements.
### Line 109

`def get_concept_graph() -> dict[str, dict]:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 110

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 111

`Return the concept graph dictionary keyed by canonical ID with display`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 112

`name and prerequisites for consumption by adaptive engine and UI.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 113

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 114

`return {`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 115

`c_id: {`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 116

`"name": c.name,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 117

`"prereqs": list(c.prerequisites),`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 118

`"type": c.concept_type,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 119

`"description": c.description,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 120

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 121

`for c_id, c in CANONICAL_CONCEPTS.items()`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 122

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 123

`(blank)`

Blank line used to separate nearby statements.
### Line 125

`# Backward-compatible dictionary matching the original M2 CONCEPT_GRAPH structure`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 126

`# Keyed by display name with display name prereqs, so existing call sites work seamlessly.`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 127

`CONCEPT_GRAPH: dict[str, dict] = {`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 128

`"Qubits": {"prereqs": [], "type": "prerequisite", "concept_id": "quantum.qubit"},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 129

`"Quantum States": {"prereqs": ["Qubits"], "type": "prerequisite", "concept_id": "quantum.state"},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 130

`"Superposition": {"prereqs": ["Quantum States"], "type": "core", "concept_id": "quantum.superposition"},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 131

`"Quantum Gates": {"prereqs": ["Superposition"], "type": "core", "concept_id": "quantum.gates"},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 132

`"Measurement": {"prereqs": ["Quantum Gates"], "type": "core", "concept_id": "quantum.measurement"},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 133

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.

## Nearby Files

[backend/adaptive/__init__.py](__init__.py.md), [backend/adaptive/activities.py](activities.py.md), [backend/adaptive/diagnostics.py](diagnostics.py.md), [backend/adaptive/engine.py](engine.py.md), [backend/adaptive/evidence.py](evidence.py.md), [backend/adaptive/models.py](models.py.md), [backend/adaptive/repository.py](repository.py.md)
