# Q-BIT.140 — Comprehensive File-by-File Forensic Reference

This document provides an exhaustive, code-grounded forensic inspection of every source file across the Q-BIT.140 repository.

---

# SECTION 1: M3 QUANTUM ENGINE SOURCE FILES

## 1.1 `backend/quantum/schemas.py`
- **Path**: `backend/quantum/schemas.py`
- **Module**: M3 (Quantum Engine)
- **Role**: Pure-Python dataclass defining quantum experiment input parameters.
- **Imports**: `dataclasses.dataclass`
- **Classes**:
  - `QuantumExperiment`: `algorithm: str`, `num_qubits: int = 2`, `target_state: str = "10"`, `iterations: int = 1`, `shots: int = 1024`.
- **Theory**: Encapsulates finite-shot measurement sampling parameter ($N_{\text{shots}} = 1024$).
- **Test Coverage**: `tests/quantum/test_schema.py::test_quantum_experiment_dataclass`.

## 1.2 `backend/quantum/validator.py`
- **Path**: `backend/quantum/validator.py`
- **Module**: M3 (Quantum Engine)
- **Role**: Gatekeeper validation function `validate_experiment()`.
- **Imports**: `backend.quantum.registry.ALGORITHM_REGISTRY`, `backend.quantum.schemas.QuantumExperiment`.
- **Validation**: Enforces registered algorithm check, positive shots ($> 0$), and `num_qubits == len(target_state)`.
- **Test Coverage**: `tests/quantum/test_validator.py`.

## 1.3 `backend/quantum/registry.py`
- **Path**: `backend/quantum/registry.py`
- **Module**: M3 (Quantum Engine)
- **Role**: Algorithm registry mapping string keys to circuit builders.
- **Data Structures**: `ALGORITHM_REGISTRY = {"grover_2q": build_grover_circuit}`.
- **Functions**: `get_algorithm(name: str) -> Callable`. Raises `ValueError` on unregistered algorithms.
- **Test Coverage**: `tests/quantum/test_registry.py`.

## 1.4 `backend/quantum/algorithms/grover.py`
- **Path**: `backend/quantum/algorithms/grover.py`
- **Module**: M3 (Quantum Engine)
- **Role**: Authoritative Qiskit circuit builder for Grover's 2-qubit algorithm.
- **External Imports**: `qiskit.QuantumCircuit`.
- **Functions**:
  - `_apply_multi_controlled_z(circuit, num_qubits)`: Applies `cz(0, 1)` for 2 qubits, or $H \rightarrow MCX \rightarrow H$ for $n > 2$.
  - `_apply_oracle(circuit, target_state)`: Reverses bitstring for Qiskit endianness (`target_state[::-1]`), applies $X$ gates on `'0'` bits, multi-controlled Z, and restores $X$ gates. Marks target state with a phase flip ($-|w\rangle$).
  - `_apply_diffusion(circuit, num_qubits)`: Implements $D = 2|s\rangle\langle s| - I$ via $H^{\otimes n} \rightarrow X^{\otimes n} \rightarrow CZ \rightarrow X^{\otimes n} \rightarrow H^{\otimes n}$. Inverts amplitudes about the mean.
  - `build_grover_circuit(num_qubits, target_state, iterations=1) -> QuantumCircuit`: Full circuit synthesis: uniform superposition ($H^{\otimes 2}$), oracle, diffusion, measurement.
- **Theory Connection**: Implements amplitude amplification. 1 iteration on 2 qubits rotates the state vector from $|s\rangle$ directly to $|w\rangle$, yielding theoretical probability $P(w) = 1.0$ ($100\%$).
- **Test Coverage**: `tests/quantum/test_grover.py`.

## 1.5 `backend/quantum/execution.py`
- **Path**: `backend/quantum/execution.py`
- **Module**: M3 (Quantum Engine)
- **Role**: Low-level simulation execution bridge.
- **External Imports**: `qiskit.QuantumCircuit`, `qiskit_aer.AerSimulator`.
- **Functions**: `execute_circuit(circuit: QuantumCircuit, shots: int = 1024) -> dict[str, int]`. Runs `AerSimulator().run(circuit, shots=shots).result().get_counts()`.
- **Test Coverage**: `tests/quantum/test_execution.py`.

## 1.6 `backend/quantum/results.py`
- **Path**: `backend/quantum/results.py`
- **Module**: M3 (Quantum Engine)
- **Role**: Qiskit-free domain results and metadata models.
- **Classes**:
  - `CircuitMetadata`: Snapshot of circuit depth, gate counts, qubit counts, and ASCII diagram.
  - `SimulationResult`: Canonical output containing `algorithm`, `target_state`, `shots`, `counts`, `circuit`. Computed properties: `probabilities`, `target_probability`, `most_likely_state`. Method: `to_dict()`.
