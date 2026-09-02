# Explanation: `backend/quantum/engine.py`

## Purpose

This page explains the meaningful behavior in `backend/quantum/engine.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
from .execution import execute_circuit
from .registry import get_algorithm
from .results import SimulationResult, extract_circuit_metadata
from .schemas import QuantumExperiment
from .validator import validate_experiment


def run_experiment(experiment: QuantumExperiment) -> SimulationResult:
    validate_experiment(experiment)

    algorithm = get_algorithm(experiment.algorithm)

    circuit = algorithm(
        num_qubits=experiment.num_qubits,
        target_state=experiment.target_state,
        iterations=experiment.iterations,
    )

    counts = dict(execute_circuit(circuit, shots=experiment.shots))
    circuit_metadata = extract_circuit_metadata(circuit)

    return SimulationResult(
        algorithm=experiment.algorithm,
        target_state=experiment.target_state,
        shots=experiment.shots,
        counts=counts,
        circuit=circuit_metadata,
    )

```

## Line Notes

### Line 1

`from .execution import execute_circuit`

Imports a dependency or project symbol so later code can use it by name.
### Line 2

`from .registry import get_algorithm`

Imports a dependency or project symbol so later code can use it by name.
### Line 3

`from .results import SimulationResult, extract_circuit_metadata`

Imports a dependency or project symbol so later code can use it by name.
### Line 4

`from .schemas import QuantumExperiment`

Imports a dependency or project symbol so later code can use it by name.
### Line 5

`from .validator import validate_experiment`

Imports a dependency or project symbol so later code can use it by name.
### Line 6

`(blank)`

Blank line used to separate nearby statements.
### Line 8

`def run_experiment(experiment: QuantumExperiment) -> SimulationResult:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 9

`validate_experiment(experiment)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 10

`(blank)`

Blank line used to separate nearby statements.
### Line 11

`algorithm = get_algorithm(experiment.algorithm)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 12

`(blank)`

Blank line used to separate nearby statements.
### Line 13

`circuit = algorithm(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 14

`num_qubits=experiment.num_qubits,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 15

`target_state=experiment.target_state,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 16

`iterations=experiment.iterations,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 17

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 18

`(blank)`

Blank line used to separate nearby statements.
### Line 19

`counts = dict(execute_circuit(circuit, shots=experiment.shots))`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 20

`circuit_metadata = extract_circuit_metadata(circuit)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 21

`(blank)`

Blank line used to separate nearby statements.
### Line 22

`return SimulationResult(`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 23

`algorithm=experiment.algorithm,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 24

`target_state=experiment.target_state,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 25

`shots=experiment.shots,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 26

`counts=counts,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 27

`circuit=circuit_metadata,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 28

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.

## Nearby Files

[backend/quantum/__init__.py](__init__.py.md), [backend/quantum/execution.py](execution.py.md), [backend/quantum/registry.py](registry.py.md), [backend/quantum/results.py](results.py.md), [backend/quantum/schemas.py](schemas.py.md), [backend/quantum/validator.py](validator.py.md)
