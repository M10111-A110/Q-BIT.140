# Explanation: `tests/api/test_json_contracts.py`

## Purpose

This page explains the meaningful behavior in `tests/api/test_json_contracts.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
import json
import pytest
from fastapi.testclient import TestClient
from backend.adaptive.models import LearnerState
from backend.adaptive.repository import SupabaseLearnerRepository
from backend.ai.providers import MockLLMProvider
from backend.api.dependencies import reset_dependencies, set_llm_provider
from backend.api.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_environment():
    reset_dependencies()
    set_llm_provider(MockLLMProvider())
    yield


def test_health_endpoint_json_contract():
    res = client.get("/api/health")
    assert res.status_code == 200
    # Strict JSON serialization check
    json_str = json.dumps(res.json())
    data = json.loads(json_str)
    assert data["status"] == "ok"
    assert data["service"] == "qbit-api"


def test_activities_listing_json_contract():
    res = client.get("/api/activities")
    assert res.status_code == 200
    json_str = json.dumps(res.json())
    data = json.loads(json_str)
    assert isinstance(data, list)
    assert len(data) == 4
    for act in data:
        assert "activity_id" in act
        assert "concept_id" in act
        assert "task_type" in act


def test_activity_detail_json_contract():
    res = client.get("/api/activity/act_grover_2q_predict")
    assert res.status_code == 200
    json_str = json.dumps(res.json())
    data = json.loads(json_str)
    assert data["activity_id"] == "act_grover_2q_predict"
    assert data["concept_id"] == "grover.search_problem"
    assert data["quantum_experiment"]["algorithm"] == "grover"


def test_submission_endpoint_strict_json_contract_and_no_qiskit_leak():
    res = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "test_json_user", "response": "10"},
    )
    assert res.status_code == 200

    # Ensure response passes strict standard json.dumps serialization
    raw_json = res.json()
    json_str = json.dumps(raw_json)
    data = json.loads(json_str)

    # 1. Verify structure
    assert "activity" in data
    assert "learner_response" in data
    assert "verified_result" in data
    assert "evidence" in data
    assert "learner_state" in data
    assert "adaptive_decision" in data

    # 2. Verify verified_result fields & zero Qiskit objects
    verified = data["verified_result"]
    assert verified["algorithm"] == "grover"
    assert verified["target_state"] == "10"
    assert isinstance(verified["counts"], dict)
    assert isinstance(verified["probabilities"], dict)
    assert isinstance(verified["target_probability"], float)
    assert isinstance(verified["most_likely_state"], str)
    assert isinstance(verified["circuit"], dict)
    assert isinstance(verified["circuit"]["diagram"], str)

    # 3. Verify evidence fields
    ev = data["evidence"]
    assert ev["learner_id"] == "test_json_user"
    assert ev["concept_id"] == "grover.search_problem"
    assert isinstance(ev["is_correct"], bool)
    assert isinstance(ev["evaluation_details"], dict)

    # 4. Verify learner_state fields
    state = data["learner_state"]
    assert state["user_id"] == "test_json_user"
    assert isinstance(state["evidence_history"], list)
    assert isinstance(state["gap_inferences"], dict)

    # 5. Verify adaptive_decision fields
    dec = data["adaptive_decision"]
    assert isinstance(dec["action"], str)
    assert isinstance(dec["reason"], str)


def test_ai_ask_json_contract():
    res = client.post(
        "/api/ai/ask",
        json={"question": "What is superposition?", "concept_id": "quantum.superposition"},
    )
    assert res.status_code == 200
    json_str = json.dumps(res.json())
    data = json.loads(json_str)
    assert "question" in data
    assert "answer" in data
    assert "$" in data["answer"]


def test_ai_explain_experiment_json_contract():
    res = client.post(
        "/api/ai/explain_experiment",
        json={
            "learner_response": "01",
            "verified_result": {"algorithm": "grover", "most_likely_state": "10", "target_probability": 0.934},
            "evidence": {"concept_id": "grover.search_problem", "is_correct": False, "evaluation_details": {"match": False}},
            "adaptive_decision": {"action": "gather_evidence", "target": "act_grover_2q_predict", "reason": "Initial mismatch."},
        },
    )
    assert res.status_code == 200
    json_str = json.dumps(res.json())
    data = json.loads(json_str)
    assert "explanation" in data
    assert "learner_response" in data
    assert "adaptive_decision" in data


def test_supabase_learner_repository_mock_adapter():
    """Unit test verifying SupabaseLearnerRepository interaction without live credentials."""
    class MockTable:
        def __init__(self):
            self._storage = {}

        def select(self, *args):
            return self

        def eq(self, field, value):
            self._query_id = value
            return self

        def execute(self):
            class Response:
                def __init__(self, data):
                    self.data = data
            if hasattr(self, "_query_id") and self._query_id in self._storage:
                return Response([{"user_id": self._query_id, "state_data": self._storage[self._query_id]}])
            return Response([])

        def upsert(self, payload):
            self._storage[payload["user_id"]] = payload["state_data"]
            return self

    class MockClient:
        def __init__(self):
            self.tbl = MockTable()

        def table(self, name):
            return self.tbl

    mock_client = MockClient()
    repo = SupabaseLearnerRepository(client=mock_client)

    # 1. Get default state for new user
    s1 = repo.get("user_mock_01")
    assert s1.user_id == "user_mock_01"
    assert repo.exists("user_mock_01") is False

    # 2. Save state
    s1.record_attempt("Superposition", 0.9, [])
    repo.save(s1)

    # 3. Verify exists and retrieve
    assert repo.exists("user_mock_01") is True
    s2 = repo.get("user_mock_01")
    assert s2.user_id == "user_mock_01"
    assert s2.concept_scores["Superposition"] == 0.9

```

