# Explanation: `frontend/visualization/adapter.js`

## Purpose

This page explains the meaningful behavior in `frontend/visualization/adapter.js`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```javascript
/**
 * Q-BIT.140 — M6 Visualization Data Adapter
 * Normalizes M4/M3/M2 JSON response structures into clean view models.
 * Strictly presentation-only: never alters quantum probabilities, counts, or adaptive decisions.
 */

/**
 * Format a binary string (e.g. "10") into Dirac ket notation ("|10⟩").
 * @param {string} stateStr 
 * @returns {string}
 */
export function formatStateLabel(stateStr) {
    if (!stateStr) return "|?⟩";
    const cleaned = String(stateStr).trim();
    if (cleaned.startsWith("|") && cleaned.endsWith("⟩")) return cleaned;
    return `|${cleaned}⟩`;
}

/**
 * Format a probability float (e.g. 0.9345) to a formatted percentage string ("93.5%").
 * @param {number} value 
 * @returns {string}
 */
export function formatPercentage(value) {
    if (typeof value !== "number" || isNaN(value)) return "0.0%";
    return `${(value * 100).toFixed(1)}%`;
}

/**
 * Normalize the raw JSON response from POST /api/activity/{id}/submit
 * into a structured presentation model for M6 UI widgets.
 * @param {Object} response M4 API SubmissionResponse object
 * @returns {Object} Normalized visualization model
 */
export function normalizeSubmissionResponse(response) {
    if (!response || typeof response !== "object") {
        throw new Error("Invalid submission response: expected JSON object");
    }

    const activity = response.activity || {};
    const verified = response.verified_result || {};
    const evidence = response.evidence || {};
    const state = response.learner_state || {};
    const decision = response.adaptive_decision || {};

    const rawTarget = verified.target_state || "";
    const rawMostLikely = verified.most_likely_state || "";
    const rawPrediction = response.learner_response || "";
    const targetProb = typeof verified.target_probability === "number" ? verified.target_probability : 0.0;

    // Build probability distribution items for bar chart
    const probabilities = verified.probabilities || {};
    const counts = verified.counts || {};
    const allStates = Object.keys(probabilities).sort();

    const probabilityBars = allStates.map((st) => {
        const prob = probabilities[st] || 0.0;
        const count = counts[st] || 0;
        return {
            rawState: st,
            stateLabel: formatStateLabel(st),
            probability: prob,
            percentageStr: formatPercentage(prob),
            percentageNum: Number((prob * 100).toFixed(1)),
            count: count,
            isTarget: st === rawTarget,
            isMostLikely: st === rawMostLikely,
            isPredicted: st === rawPrediction,
        };
    });

    // Extract concept-level gap inference from M2 state
    const conceptId = evidence.concept_id || activity.concept_id || "";
    const gapInferences = state.gap_inferences || {};
    const conceptInference = gapInferences[conceptId] || {
        confidence: 0.0,
        status: "unassessed",
        description: "No inference recorded.",
    };

    return {
        activity: {
            activityId: activity.activity_id || "",
            title: activity.title || "Quantum Activity",
            conceptId: conceptId,
            taskType: activity.task_type || "quantum_prediction",
        },
        learner: {
            predictionRaw: rawPrediction,
            predictionLabel: formatStateLabel(rawPrediction),
            isCorrect: Boolean(evidence.is_correct),
            outcomeText: evidence.is_correct ? "Prediction Correct" : "Prediction Mismatch",
            outcomeClass: evidence.is_correct ? "success" : "mismatch",
            attemptNumber: evidence.attempt_number || 1,
        },
        quantum: {
            algorithm: verified.algorithm || "Grover's Algorithm",
            targetState: rawTarget,
            targetStateLabel: formatStateLabel(rawTarget),
            mostLikelyState: rawMostLikely,
            mostLikelyStateLabel: formatStateLabel(rawMostLikely),
            targetProbability: targetProb,
            targetProbabilityStr: formatPercentage(targetProb),
            shots: verified.shots || 1024,
            counts: counts,
            probabilities: probabilities,
            probabilityBars: probabilityBars,
            circuit: {
                numQubits: verified.circuit?.num_qubits || 2,
                numClbits: verified.circuit?.num_clbits || 2,
                depth: verified.circuit?.depth || 0,
                gateCounts: verified.circuit?.gate_counts || {},
                diagram: verified.circuit?.diagram || "",
            },
        },
        adaptive: {
            action: decision.action || "reinforce_current_concept",
            reason: decision.reason || "Continuing current activity.",
            targetActivity: decision.target || null,
            conceptId: decision.concept_id || conceptId,
            gapConfidence: conceptInference.confidence || 0.0,
            gapStatus: conceptInference.status || "observing",
            gapDescription: conceptInference.description || "",
            totalEvidenceCount: (state.evidence_history || []).length,
        },
    };
}

```

