# Explanation: `frontend/js/circuit_view.js`

## Purpose

This page explains the meaningful behavior in `frontend/js/circuit_view.js`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```javascript
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
        this.onCircuitChange = options.onCircuitChange || null;
        this.onGateSelect = options.onGateSelect || null;
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
                    gateEl.title = `${gate.type} Gate - Click to remove`;
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

```

## Line Notes

### Line 1

`/**`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 2

`* Q-BIT.140 — M6 Interactive Circuit Canvas Studio`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 3

`* Handles interactive wire grid rendering, gate placement, presets, and tooltips.`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 4

`* Does NOT execute quantum simulation (M3 on backend is authoritative).`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 5

`*/`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 6

`(blank)`

Blank line used to separate nearby statements.
### Line 7

`export const GATE_DEFINITIONS = {`

Imports or exposes a module symbol so code can be composed across frontend files.
### Line 8

`"H": { name: "Hadamard", matrix: "1/√2 [[1, 1], [1, -1]]", desc: "Creates equal superposition: H|0⟩ = (|0⟩+|1⟩)/√2" },`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 9

`"X": { name: "Pauli-X (NOT)", matrix: "[[0, 1], [1, 0]]", desc: "Bit-flip gate: X|0⟩ = |1⟩, X|1⟩ = |0⟩" },`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 10

`"Y": { name: "Pauli-Y", matrix: "[[0, -i], [i, 0]]", desc: "Bit and phase flip gate" },`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 11

`"Z": { name: "Pauli-Z (Phase)", matrix: "[[1, 0], [0, -1]]", desc: "Phase-flip gate: Z|1⟩ = -|1⟩" },`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 12

`"S": { name: "S (Phase √Z)", matrix: "[[1, 0], [0, i]]", desc: "π/2 phase gate: S|1⟩ = i|1⟩" },`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 13

`"T": { name: "T (π/4 Phase)", matrix: "[[1, 0], [0, e^(iπ/4)]]", desc: "π/4 phase gate: T = √S" },`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 14

`"CZ": { name: "Controlled-Z", matrix: "diag(1, 1, 1, -1)", desc: "Flips phase of |11⟩ target: CZ|11⟩ = -|11⟩" },`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 15

`"M": { name: "Measurement", matrix: "Projective", desc: "Collapses qubit state to computational basis |0⟩ or |1⟩" },`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 16

`};`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 17

`(blank)`

Blank line used to separate nearby statements.
### Line 18

`export class CircuitStudio {`

Imports or exposes a module symbol so code can be composed across frontend files.
### Line 19

`constructor(containerId, options = {}) {`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 20

`this.container = document.getElementById(containerId);`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 21

`this.numQubits = options.numQubits || 2;`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 22

`this.numColumns = options.numColumns || 6;`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 23

`this.gates = options.gates || [];`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 24

`this.selectedTool = null;`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 25

`this.onCircuitChange = options.onCircuitChange || null;`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 26

`this.onGateSelect = options.onGateSelect || null;`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 27

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 28

`(blank)`

Blank line used to separate nearby statements.
### Line 29

`setTool(tool) {`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 30

`this.selectedTool = tool;`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 31

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 32

`(blank)`

Blank line used to separate nearby statements.
### Line 33

`loadPreset(presetName) {`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 34

`if (presetName === "grover_2q") {`

Controls browser-side execution based on data or user/application state.
### Line 35

`this.numQubits = 2;`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 36

`this.numColumns = 6;`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 37

`this.gates = [`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 38

`{ id: 1, type: "H", qubit: 0, column: 0 },`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 39

`{ id: 2, type: "H", qubit: 1, column: 0 },`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 40

`{ id: 3, type: "X", qubit: 0, column: 1 },`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 41

`{ id: 4, type: "CZ", qubit: 1, column: 2 },`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 42

`{ id: 5, type: "X", qubit: 0, column: 3 },`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 43

`{ id: 6, type: "H", qubit: 0, column: 4 },`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 44

`{ id: 7, type: "H", qubit: 1, column: 4 },`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 45

`{ id: 8, type: "M", qubit: 0, column: 5 },`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 46

`{ id: 9, type: "M", qubit: 1, column: 5 },`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 47

`];`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 48

`} else if (presetName === "superposition") {`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 49

`this.numQubits = 2;`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 50

`this.numColumns = 4;`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 51

`this.gates = [`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 52

`{ id: 1, type: "H", qubit: 0, column: 0 },`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 53

`{ id: 2, type: "H", qubit: 1, column: 0 },`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 54

`{ id: 3, type: "M", qubit: 0, column: 3 },`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 55

`{ id: 4, type: "M", qubit: 1, column: 3 },`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 56

`];`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 57

`} else if (presetName === "bell_state") {`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 58

`this.numQubits = 2;`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 59

`this.numColumns = 4;`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 60

`this.gates = [`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 61

`{ id: 1, type: "H", qubit: 0, column: 0 },`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 62

`{ id: 2, type: "CZ", qubit: 1, column: 1 },`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 63

