"""
Q-BIT — Adaptive Learner Model (Member 2 component)
=====================================================

This single file implements everything your slides scoped for Member 2:

    A. Concept graph        -> CONCEPT_GRAPH
    B. Diagnostic system     -> Diagnostic.run() / Diagnostic.score()
    C. Mastery model         -> LearnerModel.compute_mastery()
    D. Adaptive rules        -> LearnerModel.recommend_next()

Data source: quantum_tutor_quiz_dataset.csv (the same 5 topics as your
5 HTML quiz pages: Qubits, Quantum States, Superposition, Quantum Gates,
Measurement). No ML, no external model calls — fully rule-based and
explainable, matching what your defense doc recommends.

Where your teammate's LLM plugs in later: see `interpret_free_text_answer()`
near the bottom. Everything else (state, scoring, mastery, routing) is
independent of that and works today with plain multiple-choice answers.

Persistence: one JSON file per learner in ./learner_data/<user_id>.json
Swap `JSONStore` for a real DB later without touching the logic above it.
"""

from __future__ import annotations

import csv
import json
import os
import time
from dataclasses import dataclass, field, asdict
from typing import Optional


# ---------------------------------------------------------------------------
# A. CONCEPT GRAPH
# ---------------------------------------------------------------------------
# Order matches your slide's example chain:
#   Qubit -> Superposition -> Quantum Gates -> Measurement -> [Algorithm]
# "Quantum States" is inserted between Qubits and Superposition since your
# dataset treats it as the generalization step (amplitudes, basis states)
# that superposition builds on.

CONCEPT_GRAPH = {
    "Qubits":          {"prereqs": [],                 "type": "prerequisite"},
    "Quantum States":  {"prereqs": ["Qubits"],          "type": "prerequisite"},
    "Superposition":   {"prereqs": ["Quantum States"],  "type": "core"},
    "Quantum Gates":   {"prereqs": ["Superposition"],   "type": "core"},
    "Measurement":     {"prereqs": ["Quantum Gates"],   "type": "core"},
}

MASTERY_THRESHOLD = 0.6   # below this, a concept counts as "not yet mastered"
ERROR_STREAK_LIMIT = 2    # repeated wrong answers on same concept -> flag


# ---------------------------------------------------------------------------
# DATA LOADING — reads your actual CSV (topic,question,option_a..d,
# correct_answer,explanation,difficulty)
# ---------------------------------------------------------------------------

@dataclass
class Question:
    topic: str
    question: str
    options: dict            # {"A": "...", "B": "...", "C": "...", "D": "..."}
    correct_answer: str      # "A" / "B" / "C" / "D"
    explanation: str
    difficulty: str


def load_questions(csv_path: str) -> dict[str, list[Question]]:
    """Groups questions by topic, exactly as they appear in the dataset."""
    by_topic: dict[str, list[Question]] = {}
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            q = Question(
                topic=row["topic"].strip(),
                question=row["question"].strip(),
                options={
                    "A": row["option_a"], "B": row["option_b"],
                    "C": row["option_c"], "D": row["option_d"],
                },
                correct_answer=row["correct_answer"].strip().upper(),
                explanation=row["explanation"].strip(),
                difficulty=row["difficulty"].strip(),
            )
            by_topic.setdefault(q.topic, []).append(q)
    return by_topic


# ---------------------------------------------------------------------------
# LEARNER STATE
# ---------------------------------------------------------------------------

@dataclass
class LearnerState:
    user_id: str
    concept_scores: dict = field(default_factory=dict)     # {"Qubits": 0.8}
    attempts: dict = field(default_factory=dict)            # {"Qubits": 2}
    errors: dict = field(default_factory=dict)              # {"Qubits": [question_text, ...]}
    score_history: dict = field(default_factory=dict)       # {"Qubits": [0.6, 0.8]}
    last_updated: dict = field(default_factory=dict)        # {"Qubits": timestamp}

    def record_attempt(self, topic: str, score: float, wrong_questions: list[str]):
        self.concept_scores[topic] = score
        self.attempts[topic] = self.attempts.get(topic, 0) + 1
        self.errors[topic] = wrong_questions
        self.score_history.setdefault(topic, []).append(score)
        self.last_updated[topic] = time.time()


