# Explanation: `backend/adaptive/activities.py`

## Purpose

This page explains the meaningful behavior in `backend/adaptive/activities.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
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
            "In a quantum experiment with target state |10⟩ where the state amplitude is approximately 0.968, "
            "what does the final measurement distribution represent?"
        ),
        options={
            "A": "A deterministic certainty that never produces any other state in finite shots",
            "B": "A probabilistic outcome where |10⟩ has ~93.7% probability of being measured across shots",
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

```

## Line Notes

### Line 1

`from __future__ import annotations`

Imports a dependency or project symbol so later code can use it by name.
### Line 2

`(blank)`

Blank line used to separate nearby statements.
### Line 3

`from dataclasses import asdict, dataclass, field`

Imports a dependency or project symbol so later code can use it by name.
### Line 4

`from typing import Any, Optional`

Imports a dependency or project symbol so later code can use it by name.
### Line 5

`(blank)`

Blank line used to separate nearby statements.
### Line 6

`from .concepts import resolve_concept_id`

Imports a dependency or project symbol so later code can use it by name.
### Line 7

`(blank)`

Blank line used to separate nearby statements.
### Line 9

`@dataclass`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 10

`class Activity:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 11

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 12

`Structured definition of a diagnostic or learning activity in the MVP.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 13

`Binds conceptual tasks, prerequisite dependencies, optional quantum experiment configurations,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 14

`and deterministic remediation/progression routes.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 15

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 16

`activity_id: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 17

`concept_id: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 18

`title: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 19

`description: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 20

`task_type: str  # "quantum_prediction" | "conceptual_choice"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 21

`prerequisites: list[str]`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 22

`prompt: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 23

`options: Optional[dict[str, str]] = None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 24

`expected_answer: Optional[str] = None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 25

`quantum_experiment: Optional[dict[str, Any]] = None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 26

`remediation_activity_id: Optional[str] = None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 27

`next_activity_id: Optional[str] = None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 28

`metadata: dict[str, Any] = field(default_factory=dict)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 29

`(blank)`

Blank line used to separate nearby statements.
### Line 30

`def to_dict(self) -> dict[str, Any]:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 31

`return asdict(self)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 32

`(blank)`

Blank line used to separate nearby statements.
### Line 34

`# ---------------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 35

`# MVP Explicit Activity Registry (4 Core Activities)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 36

`# ---------------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 37

`(blank)`

Blank line used to separate nearby statements.
### Line 38

`MVP_ACTIVITIES: dict[str, Activity] = {`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 39

`"act_grover_2q_predict": Activity(`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 40

`activity_id="act_grover_2q_predict",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 41

`concept_id=resolve_concept_id("grover.search_problem"),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 42

`title="Grover 2-Qubit Target State Prediction",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 43

`description="Predict the measurement outcome of a 2-qubit Grover search circuit configured for target state |10⟩.",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 44

`task_type="quantum_prediction",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 45

`prerequisites=["quantum.superposition", "quantum.measurement"],`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 46

`prompt=(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 47

`"A 2-qubit Grover search circuit has been initialized with equal superposition "`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 48

`"and executed with 1 Grover iteration marking target state |10⟩. "`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 49

`"Predict the basis state with the highest measurement count (e.g. '00', '01', '10', '11')."`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 50

`),`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 51

`expected_answer="10",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 52

`quantum_experiment={`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 53

`"algorithm": "grover",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 54

`"num_qubits": 2,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 55

`"target_state": "10",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 56

`"iterations": 1,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 57

`"shots": 1024,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 58

`},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 59

`remediation_activity_id="act_measurement_prob_diagnostic",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 60

`next_activity_id="act_grover_iteration_reasoning",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 61

`),`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 62

`"act_measurement_prob_diagnostic": Activity(`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 63

`activity_id="act_measurement_prob_diagnostic",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 64

`concept_id=resolve_concept_id("quantum.measurement"),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 65

`title="Measurement Probability Diagnostic",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 66

`description="Diagnostic task assessing understanding of quantum measurement and Born's rule probabilities.",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 67

