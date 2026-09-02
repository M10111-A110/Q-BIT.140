# Explanation: `tests/quantum/test_public_api.py`

## Purpose

This page explains the meaningful behavior in `tests/quantum/test_public_api.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
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

```

## Line Notes

### Line 1

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 2

`Public API contract tests for the M3 Quantum Engine.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 3

`(blank)`

Blank line used to separate nearby statements.
### Line 4

`These tests simulate exactly how a downstream module (M1, M2, M4, M5, M6)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 5

`would consume M3.  They import ONLY from \`\`backend.quantum\`\` — never from`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 6

`\`\`qiskit\`\`, \`\`qiskit_aer\`\`, or any internal M3 module.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 7

`(blank)`

Blank line used to separate nearby statements.
### Line 8

`If any of these tests fail, it means a Qiskit object or an internal`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 9

`implementation detail has leaked across the M3 public boundary.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 10

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 11

`import json`

Imports a dependency or project symbol so later code can use it by name.
### Line 12

`(blank)`

Blank line used to separate nearby statements.
### Line 13

`import pytest`

Imports a dependency or project symbol so later code can use it by name.
### Line 14

`(blank)`

Blank line used to separate nearby statements.
### Line 15

`# ── The ONLY imports a downstream consumer should ever need ──────────────────`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 16

`from backend.quantum import (`

Imports a dependency or project symbol so later code can use it by name.
### Line 17

`CircuitMetadata,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 18

`QuantumExperiment,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 19

`SimulationResult,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 20

`run_experiment,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 21

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 22

`(blank)`

Blank line used to separate nearby statements.
### Line 23

`# ── Helpers ──────────────────────────────────────────────────────────────────`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 24

`(blank)`

Blank line used to separate nearby statements.
### Line 25

`#: Sentinel set of types that are acceptable anywhere in public M3 output.`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 26

`#: Qiskit objects, numpy types, custom classes — none of these belong here.`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 27

`_ALLOWED_PRIMITIVE_TYPES = (dict, list, str, int, float, bool, type(None))`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 28

`(blank)`

Blank line used to separate nearby statements.
### Line 30

`def _assert_only_primitives(value, path: str = "result") -> None:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 31

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 32

`Recursively assert that \`\`value\`\` and all its children consist only of`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 33

`plain Python primitives.  Raises AssertionError with a descriptive path`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 34

`if a non-primitive is found.`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 35

`(blank)`

Blank line used to separate nearby statements.
### Line 36

`Does NOT import Qiskit — the check is purely structural.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 37

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 38

`if isinstance(value, dict):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 39

`for k, v in value.items():`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 40

`assert isinstance(k, str), (`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 41

`f"{path}: dict key must be str, got {type(k)} for key={k!r}"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 42

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 43

`_assert_only_primitives(v, path=f"{path}[{k!r}]")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 44

`elif isinstance(value, list):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 45

`for i, item in enumerate(value):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 46

`_assert_only_primitives(item, path=f"{path}[{i}]")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 47

`else:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 48

`assert isinstance(value, _ALLOWED_PRIMITIVE_TYPES), (`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 49

`f"Non-primitive type at {path}: {type(value).__module__}.{type(value).__qualname__}"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 50

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 51

`(blank)`

Blank line used to separate nearby statements.
### Line 53

`# ── Shared fixture ────────────────────────────────────────────────────────────`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 54

`(blank)`

Blank line used to separate nearby statements.
### Line 55

`@pytest.fixture(scope="module")`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 56

`def grover_result() -> SimulationResult:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 57

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 58

`Execute the exact workflow specified in the task brief and return the`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 59

`result.  Scoped to module so Aer runs only once for this test file.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 60

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 61

`experiment = QuantumExperiment(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 62

`algorithm="grover",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 63

`num_qubits=3,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 64

`target_state="101",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 65

`iterations=2,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 66

`shots=1024,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 67

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 68

`return run_experiment(experiment)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 69

`(blank)`

Blank line used to separate nearby statements.
### Line 71

`# ── 1. Public package exports ─────────────────────────────────────────────────`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 72

