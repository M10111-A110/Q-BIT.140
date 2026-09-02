# Explanation: `tests/adaptive/test_diagnostics.py`

## Purpose

This page explains the meaningful behavior in `tests/adaptive/test_diagnostics.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
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

```

## Line Notes

### Line 1

`import pytest`

Imports a dependency or project symbol so later code can use it by name.
### Line 2

`from backend.adaptive.diagnostics import Diagnostic, load_questions`

Imports a dependency or project symbol so later code can use it by name.
### Line 3

`(blank)`

Blank line used to separate nearby statements.
### Line 5

`def test_load_questions_from_default_dataset():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 6

`questions_by_topic = load_questions()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 7

`expected_topics = {"Qubits", "Quantum States", "Superposition", "Quantum Gates", "Measurement"}`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 8

`assert set(questions_by_topic.keys()) == expected_topics`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 9

`(blank)`

Blank line used to separate nearby statements.
### Line 10

`for topic, questions in questions_by_topic.items():`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 11

`assert len(questions) == 5`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 12

`for q in questions:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 13

`assert q.topic == topic`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 14

`assert len(q.question) > 0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 15

`assert set(q.options.keys()) == {"A", "B", "C", "D"}`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 16

`assert all(len(opt) > 0 for opt in q.options.values())`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 17

`assert q.correct_answer in {"A", "B", "C", "D"}`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 18

`assert len(q.explanation) > 0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 19

`assert q.difficulty in {"easy", "medium", "hard"}`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 20

`assert len(q.concept_id) > 0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 21

`(blank)`

Blank line used to separate nearby statements.
### Line 23

`def test_load_questions_invalid_path():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 24

`with pytest.raises(FileNotFoundError):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 25

`load_questions("non_existent_dataset.csv")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 26

`(blank)`

Blank line used to separate nearby statements.
### Line 28

`def test_diagnostic_topics_and_questions():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 29

`diagnostic = Diagnostic()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 30

`topics = diagnostic.get_topics()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 31

`assert len(topics) == 5`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 32

`assert "Superposition" in topics`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 33

`(blank)`

Blank line used to separate nearby statements.
### Line 34

`questions = diagnostic.get_questions("Superposition")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 35

`assert len(questions) == 5`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 36

`(blank)`

Blank line used to separate nearby statements.
### Line 37

`# Canonical ID lookup works`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 38

`by_id = diagnostic.get_questions("quantum.superposition")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 39

`assert by_id == questions`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 40

`(blank)`

Blank line used to separate nearby statements.
### Line 42

`def test_diagnostic_unknown_topic():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 43

`diagnostic = Diagnostic()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 44

`with pytest.raises(KeyError):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 45

`diagnostic.get_questions("NonExistentTopic")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 46

`(blank)`

Blank line used to separate nearby statements.
### Line 48

`def test_score_all_correct():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 49

`diagnostic = Diagnostic()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 50

`questions = diagnostic.get_questions("Qubits")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 51

`perfect_answers = {q.question: q.correct_answer for q in questions}`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 52

`(blank)`

Blank line used to separate nearby statements.
### Line 53

`score, wrong = diagnostic.score_from_answers("Qubits", perfect_answers)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 54

`assert score == 1.0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 55

`assert wrong == []`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 56

`(blank)`

Blank line used to separate nearby statements.
### Line 58

`def test_score_all_wrong():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 59

`diagnostic = Diagnostic()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 60

`questions = diagnostic.get_questions("Qubits")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 61

`# Pick a wrong letter for every question`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 62

`wrong_answers = {}`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 63

`for q in questions:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 64

`wrong_letter = "B" if q.correct_answer != "B" else "A"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 65

`wrong_answers[q.question] = wrong_letter`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 66

`(blank)`

Blank line used to separate nearby statements.
### Line 67

`score, wrong = diagnostic.score_from_answers("Qubits", wrong_answers)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 68

`assert score == 0.0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 69

`assert len(wrong) == 5`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 70

`assert set(wrong) == {q.question for q in questions}`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 71

`(blank)`

Blank line used to separate nearby statements.
### Line 73

`def test_score_partial():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 74

`diagnostic = Diagnostic()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 75

`questions = diagnostic.get_questions("Measurement")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 76

`# Answer first 3 correctly, last 2 wrongly`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 77

`answers = {}`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 78

`for i, q in enumerate(questions):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 79

`if i < 3:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 80

`answers[q.question] = q.correct_answer`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 81

`else:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 82

`wrong_letter = "B" if q.correct_answer != "B" else "A"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 83

`answers[q.question] = wrong_letter`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 84

`(blank)`

Blank line used to separate nearby statements.
### Line 85

`score, wrong = diagnostic.score_from_answers("Measurement", answers)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 86

`assert score == 0.6`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 87

`assert len(wrong) == 2`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 88

`assert wrong == [questions[3].question, questions[4].question]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 89

`(blank)`

Blank line used to separate nearby statements.
### Line 91

`def test_score_case_insensitivity_and_missing_answers():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 92

`diagnostic = Diagnostic()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 93

`questions = diagnostic.get_questions("Quantum Gates")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 94

`# lowercase letters and missing answers`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 95

`answers = {`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 96

`questions[0].question: questions[0].correct_answer.lower(),`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 97

`questions[1].question: f"  {questions[1].correct_answer}  ",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 98

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 99

`# 2 correct, 3 missing -> score 0.4`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 100

`score, wrong = diagnostic.score_from_answers("Quantum Gates", answers)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 101

`assert score == 0.4`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 102

`assert len(wrong) == 3`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 103

`(blank)`

Blank line used to separate nearby statements.
### Line 105

`def test_diagnostic_evaluate_result():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 106

`diagnostic = Diagnostic()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 107

`questions = diagnostic.get_questions("Qubits")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 108

`answers = {q.question: q.correct_answer for q in questions}`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 109

`(blank)`

Blank line used to separate nearby statements.
### Line 110

`result = diagnostic.evaluate("Qubits", answers)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 111

`assert result.topic == "Qubits"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 112

`assert result.concept_id == "quantum.qubit"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 113

`assert result.score == 1.0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 114

`assert result.total_questions == 5`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 115

`assert result.correct_count == 5`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 116

`assert result.wrong_questions == []`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.

## Nearby Files

[tests/adaptive/__init__.py](__init__.py.md), [tests/adaptive/test_activities.py](test_activities.py.md), [tests/adaptive/test_evidence.py](test_evidence.py.md), [tests/adaptive/test_evidence_progression.py](test_evidence_progression.py.md), [tests/adaptive/test_mastery.py](test_mastery.py.md), [tests/adaptive/test_models.py](test_models.py.md), [tests/adaptive/test_pass4_evidence_trace.py](test_pass4_evidence_trace.py.md), [tests/adaptive/test_persistence_hardening.py](test_persistence_hardening.py.md)
