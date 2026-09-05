# Qiskit / Practical Concepts

The MVP uses Qiskit and Qiskit Aer as the primary quantum framework and
simulator.

## Circuit Construction

The learner may construct a circuit conceptually by selecting gates and
applying them to qubits. The AI should be able to explain: which gate was
applied; which qubit it acts on; how the gate changes the state
conceptually; how the operation relates to the current lesson.

## Execution

The quantum execution layer (M3) is responsible for actual circuit
execution. The AI should receive execution results through the defined
system interfaces rather than independently executing or fabricating
results.

## Visualization

Useful representations include: circuit diagrams; measurement
distributions; state-vector information where appropriate; Bloch-sphere
representation for individual-qubit states.

A Bloch sphere is useful for visualizing an individual qubit state, but it
is not a complete representation of an arbitrary multi-qubit entangled
state.
