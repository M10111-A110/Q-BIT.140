# Explanation: `tests/quantum/test_circuit_metadata.py`

## Purpose

This page explains the meaningful behavior in `tests/quantum/test_circuit_metadata.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
"""
Tests for CircuitMetadata.

CircuitMetadata is a pure-Python, Qiskit-free data structure that captures
structural information about the quantum circuit that was constructed and
executed.  Downstream modules (M4, M5, M6) must be able to consume it
without importing Qiskit.
"""
import json

import pytest

from backend.quantum.algorithms.grover import build_grover_circuit
from backend.quantum.results import CircuitMetadata


# ---------------------------------------------------------------------------
# Helper — build a CircuitMetadata the same way the engine will
# ---------------------------------------------------------------------------

def _make_metadata(num_qubits: int, target_state: str) -> CircuitMetadata:
    """Build a CircuitMetadata from a real Grover circuit."""
    from backend.quantum.results import extract_circuit_metadata

    circuit = build_grover_circuit(
        num_qubits=num_qubits,
        target_state=target_state,
        iterations=1,
    )
    return extract_circuit_metadata(circuit)


# ---------------------------------------------------------------------------
# 1. CircuitMetadata stores expected value types
# ---------------------------------------------------------------------------

def test_circuit_metadata_stores_expected_types():
    meta = _make_metadata(2, "11")

    assert isinstance(meta.num_qubits, int)
    assert isinstance(meta.num_clbits, int)
    assert isinstance(meta.depth, int)
    assert isinstance(meta.gate_counts, dict)
    assert isinstance(meta.diagram, str)

    # All gate_counts values must be plain ints — not Qiskit objects
    for key, val in meta.gate_counts.items():
        assert isinstance(key, str), f"gate name must be str, got {type(key)}"
        assert isinstance(val, int), f"gate count must be int, got {type(val)}"


# ---------------------------------------------------------------------------
# 2. CircuitMetadata contains NO Qiskit objects
# ---------------------------------------------------------------------------

def test_circuit_metadata_contains_no_qiskit_objects():
    """Downstream modules must be able to consume this without Qiskit."""
    meta = _make_metadata(2, "11")

    for attr_name in ("num_qubits", "num_clbits", "depth", "gate_counts", "diagram"):
        value = getattr(meta, attr_name)
        module = getattr(type(value), "__module__", "") or ""
        assert not module.startswith("qiskit"), (
            f"{attr_name} has a Qiskit type: {type(value)}"
        )


# ---------------------------------------------------------------------------
# 3. num_qubits and num_clbits match circuit parameters
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "num_qubits,target_state",
    [
        (2, "00"),
        (2, "11"),
        (3, "101"),
        (4, "0110"),
        (5, "10101"),
    ],
)
def test_circuit_metadata_qubit_counts_match(num_qubits, target_state):
    meta = _make_metadata(num_qubits, target_state)

    assert meta.num_qubits == num_qubits
    assert meta.num_clbits == num_qubits  # Grover uses equal qubit/clbit registers


# ---------------------------------------------------------------------------
# 4. Depth is a positive integer
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "num_qubits,target_state",
    [
        (2, "11"),
        (3, "101"),
        (4, "0110"),
        (5, "10101"),
    ],
)
def test_circuit_metadata_depth_is_positive(num_qubits, target_state):
    meta = _make_metadata(num_qubits, target_state)

    assert meta.depth > 0, f"Expected positive depth, got {meta.depth}"


# ---------------------------------------------------------------------------
# 5. gate_counts contains 'measure' with count == num_qubits
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "num_qubits,target_state",
    [
        (2, "11"),
        (3, "000"),
        (4, "1111"),
        (5, "00000"),
    ],
)
def test_circuit_metadata_gate_counts_has_measure(num_qubits, target_state):
    meta = _make_metadata(num_qubits, target_state)

    assert "measure" in meta.gate_counts, (
        f"'measure' not in gate_counts: {meta.gate_counts}"
    )
    assert meta.gate_counts["measure"] == num_qubits


# ---------------------------------------------------------------------------
# 6. gate_counts contains 'h' (Hadamard is always present in Grover)
# ---------------------------------------------------------------------------

def test_circuit_metadata_gate_counts_has_hadamard():
    meta = _make_metadata(2, "11")

    assert "h" in meta.gate_counts, (
        f"Hadamard not found in gate_counts: {meta.gate_counts}"
    )
    assert meta.gate_counts["h"] > 0


# ---------------------------------------------------------------------------
# 7. 2-qubit gate_counts has a phase-inversion gate (cz for 2-qubit Grover)
# ---------------------------------------------------------------------------

def test_circuit_metadata_2qubit_has_cz():
    meta = _make_metadata(2, "11")

    assert "cz" in meta.gate_counts, (
        f"Expected 'cz' in 2-qubit Grover gate_counts, got: {meta.gate_counts}"
    )


# ---------------------------------------------------------------------------
# 8. Multi-qubit gate_counts has a multi-controlled gate (mcx for N>2)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("num_qubits,target_state", [(3, "101"), (4, "0110"), (5, "10101")])
def test_circuit_metadata_multi_qubit_has_mcx(num_qubits, target_state):
    meta = _make_metadata(num_qubits, target_state)

    has_multi = "mcx" in meta.gate_counts or "ccx" in meta.gate_counts
    assert has_multi, (
        f"Expected mcx/ccx in {num_qubits}-qubit gate_counts, got: {meta.gate_counts}"
    )


# ---------------------------------------------------------------------------
# 9. diagram is a non-empty string
# ---------------------------------------------------------------------------

def test_circuit_metadata_diagram_is_nonempty_string():
    meta = _make_metadata(2, "11")

    assert isinstance(meta.diagram, str)
    assert len(meta.diagram.strip()) > 0, "Circuit diagram must not be blank"


# ---------------------------------------------------------------------------
# 10. CircuitMetadata is directly JSON-serializable
# ---------------------------------------------------------------------------

def test_circuit_metadata_is_json_serializable():
    meta = _make_metadata(3, "101")

    payload = {
        "num_qubits": meta.num_qubits,
        "num_clbits": meta.num_clbits,
        "depth": meta.depth,
        "gate_counts": meta.gate_counts,
        "diagram": meta.diagram,
    }
    # Must not raise
    serialized = json.dumps(payload)
    assert len(serialized) > 0

```

