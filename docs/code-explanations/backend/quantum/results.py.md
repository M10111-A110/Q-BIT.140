# Explanation: `backend/quantum/results.py`

## Purpose

This page explains the meaningful behavior in `backend/quantum/results.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # QuantumCircuit is only referenced for type-checking and inside
    # extract_circuit_metadata(); it never appears in the public API surface.
    from qiskit import QuantumCircuit


@dataclass
class CircuitMetadata:
    """
    Pure-Python, Qiskit-free snapshot of a constructed quantum circuit.

    Downstream modules (M1, M4, M5, M6) may consume this freely without
    importing Qiskit.
    """
    num_qubits: int
    num_clbits: int
    depth: int
    gate_counts: dict[str, int]
    diagram: str


def extract_circuit_metadata(circuit: "QuantumCircuit") -> CircuitMetadata:
    """
    Extract a Qiskit-free CircuitMetadata snapshot from a QuantumCircuit.

    This is the ONLY place in M3 where Qiskit circuit internals are read
    for serialization purposes.  The returned object contains no Qiskit
    types.
    """
    diagram = circuit.draw(output="text").single_string()

    return CircuitMetadata(
        num_qubits=circuit.num_qubits,
        num_clbits=circuit.num_clbits,
        depth=circuit.depth(),
        gate_counts=dict(circuit.count_ops()),
        diagram=diagram,
    )


@dataclass
class SimulationResult:
    """
    Canonical, Qiskit-free output of a quantum experiment.

    All fields are plain Python primitives.  Downstream modules must
    never receive Qiskit objects through this dataclass.

    ``circuit`` is optional for backward compatibility: existing tests and
    call sites that do not pass it receive ``None`` and continue to work.
    """
    algorithm: str
    target_state: str
    shots: int
    counts: dict[str, int]
    circuit: CircuitMetadata | None = field(default=None)

    def __post_init__(self) -> None:
        if self.shots <= 0:
            raise ValueError("shots must be greater than zero")

        if any(count < 0 for count in self.counts.values()):
            raise ValueError("measurement counts cannot be negative")

        if sum(self.counts.values()) != self.shots:
            raise ValueError("measurement counts must sum to shots")

    # ------------------------------------------------------------------
    # Derived evidence — useful for M1 (learner), M2 (model), M5 (AI)
    # ------------------------------------------------------------------

    @property
    def probabilities(self) -> dict[str, float]:
        """Normalised measurement probability distribution."""
        return {
            state: count / self.shots
            for state, count in self.counts.items()
        }

    @property
    def target_probability(self) -> float:
        """Probability of measuring the requested target state."""
        return self.counts.get(self.target_state, 0) / self.shots

    @property
    def most_likely_state(self) -> str:
        """Computational basis state with the highest measurement count."""
        return max(self.counts, key=self.counts.get)

    # ------------------------------------------------------------------
    # Serialization — required for M4 (API / Supabase JSON transport)
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """
        Return a fully JSON-serializable representation of this result.

        Includes computed properties (probabilities, target_probability,
        most_likely_state) and circuit metadata.  This is the intended
        format for M4 to serialize to HTTP responses or Supabase rows.

        ``dataclasses.asdict()`` is deliberately NOT used because it
        would silently omit the ``@property`` derived fields.
        """
        circuit_dict = None
        if self.circuit is not None:
            circuit_dict = {
                "num_qubits": self.circuit.num_qubits,
                "num_clbits": self.circuit.num_clbits,
                "depth": self.circuit.depth,
                "gate_counts": self.circuit.gate_counts,
                "diagram": self.circuit.diagram,
            }

        return {
            "algorithm": self.algorithm,
            "target_state": self.target_state,
            "shots": self.shots,
            "counts": self.counts,
            "probabilities": self.probabilities,
            "target_probability": self.target_probability,
            "most_likely_state": self.most_likely_state,
            "circuit": circuit_dict,
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

`from dataclasses import dataclass, field`

Imports a dependency or project symbol so later code can use it by name.
### Line 4

`from typing import TYPE_CHECKING`

Imports a dependency or project symbol so later code can use it by name.
### Line 5

`(blank)`

Blank line used to separate nearby statements.
### Line 6

`if TYPE_CHECKING:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 7

`# QuantumCircuit is only referenced for type-checking and inside`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 8

`# extract_circuit_metadata(); it never appears in the public API surface.`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 9

`from qiskit import QuantumCircuit`

Imports a dependency or project symbol so later code can use it by name.
### Line 10

`(blank)`

Blank line used to separate nearby statements.
### Line 12

`@dataclass`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 13

`class CircuitMetadata:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 14

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 15

`Pure-Python, Qiskit-free snapshot of a constructed quantum circuit.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 16

`(blank)`

Blank line used to separate nearby statements.
### Line 17

`Downstream modules (M1, M4, M5, M6) may consume this freely without`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 18

`importing Qiskit.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 19

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 20

`num_qubits: int`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 21

`num_clbits: int`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 22

`depth: int`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 23

`gate_counts: dict[str, int]`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 24

`diagram: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 25

`(blank)`

Blank line used to separate nearby statements.
### Line 27

