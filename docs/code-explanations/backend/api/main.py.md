# Explanation: `backend/api/main.py`

## Purpose

This page explains the meaningful behavior in `backend/api/main.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
from __future__ import annotations

from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routes import activities, ai, health

app = FastAPI(
    title="Q-BIT API",
    version="1.0.0",
    description="Q-BIT.140 AI-Based Interactive Quantum Algorithm Learning Platform Gateway",
)

# Enable CORS for local development of any frontend client
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
        "*",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Mount API routers (always take precedence)
app.include_router(health.router, prefix="/api")
app.include_router(activities.router, prefix="/api")
app.include_router(ai.router, prefix="/api")

# Top-level health check probe
app.include_router(health.router)

# Mount static frontend directory optionally if present
frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")

```

## Line Notes

### Line 1

`from __future__ import annotations`

Imports a dependency or project symbol so later code can use it by name.
### Line 2

`(blank)`

Blank line used to separate nearby statements.
### Line 3

`from pathlib import Path`

Imports a dependency or project symbol so later code can use it by name.
### Line 4

`from fastapi import FastAPI`

Imports a dependency or project symbol so later code can use it by name.
### Line 5

`from fastapi.middleware.cors import CORSMiddleware`

Imports a dependency or project symbol so later code can use it by name.
### Line 6

`from fastapi.staticfiles import StaticFiles`

Imports a dependency or project symbol so later code can use it by name.
### Line 7

`(blank)`

Blank line used to separate nearby statements.
### Line 8

`from .routes import activities, ai, health`

Imports a dependency or project symbol so later code can use it by name.
### Line 9

`(blank)`

Blank line used to separate nearby statements.
### Line 10

`app = FastAPI(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 11

`title="Q-BIT API",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 12

`version="1.0.0",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 13

`description="Q-BIT.140 AI-Based Interactive Quantum Algorithm Learning Platform Gateway",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 14

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 15

`(blank)`

Blank line used to separate nearby statements.
### Line 16

`# Enable CORS for local development of any frontend client`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 17

`app.add_middleware(`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 18

`CORSMiddleware,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 19

`allow_origins=[`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 20

`"http://localhost:3000",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 21

`"http://localhost:5173",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 22

`"http://localhost:8000",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 23

`"http://127.0.0.1:3000",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 24

`"http://127.0.0.1:5173",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 25

`"http://127.0.0.1:8000",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 26

`"*",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 27

`],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 28

`allow_credentials=False,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 29

`allow_methods=["GET", "POST", "OPTIONS"],`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 30

`allow_headers=["*"],`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 31

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 32

`(blank)`

Blank line used to separate nearby statements.
### Line 33

`# Mount API routers (always take precedence)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 34

`app.include_router(health.router, prefix="/api")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 35

`app.include_router(activities.router, prefix="/api")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 36

`app.include_router(ai.router, prefix="/api")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 37

`(blank)`

Blank line used to separate nearby statements.
### Line 38

`# Top-level health check probe`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 39

`app.include_router(health.router)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 40

`(blank)`

Blank line used to separate nearby statements.
### Line 41

`# Mount static frontend directory optionally if present`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 42

`frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 43

`if frontend_dir.exists():`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 44

`app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")`

Calls a function or method; its arguments carry the data needed for this operation.

## Nearby Files

[backend/api/__init__.py](__init__.py.md), [backend/api/dependencies.py](dependencies.py.md), [backend/api/schemas.py](schemas.py.md)
