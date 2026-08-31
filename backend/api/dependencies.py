from __future__ import annotations

from backend.adaptive import (
    InMemoryLearnerRepository,
    LearnerModel,
    LearnerRepository,
)
from backend.ai import LLMProvider, MockLLMProvider, get_default_provider

# Global singleton instances for in-memory MVP lifecycle
_GLOBAL_REPOSITORY: LearnerRepository = InMemoryLearnerRepository()
_GLOBAL_MODEL: LearnerModel = LearnerModel()
_GLOBAL_LLM_PROVIDER: LLMProvider = get_default_provider()


def get_learner_repository() -> LearnerRepository:
    """Dependency provider for learner state persistence repository."""
    return _GLOBAL_REPOSITORY


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
