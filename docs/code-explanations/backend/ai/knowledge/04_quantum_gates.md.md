# Explanation: `backend/ai/knowledge/04_quantum_gates.md`

## Purpose

This page explains the meaningful behavior in `backend/ai/knowledge/04_quantum_gates.md`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```markdown
# Quantum Gates

Quantum gates transform quantum states. For ideal circuit evolution, |ψ'⟩ =
U|ψ⟩, where U is a unitary matrix.

## Pauli-X

Acts similarly to a classical NOT operation on computational-basis states:
X|0⟩ = |1⟩, X|1⟩ = |0⟩.

## Pauli-Y

Introduces both a basis-state transformation and complex phase factors. For
the MVP, learners primarily need to recognize that Pauli-Y is a
single-qubit unitary gate and understand that gates can modify amplitudes
and phases.

## Pauli-Z

Leaves |0⟩ unchanged and adds a phase factor of -1 to |1⟩: Z|0⟩ = |0⟩, Z|1⟩
= -|1⟩.

## Hadamard Gate

Especially important for understanding superposition and Grover's
algorithm. H = (1/√2) × [[1, 1], [1, -1]].

Important transformations:
- H|0⟩ = (|0⟩ + |1⟩) / √2
- H|1⟩ = (|0⟩ - |1⟩) / √2

Applying H to |0⟩ creates an equal superposition. Repeated
computational-basis measurements ideally produce approximately 50% 0 and
50% 1.

**Common misconception:** The approximately 50/50 measurement result does
not mean the quantum state before measurement is a classical 50/50 random
variable. The state has amplitudes and phase information that can
participate in interference.

## S and T Gates

Phase gates. They change the phase of quantum amplitudes without simply
acting like classical bit flips. For the MVP, the important conceptual
point is: quantum gates can modify phase as well as the probabilities that
will eventually be observed. Phase becomes important because interference
depends on relative phase.

## CNOT

A two-qubit controlled gate with one control qubit and one target qubit.
The target is flipped when the control is in |1⟩.

Transformations:
- |00⟩ → |00⟩
- |01⟩ → |01⟩
- |10⟩ → |11⟩
- |11⟩ → |10⟩

CNOT is important for understanding multi-qubit circuits and entanglement.

```

## Line Notes

### Line 1

`# Quantum Gates`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 2

`(blank)`

Blank line used to separate nearby statements.
### Line 3

`Quantum gates transform quantum states. For ideal circuit evolution, |ψ'⟩ =`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 4

`U|ψ⟩, where U is a unitary matrix.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 5

`(blank)`

Blank line used to separate nearby statements.
### Line 6

`## Pauli-X`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 7

`(blank)`

Blank line used to separate nearby statements.
### Line 8

`Acts similarly to a classical NOT operation on computational-basis states:`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 9

`X|0⟩ = |1⟩, X|1⟩ = |0⟩.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 10

`(blank)`

Blank line used to separate nearby statements.
### Line 11

`## Pauli-Y`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 12

`(blank)`

Blank line used to separate nearby statements.
### Line 13

`Introduces both a basis-state transformation and complex phase factors. For`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 14

`the MVP, learners primarily need to recognize that Pauli-Y is a`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 15

`single-qubit unitary gate and understand that gates can modify amplitudes`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 16

`and phases.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 17

`(blank)`

Blank line used to separate nearby statements.
### Line 18

`## Pauli-Z`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 19

`(blank)`

Blank line used to separate nearby statements.
### Line 20

`Leaves |0⟩ unchanged and adds a phase factor of -1 to |1⟩: Z|0⟩ = |0⟩, Z|1⟩`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 21

`= -|1⟩.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 22

`(blank)`

Blank line used to separate nearby statements.
### Line 23

`## Hadamard Gate`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 24

`(blank)`

Blank line used to separate nearby statements.
### Line 25

`Especially important for understanding superposition and Grover's`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 26

`algorithm. H = (1/√2) × [[1, 1], [1, -1]].`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 27

`(blank)`

Blank line used to separate nearby statements.
### Line 28

`Important transformations:`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 29

`- H|0⟩ = (|0⟩ + |1⟩) / √2`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 30

`- H|1⟩ = (|0⟩ - |1⟩) / √2`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 31

`(blank)`

Blank line used to separate nearby statements.
### Line 32

`Applying H to |0⟩ creates an equal superposition. Repeated`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 33

`computational-basis measurements ideally produce approximately 50% 0 and`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 34

`50% 1.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 35

`(blank)`

Blank line used to separate nearby statements.
### Line 36

`**Common misconception:** The approximately 50/50 measurement result does`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 37

`not mean the quantum state before measurement is a classical 50/50 random`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 38

`variable. The state has amplitudes and phase information that can`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 39

`participate in interference.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 40

`(blank)`

Blank line used to separate nearby statements.
### Line 41

`## S and T Gates`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 42

`(blank)`

Blank line used to separate nearby statements.
### Line 43

`Phase gates. They change the phase of quantum amplitudes without simply`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 44

`acting like classical bit flips. For the MVP, the important conceptual`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 45

`point is: quantum gates can modify phase as well as the probabilities that`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 46

`will eventually be observed. Phase becomes important because interference`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 47

`depends on relative phase.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 48

`(blank)`

Blank line used to separate nearby statements.
### Line 49

`## CNOT`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 50

`(blank)`

Blank line used to separate nearby statements.
### Line 51

`A two-qubit controlled gate with one control qubit and one target qubit.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 52

`The target is flipped when the control is in |1⟩.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 53

`(blank)`

Blank line used to separate nearby statements.
### Line 54

`Transformations:`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 55

`- |00⟩ → |00⟩`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 56

`- |01⟩ → |01⟩`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 57

`- |10⟩ → |11⟩`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 58

`- |11⟩ → |10⟩`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 59

`(blank)`

Blank line used to separate nearby statements.
### Line 60

`CNOT is important for understanding multi-qubit circuits and entanglement.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.

## Nearby Files

[backend/ai/knowledge/00_purpose_and_scope.md](00_purpose_and_scope.md.md), [backend/ai/knowledge/01_math_linear_algebra.md](01_math_linear_algebra.md.md), [backend/ai/knowledge/02_math_probability.md](02_math_probability.md.md), [backend/ai/knowledge/03_quantum_foundations.md](03_quantum_foundations.md.md), [backend/ai/knowledge/05_multi_qubit_entanglement.md](05_multi_qubit_entanglement.md.md), [backend/ai/knowledge/06_quantum_circuits.md](06_quantum_circuits.md.md), [backend/ai/knowledge/07_grovers_algorithm.md](07_grovers_algorithm.md.md), [backend/ai/knowledge/08_qiskit_practical.md](08_qiskit_practical.md.md)
