# Explanation: `frontend/js/adapter.js`

## Purpose

This page explains the meaningful behavior in `frontend/js/adapter.js`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```javascript
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
    const avgMastery = conceptVals.length > 0 ? (conceptVals.reduce((a, b) => a + Number(b), 0) / conceptVals.length) : 0.5;
    const points = Math.round(avgMastery * 500 + completedCount * 125);
    const masteryPct = Math.round(avgMastery * 100);
    const streak = Math.max(1, completedCount);

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

```

## Line Notes

### Line 1

`/**`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 2

`* Q-BIT.140 — Frontend Presentation Adapter`

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

`* Format raw evidence sufficiency enum to learner/judge-readable presentation label.`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 31

`* @param {string} suff`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 32

`* @returns {string}`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 33

`*/`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 34

`export function formatSufficiencyLabel(suff) {`

Imports or exposes a module symbol so code can be composed across frontend files.
### Line 35

`switch (suff) {`

Controls browser-side execution based on data or user/application state.
### Line 36

`case "sufficient_for_targeted_inference":`

Controls browser-side execution based on data or user/application state.
### Line 37

`return "Sufficient for Targeted Inference";`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 38

`case "sufficient_for_improvement_observation":`

Controls browser-side execution based on data or user/application state.
### Line 39

`return "Sufficient for Improvement Observation";`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 40

`case "sufficient_for_mastery":`

Controls browser-side execution based on data or user/application state.
### Line 41

`return "Sufficient for Stable Mastery";`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 42

`case "sufficient_for_observation":`

Controls browser-side execution based on data or user/application state.
### Line 43

`return "Sufficient for Initial Observation";`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 44

`case "insufficient":`

Controls browser-side execution based on data or user/application state.
### Line 45

`default:`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 46

`return "Insufficient (Gathering Observations)";`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 47

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 48

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 49

`(blank)`

Blank line used to separate nearby statements.
### Line 50

`/**`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 51

`* Format decision trigger key to learner-readable description.`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 52

`* @param {string} trigger`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 53

`* @returns {string}`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 54

`*/`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 55

`export function formatTriggerLabel(trigger) {`

Imports or exposes a module symbol so code can be composed across frontend files.
### Line 56

`switch (trigger) {`

Controls browser-side execution based on data or user/application state.
### Line 57

`case "single_prediction_mismatch":`

Controls browser-side execution based on data or user/application state.
### Line 58

`return "Single Prediction Mismatch";`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 59

`case "repeated_prediction_error":`

Controls browser-side execution based on data or user/application state.
### Line 60

`return "Repeated Prediction Errors";`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 61

`case "prerequisite_bottleneck_error":`

Controls browser-side execution based on data or user/application state.
### Line 62

`return "Prerequisite Bottleneck Detected";`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 63

`case "post_intervention_recovery":`

Controls browser-side execution based on data or user/application state.
### Line 64

`return "Post-Intervention Recovery & Improvement";`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 65

`case "consecutive_mastery_success":`

Controls browser-side execution based on data or user/application state.
### Line 66

`return "Consecutive Successful Predictions";`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 67

`case "correct_prediction_advancement":`

Controls browser-side execution based on data or user/application state.
### Line 68

`return "Correct Prediction Demonstration";`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 69

`case "prerequisite_mastery_check":`

Controls browser-side execution based on data or user/application state.
### Line 70

`return "Prerequisite Mastery Incomplete";`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 71

`default:`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 72

`return String(trigger || "Default Routing").replace(/_/g, " ");`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 73

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 74

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 75

`(blank)`

Blank line used to separate nearby statements.
### Line 76

`/**`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 77

`* Format M2 learner-state hypothesis into clean human description.`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 78

`* @param {string} hypothesis`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 79

`* @returns {string}`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 80

`*/`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 81

`export function formatHypothesisLabel(hypothesis) {`

Imports or exposes a module symbol so code can be composed across frontend files.
### Line 82

`if (!hypothesis || hypothesis === "unassessed") return "Unassessed Baseline";`

Controls browser-side execution based on data or user/application state.
### Line 83

`if (hypothesis.startsWith("possible_") && hypothesis.endsWith("_difficulty")) {`

Controls browser-side execution based on data or user/application state.
### Line 84

`const topic = hypothesis.replace(/^possible_/, "").replace(/_difficulty$/, "").replace(/_/g, " ");`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 85

`return \`Possible difficulty with ${topic}\`;`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 86

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 87

`if (hypothesis.startsWith("preliminary_difficulty_observation_in_")) {`

Controls browser-side execution based on data or user/application state.
### Line 88

`const topic = hypothesis.replace(/^preliminary_difficulty_observation_in_/, "").replace(/_/g, " ");`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 89

