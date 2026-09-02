# Explanation: `frontend/css/styles.css`

## Purpose

This page explains the meaningful behavior in `frontend/css/styles.css`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```css
:root {
    --bg: #03050F;
    --bg-secondary: #060A1E;
    --panel: #101736;
    --panel-border: rgba(91, 140, 255, 0.18);
    --panel-border-hi: rgba(91, 140, 255, 0.50);
    --glass: rgba(16, 23, 54, 0.65);
    --glass-2: rgba(22, 31, 68, 0.75);
    --text: #EAF0FF;
    --text-muted: #7C88B8;
    --accent: #3B82F6;
    --accent-hover: #1D4ED8;
    --accent-glow: rgba(59, 130, 246, 0.45);
    --blue-glow: rgba(59, 130, 246, 0.45);
    --cyan: #22D3EE;
    --cyan-glow: rgba(34, 211, 238, 0.40);
    --gold: #FFC845;
    --flame: #FF7A45;
    --green: #10B981;
    --yellow: #F59E0B;
    --red: #EF4444;
    --purple: #A855F7;
    --grid-line: #334155;
    --wire: #64748B;
    --gate-bg: #1E3A8A;
    --gate-text: #FFFFFF;
    --font-display: "Space Grotesk", sans-serif;
    --font-body: "Inter", sans-serif;
    --font-mono: "JetBrains Mono", monospace;
    --radius: 12px;
}

[data-theme="light"] {
    --bg: #F3F6FF;
    --bg-secondary: #E9EEFC;
    --panel: #FFFFFF;
    --panel-border: rgba(59, 130, 246, 0.20);
    --panel-border-hi: rgba(59, 130, 246, 0.45);
    --glass: rgba(255, 255, 255, 0.75);
    --glass-2: rgba(255, 255, 255, 0.90);
    --text: #0B1020;
    --text-muted: #5B638A;
    --accent: #2563EB;
    --accent-hover: #1D4ED8;
    --accent-glow: rgba(37, 99, 235, 0.25);
    --blue-glow: rgba(37, 99, 235, 0.25);
    --cyan: #0891B2;
    --cyan-glow: rgba(8, 145, 178, 0.20);
    --gold: #D97706;
    --flame: #EA580C;
    --green: #059669;
    --yellow: #D97706;
    --red: #DC2626;
    --purple: #9333EA;
    --grid-line: #CBD5E1;
    --wire: #94A3B8;
    --gate-bg: #DBEAFE;
    --gate-text: #1E3A8A;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    font-family: var(--font-body);
    background:
        radial-gradient(ellipse 60% 40% at 15% 0%, rgba(59, 130, 246, 0.16), transparent 60%),
        radial-gradient(ellipse 50% 35% at 90% 15%, rgba(34, 211, 238, 0.10), transparent 60%),
        radial-gradient(ellipse 70% 50% at 50% 100%, rgba(59, 130, 246, 0.08), transparent 60%),
        linear-gradient(180deg, var(--bg) 0%, var(--bg-secondary) 100%);
    color: var(--text);
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    position: relative;
    overflow-x: hidden;
    transition: background 0.3s ease, color 0.3s ease;
}

#fx {
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
}

/* HEADER */
header {
    padding: 12px 24px;
    background: var(--glass);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border-bottom: 1px solid var(--panel-border);
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: relative;
    z-index: 10;
}
.header-left { display: flex; align-items: center; gap: 14px; }

/* ATOM LOGO */
.atom {
    width: 36px;
    height: 36px;
    position: relative;
    filter: drop-shadow(0 0 8px var(--blue-glow));
}
.atom svg { width: 100%; height: 100%; }
.atom .orbit {
    transform-origin: 17px 17px;
    animation: spin 6s linear infinite;
}
.atom .orbit.o2 {
    animation-duration: 9s;
    animation-direction: reverse;
}
@keyframes spin { to { transform: rotate(360deg); } }
@media (prefers-reduced-motion: reduce) {
    .atom .orbit { animation: none; }
}

.brand-title {
    font-family: var(--font-display);
    font-size: 19px;
    font-weight: 700;
    letter-spacing: -0.01em;
    background: linear-gradient(90deg, #FFFFFF 20%, var(--cyan) 70%, var(--accent) 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}
[data-theme="light"] .brand-title {
    background: linear-gradient(90deg, #0B1020 20%, var(--accent) 80%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}
.brand-sub {
    font-family: var(--font-mono);
    font-size: 11px;
    color: var(--text-muted);
}

.header-right {
    display: flex;
    align-items: center;
    gap: 10px;
}

/* ACHIEVEMENT CHIPS / BADGES */
.chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--glass);
    border: 1px solid var(--panel-border);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    padding: 5px 11px;
    border-radius: 999px;
    font-family: var(--font-mono);
    font-size: 12px;
    color: var(--text);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    user-select: none;
    transition: all 0.2s ease;
}
.chip:hover {
    border-color: var(--panel-border-hi);
    transform: translateY(-1px);
}
.chip svg { width: 14px; height: 14px; }
.chip-icon { font-size: 13px; line-height: 1; }
.chip-label { font-size: 10px; color: var(--text-muted); text-transform: uppercase; }
.chip-val { font-weight: 700; color: var(--cyan); }
.chip-val.gold { color: var(--gold); }
.chip-val.flame { color: var(--flame); }
.chip-val.green { color: var(--green); }

/* PROFILE BUTTON */
.profile-btn {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--accent), var(--cyan));
    background-size: cover;
    background-position: center;
    border: none;
    color: #03050F;
    font-family: var(--font-display);
    font-weight: 700;
    font-size: 13px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.20), 0 0 14px var(--blue-glow);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.profile-btn:hover {
    transform: scale(1.05);
    box-shadow: 0 0 0 3px rgba(34, 211, 238, 0.40), 0 0 20px var(--cyan-glow);
}

/* JOURNEY TRACK */
.journey-bar {
    background: var(--glass-2);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--panel-border);
    padding: 8px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    overflow-x: auto;
    position: relative;
    z-index: 5;
}
.journey-left { display: flex; align-items: center; gap: 12px; }
.journey-title {
    font-family: var(--font-mono);
    font-size: 11px;
    color: var(--text-muted);
    text-transform: uppercase;
    white-space: nowrap;
}
.journey-steps { display: flex; align-items: center; gap: 8px; }
.journey-node {
    padding: 5px 13px;
    border-radius: 999px;
    font-size: 12px;
    font-family: var(--font-mono);
    background: var(--panel);
    border: 1px solid var(--panel-border);
    cursor: pointer;
    white-space: nowrap;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    gap: 6px;
}
.journey-node:hover {
    border-color: var(--cyan);
    transform: translateY(-1px);
}
.journey-node.active {
    border-color: var(--cyan);
    color: var(--cyan);
    font-weight: 600;
    box-shadow: 0 0 12px var(--cyan-glow);
    background: rgba(34, 211, 238, 0.12);
}
.journey-node.completed {
    border-color: var(--green);
    color: var(--green);
    background: rgba(16, 185, 129, 0.10);
}
.journey-arrow { color: var(--text-muted); font-size: 11px; }
.journey-progress-badge {
    font-family: var(--font-mono);
    font-size: 11px;
    padding: 3px 10px;
    border-radius: 6px;
    background: var(--panel);
    border: 1px solid var(--panel-border);
    color: var(--cyan);
    white-space: nowrap;
}

/* MAIN TWO-PANE WORKSPACE */
.workspace-layout {
    display: grid;
    grid-template-columns: 1.15fr 0.85fr;
    flex: 1;
    overflow: hidden;
    height: calc(100vh - 105px);
    position: relative;
    z-index: 1;
}

.pane {
    overflow-y: auto;
    padding: 18px 22px;
    display: flex;
    flex-direction: column;
    gap: 16px;
}
.pane-left {
    background: transparent;
    border-right: 1px solid var(--panel-border);
}
.pane-right {
    background: transparent;
}

/* CARDS */
.card {
    background: var(--glass);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid var(--panel-border);
    border-radius: var(--radius);
    padding: 18px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    transition: border-color 0.25s ease, box-shadow 0.25s ease, transform 0.2s ease;
    position: relative;
}
.card:hover {
    border-color: var(--panel-border-hi);
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.35);
}
.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.card-title {
    font-family: var(--font-display);
    font-size: 15px;
    font-weight: 700;
    color: var(--cyan);
    letter-spacing: -0.01em;
}

/* BADGES */
.badge {
    font-family: var(--font-mono);
    font-size: 11px;
    padding: 3px 10px;
    border-radius: 999px;
    background: var(--bg);
    border: 1px solid var(--panel-border);
}
.badge.success { color: var(--green); border-color: var(--green); }
.badge.mismatch { color: var(--red); border-color: var(--red); }
.badge.action { color: var(--yellow); border-color: var(--yellow); }
.badge.trend { color: var(--purple); border-color: var(--purple); }

/* STATE TRIAD WIDGET */
.state-triad-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin: 4px 0;
}
.triad-box {
    background: var(--panel);
    border: 1px solid var(--panel-border);
    border-radius: 10px;
    padding: 12px 10px;
    text-align: center;
    display: flex;
    flex-direction: column;
    gap: 4px;
    cursor: pointer;
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}
.triad-box:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.35);
}
.triad-box.prediction { border-color: rgba(239, 68, 68, 0.45); }
.triad-box.prediction.correct { border-color: rgba(16, 185, 129, 0.45); }
.triad-box.target { border-color: rgba(16, 185, 129, 0.45); }
.triad-box.measured { border-color: rgba(34, 211, 238, 0.45); }
.triad-label {
    font-size: 10px;
    font-family: var(--font-mono);
    text-transform: uppercase;
    color: var(--text-muted);
}
.triad-val {
    font-family: var(--font-mono);
    font-size: 18px;
    font-weight: 700;
}
.triad-val.pred { color: var(--yellow); }
.triad-val.targ { color: var(--green); }
.triad-val.meas { color: var(--cyan); }
.triad-sub {
    font-size: 11px;
    font-family: var(--font-mono);
    color: var(--text-muted);
}

/* STATE ALIGNMENT COMPARISON PANEL */
.compare-panel {
    background: rgba(0, 0, 0, 0.35);
    border: 1px solid var(--panel-border);
    border-radius: 10px;
    padding: 12px 16px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    animation: fadeIn 0.25s ease-out;
}
.compare-flow {
    display: flex;
    align-items: center;
    justify-content: space-around;
    font-family: var(--font-mono);
    font-size: 13px;
    padding: 6px 0;
}
.compare-node {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
}
.compare-node .val { font-weight: 700; font-size: 15px; }
.compare-node .lbl { font-size: 10px; color: var(--text-muted); text-transform: uppercase; }
.compare-rel {
    font-size: 18px;
    font-weight: 700;
}
.compare-rel.mismatch { color: var(--red); }
.compare-rel.match { color: var(--green); }

/* STATE INSPECTOR DETAIL DRAWER */
.state-inspector-box {
    background: var(--panel);
    border: 1px solid var(--cyan);
    border-radius: 10px;
    padding: 12px 14px;
    display: flex;
    flex-direction: column;
    gap: 6px;
    font-family: var(--font-mono);
    font-size: 12px;
    box-shadow: 0 0 16px var(--cyan-glow);
    animation: fadeIn 0.2s ease-out;
}
.inspector-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* CAUSAL TIMELINE / WHY THIS NEXT? */
.causal-chain {
    display: flex;
    flex-direction: column;
    gap: 6px;
}
.chain-step {
    background: var(--panel);
    border: 1px solid var(--panel-border);
    border-radius: 10px;
    padding: 10px 12px;
    cursor: pointer;
    transition: all 0.2s ease;
}
.chain-step:hover {
    border-color: var(--panel-border-hi);
    transform: translateX(2px);
}
.chain-step.expanded {
    border-color: var(--cyan);
    background: rgba(34, 211, 238, 0.05);
    box-shadow: 0 0 12px rgba(34, 211, 238, 0.15);
}
.chain-node-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.chain-node-title {
    font-size: 10px;
    font-family: var(--font-mono);
    text-transform: uppercase;
    color: var(--text-muted);
    display: flex;
    align-items: center;
    gap: 6px;
}
.chain-toggle-icon {
    font-size: 10px;
    color: var(--text-muted);
    transition: transform 0.2s ease;
}
.chain-step.expanded .chain-toggle-icon {
    transform: rotate(90deg);
}
.chain-node-val {
    font-family: var(--font-mono);
    font-size: 12px;
    color: var(--text);
    font-weight: 600;
    margin-top: 2px;
}
.chain-node-val.highlight-yellow { color: var(--yellow); }
.chain-node-val.highlight-cyan { color: var(--cyan); }
.chain-node-desc {
    font-size: 11px;
    line-height: 1.4;
    color: var(--text-muted);
    margin-top: 6px;
    padding-top: 6px;
    border-top: 1px dashed var(--panel-border);
    display: none;
}
.chain-step.expanded .chain-node-desc {
    display: block;
}
.chain-arrow {
    text-align: center;
    color: var(--text-muted);
    font-size: 12px;
    line-height: 1;
    font-weight: bold;
}
.supporting-chips {
    display: flex;
    flex-direction: column;
    gap: 4px;
    margin-top: 6px;
}
.evidence-chip {
    font-family: var(--font-mono);
    font-size: 11px;
    color: var(--yellow);
    background: rgba(245, 158, 11, 0.08);
    padding: 4px 8px;
    border-radius: 4px;
    border: 1px solid rgba(245, 158, 11, 0.2);
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.chain-reason {
    font-size: 12px;
    line-height: 1.45;
    color: var(--text);
    margin-top: 4px;
}
.next-step {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-color: rgba(34, 211, 238, 0.3);
    background: rgba(34, 211, 238, 0.06);
}
.next-activity-title {
    font-family: var(--font-display);
    font-size: 13px;
    font-weight: 700;
    color: var(--cyan);
}

/* BASIS PILLS */
.basis-pill-grid {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 6px;
}
.basis-pill {
    padding: 6px 14px;
    border-radius: 8px;
    background: var(--panel);
    border: 1px solid var(--panel-border);
    color: var(--text);
    font-family: var(--font-mono);
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
}
.basis-pill:hover {
    border-color: var(--cyan);
    color: var(--cyan);
    transform: translateY(-1px);
}
.basis-pill.selected {
    background: rgba(34, 211, 238, 0.15);
    border-color: var(--cyan);
    color: var(--cyan);
    box-shadow: 0 0 10px var(--cyan-glow);
}

/* PROGRESS BAR */
.execution-progress-bar {
    background: rgba(59, 130, 246, 0.12);
    border: 1px solid var(--accent);
    border-radius: 8px;
    padding: 8px 12px;
    font-family: var(--font-mono);
    font-size: 12px;
    color: var(--cyan);
    display: flex;
    align-items: center;
    gap: 8px;
    animation: pulse 1.5s infinite;
}

/* CIRCUIT STUDIO */
.circuit-studio {
    background: var(--glass);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid var(--panel-border);
    border-radius: var(--radius);
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
}
.gate-toolbar {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    align-items: center;
}
.gate-btn {
    background: var(--gate-bg);
    color: var(--gate-text);
    border: 1px solid var(--panel-border);
    padding: 6px 12px;
    border-radius: 6px;
    font-family: var(--font-mono);
    font-weight: 700;
    font-size: 12px;
    cursor: pointer;
    user-select: none;
    transition: 0.15s;
}
.gate-btn:hover { transform: translateY(-2px); box-shadow: 0 2px 8px var(--accent-glow); }
.gate-btn.active-tool { border-color: var(--cyan); box-shadow: 0 0 8px var(--cyan); }

.wire-grid {
    background: var(--bg-secondary);
    border: 1px solid var(--panel-border);
    border-radius: 10px;
    padding: 16px;
    overflow-x: auto;
}
.wire-row {
    display: flex;
    align-items: center;
    height: 48px;
    position: relative;
}
.wire-label {
    width: 44px;
    font-family: var(--font-mono);
    font-size: 13px;
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
    width: 40px;
    height: 40px;
    margin-right: 10px;
    border: 1px dashed var(--grid-line);
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    position: relative;
    z-index: 2;
    background: var(--bg);
    transition: all 0.15s ease;
}
.grid-slot:hover { border-color: var(--accent); background: var(--panel); }
.placed-gate {
    background: var(--gate-bg);
    color: var(--gate-text);
    width: 34px;
    height: 34px;
    border-radius: 5px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: var(--font-mono);
    font-weight: 700;
    font-size: 12px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
}
.placed-gate.cz-gate { background: #4C1D95; }
.placed-gate.m-gate { background: #065F46; }

.gate-info-callout {
    font-size: 11px;
    font-family: var(--font-mono);
    color: var(--text-muted);
    background: var(--bg);
    padding: 8px 12px;
    border-radius: 6px;
    border: 1px solid var(--panel-border);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* HISTOGRAM */
.hist-container { display: flex; flex-direction: column; gap: 6px; }
.hist-row {
    display: flex;
    align-items: center;
    gap: 8px;
    font-family: var(--font-mono);
    font-size: 12px;
    padding: 4px 6px;
    border-radius: 6px;
    cursor: pointer;
    transition: background 0.15s ease;
}
.hist-row:hover {
    background: rgba(255, 255, 255, 0.04);
}
.hist-row.selected {
    background: rgba(34, 211, 238, 0.08);
    border: 1px solid rgba(34, 211, 238, 0.3);
}
.hist-state { width: 38px; color: var(--cyan); font-weight: 600; }
.hist-bar-bg {
    flex: 1;
    height: 18px;
    background: var(--bg);
    border-radius: 4px;
    overflow: hidden;
    position: relative;
    border: 1px solid var(--panel-border);
}
.hist-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--accent), var(--cyan));
    border-radius: 3px;
    transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}
.hist-bar-fill.target { background: linear-gradient(90deg, #10b981, #34d399); }
.hist-bar-fill.predicted { border-right: 2px solid var(--yellow); }
.hist-pct { width: 60px; text-align: right; color: var(--text-muted); font-size: 11px; }

/* QUESTION OPTIONS */
.options-grid { display: flex; flex-direction: column; gap: 8px; }
.option-btn {
    background: var(--panel);
    border: 1px solid var(--panel-border);
    border-radius: 10px;
    padding: 10px 14px;
    display: flex;
    align-items: center;
    gap: 12px;
    color: var(--text);
    cursor: pointer;
    text-align: left;
    font-size: 13px;
    line-height: 1.4;
    transition: 0.15s;
}
.option-btn:hover { border-color: var(--accent); background: var(--panel); }
.option-btn.selected { border-color: var(--cyan); background: rgba(34, 211, 238, 0.1); }
.option-key {
    font-family: var(--font-mono);
    font-weight: 700;
    color: var(--cyan);
    width: 20px;
}

/* BUTTONS & CONTROLS */
.btn {
    background: var(--accent);
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 8px;
    font-family: var(--font-display);
    font-weight: 600;
    font-size: 13px;
    cursor: pointer;
    transition: all 0.2s ease;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.20);
}
.btn:hover { background: var(--accent-hover); transform: translateY(-1px); box-shadow: 0 4px 12px var(--blue-glow); }
.btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; box-shadow: none; }
.btn.secondary { background: var(--panel); border: 1px solid var(--panel-border); color: var(--text); }
.btn.secondary:hover { border-color: var(--panel-border-hi); }
.btn.success { background: var(--green); color: #042f2e; }
.btn.success:hover { background: #059669; }

.explanation-box {
    background: var(--panel);
    border-left: 3px solid var(--cyan);
    border-radius: 8px;
    padding: 14px;
    font-size: 13px;
    line-height: 1.6;
    max-height: 280px;
    overflow-y: auto;
}

/* CUSTOM SLEEK SCROLLBARS */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: transparent;
}
::-webkit-scrollbar-thumb {
    background: rgba(91, 140, 255, 0.25);
    border-radius: 999px;
}
::-webkit-scrollbar-thumb:hover {
    background: var(--cyan);
}

/* TACTILE PRESS FEEDBACK */
.btn:active, .profile-btn:active, .chip:active, .basis-pill:active, .option-btn:active, .journey-node:active, .gate-btn:active {
    transform: scale(0.98);
}

/* MODALS */
.modal-overlay, .overlay {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(3, 5, 15, 0.75);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    display: none;
    align-items: center;
    justify-content: center;
    z-index: 100;
}
.modal-overlay.open, .overlay.open { display: flex; }
.modal-card {
    background: var(--glass-2);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid var(--panel-border-hi);
    border-radius: 16px;
    padding: 24px;
    width: 520px;
    max-width: 90vw;
    display: flex;
    flex-direction: column;
    gap: 14px;
    box-shadow: 0 16px 48px rgba(0, 0, 0, 0.6);
    animation: modalScaleIn 0.22s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes modalScaleIn {
    from { opacity: 0; transform: scale(0.96) translateY(6px); }
    to { opacity: 1; transform: scale(1) translateY(0); }
}

/* PROFILE MODAL SPECIFICS */
.profile-modal-card {
    width: 440px;
    max-width: 90vw;
}
.profile-view { display: none; }
.profile-view.active { display: block; }
.profile-header-preview {
    display: flex;
    align-items: center;
    gap: 14px;
    padding-bottom: 14px;
    border-bottom: 1px solid var(--panel-border);
    margin-bottom: 14px;
}
.profile-avatar-large {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--accent), var(--cyan));
    background-size: cover;
    background-position: center;
    color: #03050F;
    font-family: var(--font-display);
    font-weight: 700;
    font-size: 22px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 16px var(--blue-glow);
}
.menu-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 14px;
    border-radius: 10px;
    background: var(--panel);
    border: 1px solid var(--panel-border);
    color: var(--text);
    font-size: 13px;
    font-weight: 500;
    margin-bottom: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
}
.menu-item:hover {
    border-color: var(--panel-border-hi);
    background: rgba(59, 130, 246, 0.10);
}
.toggle-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 14px;
    border-radius: 10px;
    background: var(--panel);
    border: 1px solid var(--panel-border);
    margin-bottom: 8px;
}
.toggle {
    width: 44px;
    height: 24px;
    background: var(--bg-secondary);
    border: 1px solid var(--panel-border);
    border-radius: 999px;
    position: relative;
    cursor: pointer;
    transition: background 0.2s;
}
.toggle::after {
    content: '';
    position: absolute;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: var(--text-muted);
    top: 2px;
    left: 2px;
    transition: transform 0.2s, background 0.2s;
}
.toggle.on {
    background: var(--cyan);
}
.toggle.on::after {
    transform: translateX(20px);
    background: #03050F;
}
.profile-input {
    width: 100%;
    background: var(--bg);
    border: 1px solid var(--panel-border);
    color: var(--text);
    padding: 8px 12px;
    border-radius: 8px;
    font-family: var(--font-body);
    font-size: 13px;
    margin-bottom: 12px;
}
.profile-input:focus {
    outline: none;
    border-color: var(--cyan);
    box-shadow: 0 0 8px var(--cyan-glow);
}

/* ANIMATIONS */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(4px); }
    to { opacity: 1; transform: translateY(0); }
}
/* AI GUIDANCE MARKDOWN FORMATTING */
.ai-heading {
    font-family: var(--font-display);
    font-size: 13px;
    font-weight: 700;
    color: var(--cyan);
    margin: 10px 0 4px 0;
    text-transform: uppercase;
    letter-spacing: 0.02em;
}
.ai-heading:first-child {
    margin-top: 0;
}
.ai-heading-large {
    font-family: var(--font-display);
    font-size: 14px;
    font-weight: 700;
    color: var(--text);
    margin: 12px 0 6px 0;
}
.ai-list {
    margin: 4px 0 8px 18px;
    padding: 0;
    list-style-type: disc;
    font-size: 13px;
    line-height: 1.5;
    color: var(--text);
}
.ai-list li {
    margin-bottom: 4px;
}
.ai-para {
    font-size: 13px;
    line-height: 1.55;
    margin-bottom: 8px;
    color: var(--text);
}
.ai-inline-code {
    font-family: var(--font-mono);
    font-size: 11px;
    background: rgba(34, 211, 238, 0.12);
    color: var(--cyan);
    padding: 2px 6px;
    border-radius: 4px;
    border: 1px solid rgba(34, 211, 238, 0.25);
}
.ai-ordered-item {
    font-size: 13px;
    line-height: 1.5;
    margin-bottom: 6px;
    padding-left: 8px;
    border-left: 2px solid var(--accent);
}

@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        transition-duration: 0.01ms !important;
    }
}

/* RESPONSIVENESS */
@media (max-width: 1024px) {
    .workspace-layout {
        grid-template-columns: 1fr;
        height: auto;
        overflow-y: auto;
    }
    .state-triad-grid {
        grid-template-columns: 1fr;
    }
    header {
        flex-wrap: wrap;
        gap: 10px;
    }
    .header-left {
        flex-wrap: wrap;
    }
    #topbarBadges {
        order: 3;
        width: 100%;
        justify-content: flex-start;
    }
}

@media (max-width: 640px) {
    header {
        padding: 10px 14px;
    }
    .journey-bar {
        padding: 6px 14px;
    }
    .pane {
        padding: 12px 14px;
    }
}

```

