# Q-BIT.140 — Technical Judge Examination Q&A Database

This document provides concise, technically rigorous, code-grounded answers to realistic questions asked by SIH technical judges.

---

## Category 1: Problem & Architectural Motivation

### Q1.1: What exact problem does Q-BIT.140 solve that generic AI tutors (e.g. ChatGPT) cannot?
- **Short Answer**: It eliminates pedagogical and physical hallucinations by decoupling deterministic cognitive modeling (M2) and real Qiskit quantum execution (M3) from generative text synthesis (M5).
- **Detailed Answer**: Generic LLMs hallucinate quantum simulation outcomes (e.g. claiming a circuit produced $|11\rangle$ when physics dictates $|10\rangle$) and arbitrarily jump between curriculum topics. Q-BIT.140 uses real Qiskit Aer simulation for physical ground truth and a deterministic Bayesian DAG for student mastery. The LLM is restricted to an explanation-only role.
- **Code Evidence**: `backend/quantum/execution.py:execute_circuit` (Real Aer simulator), `backend/adaptive/engine.py:LearnerModel` (Deterministic DAG).

---

## Category 2: Quantum Engine & Grover's Algorithm

### Q2.1: Is your quantum execution simulated or running on real hardware? Why?
- **Short Answer**: It runs on a local `qiskit_aer.AerSimulator()` executing 1024 shots.
- **Detailed Answer**: For an educational MVP, AerSimulator provides deterministic, zero-latency, zero-cost execution with full support for finite-shot statistical sampling. The M3 interface (`run_experiment()`) is fully decoupled; swapping `AerSimulator` for IBM Quantum's cloud `SamplerV2` requires changing only one file (`backend/quantum/execution.py`).
- **Code Evidence**: `backend/quantum/execution.py:execute_circuit`.

### Q2.2: Walk through the exact gates applied for a 2-qubit Grover search targeting $|10\rangle$.
- **Short Answer**: $H^{\otimes 2} \rightarrow X(q_0) \rightarrow CZ(q_0, q_1) \rightarrow X(q_0) \rightarrow H^{\otimes 2} \rightarrow X^{\otimes 2} \rightarrow CZ(q_0, q_1) \rightarrow X^{\otimes 2} \rightarrow H^{\otimes 2} \rightarrow \text{Measure}$.
- **Detailed Answer**:
  1. $H^{\otimes 2}$ creates uniform superposition $|s\rangle = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.
  2. Oracle $X(q_0) \rightarrow CZ \rightarrow X(q_0)$ flips the phase of $|10\rangle \mapsto -|10\rangle$.
  3. Diffusion $H^{\otimes 2} \rightarrow X^{\otimes 2} \rightarrow CZ \rightarrow X^{\otimes 2} \rightarrow H^{\otimes 2}$ performs inversion about the mean, boosting amplitude of $|10\rangle$ to $1.0$.
  4. Measurement yields outcome $10$ with theoretical $100\%$ probability.
- **Code Evidence**: `backend/quantum/algorithms/grover.py:build_grover_circuit`.

---

## Category 3: Adaptive Learner Model (M2)

### Q3.1: How do you prevent a single accidental click from triggering unnecessary remediation?
- **Short Answer**: Through **Evidence Sufficiency Semantics**. A single error is classified as `insufficient`, triggering `gather_evidence` on the same activity rather than immediate remediation.
- **Detailed Answer**: M2 enforces a 2-error threshold before diagnosing a persistent misconception. If `recent_errors == 1`, M2 emits `AdaptiveRecommendation(action="gather_evidence", trigger="single_prediction_mismatch", evidence_sufficiency="insufficient")`. Only when $\ge 2$ errors occur does M2 escalate to `targeted_remediation`.
- **Code Evidence**: `backend/adaptive/engine.py:360-372`.

### Q3.2: How is learner mastery calculated? Is it machine learning?
- **Short Answer**: It is a deterministic Bayesian recency-weighted formula, not a black-box neural network.
- **Detailed Answer**: Mastery is calculated as $\text{Mastery}(c) = \frac{1.0 + \sum w_i S_i}{2.0 + \sum w_i}$ with recency decay $w_i = 0.85^{k-1-i}$. It is further gated by the minimum mastery of foundational prerequisites: $\text{Mastery}_{\text{gated}}(c) = \min(\text{Mastery}(c), \min_p \text{Mastery}(p))$.
- **Code Evidence**: `backend/adaptive/engine.py:compute_mastery`.

---

## Category 4: AI Guidance & Grounding (M5)

### Q4.1: Can your AI tutor change a student's score or assign a different activity?
- **Short Answer**: **No. It is architecturally impossible.**
- **Detailed Answer**: The LLM service in M5 only has read access to the verified simulation results and M2's decision. Its text output is returned directly to the browser client and is never parsed or fed back into M2, M3, or the database.
- **Code Evidence**: `backend/ai/service.py:explain_experiment`, `tests/ai/test_m5_grounded_guidance.py`.

### Q4.2: What happens if the Groq API goes down or you lose internet access during the hackathon presentation?
- **Short Answer**: The system automatically and transparently falls back to `MockLLMProvider`, which runs 100% locally and offline.
- **Detailed Answer**: `get_default_provider()` catches API initialization errors and initializes `MockLLMProvider`. This offline provider uses a 9-tier deterministic intent matcher to generate complete KaTeX-formatted quantum explanations without sending a single network packet.
- **Code Evidence**: `backend/ai/providers.py:MockLLMProvider`, `get_default_provider`.

---

## Category 5: Frontend & Visualization (M1 / M6)

### Q5.1: What is the "State Triad" in your UI?
- **Short Answer**: It is the explicit visual separation of **Learner Prediction** ($|01\rangle$) $\neq$ **Theoretical Target** ($|10\rangle$) $\neq$ **Physical Simulation Result** ($|10\rangle$ at $93.8\%$).
- **Detailed Answer**: Novice students frequently confuse what they guessed with what the algorithm was designed to find, or confuse theoretical target states with empirical measurement distributions. The State Triad renders three distinct cards with color-coded badges to build clear conceptual separation.
- **Code Evidence**: `frontend/index.html` lines 250–310, `frontend/js/adapter.js:normalizeSubmissionResponse`.
