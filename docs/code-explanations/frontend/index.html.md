# Explanation: `frontend/index.html`

## Purpose

This page explains the meaningful behavior in `frontend/index.html`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```html
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Q-BIT.140 — AI-Based Interactive Quantum Algorithm Learning Platform</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">

    <!-- KaTeX for Grounded Quantum Math Notation -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css" crossorigin="anonymous">
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js" crossorigin="anonymous"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js" crossorigin="anonymous"></script>

    <link rel="stylesheet" href="./css/styles.css">
</head>
<body>

<!-- BACKGROUND PARTICLE CANVAS (DECORATIVE QUANTUM CLOUD) -->
<canvas id="fx"></canvas>

<!-- TOP BAR -->
<header>
    <div class="header-left">
        <div class="atom" title="Q-BIT Quantum Engine">
            <svg viewBox="0 0 36 36" fill="none">
                <circle cx="18" cy="18" r="4" fill="url(#coreGlow)" />
                <ellipse class="orbit" cx="18" cy="18" rx="14" ry="5" stroke="var(--cyan)" stroke-width="1.2" opacity="0.85" transform="rotate(30 18 18)" />
                <ellipse class="orbit o2" cx="18" cy="18" rx="14" ry="5" stroke="var(--accent)" stroke-width="1.2" opacity="0.85" transform="rotate(-30 18 18)" />
                <defs>
                    <radialGradient id="coreGlow" cx="50%" cy="50%" r="50%">
                        <stop offset="0%" stop-color="#FFFFFF" />
                        <stop offset="100%" stop-color="var(--cyan)" />
                    </radialGradient>
                </defs>
            </svg>
        </div>
        <div>
            <h1 class="brand-title">Q-BIT.140</h1>
            <div class="brand-sub">Evidence-Driven Adaptive Quantum Learning Platform • SIH 2026</div>
        </div>
    </div>

    <!-- TOPBAR MASTERY BADGE -->
    <div style="display: flex; align-items: center; gap: 8px;" id="topbarBadges">
        <div class="chip" id="chipMastery" title="Concepts mastered">
            <span class="chip-icon">🏆</span>
            <span class="chip-label">Mastery</span>
            <span class="chip-val green" id="badgeMastery">1/4</span>
        </div>
    </div>

    <div class="header-right">
        <input type="hidden" id="learnerIdInput" value="">
        <button class="btn secondary" style="padding: 6px 12px; font-size: 11px;" onclick="handleResetSession()">🔄 Reset Session</button>
        <button class="btn secondary" style="padding: 6px 12px; font-size: 11px;" onclick="openAskModal()">🤖 Ask AI</button>
        <button class="profile-btn" id="profileOpenBtn" onclick="openProfileModal()" title="Learner Profile & Settings">QE</button>
    </div>
</header>

<!-- GLOBAL NOTIFICATION / ERROR BANNER -->
<div id="errorNotificationBanner" style="display: none; padding: 10px 28px; font-size: 12px; font-family: var(--font-mono); background: rgba(239, 68, 68, 0.15); border-bottom: 1px solid var(--red); color: var(--red); align-items: center; justify-content: space-between;">
    <span id="errorBannerMessage">Error message</span>
    <button style="background: none; border: none; color: var(--red); cursor: pointer; font-size: 14px;" onclick="closeErrorBanner()">✕</button>
</div>

<!-- CURRICULUM JOURNEY TRACK (REQUIREMENT 5) -->
<div class="journey-bar">
    <div class="journey-left">
        <span class="journey-title">Curriculum Path:</span>
        <div class="journey-steps" id="journeySteps">
            <!-- Dynamically rendered activity nodes -->
        </div>
    </div>
    <div class="journey-progress-badge" id="journeyProgressBadge">Step 1 of 4</div>
</div>

<!-- WORKSPACE LAYOUT -->
<div class="workspace-layout">
    <!-- LEFT PANE: Circuit Studio & M3 Simulation (M6) -->
    <div class="pane pane-left">
        <!-- Circuit Studio -->
        <div class="circuit-studio">
            <div class="card-header">
                <span class="card-title">Interactive Quantum Circuit Studio (Visual Exploration)</span>
                <span style="font-family: var(--font-mono); font-size: 12px; color: var(--text-muted);">
                    Tool: <strong id="activeToolDisplay" style="color: var(--cyan);">None</strong>
                </span>
            </div>

            <div class="gate-toolbar">
                <button class="gate-btn" onclick="selectGate('H')">H</button>
                <button class="gate-btn" onclick="selectGate('X')">X</button>
                <button class="gate-btn" onclick="selectGate('Y')">Y</button>
                <button class="gate-btn" onclick="selectGate('Z')">Z</button>
                <button class="gate-btn" onclick="selectGate('S')">S</button>
                <button class="gate-btn" onclick="selectGate('T')">T</button>
                <button class="gate-btn" onclick="selectGate('CZ')">CZ</button>
                <button class="gate-btn" onclick="selectGate('M')">M</button>
                <div style="flex: 1;"></div>
                <button class="btn secondary" style="padding: 5px 10px; font-size: 11px;" onclick="loadCircuitPreset('grover_2q')">Preset: Grover 2Q</button>
                <button class="btn secondary" style="padding: 5px 10px; font-size: 11px;" onclick="addStudioQubit()">+ Qubit</button>
                <button class="btn secondary" style="padding: 5px 10px; font-size: 11px;" onclick="clearStudioCircuit()">Clear</button>
            </div>

            <div class="wire-grid" id="circuitWireGrid"></div>

            <div class="gate-info-callout" id="gateInfoDisplay">
                <span>💡 Visual Circuit Explorer: Place gates on the grid to inspect quantum operations. Submissions execute the active activity circuit on Qiskit Aer (1024 shots).</span>
            </div>
        </div>

        <!-- M3 Verified Quantum Results (Revealed after submission) -->
        <div class="card" id="quantumResultsCard" style="display: none;">
            <div class="card-header">
                <span class="card-title">M3 Verified Quantum Simulation Result</span>
                <div style="display: flex; gap: 8px; align-items: center;">
                    <button class="btn secondary" style="padding: 3px 8px; font-size: 11px;" onclick="toggleComparePanel()">⚖️ Compare States</button>
                    <span class="badge" id="simAlgorithmBadge">Grover (1024 shots)</span>
                </div>
            </div>

            <!-- STATE TRIAD WIDGET (REQUIREMENT 3A) -->
            <div class="state-triad-grid" id="stateTriadContainer">
                <div class="triad-box prediction" id="triadPredictionBox" onclick="inspectStateFromTriad('prediction')">
                    <div class="triad-label">Learner Prediction</div>
                    <div class="triad-val pred" id="resPredictedState">|01⟩</div>
                    <div class="triad-sub" id="resPredictionStatus">Prediction Mismatch</div>
                </div>
                <div class="triad-box target" id="triadTargetBox" onclick="inspectStateFromTriad('target')">
                    <div class="triad-label">Theoretical Target</div>
                    <div class="triad-val targ" id="resTargetState">|10⟩</div>
                    <div class="triad-sub">Marked Target State</div>
                </div>
                <div class="triad-box measured" id="triadMeasuredBox" onclick="inspectStateFromTriad('measured')">
                    <div class="triad-label">Empirical Measured</div>
                    <div class="triad-val meas" id="resMostLikely">|10⟩</div>
                    <div class="triad-sub" id="resTargetProb">93.8% (1024 shots)</div>
                </div>
            </div>

            <!-- STATE ALIGNMENT COMPARISON PANEL (REQUIREMENT 9) -->
            <div class="compare-panel" id="comparePanel" style="display: none;">
                <div style="font-size: 11px; font-family: var(--font-mono); color: var(--cyan); text-transform: uppercase; font-weight: bold;">
                    State Triad Alignment Overview
                </div>
                <div class="compare-flow">
                    <div class="compare-node">
                        <span class="lbl">Prediction</span>
                        <span class="val" style="color: var(--yellow);" id="compPredVal">|01⟩</span>
                    </div>
                    <span class="compare-rel mismatch" id="compRel1">≠</span>
                    <div class="compare-node">
                        <span class="lbl">Theoretical Target</span>
                        <span class="val" style="color: var(--green);" id="compTargVal">|10⟩</span>
                    </div>
                    <span class="compare-rel match" id="compRel2">=</span>
                    <div class="compare-node">
                        <span class="lbl">Measured Empirical</span>
                        <span class="val" style="color: var(--cyan);" id="compMeasVal">|10⟩</span>
                    </div>
                </div>
                <div style="font-size: 11px; color: var(--text-muted); font-family: var(--font-mono); text-align: center;" id="compSummaryText">
                    Learner prediction deviated from theoretical target, while Qiskit Aer empirical execution confirmed the target state.
                </div>
            </div>

            <!-- STATE INSPECTOR DRAWER (REQUIREMENT 3C) -->
            <div class="state-inspector-box" id="stateInspectorDrawer" style="display: none;">
                <div class="inspector-row">
                    <strong style="color: var(--cyan);">State Inspection: <span id="inspStateName">|10⟩</span></strong>
                    <button style="background: none; border: none; color: var(--text-muted); cursor: pointer;" onclick="closeStateInspector()">✕</button>
                </div>
                <div class="inspector-row">
                    <span>Measurement Count:</span>
                    <span id="inspCountVal">961 / 1024 shots</span>
                </div>
                <div class="inspector-row">
                    <span>Empirical Probability:</span>
                    <span id="inspProbVal" style="color: var(--cyan);">93.8%</span>
                </div>
                <div class="inspector-row">
                    <span>Theoretical Target Match:</span>
                    <span id="inspTargetMatch" style="color: var(--green);">Yes (Marked State)</span>
                </div>
                <div class="inspector-row">
                    <span>Learner Prediction Match:</span>
                    <span id="inspPredMatch" style="color: var(--red);">No (Predicted |01⟩)</span>
                </div>
            </div>

            <!-- MEASUREMENT HISTOGRAM (REQUIREMENT 3B) -->
            <div style="font-family: var(--font-mono); font-size: 11px; text-transform: uppercase; color: var(--text-muted); margin-top: 4px; display: flex; justify-content: space-between;">
                <span>Empirical Measurement Distribution (Qiskit Aer)</span>
                <span style="font-size: 10px; color: var(--cyan);">Click any bar to inspect</span>
            </div>
            <div class="hist-container" id="histogramContainer"></div>

            <div id="asciiCircuitContainer" style="display: none; margin-top: 8px;">
                <div style="font-family: var(--font-mono); font-size: 11px; color: var(--text-muted); margin-bottom: 4px;">Verified Circuit Diagram (ASCII):</div>
                <pre id="asciiCircuitDiagram" style="background: var(--bg); padding: 8px; border-radius: 6px; font-family: var(--font-mono); font-size: 10px; overflow-x: auto; color: var(--cyan);"></pre>
            </div>
        </div>
    </div>

    <!-- RIGHT PANE: Task Prompt, Learner Submission & M2 Adaptive Cognition (M1) -->
    <div class="pane pane-right">
        <!-- 1. Active Task Card -->
        <div class="card" id="activityCard">
            <div class="card-header">
                <span class="card-title" id="activityTitle">Loading Activity...</span>
                <span class="badge" id="activityConceptBadge">quantum</span>
            </div>
            <div style="font-size: 13px; color: var(--text); line-height: 1.5;" id="activityPrompt">
                Loading task prompt...
            </div>

            <!-- Quantum Prediction Input (for prediction tasks - Requirement 7) -->
            <div id="predictionInputSection" style="display: none; flex-direction: column; gap: 8px;">
                <label style="font-size: 11px; font-family: var(--font-mono); color: var(--text-muted);">Quick Select Basis State or Type:</label>
                <div class="basis-pill-grid">
                    <button class="basis-pill" onclick="selectBasisPill('00')">|00⟩</button>
                    <button class="basis-pill" onclick="selectBasisPill('01')">|01⟩</button>
                    <button class="basis-pill" onclick="selectBasisPill('10')">|10⟩</button>
                    <button class="basis-pill" onclick="selectBasisPill('11')">|11⟩</button>
                </div>
                <div style="display: flex; gap: 8px;">
                    <input type="text" class="text-input" id="predictionField" value="01" placeholder="e.g. 01, 10" style="background: var(--bg); border: 1px solid var(--panel-border); color: var(--text); padding: 8px 12px; border-radius: 6px; font-family: var(--font-mono); font-size: 13px; flex: 1;">
                    <button class="btn" id="submitPredictionBtn" onclick="handleSubmitPrediction()">Run & Evaluate</button>
                </div>
            </div>

            <!-- Submission Progress Indicator (Requirement 7) -->
            <div id="executionProgressBanner" class="execution-progress-bar" style="display: none;">
                <span>⚡</span>
                <span id="executionProgressText">Submitting prediction to M4 gateway...</span>
            </div>

            <!-- Conceptual Choice Options (for MCQ tasks) -->
            <div id="choiceInputSection" style="display: none; flex-direction: column; gap: 10px;">
                <div class="options-grid" id="optionsContainer"></div>
                <button class="btn" id="submitChoiceBtn" onclick="handleSubmitChoice()">Submit Answer</button>
            </div>
        </div>

        <!-- 2. Empirical Evidence & Learner Cognition Card -->
        <div class="card" id="evidenceOutcomeCard" style="display: none;">
            <div class="card-header">
                <span class="card-title">Learner Evidence & Cognitive State</span>
                <span class="badge" id="outcomeBadge">Prediction Outcome</span>
            </div>

            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px;">
                <div class="stat-box" style="text-align: left; padding: 10px; background: var(--bg); border: 1px solid var(--panel-border); border-radius: 8px;">
                    <div class="stat-label">Cognitive Trajectory Trend</div>
                    <div class="stat-val" style="font-size: 13px; color: var(--purple);" id="trajectoryTrendDisplay">observing</div>
                </div>
                <div class="stat-box" style="text-align: left; padding: 10px; background: var(--bg); border: 1px solid var(--panel-border); border-radius: 8px;">
                    <div class="stat-label">Inference Confidence</div>
                    <div class="stat-val" style="font-size: 13px; color: var(--cyan);" id="confidenceBadgeDisplay">35%</div>
                </div>
            </div>

            <div style="font-size: 12px; font-family: var(--font-mono); color: var(--text); background: var(--bg); padding: 10px; border-radius: 8px; border: 1px solid var(--panel-border); display: flex; flex-direction: column; gap: 6px;">
                <div><strong style="color: var(--text-muted);">Evidence Sufficiency:</strong> <span style="color: var(--yellow);" id="evidenceSufficiencyDisplay">Insufficient (Gathering Observations)</span></div>
                <div><strong style="color: var(--text-muted);">Learner-State Hypothesis:</strong> <span style="color: var(--cyan);" id="inferredHypothesisDisplay">Preliminary difficulty observation</span></div>
                <div><strong style="color: var(--text-muted);">Latest Evidence Record:</strong> <span style="color: var(--text-muted);" id="evidenceIdDisplay">ev_001</span></div>
            </div>
        </div>

        <!-- 3. "WHY THIS NEXT?" ADAPTIVE DECISION TIMELINE (REQUIREMENT 4) -->
        <div class="card" id="adaptiveDecisionCard" style="display: none;">
            <div class="card-header">
                <span class="card-title">Why This Next? (Adaptive Recommendation)</span>
                <span class="badge action" id="adaptiveActionBadge">gather_evidence</span>
            </div>

            <div class="causal-chain">
                <!-- 1. Trigger -->
                <div class="chain-step" onclick="toggleChainStep(this)">
                    <div class="chain-node-header">
                        <div class="chain-node-title"><span>1. Decision Trigger</span></div>
                        <span class="chain-toggle-icon">▶</span>
                    </div>
                    <div class="chain-node-val" id="decisionTriggerDisplay">Single Prediction Mismatch</div>
                    <div class="chain-node-desc" id="triggerDesc">Triggered because the learner's initial prediction mismatched the target outcome.</div>
                </div>
                <div class="chain-arrow">↓</div>

                <!-- 2. Evidence Sufficiency -->
                <div class="chain-step" onclick="toggleChainStep(this)">
                    <div class="chain-node-header">
                        <div class="chain-node-title"><span>2. Evidence Sufficiency</span></div>
                        <span class="chain-toggle-icon">▶</span>
                    </div>
                    <div class="chain-node-val highlight-yellow" id="chainSufficiencyDisplay">Insufficient (Gathering Observations)</div>
                    <div class="chain-node-desc" id="sufficiencyDesc">Single observations do not establish cognitive certainty; more evidence is required.</div>
                </div>
                <div class="chain-arrow">↓</div>

                <!-- 3. Inferred Hypothesis -->
                <div class="chain-step" onclick="toggleChainStep(this)">
                    <div class="chain-node-header">
                        <div class="chain-node-title"><span>3. Inferred Learner-State Hypothesis</span></div>
                        <span class="chain-toggle-icon">▶</span>
                    </div>
                    <div class="chain-node-val highlight-cyan" id="chainHypothesisDisplay">Preliminary difficulty observation</div>
                    <div class="chain-node-desc" id="hypothesisDesc">M2 cognitive model hypothesis representing estimated understanding.</div>
                </div>
                <div class="chain-arrow">↓</div>

                <!-- 4. Supporting Evidence IDs -->
                <div class="chain-step" id="supportingEvidenceSection" onclick="toggleChainStep(this)">
                    <div class="chain-node-header">
                        <div class="chain-node-title"><span>4. Supporting Evidence Used</span></div>
                        <span class="chain-toggle-icon">▶</span>
                    </div>
                    <div id="supportingEvidenceList" class="supporting-chips"></div>
                    <div class="chain-node-desc">Direct audit trail of historical attempt evidence cited by M2.</div>
                </div>
                <div class="chain-arrow">↓</div>

                <!-- 5. Decision & Pedagogical Rationale -->
                <div class="chain-step expanded" onclick="toggleChainStep(this)">
                    <div class="chain-node-header">
                        <div class="chain-node-title"><span>5. Pedagogical Action & Rationale</span></div>
                        <span class="chain-toggle-icon">▶</span>
                    </div>
                    <p class="chain-reason" id="adaptiveReasonText">
                        Adaptive pedagogical rationale explaining why this action was selected.
                    </p>
                </div>
                <div class="chain-arrow">↓</div>

                <!-- 6. Next Activity & Navigation -->
                <div class="chain-step next-step">
                    <div>
                        <div class="chain-node-title">6. Next Recommended Activity</div>
                        <div class="next-activity-title" id="nextTargetActivityId">Grover 2-Qubit Target State Prediction</div>
                    </div>
                    <button class="btn success" id="continueNextBtn" onclick="handleContinueToTarget()">Continue →</button>
                </div>
            </div>

            <div id="prereqGapCallout" style="display: none; margin-top: 6px; font-size: 12px; color: var(--yellow); background: rgba(245, 158, 11, 0.1); padding: 8px 12px; border-radius: 6px; border: 1px solid rgba(245, 158, 11, 0.3);">
                ⚠️ Prerequisite Gap Identified in Concept: <strong id="prereqGapName">Superposition</strong>
            </div>
        </div>

        <!-- 4. Grounded AI Guidance Card (M5 - Requirement 8) -->
        <div class="card" id="aiGuidanceCard" style="display: none;">
            <div class="card-header">
                <span class="card-title">M5 Grounded AI Guidance</span>
                <button class="btn secondary" style="padding: 4px 10px; font-size: 11px;" id="explainBtn" onclick="handleExplain()">Explain My Result</button>
            </div>
            <div style="font-size: 11px; font-family: var(--font-mono); color: var(--cyan); margin-bottom: 2px;">
                💡 Grounded Guidance: M2 determined the adaptive learning path. M5 explains the underlying concept and verified evidence.
            </div>
            <div class="explanation-box" id="aiExplanationText">Click "Explain My Result" to generate an authoritative explanation grounded in the quantum curriculum.</div>
        </div>
    </div>
</div>

<!-- AI CONCEPTUAL ASK MODAL -->
<div class="modal-overlay" id="askModal" style="display: none;">
    <div class="modal-card">
        <div class="card-header">
            <span class="card-title">🤖 Ask Quantum AI Assistant</span>
            <button class="btn secondary" style="padding: 2px 8px; font-size: 11px;" onclick="closeAskModal()">✕</button>
        </div>
        <p style="font-size: 12px; color: var(--text-muted);">Ask any conceptual question about qubits, states, superposition, quantum gates, or Grover's algorithm:</p>
        <textarea id="askQuestionInput" rows="3" style="background: var(--bg); border: 1px solid var(--panel-border); color: var(--text); padding: 10px; border-radius: 8px; font-family: var(--font-body); font-size: 13px; resize: vertical;" placeholder="e.g. Why does Grover amplitude amplification over-rotate?"></textarea>
        <button class="btn" id="askSubmitBtn" onclick="handleAskQuestion()">Inquire</button>
        <div class="explanation-box" id="askAnswerBox" style="display: none; max-height: 180px;"></div>
    </div>
</div>

<!-- LEARNER PROFILE & SETTINGS MODAL -->
<div class="modal-overlay" id="profileModal" style="display: none;">
    <div class="modal-card profile-modal-card">
        <div class="card-header">
            <span class="card-title" id="profileModalTitle">Learner Profile</span>
            <button class="btn secondary" style="padding: 2px 8px; font-size: 11px;" onclick="closeProfileModal()">✕</button>
        </div>

        <!-- VIEW 1: MENU -->
        <div class="profile-view active" id="profileView-menu">
            <div class="profile-header-preview">
                <div class="profile-avatar-large" id="profileAvatar">QE</div>
                <div style="flex: 1;">
                    <div style="font-family: var(--font-display); font-size: 16px; font-weight: 700;" id="profileNameDisplay">Quantum Explorer</div>
                    <div style="font-size: 12px; color: var(--text-muted);" id="profileStudyingDisplay">Grover's Algorithm & Quantum State Triads</div>
                </div>
            </div>

            <div class="menu-item" onclick="showProfileView('edit')">
                <span>✏️ Edit Profile Details</span>
                <span>→</span>
            </div>
            <div class="menu-item" onclick="showProfileView('settings')">
                <span>⚙️ Preferences & Display Settings</span>
                <span>→</span>
            </div>
            <div class="toggle-row" id="darkModeToggleRow" onclick="toggleThemeFromModal()">
                <span style="font-size: 13px; font-weight: 500;">🌙 Theme Mode</span>
                <div class="toggle on" id="darkModeToggle"></div>
            </div>
        </div>

        <!-- VIEW 2: EDIT PROFILE -->
        <div class="profile-view" id="profileView-edit">
            <div style="font-size: 12px; font-family: var(--font-mono); color: var(--text-muted); margin-bottom: 8px;">CUSTOMIZE AVATAR & INFO:</div>

            <label style="font-size: 11px; color: var(--text-muted); display: block; margin-bottom: 4px;">Upload Profile Photo / Avatar:</label>
            <input type="file" id="avatarInput" accept="image/*" class="profile-input" style="padding: 6px;" />

            <label style="font-size: 11px; color: var(--text-muted); display: block; margin-bottom: 4px;">Display Name:</label>
            <input type="text" id="nameInput" class="profile-input" value="Quantum Explorer" placeholder="Enter your name" />

            <label style="font-size: 11px; color: var(--text-muted); display: block; margin-bottom: 4px;">Learning Focus / Bio:</label>
            <input type="text" id="studyingInput" class="profile-input" value="Grover's Algorithm & Quantum State Triads" placeholder="What are you studying?" />

            <div style="display: flex; gap: 8px; justify-content: flex-end;">
                <button class="btn secondary" onclick="showProfileView('menu')">Back</button>
                <button class="btn" onclick="saveProfileDetails()">Save Profile</button>
            </div>
        </div>

        <!-- VIEW 3: SETTINGS -->
        <div class="profile-view" id="profileView-settings">
            <div style="font-size: 12px; font-family: var(--font-mono); color: var(--text-muted); margin-bottom: 8px;">SESSION & PREFERENCES:</div>

            <div class="menu-item" onclick="handleResetSession(); closeProfileModal();">
                <span>🔄 Reset Active Learner Session</span>
                <span style="font-size: 11px; color: var(--yellow);">Generate New ID</span>
            </div>

            <div style="padding: 10px; background: var(--bg); border: 1px solid var(--panel-border); border-radius: 8px; margin-bottom: 12px; font-size: 11px; font-family: var(--font-mono); color: var(--text-muted);">
                💡 Active Learner State is managed securely in-memory by the M4 FastAPI Gateway.
            </div>

            <div style="display: flex; justify-content: flex-end;">
                <button class="btn secondary" onclick="showProfileView('menu')">Back to Menu</button>
            </div>
        </div>
    </div>
</div>

<script type="module">
    import { fetchActivities, fetchActivity, submitPrediction, explainExperiment, askConceptualQuestion } from './js/api_client.js';
    import { normalizeSubmissionResponse, formatStateLabel, formatPercentage, computeBadgeMetrics, getLearnerProfile, saveLearnerProfile } from './js/adapter.js';
    import { CircuitStudio, GATE_DEFINITIONS } from './js/circuit_view.js';

    let activitiesList = [];
    let currentActivityId = "act_grover_2q_predict";
    let currentActivityData = null;
    let selectedOptionLetter = null;
    let lastSubmitResult = null;
    let normalizedModel = null;
    let circuitStudio = null;
    let currentLearnerState = {};

    // -------------------------------------------------------------------
    // 1. Particle Cloud Background Animation (Non-blocking & graceful)
    // -------------------------------------------------------------------
    function initBackgroundParticles() {
        const canvas = document.getElementById('fx');
        if (!canvas || !canvas.getContext) return;
        const ctx = canvas.getContext('2d');
        const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        let w, h, particles;

        function resize() {
            w = canvas.width = window.innerWidth;
            h = canvas.height = window.innerHeight;
        }

        function initParticles() {
            const count = Math.min(65, Math.floor((w * h) / 22000));
            particles = Array.from({ length: count }, () => ({
                x: Math.random() * w,
                y: Math.random() * h,
                r: Math.random() * 1.5 + 0.5,
                vx: (Math.random() - 0.5) * 0.15,
                vy: (Math.random() - 0.5) * 0.15,
                hue: Math.random() > 0.5 ? '59,130,246' : '34,211,238',
                a: Math.random() * 0.45 + 0.15
            }));
        }

        function draw() {
            ctx.clearRect(0, 0, w, h);
            particles.forEach(p => {
                if (!reduceMotion) {
                    p.x += p.vx; p.y += p.vy;
                    if (p.x < 0) p.x = w; if (p.x > w) p.x = 0;
                    if (p.y < 0) p.y = h; if (p.y > h) p.y = 0;
                }
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(${p.hue},${p.a})`;
                ctx.fill();
            });
            if (!reduceMotion) requestAnimationFrame(draw);
        }

        resize();
        initParticles();
        draw();
        window.addEventListener('resize', () => { resize(); initParticles(); if (reduceMotion) draw(); });
    }
    initBackgroundParticles();

    // -------------------------------------------------------------------
    // 2. Mousemove Card Halo Glow
    // -------------------------------------------------------------------
    document.querySelectorAll('.card, .circuit-studio').forEach(box => {
        box.addEventListener('mousemove', e => {
            const rect = box.getBoundingClientRect();
            box.style.setProperty('--mx', `${e.clientX - rect.left}px`);
            box.style.setProperty('--my', `${e.clientY - rect.top}px`);
        });
    });

    // -------------------------------------------------------------------
    // 3. Initialize Circuit Studio with gate selection hook
    // -------------------------------------------------------------------
    circuitStudio = new CircuitStudio("circuitWireGrid", {
        numQubits: 2,
        numColumns: 6,
        onGateSelect: (gate) => {
            if (gate && GATE_DEFINITIONS[gate.type]) {
                const info = GATE_DEFINITIONS[gate.type];
                document.getElementById("gateInfoDisplay").innerHTML = `<span><strong>${info.name} Gate:</strong> ${info.desc}</span>`;
            }
        }
    });
    circuitStudio.loadPreset("grover_2q");

    // KaTeX Helper Function
    function renderMath(element) {
        if (typeof renderMathInElement === "function" && element) {
            renderMathInElement(element, {
                delimiters: [
                    { left: "$$", right: "$$", display: true },
                    { left: "$", right: "$", display: false }
                ],
                throwOnError: false
            });
        }
    }

    // Safe Lightweight Markdown Formatter for AI Guidance
    function formatGroundedMarkdown(rawText) {
        if (!rawText) return "";
        // 1. Escape HTML special characters for XSS safety
        const escaped = String(rawText)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");

        // 2. Parse lines into structured semantic elements
        const lines = escaped.split("\n");
        let html = "";
        let inList = false;

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            if (!line) {
                if (inList) { html += "</ul>"; inList = false; }
                continue;
            }

            if (line.startsWith("### ")) {
                if (inList) { html += "</ul>"; inList = false; }
                html += `<h4 class="ai-heading">${line.slice(4)}</h4>`;
            } else if (line.startsWith("## ")) {
                if (inList) { html += "</ul>"; inList = false; }
                html += `<h3 class="ai-heading-large">${line.slice(3)}</h3>`;
            } else if (line.startsWith("- ") || line.startsWith("* ")) {
                if (!inList) { html += `<ul class="ai-list">`; inList = true; }
                let item = line.slice(2)
                    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                    .replace(/`([^`]+)`/g, '<code class="ai-inline-code">$1</code>');
                html += `<li>${item}</li>`;
            } else if (/^\d+\.\s/.test(line)) {
                if (inList) { html += "</ul>"; inList = false; }
                let item = line.replace(/^\d+\.\s/, '')
                    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                    .replace(/`([^`]+)`/g, '<code class="ai-inline-code">$1</code>');
                html += `<div class="ai-ordered-item">${item}</div>`;
            } else {
                if (inList) { html += "</ul>"; inList = false; }
                let para = line
                    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                    .replace(/`([^`]+)`/g, '<code class="ai-inline-code">$1</code>');
                html += `<p class="ai-para">${para}</p>`;
            }
        }
        if (inList) { html += "</ul>"; }
        return html;
    }

    // -------------------------------------------------------------------
    // 4. Progress Updater (M2-driven)
    // -------------------------------------------------------------------
    function updateBadgeDisplays(learnerState = {}) {
        const metrics = computeBadgeMetrics(learnerState, activitiesList);
        const masteryEl = document.getElementById("badgeMastery");
        if (masteryEl) masteryEl.textContent = `${metrics.completedCount}/${metrics.totalCount}`;
    }

    // -------------------------------------------------------------------
    // 5. Learner Profile & Modal Handlers
    // -------------------------------------------------------------------
    window.openProfileModal = function() {
        const modal = document.getElementById("profileModal");
        modal.style.display = "flex";
        showProfileView('menu');
    };

    window.closeProfileModal = function() {
        document.getElementById("profileModal").style.display = "none";
    };

    const profileTitles = { menu: 'Learner Profile', edit: 'Edit Profile Details', settings: 'Preferences & Settings' };
    window.showProfileView = function(view) {
        document.querySelectorAll('.profile-view').forEach(v => v.classList.remove('active'));
        const targetView = document.getElementById(`profileView-${view}`);
        if (targetView) targetView.classList.add('active');
        const titleEl = document.getElementById('profileModalTitle');
        if (titleEl) titleEl.textContent = profileTitles[view] || 'Learner Profile';
    };

    function loadProfileOnBoot() {
        const learnerId = document.getElementById("learnerIdInput").value.trim() || "demo_learner";
        const profile = getLearnerProfile(learnerId);

        const nameDisp = document.getElementById("profileNameDisplay");
        const studyDisp = document.getElementById("profileStudyingDisplay");
        const nameInp = document.getElementById("nameInput");
        const studyInp = document.getElementById("studyingInput");
        const avatarEl = document.getElementById("profileAvatar");
        const openBtn = document.getElementById("profileOpenBtn");

        if (nameDisp) nameDisp.textContent = profile.name;
        if (studyDisp) studyDisp.textContent = profile.studying;
        if (nameInp) nameInp.value = profile.name;
        if (studyInp) studyInp.value = profile.studying;

        if (profile.avatar) {
            if (avatarEl) { avatarEl.style.backgroundImage = `url(${profile.avatar})`; avatarEl.textContent = ''; }
            if (openBtn) { openBtn.style.backgroundImage = `url(${profile.avatar})`; openBtn.textContent = ''; }
        } else {
            const initials = profile.name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase() || 'QE';
            if (avatarEl) { avatarEl.style.backgroundImage = ''; avatarEl.textContent = initials; }
            if (openBtn) { openBtn.style.backgroundImage = ''; openBtn.textContent = initials; }
        }

        // Apply theme preference
        const isDark = profile.theme !== "light";
        document.documentElement.setAttribute("data-theme", isDark ? "dark" : "light");
        const toggle = document.getElementById("darkModeToggle");
        if (toggle) toggle.classList.toggle("on", isDark);
    }

    window.saveProfileDetails = function() {
        const learnerId = document.getElementById("learnerIdInput").value.trim() || "demo_learner";
        const profile = getLearnerProfile(learnerId);
        profile.name = document.getElementById("nameInput").value.trim() || profile.name;
        profile.studying = document.getElementById("studyingInput").value.trim() || profile.studying;
        saveLearnerProfile(learnerId, profile);
        loadProfileOnBoot();
        showProfileView('menu');
    };

    // Avatar File Input Change Listener
    const avatarInput = document.getElementById('avatarInput');
    if (avatarInput) {
        avatarInput.addEventListener('change', () => {
            const file = avatarInput.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = e => {
                const learnerId = document.getElementById("learnerIdInput").value.trim() || "demo_learner";
                const profile = getLearnerProfile(learnerId);
                profile.avatar = e.target.result;
                saveLearnerProfile(learnerId, profile);
                loadProfileOnBoot();
            };
            reader.readAsDataURL(file);
        });
    }

    window.toggleThemeFromModal = function() {
        const html = document.documentElement;
        const isDark = html.getAttribute("data-theme") === "dark";
        const newTheme = isDark ? "light" : "dark";
        html.setAttribute("data-theme", newTheme);
        const toggle = document.getElementById("darkModeToggle");
        if (toggle) toggle.classList.toggle("on", !isDark);

        const learnerId = document.getElementById("learnerIdInput").value.trim() || "demo_learner";
        const profile = getLearnerProfile(learnerId);
        profile.theme = newTheme;
        saveLearnerProfile(learnerId, profile);
    };

    // -------------------------------------------------------------------
    // 6. Global Functions for Toolbar & Interactions
    // -------------------------------------------------------------------
    window.selectGate = function(type) {
        circuitStudio.setTool(type);
        document.querySelectorAll(".gate-btn").forEach(b => b.classList.remove("active-tool"));
        event.target.classList.add("active-tool");
        document.getElementById("activeToolDisplay").textContent = type;
        if (GATE_DEFINITIONS[type]) {
            const def = GATE_DEFINITIONS[type];
            document.getElementById("gateInfoDisplay").innerHTML = `<span><strong>${def.name} (${type}):</strong> ${def.desc} • <code>${def.matrix}</code></span>`;
        }
    };
    window.addStudioQubit = function() { circuitStudio.addQubit(); };
    window.clearStudioCircuit = function() { circuitStudio.clear(); };
    window.loadCircuitPreset = function(name) { circuitStudio.loadPreset(name); };

    window.selectBasisPill = function(basis) {
        document.querySelectorAll(".basis-pill").forEach(p => p.classList.remove("selected"));
        event.target.classList.add("selected");
        document.getElementById("predictionField").value = basis;
    };

    window.toggleChainStep = function(stepElement) {
        stepElement.classList.toggle("expanded");
    };

    window.toggleComparePanel = function() {
        const panel = document.getElementById("comparePanel");
        panel.style.display = panel.style.display === "none" ? "flex" : "none";
    };

    window.inspectState = function(stateObj) {
        if (!stateObj || !normalizedModel) return;
        const drawer = document.getElementById("stateInspectorDrawer");
        drawer.style.display = "flex";
        document.getElementById("inspStateName").textContent = stateObj.stateLabel;
        document.getElementById("inspCountVal").textContent = `${stateObj.count} / ${normalizedModel.quantum.shots} shots`;
        document.getElementById("inspProbVal").textContent = stateObj.percentageStr;
        document.getElementById("inspTargetMatch").textContent = stateObj.isTarget ? "Yes (Marked Target State)" : "No";
        document.getElementById("inspTargetMatch").style.color = stateObj.isTarget ? "var(--green)" : "var(--text-muted)";
        document.getElementById("inspPredMatch").textContent = stateObj.isPredicted ? `Yes (Predicted ${stateObj.stateLabel})` : `No (Learner predicted ${normalizedModel.learner.predictionLabel})`;
        document.getElementById("inspPredMatch").style.color = stateObj.isPredicted ? "var(--yellow)" : "var(--text-muted)";
    };

    window.inspectStateFromTriad = function(type) {
        if (!normalizedModel || !normalizedModel.quantum) return;
        if (type === "target") {
            const bar = normalizedModel.quantum.probabilityBars.find(b => b.isTarget);
            if (bar) inspectState(bar);
        } else if (type === "measured") {
            const bar = normalizedModel.quantum.probabilityBars.find(b => b.isMostLikely);
            if (bar) inspectState(bar);
        } else if (type === "prediction") {
            const bar = normalizedModel.quantum.probabilityBars.find(b => b.isPredicted);
            if (bar) inspectState(bar);
        }
    };

    window.closeStateInspector = function() {
        document.getElementById("stateInspectorDrawer").style.display = "none";
    };

    window.closeErrorBanner = function() {
        document.getElementById("errorNotificationBanner").style.display = "none";
    };

    function showError(message) {
        const banner = document.getElementById("errorNotificationBanner");
        document.getElementById("errorBannerMessage").textContent = message;
        banner.style.display = "flex";
    }

    function initLearnerId() {
        let savedId = null;
        try {
            savedId = localStorage.getItem("qbit_current_learner_id");
        } catch {}

        if (!savedId) {
            const uuid = (typeof crypto !== "undefined" && crypto.randomUUID)
                ? crypto.randomUUID()
                : Math.random().toString(36).substring(2, 10);
            savedId = `learner_${uuid}`;
            try {
                localStorage.setItem("qbit_current_learner_id", savedId);
            } catch {}
        }
        const inputEl = document.getElementById("learnerIdInput");
        if (inputEl) {
            inputEl.value = savedId;
        }
    }

    window.handleResetSession = function() {
        const uuid = (typeof crypto !== "undefined" && crypto.randomUUID)
            ? crypto.randomUUID()
            : Math.random().toString(36).substring(2, 10);
        const newLearnerId = `learner_${uuid}`;
        const inputEl = document.getElementById("learnerIdInput");
        if (inputEl) {
            inputEl.value = newLearnerId;
        }
        try {
            localStorage.setItem("qbit_current_learner_id", newLearnerId);
        } catch {}
        loadProfileOnBoot();
        loadActivity("act_grover_2q_predict");
    };

    // -------------------------------------------------------------------
    // 7. App Initialization & Curriculum Loading
    // -------------------------------------------------------------------
    async function initApp() {
        try {
            initLearnerId();
            activitiesList = await fetchActivities();
            renderJourneyTrack();
            loadProfileOnBoot();
            updateBadgeDisplays({});
            await loadActivity(currentActivityId);
        } catch (err) {
            console.error("Failed to load initial activities:", err);
            showError(`Failed to load activities: ${err.message}`);
            document.getElementById("activityTitle").textContent = "Grover 2-Qubit Prediction";
            document.getElementById("predictionInputSection").style.display = "flex";
        }
    }

    function renderJourneyTrack() {
        const container = document.getElementById("journeySteps");
        container.innerHTML = "";
        const curIdx = activitiesList.findIndex(a => a.activity_id === currentActivityId);
        document.getElementById("journeyProgressBadge").textContent = `Step ${curIdx >= 0 ? curIdx + 1 : 1} of ${activitiesList.length || 4}`;

        activitiesList.forEach((act, idx) => {
            const node = document.createElement("div");
            const isCur = act.activity_id === currentActivityId;
            const isCompleted = idx < curIdx;
            node.className = `journey-node ${isCur ? 'active' : ''} ${isCompleted ? 'completed' : ''}`;
            node.innerHTML = `<span>${idx + 1}.</span> <span>${act.title.split(' ')[0]}</span>`;
            node.title = act.title;
            node.onclick = () => loadActivity(act.activity_id);
            container.appendChild(node);

            if (idx < activitiesList.length - 1) {
                const arr = document.createElement("span");
                arr.className = "journey-arrow";
                arr.textContent = "→";
                container.appendChild(arr);
            }
        });
    }

    window.loadActivity = async function(activityId) {
        currentActivityId = activityId;
        renderJourneyTrack();
        closeErrorBanner();

        // Reset outcome displays
        document.getElementById("quantumResultsCard").style.display = "none";
        document.getElementById("comparePanel").style.display = "none";
        document.getElementById("stateInspectorDrawer").style.display = "none";
        document.getElementById("evidenceOutcomeCard").style.display = "none";
        document.getElementById("adaptiveDecisionCard").style.display = "none";
        document.getElementById("aiGuidanceCard").style.display = "none";
        selectedOptionLetter = null;
        lastSubmitResult = null;
        normalizedModel = null;

        try {
            const act = await fetchActivity(activityId);
            currentActivityData = act;

            document.getElementById("activityTitle").textContent = act.title;
            document.getElementById("activityConceptBadge").textContent = act.concept_id;
            const promptEl = document.getElementById("activityPrompt");
            promptEl.textContent = act.prompt;
            renderMath(promptEl);

            if (act.task_type === "quantum_prediction") {
                document.getElementById("predictionInputSection").style.display = "flex";
                document.getElementById("choiceInputSection").style.display = "none";
                if (act.quantum_experiment) {
                    circuitStudio.loadPreset("grover_2q");
                }
            } else {
                document.getElementById("predictionInputSection").style.display = "none";
                document.getElementById("choiceInputSection").style.display = "flex";
                renderOptions(act.options || {});
            }
        } catch (err) {
            showError(`Error loading activity: ${err.message}`);
        }
    };

    function renderOptions(options) {
        const container = document.getElementById("optionsContainer");
        container.innerHTML = "";
        selectedOptionLetter = null;

        Object.entries(options).forEach(([letter, text]) => {
            const btn = document.createElement("div");
            btn.className = "option-btn";
            btn.innerHTML = `<span class="option-key">${letter}.</span> <span class="opt-text">${text}</span>`;
            renderMath(btn.querySelector(".opt-text"));
            btn.onclick = () => {
                document.querySelectorAll(".option-btn").forEach(b => b.classList.remove("selected"));
                btn.classList.add("selected");
                selectedOptionLetter = letter;
            };
            container.appendChild(btn);
        });
    }

    window.handleSubmitPrediction = async function() {
        const pred = document.getElementById("predictionField").value.trim();
        if (!pred) return alert("Please enter a prediction basis state (e.g. 01 or 10)");
        await executeSubmission(pred);
    };

    window.handleSubmitChoice = async function() {
        if (!selectedOptionLetter) return alert("Please select an option letter (A, B, C, or D)");
        await executeSubmission(selectedOptionLetter);
    };

    async function executeSubmission(learnerResponse) {
        const learnerId = document.getElementById("learnerIdInput").value.trim() || "demo_learner";
        const submitBtn = document.getElementById("submitPredictionBtn");
        const choiceBtn = document.getElementById("submitChoiceBtn");
        const progressBanner = document.getElementById("executionProgressBanner");
        const progressText = document.getElementById("executionProgressText");

        submitBtn.disabled = true; choiceBtn.disabled = true;
        progressBanner.style.display = "flex";
        progressText.textContent = "Executing quantum circuit on Qiskit Aer (1024 shots)...";
        closeErrorBanner();

        try {
            const rawResponse = await submitPrediction(currentActivityId, learnerId, learnerResponse);
            lastSubmitResult = rawResponse;
            normalizedModel = normalizeSubmissionResponse(rawResponse);
            const model = normalizedModel;

            if (model.learnerState) {
                currentLearnerState = model.learnerState;
                updateBadgeDisplays(currentLearnerState);
            }

            // 1. Render Quantum Simulation Result & State Triad
            if (model.quantum) {
                document.getElementById("quantumResultsCard").style.display = "flex";

                // Populate State Triad
                const predBox = document.getElementById("triadPredictionBox");
                predBox.className = `triad-box prediction ${model.learner.isCorrect ? 'correct' : ''}`;
                document.getElementById("resPredictedState").textContent = model.learner.predictionLabel;
                document.getElementById("resPredictionStatus").textContent = model.learner.outcomeText;
                document.getElementById("resTargetState").textContent = model.quantum.targetStateLabel;
                document.getElementById("resMostLikely").textContent = model.quantum.mostLikelyStateLabel;
                document.getElementById("resTargetProb").textContent = `${model.quantum.targetProbabilityStr} (${model.quantum.shots} shots)`;
                document.getElementById("simAlgorithmBadge").textContent = `${model.quantum.algorithm} (${model.quantum.shots} shots)`;

                // Populate State Compare Diagram
                document.getElementById("compPredVal").textContent = model.learner.predictionLabel;
                document.getElementById("compTargVal").textContent = model.quantum.targetStateLabel;
                document.getElementById("compMeasVal").textContent = `${model.quantum.mostLikelyStateLabel} (${model.quantum.targetProbabilityStr})`;
                document.getElementById("compRel1").textContent = model.learner.isCorrect ? "=" : "≠";
                document.getElementById("compRel1").className = `compare-rel ${model.learner.isCorrect ? 'match' : 'mismatch'}`;

                // Populate Interactive Measurement Histogram
                const hist = document.getElementById("histogramContainer");
                hist.innerHTML = "";
                model.quantum.probabilityBars.forEach(b => {
                    const row = document.createElement("div");
                    row.className = `hist-row ${b.isTarget ? 'target-row' : ''}`;
                    row.title = `State ${b.stateLabel}: ${b.percentageStr} (${b.count} shots). Click to inspect details.`;
                    row.onclick = () => {
                        document.querySelectorAll(".hist-row").forEach(r => r.classList.remove("selected"));
                        row.classList.add("selected");
                        inspectState(b);
                    };
                    row.innerHTML = `
                        <span class="hist-state">${b.stateLabel}</span>
                        <div class="hist-bar-bg">
                            <div class="hist-bar-fill ${b.isTarget ? 'target' : ''} ${b.isPredicted ? 'predicted' : ''}" style="width: ${Math.max(b.percentageNum, 3)}%;"></div>
                        </div>
                        <span class="hist-pct">${b.percentageStr}</span>
                    `;
                    hist.appendChild(row);
                });

                if (model.quantum.circuit.diagram) {
                    document.getElementById("asciiCircuitContainer").style.display = "block";
                    document.getElementById("asciiCircuitDiagram").textContent = model.quantum.circuit.diagram;
                }
            } else {
                document.getElementById("quantumResultsCard").style.display = "none";
            }

            // 2. Render Evidence & Cognition Panel
            document.getElementById("evidenceOutcomeCard").style.display = "flex";
            const outcomeBadge = document.getElementById("outcomeBadge");
            outcomeBadge.textContent = `${model.learner.outcomeText} (Attempt #${model.learner.attemptNumber})`;
            outcomeBadge.className = `badge ${model.learner.outcomeClass}`;

            document.getElementById("trajectoryTrendDisplay").textContent = model.adaptive.gapTrend;
            document.getElementById("confidenceBadgeDisplay").textContent = `${Math.round(model.adaptive.gapConfidence * 100)}%`;
            document.getElementById("evidenceSufficiencyDisplay").textContent = model.adaptive.evidenceSufficiencyLabel;
            document.getElementById("inferredHypothesisDisplay").textContent = model.adaptive.hypothesisLabel;
            document.getElementById("evidenceIdDisplay").textContent = model.learner.evidenceId || "N/A";

            // 3. Render "Why This Next?" Adaptive Decision Card
            document.getElementById("adaptiveDecisionCard").style.display = "flex";
            document.getElementById("adaptiveActionBadge").textContent = model.adaptive.actionLabel;
            document.getElementById("decisionTriggerDisplay").textContent = model.adaptive.triggerLabel;
            document.getElementById("chainSufficiencyDisplay").textContent = model.adaptive.evidenceSufficiencyLabel;
            document.getElementById("chainHypothesisDisplay").textContent = model.adaptive.hypothesisLabel;
            document.getElementById("adaptiveReasonText").textContent = model.adaptive.reason;

            // Render Supporting Evidence Chips
            const suppList = document.getElementById("supportingEvidenceList");
            suppList.innerHTML = "";
            if (model.adaptive.supportingEvidenceIds && model.adaptive.supportingEvidenceIds.length > 0) {
                model.adaptive.supportingEvidenceIds.forEach((eid, idx) => {
                    const chip = document.createElement("span");
                    chip.className = "evidence-chip";
                    chip.innerHTML = `<span>Attempt #${idx + 1} Record</span> <strong>${eid}</strong>`;
                    suppList.appendChild(chip);
                });
                document.getElementById("supportingEvidenceSection").style.display = "block";
            } else {
                document.getElementById("supportingEvidenceSection").style.display = "none";
            }

            if (model.adaptive.prerequisiteGap) {
                document.getElementById("prereqGapCallout").style.display = "block";
                document.getElementById("prereqGapName").textContent = model.adaptive.prerequisiteGap;
            } else {
                document.getElementById("prereqGapCallout").style.display = "none";
            }

            const targetAct = model.adaptive.targetActivity;
            if (targetAct) {
                const targetTitle = (activitiesList.find(a => a.activity_id === targetAct)?.title) || targetAct;
                document.getElementById("nextTargetActivityId").textContent = targetTitle;
                document.getElementById("continueNextBtn").style.display = "inline-block";
                document.getElementById("continueNextBtn").dataset.target = targetAct;
            } else {
                document.getElementById("nextTargetActivityId").textContent = "End of Sequence (Curriculum Complete)";
                document.getElementById("continueNextBtn").style.display = "none";
            }

            // 4. Reveal AI Guidance Card
            document.getElementById("aiGuidanceCard").style.display = "flex";
            document.getElementById("aiExplanationText").textContent = 'Click "Explain My Result" for grounded AI explanation of this attempt.';

        } catch (err) {
            showError(`Submission Error: ${err.message}`);
        } finally {
            submitBtn.disabled = false; choiceBtn.disabled = false;
            progressBanner.style.display = "none";
        }
    }

    window.handleContinueToTarget = function() {
        const target = document.getElementById("continueNextBtn").dataset.target;
        if (target) loadActivity(target);
    };

    window.handleExplain = async function() {
        if (!lastSubmitResult) return;
        const btn = document.getElementById("explainBtn");
        btn.disabled = true; btn.textContent = "Generating Grounded Guidance...";

        try {
            const exp = await explainExperiment(lastSubmitResult);
            const expBox = document.getElementById("aiExplanationText");
            expBox.innerHTML = formatGroundedMarkdown(exp.explanation);
            renderMath(expBox);
        } catch (err) {
            document.getElementById("aiExplanationText").innerHTML = `<p class="ai-para">AI Guidance Notice: Grounded explanation is temporarily unavailable (${err.message}). Your verified quantum simulation result and adaptive progress remain safely recorded.</p>`;
        } finally {
            btn.disabled = false; btn.textContent = "Explain My Result";
        }
    };

    // Modal AI Question Inquirer
    window.openAskModal = function() {
        document.getElementById("askModal").style.display = "flex";
        document.getElementById("askAnswerBox").style.display = "none";
    };
    window.closeAskModal = function() {
        document.getElementById("askModal").style.display = "none";
    };
    window.handleAskQuestion = async function() {
        const q = document.getElementById("askQuestionInput").value.trim();
        if (!q) return;
        const btn = document.getElementById("askSubmitBtn");
        btn.disabled = true; btn.textContent = "Consulting Curriculum...";

        try {
            const res = await askConceptualQuestion(q, currentActivityData?.concept_id || null);
            const box = document.getElementById("askAnswerBox");
            box.style.display = "block";
            box.innerHTML = formatGroundedMarkdown(res.answer);
            renderMath(box);
        } catch (err) {
            showError(`Question error: ${err.message}`);
        } finally {
            btn.disabled = false; btn.textContent = "Inquire";
        }
    };

    window.toggleTheme = function() {
        toggleThemeFromModal();
    };

    // Boot
    initApp();