`task_type="conceptual_choice",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 68

`prerequisites=["quantum.state"],`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 69

`prompt=(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 70

`"In a quantum experiment with target state |10⟩ where the state amplitude is approximately 0.968, "`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 71

`"what does the final measurement distribution represent?"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 72

`),`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 73

`options={`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 74

`"A": "A deterministic certainty that never produces any other state in finite shots",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 75

`"B": "A probabilistic outcome where |10⟩ has ~93.7% probability of being measured across shots",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 76

`"C": "The circuit destroying quantum information and returning classical 00 always",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 77

`"D": "Two classical bits existing simultaneously without state collapse",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 78

`},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 79

`expected_answer="B",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 80

`remediation_activity_id="act_superposition_remediation",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 81

`next_activity_id="act_grover_2q_predict",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 82

`),`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 83

`"act_superposition_remediation": Activity(`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 84

`activity_id="act_superposition_remediation",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 85

`concept_id=resolve_concept_id("quantum.superposition"),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 86

`title="Equal Superposition Foundation",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 87

`description="Remediation task reviewing equal superposition before oracle interference.",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 88

`task_type="conceptual_choice",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 89

`prerequisites=["quantum.qubit"],`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 90

`prompt=(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 91

`"Applying Hadamard gates H^⊗2 to ground state |00⟩ creates an equal superposition of all 4 basis states. "`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 92

`"What is the theoretical measurement probability for each basis state before the oracle is applied?"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 93

`),`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 94

`options={`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 95

`"A": "100% for |00⟩, 0% for all others",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 96

`"B": "25% (1/4) for each of |00⟩, |01⟩, |10⟩, and |11⟩",`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 97

`"C": "50% for |00⟩ and 50% for |11⟩",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 98

`"D": "0% because qubits cannot be measured in superposition",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 99

`},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 100

`expected_answer="B",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 101

`remediation_activity_id=None,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 102

`next_activity_id="act_measurement_prob_diagnostic",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 103

`),`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 104

`"act_grover_iteration_reasoning": Activity(`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 105

`activity_id="act_grover_iteration_reasoning",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 106

`concept_id=resolve_concept_id("grover.amplitude_amplification"),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 107

`title="Grover Iteration and Over-Rotation",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 108

`description="Reasoning about the oscillatory nature of Grover amplitude amplification.",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 109

`task_type="conceptual_choice",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 110

`prerequisites=["grover.search_problem"],`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 111

`prompt=(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 112

`"Why does applying too many Grover iterations (e.g. 5 iterations on a 2-qubit system) "`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 113

`"decrease the target state measurement probability?"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 114

`),`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 115

`options={`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 116

`"A": "Because the quantum simulator runs out of memory registers",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 117

`"B": "Because amplitude amplification is oscillatory and rotates the state vector past the target state",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 118

`"C": "Because the oracle deletes the marked state permanently after 2 queries",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 119

`"D": "Because measurement counts can never exceed 100 shots",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 120

`},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 121

`expected_answer="B",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 122

`remediation_activity_id="act_grover_2q_predict",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 123

`next_activity_id=None,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 124

`),`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 125

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 126

`(blank)`

Blank line used to separate nearby statements.
### Line 128

`def get_activity(activity_id: str) -> Activity:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 129

`"""Retrieve an Activity definition by ID or raise KeyError."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 130

`if activity_id not in MVP_ACTIVITIES:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 131

`raise KeyError(f"Unknown activity ID: '{activity_id}'. Available: {list(MVP_ACTIVITIES.keys())}")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 132

`return MVP_ACTIVITIES[activity_id]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 133

`(blank)`

Blank line used to separate nearby statements.
### Line 135

`def list_activities() -> list[Activity]:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 136

`"""Return all registered MVP activities in default sequence."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 137

`return list(MVP_ACTIVITIES.values())`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 138

`(blank)`

Blank line used to separate nearby statements.
### Line 140

`def get_activities_for_concept(concept_id: str) -> list[Activity]:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 141

`"""Retrieve all activities mapped to a canonical concept ID."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 142

`canonical = resolve_concept_id(concept_id)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 143

`return [act for act in MVP_ACTIVITIES.values() if act.concept_id == canonical]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.

## Nearby Files

[backend/adaptive/__init__.py](__init__.py.md), [backend/adaptive/concepts.py](concepts.py.md), [backend/adaptive/diagnostics.py](diagnostics.py.md), [backend/adaptive/engine.py](engine.py.md), [backend/adaptive/evidence.py](evidence.py.md), [backend/adaptive/models.py](models.py.md), [backend/adaptive/repository.py](repository.py.md)
