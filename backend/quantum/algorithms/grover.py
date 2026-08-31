from qiskit import QuantumCircuit


def _apply_multi_controlled_z(circuit: QuantumCircuit, num_qubits: int) -> None:
    """Applies a multi-controlled Z gate (phase inversion for |1...1> state)."""
    if num_qubits == 2:
        circuit.cz(0, 1)
    else:
        target_qubit = num_qubits - 1
        control_qubits = list(range(num_qubits - 1))
        circuit.h(target_qubit)
        circuit.mcx(control_qubits, target_qubit)
        circuit.h(target_qubit)


def _apply_oracle(circuit: QuantumCircuit, target_state: str) -> None:
    num_qubits = len(target_state)
    target_bits = target_state[::-1]

    for qubit, bit in enumerate(target_bits):
        if bit == "0":
            circuit.x(qubit)

    _apply_multi_controlled_z(circuit, num_qubits)

    for qubit, bit in enumerate(target_bits):
        if bit == "0":
            circuit.x(qubit)


def _apply_diffusion(circuit: QuantumCircuit, num_qubits: int) -> None:
    for qubit in range(num_qubits):
        circuit.h(qubit)
        circuit.x(qubit)

    _apply_multi_controlled_z(circuit, num_qubits)

    for qubit in range(num_qubits):
        circuit.x(qubit)
        circuit.h(qubit)


def build_grover_circuit(
    num_qubits: int,
    target_state: str,
    iterations: int = 1,
) -> QuantumCircuit:
    if num_qubits < 2:
        raise ValueError(
            f"Grover circuit requires at least 2 qubits, got {num_qubits}."
        )

    if len(target_state) != num_qubits:
        raise ValueError(
            f"Target state length ({len(target_state)}) must match number of qubits ({num_qubits})."
        )

    if not all(bit in "01" for bit in target_state):
        raise ValueError("Target state must contain only binary values: 0 or 1.")

    if iterations < 1:
        raise ValueError("Iterations must be at least 1.")

    circuit = QuantumCircuit(num_qubits, num_qubits)

    # Create uniform superposition
    for qubit in range(num_qubits):
        circuit.h(qubit)

    # Grover Iterations
    for _ in range(iterations):
        _apply_oracle(circuit, target_state)
        _apply_diffusion(circuit, num_qubits)

    # Measure
    circuit.measure(range(num_qubits), range(num_qubits))

    return circuit
