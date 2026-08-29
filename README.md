# Q-BIT — AI-Based Interactive Quantum Algorithm Learning Platform

An AI-based interactive learning platform for learning quantum algorithms through guided experimentation, verified quantum execution, learner modeling, and adaptive AI feedback.

> **SIH 2026 Project — Q-BIT.140**

## Table of Contents

- [Overview](#overview)
- [Problem](#problem)
- [Core Idea](#core-idea)
- [MVP Scope](#mvp-scope)
- [System Architecture](#system-architecture)
- [Team Responsibilities](#team-responsibilities)
- [Repository Structure](#repository-structure)
- [Technology Stack](#technology-stack)
- [Development Principles](#development-principles)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Running the Project](#running-the-project)
- [Testing](#testing)
- [Git Workflow](#git-workflow)
- [Component Boundaries](#component-boundaries)
- [M3 Quantum Engine Contract](#m3-quantum-engine-contract)
- [Integration Flow](#integration-flow)
- [Current MVP Design](#current-mvp-design)
- [Future Scope](#future-scope)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

Q-BIT is built around a closed learning loop:

```text
Learner
   ↓
Prediction / Attempt
   ↓
Quantum Experiment
   ↓
Verified Quantum Evidence
   ↓
Learner Model
   ↓
Adaptive Interpretation
   ↓
AI Guidance
   ↓
Next Learning Activity
   ↓
New Evidence
```

The platform connects interactive experimentation, verified quantum execution, learner evidence, adaptive learner modeling, and AI-supported explanations.

---

## Problem

Quantum computing education can be difficult for beginners because learners must simultaneously understand abstract quantum concepts, circuit notation, algorithmic reasoning, probabilistic measurement, and the relationship between circuit operations and observed outcomes.

Q-BIT aims to connect:

1. Interactive experimentation
2. Verified quantum execution
3. Learner evidence
4. Adaptive learner modeling
5. AI-supported explanations and guidance

---

## Core Idea

The platform separates the responsibilities of the quantum engine, learner model, and AI system.

### Quantum layer — M3

Answers:

> **What actually happened when the experiment was executed?**

M3 constructs, validates, executes, and normalizes quantum experiments.

### Learner model — M2

Answers:

> **What does the learner's evidence indicate?**

M2 uses learner attempts, predictions, history, and quantum evidence to reason about learning progress.

### AI layer — M5

Answers:

> **How should this be explained or guided to the learner?**

M5 receives structured context and verified evidence rather than being the source of truth for quantum execution.

---

# MVP Scope

The MVP focuses on **one quantum algorithm**:

## Grover's Algorithm

The initial quantum implementation uses:

- Python
- Qiskit
- Qiskit Aer
- simulated execution

The MVP is intentionally constrained so the team can demonstrate a complete learning loop instead of building a general-purpose quantum-computing platform.

### MVP learning flow

1. Learner receives a Grover activity.
2. Learner makes a prediction.
3. The experiment is executed.
4. The measured result is displayed.
5. The prediction is compared with the outcome.
6. Learner evidence is produced.
7. The learner model interprets the evidence.
8. AI guidance is generated.
9. The learner continues with a targeted activity.

---

# System Architecture

```text
                         ┌──────────────────┐
                         │     M1 — UI      │
                         │ Learner Interface│
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │   M4 — API/DB    │
                         │ FastAPI + Supabase│
                         └────────┬─────────┘
                                  │
             ┌────────────────────┼────────────────────┐
             │                    │                    │
             ▼                    ▼                    ▼
      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
      │ M2 — Learner│      │ M3 — Quantum│      │ M5 — AI     │
      │ Model       │      │ Engine      │      │ Guidance    │
      └──────┬──────┘      └──────┬──────┘      └──────┬──────┘
             │                    │                    │
             │                    ▼                    │
             │             ┌─────────────┐             │
             │             │ Qiskit/Aer  │             │
             │             └─────────────┘             │
             │                                         │
             └────────────────────┬────────────────────┘
                                  ▼
                         ┌──────────────────┐
                         │ M6 — Visualization│
                         └──────────────────┘
```

### Logical learning loop

```text
Prediction
    ↓
Experiment
    ↓
Quantum Execution
    ↓
Verified Result
    ↓
Learner Evidence
    ↓
Learner Model
    ↓
AI Guidance
    ↓
Next Experiment
```

---

# Team Responsibilities

| Member | Designation | Responsibility | Primary Technologies |
|---|---|---|---|
| **M1** | Frontend / Learner Experience | Learner-facing interface and interaction flow | React / Next.js / TypeScript |
| **M2** | Adaptive Learner Model | Prerequisites, diagnostics, mastery, learner context, adaptation | Python |
| **M3** | Quantum Engine | Experiment schemas, validation, algorithms, execution, normalized results | Python / Qiskit / Aer |
| **M4** | Backend / Integration | API, persistence, and integration between components | Python / FastAPI / Supabase |
| **M5** | AI Guidance | Context construction, prompting, explanations and guidance | Python / LLM API |
| **M6** | Visualization | Quantum-result visualization and frontend visualization integration | TypeScript / React |

---

# Repository Structure

The project uses a monorepo so all six members can work independently while sharing stable interfaces.

```text
Q-BIT.140/
│
├── frontend/                         # M1 + M6
│
├── backend/
│   ├── adaptive/                     # M2
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── rules.py
│   │   ├── diagnostics.py
│   │   └── ...
│   │
│   ├── quantum/                      # M3
│   │   ├── __init__.py
│   │   ├── schemas.py
│   │   ├── validator.py
│   │   ├── execution.py
│   │   ├── results.py
│   │   ├── engine.py
│   │   └── algorithms/
│   │       ├── __init__.py
│   │       └── grover.py
│   │
│   ├── api/                          # M4
│   │   ├── __init__.py
│   │   ├── routes/
│   │   └── ...
│   │
│   └── ai/                           # M5
│       ├── __init__.py
│       ├── context.py
│       ├── prompts.py
│       └── ...
│
├── tests/
│   ├── adaptive/                     # M2
│   ├── quantum/                      # M3
│   ├── api/                          # M4
│   └── ai/                           # M5
│
├── content/                          # Shared learning content
│   ├── concepts/
│   └── ...
│
├── docs/
│   └── architecture/
│
├── experiments/                      # Optional experiment configurations
│
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

# Development Principles

## 1. Separation of concerns

```text
M3 → executes quantum experiments
M2 → interprets learner evidence
M5 → generates explanations/guidance
M4 → connects components and persistence
```

Do not duplicate these responsibilities across members.

## 2. Stable interfaces

Other components should depend on public contracts rather than internal implementation.

For example, M4 should eventually call:

```python
result = run_experiment(experiment)
```

rather than constructing Qiskit circuits directly.

## 3. Verified quantum evidence

Quantum results must originate from the quantum execution layer. The AI layer should not independently invent or modify quantum results.

## 4. Test before integration

New functionality should have tests before it is exposed to other components.

## 5. Controlled MVP scope

The MVP uses Grover's Algorithm as the single algorithm. The surrounding quantum infrastructure should remain general enough for additional algorithms later.

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

## Python virtual environment

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

## Install Python dependencies

```bash
pip install -r requirements.txt
```

If the requirements file has not yet been finalized:

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

Never commit `.env` or files containing API keys, Supabase secrets, database credentials, LLM credentials, or private tokens.

Only `.env.example` with placeholder values should be committed.

---

# Running the Project

The exact full-stack commands will be finalized as M1–M6 components are integrated.

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

Run only quantum-engine tests:

```bash
pytest tests/quantum
```

Run a specific test file:

```bash
pytest tests/quantum/test_execution.py
```

Tests should remain deterministic wherever possible.

---

# Git Workflow

Because six members are working remotely, the project uses a **branch + pull request workflow**.

## Main branch

```text
main
```

`main` should contain integration-ready code. Do not push unfinished feature work directly to `main`.

## Member branches

Examples:

```text
feature/m1-learner-ui
feature/m2-learner-model
feature/m3-quantum-engine
feature/m4-api
feature/m5-ai-guidance
feature/m6-visualization
```

For smaller tasks:

```text
feature/m3-result-schema
feature/m3-grover-tests
```

## Basic workflow

```bash
git checkout main
git pull origin main

git checkout -b feature/m3-result-schema
```

After making changes:

```bash
git add .
git commit -m "feat(quantum): add normalized result schema"
git push -u origin feature/m3-result-schema
```

Open a Pull Request into `main`.

---

# Commit Convention

Use concise conventional-style commits.

Examples:

```text
feat(quantum): add Grover circuit
feat(api): add experiment endpoint
feat(adaptive): add mastery rule
feat(ai): add learner context builder
feat(frontend): add experiment panel

fix(quantum): correct measurement bit ordering

test(quantum): add Grover target-state tests

docs: update architecture documentation

refactor(quantum): separate execution layer
```

Avoid commits such as:

```text
stuff
final
final_final
changes
working
```

---

# Pull Request Rules

Before opening a PR:

```bash
git pull origin main
pytest
```

A PR should explain:

- what changed,
- why it changed,
- what was tested,
- whether another member needs to update their code.

Keep PRs focused and logically scoped.

### Cross-component changes

If a change affects another member's contract:

1. Communicate with that member first.
2. Document the contract change.
3. Update affected tests.
4. Update relevant architecture documentation.

---

# Component Boundaries

## M1 — Frontend / Learner Experience

M1 owns the learner-facing interaction.

M1 should consume backend data through the API.

M1 should not directly import Qiskit or M3's internal quantum modules.

## M2 — Adaptive Learner Model

M2 owns:

- learner state,
- prerequisites,
- diagnostics,
- mastery interpretation,
- adaptation rules,
- learner context.

M2 consumes verified quantum evidence from M3.

M2 should not execute quantum circuits.

## M3 — Quantum Engine

M3 owns:

- quantum experiment schemas,
- quantum validation,
- algorithm implementations,
- circuit construction,
- quantum execution,
- result normalization,
- quantum-specific errors.

M3 should not decide what a learner understands.

## M4 — Backend / Integration

M4 owns:

- API endpoints,
- authentication/integration,
- persistence,
- communication between services/components.

M4 should use M3's public interface instead of depending on internal Qiskit implementation.

## M5 — AI Guidance

M5 owns:

- AI context preparation,
- prompt construction,
- explanation generation,
- guidance generation,
- learner-facing AI feedback.

M5 should receive structured, verified evidence.

## M6 — Visualization

M6 owns:

- quantum-result visualization,
- circuit/result presentation,
- visual learning components.

M6 should visualize verified output produced by M3 rather than independently calculating quantum results.

---

# M3 Quantum Engine Contract

M3 is a **general quantum foundation** with Grover as the first algorithm.

## Internal architecture

```text
backend/quantum/
│
├── schemas.py
│       ↓
├── validator.py
│       ↓
├── algorithms/
│   └── grover.py
│       ↓
├── execution.py
│       ↓
├── results.py
│       ↓
└── engine.py
```

### Conceptual flow

```text
QuantumExperiment
       ↓
Validation
       ↓
Algorithm Selection
       ↓
Circuit Construction
       ↓
Backend Execution
       ↓
Normalized SimulationResult
```

## QuantumExperiment

The experiment schema represents a quantum experiment without exposing Qiskit's internal objects.

Example:

```json
{
  "algorithm": "grover",
  "num_qubits": 2,
  "target_state": "01",
  "iterations": 1,
  "shots": 1024
}
```

## SimulationResult

The intended normalized result will provide a stable representation such as:

```json
{
  "algorithm": "grover",
  "target_state": "01",
  "shots": 1024,
  "counts": {
    "01": 1024
  },
  "probabilities": {
    "01": 1.0
  }
}
```

The exact result schema will be finalized as the quantum engine is completed.

## Qiskit abstraction

Other components should not need to know that the underlying implementation uses Qiskit Aer.

Conceptually:

```python
result = run_experiment(experiment)
```

rather than importing `qiskit_aer` inside unrelated components.

This keeps the quantum backend replaceable without forcing changes throughout the application.

---

# Integration Flow

```text
                 Learner
                    │
                    ▼
              ┌───────────┐
              │    M1     │
              │    UI     │
              └─────┬─────┘
                    │
                    ▼
              ┌───────────┐
              │    M4     │
              │    API    │
              └─────┬─────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
       M2          M3          M5
     Learner     Quantum        AI
      Model       Engine      Guidance
        │           │           │
        │           ▼           │
        │        Qiskit/Aer     │
        │                       │
        └───────────┬───────────┘
                    ▼
                   M6
              Visualization
```

### Example learning cycle

```text
1. Learner receives a Grover activity
2. Learner predicts the result
3. M4 sends the experiment request
4. M3 validates the experiment
5. M3 constructs and executes Grover
6. M3 returns normalized quantum evidence
7. M2 combines that evidence with learner history
8. M2 produces learner context
9. M5 uses the context to generate guidance
10. M1 displays the feedback
11. M6 visualizes the quantum evidence
12. Learner attempts the next activity
```

---

# Current MVP Design

The MVP uses a constrained Grover implementation to demonstrate the complete architecture.

### Quantum side

```text
Input
  ↓
Grover experiment
  ↓
Oracle
  ↓
Diffusion
  ↓
Measurement
  ↓
Counts / probabilities
```

### Learning side

```text
Prediction
  ↓
Execution
  ↓
Outcome
  ↓
Prediction vs outcome
  ↓
Learner evidence
  ↓
Adaptive feedback
```

The quantum engine should remain general enough that future algorithms can be added under:

```text
backend/quantum/algorithms/
```

without redesigning the core execution system unnecessarily.

---

# Future Scope

Potential extensions include:

- Additional quantum algorithms
- More advanced circuit experimentation
- Noisy simulation
- Hardware-backed execution
- Expanded learner diagnostics
- More sophisticated mastery models
- Richer learning content
- More advanced AI guidance
- Additional visualization modes
- Longitudinal learner analytics

These are future extensions rather than requirements for the initial MVP.

---

# Contributing

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
