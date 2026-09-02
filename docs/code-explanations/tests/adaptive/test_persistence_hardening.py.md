# Explanation: `tests/adaptive/test_persistence_hardening.py`

## Purpose

This page explains the meaningful behavior in `tests/adaptive/test_persistence_hardening.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
import json
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from backend.adaptive import (
    InMemoryLearnerRepository,
    JSONFileLearnerRepository,
    LearnerState,
    PersistenceError,
    StorageUnavailableError,
    SupabaseLearnerRepository,
)
from backend.api.dependencies import reset_dependencies, set_learner_repository
from backend.api.main import app


def test_missing_learner_returns_fresh_state_in_memory():
    """Requirement A/J: Missing learner returns clean default LearnerState without storage error."""
    repo = InMemoryLearnerRepository()
    state = repo.get("non_existent_learner")
    assert state.user_id == "non_existent_learner"
    assert len(state.evidence_history) == 0
    assert len(state.gap_inferences) == 0


def test_successful_get_and_save_in_memory():
    """Requirement B/D: Persisted state reconstructed correctly."""
    repo = InMemoryLearnerRepository()
    state = LearnerState(user_id="u_persisted")
    state.record_attempt("Qubits", 1.0, [])
    repo.save(state)

    loaded = repo.get("u_persisted")
    assert loaded.user_id == "u_persisted"
    assert loaded.concept_scores["Qubits"] == 1.0
    assert loaded.attempts["Qubits"] == 1


def test_exists_in_memory():
    """Requirement F: exists() returns true for present learner, false for missing."""
    repo = InMemoryLearnerRepository()
    assert repo.exists("u1") is False
    repo.save(LearnerState(user_id="u1"))
    assert repo.exists("u1") is True


def test_repeated_saves_preserve_accumulated_evidence(tmp_path):
    """Requirement H: Repeated saves preserve history and do not overwrite with empty state."""
    repo = JSONFileLearnerRepository(directory=tmp_path)
    state = repo.get("u_repeat")

    # Step 1: Record first attempt
    state.evidence_history.append({"attempt": 1, "is_correct": False})
    state.score_history.setdefault("Qubits", []).append(0.0)
    repo.save(state)

    # Step 2: Reload and record second attempt
    loaded_1 = repo.get("u_repeat")
    assert len(loaded_1.evidence_history) == 1
    loaded_1.evidence_history.append({"attempt": 2, "is_correct": True})
    loaded_1.score_history.setdefault("Qubits", []).append(1.0)
    repo.save(loaded_1)

    # Step 3: Final verification
    loaded_2 = repo.get("u_repeat")
    assert len(loaded_2.evidence_history) == 2
    assert loaded_2.evidence_history[0]["attempt"] == 1
    assert loaded_2.evidence_history[1]["attempt"] == 2
    assert loaded_2.score_history["Qubits"] == [0.0, 1.0]


def test_json_file_repository_malformed_data_raises_storage_error(tmp_path):
    """Requirement C/K: Malformed persisted file raises StorageUnavailableError."""
    repo = JSONFileLearnerRepository(directory=tmp_path)
    bad_file = tmp_path / "corrupt_user.json"
    bad_file.write_text("{ this is not valid json", encoding="utf-8")

    with pytest.raises(StorageUnavailableError):
        repo.get("corrupt_user")


def test_json_file_repository_write_failure_raises_storage_error(tmp_path, monkeypatch):
    """Requirement E: Filesystem write error raises StorageUnavailableError."""
    repo = JSONFileLearnerRepository(directory=tmp_path)
    state = LearnerState(user_id="u_write_err")

    # Force open to fail
    def fake_open(*args, **kwargs):
        raise PermissionError("Simulated permission denied")

    monkeypatch.setattr("builtins.open", fake_open)

    with pytest.raises(StorageUnavailableError):
        repo.save(state)


def test_supabase_unconfigured_raises_storage_error():
    """Requirement C/E: Supabase repository without client raises StorageUnavailableError."""
    repo = SupabaseLearnerRepository(client=None)

    with pytest.raises(StorageUnavailableError):
        repo.get("user_1")

    with pytest.raises(StorageUnavailableError):
        repo.save(LearnerState(user_id="user_1"))

    with pytest.raises(StorageUnavailableError):
        repo.exists("user_1")


def test_supabase_mock_successful_get_and_save():
    """Requirement B/D: Mocked healthy Supabase query and upsert."""
    mock_client = MagicMock()
    mock_table = MagicMock()
    mock_client.table.return_value = mock_table

    # Mock get()
    mock_select = MagicMock()
    mock_eq = MagicMock()
    mock_table.select.return_value = mock_select
    mock_select.eq.return_value = mock_eq

    sample_state = LearnerState(user_id="sb_user")
    sample_state.concept_scores["Qubits"] = 1.0

    mock_resp = MagicMock()
    mock_resp.data = [{"state_data": sample_state.to_dict()}]
    mock_eq.execute.return_value = mock_resp

    repo = SupabaseLearnerRepository(client=mock_client)
    loaded = repo.get("sb_user")

    assert loaded.user_id == "sb_user"
    assert loaded.concept_scores["Qubits"] == 1.0

    # Mock save()
    mock_upsert = MagicMock()
    mock_table.upsert.return_value = mock_upsert
    mock_upsert.execute.return_value = MagicMock()

    repo.save(loaded)
    mock_table.upsert.assert_called_once()


def test_supabase_mock_database_failure_during_get():
    """Requirement C: Database query failure raises StorageUnavailableError instead of fresh state."""
    mock_client = MagicMock()
    mock_table = MagicMock()
    mock_client.table.return_value = mock_table
    mock_table.select.side_effect = RuntimeError("PostgreSQL connection timeout")

    repo = SupabaseLearnerRepository(client=mock_client)

    with pytest.raises(StorageUnavailableError) as exc_info:
        repo.get("sb_failing_user")

    assert "Database query failed" in str(exc_info.value)


def test_supabase_mock_database_failure_during_save():
    """Requirement E: Database upsert failure raises StorageUnavailableError."""
    mock_client = MagicMock()
    mock_table = MagicMock()
    mock_client.table.return_value = mock_table
    mock_table.upsert.side_effect = RuntimeError("PostgreSQL disk quota exceeded")

    repo = SupabaseLearnerRepository(client=mock_client)

    with pytest.raises(StorageUnavailableError) as exc_info:
        repo.save(LearnerState(user_id="sb_user"))

    assert "Database upsert failed" in str(exc_info.value)


def test_supabase_mock_database_failure_during_exists():
    """Requirement G: Database query failure during exists() raises StorageUnavailableError."""
    mock_client = MagicMock()
    mock_table = MagicMock()
    mock_client.table.return_value = mock_table
    mock_table.select.side_effect = RuntimeError("Network partition")

    repo = SupabaseLearnerRepository(client=mock_client)

    with pytest.raises(StorageUnavailableError):
        repo.exists("sb_user")


def test_api_submission_returns_503_when_get_fails():
    """Requirement I: API submission returns HTTP 503 if loading learner state fails."""
    client = TestClient(app)

    # Repository that fails on get
    class FailingGetRepo(InMemoryLearnerRepository):
        def get(self, user_id: str) -> LearnerState:
            raise StorageUnavailableError("Database unreachable")

    set_learner_repository(FailingGetRepo())

    res = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_fail_get", "response": "10"},
    )
    assert res.status_code == 503
    assert "Learner state persistence service is currently unavailable" in res.json()["detail"]

    reset_dependencies()


def test_api_submission_returns_503_when_save_fails():
    """Requirement I: API submission returns HTTP 503 if saving state fails, never pretending success."""
    client = TestClient(app)

    # Repository that succeeds on get but fails on save
    class FailingSaveRepo(InMemoryLearnerRepository):
        def save(self, state: LearnerState) -> None:
            raise StorageUnavailableError("Failed to write to database")

    set_learner_repository(FailingSaveRepo())

    res = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_fail_save", "response": "10"},
    )
    assert res.status_code == 503
    assert "Failed to persist updated learner state" in res.json()["detail"]

    reset_dependencies()

```