## Line Notes

### Line 1

`import json`

Imports a dependency or project symbol so later code can use it by name.
### Line 2

`import pytest`

Imports a dependency or project symbol so later code can use it by name.
### Line 3

`from fastapi.testclient import TestClient`

Imports a dependency or project symbol so later code can use it by name.
### Line 4

`from backend.adaptive.models import LearnerState`

Imports a dependency or project symbol so later code can use it by name.
### Line 5

`from backend.adaptive.repository import SupabaseLearnerRepository`

Imports a dependency or project symbol so later code can use it by name.
### Line 6

`from backend.ai.providers import MockLLMProvider`

Imports a dependency or project symbol so later code can use it by name.
### Line 7

`from backend.api.dependencies import reset_dependencies, set_llm_provider`

Imports a dependency or project symbol so later code can use it by name.
### Line 8

`from backend.api.main import app`

Imports a dependency or project symbol so later code can use it by name.
### Line 9

`(blank)`

Blank line used to separate nearby statements.
### Line 10

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 11

`(blank)`

Blank line used to separate nearby statements.
### Line 13

`@pytest.fixture(autouse=True)`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 14

`def setup_test_environment():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 15

`reset_dependencies()`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 16

`set_llm_provider(MockLLMProvider())`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 17

`yield`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 18

`(blank)`

Blank line used to separate nearby statements.
### Line 20

`def test_health_endpoint_json_contract():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 21

`res = client.get("/api/health")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 22

`assert res.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 23

`# Strict JSON serialization check`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 24

`json_str = json.dumps(res.json())`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 25

`data = json.loads(json_str)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 26

`assert data["status"] == "ok"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 27

`assert data["service"] == "qbit-api"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 28

`(blank)`

Blank line used to separate nearby statements.
### Line 30

`def test_activities_listing_json_contract():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 31

`res = client.get("/api/activities")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 32

`assert res.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 33

`json_str = json.dumps(res.json())`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 34

`data = json.loads(json_str)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 35

`assert isinstance(data, list)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 36

