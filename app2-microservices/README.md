# app2-microservices

**SE-II Week 6 — TaskFlow split into two communicating services.**

Same features as `app2-layered`. Different inside — validation now lives
in a separate service that task-intake calls over HTTP.

---

## Services

| Service | Folder | Port | Job |
|---|---|---|---|
| task-intake | `task-intake/` | 5001 | Handles HTTP, business logic, storage |
| task-validator | `task-validator/` | 5002 | Validates tasks before they are created |

---

## Run it

Open **two terminals**.

**Terminal 1 — start the validator first:**
```bash
cd task-validator
pip install -r requirements.txt
python app.py
```

**Terminal 2 — start the intake service:**
```bash
cd task-intake
pip install -r requirements.txt
python app.py
```

Open http://localhost:5001

---

## What changed from app2-layered

Only two files changed. Everything else is identical.

**`task-intake/services.py`**
`add_task()` now calls the validator service before creating a task.
One HTTP POST to `http://localhost:5002/validate`.
If the validator says no — task is rejected with a reason.
If the validator is unreachable — `ValidatorUnavailableError` is raised.

**`task-intake/app.py`**
The `/add` route now handles two new error cases:
`ValidationError` shows the rejection reason to the user.
`ValidatorUnavailableError` shows a warning and does not save the task.

---

## Try these in class

**Normal flow:**
Add any task. It calls the validator. Validator approves. Task appears.

**Validation rejection:**
Try adding a task with an empty title, or a priority that is not
high/medium/low. The validator rejects it and the reason appears on screen.

**Validator down — graceful degradation:**
Stop the validator (Ctrl+C in Terminal 1).
Try adding a task. The intake service times out after 3 seconds
and shows a warning instead of crashing.

**Validator slow — timeout demo:**
Add `import time; time.sleep(10)` at the top of the `/validate`
route in `task-validator/app.py`. Restart the validator.
Add a task and watch the intake service wait, then time out cleanly.

---

## What this demonstrates

- Two independent services communicating over HTTP
- Synchronous inter-service communication (intake waits for validator)
- Timeout handling — intake does not wait forever
- Graceful degradation — intake keeps running even when validator is down
- Health check endpoints — both services expose `/health`
- Service boundary — validation logic is completely isolated
