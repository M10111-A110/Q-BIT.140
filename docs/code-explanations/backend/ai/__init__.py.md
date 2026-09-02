# Explanation: `backend/ai/__init__.py`

## Purpose

This page explains the meaningful behavior in `backend/ai/__init__.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
from .prompts import SYSTEM_PROMPT, build_ask_prompt, build_experiment_explanation_prompt
from .providers import (
    GroqLLMProvider,
    LLMProvider,
    MockLLMProvider,
    get_default_provider,
)
from .retrieval import find_relevant_knowledge
from .service import ask_question, explain_experiment

__all__ = [
    "GroqLLMProvider",
    "LLMProvider",
    "MockLLMProvider",
    "SYSTEM_PROMPT",
    "ask_question",
    "build_ask_prompt",
    "build_experiment_explanation_prompt",
    "explain_experiment",
    "find_relevant_knowledge",
    "get_default_provider",
]

```

## Line Notes

### Line 1

`from .prompts import SYSTEM_PROMPT, build_ask_prompt, build_experiment_explanation_prompt`

Imports a dependency or project symbol so later code can use it by name.
### Line 2

`from .providers import (`

Imports a dependency or project symbol so later code can use it by name.
### Line 3

`GroqLLMProvider,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 4

`LLMProvider,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 5

`MockLLMProvider,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 6

`get_default_provider,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 7

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 8

`from .retrieval import find_relevant_knowledge`

Imports a dependency or project symbol so later code can use it by name.
### Line 9

`from .service import ask_question, explain_experiment`

Imports a dependency or project symbol so later code can use it by name.
### Line 10

`(blank)`

Blank line used to separate nearby statements.
### Line 11

`__all__ = [`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 12

`"GroqLLMProvider",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 13

`"LLMProvider",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 14

`"MockLLMProvider",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 15

`"SYSTEM_PROMPT",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 16

`"ask_question",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 17

`"build_ask_prompt",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 18

`"build_experiment_explanation_prompt",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 19

`"explain_experiment",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 20

`"find_relevant_knowledge",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 21

`"get_default_provider",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 22

`]`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.

## Nearby Files

[backend/ai/prompts.py](prompts.py.md), [backend/ai/providers.py](providers.py.md), [backend/ai/retrieval.py](retrieval.py.md), [backend/ai/service.py](service.py.md)
