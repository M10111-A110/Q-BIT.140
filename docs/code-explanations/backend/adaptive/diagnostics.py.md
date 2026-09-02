# Explanation: `backend/adaptive/diagnostics.py`

## Purpose

This page explains the meaningful behavior in `backend/adaptive/diagnostics.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
from __future__ import annotations

import csv
from pathlib import Path
from typing import Optional

from .concepts import resolve_concept_id
from .models import Question, QuizResult

DEFAULT_DATASET_PATH = Path(__file__).parent / "data" / "quantum_tutor_quiz_dataset.csv"


def load_questions(csv_path: Optional[str | Path] = None) -> dict[str, list[Question]]:
    """
    Load diagnostic quiz questions from the dataset CSV grouped by topic.
    Defaults to the package-bundled quantum_tutor_quiz_dataset.csv.
    """
    path = Path(csv_path) if csv_path else DEFAULT_DATASET_PATH
    if not path.exists():
        raise FileNotFoundError(f"Question dataset not found at {path}")

    by_topic: dict[str, list[Question]] = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            topic = row["topic"].strip()
            q = Question(
                topic=topic,
                question=row["question"].strip(),
                options={
                    "A": row["option_a"],
                    "B": row["option_b"],
                    "C": row["option_c"],
                    "D": row["option_d"],
                },
                correct_answer=row["correct_answer"].strip().upper(),
                explanation=row["explanation"].strip(),
                difficulty=row["difficulty"].strip(),
                concept_id=resolve_concept_id(topic),
            )
            by_topic.setdefault(topic, []).append(q)

    return by_topic


class Diagnostic:
    """
    Diagnostic assessment engine for scoring learner quiz submissions
    and identifying specific error items per concept.
    """

    def __init__(
        self,
        questions_by_topic: Optional[dict[str, list[Question]]] = None,
        dataset_path: Optional[str | Path] = None,
    ) -> None:
        if questions_by_topic is not None:
            self.questions_by_topic = questions_by_topic
        else:
            self.questions_by_topic = load_questions(dataset_path)

    def get_topics(self) -> list[str]:
        """Return all available quiz topic names."""
        return list(self.questions_by_topic.keys())

    def get_questions(self, topic: str) -> list[Question]:
        """Retrieve question bank for a specific topic (or raise KeyError)."""
        if topic in self.questions_by_topic:
            return self.questions_by_topic[topic]

        # Check if topic was supplied as canonical concept ID
        for top_name, qs in self.questions_by_topic.items():
            if qs and qs[0].concept_id == topic:
                return qs

        raise KeyError(f"Unknown topic or concept: '{topic}'. Available: {self.get_topics()}")

    def score_from_answers(
        self,
        topic: str,
        answers: dict[str, str],
    ) -> tuple[float, list[str]]:
        """
        Score a non-interactive quiz submission.
        `answers` maps question_text -> chosen_letter (e.g. 'A', 'B', 'C', 'D').

        Returns (score between 0.0 and 1.0, list of wrong question texts).
        Preserves exact original M2 scoring logic.
        """
        questions = self.get_questions(topic)
        if not questions:
            return 0.0, []

        correct = 0
        wrong_questions: list[str] = []

        for q in questions:
            chosen = answers.get(q.question)
            if chosen and chosen.strip().upper() == q.correct_answer:
                correct += 1
            else:
                wrong_questions.append(q.question)

        score = correct / len(questions)
        return round(score, 4), wrong_questions

    def evaluate(self, topic: str, answers: dict[str, str]) -> QuizResult:
        """
        Structured evaluation of a quiz submission returning a QuizResult domain object.
        """
        questions = self.get_questions(topic)
        score, wrong = self.score_from_answers(topic, answers)
        correct_count = len(questions) - len(wrong)
        concept_id = questions[0].concept_id if questions else resolve_concept_id(topic)

        return QuizResult(
            topic=topic,
            concept_id=concept_id,
            score=score,
            total_questions=len(questions),
            correct_count=correct_count,
            wrong_questions=wrong,
        )

```

## Line Notes

### Line 1

`from __future__ import annotations`

Imports a dependency or project symbol so later code can use it by name.
### Line 2

`(blank)`

Blank line used to separate nearby statements.
### Line 3

`import csv`

Imports a dependency or project symbol so later code can use it by name.
### Line 4

`from pathlib import Path`

Imports a dependency or project symbol so later code can use it by name.
### Line 5

`from typing import Optional`

Imports a dependency or project symbol so later code can use it by name.
### Line 6

`(blank)`

Blank line used to separate nearby statements.
### Line 7

`from .concepts import resolve_concept_id`

Imports a dependency or project symbol so later code can use it by name.
### Line 8

`from .models import Question, QuizResult`

Imports a dependency or project symbol so later code can use it by name.
### Line 9

`(blank)`

Blank line used to separate nearby statements.
### Line 10

`DEFAULT_DATASET_PATH = Path(__file__).parent / "data" / "quantum_tutor_quiz_dataset.csv"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 11

`(blank)`

Blank line used to separate nearby statements.
### Line 13

`def load_questions(csv_path: Optional[str | Path] = None) -> dict[str, list[Question]]:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 14

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 15

`Load diagnostic quiz questions from the dataset CSV grouped by topic.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 16

`Defaults to the package-bundled quantum_tutor_quiz_dataset.csv.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 17

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 18

