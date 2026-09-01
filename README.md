# Q-BIT.140

## AI-Based Interactive Quantum Algorithm Learning Platform

Q-BIT.140 is an evidence-driven adaptive quantum-computing learning prototype designed for **Smart India Hackathon (SIH) 2026** (Problem Statement provided by **Egreen Quanta**).

The platform bridges the gap between abstract quantum theory and hands-on physical execution:

```text
PREDICT
  ↓
EXECUTE (Qiskit Aer)
  ↓
OBSERVE (State Triad & Measurement Counts)
  ↓
RECORD EVIDENCE (Deterministic Evidence IDs)
  ↓
INTERPRET (M2 Cognitive Gap Inference & Sufficiency)
  ↓
ADAPT ("Why This Next?" Pedagogical Routing)
  ↓
EXPLAIN (Grounded M5 KaTeX Guidance)
  ↓
RETRY (Post-Intervention Recovery & Advancement)
```

---

## Strategic Alignment & Bounded MVP Scope

Beginners often struggle with quantum computing because they can memorize theoretical formulas while failing to understand how circuits physically execute and collapse under measurement.

Q-BIT.140 addresses this by using **Grover's 2-Qubit Algorithm** as a bounded, rigorous proof scenario. The MVP demonstrates:

1. **Prediction vs Verified Quantum Execution**: Learners predict the computational basis state outcome before executing a 1024-shot simulation on Qiskit Aer.
2. **State Triad Separation**: Explicitly distinguishes **Learner Prediction** ($|01\rangle$) $\neq$ **Theoretical Target** ($|10\rangle$) $\neq$ **Empirical Measurement** ($|10\rangle$ at $93.8\%$).
3. **Deterministic Evidence Semantics**: Every attempt produces an auditable `LearnerEvidence` record with a unique ID and sufficiency classification (`insufficient` $\rightarrow$ `sufficient_for_targeted_inference` $\rightarrow$ `sufficient_for_improvement_observation` $\rightarrow$ `sufficient_for_mastery`).
4. **Deterministic Adaptive Modeling (M2)**: M2 is the sole decision authority. A single error triggers evidence gathering (`gather_evidence`); repeated errors escalate to prerequisite remediation (`targeted_remediation`).
5. **Grounded AI Guidance (M5)**: AI explanations are strictly constrained by verified simulation counts and the M2 decision trace. M5 never fabricates results or makes adaptive decisions.

---

## Canonical 5-Step Evaluator Demo Journey

| Step | Learner Action | Verified Quantum Result (M3) | M2 Cognitive State | Adaptive Decision & Rationale ("Why This Next?") |
| :---: | :--- | :--- | :--- | :--- |
| **1** | Predicts $\|01\rangle$ on Grover 2Q | Simulated $\|10\rangle$ ($93.8\%$) | `insufficient` evidence; preliminary observation | **`gather_evidence`**: Single mismatch is insufficient to infer a conceptual gap. Prompts retry. |
| **2** | Predicts $\|00\rangle$ on Grover 2Q | Simulated $\|10\rangle$ ($93.8\%$) | `sufficient_for_targeted_inference`; possible Grover difficulty ($90\%$ confidence) | **`targeted_remediation`**: Repeated errors cite Attempt #1 & #2 records $\rightarrow$ routes to *Measurement Probability Diagnostic*. |
| **3** | Answers Born's Rule MCQ: Option B | N/A (Conceptual diagnostic) | Prerequisite bottleneck resolved | **`advance`**: Mastery demonstrated $\rightarrow$ routes back to Grover retry. |
| **4** | Predicts $\|10\rangle$ on Grover 2Q | Simulated $\|10\rangle$ ($93.8\%$) | `sufficient_for_improvement_observation`; post-intervention recovery | **`advance`**: Success following remediation demonstrates recovery $\rightarrow$ advances to *Grover Iteration Reasoning*. |
| **5** | Clicks "Explain My Result" | Physical Oracle & Diffusion analysis | Grounded in empirical counts | **M5 AI Guidance**: Explains phase inversion ($O\|w\rangle = -\|w\rangle$) and diffusion ($D = 2\|s\rangle\langle s\| - I$) without altering M2 decisions. |

---

## System Architecture (M1–M6)

