/**
 * Q-BIT.140 — M6 Interactive Circuit Canvas Studio
 * Handles interactive wire grid rendering, gate placement, presets, and tooltips.
 * Does NOT execute quantum simulation (M3 on backend is authoritative).
 */

export const GATE_DEFINITIONS = {
    "H": { name: "Hadamard", matrix: "1/√2 [[1, 1], [1, -1]]", desc: "Creates equal superposition: H|0⟩ = (|0⟩+|1⟩)/√2" },
    "X": { name: "Pauli-X (NOT)", matrix: "[[0, 1], [1, 0]]", desc: "Bit-flip gate: X|0⟩ = |1⟩, X|1⟩ = |0⟩" },
    "Y": { name: "Pauli-Y", matrix: "[[0, -i], [i, 0]]", desc: "Bit and phase flip gate" },
    "Z": { name: "Pauli-Z (Phase)", matrix: "[[1, 0], [0, -1]]", desc: "Phase-flip gate: Z|1⟩ = -|1⟩" },
    "S": { name: "S (Phase √Z)", matrix: "[[1, 0], [0, i]]", desc: "π/2 phase gate: S|1⟩ = i|1⟩" },
    "T": { name: "T (π/4 Phase)", matrix: "[[1, 0], [0, e^(iπ/4)]]", desc: "π/4 phase gate: T = √S" },
    "CZ": { name: "Controlled-Z", matrix: "diag(1, 1, 1, -1)", desc: "Flips phase of |11⟩ target: CZ|11⟩ = -|11⟩" },
    "M": { name: "Measurement", matrix: "Projective", desc: "Collapses qubit state to computational basis |0⟩ or |1⟩" },
};