</script>

</body>
</html>

```

## Line Notes

### Line 1

`<!DOCTYPE html>`

Declares the HTML standard used to parse this document.
### Line 2

`<html lang="en" data-theme="dark">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 3

`<head>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 4

`<meta charset="UTF-8">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 5

`<meta name="viewport" content="width=device-width, initial-scale=1.0">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 6

`<title>Q-BIT.140 — AI-Based Interactive Quantum Algorithm Learning Platform</title>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 7

`<link rel="preconnect" href="https://fonts.googleapis.com">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 8

`<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 9

`(blank)`

Blank line used to separate nearby statements.
### Line 10

`<!-- KaTeX for Grounded Quantum Math Notation -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 11

`<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css" crossorigin="anonymous">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 12

`<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js" crossorigin="anonymous"></script>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 13

`<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js" crossorigin="anonymous"></script>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 14

`(blank)`

Blank line used to separate nearby statements.
### Line 15

`<link rel="stylesheet" href="./css/styles.css">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 16

`</head>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 17

`<body>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 18

`(blank)`

Blank line used to separate nearby statements.
### Line 19

`<!-- BACKGROUND PARTICLE CANVAS (DECORATIVE QUANTUM CLOUD) -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 20

`<canvas id="fx"></canvas>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 21

`(blank)`

Blank line used to separate nearby statements.
### Line 22

`<!-- TOP BAR -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 23

