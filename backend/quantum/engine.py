from .algorithms.grover import build_grover_circuit
from .execution import execute_circuit
from .results import SimulationResult
from .schemas import QuantumExperiment
from .validator import validate_experiment


def run_experiment(experiment: QuantumExperiment) -> SimulationResult:
    validate_experiment(experiment)

    algo = experiment.algorithm.lower()
    if algo == "grover":
        if experiment.num_qubits != 2:
            raise NotImplementedError(
                f"Grover's algorithm currently only supports 2 qubits, got {experiment.num_qubits} qubits."
            )
        circuit = build_grover_circuit(
            num_qubits=experiment.num_qubits,
            target_state=experiment.target_state,
            iterations=experiment.iterations,
        )
    else:
        raise NotImplementedError(f"Algorithm '{experiment.algorithm}' is not supported.")

    counts = execute_circuit(circuit, shots=experiment.shots)

    return SimulationResult(
        algorithm=experiment.algorithm,
        target_state=experiment.target_state,
        shots=experiment.shots,
        counts=counts,
    )
