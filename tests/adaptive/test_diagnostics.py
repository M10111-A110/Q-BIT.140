import pytest
from backend.adaptive.diagnostics import Diagnostic, load_questions


def test_load_questions_from_default_dataset():
    questions_by_topic = load_questions()
    expected_topics = {"Qubits", "Quantum States", "Superposition", "Quantum Gates", "Measurement"}
    assert set(questions_by_topic.keys()) == expected_topics

    for topic, questions in questions_by_topic.items():
        assert len(questions) == 5
        for q in questions:
            assert q.topic == topic
            assert len(q.question) > 0
            assert set(q.options.keys()) == {"A", "B", "C", "D"}
            assert all(len(opt) > 0 for opt in q.options.values())
            assert q.correct_answer in {"A", "B", "C", "D"}
            assert len(q.explanation) > 0
            assert q.difficulty in {"easy", "medium", "hard"}
            assert len(q.concept_id) > 0


def test_load_questions_invalid_path():
    with pytest.raises(FileNotFoundError):
        load_questions("non_existent_dataset.csv")


def test_diagnostic_topics_and_questions():
    diagnostic = Diagnostic()
    topics = diagnostic.get_topics()
    assert len(topics) == 5
    assert "Superposition" in topics

    questions = diagnostic.get_questions("Superposition")
    assert len(questions) == 5

    # Canonical ID lookup works
    by_id = diagnostic.get_questions("quantum.superposition")
    assert by_id == questions


def test_diagnostic_unknown_topic():
    diagnostic = Diagnostic()
    with pytest.raises(KeyError):
        diagnostic.get_questions("NonExistentTopic")


def test_score_all_correct():
    diagnostic = Diagnostic()
    questions = diagnostic.get_questions("Qubits")
    perfect_answers = {q.question: q.correct_answer for q in questions}

    score, wrong = diagnostic.score_from_answers("Qubits", perfect_answers)
    assert score == 1.0
    assert wrong == []


def test_score_all_wrong():
    diagnostic = Diagnostic()
    questions = diagnostic.get_questions("Qubits")
    # Pick a wrong letter for every question
    wrong_answers = {}
    for q in questions:
        wrong_letter = "B" if q.correct_answer != "B" else "A"
        wrong_answers[q.question] = wrong_letter

    score, wrong = diagnostic.score_from_answers("Qubits", wrong_answers)
    assert score == 0.0
    assert len(wrong) == 5
    assert set(wrong) == {q.question for q in questions}


def test_score_partial():
    diagnostic = Diagnostic()
    questions = diagnostic.get_questions("Measurement")
    # Answer first 3 correctly, last 2 wrongly
    answers = {}
    for i, q in enumerate(questions):
        if i < 3:
            answers[q.question] = q.correct_answer
        else:
            wrong_letter = "B" if q.correct_answer != "B" else "A"
            answers[q.question] = wrong_letter

    score, wrong = diagnostic.score_from_answers("Measurement", answers)
    assert score == 0.6
    assert len(wrong) == 2
    assert wrong == [questions[3].question, questions[4].question]


def test_score_case_insensitivity_and_missing_answers():
    diagnostic = Diagnostic()
    questions = diagnostic.get_questions("Quantum Gates")
    # lowercase letters and missing answers
    answers = {
        questions[0].question: questions[0].correct_answer.lower(),
        questions[1].question: f"  {questions[1].correct_answer}  ",
    }
    # 2 correct, 3 missing -> score 0.4
    score, wrong = diagnostic.score_from_answers("Quantum Gates", answers)
    assert score == 0.4
    assert len(wrong) == 3


def test_diagnostic_evaluate_result():
    diagnostic = Diagnostic()
    questions = diagnostic.get_questions("Qubits")
    answers = {q.question: q.correct_answer for q in questions}

    result = diagnostic.evaluate("Qubits", answers)
    assert result.topic == "Qubits"
    assert result.concept_id == "quantum.qubit"
    assert result.score == 1.0
    assert result.total_questions == 5
    assert result.correct_count == 5
    assert result.wrong_questions == []