`(blank)`

Blank line used to separate nearby statements.
### Line 73

`class TestPublicPackageExports:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 74

`def test_run_experiment_is_callable(self):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 75

`assert callable(run_experiment)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 76

`(blank)`

Blank line used to separate nearby statements.
### Line 77

`def test_quantum_experiment_is_exported(self):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 78

`assert QuantumExperiment is not None`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 79

`(blank)`

Blank line used to separate nearby statements.
### Line 80

`def test_simulation_result_is_exported(self):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 81

`assert SimulationResult is not None`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 82

`(blank)`

Blank line used to separate nearby statements.
### Line 83

`def test_circuit_metadata_is_exported(self):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 84

`assert CircuitMetadata is not None`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 85

`(blank)`

Blank line used to separate nearby statements.
### Line 87

`# ── 2. SimulationResult contract ─────────────────────────────────────────────`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 88

`(blank)`

Blank line used to separate nearby statements.
### Line 89

`class TestSimulationResultContract:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 90

`def test_result_is_simulation_result(self, grover_result):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 91

`assert isinstance(grover_result, SimulationResult)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 92

`(blank)`

Blank line used to separate nearby statements.
### Line 93

`def test_algorithm_field(self, grover_result):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 94

`assert grover_result.algorithm == "grover"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 95

`(blank)`

Blank line used to separate nearby statements.
### Line 96

`def test_target_state_field(self, grover_result):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 97

`assert grover_result.target_state == "101"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 98

`(blank)`

Blank line used to separate nearby statements.
### Line 99

`def test_shots_field(self, grover_result):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 100

`assert grover_result.shots == 1024`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 101

`(blank)`

Blank line used to separate nearby statements.
### Line 102

