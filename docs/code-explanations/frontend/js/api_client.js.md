# Explanation: `frontend/js/api_client.js`

## Purpose

This page explains the meaningful behavior in `frontend/js/api_client.js`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```javascript
/**
 * Q-BIT.140 — Frontend API Client for FastAPI Gateway (M4)
 * Authoritative HTTP communication layer connecting M1/M6 to FastAPI endpoints.
 * Never stores or transmits Supabase credentials.
 */

const API_BASE = window.QBIT_API_BASE || "/api";

/**
 * Fetch all registered activities in curriculum order.
 * @returns {Promise<Array>}
 */
export async function fetchActivities() {
    const res = await fetch(`${API_BASE}/activities`);
    if (!res.ok) {
        throw new Error(`Failed to fetch activities: HTTP ${res.status}`);
    }
    return await res.json();
}

/**
 * Fetch detailed specification for a single activity.
 * @param {string} activityId 
 * @returns {Promise<Object>}
 */
export async function fetchActivity(activityId) {
    const res = await fetch(`${API_BASE}/activity/${encodeURIComponent(activityId)}`);
    if (!res.ok) {
        throw new Error(`Activity '${activityId}' not found: HTTP ${res.status}`);
    }
    return await res.json();
}

/**
 * Submit learner prediction (for quantum experiment) or option letter (for MCQ task).
 * Triggers authoritative M3 execution (if experiment defined), M2 evidence derivation,
 * trajectory tracking, and adaptive decision generation.
 * @param {string} activityId 
 * @param {string} learnerId 
 * @param {string} response 
 * @returns {Promise<Object>}
 */
export async function submitPrediction(activityId, learnerId, response) {
    const res = await fetch(`${API_BASE}/activity/${encodeURIComponent(activityId)}/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            learner_id: learnerId,
            response: String(response).trim(),
        }),
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Submission failed: HTTP ${res.status}`);
    }
    return await res.json();
}

/**
 * Request a grounded AI explanation from M5 for a completed experiment/task attempt.
 * @param {Object} submitData The complete response object returned by submitPrediction
 * @param {string|null} userQuestion Optional learner inquiry
 * @returns {Promise<Object>}
 */
export async function explainExperiment(submitData, userQuestion = null) {
    const payload = {
        learner_response: submitData.learner_response,
        verified_result: submitData.verified_result || null,
        evidence: submitData.evidence,
        adaptive_decision: submitData.adaptive_decision,
        user_question: userQuestion || null,
    };

    const res = await fetch(`${API_BASE}/ai/explain_experiment`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Explanation request failed: HTTP ${res.status}`);
    }
    return await res.json();
}

/**
 * Ask a conceptual quantum question grounded in the curated knowledge base.
 * @param {string} question 
 * @param {string|null} conceptId 
 * @param {Object|null} learnerContext 
 * @returns {Promise<Object>}
 */
export async function askConceptualQuestion(question, conceptId = null, learnerContext = null) {
    const payload = {
        question: question,
        concept_id: conceptId || null,
        learner_context: learnerContext || null,
    };

    const res = await fetch(`${API_BASE}/ai/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Question request failed: HTTP ${res.status}`);
    }
    return await res.json();
}

