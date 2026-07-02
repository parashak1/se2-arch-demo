# =============================================================
#  repository.py — TaskFlow v2
#  Layer: Data
#
#  What lives here:
#    - TaskRepository  (how tasks are STORED and RETRIEVED)
#
#  What does NOT live here:
#    - Business rules  → services.py
#    - HTTP handling   → app.py
#    - Task definition → models.py
#
#  Key idea: if we switch from file storage to a database,
#  only THIS file changes. Nothing else in the app knows
#  or cares how storage works.
# =============================================================

import json
import os
from models import Task, TaskFactory


TASKS_FILE = "tasks.json"


class TaskRepository:
    """
    Manages persistence for tasks.

    Stores tasks in memory (self._tasks).
    Optionally persists to a JSON file.

    The rest of the app never touches the file directly.
    """

    def __init__(self):
        self._tasks = []
        self._load()

    # ── public interface ──────────────────────────────────────

    def get_all(self):
        """Return all tasks as a list."""
        return list(self._tasks)

    def add(self, task):
        """Add a task to the store and persist."""
        self._tasks.append(task)
        self._save()

    def update(self, task):
        """
        Persist changes to an existing task.
        (Task object is already mutated by the service layer —
        we just need to save the updated state.)
        """
        self._save()

    def delete(self, task_id):
        """Remove a task by ID and persist."""
        self._tasks = [t for t in self._tasks if t.id != task_id]
        self._save()

    def find_by_id(self, task_id):
        """Return a single task by ID, or None."""
        for task in self._tasks:
            if task.id == task_id:
                return task
        return None

    # ── private: storage mechanics ────────────────────────────

    def _save(self):
        """Write current tasks to the JSON file."""
        data = {
            "next_id": TaskFactory._next_id,
            "tasks":   [t.to_dict() for t in self._tasks],
        }
        with open(TASKS_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def _load(self):
        """Load tasks from the JSON file if it exists."""
        if not os.path.exists(TASKS_FILE):
            self._seed()
            return

        with open(TASKS_FILE) as f:
            data = json.load(f)

        self._tasks = [Task.from_dict(d) for d in data["tasks"]]
        TaskFactory.set_next_id(data.get("next_id", len(self._tasks) + 1))

    def _seed(self):
        """
        Populate sample tasks on first run so class
        does not start with an empty screen.
        """
        samples = [
            ("Submit Sprint 0 deliverables",  "high"),
            ("Set up GitHub org and repo",    "high"),
            ("Write 10 user stories",         "medium"),
            ("Choose tech stack",             "medium"),
            ("Read the project document",     "low"),
        ]
        for title, priority in samples:
            task = TaskFactory.create(title, priority)
            self._tasks.append(task)

        self._tasks[2].done = True   # one done for visual variety
        self._save()
