# Explanation: `tests/quantum/test_results.py`

## Purpose

This page explains the meaningful behavior in `tests/quantum/test_results.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
import pytest

from backend.quantum.results import SimulationResult

def test_simulation_result_stores_values():
    result = SimulationResult(
        algorithm="grover",
        target_state="11",
        shots=100,
        counts={
            "11":90,
            "00":10
        }
    )

    assert result.algorithm == "grover"
    assert result.target_state == "11"
    assert result.shots == 100
    assert result.counts == {"11":90, "00":10}

def test_simulation_result_rejects_non_positive_shots():
    with pytest.raises(ValueError):
        SimulationResult(
            algorithm="grover",
            target_state="11",
            shots=0,
            counts={},
        )


def test_simulation_result_rejects_negative_counts():
    with pytest.raises(ValueError):
        SimulationResult(
            algorithm="grover",
            target_state="11",
            shots=100,
            counts={"11": -1, "00": 101},
        )


def test_simulation_result_rejects_counts_not_matching_shots():
    with pytest.raises(ValueError):
        SimulationResult(
            algorithm="grover",
            target_state="11",
            shots=100,
            counts={"11": 80, "00": 10},
        )


def test_simulation_result_calculates_probabilities():
    result = SimulationResult(
        algorithm="grover",
        target_state="11",
        shots=1000,
        counts={"00": 250, "11": 750},
    )

    assert result.probabilities == {"00": 0.25, "11": 0.75}
    assert sum(result.probabilities.values()) == 1.0


def test_target_probability():
    result = SimulationResult(
            algorithm="grover",
            target_state="11",
            shots=1000,
            counts={"00": 100, "11": 900},
        )

    assert result.target_probability == 0.9

def test_most_likely_state():
    result = SimulationResult(
            algorithm="grover",
            target_state="11",
            shots=1000,
            counts={"00": 100, "11": 900},
        )

    assert result.most_likely_state == "11"

def test_target_probability_when_not_most_likely():
    result = SimulationResult(
            algorithm="grover",
            target_state="11",
            shots=1000,
            counts={"00": 800, "11": 200},
        )

    assert result.target_probability == 0.2
    assert result.most_likely_state == "00"


# ---------------------------------------------------------------------------
# to_dict() serialization tests
# ---------------------------------------------------------------------------

def test_to_dict_includes_all_fields():
    import json
    result = SimulationResult(
        algorithm="grover",
        target_state="11",
        shots=1000,
        counts={"11": 800, "00": 200},
    )

    d = result.to_dict()

    assert d["algorithm"] == "grover"
    assert d["target_state"] == "11"
    assert d["shots"] == 1000
    assert d["counts"] == {"11": 800, "00": 200}
    assert d["probabilities"] == {"11": 0.8, "00": 0.2}
    assert d["target_probability"] == 0.8
    assert d["most_likely_state"] == "11"
    assert "circuit" in d


def test_to_dict_without_circuit_is_json_serializable():
    import json
    result = SimulationResult(
        algorithm="grover",
        target_state="11",
        shots=100,
        counts={"11": 100},
    )

    # Must not raise
    serialized = json.dumps(result.to_dict())
    assert len(serialized) > 0


def test_to_dict_circuit_is_none_when_not_set():
    result = SimulationResult(
        algorithm="grover",
        target_state="11",
        shots=100,
        counts={"11": 100},
    )

    d = result.to_dict()
    assert d["circuit"] is None


def test_simulation_result_circuit_defaults_to_none():
    """Backward compatibility: existing call sites that don't pass circuit still work."""
    result = SimulationResult(
        algorithm="grover",
        target_state="11",
        shots=100,
        counts={"11": 100},
    )

    assert result.circuit is None


def test_to_dict_with_circuit_metadata_is_json_serializable():
    import json
    from backend.quantum.results import CircuitMetadata

    meta = CircuitMetadata(
        num_qubits=2,
        num_clbits=2,
        depth=5,
        gate_counts={"h": 4, "cz": 1, "measure": 2},
        diagram="     ┌───┐\nq_0: ┤ H ├\n     └───┘",
    )
    result = SimulationResult(
        algorithm="grover",
        target_state="11",
        shots=1000,
        counts={"11": 900, "00": 100},
        circuit=meta,
    )

    serialized = json.dumps(result.to_dict())
    reloaded = json.loads(serialized)

    assert reloaded["circuit"]["num_qubits"] == 2
    assert reloaded["circuit"]["depth"] == 5
    assert reloaded["circuit"]["gate_counts"] == {"h": 4, "cz": 1, "measure": 2}
    assert "diagram" in reloaded["circuit"]

```

