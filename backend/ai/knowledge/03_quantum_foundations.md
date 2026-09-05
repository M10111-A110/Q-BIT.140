# Quantum Computing Foundations

## Classical Bit vs. Qubit

A classical bit has two possible logical values: 0, 1.

A qubit is the basic unit of quantum information. A pure single-qubit state
can be written as |ψ⟩ = α|0⟩ + β|1⟩, with |α|^2 + |β|^2 = 1.

**Important distinction:** A qubit in a superposition is not simply a
classical bit whose value is secretly random. The quantum state contains
amplitudes, including possible relative-phase information, which can affect
later interference.

## Dirac / Ket Notation

Quantum states are commonly represented using Dirac notation. Examples: |0⟩,
|1⟩. A general qubit state is |ψ⟩ = α|0⟩ + β|1⟩.

The notation |ψ⟩ is called a ket. The corresponding bra is ⟨ψ|.

## Superposition

Superposition describes a quantum state represented as a combination of
basis states. For example, |+⟩ = (|0⟩ + |1⟩) / √2 is an equal superposition.

Measurement in the computational basis gives P(0) = 1/2, P(1) = 1/2.

**Common misconception:** Do not explain superposition as "the qubit is
literally both 0 and 1 in the same classical sense." A better explanation
is: before measurement, the quantum state can be represented as a
superposition of basis states. Measurement produces a classical outcome
according to the state's probabilities.

## Measurement

Measurement converts quantum information into a classical observable
outcome. For |ψ⟩ = α|0⟩ + β|1⟩, computational-basis measurement gives P(0) =
|α|^2, P(1) = |β|^2.

A single measurement produces one classical outcome. Repeated measurements
can reveal the probability distribution.

**Important distinction:** Do not say that measurement "reads all
amplitudes directly." A measurement produces an outcome; repeated
measurements can be used to estimate the distribution.

## Unitary Evolution

Ideal quantum gates are represented by unitary transformations. A matrix U
is unitary if U†U = I, where U† is the conjugate transpose.

Unitary evolution preserves state normalization.
