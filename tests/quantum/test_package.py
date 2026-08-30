def test_package_exports():
    from backend.quantum import (
        QuantumExperiment,
        SimulationResult,
        run_experiment,
    )

    assert callable(run_experiment)
    assert QuantumExperiment is not None
    assert SimulationResult is not None