class JSONStore:
    """Minimal per-user persistence. Swap for a real DB later."""

    def __init__(self, directory: str = "learner_data"):
        self.directory = directory
        os.makedirs(directory, exist_ok=True)

    def _path(self, user_id: str) -> str:
        return os.path.join(self.directory, f"{user_id}.json")

    def load(self, user_id: str) -> LearnerState:
        path = self._path(user_id)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            return LearnerState(**data)
        return LearnerState(user_id=user_id)

    def save(self, state: LearnerState):
        with open(self._path(state.user_id), "w", encoding="utf-8") as f:
            json.dump(asdict(state), f, indent=2)


# ---------------------------------------------------------------------------
# B. DIAGNOSTIC SYSTEM
# ---------------------------------------------------------------------------

class Diagnostic:
    """Runs a topic's quiz (CLI for now) and scores it."""

    def __init__(self, questions_by_topic: dict[str, list[Question]]):
        self.questions_by_topic = questions_by_topic

    def run_cli(self, topic: str) -> tuple[float, list[str]]:
        """Presents each question in the terminal, returns (score 0-1, wrong_qs)."""
        questions = self.questions_by_topic[topic]
        correct = 0
        wrong_questions = []

        print(f"\n--- {topic} Quiz ---")
        for i, q in enumerate(questions, 1):
            print(f"\nQ{i}. {q.question}")
            for letter, text in q.options.items():
                print(f"   {letter}) {text}")
            answer = input("Your answer (A/B/C/D): ").strip().upper()

            if answer == q.correct_answer:
                correct += 1
                print("Correct.")
            else:
                wrong_questions.append(q.question)
                print(f"Incorrect. Correct answer: {q.correct_answer} — {q.explanation}")

        score = correct / len(questions)
        return score, wrong_questions

    def score_from_answers(self, topic: str, answers: dict[str, str]) -> tuple[float, list[str]]:
        """
        Non-interactive scoring path — use this from a web backend.
        `answers` = {question_text: chosen_letter}
        """
        questions = self.questions_by_topic[topic]
        correct = 0
        wrong_questions = []
        for q in questions:
            chosen = answers.get(q.question)
            if chosen and chosen.strip().upper() == q.correct_answer:
                correct += 1
            else:
                wrong_questions.append(q.question)
        score = correct / len(questions)
        return score, wrong_questions


# ---------------------------------------------------------------------------
# C. MASTERY MODEL  +  D. ADAPTIVE RULES
# ---------------------------------------------------------------------------