## Line Notes

### Line 1

`:root {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 2

`--bg: #03050F;`

Sets one visual or layout property for the active selector.
### Line 3

`--bg-secondary: #060A1E;`

Sets one visual or layout property for the active selector.
### Line 4

`--panel: #101736;`

Sets one visual or layout property for the active selector.
### Line 5

`--panel-border: rgba(91, 140, 255, 0.18);`

Sets one visual or layout property for the active selector.
### Line 6

`--panel-border-hi: rgba(91, 140, 255, 0.50);`

Sets one visual or layout property for the active selector.
### Line 7

`--glass: rgba(16, 23, 54, 0.65);`

Sets one visual or layout property for the active selector.
### Line 8

`--glass-2: rgba(22, 31, 68, 0.75);`

Sets one visual or layout property for the active selector.
### Line 9

`--text: #EAF0FF;`

Sets one visual or layout property for the active selector.
### Line 10

`--text-muted: #7C88B8;`

Sets one visual or layout property for the active selector.
### Line 11

`--accent: #3B82F6;`

Sets one visual or layout property for the active selector.
### Line 12

`--accent-hover: #1D4ED8;`

Sets one visual or layout property for the active selector.
### Line 13

`--accent-glow: rgba(59, 130, 246, 0.45);`

Sets one visual or layout property for the active selector.
### Line 14

