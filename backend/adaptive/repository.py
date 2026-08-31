from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from dataclasses import asdict
from pathlib import Path
from typing import Optional

from .models import LearnerState


class LearnerRepository(ABC):
    """Abstract repository boundary for learner state persistence."""

    @abstractmethod
    def get(self, user_id: str) -> LearnerState:
        """Retrieve learner state or return a fresh default instance."""
        raise NotImplementedError

    @abstractmethod
    def save(self, state: LearnerState) -> None:
        """Persist updated learner state."""
        raise NotImplementedError

    @abstractmethod
    def exists(self, user_id: str) -> bool:
        """Check if learner state exists in storage."""
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
        self.directory.mkdir(parents=True, exist_ok=True)

    def _path(self, user_id: str) -> Path:
        return self.directory / f"{user_id}.json"

    def get(self, user_id: str) -> LearnerState:
        path = self._path(user_id)
        if path.exists():
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            return LearnerState(**data)
        return LearnerState(user_id=user_id)

    def load(self, user_id: str) -> LearnerState:
        """Backward-compatible alias for get()."""
        return self.get(user_id)

    def save(self, state: LearnerState) -> None:
        path = self._path(state.user_id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(state), f, indent=2)

    def exists(self, user_id: str) -> bool:
        return self._path(user_id).exists()


# Backward-compatible alias matching original M2 name
JSONStore = JSONFileLearnerRepository
