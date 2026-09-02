# Q-BIT.140 — Theory-to-Code Mathematical Mapping

This document maps theoretical principles in Quantum Mechanics, Adaptive Cognitive Modeling, and AI Grounding directly to concrete Python source code symbols, file paths, and function implementations.

---

## 1. Quantum Computing Theory $\leftrightarrow$ Code Map

| Theoretical Concept | Mathematical Formulation | Code Implementation Symbol | File Path & Function | Implementation Status | System Meaning & Impact |
|---|---|---|---|---|---|
| **Qubit & State Vector** | $|\psi\rangle = \alpha|0\rangle + \beta|1\rangle, \; \|\alpha\|^2 + \|\beta\|^2 = 1$ | `QuantumCircuit(num_qubits, num_qubits)` | `backend/quantum/algorithms/grover.py:build_grover_circuit` | **IMPLEMENTED** | Allocates 2 physical qubits in ground state $|00\rangle$. |
| **Hadamard Gate (Superposition)** | $H = \frac{1}{\sqrt{2}}\begin{bmatrix} 1 & 1 \\ 1 & -1 \end{bmatrix}$ | `circuit.h(qubit)` | `backend/quantum/algorithms/grover.py:_apply_diffusion` | **IMPLEMENTED** | Creates uniform superposition $|s\rangle = \frac{1}{2}\sum_{x}|x\rangle$. |
| **Pauli-X Gate (Bit-Flip)** | $X = \begin{bmatrix} 0 & 1 \\ 1 & 0 \end{bmatrix}$ | `circuit.x(qubit)` | `backend/quantum/algorithms/grover.py:_apply_oracle` | **IMPLEMENTED** | Flips basis bits ($0 \leftrightarrow 1$) to target arbitrary search states. |
| **Controlled-Z (Phase Tagging)** | $CZ = \text{diag}(1, 1, 1, -1)$ | `circuit.cz(0, 1)` | `backend/quantum/algorithms/grover.py:_apply_multi_controlled_z` | **IMPLEMENTED** | Inverts the quantum phase of the marked state ($|w\rangle \mapsto -|w\rangle$). |
| **Grover Diffusion Operator** | $D = 2|s\rangle\langle s| - I$ | `_apply_diffusion(circuit, 2)` | `backend/quantum/algorithms/grover.py:_apply_diffusion` | **IMPLEMENTED** | Performs inversion of all amplitudes about the mean amplitude $\mu$. |
| **Computational Measurement** | Projector $M_x = |x\rangle\langle x|$ | `circuit.measure(range(2), range(2))` | `backend/quantum/algorithms/grover.py:build_grover_circuit` | **IMPLEMENTED** | Collapses state vector into discrete classical bit outcomes. |
| **Born's Rule & Empirical Sampling** | $P(x) = |\alpha_x|^2$ | `probabilities = count / shots` | `backend/quantum/results.py:SimulationResult.probabilities` | **IMPLEMENTED** | Converts counts from 1024 AerSimulator shots into empirical probability distribution. |
| **Physical Quantum Hardware (QPU)** | Cloud QPU Sampler Execution | IBM Quantum Cloud Connectors | N/A | **FUTURE SCOPE / NOT IN MVP** | MVP uses local Qiskit AerSimulator for deterministic, free, fast simulation. |

---

## 2. Adaptive Learning Theory $\leftrightarrow$ Code Map

| Theoretical Concept | Mathematical Formulation | Code Implementation Symbol | File Path & Function | Implementation Status | System Meaning & Impact |
|---|---|---|---|---|---|
| **Deterministic Linear Mastery** | $\text{clamp}_{[0, 1]}(\text{diag} + \text{improv} - \text{penalty})$ | `compute_mastery()` | `backend/adaptive/engine.py:LearnerModel.compute_mastery` | **IMPLEMENTED** | Computes transparent, deterministic mastery score updated with each attempt. |
| **Improvement Bonus** | $\max(0.0, S_{\text{latest}} - S_{\text{prior}}) \times 0.2$ | `improvement = max(0.0, history[-1] - history[-2]) * 0.2` | `backend/adaptive/engine.py:LearnerModel.compute_mastery` | **IMPLEMENTED** | Rewards positive score trajectory between consecutive attempts (up to $+0.20$). |
| **Error Penalty Cap** | $\min(\text{err\_count} \times 0.05, 0.30)$ | `error_penalty = min(error_count * 0.05, 0.3)` | `backend/adaptive/engine.py:LearnerModel.compute_mastery` | **IMPLEMENTED** | Deducts $0.05$ per error, capped at $0.30$. |
| **Bayesian Knowledge Tracing (BKT)** | Hidden Markov Model with Slip/Guess | N/A | N/A | **THEORY ONLY / NOT IN MVP** | MVP uses deterministic linear heuristic rather than stochastic BKT. |
| **Prerequisite Bottleneck Inference** | Multi-Priority DAG Traversal | `find_unmastered_prerequisite()` | `backend/adaptive/engine.py:find_unmastered_prerequisite` | **IMPLEMENTED** | Detects active errors on prerequisites (Priority 1) or mastery $< 0.6$ (Priority 2). |
| **Evidence Sufficiency Semantics** | Threshold Classification | `evidence_sufficiency: str` | `backend/adaptive/evidence.py:evaluate_quantum_prediction` | **IMPLEMENTED** | Classifies attempt as `insufficient` (1 error) vs `sufficient` ($\ge 2$ errors). |

---

## 3. Grounded AI Theory $\leftrightarrow$ Code Map

| Theoretical Concept | Mathematical / System Principle | Code Implementation Symbol | File Path & Function | Implementation Status | System Meaning & Impact |
|---|---|---|---|---|---|
| **Context Injection (RAG)** | $P(\text{Text} \mid \text{Prompt}, \text{Evidence})$ | `retrieve_context()` | `backend/ai/retrieval.py:retrieve_context` | **IMPLEMENTED** | Injects verified Qiskit counts and curriculum Markdown into the LLM context. |
| **Read-Only AI Boundary** | Deterministic Authority Isolation | Architecture Isolation | `backend/ai/service.py:explain_experiment` | **IMPLEMENTED** | LLM is strictly an explanation layer; cannot alter learner state or simulation. |
| **Offline Deterministic Fallback** | Structured Marker Parsing | `MockLLMProvider.generate()` | `backend/ai/providers.py:MockLLMProvider` | **IMPLEMENTED** | Provides 100% offline, predictable explanations formatted in KaTeX. |