export class CircuitStudio {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.numQubits = options.numQubits || 2;
        this.numColumns = options.numColumns || 6;
        this.gates = options.gates || [];
        this.selectedTool = null;
        this.isDragging = false;
        this.justDropped = false;
        this.onCircuitChange = options.onCircuitChange || null;
        this.onGateSelect = options.onGateSelect || null;
        this.initPaletteDrag();
    }

    initPaletteDrag() {
        if (typeof document === "undefined") return;
        document.querySelectorAll(".gate-btn").forEach(btn => {
            btn.setAttribute("draggable", "true");
            btn.ondragstart = (e) => {
                const gateType = btn.textContent.trim();
                const payload = JSON.stringify({ source: "palette", type: gateType });
                e.dataTransfer.setData("application/json", payload);
                e.dataTransfer.setData("text/plain", payload);
                e.dataTransfer.effectAllowed = "all";
                btn.classList.add("gate-dragging");
            };
            btn.ondragend = () => {
                btn.classList.remove("gate-dragging");
                this.isDragging = false;
            };
        });
    }



    setTool(tool) {
        this.selectedTool = tool;
    }

    loadPreset(presetName) {
        if (presetName === "grover_2q") {
            this.numQubits = 2;
            this.numColumns = 6;
            this.gates = [
                { id: 1, type: "H", qubit: 0, column: 0 },
                { id: 2, type: "H", qubit: 1, column: 0 },
                { id: 3, type: "X", qubit: 0, column: 1 },
                { id: 4, type: "CZ", qubit: 1, column: 2 },
                { id: 5, type: "X", qubit: 0, column: 3 },
                { id: 6, type: "H", qubit: 0, column: 4 },
                { id: 7, type: "H", qubit: 1, column: 4 },
                { id: 8, type: "M", qubit: 0, column: 5 },
                { id: 9, type: "M", qubit: 1, column: 5 },
            ];
        } else if (presetName === "superposition") {
            this.numQubits = 2;
            this.numColumns = 4;
            this.gates = [
                { id: 1, type: "H", qubit: 0, column: 0 },
                { id: 2, type: "H", qubit: 1, column: 0 },
                { id: 3, type: "M", qubit: 0, column: 3 },
                { id: 4, type: "M", qubit: 1, column: 3 },
            ];
        } else if (presetName === "bell_state") {
            this.numQubits = 2;
            this.numColumns = 4;
            this.gates = [
                { id: 1, type: "H", qubit: 0, column: 0 },
                { id: 2, type: "CZ", qubit: 1, column: 1 },
                { id: 3, type: "M", qubit: 0, column: 3 },
                { id: 4, type: "M", qubit: 1, column: 3 },
            ];
        }
        this.render();
        if (this.onCircuitChange) this.onCircuitChange(this.gates);
    }

    addQubit() {
        if (this.numQubits < 5) {
            this.numQubits++;
            this.render();
        }
    }

    removeQubit() {
        if (this.numQubits > 1) {
            this.numQubits--;
            this.gates = this.gates.filter(g => g.qubit < this.numQubits);
            this.render();
        }
    }

    clear() {
        this.gates = [];
        this.render();
    }

    render() {
        if (!this.container) return;
        this.container.innerHTML = "";

        for (let q = 0; q < this.numQubits; q++) {
            const row = document.createElement("div");
            row.className = "wire-row";

            const label = document.createElement("div");
            label.className = "wire-label";
            label.textContent = `q_${q}:`;
            row.appendChild(label);

            const line = document.createElement("div");
            line.className = "wire-line";

            for (let c = 0; c < this.numColumns; c++) {
                const slot = document.createElement("div");
                slot.className = "grid-slot";
                slot.dataset.qubit = q;
                slot.dataset.column = c;

                const gate = this.gates.find(g => g.qubit === q && g.column === c);
                if (gate) {
                    const gateEl = document.createElement("div");
                    gateEl.className = `placed-gate ${gate.type === 'CZ' ? 'cz-gate' : ''} ${gate.type === 'M' ? 'm-gate' : ''}`;
                    gateEl.textContent = gate.type;
                    gateEl.title = `${gate.type} Gate — Drag to move, or click to remove`;
                    gateEl.setAttribute("draggable", "true");

                    gateEl.ondragstart = (e) => {
                        e.stopPropagation();
                        this.isDragging = true;
                        const payload = JSON.stringify({
                            source: "placed",
                            id: gate.id,
                            type: gate.type,
                            fromQubit: q,
                            fromColumn: c,
                        });
                        e.dataTransfer.setData("application/json", payload);
                        e.dataTransfer.setData("text/plain", payload);
                        e.dataTransfer.effectAllowed = "all";
                        gateEl.classList.add("gate-dragging");
                    };

                    gateEl.ondragend = () => {
                        gateEl.classList.remove("gate-dragging");
                        setTimeout(() => { this.isDragging = false; }, 50);
                    };

                    slot.appendChild(gateEl);
                }

                // Drag over slot feedback
                slot.ondragover = (e) => {
                    e.preventDefault();
                    e.dataTransfer.dropEffect = "copy";
                    slot.classList.add("drag-over");
                };

                slot.ondragleave = (e) => {
                    if (!slot.contains(e.relatedTarget)) {
                        slot.classList.remove("drag-over");
                    }
                };

                slot.ondrop = (e) => {
                    e.preventDefault();
                    slot.classList.remove("drag-over");
                    this.isDragging = false;
                    slot._justDropped = true;
                    setTimeout(() => { slot._justDropped = false; }, 50);

                    let payload = null;
                    try {
                        const raw = e.dataTransfer.getData("application/json") || e.dataTransfer.getData("text/plain");
                        if (raw) payload = JSON.parse(raw);
                    } catch {
                        return;
                    }
                    if (!payload || !payload.type) return;

                    this.handleDrop(payload, q, c);
                };

                // Click-to-place or click-to-remove
                slot.onclick = () => {
                    if (slot._justDropped) {
                        slot._justDropped = false;
                        return;
                    }
                    this.handleSlotClick(q, c);
                };
                line.appendChild(slot);

            }

            row.appendChild(line);
            this.container.appendChild(row);
        }
    }

    handleDrop(payload, toQubit, toColumn) {
        if (toQubit < 0 || toQubit >= this.numQubits || toColumn < 0 || toColumn >= this.numColumns) {
            return;
        }

        if (payload.source === "palette") {
            const existingIdx = this.gates.findIndex(g => g.qubit === toQubit && g.column === toColumn);
            if (existingIdx >= 0) {
                this.gates.splice(existingIdx, 1);
            }
            const newGate = {
                id: Date.now(),
                type: payload.type,
                qubit: toQubit,
                column: toColumn,
            };
            this.gates.push(newGate);
            if (this.onGateSelect) this.onGateSelect(newGate);
        } else if (payload.source === "placed") {
            const fromQ = payload.fromQubit;
            const fromC = payload.fromColumn;
            if (fromQ === toQubit && fromC === toColumn) return;

            const oldIdx = this.gates.findIndex(g => g.qubit === fromQ && g.column === fromC);
            if (oldIdx >= 0) {
                this.gates.splice(oldIdx, 1);
            }
            const targetIdx = this.gates.findIndex(g => g.qubit === toQubit && g.column === toColumn);
            if (targetIdx >= 0) {
                this.gates.splice(targetIdx, 1);
            }

            const movedGate = {
                id: payload.id || Date.now(),
                type: payload.type,
                qubit: toQubit,
                column: toColumn,
            };
            this.gates.push(movedGate);
            if (this.onGateSelect) this.onGateSelect(movedGate);
        }

        this.isDragging = false;
        this.render();
        if (this.onCircuitChange) this.onCircuitChange(this.gates);
    }

    handleSlotClick(q, c) {
        const idx = this.gates.findIndex(g => g.qubit === q && g.column === c);

        if (idx >= 0) {
            const removed = this.gates.splice(idx, 1)[0];
            if (this.onGateSelect) this.onGateSelect(null);
        } else if (this.selectedTool) {
            const newGate = {
                id: Date.now(),
                type: this.selectedTool,
                qubit: q,
                column: c,
            };
            this.gates.push(newGate);
            if (this.onGateSelect) this.onGateSelect(newGate);
        }
        this.render();
        if (this.onCircuitChange) this.onCircuitChange(this.gates);
    }

}
