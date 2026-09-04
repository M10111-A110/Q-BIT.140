# Multi-Qubit States and Entanglement

## Two-Qubit Basis

Two qubits have four computational-basis states: |00⟩, |01⟩, |10⟩, |11⟩.

A general pure two-qubit state can be written as |ψ⟩ = α00|00⟩ + α01|01⟩ +
α10|10⟩ + α11|11⟩, with normalized amplitudes summing (squared) to 1.

## Bell State Example

A standard entangled Bell state is |Φ+⟩ = (|00⟩ + |11⟩) / √2.

One circuit construction: start at |00⟩, apply Hadamard to the first qubit
to get (|00⟩ + |10⟩)/√2, then apply CNOT to get (|00⟩ + |11⟩)/√2.

Measuring both qubits in the computational basis ideally produces
correlated outcomes 00 or 11.

**Important misconception:** Entanglement is not merely "two bits having
the same random value." It is a property of a joint quantum state that
cannot, in general, be represented as independent states for the individual
qubits.
