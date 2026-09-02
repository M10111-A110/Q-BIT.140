# Explanation: `backend/ai/prompts.py`

## Purpose

This page explains the meaningful behavior in `backend/ai/prompts.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
from __future__ import annotations

import json
from typing import Any, Optional

SYSTEM_PROMPT = """You are the Q-BIT AI Guidance assistant for an evidence-driven adaptive quantum computing learning platform.
You help learners understand quantum concepts, algorithms (including Grover's algorithm), and their mathematical foundations.

Grounding Contract & Strict Rules:
- Base your answers strictly on the supplied EVIDENCE and CURRICULUM CONTEXT.
- Maintain a strict distinction between:
  1. CURRICULUM KNOWLEDGE: General educational principles (used strictly for conceptual explanations, never as learner evidence).
  2. LEARNER EVIDENCE: The learner's actual response/choice, correctness, and task metadata.
  3. QUANTUM EXECUTION EVIDENCE: Authoritative simulation outputs (counts, probabilities, measured states, circuits) from verified quantum executions.
  4. ADAPTIVE DECISION: Deterministic pedagogical actions, hypotheses, and rationales from M2.
- NEVER claim an interaction was a quantum execution or simulation unless QUANTUM EXECUTION EVIDENCE is explicitly provided in the prompt.
- NEVER format non-state choices (e.g. MCQ option letters A, B, C, D) as Dirac quantum state kets like |A⟩ or |B⟩.
- NEVER fabricate missing values, target states, predictions, measurement counts, or shot statistics.
- If a field is missing or not applicable, omit that claim completely. Never output placeholder tokens like "N/A" or "|N/A⟩" as observed facts.
- For conceptual responses without execution evidence: explain what was asked, the learner's response, correctness, the underlying quantum concept, and learning takeaways.
- For quantum executions: explain the prediction vs verified outcome, target state (if present), measurement probabilities/counts (if present), and circuit mechanism.
- For adaptive decisions: explain why M2 selected the action based on the supplied evidence sufficiency and trigger.
- Format equations using standard KaTeX: inline as $formula$ and block display as $$formula$$.
"""


def build_ask_prompt(
    question: str,
    curriculum_context: str,
    learner_context: Optional[dict[str, Any]] = None,
) -> list[dict[str, str]]:
    """Build messages list for conceptual question answering."""
    learner_context_str = ""
    if learner_context:
        learner_context_str = f"\nLEARNER STATE CONTEXT:\n{json.dumps(learner_context, indent=2)}\n"

    user_content = f"""CURRICULUM KNOWLEDGE CONTEXT:
{curriculum_context}
{learner_context_str}
LEARNER QUESTION:
{question}

Please answer the learner's question using the curriculum knowledge context above. If the question asks about a specific learner attempt or execution outcome that is not present in the supplied learner state context, state honestly that no execution evidence is present. Format all math with KaTeX ($...$ or $$...$$)."""

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]


def build_experiment_explanation_prompt(
    learner_response: str,
    verified_result: Optional[dict[str, Any]],
    evidence: dict[str, Any],
    adaptive_decision: dict[str, Any],
    curriculum_context: str,
    user_question: Optional[str] = None,
) -> list[dict[str, str]]:
    """
    Build messages list for explaining a learner attempt.
    Strictly structures:
      1. Curriculum Knowledge Context (Educational background)
      2. Learner Evidence (Observed response and evaluation)
      3. Quantum Execution Evidence (Actual simulation output if present, or explicitly None)
      4. Adaptive Recommendation from M2 (Deterministic pedagogical routing)
    """
    user_q_section = f"\nLEARNER ADDITIONAL QUESTION:\n{user_question}\n" if user_question else ""

    evidence_id = evidence.get("evidence_id", "N/A")
    evidence_type = evidence.get("evidence_type", "derived_evaluation")
    evidence_source = evidence.get("evidence_source", "learner")
    concept_id = evidence.get("concept_id", "")
    activity_id = evidence.get("activity_id", "")
    is_correct = evidence.get("is_correct", False)
    outcome_str = "CORRECT" if is_correct else "INCORRECT / MISMATCH"
    eval_details = evidence.get("evaluation_details", {})

    # 1. Learner Evidence block
    learner_ev_lines = [
        f"- Evidence ID: {evidence_id}",
        f"- Evidence Type: {evidence_type}",
        f"- Evidence Source: {evidence_source}",
    ]
    if concept_id:
        learner_ev_lines.append(f"- Concept ID: {concept_id}")
    if activity_id:
        learner_ev_lines.append(f"- Activity ID: {activity_id}")
    learner_ev_lines.append(f"- Learner Predicted State / Response: {learner_response}")
    learner_ev_lines.append(f"- Evaluation Outcome: {outcome_str}")
    if eval_details:
        learner_ev_lines.append(f"- Evaluation Details: {json.dumps(eval_details)}")
    learner_evidence_block = "\n".join(learner_ev_lines)

    # 2. Quantum Execution Evidence block (strictly omit if no execution occurred)
    has_execution = bool(verified_result and isinstance(verified_result, dict))
    if has_execution:
        exec_lines = [
            f"- Algorithm: {verified_result.get('algorithm', 'Quantum Circuit')}",
        ]
        if "target_state" in verified_result:
            exec_lines.append(f"- Theoretical Target State: {verified_result['target_state']}")
        if "most_likely_state" in verified_result:
            exec_lines.append(f"- Empirical Most-Likely Measured State: {verified_result['most_likely_state']}")
        if "target_probability" in verified_result:
            exec_lines.append(f"- Target State Probability: {verified_result['target_probability']}")
        if "counts" in verified_result:
            exec_lines.append(f"- Empirical Measurement Counts: {json.dumps(verified_result['counts'])}")
        if "shots" in verified_result:
            exec_lines.append(f"- Total Shots Sampled: {verified_result['shots']}")
        if "circuit" in verified_result:
            exec_lines.append(f"- Circuit Metadata: {json.dumps(verified_result['circuit'])}")
        quantum_execution_block = "\n".join(exec_lines)
    else:
        quantum_execution_block = "None (This interaction was a conceptual/diagnostic task without quantum circuit execution.)"

    # 3. Adaptive Decision block
    decision_lines = []
    if adaptive_decision and isinstance(adaptive_decision, dict):
        if "decision_id" in adaptive_decision:
            decision_lines.append(f"- Decision ID: {adaptive_decision['decision_id']}")
        if "action" in adaptive_decision:
            decision_lines.append(f"- Action: {adaptive_decision['action']}")
        if "target" in adaptive_decision and adaptive_decision["target"] is not None:
            decision_lines.append(f"- Target Activity: {adaptive_decision['target']}")
        if "reason" in adaptive_decision:
            decision_lines.append(f"- Pedagogical Rationale: {adaptive_decision['reason']}")
        if "hypothesis" in adaptive_decision:
            decision_lines.append(f"- Learner-State Hypothesis: {adaptive_decision['hypothesis']}")
        if "trigger" in adaptive_decision:
            decision_lines.append(f"- Decision Trigger: {adaptive_decision['trigger']}")
        if "evidence_sufficiency" in adaptive_decision:
            decision_lines.append(f"- Evidence Sufficiency: {adaptive_decision['evidence_sufficiency']}")
        if "supporting_evidence_ids" in adaptive_decision:
            decision_lines.append(f"- Supporting Evidence IDs: {json.dumps(adaptive_decision['supporting_evidence_ids'])}")

    adaptive_decision_block = "\n".join(decision_lines) if decision_lines else "None"

    # Tailor guidance instruction to the available evidence type
    if has_execution:
        instruction = (
            "Provide a Grounded Quantum Execution Analysis comparing the learner's prediction with the verified empirical outcome, "
            "explaining the physical circuit mechanism and Born's rule measurement probabilities, and explain why M2 recommended this adaptive decision. "
            "Format all equations using KaTeX ($...$ or $$...$$)."
        )
    else:
        instruction = (
            "Provide a Grounded Concept Explanation for the learner's response, explaining what was tested, whether the selection was correct, "
            "the underlying quantum concept, and why M2 recommended this adaptive decision. "
            "DO NOT include a quantum execution analysis or discuss simulator shot counts because no circuit execution occurred. "
            "Format all equations using KaTeX ($...$ or $$...$$)."
        )

    user_content = f"""CURRICULUM KNOWLEDGE CONTEXT:
{curriculum_context}

LEARNER EVIDENCE:
{learner_evidence_block}

QUANTUM EXECUTION EVIDENCE:
{quantum_execution_block}

ADAPTIVE RECOMMENDATION (M2):
{adaptive_decision_block}
{user_q_section}
{instruction}"""

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

```

