import pytest
from backend.adaptive.engine import LearnerModel
from backend.adaptive.models import LearnerState


def test_rule_1_prerequisite_enforcement():
    model = LearnerModel()
    state = LearnerState(user_id="u1")

    # Prerequisite "Qubits" not mastered (mastery 0.0 < 0.6)
    # Trying to take "Quantum States"
    rec = model.recommend_next("Quantum States", state)
    assert rec.action == "recommend_prerequisite"
    assert rec.target == "Qubits"
    assert "Qubits mastery is 0.0" in rec.reason
    assert rec.concept_id == "quantum.qubit"

    # Prerequisite "Quantum States" not mastered
    # Trying to take "Superposition"
    state.record_attempt("Qubits", 1.0, [])  # Qubits mastered
    rec = model.recommend_next("Superposition", state)
    assert rec.action == "recommend_prerequisite"
    assert rec.target == "Quantum States"
    assert rec.concept_id == "quantum.state"


def test_rule_2_targeted_review_on_error_streak():
    model = LearnerModel()
    state = LearnerState(user_id="u1")

    # 2 errors on Qubits and mastery < 0.6 (score 0.4 - 0.1 = 0.3)
    state.record_attempt("Qubits", 0.4, ["Wrong 1", "Wrong 2"])
    rec = model.recommend_next("Qubits", state)
    assert rec.action == "recommend_targeted_review"
    assert rec.target == "Qubits"
    assert "2 wrong answers on Qubits" in rec.reason
    assert rec.concept_id == "quantum.qubit"


def test_rule_3_advance_on_mastery():
    model = LearnerModel()
    state = LearnerState(user_id="u1")

    # Qubits mastered (score 1.0 >= 0.6) -> unlocks Quantum States
    state.record_attempt("Qubits", 1.0, [])
    rec = model.recommend_next("Qubits", state)
    assert rec.action == "advance"
    assert rec.target == ["Quantum States"]
    assert "ready to move on to Quantum States" in rec.reason
    assert rec.concept_id == "quantum.qubit"

    # Superposition mastered -> unlocks Quantum Gates
    state.record_attempt("Quantum States", 1.0, [])
    state.record_attempt("Superposition", 1.0, [])
    rec_sup = model.recommend_next("Superposition", state)
    assert rec_sup.action == "advance"
    assert rec_sup.target == ["Quantum Gates"]

    # Measurement (end of chain) mastered -> target None, (end of chain) in reason
    state.record_attempt("Quantum Gates", 1.0, [])
    state.record_attempt("Measurement", 1.0, [])
    rec_meas = model.recommend_next("Measurement", state)
    assert rec_meas.action == "advance"
    assert rec_meas.target is None
    assert "(end of chain)" in rec_meas.reason


def test_rule_4_reinforce_current_concept():
    model = LearnerModel()
    state = LearnerState(user_id="u1")

    # Qubits: 1 error (below error streak limit 2), score 0.4 -> mastery 0.35 (< 0.6)
    state.record_attempt("Qubits", 0.4, ["Wrong 1"])
    rec = model.recommend_next("Qubits", state)
    assert rec.action == "reinforce_current_concept"
    assert rec.target == "Qubits"
    assert "needs more practice" in rec.reason
    assert rec.concept_id == "quantum.qubit"


def test_unknown_topic_raises_key_error():
    model = LearnerModel()
    state = LearnerState(user_id="u1")
    with pytest.raises(KeyError):
        model.recommend_next("UnknownTopic", state)


def test_get_learner_context():
    model = LearnerModel()
    state = LearnerState(user_id="learner_abc")
    state.record_attempt("Qubits", 1.0, [])

    context = model.get_learner_context(state, current_topic="Qubits")
    assert context.user_id == "learner_abc"
    assert context.concept_mastery["quantum.qubit"] == 1.0
    assert context.concept_scores["Qubits"] == 1.0
    assert context.current_concept == "Qubits"
    assert context.recommendation is not None
    assert context.recommendation.action == "advance"
    assert context.recommendation.target == ["Quantum States"]

    context_dict = context.to_dict()
    assert context_dict["user_id"] == "learner_abc"
    assert context_dict["recommendation"]["action"] == "advance"
