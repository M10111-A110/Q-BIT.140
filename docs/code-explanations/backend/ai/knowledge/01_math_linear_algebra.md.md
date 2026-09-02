# Explanation: `backend/ai/knowledge/01_math_linear_algebra.md`

## Purpose

This page explains the meaningful behavior in `backend/ai/knowledge/01_math_linear_algebra.md`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```markdown
# Linear Algebra

Linear algebra is a core mathematical foundation for quantum computing.

## Scalars

A scalar is a single numerical quantity, e.g. 2, -3, 0.5. Quantum mechanics
also uses complex-valued scalars.

## Complex Numbers

A complex number has the form z = a + bi, where a, b are real numbers and
i^2 = -1.

The complex conjugate of z is z* = a - bi.

The squared magnitude is |z|^2 = z* · z.

Complex numbers are important because quantum amplitudes can be complex.

## Vectors

A vector is an ordered collection of numbers, e.g. [a, b].

A single-qubit state can be represented by a two-component complex vector.
For |ψ⟩ = α|0⟩ + β|1⟩, the corresponding state vector is [α, β].

## Vector Magnitude and Normalization

A valid pure single-qubit state satisfies |α|^2 + |β|^2 = 1. This is the
normalization condition. The squared magnitudes of the amplitudes become
measurement probabilities in the computational basis.

## Inner Product

The inner product compares vectors, written in Dirac notation as ⟨φ|ψ⟩.

For a normalized state, ⟨ψ|ψ⟩ = 1.

## Matrices

A matrix is a rectangular array of numbers. Quantum gates are commonly
represented by matrices.

## Matrix–Vector Multiplication

Applying a quantum gate to a state is represented as |ψ'⟩ = U|ψ⟩, where U is
the gate matrix.

Example: the Hadamard matrix H = (1/√2) × [[1, 1], [1, -1]] applied to |0⟩
gives H|0⟩ = (|0⟩ + |1⟩) / √2.

## Tensor Products

Multiple-qubit systems use tensor products. For example, |0⟩ ⊗ |1⟩ = |01⟩.

For two qubits, the computational basis contains |00⟩, |01⟩, |10⟩, |11⟩.

In general, an n-qubit pure state is represented using 2^n complex
amplitudes.

```

## Line Notes

### Line 1

`# Linear Algebra`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 2

`(blank)`

Blank line used to separate nearby statements.
### Line 3

`Linear algebra is a core mathematical foundation for quantum computing.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 4

`(blank)`

Blank line used to separate nearby statements.
### Line 5

`## Scalars`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 6

`(blank)`

Blank line used to separate nearby statements.
### Line 7

`A scalar is a single numerical quantity, e.g. 2, -3, 0.5. Quantum mechanics`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 8

`also uses complex-valued scalars.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 9

`(blank)`

Blank line used to separate nearby statements.
### Line 10

`## Complex Numbers`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 11

`(blank)`

Blank line used to separate nearby statements.
### Line 12

`A complex number has the form z = a + bi, where a, b are real numbers and`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 13

`i^2 = -1.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 14

`(blank)`

Blank line used to separate nearby statements.
### Line 15

`The complex conjugate of z is z* = a - bi.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 16

`(blank)`

Blank line used to separate nearby statements.
### Line 17

`The squared magnitude is |z|^2 = z* · z.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 18

`(blank)`

Blank line used to separate nearby statements.
### Line 19

`Complex numbers are important because quantum amplitudes can be complex.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 20

`(blank)`

Blank line used to separate nearby statements.
### Line 21

`## Vectors`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 22

`(blank)`

Blank line used to separate nearby statements.
### Line 23

`A vector is an ordered collection of numbers, e.g. [a, b].`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 24

`(blank)`

Blank line used to separate nearby statements.
### Line 25

`A single-qubit state can be represented by a two-component complex vector.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 26

`For |ψ⟩ = α|0⟩ + β|1⟩, the corresponding state vector is [α, β].`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 27

`(blank)`

Blank line used to separate nearby statements.
### Line 28

`## Vector Magnitude and Normalization`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 29

`(blank)`

Blank line used to separate nearby statements.
### Line 30

`A valid pure single-qubit state satisfies |α|^2 + |β|^2 = 1. This is the`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 31

`normalization condition. The squared magnitudes of the amplitudes become`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 32

`measurement probabilities in the computational basis.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 33

`(blank)`

Blank line used to separate nearby statements.
### Line 34

`## Inner Product`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 35

`(blank)`

Blank line used to separate nearby statements.
### Line 36

`The inner product compares vectors, written in Dirac notation as ⟨φ|ψ⟩.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 37

`(blank)`

Blank line used to separate nearby statements.
### Line 38

`For a normalized state, ⟨ψ|ψ⟩ = 1.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 39

`(blank)`

Blank line used to separate nearby statements.
### Line 40

`## Matrices`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 41

`(blank)`

Blank line used to separate nearby statements.
### Line 42

`A matrix is a rectangular array of numbers. Quantum gates are commonly`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 43

`represented by matrices.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 44

`(blank)`

Blank line used to separate nearby statements.
### Line 45

`## Matrix–Vector Multiplication`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 46

`(blank)`

Blank line used to separate nearby statements.
### Line 47

`Applying a quantum gate to a state is represented as |ψ'⟩ = U|ψ⟩, where U is`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 48

`the gate matrix.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 49

`(blank)`

Blank line used to separate nearby statements.
### Line 50

`Example: the Hadamard matrix H = (1/√2) × [[1, 1], [1, -1]] applied to |0⟩`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 51

`gives H|0⟩ = (|0⟩ + |1⟩) / √2.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 52

`(blank)`

Blank line used to separate nearby statements.
### Line 53

`## Tensor Products`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 54

`(blank)`

Blank line used to separate nearby statements.
### Line 55

`Multiple-qubit systems use tensor products. For example, |0⟩ ⊗ |1⟩ = |01⟩.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 56

`(blank)`

Blank line used to separate nearby statements.
### Line 57

`For two qubits, the computational basis contains |00⟩, |01⟩, |10⟩, |11⟩.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 58

`(blank)`

Blank line used to separate nearby statements.
### Line 59

`In general, an n-qubit pure state is represented using 2^n complex`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 60

`amplitudes.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.

## Nearby Files

[backend/ai/knowledge/00_purpose_and_scope.md](00_purpose_and_scope.md.md), [backend/ai/knowledge/02_math_probability.md](02_math_probability.md.md), [backend/ai/knowledge/03_quantum_foundations.md](03_quantum_foundations.md.md), [backend/ai/knowledge/04_quantum_gates.md](04_quantum_gates.md.md), [backend/ai/knowledge/05_multi_qubit_entanglement.md](05_multi_qubit_entanglement.md.md), [backend/ai/knowledge/06_quantum_circuits.md](06_quantum_circuits.md.md), [backend/ai/knowledge/07_grovers_algorithm.md](07_grovers_algorithm.md.md), [backend/ai/knowledge/08_qiskit_practical.md](08_qiskit_practical.md.md)