`def test_counts_is_plain_dict(self, grover_result):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 103

`assert type(grover_result.counts) is dict, (`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 104

`f"counts must be exactly dict, got {type(grover_result.counts)}"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 105

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 106

`(blank)`

Blank line used to separate nearby statements.
### Line 107

`def test_counts_values_are_int(self, grover_result):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 108

`for state, count in grover_result.counts.items():`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 109

`assert isinstance(state, str), f"count key is not str: {type(state)}"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 110

`assert isinstance(count, int), f"count value is not int: {type(count)}"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 111

`(blank)`

Blank line used to separate nearby statements.
### Line 112

`def test_counts_sum_equals_shots(self, grover_result):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 113

`assert sum(grover_result.counts.values()) == grover_result.shots`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 114

`(blank)`

Blank line used to separate nearby statements.
### Line 115

`def test_probabilities_is_dict(self, grover_result):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 116

`assert isinstance(grover_result.probabilities, dict)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 117

`(blank)`

Blank line used to separate nearby statements.
### Line 118

`def test_probabilities_values_are_float(self, grover_result):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 119

`for state, prob in grover_result.probabilities.items():`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 120

`assert isinstance(state, str)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 121

`assert isinstance(prob, float)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 122

`(blank)`

Blank line used to separate nearby statements.
### Line 123

`def test_probabilities_sum_to_one(self, grover_result):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 124

`assert abs(sum(grover_result.probabilities.values()) - 1.0) < 1e-9`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 125

`(blank)`

Blank line used to separate nearby statements.
### Line 126

`def test_target_probability_is_float(self, grover_result):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 127

`assert isinstance(grover_result.target_probability, float)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 128

`(blank)`

Blank line used to separate nearby statements.
### Line 129

`def test_target_probability_in_unit_interval(self, grover_result):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 130

`assert 0.0 <= grover_result.target_probability <= 1.0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 131

`(blank)`

Blank line used to separate nearby statements.
### Line 132

`def test_most_likely_state_is_str(self, grover_result):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 133

`assert isinstance(grover_result.most_likely_state, str)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 134

`(blank)`

Blank line used to separate nearby statements.
### Line 135

`def test_most_likely_state_is_in_counts(self, grover_result):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 136

`assert grover_result.most_likely_state in grover_result.counts`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 137

`(blank)`

Blank line used to separate nearby statements.
### Line 138

`def test_grover_amplifies_target_state(self, grover_result):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 139

`"""Grover with 2 iterations on 3 qubits should amplify the target."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 140

`assert grover_result.most_likely_state == "101"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 141

`assert grover_result.target_probability > 0.8`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 142

`(blank)`

Blank line used to separate nearby statements.
### Line 144

`# ── 3. CircuitMetadata contract ───────────────────────────────────────────────`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 145

`(blank)`

Blank line used to separate nearby statements.
### Line 146

`class TestCircuitMetadataContract:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 147

`def test_circuit_is_not_none(self, grover_result):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 148

`assert grover_result.circuit is not None`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 149

`(blank)`

Blank line used to separate nearby statements.
### Line 150

`def test_circuit_is_circuit_metadata(self, grover_result):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 151

`assert isinstance(grover_result.circuit, CircuitMetadata)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 152

`(blank)`

Blank line used to separate nearby statements.
### Line 153

`def test_num_qubits_matches_experiment(self, grover_result):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 154

`assert grover_result.circuit.num_qubits == 3`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 155

`(blank)`

Blank line used to separate nearby statements.
### Line 156

`def test_num_clbits_matches_experiment(self, grover_result):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 157

`assert grover_result.circuit.num_clbits == 3`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 158

`(blank)`

Blank line used to separate nearby statements.
### Line 159

`def test_depth_is_int(self, grover_result):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 160

`assert isinstance(grover_result.circuit.depth, int)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 161

`(blank)`

Blank line used to separate nearby statements.
### Line 162

`def test_depth_is_positive(self, grover_result):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 163

`assert grover_result.circuit.depth > 0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 164

`(blank)`

Blank line used to separate nearby statements.
### Line 165

`def test_gate_counts_is_dict(self, grover_result):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 166

`assert isinstance(grover_result.circuit.gate_counts, dict)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 167

`(blank)`

Blank line used to separate nearby statements.
### Line 168

`def test_gate_counts_keys_are_str(self, grover_result):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 169

`for key in grover_result.circuit.gate_counts:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 170

`assert isinstance(key, str), f"gate_count key is not str: {type(key)}"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 171

`(blank)`

Blank line used to separate nearby statements.
### Line 172

`def test_gate_counts_values_are_int(self, grover_result):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 173

`for val in grover_result.circuit.gate_counts.values():`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 174

`assert isinstance(val, int), f"gate_count value is not int: {type(val)}"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 175

`(blank)`

Blank line used to separate nearby statements.
### Line 176

`def test_gate_counts_has_measure(self, grover_result):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 177

`assert "measure" in grover_result.circuit.gate_counts`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 178

`assert grover_result.circuit.gate_counts["measure"] == 3`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 179

`(blank)`

Blank line used to separate nearby statements.
### Line 180

`def test_diagram_is_str(self, grover_result):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 181

`assert isinstance(grover_result.circuit.diagram, str)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 182

`(blank)`

Blank line used to separate nearby statements.
### Line 183

`def test_diagram_is_nonempty(self, grover_result):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 184

`assert len(grover_result.circuit.diagram.strip()) > 0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 185

`(blank)`

Blank line used to separate nearby statements.
### Line 187

`# ── 4. No Qiskit objects in public output ────────────────────────────────────`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 188

`(blank)`

Blank line used to separate nearby statements.
### Line 189

`class TestNoQiskitObjectsInPublicBoundary:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 190

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 191

`Verifies the encapsulation contract: nothing that crosses the M3 public`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 192

`boundary may be a Qiskit type.  These tests do NOT import Qiskit.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 193

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 194

`(blank)`

Blank line used to separate nearby statements.
### Line 195

`def test_counts_type_is_exactly_dict(self, grover_result):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 196

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 197

`Qiskit returns qiskit.result.counts.Counts from get_counts().`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 198

`That class subclasses dict, so isinstance(counts, dict) is True,`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 199

`but type(counts) is not dict — which would leak a Qiskit object.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 200

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 201

`assert type(grover_result.counts) is dict, (`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 202

`f"result.counts must be exactly dict (not a Qiskit subclass), "`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 203

`f"got {type(grover_result.counts)}"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 204

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 205

`(blank)`

Blank line used to separate nearby statements.
### Line 206

`def test_result_object_contains_only_primitives_recursively(self, grover_result):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 207

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 208

`Walk the dataclass fields directly (not via to_dict) and verify`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 209

`that every stored value is a plain Python primitive.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 210

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 211

`_assert_only_primitives(grover_result.algorithm, "result.algorithm")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 212

`_assert_only_primitives(grover_result.target_state, "result.target_state")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 213

`_assert_only_primitives(grover_result.shots, "result.shots")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 214

`_assert_only_primitives(grover_result.counts, "result.counts")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 215

`# circuit sub-fields`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 216

`meta = grover_result.circuit`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 217

`_assert_only_primitives(meta.num_qubits, "result.circuit.num_qubits")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 218

`_assert_only_primitives(meta.num_clbits, "result.circuit.num_clbits")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 219

`_assert_only_primitives(meta.depth, "result.circuit.depth")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 220

`_assert_only_primitives(meta.gate_counts, "result.circuit.gate_counts")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 221

`_assert_only_primitives(meta.diagram, "result.circuit.diagram")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 222

`(blank)`

Blank line used to separate nearby statements.
### Line 223

`def test_to_dict_contains_only_primitives_recursively(self, grover_result):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 224

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 225

`Walk the entire to_dict() output and verify no Qiskit types survive.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 226

`This is the contract M4 relies on before calling json.dumps().`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 227

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 228

`_assert_only_primitives(grover_result.to_dict(), "result.to_dict()")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 229

`(blank)`

Blank line used to separate nearby statements.
### Line 231

`# ── 5. JSON round-trip ────────────────────────────────────────────────────────`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 232

`(blank)`

Blank line used to separate nearby statements.
### Line 233

`class TestJsonRoundTrip:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 234

`def test_to_dict_is_json_serializable(self, grover_result):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 235

`"""json.dumps must not raise."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 236

`payload = grover_result.to_dict()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 237

`encoded = json.dumps(payload)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 238

`assert len(encoded) > 0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 239

`(blank)`

Blank line used to separate nearby statements.
### Line 240

`def test_json_round_trip_is_lossless(self, grover_result):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 241

`"""Encoding then decoding must reproduce the exact same dict."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 242

`payload = grover_result.to_dict()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 243

`decoded = json.loads(json.dumps(payload))`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 244

`assert decoded == payload`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 245

`(blank)`

Blank line used to separate nearby statements.
### Line 246

`def test_decoded_top_level_keys(self, grover_result):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 247

`decoded = json.loads(json.dumps(grover_result.to_dict()))`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 248

`expected_keys = {`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 249

`"algorithm", "target_state", "shots",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 250

`"counts", "probabilities",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 251

`"target_probability", "most_likely_state",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 252

`"circuit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 253

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 254

`assert set(decoded.keys()) == expected_keys`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 255

`(blank)`

Blank line used to separate nearby statements.
### Line 256

`def test_decoded_circuit_keys(self, grover_result):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 257

`decoded = json.loads(json.dumps(grover_result.to_dict()))`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 258

`expected_keys = {"num_qubits", "num_clbits", "depth", "gate_counts", "diagram"}`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 259

`assert set(decoded["circuit"].keys()) == expected_keys`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 260

`(blank)`

Blank line used to separate nearby statements.
### Line 261

`def test_decoded_values_match_result_fields(self, grover_result):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 262

`decoded = json.loads(json.dumps(grover_result.to_dict()))`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 263

`assert decoded["algorithm"] == grover_result.algorithm`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 264

`assert decoded["target_state"] == grover_result.target_state`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 265

`assert decoded["shots"] == grover_result.shots`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 266

`assert decoded["counts"] == grover_result.counts`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 267

`assert decoded["target_probability"] == grover_result.target_probability`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 268

`assert decoded["most_likely_state"] == grover_result.most_likely_state`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 269

`assert decoded["circuit"]["num_qubits"] == grover_result.circuit.num_qubits`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 270

`assert decoded["circuit"]["depth"] == grover_result.circuit.depth`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 271

`(blank)`

Blank line used to separate nearby statements.
### Line 273

`# ── 6. Downstream consumer simulation ────────────────────────────────────────`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 274

`(blank)`

Blank line used to separate nearby statements.
### Line 275

`class TestDownstreamConsumerSimulation:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 276

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 277

`Simulates a downstream module (e.g. M4 API handler or M6 visualizer)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 278

`that works exclusively from result.to_dict() and never touches Qiskit.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 279

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 280

`(blank)`

Blank line used to separate nearby statements.
### Line 281

`def test_consumer_can_read_result_without_qiskit(self, grover_result):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 282

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 283

`A downstream module receives only the dict.  It must be able to`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 284

`extract every piece of information it needs without any Qiskit import.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 285

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 286

`# Downstream receives this dict (e.g. from an API response body)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 287

`payload: dict = grover_result.to_dict()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 288

`(blank)`

Blank line used to separate nearby statements.
### Line 289

`# M6 (Visualization): render a probability histogram`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 290

`probabilities: dict = payload["probabilities"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 291

`assert isinstance(probabilities, dict)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 292

`most_likely: str = payload["most_likely_state"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 293

`assert isinstance(most_likely, str)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 294

`# Verify the most likely state has the highest probability`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 295

`assert probabilities[most_likely] == max(probabilities.values())`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 296

`(blank)`

Blank line used to separate nearby statements.
### Line 297

`# M1 (Learner): show circuit complexity badges`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 298

`depth: int = payload["circuit"]["depth"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 299

`gate_counts: dict = payload["circuit"]["gate_counts"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 300

`assert isinstance(depth, int) and depth > 0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 301

`assert isinstance(gate_counts, dict)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 302

`(blank)`

Blank line used to separate nearby statements.
### Line 303

`# M2 (Learner Model): record quantum evidence`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 304

`target_prob: float = payload["target_probability"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 305

`assert isinstance(target_prob, float)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 306

`assert 0.0 <= target_prob <= 1.0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 307

`(blank)`

Blank line used to separate nearby statements.
### Line 308

`# M5 (AI Guidance): build an LLM prompt with evidence`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 309

`prompt_context = (`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 310

`f"Algorithm: {payload['algorithm']}\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 311

`f"Target: {payload['target_state']}\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 312

`f"Success probability: {payload['target_probability']:.2%}\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 313

`f"Circuit depth: {payload['circuit']['depth']}\n"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 314

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 315

`assert "grover" in prompt_context`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 316

`assert "101" in prompt_context`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 317

`(blank)`

Blank line used to separate nearby statements.
### Line 318

`def test_consumer_can_reconstruct_experiment_parameters(self, grover_result):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 319

`"""Downstream can reconstruct the original experiment parameters from the dict."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 320

`payload: dict = grover_result.to_dict()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 321

`(blank)`

Blank line used to separate nearby statements.
### Line 322

`reconstructed = QuantumExperiment(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 323

`algorithm=payload["algorithm"],`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 324

`num_qubits=payload["circuit"]["num_qubits"],`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 325

`target_state=payload["target_state"],`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 326

`shots=payload["shots"],`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 327

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 328

`(blank)`

Blank line used to separate nearby statements.
### Line 329

`assert reconstructed.algorithm == "grover"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 330

`assert reconstructed.num_qubits == 3`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 331

`assert reconstructed.target_state == "101"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 332

`assert reconstructed.shots == 1024`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.

## Nearby Files

[tests/quantum/test_circuit_metadata.py](test_circuit_metadata.py.md), [tests/quantum/test_engine.py](test_engine.py.md), [tests/quantum/test_execution.py](test_execution.py.md), [tests/quantum/test_grover.py](test_grover.py.md), [tests/quantum/test_package.py](test_package.py.md), [tests/quantum/test_registry.py](test_registry.py.md), [tests/quantum/test_results.py](test_results.py.md), [tests/quantum/test_schema.py](test_schema.py.md)
