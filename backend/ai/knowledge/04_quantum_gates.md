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