```text
                         ┌──────────────────────────────────┐
                         │   M1 / M6 Presentation Layer     │
                         │ (Circuit Studio, State Triad, UX)│
                         └─────────────────┬────────────────┘
                                           │ HTTP REST / JSON
                                           ▼
                         ┌──────────────────────────────────┐
                         │      M4 FastAPI Gateway          │
                         │   (Pydantic Validation & Auth)   │
                         └─────┬───────────┼──────────┬─────┘
                               │           │          │
                               ▼           ▼          ▼
                     ┌───────────┐   ┌───────────┐   ┌───────────┐
                     │ M3        │   │ M2        │   │ M5        │
                     │ Quantum   │   │ Learner   │   │ AI        │
                     │ Engine    │   │ Model     │   │ Guidance  │
                     └─────┬─────┘   └─────┬─────┘   └───────────┘
                           │               │
                           │               ▼
                           │     ┌───────────────────┐
                           │     │ Persistence Layer │
                           │     │(InMemory/DB/JSON) │
                           │     └───────────────────┘
                           ▼
                 ┌───────────────────┐
                 │ Qiskit Aer (1024) │
                 └───────────────────┘
```

- **M1 / M6 (Presentation)**: Pure view-model consumer. No client-side mastery math or duplicate routing logic.
- **M2 (Learner Model)**: Sole authority for cognitive state, evidence sufficiency, hypotheses, and pedagogical actions. Purely deterministic; zero LLM dependency.
- **M3 (Quantum Engine)**: Sole authority for physical execution and measurement counts. **100% frozen.**
- **M4 (Backend Gateway)**: Pure JSON serialization, strict input validation, transparent error handling (404/500/503).
- **M5 (AI Guidance)**: Explanation-only layer grounded in M3 results and M2 traces.
- **Persistence Layer**: Fail-safe repository preventing corrupted states or silent resets.

---

## Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | Modern HTML5 / CSS3 / ES Modules / KaTeX | Lightweight, zero-build client with Dirac notation & KaTeX math |
| **Backend API** | FastAPI / Pydantic / Uvicorn | High-performance asynchronous REST API gateway (M4) |
| **Quantum Engine** | Qiskit 1.0+ / Qiskit Aer | Authoritative quantum circuit construction & 1024-shot simulation (M3) |
| **Learner Engine** | Python 3.11+ / Dataclasses | Deterministic cognitive DAG, mastery modeling & decision engine (M2) |
| **AI Guidance** | Python / Groq LLM API / MockLLM | Grounded curriculum explanation layer with offline fallback (M5) |
| **Testing** | pytest / pytest-asyncio | 295 automated unit, integration, and regression tests |

---

## Quickstart Guide

### 1. Prerequisites
- Python 3.11+
- Git

### 2. Setup Virtual Environment
```bash
git clone https://github.com/M10111-A110/Q-BIT.140.git
cd Q-BIT.140

# Windows
python -m venv .venv
.\.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
Start the FastAPI server (serves the API and interactive frontend):
```bash
uvicorn backend.api.main:app --reload --port 8000
```
Open your browser at:
```text
http://127.0.0.1:8000/frontend/index.html
```

---

## Running Automated Tests

Run the complete test suite (295 tests):
```bash
pytest -q
```

Run specific test modules:
```bash
# Quantum Engine tests
pytest tests/quantum

# Adaptive Learner & Provenance tests
pytest tests/adaptive

# API Contracts & Evaluator Journey tests
pytest tests/api
```

---

## Limitations & Deferred Scope

The following capabilities are deliberately outside the bounded MVP scope:
- **Multi-Algorithm Library**: Grover's algorithm is the dedicated proof scenario; Shor's algorithm and VQE are deferred.
- **Real Quantum Hardware Backends**: Qiskit Aer simulation is used to ensure deterministic, zero-queue response times during evaluation.
- **Instructor / School Dashboards**: Focus is placed entirely on the active learner adaptive feedback loop.
- **Machine Learning Black-Box Grading**: M2 uses explainable cognitive graph rules rather than un-auditable neural network scoring.

---

## Team & License

**Q-BIT.140 — SIH 2026**
- **Problem Statement Organization**: Egreen Quanta
- **License**: MIT
