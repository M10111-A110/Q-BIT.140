# Explanation: `backend/api/dependencies.py`

## Purpose

This page explains the meaningful behavior in `backend/api/dependencies.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
from __future__ import annotations

import logging
import os
from typing import Optional

from backend.adaptive import (
    InMemoryLearnerRepository,
    LearnerModel,
    LearnerRepository,
    SupabaseLearnerRepository,
)
from backend.ai import LLMProvider, MockLLMProvider, get_default_provider

logger = logging.getLogger(__name__)


def _create_default_repository() -> LearnerRepository:
    """Factory creating Supabase repository if credentials exist, else in-memory store."""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if supabase_url and supabase_key:
        try:
            return SupabaseLearnerRepository(url=supabase_url, key=supabase_key)
        except Exception as exc:
            logger.warning("Failed to initialize SupabaseLearnerRepository; falling back to InMemoryLearnerRepository: %s", exc)
            return InMemoryLearnerRepository()
    return InMemoryLearnerRepository()


# Global singleton instances for API lifecycle
_GLOBAL_REPOSITORY: LearnerRepository = _create_default_repository()
_GLOBAL_MODEL: LearnerModel = LearnerModel()
_GLOBAL_LLM_PROVIDER: LLMProvider = get_default_provider()


def get_learner_repository() -> LearnerRepository:
    """Dependency provider for learner state persistence repository."""
    return _GLOBAL_REPOSITORY


def set_learner_repository(repo: LearnerRepository) -> None:
    """Explicitly override learner repository (useful for testing or switching store)."""
    global _GLOBAL_REPOSITORY
    _GLOBAL_REPOSITORY = repo


def get_learner_model() -> LearnerModel:
    """Dependency provider for the M2 adaptive learner model engine."""
    return _GLOBAL_MODEL


def get_llm_provider() -> LLMProvider:
    """Dependency provider for LLM explanation generation."""
    return _GLOBAL_LLM_PROVIDER


def set_llm_provider(provider: LLMProvider) -> None:
    """Explicitly override LLM provider (useful for deterministic tests)."""
    global _GLOBAL_LLM_PROVIDER
    _GLOBAL_LLM_PROVIDER = provider


def reset_dependencies() -> None:
    """Helper to reset in-memory state during isolated test execution."""
    global _GLOBAL_REPOSITORY, _GLOBAL_MODEL, _GLOBAL_LLM_PROVIDER
    _GLOBAL_REPOSITORY = InMemoryLearnerRepository()
    _GLOBAL_MODEL = LearnerModel()
    _GLOBAL_LLM_PROVIDER = get_default_provider()

```

## Line Notes

### Line 1

`from __future__ import annotations`

Imports a dependency or project symbol so later code can use it by name.
### Line 2

`(blank)`

Blank line used to separate nearby statements.
### Line 3

`import logging`

Imports a dependency or project symbol so later code can use it by name.
### Line 4

`import os`

Imports a dependency or project symbol so later code can use it by name.
### Line 5

`from typing import Optional`

Imports a dependency or project symbol so later code can use it by name.
### Line 6

`(blank)`

Blank line used to separate nearby statements.
### Line 7

`from backend.adaptive import (`

Imports a dependency or project symbol so later code can use it by name.
### Line 8

`InMemoryLearnerRepository,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 9

`LearnerModel,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 10

`LearnerRepository,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 11

`SupabaseLearnerRepository,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 12

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 13

`from backend.ai import LLMProvider, MockLLMProvider, get_default_provider`

Imports a dependency or project symbol so later code can use it by name.
### Line 14

`(blank)`

Blank line used to separate nearby statements.
### Line 15

`logger = logging.getLogger(__name__)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 16

`(blank)`

Blank line used to separate nearby statements.
### Line 18

`def _create_default_repository() -> LearnerRepository:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 19

`"""Factory creating Supabase repository if credentials exist, else in-memory store."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 20

`supabase_url = os.getenv("SUPABASE_URL")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 21

`supabase_key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 22

`if supabase_url and supabase_key:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 23

`try:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 24

`return SupabaseLearnerRepository(url=supabase_url, key=supabase_key)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 25

`except Exception as exc:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 26

`logger.warning("Failed to initialize SupabaseLearnerRepository; falling back to InMemoryLearnerRepository: %s", exc)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 27

`return InMemoryLearnerRepository()`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 28

`return InMemoryLearnerRepository()`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 29

`(blank)`

Blank line used to separate nearby statements.
### Line 31

`# Global singleton instances for API lifecycle`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 32

`_GLOBAL_REPOSITORY: LearnerRepository = _create_default_repository()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 33

`_GLOBAL_MODEL: LearnerModel = LearnerModel()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 34

`_GLOBAL_LLM_PROVIDER: LLMProvider = get_default_provider()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 35

`(blank)`

Blank line used to separate nearby statements.
### Line 37

`def get_learner_repository() -> LearnerRepository:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 38

`"""Dependency provider for learner state persistence repository."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 39

`return _GLOBAL_REPOSITORY`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 40

`(blank)`

Blank line used to separate nearby statements.
### Line 42

`def set_learner_repository(repo: LearnerRepository) -> None:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 43

`"""Explicitly override learner repository (useful for testing or switching store)."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 44

`global _GLOBAL_REPOSITORY`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 45

`_GLOBAL_REPOSITORY = repo`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 46

`(blank)`

Blank line used to separate nearby statements.
### Line 48

`def get_learner_model() -> LearnerModel:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 49

`"""Dependency provider for the M2 adaptive learner model engine."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 50

`return _GLOBAL_MODEL`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 51

`(blank)`

Blank line used to separate nearby statements.
### Line 53

`def get_llm_provider() -> LLMProvider:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 54

`"""Dependency provider for LLM explanation generation."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 55

`return _GLOBAL_LLM_PROVIDER`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 56

`(blank)`

Blank line used to separate nearby statements.
### Line 58

`def set_llm_provider(provider: LLMProvider) -> None:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 59

`"""Explicitly override LLM provider (useful for deterministic tests)."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 60

`global _GLOBAL_LLM_PROVIDER`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 61

`_GLOBAL_LLM_PROVIDER = provider`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 62

`(blank)`

Blank line used to separate nearby statements.
### Line 64

`def reset_dependencies() -> None:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 65

`"""Helper to reset in-memory state during isolated test execution."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 66

`global _GLOBAL_REPOSITORY, _GLOBAL_MODEL, _GLOBAL_LLM_PROVIDER`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 67

`_GLOBAL_REPOSITORY = InMemoryLearnerRepository()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 68

`_GLOBAL_MODEL = LearnerModel()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 69

`_GLOBAL_LLM_PROVIDER = get_default_provider()`

Creates or updates state used by later statements; the expression on the right supplies the value.

## Nearby Files

[backend/api/__init__.py](__init__.py.md), [backend/api/main.py](main.py.md), [backend/api/schemas.py](schemas.py.md)
