import time
from backend.adaptive.concepts import (
    CONCEPT_GRAPH,
    get_concept,
    get_concept_display_name,
    get_concept_graph,
    resolve_concept_id,
)
from backend.adaptive.models import (
    AdaptiveRecommendation,
    LearnerContext,
    LearnerState,
    Question,
    QuizResult,
    QuizSubmission,
)
from backend.adaptive.repository import (
    InMemoryLearnerRepository,
    JSONFileLearnerRepository,
)


def test_question_creation_and_concept_id_resolution():
    q = Question(
        topic="Qubits",
        question="What is a qubit?",
        options={"A": "Classical bit", "B": "Quantum bit", "C": "Gate", "D": "Circuit"},
        correct_answer="b",
        explanation="A qubit is a quantum bit.",
        difficulty="easy",
    )
    assert q.topic == "Qubits"
    assert q.correct_answer == "B"
    assert q.concept_id == "quantum.qubit"


def test_canonical_concept_resolution():
    assert resolve_concept_id("Qubits") == "quantum.qubit"
    assert resolve_concept_id("Quantum States") == "quantum.state"
    assert resolve_concept_id("Superposition") == "quantum.superposition"
    assert resolve_concept_id("Quantum Gates") == "quantum.gates"
    assert resolve_concept_id("Measurement") == "quantum.measurement"
    assert resolve_concept_id("quantum.qubit") == "quantum.qubit"
    assert resolve_concept_id("unknown_concept") == "unknown_concept"


def test_concept_display_name():
    assert get_concept_display_name("quantum.qubit") == "Qubits"
    assert get_concept_display_name("quantum.superposition") == "Superposition"
    assert get_concept_display_name("unknown.concept") == "unknown.concept"


def test_get_concept():
    concept = get_concept("quantum.superposition")
    assert concept is not None
    assert concept.name == "Superposition"
    assert concept.prerequisites == ("quantum.state",)
    assert concept.concept_type == "core"

    # Lookup by display name
    by_name = get_concept("Superposition")
    assert by_name == concept


def test_get_concept_graph():
    graph = get_concept_graph()
    assert "quantum.qubit" in graph
    assert graph["quantum.qubit"]["prereqs"] == []
    assert graph["quantum.state"]["prereqs"] == ["quantum.qubit"]
    assert graph["quantum.superposition"]["prereqs"] == ["quantum.state"]
    assert graph["quantum.gates"]["prereqs"] == ["quantum.superposition"]
    assert graph["quantum.measurement"]["prereqs"] == ["quantum.gates"]


def test_learner_state_record_attempt():
    state = LearnerState(user_id="user_123")
    assert state.user_id == "user_123"
    assert state.concept_scores == {}
    assert state.attempts == {}
    assert state.errors == {}
    assert state.score_history == {}

    before = time.time()
    state.record_attempt("Qubits", 0.8, ["Question 1"])
    after = time.time()

    assert state.concept_scores["Qubits"] == 0.8
    assert state.attempts["Qubits"] == 1
    assert state.errors["Qubits"] == ["Question 1"]
    assert state.score_history["Qubits"] == [0.8]
    assert before <= state.last_updated["Qubits"] <= after

    # Record second attempt
    state.record_attempt("Qubits", 1.0, [])
    assert state.concept_scores["Qubits"] == 1.0
    assert state.attempts["Qubits"] == 2
    assert state.errors["Qubits"] == []
    assert state.score_history["Qubits"] == [0.8, 1.0]


def test_learner_state_to_dict():
    state = LearnerState(user_id="user_123")
    state.record_attempt("Qubits", 1.0, [])
    d = state.to_dict()
    assert d["user_id"] == "user_123"
    assert d["concept_scores"]["Qubits"] == 1.0
    assert d["attempts"]["Qubits"] == 1


def test_learner_context_creation_and_to_dict():
    rec = AdaptiveRecommendation(
        action="advance",
        target=["Quantum States"],
        reason="Mastered Qubits.",
        concept_id="quantum.qubit",
    )
    context = LearnerContext(
        user_id="user_123",
        concept_mastery={"quantum.qubit": 0.95},
        concept_scores={"Qubits": 1.0},
        attempts={"Qubits": 1},
        errors={"Qubits": []},
        score_history={"Qubits": [1.0]},
        current_concept="Qubits",
        recommendation=rec,
    )
    d = context.to_dict()
    assert d["user_id"] == "user_123"
    assert d["concept_mastery"]["quantum.qubit"] == 0.95
    assert d["recommendation"]["action"] == "advance"
    assert d["recommendation"]["target"] == ["Quantum States"]


def test_quiz_result_and_submission():
    sub = QuizSubmission(user_id="u1", topic="Qubits", answers={"Q1": "A"})
    assert sub.user_id == "u1"
    assert sub.topic == "Qubits"
    assert sub.answers == {"Q1": "A"}

    res = QuizResult(
        topic="Qubits",
        concept_id="quantum.qubit",
        score=0.8,
        total_questions=5,
        correct_count=4,
        wrong_questions=["Q2"],
    )
    d = res.to_dict()
    assert d["score"] == 0.8
    assert d["correct_count"] == 4
    assert d["wrong_questions"] == ["Q2"]


def test_in_memory_repository():
    repo = InMemoryLearnerRepository()
    assert not repo.exists("u1")
    fresh = repo.get("u1")
    assert fresh.user_id == "u1"
    assert fresh.attempts == {}

    fresh.record_attempt("Qubits", 1.0, [])
    repo.save(fresh)
    assert repo.exists("u1")

    loaded = repo.get("u1")
    assert loaded.concept_scores["Qubits"] == 1.0
    assert loaded.attempts["Qubits"] == 1

    repo.clear()
    assert not repo.exists("u1")


def test_json_file_repository(tmp_path):
    repo = JSONFileLearnerRepository(directory=tmp_path)
    state = repo.get("user_test")
    assert state.user_id == "user_test"

    state.record_attempt("Superposition", 0.6, ["Wrong 1"])
    repo.save(state)
    assert repo.exists("user_test")

    # Reload from fresh repository instance
    repo2 = JSONFileLearnerRepository(directory=tmp_path)
    reloaded = repo2.get("user_test")
    assert reloaded.user_id == "user_test"
    assert reloaded.concept_scores["Superposition"] == 0.6
    assert reloaded.errors["Superposition"] == ["Wrong 1"]
