/**
 * Q-BIT.140 — Frontend API Client for FastAPI Gateway (M4)
 * Authoritative HTTP communication layer connecting M1/M6 to FastAPI endpoints.
 * Never stores or transmits Supabase credentials.
 */

const API_BASE = window.QBIT_API_BASE || (
    typeof window !== "undefined" && window.location && window.location.port && window.location.port !== "8000" && window.location.protocol.startsWith("http")
        ? `${window.location.protocol}//${window.location.hostname}:8000/api`
        : "/api"
);

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

/**
 * Fetch questions for the Quick Quantum Readiness Check.
 * @returns {Promise<Object>}
 */
export async function fetchDiagnosticReadiness() {
    const res = await fetch(`${API_BASE}/diagnostic/readiness_check`);
    if (!res.ok) {
        throw new Error(`Failed to fetch diagnostic questions: HTTP ${res.status}`);
    }
    return await res.json();
}

/**
 * Submit answers to the Quick Quantum Readiness Check.
 * Ingests evidence into M2 and persists updated state.
 * @param {string} learnerId
 * @param {Object} answers { [questionId]: chosenOptionLetter }
 * @returns {Promise<Object>}
 */
export async function submitDiagnosticAnswers(learnerId, answers) {
    const res = await fetch(`${API_BASE}/diagnostic/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            learner_id: learnerId,
            answers: answers,
        }),
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Diagnostic submission failed: HTTP ${res.status}`);
    }
    return await res.json();
}

/**
 * Fetch authoritative persistent learner state and evidence history.
 * @param {string} learnerId
 * @returns {Promise<Object>}
 */
export async function fetchLearnerState(learnerId) {
    const res = await fetch(`${API_BASE}/learner/${encodeURIComponent(learnerId)}/state`);
    if (!res.ok) {
        throw new Error(`Failed to fetch learner state: HTTP ${res.status}`);
    }
    return await res.json();
}
