# Explanation: `tests/adaptive/test_models.py`

## Purpose

This page explains the meaningful behavior in `tests/adaptive/test_models.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
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

```

## Line Notes

### Line 1

`import time`

Imports a dependency or project symbol so later code can use it by name.
### Line 2

`from backend.adaptive.concepts import (`

Imports a dependency or project symbol so later code can use it by name.
### Line 3

`CONCEPT_GRAPH,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 4

`get_concept,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 5

`get_concept_display_name,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 6

`get_concept_graph,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 7

`resolve_concept_id,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 8

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 9

`from backend.adaptive.models import (`

Imports a dependency or project symbol so later code can use it by name.
### Line 10

`AdaptiveRecommendation,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 11

`LearnerContext,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 12

`LearnerState,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 13

`Question,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 14

`QuizResult,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 15

`QuizSubmission,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 16

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 17

`from backend.adaptive.repository import (`

Imports a dependency or project symbol so later code can use it by name.
### Line 18

`InMemoryLearnerRepository,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 19

`JSONFileLearnerRepository,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 20

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 21

`(blank)`

Blank line used to separate nearby statements.
### Line 23

`def test_question_creation_and_concept_id_resolution():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 24

`q = Question(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 25

`topic="Qubits",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 26

`question="What is a qubit?",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 27

`options={"A": "Classical bit", "B": "Quantum bit", "C": "Gate", "D": "Circuit"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 28

`correct_answer="b",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 29

`explanation="A qubit is a quantum bit.",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 30

`difficulty="easy",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 31

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 32

`assert q.topic == "Qubits"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 33

`assert q.correct_answer == "B"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 34

`assert q.concept_id == "quantum.qubit"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 35

`(blank)`

Blank line used to separate nearby statements.
### Line 37

`def test_canonical_concept_resolution():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 38

`assert resolve_concept_id("Qubits") == "quantum.qubit"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 39

`assert resolve_concept_id("Quantum States") == "quantum.state"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 40

`assert resolve_concept_id("Superposition") == "quantum.superposition"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 41

`assert resolve_concept_id("Quantum Gates") == "quantum.gates"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 42

`assert resolve_concept_id("Measurement") == "quantum.measurement"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 43

`assert resolve_concept_id("quantum.qubit") == "quantum.qubit"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 44

`assert resolve_concept_id("unknown_concept") == "unknown_concept"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 45

`(blank)`

Blank line used to separate nearby statements.
### Line 47

`def test_concept_display_name():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 48

`assert get_concept_display_name("quantum.qubit") == "Qubits"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 49

`assert get_concept_display_name("quantum.superposition") == "Superposition"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 50

`assert get_concept_display_name("unknown.concept") == "unknown.concept"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 51

`(blank)`

Blank line used to separate nearby statements.
### Line 53

`def test_get_concept():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 54

`concept = get_concept("quantum.superposition")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 55

`assert concept is not None`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 56

`assert concept.name == "Superposition"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 57

`assert concept.prerequisites == ("quantum.state",)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 58

`assert concept.concept_type == "core"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 59

`(blank)`

Blank line used to separate nearby statements.
### Line 60

`# Lookup by display name`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 61

`by_name = get_concept("Superposition")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 62

`assert by_name == concept`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 63

`(blank)`

Blank line used to separate nearby statements.
### Line 65

`def test_get_concept_graph():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 66

`graph = get_concept_graph()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 67

`assert "quantum.qubit" in graph`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 68

`assert graph["quantum.qubit"]["prereqs"] == []`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 69

`assert graph["quantum.state"]["prereqs"] == ["quantum.qubit"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 70

`assert graph["quantum.superposition"]["prereqs"] == ["quantum.state"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 71

`assert graph["quantum.gates"]["prereqs"] == ["quantum.superposition"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 72

`assert graph["quantum.measurement"]["prereqs"] == ["quantum.gates"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 73

`(blank)`

Blank line used to separate nearby statements.
### Line 75

`def test_learner_state_record_attempt():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 76

`state = LearnerState(user_id="user_123")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 77

`assert state.user_id == "user_123"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 78

`assert state.concept_scores == {}`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 79

`assert state.attempts == {}`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 80

`assert state.errors == {}`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 81

`assert state.score_history == {}`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 82

`(blank)`

Blank line used to separate nearby statements.
### Line 83

`before = time.time()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 84

`state.record_attempt("Qubits", 0.8, ["Question 1"])`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 85

`after = time.time()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 86

`(blank)`

Blank line used to separate nearby statements.
### Line 87

`assert state.concept_scores["Qubits"] == 0.8`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 88

`assert state.attempts["Qubits"] == 1`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 89

`assert state.errors["Qubits"] == ["Question 1"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 90

`assert state.score_history["Qubits"] == [0.8]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 91

`assert before <= state.last_updated["Qubits"] <= after`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 92

`(blank)`

Blank line used to separate nearby statements.
### Line 93

`# Record second attempt`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 94

`state.record_attempt("Qubits", 1.0, [])`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 95

`assert state.concept_scores["Qubits"] == 1.0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 96

`assert state.attempts["Qubits"] == 2`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 97

`assert state.errors["Qubits"] == []`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 98

`assert state.score_history["Qubits"] == [0.8, 1.0]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 99

`(blank)`

Blank line used to separate nearby statements.
### Line 101

`def test_learner_state_to_dict():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 102

`state = LearnerState(user_id="user_123")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 103

`state.record_attempt("Qubits", 1.0, [])`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 104

`d = state.to_dict()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 105

`assert d["user_id"] == "user_123"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 106

`assert d["concept_scores"]["Qubits"] == 1.0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 107

`assert d["attempts"]["Qubits"] == 1`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 108

`(blank)`

Blank line used to separate nearby statements.
### Line 110

`def test_learner_context_creation_and_to_dict():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 111

`rec = AdaptiveRecommendation(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 112

`action="advance",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 113

`target=["Quantum States"],`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 114

`reason="Mastered Qubits.",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 115

`concept_id="quantum.qubit",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 116

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 117

`context = LearnerContext(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 118

`user_id="user_123",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 119

`concept_mastery={"quantum.qubit": 0.95},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 120

`concept_scores={"Qubits": 1.0},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 121

`attempts={"Qubits": 1},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 122

`errors={"Qubits": []},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 123

`score_history={"Qubits": [1.0]},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 124

`current_concept="Qubits",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 125

`recommendation=rec,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 126

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 127

`d = context.to_dict()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 128

`assert d["user_id"] == "user_123"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 129

`assert d["concept_mastery"]["quantum.qubit"] == 0.95`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 130

`assert d["recommendation"]["action"] == "advance"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 131

`assert d["recommendation"]["target"] == ["Quantum States"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 132

`(blank)`

Blank line used to separate nearby statements.
### Line 134

`def test_quiz_result_and_submission():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 135

`sub = QuizSubmission(user_id="u1", topic="Qubits", answers={"Q1": "A"})`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 136

`assert sub.user_id == "u1"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 137

`assert sub.topic == "Qubits"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 138

`assert sub.answers == {"Q1": "A"}`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 139

`(blank)`

Blank line used to separate nearby statements.
### Line 140

`res = QuizResult(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 141

`topic="Qubits",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 142

`concept_id="quantum.qubit",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 143

`score=0.8,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 144

`total_questions=5,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 145

`correct_count=4,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 146

`wrong_questions=["Q2"],`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 147

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 148

`d = res.to_dict()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 149

`assert d["score"] == 0.8`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 150

`assert d["correct_count"] == 4`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 151

`assert d["wrong_questions"] == ["Q2"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 152

`(blank)`

Blank line used to separate nearby statements.
### Line 154

`def test_in_memory_repository():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 155

`repo = InMemoryLearnerRepository()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 156

`assert not repo.exists("u1")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 157

`fresh = repo.get("u1")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 158

`assert fresh.user_id == "u1"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 159

`assert fresh.attempts == {}`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 160

`(blank)`

Blank line used to separate nearby statements.
### Line 161

`fresh.record_attempt("Qubits", 1.0, [])`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 162

`repo.save(fresh)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 163

`assert repo.exists("u1")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 164

`(blank)`

Blank line used to separate nearby statements.
### Line 165

`loaded = repo.get("u1")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 166

`assert loaded.concept_scores["Qubits"] == 1.0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 167

`assert loaded.attempts["Qubits"] == 1`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 168

`(blank)`

Blank line used to separate nearby statements.
### Line 169

`repo.clear()`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 170

`assert not repo.exists("u1")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 171

`(blank)`

Blank line used to separate nearby statements.
### Line 173

`def test_json_file_repository(tmp_path):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 174

`repo = JSONFileLearnerRepository(directory=tmp_path)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 175

`state = repo.get("user_test")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 176

`assert state.user_id == "user_test"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 177

`(blank)`

Blank line used to separate nearby statements.
### Line 178

`state.record_attempt("Superposition", 0.6, ["Wrong 1"])`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 179

`repo.save(state)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 180

`assert repo.exists("user_test")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 181

`(blank)`

Blank line used to separate nearby statements.
### Line 182

`# Reload from fresh repository instance`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 183

`repo2 = JSONFileLearnerRepository(directory=tmp_path)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 184

`reloaded = repo2.get("user_test")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 185

`assert reloaded.user_id == "user_test"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 186

`assert reloaded.concept_scores["Superposition"] == 0.6`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 187

`assert reloaded.errors["Superposition"] == ["Wrong 1"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.

## Nearby Files

[tests/adaptive/__init__.py](__init__.py.md), [tests/adaptive/test_activities.py](test_activities.py.md), [tests/adaptive/test_diagnostics.py](test_diagnostics.py.md), [tests/adaptive/test_evidence.py](test_evidence.py.md), [tests/adaptive/test_evidence_progression.py](test_evidence_progression.py.md), [tests/adaptive/test_mastery.py](test_mastery.py.md), [tests/adaptive/test_pass4_evidence_trace.py](test_pass4_evidence_trace.py.md), [tests/adaptive/test_persistence_hardening.py](test_persistence_hardening.py.md)