## Line Notes

### Line 1

`import json`

Imports a dependency or project symbol so later code can use it by name.
### Line 2

`import pytest`

Imports a dependency or project symbol so later code can use it by name.
### Line 3

`from unittest.mock import MagicMock`

Imports a dependency or project symbol so later code can use it by name.
### Line 4

`from fastapi.testclient import TestClient`

Imports a dependency or project symbol so later code can use it by name.
### Line 5

`(blank)`

Blank line used to separate nearby statements.
### Line 6

`from backend.adaptive import (`

Imports a dependency or project symbol so later code can use it by name.
### Line 7

`InMemoryLearnerRepository,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 8

`JSONFileLearnerRepository,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 9

`LearnerState,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 10

`PersistenceError,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 11

`StorageUnavailableError,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 12

`SupabaseLearnerRepository,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 13

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 14

`from backend.api.dependencies import reset_dependencies, set_learner_repository`

Imports a dependency or project symbol so later code can use it by name.
### Line 15

`from backend.api.main import app`

Imports a dependency or project symbol so later code can use it by name.
### Line 16

`(blank)`

Blank line used to separate nearby statements.
### Line 18

`def test_missing_learner_returns_fresh_state_in_memory():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 19

`"""Requirement A/J: Missing learner returns clean default LearnerState without storage error."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 20

`repo = InMemoryLearnerRepository()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 21

`state = repo.get("non_existent_learner")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 22

`assert state.user_id == "non_existent_learner"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 23

`assert len(state.evidence_history) == 0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 24

`assert len(state.gap_inferences) == 0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 25

`(blank)`

Blank line used to separate nearby statements.
### Line 27

`def test_successful_get_and_save_in_memory():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 28

`"""Requirement B/D: Persisted state reconstructed correctly."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 29