`<header>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 24

`<div class="header-left">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 25

`<div class="atom" title="Q-BIT Quantum Engine">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 26

`<svg viewBox="0 0 36 36" fill="none">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 27

`<circle cx="18" cy="18" r="4" fill="url(#coreGlow)" />`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 28

`<ellipse class="orbit" cx="18" cy="18" rx="14" ry="5" stroke="var(--cyan)" stroke-width="1.2" opacity="0.85" transform="rotate(30 18 18)" />`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 29

`<ellipse class="orbit o2" cx="18" cy="18" rx="14" ry="5" stroke="var(--accent)" stroke-width="1.2" opacity="0.85" transform="rotate(-30 18 18)" />`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 30

`<defs>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 31

`<radialGradient id="coreGlow" cx="50%" cy="50%" r="50%">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 32

`<stop offset="0%" stop-color="#FFFFFF" />`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 33

`<stop offset="100%" stop-color="var(--cyan)" />`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 34

`</radialGradient>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 35

`</defs>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 36

`</svg>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 37

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 38

`<div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 39

`<h1 class="brand-title">Q-BIT.140</h1>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 40

`<div class="brand-sub">Evidence-Driven Adaptive Quantum Learning Platform • SIH 2026</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 41

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 42

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 43

`(blank)`

Blank line used to separate nearby statements.
### Line 44

`<!-- TOPBAR MASTERY BADGE -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 45

`<div style="display: flex; align-items: center; gap: 8px;" id="topbarBadges">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 46

`<div class="chip" id="chipMastery" title="Concepts mastered">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 47

`<span class="chip-icon">🏆</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 48

`<span class="chip-label">Mastery</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 49

`<span class="chip-val green" id="badgeMastery">1/4</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 50

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 51

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 52

`(blank)`

Blank line used to separate nearby statements.
### Line 53

`<div class="header-right">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 54

`<input type="hidden" id="learnerIdInput" value="">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 55

`<button class="btn secondary" style="padding: 6px 12px; font-size: 11px;" onclick="handleResetSession()">🔄 Reset Session</button>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 56

`<button class="btn secondary" style="padding: 6px 12px; font-size: 11px;" onclick="openAskModal()">🤖 Ask AI</button>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 57

`<button class="profile-btn" id="profileOpenBtn" onclick="openProfileModal()" title="Learner Profile & Settings">QE</button>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 58

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 59

`</header>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 60

`(blank)`

Blank line used to separate nearby statements.
### Line 61

`<!-- GLOBAL NOTIFICATION / ERROR BANNER -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 62

`<div id="errorNotificationBanner" style="display: none; padding: 10px 28px; font-size: 12px; font-family: var(--font-mono); background: rgba(239, 68, 68, 0.15); border-bottom: 1px solid var(--red); color: var(--red); align-items: center; justify-content: space-between;">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 63

