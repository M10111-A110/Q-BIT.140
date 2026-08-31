# Q-BIT.140

## AI-Based Interactive Quantum Algorithm Learning Platform

Q-BIT.140 is an adaptive quantum-computing learning prototype designed for SIH 2026.

The platform connects:

1. Interactive quantum experimentation
2. Verified quantum execution
3. Learner evidence
4. Deterministic learner modeling
5. Adaptive activity selection
6. Grounded AI explanations
7. Visualization of quantum and learning state

The project is intentionally focused on demonstrating this connected workflow rather than building a general-purpose quantum-learning platform.

---

# Problem

Quantum computing education can be difficult for beginners because learners must simultaneously understand:

- abstract quantum concepts,
- quantum states and notation,
- circuit construction,
- quantum gates,
- probabilistic measurement,
- algorithmic reasoning,
- and the relationship between circuit operations and observed outcomes.

A learner may be able to answer a theoretical question while still misunderstanding what a quantum circuit will actually produce.

Q-BIT therefore aims to connect learning assessment with experimentation:

```text
Conceptual Understanding
        +
Learner Prediction / Attempt
        +
Verified Quantum Experiment
        ↓
Evidence About Understanding
        ↓
Adaptive Learning Response
```

---

# Core Idea

Q-BIT separates the responsibilities of the quantum engine, learner model, integration layer, and AI guidance system.

## Quantum Layer — M3

Answers:

> **What actually happened when the experiment was executed?**

M3 is responsible for:

- experiment schemas,
- validation,
- circuit construction,
- quantum execution,
- and normalized quantum results.

M3 is the source of verified quantum evidence.

---

## Learner Model — M2

Answers:

> **What does the accumulated learner evidence indicate?**

M2 is responsible for:

- learner state,
- prerequisite reasoning,
- diagnostics,
- mastery interpretation,
- evidence aggregation,
- candidate conceptual-gap interpretation,
- adaptive decisions,
- and explaining why an intervention or next activity was selected.

M2 should use deterministic and explainable rules for the MVP.

A single incorrect response or prediction should not automatically be treated as proof of a misconception. M2 should distinguish observed evidence from inference and maintain confidence where appropriate.

M2 does not execute quantum circuits.

---

## Backend / Integration — M4

Answers:

> **How are the components connected reliably?**

M4 is responsible for:

- API endpoints,
- request/response orchestration,
- persistence,
- authentication/integration,
- and communication between components.

M4 should use public module contracts rather than internal implementation details.

---

## AI Guidance — M5

Answers:

> **How should the evidence and decision be explained to the learner?**

M5 is responsible for:

- context construction,
- retrieval of relevant learning material,
- prompt construction,
- explanations,
- and learner-facing guidance.

M5 does not determine learner mastery and does not fabricate quantum results.

---

## Visualization — M6

Answers:

> **How can the learner understand what happened and why?**

M6 is responsible for presenting:

- learner predictions,
- verified quantum results,
- evidence,
- interpretations,
- and adaptive decisions.

---

# Evidence-Driven Adaptive Experimentation

The central MVP mechanism is an evidence-driven adaptive workflow.

The system should not simply give the learner another generic question after every attempt.

Instead, the intended mechanism is:

```text
Learner Evidence
      ↓
Learner-State Interpretation
      ↓
Identify Remaining Gap / Uncertainty / Candidate Conceptual Issue
      ↓
Select Targeted Diagnostic Activity
      ↓
Learner Prediction / Attempt
      ↓
Verified Quantum Execution
      ↓
New Evidence
      ↓
Update Learner State
      ↓
Select Next Activity
```

For example:

```text
Learner predicts an incorrect measurement distribution
                    ↓
Evidence suggests uncertainty about probability
                    ↓
System selects a targeted probability activity
                    ↓
Learner makes another prediction
                    ↓
Quantum experiment is executed
                    ↓
New evidence is collected
                    ↓
Learner state is updated
```

### Differentiation focus

The MVP uses quantum experiments not only to demonstrate concepts, but also to collect evidence about learner understanding and determine what additional evidence or learning intervention is appropriate next.

Q-BIT does **not** claim that this overall educational approach is unprecedented. The intended differentiation is the concrete implementation and evaluation of this evidence-driven mechanism within a quantum-computing learning workflow.

The system identifies patterns consistent with possible conceptual gaps; it does not claim certainty about a learner's conceptual state.

---

# MVP Scope

The MVP focuses on **one quantum algorithm**:

## Grover's Algorithm

The initial quantum implementation uses:

- Python
- Qiskit
- Qiskit Aer
- simulated execution

Grover is used as the primary proof case because it provides a compact setting in which learners can demonstrate understanding of:

- qubits,
- quantum states,
- superposition,
- measurement probability,
- oracle concepts,
- amplitude amplification,
- diffusion,
- circuit construction,
- and algorithmic reasoning.

The MVP deliberately avoids adding many algorithms merely for feature count.

