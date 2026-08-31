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