`repo = InMemoryLearnerRepository()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 30

`state = LearnerState(user_id="u_persisted")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 31

`state.record_attempt("Qubits", 1.0, [])`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 32

`repo.save(state)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 33

`(blank)`

Blank line used to separate nearby statements.
### Line 34

`loaded = repo.get("u_persisted")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 35

`assert loaded.user_id == "u_persisted"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 36

`assert loaded.concept_scores["Qubits"] == 1.0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 37

`assert loaded.attempts["Qubits"] == 1`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 38

`(blank)`

Blank line used to separate nearby statements.
### Line 40

`def test_exists_in_memory():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 41

`"""Requirement F: exists() returns true for present learner, false for missing."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 42

`repo = InMemoryLearnerRepository()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 43

`assert repo.exists("u1") is False`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 44

`repo.save(LearnerState(user_id="u1"))`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 45

`assert repo.exists("u1") is True`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 46

`(blank)`

Blank line used to separate nearby statements.
### Line 48

`def test_repeated_saves_preserve_accumulated_evidence(tmp_path):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 49

`"""Requirement H: Repeated saves preserve history and do not overwrite with empty state."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 50

`repo = JSONFileLearnerRepository(directory=tmp_path)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 51

`state = repo.get("u_repeat")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 52

`(blank)`

Blank line used to separate nearby statements.
### Line 53

`# Step 1: Record first attempt`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 54

`state.evidence_history.append({"attempt": 1, "is_correct": False})`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 55

`state.score_history.setdefault("Qubits", []).append(0.0)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 56

`repo.save(state)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 57

`(blank)`

Blank line used to separate nearby statements.
### Line 58

`# Step 2: Reload and record second attempt`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 59

`loaded_1 = repo.get("u_repeat")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 60

`assert len(loaded_1.evidence_history) == 1`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 61

`loaded_1.evidence_history.append({"attempt": 2, "is_correct": True})`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 62

`loaded_1.score_history.setdefault("Qubits", []).append(1.0)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 63

`repo.save(loaded_1)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 64

`(blank)`

Blank line used to separate nearby statements.
### Line 65

`# Step 3: Final verification`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 66

`loaded_2 = repo.get("u_repeat")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 67

`assert len(loaded_2.evidence_history) == 2`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 68

`assert loaded_2.evidence_history[0]["attempt"] == 1`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 69

`assert loaded_2.evidence_history[1]["attempt"] == 2`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 70

`assert loaded_2.score_history["Qubits"] == [0.0, 1.0]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 71

`(blank)`

Blank line used to separate nearby statements.
### Line 73

`def test_json_file_repository_malformed_data_raises_storage_error(tmp_path):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 74

`"""Requirement C/K: Malformed persisted file raises StorageUnavailableError."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 75

`repo = JSONFileLearnerRepository(directory=tmp_path)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 76

`bad_file = tmp_path / "corrupt_user.json"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 77

`bad_file.write_text("{ this is not valid json", encoding="utf-8")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 78

`(blank)`

Blank line used to separate nearby statements.
### Line 79

`with pytest.raises(StorageUnavailableError):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 80

`repo.get("corrupt_user")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 81

`(blank)`

Blank line used to separate nearby statements.
### Line 83

`def test_json_file_repository_write_failure_raises_storage_error(tmp_path, monkeypatch):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 84

`"""Requirement E: Filesystem write error raises StorageUnavailableError."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 85

