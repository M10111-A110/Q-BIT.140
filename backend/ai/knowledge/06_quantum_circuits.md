# Quantum Circuits

A quantum circuit represents a sequence of operations applied to qubits. A
basic circuit can contain: qubit initialization, quantum gates, measurement,
classical output.

Conceptually: Initial state → Quantum gates → Final state → Measurement →
Classical result.

## Circuit Execution

For a simulator using repeated shots: Circuit → Execute many times → Counts
→ Empirical probabilities.

## Shots

A shot is one execution of a circuit. If a circuit is executed for 1000
shots, there are 1000 sampled measurement outcomes.

## Counts

Counts record how often each classical outcome occurred. Example: outcome
"00" occurred 491 times, "11" occurred 498 times, out of 1000 shots. The
exact counts depend on the circuit and execution conditions.

## Probabilities

Counts can be normalized: P(x) ≈ count(x) / total_shots. For example, 498
occurrences of "11" in 1000 shots gives P(11) ≈ 0.498.

**AI rule:** If actual counts or probabilities are provided by M3, explain
those values as verified simulation evidence. Do not replace them with an
invented ideal result.
