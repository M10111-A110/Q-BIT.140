"""
Public API contract tests for the M3 Quantum Engine.

These tests simulate exactly how a downstream module (M1, M2, M4, M5, M6)
would consume M3.  They import ONLY from ``backend.quantum`` — never from
``qiskit``, ``qiskit_aer``, or any internal M3 module.

If any of these tests fail, it means a Qiskit object or an internal
implementation detail has leaked across the M3 public boundary.
"""
import json

import pytest

# ── The ONLY imports a downstream consumer should ever need ──────────────────
from backend.quantum import (
    CircuitMetadata,
    QuantumExperiment,
    SimulationResult,
    run_experiment,
)

# ── Helpers ──────────────────────────────────────────────────────────────────

#: Sentinel set of types that are acceptable anywhere in public M3 output.
#: Qiskit objects, numpy types, custom classes — none of these belong here.
_ALLOWED_PRIMITIVE_TYPES = (dict, list, str, int, float, bool, type(None))


def _assert_only_primitives(value, path: str = "result") -> None:
    """
    Recursively assert that ``value`` and all its children consist only of
    plain Python primitives.  Raises AssertionError with a descriptive path
    if a non-primitive is found.

    Does NOT import Qiskit — the check is purely structural.
    """
    if isinstance(value, dict):
        for k, v in value.items():
            assert isinstance(k, str), (
                f"{path}: dict key must be str, got {type(k)} for key={k!r}"
            )
            _assert_only_primitives(v, path=f"{path}[{k!r}]")
    elif isinstance(value, list):
        for i, item in enumerate(value):
            _assert_only_primitives(item, path=f"{path}[{i}]")
    else:
        assert isinstance(value, _ALLOWED_PRIMITIVE_TYPES), (
            f"Non-primitive type at {path}: {type(value).__module__}.{type(value).__qualname__}"
        )


# ── Shared fixture ────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def grover_result() -> SimulationResult:
    """
    Execute the exact workflow specified in the task brief and return the
    result.  Scoped to module so Aer runs only once for this test file.
    """
    experiment = QuantumExperiment(
        algorithm="grover",
        num_qubits=3,
        target_state="101",
        iterations=2,
        shots=1024,
    )
    return run_experiment(experiment)


# ── 1. Public package exports ─────────────────────────────────────────────────

class TestPublicPackageExports:
    def test_run_experiment_is_callable(self):
        assert callable(run_experiment)

    def test_quantum_experiment_is_exported(self):
        assert QuantumExperiment is not None

    def test_simulation_result_is_exported(self):
        assert SimulationResult is not None

    def test_circuit_metadata_is_exported(self):
        assert CircuitMetadata is not None


# ── 2. SimulationResult contract ─────────────────────────────────────────────

class TestSimulationResultContract:
    def test_result_is_simulation_result(self, grover_result):
        assert isinstance(grover_result, SimulationResult)

    def test_algorithm_field(self, grover_result):
        assert grover_result.algorithm == "grover"

    def test_target_state_field(self, grover_result):
        assert grover_result.target_state == "101"

    def test_shots_field(self, grover_result):
        assert grover_result.shots == 1024

    def test_counts_is_plain_dict(self, grover_result):
        assert type(grover_result.counts) is dict, (
            f"counts must be exactly dict, got {type(grover_result.counts)}"
        )

    def test_counts_values_are_int(self, grover_result):
        for state, count in grover_result.counts.items():
            assert isinstance(state, str), f"count key is not str: {type(state)}"
            assert isinstance(count, int), f"count value is not int: {type(count)}"

    def test_counts_sum_equals_shots(self, grover_result):
        assert sum(grover_result.counts.values()) == grover_result.shots

    def test_probabilities_is_dict(self, grover_result):
        assert isinstance(grover_result.probabilities, dict)

    def test_probabilities_values_are_float(self, grover_result):
        for state, prob in grover_result.probabilities.items():
            assert isinstance(state, str)
            assert isinstance(prob, float)

    def test_probabilities_sum_to_one(self, grover_result):
        assert abs(sum(grover_result.probabilities.values()) - 1.0) < 1e-9

    def test_target_probability_is_float(self, grover_result):
        assert isinstance(grover_result.target_probability, float)

    def test_target_probability_in_unit_interval(self, grover_result):
        assert 0.0 <= grover_result.target_probability <= 1.0

    def test_most_likely_state_is_str(self, grover_result):
        assert isinstance(grover_result.most_likely_state, str)

    def test_most_likely_state_is_in_counts(self, grover_result):
        assert grover_result.most_likely_state in grover_result.counts

    def test_grover_amplifies_target_state(self, grover_result):
        """Grover with 2 iterations on 3 qubits should amplify the target."""
        assert grover_result.most_likely_state == "101"
        assert grover_result.target_probability > 0.8