## Line Notes

### Line 1

`/**`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 2

`* Q-BIT.140 — M6 Visualization Data Adapter`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 3

`* Normalizes M4/M3/M2 JSON response structures into clean view models.`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 4

`* Strictly presentation-only: never alters quantum probabilities, counts, or adaptive decisions.`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 5

`*/`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 6

`(blank)`

Blank line used to separate nearby statements.
### Line 7

`/**`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 8

`* Format a binary string (e.g. "10") into Dirac ket notation ("|10⟩").`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 9

`* @param {string} stateStr`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 10

`* @returns {string}`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 11

`*/`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 12

`export function formatStateLabel(stateStr) {`

Imports or exposes a module symbol so code can be composed across frontend files.
### Line 13

`if (!stateStr) return "|?⟩";`

Controls browser-side execution based on data or user/application state.
### Line 14

`const cleaned = String(stateStr).trim();`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 15

`if (cleaned.startsWith("|") && cleaned.endsWith("⟩")) return cleaned;`

Controls browser-side execution based on data or user/application state.
### Line 16

`return \`|${cleaned}⟩\`;`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 17

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 18

`(blank)`

Blank line used to separate nearby statements.
### Line 19

`/**`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 20

`* Format a probability float (e.g. 0.9345) to a formatted percentage string ("93.5%").`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 21

`* @param {number} value`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 22

`* @returns {string}`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 23

`*/`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 24

`export function formatPercentage(value) {`

Imports or exposes a module symbol so code can be composed across frontend files.
### Line 25

`if (typeof value !== "number" || isNaN(value)) return "0.0%";`

Controls browser-side execution based on data or user/application state.
### Line 26

`return \`${(value * 100).toFixed(1)}%\`;`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 27

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 28

`(blank)`

Blank line used to separate nearby statements.
### Line 29

`/**`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 30

`* Normalize the raw JSON response from POST /api/activity/{id}/submit`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 31

`* into a structured presentation model for M6 UI widgets.`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 32

`* @param {Object} response M4 API SubmissionResponse object`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 33

`* @returns {Object} Normalized visualization model`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 34

`*/`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 35

`export function normalizeSubmissionResponse(response) {`

Imports or exposes a module symbol so code can be composed across frontend files.
### Line 36

`if (!response || typeof response !== "object") {`

Controls browser-side execution based on data or user/application state.
### Line 37

`throw new Error("Invalid submission response: expected JSON object");`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 38

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 39

`(blank)`

Blank line used to separate nearby statements.
### Line 40

`const activity = response.activity || {};`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 41

`const verified = response.verified_result || {};`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 42

`const evidence = response.evidence || {};`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 43

`const state = response.learner_state || {};`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 44

`const decision = response.adaptive_decision || {};`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 45

`(blank)`

Blank line used to separate nearby statements.
### Line 46

`const rawTarget = verified.target_state || "";`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 47

`const rawMostLikely = verified.most_likely_state || "";`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 48

`const rawPrediction = response.learner_response || "";`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 49

`const targetProb = typeof verified.target_probability === "number" ? verified.target_probability : 0.0;`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 50

