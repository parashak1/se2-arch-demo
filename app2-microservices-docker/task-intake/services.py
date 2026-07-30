# =============================================================
#  services.py — TaskFlow Microservices Docker (task-intake)
#
#  One change from the plain Python version:
#  VALIDATOR_URL is read from an environment variable.
#
#  Locally:   defaults to http://localhost:5002/validate
#  In Docker: docker-compose injects
#             http://task-validator:5002/validate
#
#  This is how real services are configured — the code
#  never hardcodes a host. The environment decides.
# =============================================================

import os
import requests
from models import TaskFactory
from repository import TaskRepository
from strategies_and_observers import (
    SortByPriority, SortByDate, SortAlphabetically,
    StatsObserver, LogObserver
)

# ── Read validator URL from environment ───────────────────────
# Locally this falls back to localhost.
# In docker-compose this is set to http://task-validator:5002/validate
# "task-validator" is the service name in docker-compose.yml
# Docker's internal DNS resolves it to the right container.

VALIDATOR_URL     = os.environ.get(
    "VALIDATOR_URL",
    "http://localhost:5002/validate"
)
VALIDATOR_TIMEOUT = int(os.environ.get("VALIDATOR_TIMEOUT", 3))


class ValidationError(Exception):
    pass


class ValidatorUnavailableError(Exception):
    pass


class TaskService:

    SORT_STRATEGIES = {
        "priority":     SortByPriority,
        "date":         SortByDate,
        "alphabetical": SortAlphabetically,
    }

    def __init__(self):
        self.repository      = TaskRepository()
        self._strategy       = SortByPriority()
        self._stats_observer = StatsObserver()
        self._observers      = [self._stats_observer, LogObserver()]
        self._rebuild_stats()
        print(f"  TaskService: calling validator at {VALIDATOR_URL}")

    # ── commands ──────────────────────────────────────────────

    def add_task(self, title, priority="medium"):
        try:
            response = requests.post(
                VALIDATOR_URL,
                json={"title": title, "priority": priority},
                timeout=VALIDATOR_TIMEOUT
            )
            result = response.json()
            if not result.get("valid"):
                raise ValidationError(result.get("reason", "Invalid task"))

        except requests.exceptions.Timeout:
            raise ValidatorUnavailableError(
                "Validator service did not respond in time"
            )
        except requests.exceptions.ConnectionError:
            raise ValidatorUnavailableError(
                "Validator service is not reachable"
            )

        title = title.strip()
        task  = TaskFactory.create(title, priority)
        self.repository.add(task)
        self._notify("added", task)
        return task

    def complete_task(self, task_id):
        task = self.repository.find_by_id(task_id)
        if task and not task.done:
            task.mark_done()
            self.repository.update(task)
            self._notify("completed", task)
        return task

    def delete_task(self, task_id):
        task = self.repository.find_by_id(task_id)
        if task:
            self._notify("deleted", task)
            self.repository.delete(task_id)
        return task

    # ── queries ───────────────────────────────────────────────

    def get_filtered_tasks(self, filter_by="all"):
        all_tasks = self.repository.get_all()
        if filter_by == "pending":
            tasks = [t for t in all_tasks if not t.done]
        elif filter_by == "done":
            tasks = [t for t in all_tasks if t.done]
        elif filter_by == "high":
            tasks = [t for t in all_tasks if t.priority == "high" and not t.done]
        else:
            tasks = all_tasks
        return self._strategy.sort(tasks)

    def get_stats(self):
        return self._stats_observer.get_stats()

    def set_sort_strategy(self, strategy_name):
        strategy_class = self.SORT_STRATEGIES.get(strategy_name)
        if strategy_class:
            self._strategy = strategy_class()

    def _notify(self, event, task):
        for observer in self._observers:
            observer.update(event, task)

    def _rebuild_stats(self):
        for task in self.repository.get_all():
            self._stats_observer.update("added", task)
            if task.done:
                self._stats_observer.update("completed", task)