## Line Notes

### Line 1

`import pytest`

Imports a dependency or project symbol so later code can use it by name.
### Line 2

`(blank)`

Blank line used to separate nearby statements.
### Line 3

`from backend.quantum.results import SimulationResult`

Imports a dependency or project symbol so later code can use it by name.
### Line 4

`(blank)`

Blank line used to separate nearby statements.
### Line 5

`def test_simulation_result_stores_values():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 6

`result = SimulationResult(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 7

`algorithm="grover",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 8

`target_state="11",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 9

`shots=100,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 10

`counts={`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 11

`"11":90,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 12

`"00":10`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 13

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 14

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 15

`(blank)`

Blank line used to separate nearby statements.
### Line 16

`assert result.algorithm == "grover"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 17

`assert result.target_state == "11"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 18

`assert result.shots == 100`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 19

`assert result.counts == {"11":90, "00":10}`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 20

`(blank)`

Blank line used to separate nearby statements.
### Line 21

`def test_simulation_result_rejects_non_positive_shots():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 22

`with pytest.raises(ValueError):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 23

`SimulationResult(`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 24

`algorithm="grover",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 25

`target_state="11",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 26

`shots=0,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 27

`counts={},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 28

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 29

`(blank)`

Blank line used to separate nearby statements.
### Line 31

`def test_simulation_result_rejects_negative_counts():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 32

`with pytest.raises(ValueError):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 33

`SimulationResult(`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 34

`algorithm="grover",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 35

`target_state="11",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 36

`shots=100,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 37

`counts={"11": -1, "00": 101},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 38

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 39

`(blank)`

Blank line used to separate nearby statements.
### Line 41

`def test_simulation_result_rejects_counts_not_matching_shots():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 42

`with pytest.raises(ValueError):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 43

`SimulationResult(`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 44

`algorithm="grover",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 45

`target_state="11",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 46

`shots=100,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 47

`counts={"11": 80, "00": 10},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 48

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 49

`(blank)`

Blank line used to separate nearby statements.
### Line 51

`def test_simulation_result_calculates_probabilities():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 52

`result = SimulationResult(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 53

`algorithm="grover",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 54

`target_state="11",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 55

`shots=1000,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 56

`counts={"00": 250, "11": 750},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 57

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 58

`(blank)`

Blank line used to separate nearby statements.
### Line 59

`assert result.probabilities == {"00": 0.25, "11": 0.75}`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 60

`assert sum(result.probabilities.values()) == 1.0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 61

`(blank)`

Blank line used to separate nearby statements.
### Line 63

`def test_target_probability():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 64

`result = SimulationResult(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 65

`algorithm="grover",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 66

`target_state="11",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 67

`shots=1000,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 68

`counts={"00": 100, "11": 900},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 69

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 70

`(blank)`

Blank line used to separate nearby statements.
### Line 71

`assert result.target_probability == 0.9`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 72

`(blank)`

Blank line used to separate nearby statements.
### Line 73

`def test_most_likely_state():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 74

`result = SimulationResult(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 75

`algorithm="grover",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 76

`target_state="11",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 77

`shots=1000,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 78

`counts={"00": 100, "11": 900},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 79

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 80

`(blank)`

Blank line used to separate nearby statements.
### Line 81

`assert result.most_likely_state == "11"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 82

`(blank)`

Blank line used to separate nearby statements.
### Line 83

`def test_target_probability_when_not_most_likely():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 84

`result = SimulationResult(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 85

`algorithm="grover",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 86

`target_state="11",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 87

`shots=1000,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 88

`counts={"00": 800, "11": 200},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 89

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 90

`(blank)`

Blank line used to separate nearby statements.
### Line 91

`assert result.target_probability == 0.2`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 92

`assert result.most_likely_state == "00"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 93

`(blank)`

Blank line used to separate nearby statements.
### Line 95

`# ---------------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 96

`# to_dict() serialization tests`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 97

`# ---------------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 98

`(blank)`

Blank line used to separate nearby statements.
### Line 99

`def test_to_dict_includes_all_fields():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 100

`import json`

Imports a dependency or project symbol so later code can use it by name.
### Line 101

`result = SimulationResult(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 102

`algorithm="grover",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 103

`target_state="11",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 104

`shots=1000,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 105

`counts={"11": 800, "00": 200},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 106

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 107

`(blank)`

Blank line used to separate nearby statements.
### Line 108

`d = result.to_dict()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 109

`(blank)`

Blank line used to separate nearby statements.
### Line 110

`assert d["algorithm"] == "grover"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 111

`assert d["target_state"] == "11"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 112

`assert d["shots"] == 1000`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 113

`assert d["counts"] == {"11": 800, "00": 200}`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 114

`assert d["probabilities"] == {"11": 0.8, "00": 0.2}`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 115

`assert d["target_probability"] == 0.8`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 116

`assert d["most_likely_state"] == "11"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 117

`assert "circuit" in d`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 118

`(blank)`

Blank line used to separate nearby statements.
### Line 120

`def test_to_dict_without_circuit_is_json_serializable():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 121

`import json`

Imports a dependency or project symbol so later code can use it by name.
### Line 122

`result = SimulationResult(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 123

`algorithm="grover",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 124

`target_state="11",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 125

`shots=100,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 126

`counts={"11": 100},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 127

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 128

`(blank)`

Blank line used to separate nearby statements.
### Line 129

`# Must not raise`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 130

`serialized = json.dumps(result.to_dict())`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 131

`assert len(serialized) > 0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 132

`(blank)`

Blank line used to separate nearby statements.
### Line 134

`def test_to_dict_circuit_is_none_when_not_set():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 135

`result = SimulationResult(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 136

`algorithm="grover",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 137

`target_state="11",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 138

`shots=100,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 139

`counts={"11": 100},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 140

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 141

`(blank)`

Blank line used to separate nearby statements.
### Line 142

`d = result.to_dict()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 143

`assert d["circuit"] is None`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 144

`(blank)`

Blank line used to separate nearby statements.
### Line 146

`def test_simulation_result_circuit_defaults_to_none():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 147

`"""Backward compatibility: existing call sites that don't pass circuit still work."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 148

`result = SimulationResult(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 149

`algorithm="grover",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 150

`target_state="11",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 151

`shots=100,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 152

`counts={"11": 100},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 153

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 154

`(blank)`

Blank line used to separate nearby statements.
### Line 155

`assert result.circuit is None`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 156

`(blank)`

Blank line used to separate nearby statements.
### Line 158

`def test_to_dict_with_circuit_metadata_is_json_serializable():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 159

`import json`

Imports a dependency or project symbol so later code can use it by name.
### Line 160

`from backend.quantum.results import CircuitMetadata`

Imports a dependency or project symbol so later code can use it by name.
### Line 161

`(blank)`

Blank line used to separate nearby statements.
### Line 162

`meta = CircuitMetadata(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 163

`num_qubits=2,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 164

`num_clbits=2,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 165

`depth=5,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 166

`gate_counts={"h": 4, "cz": 1, "measure": 2},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 167

`diagram="     ┌───┐\nq_0: ┤ H ├\n     └───┘",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 168

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 169

`result = SimulationResult(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 170

`algorithm="grover",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 171

`target_state="11",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 172

`shots=1000,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 173

`counts={"11": 900, "00": 100},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 174

`circuit=meta,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 175

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 176

`(blank)`

Blank line used to separate nearby statements.
### Line 177

`serialized = json.dumps(result.to_dict())`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 178

`reloaded = json.loads(serialized)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 179

`(blank)`

Blank line used to separate nearby statements.
### Line 180

`assert reloaded["circuit"]["num_qubits"] == 2`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 181

`assert reloaded["circuit"]["depth"] == 5`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 182

`assert reloaded["circuit"]["gate_counts"] == {"h": 4, "cz": 1, "measure": 2}`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 183

`assert "diagram" in reloaded["circuit"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.

## Nearby Files

[tests/quantum/test_circuit_metadata.py](test_circuit_metadata.py.md), [tests/quantum/test_engine.py](test_engine.py.md), [tests/quantum/test_execution.py](test_execution.py.md), [tests/quantum/test_grover.py](test_grover.py.md), [tests/quantum/test_package.py](test_package.py.md), [tests/quantum/test_public_api.py](test_public_api.py.md), [tests/quantum/test_registry.py](test_registry.py.md), [tests/quantum/test_schema.py](test_schema.py.md)
