# Q-BIT.140 — M5 Grounded AI Guidance Deep Dive

## 1. Architectural Philosophy: Grounded AI with Explicit Evidence Boundaries

The M5 Grounded AI Guidance layer (`backend/ai/`) provides explanatory pedagogical tutoring while enforcing an **explicit operational boundary** between generative text synthesis and authoritative system facts.

```mermaid
graph TD
    subgraph "External World / User"
        Q[Student Inquiry / Prediction]
    end

    subgraph "M5 Grounded Pipeline"
        EV[Verified M3 Aer Counts & M2 Decision]
        RAG[In-Tree Knowledge Retrieval (12 Markdown Docs)]
        PROMPT[Grounding Prompt Assembly (prompts.py)]
        LLM[LLM Provider: Groq / MockLLM]
        OUT[KaTeX Formatted Explanation]
        
        Q --> PROMPT
        EV --> PROMPT
        RAG --> PROMPT
        PROMPT --> LLM
        LLM --> OUT
    end

    subgraph "Forbidden Actions (Hard Blocked by Architecture)"
        F1["Modifying Learner State / Mastery"]
        F2["Selecting Next Curriculum Activity"]
        F3["Fabricating Simulation Counts / Gates"]
    end

    OUT -.-> F1
    OUT -.-> F2
    OUT -.-> F3
```

---

## 2. Strict Boundary Matrix: What the LLM Is and Is NOT Allowed to Do

| System Capability | Allowed for LLM? | Enforcement Mechanism | Verification Test |
|---|---|---|---|
| **Fabricating Quantum Counts** | ❌ **FORBIDDEN** | The prompt strictly injects verified counts from `verified_result.counts`. The LLM has no simulation engine. | `tests/ai/test_m5_grounded_guidance.py` |
| **Deciding Learner Mastery** | ❌ **FORBIDDEN** | M2 calculates mastery deterministically in Python. The LLM output is never parsed or fed back to M2. | `tests/ai/test_m5_grounded_guidance.py` |
| **Selecting Next Activity** | ❌ **FORBIDDEN** | M2 selects `AdaptiveRecommendation.target`. The LLM only receives this decision as read-only context to explain it. | `tests/ai/test_m5_grounded_guidance.py` |
| **Inventing Learner History** | ❌ **FORBIDDEN** | Past attempt counts are passed as static integers from M2's `evidence_history`. | `tests/adaptive/test_pass4_evidence_trace.py` |
| **Explaining Dirac Notation & Math** | ✅ **ALLOWED** | Uses retrieved concepts from `backend/ai/knowledge/` to format LaTeX formulas ($|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$). | `tests/ai/test_service.py` |
| **Explaining Prediction Mismatches** | ✅ **ALLOWED** | Compares `learner_response` against `verified_result.most_likely_state` and explains quantum mechanics reasons. | `tests/ai/test_service.py` |
| **Explaining "Why This Next?"** | ✅ **ALLOWED** | Translates M2's `adaptive_decision.reason` and `trigger` into student-friendly pedagogical guidance. | `tests/api/test_pass5_why_this_next_ux.py` |

---

## 3. In-Tree Knowledge Base Architecture

M5 is grounded in 12 verified, authoritative markdown files stored in `backend/ai/knowledge/`:

| File | Topic & Scope | Key Mathematical & Quantum Principles Included |
|---|---|---|
| `00_purpose_and_scope.md` | System Scope | Explains M1-M6 boundaries and pedagogical role of Q-BIT.140 |
| `01_math_linear_algebra.md` | Linear Algebra | Inner products $\langle\phi|\psi\rangle$, unitary operators ($U^\dagger U = I$), orthonormal bases |
| `02_math_probability.md` | Probability | Discrete distributions, normalization condition $\sum P(x) = 1$, expectation values |
| `03_quantum_foundations.md` | Quantum Foundations | Qubit definition, state vector $|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$, normalization $|\alpha|^2 + |\beta|^2 = 1$ |
| `04_quantum_gates.md` | Single-Qubit Gates | Pauli matrices ($X, Y, Z$), Hadamard gate ($H$), phase properties ($Z|1\rangle = -|1\rangle$) |
| `05_multi_qubit_entanglement.md` | Multi-Qubit Systems | Tensor products $|\psi\rangle \otimes |\phi\rangle$, Bell states, entanglement, 2-qubit computational basis |
| `06_quantum_circuits.md` | Circuit Synthesis | Wires, gate sequencing, control-target dynamics, measurement operators |
| `07_grovers_algorithm.md` | Grover Search | Oracle phase tagging ($(-1)^{f(x)}$), diffusion operator ($2|s\rangle\langle s| - I$), $\mathcal{O}(\sqrt{N})$ complexity |
| `08_qiskit_practical.md` | Qiskit Execution | `QuantumCircuit`, `AerSimulator`, shot statistics, little-endian bitstring indexing |
| `09_common_misconceptions.md` | Student Pitfalls | Bit vs qubit, superposition vs classical probability, phase flip vs bit flip |
| `10_ai_guidance_rules.md` | AI Grounding Rules | Operational constraints: cite exact counts, never contradict M2, explain mismatch calmly |
| `11_concept_ids.md` | Concept Taxonomy | Canonical mappings linking curriculum DAG IDs (`quantum.qubit`) to M5 topics |

---

## 4. Provider Implementations & Offline Fallback

M5 implements two provider backends under `LLMProvider` (`backend/ai/providers.py`):

1. **`GroqLLMProvider` (Production Cloud)**:
   - Uses `groq.Groq` client calling OpenAI-compatible completions API (e.g. `openai/gpt-oss-120b`).
   - Enabled when `GROQ_API_KEY` is present in environment variables.
2. **`MockLLMProvider` (Deterministic Offline Engine)**:
   - 100% offline, zero-network-dependency provider.
   - Extracts structured prompt markers (`Evidence Type:`, `- Concept ID:`, `- Activity ID:`, `- Evidence ID:`, `- Learner Response:`, `- Evaluation Outcome:`, `- Theoretical Target State:`, `- Empirical Most-Likely Measured State:`, `- Action:`, `- Target Activity:`, `- Pedagogical Rationale:`).
   - Routes to two evidence-grounded generators:
     1. `_generate_quantum_execution_explanation`: Explains physical simulation counts, target states, and amplitude amplification.
     2. `_generate_conceptual_explanation`: Explains conceptual multiple-choice diagnostic options, Born's rule, or Grover iteration reasoning.
   - For free-form inquiries without structured evidence, routes to `_generate_qa_explanation` using curriculum keyword matching.
   - Outputs formatted Markdown with native KaTeX LaTeX equations.
