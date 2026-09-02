# Explanation: `frontend/visualization/api_client.js`

## Purpose

This page explains the meaningful behavior in `frontend/visualization/api_client.js`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```javascript
/**
 * Q-BIT.140 — Frontend API Client for M4 Backend Gateway
 * Connects M1/M6 frontend interfaces to real FastAPI backend endpoints.
 * Never stores or transmits Supabase credentials.
 */

const API_BASE = window.QBIT_API_BASE || "http://localhost:8000/api";

/**
 * Fetch list of all registered activities.
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
 * Submit a learner prediction or response to an activity.
 * Triggers real M3 Aer simulation, M2 evidence accumulation, and returns adaptive recommendation.
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
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || `Submission failed with HTTP ${res.status}`);
    }
    return await res.json();
}

/**
 * Request a grounded AI explanation from M5 for a completed experiment attempt.
 * @param {Object} submitData The complete response object returned by submitPrediction
 * @param {string|null} userQuestion Optional learner inquiry
 * @returns {Promise<Object>}
 */
export async function explainExperiment(submitData, userQuestion = null) {
    const payload = {
        learner_response: submitData.learner_response,
        verified_result: submitData.verified_result,
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
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || `Explanation request failed with HTTP ${res.status}`);
    }
    return await res.json();
}

```

## Line Notes

### Line 1

`/**`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 2

`* Q-BIT.140 — Frontend API Client for M4 Backend Gateway`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 3

`* Connects M1/M6 frontend interfaces to real FastAPI backend endpoints.`

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

`const API_BASE = window.QBIT_API_BASE || "http://localhost:8000/api";`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 8

`(blank)`

Blank line used to separate nearby statements.
### Line 9

`/**`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 10

`* Fetch list of all registered activities.`

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

`* Submit a learner prediction or response to an activity.`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 36

`* Triggers real M3 Aer simulation, M2 evidence accumulation, and returns adaptive recommendation.`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 37

`* @param {string} activityId`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 38

`* @param {string} learnerId`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 39

`* @param {string} response`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 40

`* @returns {Promise<Object>}`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 41

`*/`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 42

`export async function submitPrediction(activityId, learnerId, response) {`

Imports or exposes a module symbol so code can be composed across frontend files.
### Line 43

`const res = await fetch(\`${API_BASE}/activity/${encodeURIComponent(activityId)}/submit\`, {`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 44

`method: "POST",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 45

`headers: { "Content-Type": "application/json" },`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 46

`body: JSON.stringify({`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 47

`learner_id: learnerId,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 48

`response: String(response).trim(),`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 49

`}),`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 50

`});`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 51

`if (!res.ok) {`

Controls browser-side execution based on data or user/application state.
### Line 52

`const errorData = await res.json().catch(() => ({}));`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 53

`throw new Error(errorData.detail || \`Submission failed with HTTP ${res.status}\`);`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 54

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 55

`return await res.json();`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 56

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 57

`(blank)`

Blank line used to separate nearby statements.
### Line 58

`/**`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 59

`* Request a grounded AI explanation from M5 for a completed experiment attempt.`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 60

`* @param {Object} submitData The complete response object returned by submitPrediction`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 61

`* @param {string|null} userQuestion Optional learner inquiry`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 62

`* @returns {Promise<Object>}`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 63

`*/`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 64

`export async function explainExperiment(submitData, userQuestion = null) {`

Imports or exposes a module symbol so code can be composed across frontend files.
### Line 65

`const payload = {`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 66

`learner_response: submitData.learner_response,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 67

`verified_result: submitData.verified_result,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 68

`evidence: submitData.evidence,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 69

`adaptive_decision: submitData.adaptive_decision,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 70

`user_question: userQuestion || null,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 71

`};`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 72

`(blank)`

Blank line used to separate nearby statements.
### Line 73

`const res = await fetch(\`${API_BASE}/ai/explain_experiment\`, {`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 74

`method: "POST",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 75

`headers: { "Content-Type": "application/json" },`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 76

`body: JSON.stringify(payload),`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 77

`});`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 78

`if (!res.ok) {`

Controls browser-side execution based on data or user/application state.
### Line 79

`const errorData = await res.json().catch(() => ({}));`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 80

`throw new Error(errorData.detail || \`Explanation request failed with HTTP ${res.status}\`);`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 81

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 82

`return await res.json();`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 83

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.

## Nearby Files

[frontend/visualization/adapter.js](adapter.js.md), [frontend/visualization/index.html](index.html.md)
