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
