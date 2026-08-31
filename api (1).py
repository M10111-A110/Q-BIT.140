"""
Q-BIT Learner Model API
========================
Thin Flask wrapper around learner_model.py so the existing quiz HTML
pages can POST answers and get back mastery + the adaptive recommendation.

Run:
    pip install flask
    python api.py
    -> served at http://localhost:5000

Endpoints:
    POST /submit_quiz
        body: {
            "user_id": "u123",
            "topic": "Superposition",
            "answers": { "<question text>": "C", ... }
        }
        returns: {
            "score": 0.8,
            "mastery": 0.75,
            "wrong_questions": [...],
            "recommendation": {"action": ..., "target": ..., "reason": ...}
        }

    GET /learner/<user_id>
        returns the learner's full stored state (for a dashboard later)
"""

from flask import Flask, request, jsonify

from learner_model import (
    load_questions, Diagnostic, LearnerModel, JSONStore, CONCEPT_GRAPH
)

app = Flask(__name__)


@app.after_request
def add_cors_headers(response):
    # Allows your HTML pages (served from a different port/origin) to call this API.
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

questions_by_topic = load_questions("quantum_tutor_quiz_dataset.csv")
diagnostic = Diagnostic(questions_by_topic)
model = LearnerModel()
store = JSONStore()


@app.route("/submit_quiz", methods=["POST"])
def submit_quiz():
    data = request.get_json(force=True)
    user_id = data.get("user_id")
    topic = data.get("topic")
    answers = data.get("answers", {})

    if not user_id or not topic:
        return jsonify({"error": "user_id and topic are required"}), 400
    if topic not in questions_by_topic:
        return jsonify({"error": f"unknown topic '{topic}'"}), 400

    score, wrong_questions = diagnostic.score_from_answers(topic, answers)

    state = store.load(user_id)
    state.record_attempt(topic, score, wrong_questions)
    store.save(state)

    mastery = model.compute_mastery(topic, state)
    recommendation = model.recommend_next(topic, state)

    return jsonify({
        "score": score,
        "mastery": mastery,
        "wrong_questions": wrong_questions,
        "recommendation": recommendation,
    })


@app.route("/learner/<user_id>", methods=["GET"])
def get_learner(user_id):
    state = store.load(user_id)
    return jsonify({
        "user_id": state.user_id,
        "concept_scores": state.concept_scores,
        "attempts": state.attempts,
        "errors": state.errors,
        "mastery": {
            topic: model.compute_mastery(topic, state)
            for topic in CONCEPT_GRAPH
        },
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
