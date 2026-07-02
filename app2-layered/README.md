# TaskFlow v2 — Layered Architecture

**SE-II Session 3 demo app.**

Same features as v1. Different inside. Every concern in its own layer.

## Run it

```bash
pip install flask
python app.py
```

Open http://localhost:5000

## File map

| File | Layer | Job |
|------|-------|-----|
| `app.py` | Presentation | HTTP routes only — receives request, calls service, returns response |
| `services.py` | Business Logic | All decisions — add, complete, delete, filter, sort, stats |
| `repository.py` | Data | All storage — load and save tasks to JSON file |
| `models.py` | Model | Task class and TaskFactory |
| `strategies_and_observers.py` | Patterns | Strategy (sort behaviors) + Observer (event reactions) |

## The two change requests

**Change 1 — Persist tasks to a file**
Already implemented. Touch `repository.py` only. Routes and services unchanged.

**Change 2 — Sort by priority**
Already implemented via `SortByPriority` in `strategies_and_observers.py`.
Service calls `self._strategy.sort(tasks)`. Swap strategy, nothing else moves.

## What to compare with v1

Open `app1-monolith/app.py` and `app2-layered/app.py` side by side.
Count the lines in each route function. That difference is the architecture.