`--blue-glow: rgba(59, 130, 246, 0.45);`

Sets one visual or layout property for the active selector.
### Line 15

`--cyan: #22D3EE;`

Sets one visual or layout property for the active selector.
### Line 16

`--cyan-glow: rgba(34, 211, 238, 0.40);`

Sets one visual or layout property for the active selector.
### Line 17

`--gold: #FFC845;`

Sets one visual or layout property for the active selector.
### Line 18

`--flame: #FF7A45;`

Sets one visual or layout property for the active selector.
### Line 19

`--green: #10B981;`

Sets one visual or layout property for the active selector.
### Line 20

`--yellow: #F59E0B;`

Sets one visual or layout property for the active selector.
### Line 21

`--red: #EF4444;`

Sets one visual or layout property for the active selector.
### Line 22

`--purple: #A855F7;`

Sets one visual or layout property for the active selector.
### Line 23

`--grid-line: #334155;`

Sets one visual or layout property for the active selector.
### Line 24

`--wire: #64748B;`

Sets one visual or layout property for the active selector.
### Line 25

`--gate-bg: #1E3A8A;`

Sets one visual or layout property for the active selector.
### Line 26

`--gate-text: #FFFFFF;`

Sets one visual or layout property for the active selector.
### Line 27

`--font-display: "Space Grotesk", sans-serif;`

Sets one visual or layout property for the active selector.
### Line 28

`--font-body: "Inter", sans-serif;`

Sets one visual or layout property for the active selector.
### Line 29

`--font-mono: "JetBrains Mono", monospace;`

Sets one visual or layout property for the active selector.
### Line 30

`--radius: 12px;`

Sets one visual or layout property for the active selector.
### Line 31

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 32

`(blank)`

Blank line used to separate nearby statements.
### Line 33

`[data-theme="light"] {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 34

`--bg: #F3F6FF;`

Sets one visual or layout property for the active selector.
### Line 35

`--bg-secondary: #E9EEFC;`

Sets one visual or layout property for the active selector.
### Line 36

`--panel: #FFFFFF;`

Sets one visual or layout property for the active selector.
### Line 37

`--panel-border: rgba(59, 130, 246, 0.20);`

Sets one visual or layout property for the active selector.
### Line 38

`--panel-border-hi: rgba(59, 130, 246, 0.45);`

Sets one visual or layout property for the active selector.
### Line 39

`--glass: rgba(255, 255, 255, 0.75);`

Sets one visual or layout property for the active selector.
### Line 40

`--glass-2: rgba(255, 255, 255, 0.90);`

Sets one visual or layout property for the active selector.
### Line 41

`--text: #0B1020;`

Sets one visual or layout property for the active selector.
### Line 42

`--text-muted: #5B638A;`

Sets one visual or layout property for the active selector.
### Line 43

`--accent: #2563EB;`

Sets one visual or layout property for the active selector.
### Line 44

`--accent-hover: #1D4ED8;`

Sets one visual or layout property for the active selector.
### Line 45

`--accent-glow: rgba(37, 99, 235, 0.25);`

Sets one visual or layout property for the active selector.
### Line 46

`--blue-glow: rgba(37, 99, 235, 0.25);`

Sets one visual or layout property for the active selector.
### Line 47

`--cyan: #0891B2;`

Sets one visual or layout property for the active selector.
### Line 48

`--cyan-glow: rgba(8, 145, 178, 0.20);`

Sets one visual or layout property for the active selector.
### Line 49

`--gold: #D97706;`

Sets one visual or layout property for the active selector.
### Line 50

`--flame: #EA580C;`

Sets one visual or layout property for the active selector.
### Line 51

`--green: #059669;`

Sets one visual or layout property for the active selector.
### Line 52

`--yellow: #D97706;`

Sets one visual or layout property for the active selector.
### Line 53

`--red: #DC2626;`

Sets one visual or layout property for the active selector.
### Line 54

`--purple: #9333EA;`

Sets one visual or layout property for the active selector.
### Line 55

`--grid-line: #CBD5E1;`

Sets one visual or layout property for the active selector.
### Line 56

`--wire: #94A3B8;`

Sets one visual or layout property for the active selector.
### Line 57

`--gate-bg: #DBEAFE;`

Sets one visual or layout property for the active selector.
### Line 58

`--gate-text: #1E3A8A;`

Sets one visual or layout property for the active selector.
### Line 59

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 60

`(blank)`

Blank line used to separate nearby statements.
### Line 61

`* { box-sizing: border-box; margin: 0; padding: 0; }`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 62

`(blank)`

Blank line used to separate nearby statements.
### Line 63

`body {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 64

`font-family: var(--font-body);`

Sets one visual or layout property for the active selector.
### Line 65

`background:`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 66

`radial-gradient(ellipse 60% 40% at 15% 0%, rgba(59, 130, 246, 0.16), transparent 60%),`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 67

`radial-gradient(ellipse 50% 35% at 90% 15%, rgba(34, 211, 238, 0.10), transparent 60%),`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 68

`radial-gradient(ellipse 70% 50% at 50% 100%, rgba(59, 130, 246, 0.08), transparent 60%),`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 69

`linear-gradient(180deg, var(--bg) 0%, var(--bg-secondary) 100%);`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 70

`color: var(--text);`

Sets one visual or layout property for the active selector.
### Line 71

`min-height: 100vh;`

Sets one visual or layout property for the active selector.
### Line 72

`display: flex;`

Sets one visual or layout property for the active selector.
### Line 73

`flex-direction: column;`

Sets one visual or layout property for the active selector.
### Line 74

`position: relative;`

Sets one visual or layout property for the active selector.
### Line 75

`overflow-x: hidden;`

Sets one visual or layout property for the active selector.
### Line 76

`transition: background 0.3s ease, color 0.3s ease;`

Sets one visual or layout property for the active selector.
### Line 77

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 78

`(blank)`

Blank line used to separate nearby statements.
### Line 79

`#fx {`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 80

`position: fixed;`

Sets one visual or layout property for the active selector.
### Line 81

`inset: 0;`

Sets one visual or layout property for the active selector.
### Line 82

`z-index: 0;`

Sets one visual or layout property for the active selector.
### Line 83

`pointer-events: none;`

Sets one visual or layout property for the active selector.
### Line 84

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 85

`(blank)`

Blank line used to separate nearby statements.
### Line 86

`/* HEADER */`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 87

`header {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 88

`padding: 12px 24px;`

Sets one visual or layout property for the active selector.
### Line 89

`background: var(--glass);`

Sets one visual or layout property for the active selector.
### Line 90

`backdrop-filter: blur(14px);`

Sets one visual or layout property for the active selector.
### Line 91

`-webkit-backdrop-filter: blur(14px);`

Sets one visual or layout property for the active selector.
### Line 92

`border-bottom: 1px solid var(--panel-border);`

Sets one visual or layout property for the active selector.
### Line 93

`display: flex;`

Sets one visual or layout property for the active selector.
### Line 94

`justify-content: space-between;`

Sets one visual or layout property for the active selector.
### Line 95

`align-items: center;`

Sets one visual or layout property for the active selector.
### Line 96

`position: relative;`

Sets one visual or layout property for the active selector.
### Line 97

`z-index: 10;`

Sets one visual or layout property for the active selector.
### Line 98

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 99

`.header-left { display: flex; align-items: center; gap: 14px; }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 100

`(blank)`

Blank line used to separate nearby statements.
### Line 101

`/* ATOM LOGO */`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 102

`.atom {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 103

`width: 36px;`

Sets one visual or layout property for the active selector.
### Line 104

`height: 36px;`

Sets one visual or layout property for the active selector.
### Line 105

`position: relative;`

Sets one visual or layout property for the active selector.
### Line 106

`filter: drop-shadow(0 0 8px var(--blue-glow));`

Sets one visual or layout property for the active selector.
### Line 107

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 108

`.atom svg { width: 100%; height: 100%; }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 109

