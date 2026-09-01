from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from dataclasses import asdict
from pathlib import Path
from typing import Any, Optional

from .models import LearnerState


class PersistenceError(RuntimeError):
    """Base exception raised when a repository storage operation fails."""
    pass


class StorageUnavailableError(PersistenceError):
    """Raised when persistent storage (e.g. database, filesystem) cannot be reached or fails during I/O."""
    pass


class LearnerRepository(ABC):
    """
    Abstract repository boundary for learner state persistence.
    Distinguishes clean missing-learner state from storage/database failures.
    """

    @abstractmethod
    def get(self, user_id: str) -> LearnerState:
        """
        Retrieve learner state.
        Returns a fresh default LearnerState(user_id=user_id) if learner does not exist in storage.
        Raises StorageUnavailableError if storage is unreachable or query fails.
        """
        raise NotImplementedError

    @abstractmethod
    def save(self, state: LearnerState) -> None:
        """
        Persist updated learner state.
        Raises StorageUnavailableError if storage is unreachable or write fails.
        """
        raise NotImplementedError

    @abstractmethod
    def exists(self, user_id: str) -> bool:
        """
        Check if learner state exists in storage.
        Returns True if record exists, False if missing.
        Raises StorageUnavailableError if storage is unreachable or query fails.
        """
        raise NotImplementedError


class InMemoryLearnerRepository(LearnerRepository):
    """
    In-memory learner state store for unit testing, CI, and stateless execution.
    """

    def __init__(self) -> None:
        self._store: dict[str, LearnerState] = {}

    def get(self, user_id: str) -> LearnerState:
        if user_id in self._store:
            return self._store[user_id]
        return LearnerState(user_id=user_id)

    def save(self, state: LearnerState) -> None:
        self._store[state.user_id] = state

    def exists(self, user_id: str) -> bool:
        return user_id in self._store

    def clear(self) -> None:
        self._store.clear()


class JSONFileLearnerRepository(LearnerRepository):
    """
    File-based JSON persistence in a local directory (e.g. ./learner_data/).
    Maintains backward compatibility with original M2 JSONStore interface.
    """

    def __init__(self, directory: str | Path = "learner_data") -> None:
        self.directory = Path(directory)
        try:
            self.directory.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            raise StorageUnavailableError(f"Failed to initialize directory '{self.directory}': {exc}") from exc

    def _path(self, user_id: str) -> Path:
        return self.directory / f"{user_id}.json"

    def get(self, user_id: str) -> LearnerState:
        path = self._path(user_id)
        if path.exists():
            try:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                return LearnerState.from_dict(data)
            except Exception as exc:
                raise StorageUnavailableError(f"Failed to read learner state file for '{user_id}': {exc}") from exc
        return LearnerState(user_id=user_id)

    def load(self, user_id: str) -> LearnerState:
        """Backward-compatible alias for get()."""
        return self.get(user_id)

    def save(self, state: LearnerState) -> None:
        path = self._path(state.user_id)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(asdict(state), f, indent=2)
        except Exception as exc:
            raise StorageUnavailableError(f"Failed to write learner state file for '{state.user_id}': {exc}") from exc

    def exists(self, user_id: str) -> bool:
        try:
            return self._path(user_id).exists()
        except Exception as exc:
            raise StorageUnavailableError(f"Failed to check existence for '{user_id}': {exc}") from exc


class SupabaseLearnerRepository(LearnerRepository):
    """
    Supabase/PostgreSQL repository adapter.
    Persists LearnerState domain models into the 'learner_states' table.
    Uses supabase-py client when credentials are provided in the environment.
    Strictly differentiates between a non-existent learner record and database/network errors.
    """

    def __init__(
        self,
        client: Any = None,
        url: Optional[str] = None,
        key: Optional[str] = None,
        table_name: str = "learner_states",
    ) -> None:
        self.table_name = table_name
        self.client = client
        if self.client is None:
            supabase_url = url or os.getenv("SUPABASE_URL")
            supabase_key = key or os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            if supabase_url and supabase_key:
                try:
                    from supabase import create_client
                    self.client = create_client(supabase_url, supabase_key)
                except Exception as exc:
                    raise StorageUnavailableError(f"Failed to initialize Supabase client: {exc}") from exc

    def get(self, user_id: str) -> LearnerState:
        if self.client is None:
            raise StorageUnavailableError("Supabase client is not configured (missing credentials or client instance)")

        try:
            response = (
                self.client.table(self.table_name)
                .select("state_data")
                .eq("user_id", user_id)
                .execute()
            )
        except Exception as exc:
            raise StorageUnavailableError(f"Database query failed for learner '{user_id}': {exc}") from exc

        if response and getattr(response, "data", None) and len(response.data) > 0:
            state_data = response.data[0].get("state_data", {})
            try:
                return LearnerState.from_dict(state_data)
            except Exception as exc:
                raise StorageUnavailableError(f"Malformed persisted learner state for '{user_id}': {exc}") from exc

        # Clean missing learner in healthy database
        return LearnerState(user_id=user_id)

    def save(self, state: LearnerState) -> None:
        if self.client is None:
            raise StorageUnavailableError("Supabase client is not configured (missing credentials or client instance)")

        try:
            payload = {
                "user_id": state.user_id,
                "state_data": state.to_dict(),
            }
            self.client.table(self.table_name).upsert(payload).execute()
        except Exception as exc:
            raise StorageUnavailableError(f"Database upsert failed for learner '{state.user_id}': {exc}") from exc

    def exists(self, user_id: str) -> bool:
        if self.client is None:
            raise StorageUnavailableError("Supabase client is not configured (missing credentials or client instance)")

        try:
            response = (
                self.client.table(self.table_name)
                .select("user_id")
                .eq("user_id", user_id)
                .execute()
            )
            return bool(response and getattr(response, "data", None) and len(response.data) > 0)
        except Exception as exc:
            raise StorageUnavailableError(f"Database existence check failed for '{user_id}': {exc}") from exc


# Backward-compatible alias matching original M2 name
JSONStore = JSONFileLearnerRepository
