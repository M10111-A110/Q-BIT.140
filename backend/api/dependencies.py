from __future__ import annotations

import os
from typing import Optional

from backend.adaptive import (
    InMemoryLearnerRepository,
    LearnerModel,
    LearnerRepository,
    SupabaseLearnerRepository,
)
from backend.ai import LLMProvider, MockLLMProvider, get_default_provider


def _create_default_repository() -> LearnerRepository:
    """Factory creating Supabase repository if credentials exist, else in-memory store."""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if supabase_url and supabase_key:
        try:
            return SupabaseLearnerRepository(url=supabase_url, key=supabase_key)
        except Exception:
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