## Line Notes

### Line 1

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 2

`Tests for CircuitMetadata.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 3

`(blank)`

Blank line used to separate nearby statements.
### Line 4

`CircuitMetadata is a pure-Python, Qiskit-free data structure that captures`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 5

`structural information about the quantum circuit that was constructed and`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 6

`executed.  Downstream modules (M4, M5, M6) must be able to consume it`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 7

`without importing Qiskit.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 8

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 9

`import json`

Imports a dependency or project symbol so later code can use it by name.
### Line 10

`(blank)`

Blank line used to separate nearby statements.
### Line 11

`import pytest`

Imports a dependency or project symbol so later code can use it by name.
### Line 12

`(blank)`

Blank line used to separate nearby statements.
### Line 13

`from backend.quantum.algorithms.grover import build_grover_circuit`

Imports a dependency or project symbol so later code can use it by name.
### Line 14

`from backend.quantum.results import CircuitMetadata`

Imports a dependency or project symbol so later code can use it by name.
### Line 15

`(blank)`

Blank line used to separate nearby statements.
### Line 17

`# ---------------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 18

`# Helper — build a CircuitMetadata the same way the engine will`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 19

`# ---------------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 20

`(blank)`

Blank line used to separate nearby statements.
### Line 21

`def _make_metadata(num_qubits: int, target_state: str) -> CircuitMetadata:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 22

