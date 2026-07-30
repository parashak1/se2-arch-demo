# =============================================================
#  repository.py — TaskFlow Microservices (task-intake)
#  Unchanged from app2-layered.
#  All storage and retrieval lives here.
# =============================================================

import json
import os
from models import Task, TaskFactory

TASKS_FILE = "tasks.json"


class TaskRepository:
    def __init__(self):
        self._tasks = []
        self._load()

    def get_all(self):
        return list(self._tasks)

    def add(self, task):
        self._tasks.append(task)
        self._save()

    def update(self, task):
        self._save()

    def delete(self, task_id):
        self._tasks = [t for t in self._tasks if t.id != task_id]
        self._save()

    def find_by_id(self, task_id):
        for task in self._tasks:
            if task.id == task_id:
                return task
        return None

    def _save(self):
        data = {
            "next_id": TaskFactory._next_id,
            "tasks":   [t.to_dict() for t in self._tasks],
        }
        with open(TASKS_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def _load(self):
        if not os.path.exists(TASKS_FILE):
            self._seed()
            return
        with open(TASKS_FILE) as f:
            data = json.load(f)
        self._tasks = [Task.from_dict(d) for d in data["tasks"]]
        TaskFactory.set_next_id(data.get("next_id", len(self._tasks) + 1))

    def _seed(self):
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
        self._tasks[2].done = True
        self._save()
