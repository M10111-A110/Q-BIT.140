def test_package_exports():
    from backend.quantum import (
        CircuitMetadata,
        QuantumExperiment,
        SimulationResult,
        run_experiment,
    )

    assert callable(run_experiment)
    assert QuantumExperiment is not None
    assert SimulationResult is not None
    assert CircuitMetadata is not None