`return \`Preliminary difficulty observation in ${topic}\`;`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 90

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 91

`if (hypothesis.startsWith("post_intervention_improvement_in_")) {`

Controls browser-side execution based on data or user/application state.
### Line 92

`const topic = hypothesis.replace(/^post_intervention_improvement_in_/, "").replace(/_/g, " ");`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 93

`return \`Post-intervention improvement in ${topic}\`;`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 94

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 95

`if (hypothesis.startsWith("consistent_mastery_in_")) {`

Controls browser-side execution based on data or user/application state.
### Line 96

`const topic = hypothesis.replace(/^consistent_mastery_in_/, "").replace(/_/g, " ");`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 97

`return \`Consistent mastery in ${topic}\`;`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 98

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 99

`if (hypothesis.startsWith("demonstrated_understanding_in_")) {`

Controls browser-side execution based on data or user/application state.
### Line 100

`const topic = hypothesis.replace(/^demonstrated_understanding_in_/, "").replace(/_/g, " ");`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 101

`return \`Demonstrated understanding in ${topic}\`;`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 102

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 103

`return String(hypothesis).replace(/_/g, " ");`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 104

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 105

`(blank)`

Blank line used to separate nearby statements.
### Line 106

`/**`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 107

`* Format adaptive action key to clear action label.`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 108

`* @param {string} action`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 109

`* @returns {string}`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 110

`*/`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 111

`export function formatActionLabel(action) {`

Imports or exposes a module symbol so code can be composed across frontend files.
### Line 112

`switch (action) {`

Controls browser-side execution based on data or user/application state.
### Line 113

`case "targeted_remediation":`

Controls browser-side execution based on data or user/application state.
### Line 114

`return "Targeted Remediation";`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 115

`case "gather_evidence":`

Controls browser-side execution based on data or user/application state.
### Line 116

`return "Gather Additional Evidence";`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 117

`case "advance":`

Controls browser-side execution based on data or user/application state.
### Line 118

`return "Advance to Next Activity";`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 119

`case "recommend_prerequisite":`

Controls browser-side execution based on data or user/application state.
### Line 120

`return "Review Prerequisite Concept";`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 121

`case "recommend_targeted_review":`

Controls browser-side execution based on data or user/application state.
### Line 122

`return "Focused Concept Review";`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 123

`case "reinforce_current_concept":`

Controls browser-side execution based on data or user/application state.
### Line 124

`default:`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 125

`return "Reinforce Current Concept";`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 126

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 127

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 128

`(blank)`

Blank line used to separate nearby statements.
### Line 129

`/**`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 130

`* Normalize the raw JSON response from POST /api/activity/{id}/submit`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 131

`* into a structured presentation model for M1/M6 UI widgets.`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 132

`* @param {Object} response M4 API SubmissionResponse object`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 133

`* @returns {Object} Normalized visualization and learner model`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 134

`*/`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 135

`export function normalizeSubmissionResponse(response) {`

Imports or exposes a module symbol so code can be composed across frontend files.
### Line 136

`if (!response || typeof response !== "object") {`

Controls browser-side execution based on data or user/application state.
### Line 137

`throw new Error("Invalid submission response: expected JSON object");`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 138

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 139

`(blank)`

Blank line used to separate nearby statements.
### Line 140

`const activity = response.activity || {};`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 141

`const verified = response.verified_result || null;`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 142

`const evidence = response.evidence || {};`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 143

`const state = response.learner_state || {};`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 144

`const decision = response.adaptive_decision || {};`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 145

`(blank)`

Blank line used to separate nearby statements.
### Line 146

`const rawPrediction = response.learner_response || "";`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 147

`const isCorrect = Boolean(evidence.is_correct);`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 148

`(blank)`

Blank line used to separate nearby statements.
### Line 149

`// Extract concept-level gap inference & trend from M2 state`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 150

`const conceptId = evidence.concept_id || activity.concept_id || "";`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 151

`const gapInferences = state.gap_inferences || {};`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 152

`const conceptInference = gapInferences[conceptId] || {`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 153

`confidence: 0.0,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 154

`status: "unassessed",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 155

`trend: "unassessed",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 156

`hypothesis: "unassessed",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 157

`supporting_evidence_ids: [],`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 158

`evidence_sufficiency: "insufficient",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 159

`prerequisite_concept_id: null,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 160

