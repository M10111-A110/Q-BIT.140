# Q-BIT.140 — M2 Adaptive Learner Model Deep Dive

## 1. Cognitive Architecture & Philosophy

The M2 Adaptive Learner Engine (`backend/adaptive/`) is a **purely deterministic cognitive modeling system** designed to solve the pedagogical hallucination problem in AI tutors.

In traditional LLM-based tutoring platforms, the language model decides what the student knows and what activity to assign next. This leads to erratic curriculum jumping, inconsistent remediation, and fabricated mastery.

In Q-BIT.140, **M2 is the sole decision authority**. The LLM (M5) is completely forbidden from modifying learner state or choosing activities.

```
+-----------------------------------------------------------------------------------+
| TIER 1: RAW OBSERVATION & EVIDENCE EXTRACTION                                     |
|  - Compares student response against verified quantum simulation / answer keys    |
|  - Produces immutable LearnerEvidence record with unique ID (ev_...)              |
+-----------------------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------------------+
| TIER 2: HISTORICAL EVIDENCE ACCUMULATION                                          |
|  - Maintains complete audit trail in LearnerState (evidence_history)              |
|  - Tracks chronological attempts, errors, and score history per concept           |
+-----------------------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------------------+
| TIER 3: DOMAIN-LEVEL COGNITIVE INFERENCE & MASTERY                               |
|  - Computes deterministic linear mastery score for each concept in DAG            |
|  - Evaluates prerequisite mastery bottlenecks and active error states             |
|  - Formulates GapInference hypotheses (e.g. possible_qubit_difficulty)            |
+-----------------------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------------------+
| TIER 4: DETERMINISTIC PEDAGOGICAL DECISION                                        |
|  - Executes deterministic routing rules                                           |
|  - Emits AdaptiveRecommendation (advance, gather_evidence, targeted_remediation)  |
+-----------------------------------------------------------------------------------+
```

---

## 2. Mathematical Mastery Formulation

### Actual Implemented Mastery Formula (`backend/adaptive/engine.py:48-64`)

The mastery score for a topic given learner history is computed via a transparent, deterministic linear heuristic:

$$\text{Mastery}(c) = \text{clamp}_{[0.0, 1.0]}\big(\text{diag\_score}(c) + \text{improvement\_bonus}(c) - \text{error\_penalty}(c)\big)$$

where:
- **`diag_score(c)`**: The latest recorded base score from diagnostic assessments or activity attempts (`state.concept_scores.get(topic, 0.0)`).
- **`improvement_bonus(c)`**:
  $$\text{improvement\_bonus} = \begin{cases} \max(0.0, S_{\text{latest}} - S_{\text{prior}}) \times 0.2 & \text{if } \text{len}(\text{history}) \ge 2 \\ 0.0 & \text{otherwise} \end{cases}$$
  (Provides up to $+0.20$ bonus when a learner demonstrates positive score delta between consecutive attempts).
- **`error_penalty(c)`**:
  $$\text{error\_penalty} = \min(\text{len}(\text{errors}) \times 0.05, 0.30)$$
  (Subtracts $0.05$ per recorded error, capped at a maximum deduction of $0.30$).
- **Clamping and Rounding**: The result is clamped to $[0.0, 1.0]$ and rounded to 3 decimal places via `round(max(0.0, min(1.0, mastery)), 3)`.

### Concrete Numerical Examples (Verified against `tests/adaptive/test_mastery.py`):
1. **Initial single attempt with 1 error**: Base score $0.80$, 1 error ($0.05$ penalty) $\rightarrow \text{Mastery} = 0.80 + 0.0 - 0.05 = 0.75$.
2. **Improvement from 0.40 to 0.80**: Base score $0.80$, improvement delta $(0.80 - 0.40) \times 0.2 = +0.08$, 1 error ($0.05$ penalty) $\rightarrow \text{Mastery} = 0.80 + 0.08 - 0.05 = 0.83$.
3. **Score drop (no bonus)**: Attempt 1 = $0.80$, Attempt 2 = $0.60$, 2 errors ($0.10$ penalty) $\rightarrow \text{Mastery} = 0.60 + 0.0 - 0.10 = 0.50$.
4. **Many errors cap**: 10 errors ($10 \times 0.05 = 0.50$, capped at $0.30$), score $0.40$ $\rightarrow \text{Mastery} = 0.40 - 0.30 = 0.10$.