`<span id="errorBannerMessage">Error message</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 64

`<button style="background: none; border: none; color: var(--red); cursor: pointer; font-size: 14px;" onclick="closeErrorBanner()">✕</button>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 65

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 66

`(blank)`

Blank line used to separate nearby statements.
### Line 67

`<!-- CURRICULUM JOURNEY TRACK (REQUIREMENT 5) -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 68

`<div class="journey-bar">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 69

`<div class="journey-left">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 70

`<span class="journey-title">Curriculum Path:</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 71

`<div class="journey-steps" id="journeySteps">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 72

`<!-- Dynamically rendered activity nodes -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 73

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 74

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 75

`<div class="journey-progress-badge" id="journeyProgressBadge">Step 1 of 4</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 76

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 77

`(blank)`

Blank line used to separate nearby statements.
### Line 78

`<!-- WORKSPACE LAYOUT -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 79

`<div class="workspace-layout">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 80

`<!-- LEFT PANE: Circuit Studio & M3 Simulation (M6) -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 81

`<div class="pane pane-left">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 82

`<!-- Circuit Studio -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 83

`<div class="circuit-studio">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 84

`<div class="card-header">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 85

`<span class="card-title">Interactive Quantum Circuit Studio (Visual Exploration)</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 86

`<span style="font-family: var(--font-mono); font-size: 12px; color: var(--text-muted);">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 87

`Tool: <strong id="activeToolDisplay" style="color: var(--cyan);">None</strong>`

Text content rendered inside the nearest HTML element.
### Line 88

`</span>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 89

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 90

`(blank)`

Blank line used to separate nearby statements.
### Line 91

`<div class="gate-toolbar">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 92

`<button class="gate-btn" onclick="selectGate('H')">H</button>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 93

`<button class="gate-btn" onclick="selectGate('X')">X</button>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 94

`<button class="gate-btn" onclick="selectGate('Y')">Y</button>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 95

`<button class="gate-btn" onclick="selectGate('Z')">Z</button>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 96

`<button class="gate-btn" onclick="selectGate('S')">S</button>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 97

`<button class="gate-btn" onclick="selectGate('T')">T</button>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 98

`<button class="gate-btn" onclick="selectGate('CZ')">CZ</button>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 99

`<button class="gate-btn" onclick="selectGate('M')">M</button>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 100

`<div style="flex: 1;"></div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 101

`<button class="btn secondary" style="padding: 5px 10px; font-size: 11px;" onclick="loadCircuitPreset('grover_2q')">Preset: Grover 2Q</button>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 102

`<button class="btn secondary" style="padding: 5px 10px; font-size: 11px;" onclick="addStudioQubit()">+ Qubit</button>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 103

`<button class="btn secondary" style="padding: 5px 10px; font-size: 11px;" onclick="clearStudioCircuit()">Clear</button>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 104

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 105

`(blank)`

Blank line used to separate nearby statements.
### Line 106

`<div class="wire-grid" id="circuitWireGrid"></div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 107

`(blank)`

Blank line used to separate nearby statements.
### Line 108

`<div class="gate-info-callout" id="gateInfoDisplay">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 109

`<span>💡 Visual Circuit Explorer: Place gates on the grid to inspect quantum operations. Submissions execute the active activity circuit on Qiskit Aer (1024 shots).</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 110

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 111

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 112

`(blank)`

Blank line used to separate nearby statements.
### Line 113

`<!-- M3 Verified Quantum Results (Revealed after submission) -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 114

`<div class="card" id="quantumResultsCard" style="display: none;">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 115

`<div class="card-header">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 116

`<span class="card-title">M3 Verified Quantum Simulation Result</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 117

`<div style="display: flex; gap: 8px; align-items: center;">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 118

`<button class="btn secondary" style="padding: 3px 8px; font-size: 11px;" onclick="toggleComparePanel()">⚖️ Compare States</button>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 119

`<span class="badge" id="simAlgorithmBadge">Grover (1024 shots)</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 120

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 121

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 122

`(blank)`

Blank line used to separate nearby statements.
### Line 123

`<!-- STATE TRIAD WIDGET (REQUIREMENT 3A) -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 124

`<div class="state-triad-grid" id="stateTriadContainer">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 125

`<div class="triad-box prediction" id="triadPredictionBox" onclick="inspectStateFromTriad('prediction')">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 126

`<div class="triad-label">Learner Prediction</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 127

`<div class="triad-val pred" id="resPredictedState">|01⟩</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 128

`<div class="triad-sub" id="resPredictionStatus">Prediction Mismatch</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 129

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 130

`<div class="triad-box target" id="triadTargetBox" onclick="inspectStateFromTriad('target')">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 131

`<div class="triad-label">Theoretical Target</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 132

`<div class="triad-val targ" id="resTargetState">|10⟩</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 133

`<div class="triad-sub">Marked Target State</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 134

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 135

`<div class="triad-box measured" id="triadMeasuredBox" onclick="inspectStateFromTriad('measured')">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 136

`<div class="triad-label">Empirical Measured</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 137

`<div class="triad-val meas" id="resMostLikely">|10⟩</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 138

`<div class="triad-sub" id="resTargetProb">93.8% (1024 shots)</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 139

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 140

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 141

`(blank)`

Blank line used to separate nearby statements.
### Line 142

`<!-- STATE ALIGNMENT COMPARISON PANEL (REQUIREMENT 9) -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 143

`<div class="compare-panel" id="comparePanel" style="display: none;">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 144

`<div style="font-size: 11px; font-family: var(--font-mono); color: var(--cyan); text-transform: uppercase; font-weight: bold;">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 145

`State Triad Alignment Overview`

Text content rendered inside the nearest HTML element.
### Line 146

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 147

`<div class="compare-flow">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 148

`<div class="compare-node">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 149

`<span class="lbl">Prediction</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 150

`<span class="val" style="color: var(--yellow);" id="compPredVal">|01⟩</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 151

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 152

`<span class="compare-rel mismatch" id="compRel1">≠</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 153

`<div class="compare-node">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 154

`<span class="lbl">Theoretical Target</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 155

`<span class="val" style="color: var(--green);" id="compTargVal">|10⟩</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 156

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 157

`<span class="compare-rel match" id="compRel2">=</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 158

`<div class="compare-node">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 159

`<span class="lbl">Measured Empirical</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 160

`<span class="val" style="color: var(--cyan);" id="compMeasVal">|10⟩</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 161

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 162

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 163

`<div style="font-size: 11px; color: var(--text-muted); font-family: var(--font-mono); text-align: center;" id="compSummaryText">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 164

`Learner prediction deviated from theoretical target, while Qiskit Aer empirical execution confirmed the target state.`

Text content rendered inside the nearest HTML element.
### Line 165

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 166

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 167

`(blank)`

Blank line used to separate nearby statements.
### Line 168

`<!-- STATE INSPECTOR DRAWER (REQUIREMENT 3C) -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 169

`<div class="state-inspector-box" id="stateInspectorDrawer" style="display: none;">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 170

`<div class="inspector-row">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 171

`<strong style="color: var(--cyan);">State Inspection: <span id="inspStateName">|10⟩</span></strong>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 172

`<button style="background: none; border: none; color: var(--text-muted); cursor: pointer;" onclick="closeStateInspector()">✕</button>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 173

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 174

`<div class="inspector-row">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 175

`<span>Measurement Count:</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 176

`<span id="inspCountVal">961 / 1024 shots</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 177

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 178

`<div class="inspector-row">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 179

`<span>Empirical Probability:</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 180

`<span id="inspProbVal" style="color: var(--cyan);">93.8%</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 181

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 182

`<div class="inspector-row">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 183

`<span>Theoretical Target Match:</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 184

`<span id="inspTargetMatch" style="color: var(--green);">Yes (Marked State)</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 185

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 186

`<div class="inspector-row">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 187

`<span>Learner Prediction Match:</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 188

`<span id="inspPredMatch" style="color: var(--red);">No (Predicted |01⟩)</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 189

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 190

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 191

`(blank)`

Blank line used to separate nearby statements.
### Line 192

`<!-- MEASUREMENT HISTOGRAM (REQUIREMENT 3B) -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 193

`<div style="font-family: var(--font-mono); font-size: 11px; text-transform: uppercase; color: var(--text-muted); margin-top: 4px; display: flex; justify-content: space-between;">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 194

`<span>Empirical Measurement Distribution (Qiskit Aer)</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 195

`<span style="font-size: 10px; color: var(--cyan);">Click any bar to inspect</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 196

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 197

`<div class="hist-container" id="histogramContainer"></div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 198

`(blank)`

Blank line used to separate nearby statements.
### Line 199

`<div id="asciiCircuitContainer" style="display: none; margin-top: 8px;">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 200

`<div style="font-family: var(--font-mono); font-size: 11px; color: var(--text-muted); margin-bottom: 4px;">Verified Circuit Diagram (ASCII):</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 201

`<pre id="asciiCircuitDiagram" style="background: var(--bg); padding: 8px; border-radius: 6px; font-family: var(--font-mono); font-size: 10px; overflow-x: auto; color: var(--cyan);"></pre>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 202

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 203

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 204

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 205

`(blank)`

Blank line used to separate nearby statements.
### Line 206

`<!-- RIGHT PANE: Task Prompt, Learner Submission & M2 Adaptive Cognition (M1) -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 207

`<div class="pane pane-right">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 208

`<!-- 1. Active Task Card -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 209

`<div class="card" id="activityCard">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 210

`<div class="card-header">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 211

`<span class="card-title" id="activityTitle">Loading Activity...</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 212

`<span class="badge" id="activityConceptBadge">quantum</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 213

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 214

`<div style="font-size: 13px; color: var(--text); line-height: 1.5;" id="activityPrompt">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 215

`Loading task prompt...`

Text content rendered inside the nearest HTML element.
### Line 216

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 217

`(blank)`

Blank line used to separate nearby statements.
### Line 218

`<!-- Quantum Prediction Input (for prediction tasks - Requirement 7) -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 219

`<div id="predictionInputSection" style="display: none; flex-direction: column; gap: 8px;">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 220

`<label style="font-size: 11px; font-family: var(--font-mono); color: var(--text-muted);">Quick Select Basis State or Type:</label>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 221

`<div class="basis-pill-grid">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 222

`<button class="basis-pill" onclick="selectBasisPill('00')">|00⟩</button>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 223

`<button class="basis-pill" onclick="selectBasisPill('01')">|01⟩</button>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 224

`<button class="basis-pill" onclick="selectBasisPill('10')">|10⟩</button>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 225

`<button class="basis-pill" onclick="selectBasisPill('11')">|11⟩</button>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 226

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 227

`<div style="display: flex; gap: 8px;">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 228

`<input type="text" class="text-input" id="predictionField" value="01" placeholder="e.g. 01, 10" style="background: var(--bg); border: 1px solid var(--panel-border); color: var(--text); padding: 8px 12px; border-radius: 6px; font-family: var(--font-mono); font-size: 13px; flex: 1;">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 229

`<button class="btn" id="submitPredictionBtn" onclick="handleSubmitPrediction()">Run & Evaluate</button>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 230

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 231

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 232

`(blank)`

Blank line used to separate nearby statements.
### Line 233

`<!-- Submission Progress Indicator (Requirement 7) -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 234

`<div id="executionProgressBanner" class="execution-progress-bar" style="display: none;">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 235

`<span>⚡</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 236

`<span id="executionProgressText">Submitting prediction to M4 gateway...</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 237

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 238

`(blank)`

Blank line used to separate nearby statements.
### Line 239

`<!-- Conceptual Choice Options (for MCQ tasks) -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 240

`<div id="choiceInputSection" style="display: none; flex-direction: column; gap: 10px;">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 241

`<div class="options-grid" id="optionsContainer"></div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 242

`<button class="btn" id="submitChoiceBtn" onclick="handleSubmitChoice()">Submit Answer</button>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 243

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 244

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 245

`(blank)`

Blank line used to separate nearby statements.
### Line 246

`<!-- 2. Empirical Evidence & Learner Cognition Card -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 247

`<div class="card" id="evidenceOutcomeCard" style="display: none;">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 248

`<div class="card-header">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 249

`<span class="card-title">Learner Evidence & Cognitive State</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 250

`<span class="badge" id="outcomeBadge">Prediction Outcome</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 251

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 252

`(blank)`

Blank line used to separate nearby statements.
### Line 253

`<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px;">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 254

`<div class="stat-box" style="text-align: left; padding: 10px; background: var(--bg); border: 1px solid var(--panel-border); border-radius: 8px;">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 255

`<div class="stat-label">Cognitive Trajectory Trend</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 256

`<div class="stat-val" style="font-size: 13px; color: var(--purple);" id="trajectoryTrendDisplay">observing</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 257

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 258

`<div class="stat-box" style="text-align: left; padding: 10px; background: var(--bg); border: 1px solid var(--panel-border); border-radius: 8px;">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 259

`<div class="stat-label">Inference Confidence</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 260

`<div class="stat-val" style="font-size: 13px; color: var(--cyan);" id="confidenceBadgeDisplay">35%</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 261

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 262

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 263

`(blank)`

Blank line used to separate nearby statements.
### Line 264

`<div style="font-size: 12px; font-family: var(--font-mono); color: var(--text); background: var(--bg); padding: 10px; border-radius: 8px; border: 1px solid var(--panel-border); display: flex; flex-direction: column; gap: 6px;">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 265

`<div><strong style="color: var(--text-muted);">Evidence Sufficiency:</strong> <span style="color: var(--yellow);" id="evidenceSufficiencyDisplay">Insufficient (Gathering Observations)</span></div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 266

`<div><strong style="color: var(--text-muted);">Learner-State Hypothesis:</strong> <span style="color: var(--cyan);" id="inferredHypothesisDisplay">Preliminary difficulty observation</span></div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 267

`<div><strong style="color: var(--text-muted);">Latest Evidence Record:</strong> <span style="color: var(--text-muted);" id="evidenceIdDisplay">ev_001</span></div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 268

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 269

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 270

`(blank)`

Blank line used to separate nearby statements.
### Line 271

`<!-- 3. "WHY THIS NEXT?" ADAPTIVE DECISION TIMELINE (REQUIREMENT 4) -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 272

`<div class="card" id="adaptiveDecisionCard" style="display: none;">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 273

`<div class="card-header">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 274

`<span class="card-title">Why This Next? (Adaptive Recommendation)</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 275

`<span class="badge action" id="adaptiveActionBadge">gather_evidence</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 276

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 277

`(blank)`

Blank line used to separate nearby statements.
### Line 278

`<div class="causal-chain">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 279

`<!-- 1. Trigger -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 280

`<div class="chain-step" onclick="toggleChainStep(this)">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 281

`<div class="chain-node-header">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 282

`<div class="chain-node-title"><span>1. Decision Trigger</span></div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 283

`<span class="chain-toggle-icon">▶</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 284

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 285

`<div class="chain-node-val" id="decisionTriggerDisplay">Single Prediction Mismatch</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 286

`<div class="chain-node-desc" id="triggerDesc">Triggered because the learner's initial prediction mismatched the target outcome.</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 287

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 288

`<div class="chain-arrow">↓</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 289

`(blank)`

Blank line used to separate nearby statements.
### Line 290

`<!-- 2. Evidence Sufficiency -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 291

`<div class="chain-step" onclick="toggleChainStep(this)">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 292

`<div class="chain-node-header">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 293

`<div class="chain-node-title"><span>2. Evidence Sufficiency</span></div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 294

`<span class="chain-toggle-icon">▶</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 295

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 296

`<div class="chain-node-val highlight-yellow" id="chainSufficiencyDisplay">Insufficient (Gathering Observations)</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 297

`<div class="chain-node-desc" id="sufficiencyDesc">Single observations do not establish cognitive certainty; more evidence is required.</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 298

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 299

`<div class="chain-arrow">↓</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 300

`(blank)`

Blank line used to separate nearby statements.
### Line 301

`<!-- 3. Inferred Hypothesis -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 302

`<div class="chain-step" onclick="toggleChainStep(this)">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 303

`<div class="chain-node-header">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 304

`<div class="chain-node-title"><span>3. Inferred Learner-State Hypothesis</span></div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 305

`<span class="chain-toggle-icon">▶</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 306

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 307

`<div class="chain-node-val highlight-cyan" id="chainHypothesisDisplay">Preliminary difficulty observation</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 308

`<div class="chain-node-desc" id="hypothesisDesc">M2 cognitive model hypothesis representing estimated understanding.</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 309

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 310

`<div class="chain-arrow">↓</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 311

`(blank)`

Blank line used to separate nearby statements.
### Line 312

`<!-- 4. Supporting Evidence IDs -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 313

`<div class="chain-step" id="supportingEvidenceSection" onclick="toggleChainStep(this)">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 314

`<div class="chain-node-header">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 315

`<div class="chain-node-title"><span>4. Supporting Evidence Used</span></div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 316

`<span class="chain-toggle-icon">▶</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 317

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 318

`<div id="supportingEvidenceList" class="supporting-chips"></div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 319

`<div class="chain-node-desc">Direct audit trail of historical attempt evidence cited by M2.</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 320

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 321

`<div class="chain-arrow">↓</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 322

`(blank)`

Blank line used to separate nearby statements.
### Line 323

`<!-- 5. Decision & Pedagogical Rationale -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 324

`<div class="chain-step expanded" onclick="toggleChainStep(this)">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 325

`<div class="chain-node-header">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 326

`<div class="chain-node-title"><span>5. Pedagogical Action & Rationale</span></div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 327

`<span class="chain-toggle-icon">▶</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 328

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 329

`<p class="chain-reason" id="adaptiveReasonText">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 330

`Adaptive pedagogical rationale explaining why this action was selected.`

Text content rendered inside the nearest HTML element.
### Line 331

`</p>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 332

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 333

`<div class="chain-arrow">↓</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 334

`(blank)`

Blank line used to separate nearby statements.
### Line 335

`<!-- 6. Next Activity & Navigation -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 336

`<div class="chain-step next-step">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 337

`<div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 338

`<div class="chain-node-title">6. Next Recommended Activity</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 339

`<div class="next-activity-title" id="nextTargetActivityId">Grover 2-Qubit Target State Prediction</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 340

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 341

`<button class="btn success" id="continueNextBtn" onclick="handleContinueToTarget()">Continue →</button>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 342

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 343

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 344

`(blank)`

Blank line used to separate nearby statements.
### Line 345

`<div id="prereqGapCallout" style="display: none; margin-top: 6px; font-size: 12px; color: var(--yellow); background: rgba(245, 158, 11, 0.1); padding: 8px 12px; border-radius: 6px; border: 1px solid rgba(245, 158, 11, 0.3);">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 346

`⚠️ Prerequisite Gap Identified in Concept: <strong id="prereqGapName">Superposition</strong>`

Text content rendered inside the nearest HTML element.
### Line 347

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 348

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 349

`(blank)`

Blank line used to separate nearby statements.
### Line 350

`<!-- 4. Grounded AI Guidance Card (M5 - Requirement 8) -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 351