`def extract_circuit_metadata(circuit: "QuantumCircuit") -> CircuitMetadata:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 28

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 29

`Extract a Qiskit-free CircuitMetadata snapshot from a QuantumCircuit.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 30

`(blank)`

Blank line used to separate nearby statements.
### Line 31

`This is the ONLY place in M3 where Qiskit circuit internals are read`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 32

`for serialization purposes.  The returned object contains no Qiskit`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 33

`types.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 34

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 35

`diagram = circuit.draw(output="text").single_string()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 36

`(blank)`

Blank line used to separate nearby statements.
### Line 37

`return CircuitMetadata(`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 38

`num_qubits=circuit.num_qubits,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 39

`num_clbits=circuit.num_clbits,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 40

`depth=circuit.depth(),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 41

`gate_counts=dict(circuit.count_ops()),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 42

`diagram=diagram,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 43

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 44

`(blank)`

Blank line used to separate nearby statements.
### Line 46

`@dataclass`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 47

`class SimulationResult:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 48

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 49

`Canonical, Qiskit-free output of a quantum experiment.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 50

`(blank)`

Blank line used to separate nearby statements.
### Line 51

`All fields are plain Python primitives.  Downstream modules must`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 52

`never receive Qiskit objects through this dataclass.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 53

`(blank)`

Blank line used to separate nearby statements.
### Line 54

`\`\`circuit\`\` is optional for backward compatibility: existing tests and`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 55

`call sites that do not pass it receive \`\`None\`\` and continue to work.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 56

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 57

`algorithm: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 58

`target_state: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 59

`shots: int`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 60

`counts: dict[str, int]`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 61

`circuit: CircuitMetadata | None = field(default=None)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 62

`(blank)`

Blank line used to separate nearby statements.
### Line 63

`def __post_init__(self) -> None:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 64

`if self.shots <= 0:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 65

`raise ValueError("shots must be greater than zero")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 66

`(blank)`

Blank line used to separate nearby statements.
### Line 67

`if any(count < 0 for count in self.counts.values()):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 68

`raise ValueError("measurement counts cannot be negative")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 69

`(blank)`

Blank line used to separate nearby statements.
### Line 70

`if sum(self.counts.values()) != self.shots:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 71

`raise ValueError("measurement counts must sum to shots")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 72

`(blank)`

Blank line used to separate nearby statements.
### Line 73

`# ------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 74

`# Derived evidence — useful for M1 (learner), M2 (model), M5 (AI)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 75

`# ------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 76

`(blank)`

Blank line used to separate nearby statements.
### Line 77

`@property`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 78

`def probabilities(self) -> dict[str, float]:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 79

`"""Normalised measurement probability distribution."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 80

`return {`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 81

`state: count / self.shots`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 82

`for state, count in self.counts.items()`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 83

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 84

`(blank)`

Blank line used to separate nearby statements.
### Line 85

`@property`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 86

`def target_probability(self) -> float:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 87

`"""Probability of measuring the requested target state."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 88

`return self.counts.get(self.target_state, 0) / self.shots`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 89

`(blank)`

Blank line used to separate nearby statements.
### Line 90

`@property`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 91

`def most_likely_state(self) -> str:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 92

`"""Computational basis state with the highest measurement count."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 93

`return max(self.counts, key=self.counts.get)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 94

`(blank)`

Blank line used to separate nearby statements.
### Line 95

`# ------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 96

`# Serialization — required for M4 (API / Supabase JSON transport)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 97

`# ------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 98

`(blank)`

Blank line used to separate nearby statements.
### Line 99

`def to_dict(self) -> dict:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 100

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 101

`Return a fully JSON-serializable representation of this result.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 102

`(blank)`

Blank line used to separate nearby statements.
### Line 103

`Includes computed properties (probabilities, target_probability,`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 104

`most_likely_state) and circuit metadata.  This is the intended`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 105

`format for M4 to serialize to HTTP responses or Supabase rows.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 106

`(blank)`

Blank line used to separate nearby statements.
### Line 107

`\`\`dataclasses.asdict()\`\` is deliberately NOT used because it`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 108

`would silently omit the \`\`@property\`\` derived fields.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 109

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 110

`circuit_dict = None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 111

`if self.circuit is not None:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 112

`circuit_dict = {`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 113

`"num_qubits": self.circuit.num_qubits,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 114

`"num_clbits": self.circuit.num_clbits,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 115

`"depth": self.circuit.depth,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 116

`"gate_counts": self.circuit.gate_counts,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 117

`"diagram": self.circuit.diagram,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 118

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 119

`(blank)`

Blank line used to separate nearby statements.
### Line 120

`return {`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 121

`"algorithm": self.algorithm,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 122

`"target_state": self.target_state,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 123

`"shots": self.shots,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 124

`"counts": self.counts,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 125

`"probabilities": self.probabilities,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 126

`"target_probability": self.target_probability,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 127

`"most_likely_state": self.most_likely_state,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 128

`"circuit": circuit_dict,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 129

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.

## Nearby Files

[backend/quantum/__init__.py](__init__.py.md), [backend/quantum/engine.py](engine.py.md), [backend/quantum/execution.py](execution.py.md), [backend/quantum/registry.py](registry.py.md), [backend/quantum/schemas.py](schemas.py.md), [backend/quantum/validator.py](validator.py.md)
