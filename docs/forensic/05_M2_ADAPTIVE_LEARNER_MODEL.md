# Q-BIT.140 — M2 Adaptive Learner Model Deep Dive

## 1. Cognitive Architecture & Philosophy

The M2 Adaptive Learner Engine is a **purely deterministic cognitive modeling system** designed to solve the *pedagogical hallucination problem* in AI tutors.

In traditional LLM-based tutoring platforms, the language model decides what the student knows and what activity to give next. This leads to erratic curriculum jumping, inconsistent remediation, and fabricated mastery.

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
|  - Computes recency-weighted Bayesian mastery for each concept in DAG             |
|  - Evaluates prerequisite mastery gates                                           |
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

### Recency-Weighted Empirical Mastery
For a concept $c$ with an observed score history $S = [s_0, s_1, \dots, s_{k-1}]$ where $s_i \in \{0.0, 1.0\}$:

$$\text{RawMastery}(c) = \frac{1.0 + \sum_{i=0}^{k-1} w_i \cdot s_i}{2.0 + \sum_{i=0}^{k-1} w_i}$$

where the recency decay weight $w_i$ is given by:

$$w_i = \lambda^{k - 1 - i}, \quad \lambda = 0.85$$

### Prior & Asymptotes:
- **Zero Evidence ($k = 0$)**: $\text{RawMastery} = \frac{1.0}{2.0} = 0.50$ (Prior of uniform uncertainty).
- **Single Failure ($S = [0]$)**: $\text{RawMastery} = \frac{1 + 0}{2 + 1} = \frac{1}{3} \approx 0.33$.
- **Single Success ($S = [1]$)**: $\text{RawMastery} = \frac{1 + 1}{2 + 1} = \frac{2}{3} \approx 0.67$.
- **Sustained Success ($S = [1, 1, 1, 1]$)**: $\text{RawMastery} \approx 0.88 - 0.95$.

### Prerequisite Gating Rule:
Mastery cannot advance beyond the mastery of foundational prerequisites:

$$\text{Mastery}_{\text{gated}}(c) = \min\left(\text{RawMastery}(c), \min_{p \in \text{Prereqs}(c)} \text{Mastery}(p)\right)$$

This mathematical constraint guarantees that a student cannot be marked "mastered" in Grover's Algorithm if their Superposition or Qubit mastery is degraded.

---

## 3. Evidence Sufficiency Semantics

Every piece of evidence and cognitive inference is tagged with an auditable **Evidence Sufficiency Classification**:

| Sufficiency Level | Threshold Condition | Pedagogical Meaning | Action Permitted |
|---|---|---|---|
| `insufficient` | 1 observed error | Preliminary anomaly; could be typo or slip | `gather_evidence` only (no remediation yet) |
| `sufficient_for_targeted_inference` | $\ge 2$ consecutive errors | Persistent conceptual bottleneck detected | `targeted_remediation` to prerequisite |
| `sufficient_for_improvement_observation` | 1 correct attempt after remediation | Recovery observed; validating stability | `gather_evidence` or step-up activity |
| `sufficient_for_mastery` | $\ge 3$ consistent successes ($M \ge 0.85$) | Conceptual mastery demonstrated | `advance` to downstream curriculum node |

---

## 4. Deterministic Adaptive Routing Rules Table

| Rule Name | Condition / Evidence State | M2 Action | Target Activity | Reason String | Code Location |
|---|---|---|---|---|---|
| **Rule 1: Immediate Success** | `evidence.is_correct == True` | `advance` | `activity.next_activity_id` | *"Learner demonstrated correct understanding in '<title>'. Ready to advance."* | `engine.py:338-356` |
| **Rule 2: Single Error Observation** | `evidence.is_correct == False` AND `recent_errors == 1` | `gather_evidence` | Current activity ID | *"Initial prediction mismatch on '<title>'. Gathering additional evidence before selecting remediation."* | `engine.py:360-372` |
| **Rule 3: Repeated Errors (Prerequisite Gap)** | `evidence.is_correct == False` AND `recent_errors >= 2` AND `prereq_gap != None` | `targeted_remediation` | Prerequisite activity ID (e.g. `act_diag_superposition`) | *"Repeated prediction errors provide evidence consistent with difficulty in <concept>. Recommending targeted remediation in '<prereq>'."* | `engine.py:375-397` |
| **Rule 4: Terminal Curriculum Node** | `evidence.is_correct == True` AND `next_activity_id == None` | `advance` | `None` | *"Learner demonstrated correct understanding in '<title>' (end of activity sequence)."* | `engine.py:350-356` |
