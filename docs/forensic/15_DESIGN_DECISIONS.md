# Q-BIT.140 — Architecture Decision Records (ADR)

## ADR-001: Strict Separation of Quantum Engine (M3) and Learner Engine (M2)
- **Status**: **ACCEPTED & IMPLEMENTED**
- **Problem**: In educational software, quantum mechanics simulation logic and cognitive student modeling are frequently intertwined, causing physics rules to be distorted by pedagogical heuristics.
- **Decision**: M3 is an isolated, Qiskit-free physical simulator. M2 is a pure-Python cognitive model. M3 executes quantum circuits without knowing who the student is; M2 evaluates evidence without knowing how Qiskit constructs gates.
- **Tradeoff**: Requires M4 to orchestrate data transfer between M3 and M2, increasing boilerplate.
- **Code Evidence**: `backend/quantum/` has zero imports from `backend/adaptive/`, and `backend/adaptive/` has zero imports from `backend/quantum/` or `qiskit`.

## ADR-002: Deterministic Adaptive Decision Making vs LLM-Based Routing
- **Status**: **ACCEPTED & IMPLEMENTED**
- **Problem**: LLMs used as pedagogical decision makers suffer from hallucinations, inconsistent curriculum progression, and unrepeatable remediation paths.
- **Decision**: M2 is 100% deterministic, implementing formal graph traversal, Bayesian mastery formulas, and explicit rule tables. M5 (LLM) is strictly an explanation layer.
- **Tradeoff**: Creating new curriculum paths requires explicit DAG definition rather than dynamic prompt engineering.
- **Code Evidence**: `backend/adaptive/engine.py` contains zero imports from `backend/ai/` or LLM libraries.

## ADR-003: Qiskit-Free Serialization Boundary (`SimulationResult`)
- **Status**: **ACCEPTED & IMPLEMENTED**
- **Problem**: Qiskit circuit objects (`QuantumCircuit`, `DAGCircuit`) are complex C++/Python structures that cannot be JSON serialized and create heavy dependency burdens on API and UI layers.
- **Decision**: M3 converts all simulation outputs into `SimulationResult` and `CircuitMetadata` dataclasses containing only standard Python primitives (`int`, `str`, `dict`, `float`).
- **Tradeoff**: Downstream consumers cannot dynamically manipulate gates without calling M3 builder APIs.
- **Code Evidence**: `backend/quantum/results.py:SimulationResult.to_dict()`.

## ADR-004: State Triad UI Architecture
- **Status**: **ACCEPTED & IMPLEMENTED**
- **Problem**: Novice quantum students frequently conflate their prediction, the theoretical target, and empirical measurement counts.
- **Decision**: The UI explicitly renders three distinct cards in every activity: (1) Learner Prediction, (2) Theoretical Target, (3) Physical Simulation Result.
- **Tradeoff**: Requires more screen real estate.
- **Code Evidence**: `frontend/index.html` lines 250–310, `frontend/js/adapter.js:normalizeSubmissionResponse`.

## ADR-005: 100% Offline Fallback via `MockLLMProvider`
- **Status**: **ACCEPTED & IMPLEMENTED**
- **Problem**: Hackathon environments, student classrooms, and offline evaluations cannot rely on guaranteed external LLM API connectivity or paid API credits.
- **Decision**: Implement `MockLLMProvider` featuring a 9-tier deterministic intent engine producing KaTeX-formatted quantum explanations.
- **Tradeoff**: Pre-defined explanations cover curriculum topics thoroughly but cannot answer arbitrary out-of-domain trivia.
- **Code Evidence**: `backend/ai/providers.py:MockLLMProvider`.