- **Post-Init Invariants**: `shots > 0`, `counts >= 0`, `sum(counts) == shots`.
- **Test Coverage**: `tests/quantum/test_results.py`, `tests/quantum/test_circuit_metadata.py`.

## 1.7 `backend/quantum/engine.py`
- **Path**: `backend/quantum/engine.py`
- **Module**: M3 (Quantum Engine)
- **Role**: High-level execution orchestrator `run_experiment(experiment: QuantumExperiment) -> SimulationResult`.
- **Pipeline**: `validate_experiment` $\rightarrow$ `get_algorithm` $\rightarrow$ build circuit $\rightarrow$ `execute_circuit` $\rightarrow$ `extract_circuit_metadata` $\rightarrow$ return `SimulationResult`.
- **Test Coverage**: `tests/quantum/test_engine.py`, `tests/quantum/test_public_api.py`.

---

# SECTION 2: M2 ADAPTIVE LEARNER ENGINE SOURCE FILES

## 2.1 `backend/adaptive/concepts.py`
- **Path**: `backend/adaptive/concepts.py`
- **Module**: M2 (Adaptive Engine)
- **Role**: Defines canonical curriculum concept DAG and prerequisite dependencies.
- **Classes & Dataclasses**:
  - `Concept`: `id: str`, `name: str`, `prerequisites: tuple[str, ...]`, `concept_type: Literal["prerequisite", "core", "algorithm"]`, `description: str`.
- **DAG Constants**:
  - `CANONICAL_CONCEPTS`:
    1. `quantum.qubit` (Prerequisite, prereqs: ())
    2. `quantum.state` (Prerequisite, prereqs: (`quantum.qubit`,))
    3. `quantum.superposition` (Core, prereqs: (`quantum.qubit`, `quantum.state`))
    4. `quantum.gates` (Core, prereqs: (`quantum.qubit`, `quantum.state`))
    5. `quantum.measurement` (Core, prereqs: (`quantum.state`, `quantum.superposition`))
    6. `quantum.algorithm.grover_2q` (Algorithm, prereqs: (`quantum.qubit`, `quantum.state`, `quantum.superposition`, `quantum.gates`, `quantum.measurement`))
- **Functions**:
  - `get_concept(concept_id: str) -> Concept`: Lookup by canonical ID.
  - `get_prerequisites(concept_id: str) -> tuple[str, ...]`: Fetch immediate prerequisite IDs.
  - `resolve_concept_id(name_or_id: str) -> str`: Normalizes human display names (e.g. `"Superposition"`) to canonical IDs (`"quantum.superposition"`).
  - `get_concept_display_name(canonical_id: str) -> str`: Reverse lookup to human display name.
- **Test Coverage**: `tests/adaptive/test_models.py`, `tests/adaptive/test_state_semantics.py`.

## 2.2 `backend/adaptive/activities.py`
- **Path**: `backend/adaptive/activities.py`
- **Module**: M2 (Adaptive Engine)
- **Role**: Catalog of interactive learner activities and curriculum sequencing metadata.
- **Dataclasses**:
  - `Activity`: `activity_id: str`, `concept_id: str`, `title: str`, `description: str`, `task_type: Literal["quantum_prediction", "conceptual_choice"]`, `prompt: str`, `options: dict[str, str] | None`, `expected_answer: str | None`, `quantum_experiment: dict[str, Any] | None`, `prerequisites: tuple[str, ...]`, `remediation_activity_id: str | None`, `next_activity_id: str | None`.
- **Catalog (`MVP_ACTIVITIES`)**:
  1. `act_grover_2q_predict`: Task type `quantum_prediction`. Target state `"10"`. Options: `{"00": "|00⟩", "01": "|01⟩", "10": "|10⟩", "11": "|11⟩"}`. Remediation: `act_diag_superposition`. Next: `act_diag_grover_eval`.
  2. `act_diag_qubit`: Task type `conceptual_choice`. Prerequisite diagnostic for `quantum.qubit`.
  3. `act_diag_superposition`: Task type `conceptual_choice`. Prerequisite diagnostic for `quantum.superposition`. Remediation: `act_diag_qubit`. Next: `act_grover_2q_predict`.
  4. `act_diag_grover_eval`: Task type `conceptual_choice`. Post-experiment evaluation for `quantum.algorithm.grover_2q`.
- **Functions**: `get_activity(id)`, `list_activities()`, `get_activities_for_concept(concept_id)`.
- **Test Coverage**: `tests/adaptive/test_activities.py`.