`description: "No inference recorded.",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 161

`};`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 162

`(blank)`

Blank line used to separate nearby statements.
### Line 163

`let quantumModel = null;`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 164

`if (verified) {`

Controls browser-side execution based on data or user/application state.
### Line 165

`const rawTarget = verified.target_state || "";`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 166

`const rawMostLikely = verified.most_likely_state || "";`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 167

`const targetProb = typeof verified.target_probability === "number" ? verified.target_probability : 0.0;`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 168

`const probabilities = verified.probabilities || {};`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 169

`const counts = verified.counts || {};`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 170

`const allStates = Object.keys(probabilities).sort();`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 171

`(blank)`

Blank line used to separate nearby statements.
### Line 172

`const probabilityBars = allStates.map((st) => {`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 173

`const prob = probabilities[st] || 0.0;`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 174

`const count = counts[st] || 0;`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 175

`return {`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 176

`rawState: st,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 177

`stateLabel: formatStateLabel(st),`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 178

`probability: prob,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 179

`percentageStr: formatPercentage(prob),`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 180

`percentageNum: Number((prob * 100).toFixed(1)),`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 181

`count: count,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 182

`isTarget: st === rawTarget,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 183

`isMostLikely: st === rawMostLikely,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 184

`isPredicted: st === rawPrediction,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 185

`};`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 186

`});`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 187

`(blank)`

Blank line used to separate nearby statements.
### Line 188

`quantumModel = {`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 189

`algorithm: verified.algorithm || "Quantum Algorithm",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 190

`targetState: rawTarget,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 191

`targetStateLabel: formatStateLabel(rawTarget),`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 192

`mostLikelyState: rawMostLikely,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 193

`mostLikelyStateLabel: formatStateLabel(rawMostLikely),`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 194

`targetProbability: targetProb,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 195

`targetProbabilityStr: formatPercentage(targetProb),`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 196

`shots: verified.shots || 1024,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 197

`counts: counts,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 198

`probabilities: probabilities,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 199

`probabilityBars: probabilityBars,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 200

`circuit: {`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 201

`numQubits: verified.circuit?.num_qubits || 2,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 202

`numClbits: verified.circuit?.num_clbits || 2,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 203

`depth: verified.circuit?.depth || 0,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 204

`gateCounts: verified.circuit?.gate_counts || {},`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 205

`diagram: verified.circuit?.diagram || "",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 206

`},`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 207

`};`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 208

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 209

`(blank)`

Blank line used to separate nearby statements.
### Line 210

`const rawSufficiency = decision.evidence_sufficiency || conceptInference.evidence_sufficiency || "insufficient";`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 211

`const rawTrigger = decision.trigger || "default_routing";`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 212

`const rawHypothesis = conceptInference.hypothesis || "unassessed";`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 213

`const rawAction = decision.action || "reinforce_current_concept";`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 214

`(blank)`

Blank line used to separate nearby statements.
### Line 215

`return {`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 216

`activity: {`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 217

`activityId: activity.activity_id || "",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 218

`title: activity.title || "Quantum Activity",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 219

`conceptId: conceptId,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 220

`taskType: activity.task_type || "quantum_prediction",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 221

`},`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 222

`learner: {`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 223

`predictionRaw: rawPrediction,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 224

`predictionLabel: formatStateLabel(rawPrediction),`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 225

`isCorrect: isCorrect,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 226

`outcomeText: isCorrect ? "Prediction Correct" : "Prediction Mismatch",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 227

`outcomeClass: isCorrect ? "success" : "mismatch",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 228

`attemptNumber: evidence.attempt_number || 1,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 229

`evidenceId: evidence.evidence_id || "",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 230

`evidenceType: evidence.evidence_type || "derived_evaluation",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 231

`evidenceSource: evidence.evidence_source || "learner",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 232

`evaluationDetails: evidence.evaluation_details || {},`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 233

`},`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 234

`quantum: quantumModel,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 235

`adaptive: {`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 236

`decisionId: decision.decision_id || "",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 237

`action: rawAction,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 238

`actionLabel: formatActionLabel(rawAction),`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 239

`reason: decision.reason || "Continuing current activity.",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 240

`targetActivity: decision.target || null,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 241

`conceptId: decision.concept_id || conceptId,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 242

`gapConfidence: typeof decision.confidence === "number" ? decision.confidence : (conceptInference.confidence || 0.0),`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 243

`gapStatus: conceptInference.status || "observing",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 244

`gapTrend: conceptInference.trend || "unassessed",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 245

`hypothesis: rawHypothesis,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 246

`hypothesisLabel: formatHypothesisLabel(rawHypothesis),`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 247

`evidenceSufficiency: rawSufficiency,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 248

`evidenceSufficiencyLabel: formatSufficiencyLabel(rawSufficiency),`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 249

`supportingEvidenceIds: decision.supporting_evidence_ids || conceptInference.supporting_evidence_ids || [],`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 250

`trigger: rawTrigger,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 251

`triggerLabel: formatTriggerLabel(rawTrigger),`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 252

`prerequisiteGap: conceptInference.prerequisite_concept_id || null,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 253

`gapDescription: conceptInference.description || "",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 254

`totalEvidenceCount: (state.evidence_history || []).length,`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 255

`},`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 256

`learnerState: {`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 257

`conceptScores: state.concept_scores || {},`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 258

`attempts: state.attempts || {},`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 259

`errors: state.errors || {},`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 260

`},`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 261

`};`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 262

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 263

`(blank)`

Blank line used to separate nearby statements.
### Line 264

`/**`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 265

`* Compute aggregate UI achievement badge metrics from authoritative M2 state.`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 266

`* @param {Object} state - Learner state dictionary`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 267

`* @param {Array} activities - List of curriculum activities`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 268

`* @returns {Object}`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 269

`*/`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 270

`export function computeBadgeMetrics(state = {}, activities = []) {`

Imports or exposes a module symbol so code can be composed across frontend files.
### Line 271

`const attempts = state.attempts || {};`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 272

`const errors = state.errors || {};`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 273

`const conceptScores = state.concept_scores || {};`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 274

`(blank)`

Blank line used to separate nearby statements.
### Line 275

`let totalAttempts = 0;`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 276

`let totalErrors = 0;`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 277

`for (const cnt of Object.values(attempts)) totalAttempts += Number(cnt) || 0;`

Controls browser-side execution based on data or user/application state.
### Line 278

`for (const cnt of Object.values(errors)) totalErrors += Number(cnt) || 0;`

Controls browser-side execution based on data or user/application state.
### Line 279

`(blank)`

Blank line used to separate nearby statements.
### Line 280

`const correctAttempts = Math.max(0, totalAttempts - totalErrors);`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 281

`const accuracyPct = totalAttempts > 0 ? Math.round((correctAttempts / totalAttempts) * 100) : 100;`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 282

`(blank)`

Blank line used to separate nearby statements.
### Line 283

`const completedCount = Object.keys(attempts).length;`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 284

`const totalCount = activities.length || 4;`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 285

`(blank)`

Blank line used to separate nearby statements.
### Line 286

`const conceptVals = Object.values(conceptScores);`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 287

`const avgMastery = conceptVals.length > 0 ? (conceptVals.reduce((a, b) => a + Number(b), 0) / conceptVals.length) : 0.5;`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 288

`const points = Math.round(avgMastery * 500 + completedCount * 125);`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 289

`const masteryPct = Math.round(avgMastery * 100);`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 290

`const streak = Math.max(1, completedCount);`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 291

`(blank)`

Blank line used to separate nearby statements.
### Line 292

`return {`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 293

`streak,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 294

`completedCount,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 295

`totalCount,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 296

`masteryPct,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 297

`points,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 298

`accuracyPct,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 299

`};`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 300

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 301

`(blank)`

Blank line used to separate nearby statements.
### Line 302

`/**`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 303

`* Load local learner profile preferences from browser localStorage.`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 304

`* @param {string} learnerId`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 305

`* @returns {Object}`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 306

`*/`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 307

`export function getLearnerProfile(learnerId = "demo_learner") {`

Imports or exposes a module symbol so code can be composed across frontend files.
### Line 308

`try {`

Controls browser-side execution based on data or user/application state.
### Line 309

`const stored = localStorage.getItem(\`qbit_profile_${learnerId}\`);`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 310

`if (stored) return JSON.parse(stored);`

Controls browser-side execution based on data or user/application state.
### Line 311

`} catch {`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 312

`// ignore localStorage access error`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 313

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 314

`return {`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 315

`name: learnerId === "demo_learner" ? "Quantum Explorer" : learnerId,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 316

`studying: "Grover's Algorithm & Quantum State Triads",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 317

`avatar: "",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 318

`theme: "dark",`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 319

`};`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 320

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 321

`(blank)`

Blank line used to separate nearby statements.
### Line 322

`/**`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 323

`* Save local learner profile preferences to browser localStorage.`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 324

`* @param {string} learnerId`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 325

`* @param {Object} profile`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 326

`*/`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 327

`export function saveLearnerProfile(learnerId = "demo_learner", profile = {}) {`

Imports or exposes a module symbol so code can be composed across frontend files.
### Line 328

`try {`

Controls browser-side execution based on data or user/application state.
### Line 329

`localStorage.setItem(\`qbit_profile_${learnerId}\`, JSON.stringify(profile));`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 330

`} catch {`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 331

`// ignore localStorage access error`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 332

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 333

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.

## Nearby Files

[frontend/js/api_client.js](api_client.js.md), [frontend/js/circuit_view.js](circuit_view.js.md)
