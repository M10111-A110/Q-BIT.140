# Probability

Probability is needed to understand quantum measurement and simulator
results.

## Probability Basics

A probability satisfies 0 ≤ P ≤ 1. For mutually exclusive and exhaustive
outcomes, the probabilities sum to 1.

## Amplitudes and Probabilities

Quantum amplitudes are **not** themselves measurement probabilities.

For |ψ⟩ = α|0⟩ + β|1⟩, computational-basis measurement gives:
- P(0) = |α|^2
- P(1) = |β|^2

Normalization gives P(0) + P(1) = 1.

## Counts and Probabilities

If an outcome occurs N_x times in N total shots, its empirical frequency is
P̂(x) = N_x / N.

The observed frequency approximates the underlying probability more closely
as the number of shots increases, subject to the simulator and execution
conditions.
