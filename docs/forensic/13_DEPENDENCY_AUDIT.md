# Q-BIT.140 — Dependency & Technology Audit

## 1. Backend Python Dependencies

| Package | Minimum Version in Manifest | Installed Version | Architectural Location | Why Used / Functionality Provided | Replacement Feasibility | Security / Reliability Notes |
|---|---|---|---|---|---|---|
| **`fastapi`** | `>=0.110.0` | `0.141.1` | M4 REST Gateway | High-performance asynchronous REST API routing, request validation, OpenAPI auto-generation. | Moderate (Could use Starlette/Flask, but would lose native Pydantic v2 routing & automatic docs). | Actively maintained, zero CVEs in tested version. |
| **`uvicorn`** | `>=0.29.0` | `0.52.4` | M4 Web Server | Lightning-fast ASGI web server running FastAPI. | High (Could use Hypercorn or Daphne). | Standard production ASGI server. |
| **`pydantic`** | `>=2.7.0` | `2.13.5` | M4 Schemas | Strict data validation, type coercion, and serialization. | Low (Deeply coupled with FastAPI request contracts). | Core written in Rust (`pydantic-core`), highly performant. |
| **`python-dotenv`** | `>=1.0.0` | `1.2.3` | M4 / Config | Loads environment variables from `.env` file into `os.environ`. | High (Could read env vars natively or via custom parser). | Small, stable utility. |
| **`qiskit`** | `>=1.0.0` | `2.1.2` | M3 Quantum Engine | Core quantum circuit representation, gate definitions, and unitary transformations. | Low (Qiskit is the industry-standard SDK for quantum circuit design). | 100% isolated to M3; never leaked to M1/M4. |
| **`qiskit-aer`** | `>=0.14.0` | `0.17.2` | M3 Quantum Engine | High-performance C++ quantum simulator backend (`AerSimulator`). | Moderate (Could use Qiskit BasicSimulator, but Aer is much faster and supports noise models). | Local C++ execution; zero network overhead. |
| **`numpy`** | `>=1.26.0` | `2.2.6` | M3 / Scientific | Vector and matrix calculations, array manipulation. | Low (Required by Qiskit and scientific libraries). | Fundamental scientific package. |
| **`scipy`** | `>=1.12.0` | `1.16.2` | M3 / Scientific | Linear algebra and sparse matrix computations for quantum state vectors. | Low (Underlying engine for Qiskit state manipulation). | Standard scientific package. |
| **`pytest`** | `>=8.0.0` | `9.1.1` | Test Suite | Test discovery, execution, assertion inspection, and test fixtures. | Low (Defacto testing framework in Python ecosystem). | Robust, reliable test runner. |
| **`httpx`** | `>=0.27.0` | `0.28.1` | Test Suite / M4 | Asynchronous HTTP client used by FastAPI `TestClient` for integration tests. | Moderate (Could use `requests` for sync tests, but HTTPX supports async). | High reliability. |
| **`groq`** | `>=0.9.0` | Optional | M5 Grounded AI | Official SDK for calling Groq Cloud LLM completion endpoints. | High (Can fall back to `MockLLMProvider` or use generic OpenAI client). | Optional dependency; system works 100% offline without it. |

---

## 2. Frontend Technology Audit

### Current Audited Frontend Stack:
- **Framework**: **Vanilla JavaScript (ES6+ ECMAScript Modules)**.
- **HTML**: Native HTML5 (`frontend/index.html`).
- **CSS**: Custom CSS3 design system with CSS custom properties (`frontend/css/styles.css`).
- **CDN Libraries**:
  - `KaTeX 0.16.8` (`katex.min.js`, `auto-render.min.js`, `katex.min.css`) for LaTeX rendering.
- **Important Finding on Frontend Technology**:
  - Certain historical documentation references React or Next.js.
  - **Actual Source of Truth**: The actual implementation is **Pure Vanilla HTML/JS/CSS**. There is no Node.js runtime, Webpack build step, or npm bundle required. The frontend runs directly in any modern browser.
