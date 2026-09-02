# Q-BIT.140 — M6 Visualization Architecture Deep Dive

## 1. Visualization Architecture & Principles

The M6 Visualization layer (`frontend/js/adapter.js`, `frontend/js/circuit_view.js`, `frontend/visualization/`) transforms raw API responses into intuitive, interactive visual models.

### Primary Responsibilities:
1. **Dirac Ket Notation Normalization**: Converts raw bitstrings (`"10"`) to Dirac ket strings (`"|10⟩"`).
2. **Probability Distribution Rendering**: Transforms measurement counts into animated probability bar charts.
3. **State Triad Normalization**: Maps the 3-part cognitive state (Prediction vs Target vs Result).
4. **Interactive Circuit Canvas**: Renders quantum wires, gates, and Grover presets on HTML5 canvas/SVG.
5. **Presentation Isolation**: M6 never mutates data; it only normalizes for rendering.

---

## 2. Normalization Engine (`normalizeSubmissionResponse`)

The primary transformation pipeline in `frontend/js/adapter.js` converts the raw M4 `SubmissionResponse` into a presentation view model:

```javascript
// Input: Raw M4 SubmissionResponse JSON
{
  "activity": { "activity_id": "act_grover_2q_predict", "concept_id": "quantum.algorithm.grover_2q" },
  "learner_response": "01",
  "verified_result": {
    "algorithm": "grover_2q",
    "target_state": "10",
    "most_likely_state": "10",
    "target_probability": 0.9385,
    "shots": 1024,
    "counts": { "10": 961, "00": 21, "01": 22, "11": 20 },
    "probabilities": { "10": 0.9385, "00": 0.0205, "01": 0.0215, "11": 0.0195 }
  },
  "evidence": { "is_correct": false, "attempt_number": 1, "evidence_sufficiency": "insufficient" },
  "learner_state": { "gap_inferences": { ... } },
  "adaptive_decision": { "action": "gather_evidence", "trigger": "single_prediction_mismatch" }
}

// Output: Normalized M6 Presentation Model
{
  activity: { activityId: "act_grover_2q_predict", title: "Quantum Activity", ... },
  learner: {
    predictionRaw: "01",
    predictionLabel: "|01⟩",
    isCorrect: false,
    outcomeText: "Prediction Mismatch",
    outcomeClass: "mismatch"
  },
  quantum: {
    targetStateLabel: "|10⟩",
    mostLikelyStateLabel: "|10⟩",
    targetProbabilityStr: "93.8%",
    probabilityBars: [
      { rawState: "00", stateLabel: "|00⟩", probability: 0.0205, percentageStr: "2.1%", count: 21, isTarget: false, isPredicted: false },
      { rawState: "01", stateLabel: "|01⟩", probability: 0.0215, percentageStr: "2.2%", count: 22, isTarget: false, isPredicted: true },
      { rawState: "10", stateLabel: "|10⟩", probability: 0.9385, percentageStr: "93.8%", count: 961, isTarget: true, isPredicted: false },
      { rawState: "11", stateLabel: "|11⟩", probability: 0.0195, percentageStr: "2.0%", count: 20, isTarget: false, isPredicted: false }
    ]
  },
  adaptive: {
    action: "gather_evidence",
    reason: "Initial prediction mismatch...",
    triggerLabel: "Single Prediction Mismatch",
    sufficiencyLabel: "Insufficient (Gathering Observations)"
  }
}
```

---

## 3. Circuit Studio Architecture (`CircuitStudio`)

The interactive circuit editor (`frontend/js/circuit_view.js`) manages an interactive 2-qubit grid:

- **Grid Dimensions**: 2 Qubit Wires ($q_0, q_1$) $\times$ 6 Gate Columns.
- **Supported Gate Library**:
  - `H` (Hadamard): Superposition builder.
  - `X` (Pauli-X): Bit flip ($|0\rangle \leftrightarrow |1\rangle$).
  - `Z` (Pauli-Z): Phase flip ($|1\rangle \mapsto -|1\rangle$).
  - `CZ` (Controlled-Z): 2-qubit phase entanglement gate.
  - `CNOT` (Controlled-NOT): 2-qubit entanglement gate.
  - `Measure`: Classical readout.
- **Built-in Presets**:
  - `grover_2q`: Preloads uniform superposition ($H, H$), target $|10\rangle$ oracle ($X, CZ, X$), diffusion ($H, X, CZ, X, H$), and measurement.
  - `bell_state`: Preloads Hadamard on $q_0$ and CNOT between $q_0 \rightarrow q_1$.
