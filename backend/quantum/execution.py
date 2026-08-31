from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

def execute_circuit(
        circuit: QuantumCircuit,
        shots: int = 1024,
) -> dict[str, int]:
    simulator = AerSimulator()

    result = simulator.run(
        circuit,
        shots=shots,
    ).result()

    return result.get_counts()