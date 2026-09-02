# Q-BIT.140 — Failure Modes & Developer Debugging Guide

## 1. System Failure Taxonomy

```
+-----------------------------------------------------------------------------------+
| LAYER 1: CLIENT / UI FAILURES                                                     |
|  - Network disconnect to backend                                                  |
|  - Malformed DOM selection or NaN probability parsing                             |
+-----------------------------------------------------------------------------------+
| LAYER 2: API / REST GATEWAY FAILURES                                              |
|  - Schema validation failure (HTTP 422)                                           |
|  - Unregistered activity lookup (HTTP 404)                                        |
+-----------------------------------------------------------------------------------+
| LAYER 3: QUANTUM SIMULATION FAILURES                                              |
|  - AerSimulator crash / invalid quantum parameters (HTTP 500)                     |
|  - Qubit count mismatch / unknown algorithm                                       |
+-----------------------------------------------------------------------------------+
| LAYER 4: PERSISTENCE FAILURES                                                     |
|  - Disk permission error / Supabase network timeout (HTTP 503)                    |
|  - State file JSON corruption                                                     |
+-----------------------------------------------------------------------------------+
| LAYER 5: AI GUIDANCE FAILURES                                                     |
|  - Groq API rate limit / invalid API key                                          |
|  - Transparent fallback to MockLLMProvider (HTTP 200)                             |
+-----------------------------------------------------------------------------------+
```

---

## 2. Component-by-Component Failure Scenarios & Debugging Procedures

### Scenario 1: Invalid Quantum Experiment Submission
- **What Can Fail**: User submits an activity with invalid quantum parameters or an unsupported algorithm name.
- **Detection**: `backend/quantum/validator.py:validate_experiment()` raises `ValueError`.
- **Handling**: `backend/api/routes/activities.py` catches the exception and returns HTTP 500 with message `"Quantum execution engine failed: <error>"`.
- **User Visibility**: UI displays an error toast banner: *"Quantum execution engine failed"*.
- **Developer Debugging**:
  1. Inspect `activity.quantum_experiment` definition in `backend/adaptive/activities.py`.
  2. Verify that `algorithm` is listed in `backend/quantum/registry.py:ALGORITHM_REGISTRY`.
  3. Verify that `num_qubits == len(target_state)`.

### Scenario 2: Persistence Storage Unavailable (Disk or Supabase)
- **What Can Fail**: Disk writes fail due to read-only permissions, or Supabase connection times out.
- **Detection**: `JSONFileLearnerRepository` or `SupabaseLearnerRepository` catches `IOError`/`HTTPError` and raises `PersistenceError` or `StorageUnavailableError`.
- **Handling**: `backend/api/routes/activities.py` catches `PersistenceError` and returns HTTP 503 Service Unavailable.
- **User Visibility**: Yellow warning toast: *"State persistence service is currently unavailable"*.
- **Developer Debugging**:
  1. Check `.env` setting `STORAGE_BACKEND`.
  2. If using `json_file`, check write permissions on `data/learners/`.
  3. If using `supabase`, check `SUPABASE_URL` and `SUPABASE_KEY` credentials.

### Scenario 3: AI Provider Rate Limiting or Network Outage
- **What Can Fail**: Groq Cloud API returns HTTP 429 (Rate Limit) or network is offline.
- **Detection**: `GroqLLMProvider.generate()` throws an exception.
- **Handling**: `backend/ai/providers.py:get_default_provider()` automatically catches initialization errors and falls back to `MockLLMProvider`.
- **User Visibility**: Transparent. The user receives a high-quality, deterministic explanation generated offline with KaTeX formatting.
- **Developer Debugging**:
  1. Verify `GROQ_API_KEY` in environment.
  2. Inspect backend logs for warning: `"Failed to initialize GroqLLMProvider; falling back to MockLLMProvider"`.