## 2.3 `backend/adaptive/diagnostics.py`
- **Path**: `backend/adaptive/diagnostics.py`
- **Module**: M2 (Adaptive Engine)
- **Role**: Diagnostic quiz question loader and grading engine.
- **Dataclasses**:
  - `Question`: `topic: str`, `question: str`, `options: dict[str, str]`, `correct_answer: str`, `explanation: str`, `difficulty: str`, `concept_id: str`.
  - `QuizResult`: `total_questions: int`, `score: int`, `percentage: float`, `passed: bool`, `topic_breakdown: dict[str, dict]`.
- **Functions**:
  - `load_questions(csv_path: Optional[Path]) -> dict[str, list[Question]]`: Parses `quantum_tutor_quiz_dataset.csv` (25 questions across 5 concepts).
- **Test Coverage**: `tests/adaptive/test_diagnostics.py`.

## 2.4 `backend/adaptive/models.py`
- **Path**: `backend/adaptive/models.py`
- **Module**: M2 (Adaptive Engine)
- **Role**: Core domain state and recommendation dataclasses.
- **Dataclasses**:
  - `LearnerState`: Persistent learner profile. Fields: `user_id`, `concept_scores`, `attempts`, `errors`, `score_history`, `evidence_history`, `gap_inferences`, `created_at`, `updated_at`.
  - `AdaptiveRecommendation`: Output decision. Fields: `action: Literal["advance", "gather_evidence", "targeted_remediation", "reinforce_current_concept", "review_prerequisite"]`, `target: str | None`, `reason: str`, `concept_id: str`, `confidence: float`, `supporting_evidence_ids: list[str]`, `trigger: str`, `evidence_sufficiency: str`.
  - `LearnerContext`: Cognitive snapshot for M5 LLM context injection.
- **Test Coverage**: `tests/adaptive/test_models.py`, `tests/adaptive/test_state_semantics.py`.

## 2.5 `backend/adaptive/evidence.py`
- **Path**: `backend/adaptive/evidence.py`
- **Module**: M2 (Adaptive Engine)
- **Role**: Evidence evaluation and classification helpers.
- **Dataclasses**:
  - `LearnerEvidence`: `evidence_id`, `learner_id`, `activity_id`, `concept_id`, `evidence_type`, `evidence_source`, `learner_response`, `expected_response`, `is_correct`, `attempt_number`, `evidence_sufficiency`, `verified_result`, `timestamp`.
  - `GapInference`: `concept_id`, `confidence`, `status`, `supporting_evidence_count`, `description`, `trend`, `prerequisite_concept_id`, `hypothesis`, `supporting_evidence_ids`, `evidence_sufficiency`.
- **Functions**:
  - `evaluate_quantum_prediction()`: Evaluates quantum prediction vs simulation `most_likely_state`. Classifies sufficiency (`attempt == 1` $\rightarrow$ `insufficient`).
  - `evaluate_conceptual_response()`: Evaluates multiple choice selection vs expected answer.
- **Test Coverage**: `tests/adaptive/test_evidence.py`, `tests/adaptive/test_evidence_progression.py`, `tests/adaptive/test_pass4_evidence_trace.py`.

## 2.6 `backend/adaptive/repository.py`
- **Path**: `backend/adaptive/repository.py`
- **Module**: Persistence Layer
- **Role**: State storage abstraction with implementations for in-memory, JSON-file, and Supabase backends.
- **Classes**:
  - `LearnerRepository` (Abstract Base Class): `get(user_id) -> LearnerState`, `save(state: LearnerState) -> None`, `exists(user_id) -> bool`.
  - `InMemoryLearnerRepository`: Thread-safe in-memory dictionary storage.
  - `JSONFileLearnerRepository`: Local disk storage using JSON serialization with directory creation and atomic writes.
  - `SupabaseLearnerRepository`: Cloud PostgreSQL persistence via Supabase REST client with graceful offline fallback.
  - `PersistenceError`, `StorageUnavailableError`: Explicit persistence exception types.
- **Test Coverage**: `tests/adaptive/test_persistence_hardening.py`.

## 2.7 `backend/adaptive/engine.py`
- **Path**: `backend/adaptive/engine.py`
- **Module**: M2 (Adaptive Engine)
- **Role**: 4-Tier cognitive modeling and deterministic recommendation engine.
- **Classes**:
  - `LearnerModel`: Implements curriculum DAG graph traversal, mastery calculation, prerequisite bottleneck detection, and pedagogical routing.
