# Q-BIT.140 — Theory-to-Code Mathematical Mapping

This document maps theoretical principles in Quantum Mechanics, Bayesian Knowledge Modeling, and AI Grounding directly to concrete Python source code symbols, file paths, and function implementations.

---

## 1. Quantum Computing Theory $\leftrightarrow$ Code Map

| Theoretical Concept | Mathematical Formulation | Code Implementation Symbol | File Path & Function | System Meaning & Impact | Output Meaning |
|---|---|---|---|---|---|
| **Qubit & State Vector** | $|\psi\rangle = \alpha|0\rangle + \beta|1\rangle, \; \|\alpha\|^2 + \|\beta\|^2 = 1$ | `QuantumCircuit(num_qubits, num_qubits)` | `backend/quantum/algorithms/grover.py:build_grover_circuit` | Allocates 2 physical qubits in ground state $|00\rangle$. | Circuit initialized to ground state. |
| **Hadamard Gate (Superposition)** | $H = \frac{1}{\sqrt{2}}\begin{bmatrix} 1 & 1 \\ 1 & -1 \end{bmatrix}$ | `circuit.h(qubit)` | `backend/quantum/algorithms/grover.py:_apply_diffusion` | Creates uniform superposition $|s\rangle = \frac{1}{2}\sum_{x}|x\rangle$. | All basis states acquire equal amplitude $0.5$. |
| **Pauli-X Gate (Bit-Flip)** | $X = \begin{bmatrix} 0 & 1 \\ 1 & 0 \end{bmatrix}$ | `circuit.x(qubit)` | `backend/quantum/algorithms/grover.py:_apply_oracle` | Flips computational basis bits ($0 \leftrightarrow 1$) to target arbitrary search states. | Relocates target state to $|11\rangle$ for CZ operation. |
| **Controlled-Z (Phase Tagging)** | $CZ = \text{diag}(1, 1, 1, -1)$ | `circuit.cz(0, 1)` | `backend/quantum/algorithms/grover.py:_apply_multi_controlled_z` | Inverts the quantum phase of the marked state ($|w\rangle \mapsto -|w\rangle$). | Phase of target state inverted by $\pi$. |
| **Grover Diffusion Operator** | $D = 2|s\rangle\langle s| - I$ | `_apply_diffusion(circuit, 2)` | `backend/quantum/algorithms/grover.py:_apply_diffusion` | Performs geometric reflection (inversion) of all amplitudes about the mean amplitude $\mu$. | Amplifies marked state amplitude to $1.0$. |
| **Computational Measurement** | Projector $M_x = |x\rangle\langle x|$ | `circuit.measure(range(2), range(2))` | `backend/quantum/algorithms/grover.py:build_grover_circuit` | Collapses continuous state vector into discrete classical bit outcomes. | Registers classical bit measurement. |
| **Born's Rule & Probability** | $P(x) = |\alpha_x|^2$ | `probabilities = count / shots` | `backend/quantum/results.py:SimulationResult.probabilities` | Converts physical measurement counts from 1024 shots into empirical probability distribution. | Normalized percentage distribution ($93.8\%$). |
| **Finite-Shot Variance** | $\sigma = \sqrt{\frac{p(1-p)}{N_{\text{shots}}}}$ | `shots: int = 1024` | `backend/quantum/schemas.py:QuantumExperiment` | Finite sample statistics introduce empirical variance ($\sigma \approx 1.5\%$). | Slight fluctuations in empirical shot counts. |

---

## 2. Adaptive Learning Theory $\leftrightarrow$ Code Map

| Theoretical Concept | Mathematical Formulation | Code Implementation Symbol | File Path & Function | System Meaning & Impact | Output Meaning |
|---|---|---|---|---|---|
| **Bayesian Mastery Estimation** | $M(c) = \frac{1 + \sum w_i S_i}{2 + \sum w_i}$ | `compute_mastery()` | `backend/adaptive/engine.py:LearnerModel.compute_mastery` | Computes calibrated concept mastery probability updated with each attempt. | Score between $0.0$ and $1.0$. |
| **Recency Decay Weighting** | $w_i = \lambda^{k-1-i}, \; \lambda = 0.85$ | `decay_weight = 0.85 ** (len(history) - 1 - i)` | `backend/adaptive/engine.py:LearnerModel.compute_mastery` | Gives exponentially higher weight to recent attempts over historical attempts. | Faster recovery when a student learns from errors. |
| **Prerequisite Mastery Gating** | $M_{\text{gated}}(c) = \min(M(c), \min_{p} M(p))$ | `find_unmastered_prerequisite()` | `backend/adaptive/engine.py:LearnerModel.find_unmastered_prerequisite` | Prevents concept mastery from advancing if foundational prerequisites are broken. | Mastery is throttled until prerequisites are resolved. |
| **Evidence Sufficiency Classification** | 4-Tier Threshold Semantics | `evidence_sufficiency: str` | `backend/adaptive/evidence.py:evaluate_quantum_prediction` | Prevents premature interventions on single errors (`insufficient` vs `sufficient`). | Tag: `insufficient` or `sufficient_for_targeted_inference`. |
| **Deterministic DAG Routing** | $f(\text{Evidence}, \text{History}) \rightarrow \text{Action}$ | `record_evidence()` | `backend/adaptive/engine.py:LearnerModel.record_evidence` | Selects pedagogical action (`advance`, `gather_evidence`, `targeted_remediation`). | Deterministic recommendation. |

---

## 3. Grounded AI Theory $\leftrightarrow$ Code Map

| Theoretical Concept | Mathematical / System Principle | Code Implementation Symbol | File Path & Function | System Meaning & Impact | Output Meaning |
|---|---|---|---|---|---|
| **Context Injection (RAG)** | $P(\text{Text} \mid \text{Prompt}, \text{Evidence})$ | `retrieve_context()` | `backend/ai/retrieval.py:retrieve_context` | Injects verified Qiskit counts and curriculum Markdown into the LLM context. | Grounded prompt. |
| **Zero-Hallucination Guardrail** | Hard Architectural Boundary | `SYSTEM_PROMPT` | `backend/ai/prompts.py:SYSTEM_PROMPT` | Explicitly instructs model to cite verified counts and never invent simulation data. | Factual, auditable guidance. |
| **Deterministic Intent Matching** | Pattern-Based Fallback Synthesis | `MockLLMProvider.generate()` | `backend/ai/providers.py:MockLLMProvider.generate` | Provides 100% offline, predictable explanations formatted in KaTeX. | LaTeX formatted tutorial text. |