`"""Build a CircuitMetadata from a real Grover circuit."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 23

`from backend.quantum.results import extract_circuit_metadata`

Imports a dependency or project symbol so later code can use it by name.
### Line 24

`(blank)`

Blank line used to separate nearby statements.
### Line 25

`circuit = build_grover_circuit(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 26

`num_qubits=num_qubits,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 27

`target_state=target_state,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 28

`iterations=1,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 29

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 30

`return extract_circuit_metadata(circuit)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 31

`(blank)`

Blank line used to separate nearby statements.
### Line 33

`# ---------------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 34

`# 1. CircuitMetadata stores expected value types`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 35

`# ---------------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 36

`(blank)`

Blank line used to separate nearby statements.
### Line 37

`def test_circuit_metadata_stores_expected_types():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 38

`meta = _make_metadata(2, "11")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 39

`(blank)`

Blank line used to separate nearby statements.
### Line 40

`assert isinstance(meta.num_qubits, int)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 41

`assert isinstance(meta.num_clbits, int)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 42

`assert isinstance(meta.depth, int)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 43

`assert isinstance(meta.gate_counts, dict)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 44

`assert isinstance(meta.diagram, str)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 45

`(blank)`

Blank line used to separate nearby statements.
### Line 46

`# All gate_counts values must be plain ints — not Qiskit objects`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 47

`for key, val in meta.gate_counts.items():`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 48

`assert isinstance(key, str), f"gate name must be str, got {type(key)}"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 49

`assert isinstance(val, int), f"gate count must be int, got {type(val)}"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 50

`(blank)`

Blank line used to separate nearby statements.
### Line 52

`# ---------------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 53

`# 2. CircuitMetadata contains NO Qiskit objects`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 54

`# ---------------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 55

`(blank)`

Blank line used to separate nearby statements.
### Line 56

`def test_circuit_metadata_contains_no_qiskit_objects():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 57

`"""Downstream modules must be able to consume this without Qiskit."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 58

`meta = _make_metadata(2, "11")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 59

`(blank)`

Blank line used to separate nearby statements.
### Line 60

`for attr_name in ("num_qubits", "num_clbits", "depth", "gate_counts", "diagram"):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 61

`value = getattr(meta, attr_name)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 62

`module = getattr(type(value), "__module__", "") or ""`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 63

`assert not module.startswith("qiskit"), (`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 64

`f"{attr_name} has a Qiskit type: {type(value)}"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 65

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 66

`(blank)`

Blank line used to separate nearby statements.
### Line 68

`# ---------------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 69

`# 3. num_qubits and num_clbits match circuit parameters`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 70

`# ---------------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 71

`(blank)`

Blank line used to separate nearby statements.
### Line 72

`@pytest.mark.parametrize(`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 73

`"num_qubits,target_state",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 74

`[`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 75

`(2, "00"),`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 76

`(2, "11"),`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 77

`(3, "101"),`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 78

`(4, "0110"),`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 79

`(5, "10101"),`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 80

`],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 81

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 82

`def test_circuit_metadata_qubit_counts_match(num_qubits, target_state):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 83

`meta = _make_metadata(num_qubits, target_state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 84

`(blank)`

Blank line used to separate nearby statements.
### Line 85

`assert meta.num_qubits == num_qubits`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 86

`assert meta.num_clbits == num_qubits  # Grover uses equal qubit/clbit registers`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 87

`(blank)`

Blank line used to separate nearby statements.
### Line 89

`# ---------------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 90

`# 4. Depth is a positive integer`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 91

`# ---------------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 92

`(blank)`

Blank line used to separate nearby statements.
### Line 93

`@pytest.mark.parametrize(`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 94

`"num_qubits,target_state",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 95

`[`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 96

`(2, "11"),`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 97

`(3, "101"),`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 98

`(4, "0110"),`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 99

`(5, "10101"),`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 100

`],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 101

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 102

`def test_circuit_metadata_depth_is_positive(num_qubits, target_state):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 103

`meta = _make_metadata(num_qubits, target_state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 104

`(blank)`

Blank line used to separate nearby statements.
### Line 105

`assert meta.depth > 0, f"Expected positive depth, got {meta.depth}"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 106

`(blank)`

Blank line used to separate nearby statements.
### Line 108

`# ---------------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 109

`# 5. gate_counts contains 'measure' with count == num_qubits`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 110

`# ---------------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 111

`(blank)`

Blank line used to separate nearby statements.
### Line 112

`@pytest.mark.parametrize(`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 113

`"num_qubits,target_state",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 114

`[`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 115

`(2, "11"),`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 116

`(3, "000"),`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 117

`(4, "1111"),`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 118

`(5, "00000"),`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 119

`],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 120

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 121

`def test_circuit_metadata_gate_counts_has_measure(num_qubits, target_state):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 122

`meta = _make_metadata(num_qubits, target_state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 123

`(blank)`

Blank line used to separate nearby statements.
### Line 124

`assert "measure" in meta.gate_counts, (`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 125

`f"'measure' not in gate_counts: {meta.gate_counts}"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 126

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 127

`assert meta.gate_counts["measure"] == num_qubits`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 128

`(blank)`

Blank line used to separate nearby statements.
### Line 130

`# ---------------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 131

`# 6. gate_counts contains 'h' (Hadamard is always present in Grover)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 132

`# ---------------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 133

`(blank)`

Blank line used to separate nearby statements.
### Line 134

`def test_circuit_metadata_gate_counts_has_hadamard():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 135

`meta = _make_metadata(2, "11")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 136

`(blank)`

Blank line used to separate nearby statements.
### Line 137

`assert "h" in meta.gate_counts, (`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 138

`f"Hadamard not found in gate_counts: {meta.gate_counts}"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 139

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 140

`assert meta.gate_counts["h"] > 0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 141

`(blank)`

Blank line used to separate nearby statements.
### Line 143

`# ---------------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 144

`# 7. 2-qubit gate_counts has a phase-inversion gate (cz for 2-qubit Grover)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 145

`# ---------------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 146

`(blank)`

Blank line used to separate nearby statements.
### Line 147

`def test_circuit_metadata_2qubit_has_cz():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 148

`meta = _make_metadata(2, "11")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 149

`(blank)`

Blank line used to separate nearby statements.
### Line 150

`assert "cz" in meta.gate_counts, (`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 151

`f"Expected 'cz' in 2-qubit Grover gate_counts, got: {meta.gate_counts}"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 152

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 153

`(blank)`

Blank line used to separate nearby statements.
### Line 155

`# ---------------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 156

`# 8. Multi-qubit gate_counts has a multi-controlled gate (mcx for N>2)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 157

`# ---------------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 158

`(blank)`

Blank line used to separate nearby statements.
### Line 159

`@pytest.mark.parametrize("num_qubits,target_state", [(3, "101"), (4, "0110"), (5, "10101")])`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 160

`def test_circuit_metadata_multi_qubit_has_mcx(num_qubits, target_state):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 161

`meta = _make_metadata(num_qubits, target_state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 162

`(blank)`

Blank line used to separate nearby statements.
### Line 163

`has_multi = "mcx" in meta.gate_counts or "ccx" in meta.gate_counts`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 164

`assert has_multi, (`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 165

`f"Expected mcx/ccx in {num_qubits}-qubit gate_counts, got: {meta.gate_counts}"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 166

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 167

`(blank)`

Blank line used to separate nearby statements.
### Line 169

`# ---------------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 170

`# 9. diagram is a non-empty string`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 171

`# ---------------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 172

`(blank)`

Blank line used to separate nearby statements.
### Line 173

`def test_circuit_metadata_diagram_is_nonempty_string():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 174

`meta = _make_metadata(2, "11")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 175

`(blank)`

Blank line used to separate nearby statements.
### Line 176

`assert isinstance(meta.diagram, str)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 177

`assert len(meta.diagram.strip()) > 0, "Circuit diagram must not be blank"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 178

`(blank)`

Blank line used to separate nearby statements.
### Line 180

`# ---------------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 181

`# 10. CircuitMetadata is directly JSON-serializable`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 182

`# ---------------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 183

`(blank)`

Blank line used to separate nearby statements.
### Line 184

`def test_circuit_metadata_is_json_serializable():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 185

`meta = _make_metadata(3, "101")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 186

`(blank)`

Blank line used to separate nearby statements.
### Line 187

`payload = {`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 188

`"num_qubits": meta.num_qubits,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 189

`"num_clbits": meta.num_clbits,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 190

`"depth": meta.depth,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 191

`"gate_counts": meta.gate_counts,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 192

`"diagram": meta.diagram,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 193

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 194

`# Must not raise`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 195

`serialized = json.dumps(payload)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 196

`assert len(serialized) > 0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.

## Nearby Files

[tests/quantum/test_engine.py](test_engine.py.md), [tests/quantum/test_execution.py](test_execution.py.md), [tests/quantum/test_grover.py](test_grover.py.md), [tests/quantum/test_package.py](test_package.py.md), [tests/quantum/test_public_api.py](test_public_api.py.md), [tests/quantum/test_registry.py](test_registry.py.md), [tests/quantum/test_results.py](test_results.py.md), [tests/quantum/test_schema.py](test_schema.py.md)