- **Mastery Formula**:
  $$\text{Mastery}(c) = \frac{1.0 + \sum_{i=0}^{k-1} w_i \cdot S_i}{2.0 + \sum_{i=0}^{k-1} w_i}, \quad w_i = \lambda^{k-1-i} \quad (\lambda = 0.85)$$
- **Prerequisite Gate Rule**: Concept mastery is capped at the minimum mastery of its immediate prerequisites:
  $$\text{Mastery}_{\text{gated}}(c) = \min\left(\text{Mastery}(c), \min_{p \in \text{Prereqs}(c)} \text{Mastery}(p)\right)$$
- **Decision Rules**:
  - Correct Attempt $\rightarrow$ `action="advance"`, `target=activity.next_activity_id`.
  - Single Error $\rightarrow$ `action="gather_evidence"`, `target=activity.activity_id` (preliminary observation, no premature remediation).
  - Repeated Errors ($\ge 2$) $\rightarrow$ `action="targeted_remediation"`, routes to prerequisite diagnostic (e.g. `act_diag_superposition`).
- **Test Coverage**: `tests/adaptive/test_routing.py`, `tests/adaptive/test_mastery.py`, `tests/adaptive/test_vertical_slice.py`.

---

# SECTION 3: M5 GROUNDED AI GUIDANCE SOURCE FILES

## 3.1 `backend/ai/retrieval.py`
- **Path**: `backend/ai/retrieval.py`
- **Module**: M5 (AI Guidance)
- **Role**: Deterministic retrieval engine over local markdown knowledge files.
- **Functions**: `retrieve_context(query: str, max_snippets: int = 3, concept_id: Optional[str] = None) -> list[dict[str, str]]`. Scans 12 markdown documents in `backend/ai/knowledge/` using keyword matching and concept tags.
- **Test Coverage**: `tests/ai/test_retrieval.py`.

## 3.2 `backend/ai/prompts.py`
- **Path**: `backend/ai/prompts.py`
- **Module**: M5 (AI Guidance)
- **Role**: System prompts, grounded few-shot examples, and strict boundary instructions.
- **Constants**:
  - `SYSTEM_PROMPT`: Directs LLM to act as a grounded quantum tutor; forbids fabricating simulation results or overriding M2 mastery.
  - `EXPERIMENT_EXPLANATION_PROMPT`: Embeds `learner_response`, `verified_result`, `evidence`, and `adaptive_decision` into context.
  - `CONCEPT_TUTOR_PROMPT`: Formats general conceptual inquiries with retrieved knowledge snippets.
- **Test Coverage**: `tests/ai/test_m5_grounded_guidance.py`.

## 3.3 `backend/ai/providers.py`
- **Path**: `backend/ai/providers.py`
- **Module**: M5 (AI Guidance)
- **Role**: LLM provider abstractions with production Groq integration and deterministic offline MockLLM engine.
- **Classes**:
  - `LLMProvider` (ABC): `generate(messages: list[dict], model: Optional[str]) -> str`.
  - `MockLLMProvider`: 100% offline, deterministic intent matcher producing mathematically rigorous KaTeX explanations.
  - `GroqLLMProvider`: Production cloud LLM provider calling Groq completions API.
  - `get_default_provider()`: Factory returning `GroqLLMProvider` if `GROQ_API_KEY` exists, else falls back cleanly to `MockLLMProvider`.
- **Test Coverage**: `tests/ai/test_providers.py`, `tests/ai/test_m5_grounded_guidance.py`.

## 3.4 `backend/ai/service.py`
- **Path**: `backend/ai/service.py`
- **Module**: M5 (AI Guidance)
- **Role**: High-level guidance service facade exposing `ask_question()` and `explain_experiment()`.
- **Test Coverage**: `tests/ai/test_service.py`.

---

# SECTION 4: M4 BACKEND REST GATEWAY SOURCE FILES

## 4.1 `backend/api/schemas.py`
- **Path**: `backend/api/schemas.py`
- **Module**: M4 (REST Gateway)
- **Role**: Pydantic v2 schemas defining API data contracts.
- **Schemas**: `SubmissionRequest`, `SubmissionResponse`, `ActivitySummary`, `ActivityDetailResponse`, `AskRequest`, `AskResponse`, `ExplainExperimentRequest`, `ExplainExperimentResponse`, `HealthResponse`.
- **Test Coverage**: `tests/api/test_json_contracts.py`.

## 4.2 `backend/api/dependencies.py`
- **Path**: `backend/api/dependencies.py`
- **Module**: M4 (REST Gateway)
- **Role**: FastAPI dependency injection providers (`get_learner_repository`, `get_learner_model`, `get_llm_provider`).
- **Test Coverage**: `tests/api/test_adaptive_vertical_slice.py`.

