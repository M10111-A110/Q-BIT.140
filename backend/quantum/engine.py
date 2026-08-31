from .execution import execute_circuit
from .registry import get_algorithm
from .results import SimulationResult
from .schemas import QuantumExperiment
from .validator import validate_experiment


def run_experiment(experiment: QuantumExperiment) -> SimulationResult:
    validate_experiment(experiment)

    algorithm = get_algorithm(experiment.algorithm)

    circuit = algorithm(
        num_qubits=experiment.num_qubits,
        target_state=experiment.target_state,
        iterations=experiment.iterations,
    )

    counts = execute_circuit(circuit, shots=experiment.shots)

    return SimulationResult(
        algorithm=experiment.algorithm,
        target_state=experiment.target_state,
        shots=experiment.shots,
        counts=counts,
    )