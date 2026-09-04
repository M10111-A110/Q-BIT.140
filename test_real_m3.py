from backend.quantum import QuantumExperiment, run_experiment

experiment = QuantumExperiment(
    algorithm="grover",
    num_qubits=3,
    target_state="101",
    iterations=2,
    shots=1024,
)

result = run_experiment(experiment)
real_result = result.to_dict()

print("Real M3 simulation result:")
print(real_result)