`assert len(data) == 4`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 37

`for act in data:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 38

`assert "activity_id" in act`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 39

`assert "concept_id" in act`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 40

`assert "task_type" in act`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 41

`(blank)`

Blank line used to separate nearby statements.
### Line 43

`def test_activity_detail_json_contract():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 44

`res = client.get("/api/activity/act_grover_2q_predict")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 45

`assert res.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 46

`json_str = json.dumps(res.json())`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 47

`data = json.loads(json_str)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 48

`assert data["activity_id"] == "act_grover_2q_predict"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 49

`assert data["concept_id"] == "grover.search_problem"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 50

`assert data["quantum_experiment"]["algorithm"] == "grover"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 51

`(blank)`

Blank line used to separate nearby statements.
### Line 53

`def test_submission_endpoint_strict_json_contract_and_no_qiskit_leak():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 54

`res = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 55

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 56

`json={"learner_id": "test_json_user", "response": "10"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 57

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 58

`assert res.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 59

`(blank)`

Blank line used to separate nearby statements.
### Line 60

`# Ensure response passes strict standard json.dumps serialization`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 61

`raw_json = res.json()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 62

`json_str = json.dumps(raw_json)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 63

`data = json.loads(json_str)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 64

`(blank)`

Blank line used to separate nearby statements.
### Line 65

`# 1. Verify structure`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 66

`assert "activity" in data`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 67

`assert "learner_response" in data`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 68

`assert "verified_result" in data`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 69

`assert "evidence" in data`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 70

`assert "learner_state" in data`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 71

`assert "adaptive_decision" in data`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 72

`(blank)`

Blank line used to separate nearby statements.
### Line 73

`# 2. Verify verified_result fields & zero Qiskit objects`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 74

`verified = data["verified_result"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 75

`assert verified["algorithm"] == "grover"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 76

`assert verified["target_state"] == "10"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 77

`assert isinstance(verified["counts"], dict)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 78

`assert isinstance(verified["probabilities"], dict)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 79

`assert isinstance(verified["target_probability"], float)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 80

`assert isinstance(verified["most_likely_state"], str)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 81

`assert isinstance(verified["circuit"], dict)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 82

`assert isinstance(verified["circuit"]["diagram"], str)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 83

`(blank)`

Blank line used to separate nearby statements.
### Line 84

`# 3. Verify evidence fields`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 85

`ev = data["evidence"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 86

`assert ev["learner_id"] == "test_json_user"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 87

`assert ev["concept_id"] == "grover.search_problem"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 88

`assert isinstance(ev["is_correct"], bool)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 89

`assert isinstance(ev["evaluation_details"], dict)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 90

`(blank)`

Blank line used to separate nearby statements.
### Line 91

`# 4. Verify learner_state fields`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 92

`state = data["learner_state"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 93

`assert state["user_id"] == "test_json_user"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 94

`assert isinstance(state["evidence_history"], list)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 95

`assert isinstance(state["gap_inferences"], dict)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 96

`(blank)`

Blank line used to separate nearby statements.
### Line 97

`# 5. Verify adaptive_decision fields`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 98

`dec = data["adaptive_decision"]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 99

`assert isinstance(dec["action"], str)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 100

`assert isinstance(dec["reason"], str)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 101

`(blank)`

Blank line used to separate nearby statements.
### Line 103

`def test_ai_ask_json_contract():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 104

`res = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 105

`"/api/ai/ask",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 106

`json={"question": "What is superposition?", "concept_id": "quantum.superposition"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 107

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 108

`assert res.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 109

`json_str = json.dumps(res.json())`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 110

