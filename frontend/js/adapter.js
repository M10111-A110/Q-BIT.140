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
            return "Strong enough to guide targeted practice";
        case "sufficient_for_improvement_observation":
            return "Strong enough to confirm concept improvement";
        case "sufficient_for_mastery":
            return "Strong enough to confirm stable mastery";
        case "sufficient_for_observation":
            return "Strong enough to guide the next step";
        case "insufficient":
        default:
            return "Gathering more attempts to confirm pattern";
    }
}

/**
 * Format decision trigger key to learner/judge-readable description.
 * @param {string} trigger
 * @returns {string}
 */
export function formatTriggerLabel(trigger) {
    switch (trigger) {
        case "correct_prediction_advancement":
            return "You predicted correctly, so the system is ready to increase the challenge.";
        case "consecutive_mastery_success":
            return "Consistent correct answers demonstrate mastery; advancing to the next challenge.";
        case "single_prediction_mismatch":
            return "First attempt differed from quantum measurement; gathering another observation.";
        case "repeated_prediction_error":
            return "Multiple attempts show a concept gap, so we're routing you to targeted practice.";
        case "prerequisite_bottleneck_error":
            return "Foundational prerequisite gap detected, so we're recommending prerequisite review.";
        case "post_intervention_recovery":
            return "Concept recovered after review; returning to main track.";
        case "prerequisite_mastery_check":
            return "Prerequisite check requires review before proceeding.";
        default:
            return String(trigger || "Standard adaptive evaluation").replace(/_/g, " ");
    }
}

/**
 * Format M2 learner-state hypothesis into clean, natural human description.
 * @param {string} hypothesis
 * @returns {string}
 */