`repo = JSONFileLearnerRepository(directory=tmp_path)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 86

`state = LearnerState(user_id="u_write_err")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 87

`(blank)`

Blank line used to separate nearby statements.
### Line 88

`# Force open to fail`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 89

`def fake_open(*args, **kwargs):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 90

`raise PermissionError("Simulated permission denied")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 91

`(blank)`

Blank line used to separate nearby statements.
### Line 92

`monkeypatch.setattr("builtins.open", fake_open)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 93

`(blank)`

Blank line used to separate nearby statements.
### Line 94

`with pytest.raises(StorageUnavailableError):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 95

`repo.save(state)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 96

`(blank)`

Blank line used to separate nearby statements.
### Line 98

`def test_supabase_unconfigured_raises_storage_error():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 99

`"""Requirement C/E: Supabase repository without client raises StorageUnavailableError."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 100

`repo = SupabaseLearnerRepository(client=None)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 101

`(blank)`

Blank line used to separate nearby statements.
### Line 102

`with pytest.raises(StorageUnavailableError):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 103

`repo.get("user_1")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 104

`(blank)`

Blank line used to separate nearby statements.
### Line 105

`with pytest.raises(StorageUnavailableError):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 106

`repo.save(LearnerState(user_id="user_1"))`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 107

`(blank)`

Blank line used to separate nearby statements.
### Line 108

`with pytest.raises(StorageUnavailableError):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 109

`repo.exists("user_1")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 110

`(blank)`

Blank line used to separate nearby statements.
### Line 112

`def test_supabase_mock_successful_get_and_save():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 113

`"""Requirement B/D: Mocked healthy Supabase query and upsert."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 114

`mock_client = MagicMock()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 115

`mock_table = MagicMock()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 116

`mock_client.table.return_value = mock_table`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 117

`(blank)`

Blank line used to separate nearby statements.
### Line 118

`# Mock get()`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 119

`mock_select = MagicMock()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 120

`mock_eq = MagicMock()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 121

`mock_table.select.return_value = mock_select`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 122

`mock_select.eq.return_value = mock_eq`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 123

`(blank)`

Blank line used to separate nearby statements.
### Line 124

`sample_state = LearnerState(user_id="sb_user")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 125

`sample_state.concept_scores["Qubits"] = 1.0`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 126

`(blank)`

Blank line used to separate nearby statements.
### Line 127

`mock_resp = MagicMock()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 128

`mock_resp.data = [{"state_data": sample_state.to_dict()}]`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 129

`mock_eq.execute.return_value = mock_resp`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 130

`(blank)`

Blank line used to separate nearby statements.
### Line 131

`repo = SupabaseLearnerRepository(client=mock_client)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 132

`loaded = repo.get("sb_user")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 133

`(blank)`

Blank line used to separate nearby statements.
### Line 134

`assert loaded.user_id == "sb_user"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 135

`assert loaded.concept_scores["Qubits"] == 1.0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 136

`(blank)`

Blank line used to separate nearby statements.
### Line 137

`# Mock save()`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 138

`mock_upsert = MagicMock()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 139

`mock_table.upsert.return_value = mock_upsert`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 140

`mock_upsert.execute.return_value = MagicMock()`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 141

`(blank)`

Blank line used to separate nearby statements.
### Line 142

`repo.save(loaded)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 143

`mock_table.upsert.assert_called_once()`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 144

`(blank)`

Blank line used to separate nearby statements.
### Line 146

`def test_supabase_mock_database_failure_during_get():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 147

`"""Requirement C: Database query failure raises StorageUnavailableError instead of fresh state."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 148

`mock_client = MagicMock()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 149

`mock_table = MagicMock()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 150

`mock_client.table.return_value = mock_table`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 151

`mock_table.select.side_effect = RuntimeError("PostgreSQL connection timeout")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 152

`(blank)`

Blank line used to separate nearby statements.
### Line 153

`repo = SupabaseLearnerRepository(client=mock_client)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 154

`(blank)`

Blank line used to separate nearby statements.
### Line 155

`with pytest.raises(StorageUnavailableError) as exc_info:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 156

`repo.get("sb_failing_user")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 157

`(blank)`

Blank line used to separate nearby statements.
### Line 158

`assert "Database query failed" in str(exc_info.value)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 159

`(blank)`

Blank line used to separate nearby statements.
### Line 161

`def test_supabase_mock_database_failure_during_save():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 162

`"""Requirement E: Database upsert failure raises StorageUnavailableError."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 163