# ── 3. CircuitMetadata contract ───────────────────────────────────────────────

class TestCircuitMetadataContract:
    def test_circuit_is_not_none(self, grover_result):
        assert grover_result.circuit is not None

    def test_circuit_is_circuit_metadata(self, grover_result):
        assert isinstance(grover_result.circuit, CircuitMetadata)

    def test_num_qubits_matches_experiment(self, grover_result):
        assert grover_result.circuit.num_qubits == 3

    def test_num_clbits_matches_experiment(self, grover_result):
        assert grover_result.circuit.num_clbits == 3

    def test_depth_is_int(self, grover_result):
        assert isinstance(grover_result.circuit.depth, int)

    def test_depth_is_positive(self, grover_result):
        assert grover_result.circuit.depth > 0

    def test_gate_counts_is_dict(self, grover_result):
        assert isinstance(grover_result.circuit.gate_counts, dict)

    def test_gate_counts_keys_are_str(self, grover_result):
        for key in grover_result.circuit.gate_counts:
            assert isinstance(key, str), f"gate_count key is not str: {type(key)}"

    def test_gate_counts_values_are_int(self, grover_result):
        for val in grover_result.circuit.gate_counts.values():
            assert isinstance(val, int), f"gate_count value is not int: {type(val)}"

    def test_gate_counts_has_measure(self, grover_result):
        assert "measure" in grover_result.circuit.gate_counts
        assert grover_result.circuit.gate_counts["measure"] == 3

    def test_diagram_is_str(self, grover_result):
        assert isinstance(grover_result.circuit.diagram, str)

    def test_diagram_is_nonempty(self, grover_result):
        assert len(grover_result.circuit.diagram.strip()) > 0


# ── 4. No Qiskit objects in public output ────────────────────────────────────

class TestNoQiskitObjectsInPublicBoundary:
    """
    Verifies the encapsulation contract: nothing that crosses the M3 public
    boundary may be a Qiskit type.  These tests do NOT import Qiskit.
    """

    def test_counts_type_is_exactly_dict(self, grover_result):
        """
        Qiskit returns qiskit.result.counts.Counts from get_counts().
        That class subclasses dict, so isinstance(counts, dict) is True,
        but type(counts) is not dict — which would leak a Qiskit object.
        """
        assert type(grover_result.counts) is dict, (
            f"result.counts must be exactly dict (not a Qiskit subclass), "
            f"got {type(grover_result.counts)}"
        )

    def test_result_object_contains_only_primitives_recursively(self, grover_result):
        """
        Walk the dataclass fields directly (not via to_dict) and verify
        that every stored value is a plain Python primitive.
        """
        _assert_only_primitives(grover_result.algorithm, "result.algorithm")
        _assert_only_primitives(grover_result.target_state, "result.target_state")
        _assert_only_primitives(grover_result.shots, "result.shots")
        _assert_only_primitives(grover_result.counts, "result.counts")
        # circuit sub-fields
        meta = grover_result.circuit
        _assert_only_primitives(meta.num_qubits, "result.circuit.num_qubits")
        _assert_only_primitives(meta.num_clbits, "result.circuit.num_clbits")
        _assert_only_primitives(meta.depth, "result.circuit.depth")
        _assert_only_primitives(meta.gate_counts, "result.circuit.gate_counts")
        _assert_only_primitives(meta.diagram, "result.circuit.diagram")

    def test_to_dict_contains_only_primitives_recursively(self, grover_result):
        """
        Walk the entire to_dict() output and verify no Qiskit types survive.
        This is the contract M4 relies on before calling json.dumps().
        """
        _assert_only_primitives(grover_result.to_dict(), "result.to_dict()")


