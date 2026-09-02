# Q-BIT.140 — Documentation & Implementation Conflict Audit

This audit explicitly records all contradictions, stale references, and discrepancies between project documentation, comments, and actual source code.

---

## Conflict Reconciliation Table

| Conflict ID | Stale / Discrepant Claim | Affected Document(s) | Actual Implementation Source | Resolution & Correct Fact |
|---|---|---|---|---|
| **CONF-01** | *Mastery uses Bayesian Knowledge Tracing (BKT) with $\lambda = 0.85$* | Early forensic drafts, stale design notes | `backend/adaptive/engine.py:48-64`, `tests/adaptive/test_mastery.py` | **CORRECTED**: The code implements a transparent linear heuristic: $\text{clamp}_{[0, 1]}(\text{diag\_score} + \text{improvement\_bonus} - \text{error\_penalty})$. There is zero Bayesian/BKT math or $\lambda = 0.85$ decay. |
| **CONF-02** | *Stale Activity IDs (`act_diag_qubit`, `act_diag_superposition`, `act_diag_grover_eval`)* | Early forensic drafts | `backend/adaptive/activities.py:MVP_ACTIVITIES` | **CORRECTED**: Real activity IDs are `act_grover_2q_predict`, `act_measurement_prob_diagnostic`, `act_superposition_remediation`, and `act_grover_iteration_reasoning`. |
| **CONF-03** | *Mock LLM described as "9-tier intent engine"* | Early forensic drafts | `backend/ai/providers.py:MockLLMProvider` | **CORRECTED**: Real implementation uses structured prompt marker parsing routing between quantum execution explanations, conceptual diagnostics, and general Q&A. |
| **CONF-04** | *Frontend Stack claimed as React / Next.js* | Early planning notes | `frontend/index.html`, `frontend/js/adapter.js`, `frontend/css/styles.css` | **CORRECTED**: The actual implementation is pure **Vanilla HTML5, ES6 Modules, and CSS3** (zero npm/Webpack build step). |
| **CONF-05** | *Quantum Execution described as "Physical Hardware / QPU"* | Presentation drafts | `backend/quantum/execution.py` | **CORRECTED**: Execution runs on local `qiskit_aer.AerSimulator()` with 1024 shots. Hardware QPU execution is future scope. |
| **CONF-06** | *AI Tutor described as "Zero Hallucination Guarantee"* | Presentation drafts | `backend/ai/service.py`, `backend/ai/prompts.py` | **CORRECTED**: Wording replaced with technically defensible description: "Grounded AI with explicit evidence boundaries (LLM has zero authority over learner state or simulation counts)." |
| **CONF-07** | *Automated Test Count reported as 295* | Historical `README.md` at `3d65210` | `pytest -q` execution output | **CORRECTED**: Test suite contains exactly **305 tests** (all passing in 2.77s). |
| **CONF-08** | *Supabase claimed as mandatory runtime requirement* | Stale setup docs | `backend/adaptive/repository.py:get_learner_repository` | **CORRECTED**: Supabase is fully optional. System defaults seamlessly to in-memory or local JSON-file storage. |
