import pytest

from backend.quantum.registry import get_algorithm
from backend.quantum.algorithms.grover import build_grover_circuit


def test_grover_is_registered():
    builder = get_algorithm("grover")

    assert builder is build_grover_circuit


def test_algorithm_lookup_is_case_insensitive():
    builder = get_algorithm("Grover")

    assert builder is build_grover_circuit


def test_unknown_algorithm_raises_error():
    with pytest.raises(NotImplementedError):
        get_algorithm("unknown")