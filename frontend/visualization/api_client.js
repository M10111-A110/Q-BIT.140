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
