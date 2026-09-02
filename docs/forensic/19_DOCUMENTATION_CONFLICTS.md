# Q-BIT.140 — Documentation & Implementation Conflict Audit

This audit explicitly records all contradictions, stale references, and discrepancies between project documentation, comments, and actual source code.

---

## Conflict Log

### Conflict 1: Frontend Framework Stack Mismatch
- **Stale Documentation Claim**: Certain early design notes and planning files referenced building a React or Next.js frontend.
- **Actual Source of Truth**: The actual frontend is implemented in **Vanilla HTML5, ES6 Modules, and CSS3** (`frontend/index.html`, `frontend/js/adapter.js`, `frontend/css/styles.css`).
- **Resolution / Status**: The vanilla implementation is superior for the MVP as it requires zero build steps (no `npm run build`), loads instantaneously, and has zero dependency vulnerabilities.

### Conflict 2: Automated Test Count Evolution
- **Stale Documentation Claim**: `README.md` at commit `3d65210` reported 295 automated tests.
- **Actual Source of Truth**: Running `python -m pytest` executes **305 tests** (all passing in 4.92s).
- **Resolution / Status**: The 10 additional tests were added in `tests/ai/test_m5_grounded_guidance.py` and `tests/api/` during final M5 boundary hardening.

### Conflict 3: Multi-Qubit Scalability vs MVP Scope
- **Stale Documentation Claim**: General claims about arbitrary $N$-qubit Grover execution.
- **Actual Source of Truth**: While `backend/quantum/algorithms/grover.py` contains helper logic for $n > 2$, the activity catalog (`backend/adaptive/activities.py:MVP_ACTIVITIES`) and UI are strictly tuned for 2-qubit search ($N = 4$).
- **Resolution / Status**: Frame this accurately during judging as an intentional pedagogical decision: 2-qubit Grover allows complete step-by-step visualization in a single iteration without overwhelming the student.

### Conflict 4: Cloud Persistence vs Local Default
- **Stale Documentation Claim**: Descriptions claiming Supabase is required for running the platform.
- **Actual Source of Truth**: Supabase is fully optional. If unconfigured, `backend/adaptive/repository.py` automatically defaults to `InMemoryLearnerRepository` or `JSONFileLearnerRepository`, running 100% locally with zero external accounts.
- **Resolution / Status**: Highlight this as a major reliability feature for hackathon evaluation.
