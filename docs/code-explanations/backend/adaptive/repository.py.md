# Explanation: `backend/adaptive/repository.py`

## Purpose

This page explains the meaningful behavior in `backend/adaptive/repository.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
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

```

## Line Notes

### Line 1

`from __future__ import annotations`

Imports a dependency or project symbol so later code can use it by name.
### Line 2

`(blank)`

Blank line used to separate nearby statements.
### Line 3

`import json`

Imports a dependency or project symbol so later code can use it by name.
### Line 4

`import os`

Imports a dependency or project symbol so later code can use it by name.
### Line 5

`from abc import ABC, abstractmethod`

Imports a dependency or project symbol so later code can use it by name.
### Line 6

`from dataclasses import asdict`

Imports a dependency or project symbol so later code can use it by name.
### Line 7

`from pathlib import Path`

Imports a dependency or project symbol so later code can use it by name.
### Line 8

`from typing import Any, Optional`

Imports a dependency or project symbol so later code can use it by name.
### Line 9

`(blank)`

Blank line used to separate nearby statements.
### Line 10

`from .models import LearnerState`

Imports a dependency or project symbol so later code can use it by name.
### Line 11

`(blank)`

Blank line used to separate nearby statements.
### Line 13

`class PersistenceError(RuntimeError):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 14

`"""Base exception raised when a repository storage operation fails."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 15

`pass`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 16

`(blank)`

Blank line used to separate nearby statements.
### Line 18

`class StorageUnavailableError(PersistenceError):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 19

`"""Raised when persistent storage (e.g. database, filesystem) cannot be reached or fails during I/O."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 20

`pass`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 21

`(blank)`

Blank line used to separate nearby statements.
### Line 23

`class LearnerRepository(ABC):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 24

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 25

`Abstract repository boundary for learner state persistence.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 26

`Distinguishes clean missing-learner state from storage/database failures.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 27

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 28

`(blank)`

Blank line used to separate nearby statements.
### Line 29

`@abstractmethod`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 30

`def get(self, user_id: str) -> LearnerState:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 31

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 32

`Retrieve learner state.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 33

`Returns a fresh default LearnerState(user_id=user_id) if learner does not exist in storage.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 34

`Raises StorageUnavailableError if storage is unreachable or query fails.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 35

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 36

`raise NotImplementedError`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 37

`(blank)`

Blank line used to separate nearby statements.
### Line 38

`@abstractmethod`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 39

`def save(self, state: LearnerState) -> None:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 40

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 41

`Persist updated learner state.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 42

`Raises StorageUnavailableError if storage is unreachable or write fails.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 43

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 44

`raise NotImplementedError`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 45

`(blank)`

Blank line used to separate nearby statements.
### Line 46

`@abstractmethod`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 47

`def exists(self, user_id: str) -> bool:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 48

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 49

`Check if learner state exists in storage.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 50

`Returns True if record exists, False if missing.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 51

`Raises StorageUnavailableError if storage is unreachable or query fails.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 52

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 53

`raise NotImplementedError`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 54

`(blank)`

Blank line used to separate nearby statements.
### Line 56

`class InMemoryLearnerRepository(LearnerRepository):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 57

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 58

`In-memory learner state store for unit testing, CI, and stateless execution.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 59

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 60

`(blank)`

Blank line used to separate nearby statements.
### Line 61

`def __init__(self) -> None:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 62

`self._store: dict[str, LearnerState] = {}`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 63

`(blank)`

Blank line used to separate nearby statements.
### Line 64

`def get(self, user_id: str) -> LearnerState:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 65

`if user_id in self._store:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 66

`return self._store[user_id]`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 67

`return LearnerState(user_id=user_id)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 68

`(blank)`

Blank line used to separate nearby statements.
### Line 69

`def save(self, state: LearnerState) -> None:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 70

`self._store[state.user_id] = state`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 71

`(blank)`

Blank line used to separate nearby statements.
### Line 72

`def exists(self, user_id: str) -> bool:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 73

`return user_id in self._store`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 74

`(blank)`

Blank line used to separate nearby statements.
### Line 75

`def clear(self) -> None:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 76

`self._store.clear()`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 77

`(blank)`

Blank line used to separate nearby statements.
### Line 79

`class JSONFileLearnerRepository(LearnerRepository):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 80

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 81

`File-based JSON persistence in a local directory (e.g. ./learner_data/).`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 82

`Maintains backward compatibility with original M2 JSONStore interface.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 83

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 84

`(blank)`

Blank line used to separate nearby statements.
### Line 85

`def __init__(self, directory: str | Path = "learner_data") -> None:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 86

`self.directory = Path(directory)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 87

`try:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 88

`self.directory.mkdir(parents=True, exist_ok=True)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 89

`except Exception as exc:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 90

`raise StorageUnavailableError(f"Failed to initialize directory '{self.directory}': {exc}") from exc`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 91

`(blank)`

Blank line used to separate nearby statements.
### Line 92

`def _path(self, user_id: str) -> Path:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 93

`return self.directory / f"{user_id}.json"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 94

`(blank)`

Blank line used to separate nearby statements.
### Line 95

`def get(self, user_id: str) -> LearnerState:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 96

`path = self._path(user_id)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 97

`if path.exists():`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 98

`try:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 99

`with open(path, encoding="utf-8") as f:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 100

`data = json.load(f)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 101

`return LearnerState.from_dict(data)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 102

`except Exception as exc:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 103

`raise StorageUnavailableError(f"Failed to read learner state file for '{user_id}': {exc}") from exc`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 104

`return LearnerState(user_id=user_id)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 105