`(blank)`

Blank line used to separate nearby statements.
### Line 51

`// Build probability distribution items for bar chart`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 52

`const probabilities = verified.probabilities || {};`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 53

`const counts = verified.counts || {};`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 54

`const allStates = Object.keys(probabilities).sort();`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 55

`(blank)`

Blank line used to separate nearby statements.
### Line 56

`const probabilityBars = allStates.map((st) => {`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 57

`const prob = probabilities[st] || 0.0;`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 58

`const count = counts[st] || 0;`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 59

`return {`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 60

`rawState: st,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 61

`stateLabel: formatStateLabel(st),`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 62

`probability: prob,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 63

`percentageStr: formatPercentage(prob),`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 64

`percentageNum: Number((prob * 100).toFixed(1)),`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 65

`count: count,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 66

`isTarget: st === rawTarget,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 67

`isMostLikely: st === rawMostLikely,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 68

`isPredicted: st === rawPrediction,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 69

`};`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 70

`});`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 71

`(blank)`

Blank line used to separate nearby statements.
### Line 72

`// Extract concept-level gap inference from M2 state`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 73

`const conceptId = evidence.concept_id || activity.concept_id || "";`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 74

`const gapInferences = state.gap_inferences || {};`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 75

`const conceptInference = gapInferences[conceptId] || {`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 76

`confidence: 0.0,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 77

`status: "unassessed",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 78

`description: "No inference recorded.",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 79

`};`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 80

`(blank)`

Blank line used to separate nearby statements.
### Line 81

`return {`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 82

`activity: {`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 83

`activityId: activity.activity_id || "",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 84

`title: activity.title || "Quantum Activity",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 85

`conceptId: conceptId,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 86

`taskType: activity.task_type || "quantum_prediction",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 87

`},`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 88

`learner: {`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 89

`predictionRaw: rawPrediction,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 90

`predictionLabel: formatStateLabel(rawPrediction),`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 91

`isCorrect: Boolean(evidence.is_correct),`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 92

`outcomeText: evidence.is_correct ? "Prediction Correct" : "Prediction Mismatch",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 93

`outcomeClass: evidence.is_correct ? "success" : "mismatch",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 94

`attemptNumber: evidence.attempt_number || 1,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 95

`},`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 96

`quantum: {`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 97

`algorithm: verified.algorithm || "Grover's Algorithm",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 98

`targetState: rawTarget,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 99

`targetStateLabel: formatStateLabel(rawTarget),`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 100

`mostLikelyState: rawMostLikely,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 101

`mostLikelyStateLabel: formatStateLabel(rawMostLikely),`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 102

`targetProbability: targetProb,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 103

`targetProbabilityStr: formatPercentage(targetProb),`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 104

`shots: verified.shots || 1024,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 105

`counts: counts,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 106

`probabilities: probabilities,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 107

`probabilityBars: probabilityBars,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 108

`circuit: {`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 109

`numQubits: verified.circuit?.num_qubits || 2,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 110

`numClbits: verified.circuit?.num_clbits || 2,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 111

`depth: verified.circuit?.depth || 0,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 112

`gateCounts: verified.circuit?.gate_counts || {},`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 113

`diagram: verified.circuit?.diagram || "",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 114

`},`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 115

`},`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 116

`adaptive: {`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 117

`action: decision.action || "reinforce_current_concept",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 118

`reason: decision.reason || "Continuing current activity.",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 119

`targetActivity: decision.target || null,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 120

`conceptId: decision.concept_id || conceptId,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 121

`gapConfidence: conceptInference.confidence || 0.0,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 122

`gapStatus: conceptInference.status || "observing",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 123

`gapDescription: conceptInference.description || "",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 124

`totalEvidenceCount: (state.evidence_history || []).length,`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 125

`},`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 126

`};`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 127

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.

## Nearby Files

[frontend/visualization/api_client.js](api_client.js.md), [frontend/visualization/index.html](index.html.md)