`data = json.loads(json_str)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 111

`assert "question" in data`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 112

`assert "answer" in data`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 113

`assert "$" in data["answer"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 114

`(blank)`

Blank line used to separate nearby statements.
### Line 116

`def test_ai_explain_experiment_json_contract():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 117

`res = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 118

`"/api/ai/explain_experiment",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 119

`json={`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 120

`"learner_response": "01",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 121

`"verified_result": {"algorithm": "grover", "most_likely_state": "10", "target_probability": 0.934},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 122

`"evidence": {"concept_id": "grover.search_problem", "is_correct": False, "evaluation_details": {"match": False}},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 123

`"adaptive_decision": {"action": "gather_evidence", "target": "act_grover_2q_predict", "reason": "Initial mismatch."},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 124

`},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 125

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 126

`assert res.status_code == 200`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 127

`json_str = json.dumps(res.json())`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 128

`data = json.loads(json_str)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 129

`assert "explanation" in data`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 130

`assert "learner_response" in data`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 131

`assert "adaptive_decision" in data`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 132

`(blank)`

Blank line used to separate nearby statements.
### Line 134

`def test_supabase_learner_repository_mock_adapter():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 135

`"""Unit test verifying SupabaseLearnerRepository interaction without live credentials."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 136

`class MockTable:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 137

`def __init__(self):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 138

`self._storage = {}`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 139

`(blank)`

Blank line used to separate nearby statements.
### Line 140

`def select(self, *args):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 141

`return self`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 142

`(blank)`

Blank line used to separate nearby statements.
### Line 143

`def eq(self, field, value):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 144

`self._query_id = value`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 145

`return self`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 146

`(blank)`

Blank line used to separate nearby statements.
### Line 147

`def execute(self):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 148

`class Response:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 149

`def __init__(self, data):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 150

`self.data = data`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 151

`if hasattr(self, "_query_id") and self._query_id in self._storage:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 152

`return Response([{"user_id": self._query_id, "state_data": self._storage[self._query_id]}])`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 153

`return Response([])`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 154

`(blank)`

Blank line used to separate nearby statements.
### Line 155

`def upsert(self, payload):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 156

`self._storage[payload["user_id"]] = payload["state_data"]`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 157

`return self`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 158

`(blank)`

Blank line used to separate nearby statements.
### Line 159

`class MockClient:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 160

`def __init__(self):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 161

`self.tbl = MockTable()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 162

`(blank)`

Blank line used to separate nearby statements.
### Line 163

`def table(self, name):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 164

`return self.tbl`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 165

`(blank)`

Blank line used to separate nearby statements.
### Line 166

`mock_client = MockClient()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 167

`repo = SupabaseLearnerRepository(client=mock_client)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 168

`(blank)`

Blank line used to separate nearby statements.
### Line 169

`# 1. Get default state for new user`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 170

`s1 = repo.get("user_mock_01")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 171

`assert s1.user_id == "user_mock_01"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 172

`assert repo.exists("user_mock_01") is False`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 173

`(blank)`

Blank line used to separate nearby statements.
### Line 174

`# 2. Save state`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 175

`s1.record_attempt("Superposition", 0.9, [])`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 176

`repo.save(s1)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 177

`(blank)`

Blank line used to separate nearby statements.
### Line 178

`# 3. Verify exists and retrieve`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 179

`assert repo.exists("user_mock_01") is True`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 180

`s2 = repo.get("user_mock_01")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 181

`assert s2.user_id == "user_mock_01"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 182

`assert s2.concept_scores["Superposition"] == 0.9`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.

## Nearby Files

[tests/api/__init__.py](__init__.py.md), [tests/api/test_activities.py](test_activities.py.md), [tests/api/test_adaptive_vertical_slice.py](test_adaptive_vertical_slice.py.md), [tests/api/test_ai.py](test_ai.py.md), [tests/api/test_frontend_adapter_and_binding.py](test_frontend_adapter_and_binding.py.md), [tests/api/test_health.py](test_health.py.md), [tests/api/test_m1_m6_integration.py](test_m1_m6_integration.py.md), [tests/api/test_m6_adapter.py](test_m6_adapter.py.md)