---

## MVP Diagnostic Activities

The adaptive mechanism is intended to use a small set of carefully designed Grover/prerequisite activities.

Each activity should define:

- concept being tested,
- prerequisites,
- learner task,
- prediction or expected response,
- verified result where applicable,
- evidence captured,
- possible learner-state interpretations,
- follow-up selection rule,
- and remediation activity.

The MVP should use approximately **3–5 diagnostic activities** rather than a large activity framework.

---

## Target MVP Learning Flow

The intended learner workflow is:

1. Learner receives a diagnostic or learning activity.
2. Learner makes a prediction or attempt.
3. The associated quantum experiment is executed when applicable.
4. The verified result is returned.
5. Learner evidence is constructed from the attempt and result.
6. M2 updates or interprets the learner state.
7. M2 determines whether additional evidence or progression is appropriate.
8. A targeted next activity is selected.
9. M5 explains the evidence and decision.
10. M1/M6 present the result, interpretation, and next activity.

The end-to-end adaptive behavior is being validated incrementally during integration.

---

# Evidence and Decision Boundaries

Q-BIT distinguishes three layers.

## Observed Evidence

Observed evidence consists of facts directly produced by the learner or verified execution system.

Examples:

- learner prediction,
- learner answer,
- quiz score,
- selected gate,
- circuit attempt,
- quantum counts,
- measured probabilities,
- target state,
- most likely state,
- experiment metadata.

## Learner-State Inference

Inference is produced by M2 from accumulated evidence.

Examples:

- likely prerequisite gap,
- possible conceptual misunderstanding,
- repeated prediction error,
- insufficient evidence for progression,
- sufficient evidence for progression.

M2 owns these decisions.

## AI Explanation

M5 communicates evidence and M2 decisions to the learner.

M5 should not:

- independently determine mastery,
- overwrite learner state,
- fabricate simulation results,
- execute arbitrary code,
- or become the sole authority for adaptive decisions.

---

# Current Status

Q-BIT is currently in the **integration and rectification phase**.

The repository contains implemented foundations across multiple components, while the complete evidence-driven adaptive loop is still being connected and validated.

## Existing foundations

### M2

The learner-model work provides foundations for:

- prerequisite relationships,
- diagnostics,
- learner state,
- mastery calculation,
- error tracking,
- learner history,
- and deterministic adaptive routing.

### M3

The quantum engine provides:

- experiment schemas,
- validation,
- Grover circuit construction,
- Qiskit/Aer execution,
- and normalized simulation results.

### M5

The AI guidance component provides:

- curated quantum-learning knowledge,
- deterministic retrieval,
- guidance rules,
- and an LLM-based explanation layer.

### M1 / M4 / M6

Frontend, backend/integration, and visualization foundations exist and are being connected to the shared component contracts.

---

## Current Integration Goal

The next integration target is:

```text
Learner Attempt
      ↓
M3 Quantum Execution
      ↓
Verified Simulation Result
      ↓
Structured Learner Evidence
      ↓
M2 Learner-State Update
      ↓
Adaptive Decision
      ↓
M5 Grounded Guidance
      ↓
M1 / M6 Presentation
      ↓
Next Activity
```

The project should not claim that this entire loop is complete until it is demonstrated by integration tests and the running MVP.

---

# System Architecture

```text
                         ┌────────────────────┐
                         │    M1 — Learner    │
                         │     Interface      │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │ M4 — API /         │
                         │ Integration        │
                         └─────────┬──────────┘
                                   │
             ┌─────────────────────┼─────────────────────┐
             │                     │                     │
             ▼                     ▼                     ▼
       ┌───────────┐         ┌───────────┐         ┌───────────┐
       │ M2        │         │ M3        │         │ M5        │
       │ Learner   │         │ Quantum   │         │ AI        │
       │ Model     │         │ Engine    │         │ Guidance  │
       └─────┬─────┘         └─────┬─────┘         └─────┬─────┘
             │                     │                     │
             └─────────────────────┼─────────────────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │ M6 — Visualization │
                         └────────────────────┘
```

---

# Current MVP Design

The MVP should make the adaptive mechanism visible to the learner and to evaluators.

The learner should be able to see:

```text
Your Prediction
       ↓
Verified Quantum Result
       ↓
Evidence Observed
       ↓
What the System Interprets
       ↓
Why This Activity Was Selected
       ↓
Next Activity
```

The most important demonstrable behavior is:

```text
Evidence A
    ↓
Detected uncertainty / gap
    ↓
Diagnostic Activity B selected
    ↓
New learner evidence
    ↓
Updated learner state
    ↓
Different or more advanced next activity
```

The system should be able to explain the reason for the adaptive decision using structured evidence.

---

# Evaluation Direction

The MVP should eventually support evaluation of the adaptive workflow using meaningful metrics.

Potential metrics include:

- prediction accuracy,
- prerequisite improvement,
- conceptual-question improvement,
- recurrence of the same error,
- post-intervention performance,
- number of attempts required,
- successful progression,
- correctness of adaptive activity selection.

Metrics should be tied to actual learning behavior and system decisions.

Avoid metrics that merely measure feature usage without demonstrating educational value.

---

# Development Principles

## 1. Separation of concerns

Each module owns its defined responsibility and exposes stable public contracts.

## 2. Evidence before strong inference

A single incorrect response or prediction is not sufficient evidence of a conceptual misunderstanding.

## 3. Verified quantum results are authoritative

M3 execution results are the source of truth for what happened in a supplied experiment.

## 4. AI is a learning guide

M5 explains verified evidence and M2 decisions; it does not become the source of truth for quantum execution or learner state.

## 5. Test before integration

New functionality should have automated tests before becoming part of the shared integration flow.

## 6. Controlled MVP scope

The MVP uses Grover's Algorithm as the primary algorithm. Additional algorithms should only be added if they provide meaningful educational or evaluation value.

---

# Getting Started

## Prerequisites

Install:

- Git
- Python 3.11+
- Node.js / npm
- GitHub repository access

A Python virtual environment is recommended.

## Clone

```bash
git clone https://github.com/M10111-A110/Q-BIT.140.git
cd Q-BIT.140
```

## Python Virtual Environment

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Install Python Dependencies

```bash
pip install -r requirements.txt
```

If the requirements file is not yet finalized:

```bash
pip install qiskit qiskit-aer pydantic pytest fastapi uvicorn
```

---

# Environment Variables

Create a local `.env` file based on `.env.example`.

Example:

```env
SUPABASE_URL=
SUPABASE_KEY=

LLM_API_KEY=

DATABASE_URL=
```

Never commit:

- API keys,
- Supabase secrets,
- database credentials,
- LLM credentials,
- private tokens,
- or other secrets.

Only `.env.example` with placeholder values should be committed.

---

# Running the Project

The exact full-stack commands are being finalized as M1–M6 are integrated.

## Backend

The intended API stack is FastAPI.

Typical development command:

```bash
uvicorn backend.api.main:app --reload
```

## Frontend

Typical Next.js development commands:

```bash
npm install
npm run dev
```

---

# Testing

The project uses `pytest` for Python components.

Run all tests:

```bash
pytest
```

Run quantum-engine tests:

```bash
pytest tests/quantum
```

Run adaptive learner-model tests:

```bash
pytest tests/adaptive
```

Run a specific test file:

```bash
pytest tests/quantum/test_execution.py
```

Tests should remain deterministic wherever possible.

---

# Repository Structure

```text
Q-BIT.140/
│
├── frontend/                         # M1 + M6
│
├── backend/
│   ├── adaptive/                     # M2
│   ├── quantum/                      # M3
│   │   └── algorithms/
│   ├── api/                          # M4
│   └── ai/                           # M5
│
├── tests/
│   ├── adaptive/
│   ├── quantum/
│   ├── api/
│   └── ai/
│
├── content/                          # Shared learning content
├── docs/
│   └── architecture/
├── experiments/
├── .env.example
├── .gitignore
├── README.md
├── pytest.ini
├── requirements.txt
└── ...
```

### Ownership rule

Each member owns their designated component. Other members should interact through its public interface rather than importing internal implementation details.

---

# Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React / Next.js |
| Frontend Language | TypeScript |
| Backend | Python |
| API | FastAPI |
| Quantum Framework | Qiskit |
| Quantum Simulation | Qiskit Aer |
| Database | PostgreSQL via Supabase |
| AI | LLM API — provider TBD |
| Testing | pytest |
| Version Control | Git + GitHub |

The AI provider remains undecided and should be kept provider-agnostic until the team makes a final decision.

---

# Future Scope

Potential future extensions include:

- additional quantum algorithms,
- real quantum hardware execution,
- richer learner models,
- additional diagnostic activity types,
- improved retrieval,
- broader quantum-learning curricula,
- expanded analytics,
- and larger-scale evaluation.

These are outside the minimum MVP unless they provide clear educational or evaluation value.

---

# Contributing

Before contributing:

1. Pull the latest `main`.
2. Create a feature branch.
3. Work within your component unless cross-component changes are required.
4. Add or update tests.
5. Run the test suite.
6. Commit using the project convention.
7. Push your branch.
8. Open a Pull Request.
9. Request review from the relevant member(s).
10. Merge only after integration checks pass.

---

# License

License: **TBD**

---

## Project Repository

GitHub: `https://github.com/M10111-A110/Q-BIT.140`

## Team

**Q-BIT.140 — SIH 2026**

| Designation | Area |
|---|---|
| M1 | Frontend / Learner Experience |
| M2 | Adaptive Learner Model |
| M3 | Quantum Engine |
| M4 | Backend / Integration |
| M5 | AI Guidance |
| M6 | Visualization |
