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