## Line Notes

### Line 1

`from __future__ import annotations`

Imports a dependency or project symbol so later code can use it by name.
### Line 2

`(blank)`

Blank line used to separate nearby statements.
### Line 3

`import json`

Imports a dependency or project symbol so later code can use it by name.
### Line 4

`from typing import Any, Optional`

Imports a dependency or project symbol so later code can use it by name.
### Line 5

`(blank)`

Blank line used to separate nearby statements.
### Line 6

`SYSTEM_PROMPT = """You are the Q-BIT AI Guidance assistant for an evidence-driven adaptive quantum computing learning platform.`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 7

`You help learners understand quantum concepts, algorithms (including Grover's algorithm), and their mathematical foundations.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 8

`(blank)`

Blank line used to separate nearby statements.
### Line 9

`Grounding Contract & Strict Rules:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 10

`- Base your answers strictly on the supplied EVIDENCE and CURRICULUM CONTEXT.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 11

`- Maintain a strict distinction between:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 12

`1. CURRICULUM KNOWLEDGE: General educational principles (used strictly for conceptual explanations, never as learner evidence).`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 13

`2. LEARNER EVIDENCE: The learner's actual response/choice, correctness, and task metadata.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 14

`3. QUANTUM EXECUTION EVIDENCE: Authoritative simulation outputs (counts, probabilities, measured states, circuits) from verified quantum executions.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 15