`<div class="card" id="aiGuidanceCard" style="display: none;">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 352

`<div class="card-header">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 353

`<span class="card-title">M5 Grounded AI Guidance</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 354

`<button class="btn secondary" style="padding: 4px 10px; font-size: 11px;" id="explainBtn" onclick="handleExplain()">Explain My Result</button>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 355

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 356

`<div style="font-size: 11px; font-family: var(--font-mono); color: var(--cyan); margin-bottom: 2px;">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 357

`💡 Grounded Guidance: M2 determined the adaptive learning path. M5 explains the underlying concept and verified evidence.`

Text content rendered inside the nearest HTML element.
### Line 358

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 359

`<div class="explanation-box" id="aiExplanationText">Click "Explain My Result" to generate an authoritative explanation grounded in the quantum curriculum.</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 360

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 361

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 362

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 363

`(blank)`

Blank line used to separate nearby statements.
### Line 364

`<!-- AI CONCEPTUAL ASK MODAL -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 365

`<div class="modal-overlay" id="askModal" style="display: none;">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 366

`<div class="modal-card">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 367

`<div class="card-header">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 368

`<span class="card-title">🤖 Ask Quantum AI Assistant</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 369

`<button class="btn secondary" style="padding: 2px 8px; font-size: 11px;" onclick="closeAskModal()">✕</button>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 370

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 371

`<p style="font-size: 12px; color: var(--text-muted);">Ask any conceptual question about qubits, states, superposition, quantum gates, or Grover's algorithm:</p>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 372

`<textarea id="askQuestionInput" rows="3" style="background: var(--bg); border: 1px solid var(--panel-border); color: var(--text); padding: 10px; border-radius: 8px; font-family: var(--font-body); font-size: 13px; resize: vertical;" placeholder="e.g. Why does Grover amplitude amplification over-rotate?"></textarea>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 373

`<button class="btn" id="askSubmitBtn" onclick="handleAskQuestion()">Inquire</button>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 374

`<div class="explanation-box" id="askAnswerBox" style="display: none; max-height: 180px;"></div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 375

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 376

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 377

`(blank)`

Blank line used to separate nearby statements.
### Line 378

`<!-- LEARNER PROFILE & SETTINGS MODAL -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 379

`<div class="modal-overlay" id="profileModal" style="display: none;">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 380

`<div class="modal-card profile-modal-card">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 381

`<div class="card-header">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 382

`<span class="card-title" id="profileModalTitle">Learner Profile</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 383

`<button class="btn secondary" style="padding: 2px 8px; font-size: 11px;" onclick="closeProfileModal()">✕</button>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 384

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 385

`(blank)`

Blank line used to separate nearby statements.
### Line 386

`<!-- VIEW 1: MENU -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 387

`<div class="profile-view active" id="profileView-menu">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 388

`<div class="profile-header-preview">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 389

`<div class="profile-avatar-large" id="profileAvatar">QE</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 390

`<div style="flex: 1;">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 391

`<div style="font-family: var(--font-display); font-size: 16px; font-weight: 700;" id="profileNameDisplay">Quantum Explorer</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 392

`<div style="font-size: 12px; color: var(--text-muted);" id="profileStudyingDisplay">Grover's Algorithm & Quantum State Triads</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 393

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 394

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 395

`(blank)`

Blank line used to separate nearby statements.
### Line 396

`<div class="menu-item" onclick="showProfileView('edit')">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 397

`<span>✏️ Edit Profile Details</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 398

`<span>→</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 399

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 400

`<div class="menu-item" onclick="showProfileView('settings')">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 401

`<span>⚙️ Preferences & Display Settings</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 402

`<span>→</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 403

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 404

`<div class="toggle-row" id="darkModeToggleRow" onclick="toggleThemeFromModal()">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 405

`<span style="font-size: 13px; font-weight: 500;">🌙 Theme Mode</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 406

`<div class="toggle on" id="darkModeToggle"></div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 407

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 408

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 409

`(blank)`

Blank line used to separate nearby statements.
### Line 410

`<!-- VIEW 2: EDIT PROFILE -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 411

`<div class="profile-view" id="profileView-edit">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 412

`<div style="font-size: 12px; font-family: var(--font-mono); color: var(--text-muted); margin-bottom: 8px;">CUSTOMIZE AVATAR & INFO:</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 413

`(blank)`

Blank line used to separate nearby statements.
### Line 414

`<label style="font-size: 11px; color: var(--text-muted); display: block; margin-bottom: 4px;">Upload Profile Photo / Avatar:</label>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 415

`<input type="file" id="avatarInput" accept="image/*" class="profile-input" style="padding: 6px;" />`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 416

`(blank)`

Blank line used to separate nearby statements.
### Line 417

`<label style="font-size: 11px; color: var(--text-muted); display: block; margin-bottom: 4px;">Display Name:</label>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 418

`<input type="text" id="nameInput" class="profile-input" value="Quantum Explorer" placeholder="Enter your name" />`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 419

`(blank)`

Blank line used to separate nearby statements.
### Line 420

`<label style="font-size: 11px; color: var(--text-muted); display: block; margin-bottom: 4px;">Learning Focus / Bio:</label>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 421

`<input type="text" id="studyingInput" class="profile-input" value="Grover's Algorithm & Quantum State Triads" placeholder="What are you studying?" />`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 422

`(blank)`

Blank line used to separate nearby statements.
### Line 423

`<div style="display: flex; gap: 8px; justify-content: flex-end;">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 424

`<button class="btn secondary" onclick="showProfileView('menu')">Back</button>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 425

`<button class="btn" onclick="saveProfileDetails()">Save Profile</button>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 426

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 427

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 428

`(blank)`

Blank line used to separate nearby statements.
### Line 429

`<!-- VIEW 3: SETTINGS -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 430

`<div class="profile-view" id="profileView-settings">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 431

`<div style="font-size: 12px; font-family: var(--font-mono); color: var(--text-muted); margin-bottom: 8px;">SESSION & PREFERENCES:</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 432

`(blank)`

Blank line used to separate nearby statements.
### Line 433

`<div class="menu-item" onclick="handleResetSession(); closeProfileModal();">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 434

`<span>🔄 Reset Active Learner Session</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 435

`<span style="font-size: 11px; color: var(--yellow);">Generate New ID</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 436

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 437

`(blank)`

Blank line used to separate nearby statements.
### Line 438

`<div style="padding: 10px; background: var(--bg); border: 1px solid var(--panel-border); border-radius: 8px; margin-bottom: 12px; font-size: 11px; font-family: var(--font-mono); color: var(--text-muted);">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 439

`💡 Active Learner State is managed securely in-memory by the M4 FastAPI Gateway.`

Text content rendered inside the nearest HTML element.
### Line 440

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 441

`(blank)`

Blank line used to separate nearby statements.
### Line 442

`<div style="display: flex; justify-content: flex-end;">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 443

`<button class="btn secondary" onclick="showProfileView('menu')">Back to Menu</button>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 444

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 445

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 446

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 447

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 448

`(blank)`

Blank line used to separate nearby statements.
### Line 449

`<script type="module">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 450

`import { fetchActivities, fetchActivity, submitPrediction, explainExperiment, askConceptualQuestion } from './js/api_client.js';`

Text content rendered inside the nearest HTML element.
### Line 451

`import { normalizeSubmissionResponse, formatStateLabel, formatPercentage, computeBadgeMetrics, getLearnerProfile, saveLearnerProfile } from './js/adapter.js';`

Text content rendered inside the nearest HTML element.
### Line 452

`import { CircuitStudio, GATE_DEFINITIONS } from './js/circuit_view.js';`

Text content rendered inside the nearest HTML element.
### Line 453

`(blank)`

Blank line used to separate nearby statements.
### Line 454

`let activitiesList = [];`

Text content rendered inside the nearest HTML element.
### Line 455

`let currentActivityId = "act_grover_2q_predict";`

Text content rendered inside the nearest HTML element.
### Line 456

`let currentActivityData = null;`

Text content rendered inside the nearest HTML element.
### Line 457

`let selectedOptionLetter = null;`

Text content rendered inside the nearest HTML element.
### Line 458

`let lastSubmitResult = null;`

Text content rendered inside the nearest HTML element.
### Line 459

`let normalizedModel = null;`

Text content rendered inside the nearest HTML element.
### Line 460

`let circuitStudio = null;`

Text content rendered inside the nearest HTML element.
### Line 461

`let currentLearnerState = {};`

Text content rendered inside the nearest HTML element.
### Line 462

`(blank)`

Blank line used to separate nearby statements.
### Line 463

`// -------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 464

`// 1. Particle Cloud Background Animation (Non-blocking & graceful)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 465

`// -------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 466

`function initBackgroundParticles() {`

Text content rendered inside the nearest HTML element.
### Line 467

`const canvas = document.getElementById('fx');`

Text content rendered inside the nearest HTML element.
### Line 468

`if (!canvas || !canvas.getContext) return;`

Text content rendered inside the nearest HTML element.
### Line 469

`const ctx = canvas.getContext('2d');`

Text content rendered inside the nearest HTML element.
### Line 470

`const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;`

Text content rendered inside the nearest HTML element.
### Line 471

`let w, h, particles;`

Text content rendered inside the nearest HTML element.
### Line 472

`(blank)`

Blank line used to separate nearby statements.
### Line 473

`function resize() {`

Text content rendered inside the nearest HTML element.
### Line 474

`w = canvas.width = window.innerWidth;`

Text content rendered inside the nearest HTML element.
### Line 475

`h = canvas.height = window.innerHeight;`

Text content rendered inside the nearest HTML element.
### Line 476

`}`

Text content rendered inside the nearest HTML element.
### Line 477

`(blank)`

Blank line used to separate nearby statements.
### Line 478

`function initParticles() {`

Text content rendered inside the nearest HTML element.
### Line 479

`const count = Math.min(65, Math.floor((w * h) / 22000));`

Text content rendered inside the nearest HTML element.
### Line 480

`particles = Array.from({ length: count }, () => ({`

Text content rendered inside the nearest HTML element.
### Line 481

`x: Math.random() * w,`

Text content rendered inside the nearest HTML element.
### Line 482

`y: Math.random() * h,`

Text content rendered inside the nearest HTML element.
### Line 483

`r: Math.random() * 1.5 + 0.5,`

Text content rendered inside the nearest HTML element.
### Line 484

`vx: (Math.random() - 0.5) * 0.15,`

Text content rendered inside the nearest HTML element.
### Line 485

`vy: (Math.random() - 0.5) * 0.15,`

Text content rendered inside the nearest HTML element.
### Line 486

`hue: Math.random() > 0.5 ? '59,130,246' : '34,211,238',`

Text content rendered inside the nearest HTML element.
### Line 487

`a: Math.random() * 0.45 + 0.15`

Text content rendered inside the nearest HTML element.
### Line 488

`}));`

Text content rendered inside the nearest HTML element.
### Line 489

`}`

Text content rendered inside the nearest HTML element.
### Line 490

`(blank)`

Blank line used to separate nearby statements.
### Line 491

`function draw() {`

Text content rendered inside the nearest HTML element.
### Line 492

`ctx.clearRect(0, 0, w, h);`

Text content rendered inside the nearest HTML element.
### Line 493

`particles.forEach(p => {`

Text content rendered inside the nearest HTML element.
### Line 494

`if (!reduceMotion) {`

Text content rendered inside the nearest HTML element.
### Line 495

`p.x += p.vx; p.y += p.vy;`

Text content rendered inside the nearest HTML element.
### Line 496

`if (p.x < 0) p.x = w; if (p.x > w) p.x = 0;`

Text content rendered inside the nearest HTML element.
### Line 497

`if (p.y < 0) p.y = h; if (p.y > h) p.y = 0;`

Text content rendered inside the nearest HTML element.
### Line 498

`}`

Text content rendered inside the nearest HTML element.
### Line 499

`ctx.beginPath();`

Text content rendered inside the nearest HTML element.
### Line 500

`ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);`

Text content rendered inside the nearest HTML element.
### Line 501

`ctx.fillStyle = \`rgba(${p.hue},${p.a})\`;`

Text content rendered inside the nearest HTML element.
### Line 502

`ctx.fill();`

Text content rendered inside the nearest HTML element.
### Line 503

`});`

Text content rendered inside the nearest HTML element.
### Line 504

`if (!reduceMotion) requestAnimationFrame(draw);`

Text content rendered inside the nearest HTML element.
### Line 505

`}`

Text content rendered inside the nearest HTML element.
### Line 506

`(blank)`

Blank line used to separate nearby statements.
### Line 507

`resize();`

Text content rendered inside the nearest HTML element.
### Line 508

`initParticles();`

Text content rendered inside the nearest HTML element.
### Line 509

`draw();`

Text content rendered inside the nearest HTML element.
### Line 510

`window.addEventListener('resize', () => { resize(); initParticles(); if (reduceMotion) draw(); });`

Text content rendered inside the nearest HTML element.
### Line 511

`}`

Text content rendered inside the nearest HTML element.
### Line 512

`initBackgroundParticles();`

Text content rendered inside the nearest HTML element.
### Line 513

`(blank)`

Blank line used to separate nearby statements.
### Line 514

`// -------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 515

`// 2. Mousemove Card Halo Glow`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 516