`(blank)`

Blank line used to separate nearby statements.
### Line 106

`def load(self, user_id: str) -> LearnerState:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 107

`"""Backward-compatible alias for get()."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 108

`return self.get(user_id)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 109

`(blank)`

Blank line used to separate nearby statements.
### Line 110

`def save(self, state: LearnerState) -> None:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 111

`path = self._path(state.user_id)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 112

`try:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 113

`with open(path, "w", encoding="utf-8") as f:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 114

`json.dump(asdict(state), f, indent=2)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 115

`except Exception as exc:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 116

`raise StorageUnavailableError(f"Failed to write learner state file for '{state.user_id}': {exc}") from exc`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 117

`(blank)`

Blank line used to separate nearby statements.
### Line 118

`def exists(self, user_id: str) -> bool:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 119

`try:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 120

`return self._path(user_id).exists()`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 121

`except Exception as exc:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 122

`raise StorageUnavailableError(f"Failed to check existence for '{user_id}': {exc}") from exc`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 123

`(blank)`

Blank line used to separate nearby statements.
### Line 125

`class SupabaseLearnerRepository(LearnerRepository):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 126

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 127

`Supabase/PostgreSQL repository adapter.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 128

`Persists LearnerState domain models into the 'learner_states' table.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 129

`Uses supabase-py client when credentials are provided in the environment.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 130

`Strictly differentiates between a non-existent learner record and database/network errors.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 131

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 132

`(blank)`

Blank line used to separate nearby statements.
### Line 133

`def __init__(`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 134

`self,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 135

`client: Any = None,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 136

`url: Optional[str] = None,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 137

`key: Optional[str] = None,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 138

`table_name: str = "learner_states",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 139

`) -> None:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 140

`self.table_name = table_name`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 141

`self.client = client`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 142

`if self.client is None:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 143

`supabase_url = url or os.getenv("SUPABASE_URL")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 144

`supabase_key = key or os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 145

`if supabase_url and supabase_key:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 146

`try:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 147

`from supabase import create_client`

Imports a dependency or project symbol so later code can use it by name.
### Line 148

`self.client = create_client(supabase_url, supabase_key)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 149

`except Exception as exc:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 150

`raise StorageUnavailableError(f"Failed to initialize Supabase client: {exc}") from exc`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 151

`(blank)`

Blank line used to separate nearby statements.
### Line 152

`def get(self, user_id: str) -> LearnerState:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 153

`if self.client is None:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 154

`raise StorageUnavailableError("Supabase client is not configured (missing credentials or client instance)")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 155

`(blank)`

Blank line used to separate nearby statements.
### Line 156

`try:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 157

`response = (`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 158

`self.client.table(self.table_name)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 159

`.select("state_data")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 160

`.eq("user_id", user_id)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 161

`.execute()`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 162

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 163

`except Exception as exc:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 164

`raise StorageUnavailableError(f"Database query failed for learner '{user_id}': {exc}") from exc`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 165

`(blank)`

Blank line used to separate nearby statements.
### Line 166

`if response and getattr(response, "data", None) and len(response.data) > 0:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 167

`state_data = response.data[0].get("state_data", {})`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 168

`try:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 169

`return LearnerState.from_dict(state_data)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 170

`except Exception as exc:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 171

`raise StorageUnavailableError(f"Malformed persisted learner state for '{user_id}': {exc}") from exc`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 172

`(blank)`

Blank line used to separate nearby statements.
### Line 173

`# Clean missing learner in healthy database`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 174

`return LearnerState(user_id=user_id)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 175

`(blank)`

Blank line used to separate nearby statements.
### Line 176

`def save(self, state: LearnerState) -> None:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 177

`if self.client is None:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 178

`raise StorageUnavailableError("Supabase client is not configured (missing credentials or client instance)")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 179

`(blank)`

Blank line used to separate nearby statements.
### Line 180

`try:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 181

`payload = {`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 182

`"user_id": state.user_id,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 183

`"state_data": state.to_dict(),`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 184

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 185

`self.client.table(self.table_name).upsert(payload).execute()`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 186

`except Exception as exc:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 187

`raise StorageUnavailableError(f"Database upsert failed for learner '{state.user_id}': {exc}") from exc`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 188

`(blank)`

Blank line used to separate nearby statements.
### Line 189

`def exists(self, user_id: str) -> bool:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 190

`if self.client is None:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 191

`raise StorageUnavailableError("Supabase client is not configured (missing credentials or client instance)")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 192

`(blank)`

Blank line used to separate nearby statements.
### Line 193

`try:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 194

`response = (`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 195

`self.client.table(self.table_name)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 196

`.select("user_id")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 197

`.eq("user_id", user_id)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 198

`.execute()`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 199

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 200

`return bool(response and getattr(response, "data", None) and len(response.data) > 0)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 201

`except Exception as exc:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 202

`raise StorageUnavailableError(f"Database existence check failed for '{user_id}': {exc}") from exc`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 203

`(blank)`

Blank line used to separate nearby statements.
### Line 205

`# Backward-compatible alias matching original M2 name`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 206

`JSONStore = JSONFileLearnerRepository`

Creates or updates state used by later statements; the expression on the right supplies the value.

## Nearby Files

[backend/adaptive/__init__.py](__init__.py.md), [backend/adaptive/activities.py](activities.py.md), [backend/adaptive/concepts.py](concepts.py.md), [backend/adaptive/diagnostics.py](diagnostics.py.md), [backend/adaptive/engine.py](engine.py.md), [backend/adaptive/evidence.py](evidence.py.md), [backend/adaptive/models.py](models.py.md)
