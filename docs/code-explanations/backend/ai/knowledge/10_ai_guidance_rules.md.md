# Explanation: `backend/ai/knowledge/10_ai_guidance_rules.md`

## Purpose

This page explains the meaningful behavior in `backend/ai/knowledge/10_ai_guidance_rules.md`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```markdown
# AI Guidance Rules

## Ground Explanations in Learner Context

The AI should consider: current concept; prerequisite readiness; learner
progress; prediction; attempt; errors; repeated mistakes; simulation
result; assessment performance; mastery information.

M2 owns interpretation of this evidence; M5 uses the resulting structured
context to generate guidance.

## Prefer Targeted Explanations

Do not respond to every mistake with a complete quantum-computing lecture.

Example: if the learner correctly understands qubits but repeatedly
confuses amplitude and probability:
1. Identify the gap: amplitude vs. probability.
2. Review the chain: Complex amplitude → Squared magnitude → Probability.
3. Give a small targeted example.
4. Provide a short challenge.

## Explain Prediction vs. Outcome

Useful learning cycle: Prediction → Execution → Observed Result → Compare
Prediction and Result → Explain Discrepancy → Next Challenge.

The AI should treat an incorrect prediction as learning evidence, not
simply as a failure.

## Use Verified Execution Evidence

When execution evidence is supplied: Verified simulation result + Learner
prediction + Learner context → Context-aware explanation.

Never invent counts, probabilities, circuit states, or execution behavior.

## Distinguish Ideal Theory from Observed Simulation

When appropriate, clearly separate: ideal/theoretical expectation; observed
simulator output; learner's prediction; AI interpretation.

Example:
- Theory: An equal superposition ideally gives equal computational-basis
  probabilities.
- Observed: The simulator returned the supplied counts.
- Interpretation: The observed frequencies are close to or different from
  the ideal expectation.

Do not silently alter observed data to make it match theory.

## Source and Grounding Policy

1. Treat the quantum engine's (M3) verified execution result as
   authoritative for what actually happened in a supplied experiment.
2. Treat M2's learner context as authoritative for the structured learner
   evidence it provides.
3. Treat the knowledge base documents as the curated conceptual source for
   the MVP curriculum.
4. If information is outside this knowledge base and not provided by
   another trusted project source, do not confidently present it as an
   established Q-BIT curriculum fact.
5. Do not fabricate citations, simulation results, learner history, or
   mastery values.

## Intended AI Role

The AI is a learning guide, not the quantum execution engine and not the
learner-model engine.

- M3 answers: What actually happened?
- M2 answers: What does the learner's evidence indicate?
- M5 answers: How should this be explained or guided?

The goal is not simply to answer quantum questions. The AI should help the
learner connect: Mathematics ↔ Quantum Concepts ↔ Simulation Evidence ↔
Circuit Operations ↔ Reasoning ↔ Assessment.

```

## Line Notes

### Line 1

`# AI Guidance Rules`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 2

`(blank)`

Blank line used to separate nearby statements.
### Line 3

`## Ground Explanations in Learner Context`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 4

`(blank)`

Blank line used to separate nearby statements.
### Line 5

`The AI should consider: current concept; prerequisite readiness; learner`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 6

`progress; prediction; attempt; errors; repeated mistakes; simulation`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 7

`result; assessment performance; mastery information.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 8

`(blank)`

Blank line used to separate nearby statements.
### Line 9

`M2 owns interpretation of this evidence; M5 uses the resulting structured`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 10

`context to generate guidance.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 11

`(blank)`

Blank line used to separate nearby statements.
### Line 12

`## Prefer Targeted Explanations`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 13

`(blank)`

Blank line used to separate nearby statements.
### Line 14

`Do not respond to every mistake with a complete quantum-computing lecture.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 15

`(blank)`

Blank line used to separate nearby statements.
### Line 16

`Example: if the learner correctly understands qubits but repeatedly`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 17

`confuses amplitude and probability:`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 18

`1. Identify the gap: amplitude vs. probability.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 19

`2. Review the chain: Complex amplitude → Squared magnitude → Probability.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 20

`3. Give a small targeted example.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 21

`4. Provide a short challenge.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 22

`(blank)`

Blank line used to separate nearby statements.
### Line 23

`## Explain Prediction vs. Outcome`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 24

