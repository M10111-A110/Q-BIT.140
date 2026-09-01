/**
 * Q-BIT.140 — M6 Interactive Circuit Canvas Studio
 * Handles interactive wire grid rendering, gate placement, and presets.
 * Does NOT execute quantum simulation (M3 on backend is authoritative).
 */

export class CircuitStudio {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.numQubits = options.numQubits || 2;
        this.numColumns = options.numColumns || 6;
        this.gates = options.gates || [];
        this.selectedTool = null;
        this.onCircuitChange = options.onCircuitChange || null;
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
                    gateEl.className = "placed-gate";
                    gateEl.textContent = gate.type;
                    slot.appendChild(gateEl);
                }

                slot.onclick = () => this.handleSlotClick(q, c);
                line.appendChild(slot);
            }

            row.appendChild(line);
            this.container.appendChild(row);
        }
    }

    handleSlotClick(q, c) {
        const idx = this.gates.findIndex(g => g.qubit === q && g.column === c);
        if (idx >= 0) {
            this.gates.splice(idx, 1);
        } else if (this.selectedTool) {
            this.gates.push({
                id: Date.now(),
                type: this.selectedTool,
                qubit: q,
                column: c,
            });
        }
        this.render();
        if (this.onCircuitChange) this.onCircuitChange(this.gates);
    }
}
