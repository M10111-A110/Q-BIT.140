from backend.adaptive.engine import LearnerModel
from backend.adaptive.models import LearnerState


def test_mastery_initial_single_attempt():
    model = LearnerModel()
    state = LearnerState(user_id="u1")

    # 1 attempt: score 0.8, 1 error -> mastery = 0.8 + 0.0 - 0.05 = 0.75
    state.record_attempt("Qubits", 0.8, ["Question 1"])
    mastery = model.compute_mastery("Qubits", state)
    assert mastery == 0.75


def test_mastery_with_improvement_bonus():
    model = LearnerModel()
    state = LearnerState(user_id="u1")

    # Attempt 1: score 0.4
    state.record_attempt("Superposition", 0.4, ["Q1", "Q2", "Q3"])
    # Attempt 2: score 0.8, 1 error
    # improvement = (0.8 - 0.4) * 0.2 = +0.08
    # error penalty = 1 * 0.05 = 0.05
    # mastery = 0.8 + 0.08 - 0.05 = 0.83
    state.record_attempt("Superposition", 0.8, ["Q1"])
    mastery = model.compute_mastery("Superposition", state)
    assert mastery == 0.83


def test_mastery_improvement_bonus_cap():
    model = LearnerModel()
    state = LearnerState(user_id="u1")

    # Jump from 0.0 to 1.0 -> improvement = 1.0 * 0.2 = 0.2 (max bonus)
    state.record_attempt("Measurement", 0.0, ["Q1", "Q2", "Q3", "Q4", "Q5"])
    state.record_attempt("Measurement", 1.0, [])
    # mastery = 1.0 + 0.2 - 0 = 1.2 -> clamped to 1.0
    mastery = model.compute_mastery("Measurement", state)
    assert mastery == 1.0


def test_mastery_no_bonus_on_score_drop():
    model = LearnerModel()
    state = LearnerState(user_id="u1")

    # Attempt 1: 0.8, Attempt 2: 0.6 -> score drop gives 0 bonus
    state.record_attempt("Quantum Gates", 0.8, ["Q1"])
    state.record_attempt("Quantum Gates", 0.6, ["Q1", "Q2"])
    # mastery = 0.6 + 0.0 - (2 * 0.05) = 0.50
    mastery = model.compute_mastery("Quantum Gates", state)
    assert mastery == 0.5


def test_mastery_error_penalty_cap():
    model = LearnerModel()
    state = LearnerState(user_id="u1")

    # 10 errors -> 10 * 0.05 = 0.50, but penalty is capped at 0.30
    many_errors = [f"Err {i}" for i in range(10)]
    state.record_attempt("Quantum States", 0.4, many_errors)
    # mastery = 0.4 + 0.0 - 0.3 = 0.10
    mastery = model.compute_mastery("Quantum States", state)
    assert mastery == 0.1


def test_mastery_bounds_and_rounding():
    model = LearnerModel()
    state = LearnerState(user_id="u1")

    # Lower bound clamp
    state.record_attempt("Qubits", 0.0, ["Q1", "Q2", "Q3", "Q4", "Q5"])
    mastery_low = model.compute_mastery("Qubits", state)
    assert mastery_low == 0.0

    # Upper bound clamp
    state.record_attempt("Measurement", 1.0, [])
    mastery_high = model.compute_mastery("Measurement", state)
    assert mastery_high == 1.0


def test_get_mastery_profile():
    model = LearnerModel()
    state = LearnerState(user_id="u1")
    state.record_attempt("Qubits", 1.0, [])
    state.record_attempt("Quantum States", 0.8, ["Q1"])

    profile = model.get_mastery_profile(state)
    assert len(profile) == 5
    assert profile["Qubits"] == 1.0
    assert profile["Quantum States"] == 0.75
    assert profile["Superposition"] == 0.0
    assert profile["Quantum Gates"] == 0.0
    assert profile["Measurement"] == 0.0
