# Explanation: `frontend/visualization/index.html`

## Purpose

This page explains the meaningful behavior in `frontend/visualization/index.html`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```html
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Q-BIT.140 — Interactive Quantum Circuit Builder & Adaptive Verification</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #0b0f19;
            --bg-secondary: #111827;
            --panel: #1a2234;
            --panel-border: rgba(91, 140, 255, 0.18);
            --panel-border-hi: rgba(91, 140, 255, 0.45);
            --text: #f3f4f6;
            --text-muted: #9ca3af;
            --accent: #3b82f6;
            --accent-glow: rgba(59, 130, 246, 0.35);
            --cyan: #22d3ee;
            --green: #10b981;
            --yellow: #f59e0b;
            --red: #ef4444;
            --grid-line: #334155;
            --wire: #64748b;
            --gate-bg: #1e3a8a;
            --gate-text: #ffffff;
            --font-display: "Space Grotesk", sans-serif;
            --font-body: "Inter", sans-serif;
            --font-mono: "JetBrains Mono", monospace;
        }

        [data-theme="light"] {
            --bg: #f8fafc;
            --bg-secondary: #ffffff;
            --panel: #f1f5f9;
            --panel-border: rgba(59, 130, 246, 0.2);
            --panel-border-hi: rgba(59, 130, 246, 0.4);
            --text: #0f172a;
            --text-muted: #64748b;
            --accent: #2563eb;
            --accent-glow: rgba(37, 99, 235, 0.2);
            --cyan: #0891b2;
            --green: #059669;
            --yellow: #d97706;
            --red: #dc2626;
            --grid-line: #cbd5e1;
            --wire: #94a3b8;
            --gate-bg: #dbeafe;
            --gate-text: #1e3a8a;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: var(--font-body);
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            transition: background 0.2s ease, color 0.2s ease;
        }

        header {
            padding: 16px 28px;
            background: var(--panel);
            border-bottom: 1px solid var(--panel-border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .brand-title {
            font-family: var(--font-display);
            font-size: 20px;
            font-weight: 700;
            background: linear-gradient(90deg, #fff, var(--cyan));
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }
        [data-theme="light"] .brand-title {
            background: linear-gradient(90deg, #0f172a, var(--accent));
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }
        .brand-sub { font-family: var(--font-mono); font-size: 11px; color: var(--text-muted); }

        .theme-btn {
            background: var(--panel);
            color: var(--text);
            border: 1px solid var(--panel-border);
            padding: 8px 14px;
            border-radius: 8px;
            font-family: var(--font-mono);
            font-size: 12px;
            cursor: pointer;
            transition: 0.2s;
        }
        .theme-btn:hover { border-color: var(--accent); }

        .layout {
            display: grid;
            grid-template-columns: 240px 1fr 420px;
            flex: 1;
            overflow: hidden;
            height: calc(100vh - 65px);
        }

        /* SIDEBAR (Gate toolbox) */
        .sidebar {
            background: var(--bg-secondary);
            border-right: 1px solid var(--panel-border);
            padding: 16px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        .section-title {
            font-family: var(--font-display);
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            margin-bottom: 8px;
        }
        .gate-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 8px;
        }
        .gate-btn {
            background: var(--gate-bg);
            color: var(--gate-text);
            border: 1px solid var(--panel-border);
            padding: 10px;
            border-radius: 8px;
            font-family: var(--font-mono);
            font-weight: 600;
            cursor: grab;
            text-align: center;
            user-select: none;
            transition: 0.15s;
        }
        .gate-btn:hover { transform: translateY(-2px); box-shadow: 0 4px 12px var(--accent-glow); }

        .btn-group { display: flex; flex-direction: column; gap: 6px; }
        .ctrl-btn {
            background: var(--panel);
            color: var(--text);
            border: 1px solid var(--panel-border);
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-family: var(--font-body);
            cursor: pointer;
            text-align: left;
            transition: 0.15s;
        }
        .ctrl-btn:hover { background: var(--accent); color: white; border-color: var(--accent); }
        .ctrl-btn.danger:hover { background: var(--red); border-color: var(--red); }

        /* CENTER (Circuit Grid Canvas) */
        .center-area {
            display: flex;
            flex-direction: column;
            background: var(--bg);
            overflow-y: auto;
            border-right: 1px solid var(--panel-border);
        }
        .circuit-toolbar {
            padding: 12px 20px;
            background: var(--panel);
            border-bottom: 1px solid var(--panel-border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .canvas-container {
            padding: 24px;
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        .wire-grid {
            background: var(--bg-secondary);
            border: 1px solid var(--panel-border);
            border-radius: 12px;
            padding: 20px;
            min-height: 240px;
            position: relative;
            overflow-x: auto;
        }

        .wire-row {
            display: flex;
            align-items: center;
            height: 52px;
            position: relative;
        }
        .wire-label {
            width: 48px;
            font-family: var(--font-mono);
            font-size: 14px;
            color: var(--cyan);
            font-weight: 600;
        }
        .wire-line {
            flex: 1;
            height: 2px;
            background: var(--wire);
            position: relative;
            display: flex;
            align-items: center;
        }
        .grid-slot {
            width: 44px;
            height: 44px;
            margin-right: 12px;
            border: 1px dashed var(--grid-line);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: 0.15s;
            position: relative;
            z-index: 2;
            background: var(--bg-secondary);
        }
        .grid-slot:hover { border-color: var(--accent); background: var(--panel); }
        .placed-gate {
            background: var(--gate-bg);
            color: var(--gate-text);
            width: 38px;
            height: 38px;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: var(--font-mono);
            font-weight: 700;
            font-size: 13px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        }

        /* RIGHT PANEL (Experiment, Verification, M2 & M5) */
        .right-panel {
            background: var(--bg-secondary);
            padding: 18px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        .card {
            background: var(--panel);
            border: 1px solid var(--panel-border);
            border-radius: 10px;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .card-title {
            font-family: var(--font-display);
            font-size: 14px;
            font-weight: 700;
            color: var(--cyan);
        }

        .badge {
            font-family: var(--font-mono);
            font-size: 11px;
            padding: 3px 8px;
            border-radius: 999px;
            background: var(--bg);
            border: 1px solid var(--panel-border);
        }
        .badge.success { color: var(--green); border-color: var(--green); }
        .badge.mismatch { color: var(--red); border-color: var(--red); }
        .badge.action { color: var(--yellow); border-color: var(--yellow); }

        .stat-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 8px;
        }
        .stat-box {
            background: var(--bg);
            border: 1px solid var(--panel-border);
            border-radius: 8px;
            padding: 8px;
            text-align: center;
        }
        .stat-label { font-size: 10px; color: var(--text-muted); font-family: var(--font-mono); text-transform: uppercase; }
        .stat-val { font-size: 14px; font-weight: 700; font-family: var(--font-mono); color: var(--text); margin-top: 2px; }

        /* Histogram bars */
        .hist-container { display: flex; flex-direction: column; gap: 6px; margin-top: 4px; }
        .hist-row { display: flex; align-items: center; gap: 8px; font-family: var(--font-mono); font-size: 12px; }
        .hist-state { width: 38px; color: var(--cyan); font-weight: 600; }
        .hist-bar-bg {
            flex: 1;
            height: 16px;
            background: var(--bg);
            border-radius: 4px;
            overflow: hidden;
            position: relative;
        }
        .hist-bar-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--accent), var(--cyan));
            border-radius: 4px;
            transition: width 0.4s ease;
        }
        .hist-bar-fill.target { background: linear-gradient(90deg, #10b981, #34d399); }
        .hist-pct { width: 44px; text-align: right; color: var(--text-muted); font-size: 11px; }

        .input-group { display: flex; gap: 8px; align-items: center; }
        .text-input {
            flex: 1;
            background: var(--bg);
            border: 1px solid var(--panel-border);
            color: var(--text);
            padding: 8px 12px;
            border-radius: 6px;
            font-family: var(--font-mono);
            font-size: 13px;
        }
        .text-input:focus { outline: none; border-color: var(--accent); }
        .action-btn {
            background: var(--accent);
            color: white;
            border: none;
            padding: 9px 16px;
            border-radius: 6px;
            font-family: var(--font-display);
            font-weight: 600;
            font-size: 13px;
            cursor: pointer;
            transition: 0.15s;
        }
        .action-btn:hover { background: #1d4ed8; }
        .action-btn:disabled { opacity: 0.5; cursor: not-allowed; }

        .explanation-box {
            background: var(--bg);
            border-left: 3px solid var(--cyan);
            border-radius: 6px;
            padding: 12px;
            font-size: 13px;
            line-height: 1.5;
            color: var(--text);
            max-height: 200px;
            overflow-y: auto;
            white-space: pre-wrap;
        }
        pre.circuit-ascii {
            font-family: var(--font-mono);
            font-size: 11px;
            background: var(--bg);
            padding: 8px;
            border-radius: 6px;
            overflow-x: auto;
            color: var(--cyan);
        }
    </style>
</head>
<body>

<header>
    <div>
        <h1 class="brand-title">Q-BIT.140</h1>
        <div class="brand-sub">Interactive Quantum Engine & Adaptive Verification</div>
    </div>
    <button class="theme-btn" id="themeToggleBtn" onclick="toggleTheme()">☀️ Light Mode</button>
</header>

<div class="layout">
    <!-- LEFT: Gate Toolbox -->
    <aside class="sidebar">
        <div>
            <div class="section-title">Quantum Gates</div>
            <div class="gate-grid">
                <div class="gate-btn" onclick="selectGateTool('H')">H</div>
                <div class="gate-btn" onclick="selectGateTool('X')">X</div>
                <div class="gate-btn" onclick="selectGateTool('Y')">Y</div>
                <div class="gate-btn" onclick="selectGateTool('Z')">Z</div>
                <div class="gate-btn" onclick="selectGateTool('S')">S</div>
                <div class="gate-btn" onclick="selectGateTool('T')">T</div>
                <div class="gate-btn" onclick="selectGateTool('CZ')">CZ</div>
                <div class="gate-btn" onclick="selectGateTool('M')">M</div>
            </div>
        </div>

        <div>
            <div class="section-title">Circuit Controls</div>
            <div class="btn-group">
                <button class="ctrl-btn" onclick="addQubit()">+ Add Qubit</button>
                <button class="ctrl-btn" onclick="removeQubit()">− Remove Qubit</button>
                <button class="ctrl-btn" onclick="addColumn()">+ Add Column</button>
                <button class="ctrl-btn" onclick="removeColumn()">− Remove Column</button>
                <button class="ctrl-btn danger" onclick="clearCircuit()">Clear Circuit</button>
            </div>
        </div>

        <div>
            <div class="section-title">API Connection</div>
            <div style="font-size: 11px; font-family: var(--font-mono); color: var(--green);">
                ● Connected to M4 Gateway
            </div>
        </div>
    </aside>

    <!-- CENTER: Circuit Wire Grid -->
    <main class="center-area">
        <div class="circuit-toolbar">
            <span style="font-family: var(--font-mono); font-size: 13px; color: var(--text-muted);">
                Selected Gate: <strong id="activeToolDisplay" style="color: var(--cyan);">None</strong>
            </span>
            <button class="ctrl-btn" onclick="presetGrover2Q()">Load 2-Qubit Grover Circuit</button>
        </div>

        <div class="canvas-container">
            <div class="wire-grid" id="wireGrid"></div>
            
            <div class="card" id="asciiDiagramCard" style="display: none;">
                <div class="card-header">
                    <span class="card-title">M3 Verified Qiskit Circuit Diagram</span>
                    <span class="badge" id="circuitDepthBadge">Depth: 5</span>
                </div>
                <pre class="circuit-ascii" id="circuitAsciiDiagram"></pre>
            </div>
        </div>
    </main>

    <!-- RIGHT: Activity, Prediction, M3 Simulation, M2 Adaptive Decision, M5 Guidance -->
    <aside class="right-panel">
        <!-- 1. Activity & Prediction Input -->
        <div class="card">
            <div class="card-header">
                <span class="card-title" id="activityTitle">Grover 2-Qubit Target Prediction</span>
                <span class="badge" id="activityConceptBadge">grover.search_problem</span>
            </div>
            <p style="font-size: 12px; color: var(--text-muted); line-height: 1.4;" id="activityPrompt">
                A 2-qubit Grover search circuit has been initialized with equal superposition and executed with 1 Grover iteration marking target state |10⟩. Predict the measurement outcome.
            </p>
            <div class="input-group">
                <input type="text" class="text-input" id="predictionInput" value="01" placeholder="Enter basis state (e.g. 01, 10)">
                <button class="action-btn" id="submitBtn" onclick="handleRunExperiment()">Run & Evaluate</button>
            </div>
        </div>

        <!-- 2. Real M3 Quantum Simulation Results -->
        <div class="card" id="quantumResultsCard" style="display: none;">
            <div class="card-header">
                <span class="card-title">M3 Verified Quantum Result</span>
                <span class="badge" id="algorithmBadge">Grover (1024 shots)</span>
            </div>
            <div class="stat-grid">
                <div class="stat-box">
                    <div class="stat-label">Target State</div>
                    <div class="stat-val" style="color: var(--green);" id="targetStateVal">|10⟩</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Most Likely</div>
                    <div class="stat-val" id="mostLikelyVal">|10⟩</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Target Prob</div>
                    <div class="stat-val" style="color: var(--cyan);" id="targetProbVal">93.5%</div>
                </div>
            </div>

            <div class="section-title" style="margin-top: 6px;">Measured Probabilities & Counts</div>
            <div class="hist-container" id="histogramContainer"></div>
        </div>

        <!-- 3. M2 Learner Evidence & Adaptive Decision -->
        <div class="card" id="adaptiveDecisionCard" style="display: none;">
            <div class="card-header">
                <span class="card-title">M2 Adaptive Cognition</span>
                <span class="badge" id="outcomeBadge">Prediction Mismatch</span>
            </div>
            <div style="font-size: 12px; line-height: 1.4;">
                <div><strong>Action:</strong> <span class="badge action" id="decisionActionBadge">gather_evidence</span></div>
                <div style="margin-top: 6px; color: var(--text-muted);" id="decisionReasonText">
                    Initial prediction mismatch on 'Grover 2-Qubit Target State Prediction'. Gathering additional evidence before selecting remediation.
                </div>
                <div style="margin-top: 8px; font-size: 11px; font-family: var(--font-mono); color: var(--cyan);" id="nextActivityText">
                    Next Target: act_grover_2q_predict
                </div>
            </div>
        </div>

        <!-- 4. M5 Grounded AI Guidance -->
        <div class="card" id="aiGuidanceCard" style="display: none;">
            <div class="card-header">
                <span class="card-title">M5 Grounded AI Guidance</span>
                <button class="ctrl-btn" style="padding: 4px 10px; font-size: 11px;" id="explainBtn" onclick="handleExplain()">Explain My Result</button>
            </div>
            <div class="explanation-box" id="aiExplanationBox">Click "Explain My Result" to generate a grounded explanation from the M5 curriculum knowledge base.</div>
        </div>
    </aside>
</div>

<script type="module">
    import { fetchActivity, submitPrediction, explainExperiment } from './api_client.js';
    import { normalizeSubmissionResponse, formatStateLabel, formatPercentage } from './adapter.js';

    let currentActivityId = "act_grover_2q_predict";
    let lastSubmitData = null;
    let selectedGate = null;

    let circuit = {
        num_qubits: 2,
        num_columns: 6,
        gates: [
            { id: 1, type: "H", qubit: 0, column: 0 },
            { id: 2, type: "H", qubit: 1, column: 0 },
            { id: 3, type: "X", qubit: 0, column: 1 },
            { id: 4, type: "CZ", qubit: 1, column: 2 },
            { id: 5, type: "X", qubit: 0, column: 3 },
            { id: 6, type: "H", qubit: 0, column: 4 },
            { id: 7, type: "H", qubit: 1, column: 4 },
            { id: 8, type: "M", qubit: 0, column: 5 },
            { id: 9, type: "M", qubit: 1, column: 5 },
        ]
    };

    window.selectGateTool = function(type) {
        selectedGate = type;
        document.getElementById('activeToolDisplay').textContent = type;
    };

    window.addQubit = function() {
        if (circuit.num_qubits < 5) {
            circuit.num_qubits++;
            renderGrid();
        }
    };

    window.removeQubit = function() {
        if (circuit.num_qubits > 1) {
            circuit.num_qubits--;
            circuit.gates = circuit.gates.filter(g => g.qubit < circuit.num_qubits);
            renderGrid();
        }
    };

    window.addColumn = function() {
        circuit.num_columns++;
        renderGrid();
    };

    window.removeColumn = function() {
        if (circuit.num_columns > 2) {
            circuit.num_columns--;
            circuit.gates = circuit.gates.filter(g => g.column < circuit.num_columns);
            renderGrid();
        }
    };

    window.clearCircuit = function() {
        circuit.gates = [];
        renderGrid();
    };

    window.presetGrover2Q = function() {
        circuit = {
            num_qubits: 2,
            num_columns: 6,
            gates: [
                { id: 1, type: "H", qubit: 0, column: 0 },
                { id: 2, type: "H", qubit: 1, column: 0 },
                { id: 3, type: "X", qubit: 0, column: 1 },
                { id: 4, type: "CZ", qubit: 1, column: 2 },
                { id: 5, type: "X", qubit: 0, column: 3 },
                { id: 6, type: "H", qubit: 0, column: 4 },
                { id: 7, type: "H", qubit: 1, column: 4 },
                { id: 8, type: "M", qubit: 0, column: 5 },
                { id: 9, type: "M", qubit: 1, column: 5 },
            ]
        };
        renderGrid();
    };

    function renderGrid() {
        const container = document.getElementById('wireGrid');
        container.innerHTML = '';

        for (let q = 0; q < circuit.num_qubits; q++) {
            const row = document.createElement('div');
            row.className = 'wire-row';

            const label = document.createElement('div');
            label.className = 'wire-label';
            label.textContent = `q_${q}:`;
            row.appendChild(label);

            const line = document.createElement('div');
            line.className = 'wire-line';

            for (let c = 0; c < circuit.num_columns; c++) {
                const slot = document.createElement('div');
                slot.className = 'grid-slot';
                slot.dataset.qubit = q;
                slot.dataset.column = c;

                const gate = circuit.gates.find(g => g.qubit === q && g.column === c);
                if (gate) {
                    const gateEl = document.createElement('div');
                    gateEl.className = 'placed-gate';
                    gateEl.textContent = gate.type;
                    slot.appendChild(gateEl);
                }

                slot.onclick = () => handleSlotClick(q, c);
                line.appendChild(slot);
            }

            row.appendChild(line);
            container.appendChild(row);
        }
    }

    function handleSlotClick(q, c) {
        const existingIdx = circuit.gates.findIndex(g => g.qubit === q && g.column === c);
        if (existingIdx >= 0) {
            circuit.gates.splice(existingIdx, 1);
        } else if (selectedGate) {
            circuit.gates.push({
                id: Date.now(),
                type: selectedGate,
                qubit: q,
                column: c
            });
        }
        renderGrid();
    }

    window.handleRunExperiment = async function() {
        const pred = document.getElementById('predictionInput').value.trim();
        if (!pred) return alert('Please enter a prediction (e.g. 10 or 01)');

        const btn = document.getElementById('submitBtn');
        btn.disabled = true;
        btn.textContent = 'Simulating...';

        try {
            const rawResponse = await submitPrediction(currentActivityId, "learner_ui_demo", pred);
            lastSubmitData = rawResponse;

            // Normalize response through M6 adapter
            const model = normalizeSubmissionResponse(rawResponse);

            // 1. Render Quantum Result
            document.getElementById('quantumResultsCard').style.display = 'flex';
            document.getElementById('targetStateVal').textContent = model.quantum.targetStateLabel;
            document.getElementById('mostLikelyVal').textContent = model.quantum.mostLikelyStateLabel;
            document.getElementById('targetProbVal').textContent = model.quantum.targetProbabilityStr;
            document.getElementById('algorithmBadge').textContent = `${model.quantum.algorithm} (${model.quantum.shots} shots)`;

            // Render Histogram
            const hist = document.getElementById('histogramContainer');
            hist.innerHTML = '';
            model.quantum.probabilityBars.forEach(b => {
                const row = document.createElement('div');
                row.className = 'hist-row';
                row.innerHTML = `
                    <span class="hist-state">${b.stateLabel}</span>
                    <div class="hist-bar-bg">
                        <div class="hist-bar-fill ${b.isTarget ? 'target' : ''}" style="width: ${Math.max(b.percentageNum, 3)}%;"></div>
                    </div>
                    <span class="hist-pct">${b.percentageStr} (${b.count})</span>
                `;
                hist.appendChild(row);
            });

            // 2. Render ASCII Circuit if available
            if (model.quantum.circuit.diagram) {
                document.getElementById('asciiDiagramCard').style.display = 'flex';
                document.getElementById('circuitDepthBadge').textContent = `Depth: ${model.quantum.circuit.depth}`;
                document.getElementById('circuitAsciiDiagram').textContent = model.quantum.circuit.diagram;
            }

            // 3. Render M2 Adaptive Decision
            document.getElementById('adaptiveDecisionCard').style.display = 'flex';
            const outcomeBadge = document.getElementById('outcomeBadge');
            outcomeBadge.textContent = model.learner.outcomeText;
            outcomeBadge.className = `badge ${model.learner.outcomeClass}`;

            document.getElementById('decisionActionBadge').textContent = model.adaptive.action;
            document.getElementById('decisionReasonText').textContent = model.adaptive.reason;
            document.getElementById('nextActivityText').textContent = `Next Target: ${model.adaptive.targetActivity || 'End of sequence'}`;

            // 4. Reveal AI Guidance card
            document.getElementById('aiGuidanceCard').style.display = 'flex';
            document.getElementById('aiExplanationBox').textContent = 'Click "Explain My Result" for grounded AI guidance on this attempt.';

        } catch (err) {
            alert(`Error: ${err.message}`);
        } finally {
            btn.disabled = false;
            btn.textContent = 'Run & Evaluate';
        }
    };

    window.handleExplain = async function() {
        if (!lastSubmitData) return;
        const btn = document.getElementById('explainBtn');
        btn.disabled = true;
        btn.textContent = 'Generating...';

        try {
            const exp = await explainExperiment(lastSubmitData);
            document.getElementById('aiExplanationBox').textContent = exp.explanation;
        } catch (err) {
            document.getElementById('aiExplanationBox').textContent = `AI Guidance Error: ${err.message}`;
        } finally {
            btn.disabled = false;
            btn.textContent = 'Explain My Result';
        }
    };

    window.toggleTheme = function() {
        const html = document.documentElement;
        const isDark = html.getAttribute('data-theme') === 'dark';
        html.setAttribute('data-theme', isDark ? 'light' : 'dark');
        document.getElementById('themeToggleBtn').textContent = isDark ? '🌙 Dark Mode' : '☀️ Light Mode';
    };

    // Initialize
    renderGrid();
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

`<title>Q-BIT.140 — Interactive Quantum Circuit Builder & Adaptive Verification</title>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 7