```

## Line Notes

### Line 1

`/**`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 2

`* Q-BIT.140 — Frontend API Client for FastAPI Gateway (M4)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 3

`* Authoritative HTTP communication layer connecting M1/M6 to FastAPI endpoints.`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 4

`* Never stores or transmits Supabase credentials.`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 5

`*/`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 6

`(blank)`

Blank line used to separate nearby statements.
### Line 7

`const API_BASE = window.QBIT_API_BASE || "/api";`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 8

`(blank)`

Blank line used to separate nearby statements.
### Line 9

`/**`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 10

`* Fetch all registered activities in curriculum order.`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 11

`* @returns {Promise<Array>}`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 12

`*/`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 13

`export async function fetchActivities() {`

Imports or exposes a module symbol so code can be composed across frontend files.
### Line 14

`const res = await fetch(\`${API_BASE}/activities\`);`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 15

`if (!res.ok) {`

Controls browser-side execution based on data or user/application state.
### Line 16

`throw new Error(\`Failed to fetch activities: HTTP ${res.status}\`);`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 17

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 18

`return await res.json();`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 19

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 20

`(blank)`

Blank line used to separate nearby statements.
### Line 21

`/**`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 22

`* Fetch detailed specification for a single activity.`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 23

`* @param {string} activityId`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 24

`* @returns {Promise<Object>}`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 25

`*/`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 26

`export async function fetchActivity(activityId) {`

Imports or exposes a module symbol so code can be composed across frontend files.
### Line 27

`const res = await fetch(\`${API_BASE}/activity/${encodeURIComponent(activityId)}\`);`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 28

`if (!res.ok) {`

Controls browser-side execution based on data or user/application state.
### Line 29

`throw new Error(\`Activity '${activityId}' not found: HTTP ${res.status}\`);`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 30

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 31

`return await res.json();`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 32

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 33

`(blank)`

Blank line used to separate nearby statements.
### Line 34

`/**`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 35

`* Submit learner prediction (for quantum experiment) or option letter (for MCQ task).`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 36

`* Triggers authoritative M3 execution (if experiment defined), M2 evidence derivation,`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 37

`* trajectory tracking, and adaptive decision generation.`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 38

`* @param {string} activityId`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 39

`* @param {string} learnerId`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 40

`* @param {string} response`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 41

`* @returns {Promise<Object>}`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 42

`*/`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 43

`export async function submitPrediction(activityId, learnerId, response) {`

Imports or exposes a module symbol so code can be composed across frontend files.
### Line 44

`const res = await fetch(\`${API_BASE}/activity/${encodeURIComponent(activityId)}/submit\`, {`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 45

`method: "POST",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 46

`headers: { "Content-Type": "application/json" },`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 47

`body: JSON.stringify({`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 48

`learner_id: learnerId,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 49

`response: String(response).trim(),`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 50

`}),`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 51

`});`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 52

`if (!res.ok) {`

Controls browser-side execution based on data or user/application state.
### Line 53

`const err = await res.json().catch(() => ({}));`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 54

`throw new Error(err.detail || \`Submission failed: HTTP ${res.status}\`);`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 55

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 56

`return await res.json();`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 57

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 58

`(blank)`

Blank line used to separate nearby statements.
### Line 59

`/**`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 60

`* Request a grounded AI explanation from M5 for a completed experiment/task attempt.`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 61

`* @param {Object} submitData The complete response object returned by submitPrediction`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 62

`* @param {string|null} userQuestion Optional learner inquiry`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 63

`* @returns {Promise<Object>}`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 64

`*/`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 65

`export async function explainExperiment(submitData, userQuestion = null) {`

Imports or exposes a module symbol so code can be composed across frontend files.
### Line 66

`const payload = {`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 67

`learner_response: submitData.learner_response,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 68

`verified_result: submitData.verified_result || null,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 69

`evidence: submitData.evidence,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 70

`adaptive_decision: submitData.adaptive_decision,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 71

`user_question: userQuestion || null,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 72

`};`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 73

`(blank)`

Blank line used to separate nearby statements.
### Line 74

`const res = await fetch(\`${API_BASE}/ai/explain_experiment\`, {`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 75

`method: "POST",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 76

`headers: { "Content-Type": "application/json" },`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 77

`body: JSON.stringify(payload),`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 78

`});`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 79

`if (!res.ok) {`

Controls browser-side execution based on data or user/application state.
### Line 80

`const err = await res.json().catch(() => ({}));`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 81

`throw new Error(err.detail || \`Explanation request failed: HTTP ${res.status}\`);`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 82

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 83

`return await res.json();`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 84

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 85

`(blank)`

Blank line used to separate nearby statements.
### Line 86

`/**`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 87

`* Ask a conceptual quantum question grounded in the curated knowledge base.`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 88

`* @param {string} question`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 89

`* @param {string|null} conceptId`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 90

`* @param {Object|null} learnerContext`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 91

`* @returns {Promise<Object>}`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 92

`*/`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 93

`export async function askConceptualQuestion(question, conceptId = null, learnerContext = null) {`

Imports or exposes a module symbol so code can be composed across frontend files.
### Line 94

`const payload = {`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 95

`question: question,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 96

`concept_id: conceptId || null,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 97

`learner_context: learnerContext || null,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 98

`};`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 99

`(blank)`

Blank line used to separate nearby statements.
### Line 100

`const res = await fetch(\`${API_BASE}/ai/ask\`, {`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 101

`method: "POST",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 102

`headers: { "Content-Type": "application/json" },`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 103

`body: JSON.stringify(payload),`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 104

`});`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 105

`if (!res.ok) {`

Controls browser-side execution based on data or user/application state.
### Line 106

`const err = await res.json().catch(() => ({}));`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 107

`throw new Error(err.detail || \`Question request failed: HTTP ${res.status}\`);`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 108

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 109

`return await res.json();`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 110

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.

## Nearby Files

[frontend/js/adapter.js](adapter.js.md), [frontend/js/circuit_view.js](circuit_view.js.md)