`{ id: 3, type: "M", qubit: 0, column: 3 },`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 64

`{ id: 4, type: "M", qubit: 1, column: 3 },`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 65

`];`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 66

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 67

`this.render();`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 68

`if (this.onCircuitChange) this.onCircuitChange(this.gates);`

Controls browser-side execution based on data or user/application state.
### Line 69

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 70

`(blank)`

Blank line used to separate nearby statements.
### Line 71

`addQubit() {`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 72

`if (this.numQubits < 5) {`

Controls browser-side execution based on data or user/application state.
### Line 73

`this.numQubits++;`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 74

`this.render();`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 75

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 76

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 77

`(blank)`

Blank line used to separate nearby statements.
### Line 78

`removeQubit() {`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 79

`if (this.numQubits > 1) {`

Controls browser-side execution based on data or user/application state.
### Line 80

`this.numQubits--;`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 81

`this.gates = this.gates.filter(g => g.qubit < this.numQubits);`

Defines an arrow-function callback, commonly passed to an event, promise, or collection operation.
### Line 82

`this.render();`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 83

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 84

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 85

`(blank)`

Blank line used to separate nearby statements.
### Line 86

`clear() {`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 87

`this.gates = [];`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 88

`this.render();`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 89

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 90

`(blank)`

Blank line used to separate nearby statements.
### Line 91

`render() {`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 92

`if (!this.container) return;`

Controls browser-side execution based on data or user/application state.
### Line 93

`this.container.innerHTML = "";`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 94

`(blank)`

Blank line used to separate nearby statements.
### Line 95

`for (let q = 0; q < this.numQubits; q++) {`

Controls browser-side execution based on data or user/application state.
### Line 96

`const row = document.createElement("div");`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 97

`row.className = "wire-row";`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 98

`(blank)`

Blank line used to separate nearby statements.
### Line 99

`const label = document.createElement("div");`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 100

`label.className = "wire-label";`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 101

`label.textContent = \`q_${q}:\`;`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 102

`row.appendChild(label);`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 103

`(blank)`

Blank line used to separate nearby statements.
### Line 104

`const line = document.createElement("div");`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 105

`line.className = "wire-line";`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 106

`(blank)`

Blank line used to separate nearby statements.
### Line 107

`for (let c = 0; c < this.numColumns; c++) {`

Controls browser-side execution based on data or user/application state.
### Line 108

`const slot = document.createElement("div");`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 109

`slot.className = "grid-slot";`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 110

`slot.dataset.qubit = q;`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 111

`slot.dataset.column = c;`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 112

`(blank)`

Blank line used to separate nearby statements.
### Line 113

`const gate = this.gates.find(g => g.qubit === q && g.column === c);`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 114

`if (gate) {`

Controls browser-side execution based on data or user/application state.
### Line 115

`const gateEl = document.createElement("div");`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 116

`gateEl.className = \`placed-gate ${gate.type === 'CZ' ? 'cz-gate' : ''} ${gate.type === 'M' ? 'm-gate' : ''}\`;`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 117

`gateEl.textContent = gate.type;`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 118

`gateEl.title = \`${gate.type} Gate - Click to remove\`;`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 119

`slot.appendChild(gateEl);`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 120

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 121

`(blank)`

Blank line used to separate nearby statements.
### Line 122

`slot.onclick = () => this.handleSlotClick(q, c);`

Defines an arrow-function callback, commonly passed to an event, promise, or collection operation.
### Line 123

`line.appendChild(slot);`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 124

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 125

`(blank)`

Blank line used to separate nearby statements.
### Line 126

`row.appendChild(line);`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 127

`this.container.appendChild(row);`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 128

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 129

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 130

`(blank)`

Blank line used to separate nearby statements.
### Line 131

`handleSlotClick(q, c) {`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 132

`const idx = this.gates.findIndex(g => g.qubit === q && g.column === c);`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 133

`if (idx >= 0) {`

Controls browser-side execution based on data or user/application state.
### Line 134

`const removed = this.gates.splice(idx, 1)[0];`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 135

`if (this.onGateSelect) this.onGateSelect(null);`

Controls browser-side execution based on data or user/application state.
### Line 136

`} else if (this.selectedTool) {`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 137

`const newGate = {`

Declares local JavaScript state or a computed value used by subsequent code.
### Line 138

`id: Date.now(),`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 139

`type: this.selectedTool,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 140

`qubit: q,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 141

`column: c,`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 142

`};`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 143

`this.gates.push(newGate);`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 144

`if (this.onGateSelect) this.onGateSelect(newGate);`

Controls browser-side execution based on data or user/application state.
### Line 145

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 146

`this.render();`

Invokes a browser API, project helper, or callback with the values visible in this statement.
### Line 147

`if (this.onCircuitChange) this.onCircuitChange(this.gates);`

Controls browser-side execution based on data or user/application state.
### Line 148

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.
### Line 149

`}`

Contributes to the surrounding frontend behavior, data mapping, or presentation rule.

## Nearby Files

[frontend/js/adapter.js](adapter.js.md), [frontend/js/api_client.js](api_client.js.md)
