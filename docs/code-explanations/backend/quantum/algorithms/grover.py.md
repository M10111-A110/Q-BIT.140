# Explanation: `backend/quantum/algorithms/grover.py`

## Purpose

This page explains the meaningful behavior in `backend/quantum/algorithms/grover.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
from qiskit import QuantumCircuit


def _apply_multi_controlled_z(circuit: QuantumCircuit, num_qubits: int) -> None:
    """Applies a multi-controlled Z gate (phase inversion for |1...1> state)."""
    if num_qubits == 2:
        circuit.cz(0, 1)
    else:
        target_qubit = num_qubits - 1
        control_qubits = list(range(num_qubits - 1))
        circuit.h(target_qubit)
        circuit.mcx(control_qubits, target_qubit)
        circuit.h(target_qubit)


def _apply_oracle(circuit: QuantumCircuit, target_state: str) -> None:
    num_qubits = len(target_state)
    target_bits = target_state[::-1]

    for qubit, bit in enumerate(target_bits):
        if bit == "0":
            circuit.x(qubit)

    _apply_multi_controlled_z(circuit, num_qubits)

    for qubit, bit in enumerate(target_bits):
        if bit == "0":
            circuit.x(qubit)


def _apply_diffusion(circuit: QuantumCircuit, num_qubits: int) -> None:
    for qubit in range(num_qubits):
        circuit.h(qubit)
        circuit.x(qubit)

    _apply_multi_controlled_z(circuit, num_qubits)

    for qubit in range(num_qubits):
        circuit.x(qubit)
        circuit.h(qubit)


def build_grover_circuit(
    num_qubits: int,
    target_state: str,
    iterations: int = 1,
) -> QuantumCircuit:
    if num_qubits < 2:
        raise ValueError(
            f"Grover circuit requires at least 2 qubits, got {num_qubits}."
        )

    if len(target_state) != num_qubits:
        raise ValueError(
            f"Target state length ({len(target_state)}) must match number of qubits ({num_qubits})."
        )

    if not all(bit in "01" for bit in target_state):
        raise ValueError("Target state must contain only binary values: 0 or 1.")

    if iterations < 1:
        raise ValueError("Iterations must be at least 1.")

    circuit = QuantumCircuit(num_qubits, num_qubits)

    # Create uniform superposition
    for qubit in range(num_qubits):
        circuit.h(qubit)

    # Grover Iterations
    for _ in range(iterations):
        _apply_oracle(circuit, target_state)
        _apply_diffusion(circuit, num_qubits)

    # Measure
    circuit.measure(range(num_qubits), range(num_qubits))

    return circuit


```

## Line Notes

### Line 1

`from qiskit import QuantumCircuit`

Imports a dependency or project symbol so later code can use it by name.
### Line 2

`(blank)`

Blank line used to separate nearby statements.
### Line 4

`def _apply_multi_controlled_z(circuit: QuantumCircuit, num_qubits: int) -> None:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 5

`"""Applies a multi-controlled Z gate (phase inversion for |1...1> state)."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 6

`if num_qubits == 2:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 7

`circuit.cz(0, 1)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 8

`else:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 9

`target_qubit = num_qubits - 1`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 10

`control_qubits = list(range(num_qubits - 1))`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 11

`circuit.h(target_qubit)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 12

`circuit.mcx(control_qubits, target_qubit)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 13

`circuit.h(target_qubit)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 14

`(blank)`

Blank line used to separate nearby statements.
### Line 16

`def _apply_oracle(circuit: QuantumCircuit, target_state: str) -> None:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 17

`num_qubits = len(target_state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 18

`target_bits = target_state[::-1]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 19

`(blank)`

Blank line used to separate nearby statements.
### Line 20

`for qubit, bit in enumerate(target_bits):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 21

`if bit == "0":`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 22

`circuit.x(qubit)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 23

`(blank)`

Blank line used to separate nearby statements.
### Line 24

`_apply_multi_controlled_z(circuit, num_qubits)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 25

`(blank)`

Blank line used to separate nearby statements.
### Line 26

`for qubit, bit in enumerate(target_bits):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 27

`if bit == "0":`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 28

`circuit.x(qubit)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 29

`(blank)`

Blank line used to separate nearby statements.
### Line 31

`def _apply_diffusion(circuit: QuantumCircuit, num_qubits: int) -> None:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 32

`for qubit in range(num_qubits):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 33

`circuit.h(qubit)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 34

`circuit.x(qubit)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 35

`(blank)`

Blank line used to separate nearby statements.
### Line 36

`_apply_multi_controlled_z(circuit, num_qubits)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 37

`(blank)`

Blank line used to separate nearby statements.
### Line 38

`for qubit in range(num_qubits):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 39

`circuit.x(qubit)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 40

`circuit.h(qubit)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 41

`(blank)`

Blank line used to separate nearby statements.
### Line 43

`def build_grover_circuit(`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 44

`num_qubits: int,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 45

`target_state: str,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 46

`iterations: int = 1,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 47

`) -> QuantumCircuit:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 48

`if num_qubits < 2:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 49

`raise ValueError(`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 50

`f"Grover circuit requires at least 2 qubits, got {num_qubits}."`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 51

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 52

`(blank)`

Blank line used to separate nearby statements.
### Line 53

`if len(target_state) != num_qubits:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 54

`raise ValueError(`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 55

`f"Target state length ({len(target_state)}) must match number of qubits ({num_qubits})."`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 56

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 57

`(blank)`

Blank line used to separate nearby statements.
### Line 58

`if not all(bit in "01" for bit in target_state):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 59

`raise ValueError("Target state must contain only binary values: 0 or 1.")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 60

`(blank)`

Blank line used to separate nearby statements.
### Line 61

`if iterations < 1:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 62

`raise ValueError("Iterations must be at least 1.")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 63

`(blank)`

Blank line used to separate nearby statements.
### Line 64

`circuit = QuantumCircuit(num_qubits, num_qubits)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 65

`(blank)`

Blank line used to separate nearby statements.
### Line 66

`# Create uniform superposition`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 67

`for qubit in range(num_qubits):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 68

`circuit.h(qubit)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 69

`(blank)`

Blank line used to separate nearby statements.
### Line 70

`# Grover Iterations`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 71

`for _ in range(iterations):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 72

`_apply_oracle(circuit, target_state)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 73

`_apply_diffusion(circuit, num_qubits)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 74

`(blank)`

Blank line used to separate nearby statements.
### Line 75

`# Measure`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 76

`circuit.measure(range(num_qubits), range(num_qubits))`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 77

`(blank)`

Blank line used to separate nearby statements.
### Line 78

`return circuit`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.

## Nearby Files

[backend/quantum/algorithms/__init__.py](__init__.py.md)