`4. ADAPTIVE DECISION: Deterministic pedagogical actions, hypotheses, and rationales from M2.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 16

`- NEVER claim an interaction was a quantum execution or simulation unless QUANTUM EXECUTION EVIDENCE is explicitly provided in the prompt.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 17

`- NEVER format non-state choices (e.g. MCQ option letters A, B, C, D) as Dirac quantum state kets like |A⟩ or |B⟩.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 18

`- NEVER fabricate missing values, target states, predictions, measurement counts, or shot statistics.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 19

`- If a field is missing or not applicable, omit that claim completely. Never output placeholder tokens like "N/A" or "|N/A⟩" as observed facts.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 20

`- For conceptual responses without execution evidence: explain what was asked, the learner's response, correctness, the underlying quantum concept, and learning takeaways.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 21

`- For quantum executions: explain the prediction vs verified outcome, target state (if present), measurement probabilities/counts (if present), and circuit mechanism.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 22

`- For adaptive decisions: explain why M2 selected the action based on the supplied evidence sufficiency and trigger.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 23

`- Format equations using standard KaTeX: inline as $formula$ and block display as $$formula$$.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 24

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 25

`(blank)`

Blank line used to separate nearby statements.
### Line 27

`def build_ask_prompt(`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 28

`question: str,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 29

`curriculum_context: str,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 30

`learner_context: Optional[dict[str, Any]] = None,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 31

`) -> list[dict[str, str]]:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 32

`"""Build messages list for conceptual question answering."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 33

`learner_context_str = ""`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 34

`if learner_context:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 35

`learner_context_str = f"\nLEARNER STATE CONTEXT:\n{json.dumps(learner_context, indent=2)}\n"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 36

`(blank)`

Blank line used to separate nearby statements.
### Line 37

`user_content = f"""CURRICULUM KNOWLEDGE CONTEXT:`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 38

`{curriculum_context}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 39

`{learner_context_str}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 40

`LEARNER QUESTION:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 41

`{question}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 42

`(blank)`

Blank line used to separate nearby statements.
### Line 43

`Please answer the learner's question using the curriculum knowledge context above. If the question asks about a specific learner attempt or execution outcome that is not present in the supplied learner state context, state honestly that no execution evidence is present. Format all math with KaTeX ($...$ or $$...$$)."""`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 44

`(blank)`

Blank line used to separate nearby statements.
### Line 45

`return [`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 46

`{"role": "system", "content": SYSTEM_PROMPT},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 47

`{"role": "user", "content": user_content},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 48

`]`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 49

`(blank)`

Blank line used to separate nearby statements.
### Line 51

`def build_experiment_explanation_prompt(`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 52

`learner_response: str,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 53

`verified_result: Optional[dict[str, Any]],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 54

`evidence: dict[str, Any],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 55

`adaptive_decision: dict[str, Any],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 56

`curriculum_context: str,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 57

`user_question: Optional[str] = None,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 58

`) -> list[dict[str, str]]:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 59

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 60

`Build messages list for explaining a learner attempt.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 61

`Strictly structures:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 62

`1. Curriculum Knowledge Context (Educational background)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 63

`2. Learner Evidence (Observed response and evaluation)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 64

`3. Quantum Execution Evidence (Actual simulation output if present, or explicitly None)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 65

`4. Adaptive Recommendation from M2 (Deterministic pedagogical routing)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 66

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 67

`user_q_section = f"\nLEARNER ADDITIONAL QUESTION:\n{user_question}\n" if user_question else ""`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 68

`(blank)`

Blank line used to separate nearby statements.
### Line 69

`evidence_id = evidence.get("evidence_id", "N/A")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 70

`evidence_type = evidence.get("evidence_type", "derived_evaluation")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 71

`evidence_source = evidence.get("evidence_source", "learner")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 72

`concept_id = evidence.get("concept_id", "")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 73

`activity_id = evidence.get("activity_id", "")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 74

`is_correct = evidence.get("is_correct", False)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 75

`outcome_str = "CORRECT" if is_correct else "INCORRECT / MISMATCH"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 76

`eval_details = evidence.get("evaluation_details", {})`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 77

`(blank)`

Blank line used to separate nearby statements.
### Line 78

`# 1. Learner Evidence block`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 79

`learner_ev_lines = [`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 80

`f"- Evidence ID: {evidence_id}",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 81

`f"- Evidence Type: {evidence_type}",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 82

`f"- Evidence Source: {evidence_source}",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 83

`]`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 84

`if concept_id:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 85

