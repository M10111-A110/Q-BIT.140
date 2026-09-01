/**
 * Q-BIT.140 — Frontend Presentation Adapter
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
 * into a structured presentation model for M1/M6 UI widgets.
 * @param {Object} response M4 API SubmissionResponse object
 * @returns {Object} Normalized visualization and learner model
 */
export function normalizeSubmissionResponse(response) {
    if (!response || typeof response !== "object") {
        throw new Error("Invalid submission response: expected JSON object");
    }

    const activity = response.activity || {};
    const verified = response.verified_result || null;
    const evidence = response.evidence || {};
    const state = response.learner_state || {};
    const decision = response.adaptive_decision || {};

    const rawPrediction = response.learner_response || "";
    const isCorrect = Boolean(evidence.is_correct);

    // Extract concept-level gap inference & trend from M2 state
    const conceptId = evidence.concept_id || activity.concept_id || "";
    const gapInferences = state.gap_inferences || {};
    const conceptInference = gapInferences[conceptId] || {
        confidence: 0.0,
        status: "unassessed",
        trend: "unassessed",
        prerequisite_concept_id: null,
        description: "No inference recorded.",
    };

    let quantumModel = null;
    if (verified) {
        const rawTarget = verified.target_state || "";
        const rawMostLikely = verified.most_likely_state || "";
        const targetProb = typeof verified.target_probability === "number" ? verified.target_probability : 0.0;
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

        quantumModel = {
            algorithm: verified.algorithm || "Quantum Algorithm",
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
        };
    }

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
            isCorrect: isCorrect,
            outcomeText: isCorrect ? "Prediction Correct" : "Prediction Mismatch",
            outcomeClass: isCorrect ? "success" : "mismatch",
            attemptNumber: evidence.attempt_number || 1,
            evaluationDetails: evidence.evaluation_details || {},
        },
        quantum: quantumModel,
        adaptive: {
            action: decision.action || "reinforce_current_concept",
            reason: decision.reason || "Continuing current activity.",
            targetActivity: decision.target || null,
            conceptId: decision.concept_id || conceptId,
            gapConfidence: conceptInference.confidence || 0.0,
            gapStatus: conceptInference.status || "observing",
            gapTrend: conceptInference.trend || "unassessed",
            prerequisiteGap: conceptInference.prerequisite_concept_id || null,
            gapDescription: conceptInference.description || "",
            totalEvidenceCount: (state.evidence_history || []).length,
        },
        learnerState: {
            conceptScores: state.concept_scores || {},
            attempts: state.attempts || {},
            errors: state.errors || {},
        },
    };
}
