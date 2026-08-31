# Grover's Algorithm — MVP Algorithm

Grover's algorithm is the single quantum algorithm in the Q-BIT MVP.

## Problem

Grover's algorithm addresses an unstructured search problem. Given a search
space of N possible items and an oracle that marks the desired solution,
Grover's algorithm can find a marked item using approximately O(√N) oracle
queries, compared with O(N) queries for classical exhaustive search.

The MVP should focus on understanding the algorithm's mechanism rather than
making broad claims about practical quantum speedups.

## High-Level Structure

Initialize Qubits → Create Superposition → Oracle → Diffusion / Amplitude
Amplification → Repeat → Measure.

## Initialization

The algorithm begins with qubits in a known computational-basis state,
commonly |0⟩^⊗n, where n is the number of search qubits.

## Creating the Search-Space Superposition

Hadamard gates are applied to create an equal superposition: H^⊗n |0⟩^⊗n.
The resulting state gives all N = 2^n search states equal initial
amplitudes.

## Oracle

The oracle marks the desired solution. Conceptually, the oracle applies a
phase change to the marked state: O|w⟩ = -|w⟩, while for an unmarked state,
O|x⟩ = |x⟩.

**Important point:** The oracle does not directly output the answer to the
learner. It marks the target through phase so that later interference can
amplify the target's amplitude.

## Diffusion Operator

Often called the inversion-about-the-mean operation. Its role is to
transform the amplitudes after the oracle has marked the target.

Conceptually: Oracle marks target (sign flips) → Diffusion → Target
amplitude increases.

The combined oracle and diffusion operation is one **Grover iteration**. A
common mathematical representation is D = 2|s⟩⟨s| - I, where |s⟩ is the
equal-superposition state.

## Amplitude Amplification

The central mechanism of Grover's algorithm. The algorithm does not make
the target appear with probability 1 after a single oracle call in general.
Instead, repeated Grover iterations increase the target state's amplitude
and therefore its measurement probability.

## Number of Iterations

For a single marked item in a search space of size N, the useful number of
Grover iterations is approximately (π/4)√N, with the exact optimal integer
depending on the problem size and implementation.

Too few iterations may leave the target probability lower than desired. Too
many iterations can reduce the target probability again because Grover
evolution is oscillatory.

**AI explanation rule:** If discussing a specific circuit, use the actual
circuit configuration and verified simulator output rather than claiming
that the target must occur with exactly 100% probability.

## Measurement

After the chosen number of Grover iterations, the search register is
measured. The desired state should have a significantly increased
measurement probability compared with the initial uniform distribution,
assuming the oracle and circuit are correctly implemented. Repeated shots
produce a distribution of observed outcomes.

## Concept Dependency Chain

Complex Numbers → Vectors → Matrices → Normalization → Matrix-Vector
Multiplication → Quantum States → Quantum Circuits → Quantum Gates → Grover
Components.

Probability thread: Probability → Amplitude Magnitude → Measurement
Probability → Counts/Empirical Probability → Interpreting Grover Output.

Grover-specific dependencies: Qubit → Superposition → Multi-Qubit States →
Hadamard → Oracle → Phase Marking → Diffusion → Amplitude Amplification →
Grover Iteration → Measurement.
