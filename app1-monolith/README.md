# TaskFlow v1 — The Monolith

**SE-II Session 2 demo app.**

A working task manager where everything lives in a single file: routes, business logic, data storage, and HTML template. It works perfectly. The question is what happens when you try to change it.

---

## Run it

```bash
pip install flask
python app.py
```

Open [http://localhost:5000](http://localhost:5000)

---

## What's in `app.py`

| What | Where |
|------|-------|
| HTML template | `TEMPLATE` string near the top |
| In-memory data store | `tasks` list and `next_id` global |
| Filtering logic | Inside `index()` route |
| Stats calculation | Inside `index()` route |
| Input validation | Inside `add_task()` route |
| Data creation | Inside `add_task()` route |
| Business logic (mark done) | Inside `complete_task()` route |
| Data mutation (delete) | Inside `delete_task()` route |


---

## The two change requests

I will make these changes live during class.

**Change 1 — Persist tasks to a file**
> "Tasks disappear when we restart the server. We need them saved."

Before you make it: predict which parts of the file will need to change.
This is a data storage change — should it touch the route functions?

**Change 2 — Sort pending tasks by priority**
> "When I look at pending tasks, high priority should be at the top."

Before you make it: predict where the sort logic should live.
Should adding a sort feature require touching an HTTP route handler?

---

## Seeded sample data

The app starts with 5 sample tasks so class doesn't begin with an empty screen. Defined in the `seed()` function at the bottom of `app.py`.
