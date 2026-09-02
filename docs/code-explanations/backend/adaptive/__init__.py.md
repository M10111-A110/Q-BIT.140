# Explanation: `backend/adaptive/__init__.py`

## Purpose

This page explains the meaningful behavior in `backend/adaptive/__init__.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
from .activities import (
    MVP_ACTIVITIES,
    Activity,
    get_activities_for_concept,
    get_activity,
    list_activities,
)
from .concepts import (
    CONCEPT_GRAPH,
    Concept,
    get_concept,
    get_concept_display_name,
    get_concept_graph,
    resolve_concept_id,
)
from .diagnostics import Diagnostic, load_questions
from .engine import (
    ERROR_STREAK_LIMIT,
    MASTERY_THRESHOLD,
    LearnerModel,
)
from .evidence import (
    GapInference,
    LearnerEvidence,
    evaluate_conceptual_response,
    evaluate_quantum_prediction,
)
from .models import (
    AdaptiveRecommendation,
    LearnerContext,
    LearnerState,
    Question,
    QuizResult,
    QuizSubmission,
)
from .repository import (
    InMemoryLearnerRepository,
    JSONFileLearnerRepository,
    JSONStore,
    LearnerRepository,
    PersistenceError,
    StorageUnavailableError,
    SupabaseLearnerRepository,
)

__all__ = [
    "Activity",
    "AdaptiveRecommendation",
    "CONCEPT_GRAPH",
    "Concept",
    "Diagnostic",
    "ERROR_STREAK_LIMIT",
    "GapInference",
    "InMemoryLearnerRepository",
    "JSONFileLearnerRepository",
    "JSONStore",
    "LearnerContext",
    "LearnerEvidence",
    "LearnerModel",
    "LearnerRepository",
    "LearnerState",
    "MASTERY_THRESHOLD",
    "MVP_ACTIVITIES",
    "PersistenceError",
    "Question",
    "QuizResult",
    "QuizSubmission",
    "StorageUnavailableError",
    "SupabaseLearnerRepository",
    "evaluate_conceptual_response",
    "evaluate_quantum_prediction",
    "get_activities_for_concept",
    "get_activity",
    "get_concept",
    "get_concept_display_name",
    "get_concept_graph",
    "list_activities",
    "load_questions",
    "resolve_concept_id",
]

```

## Line Notes

### Line 1

`from .activities import (`

Imports a dependency or project symbol so later code can use it by name.
### Line 2

`MVP_ACTIVITIES,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 3

`Activity,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 4

`get_activities_for_concept,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 5

`get_activity,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 6

`list_activities,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 7

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 8

`from .concepts import (`

Imports a dependency or project symbol so later code can use it by name.
### Line 9

`CONCEPT_GRAPH,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 10

`Concept,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 11

`get_concept,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 12

`get_concept_display_name,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 13

`get_concept_graph,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 14

`resolve_concept_id,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 15

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 16

`from .diagnostics import Diagnostic, load_questions`

Imports a dependency or project symbol so later code can use it by name.
### Line 17

`from .engine import (`

Imports a dependency or project symbol so later code can use it by name.
### Line 18

`ERROR_STREAK_LIMIT,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 19

`MASTERY_THRESHOLD,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 20

`LearnerModel,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 21

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 22

`from .evidence import (`

Imports a dependency or project symbol so later code can use it by name.
### Line 23

`GapInference,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 24

`LearnerEvidence,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 25

`evaluate_conceptual_response,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 26

`evaluate_quantum_prediction,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 27

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 28

`from .models import (`

Imports a dependency or project symbol so later code can use it by name.
### Line 29

`AdaptiveRecommendation,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 30

`LearnerContext,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 31

`LearnerState,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 32

`Question,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 33

`QuizResult,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 34

`QuizSubmission,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 35

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 36

`from .repository import (`

Imports a dependency or project symbol so later code can use it by name.
### Line 37

`InMemoryLearnerRepository,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 38

`JSONFileLearnerRepository,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 39

`JSONStore,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 40

`LearnerRepository,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 41

`PersistenceError,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 42

`StorageUnavailableError,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 43

`SupabaseLearnerRepository,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 44

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 45

`(blank)`

Blank line used to separate nearby statements.
### Line 46

`__all__ = [`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 47

`"Activity",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 48

`"AdaptiveRecommendation",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 49

`"CONCEPT_GRAPH",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 50

`"Concept",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 51

`"Diagnostic",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 52

`"ERROR_STREAK_LIMIT",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 53

`"GapInference",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 54

`"InMemoryLearnerRepository",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 55

`"JSONFileLearnerRepository",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 56

`"JSONStore",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 57

`"LearnerContext",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 58

`"LearnerEvidence",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 59

`"LearnerModel",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 60

`"LearnerRepository",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 61

`"LearnerState",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 62

`"MASTERY_THRESHOLD",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 63

`"MVP_ACTIVITIES",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 64

`"PersistenceError",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 65

`"Question",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 66

`"QuizResult",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 67

`"QuizSubmission",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 68

`"StorageUnavailableError",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 69

`"SupabaseLearnerRepository",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 70

`"evaluate_conceptual_response",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 71

`"evaluate_quantum_prediction",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 72

`"get_activities_for_concept",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 73

`"get_activity",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 74

`"get_concept",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 75

`"get_concept_display_name",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 76

`"get_concept_graph",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 77

`"list_activities",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 78

`"load_questions",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 79

`"resolve_concept_id",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 80

`]`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.

## Nearby Files

[backend/adaptive/activities.py](activities.py.md), [backend/adaptive/concepts.py](concepts.py.md), [backend/adaptive/diagnostics.py](diagnostics.py.md), [backend/adaptive/engine.py](engine.py.md), [backend/adaptive/evidence.py](evidence.py.md), [backend/adaptive/models.py](models.py.md), [backend/adaptive/repository.py](repository.py.md)
