# Explanation: `tests/quantum/test_validator.py`

## Purpose

This page explains the meaningful behavior in `tests/quantum/test_validator.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
import pytest

from backend.quantum.schemas import QuantumExperiment
from backend.quantum.validator import validate_experiment

def test_valid_experiment():
    experiment = QuantumExperiment(
        algorithm="grover",
        num_qubits=2,
        target_state="11",
        iterations=1,
        shots=1024,
    )

    validate_experiment(experiment)

def test_target_state_must_match_qubit_count():
    experiment = QuantumExperiment(
            algorithm="grover",
            num_qubits=2,
            target_state="101",
            iterations=1,
            shots=1024,
    )

    with pytest.raises(ValueError):
        validate_experiment(experiment)

def test_target_state_must_be_binary():
    experiment = QuantumExperiment(
            algorithm="grover",
            num_qubits=2,
            target_state="1A",
            iterations=1,
            shots=1024,
    )

    with pytest.raises(ValueError):
        validate_experiment(experiment)

def test_only_grover_is_supported():
    experiment = QuantumExperiment(
            algorithm="qft",
            num_qubits=2,
            target_state="11",
            iterations=1,
            shots=1024,
    )

    with pytest.raises(ValueError):
        validate_experiment(experiment)
    
```

## Line Notes

### Line 1

`import pytest`

Imports a dependency or project symbol so later code can use it by name.
### Line 2

`(blank)`

Blank line used to separate nearby statements.
### Line 3

`from backend.quantum.schemas import QuantumExperiment`

Imports a dependency or project symbol so later code can use it by name.
### Line 4

`from backend.quantum.validator import validate_experiment`

Imports a dependency or project symbol so later code can use it by name.
### Line 5

`(blank)`

Blank line used to separate nearby statements.
### Line 6

`def test_valid_experiment():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 7

`experiment = QuantumExperiment(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 8

`algorithm="grover",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 9

`num_qubits=2,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 10

`target_state="11",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 11

`iterations=1,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 12

`shots=1024,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 13

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 14

`(blank)`

Blank line used to separate nearby statements.
### Line 15

`validate_experiment(experiment)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 16

`(blank)`

Blank line used to separate nearby statements.
### Line 17

`def test_target_state_must_match_qubit_count():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 18

`experiment = QuantumExperiment(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 19

`algorithm="grover",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 20

`num_qubits=2,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 21

`target_state="101",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 22

`iterations=1,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 23

`shots=1024,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 24

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 25

`(blank)`

Blank line used to separate nearby statements.
### Line 26

`with pytest.raises(ValueError):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 27

`validate_experiment(experiment)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 28

`(blank)`

Blank line used to separate nearby statements.
### Line 29

`def test_target_state_must_be_binary():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 30

`experiment = QuantumExperiment(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 31

`algorithm="grover",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 32

`num_qubits=2,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 33

`target_state="1A",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 34

`iterations=1,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 35

`shots=1024,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 36

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 37

`(blank)`

Blank line used to separate nearby statements.
### Line 38

`with pytest.raises(ValueError):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 39

`validate_experiment(experiment)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 40

`(blank)`

Blank line used to separate nearby statements.
### Line 41

`def test_only_grover_is_supported():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 42

`experiment = QuantumExperiment(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 43

`algorithm="qft",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 44

`num_qubits=2,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 45

`target_state="11",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 46

`iterations=1,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 47

`shots=1024,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 48

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 49

`(blank)`

Blank line used to separate nearby statements.
### Line 50

`with pytest.raises(ValueError):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 51

`validate_experiment(experiment)`

Calls a function or method; its arguments carry the data needed for this operation.

## Nearby Files

[tests/quantum/test_circuit_metadata.py](test_circuit_metadata.py.md), [tests/quantum/test_engine.py](test_engine.py.md), [tests/quantum/test_execution.py](test_execution.py.md), [tests/quantum/test_grover.py](test_grover.py.md), [tests/quantum/test_package.py](test_package.py.md), [tests/quantum/test_public_api.py](test_public_api.py.md), [tests/quantum/test_registry.py](test_registry.py.md), [tests/quantum/test_results.py](test_results.py.md)
