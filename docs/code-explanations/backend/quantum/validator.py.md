# Explanation: `backend/quantum/validator.py`

## Purpose

This page explains the meaningful behavior in `backend/quantum/validator.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
from .schemas import QuantumExperiment

def validate_experiment(experiment: QuantumExperiment) -> None:
    if experiment.algorithm.lower() != "grover":
        raise ValueError("Only Grover's Algorithm is supported")

    if len(experiment.target_state) != experiment.num_qubits:
        raise ValueError("Target state length must match the number of qubits.")

    if not all(bit in "01" for bit in experiment.target_state):
        raise ValueError("Target state must contain only binary values: 0 or 1.")
    
```

## Line Notes

### Line 1

`from .schemas import QuantumExperiment`

Imports a dependency or project symbol so later code can use it by name.
### Line 2

`(blank)`

Blank line used to separate nearby statements.
### Line 3

`def validate_experiment(experiment: QuantumExperiment) -> None:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 4

`if experiment.algorithm.lower() != "grover":`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 5

`raise ValueError("Only Grover's Algorithm is supported")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 6

`(blank)`

Blank line used to separate nearby statements.
### Line 7

`if len(experiment.target_state) != experiment.num_qubits:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 8

`raise ValueError("Target state length must match the number of qubits.")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 9

`(blank)`

Blank line used to separate nearby statements.
### Line 10

`if not all(bit in "01" for bit in experiment.target_state):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 11

`raise ValueError("Target state must contain only binary values: 0 or 1.")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.

## Nearby Files

[backend/quantum/__init__.py](__init__.py.md), [backend/quantum/engine.py](engine.py.md), [backend/quantum/execution.py](execution.py.md), [backend/quantum/registry.py](registry.py.md), [backend/quantum/results.py](results.py.md), [backend/quantum/schemas.py](schemas.py.md)