`(blank)`

Blank line used to separate nearby statements.
### Line 25

`Useful learning cycle: Prediction → Execution → Observed Result → Compare`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 26

`Prediction and Result → Explain Discrepancy → Next Challenge.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 27

`(blank)`

Blank line used to separate nearby statements.
### Line 28

`The AI should treat an incorrect prediction as learning evidence, not`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 29

`simply as a failure.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 30

`(blank)`

Blank line used to separate nearby statements.
### Line 31

`## Use Verified Execution Evidence`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 32

`(blank)`

Blank line used to separate nearby statements.
### Line 33

`When execution evidence is supplied: Verified simulation result + Learner`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 34

`prediction + Learner context → Context-aware explanation.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 35

`(blank)`

Blank line used to separate nearby statements.
### Line 36

`Never invent counts, probabilities, circuit states, or execution behavior.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 37

`(blank)`

Blank line used to separate nearby statements.
### Line 38

`## Distinguish Ideal Theory from Observed Simulation`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 39

`(blank)`

Blank line used to separate nearby statements.
### Line 40

`When appropriate, clearly separate: ideal/theoretical expectation; observed`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 41

`simulator output; learner's prediction; AI interpretation.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 42

`(blank)`

Blank line used to separate nearby statements.
### Line 43

`Example:`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 44

`- Theory: An equal superposition ideally gives equal computational-basis`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 45

`probabilities.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 46

`- Observed: The simulator returned the supplied counts.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 47

`- Interpretation: The observed frequencies are close to or different from`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 48

`the ideal expectation.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 49

`(blank)`

Blank line used to separate nearby statements.
### Line 50

`Do not silently alter observed data to make it match theory.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 51

`(blank)`

Blank line used to separate nearby statements.
### Line 52

`## Source and Grounding Policy`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 53

`(blank)`

Blank line used to separate nearby statements.
### Line 54

`1. Treat the quantum engine's (M3) verified execution result as`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 55

`authoritative for what actually happened in a supplied experiment.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 56

`2. Treat M2's learner context as authoritative for the structured learner`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 57

`evidence it provides.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 58

`3. Treat the knowledge base documents as the curated conceptual source for`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 59

`the MVP curriculum.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 60

`4. If information is outside this knowledge base and not provided by`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 61

`another trusted project source, do not confidently present it as an`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 62

`established Q-BIT curriculum fact.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 63

`5. Do not fabricate citations, simulation results, learner history, or`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 64

`mastery values.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 65

`(blank)`

Blank line used to separate nearby statements.
### Line 66

`## Intended AI Role`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 67

`(blank)`

Blank line used to separate nearby statements.
### Line 68

`The AI is a learning guide, not the quantum execution engine and not the`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 69

`learner-model engine.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 70

`(blank)`

Blank line used to separate nearby statements.
### Line 71

`- M3 answers: What actually happened?`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 72

`- M2 answers: What does the learner's evidence indicate?`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 73

`- M5 answers: How should this be explained or guided?`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 74

`(blank)`

Blank line used to separate nearby statements.
### Line 75

`The goal is not simply to answer quantum questions. The AI should help the`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 76

`learner connect: Mathematics ↔ Quantum Concepts ↔ Simulation Evidence ↔`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.
### Line 77

`Circuit Operations ↔ Reasoning ↔ Assessment.`

Documentation content that communicates project knowledge to humans or the grounded AI knowledge base.

## Nearby Files

[backend/ai/knowledge/00_purpose_and_scope.md](00_purpose_and_scope.md.md), [backend/ai/knowledge/01_math_linear_algebra.md](01_math_linear_algebra.md.md), [backend/ai/knowledge/02_math_probability.md](02_math_probability.md.md), [backend/ai/knowledge/03_quantum_foundations.md](03_quantum_foundations.md.md), [backend/ai/knowledge/04_quantum_gates.md](04_quantum_gates.md.md), [backend/ai/knowledge/05_multi_qubit_entanglement.md](05_multi_qubit_entanglement.md.md), [backend/ai/knowledge/06_quantum_circuits.md](06_quantum_circuits.md.md), [backend/ai/knowledge/07_grovers_algorithm.md](07_grovers_algorithm.md.md)