`.atom .orbit {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 110

`transform-origin: 17px 17px;`

Sets one visual or layout property for the active selector.
### Line 111

`animation: spin 6s linear infinite;`

Sets one visual or layout property for the active selector.
### Line 112

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 113

`.atom .orbit.o2 {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 114

`animation-duration: 9s;`

Sets one visual or layout property for the active selector.
### Line 115

`animation-direction: reverse;`

Sets one visual or layout property for the active selector.
### Line 116

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 117

`@keyframes spin { to { transform: rotate(360deg); } }`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 118

`@media (prefers-reduced-motion: reduce) {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 119

`.atom .orbit { animation: none; }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 120

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 121

`(blank)`

Blank line used to separate nearby statements.
### Line 122

`.brand-title {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 123

`font-family: var(--font-display);`

Sets one visual or layout property for the active selector.
### Line 124

`font-size: 19px;`

Sets one visual or layout property for the active selector.
### Line 125

`font-weight: 700;`

Sets one visual or layout property for the active selector.
### Line 126

`letter-spacing: -0.01em;`

Sets one visual or layout property for the active selector.
### Line 127

`background: linear-gradient(90deg, #FFFFFF 20%, var(--cyan) 70%, var(--accent) 100%);`

Sets one visual or layout property for the active selector.
### Line 128

`-webkit-background-clip: text;`

Sets one visual or layout property for the active selector.
### Line 129

`background-clip: text;`

Sets one visual or layout property for the active selector.
### Line 130

`color: transparent;`

Sets one visual or layout property for the active selector.
### Line 131

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 132

`[data-theme="light"] .brand-title {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 133

`background: linear-gradient(90deg, #0B1020 20%, var(--accent) 80%);`

Sets one visual or layout property for the active selector.
### Line 134

`-webkit-background-clip: text;`

Sets one visual or layout property for the active selector.
### Line 135

`background-clip: text;`

Sets one visual or layout property for the active selector.
### Line 136

`color: transparent;`

Sets one visual or layout property for the active selector.
### Line 137

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 138

`.brand-sub {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 139

`font-family: var(--font-mono);`

Sets one visual or layout property for the active selector.
### Line 140

`font-size: 11px;`

Sets one visual or layout property for the active selector.
### Line 141

`color: var(--text-muted);`

Sets one visual or layout property for the active selector.
### Line 142

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 143

`(blank)`

Blank line used to separate nearby statements.
### Line 144

`.header-right {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 145

`display: flex;`

Sets one visual or layout property for the active selector.
### Line 146

`align-items: center;`

Sets one visual or layout property for the active selector.
### Line 147

`gap: 10px;`

Sets one visual or layout property for the active selector.
### Line 148

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 149

`(blank)`

Blank line used to separate nearby statements.
### Line 150

`/* ACHIEVEMENT CHIPS / BADGES */`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 151

`.chip {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 152

`display: inline-flex;`

Sets one visual or layout property for the active selector.
### Line 153

`align-items: center;`

Sets one visual or layout property for the active selector.
### Line 154

`gap: 6px;`

Sets one visual or layout property for the active selector.
### Line 155

`background: var(--glass);`

Sets one visual or layout property for the active selector.
### Line 156

`border: 1px solid var(--panel-border);`

Sets one visual or layout property for the active selector.
### Line 157

`backdrop-filter: blur(10px);`

Sets one visual or layout property for the active selector.
### Line 158

`-webkit-backdrop-filter: blur(10px);`

Sets one visual or layout property for the active selector.
### Line 159

`padding: 5px 11px;`

Sets one visual or layout property for the active selector.
### Line 160

`border-radius: 999px;`

Sets one visual or layout property for the active selector.
### Line 161

`font-family: var(--font-mono);`

Sets one visual or layout property for the active selector.
### Line 162

`font-size: 12px;`

Sets one visual or layout property for the active selector.
### Line 163

`color: var(--text);`

Sets one visual or layout property for the active selector.
### Line 164

`box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);`

Sets one visual or layout property for the active selector.
### Line 165

`user-select: none;`

Sets one visual or layout property for the active selector.
### Line 166

`transition: all 0.2s ease;`

Sets one visual or layout property for the active selector.
### Line 167

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 168

`.chip:hover {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 169

`border-color: var(--panel-border-hi);`

Sets one visual or layout property for the active selector.
### Line 170

`transform: translateY(-1px);`

Sets one visual or layout property for the active selector.
### Line 171

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 172

`.chip svg { width: 14px; height: 14px; }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 173

`.chip-icon { font-size: 13px; line-height: 1; }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 174

`.chip-label { font-size: 10px; color: var(--text-muted); text-transform: uppercase; }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 175

`.chip-val { font-weight: 700; color: var(--cyan); }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 176

`.chip-val.gold { color: var(--gold); }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 177

`.chip-val.flame { color: var(--flame); }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 178

`.chip-val.green { color: var(--green); }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 179

`(blank)`

Blank line used to separate nearby statements.
### Line 180

`/* PROFILE BUTTON */`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 181

`.profile-btn {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 182

`width: 38px;`

Sets one visual or layout property for the active selector.
### Line 183

`height: 38px;`

Sets one visual or layout property for the active selector.
### Line 184

`border-radius: 50%;`

Sets one visual or layout property for the active selector.
### Line 185

`background: linear-gradient(135deg, var(--accent), var(--cyan));`

Sets one visual or layout property for the active selector.
### Line 186

`background-size: cover;`

Sets one visual or layout property for the active selector.
### Line 187

`background-position: center;`

Sets one visual or layout property for the active selector.
### Line 188

`border: none;`

Sets one visual or layout property for the active selector.
### Line 189

`color: #03050F;`

Sets one visual or layout property for the active selector.
### Line 190

`font-family: var(--font-display);`

Sets one visual or layout property for the active selector.
### Line 191

`font-weight: 700;`

Sets one visual or layout property for the active selector.
### Line 192

`font-size: 13px;`

Sets one visual or layout property for the active selector.
### Line 193

`display: flex;`

Sets one visual or layout property for the active selector.
### Line 194

`align-items: center;`

Sets one visual or layout property for the active selector.
### Line 195

`justify-content: center;`

Sets one visual or layout property for the active selector.
### Line 196

`cursor: pointer;`

Sets one visual or layout property for the active selector.
### Line 197

`box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.20), 0 0 14px var(--blue-glow);`

Sets one visual or layout property for the active selector.
### Line 198

`transition: transform 0.2s ease, box-shadow 0.2s ease;`

Sets one visual or layout property for the active selector.
### Line 199

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 200

`.profile-btn:hover {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 201

`transform: scale(1.05);`

Sets one visual or layout property for the active selector.
### Line 202

`box-shadow: 0 0 0 3px rgba(34, 211, 238, 0.40), 0 0 20px var(--cyan-glow);`

Sets one visual or layout property for the active selector.
### Line 203

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 204

`(blank)`

Blank line used to separate nearby statements.
### Line 205

`/* JOURNEY TRACK */`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 206

`.journey-bar {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 207

`background: var(--glass-2);`

Sets one visual or layout property for the active selector.
### Line 208

`backdrop-filter: blur(12px);`

Sets one visual or layout property for the active selector.
### Line 209

`-webkit-backdrop-filter: blur(12px);`

Sets one visual or layout property for the active selector.
### Line 210

`border-bottom: 1px solid var(--panel-border);`

Sets one visual or layout property for the active selector.
### Line 211

`padding: 8px 24px;`

Sets one visual or layout property for the active selector.
### Line 212

`display: flex;`

Sets one visual or layout property for the active selector.
### Line 213

`align-items: center;`

Sets one visual or layout property for the active selector.
### Line 214

`justify-content: space-between;`

Sets one visual or layout property for the active selector.
### Line 215

`gap: 12px;`

Sets one visual or layout property for the active selector.
### Line 216

`overflow-x: auto;`

Sets one visual or layout property for the active selector.
### Line 217

`position: relative;`

Sets one visual or layout property for the active selector.
### Line 218

`z-index: 5;`

Sets one visual or layout property for the active selector.
### Line 219

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 220

`.journey-left { display: flex; align-items: center; gap: 12px; }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 221

`.journey-title {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 222

`font-family: var(--font-mono);`

Sets one visual or layout property for the active selector.
### Line 223

`font-size: 11px;`

Sets one visual or layout property for the active selector.
### Line 224

`color: var(--text-muted);`

Sets one visual or layout property for the active selector.
### Line 225

`text-transform: uppercase;`

Sets one visual or layout property for the active selector.
### Line 226

`white-space: nowrap;`

Sets one visual or layout property for the active selector.
### Line 227

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 228

`.journey-steps { display: flex; align-items: center; gap: 8px; }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 229

`.journey-node {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 230

`padding: 5px 13px;`

Sets one visual or layout property for the active selector.
### Line 231

`border-radius: 999px;`

Sets one visual or layout property for the active selector.
### Line 232

`font-size: 12px;`

Sets one visual or layout property for the active selector.
### Line 233

`font-family: var(--font-mono);`

Sets one visual or layout property for the active selector.
### Line 234

`background: var(--panel);`

Sets one visual or layout property for the active selector.
### Line 235

`border: 1px solid var(--panel-border);`

Sets one visual or layout property for the active selector.
### Line 236

`cursor: pointer;`

Sets one visual or layout property for the active selector.
### Line 237

`white-space: nowrap;`

Sets one visual or layout property for the active selector.
### Line 238

`transition: all 0.2s ease;`

Sets one visual or layout property for the active selector.
### Line 239

`display: flex;`

Sets one visual or layout property for the active selector.
### Line 240

`align-items: center;`

Sets one visual or layout property for the active selector.
### Line 241

`gap: 6px;`

Sets one visual or layout property for the active selector.
### Line 242

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 243

`.journey-node:hover {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 244

`border-color: var(--cyan);`

Sets one visual or layout property for the active selector.
### Line 245

`transform: translateY(-1px);`

Sets one visual or layout property for the active selector.
### Line 246

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 247

`.journey-node.active {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 248

`border-color: var(--cyan);`

Sets one visual or layout property for the active selector.
### Line 249

`color: var(--cyan);`

Sets one visual or layout property for the active selector.
### Line 250

`font-weight: 600;`

Sets one visual or layout property for the active selector.
### Line 251

`box-shadow: 0 0 12px var(--cyan-glow);`

Sets one visual or layout property for the active selector.
### Line 252

`background: rgba(34, 211, 238, 0.12);`

Sets one visual or layout property for the active selector.
### Line 253

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 254

`.journey-node.completed {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 255

`border-color: var(--green);`

Sets one visual or layout property for the active selector.
### Line 256

`color: var(--green);`

Sets one visual or layout property for the active selector.
### Line 257

`background: rgba(16, 185, 129, 0.10);`

Sets one visual or layout property for the active selector.
### Line 258

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 259

`.journey-arrow { color: var(--text-muted); font-size: 11px; }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 260

`.journey-progress-badge {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 261

`font-family: var(--font-mono);`

Sets one visual or layout property for the active selector.
### Line 262

`font-size: 11px;`

Sets one visual or layout property for the active selector.
### Line 263

`padding: 3px 10px;`

Sets one visual or layout property for the active selector.
### Line 264

`border-radius: 6px;`

Sets one visual or layout property for the active selector.
### Line 265

`background: var(--panel);`

Sets one visual or layout property for the active selector.
### Line 266

`border: 1px solid var(--panel-border);`

Sets one visual or layout property for the active selector.
### Line 267

`color: var(--cyan);`

Sets one visual or layout property for the active selector.
### Line 268

`white-space: nowrap;`

Sets one visual or layout property for the active selector.
### Line 269

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 270

`(blank)`

Blank line used to separate nearby statements.
### Line 271

`/* MAIN TWO-PANE WORKSPACE */`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 272

`.workspace-layout {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 273

`display: grid;`

Sets one visual or layout property for the active selector.
### Line 274

`grid-template-columns: 1.15fr 0.85fr;`

Sets one visual or layout property for the active selector.
### Line 275

`flex: 1;`

Sets one visual or layout property for the active selector.
### Line 276

`overflow: hidden;`

Sets one visual or layout property for the active selector.
### Line 277

`height: calc(100vh - 105px);`

Sets one visual or layout property for the active selector.
### Line 278

`position: relative;`

Sets one visual or layout property for the active selector.
### Line 279

`z-index: 1;`

Sets one visual or layout property for the active selector.
### Line 280

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 281

`(blank)`

Blank line used to separate nearby statements.
### Line 282

`.pane {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 283

`overflow-y: auto;`

Sets one visual or layout property for the active selector.
### Line 284

`padding: 18px 22px;`

Sets one visual or layout property for the active selector.
### Line 285

`display: flex;`

Sets one visual or layout property for the active selector.
### Line 286

`flex-direction: column;`

Sets one visual or layout property for the active selector.
### Line 287

`gap: 16px;`

Sets one visual or layout property for the active selector.
### Line 288

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 289

`.pane-left {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 290

`background: transparent;`

Sets one visual or layout property for the active selector.
### Line 291

`border-right: 1px solid var(--panel-border);`

Sets one visual or layout property for the active selector.
### Line 292

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 293

`.pane-right {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 294

`background: transparent;`

Sets one visual or layout property for the active selector.
### Line 295

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 296

`(blank)`

Blank line used to separate nearby statements.
### Line 297

`/* CARDS */`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 298

`.card {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 299

`background: var(--glass);`

Sets one visual or layout property for the active selector.
### Line 300

`backdrop-filter: blur(12px);`

Sets one visual or layout property for the active selector.
### Line 301

`-webkit-backdrop-filter: blur(12px);`

Sets one visual or layout property for the active selector.
### Line 302

`border: 1px solid var(--panel-border);`

Sets one visual or layout property for the active selector.
### Line 303

`border-radius: var(--radius);`

Sets one visual or layout property for the active selector.
### Line 304

`padding: 18px;`

Sets one visual or layout property for the active selector.
### Line 305

`display: flex;`

Sets one visual or layout property for the active selector.
### Line 306

`flex-direction: column;`

Sets one visual or layout property for the active selector.
### Line 307

`gap: 12px;`

Sets one visual or layout property for the active selector.
### Line 308

`box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);`

Sets one visual or layout property for the active selector.
### Line 309

`transition: border-color 0.25s ease, box-shadow 0.25s ease, transform 0.2s ease;`

Sets one visual or layout property for the active selector.
### Line 310

`position: relative;`

Sets one visual or layout property for the active selector.
### Line 311

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 312

`.card:hover {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 313

`border-color: var(--panel-border-hi);`

Sets one visual or layout property for the active selector.
### Line 314

`box-shadow: 0 6px 24px rgba(0, 0, 0, 0.35);`

Sets one visual or layout property for the active selector.
### Line 315

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 316

`.card-header {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 317

`display: flex;`

Sets one visual or layout property for the active selector.
### Line 318

`justify-content: space-between;`

Sets one visual or layout property for the active selector.
### Line 319

`align-items: center;`

Sets one visual or layout property for the active selector.
### Line 320

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 321

`.card-title {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 322

`font-family: var(--font-display);`

Sets one visual or layout property for the active selector.
### Line 323

`font-size: 15px;`

Sets one visual or layout property for the active selector.
### Line 324

`font-weight: 700;`

Sets one visual or layout property for the active selector.
### Line 325

`color: var(--cyan);`

Sets one visual or layout property for the active selector.
### Line 326

`letter-spacing: -0.01em;`

Sets one visual or layout property for the active selector.
### Line 327

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 328

`(blank)`

Blank line used to separate nearby statements.
### Line 329

`/* BADGES */`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 330

`.badge {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 331

`font-family: var(--font-mono);`

Sets one visual or layout property for the active selector.
### Line 332

`font-size: 11px;`

Sets one visual or layout property for the active selector.
### Line 333

`padding: 3px 10px;`

Sets one visual or layout property for the active selector.
### Line 334

`border-radius: 999px;`

Sets one visual or layout property for the active selector.
### Line 335

`background: var(--bg);`

Sets one visual or layout property for the active selector.
### Line 336

`border: 1px solid var(--panel-border);`

Sets one visual or layout property for the active selector.
### Line 337

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 338

`.badge.success { color: var(--green); border-color: var(--green); }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 339

`.badge.mismatch { color: var(--red); border-color: var(--red); }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 340

`.badge.action { color: var(--yellow); border-color: var(--yellow); }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 341

`.badge.trend { color: var(--purple); border-color: var(--purple); }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 342

`(blank)`

Blank line used to separate nearby statements.
### Line 343

`/* STATE TRIAD WIDGET */`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 344

`.state-triad-grid {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 345

`display: grid;`

Sets one visual or layout property for the active selector.
### Line 346

`grid-template-columns: repeat(3, 1fr);`

Sets one visual or layout property for the active selector.
### Line 347

`gap: 10px;`

Sets one visual or layout property for the active selector.
### Line 348

`margin: 4px 0;`

Sets one visual or layout property for the active selector.
### Line 349

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 350

`.triad-box {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 351

`background: var(--panel);`

Sets one visual or layout property for the active selector.
### Line 352

`border: 1px solid var(--panel-border);`

Sets one visual or layout property for the active selector.
### Line 353

`border-radius: 10px;`

Sets one visual or layout property for the active selector.
### Line 354

`padding: 12px 10px;`

Sets one visual or layout property for the active selector.
### Line 355

`text-align: center;`

Sets one visual or layout property for the active selector.
### Line 356

`display: flex;`

Sets one visual or layout property for the active selector.
### Line 357

`flex-direction: column;`

Sets one visual or layout property for the active selector.
### Line 358

`gap: 4px;`

Sets one visual or layout property for the active selector.
### Line 359

`cursor: pointer;`

Sets one visual or layout property for the active selector.
### Line 360

`transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;`

Sets one visual or layout property for the active selector.
### Line 361

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 362

`.triad-box:hover {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 363

`transform: translateY(-2px);`

Sets one visual or layout property for the active selector.
### Line 364

`box-shadow: 0 6px 16px rgba(0, 0, 0, 0.35);`

Sets one visual or layout property for the active selector.
### Line 365

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 366

`.triad-box.prediction { border-color: rgba(239, 68, 68, 0.45); }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 367

`.triad-box.prediction.correct { border-color: rgba(16, 185, 129, 0.45); }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 368

`.triad-box.target { border-color: rgba(16, 185, 129, 0.45); }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 369

`.triad-box.measured { border-color: rgba(34, 211, 238, 0.45); }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 370

`.triad-label {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 371

`font-size: 10px;`

Sets one visual or layout property for the active selector.
### Line 372

`font-family: var(--font-mono);`

Sets one visual or layout property for the active selector.
### Line 373

`text-transform: uppercase;`

Sets one visual or layout property for the active selector.
### Line 374

`color: var(--text-muted);`

Sets one visual or layout property for the active selector.
### Line 375

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 376

`.triad-val {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 377

`font-family: var(--font-mono);`

Sets one visual or layout property for the active selector.
### Line 378

`font-size: 18px;`

Sets one visual or layout property for the active selector.
### Line 379

`font-weight: 700;`

Sets one visual or layout property for the active selector.
### Line 380

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 381

`.triad-val.pred { color: var(--yellow); }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 382

`.triad-val.targ { color: var(--green); }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 383

`.triad-val.meas { color: var(--cyan); }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 384

`.triad-sub {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 385

`font-size: 11px;`

Sets one visual or layout property for the active selector.
### Line 386

`font-family: var(--font-mono);`

Sets one visual or layout property for the active selector.
### Line 387

`color: var(--text-muted);`

Sets one visual or layout property for the active selector.
### Line 388

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 389

`(blank)`

Blank line used to separate nearby statements.
### Line 390

`/* STATE ALIGNMENT COMPARISON PANEL */`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 391

`.compare-panel {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 392

`background: rgba(0, 0, 0, 0.35);`

Sets one visual or layout property for the active selector.
### Line 393

`border: 1px solid var(--panel-border);`

Sets one visual or layout property for the active selector.
### Line 394

`border-radius: 10px;`

Sets one visual or layout property for the active selector.
### Line 395

`padding: 12px 16px;`

Sets one visual or layout property for the active selector.
### Line 396

`display: flex;`

Sets one visual or layout property for the active selector.
### Line 397

`flex-direction: column;`

Sets one visual or layout property for the active selector.
### Line 398

`gap: 8px;`

Sets one visual or layout property for the active selector.
### Line 399

`animation: fadeIn 0.25s ease-out;`

Sets one visual or layout property for the active selector.
### Line 400

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 401

`.compare-flow {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 402

`display: flex;`

Sets one visual or layout property for the active selector.
### Line 403

`align-items: center;`

Sets one visual or layout property for the active selector.
### Line 404

`justify-content: space-around;`

Sets one visual or layout property for the active selector.
### Line 405

`font-family: var(--font-mono);`

Sets one visual or layout property for the active selector.
### Line 406

`font-size: 13px;`

Sets one visual or layout property for the active selector.
### Line 407

`padding: 6px 0;`

Sets one visual or layout property for the active selector.
### Line 408

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 409

`.compare-node {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 410

`display: flex;`

Sets one visual or layout property for the active selector.
### Line 411

`flex-direction: column;`

Sets one visual or layout property for the active selector.
### Line 412

`align-items: center;`

Sets one visual or layout property for the active selector.
### Line 413

`gap: 2px;`

Sets one visual or layout property for the active selector.
### Line 414

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 415

`.compare-node .val { font-weight: 700; font-size: 15px; }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 416

`.compare-node .lbl { font-size: 10px; color: var(--text-muted); text-transform: uppercase; }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 417

`.compare-rel {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 418

`font-size: 18px;`

Sets one visual or layout property for the active selector.
### Line 419

`font-weight: 700;`

Sets one visual or layout property for the active selector.
### Line 420

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 421

`.compare-rel.mismatch { color: var(--red); }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 422

`.compare-rel.match { color: var(--green); }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 423

`(blank)`

Blank line used to separate nearby statements.
### Line 424

`/* STATE INSPECTOR DETAIL DRAWER */`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 425

`.state-inspector-box {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 426

`background: var(--panel);`

Sets one visual or layout property for the active selector.
### Line 427

`border: 1px solid var(--cyan);`

Sets one visual or layout property for the active selector.
### Line 428

`border-radius: 10px;`

Sets one visual or layout property for the active selector.
### Line 429

`padding: 12px 14px;`

Sets one visual or layout property for the active selector.
### Line 430

`display: flex;`

Sets one visual or layout property for the active selector.
### Line 431

`flex-direction: column;`

Sets one visual or layout property for the active selector.
### Line 432

`gap: 6px;`

Sets one visual or layout property for the active selector.
### Line 433

`font-family: var(--font-mono);`

Sets one visual or layout property for the active selector.
### Line 434

`font-size: 12px;`

Sets one visual or layout property for the active selector.
### Line 435

`box-shadow: 0 0 16px var(--cyan-glow);`

Sets one visual or layout property for the active selector.
### Line 436

`animation: fadeIn 0.2s ease-out;`

Sets one visual or layout property for the active selector.
### Line 437

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 438

`.inspector-row {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 439

`display: flex;`

Sets one visual or layout property for the active selector.
### Line 440

`justify-content: space-between;`

Sets one visual or layout property for the active selector.
### Line 441

`align-items: center;`

Sets one visual or layout property for the active selector.
### Line 442

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 443

`(blank)`

Blank line used to separate nearby statements.
### Line 444

`/* CAUSAL TIMELINE / WHY THIS NEXT? */`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 445

`.causal-chain {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 446

`display: flex;`

Sets one visual or layout property for the active selector.
### Line 447

`flex-direction: column;`

Sets one visual or layout property for the active selector.
### Line 448

`gap: 6px;`

Sets one visual or layout property for the active selector.
### Line 449

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 450

`.chain-step {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 451

`background: var(--panel);`

Sets one visual or layout property for the active selector.
### Line 452

`border: 1px solid var(--panel-border);`

Sets one visual or layout property for the active selector.
### Line 453

`border-radius: 10px;`

Sets one visual or layout property for the active selector.
### Line 454

`padding: 10px 12px;`

Sets one visual or layout property for the active selector.
### Line 455

`cursor: pointer;`

Sets one visual or layout property for the active selector.
### Line 456

`transition: all 0.2s ease;`

Sets one visual or layout property for the active selector.
### Line 457

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 458

`.chain-step:hover {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 459

`border-color: var(--panel-border-hi);`

Sets one visual or layout property for the active selector.
### Line 460

`transform: translateX(2px);`

Sets one visual or layout property for the active selector.
### Line 461

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 462

`.chain-step.expanded {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 463

`border-color: var(--cyan);`

Sets one visual or layout property for the active selector.
### Line 464

`background: rgba(34, 211, 238, 0.05);`

Sets one visual or layout property for the active selector.
### Line 465

`box-shadow: 0 0 12px rgba(34, 211, 238, 0.15);`

Sets one visual or layout property for the active selector.
### Line 466

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 467

`.chain-node-header {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 468

`display: flex;`

Sets one visual or layout property for the active selector.
### Line 469

`justify-content: space-between;`

Sets one visual or layout property for the active selector.
### Line 470

`align-items: center;`

Sets one visual or layout property for the active selector.
### Line 471

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 472

`.chain-node-title {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 473

`font-size: 10px;`

Sets one visual or layout property for the active selector.
### Line 474

`font-family: var(--font-mono);`

Sets one visual or layout property for the active selector.
### Line 475

`text-transform: uppercase;`

Sets one visual or layout property for the active selector.
### Line 476

`color: var(--text-muted);`

Sets one visual or layout property for the active selector.
### Line 477

`display: flex;`

Sets one visual or layout property for the active selector.
### Line 478

`align-items: center;`

Sets one visual or layout property for the active selector.
### Line 479

`gap: 6px;`

Sets one visual or layout property for the active selector.
### Line 480

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 481

`.chain-toggle-icon {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 482

`font-size: 10px;`

Sets one visual or layout property for the active selector.
### Line 483

`color: var(--text-muted);`

Sets one visual or layout property for the active selector.
### Line 484

`transition: transform 0.2s ease;`

Sets one visual or layout property for the active selector.
### Line 485

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 486

`.chain-step.expanded .chain-toggle-icon {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 487

`transform: rotate(90deg);`

Sets one visual or layout property for the active selector.
### Line 488

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 489

`.chain-node-val {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 490

`font-family: var(--font-mono);`

Sets one visual or layout property for the active selector.
### Line 491

`font-size: 12px;`

Sets one visual or layout property for the active selector.
### Line 492

`color: var(--text);`

Sets one visual or layout property for the active selector.
### Line 493

`font-weight: 600;`

Sets one visual or layout property for the active selector.
### Line 494

`margin-top: 2px;`

Sets one visual or layout property for the active selector.
### Line 495

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 496

`.chain-node-val.highlight-yellow { color: var(--yellow); }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 497

`.chain-node-val.highlight-cyan { color: var(--cyan); }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 498

`.chain-node-desc {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 499

`font-size: 11px;`

Sets one visual or layout property for the active selector.
### Line 500

`line-height: 1.4;`

Sets one visual or layout property for the active selector.
### Line 501

`color: var(--text-muted);`

Sets one visual or layout property for the active selector.
### Line 502

`margin-top: 6px;`

Sets one visual or layout property for the active selector.
### Line 503

`padding-top: 6px;`

Sets one visual or layout property for the active selector.
### Line 504

`border-top: 1px dashed var(--panel-border);`

Sets one visual or layout property for the active selector.
### Line 505

`display: none;`

Sets one visual or layout property for the active selector.
### Line 506

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 507

`.chain-step.expanded .chain-node-desc {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 508

`display: block;`

Sets one visual or layout property for the active selector.
### Line 509

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 510

`.chain-arrow {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 511

`text-align: center;`

Sets one visual or layout property for the active selector.
### Line 512

`color: var(--text-muted);`

Sets one visual or layout property for the active selector.
### Line 513

`font-size: 12px;`

Sets one visual or layout property for the active selector.
### Line 514

`line-height: 1;`

Sets one visual or layout property for the active selector.
### Line 515

`font-weight: bold;`

Sets one visual or layout property for the active selector.
### Line 516

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 517

`.supporting-chips {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 518

`display: flex;`

Sets one visual or layout property for the active selector.
### Line 519

`flex-direction: column;`

Sets one visual or layout property for the active selector.
### Line 520

`gap: 4px;`

Sets one visual or layout property for the active selector.
### Line 521

`margin-top: 6px;`

Sets one visual or layout property for the active selector.
### Line 522

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 523

`.evidence-chip {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 524

`font-family: var(--font-mono);`

Sets one visual or layout property for the active selector.
### Line 525

`font-size: 11px;`

Sets one visual or layout property for the active selector.
### Line 526

`color: var(--yellow);`

Sets one visual or layout property for the active selector.
### Line 527

`background: rgba(245, 158, 11, 0.08);`

Sets one visual or layout property for the active selector.
### Line 528

`padding: 4px 8px;`

Sets one visual or layout property for the active selector.
### Line 529

`border-radius: 4px;`

Sets one visual or layout property for the active selector.
### Line 530

`border: 1px solid rgba(245, 158, 11, 0.2);`

Sets one visual or layout property for the active selector.
### Line 531

`display: flex;`

Sets one visual or layout property for the active selector.
### Line 532

`justify-content: space-between;`

Sets one visual or layout property for the active selector.
### Line 533

`align-items: center;`

Sets one visual or layout property for the active selector.
### Line 534

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 535

`.chain-reason {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 536

`font-size: 12px;`

Sets one visual or layout property for the active selector.
### Line 537

`line-height: 1.45;`

Sets one visual or layout property for the active selector.
### Line 538

`color: var(--text);`

Sets one visual or layout property for the active selector.
### Line 539

`margin-top: 4px;`

Sets one visual or layout property for the active selector.
### Line 540

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 541

`.next-step {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 542

`display: flex;`

Sets one visual or layout property for the active selector.
### Line 543

`justify-content: space-between;`

Sets one visual or layout property for the active selector.
### Line 544

`align-items: center;`

Sets one visual or layout property for the active selector.
### Line 545

`border-color: rgba(34, 211, 238, 0.3);`

Sets one visual or layout property for the active selector.
### Line 546

`background: rgba(34, 211, 238, 0.06);`

Sets one visual or layout property for the active selector.
### Line 547

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 548

`.next-activity-title {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 549

`font-family: var(--font-display);`

Sets one visual or layout property for the active selector.
### Line 550

`font-size: 13px;`

Sets one visual or layout property for the active selector.
### Line 551

`font-weight: 700;`

Sets one visual or layout property for the active selector.
### Line 552

`color: var(--cyan);`

Sets one visual or layout property for the active selector.
### Line 553

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 554

`(blank)`

Blank line used to separate nearby statements.
### Line 555

`/* BASIS PILLS */`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 556

`.basis-pill-grid {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 557

`display: flex;`

Sets one visual or layout property for the active selector.
### Line 558

`gap: 8px;`

Sets one visual or layout property for the active selector.
### Line 559

`flex-wrap: wrap;`

Sets one visual or layout property for the active selector.
### Line 560

`margin-bottom: 6px;`

Sets one visual or layout property for the active selector.
### Line 561

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 562

`.basis-pill {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 563

`padding: 6px 14px;`

Sets one visual or layout property for the active selector.
### Line 564

`border-radius: 8px;`

Sets one visual or layout property for the active selector.
### Line 565

`background: var(--panel);`

Sets one visual or layout property for the active selector.
### Line 566

`border: 1px solid var(--panel-border);`

Sets one visual or layout property for the active selector.
### Line 567

`color: var(--text);`

Sets one visual or layout property for the active selector.
### Line 568

`font-family: var(--font-mono);`

Sets one visual or layout property for the active selector.
### Line 569

`font-size: 13px;`

Sets one visual or layout property for the active selector.
### Line 570

`font-weight: 600;`

Sets one visual or layout property for the active selector.
### Line 571

`cursor: pointer;`

Sets one visual or layout property for the active selector.
### Line 572

`transition: all 0.2s ease;`

Sets one visual or layout property for the active selector.
### Line 573

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 574

`.basis-pill:hover {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 575

`border-color: var(--cyan);`

Sets one visual or layout property for the active selector.
### Line 576

`color: var(--cyan);`

Sets one visual or layout property for the active selector.
### Line 577

`transform: translateY(-1px);`

Sets one visual or layout property for the active selector.
### Line 578

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 579

`.basis-pill.selected {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 580

`background: rgba(34, 211, 238, 0.15);`

Sets one visual or layout property for the active selector.
### Line 581

`border-color: var(--cyan);`

Sets one visual or layout property for the active selector.
### Line 582

`color: var(--cyan);`

Sets one visual or layout property for the active selector.
### Line 583

`box-shadow: 0 0 10px var(--cyan-glow);`

Sets one visual or layout property for the active selector.
### Line 584

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 585

`(blank)`

Blank line used to separate nearby statements.
### Line 586

`/* PROGRESS BAR */`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 587

`.execution-progress-bar {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 588

`background: rgba(59, 130, 246, 0.12);`

Sets one visual or layout property for the active selector.
### Line 589

`border: 1px solid var(--accent);`

Sets one visual or layout property for the active selector.
### Line 590

`border-radius: 8px;`

Sets one visual or layout property for the active selector.
### Line 591

`padding: 8px 12px;`

Sets one visual or layout property for the active selector.
### Line 592

`font-family: var(--font-mono);`

Sets one visual or layout property for the active selector.
### Line 593

`font-size: 12px;`

Sets one visual or layout property for the active selector.
### Line 594

`color: var(--cyan);`

Sets one visual or layout property for the active selector.
### Line 595

`display: flex;`

Sets one visual or layout property for the active selector.
### Line 596

`align-items: center;`

Sets one visual or layout property for the active selector.
### Line 597

`gap: 8px;`

Sets one visual or layout property for the active selector.
### Line 598

`animation: pulse 1.5s infinite;`

Sets one visual or layout property for the active selector.
### Line 599

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 600

`(blank)`

Blank line used to separate nearby statements.
### Line 601

`/* CIRCUIT STUDIO */`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 602

`.circuit-studio {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 603

`background: var(--glass);`

Sets one visual or layout property for the active selector.
### Line 604

`backdrop-filter: blur(12px);`

Sets one visual or layout property for the active selector.
### Line 605

`-webkit-backdrop-filter: blur(12px);`

Sets one visual or layout property for the active selector.
### Line 606

`border: 1px solid var(--panel-border);`

Sets one visual or layout property for the active selector.
### Line 607

`border-radius: var(--radius);`

Sets one visual or layout property for the active selector.
### Line 608

`padding: 16px;`

Sets one visual or layout property for the active selector.
### Line 609

`display: flex;`

Sets one visual or layout property for the active selector.
### Line 610

`flex-direction: column;`

Sets one visual or layout property for the active selector.
### Line 611

`gap: 12px;`

Sets one visual or layout property for the active selector.
### Line 612

`box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);`

Sets one visual or layout property for the active selector.
### Line 613

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 614

`.gate-toolbar {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 615

`display: flex;`

Sets one visual or layout property for the active selector.
### Line 616

`gap: 6px;`

Sets one visual or layout property for the active selector.
### Line 617

`flex-wrap: wrap;`

Sets one visual or layout property for the active selector.
### Line 618

`align-items: center;`

Sets one visual or layout property for the active selector.
### Line 619

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 620

`.gate-btn {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 621

`background: var(--gate-bg);`

Sets one visual or layout property for the active selector.
### Line 622

`color: var(--gate-text);`

Sets one visual or layout property for the active selector.
### Line 623

`border: 1px solid var(--panel-border);`

Sets one visual or layout property for the active selector.
### Line 624

`padding: 6px 12px;`

Sets one visual or layout property for the active selector.
### Line 625

`border-radius: 6px;`

Sets one visual or layout property for the active selector.
### Line 626

`font-family: var(--font-mono);`

Sets one visual or layout property for the active selector.
### Line 627

`font-weight: 700;`

Sets one visual or layout property for the active selector.
### Line 628

`font-size: 12px;`

Sets one visual or layout property for the active selector.
### Line 629

`cursor: pointer;`

Sets one visual or layout property for the active selector.
### Line 630

`user-select: none;`

Sets one visual or layout property for the active selector.
### Line 631

`transition: 0.15s;`

Sets one visual or layout property for the active selector.
### Line 632

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 633

`.gate-btn:hover { transform: translateY(-2px); box-shadow: 0 2px 8px var(--accent-glow); }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 634

`.gate-btn.active-tool { border-color: var(--cyan); box-shadow: 0 0 8px var(--cyan); }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 635

`(blank)`

Blank line used to separate nearby statements.
### Line 636

`.wire-grid {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 637

`background: var(--bg-secondary);`

Sets one visual or layout property for the active selector.
### Line 638

`border: 1px solid var(--panel-border);`

Sets one visual or layout property for the active selector.
### Line 639

`border-radius: 10px;`

Sets one visual or layout property for the active selector.
### Line 640

`padding: 16px;`

Sets one visual or layout property for the active selector.
### Line 641

`overflow-x: auto;`

Sets one visual or layout property for the active selector.
### Line 642

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 643

`.wire-row {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 644

`display: flex;`

Sets one visual or layout property for the active selector.
### Line 645

`align-items: center;`

Sets one visual or layout property for the active selector.
### Line 646

`height: 48px;`

Sets one visual or layout property for the active selector.
### Line 647

`position: relative;`

Sets one visual or layout property for the active selector.
### Line 648

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 649

`.wire-label {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 650

`width: 44px;`

Sets one visual or layout property for the active selector.
### Line 651

`font-family: var(--font-mono);`

Sets one visual or layout property for the active selector.
### Line 652

`font-size: 13px;`

Sets one visual or layout property for the active selector.
### Line 653

`color: var(--cyan);`

Sets one visual or layout property for the active selector.
### Line 654

`font-weight: 600;`

Sets one visual or layout property for the active selector.
### Line 655

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 656

`.wire-line {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 657

`flex: 1;`

Sets one visual or layout property for the active selector.
### Line 658

`height: 2px;`

Sets one visual or layout property for the active selector.
### Line 659

`background: var(--wire);`

Sets one visual or layout property for the active selector.
### Line 660

`position: relative;`

Sets one visual or layout property for the active selector.
### Line 661

`display: flex;`

Sets one visual or layout property for the active selector.
### Line 662

`align-items: center;`

Sets one visual or layout property for the active selector.
### Line 663

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 664

`.grid-slot {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 665

`width: 40px;`

Sets one visual or layout property for the active selector.
### Line 666

`height: 40px;`

Sets one visual or layout property for the active selector.
### Line 667

`margin-right: 10px;`

Sets one visual or layout property for the active selector.
### Line 668

`border: 1px dashed var(--grid-line);`

Sets one visual or layout property for the active selector.
### Line 669

`border-radius: 6px;`

Sets one visual or layout property for the active selector.
### Line 670

`display: flex;`

Sets one visual or layout property for the active selector.
### Line 671

`align-items: center;`

Sets one visual or layout property for the active selector.
### Line 672

`justify-content: center;`

Sets one visual or layout property for the active selector.
### Line 673

`cursor: pointer;`

Sets one visual or layout property for the active selector.
### Line 674

`position: relative;`

Sets one visual or layout property for the active selector.
### Line 675

`z-index: 2;`

Sets one visual or layout property for the active selector.
### Line 676

`background: var(--bg);`

Sets one visual or layout property for the active selector.
### Line 677

`transition: all 0.15s ease;`

Sets one visual or layout property for the active selector.
### Line 678

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 679

`.grid-slot:hover { border-color: var(--accent); background: var(--panel); }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 680

`.placed-gate {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 681

`background: var(--gate-bg);`

Sets one visual or layout property for the active selector.
### Line 682

`color: var(--gate-text);`

Sets one visual or layout property for the active selector.
### Line 683

`width: 34px;`

Sets one visual or layout property for the active selector.
### Line 684

`height: 34px;`

Sets one visual or layout property for the active selector.
### Line 685

`border-radius: 5px;`

Sets one visual or layout property for the active selector.
### Line 686

`display: flex;`

Sets one visual or layout property for the active selector.
### Line 687

`align-items: center;`

Sets one visual or layout property for the active selector.
### Line 688

`justify-content: center;`

Sets one visual or layout property for the active selector.
### Line 689

`font-family: var(--font-mono);`

Sets one visual or layout property for the active selector.
### Line 690

`font-weight: 700;`

Sets one visual or layout property for the active selector.
### Line 691

`font-size: 12px;`

Sets one visual or layout property for the active selector.
### Line 692

`box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);`

Sets one visual or layout property for the active selector.
### Line 693

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 694

`.placed-gate.cz-gate { background: #4C1D95; }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 695

`.placed-gate.m-gate { background: #065F46; }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 696

`(blank)`

Blank line used to separate nearby statements.
### Line 697

`.gate-info-callout {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 698

`font-size: 11px;`

Sets one visual or layout property for the active selector.
### Line 699

`font-family: var(--font-mono);`

Sets one visual or layout property for the active selector.
### Line 700

`color: var(--text-muted);`

Sets one visual or layout property for the active selector.
### Line 701

`background: var(--bg);`

Sets one visual or layout property for the active selector.
### Line 702

`padding: 8px 12px;`

Sets one visual or layout property for the active selector.
### Line 703

`border-radius: 6px;`

Sets one visual or layout property for the active selector.
### Line 704

`border: 1px solid var(--panel-border);`

Sets one visual or layout property for the active selector.
### Line 705

`display: flex;`

Sets one visual or layout property for the active selector.
### Line 706

`justify-content: space-between;`

Sets one visual or layout property for the active selector.
### Line 707

`align-items: center;`

Sets one visual or layout property for the active selector.
### Line 708

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 709

`(blank)`

Blank line used to separate nearby statements.
### Line 710

`/* HISTOGRAM */`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 711

`.hist-container { display: flex; flex-direction: column; gap: 6px; }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 712

`.hist-row {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 713

`display: flex;`

Sets one visual or layout property for the active selector.
### Line 714

`align-items: center;`

Sets one visual or layout property for the active selector.
### Line 715

`gap: 8px;`

Sets one visual or layout property for the active selector.
### Line 716

`font-family: var(--font-mono);`

Sets one visual or layout property for the active selector.
### Line 717

`font-size: 12px;`

Sets one visual or layout property for the active selector.
### Line 718

`padding: 4px 6px;`

Sets one visual or layout property for the active selector.
### Line 719

`border-radius: 6px;`

Sets one visual or layout property for the active selector.
### Line 720

`cursor: pointer;`

Sets one visual or layout property for the active selector.
### Line 721

`transition: background 0.15s ease;`

Sets one visual or layout property for the active selector.
### Line 722

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 723

`.hist-row:hover {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 724

`background: rgba(255, 255, 255, 0.04);`

Sets one visual or layout property for the active selector.
### Line 725

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 726

`.hist-row.selected {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 727

`background: rgba(34, 211, 238, 0.08);`

Sets one visual or layout property for the active selector.
### Line 728

`border: 1px solid rgba(34, 211, 238, 0.3);`

Sets one visual or layout property for the active selector.
### Line 729

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 730

`.hist-state { width: 38px; color: var(--cyan); font-weight: 600; }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 731

`.hist-bar-bg {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 732

`flex: 1;`

Sets one visual or layout property for the active selector.
### Line 733

`height: 18px;`

Sets one visual or layout property for the active selector.
### Line 734

`background: var(--bg);`

Sets one visual or layout property for the active selector.
### Line 735

`border-radius: 4px;`

Sets one visual or layout property for the active selector.
### Line 736

`overflow: hidden;`

Sets one visual or layout property for the active selector.
### Line 737

`position: relative;`

Sets one visual or layout property for the active selector.
### Line 738

`border: 1px solid var(--panel-border);`

Sets one visual or layout property for the active selector.
### Line 739

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 740

`.hist-bar-fill {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 741

`height: 100%;`

Sets one visual or layout property for the active selector.
### Line 742

`background: linear-gradient(90deg, var(--accent), var(--cyan));`

Sets one visual or layout property for the active selector.
### Line 743

`border-radius: 3px;`

Sets one visual or layout property for the active selector.
### Line 744

`transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);`

Sets one visual or layout property for the active selector.
### Line 745

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 746

`.hist-bar-fill.target { background: linear-gradient(90deg, #10b981, #34d399); }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 747

`.hist-bar-fill.predicted { border-right: 2px solid var(--yellow); }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 748

`.hist-pct { width: 60px; text-align: right; color: var(--text-muted); font-size: 11px; }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 749

`(blank)`

Blank line used to separate nearby statements.
### Line 750

`/* QUESTION OPTIONS */`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 751

`.options-grid { display: flex; flex-direction: column; gap: 8px; }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 752

`.option-btn {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 753

`background: var(--panel);`

Sets one visual or layout property for the active selector.
### Line 754

`border: 1px solid var(--panel-border);`

Sets one visual or layout property for the active selector.
### Line 755

`border-radius: 10px;`

Sets one visual or layout property for the active selector.
### Line 756

`padding: 10px 14px;`

Sets one visual or layout property for the active selector.
### Line 757

`display: flex;`

Sets one visual or layout property for the active selector.
### Line 758

`align-items: center;`

Sets one visual or layout property for the active selector.
### Line 759

`gap: 12px;`

Sets one visual or layout property for the active selector.
### Line 760

`color: var(--text);`

Sets one visual or layout property for the active selector.
### Line 761

`cursor: pointer;`

Sets one visual or layout property for the active selector.
### Line 762

`text-align: left;`

Sets one visual or layout property for the active selector.
### Line 763

`font-size: 13px;`

Sets one visual or layout property for the active selector.
### Line 764

`line-height: 1.4;`

Sets one visual or layout property for the active selector.
### Line 765

`transition: 0.15s;`

Sets one visual or layout property for the active selector.
### Line 766

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 767

`.option-btn:hover { border-color: var(--accent); background: var(--panel); }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 768

`.option-btn.selected { border-color: var(--cyan); background: rgba(34, 211, 238, 0.1); }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 769

`.option-key {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 770

`font-family: var(--font-mono);`

Sets one visual or layout property for the active selector.
### Line 771

`font-weight: 700;`

Sets one visual or layout property for the active selector.
### Line 772

`color: var(--cyan);`

Sets one visual or layout property for the active selector.
### Line 773

`width: 20px;`

Sets one visual or layout property for the active selector.
### Line 774

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 775

`(blank)`

Blank line used to separate nearby statements.
### Line 776

`/* BUTTONS & CONTROLS */`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 777

`.btn {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 778

`background: var(--accent);`

Sets one visual or layout property for the active selector.
### Line 779

`color: white;`

Sets one visual or layout property for the active selector.
### Line 780

`border: none;`

Sets one visual or layout property for the active selector.
### Line 781

`padding: 8px 16px;`

Sets one visual or layout property for the active selector.
### Line 782

`border-radius: 8px;`

Sets one visual or layout property for the active selector.
### Line 783

`font-family: var(--font-display);`

Sets one visual or layout property for the active selector.
### Line 784

`font-weight: 600;`

Sets one visual or layout property for the active selector.
### Line 785

`font-size: 13px;`

Sets one visual or layout property for the active selector.
### Line 786

`cursor: pointer;`

Sets one visual or layout property for the active selector.
### Line 787

`transition: all 0.2s ease;`

Sets one visual or layout property for the active selector.
### Line 788

`display: inline-flex;`

Sets one visual or layout property for the active selector.
### Line 789

`align-items: center;`

Sets one visual or layout property for the active selector.
### Line 790

`gap: 6px;`

Sets one visual or layout property for the active selector.
### Line 791

`box-shadow: 0 2px 8px rgba(0, 0, 0, 0.20);`

Sets one visual or layout property for the active selector.
### Line 792

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 793

`.btn:hover { background: var(--accent-hover); transform: translateY(-1px); box-shadow: 0 4px 12px var(--blue-glow); }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 794

`.btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; box-shadow: none; }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 795

`.btn.secondary { background: var(--panel); border: 1px solid var(--panel-border); color: var(--text); }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 796

`.btn.secondary:hover { border-color: var(--panel-border-hi); }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 797

`.btn.success { background: var(--green); color: #042f2e; }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 798

`.btn.success:hover { background: #059669; }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 799

`(blank)`

Blank line used to separate nearby statements.
### Line 800

`.explanation-box {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 801

`background: var(--panel);`

Sets one visual or layout property for the active selector.
### Line 802

`border-left: 3px solid var(--cyan);`

Sets one visual or layout property for the active selector.
### Line 803

`border-radius: 8px;`

Sets one visual or layout property for the active selector.
### Line 804

`padding: 14px;`

Sets one visual or layout property for the active selector.
### Line 805

`font-size: 13px;`

Sets one visual or layout property for the active selector.
### Line 806

`line-height: 1.6;`

Sets one visual or layout property for the active selector.
### Line 807

`max-height: 280px;`

Sets one visual or layout property for the active selector.
### Line 808

`overflow-y: auto;`

Sets one visual or layout property for the active selector.
### Line 809

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 810

`(blank)`

Blank line used to separate nearby statements.
### Line 811

`/* CUSTOM SLEEK SCROLLBARS */`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 812

`::-webkit-scrollbar {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 813

`width: 6px;`

Sets one visual or layout property for the active selector.
### Line 814

`height: 6px;`

Sets one visual or layout property for the active selector.
### Line 815

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 816

`::-webkit-scrollbar-track {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 817

`background: transparent;`

Sets one visual or layout property for the active selector.
### Line 818

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 819

`::-webkit-scrollbar-thumb {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 820

`background: rgba(91, 140, 255, 0.25);`

Sets one visual or layout property for the active selector.
### Line 821

`border-radius: 999px;`

Sets one visual or layout property for the active selector.
### Line 822

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 823

`::-webkit-scrollbar-thumb:hover {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 824

`background: var(--cyan);`

Sets one visual or layout property for the active selector.
### Line 825

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 826

`(blank)`

Blank line used to separate nearby statements.
### Line 827

`/* TACTILE PRESS FEEDBACK */`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 828

`.btn:active, .profile-btn:active, .chip:active, .basis-pill:active, .option-btn:active, .journey-node:active, .gate-btn:active {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 829

`transform: scale(0.98);`

Sets one visual or layout property for the active selector.
### Line 830

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 831

`(blank)`

Blank line used to separate nearby statements.
### Line 832

`/* MODALS */`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 833

`.modal-overlay, .overlay {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 834

`position: fixed;`

Sets one visual or layout property for the active selector.
### Line 835

`top: 0; left: 0; right: 0; bottom: 0;`

Sets one visual or layout property for the active selector.
### Line 836

`background: rgba(3, 5, 15, 0.75);`

Sets one visual or layout property for the active selector.
### Line 837

`backdrop-filter: blur(8px);`

Sets one visual or layout property for the active selector.
### Line 838

`-webkit-backdrop-filter: blur(8px);`

Sets one visual or layout property for the active selector.
### Line 839

`display: none;`

Sets one visual or layout property for the active selector.
### Line 840

`align-items: center;`

Sets one visual or layout property for the active selector.
### Line 841

`justify-content: center;`

Sets one visual or layout property for the active selector.
### Line 842

`z-index: 100;`

Sets one visual or layout property for the active selector.
### Line 843

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 844

`.modal-overlay.open, .overlay.open { display: flex; }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 845

`.modal-card {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 846

`background: var(--glass-2);`

Sets one visual or layout property for the active selector.
### Line 847

`backdrop-filter: blur(16px);`

Sets one visual or layout property for the active selector.
### Line 848

`-webkit-backdrop-filter: blur(16px);`

Sets one visual or layout property for the active selector.
### Line 849

`border: 1px solid var(--panel-border-hi);`

Sets one visual or layout property for the active selector.
### Line 850

`border-radius: 16px;`

Sets one visual or layout property for the active selector.
### Line 851

`padding: 24px;`

Sets one visual or layout property for the active selector.
### Line 852

`width: 520px;`

Sets one visual or layout property for the active selector.
### Line 853

`max-width: 90vw;`

Sets one visual or layout property for the active selector.
### Line 854

`display: flex;`

Sets one visual or layout property for the active selector.
### Line 855

`flex-direction: column;`

Sets one visual or layout property for the active selector.
### Line 856

`gap: 14px;`

Sets one visual or layout property for the active selector.
### Line 857

`box-shadow: 0 16px 48px rgba(0, 0, 0, 0.6);`

Sets one visual or layout property for the active selector.
### Line 858

`animation: modalScaleIn 0.22s cubic-bezier(0.16, 1, 0.3, 1);`

Sets one visual or layout property for the active selector.
### Line 859

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 860

`(blank)`

Blank line used to separate nearby statements.
### Line 861

`@keyframes modalScaleIn {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 862

`from { opacity: 0; transform: scale(0.96) translateY(6px); }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 863

`to { opacity: 1; transform: scale(1) translateY(0); }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 864

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 865

`(blank)`

Blank line used to separate nearby statements.
### Line 866

`/* PROFILE MODAL SPECIFICS */`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 867

`.profile-modal-card {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 868

`width: 440px;`

Sets one visual or layout property for the active selector.
### Line 869

`max-width: 90vw;`

Sets one visual or layout property for the active selector.
### Line 870

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 871

`.profile-view { display: none; }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 872

`.profile-view.active { display: block; }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 873

`.profile-header-preview {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 874

`display: flex;`

Sets one visual or layout property for the active selector.
### Line 875

`align-items: center;`

Sets one visual or layout property for the active selector.
### Line 876

`gap: 14px;`

Sets one visual or layout property for the active selector.
### Line 877

`padding-bottom: 14px;`

Sets one visual or layout property for the active selector.
### Line 878

`border-bottom: 1px solid var(--panel-border);`

Sets one visual or layout property for the active selector.
### Line 879

`margin-bottom: 14px;`

Sets one visual or layout property for the active selector.
### Line 880

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 881

`.profile-avatar-large {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 882

`width: 60px;`

Sets one visual or layout property for the active selector.
### Line 883

`height: 60px;`

Sets one visual or layout property for the active selector.
### Line 884

`border-radius: 50%;`

Sets one visual or layout property for the active selector.
### Line 885

`background: linear-gradient(135deg, var(--accent), var(--cyan));`

Sets one visual or layout property for the active selector.
### Line 886

`background-size: cover;`

Sets one visual or layout property for the active selector.
### Line 887

`background-position: center;`

Sets one visual or layout property for the active selector.
### Line 888

`color: #03050F;`

Sets one visual or layout property for the active selector.
### Line 889

`font-family: var(--font-display);`

Sets one visual or layout property for the active selector.
### Line 890

`font-weight: 700;`

Sets one visual or layout property for the active selector.
### Line 891

`font-size: 22px;`

Sets one visual or layout property for the active selector.
### Line 892

`display: flex;`

Sets one visual or layout property for the active selector.
### Line 893

`align-items: center;`

Sets one visual or layout property for the active selector.
### Line 894

`justify-content: center;`

Sets one visual or layout property for the active selector.
### Line 895

`box-shadow: 0 0 16px var(--blue-glow);`

Sets one visual or layout property for the active selector.
### Line 896

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 897

`.menu-item {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 898

`display: flex;`

Sets one visual or layout property for the active selector.
### Line 899

`align-items: center;`

Sets one visual or layout property for the active selector.
### Line 900

`justify-content: space-between;`

Sets one visual or layout property for the active selector.
### Line 901

`padding: 12px 14px;`

Sets one visual or layout property for the active selector.
### Line 902

`border-radius: 10px;`

Sets one visual or layout property for the active selector.
### Line 903

`background: var(--panel);`

Sets one visual or layout property for the active selector.
### Line 904

`border: 1px solid var(--panel-border);`

Sets one visual or layout property for the active selector.
### Line 905

`color: var(--text);`

Sets one visual or layout property for the active selector.
### Line 906

`font-size: 13px;`

Sets one visual or layout property for the active selector.
### Line 907

`font-weight: 500;`

Sets one visual or layout property for the active selector.
### Line 908

`margin-bottom: 8px;`

Sets one visual or layout property for the active selector.
### Line 909

`cursor: pointer;`

Sets one visual or layout property for the active selector.
### Line 910

`transition: all 0.2s ease;`

Sets one visual or layout property for the active selector.
### Line 911

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 912

`.menu-item:hover {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 913

`border-color: var(--panel-border-hi);`

Sets one visual or layout property for the active selector.
### Line 914

`background: rgba(59, 130, 246, 0.10);`

Sets one visual or layout property for the active selector.
### Line 915

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 916

`.toggle-row {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 917

`display: flex;`

Sets one visual or layout property for the active selector.
### Line 918

`align-items: center;`

Sets one visual or layout property for the active selector.
### Line 919

`justify-content: space-between;`

Sets one visual or layout property for the active selector.
### Line 920

`padding: 12px 14px;`

Sets one visual or layout property for the active selector.
### Line 921

`border-radius: 10px;`

Sets one visual or layout property for the active selector.
### Line 922

`background: var(--panel);`

Sets one visual or layout property for the active selector.
### Line 923

`border: 1px solid var(--panel-border);`

Sets one visual or layout property for the active selector.
### Line 924

`margin-bottom: 8px;`

Sets one visual or layout property for the active selector.
### Line 925

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 926

`.toggle {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 927

`width: 44px;`

Sets one visual or layout property for the active selector.
### Line 928

`height: 24px;`

Sets one visual or layout property for the active selector.
### Line 929

`background: var(--bg-secondary);`

Sets one visual or layout property for the active selector.
### Line 930

`border: 1px solid var(--panel-border);`

Sets one visual or layout property for the active selector.
### Line 931

`border-radius: 999px;`

Sets one visual or layout property for the active selector.
### Line 932

`position: relative;`

Sets one visual or layout property for the active selector.
### Line 933

`cursor: pointer;`

Sets one visual or layout property for the active selector.
### Line 934

`transition: background 0.2s;`

Sets one visual or layout property for the active selector.
### Line 935

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 936

`.toggle::after {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 937

`content: '';`

Sets one visual or layout property for the active selector.
### Line 938

`position: absolute;`

Sets one visual or layout property for the active selector.
### Line 939

`width: 18px;`

Sets one visual or layout property for the active selector.
### Line 940

`height: 18px;`

Sets one visual or layout property for the active selector.
### Line 941

`border-radius: 50%;`

Sets one visual or layout property for the active selector.
### Line 942

`background: var(--text-muted);`

Sets one visual or layout property for the active selector.
### Line 943

`top: 2px;`

Sets one visual or layout property for the active selector.
### Line 944

`left: 2px;`

Sets one visual or layout property for the active selector.
### Line 945

`transition: transform 0.2s, background 0.2s;`

Sets one visual or layout property for the active selector.
### Line 946

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 947

`.toggle.on {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 948

`background: var(--cyan);`

Sets one visual or layout property for the active selector.
### Line 949

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 950

`.toggle.on::after {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 951

`transform: translateX(20px);`

Sets one visual or layout property for the active selector.
### Line 952

`background: #03050F;`

Sets one visual or layout property for the active selector.
### Line 953

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 954

`.profile-input {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 955

`width: 100%;`

Sets one visual or layout property for the active selector.
### Line 956

`background: var(--bg);`

Sets one visual or layout property for the active selector.
### Line 957

`border: 1px solid var(--panel-border);`

Sets one visual or layout property for the active selector.
### Line 958

`color: var(--text);`

Sets one visual or layout property for the active selector.
### Line 959

`padding: 8px 12px;`

Sets one visual or layout property for the active selector.
### Line 960

`border-radius: 8px;`

Sets one visual or layout property for the active selector.
### Line 961

`font-family: var(--font-body);`

Sets one visual or layout property for the active selector.
### Line 962

`font-size: 13px;`

Sets one visual or layout property for the active selector.
### Line 963

`margin-bottom: 12px;`

Sets one visual or layout property for the active selector.
### Line 964

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 965

`.profile-input:focus {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 966

`outline: none;`

Sets one visual or layout property for the active selector.
### Line 967

`border-color: var(--cyan);`

Sets one visual or layout property for the active selector.
### Line 968

`box-shadow: 0 0 8px var(--cyan-glow);`

Sets one visual or layout property for the active selector.
### Line 969

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 970

`(blank)`

Blank line used to separate nearby statements.
### Line 971

`/* ANIMATIONS */`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 972

`@keyframes fadeIn {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 973

`from { opacity: 0; transform: translateY(4px); }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 974

`to { opacity: 1; transform: translateY(0); }`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 975

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 976

`/* AI GUIDANCE MARKDOWN FORMATTING */`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 977

`.ai-heading {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 978

`font-family: var(--font-display);`

Sets one visual or layout property for the active selector.
### Line 979

`font-size: 13px;`

Sets one visual or layout property for the active selector.
### Line 980

`font-weight: 700;`

Sets one visual or layout property for the active selector.
### Line 981

`color: var(--cyan);`

Sets one visual or layout property for the active selector.
### Line 982

`margin: 10px 0 4px 0;`

Sets one visual or layout property for the active selector.
### Line 983

`text-transform: uppercase;`

Sets one visual or layout property for the active selector.
### Line 984

`letter-spacing: 0.02em;`

Sets one visual or layout property for the active selector.
### Line 985

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 986

`.ai-heading:first-child {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 987

`margin-top: 0;`

Sets one visual or layout property for the active selector.
### Line 988

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 989

`.ai-heading-large {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 990

`font-family: var(--font-display);`

Sets one visual or layout property for the active selector.
### Line 991

`font-size: 14px;`

Sets one visual or layout property for the active selector.
### Line 992

`font-weight: 700;`

Sets one visual or layout property for the active selector.
### Line 993

`color: var(--text);`

Sets one visual or layout property for the active selector.
### Line 994

`margin: 12px 0 6px 0;`

Sets one visual or layout property for the active selector.
### Line 995

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 996

`.ai-list {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 997

`margin: 4px 0 8px 18px;`

Sets one visual or layout property for the active selector.
### Line 998

`padding: 0;`

Sets one visual or layout property for the active selector.
### Line 999

`list-style-type: disc;`

Sets one visual or layout property for the active selector.
### Line 1000

`font-size: 13px;`

Sets one visual or layout property for the active selector.
### Line 1001

`line-height: 1.5;`

Sets one visual or layout property for the active selector.
### Line 1002

`color: var(--text);`

Sets one visual or layout property for the active selector.
### Line 1003

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 1004

`.ai-list li {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 1005

`margin-bottom: 4px;`

Sets one visual or layout property for the active selector.
### Line 1006

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 1007

`.ai-para {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 1008

`font-size: 13px;`

Sets one visual or layout property for the active selector.
### Line 1009

`line-height: 1.55;`

Sets one visual or layout property for the active selector.
### Line 1010

`margin-bottom: 8px;`

Sets one visual or layout property for the active selector.
### Line 1011

`color: var(--text);`

Sets one visual or layout property for the active selector.
### Line 1012

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 1013

`.ai-inline-code {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 1014

`font-family: var(--font-mono);`

Sets one visual or layout property for the active selector.
### Line 1015

`font-size: 11px;`

Sets one visual or layout property for the active selector.
### Line 1016

`background: rgba(34, 211, 238, 0.12);`

Sets one visual or layout property for the active selector.
### Line 1017

`color: var(--cyan);`

Sets one visual or layout property for the active selector.
### Line 1018

`padding: 2px 6px;`

Sets one visual or layout property for the active selector.
### Line 1019

`border-radius: 4px;`

Sets one visual or layout property for the active selector.
### Line 1020

`border: 1px solid rgba(34, 211, 238, 0.25);`

Sets one visual or layout property for the active selector.
### Line 1021

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 1022

`.ai-ordered-item {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 1023

`font-size: 13px;`

Sets one visual or layout property for the active selector.
### Line 1024

`line-height: 1.5;`

Sets one visual or layout property for the active selector.
### Line 1025

`margin-bottom: 6px;`

Sets one visual or layout property for the active selector.
### Line 1026

`padding-left: 8px;`

Sets one visual or layout property for the active selector.
### Line 1027

`border-left: 2px solid var(--accent);`

Sets one visual or layout property for the active selector.
### Line 1028

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 1029

`(blank)`

Blank line used to separate nearby statements.
### Line 1030

`@media (prefers-reduced-motion: reduce) {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 1031

`* {`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 1032

`animation-duration: 0.01ms !important;`

Sets one visual or layout property for the active selector.
### Line 1033

`transition-duration: 0.01ms !important;`

Sets one visual or layout property for the active selector.
### Line 1034

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 1035

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 1036

`(blank)`

Blank line used to separate nearby statements.
### Line 1037

`/* RESPONSIVENESS */`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 1038

`@media (max-width: 1024px) {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 1039

`.workspace-layout {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 1040

`grid-template-columns: 1fr;`

Sets one visual or layout property for the active selector.
### Line 1041

`height: auto;`

Sets one visual or layout property for the active selector.
### Line 1042

`overflow-y: auto;`

Sets one visual or layout property for the active selector.
### Line 1043

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 1044

`.state-triad-grid {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 1045

`grid-template-columns: 1fr;`

Sets one visual or layout property for the active selector.
### Line 1046

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 1047

`header {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 1048

`flex-wrap: wrap;`

Sets one visual or layout property for the active selector.
### Line 1049

`gap: 10px;`

Sets one visual or layout property for the active selector.
### Line 1050

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 1051

`.header-left {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 1052

`flex-wrap: wrap;`

Sets one visual or layout property for the active selector.
### Line 1053

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 1054

`#topbarBadges {`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 1055

`order: 3;`

Sets one visual or layout property for the active selector.
### Line 1056

`width: 100%;`

Sets one visual or layout property for the active selector.
### Line 1057

`justify-content: flex-start;`

Sets one visual or layout property for the active selector.
### Line 1058

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 1059

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 1060

`(blank)`

Blank line used to separate nearby statements.
### Line 1061

`@media (max-width: 640px) {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 1062

`header {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 1063

`padding: 10px 14px;`

Sets one visual or layout property for the active selector.
### Line 1064

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 1065

`.journey-bar {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 1066

`padding: 6px 14px;`

Sets one visual or layout property for the active selector.
### Line 1067

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 1068

`.pane {`

Starts a CSS rule or at-rule; the following declarations apply to the selected UI elements or media context.
### Line 1069

`padding: 12px 14px;`

Sets one visual or layout property for the active selector.
### Line 1070

`}`

Part of the stylesheet structure or a value used by the surrounding rule.
### Line 1071

`}`

Part of the stylesheet structure or a value used by the surrounding rule.

## Nearby Files

No same-folder source files.
