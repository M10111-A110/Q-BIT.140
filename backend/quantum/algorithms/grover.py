from qiskit import QuantumCircuit

#works currently only for 2 qubits
def _apply_oracle(circuit: QuantumCircuit, target_state: str) -> None:
    target_bits = target_state[::-1]

    for qubit, bit in enumerate(target_bits):
        if bit == "0":
            circuit.x(qubit)

    circuit.cz(0,1)

    for qubit, bit in enumerate(target_bits):
        if bit == "0":
            circuit.x(qubit)

def _apply_diffusion(circuit: QuantumCircuit) -> None:
    for qubit in range(2):
        circuit.h(qubit)
        circuit.x(qubit)

    circuit.cz(0,1)

    for qubit in range(2):
        circuit.x(qubit)
        circuit.h(qubit)

def build_grover_circuit(
        num_qubits: int,
        target_state: str,
        iterations: int=1,
) -> QuantumCircuit:
    circuit = QuantumCircuit(num_qubits, num_qubits)

    #Create uniform superposition
    for qubit in range(num_qubits):
        circuit.h(qubit)

    #Grover Iterations
    for _ in range(iterations):
        _apply_oracle(circuit, target_state)
        _apply_diffusion(circuit)

    #Measure
    circuit.measure(range(num_qubits), range(num_qubits))

    return circuit