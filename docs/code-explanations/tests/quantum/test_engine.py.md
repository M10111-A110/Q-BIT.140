# Explanation: `tests/quantum/test_engine.py`

## Purpose

This page explains the meaningful behavior in `tests/quantum/test_engine.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
from unittest.mock import MagicMock, patch
import pytest

from backend.quantum.engine import run_experiment
from backend.quantum.results import SimulationResult
from backend.quantum.schemas import QuantumExperiment


def test_run_experiment_success():
    experiment = QuantumExperiment(
        algorithm="grover",
        num_qubits=2,
        target_state="11",
        iterations=1,
        shots=1024,
    )

    result = run_experiment(experiment)

    assert isinstance(result, SimulationResult)
    assert result.algorithm == "grover"
    assert result.target_state == "11"
    assert result.shots == 1024
    assert result.counts == {"11": 1024}
    assert result.probabilities == {"11": 1.0}


def test_run_experiment_custom_shots():
    experiment = QuantumExperiment(
        algorithm="grover",
        num_qubits=2,
        target_state="01",
        iterations=1,
        shots=500,
    )

    result = run_experiment(experiment)

    assert result.shots == 500
    assert sum(result.counts.values()) == 500
    assert result.counts.get("01") == 500


@pytest.mark.parametrize(
    "num_qubits,target_state,iterations",
    [
        (3, "101", 2),
        (4, "0110", 3),
        (5, "10101", 4),
    ],
)
def test_run_experiment_multi_qubits(num_qubits, target_state, iterations):
    experiment = QuantumExperiment(
        algorithm="grover",
        num_qubits=num_qubits,
        target_state=target_state,
        iterations=iterations,
        shots=1024,
    )

    result = run_experiment(experiment)

    assert isinstance(result, SimulationResult)
    assert result.algorithm == "grover"
    assert result.target_state == target_state
    assert result.shots == 1024
    top_state = max(result.counts, key=result.counts.get)
    assert top_state == target_state
    assert result.probabilities[target_state] > 0.8



def test_run_experiment_validation_error():
    experiment = QuantumExperiment(
        algorithm="grover",
        num_qubits=2,
        target_state="101",  # target_state length (3) != num_qubits (2)
        iterations=1,
        shots=1024,
    )

    with pytest.raises(ValueError):
        run_experiment(experiment)


def test_run_experiment_orchestration_isolated():
    # Tests the orchestration pipeline independently from simulator execution
    experiment = QuantumExperiment(
        algorithm="grover",
        num_qubits=2,
        target_state="10",
        iterations=1,
        shots=256,
    )

    fake_circuit = MagicMock()
    fake_counts = {"10": 256}
    fake_builder = MagicMock(return_value=fake_circuit)

    with patch("backend.quantum.engine.validate_experiment") as mock_validate, \
         patch("backend.quantum.engine.get_algorithm", return_value=fake_builder) as mock_get_algorithm, \
         patch("backend.quantum.engine.execute_circuit", return_value=fake_counts) as mock_exec:

        result = run_experiment(experiment)

    mock_validate.assert_called_once_with(experiment)
    mock_get_algorithm.assert_called_once_with("grover")
    fake_builder.assert_called_once_with(
        num_qubits=2,
        target_state="10",
        iterations=1,
    )
    mock_exec.assert_called_once_with(
        fake_circuit,
        shots=256,
    )

    assert result.algorithm == "grover"
    assert result.target_state == "10"
    assert result.shots == 256
    assert result.counts == fake_counts


# ---------------------------------------------------------------------------
# Circuit metadata integration tests
# ---------------------------------------------------------------------------

def test_run_experiment_result_has_circuit_metadata():
    """run_experiment() must return a result with populated CircuitMetadata."""
    from backend.quantum.results import CircuitMetadata

    experiment = QuantumExperiment(
        algorithm="grover",
        num_qubits=2,
        target_state="11",
        iterations=1,
        shots=1024,
    )

    result = run_experiment(experiment)

    assert result.circuit is not None
    assert isinstance(result.circuit, CircuitMetadata)
    assert result.circuit.num_qubits == 2
    assert result.circuit.num_clbits == 2
    assert result.circuit.depth > 0
    assert "measure" in result.circuit.gate_counts
    assert result.circuit.gate_counts["measure"] == 2
    assert isinstance(result.circuit.diagram, str)
    assert len(result.circuit.diagram.strip()) > 0


@pytest.mark.parametrize(
    "num_qubits,target_state,iterations",
    [
        (2, "11", 1),
        (3, "101", 2),
        (4, "0110", 3),
        (5, "10101", 4),
    ],
)
def test_run_experiment_circuit_metadata_qubit_count_matches(
    num_qubits, target_state, iterations
):
    """CircuitMetadata.num_qubits must match the experiment's num_qubits."""
    experiment = QuantumExperiment(
        algorithm="grover",
        num_qubits=num_qubits,
        target_state=target_state,
        iterations=iterations,
        shots=1024,
    )

    result = run_experiment(experiment)

    assert result.circuit is not None
    assert result.circuit.num_qubits == num_qubits


def test_run_experiment_result_is_json_serializable():
    """run_experiment() result must be fully serializable via to_dict()."""
    import json

    experiment = QuantumExperiment(
        algorithm="grover",
        num_qubits=2,
        target_state="11",
        iterations=1,
        shots=1024,
    )

    result = run_experiment(experiment)

    # Must not raise
    serialized = json.dumps(result.to_dict())
    reloaded = json.loads(serialized)

    assert reloaded["algorithm"] == "grover"
    assert reloaded["target_state"] == "11"
    assert reloaded["shots"] == 1024
    assert "counts" in reloaded
    assert "probabilities" in reloaded
    assert "target_probability" in reloaded
    assert "most_likely_state" in reloaded
    assert reloaded["circuit"]["num_qubits"] == 2
    assert reloaded["circuit"]["depth"] > 0

```

