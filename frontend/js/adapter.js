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
 * Format raw evidence sufficiency enum to learner/judge-readable presentation label.
 * @param {string} suff
 * @returns {string}
 */
export function formatSufficiencyLabel(suff) {
    switch (suff) {
        case "sufficient_for_targeted_inference":
            return "Sufficient for Targeted Inference";
        case "sufficient_for_improvement_observation":
            return "Sufficient for Improvement Observation";
        case "sufficient_for_mastery":
            return "Sufficient for Stable Mastery";
        case "sufficient_for_observation":
            return "Sufficient for Initial Observation";
        case "insufficient":
        default:
            return "Insufficient (Gathering Observations)";
    }
}

/**
 * Format decision trigger key to learner-readable description.
 * @param {string} trigger
 * @returns {string}
 */
export function formatTriggerLabel(trigger) {
    switch (trigger) {
        case "single_prediction_mismatch":
            return "Single Prediction Mismatch";
        case "repeated_prediction_error":
            return "Repeated Prediction Errors";
        case "prerequisite_bottleneck_error":
            return "Prerequisite Bottleneck Detected";
        case "post_intervention_recovery":
            return "Post-Intervention Recovery & Improvement";
        case "consecutive_mastery_success":
            return "Consecutive Successful Predictions";
        case "correct_prediction_advancement":
            return "Correct Prediction Demonstration";
        case "prerequisite_mastery_check":
            return "Prerequisite Mastery Incomplete";
        default:
            return String(trigger || "Default Routing").replace(/_/g, " ");
    }
}

/**
 * Format M2 learner-state hypothesis into clean human description.
 * @param {string} hypothesis
 * @returns {string}
 */
export function formatHypothesisLabel(hypothesis) {
    if (!hypothesis || hypothesis === "unassessed") return "Unassessed Baseline";
    if (hypothesis.startsWith("possible_") && hypothesis.endsWith("_difficulty")) {
        const topic = hypothesis.replace(/^possible_/, "").replace(/_difficulty$/, "").replace(/_/g, " ");
        return `Possible difficulty with ${topic}`;
    }
    if (hypothesis.startsWith("preliminary_difficulty_observation_in_")) {
        const topic = hypothesis.replace(/^preliminary_difficulty_observation_in_/, "").replace(/_/g, " ");
        return `Preliminary difficulty observation in ${topic}`;
    }
    if (hypothesis.startsWith("post_intervention_improvement_in_")) {
        const topic = hypothesis.replace(/^post_intervention_improvement_in_/, "").replace(/_/g, " ");
        return `Post-intervention improvement in ${topic}`;
    }
    if (hypothesis.startsWith("consistent_mastery_in_")) {
        const topic = hypothesis.replace(/^consistent_mastery_in_/, "").replace(/_/g, " ");
        return `Consistent mastery in ${topic}`;
    }
    if (hypothesis.startsWith("demonstrated_understanding_in_")) {
        const topic = hypothesis.replace(/^demonstrated_understanding_in_/, "").replace(/_/g, " ");
        return `Demonstrated understanding in ${topic}`;
    }
    return String(hypothesis).replace(/_/g, " ");
}

/**
 * Format adaptive action key to clear action label.
 * @param {string} action
 * @returns {string}
 */
export function formatActionLabel(action) {
    switch (action) {
        case "targeted_remediation":
            return "Targeted Remediation";
        case "gather_evidence":
            return "Gather Additional Evidence";
        case "advance":
            return "Advance to Next Activity";
        case "recommend_prerequisite":
            return "Review Prerequisite Concept";
        case "recommend_targeted_review":
            return "Focused Concept Review";
        case "reinforce_current_concept":
        default:
            return "Reinforce Current Concept";
    }
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
        hypothesis: "unassessed",
        supporting_evidence_ids: [],
        evidence_sufficiency: "insufficient",
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

    const rawSufficiency = decision.evidence_sufficiency || conceptInference.evidence_sufficiency || "insufficient";
    const rawTrigger = decision.trigger || "default_routing";
    const rawHypothesis = conceptInference.hypothesis || "unassessed";
    const rawAction = decision.action || "reinforce_current_concept";

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
            evidenceId: evidence.evidence_id || "",
            evidenceType: evidence.evidence_type || "derived_evaluation",
            evidenceSource: evidence.evidence_source || "learner",
            evaluationDetails: evidence.evaluation_details || {},
        },
        quantum: quantumModel,
        adaptive: {
            decisionId: decision.decision_id || "",
            action: rawAction,
            actionLabel: formatActionLabel(rawAction),
            reason: decision.reason || "Continuing current activity.",
            targetActivity: decision.target || null,
            conceptId: decision.concept_id || conceptId,
            gapConfidence: typeof decision.confidence === "number" ? decision.confidence : (conceptInference.confidence || 0.0),
            gapStatus: conceptInference.status || "observing",
            gapTrend: conceptInference.trend || "unassessed",
            hypothesis: rawHypothesis,
            hypothesisLabel: formatHypothesisLabel(rawHypothesis),
            evidenceSufficiency: rawSufficiency,
            evidenceSufficiencyLabel: formatSufficiencyLabel(rawSufficiency),
            supportingEvidenceIds: decision.supporting_evidence_ids || conceptInference.supporting_evidence_ids || [],
            trigger: rawTrigger,
            triggerLabel: formatTriggerLabel(rawTrigger),
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
