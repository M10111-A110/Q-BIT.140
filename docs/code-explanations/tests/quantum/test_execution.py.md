# Explanation: `tests/quantum/test_execution.py`

## Purpose

This page explains the meaningful behavior in `tests/quantum/test_execution.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
import pytest

from backend.quantum.algorithms.grover import build_grover_circuit
from backend.quantum.execution import execute_circuit


@pytest.mark.parametrize("target_state", ["00", "01", "10", "11"])
def test_grover_2qubit_finds_target_state(target_state):
    circuit = build_grover_circuit(
        num_qubits=2,
        target_state=target_state,
        iterations=1,
    )

    counts = execute_circuit(circuit, shots=1024)

    assert counts[target_state] == 1024


@pytest.mark.parametrize("target_state", ["000", "010", "101", "110", "111"])
def test_grover_3qubit_amplifies_target_state(target_state):
    circuit = build_grover_circuit(
        num_qubits=3,
        target_state=target_state,
        iterations=2,
    )

    counts = execute_circuit(circuit, shots=1024)
    top_state = max(counts, key=counts.get)

    assert top_state == target_state
    # 2 iterations on 3 qubits yields ~94.5% theoretical probability
    assert counts[target_state] > 850


@pytest.mark.parametrize("target_state", ["0000", "0110", "1001", "1111"])
def test_grover_4qubit_amplifies_target_state(target_state):
    circuit = build_grover_circuit(
        num_qubits=4,
        target_state=target_state,
        iterations=3,
    )

    counts = execute_circuit(circuit, shots=1024)
    top_state = max(counts, key=counts.get)

    assert top_state == target_state
    # 3 iterations on 4 qubits yields ~96% theoretical probability
    assert counts[target_state] > 850


@pytest.mark.parametrize("target_state", ["00000", "01010", "10101", "11111"])
def test_grover_5qubit_amplifies_target_state(target_state):
    circuit = build_grover_circuit(
        num_qubits=5,
        target_state=target_state,
        iterations=4,
    )

    counts = execute_circuit(circuit, shots=1024)
    top_state = max(counts, key=counts.get)

    assert top_state == target_state
    # 4 iterations on 5 qubits yields ~99.9% theoretical probability
    assert counts[target_state] > 900


```

## Line Notes

### Line 1

`import pytest`

Imports a dependency or project symbol so later code can use it by name.
### Line 2

`(blank)`

Blank line used to separate nearby statements.
### Line 3

`from backend.quantum.algorithms.grover import build_grover_circuit`

Imports a dependency or project symbol so later code can use it by name.
### Line 4

`from backend.quantum.execution import execute_circuit`

Imports a dependency or project symbol so later code can use it by name.
### Line 5

`(blank)`

Blank line used to separate nearby statements.
### Line 7

`@pytest.mark.parametrize("target_state", ["00", "01", "10", "11"])`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 8

`def test_grover_2qubit_finds_target_state(target_state):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 9

`circuit = build_grover_circuit(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 10

`num_qubits=2,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 11

`target_state=target_state,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 12

`iterations=1,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 13

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 14

`(blank)`

Blank line used to separate nearby statements.
### Line 15

`counts = execute_circuit(circuit, shots=1024)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 16

`(blank)`

Blank line used to separate nearby statements.
### Line 17

`assert counts[target_state] == 1024`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 18

`(blank)`

Blank line used to separate nearby statements.
### Line 20

`@pytest.mark.parametrize("target_state", ["000", "010", "101", "110", "111"])`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 21

`def test_grover_3qubit_amplifies_target_state(target_state):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 22

`circuit = build_grover_circuit(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 23

`num_qubits=3,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 24

`target_state=target_state,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 25

`iterations=2,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 26

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 27

`(blank)`

Blank line used to separate nearby statements.
### Line 28

`counts = execute_circuit(circuit, shots=1024)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 29

`top_state = max(counts, key=counts.get)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 30

`(blank)`

Blank line used to separate nearby statements.
### Line 31

`assert top_state == target_state`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 32

`# 2 iterations on 3 qubits yields ~94.5% theoretical probability`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 33

`assert counts[target_state] > 850`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 34

`(blank)`

Blank line used to separate nearby statements.
### Line 36

`@pytest.mark.parametrize("target_state", ["0000", "0110", "1001", "1111"])`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 37

`def test_grover_4qubit_amplifies_target_state(target_state):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 38

`circuit = build_grover_circuit(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 39

`num_qubits=4,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 40

`target_state=target_state,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 41

`iterations=3,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 42

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 43

`(blank)`

Blank line used to separate nearby statements.
### Line 44

`counts = execute_circuit(circuit, shots=1024)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 45

`top_state = max(counts, key=counts.get)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 46

`(blank)`

Blank line used to separate nearby statements.
### Line 47

`assert top_state == target_state`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 48

`# 3 iterations on 4 qubits yields ~96% theoretical probability`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 49

`assert counts[target_state] > 850`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 50

`(blank)`

Blank line used to separate nearby statements.
### Line 52

`@pytest.mark.parametrize("target_state", ["00000", "01010", "10101", "11111"])`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 53

`def test_grover_5qubit_amplifies_target_state(target_state):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 54

`circuit = build_grover_circuit(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 55

`num_qubits=5,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 56

`target_state=target_state,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 57

`iterations=4,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 58

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 59

`(blank)`

Blank line used to separate nearby statements.
### Line 60

`counts = execute_circuit(circuit, shots=1024)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 61

`top_state = max(counts, key=counts.get)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 62

`(blank)`

Blank line used to separate nearby statements.
### Line 63

`assert top_state == target_state`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 64

`# 4 iterations on 5 qubits yields ~99.9% theoretical probability`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 65

`assert counts[target_state] > 900`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.

## Nearby Files

[tests/quantum/test_circuit_metadata.py](test_circuit_metadata.py.md), [tests/quantum/test_engine.py](test_engine.py.md), [tests/quantum/test_grover.py](test_grover.py.md), [tests/quantum/test_package.py](test_package.py.md), [tests/quantum/test_public_api.py](test_public_api.py.md), [tests/quantum/test_registry.py](test_registry.py.md), [tests/quantum/test_results.py](test_results.py.md), [tests/quantum/test_schema.py](test_schema.py.md)
