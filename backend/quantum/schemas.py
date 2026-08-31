from pydantic import BaseModel, Field

class QuantumExperiment(BaseModel):
    algorithm: str = Field(default="grover")
    num_qubits: int = Field(default=2, ge=2, le=5)
    target_state: str
    iterations: int = Field(default=1, ge=1, le=5)
    shots: int = Field(default=1024, ge=100, le=10_000)