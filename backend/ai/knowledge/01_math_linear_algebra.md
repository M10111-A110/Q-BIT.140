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