## Line Notes

### Line 1

`from unittest.mock import MagicMock, patch`

Imports a dependency or project symbol so later code can use it by name.
### Line 2

`import pytest`

Imports a dependency or project symbol so later code can use it by name.
### Line 3

`(blank)`

Blank line used to separate nearby statements.
### Line 4

`from backend.quantum.engine import run_experiment`

Imports a dependency or project symbol so later code can use it by name.
### Line 5

`from backend.quantum.results import SimulationResult`

Imports a dependency or project symbol so later code can use it by name.
### Line 6

`from backend.quantum.schemas import QuantumExperiment`

Imports a dependency or project symbol so later code can use it by name.
### Line 7

`(blank)`

Blank line used to separate nearby statements.
### Line 9

`def test_run_experiment_success():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 10

`experiment = QuantumExperiment(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 11

`algorithm="grover",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 12

`num_qubits=2,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 13

`target_state="11",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 14

`iterations=1,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 15

`shots=1024,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 16

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 17

`(blank)`

Blank line used to separate nearby statements.
### Line 18

`result = run_experiment(experiment)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 19

`(blank)`

Blank line used to separate nearby statements.
### Line 20

`assert isinstance(result, SimulationResult)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 21

`assert result.algorithm == "grover"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 22

`assert result.target_state == "11"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 23

`assert result.shots == 1024`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 24

`assert result.counts == {"11": 1024}`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 25

`assert result.probabilities == {"11": 1.0}`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 26

`(blank)`

Blank line used to separate nearby statements.
### Line 28

`def test_run_experiment_custom_shots():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 29

`experiment = QuantumExperiment(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 30

`algorithm="grover",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 31

`num_qubits=2,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 32

`target_state="01",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 33

`iterations=1,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 34

`shots=500,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 35

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 36

`(blank)`

Blank line used to separate nearby statements.
### Line 37

`result = run_experiment(experiment)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 38

`(blank)`

Blank line used to separate nearby statements.
### Line 39

`assert result.shots == 500`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 40

`assert sum(result.counts.values()) == 500`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 41

`assert result.counts.get("01") == 500`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 42

`(blank)`

Blank line used to separate nearby statements.
### Line 44

`@pytest.mark.parametrize(`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 45

`"num_qubits,target_state,iterations",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 46

`[`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 47

`(3, "101", 2),`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 48

`(4, "0110", 3),`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 49

`(5, "10101", 4),`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 50

`],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 51

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 52

`def test_run_experiment_multi_qubits(num_qubits, target_state, iterations):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 53

`experiment = QuantumExperiment(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 54

`algorithm="grover",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 55

`num_qubits=num_qubits,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 56

`target_state=target_state,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 57

`iterations=iterations,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 58

`shots=1024,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 59

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 60

`(blank)`

Blank line used to separate nearby statements.
### Line 61

`result = run_experiment(experiment)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 62

`(blank)`

Blank line used to separate nearby statements.
### Line 63

`assert isinstance(result, SimulationResult)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 64

`assert result.algorithm == "grover"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 65

`assert result.target_state == target_state`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 66

`assert result.shots == 1024`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 67

`top_state = max(result.counts, key=result.counts.get)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 68

`assert top_state == target_state`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 69

`assert result.probabilities[target_state] > 0.8`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 70

`(blank)`

Blank line used to separate nearby statements.
### Line 73

`def test_run_experiment_validation_error():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 74

`experiment = QuantumExperiment(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 75

`algorithm="grover",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 76

`num_qubits=2,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 77

`target_state="101",  # target_state length (3) != num_qubits (2)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 78

`iterations=1,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 79

`shots=1024,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 80

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 81

`(blank)`

Blank line used to separate nearby statements.
### Line 82

`with pytest.raises(ValueError):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 83

`run_experiment(experiment)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 84

`(blank)`

Blank line used to separate nearby statements.
### Line 86

`def test_run_experiment_orchestration_isolated():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 87

`# Tests the orchestration pipeline independently from simulator execution`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 88

`experiment = QuantumExperiment(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 89

`algorithm="grover",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 90

`num_qubits=2,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 91

`target_state="10",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 92

`iterations=1,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 93

`shots=256,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 94

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 95

`(blank)`

Blank line used to separate nearby statements.
### Line 96

`fake_circuit = MagicMock()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 97

`fake_counts = {"10": 256}`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 98

`fake_builder = MagicMock(return_value=fake_circuit)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 99

`(blank)`

Blank line used to separate nearby statements.
### Line 100

`with patch("backend.quantum.engine.validate_experiment") as mock_validate, \`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 101

`patch("backend.quantum.engine.get_algorithm", return_value=fake_builder) as mock_get_algorithm, \`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 102

`patch("backend.quantum.engine.execute_circuit", return_value=fake_counts) as mock_exec:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 103

`(blank)`

Blank line used to separate nearby statements.
### Line 104

`result = run_experiment(experiment)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 105

`(blank)`

Blank line used to separate nearby statements.
### Line 106

`mock_validate.assert_called_once_with(experiment)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 107

`mock_get_algorithm.assert_called_once_with("grover")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 108

`fake_builder.assert_called_once_with(`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 109

`num_qubits=2,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 110

`target_state="10",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 111

`iterations=1,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 112

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 113

`mock_exec.assert_called_once_with(`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 114

`fake_circuit,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 115

`shots=256,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 116

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 117

`(blank)`

Blank line used to separate nearby statements.
### Line 118

`assert result.algorithm == "grover"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 119

`assert result.target_state == "10"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 120

`assert result.shots == 256`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 121

`assert result.counts == fake_counts`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 122

`(blank)`

Blank line used to separate nearby statements.
### Line 124

`# ---------------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 125

`# Circuit metadata integration tests`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 126

`# ---------------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 127

`(blank)`

Blank line used to separate nearby statements.
### Line 128

`def test_run_experiment_result_has_circuit_metadata():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 129

`"""run_experiment() must return a result with populated CircuitMetadata."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 130

`from backend.quantum.results import CircuitMetadata`

Imports a dependency or project symbol so later code can use it by name.
### Line 131

`(blank)`

Blank line used to separate nearby statements.
### Line 132

`experiment = QuantumExperiment(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 133

`algorithm="grover",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 134

`num_qubits=2,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 135

`target_state="11",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 136

`iterations=1,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 137

`shots=1024,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 138

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 139

`(blank)`

Blank line used to separate nearby statements.
### Line 140

`result = run_experiment(experiment)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 141

`(blank)`

Blank line used to separate nearby statements.
### Line 142

`assert result.circuit is not None`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 143

`assert isinstance(result.circuit, CircuitMetadata)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 144

`assert result.circuit.num_qubits == 2`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 145

`assert result.circuit.num_clbits == 2`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 146

`assert result.circuit.depth > 0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 147

`assert "measure" in result.circuit.gate_counts`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 148

`assert result.circuit.gate_counts["measure"] == 2`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 149

`assert isinstance(result.circuit.diagram, str)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 150

`assert len(result.circuit.diagram.strip()) > 0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 151

`(blank)`

Blank line used to separate nearby statements.
### Line 153

`@pytest.mark.parametrize(`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 154

`"num_qubits,target_state,iterations",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 155

`[`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 156

`(2, "11", 1),`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 157

`(3, "101", 2),`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 158

`(4, "0110", 3),`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 159

`(5, "10101", 4),`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 160

`],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 161

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 162

`def test_run_experiment_circuit_metadata_qubit_count_matches(`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 163

`num_qubits, target_state, iterations`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 164

`):`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 165

`"""CircuitMetadata.num_qubits must match the experiment's num_qubits."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 166

`experiment = QuantumExperiment(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 167

`algorithm="grover",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 168

`num_qubits=num_qubits,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 169

`target_state=target_state,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 170

`iterations=iterations,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 171

`shots=1024,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 172

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 173

`(blank)`

Blank line used to separate nearby statements.
### Line 174

`result = run_experiment(experiment)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 175

`(blank)`

Blank line used to separate nearby statements.
### Line 176

`assert result.circuit is not None`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 177

`assert result.circuit.num_qubits == num_qubits`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 178

`(blank)`

Blank line used to separate nearby statements.
### Line 180

`def test_run_experiment_result_is_json_serializable():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 181

`"""run_experiment() result must be fully serializable via to_dict()."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 182

`import json`

Imports a dependency or project symbol so later code can use it by name.
### Line 183

`(blank)`

Blank line used to separate nearby statements.
### Line 184

`experiment = QuantumExperiment(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 185

`algorithm="grover",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 186

`num_qubits=2,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 187

`target_state="11",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 188

`iterations=1,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 189

`shots=1024,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 190

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 191

`(blank)`

Blank line used to separate nearby statements.
### Line 192

`result = run_experiment(experiment)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 193

`(blank)`

Blank line used to separate nearby statements.
### Line 194

`# Must not raise`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 195

`serialized = json.dumps(result.to_dict())`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 196

`reloaded = json.loads(serialized)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 197

`(blank)`

Blank line used to separate nearby statements.
### Line 198

`assert reloaded["algorithm"] == "grover"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 199

`assert reloaded["target_state"] == "11"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 200

`assert reloaded["shots"] == 1024`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 201

`assert "counts" in reloaded`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 202

`assert "probabilities" in reloaded`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 203

`assert "target_probability" in reloaded`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 204

`assert "most_likely_state" in reloaded`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 205

`assert reloaded["circuit"]["num_qubits"] == 2`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 206

`assert reloaded["circuit"]["depth"] > 0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.

## Nearby Files

[tests/quantum/test_circuit_metadata.py](test_circuit_metadata.py.md), [tests/quantum/test_execution.py](test_execution.py.md), [tests/quantum/test_grover.py](test_grover.py.md), [tests/quantum/test_package.py](test_package.py.md), [tests/quantum/test_public_api.py](test_public_api.py.md), [tests/quantum/test_registry.py](test_registry.py.md), [tests/quantum/test_results.py](test_results.py.md), [tests/quantum/test_schema.py](test_schema.py.md)