export function formatHypothesisLabel(hypothesis) {
    if (!hypothesis || hypothesis === "unassessed") return "Initial baseline — completing first challenges";
    if (hypothesis.startsWith("possible_") && hypothesis.endsWith("_difficulty")) {
        const topic = hypothesis.replace(/^possible_/, "").replace(/_difficulty$/, "").replace(/_/g, " ");
        return `Reviewing foundations of ${topic}`;
    }
    if (hypothesis.startsWith("preliminary_difficulty_observation_in_")) {
        const topic = hypothesis.replace(/^preliminary_difficulty_observation_in_/, "").replace(/_/g, " ");
        return `Noticing initial questions around ${topic}`;
    }
    if (hypothesis.startsWith("post_intervention_improvement_in_")) {
        const topic = hypothesis.replace(/^post_intervention_improvement_in_/, "").replace(/_/g, " ");
        return `Showing clear improvement in ${topic}`;
    }
    if (hypothesis.startsWith("consistent_mastery_in_")) {
        const topic = hypothesis.replace(/^consistent_mastery_in_/, "").replace(/_/g, " ");
        return `Comfortable and confident in ${topic}`;
    }
    if (hypothesis.startsWith("demonstrated_understanding_in_")) {
        const topic = hypothesis.replace(/^demonstrated_understanding_in_/, "").replace(/_/g, " ");
        return `Understands core principles of ${topic}`;
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

/**
 * Compute aggregate UI achievement badge metrics from authoritative M2 state.
 * @param {Object} state - Learner state dictionary
 * @param {Array} activities - List of curriculum activities
 * @returns {Object}
 */
export function computeBadgeMetrics(state = {}, activities = []) {
    const attempts = state.attempts || {};
    const errors = state.errors || {};
    const conceptScores = state.concept_scores || {};

    let totalAttempts = 0;
    let totalErrors = 0;
    for (const cnt of Object.values(attempts)) totalAttempts += Number(cnt) || 0;
    for (const cnt of Object.values(errors)) totalErrors += Number(cnt) || 0;

    const correctAttempts = Math.max(0, totalAttempts - totalErrors);
    const accuracyPct = totalAttempts > 0 ? Math.round((correctAttempts / totalAttempts) * 100) : 100;

    const completedCount = Object.keys(attempts).length;
    const totalCount = activities.length || 4;

    const conceptVals = Object.values(conceptScores);
    const avgMastery = conceptVals.length > 0 ? (conceptVals.reduce((a, b) => a + Number(b), 0) / conceptVals.length) : 0.0;
    const points = completedCount > 0 ? Math.round(avgMastery * 500 + completedCount * 125) : 0;
    const masteryPct = Math.round(avgMastery * 100);
    const streak = completedCount > 0 ? completedCount : 0;

    return {
        streak,
        completedCount,
        totalCount,
        masteryPct,
        points,
        accuracyPct,
    };
}


/**
 * Load local learner profile preferences from browser localStorage.
 * @param {string} learnerId
 * @returns {Object}
 */
export function getLearnerProfile(learnerId = "demo_learner") {
    try {
        const stored = localStorage.getItem(`qbit_profile_${learnerId}`);
        if (stored) return JSON.parse(stored);
    } catch {
        // ignore localStorage access error
    }
    return {
        name: learnerId === "demo_learner" ? "Quantum Explorer" : learnerId,
        studying: "Grover's Algorithm & Quantum State Triads",
        avatar: "",
        theme: "dark",
    };
}

/**
 * Save local learner profile preferences to browser localStorage.
 * @param {string} learnerId
 * @param {Object} profile
 */
export function saveLearnerProfile(learnerId = "demo_learner", profile = {}) {
    try {
        localStorage.setItem(`qbit_profile_${learnerId}`, JSON.stringify(profile));
    } catch {
        // ignore localStorage access error
    }
}

/**
 * Pedagogical role classifier for curriculum activities.
 * Returns one of: "challenge" | "remediation" | "foundation" | "advancement".
 * Uses existing activity metadata without creating a parallel curriculum system.
 * @param {Object} activity
 * @returns {string}
 */
export function getActivityRole(activity) {
    if (!activity) return "challenge";
    const id = activity.activity_id || "";
    if (id === "act_grover_2q_predict") return "challenge";
    if (id === "act_measurement_prob_diagnostic") return "remediation";
    if (id === "act_superposition_remediation") return "foundation";
    if (id === "act_grover_iteration_reasoning") return "advancement";

    // Metadata-driven fallbacks
    if (activity.task_type === "quantum_prediction") return "challenge";
    if (activity.prerequisites?.includes("grover.search_problem")) return "advancement";
    if (activity.concept_id === "quantum.superposition") return "foundation";
    if (activity.concept_id === "quantum.measurement") return "remediation";
    return "challenge";
}

/**
 * Format activity pedagogical role to learner-facing label.
 * @param {string} role
 * @returns {string}
 */
export function formatRoleLabel(role) {
    switch (role) {
        case "challenge":
            return "Challenge";
        case "remediation":
            return "Remediation";
        case "foundation":
            return "Foundation";
        case "advancement":
            return "Advancement";
        default:
            return String(role || "Challenge");
    }
}

/**
 * Determine the runtime semantic state of an activity for the active learner.
 * Returns one of: "active" | "remediation_target" | "next_target" | "mastered" | "idle".
 * Priority order:
 *   1. active
 *   2. remediation_target
 *   3. next_target
 *   4. mastered
 *   5. idle
 * Uses authoritative backend state and decisions without client-side guessing.
 * @param {string} activityId
 * @param {string} currentActivityId
 * @param {Object} learnerState
 * @param {Object} adaptiveDecision
 * @returns {string}
 */
export function getActivityStatus(activityId, currentActivityId, learnerState = {}, adaptiveDecision = null) {
    // 1. Priority 1: Currently active activity
    if (activityId === currentActivityId) {
        return "active";
    }

    // 2. Priority 2: Recommended remediation target chosen by M2
    if (
        adaptiveDecision &&
        adaptiveDecision.action === "targeted_remediation" &&
        adaptiveDecision.target === activityId
    ) {
        return "remediation_target";
    }

    // 3. Priority 3: Recommended next advancement / retry target chosen by M2
    if (
        adaptiveDecision &&
        adaptiveDecision.action === "advance" &&
        adaptiveDecision.target === activityId
    ) {
        return "next_target";
    }

    // 4. Priority 4: Mastered based on authoritative evidence and state
    const evidenceHistory = learnerState.evidence_history || [];
    const hasCorrectAttempt = evidenceHistory.some(
        e => e.activity_id === activityId && Boolean(e.is_correct)
    );

    const conceptMapping = {
        "act_grover_2q_predict": "grover.search_problem",
        "act_measurement_prob_diagnostic": "quantum.measurement",
        "act_superposition_remediation": "quantum.superposition",
        "act_grover_iteration_reasoning": "grover.amplitude_amplification",
    };
    const conceptId = conceptMapping[activityId];
    const gapInf = learnerState.gap_inferences?.[conceptId];
    const isConceptMastered = gapInf && (gapInf.status === "mastered" || gapInf.status === "improving");

    // Also check concept scores if recorded
    const conceptScores = learnerState.concept_scores || {};
    const hasHighScore = Object.entries(conceptScores).some(
        ([topic, score]) => (topic === conceptId || topic.toLowerCase().includes(activityId.replace("act_", "").split("_")[0])) && Number(score) >= 0.8
    );

    if (hasCorrectAttempt || isConceptMastered || hasHighScore) {
        return "mastered";
    }

    // 5. Priority 5: Idle
    return "idle";
}

/**
 * Format activity runtime status to clear human badge text.
 * @param {string} status
 * @returns {string}
 */
export function formatStatusLabel(status) {
    switch (status) {
        case "active":
            return "Active";
        case "remediation_target":
            return "Recommended";
        case "next_target":
            return "Up Next";
        case "mastered":
            return "Mastered";
        case "idle":
        default:
            return "Idle";
    }
}