---

## 3. Prerequisite Bottleneck Inference (`find_unmastered_prerequisite`)

To find unmastered prerequisite gaps for a concept $c$ (`backend/adaptive/engine.py:66-107`), the engine traverses concept dependencies using a two-tier priority rule:

- **Priority 1 (Active Error Check)**: Checks if any prerequisite concept has active error records in `state.errors`. If so, returns the earliest prerequisite with active errors.
- **Priority 2 (Mastery Threshold Check)**: Checks if any prerequisite concept has computed mastery strictly below `MASTERY_THRESHOLD = 0.6`. If so, returns that prerequisite.
- If all prerequisites have $\ge 0.6$ mastery and zero active errors, returns `None`.

---

## 4. Evidence Sufficiency Semantics & Confidence Calculation

Every piece of evidence and cognitive inference is tagged with an auditable **Evidence Sufficiency Classification**:

| Sufficiency Level | Threshold Condition | Confidence Value | Pedagogical Meaning | Action Permitted |
|---|---|---|---|---|
| `insufficient` | 1 observed error | $0.35$ (Fixed) | Preliminary anomaly; could be typo or slip | `gather_evidence` on current activity (no premature remediation) |
| `sufficient_for_targeted_inference` | $\ge 2$ consecutive errors | $\min(0.40 + N_{\text{err}} \times 0.25, 0.90)$ | Persistent conceptual bottleneck detected | `targeted_remediation` to prerequisite diagnostic |
| `sufficient_for_improvement_observation` | 1 correct attempt after remediation | $\ge 0.70$ | Recovery observed; validating stability | Advance or step-up activity |
| `sufficient_for_mastery` | Consistent correct attempts ($M \ge 0.60$) | $1.0$ (or $0.0$ for general advance) | Conceptual mastery demonstrated | `advance` to downstream curriculum node |

---

## 5. Current Activity Catalog & Deterministic Routing Rules

The active MVP catalog in `backend/adaptive/activities.py` registers **4 Core Activities**:

| Activity ID | Task Type | Canonical Concept ID | Prerequisites | Remediation Target | Next Activity |
|---|---|---|---|---|---|
| **`act_grover_2q_predict`** | `quantum_prediction` | `grover.search_problem` | `quantum.superposition`, `quantum.measurement` | `act_measurement_prob_diagnostic` | `act_grover_iteration_reasoning` |
| **`act_measurement_prob_diagnostic`** | `conceptual_choice` | `quantum.measurement` | `quantum.state` | `act_superposition_remediation` | `act_grover_2q_predict` |
| **`act_superposition_remediation`** | `conceptual_choice` | `quantum.superposition` | `quantum.qubit` | `None` | `act_measurement_prob_diagnostic` |
| **`act_grover_iteration_reasoning`** | `conceptual_choice` | `grover.amplitude_amplification` | `grover.search_problem` | `act_grover_2q_predict` | `None` |

### Deterministic Routing Rules Table (`backend/adaptive/engine.py:338-410`):

| Rule Name | Condition / Evidence State | Action | Target Activity | Reason String |
|---|---|---|---|---|
| **Rule 1: Immediate Success** | `evidence.is_correct == True` AND `next_activity_id != None` | `advance` | `activity.next_activity_id` | *"Learner demonstrated correct understanding in '<title>'. Ready to advance to '<next_title>'."* |
| **Rule 2: Terminal Success** | `evidence.is_correct == True` AND `next_activity_id == None` | `advance` | `None` | *"Learner demonstrated correct understanding in '<title>' (end of activity sequence)."* |
| **Rule 3: Single Error Observation** | `evidence.is_correct == False` AND `recent_errors == 1` | `gather_evidence` | Current activity ID (`activity.activity_id`) | *"Initial prediction mismatch on '<title>'. Gathering additional evidence before selecting remediation."* |
| **Rule 4: Repeated Errors (Prerequisite Remediation)** | `evidence.is_correct == False` AND `recent_errors >= 2` | `targeted_remediation` | `activity.remediation_activity_id` (or unmastered prerequisite activity) | *"Repeated prediction errors provide evidence consistent with possible difficulty in <concept>. Recommending targeted remediation in '<remed_title>'."* |