`learner_ev_lines.append(f"- Concept ID: {concept_id}")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 86

`if activity_id:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 87

`learner_ev_lines.append(f"- Activity ID: {activity_id}")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 88

`learner_ev_lines.append(f"- Learner Predicted State / Response: {learner_response}")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 89

`learner_ev_lines.append(f"- Evaluation Outcome: {outcome_str}")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 90

`if eval_details:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 91

`learner_ev_lines.append(f"- Evaluation Details: {json.dumps(eval_details)}")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 92

`learner_evidence_block = "\n".join(learner_ev_lines)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 93

`(blank)`

Blank line used to separate nearby statements.
### Line 94

`# 2. Quantum Execution Evidence block (strictly omit if no execution occurred)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 95

`has_execution = bool(verified_result and isinstance(verified_result, dict))`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 96

`if has_execution:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 97

`exec_lines = [`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 98

`f"- Algorithm: {verified_result.get('algorithm', 'Quantum Circuit')}",`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 99

`]`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 100

`if "target_state" in verified_result:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 101

`exec_lines.append(f"- Theoretical Target State: {verified_result['target_state']}")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 102

`if "most_likely_state" in verified_result:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 103

`exec_lines.append(f"- Empirical Most-Likely Measured State: {verified_result['most_likely_state']}")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 104

`if "target_probability" in verified_result:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 105

`exec_lines.append(f"- Target State Probability: {verified_result['target_probability']}")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 106

`if "counts" in verified_result:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 107

`exec_lines.append(f"- Empirical Measurement Counts: {json.dumps(verified_result['counts'])}")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 108

`if "shots" in verified_result:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 109

`exec_lines.append(f"- Total Shots Sampled: {verified_result['shots']}")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 110

`if "circuit" in verified_result:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 111

`exec_lines.append(f"- Circuit Metadata: {json.dumps(verified_result['circuit'])}")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 112

