# Explanation: `backend/ai/knowledge/09_common_misconceptions.md`

## Purpose

This page explains the meaningful behavior in `backend/ai/knowledge/09_common_misconceptions.md`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```markdown
# Common Misconceptions

The AI should actively avoid reinforcing these misconceptions.

## "A qubit is both 0 and 1 like two classical bits."
Better: A qubit can be in a quantum superposition of computational-basis
states. Measurement produces a classical outcome according to the state's
probabilities.

## "Superposition is just classical randomness."
Better: A quantum superposition contains amplitudes and phase information
that can produce interference. It is not merely a classical probability
distribution.

## "An amplitude is the same thing as probability."
Better: P(x) = |αx|^2. Amplitudes determine measurement probabilities
through squared magnitude.

## "Measurement reveals the complete quantum state."
Better: A single measurement gives a classical outcome. Repeated
measurements can estimate an outcome distribution.

## "Hadamard always produces a 50/50 final result."
Better: Hadamard applied to |0⟩ creates an equal superposition, which gives
50/50 computational-basis measurement probabilities. Later gates can change
the state and therefore the final distribution.

## "The oracle tells the computer the answer."
Better: The oracle marks the desired state, typically through a phase
change. The diffusion step then enables amplitude amplification.

## "Grover always gives the answer with 100% probability."
Better: Grover amplifies the target state's probability. The exact result
depends on the search-space size, number of iterations, oracle, and
execution conditions.

## "More Grover iterations always improve the result."
Better: Grover's amplitude amplification is oscillatory. After an optimal
region, additional iterations can decrease the target probability.

## "Counts are exact probabilities."
Better: Counts are finite-shot observations. Normalized counts provide
empirical probabilities that approximate the underlying distribution.

```

## Line Notes

### Line 1

`# Common Misconceptions`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 2

`(blank)`

Blank line used to separate nearby statements.
### Line 3

`The AI should actively avoid reinforcing these misconceptions.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 4

`(blank)`

Blank line used to separate nearby statements.
### Line 5

`## "A qubit is both 0 and 1 like two classical bits."`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 6

`Better: A qubit can be in a quantum superposition of computational-basis`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 7

`states. Measurement produces a classical outcome according to the state's`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 8

`probabilities.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 9

`(blank)`

Blank line used to separate nearby statements.
### Line 10

`## "Superposition is just classical randomness."`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 11

`Better: A quantum superposition contains amplitudes and phase information`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 12

`that can produce interference. It is not merely a classical probability`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 13

`distribution.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 14

`(blank)`

Blank line used to separate nearby statements.
### Line 15

`## "An amplitude is the same thing as probability."`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 16

`Better: P(x) = |αx|^2. Amplitudes determine measurement probabilities`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 17

`through squared magnitude.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 18

`(blank)`

Blank line used to separate nearby statements.
### Line 19

`## "Measurement reveals the complete quantum state."`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 20

`Better: A single measurement gives a classical outcome. Repeated`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 21

`measurements can estimate an outcome distribution.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 22

`(blank)`

Blank line used to separate nearby statements.
### Line 23

`## "Hadamard always produces a 50/50 final result."`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 24

`Better: Hadamard applied to |0⟩ creates an equal superposition, which gives`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 25

`50/50 computational-basis measurement probabilities. Later gates can change`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 26

`the state and therefore the final distribution.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 27

`(blank)`

Blank line used to separate nearby statements.
### Line 28

`## "The oracle tells the computer the answer."`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 29

`Better: The oracle marks the desired state, typically through a phase`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 30

`change. The diffusion step then enables amplitude amplification.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 31

`(blank)`

Blank line used to separate nearby statements.
### Line 32

`## "Grover always gives the answer with 100% probability."`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 33

`Better: Grover amplifies the target state's probability. The exact result`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 34

`depends on the search-space size, number of iterations, oracle, and`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 35

`execution conditions.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 36

`(blank)`

Blank line used to separate nearby statements.
### Line 37

`## "More Grover iterations always improve the result."`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 38

`Better: Grover's amplitude amplification is oscillatory. After an optimal`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 39

`region, additional iterations can decrease the target probability.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 40

`(blank)`

Blank line used to separate nearby statements.
### Line 41

`## "Counts are exact probabilities."`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 42

`Better: Counts are finite-shot observations. Normalized counts provide`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 43

`empirical probabilities that approximate the underlying distribution.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.

## Nearby Files

[backend/ai/knowledge/00_purpose_and_scope.md](00_purpose_and_scope.md.md), [backend/ai/knowledge/01_math_linear_algebra.md](01_math_linear_algebra.md.md), [backend/ai/knowledge/02_math_probability.md](02_math_probability.md.md), [backend/ai/knowledge/03_quantum_foundations.md](03_quantum_foundations.md.md), [backend/ai/knowledge/04_quantum_gates.md](04_quantum_gates.md.md), [backend/ai/knowledge/05_multi_qubit_entanglement.md](05_multi_qubit_entanglement.md.md), [backend/ai/knowledge/06_quantum_circuits.md](06_quantum_circuits.md.md), [backend/ai/knowledge/07_grovers_algorithm.md](07_grovers_algorithm.md.md)