`// -------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 517

`document.querySelectorAll('.card, .circuit-studio').forEach(box => {`

Text content rendered inside the nearest HTML element.
### Line 518

`box.addEventListener('mousemove', e => {`

Text content rendered inside the nearest HTML element.
### Line 519

`const rect = box.getBoundingClientRect();`

Text content rendered inside the nearest HTML element.
### Line 520

`box.style.setProperty('--mx', \`${e.clientX - rect.left}px\`);`

Text content rendered inside the nearest HTML element.
### Line 521

`box.style.setProperty('--my', \`${e.clientY - rect.top}px\`);`

Text content rendered inside the nearest HTML element.
### Line 522

`});`

Text content rendered inside the nearest HTML element.
### Line 523

`});`

Text content rendered inside the nearest HTML element.
### Line 524

`(blank)`

Blank line used to separate nearby statements.
### Line 525

`// -------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 526

`// 3. Initialize Circuit Studio with gate selection hook`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 527

`// -------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 528

`circuitStudio = new CircuitStudio("circuitWireGrid", {`

Text content rendered inside the nearest HTML element.
### Line 529

`numQubits: 2,`

Text content rendered inside the nearest HTML element.
### Line 530

`numColumns: 6,`

Text content rendered inside the nearest HTML element.
### Line 531

`onGateSelect: (gate) => {`

Text content rendered inside the nearest HTML element.
### Line 532

`if (gate && GATE_DEFINITIONS[gate.type]) {`

Text content rendered inside the nearest HTML element.
### Line 533

`const info = GATE_DEFINITIONS[gate.type];`

Text content rendered inside the nearest HTML element.
### Line 534

`document.getElementById("gateInfoDisplay").innerHTML = \`<span><strong>${info.name} Gate:</strong> ${info.desc}</span>\`;`

Text content rendered inside the nearest HTML element.
### Line 535

`}`

Text content rendered inside the nearest HTML element.
### Line 536

`}`

Text content rendered inside the nearest HTML element.
### Line 537

`});`

Text content rendered inside the nearest HTML element.
### Line 538

`circuitStudio.loadPreset("grover_2q");`

Text content rendered inside the nearest HTML element.
### Line 539

`(blank)`

Blank line used to separate nearby statements.
### Line 540

`// KaTeX Helper Function`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 541

`function renderMath(element) {`

Text content rendered inside the nearest HTML element.
### Line 542

`if (typeof renderMathInElement === "function" && element) {`

Text content rendered inside the nearest HTML element.
### Line 543

`renderMathInElement(element, {`

Text content rendered inside the nearest HTML element.
### Line 544

`delimiters: [`

Text content rendered inside the nearest HTML element.
### Line 545

`{ left: "$$", right: "$$", display: true },`

Text content rendered inside the nearest HTML element.
### Line 546

`{ left: "$", right: "$", display: false }`

Text content rendered inside the nearest HTML element.
### Line 547

`],`

Text content rendered inside the nearest HTML element.
### Line 548

`throwOnError: false`

Text content rendered inside the nearest HTML element.
### Line 549

`});`

Text content rendered inside the nearest HTML element.
### Line 550

`}`

Text content rendered inside the nearest HTML element.
### Line 551

`}`

Text content rendered inside the nearest HTML element.
### Line 552

`(blank)`

Blank line used to separate nearby statements.
### Line 553

`// Safe Lightweight Markdown Formatter for AI Guidance`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 554

`function formatGroundedMarkdown(rawText) {`

Text content rendered inside the nearest HTML element.
### Line 555

`if (!rawText) return "";`

Text content rendered inside the nearest HTML element.
### Line 556

`// 1. Escape HTML special characters for XSS safety`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 557

`const escaped = String(rawText)`

Text content rendered inside the nearest HTML element.
### Line 558

`.replace(/&/g, "&amp;")`

Text content rendered inside the nearest HTML element.
### Line 559

`.replace(/</g, "&lt;")`

Text content rendered inside the nearest HTML element.
### Line 560

`.replace(/>/g, "&gt;");`

Text content rendered inside the nearest HTML element.
### Line 561

`(blank)`

Blank line used to separate nearby statements.
### Line 562

`// 2. Parse lines into structured semantic elements`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 563

`const lines = escaped.split("\n");`

Text content rendered inside the nearest HTML element.
### Line 564

`let html = "";`

Text content rendered inside the nearest HTML element.
### Line 565

`let inList = false;`

Text content rendered inside the nearest HTML element.
### Line 566

`(blank)`

Blank line used to separate nearby statements.
### Line 567

`for (let i = 0; i < lines.length; i++) {`

Text content rendered inside the nearest HTML element.
### Line 568

`const line = lines[i].trim();`

Text content rendered inside the nearest HTML element.
### Line 569

`if (!line) {`

Text content rendered inside the nearest HTML element.
### Line 570

`if (inList) { html += "</ul>"; inList = false; }`

Text content rendered inside the nearest HTML element.
### Line 571

`continue;`

Text content rendered inside the nearest HTML element.
### Line 572

`}`

Text content rendered inside the nearest HTML element.
### Line 573

`(blank)`

Blank line used to separate nearby statements.
### Line 574

`if (line.startsWith("### ")) {`

Text content rendered inside the nearest HTML element.
### Line 575

`if (inList) { html += "</ul>"; inList = false; }`

Text content rendered inside the nearest HTML element.
### Line 576

`html += \`<h4 class="ai-heading">${line.slice(4)}</h4>\`;`

Text content rendered inside the nearest HTML element.
### Line 577

`} else if (line.startsWith("## ")) {`

Text content rendered inside the nearest HTML element.
### Line 578

`if (inList) { html += "</ul>"; inList = false; }`

Text content rendered inside the nearest HTML element.
### Line 579

`html += \`<h3 class="ai-heading-large">${line.slice(3)}</h3>\`;`

Text content rendered inside the nearest HTML element.
### Line 580

`} else if (line.startsWith("- ") || line.startsWith("* ")) {`

Text content rendered inside the nearest HTML element.
### Line 581

`if (!inList) { html += \`<ul class="ai-list">\`; inList = true; }`

Text content rendered inside the nearest HTML element.
### Line 582

`let item = line.slice(2)`

Text content rendered inside the nearest HTML element.
### Line 583

`.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')`

Text content rendered inside the nearest HTML element.
### Line 584

`.replace(/\`([^\`]+)\`/g, '<code class="ai-inline-code">$1</code>');`

Text content rendered inside the nearest HTML element.
### Line 585

`html += \`<li>${item}</li>\`;`

Text content rendered inside the nearest HTML element.
### Line 586

`} else if (/^\d+\.\s/.test(line)) {`

Text content rendered inside the nearest HTML element.
### Line 587

`if (inList) { html += "</ul>"; inList = false; }`

Text content rendered inside the nearest HTML element.
### Line 588

`let item = line.replace(/^\d+\.\s/, '')`

Text content rendered inside the nearest HTML element.
### Line 589

`.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')`

Text content rendered inside the nearest HTML element.
### Line 590

`.replace(/\`([^\`]+)\`/g, '<code class="ai-inline-code">$1</code>');`

Text content rendered inside the nearest HTML element.
### Line 591

`html += \`<div class="ai-ordered-item">${item}</div>\`;`

Text content rendered inside the nearest HTML element.
### Line 592

`} else {`

Text content rendered inside the nearest HTML element.
### Line 593

`if (inList) { html += "</ul>"; inList = false; }`

Text content rendered inside the nearest HTML element.
### Line 594

`let para = line`

Text content rendered inside the nearest HTML element.
### Line 595

`.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')`

Text content rendered inside the nearest HTML element.
### Line 596

`.replace(/\`([^\`]+)\`/g, '<code class="ai-inline-code">$1</code>');`

Text content rendered inside the nearest HTML element.
### Line 597

`html += \`<p class="ai-para">${para}</p>\`;`

Text content rendered inside the nearest HTML element.
### Line 598

`}`

Text content rendered inside the nearest HTML element.
### Line 599

`}`

Text content rendered inside the nearest HTML element.
### Line 600

`if (inList) { html += "</ul>"; }`

Text content rendered inside the nearest HTML element.
### Line 601

`return html;`

Text content rendered inside the nearest HTML element.
### Line 602

`}`

Text content rendered inside the nearest HTML element.
### Line 603

`(blank)`

Blank line used to separate nearby statements.
### Line 604

`// -------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 605

`// 4. Progress Updater (M2-driven)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 606

`// -------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 607

`function updateBadgeDisplays(learnerState = {}) {`

Text content rendered inside the nearest HTML element.
### Line 608

`const metrics = computeBadgeMetrics(learnerState, activitiesList);`

Text content rendered inside the nearest HTML element.
### Line 609

`const masteryEl = document.getElementById("badgeMastery");`

Text content rendered inside the nearest HTML element.
### Line 610

`if (masteryEl) masteryEl.textContent = \`${metrics.completedCount}/${metrics.totalCount}\`;`

Text content rendered inside the nearest HTML element.
### Line 611

`}`

Text content rendered inside the nearest HTML element.
### Line 612

`(blank)`

Blank line used to separate nearby statements.
### Line 613

`// -------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 614

`// 5. Learner Profile & Modal Handlers`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 615

`// -------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 616

`window.openProfileModal = function() {`

Text content rendered inside the nearest HTML element.
### Line 617

`const modal = document.getElementById("profileModal");`

Text content rendered inside the nearest HTML element.
### Line 618

`modal.style.display = "flex";`

Text content rendered inside the nearest HTML element.
### Line 619

`showProfileView('menu');`

Text content rendered inside the nearest HTML element.
### Line 620

`};`

Text content rendered inside the nearest HTML element.
### Line 621

`(blank)`

Blank line used to separate nearby statements.
### Line 622

`window.closeProfileModal = function() {`

Text content rendered inside the nearest HTML element.
### Line 623

`document.getElementById("profileModal").style.display = "none";`

Text content rendered inside the nearest HTML element.
### Line 624

`};`

Text content rendered inside the nearest HTML element.
### Line 625

`(blank)`

Blank line used to separate nearby statements.
### Line 626

`const profileTitles = { menu: 'Learner Profile', edit: 'Edit Profile Details', settings: 'Preferences & Settings' };`

Text content rendered inside the nearest HTML element.
### Line 627

`window.showProfileView = function(view) {`

Text content rendered inside the nearest HTML element.
### Line 628

`document.querySelectorAll('.profile-view').forEach(v => v.classList.remove('active'));`

Text content rendered inside the nearest HTML element.
### Line 629

`const targetView = document.getElementById(\`profileView-${view}\`);`

Text content rendered inside the nearest HTML element.
### Line 630

`if (targetView) targetView.classList.add('active');`

Text content rendered inside the nearest HTML element.
### Line 631

`const titleEl = document.getElementById('profileModalTitle');`

Text content rendered inside the nearest HTML element.
### Line 632

`if (titleEl) titleEl.textContent = profileTitles[view] || 'Learner Profile';`

Text content rendered inside the nearest HTML element.
### Line 633

`};`

Text content rendered inside the nearest HTML element.
### Line 634

`(blank)`

Blank line used to separate nearby statements.
### Line 635

`function loadProfileOnBoot() {`

Text content rendered inside the nearest HTML element.
### Line 636

`const learnerId = document.getElementById("learnerIdInput").value.trim() || "demo_learner";`

Text content rendered inside the nearest HTML element.
### Line 637

`const profile = getLearnerProfile(learnerId);`

Text content rendered inside the nearest HTML element.
### Line 638

`(blank)`

Blank line used to separate nearby statements.
### Line 639

`const nameDisp = document.getElementById("profileNameDisplay");`

Text content rendered inside the nearest HTML element.
### Line 640

`const studyDisp = document.getElementById("profileStudyingDisplay");`

Text content rendered inside the nearest HTML element.
### Line 641

`const nameInp = document.getElementById("nameInput");`

Text content rendered inside the nearest HTML element.
### Line 642

`const studyInp = document.getElementById("studyingInput");`

Text content rendered inside the nearest HTML element.
### Line 643

`const avatarEl = document.getElementById("profileAvatar");`

Text content rendered inside the nearest HTML element.
### Line 644

`const openBtn = document.getElementById("profileOpenBtn");`

Text content rendered inside the nearest HTML element.
### Line 645

`(blank)`

Blank line used to separate nearby statements.
### Line 646

`if (nameDisp) nameDisp.textContent = profile.name;`

Text content rendered inside the nearest HTML element.
### Line 647

`if (studyDisp) studyDisp.textContent = profile.studying;`

Text content rendered inside the nearest HTML element.
### Line 648

`if (nameInp) nameInp.value = profile.name;`

Text content rendered inside the nearest HTML element.
### Line 649

`if (studyInp) studyInp.value = profile.studying;`

Text content rendered inside the nearest HTML element.
### Line 650

`(blank)`

Blank line used to separate nearby statements.
### Line 651

`if (profile.avatar) {`

Text content rendered inside the nearest HTML element.
### Line 652

`if (avatarEl) { avatarEl.style.backgroundImage = \`url(${profile.avatar})\`; avatarEl.textContent = ''; }`

Text content rendered inside the nearest HTML element.
### Line 653

`if (openBtn) { openBtn.style.backgroundImage = \`url(${profile.avatar})\`; openBtn.textContent = ''; }`

Text content rendered inside the nearest HTML element.
### Line 654

`} else {`

Text content rendered inside the nearest HTML element.
### Line 655

`const initials = profile.name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase() || 'QE';`

Text content rendered inside the nearest HTML element.
### Line 656

`if (avatarEl) { avatarEl.style.backgroundImage = ''; avatarEl.textContent = initials; }`

Text content rendered inside the nearest HTML element.
### Line 657

`if (openBtn) { openBtn.style.backgroundImage = ''; openBtn.textContent = initials; }`

Text content rendered inside the nearest HTML element.
### Line 658

`}`

Text content rendered inside the nearest HTML element.
### Line 659

`(blank)`

Blank line used to separate nearby statements.
### Line 660

`// Apply theme preference`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 661

`const isDark = profile.theme !== "light";`

Text content rendered inside the nearest HTML element.
### Line 662

`document.documentElement.setAttribute("data-theme", isDark ? "dark" : "light");`

Text content rendered inside the nearest HTML element.
### Line 663

`const toggle = document.getElementById("darkModeToggle");`

Text content rendered inside the nearest HTML element.
### Line 664

`if (toggle) toggle.classList.toggle("on", isDark);`

Text content rendered inside the nearest HTML element.
### Line 665

`}`

Text content rendered inside the nearest HTML element.
### Line 666

`(blank)`

Blank line used to separate nearby statements.
### Line 667

`window.saveProfileDetails = function() {`

Text content rendered inside the nearest HTML element.
### Line 668

`const learnerId = document.getElementById("learnerIdInput").value.trim() || "demo_learner";`

Text content rendered inside the nearest HTML element.
### Line 669

`const profile = getLearnerProfile(learnerId);`

Text content rendered inside the nearest HTML element.
### Line 670

`profile.name = document.getElementById("nameInput").value.trim() || profile.name;`

Text content rendered inside the nearest HTML element.
### Line 671

`profile.studying = document.getElementById("studyingInput").value.trim() || profile.studying;`

Text content rendered inside the nearest HTML element.
### Line 672

`saveLearnerProfile(learnerId, profile);`

Text content rendered inside the nearest HTML element.
### Line 673

`loadProfileOnBoot();`

Text content rendered inside the nearest HTML element.
### Line 674

`showProfileView('menu');`

Text content rendered inside the nearest HTML element.
### Line 675

`};`

Text content rendered inside the nearest HTML element.
### Line 676

`(blank)`

Blank line used to separate nearby statements.
### Line 677

`// Avatar File Input Change Listener`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 678

`const avatarInput = document.getElementById('avatarInput');`

Text content rendered inside the nearest HTML element.
### Line 679

`if (avatarInput) {`

Text content rendered inside the nearest HTML element.
### Line 680

`avatarInput.addEventListener('change', () => {`

Text content rendered inside the nearest HTML element.
### Line 681

`const file = avatarInput.files[0];`

Text content rendered inside the nearest HTML element.
### Line 682

`if (!file) return;`

Text content rendered inside the nearest HTML element.
### Line 683

`const reader = new FileReader();`

Text content rendered inside the nearest HTML element.
### Line 684

`reader.onload = e => {`

Text content rendered inside the nearest HTML element.
### Line 685

`const learnerId = document.getElementById("learnerIdInput").value.trim() || "demo_learner";`

Text content rendered inside the nearest HTML element.
### Line 686

`const profile = getLearnerProfile(learnerId);`

Text content rendered inside the nearest HTML element.
### Line 687

`profile.avatar = e.target.result;`

Text content rendered inside the nearest HTML element.
### Line 688

`saveLearnerProfile(learnerId, profile);`

Text content rendered inside the nearest HTML element.
### Line 689

`loadProfileOnBoot();`

Text content rendered inside the nearest HTML element.
### Line 690

`};`

Text content rendered inside the nearest HTML element.
### Line 691

`reader.readAsDataURL(file);`

Text content rendered inside the nearest HTML element.
### Line 692

`});`

Text content rendered inside the nearest HTML element.
### Line 693

`}`

Text content rendered inside the nearest HTML element.
### Line 694

`(blank)`

Blank line used to separate nearby statements.
### Line 695

`window.toggleThemeFromModal = function() {`

Text content rendered inside the nearest HTML element.
### Line 696

`const html = document.documentElement;`

Text content rendered inside the nearest HTML element.
### Line 697

`const isDark = html.getAttribute("data-theme") === "dark";`

Text content rendered inside the nearest HTML element.
### Line 698

`const newTheme = isDark ? "light" : "dark";`

Text content rendered inside the nearest HTML element.
### Line 699

`html.setAttribute("data-theme", newTheme);`

Text content rendered inside the nearest HTML element.
### Line 700

`const toggle = document.getElementById("darkModeToggle");`

Text content rendered inside the nearest HTML element.
### Line 701

`if (toggle) toggle.classList.toggle("on", !isDark);`

Text content rendered inside the nearest HTML element.
### Line 702

`(blank)`

Blank line used to separate nearby statements.
### Line 703

`const learnerId = document.getElementById("learnerIdInput").value.trim() || "demo_learner";`

Text content rendered inside the nearest HTML element.
### Line 704

`const profile = getLearnerProfile(learnerId);`

Text content rendered inside the nearest HTML element.
### Line 705

`profile.theme = newTheme;`

Text content rendered inside the nearest HTML element.
### Line 706

`saveLearnerProfile(learnerId, profile);`

Text content rendered inside the nearest HTML element.
### Line 707

`};`

Text content rendered inside the nearest HTML element.
### Line 708

`(blank)`

Blank line used to separate nearby statements.
### Line 709

`// -------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 710

`// 6. Global Functions for Toolbar & Interactions`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 711

`// -------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 712

`window.selectGate = function(type) {`

Text content rendered inside the nearest HTML element.
### Line 713

`circuitStudio.setTool(type);`

Text content rendered inside the nearest HTML element.
### Line 714

`document.querySelectorAll(".gate-btn").forEach(b => b.classList.remove("active-tool"));`

Text content rendered inside the nearest HTML element.
### Line 715

`event.target.classList.add("active-tool");`

Text content rendered inside the nearest HTML element.
### Line 716

`document.getElementById("activeToolDisplay").textContent = type;`

Text content rendered inside the nearest HTML element.
### Line 717

`if (GATE_DEFINITIONS[type]) {`

Text content rendered inside the nearest HTML element.
### Line 718

`const def = GATE_DEFINITIONS[type];`

Text content rendered inside the nearest HTML element.
### Line 719

`document.getElementById("gateInfoDisplay").innerHTML = \`<span><strong>${def.name} (${type}):</strong> ${def.desc} • <code>${def.matrix}</code></span>\`;`

Text content rendered inside the nearest HTML element.
### Line 720

`}`

Text content rendered inside the nearest HTML element.
### Line 721

`};`

Text content rendered inside the nearest HTML element.
### Line 722

`window.addStudioQubit = function() { circuitStudio.addQubit(); };`

Text content rendered inside the nearest HTML element.
### Line 723

`window.clearStudioCircuit = function() { circuitStudio.clear(); };`

Text content rendered inside the nearest HTML element.
### Line 724

`window.loadCircuitPreset = function(name) { circuitStudio.loadPreset(name); };`

Text content rendered inside the nearest HTML element.
### Line 725

`(blank)`

Blank line used to separate nearby statements.
### Line 726

`window.selectBasisPill = function(basis) {`

Text content rendered inside the nearest HTML element.
### Line 727

`document.querySelectorAll(".basis-pill").forEach(p => p.classList.remove("selected"));`

Text content rendered inside the nearest HTML element.
### Line 728

`event.target.classList.add("selected");`

Text content rendered inside the nearest HTML element.
### Line 729

`document.getElementById("predictionField").value = basis;`

Text content rendered inside the nearest HTML element.
### Line 730

`};`

Text content rendered inside the nearest HTML element.
### Line 731

`(blank)`

Blank line used to separate nearby statements.
### Line 732

`window.toggleChainStep = function(stepElement) {`

Text content rendered inside the nearest HTML element.
### Line 733

`stepElement.classList.toggle("expanded");`

Text content rendered inside the nearest HTML element.
### Line 734

`};`

Text content rendered inside the nearest HTML element.
### Line 735

`(blank)`

Blank line used to separate nearby statements.
### Line 736

`window.toggleComparePanel = function() {`

Text content rendered inside the nearest HTML element.
### Line 737

`const panel = document.getElementById("comparePanel");`

Text content rendered inside the nearest HTML element.
### Line 738

`panel.style.display = panel.style.display === "none" ? "flex" : "none";`

Text content rendered inside the nearest HTML element.
### Line 739

`};`

Text content rendered inside the nearest HTML element.
### Line 740

`(blank)`

Blank line used to separate nearby statements.
### Line 741

`window.inspectState = function(stateObj) {`

Text content rendered inside the nearest HTML element.
### Line 742

`if (!stateObj || !normalizedModel) return;`

Text content rendered inside the nearest HTML element.
### Line 743

`const drawer = document.getElementById("stateInspectorDrawer");`

Text content rendered inside the nearest HTML element.
### Line 744

`drawer.style.display = "flex";`

Text content rendered inside the nearest HTML element.
### Line 745

`document.getElementById("inspStateName").textContent = stateObj.stateLabel;`

Text content rendered inside the nearest HTML element.
### Line 746

`document.getElementById("inspCountVal").textContent = \`${stateObj.count} / ${normalizedModel.quantum.shots} shots\`;`

Text content rendered inside the nearest HTML element.
### Line 747

`document.getElementById("inspProbVal").textContent = stateObj.percentageStr;`

Text content rendered inside the nearest HTML element.
### Line 748

`document.getElementById("inspTargetMatch").textContent = stateObj.isTarget ? "Yes (Marked Target State)" : "No";`

Text content rendered inside the nearest HTML element.
### Line 749

`document.getElementById("inspTargetMatch").style.color = stateObj.isTarget ? "var(--green)" : "var(--text-muted)";`

Text content rendered inside the nearest HTML element.
### Line 750

`document.getElementById("inspPredMatch").textContent = stateObj.isPredicted ? \`Yes (Predicted ${stateObj.stateLabel})\` : \`No (Learner predicted ${normalizedModel.learner.predictionLabel})\`;`

Text content rendered inside the nearest HTML element.
### Line 751

`document.getElementById("inspPredMatch").style.color = stateObj.isPredicted ? "var(--yellow)" : "var(--text-muted)";`

Text content rendered inside the nearest HTML element.
### Line 752

`};`

Text content rendered inside the nearest HTML element.
### Line 753

`(blank)`

Blank line used to separate nearby statements.
### Line 754

`window.inspectStateFromTriad = function(type) {`

Text content rendered inside the nearest HTML element.
### Line 755

`if (!normalizedModel || !normalizedModel.quantum) return;`

Text content rendered inside the nearest HTML element.
### Line 756

`if (type === "target") {`

Text content rendered inside the nearest HTML element.
### Line 757

`const bar = normalizedModel.quantum.probabilityBars.find(b => b.isTarget);`

Text content rendered inside the nearest HTML element.
### Line 758

`if (bar) inspectState(bar);`

Text content rendered inside the nearest HTML element.
### Line 759

`} else if (type === "measured") {`

Text content rendered inside the nearest HTML element.
### Line 760

`const bar = normalizedModel.quantum.probabilityBars.find(b => b.isMostLikely);`

Text content rendered inside the nearest HTML element.
### Line 761

`if (bar) inspectState(bar);`

Text content rendered inside the nearest HTML element.
### Line 762

`} else if (type === "prediction") {`

Text content rendered inside the nearest HTML element.
### Line 763

`const bar = normalizedModel.quantum.probabilityBars.find(b => b.isPredicted);`

Text content rendered inside the nearest HTML element.
### Line 764

`if (bar) inspectState(bar);`

Text content rendered inside the nearest HTML element.
### Line 765

`}`

Text content rendered inside the nearest HTML element.
### Line 766

`};`

Text content rendered inside the nearest HTML element.
### Line 767

`(blank)`

Blank line used to separate nearby statements.
### Line 768

`window.closeStateInspector = function() {`

Text content rendered inside the nearest HTML element.
### Line 769

`document.getElementById("stateInspectorDrawer").style.display = "none";`

Text content rendered inside the nearest HTML element.
### Line 770

`};`

Text content rendered inside the nearest HTML element.
### Line 771

`(blank)`

Blank line used to separate nearby statements.
### Line 772

`window.closeErrorBanner = function() {`

Text content rendered inside the nearest HTML element.
### Line 773

`document.getElementById("errorNotificationBanner").style.display = "none";`

Text content rendered inside the nearest HTML element.
### Line 774

`};`

Text content rendered inside the nearest HTML element.
### Line 775

`(blank)`

Blank line used to separate nearby statements.
### Line 776

`function showError(message) {`

Text content rendered inside the nearest HTML element.
### Line 777

`const banner = document.getElementById("errorNotificationBanner");`

Text content rendered inside the nearest HTML element.
### Line 778

`document.getElementById("errorBannerMessage").textContent = message;`

Text content rendered inside the nearest HTML element.
### Line 779

`banner.style.display = "flex";`

Text content rendered inside the nearest HTML element.
### Line 780

`}`

Text content rendered inside the nearest HTML element.
### Line 781

`(blank)`

Blank line used to separate nearby statements.
### Line 782

`function initLearnerId() {`

Text content rendered inside the nearest HTML element.
### Line 783

`let savedId = null;`

Text content rendered inside the nearest HTML element.
### Line 784

`try {`

Text content rendered inside the nearest HTML element.
### Line 785

`savedId = localStorage.getItem("qbit_current_learner_id");`

Text content rendered inside the nearest HTML element.
### Line 786

`} catch {}`

Text content rendered inside the nearest HTML element.
### Line 787

`(blank)`

Blank line used to separate nearby statements.
### Line 788

`if (!savedId) {`

Text content rendered inside the nearest HTML element.
### Line 789

`const uuid = (typeof crypto !== "undefined" && crypto.randomUUID)`

Text content rendered inside the nearest HTML element.
### Line 790

`? crypto.randomUUID()`

Text content rendered inside the nearest HTML element.
### Line 791

`: Math.random().toString(36).substring(2, 10);`

Text content rendered inside the nearest HTML element.
### Line 792

`savedId = \`learner_${uuid}\`;`

Text content rendered inside the nearest HTML element.
### Line 793

`try {`

Text content rendered inside the nearest HTML element.
### Line 794

`localStorage.setItem("qbit_current_learner_id", savedId);`

Text content rendered inside the nearest HTML element.
### Line 795

`} catch {}`

Text content rendered inside the nearest HTML element.
### Line 796

`}`

Text content rendered inside the nearest HTML element.
### Line 797

`const inputEl = document.getElementById("learnerIdInput");`

Text content rendered inside the nearest HTML element.
### Line 798

`if (inputEl) {`

Text content rendered inside the nearest HTML element.
### Line 799

`inputEl.value = savedId;`

Text content rendered inside the nearest HTML element.
### Line 800

`}`

Text content rendered inside the nearest HTML element.
### Line 801

`}`

Text content rendered inside the nearest HTML element.
### Line 802

`(blank)`

Blank line used to separate nearby statements.
### Line 803

`window.handleResetSession = function() {`

Text content rendered inside the nearest HTML element.
### Line 804

`const uuid = (typeof crypto !== "undefined" && crypto.randomUUID)`

Text content rendered inside the nearest HTML element.
### Line 805

`? crypto.randomUUID()`

Text content rendered inside the nearest HTML element.
### Line 806

`: Math.random().toString(36).substring(2, 10);`

Text content rendered inside the nearest HTML element.
### Line 807

`const newLearnerId = \`learner_${uuid}\`;`

Text content rendered inside the nearest HTML element.
### Line 808

`const inputEl = document.getElementById("learnerIdInput");`

Text content rendered inside the nearest HTML element.
### Line 809

`if (inputEl) {`

Text content rendered inside the nearest HTML element.
### Line 810

`inputEl.value = newLearnerId;`

Text content rendered inside the nearest HTML element.
### Line 811

`}`

Text content rendered inside the nearest HTML element.
### Line 812

`try {`

Text content rendered inside the nearest HTML element.
### Line 813

`localStorage.setItem("qbit_current_learner_id", newLearnerId);`

Text content rendered inside the nearest HTML element.
### Line 814

`} catch {}`

Text content rendered inside the nearest HTML element.
### Line 815

`loadProfileOnBoot();`

Text content rendered inside the nearest HTML element.
### Line 816

`loadActivity("act_grover_2q_predict");`

Text content rendered inside the nearest HTML element.
### Line 817

`};`

Text content rendered inside the nearest HTML element.
### Line 818

`(blank)`

Blank line used to separate nearby statements.
### Line 819

`// -------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 820

`// 7. App Initialization & Curriculum Loading`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 821

`// -------------------------------------------------------------------`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 822

`async function initApp() {`

Text content rendered inside the nearest HTML element.
### Line 823

`try {`

Text content rendered inside the nearest HTML element.
### Line 824

`initLearnerId();`

Text content rendered inside the nearest HTML element.
### Line 825

`activitiesList = await fetchActivities();`

Text content rendered inside the nearest HTML element.
### Line 826

`renderJourneyTrack();`

Text content rendered inside the nearest HTML element.
### Line 827

`loadProfileOnBoot();`

Text content rendered inside the nearest HTML element.
### Line 828

`updateBadgeDisplays({});`

Text content rendered inside the nearest HTML element.
### Line 829

`await loadActivity(currentActivityId);`

Text content rendered inside the nearest HTML element.
### Line 830

`} catch (err) {`

Text content rendered inside the nearest HTML element.
### Line 831

`console.error("Failed to load initial activities:", err);`

Text content rendered inside the nearest HTML element.
### Line 832

`showError(\`Failed to load activities: ${err.message}\`);`

Text content rendered inside the nearest HTML element.
### Line 833

`document.getElementById("activityTitle").textContent = "Grover 2-Qubit Prediction";`

Text content rendered inside the nearest HTML element.
### Line 834

`document.getElementById("predictionInputSection").style.display = "flex";`

Text content rendered inside the nearest HTML element.
### Line 835

`}`

Text content rendered inside the nearest HTML element.
### Line 836

`}`

Text content rendered inside the nearest HTML element.
### Line 837

`(blank)`

Blank line used to separate nearby statements.
### Line 838

`function renderJourneyTrack() {`

Text content rendered inside the nearest HTML element.
### Line 839

`const container = document.getElementById("journeySteps");`

Text content rendered inside the nearest HTML element.
### Line 840

`container.innerHTML = "";`

Text content rendered inside the nearest HTML element.
### Line 841

`const curIdx = activitiesList.findIndex(a => a.activity_id === currentActivityId);`

Text content rendered inside the nearest HTML element.
### Line 842

`document.getElementById("journeyProgressBadge").textContent = \`Step ${curIdx >= 0 ? curIdx + 1 : 1} of ${activitiesList.length || 4}\`;`

Text content rendered inside the nearest HTML element.
### Line 843

`(blank)`

Blank line used to separate nearby statements.
### Line 844

`activitiesList.forEach((act, idx) => {`

Text content rendered inside the nearest HTML element.
### Line 845

`const node = document.createElement("div");`

Text content rendered inside the nearest HTML element.
### Line 846

`const isCur = act.activity_id === currentActivityId;`

Text content rendered inside the nearest HTML element.
### Line 847

`const isCompleted = idx < curIdx;`

Text content rendered inside the nearest HTML element.
### Line 848

`node.className = \`journey-node ${isCur ? 'active' : ''} ${isCompleted ? 'completed' : ''}\`;`

Text content rendered inside the nearest HTML element.
### Line 849

`node.innerHTML = \`<span>${idx + 1}.</span> <span>${act.title.split(' ')[0]}</span>\`;`

Text content rendered inside the nearest HTML element.
### Line 850

`node.title = act.title;`

Text content rendered inside the nearest HTML element.
### Line 851

`node.onclick = () => loadActivity(act.activity_id);`

Text content rendered inside the nearest HTML element.
### Line 852

`container.appendChild(node);`

Text content rendered inside the nearest HTML element.
### Line 853

`(blank)`

Blank line used to separate nearby statements.
### Line 854

`if (idx < activitiesList.length - 1) {`

Text content rendered inside the nearest HTML element.
### Line 855

`const arr = document.createElement("span");`

Text content rendered inside the nearest HTML element.
### Line 856

`arr.className = "journey-arrow";`

Text content rendered inside the nearest HTML element.
### Line 857

`arr.textContent = "→";`

Text content rendered inside the nearest HTML element.
### Line 858

`container.appendChild(arr);`

Text content rendered inside the nearest HTML element.
### Line 859

`}`

Text content rendered inside the nearest HTML element.
### Line 860

`});`

Text content rendered inside the nearest HTML element.
### Line 861

`}`

Text content rendered inside the nearest HTML element.
### Line 862

`(blank)`

Blank line used to separate nearby statements.
### Line 863

`window.loadActivity = async function(activityId) {`

Text content rendered inside the nearest HTML element.
### Line 864

`currentActivityId = activityId;`

Text content rendered inside the nearest HTML element.
### Line 865

`renderJourneyTrack();`

Text content rendered inside the nearest HTML element.
### Line 866

`closeErrorBanner();`

Text content rendered inside the nearest HTML element.
### Line 867

`(blank)`

Blank line used to separate nearby statements.
### Line 868

`// Reset outcome displays`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 869

`document.getElementById("quantumResultsCard").style.display = "none";`

Text content rendered inside the nearest HTML element.
### Line 870

`document.getElementById("comparePanel").style.display = "none";`

Text content rendered inside the nearest HTML element.
### Line 871

`document.getElementById("stateInspectorDrawer").style.display = "none";`

Text content rendered inside the nearest HTML element.
### Line 872

`document.getElementById("evidenceOutcomeCard").style.display = "none";`

Text content rendered inside the nearest HTML element.
### Line 873

`document.getElementById("adaptiveDecisionCard").style.display = "none";`

Text content rendered inside the nearest HTML element.
### Line 874

`document.getElementById("aiGuidanceCard").style.display = "none";`

Text content rendered inside the nearest HTML element.
### Line 875

`selectedOptionLetter = null;`

Text content rendered inside the nearest HTML element.
### Line 876

`lastSubmitResult = null;`

Text content rendered inside the nearest HTML element.
### Line 877

`normalizedModel = null;`

Text content rendered inside the nearest HTML element.
### Line 878

`(blank)`

Blank line used to separate nearby statements.
### Line 879

`try {`

Text content rendered inside the nearest HTML element.
### Line 880

`const act = await fetchActivity(activityId);`

Text content rendered inside the nearest HTML element.
### Line 881

`currentActivityData = act;`

Text content rendered inside the nearest HTML element.
### Line 882

`(blank)`

Blank line used to separate nearby statements.
### Line 883

`document.getElementById("activityTitle").textContent = act.title;`

Text content rendered inside the nearest HTML element.
### Line 884

`document.getElementById("activityConceptBadge").textContent = act.concept_id;`

Text content rendered inside the nearest HTML element.
### Line 885

`const promptEl = document.getElementById("activityPrompt");`

Text content rendered inside the nearest HTML element.
### Line 886

`promptEl.textContent = act.prompt;`

Text content rendered inside the nearest HTML element.
### Line 887

`renderMath(promptEl);`

Text content rendered inside the nearest HTML element.
### Line 888

`(blank)`

Blank line used to separate nearby statements.
### Line 889

`if (act.task_type === "quantum_prediction") {`

Text content rendered inside the nearest HTML element.
### Line 890

`document.getElementById("predictionInputSection").style.display = "flex";`

Text content rendered inside the nearest HTML element.
### Line 891

`document.getElementById("choiceInputSection").style.display = "none";`

Text content rendered inside the nearest HTML element.
### Line 892

`if (act.quantum_experiment) {`

Text content rendered inside the nearest HTML element.
### Line 893

`circuitStudio.loadPreset("grover_2q");`

Text content rendered inside the nearest HTML element.
### Line 894

`}`

Text content rendered inside the nearest HTML element.
### Line 895

`} else {`

Text content rendered inside the nearest HTML element.
### Line 896

`document.getElementById("predictionInputSection").style.display = "none";`

Text content rendered inside the nearest HTML element.
### Line 897

`document.getElementById("choiceInputSection").style.display = "flex";`

Text content rendered inside the nearest HTML element.
### Line 898

`renderOptions(act.options || {});`

Text content rendered inside the nearest HTML element.
### Line 899

`}`

Text content rendered inside the nearest HTML element.
### Line 900

`} catch (err) {`

Text content rendered inside the nearest HTML element.
### Line 901

`showError(\`Error loading activity: ${err.message}\`);`

Text content rendered inside the nearest HTML element.
### Line 902

`}`

Text content rendered inside the nearest HTML element.
### Line 903

`};`

Text content rendered inside the nearest HTML element.
### Line 904

`(blank)`

Blank line used to separate nearby statements.
### Line 905

`function renderOptions(options) {`

Text content rendered inside the nearest HTML element.
### Line 906

`const container = document.getElementById("optionsContainer");`

Text content rendered inside the nearest HTML element.
### Line 907

`container.innerHTML = "";`

Text content rendered inside the nearest HTML element.
### Line 908

`selectedOptionLetter = null;`

Text content rendered inside the nearest HTML element.
### Line 909

`(blank)`

Blank line used to separate nearby statements.
### Line 910

`Object.entries(options).forEach(([letter, text]) => {`

Text content rendered inside the nearest HTML element.
### Line 911

`const btn = document.createElement("div");`

Text content rendered inside the nearest HTML element.
### Line 912

`btn.className = "option-btn";`

Text content rendered inside the nearest HTML element.
### Line 913

`btn.innerHTML = \`<span class="option-key">${letter}.</span> <span class="opt-text">${text}</span>\`;`

Text content rendered inside the nearest HTML element.
### Line 914

`renderMath(btn.querySelector(".opt-text"));`

Text content rendered inside the nearest HTML element.
### Line 915

`btn.onclick = () => {`

Text content rendered inside the nearest HTML element.
### Line 916

`document.querySelectorAll(".option-btn").forEach(b => b.classList.remove("selected"));`

Text content rendered inside the nearest HTML element.
### Line 917

`btn.classList.add("selected");`

Text content rendered inside the nearest HTML element.
### Line 918

`selectedOptionLetter = letter;`

Text content rendered inside the nearest HTML element.
### Line 919

`};`

Text content rendered inside the nearest HTML element.
### Line 920

`container.appendChild(btn);`

Text content rendered inside the nearest HTML element.
### Line 921

`});`

Text content rendered inside the nearest HTML element.
### Line 922

`}`

Text content rendered inside the nearest HTML element.
### Line 923

`(blank)`

Blank line used to separate nearby statements.
### Line 924

`window.handleSubmitPrediction = async function() {`

Text content rendered inside the nearest HTML element.
### Line 925

`const pred = document.getElementById("predictionField").value.trim();`

Text content rendered inside the nearest HTML element.
### Line 926

`if (!pred) return alert("Please enter a prediction basis state (e.g. 01 or 10)");`

Text content rendered inside the nearest HTML element.
### Line 927

`await executeSubmission(pred);`

Text content rendered inside the nearest HTML element.
### Line 928

`};`

Text content rendered inside the nearest HTML element.
### Line 929

`(blank)`

Blank line used to separate nearby statements.
### Line 930

`window.handleSubmitChoice = async function() {`

Text content rendered inside the nearest HTML element.
### Line 931

`if (!selectedOptionLetter) return alert("Please select an option letter (A, B, C, or D)");`

Text content rendered inside the nearest HTML element.
### Line 932

`await executeSubmission(selectedOptionLetter);`

Text content rendered inside the nearest HTML element.
### Line 933

`};`

Text content rendered inside the nearest HTML element.
### Line 934

`(blank)`

Blank line used to separate nearby statements.
### Line 935

`async function executeSubmission(learnerResponse) {`

Text content rendered inside the nearest HTML element.
### Line 936

`const learnerId = document.getElementById("learnerIdInput").value.trim() || "demo_learner";`

Text content rendered inside the nearest HTML element.
### Line 937

`const submitBtn = document.getElementById("submitPredictionBtn");`

Text content rendered inside the nearest HTML element.
### Line 938

`const choiceBtn = document.getElementById("submitChoiceBtn");`

Text content rendered inside the nearest HTML element.
### Line 939

`const progressBanner = document.getElementById("executionProgressBanner");`

Text content rendered inside the nearest HTML element.
### Line 940

`const progressText = document.getElementById("executionProgressText");`

Text content rendered inside the nearest HTML element.
### Line 941

`(blank)`

Blank line used to separate nearby statements.
### Line 942

`submitBtn.disabled = true; choiceBtn.disabled = true;`

Text content rendered inside the nearest HTML element.
### Line 943

`progressBanner.style.display = "flex";`

Text content rendered inside the nearest HTML element.
### Line 944

`progressText.textContent = "Executing quantum circuit on Qiskit Aer (1024 shots)...";`

Text content rendered inside the nearest HTML element.
### Line 945

`closeErrorBanner();`

Text content rendered inside the nearest HTML element.
### Line 946

`(blank)`

Blank line used to separate nearby statements.
### Line 947

`try {`

Text content rendered inside the nearest HTML element.
### Line 948

`const rawResponse = await submitPrediction(currentActivityId, learnerId, learnerResponse);`

Text content rendered inside the nearest HTML element.
### Line 949

`lastSubmitResult = rawResponse;`

Text content rendered inside the nearest HTML element.
### Line 950

`normalizedModel = normalizeSubmissionResponse(rawResponse);`

Text content rendered inside the nearest HTML element.
### Line 951

`const model = normalizedModel;`

Text content rendered inside the nearest HTML element.
### Line 952

`(blank)`

Blank line used to separate nearby statements.
### Line 953

`if (model.learnerState) {`

Text content rendered inside the nearest HTML element.
### Line 954

`currentLearnerState = model.learnerState;`

Text content rendered inside the nearest HTML element.
### Line 955

`updateBadgeDisplays(currentLearnerState);`

Text content rendered inside the nearest HTML element.
### Line 956

`}`

Text content rendered inside the nearest HTML element.
### Line 957

`(blank)`

Blank line used to separate nearby statements.
### Line 958

`// 1. Render Quantum Simulation Result & State Triad`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 959

`if (model.quantum) {`

Text content rendered inside the nearest HTML element.
### Line 960

`document.getElementById("quantumResultsCard").style.display = "flex";`

Text content rendered inside the nearest HTML element.
### Line 961

`(blank)`

Blank line used to separate nearby statements.
### Line 962

`// Populate State Triad`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 963

`const predBox = document.getElementById("triadPredictionBox");`

Text content rendered inside the nearest HTML element.
### Line 964

`predBox.className = \`triad-box prediction ${model.learner.isCorrect ? 'correct' : ''}\`;`

Text content rendered inside the nearest HTML element.
### Line 965

`document.getElementById("resPredictedState").textContent = model.learner.predictionLabel;`

Text content rendered inside the nearest HTML element.
### Line 966

`document.getElementById("resPredictionStatus").textContent = model.learner.outcomeText;`

Text content rendered inside the nearest HTML element.
### Line 967

`document.getElementById("resTargetState").textContent = model.quantum.targetStateLabel;`

Text content rendered inside the nearest HTML element.
### Line 968

`document.getElementById("resMostLikely").textContent = model.quantum.mostLikelyStateLabel;`

Text content rendered inside the nearest HTML element.
### Line 969

`document.getElementById("resTargetProb").textContent = \`${model.quantum.targetProbabilityStr} (${model.quantum.shots} shots)\`;`

Text content rendered inside the nearest HTML element.
### Line 970

`document.getElementById("simAlgorithmBadge").textContent = \`${model.quantum.algorithm} (${model.quantum.shots} shots)\`;`

Text content rendered inside the nearest HTML element.
### Line 971

`(blank)`

Blank line used to separate nearby statements.
### Line 972

`// Populate State Compare Diagram`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 973

`document.getElementById("compPredVal").textContent = model.learner.predictionLabel;`

Text content rendered inside the nearest HTML element.
### Line 974

`document.getElementById("compTargVal").textContent = model.quantum.targetStateLabel;`

Text content rendered inside the nearest HTML element.
### Line 975

`document.getElementById("compMeasVal").textContent = \`${model.quantum.mostLikelyStateLabel} (${model.quantum.targetProbabilityStr})\`;`

Text content rendered inside the nearest HTML element.
### Line 976

`document.getElementById("compRel1").textContent = model.learner.isCorrect ? "=" : "≠";`

Text content rendered inside the nearest HTML element.
### Line 977

`document.getElementById("compRel1").className = \`compare-rel ${model.learner.isCorrect ? 'match' : 'mismatch'}\`;`

Text content rendered inside the nearest HTML element.
### Line 978

`(blank)`

Blank line used to separate nearby statements.
### Line 979

`// Populate Interactive Measurement Histogram`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 980

`const hist = document.getElementById("histogramContainer");`

Text content rendered inside the nearest HTML element.
### Line 981

`hist.innerHTML = "";`

Text content rendered inside the nearest HTML element.
### Line 982

`model.quantum.probabilityBars.forEach(b => {`

Text content rendered inside the nearest HTML element.
### Line 983

`const row = document.createElement("div");`

Text content rendered inside the nearest HTML element.
### Line 984

`row.className = \`hist-row ${b.isTarget ? 'target-row' : ''}\`;`

Text content rendered inside the nearest HTML element.
### Line 985

`row.title = \`State ${b.stateLabel}: ${b.percentageStr} (${b.count} shots). Click to inspect details.\`;`

Text content rendered inside the nearest HTML element.
### Line 986

`row.onclick = () => {`

Text content rendered inside the nearest HTML element.
### Line 987

`document.querySelectorAll(".hist-row").forEach(r => r.classList.remove("selected"));`

Text content rendered inside the nearest HTML element.
### Line 988

`row.classList.add("selected");`

Text content rendered inside the nearest HTML element.
### Line 989

`inspectState(b);`

Text content rendered inside the nearest HTML element.
### Line 990

`};`

Text content rendered inside the nearest HTML element.
### Line 991

`row.innerHTML = \``

Text content rendered inside the nearest HTML element.
### Line 992

`<span class="hist-state">${b.stateLabel}</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 993

`<div class="hist-bar-bg">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 994

`<div class="hist-bar-fill ${b.isTarget ? 'target' : ''} ${b.isPredicted ? 'predicted' : ''}" style="width: ${Math.max(b.percentageNum, 3)}%;"></div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 995

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 996

`<span class="hist-pct">${b.percentageStr}</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 997

`\`;`

Text content rendered inside the nearest HTML element.
### Line 998

`hist.appendChild(row);`

Text content rendered inside the nearest HTML element.
### Line 999

`});`

Text content rendered inside the nearest HTML element.
### Line 1000

`(blank)`

Blank line used to separate nearby statements.
### Line 1001

`if (model.quantum.circuit.diagram) {`

Text content rendered inside the nearest HTML element.
### Line 1002

`document.getElementById("asciiCircuitContainer").style.display = "block";`

Text content rendered inside the nearest HTML element.
### Line 1003

`document.getElementById("asciiCircuitDiagram").textContent = model.quantum.circuit.diagram;`

Text content rendered inside the nearest HTML element.
### Line 1004

`}`

Text content rendered inside the nearest HTML element.
### Line 1005

`} else {`

Text content rendered inside the nearest HTML element.
### Line 1006

`document.getElementById("quantumResultsCard").style.display = "none";`

Text content rendered inside the nearest HTML element.
### Line 1007

`}`

Text content rendered inside the nearest HTML element.
### Line 1008

`(blank)`

Blank line used to separate nearby statements.
### Line 1009

`// 2. Render Evidence & Cognition Panel`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 1010

`document.getElementById("evidenceOutcomeCard").style.display = "flex";`

Text content rendered inside the nearest HTML element.
### Line 1011

`const outcomeBadge = document.getElementById("outcomeBadge");`

Text content rendered inside the nearest HTML element.
### Line 1012

`outcomeBadge.textContent = \`${model.learner.outcomeText} (Attempt #${model.learner.attemptNumber})\`;`

Text content rendered inside the nearest HTML element.
### Line 1013

`outcomeBadge.className = \`badge ${model.learner.outcomeClass}\`;`

Text content rendered inside the nearest HTML element.
### Line 1014

`(blank)`

Blank line used to separate nearby statements.
### Line 1015

`document.getElementById("trajectoryTrendDisplay").textContent = model.adaptive.gapTrend;`

Text content rendered inside the nearest HTML element.
### Line 1016

`document.getElementById("confidenceBadgeDisplay").textContent = \`${Math.round(model.adaptive.gapConfidence * 100)}%\`;`

Text content rendered inside the nearest HTML element.
### Line 1017

`document.getElementById("evidenceSufficiencyDisplay").textContent = model.adaptive.evidenceSufficiencyLabel;`

Text content rendered inside the nearest HTML element.
### Line 1018

`document.getElementById("inferredHypothesisDisplay").textContent = model.adaptive.hypothesisLabel;`

Text content rendered inside the nearest HTML element.
### Line 1019

`document.getElementById("evidenceIdDisplay").textContent = model.learner.evidenceId || "N/A";`

Text content rendered inside the nearest HTML element.
### Line 1020

`(blank)`

Blank line used to separate nearby statements.
### Line 1021

`// 3. Render "Why This Next?" Adaptive Decision Card`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 1022

`document.getElementById("adaptiveDecisionCard").style.display = "flex";`

Text content rendered inside the nearest HTML element.
### Line 1023

`document.getElementById("adaptiveActionBadge").textContent = model.adaptive.actionLabel;`

Text content rendered inside the nearest HTML element.
### Line 1024

`document.getElementById("decisionTriggerDisplay").textContent = model.adaptive.triggerLabel;`

Text content rendered inside the nearest HTML element.
### Line 1025

`document.getElementById("chainSufficiencyDisplay").textContent = model.adaptive.evidenceSufficiencyLabel;`

Text content rendered inside the nearest HTML element.
### Line 1026

`document.getElementById("chainHypothesisDisplay").textContent = model.adaptive.hypothesisLabel;`

Text content rendered inside the nearest HTML element.
### Line 1027

`document.getElementById("adaptiveReasonText").textContent = model.adaptive.reason;`

Text content rendered inside the nearest HTML element.
### Line 1028

`(blank)`

Blank line used to separate nearby statements.
### Line 1029

`// Render Supporting Evidence Chips`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 1030

`const suppList = document.getElementById("supportingEvidenceList");`

Text content rendered inside the nearest HTML element.
### Line 1031

`suppList.innerHTML = "";`

Text content rendered inside the nearest HTML element.
### Line 1032

`if (model.adaptive.supportingEvidenceIds && model.adaptive.supportingEvidenceIds.length > 0) {`

Text content rendered inside the nearest HTML element.
### Line 1033

`model.adaptive.supportingEvidenceIds.forEach((eid, idx) => {`

Text content rendered inside the nearest HTML element.
### Line 1034

`const chip = document.createElement("span");`

Text content rendered inside the nearest HTML element.
### Line 1035

`chip.className = "evidence-chip";`

Text content rendered inside the nearest HTML element.
### Line 1036

`chip.innerHTML = \`<span>Attempt #${idx + 1} Record</span> <strong>${eid}</strong>\`;`

Text content rendered inside the nearest HTML element.
### Line 1037

`suppList.appendChild(chip);`

Text content rendered inside the nearest HTML element.
### Line 1038

`});`

Text content rendered inside the nearest HTML element.
### Line 1039

`document.getElementById("supportingEvidenceSection").style.display = "block";`

Text content rendered inside the nearest HTML element.
### Line 1040

`} else {`

Text content rendered inside the nearest HTML element.
### Line 1041

`document.getElementById("supportingEvidenceSection").style.display = "none";`

Text content rendered inside the nearest HTML element.
### Line 1042

`}`

Text content rendered inside the nearest HTML element.
### Line 1043

`(blank)`

Blank line used to separate nearby statements.
### Line 1044

`if (model.adaptive.prerequisiteGap) {`

Text content rendered inside the nearest HTML element.
### Line 1045

`document.getElementById("prereqGapCallout").style.display = "block";`

Text content rendered inside the nearest HTML element.
### Line 1046

`document.getElementById("prereqGapName").textContent = model.adaptive.prerequisiteGap;`

Text content rendered inside the nearest HTML element.
### Line 1047

`} else {`

Text content rendered inside the nearest HTML element.
### Line 1048

`document.getElementById("prereqGapCallout").style.display = "none";`

Text content rendered inside the nearest HTML element.
### Line 1049

`}`

Text content rendered inside the nearest HTML element.
### Line 1050

`(blank)`

Blank line used to separate nearby statements.
### Line 1051

`const targetAct = model.adaptive.targetActivity;`

Text content rendered inside the nearest HTML element.
### Line 1052

`if (targetAct) {`

Text content rendered inside the nearest HTML element.
### Line 1053

`const targetTitle = (activitiesList.find(a => a.activity_id === targetAct)?.title) || targetAct;`

Text content rendered inside the nearest HTML element.
### Line 1054

`document.getElementById("nextTargetActivityId").textContent = targetTitle;`

Text content rendered inside the nearest HTML element.
### Line 1055

`document.getElementById("continueNextBtn").style.display = "inline-block";`

Text content rendered inside the nearest HTML element.
### Line 1056

`document.getElementById("continueNextBtn").dataset.target = targetAct;`

Text content rendered inside the nearest HTML element.
### Line 1057

`} else {`

Text content rendered inside the nearest HTML element.
### Line 1058

`document.getElementById("nextTargetActivityId").textContent = "End of Sequence (Curriculum Complete)";`

Text content rendered inside the nearest HTML element.
### Line 1059

`document.getElementById("continueNextBtn").style.display = "none";`

Text content rendered inside the nearest HTML element.
### Line 1060

`}`

Text content rendered inside the nearest HTML element.
### Line 1061

`(blank)`

Blank line used to separate nearby statements.
### Line 1062

`// 4. Reveal AI Guidance Card`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 1063

`document.getElementById("aiGuidanceCard").style.display = "flex";`

Text content rendered inside the nearest HTML element.
### Line 1064

`document.getElementById("aiExplanationText").textContent = 'Click "Explain My Result" for grounded AI explanation of this attempt.';`

Text content rendered inside the nearest HTML element.
### Line 1065

`(blank)`

Blank line used to separate nearby statements.
### Line 1066

`} catch (err) {`

Text content rendered inside the nearest HTML element.
### Line 1067

`showError(\`Submission Error: ${err.message}\`);`

Text content rendered inside the nearest HTML element.
### Line 1068

`} finally {`

Text content rendered inside the nearest HTML element.
### Line 1069

`submitBtn.disabled = false; choiceBtn.disabled = false;`

Text content rendered inside the nearest HTML element.
### Line 1070

`progressBanner.style.display = "none";`

Text content rendered inside the nearest HTML element.
### Line 1071

`}`

Text content rendered inside the nearest HTML element.
### Line 1072

`}`

Text content rendered inside the nearest HTML element.
### Line 1073

`(blank)`

Blank line used to separate nearby statements.
### Line 1074

`window.handleContinueToTarget = function() {`

Text content rendered inside the nearest HTML element.
### Line 1075

`const target = document.getElementById("continueNextBtn").dataset.target;`

Text content rendered inside the nearest HTML element.
### Line 1076

`if (target) loadActivity(target);`

Text content rendered inside the nearest HTML element.
### Line 1077

`};`

Text content rendered inside the nearest HTML element.
### Line 1078

`(blank)`

Blank line used to separate nearby statements.
### Line 1079

`window.handleExplain = async function() {`

Text content rendered inside the nearest HTML element.
### Line 1080

`if (!lastSubmitResult) return;`

Text content rendered inside the nearest HTML element.
### Line 1081

`const btn = document.getElementById("explainBtn");`

Text content rendered inside the nearest HTML element.
### Line 1082

`btn.disabled = true; btn.textContent = "Generating Grounded Guidance...";`

Text content rendered inside the nearest HTML element.
### Line 1083

`(blank)`

Blank line used to separate nearby statements.
### Line 1084

`try {`

Text content rendered inside the nearest HTML element.
### Line 1085

`const exp = await explainExperiment(lastSubmitResult);`

Text content rendered inside the nearest HTML element.
### Line 1086

`const expBox = document.getElementById("aiExplanationText");`

Text content rendered inside the nearest HTML element.
### Line 1087

`expBox.innerHTML = formatGroundedMarkdown(exp.explanation);`

Text content rendered inside the nearest HTML element.
### Line 1088

`renderMath(expBox);`

Text content rendered inside the nearest HTML element.
### Line 1089

`} catch (err) {`

Text content rendered inside the nearest HTML element.
### Line 1090

`document.getElementById("aiExplanationText").innerHTML = \`<p class="ai-para">AI Guidance Notice: Grounded explanation is temporarily unavailable (${err.message}). Your verified quantum simulation result and adaptive progress remain safely recorded.</p>\`;`

Text content rendered inside the nearest HTML element.
### Line 1091

`} finally {`

Text content rendered inside the nearest HTML element.
### Line 1092

`btn.disabled = false; btn.textContent = "Explain My Result";`

Text content rendered inside the nearest HTML element.
### Line 1093

`}`

Text content rendered inside the nearest HTML element.
### Line 1094

`};`

Text content rendered inside the nearest HTML element.
### Line 1095

`(blank)`

Blank line used to separate nearby statements.
### Line 1096

`// Modal AI Question Inquirer`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 1097

`window.openAskModal = function() {`

Text content rendered inside the nearest HTML element.
### Line 1098

`document.getElementById("askModal").style.display = "flex";`

Text content rendered inside the nearest HTML element.
### Line 1099

`document.getElementById("askAnswerBox").style.display = "none";`

Text content rendered inside the nearest HTML element.
### Line 1100

`};`

Text content rendered inside the nearest HTML element.
### Line 1101

`window.closeAskModal = function() {`

Text content rendered inside the nearest HTML element.
### Line 1102

`document.getElementById("askModal").style.display = "none";`

Text content rendered inside the nearest HTML element.
### Line 1103

`};`

Text content rendered inside the nearest HTML element.
### Line 1104

`window.handleAskQuestion = async function() {`

Text content rendered inside the nearest HTML element.
### Line 1105

`const q = document.getElementById("askQuestionInput").value.trim();`

Text content rendered inside the nearest HTML element.
### Line 1106

`if (!q) return;`

Text content rendered inside the nearest HTML element.
### Line 1107

`const btn = document.getElementById("askSubmitBtn");`

Text content rendered inside the nearest HTML element.
### Line 1108

`btn.disabled = true; btn.textContent = "Consulting Curriculum...";`

Text content rendered inside the nearest HTML element.
### Line 1109

`(blank)`

Blank line used to separate nearby statements.
### Line 1110

`try {`

Text content rendered inside the nearest HTML element.
### Line 1111

`const res = await askConceptualQuestion(q, currentActivityData?.concept_id || null);`

Text content rendered inside the nearest HTML element.
### Line 1112

`const box = document.getElementById("askAnswerBox");`

Text content rendered inside the nearest HTML element.
### Line 1113

`box.style.display = "block";`

Text content rendered inside the nearest HTML element.
### Line 1114

`box.innerHTML = formatGroundedMarkdown(res.answer);`

Text content rendered inside the nearest HTML element.
### Line 1115

`renderMath(box);`

Text content rendered inside the nearest HTML element.
### Line 1116

`} catch (err) {`

Text content rendered inside the nearest HTML element.
### Line 1117

`showError(\`Question error: ${err.message}\`);`

Text content rendered inside the nearest HTML element.
### Line 1118

`} finally {`

Text content rendered inside the nearest HTML element.
### Line 1119

`btn.disabled = false; btn.textContent = "Inquire";`

Text content rendered inside the nearest HTML element.
### Line 1120

`}`

Text content rendered inside the nearest HTML element.
### Line 1121

`};`

Text content rendered inside the nearest HTML element.
### Line 1122

`(blank)`

Blank line used to separate nearby statements.
### Line 1123

`window.toggleTheme = function() {`

Text content rendered inside the nearest HTML element.
### Line 1124

`toggleThemeFromModal();`

Text content rendered inside the nearest HTML element.
### Line 1125

`};`

Text content rendered inside the nearest HTML element.
### Line 1126

`(blank)`

Blank line used to separate nearby statements.
### Line 1127

`// Boot`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 1128

`initApp();`

Text content rendered inside the nearest HTML element.
### Line 1129

`</script>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 1130

`(blank)`

Blank line used to separate nearby statements.
### Line 1131

`</body>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 1132

`</html>`

Closes the corresponding HTML element and returns parsing to its parent.

## Nearby Files

No same-folder source files.