`quantum_execution_block = "\n".join(exec_lines)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 113

`else:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 114

`quantum_execution_block = "None (This interaction was a conceptual/diagnostic task without quantum circuit execution.)"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 115

`(blank)`

Blank line used to separate nearby statements.
### Line 116

`# 3. Adaptive Decision block`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 117

`decision_lines = []`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 118

`if adaptive_decision and isinstance(adaptive_decision, dict):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 119

`if "decision_id" in adaptive_decision:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 120

`decision_lines.append(f"- Decision ID: {adaptive_decision['decision_id']}")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 121

`if "action" in adaptive_decision:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 122

`decision_lines.append(f"- Action: {adaptive_decision['action']}")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 123

`if "target" in adaptive_decision and adaptive_decision["target"] is not None:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 124

`decision_lines.append(f"- Target Activity: {adaptive_decision['target']}")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 125

`if "reason" in adaptive_decision:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 126

`decision_lines.append(f"- Pedagogical Rationale: {adaptive_decision['reason']}")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 127

`if "hypothesis" in adaptive_decision:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 128

`decision_lines.append(f"- Learner-State Hypothesis: {adaptive_decision['hypothesis']}")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 129

`if "trigger" in adaptive_decision:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 130

`decision_lines.append(f"- Decision Trigger: {adaptive_decision['trigger']}")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 131

`if "evidence_sufficiency" in adaptive_decision:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 132

`decision_lines.append(f"- Evidence Sufficiency: {adaptive_decision['evidence_sufficiency']}")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 133

`if "supporting_evidence_ids" in adaptive_decision:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 134

`decision_lines.append(f"- Supporting Evidence IDs: {json.dumps(adaptive_decision['supporting_evidence_ids'])}")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 135

`(blank)`

Blank line used to separate nearby statements.
### Line 136

`adaptive_decision_block = "\n".join(decision_lines) if decision_lines else "None"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 137

`(blank)`

Blank line used to separate nearby statements.
### Line 138

`# Tailor guidance instruction to the available evidence type`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 139

`if has_execution:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 140

`instruction = (`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 141

`"Provide a Grounded Quantum Execution Analysis comparing the learner's prediction with the verified empirical outcome, "`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 142

`"explaining the physical circuit mechanism and Born's rule measurement probabilities, and explain why M2 recommended this adaptive decision. "`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 143

`"Format all equations using KaTeX ($...$ or $$...$$)."`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 144

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 145

`else:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 146

`instruction = (`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 147

`"Provide a Grounded Concept Explanation for the learner's response, explaining what was tested, whether the selection was correct, "`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 148

`"the underlying quantum concept, and why M2 recommended this adaptive decision. "`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 149

`"DO NOT include a quantum execution analysis or discuss simulator shot counts because no circuit execution occurred. "`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 150

`"Format all equations using KaTeX ($...$ or $$...$$)."`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 151

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 152

`(blank)`

Blank line used to separate nearby statements.
### Line 153

`user_content = f"""CURRICULUM KNOWLEDGE CONTEXT:`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 154

`{curriculum_context}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 155

`(blank)`

Blank line used to separate nearby statements.
### Line 156

`LEARNER EVIDENCE:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 157

`{learner_evidence_block}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 158

`(blank)`

Blank line used to separate nearby statements.
### Line 159

`QUANTUM EXECUTION EVIDENCE:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 160

`{quantum_execution_block}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 161

`(blank)`

Blank line used to separate nearby statements.
### Line 162

`ADAPTIVE RECOMMENDATION (M2):`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 163

`{adaptive_decision_block}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 164

`{user_q_section}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 165

`{instruction}"""`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 166

`(blank)`

Blank line used to separate nearby statements.
### Line 167

`return [`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 168

`{"role": "system", "content": SYSTEM_PROMPT},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 169

`{"role": "user", "content": user_content},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 170

`]`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.

## Nearby Files

[backend/ai/__init__.py](__init__.py.md), [backend/ai/providers.py](providers.py.md), [backend/ai/retrieval.py](retrieval.py.md), [backend/ai/service.py](service.py.md)