# ── 5. JSON round-trip ────────────────────────────────────────────────────────

class TestJsonRoundTrip:
    def test_to_dict_is_json_serializable(self, grover_result):
        """json.dumps must not raise."""
        payload = grover_result.to_dict()
        encoded = json.dumps(payload)
        assert len(encoded) > 0

    def test_json_round_trip_is_lossless(self, grover_result):
        """Encoding then decoding must reproduce the exact same dict."""
        payload = grover_result.to_dict()
        decoded = json.loads(json.dumps(payload))
        assert decoded == payload

    def test_decoded_top_level_keys(self, grover_result):
        decoded = json.loads(json.dumps(grover_result.to_dict()))
        expected_keys = {
            "algorithm", "target_state", "shots",
            "counts", "probabilities",
            "target_probability", "most_likely_state",
            "circuit",
        }
        assert set(decoded.keys()) == expected_keys

    def test_decoded_circuit_keys(self, grover_result):
        decoded = json.loads(json.dumps(grover_result.to_dict()))
        expected_keys = {"num_qubits", "num_clbits", "depth", "gate_counts", "diagram"}
        assert set(decoded["circuit"].keys()) == expected_keys

    def test_decoded_values_match_result_fields(self, grover_result):
        decoded = json.loads(json.dumps(grover_result.to_dict()))
        assert decoded["algorithm"] == grover_result.algorithm
        assert decoded["target_state"] == grover_result.target_state
        assert decoded["shots"] == grover_result.shots
        assert decoded["counts"] == grover_result.counts
        assert decoded["target_probability"] == grover_result.target_probability
        assert decoded["most_likely_state"] == grover_result.most_likely_state
        assert decoded["circuit"]["num_qubits"] == grover_result.circuit.num_qubits
        assert decoded["circuit"]["depth"] == grover_result.circuit.depth


# ── 6. Downstream consumer simulation ────────────────────────────────────────

class TestDownstreamConsumerSimulation:
    """
    Simulates a downstream module (e.g. M4 API handler or M6 visualizer)
    that works exclusively from result.to_dict() and never touches Qiskit.
    """

    def test_consumer_can_read_result_without_qiskit(self, grover_result):
        """
        A downstream module receives only the dict.  It must be able to
        extract every piece of information it needs without any Qiskit import.
        """
        # Downstream receives this dict (e.g. from an API response body)
        payload: dict = grover_result.to_dict()

        # M6 (Visualization): render a probability histogram
        probabilities: dict = payload["probabilities"]
        assert isinstance(probabilities, dict)
        most_likely: str = payload["most_likely_state"]
        assert isinstance(most_likely, str)
        # Verify the most likely state has the highest probability
        assert probabilities[most_likely] == max(probabilities.values())

        # M1 (Learner): show circuit complexity badges
        depth: int = payload["circuit"]["depth"]
        gate_counts: dict = payload["circuit"]["gate_counts"]
        assert isinstance(depth, int) and depth > 0
        assert isinstance(gate_counts, dict)

        # M2 (Learner Model): record quantum evidence
        target_prob: float = payload["target_probability"]
        assert isinstance(target_prob, float)
        assert 0.0 <= target_prob <= 1.0

        # M5 (AI Guidance): build an LLM prompt with evidence
        prompt_context = (
            f"Algorithm: {payload['algorithm']}\n"
            f"Target: {payload['target_state']}\n"
            f"Success probability: {payload['target_probability']:.2%}\n"
            f"Circuit depth: {payload['circuit']['depth']}\n"
        )
        assert "grover" in prompt_context
        assert "101" in prompt_context

    def test_consumer_can_reconstruct_experiment_parameters(self, grover_result):
        """Downstream can reconstruct the original experiment parameters from the dict."""
        payload: dict = grover_result.to_dict()

        reconstructed = QuantumExperiment(
            algorithm=payload["algorithm"],
            num_qubits=payload["circuit"]["num_qubits"],
            target_state=payload["target_state"],
            shots=payload["shots"],
        )

        assert reconstructed.algorithm == "grover"
        assert reconstructed.num_qubits == 3
        assert reconstructed.target_state == "101"
        assert reconstructed.shots == 1024