`<link rel="preconnect" href="https://fonts.googleapis.com">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 8

`<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 9

`<style>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 10

`:root {`

Text content rendered inside the nearest HTML element.
### Line 11

`--bg: #0b0f19;`

Text content rendered inside the nearest HTML element.
### Line 12

`--bg-secondary: #111827;`

Text content rendered inside the nearest HTML element.
### Line 13

`--panel: #1a2234;`

Text content rendered inside the nearest HTML element.
### Line 14

`--panel-border: rgba(91, 140, 255, 0.18);`

Text content rendered inside the nearest HTML element.
### Line 15

`--panel-border-hi: rgba(91, 140, 255, 0.45);`

Text content rendered inside the nearest HTML element.
### Line 16

`--text: #f3f4f6;`

Text content rendered inside the nearest HTML element.
### Line 17

`--text-muted: #9ca3af;`

Text content rendered inside the nearest HTML element.
### Line 18

`--accent: #3b82f6;`

Text content rendered inside the nearest HTML element.
### Line 19

`--accent-glow: rgba(59, 130, 246, 0.35);`

Text content rendered inside the nearest HTML element.
### Line 20

`--cyan: #22d3ee;`

Text content rendered inside the nearest HTML element.
### Line 21

`--green: #10b981;`

Text content rendered inside the nearest HTML element.
### Line 22

`--yellow: #f59e0b;`

Text content rendered inside the nearest HTML element.
### Line 23

`--red: #ef4444;`

Text content rendered inside the nearest HTML element.
### Line 24

`--grid-line: #334155;`

Text content rendered inside the nearest HTML element.
### Line 25

`--wire: #64748b;`

Text content rendered inside the nearest HTML element.
### Line 26

`--gate-bg: #1e3a8a;`

Text content rendered inside the nearest HTML element.
### Line 27

`--gate-text: #ffffff;`

Text content rendered inside the nearest HTML element.
### Line 28

`--font-display: "Space Grotesk", sans-serif;`

Text content rendered inside the nearest HTML element.
### Line 29

`--font-body: "Inter", sans-serif;`

Text content rendered inside the nearest HTML element.
### Line 30

`--font-mono: "JetBrains Mono", monospace;`

Text content rendered inside the nearest HTML element.
### Line 31

`}`

Text content rendered inside the nearest HTML element.
### Line 32

`(blank)`

Blank line used to separate nearby statements.
### Line 33

`[data-theme="light"] {`

Text content rendered inside the nearest HTML element.
### Line 34

`--bg: #f8fafc;`

Text content rendered inside the nearest HTML element.
### Line 35

`--bg-secondary: #ffffff;`

Text content rendered inside the nearest HTML element.
### Line 36

`--panel: #f1f5f9;`

Text content rendered inside the nearest HTML element.
### Line 37

`--panel-border: rgba(59, 130, 246, 0.2);`

Text content rendered inside the nearest HTML element.
### Line 38

`--panel-border-hi: rgba(59, 130, 246, 0.4);`

Text content rendered inside the nearest HTML element.
### Line 39

`--text: #0f172a;`

Text content rendered inside the nearest HTML element.
### Line 40

`--text-muted: #64748b;`

Text content rendered inside the nearest HTML element.
### Line 41

`--accent: #2563eb;`

Text content rendered inside the nearest HTML element.
### Line 42

`--accent-glow: rgba(37, 99, 235, 0.2);`

Text content rendered inside the nearest HTML element.
### Line 43

`--cyan: #0891b2;`

Text content rendered inside the nearest HTML element.
### Line 44

`--green: #059669;`

Text content rendered inside the nearest HTML element.
### Line 45

`--yellow: #d97706;`

Text content rendered inside the nearest HTML element.
### Line 46

`--red: #dc2626;`

Text content rendered inside the nearest HTML element.
### Line 47

`--grid-line: #cbd5e1;`

Text content rendered inside the nearest HTML element.
### Line 48

`--wire: #94a3b8;`

Text content rendered inside the nearest HTML element.
### Line 49

`--gate-bg: #dbeafe;`

Text content rendered inside the nearest HTML element.
### Line 50

`--gate-text: #1e3a8a;`

Text content rendered inside the nearest HTML element.
### Line 51

`}`

Text content rendered inside the nearest HTML element.
### Line 52

`(blank)`

Blank line used to separate nearby statements.
### Line 53

`* { box-sizing: border-box; margin: 0; padding: 0; }`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 54

`body {`

Text content rendered inside the nearest HTML element.
### Line 55

`font-family: var(--font-body);`

Text content rendered inside the nearest HTML element.
### Line 56

`background: var(--bg);`

Text content rendered inside the nearest HTML element.
### Line 57

`color: var(--text);`

Text content rendered inside the nearest HTML element.
### Line 58

`min-height: 100vh;`

Text content rendered inside the nearest HTML element.
### Line 59

`display: flex;`

Text content rendered inside the nearest HTML element.
### Line 60

`flex-direction: column;`

Text content rendered inside the nearest HTML element.
### Line 61

`transition: background 0.2s ease, color 0.2s ease;`

Text content rendered inside the nearest HTML element.
### Line 62

`}`

Text content rendered inside the nearest HTML element.
### Line 63

`(blank)`

Blank line used to separate nearby statements.
### Line 64

`header {`

Text content rendered inside the nearest HTML element.
### Line 65

`padding: 16px 28px;`

Text content rendered inside the nearest HTML element.
### Line 66

`background: var(--panel);`

Text content rendered inside the nearest HTML element.
### Line 67

`border-bottom: 1px solid var(--panel-border);`

Text content rendered inside the nearest HTML element.
### Line 68

`display: flex;`

Text content rendered inside the nearest HTML element.
### Line 69

`justify-content: space-between;`

Text content rendered inside the nearest HTML element.
### Line 70

`align-items: center;`

Text content rendered inside the nearest HTML element.
### Line 71

`}`

Text content rendered inside the nearest HTML element.
### Line 72

`.brand-title {`

Text content rendered inside the nearest HTML element.
### Line 73

`font-family: var(--font-display);`

Text content rendered inside the nearest HTML element.
### Line 74

`font-size: 20px;`

Text content rendered inside the nearest HTML element.
### Line 75

`font-weight: 700;`

Text content rendered inside the nearest HTML element.
### Line 76

`background: linear-gradient(90deg, #fff, var(--cyan));`

Text content rendered inside the nearest HTML element.
### Line 77

`-webkit-background-clip: text;`

Text content rendered inside the nearest HTML element.
### Line 78

`background-clip: text;`

Text content rendered inside the nearest HTML element.
### Line 79

`color: transparent;`

Text content rendered inside the nearest HTML element.
### Line 80

`}`

Text content rendered inside the nearest HTML element.
### Line 81

`[data-theme="light"] .brand-title {`

Text content rendered inside the nearest HTML element.
### Line 82

`background: linear-gradient(90deg, #0f172a, var(--accent));`

Text content rendered inside the nearest HTML element.
### Line 83

`-webkit-background-clip: text;`

Text content rendered inside the nearest HTML element.
### Line 84

`background-clip: text;`

Text content rendered inside the nearest HTML element.
### Line 85

`color: transparent;`

Text content rendered inside the nearest HTML element.
### Line 86

`}`

Text content rendered inside the nearest HTML element.
### Line 87

`.brand-sub { font-family: var(--font-mono); font-size: 11px; color: var(--text-muted); }`

Text content rendered inside the nearest HTML element.
### Line 88

`(blank)`

Blank line used to separate nearby statements.
### Line 89

`.theme-btn {`

Text content rendered inside the nearest HTML element.
### Line 90

`background: var(--panel);`

Text content rendered inside the nearest HTML element.
### Line 91

`color: var(--text);`

Text content rendered inside the nearest HTML element.
### Line 92

`border: 1px solid var(--panel-border);`

Text content rendered inside the nearest HTML element.
### Line 93

`padding: 8px 14px;`

Text content rendered inside the nearest HTML element.
### Line 94

`border-radius: 8px;`

Text content rendered inside the nearest HTML element.
### Line 95

`font-family: var(--font-mono);`

Text content rendered inside the nearest HTML element.
### Line 96

`font-size: 12px;`

Text content rendered inside the nearest HTML element.
### Line 97

`cursor: pointer;`

Text content rendered inside the nearest HTML element.
### Line 98

`transition: 0.2s;`

Text content rendered inside the nearest HTML element.
### Line 99

`}`

Text content rendered inside the nearest HTML element.
### Line 100

`.theme-btn:hover { border-color: var(--accent); }`

Text content rendered inside the nearest HTML element.
### Line 101

`(blank)`

Blank line used to separate nearby statements.
### Line 102

`.layout {`

Text content rendered inside the nearest HTML element.
### Line 103

`display: grid;`

Text content rendered inside the nearest HTML element.
### Line 104

`grid-template-columns: 240px 1fr 420px;`

Text content rendered inside the nearest HTML element.
### Line 105

`flex: 1;`

Text content rendered inside the nearest HTML element.
### Line 106

`overflow: hidden;`

Text content rendered inside the nearest HTML element.
### Line 107

`height: calc(100vh - 65px);`

Text content rendered inside the nearest HTML element.
### Line 108

`}`

Text content rendered inside the nearest HTML element.
### Line 109

`(blank)`

Blank line used to separate nearby statements.
### Line 110

`/* SIDEBAR (Gate toolbox) */`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 111

`.sidebar {`

Text content rendered inside the nearest HTML element.
### Line 112

`background: var(--bg-secondary);`

Text content rendered inside the nearest HTML element.
### Line 113

`border-right: 1px solid var(--panel-border);`

Text content rendered inside the nearest HTML element.
### Line 114

`padding: 16px;`

Text content rendered inside the nearest HTML element.
### Line 115

`overflow-y: auto;`

Text content rendered inside the nearest HTML element.
### Line 116

`display: flex;`

Text content rendered inside the nearest HTML element.
### Line 117

`flex-direction: column;`

Text content rendered inside the nearest HTML element.
### Line 118

`gap: 16px;`

Text content rendered inside the nearest HTML element.
### Line 119

`}`

Text content rendered inside the nearest HTML element.
### Line 120

`.section-title {`

Text content rendered inside the nearest HTML element.
### Line 121

`font-family: var(--font-display);`

Text content rendered inside the nearest HTML element.
### Line 122

`font-size: 13px;`

Text content rendered inside the nearest HTML element.
### Line 123

`text-transform: uppercase;`

Text content rendered inside the nearest HTML element.
### Line 124

`letter-spacing: 0.05em;`

Text content rendered inside the nearest HTML element.
### Line 125

`color: var(--text-muted);`

Text content rendered inside the nearest HTML element.
### Line 126

`margin-bottom: 8px;`

Text content rendered inside the nearest HTML element.
### Line 127

`}`

Text content rendered inside the nearest HTML element.
### Line 128

`.gate-grid {`

Text content rendered inside the nearest HTML element.
### Line 129

`display: grid;`

Text content rendered inside the nearest HTML element.
### Line 130

`grid-template-columns: repeat(2, 1fr);`

Text content rendered inside the nearest HTML element.
### Line 131

`gap: 8px;`

Text content rendered inside the nearest HTML element.
### Line 132

`}`

Text content rendered inside the nearest HTML element.
### Line 133

`.gate-btn {`

Text content rendered inside the nearest HTML element.
### Line 134

`background: var(--gate-bg);`

Text content rendered inside the nearest HTML element.
### Line 135

`color: var(--gate-text);`

Text content rendered inside the nearest HTML element.
### Line 136

`border: 1px solid var(--panel-border);`

Text content rendered inside the nearest HTML element.
### Line 137

`padding: 10px;`

Text content rendered inside the nearest HTML element.
### Line 138

`border-radius: 8px;`

Text content rendered inside the nearest HTML element.
### Line 139

`font-family: var(--font-mono);`

Text content rendered inside the nearest HTML element.
### Line 140

`font-weight: 600;`

Text content rendered inside the nearest HTML element.
### Line 141

`cursor: grab;`

Text content rendered inside the nearest HTML element.
### Line 142

`text-align: center;`

Text content rendered inside the nearest HTML element.
### Line 143

`user-select: none;`

Text content rendered inside the nearest HTML element.
### Line 144

`transition: 0.15s;`

Text content rendered inside the nearest HTML element.
### Line 145

`}`

Text content rendered inside the nearest HTML element.
### Line 146

`.gate-btn:hover { transform: translateY(-2px); box-shadow: 0 4px 12px var(--accent-glow); }`

Text content rendered inside the nearest HTML element.
### Line 147

`(blank)`

Blank line used to separate nearby statements.
### Line 148

`.btn-group { display: flex; flex-direction: column; gap: 6px; }`

Text content rendered inside the nearest HTML element.
### Line 149

`.ctrl-btn {`

Text content rendered inside the nearest HTML element.
### Line 150

`background: var(--panel);`

Text content rendered inside the nearest HTML element.
### Line 151

`color: var(--text);`

Text content rendered inside the nearest HTML element.
### Line 152

`border: 1px solid var(--panel-border);`

Text content rendered inside the nearest HTML element.
### Line 153

`padding: 8px 12px;`

Text content rendered inside the nearest HTML element.
### Line 154

`border-radius: 6px;`

Text content rendered inside the nearest HTML element.
### Line 155

`font-size: 12px;`

Text content rendered inside the nearest HTML element.
### Line 156

`font-family: var(--font-body);`

Text content rendered inside the nearest HTML element.
### Line 157

`cursor: pointer;`

Text content rendered inside the nearest HTML element.
### Line 158

`text-align: left;`

Text content rendered inside the nearest HTML element.
### Line 159

`transition: 0.15s;`

Text content rendered inside the nearest HTML element.
### Line 160

`}`

Text content rendered inside the nearest HTML element.
### Line 161

`.ctrl-btn:hover { background: var(--accent); color: white; border-color: var(--accent); }`

Text content rendered inside the nearest HTML element.
### Line 162

`.ctrl-btn.danger:hover { background: var(--red); border-color: var(--red); }`

Text content rendered inside the nearest HTML element.
### Line 163

`(blank)`

Blank line used to separate nearby statements.
### Line 164

`/* CENTER (Circuit Grid Canvas) */`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 165

`.center-area {`

Text content rendered inside the nearest HTML element.
### Line 166

`display: flex;`

Text content rendered inside the nearest HTML element.
### Line 167

`flex-direction: column;`

Text content rendered inside the nearest HTML element.
### Line 168

`background: var(--bg);`

Text content rendered inside the nearest HTML element.
### Line 169

`overflow-y: auto;`

Text content rendered inside the nearest HTML element.
### Line 170

`border-right: 1px solid var(--panel-border);`

Text content rendered inside the nearest HTML element.
### Line 171

`}`

Text content rendered inside the nearest HTML element.
### Line 172

`.circuit-toolbar {`

Text content rendered inside the nearest HTML element.
### Line 173

`padding: 12px 20px;`

Text content rendered inside the nearest HTML element.
### Line 174

`background: var(--panel);`

Text content rendered inside the nearest HTML element.
### Line 175

`border-bottom: 1px solid var(--panel-border);`

Text content rendered inside the nearest HTML element.
### Line 176

`display: flex;`

Text content rendered inside the nearest HTML element.
### Line 177

`justify-content: space-between;`

Text content rendered inside the nearest HTML element.
### Line 178

`align-items: center;`

Text content rendered inside the nearest HTML element.
### Line 179

`}`

Text content rendered inside the nearest HTML element.
### Line 180

`.canvas-container {`

Text content rendered inside the nearest HTML element.
### Line 181

`padding: 24px;`

Text content rendered inside the nearest HTML element.
### Line 182

`flex: 1;`

Text content rendered inside the nearest HTML element.
### Line 183

`display: flex;`

Text content rendered inside the nearest HTML element.
### Line 184

`flex-direction: column;`

Text content rendered inside the nearest HTML element.
### Line 185

`gap: 16px;`

Text content rendered inside the nearest HTML element.
### Line 186

`}`

Text content rendered inside the nearest HTML element.
### Line 187

`.wire-grid {`

Text content rendered inside the nearest HTML element.
### Line 188

`background: var(--bg-secondary);`

Text content rendered inside the nearest HTML element.
### Line 189

`border: 1px solid var(--panel-border);`

Text content rendered inside the nearest HTML element.
### Line 190

`border-radius: 12px;`

Text content rendered inside the nearest HTML element.
### Line 191

`padding: 20px;`

Text content rendered inside the nearest HTML element.
### Line 192

`min-height: 240px;`

Text content rendered inside the nearest HTML element.
### Line 193

`position: relative;`

Text content rendered inside the nearest HTML element.
### Line 194

`overflow-x: auto;`

Text content rendered inside the nearest HTML element.
### Line 195

`}`

Text content rendered inside the nearest HTML element.
### Line 196

`(blank)`

Blank line used to separate nearby statements.
### Line 197

`.wire-row {`

Text content rendered inside the nearest HTML element.
### Line 198

`display: flex;`

Text content rendered inside the nearest HTML element.
### Line 199

`align-items: center;`

Text content rendered inside the nearest HTML element.
### Line 200

`height: 52px;`

Text content rendered inside the nearest HTML element.
### Line 201

`position: relative;`

Text content rendered inside the nearest HTML element.
### Line 202

`}`

Text content rendered inside the nearest HTML element.
### Line 203

`.wire-label {`

Text content rendered inside the nearest HTML element.
### Line 204

`width: 48px;`

Text content rendered inside the nearest HTML element.
### Line 205

`font-family: var(--font-mono);`

Text content rendered inside the nearest HTML element.
### Line 206

`font-size: 14px;`

Text content rendered inside the nearest HTML element.
### Line 207

`color: var(--cyan);`

Text content rendered inside the nearest HTML element.
### Line 208

`font-weight: 600;`

Text content rendered inside the nearest HTML element.
### Line 209

`}`

Text content rendered inside the nearest HTML element.
### Line 210

`.wire-line {`

Text content rendered inside the nearest HTML element.
### Line 211

`flex: 1;`

Text content rendered inside the nearest HTML element.
### Line 212

`height: 2px;`

Text content rendered inside the nearest HTML element.
### Line 213

`background: var(--wire);`

Text content rendered inside the nearest HTML element.
### Line 214

`position: relative;`

Text content rendered inside the nearest HTML element.
### Line 215

`display: flex;`

Text content rendered inside the nearest HTML element.
### Line 216

`align-items: center;`

Text content rendered inside the nearest HTML element.
### Line 217

`}`

Text content rendered inside the nearest HTML element.
### Line 218

`.grid-slot {`

Text content rendered inside the nearest HTML element.
### Line 219

`width: 44px;`

Text content rendered inside the nearest HTML element.
### Line 220

`height: 44px;`

Text content rendered inside the nearest HTML element.
### Line 221

`margin-right: 12px;`

Text content rendered inside the nearest HTML element.
### Line 222

`border: 1px dashed var(--grid-line);`

Text content rendered inside the nearest HTML element.
### Line 223

`border-radius: 8px;`

Text content rendered inside the nearest HTML element.
### Line 224

`display: flex;`

Text content rendered inside the nearest HTML element.
### Line 225

`align-items: center;`

Text content rendered inside the nearest HTML element.
### Line 226

`justify-content: center;`

Text content rendered inside the nearest HTML element.
### Line 227

`cursor: pointer;`

Text content rendered inside the nearest HTML element.
### Line 228

`transition: 0.15s;`

Text content rendered inside the nearest HTML element.
### Line 229

`position: relative;`

Text content rendered inside the nearest HTML element.
### Line 230

`z-index: 2;`

Text content rendered inside the nearest HTML element.
### Line 231

`background: var(--bg-secondary);`

Text content rendered inside the nearest HTML element.
### Line 232

`}`

Text content rendered inside the nearest HTML element.
### Line 233

`.grid-slot:hover { border-color: var(--accent); background: var(--panel); }`

Text content rendered inside the nearest HTML element.
### Line 234

`.placed-gate {`

Text content rendered inside the nearest HTML element.
### Line 235

`background: var(--gate-bg);`

Text content rendered inside the nearest HTML element.
### Line 236

`color: var(--gate-text);`

Text content rendered inside the nearest HTML element.
### Line 237

`width: 38px;`

Text content rendered inside the nearest HTML element.
### Line 238

`height: 38px;`

Text content rendered inside the nearest HTML element.
### Line 239

`border-radius: 6px;`

Text content rendered inside the nearest HTML element.
### Line 240

`display: flex;`

Text content rendered inside the nearest HTML element.
### Line 241

`align-items: center;`

Text content rendered inside the nearest HTML element.
### Line 242

`justify-content: center;`

Text content rendered inside the nearest HTML element.
### Line 243

`font-family: var(--font-mono);`

Text content rendered inside the nearest HTML element.
### Line 244

`font-weight: 700;`

Text content rendered inside the nearest HTML element.
### Line 245

`font-size: 13px;`

Text content rendered inside the nearest HTML element.
### Line 246

`box-shadow: 0 2px 6px rgba(0,0,0,0.3);`

Text content rendered inside the nearest HTML element.
### Line 247

`}`

Text content rendered inside the nearest HTML element.
### Line 248

`(blank)`

Blank line used to separate nearby statements.
### Line 249

`/* RIGHT PANEL (Experiment, Verification, M2 & M5) */`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 250

`.right-panel {`

Text content rendered inside the nearest HTML element.
### Line 251

`background: var(--bg-secondary);`

Text content rendered inside the nearest HTML element.
### Line 252

`padding: 18px;`

Text content rendered inside the nearest HTML element.
### Line 253

`overflow-y: auto;`

Text content rendered inside the nearest HTML element.
### Line 254

`display: flex;`

Text content rendered inside the nearest HTML element.
### Line 255

`flex-direction: column;`

Text content rendered inside the nearest HTML element.
### Line 256

`gap: 16px;`

Text content rendered inside the nearest HTML element.
### Line 257

`}`

Text content rendered inside the nearest HTML element.
### Line 258

`.card {`

Text content rendered inside the nearest HTML element.
### Line 259

`background: var(--panel);`

Text content rendered inside the nearest HTML element.
### Line 260

`border: 1px solid var(--panel-border);`

Text content rendered inside the nearest HTML element.
### Line 261

`border-radius: 10px;`

Text content rendered inside the nearest HTML element.
### Line 262

`padding: 16px;`

Text content rendered inside the nearest HTML element.
### Line 263

`display: flex;`

Text content rendered inside the nearest HTML element.
### Line 264

`flex-direction: column;`

Text content rendered inside the nearest HTML element.
### Line 265

`gap: 10px;`

Text content rendered inside the nearest HTML element.
### Line 266

`}`

Text content rendered inside the nearest HTML element.
### Line 267

`.card-header {`

Text content rendered inside the nearest HTML element.
### Line 268

`display: flex;`

Text content rendered inside the nearest HTML element.
### Line 269

`justify-content: space-between;`

Text content rendered inside the nearest HTML element.
### Line 270

`align-items: center;`

Text content rendered inside the nearest HTML element.
### Line 271

`}`

Text content rendered inside the nearest HTML element.
### Line 272

`.card-title {`

Text content rendered inside the nearest HTML element.
### Line 273

`font-family: var(--font-display);`

Text content rendered inside the nearest HTML element.
### Line 274

`font-size: 14px;`

Text content rendered inside the nearest HTML element.
### Line 275

`font-weight: 700;`

Text content rendered inside the nearest HTML element.
### Line 276

`color: var(--cyan);`

Text content rendered inside the nearest HTML element.
### Line 277

`}`

Text content rendered inside the nearest HTML element.
### Line 278

`(blank)`

Blank line used to separate nearby statements.
### Line 279

`.badge {`

Text content rendered inside the nearest HTML element.
### Line 280

`font-family: var(--font-mono);`

Text content rendered inside the nearest HTML element.
### Line 281

`font-size: 11px;`

Text content rendered inside the nearest HTML element.
### Line 282

`padding: 3px 8px;`

Text content rendered inside the nearest HTML element.
### Line 283

`border-radius: 999px;`

Text content rendered inside the nearest HTML element.
### Line 284

`background: var(--bg);`

Text content rendered inside the nearest HTML element.
### Line 285

`border: 1px solid var(--panel-border);`

Text content rendered inside the nearest HTML element.
### Line 286

`}`

Text content rendered inside the nearest HTML element.
### Line 287

`.badge.success { color: var(--green); border-color: var(--green); }`

Text content rendered inside the nearest HTML element.
### Line 288

`.badge.mismatch { color: var(--red); border-color: var(--red); }`

Text content rendered inside the nearest HTML element.
### Line 289

`.badge.action { color: var(--yellow); border-color: var(--yellow); }`

Text content rendered inside the nearest HTML element.
### Line 290

`(blank)`

Blank line used to separate nearby statements.
### Line 291

`.stat-grid {`

Text content rendered inside the nearest HTML element.
### Line 292

`display: grid;`

Text content rendered inside the nearest HTML element.
### Line 293

`grid-template-columns: repeat(3, 1fr);`

Text content rendered inside the nearest HTML element.
### Line 294

`gap: 8px;`

Text content rendered inside the nearest HTML element.
### Line 295

`}`

Text content rendered inside the nearest HTML element.
### Line 296

`.stat-box {`

Text content rendered inside the nearest HTML element.
### Line 297

`background: var(--bg);`

Text content rendered inside the nearest HTML element.
### Line 298

`border: 1px solid var(--panel-border);`

Text content rendered inside the nearest HTML element.
### Line 299

`border-radius: 8px;`

Text content rendered inside the nearest HTML element.
### Line 300

`padding: 8px;`

Text content rendered inside the nearest HTML element.
### Line 301

`text-align: center;`

Text content rendered inside the nearest HTML element.
### Line 302

`}`

Text content rendered inside the nearest HTML element.
### Line 303

`.stat-label { font-size: 10px; color: var(--text-muted); font-family: var(--font-mono); text-transform: uppercase; }`

Text content rendered inside the nearest HTML element.
### Line 304

`.stat-val { font-size: 14px; font-weight: 700; font-family: var(--font-mono); color: var(--text); margin-top: 2px; }`

Text content rendered inside the nearest HTML element.
### Line 305

`(blank)`

Blank line used to separate nearby statements.
### Line 306

`/* Histogram bars */`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 307

`.hist-container { display: flex; flex-direction: column; gap: 6px; margin-top: 4px; }`

Text content rendered inside the nearest HTML element.
### Line 308

`.hist-row { display: flex; align-items: center; gap: 8px; font-family: var(--font-mono); font-size: 12px; }`

Text content rendered inside the nearest HTML element.
### Line 309

`.hist-state { width: 38px; color: var(--cyan); font-weight: 600; }`

Text content rendered inside the nearest HTML element.
### Line 310

`.hist-bar-bg {`

Text content rendered inside the nearest HTML element.
### Line 311

`flex: 1;`

Text content rendered inside the nearest HTML element.
### Line 312

`height: 16px;`

Text content rendered inside the nearest HTML element.
### Line 313

`background: var(--bg);`

Text content rendered inside the nearest HTML element.
### Line 314

`border-radius: 4px;`

Text content rendered inside the nearest HTML element.
### Line 315

`overflow: hidden;`

Text content rendered inside the nearest HTML element.
### Line 316

`position: relative;`

Text content rendered inside the nearest HTML element.
### Line 317

`}`

Text content rendered inside the nearest HTML element.
### Line 318

`.hist-bar-fill {`

Text content rendered inside the nearest HTML element.
### Line 319

`height: 100%;`

Text content rendered inside the nearest HTML element.
### Line 320

`background: linear-gradient(90deg, var(--accent), var(--cyan));`

Text content rendered inside the nearest HTML element.
### Line 321

`border-radius: 4px;`

Text content rendered inside the nearest HTML element.
### Line 322

`transition: width 0.4s ease;`

Text content rendered inside the nearest HTML element.
### Line 323

`}`

Text content rendered inside the nearest HTML element.
### Line 324

`.hist-bar-fill.target { background: linear-gradient(90deg, #10b981, #34d399); }`

Text content rendered inside the nearest HTML element.
### Line 325

`.hist-pct { width: 44px; text-align: right; color: var(--text-muted); font-size: 11px; }`

Text content rendered inside the nearest HTML element.
### Line 326

`(blank)`

Blank line used to separate nearby statements.
### Line 327

`.input-group { display: flex; gap: 8px; align-items: center; }`

Text content rendered inside the nearest HTML element.
### Line 328

`.text-input {`

Text content rendered inside the nearest HTML element.
### Line 329

`flex: 1;`

Text content rendered inside the nearest HTML element.
### Line 330

`background: var(--bg);`

Text content rendered inside the nearest HTML element.
### Line 331

`border: 1px solid var(--panel-border);`

Text content rendered inside the nearest HTML element.
### Line 332

`color: var(--text);`

Text content rendered inside the nearest HTML element.
### Line 333

`padding: 8px 12px;`

Text content rendered inside the nearest HTML element.
### Line 334

`border-radius: 6px;`

Text content rendered inside the nearest HTML element.
### Line 335

`font-family: var(--font-mono);`

Text content rendered inside the nearest HTML element.
### Line 336

`font-size: 13px;`

Text content rendered inside the nearest HTML element.
### Line 337

`}`

Text content rendered inside the nearest HTML element.
### Line 338

`.text-input:focus { outline: none; border-color: var(--accent); }`

Text content rendered inside the nearest HTML element.
### Line 339

`.action-btn {`

Text content rendered inside the nearest HTML element.
### Line 340

`background: var(--accent);`

Text content rendered inside the nearest HTML element.
### Line 341

`color: white;`

Text content rendered inside the nearest HTML element.
### Line 342

`border: none;`

Text content rendered inside the nearest HTML element.
### Line 343

`padding: 9px 16px;`

Text content rendered inside the nearest HTML element.
### Line 344

`border-radius: 6px;`

Text content rendered inside the nearest HTML element.
### Line 345

`font-family: var(--font-display);`

Text content rendered inside the nearest HTML element.
### Line 346

`font-weight: 600;`

Text content rendered inside the nearest HTML element.
### Line 347

`font-size: 13px;`

Text content rendered inside the nearest HTML element.
### Line 348

`cursor: pointer;`

Text content rendered inside the nearest HTML element.
### Line 349

`transition: 0.15s;`

Text content rendered inside the nearest HTML element.
### Line 350

`}`

Text content rendered inside the nearest HTML element.
### Line 351

`.action-btn:hover { background: #1d4ed8; }`

Text content rendered inside the nearest HTML element.
### Line 352

`.action-btn:disabled { opacity: 0.5; cursor: not-allowed; }`

Text content rendered inside the nearest HTML element.
### Line 353

`(blank)`

Blank line used to separate nearby statements.
### Line 354

`.explanation-box {`

Text content rendered inside the nearest HTML element.
### Line 355

`background: var(--bg);`

Text content rendered inside the nearest HTML element.
### Line 356

`border-left: 3px solid var(--cyan);`

Text content rendered inside the nearest HTML element.
### Line 357

`border-radius: 6px;`

Text content rendered inside the nearest HTML element.
### Line 358

`padding: 12px;`

Text content rendered inside the nearest HTML element.
### Line 359

`font-size: 13px;`

Text content rendered inside the nearest HTML element.
### Line 360

`line-height: 1.5;`

Text content rendered inside the nearest HTML element.
### Line 361

`color: var(--text);`

Text content rendered inside the nearest HTML element.
### Line 362

`max-height: 200px;`

Text content rendered inside the nearest HTML element.
### Line 363

`overflow-y: auto;`

Text content rendered inside the nearest HTML element.
### Line 364

`white-space: pre-wrap;`

Text content rendered inside the nearest HTML element.
### Line 365

`}`

Text content rendered inside the nearest HTML element.
### Line 366

`pre.circuit-ascii {`

Text content rendered inside the nearest HTML element.
### Line 367

`font-family: var(--font-mono);`

Text content rendered inside the nearest HTML element.
### Line 368

`font-size: 11px;`

Text content rendered inside the nearest HTML element.
### Line 369

`background: var(--bg);`

Text content rendered inside the nearest HTML element.
### Line 370

`padding: 8px;`

Text content rendered inside the nearest HTML element.
### Line 371

`border-radius: 6px;`

Text content rendered inside the nearest HTML element.
### Line 372

`overflow-x: auto;`

Text content rendered inside the nearest HTML element.
### Line 373

`color: var(--cyan);`

Text content rendered inside the nearest HTML element.
### Line 374

`}`

Text content rendered inside the nearest HTML element.
### Line 375

`</style>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 376

`</head>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 377

`<body>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 378

`(blank)`

Blank line used to separate nearby statements.
### Line 379

`<header>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 380

`<div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 381

`<h1 class="brand-title">Q-BIT.140</h1>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 382

`<div class="brand-sub">Interactive Quantum Engine & Adaptive Verification</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 383

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 384

`<button class="theme-btn" id="themeToggleBtn" onclick="toggleTheme()">☀️ Light Mode</button>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 385

`</header>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 386

`(blank)`

Blank line used to separate nearby statements.
### Line 387

`<div class="layout">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 388

`<!-- LEFT: Gate Toolbox -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 389

`<aside class="sidebar">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 390

`<div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 391

`<div class="section-title">Quantum Gates</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 392

`<div class="gate-grid">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 393

`<div class="gate-btn" onclick="selectGateTool('H')">H</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 394

`<div class="gate-btn" onclick="selectGateTool('X')">X</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 395

`<div class="gate-btn" onclick="selectGateTool('Y')">Y</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 396

`<div class="gate-btn" onclick="selectGateTool('Z')">Z</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 397

`<div class="gate-btn" onclick="selectGateTool('S')">S</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 398

`<div class="gate-btn" onclick="selectGateTool('T')">T</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 399

`<div class="gate-btn" onclick="selectGateTool('CZ')">CZ</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 400

`<div class="gate-btn" onclick="selectGateTool('M')">M</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 401

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 402

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 403

`(blank)`

Blank line used to separate nearby statements.
### Line 404

`<div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 405

`<div class="section-title">Circuit Controls</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 406

`<div class="btn-group">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 407

`<button class="ctrl-btn" onclick="addQubit()">+ Add Qubit</button>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 408

`<button class="ctrl-btn" onclick="removeQubit()">− Remove Qubit</button>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 409

`<button class="ctrl-btn" onclick="addColumn()">+ Add Column</button>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 410

`<button class="ctrl-btn" onclick="removeColumn()">− Remove Column</button>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 411

`<button class="ctrl-btn danger" onclick="clearCircuit()">Clear Circuit</button>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 412

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 413

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 414

`(blank)`

Blank line used to separate nearby statements.
### Line 415

`<div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 416

`<div class="section-title">API Connection</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 417

`<div style="font-size: 11px; font-family: var(--font-mono); color: var(--green);">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 418

`● Connected to M4 Gateway`

Text content rendered inside the nearest HTML element.
### Line 419

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 420

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 421

`</aside>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 422

`(blank)`

Blank line used to separate nearby statements.
### Line 423

`<!-- CENTER: Circuit Wire Grid -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 424

`<main class="center-area">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 425

`<div class="circuit-toolbar">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 426

`<span style="font-family: var(--font-mono); font-size: 13px; color: var(--text-muted);">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 427

`Selected Gate: <strong id="activeToolDisplay" style="color: var(--cyan);">None</strong>`

Text content rendered inside the nearest HTML element.
### Line 428

`</span>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 429

`<button class="ctrl-btn" onclick="presetGrover2Q()">Load 2-Qubit Grover Circuit</button>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 430

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 431

`(blank)`

Blank line used to separate nearby statements.
### Line 432

`<div class="canvas-container">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 433

`<div class="wire-grid" id="wireGrid"></div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 434

`(blank)`

Blank line used to separate nearby statements.
### Line 435

`<div class="card" id="asciiDiagramCard" style="display: none;">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 436

`<div class="card-header">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 437

`<span class="card-title">M3 Verified Qiskit Circuit Diagram</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 438

`<span class="badge" id="circuitDepthBadge">Depth: 5</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 439

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 440

`<pre class="circuit-ascii" id="circuitAsciiDiagram"></pre>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 441

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 442

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 443

`</main>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 444

`(blank)`

Blank line used to separate nearby statements.
### Line 445

`<!-- RIGHT: Activity, Prediction, M3 Simulation, M2 Adaptive Decision, M5 Guidance -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 446

`<aside class="right-panel">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 447

`<!-- 1. Activity & Prediction Input -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 448

`<div class="card">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 449

`<div class="card-header">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 450

`<span class="card-title" id="activityTitle">Grover 2-Qubit Target Prediction</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 451

`<span class="badge" id="activityConceptBadge">grover.search_problem</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 452

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 453

`<p style="font-size: 12px; color: var(--text-muted); line-height: 1.4;" id="activityPrompt">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 454

`A 2-qubit Grover search circuit has been initialized with equal superposition and executed with 1 Grover iteration marking target state |10⟩. Predict the measurement outcome.`

Text content rendered inside the nearest HTML element.
### Line 455

`</p>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 456

`<div class="input-group">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 457

`<input type="text" class="text-input" id="predictionInput" value="01" placeholder="Enter basis state (e.g. 01, 10)">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 458

`<button class="action-btn" id="submitBtn" onclick="handleRunExperiment()">Run & Evaluate</button>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 459

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 460

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 461

`(blank)`

Blank line used to separate nearby statements.
### Line 462

`<!-- 2. Real M3 Quantum Simulation Results -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 463

`<div class="card" id="quantumResultsCard" style="display: none;">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 464

`<div class="card-header">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 465

`<span class="card-title">M3 Verified Quantum Result</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 466

`<span class="badge" id="algorithmBadge">Grover (1024 shots)</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 467

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 468

`<div class="stat-grid">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 469

`<div class="stat-box">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 470

`<div class="stat-label">Target State</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 471

`<div class="stat-val" style="color: var(--green);" id="targetStateVal">|10⟩</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 472

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 473

`<div class="stat-box">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 474

`<div class="stat-label">Most Likely</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 475

`<div class="stat-val" id="mostLikelyVal">|10⟩</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 476

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 477

`<div class="stat-box">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 478

`<div class="stat-label">Target Prob</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 479

`<div class="stat-val" style="color: var(--cyan);" id="targetProbVal">93.5%</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 480

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 481

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 482

`(blank)`

Blank line used to separate nearby statements.
### Line 483

`<div class="section-title" style="margin-top: 6px;">Measured Probabilities & Counts</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 484

`<div class="hist-container" id="histogramContainer"></div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 485

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 486

`(blank)`

Blank line used to separate nearby statements.
### Line 487

`<!-- 3. M2 Learner Evidence & Adaptive Decision -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 488

`<div class="card" id="adaptiveDecisionCard" style="display: none;">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 489

`<div class="card-header">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 490

`<span class="card-title">M2 Adaptive Cognition</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 491

`<span class="badge" id="outcomeBadge">Prediction Mismatch</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 492

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 493

`<div style="font-size: 12px; line-height: 1.4;">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 494

`<div><strong>Action:</strong> <span class="badge action" id="decisionActionBadge">gather_evidence</span></div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 495

`<div style="margin-top: 6px; color: var(--text-muted);" id="decisionReasonText">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 496

`Initial prediction mismatch on 'Grover 2-Qubit Target State Prediction'. Gathering additional evidence before selecting remediation.`

Text content rendered inside the nearest HTML element.
### Line 497

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 498

`<div style="margin-top: 8px; font-size: 11px; font-family: var(--font-mono); color: var(--cyan);" id="nextActivityText">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 499

`Next Target: act_grover_2q_predict`

Text content rendered inside the nearest HTML element.
### Line 500

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 501

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 502

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 503

`(blank)`

Blank line used to separate nearby statements.
### Line 504

`<!-- 4. M5 Grounded AI Guidance -->`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 505

`<div class="card" id="aiGuidanceCard" style="display: none;">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 506

`<div class="card-header">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 507

`<span class="card-title">M5 Grounded AI Guidance</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 508

`<button class="ctrl-btn" style="padding: 4px 10px; font-size: 11px;" id="explainBtn" onclick="handleExplain()">Explain My Result</button>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 509

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 510

`<div class="explanation-box" id="aiExplanationBox">Click "Explain My Result" to generate a grounded explanation from the M5 curriculum knowledge base.</div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 511

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 512

`</aside>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 513

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 514

`(blank)`

Blank line used to separate nearby statements.
### Line 515

`<script type="module">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 516

`import { fetchActivity, submitPrediction, explainExperiment } from './api_client.js';`

Text content rendered inside the nearest HTML element.
### Line 517

`import { normalizeSubmissionResponse, formatStateLabel, formatPercentage } from './adapter.js';`

Text content rendered inside the nearest HTML element.
### Line 518

`(blank)`

Blank line used to separate nearby statements.
### Line 519

`let currentActivityId = "act_grover_2q_predict";`

Text content rendered inside the nearest HTML element.
### Line 520

`let lastSubmitData = null;`

Text content rendered inside the nearest HTML element.
### Line 521

`let selectedGate = null;`

Text content rendered inside the nearest HTML element.
### Line 522

`(blank)`

Blank line used to separate nearby statements.
### Line 523

`let circuit = {`

Text content rendered inside the nearest HTML element.
### Line 524

`num_qubits: 2,`

Text content rendered inside the nearest HTML element.
### Line 525

`num_columns: 6,`

Text content rendered inside the nearest HTML element.
### Line 526

`gates: [`

Text content rendered inside the nearest HTML element.
### Line 527

`{ id: 1, type: "H", qubit: 0, column: 0 },`

Text content rendered inside the nearest HTML element.
### Line 528

`{ id: 2, type: "H", qubit: 1, column: 0 },`

Text content rendered inside the nearest HTML element.
### Line 529

`{ id: 3, type: "X", qubit: 0, column: 1 },`

Text content rendered inside the nearest HTML element.
### Line 530

`{ id: 4, type: "CZ", qubit: 1, column: 2 },`

Text content rendered inside the nearest HTML element.
### Line 531

`{ id: 5, type: "X", qubit: 0, column: 3 },`

Text content rendered inside the nearest HTML element.
### Line 532

`{ id: 6, type: "H", qubit: 0, column: 4 },`

Text content rendered inside the nearest HTML element.
### Line 533

`{ id: 7, type: "H", qubit: 1, column: 4 },`

Text content rendered inside the nearest HTML element.
### Line 534

`{ id: 8, type: "M", qubit: 0, column: 5 },`

Text content rendered inside the nearest HTML element.
### Line 535

`{ id: 9, type: "M", qubit: 1, column: 5 },`

Text content rendered inside the nearest HTML element.
### Line 536

`]`

Text content rendered inside the nearest HTML element.
### Line 537

`};`

Text content rendered inside the nearest HTML element.
### Line 538

`(blank)`

Blank line used to separate nearby statements.
### Line 539

`window.selectGateTool = function(type) {`

Text content rendered inside the nearest HTML element.
### Line 540

`selectedGate = type;`

Text content rendered inside the nearest HTML element.
### Line 541

`document.getElementById('activeToolDisplay').textContent = type;`

Text content rendered inside the nearest HTML element.
### Line 542

`};`

Text content rendered inside the nearest HTML element.
### Line 543

`(blank)`

Blank line used to separate nearby statements.
### Line 544

`window.addQubit = function() {`

Text content rendered inside the nearest HTML element.
### Line 545

`if (circuit.num_qubits < 5) {`

Text content rendered inside the nearest HTML element.
### Line 546

`circuit.num_qubits++;`

Text content rendered inside the nearest HTML element.
### Line 547

`renderGrid();`

Text content rendered inside the nearest HTML element.
### Line 548

`}`

Text content rendered inside the nearest HTML element.
### Line 549

`};`

Text content rendered inside the nearest HTML element.
### Line 550

`(blank)`

Blank line used to separate nearby statements.
### Line 551

`window.removeQubit = function() {`

Text content rendered inside the nearest HTML element.
### Line 552

`if (circuit.num_qubits > 1) {`

Text content rendered inside the nearest HTML element.
### Line 553

`circuit.num_qubits--;`

Text content rendered inside the nearest HTML element.
### Line 554

`circuit.gates = circuit.gates.filter(g => g.qubit < circuit.num_qubits);`

Text content rendered inside the nearest HTML element.
### Line 555

`renderGrid();`

Text content rendered inside the nearest HTML element.
### Line 556

`}`

Text content rendered inside the nearest HTML element.
### Line 557

`};`

Text content rendered inside the nearest HTML element.
### Line 558

`(blank)`

Blank line used to separate nearby statements.
### Line 559

`window.addColumn = function() {`

Text content rendered inside the nearest HTML element.
### Line 560

`circuit.num_columns++;`

Text content rendered inside the nearest HTML element.
### Line 561

`renderGrid();`

Text content rendered inside the nearest HTML element.
### Line 562

`};`

Text content rendered inside the nearest HTML element.
### Line 563

`(blank)`

Blank line used to separate nearby statements.
### Line 564

`window.removeColumn = function() {`

Text content rendered inside the nearest HTML element.
### Line 565

`if (circuit.num_columns > 2) {`

Text content rendered inside the nearest HTML element.
### Line 566

`circuit.num_columns--;`

Text content rendered inside the nearest HTML element.
### Line 567

`circuit.gates = circuit.gates.filter(g => g.column < circuit.num_columns);`

Text content rendered inside the nearest HTML element.
### Line 568

`renderGrid();`

Text content rendered inside the nearest HTML element.
### Line 569

`}`

Text content rendered inside the nearest HTML element.
### Line 570

`};`

Text content rendered inside the nearest HTML element.
### Line 571

`(blank)`

Blank line used to separate nearby statements.
### Line 572

`window.clearCircuit = function() {`

Text content rendered inside the nearest HTML element.
### Line 573

`circuit.gates = [];`

Text content rendered inside the nearest HTML element.
### Line 574

`renderGrid();`

Text content rendered inside the nearest HTML element.
### Line 575

`};`

Text content rendered inside the nearest HTML element.
### Line 576

`(blank)`

Blank line used to separate nearby statements.
### Line 577

`window.presetGrover2Q = function() {`

Text content rendered inside the nearest HTML element.
### Line 578

`circuit = {`

Text content rendered inside the nearest HTML element.
### Line 579

`num_qubits: 2,`

Text content rendered inside the nearest HTML element.
### Line 580

`num_columns: 6,`

Text content rendered inside the nearest HTML element.
### Line 581

`gates: [`

Text content rendered inside the nearest HTML element.
### Line 582

`{ id: 1, type: "H", qubit: 0, column: 0 },`

Text content rendered inside the nearest HTML element.
### Line 583

`{ id: 2, type: "H", qubit: 1, column: 0 },`

Text content rendered inside the nearest HTML element.
### Line 584

`{ id: 3, type: "X", qubit: 0, column: 1 },`

Text content rendered inside the nearest HTML element.
### Line 585

`{ id: 4, type: "CZ", qubit: 1, column: 2 },`

Text content rendered inside the nearest HTML element.
### Line 586

`{ id: 5, type: "X", qubit: 0, column: 3 },`

Text content rendered inside the nearest HTML element.
### Line 587

`{ id: 6, type: "H", qubit: 0, column: 4 },`

Text content rendered inside the nearest HTML element.
### Line 588

`{ id: 7, type: "H", qubit: 1, column: 4 },`

Text content rendered inside the nearest HTML element.
### Line 589

`{ id: 8, type: "M", qubit: 0, column: 5 },`

Text content rendered inside the nearest HTML element.
### Line 590

`{ id: 9, type: "M", qubit: 1, column: 5 },`

Text content rendered inside the nearest HTML element.
### Line 591

`]`

Text content rendered inside the nearest HTML element.
### Line 592

`};`

Text content rendered inside the nearest HTML element.
### Line 593

`renderGrid();`

Text content rendered inside the nearest HTML element.
### Line 594

`};`

Text content rendered inside the nearest HTML element.
### Line 595

`(blank)`

Blank line used to separate nearby statements.
### Line 596

`function renderGrid() {`

Text content rendered inside the nearest HTML element.
### Line 597

`const container = document.getElementById('wireGrid');`

Text content rendered inside the nearest HTML element.
### Line 598

`container.innerHTML = '';`

Text content rendered inside the nearest HTML element.
### Line 599

`(blank)`

Blank line used to separate nearby statements.
### Line 600

`for (let q = 0; q < circuit.num_qubits; q++) {`

Text content rendered inside the nearest HTML element.
### Line 601

`const row = document.createElement('div');`

Text content rendered inside the nearest HTML element.
### Line 602

`row.className = 'wire-row';`

Text content rendered inside the nearest HTML element.
### Line 603

`(blank)`

Blank line used to separate nearby statements.
### Line 604

`const label = document.createElement('div');`

Text content rendered inside the nearest HTML element.
### Line 605

`label.className = 'wire-label';`

Text content rendered inside the nearest HTML element.
### Line 606

`label.textContent = \`q_${q}:\`;`

Text content rendered inside the nearest HTML element.
### Line 607

`row.appendChild(label);`

Text content rendered inside the nearest HTML element.
### Line 608

`(blank)`

Blank line used to separate nearby statements.
### Line 609

`const line = document.createElement('div');`

Text content rendered inside the nearest HTML element.
### Line 610

`line.className = 'wire-line';`

Text content rendered inside the nearest HTML element.
### Line 611

`(blank)`

Blank line used to separate nearby statements.
### Line 612

`for (let c = 0; c < circuit.num_columns; c++) {`

Text content rendered inside the nearest HTML element.
### Line 613

`const slot = document.createElement('div');`

Text content rendered inside the nearest HTML element.
### Line 614

`slot.className = 'grid-slot';`

Text content rendered inside the nearest HTML element.
### Line 615

`slot.dataset.qubit = q;`

Text content rendered inside the nearest HTML element.
### Line 616

`slot.dataset.column = c;`

Text content rendered inside the nearest HTML element.
### Line 617

`(blank)`

Blank line used to separate nearby statements.
### Line 618

`const gate = circuit.gates.find(g => g.qubit === q && g.column === c);`

Text content rendered inside the nearest HTML element.
### Line 619

`if (gate) {`

Text content rendered inside the nearest HTML element.
### Line 620

`const gateEl = document.createElement('div');`

Text content rendered inside the nearest HTML element.
### Line 621

`gateEl.className = 'placed-gate';`

Text content rendered inside the nearest HTML element.
### Line 622

`gateEl.textContent = gate.type;`

Text content rendered inside the nearest HTML element.
### Line 623

`slot.appendChild(gateEl);`

Text content rendered inside the nearest HTML element.
### Line 624

`}`

Text content rendered inside the nearest HTML element.
### Line 625

`(blank)`

Blank line used to separate nearby statements.
### Line 626

`slot.onclick = () => handleSlotClick(q, c);`

Text content rendered inside the nearest HTML element.
### Line 627

`line.appendChild(slot);`

Text content rendered inside the nearest HTML element.
### Line 628

`}`

Text content rendered inside the nearest HTML element.
### Line 629

`(blank)`

Blank line used to separate nearby statements.
### Line 630

`row.appendChild(line);`

Text content rendered inside the nearest HTML element.
### Line 631

`container.appendChild(row);`

Text content rendered inside the nearest HTML element.
### Line 632

`}`

Text content rendered inside the nearest HTML element.
### Line 633

`}`

Text content rendered inside the nearest HTML element.
### Line 634

`(blank)`

Blank line used to separate nearby statements.
### Line 635

`function handleSlotClick(q, c) {`

Text content rendered inside the nearest HTML element.
### Line 636

`const existingIdx = circuit.gates.findIndex(g => g.qubit === q && g.column === c);`

Text content rendered inside the nearest HTML element.
### Line 637

`if (existingIdx >= 0) {`

Text content rendered inside the nearest HTML element.
### Line 638

`circuit.gates.splice(existingIdx, 1);`

Text content rendered inside the nearest HTML element.
### Line 639

`} else if (selectedGate) {`

Text content rendered inside the nearest HTML element.
### Line 640

`circuit.gates.push({`

Text content rendered inside the nearest HTML element.
### Line 641

`id: Date.now(),`

Text content rendered inside the nearest HTML element.
### Line 642

`type: selectedGate,`

Text content rendered inside the nearest HTML element.
### Line 643

`qubit: q,`

Text content rendered inside the nearest HTML element.
### Line 644

`column: c`

Text content rendered inside the nearest HTML element.
### Line 645

`});`

Text content rendered inside the nearest HTML element.
### Line 646

`}`

Text content rendered inside the nearest HTML element.
### Line 647

`renderGrid();`

Text content rendered inside the nearest HTML element.
### Line 648

`}`

Text content rendered inside the nearest HTML element.
### Line 649

`(blank)`

Blank line used to separate nearby statements.
### Line 650

`window.handleRunExperiment = async function() {`

Text content rendered inside the nearest HTML element.
### Line 651

`const pred = document.getElementById('predictionInput').value.trim();`

Text content rendered inside the nearest HTML element.
### Line 652

`if (!pred) return alert('Please enter a prediction (e.g. 10 or 01)');`

Text content rendered inside the nearest HTML element.
### Line 653

`(blank)`

Blank line used to separate nearby statements.
### Line 654

`const btn = document.getElementById('submitBtn');`

Text content rendered inside the nearest HTML element.
### Line 655

`btn.disabled = true;`

Text content rendered inside the nearest HTML element.
### Line 656

`btn.textContent = 'Simulating...';`

Text content rendered inside the nearest HTML element.
### Line 657

`(blank)`

Blank line used to separate nearby statements.
### Line 658

`try {`

Text content rendered inside the nearest HTML element.
### Line 659

`const rawResponse = await submitPrediction(currentActivityId, "learner_ui_demo", pred);`

Text content rendered inside the nearest HTML element.
### Line 660

`lastSubmitData = rawResponse;`

Text content rendered inside the nearest HTML element.
### Line 661

`(blank)`

Blank line used to separate nearby statements.
### Line 662

`// Normalize response through M6 adapter`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 663

`const model = normalizeSubmissionResponse(rawResponse);`

Text content rendered inside the nearest HTML element.
### Line 664

`(blank)`

Blank line used to separate nearby statements.
### Line 665

`// 1. Render Quantum Result`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 666

`document.getElementById('quantumResultsCard').style.display = 'flex';`

Text content rendered inside the nearest HTML element.
### Line 667

`document.getElementById('targetStateVal').textContent = model.quantum.targetStateLabel;`

Text content rendered inside the nearest HTML element.
### Line 668

`document.getElementById('mostLikelyVal').textContent = model.quantum.mostLikelyStateLabel;`

Text content rendered inside the nearest HTML element.
### Line 669

`document.getElementById('targetProbVal').textContent = model.quantum.targetProbabilityStr;`

Text content rendered inside the nearest HTML element.
### Line 670

`document.getElementById('algorithmBadge').textContent = \`${model.quantum.algorithm} (${model.quantum.shots} shots)\`;`

Text content rendered inside the nearest HTML element.
### Line 671

`(blank)`

Blank line used to separate nearby statements.
### Line 672

`// Render Histogram`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 673

`const hist = document.getElementById('histogramContainer');`

Text content rendered inside the nearest HTML element.
### Line 674

`hist.innerHTML = '';`

Text content rendered inside the nearest HTML element.
### Line 675

`model.quantum.probabilityBars.forEach(b => {`

Text content rendered inside the nearest HTML element.
### Line 676

`const row = document.createElement('div');`

Text content rendered inside the nearest HTML element.
### Line 677

`row.className = 'hist-row';`

Text content rendered inside the nearest HTML element.
### Line 678

`row.innerHTML = \``

Text content rendered inside the nearest HTML element.
### Line 679

`<span class="hist-state">${b.stateLabel}</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 680

`<div class="hist-bar-bg">`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 681

`<div class="hist-bar-fill ${b.isTarget ? 'target' : ''}" style="width: ${Math.max(b.percentageNum, 3)}%;"></div>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 682

`</div>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 683

`<span class="hist-pct">${b.percentageStr} (${b.count})</span>`

Opens an HTML element; attributes configure its identity, semantics, or browser behavior.
### Line 684

`\`;`

Text content rendered inside the nearest HTML element.
### Line 685

`hist.appendChild(row);`

Text content rendered inside the nearest HTML element.
### Line 686

`});`

Text content rendered inside the nearest HTML element.
### Line 687

`(blank)`

Blank line used to separate nearby statements.
### Line 688

`// 2. Render ASCII Circuit if available`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 689

`if (model.quantum.circuit.diagram) {`

Text content rendered inside the nearest HTML element.
### Line 690

`document.getElementById('asciiDiagramCard').style.display = 'flex';`

Text content rendered inside the nearest HTML element.
### Line 691

`document.getElementById('circuitDepthBadge').textContent = \`Depth: ${model.quantum.circuit.depth}\`;`

Text content rendered inside the nearest HTML element.
### Line 692

`document.getElementById('circuitAsciiDiagram').textContent = model.quantum.circuit.diagram;`

Text content rendered inside the nearest HTML element.
### Line 693

`}`

Text content rendered inside the nearest HTML element.
### Line 694

`(blank)`

Blank line used to separate nearby statements.
### Line 695

`// 3. Render M2 Adaptive Decision`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 696

`document.getElementById('adaptiveDecisionCard').style.display = 'flex';`

Text content rendered inside the nearest HTML element.
### Line 697

`const outcomeBadge = document.getElementById('outcomeBadge');`

Text content rendered inside the nearest HTML element.
### Line 698

`outcomeBadge.textContent = model.learner.outcomeText;`

Text content rendered inside the nearest HTML element.
### Line 699

`outcomeBadge.className = \`badge ${model.learner.outcomeClass}\`;`

Text content rendered inside the nearest HTML element.
### Line 700

`(blank)`

Blank line used to separate nearby statements.
### Line 701

`document.getElementById('decisionActionBadge').textContent = model.adaptive.action;`

Text content rendered inside the nearest HTML element.
### Line 702

`document.getElementById('decisionReasonText').textContent = model.adaptive.reason;`

Text content rendered inside the nearest HTML element.
### Line 703

`document.getElementById('nextActivityText').textContent = \`Next Target: ${model.adaptive.targetActivity || 'End of sequence'}\`;`

Text content rendered inside the nearest HTML element.
### Line 704

`(blank)`

Blank line used to separate nearby statements.
### Line 705

`// 4. Reveal AI Guidance card`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 706

`document.getElementById('aiGuidanceCard').style.display = 'flex';`

Text content rendered inside the nearest HTML element.
### Line 707

`document.getElementById('aiExplanationBox').textContent = 'Click "Explain My Result" for grounded AI guidance on this attempt.';`

Text content rendered inside the nearest HTML element.
### Line 708

`(blank)`

Blank line used to separate nearby statements.
### Line 709

`} catch (err) {`

Text content rendered inside the nearest HTML element.
### Line 710

`alert(\`Error: ${err.message}\`);`

Text content rendered inside the nearest HTML element.
### Line 711

`} finally {`

Text content rendered inside the nearest HTML element.
### Line 712

`btn.disabled = false;`

Text content rendered inside the nearest HTML element.
### Line 713

`btn.textContent = 'Run & Evaluate';`

Text content rendered inside the nearest HTML element.
### Line 714

`}`

Text content rendered inside the nearest HTML element.
### Line 715

`};`

Text content rendered inside the nearest HTML element.
### Line 716

`(blank)`

Blank line used to separate nearby statements.
### Line 717

`window.handleExplain = async function() {`

Text content rendered inside the nearest HTML element.
### Line 718

`if (!lastSubmitData) return;`

Text content rendered inside the nearest HTML element.
### Line 719

`const btn = document.getElementById('explainBtn');`

Text content rendered inside the nearest HTML element.
### Line 720

`btn.disabled = true;`

Text content rendered inside the nearest HTML element.
### Line 721

`btn.textContent = 'Generating...';`

Text content rendered inside the nearest HTML element.
### Line 722

`(blank)`

Blank line used to separate nearby statements.
### Line 723

`try {`

Text content rendered inside the nearest HTML element.
### Line 724

`const exp = await explainExperiment(lastSubmitData);`

Text content rendered inside the nearest HTML element.
### Line 725

`document.getElementById('aiExplanationBox').textContent = exp.explanation;`

Text content rendered inside the nearest HTML element.
### Line 726

`} catch (err) {`

Text content rendered inside the nearest HTML element.
### Line 727

`document.getElementById('aiExplanationBox').textContent = \`AI Guidance Error: ${err.message}\`;`

Text content rendered inside the nearest HTML element.
### Line 728

`} finally {`

Text content rendered inside the nearest HTML element.
### Line 729

`btn.disabled = false;`

Text content rendered inside the nearest HTML element.
### Line 730

`btn.textContent = 'Explain My Result';`

Text content rendered inside the nearest HTML element.
### Line 731

`}`

Text content rendered inside the nearest HTML element.
### Line 732

`};`

Text content rendered inside the nearest HTML element.
### Line 733

`(blank)`

Blank line used to separate nearby statements.
### Line 734

`window.toggleTheme = function() {`

Text content rendered inside the nearest HTML element.
### Line 735

`const html = document.documentElement;`

Text content rendered inside the nearest HTML element.
### Line 736

`const isDark = html.getAttribute('data-theme') === 'dark';`

Text content rendered inside the nearest HTML element.
### Line 737

`html.setAttribute('data-theme', isDark ? 'light' : 'dark');`

Text content rendered inside the nearest HTML element.
### Line 738

`document.getElementById('themeToggleBtn').textContent = isDark ? '🌙 Dark Mode' : '☀️ Light Mode';`

Text content rendered inside the nearest HTML element.
### Line 739

`};`

Text content rendered inside the nearest HTML element.
### Line 740

`(blank)`

Blank line used to separate nearby statements.
### Line 741

`// Initialize`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 742

`renderGrid();`

Text content rendered inside the nearest HTML element.
### Line 743

`</script>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 744

`(blank)`

Blank line used to separate nearby statements.
### Line 745

`</body>`

Closes the corresponding HTML element and returns parsing to its parent.
### Line 746

`</html>`

Closes the corresponding HTML element and returns parsing to its parent.

## Nearby Files

[frontend/visualization/adapter.js](adapter.js.md), [frontend/visualization/api_client.js](api_client.js.md)
