# Q-BIT.140 — M1 Frontend Architecture Deep Dive

## 1. Frontend Technology Stack & Architecture

- **Core Paradigm**: Vanilla Single-Page Application (SPA) utilizing native ECMAScript 6+ Modules (`<script type="module">`).
- **Styling Architecture**: Modern CSS3 (`frontend/css/styles.css`) utilizing CSS Custom Properties (Design System tokens), glassmorphism effects (`backdrop-filter: blur(12px)`), CSS Grid, and Flexbox layouts.
- **Mathematical Rendering**: Client-side LaTeX rendering powered by **KaTeX 0.16.8** (loaded via CDN with auto-render extension).
- **Communication Layer**: Native browser `fetch()` wrapped in a modular asynchronous client (`frontend/js/api_client.js`).
- **Presentation Transformation**: Pure client-side data adapter (`frontend/js/adapter.js`) normalizing M4 JSON contracts into UI view models.
- **Circuit Studio**: Interactive 2-qubit circuit canvas and gate layout tool (`frontend/js/circuit_view.js`).

---

## 2. HTML Structure & DOM Breakdown

The primary interface (`frontend/index.html`, 1132 lines) is divided into 7 distinct visual sections:

```
+-----------------------------------------------------------------------------------+
| 1. HEADER & TOP NAVIGATION BAR                                                   |
|    - Logo ("Q-BIT.140"), Subtitle ("Quantum Adaptive Learning")                  |
|    - Concept Mastery Badges (Qubits, States, Superposition, Gates, Measurement)   |
|    - Learner Identity Selector ("Learner Profile")                               |
+-----------------------------------------------------------------------------------+
| 2. ERROR / NOTIFICATION TOAST BANNER (#errorNotificationBanner)                  |
+-----------------------------------------------------------------------------------+
| 3. ACTIVITY HEADER & CURRICULUM SELECTOR                                         |
|    - Activity Title, Concept Tag, Task Type Badge                                 |
|    - Dynamic Activity Selector Dropdown (#activitySelector)                       |
+-----------------------------------------------------------------------------------+
| 4. MAIN WORKSPACE (2-COLUMN GRID)                                                 |
|    LEFT COLUMN:                                RIGHT COLUMN:                      |
|    - Problem Prompt / Circuit Specs            - Interactive State Triad Cards    |
|    - Circuit Studio Canvas (Interactive Grid)  - Measurement Probability Chart    |
|    - Prediction / Conceptual Choice Controls   - "Why This Next?" Adaptive Card   |
|    - Execution Button ("Simulate & Verify")    - Causal Evidence Timeline         |
|                                                - State Inspector Table            |
+-----------------------------------------------------------------------------------+
| 5. GROUNDED AI TUTOR CHAT PANEL (#aiGuidancePanel)                               |
|    - Chat message history with live KaTeX mathematical formatting                 |
|    - Contextual prompt suggestions ("Explain Target", "Why did this happen?")     |
|    - Free-form inquiry input (#chatInput)                                         |
+-----------------------------------------------------------------------------------+
```

---

## 3. UI State Triad Architecture

A signature innovation of Q-BIT.140 is the **State Triad**, which physically separates three conceptual entities that novices frequently conflate:

```
+-----------------------------------------------------------------------------------+
| THE STATE TRIAD                                                                   |
|                                                                                   |
|  [ CARD 1: LEARNER PREDICTION ]   [ CARD 2: THEORETICAL TARGET ]  [ CARD 3: PHYSICAL EXECUTION ]  |
|  State: |01⟩                      State: |10⟩                     State: |10⟩ (93.8%)             |
|  Status: MISMATCH (Amber)         Target: Canonical Target        Shots: 1024 Aer Simulation      |
|  "What the student guessed"       "What algorithm should find"    "What quantum mechanics gave"   |
+-----------------------------------------------------------------------------------+
```

### Triad Integrity Rules:
1. **Prediction Isolation**: The prediction is strictly derived from user interaction (`response` field) and styled amber on mismatch or green on match.
2. **Target Invariance**: The target state is extracted from `activity.quantum_experiment.target_state` or `verified_result.target_state`.
3. **Physical Result Grounding**: The physical result displays the empirical `most_likely_state` and percentage calculated from real 1024-shot simulation counts.

---

## 4. User Interaction & Event Lifecycle

### Detailed Trace: Prediction Submission
```
1. USER CLICKS RADIO OPTION "|01⟩"
   ↳ Event: 'change' event on input[name="predictionOption"]
   ↳ JS: selectedOptionLetter = "01"; #submitBtn enabled

2. USER CLICKS "Run Simulation & Verify Prediction"
   ↳ Event: 'click' event on #submitBtn
   ↳ JS: submitPredictionHandler() triggered
   ↳ UI Update: #executionProgressBanner displayed; #submitBtn shows spinner
   ↳ API Call: submitPrediction("act_grover_2q_predict", "mvp_evaluator_001", "01")
   ↳ HTTP: POST /api/v1/activity/act_grover_2q_predict/submit
   ↳ Backend: Runs Aer simulation -> builds evidence -> runs M2 -> saves DB
   ↳ Response: 200 OK with SubmissionResponse JSON envelope

3. CLIENT RECEIVES RESPONSE
   ↳ JS: normalized = normalizeSubmissionResponse(response)
   ↳ UI Updates:
       a. #stateTriad: Updates Prediction (|01⟩ Mismatch), Target (|10⟩), Result (|10⟩ 93.8%)
       b. #probChart: Renders 4 animated horizontal bars (|00⟩, |01⟩, |10⟩, |11⟩)
       c. #whyThisNext: Renders action ("gather_evidence"), trigger ("single_prediction_mismatch")
       d. #causalTimeline: Appends new attempt node with evidence ID
       e. #stateInspector: Updates mastery table and gap inference tags
       f. #conceptBadges: Recalculates badge fill based on concept mastery

4. AUTOMATIC AI EXPLANATION REQUEST
   ↳ JS: explainExperiment(response) triggered in background
   ↳ HTTP: POST /api/v1/ai/explain_experiment
   ↳ Response: Grounded Markdown string
   ↳ UI Update: Injects response into #chatHistory; triggers renderMath(chatContainer)
```

---

## 5. Client-Side Error & Offline Fallback Handling

| Failure Scenario | Frontend Detection | UI Behavior | User Experience |
|---|---|---|---|
| **Backend Unreachable** | `fetch()` throws `TypeError` | Caught in `try...catch` block | Shows red error toast: *"Cannot connect to backend server at http://localhost:8000"*. No app crash. |
| **Activity Not Found (404)** | `res.status === 404` | Error alert displayed | Displays *"Activity not found. Returning to catalog."* |
| **Simulation Failure (500)** | `res.status === 500` | Error banner displayed | Shows *"Quantum simulation failed. Please try again."* |
| **Storage Failure (503)** | `res.status === 503` | Amber warning toast | Shows *"State storage temporarily unavailable. Session running in local memory."* |
| **Groq API Rate Limit** | Backend fallback to `MockLLM` | Transparent to client | Client receives grounded deterministic explanation instantly. |