`mock_client = MagicMock()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 164

`mock_table = MagicMock()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 165

`mock_client.table.return_value = mock_table`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 166

`mock_table.upsert.side_effect = RuntimeError("PostgreSQL disk quota exceeded")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 167

`(blank)`

Blank line used to separate nearby statements.
### Line 168

`repo = SupabaseLearnerRepository(client=mock_client)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 169

`(blank)`

Blank line used to separate nearby statements.
### Line 170

`with pytest.raises(StorageUnavailableError) as exc_info:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 171

`repo.save(LearnerState(user_id="sb_user"))`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 172

`(blank)`

Blank line used to separate nearby statements.
### Line 173

`assert "Database upsert failed" in str(exc_info.value)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 174

`(blank)`

Blank line used to separate nearby statements.
### Line 176

`def test_supabase_mock_database_failure_during_exists():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 177

`"""Requirement G: Database query failure during exists() raises StorageUnavailableError."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 178

`mock_client = MagicMock()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 179

`mock_table = MagicMock()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 180

`mock_client.table.return_value = mock_table`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 181

`mock_table.select.side_effect = RuntimeError("Network partition")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 182

`(blank)`

Blank line used to separate nearby statements.
### Line 183

`repo = SupabaseLearnerRepository(client=mock_client)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 184

`(blank)`

Blank line used to separate nearby statements.
### Line 185

`with pytest.raises(StorageUnavailableError):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 186

`repo.exists("sb_user")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 187

`(blank)`

Blank line used to separate nearby statements.
### Line 189

`def test_api_submission_returns_503_when_get_fails():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 190

`"""Requirement I: API submission returns HTTP 503 if loading learner state fails."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 191

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 192

`(blank)`

Blank line used to separate nearby statements.
### Line 193

`# Repository that fails on get`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 194

`class FailingGetRepo(InMemoryLearnerRepository):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 195

`def get(self, user_id: str) -> LearnerState:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 196

`raise StorageUnavailableError("Database unreachable")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 197

`(blank)`

Blank line used to separate nearby statements.
### Line 198

`set_learner_repository(FailingGetRepo())`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 199

`(blank)`

Blank line used to separate nearby statements.
### Line 200

`res = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 201

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 202

`json={"learner_id": "u_fail_get", "response": "10"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 203

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 204

`assert res.status_code == 503`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 205

`assert "Learner state persistence service is currently unavailable" in res.json()["detail"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 206

`(blank)`

Blank line used to separate nearby statements.
### Line 207

`reset_dependencies()`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 208

`(blank)`

Blank line used to separate nearby statements.
### Line 210

`def test_api_submission_returns_503_when_save_fails():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 211

`"""Requirement I: API submission returns HTTP 503 if saving state fails, never pretending success."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 212

`client = TestClient(app)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 213

`(blank)`

Blank line used to separate nearby statements.
### Line 214

`# Repository that succeeds on get but fails on save`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 215

`class FailingSaveRepo(InMemoryLearnerRepository):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 216

`def save(self, state: LearnerState) -> None:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 217

`raise StorageUnavailableError("Failed to write to database")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 218

`(blank)`

Blank line used to separate nearby statements.
### Line 219

`set_learner_repository(FailingSaveRepo())`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 220

`(blank)`

Blank line used to separate nearby statements.
### Line 221

`res = client.post(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 222

`"/api/activity/act_grover_2q_predict/submit",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 223

`json={"learner_id": "u_fail_save", "response": "10"},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 224

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 225

`assert res.status_code == 503`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 226

`assert "Failed to persist updated learner state" in res.json()["detail"]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 227

`(blank)`

Blank line used to separate nearby statements.
### Line 228

`reset_dependencies()`

Calls a function or method; its arguments carry the data needed for this operation.

## Nearby Files

[tests/adaptive/__init__.py](__init__.py.md), [tests/adaptive/test_activities.py](test_activities.py.md), [tests/adaptive/test_diagnostics.py](test_diagnostics.py.md), [tests/adaptive/test_evidence.py](test_evidence.py.md), [tests/adaptive/test_evidence_progression.py](test_evidence_progression.py.md), [tests/adaptive/test_mastery.py](test_mastery.py.md), [tests/adaptive/test_models.py](test_models.py.md), [tests/adaptive/test_pass4_evidence_trace.py](test_pass4_evidence_trace.py.md)