class LearnerModel:
    """
    Ties everything together: given a learner's state, decide their mastery
    per concept and what should happen next. Every decision returns a
    human-readable `reason` string — this is your explainability story for
    judges, instead of a black-box ML model.
    """

    def __init__(self, concept_graph: dict = CONCEPT_GRAPH, threshold: float = MASTERY_THRESHOLD):
        self.graph = concept_graph
        self.threshold = threshold

    def compute_mastery(self, topic: str, state: LearnerState) -> float:
        """
        mastery = diagnostic_score
                  + improvement_bonus (did they get better since last attempt?)
                  - error_penalty (repeated mistakes on this topic)
        Kept simple and transparent on purpose — every term is traceable
        back to something the learner actually did.
        """
        diag_score = state.concept_scores.get(topic, 0.0)

        history = state.score_history.get(topic, [])
        improvement = 0.0
        if len(history) >= 2:
            improvement = max(0.0, history[-1] - history[-2]) * 0.2  # up to +0.2 bonus

        error_count = len(state.errors.get(topic, []))
        error_penalty = min(error_count * 0.05, 0.3)  # capped so one bad quiz isn't fatal

        mastery = diag_score + improvement - error_penalty
        return round(max(0.0, min(1.0, mastery)), 3)

    def recommend_next(self, topic: str, state: LearnerState) -> dict:
        """
        Returns: {"action": ..., "target": ..., "reason": ...}
        Actions: recommend_prerequisite | recommend_targeted_review |
                 advance | reinforce_current_concept
        """
        # 1. Check prerequisites are solid before anything else
        for prereq in self.graph[topic]["prereqs"]:
            prereq_mastery = self.compute_mastery(prereq, state)
            if prereq_mastery < self.threshold:
                return {
                    "action": "recommend_prerequisite",
                    "target": prereq,
                    "reason": f"{prereq} mastery is {prereq_mastery} (< {self.threshold}), "
                              f"so {topic} isn't safe to build on yet.",
                }

        mastery = self.compute_mastery(topic, state)
        error_count = len(state.errors.get(topic, []))

        # 2. Repeated errors on this exact concept -> targeted review, not just "redo quiz"
        if error_count >= ERROR_STREAK_LIMIT and mastery < self.threshold:
            return {
                "action": "recommend_targeted_review",
                "target": topic,
                "reason": f"{error_count} wrong answers on {topic} and mastery is only "
                          f"{mastery} — needs focused review, not just repetition.",
            }

        # 3. Mastered -> unlock whatever has this topic as a prerequisite
        if mastery >= self.threshold:
            next_topics = [c for c, v in self.graph.items() if topic in v["prereqs"]]
            return {
                "action": "advance",
                "target": next_topics if next_topics else None,
                "reason": f"{topic} mastery is {mastery} (>= {self.threshold}) — "
                          f"ready to move on{' to ' + ', '.join(next_topics) if next_topics else ' (end of chain)'}.",
            }

        # 4. Default: not mastered yet, no glaring error pattern -> reinforce
        return {
            "action": "reinforce_current_concept",
            "target": topic,
            "reason": f"{topic} mastery is {mastery} (< {self.threshold}) — "
                      f"needs more practice before moving on.",
        }


# ---------------------------------------------------------------------------
# LLM PLUG-IN POINT (for your teammate's model)
# ---------------------------------------------------------------------------
# Right now, quiz answers are multiple-choice letters (A/B/C/D), scored
# exactly. If/when you add free-text or reasoning-style questions, the LLM
# slots in HERE — its only job is to turn messy user input into one of the
# structured signals below. It should NEVER touch mastery math or routing;
# keep it a thin adapter so the explainability story stays intact.

def interpret_free_text_answer(user_response: str, question: Question) -> dict:
    """
    Placeholder for the LLM integration.

    Expected return shape (fill this in once the LLM is wired up):
        {
            "matched_option": "A" | "B" | "C" | "D" | None,
            "confidence": 0.0-1.0,
            "detected_misconception": str | None,  # e.g. "confuses superposition with entanglement"
        }

    Until then, this raises — nothing downstream depends on it, so the
    rest of the pipeline (CSV -> diagnostic -> mastery -> routing) works
    standalone with plain multiple-choice input.
    """
    raise NotImplementedError("Wire this up to the LLM once it's ready.")


# ---------------------------------------------------------------------------
# DEMO / CLI ENTRY POINT
# ---------------------------------------------------------------------------

def demo(csv_path: str = "quantum_tutor_quiz_dataset.csv", user_id: str = "demo_user"):
    questions_by_topic = load_questions(csv_path)
    store = JSONStore()
    state = store.load(user_id)
    diagnostic = Diagnostic(questions_by_topic)
    model = LearnerModel()

    print("Topics available:", ", ".join(questions_by_topic.keys()))
    topic = input("Which topic quiz do you want to take? ").strip()
    if topic not in questions_by_topic:
        print("Unknown topic.")
        return

    score, wrong_qs = diagnostic.run_cli(topic)
    state.record_attempt(topic, score, wrong_qs)
    store.save(state)

    mastery = model.compute_mastery(topic, state)
    decision = model.recommend_next(topic, state)

    print(f"\nScore: {score:.0%}")
    print(f"Mastery({topic}) = {mastery}")
    print(f"Decision: {decision['action']} -> {decision['target']}")
    print(f"Why: {decision['reason']}")


if __name__ == "__main__":
    demo()
