# Q-BIT.140 — Database, Authentication & Security Audit

## 1. Persistence Layer Architecture

Q-BIT.140 employs an abstract Repository Pattern (`backend/adaptive/repository.py`) to manage learner state persistence across three swappable backends:

```
                  +--------------------------------+
                  |  LearnerRepository (ABC)       |
                  |  - get(user_id) -> State       |
                  |  - save(state: State) -> None  |
                  |  - exists(user_id) -> bool     |
                  +--------------------------------+
                                  |
         +------------------------+------------------------+
         |                        |                        |
         v                        v                        v
+------------------+    +-------------------+    +--------------------+
| InMemoryRepo     |    | JSONFileRepo      |    | SupabaseRepo       |
| - Fast testing   |    | - Local dev disk  |    | - PostgreSQL Cloud |
| - Dict storage   |    | - Atomic writes   |    | - RLS & JSONB      |
+------------------+    +-------------------+    +--------------------+
```

### Persistence Configurations:
1. **`InMemoryLearnerRepository`**: Thread-safe in-memory dictionary. Zero external dependencies. Ideal for fast unit testing and ephemeral demos.
2. **`JSONFileLearnerRepository`**: Persists each learner's `LearnerState` as a structured JSON file under a configured directory (e.g. `data/learners/<user_id>.json`).
3. **`SupabaseLearnerRepository`**: Connects to Supabase PostgreSQL using REST API. Persists to the `learner_states` table.

---

## 2. Database Schema Specification (Supabase / PostgreSQL)

```sql
-- Production Supabase Schema Definition
CREATE TABLE IF NOT EXISTS public.learner_states (
    user_id TEXT PRIMARY KEY,
    concept_scores JSONB NOT NULL DEFAULT '{}'::jsonb,
    attempts JSONB NOT NULL DEFAULT '{}'::jsonb,
    errors JSONB NOT NULL DEFAULT '{}'::jsonb,
    score_history JSONB NOT NULL DEFAULT '{}'::jsonb,
    evidence_history JSONB NOT NULL DEFAULT '[]'::jsonb,
    gap_inferences JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Row Level Security (RLS) Policy
ALTER TABLE public.learner_states ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Learners can view and modify only their own state"
ON public.learner_states
FOR ALL
USING (auth.uid()::text = user_id)
WITH CHECK (auth.uid()::text = user_id);
```

---

## 3. Security, Authentication & Threat Modeling

### 1. Authentication & Session Isolation
- **Current MVP Implementation**: MVP uses explicit `learner_id` passing via HTTP request headers/body (e.g. `learner_id: "mvp_evaluator_001"`).
- **Session Isolation**: Every repository lookup is strictly scoped by `learner_id`. State mutations for user $A$ cannot affect user $B$.
- **Production Roadmap**: Full JWT token verification via Supabase Auth middleware.

### 2. Secrets Management & Environment Isolation
- **No Hardcoded Secrets**: Zero API keys, database credentials, or passwords exist in the source code.
- **Environment Variables**: Managed via `.env` file and parsed with `python-dotenv`:
  - `GROQ_API_KEY`: Cloud LLM completion key (optional; system falls back to `MockLLMProvider` if absent).
  - `STORAGE_BACKEND`: Configures repository backend (`in_memory`, `json_file`, `supabase`).
  - `SUPABASE_URL`, `SUPABASE_KEY`: Supabase connection credentials.

### 3. Input Validation & Injection Defenses
- **Pydantic Schema Gate**: All incoming JSON payloads pass through strict Pydantic schemas. Unrecognized fields are rejected or sanitized.
- **Type Coercion & Stripping**: `response` strings are trimmed and validated before execution.
- **No SQL Injection**: Database interactions utilize parameterized Supabase client queries or file-based key lookups. No raw SQL string concatenation exists in the codebase.
- **No Remote Code Execution (RCE)**: Qiskit circuits are constructed using rigid, pre-defined parametric builder functions (`build_grover_circuit`), never through `eval()`, `exec()`, or dynamic string execution.

---

## 4. Failure Handling & Persistence Hardening

| Failure Mode | Detection | Handling Strategy | User Experience |
|---|---|---|---|
| **Disk Write Permission Denied** | `OSError` / `PermissionError` in `JSONFileRepo` | Wrapped in `PersistenceError`, caught in M4 route | Returns HTTP 503 Service Unavailable |
| **Supabase Network Timeout** | `httpx.TimeoutException` or connection error | Wrapped in `StorageUnavailableError` | Returns HTTP 503 with helpful message |
| **State File Corrupted** | `json.JSONDecodeError` on read | Catches error; raises `PersistenceError` without overwriting | Prevents corrupting or resetting historical records |