`path = Path(csv_path) if csv_path else DEFAULT_DATASET_PATH`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 19

`if not path.exists():`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 20

`raise FileNotFoundError(f"Question dataset not found at {path}")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 21

`(blank)`

Blank line used to separate nearby statements.
### Line 22

`by_topic: dict[str, list[Question]] = {}`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 23

`with open(path, newline="", encoding="utf-8-sig") as f:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 24

`reader = csv.DictReader(f)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 25

`for row in reader:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 26

`topic = row["topic"].strip()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 27

`q = Question(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 28

`topic=topic,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 29

`question=row["question"].strip(),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 30

`options={`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 31

`"A": row["option_a"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 32

`"B": row["option_b"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 33

`"C": row["option_c"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 34

`"D": row["option_d"],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 35

`},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 36

`correct_answer=row["correct_answer"].strip().upper(),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 37

`explanation=row["explanation"].strip(),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 38

`difficulty=row["difficulty"].strip(),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 39

`concept_id=resolve_concept_id(topic),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 40

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 41

`by_topic.setdefault(topic, []).append(q)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 42

`(blank)`

Blank line used to separate nearby statements.
### Line 43

`return by_topic`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 44

`(blank)`

Blank line used to separate nearby statements.
### Line 46

`class Diagnostic:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 47

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 48

`Diagnostic assessment engine for scoring learner quiz submissions`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 49

`and identifying specific error items per concept.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 50

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 51

`(blank)`

Blank line used to separate nearby statements.
### Line 52

`def __init__(`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 53

`self,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 54

`questions_by_topic: Optional[dict[str, list[Question]]] = None,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 55

`dataset_path: Optional[str | Path] = None,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 56

`) -> None:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 57

`if questions_by_topic is not None:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 58

`self.questions_by_topic = questions_by_topic`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 59

`else:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 60

`self.questions_by_topic = load_questions(dataset_path)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 61

`(blank)`

Blank line used to separate nearby statements.
### Line 62

`def get_topics(self) -> list[str]:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 63

`"""Return all available quiz topic names."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 64

`return list(self.questions_by_topic.keys())`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 65

`(blank)`

Blank line used to separate nearby statements.
### Line 66

`def get_questions(self, topic: str) -> list[Question]:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 67

`"""Retrieve question bank for a specific topic (or raise KeyError)."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 68

`if topic in self.questions_by_topic:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 69

`return self.questions_by_topic[topic]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 70

`(blank)`

Blank line used to separate nearby statements.
### Line 71

`# Check if topic was supplied as canonical concept ID`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 72

`for top_name, qs in self.questions_by_topic.items():`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 73

`if qs and qs[0].concept_id == topic:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 74

`return qs`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 75

`(blank)`

Blank line used to separate nearby statements.
### Line 76

`raise KeyError(f"Unknown topic or concept: '{topic}'. Available: {self.get_topics()}")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 77

`(blank)`

Blank line used to separate nearby statements.
### Line 78

`def score_from_answers(`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 79

`self,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 80

`topic: str,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 81

`answers: dict[str, str],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 82

`) -> tuple[float, list[str]]:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 83

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 84

`Score a non-interactive quiz submission.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 85

`\`answers\` maps question_text -> chosen_letter (e.g. 'A', 'B', 'C', 'D').`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 86

`(blank)`

Blank line used to separate nearby statements.
### Line 87

`Returns (score between 0.0 and 1.0, list of wrong question texts).`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 88

`Preserves exact original M2 scoring logic.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 89

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 90

`questions = self.get_questions(topic)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 91

`if not questions:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 92

`return 0.0, []`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 93

`(blank)`

Blank line used to separate nearby statements.
### Line 94

`correct = 0`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 95

`wrong_questions: list[str] = []`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 96

`(blank)`

Blank line used to separate nearby statements.
### Line 97

`for q in questions:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 98

`chosen = answers.get(q.question)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 99

`if chosen and chosen.strip().upper() == q.correct_answer:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 100

`correct += 1`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 101

`else:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 102

`wrong_questions.append(q.question)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 103

`(blank)`

Blank line used to separate nearby statements.
### Line 104

`score = correct / len(questions)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 105

`return round(score, 4), wrong_questions`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 106

`(blank)`

Blank line used to separate nearby statements.
### Line 107

`def evaluate(self, topic: str, answers: dict[str, str]) -> QuizResult:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 108

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 109

`Structured evaluation of a quiz submission returning a QuizResult domain object.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 110

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 111

`questions = self.get_questions(topic)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 112

`score, wrong = self.score_from_answers(topic, answers)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 113

`correct_count = len(questions) - len(wrong)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 114

`concept_id = questions[0].concept_id if questions else resolve_concept_id(topic)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 115

`(blank)`

Blank line used to separate nearby statements.
### Line 116

`return QuizResult(`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 117

`topic=topic,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 118

`concept_id=concept_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 119

`score=score,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 120

`total_questions=len(questions),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 121

`correct_count=correct_count,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 122

`wrong_questions=wrong,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 123

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.

## Nearby Files

[backend/adaptive/__init__.py](__init__.py.md), [backend/adaptive/activities.py](activities.py.md), [backend/adaptive/concepts.py](concepts.py.md), [backend/adaptive/engine.py](engine.py.md), [backend/adaptive/evidence.py](evidence.py.md), [backend/adaptive/models.py](models.py.md), [backend/adaptive/repository.py](repository.py.md)