## 4.3 `backend/api/main.py`
- **Path**: `backend/api/main.py`
- **Module**: M4 (REST Gateway)
- **Role**: FastAPI ASGI application entrypoint. Configures CORS middleware, mounts API routers under `/api/v1`, and serves frontend static files.
- **Test Coverage**: `tests/api/test_health.py`.

## 4.4 `backend/api/routes/health.py`
- **Path**: `backend/api/routes/health.py`
- **Module**: M4 (REST Gateway)
- **Role**: Health check endpoint `GET /health` returning `{"status": "ok", "service": "qbit-api", "version": "0.1.0"}`.
- **Test Coverage**: `tests/api/test_health.py`.

## 4.5 `backend/api/routes/activities.py`
- **Path**: `backend/api/routes/activities.py`
- **Module**: M4 (REST Gateway)
- **Role**: Core activity lifecycle routes:
  - `GET /api/v1/activities`: Returns summary list of activities.
  - `GET /api/v1/activity/{activity_id}`: Returns activity specification.
  - `POST /api/v1/activity/{activity_id}/submit`: Executes vertical slice (M3 simulation $\rightarrow$ M2 evidence $\rightarrow$ DB persistence $\rightarrow$ response).
- **Test Coverage**: `tests/api/test_activities.py`, `tests/api/test_submissions.py`, `tests/api/test_pass6_hardening_validation.py`.

## 4.6 `backend/api/routes/ai.py`
- **Path**: `backend/api/routes/ai.py`
- **Module**: M4 (REST Gateway)
- **Role**: AI guidance routes `POST /api/v1/ai/ask` and `POST /api/v1/ai/explain_experiment`.
- **Test Coverage**: `tests/api/test_ai.py`.

---

# SECTION 5: M1 / M6 FRONTEND & VISUALIZATION SOURCE FILES

## 5.1 `frontend/index.html`
- **Path**: `frontend/index.html`
- **Module**: M1 (Frontend UI)
- **Role**: Single-Page Application containing State Triad, Circuit Studio, Causal Timeline, State Inspector, and Tutor Chat.
- **Structure**:
  - Particle background canvas (`#fx`).
  - Top Navigation & Concept Badge tracker.
  - Interactive State Triad cards (Learner Prediction vs Theoretical Target vs Physical Result).
  - Grover 2-Qubit Visualizer with interactive probability bars.
  - Circuit Studio canvas with drag-and-drop / click-to-place quantum gate palette.
  - "Why This Next?" adaptive decision rationale callout.
  - AI Guidance panel with LaTeX rendering via KaTeX.
- **Test Coverage**: `tests/api/test_frontend_adapter_and_binding.py`, `tests/api/test_m1_m6_integration.py`.

## 5.2 `frontend/css/styles.css`
- **Path**: `frontend/css/styles.css`
- **Module**: M1 (Frontend UI)
- **Role**: Complete design system stylesheet featuring glassmorphism, responsive grid layouts, animations, and color tokens.

## 5.3 `frontend/js/api_client.js`
- **Path**: `frontend/js/api_client.js`
- **Module**: M1 (Frontend UI)
- **Role**: Asynchronous REST client wrapper for `fetch()` communicating with M4 backend.
- **Exports**: `fetchActivities()`, `fetchActivity()`, `submitPrediction()`, `explainExperiment()`, `askConceptualQuestion()`.

## 5.4 `frontend/js/adapter.js`
- **Path**: `frontend/js/adapter.js`
- **Module**: M6 (Visualization)
- **Role**: Client-side data presentation adapter.
- **Exports**:
  - `formatStateLabel(str)`: Formats `"10"` into Dirac notation `|10⟩`.
  - `formatPercentage(num)`: Formats `0.938` into `"93.8%"`.
  - `formatSufficiencyLabel(str)`: Translates sufficiency enums into human labels.
  - `formatTriggerLabel(str)`: Translates adaptive trigger keys into pedagogical descriptions.
  - `normalizeSubmissionResponse(json)`: Builds structured presentation view model for State Triad, probability bars, and timeline.
- **Test Coverage**: `tests/api/test_m6_adapter.py`, `tests/api/test_frontend_adapter_and_binding.py`.

## 5.5 `frontend/js/circuit_view.js`
- **Path**: `frontend/js/circuit_view.js`
- **Module**: M6 (Visualization)
- **Role**: Interactive 2-qubit circuit canvas renderer.
- **Exports**: `CircuitStudio` class, `GATE_DEFINITIONS` ($H, X, Z, CZ, CNOT$, Measure).
