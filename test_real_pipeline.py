"""
test_real_pipeline.py — the full real-time pipeline, no fake data.

Runs an ACTUAL Grover circuit through M3's real engine, then feeds that
real result into the AI so it explains genuine simulation evidence.

Run from the repo root (Q-BIT.140), on the integration/mvp branch:
    python test_real_pipeline.py
"""

import sys
import os

# Make backend/ai importable from here, since ask.py/retrieval.py live
# inside backend/ai, not at the repo root.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend", "ai"))

from backend.quantum import QuantumExperiment, run_experiment
from ask import ask_question  # this needs backend/ai/ask.py to exist here

# Step 1: run a REAL quantum experiment
experiment = QuantumExperiment(
    algorithm="grover",
    num_qubits=3,
    target_state="101",
    iterations=2,
    shots=1024,
)
result = run_experiment(experiment)
real_result = result.to_dict()

print("Real M3 result obtained. Now asking the AI to explain it...\n")

# Step 2: ask a question, grounded in the REAL result
question = "Explain what happened in this Grover experiment and why the target state had that probability."
answer = ask_question(question, simulation_result=real_result)

print("AI explanation:\n")
print(answer)
