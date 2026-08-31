from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # QuantumCircuit is only referenced for type-checking and inside
    # extract_circuit_metadata(); it never appears in the public API surface.
    from qiskit import QuantumCircuit


@dataclass
class CircuitMetadata:
    """
    Pure-Python, Qiskit-free snapshot of a constructed quantum circuit.

    Downstream modules (M1, M4, M5, M6) may consume this freely without
    importing Qiskit.
    """
    num_qubits: int
    num_clbits: int
    depth: int
    gate_counts: dict[str, int]
    diagram: str


def extract_circuit_metadata(circuit: "QuantumCircuit") -> CircuitMetadata:
    """
    Extract a Qiskit-free CircuitMetadata snapshot from a QuantumCircuit.

    This is the ONLY place in M3 where Qiskit circuit internals are read
    for serialization purposes.  The returned object contains no Qiskit
    types.
    """
    diagram = circuit.draw(output="text").single_string()

    return CircuitMetadata(
        num_qubits=circuit.num_qubits,
        num_clbits=circuit.num_clbits,
        depth=circuit.depth(),
        gate_counts=dict(circuit.count_ops()),
        diagram=diagram,
    )


@dataclass
class SimulationResult:
    """
    Canonical, Qiskit-free output of a quantum experiment.

    All fields are plain Python primitives.  Downstream modules must
    never receive Qiskit objects through this dataclass.

    ``circuit`` is optional for backward compatibility: existing tests and
    call sites that do not pass it receive ``None`` and continue to work.
    """
    algorithm: str
    target_state: str
    shots: int
    counts: dict[str, int]
    circuit: CircuitMetadata | None = field(default=None)

    def __post_init__(self) -> None:
        if self.shots <= 0:
            raise ValueError("shots must be greater than zero")

        if any(count < 0 for count in self.counts.values()):
            raise ValueError("measurement counts cannot be negative")

        if sum(self.counts.values()) != self.shots:
            raise ValueError("measurement counts must sum to shots")

    # ------------------------------------------------------------------
    # Derived evidence — useful for M1 (learner), M2 (model), M5 (AI)
    # ------------------------------------------------------------------

    @property
    def probabilities(self) -> dict[str, float]:
        """Normalised measurement probability distribution."""
        return {
            state: count / self.shots
            for state, count in self.counts.items()
        }

    @property
    def target_probability(self) -> float:
        """Probability of measuring the requested target state."""
        return self.counts.get(self.target_state, 0) / self.shots

    @property
    def most_likely_state(self) -> str:
        """Computational basis state with the highest measurement count."""
        return max(self.counts, key=self.counts.get)

    # ------------------------------------------------------------------
    # Serialization — required for M4 (API / Supabase JSON transport)
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """
        Return a fully JSON-serializable representation of this result.

        Includes computed properties (probabilities, target_probability,
        most_likely_state) and circuit metadata.  This is the intended
        format for M4 to serialize to HTTP responses or Supabase rows.

        ``dataclasses.asdict()`` is deliberately NOT used because it
        would silently omit the ``@property`` derived fields.
        """
        circuit_dict = None
        if self.circuit is not None:
            circuit_dict = {
                "num_qubits": self.circuit.num_qubits,
                "num_clbits": self.circuit.num_clbits,
                "depth": self.circuit.depth,
                "gate_counts": self.circuit.gate_counts,
                "diagram": self.circuit.diagram,
            }

        return {
            "algorithm": self.algorithm,
            "target_state": self.target_state,
            "shots": self.shots,
            "counts": self.counts,
            "probabilities": self.probabilities,
            "target_probability": self.target_probability,
            "most_likely_state": self.most_likely_state,
            "circuit": circuit_dict,
        }