from .schemas import QuantumExperiment

def validate_experiment(experiment: QuantumExperiment) -> None:
    if experiment.algorithm.lower() != "grover":
        raise ValueError("Only Grover's Algorithm is supported")

    if len(experiment.target_state) != experiment.num_qubits:
        raise ValueError("Target state length must match the number of qubits.")

    if not all(bit in "01" for bit in experiment.target_state):
        raise ValueError("Target state must contain only binary values: 0 or 1.")
    