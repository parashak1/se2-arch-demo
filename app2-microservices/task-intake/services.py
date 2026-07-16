# =============================================================
#  services.py — TaskFlow Microservices (task-intake)
#
#  Modified from app2-layered in ONE place only:
#  add_task() now calls the validator service before
#  creating a task.
#
#  Everything else is identical to app2-layered.
#  That is the point — one clean seam, minimal change.
# =============================================================

import requests
from models import TaskFactory
from repository import TaskRepository
from strategies_and_observers import (
    SortByPriority, SortByDate, SortAlphabetically,
    StatsObserver, LogObserver
)

# ── Validator service config ──────────────────────────────────
# The URL lives here in the service layer, not in the route.
# If the validator moves to a different host, change one line.

VALIDATOR_URL = "http://localhost:5002/validate"
VALIDATOR_TIMEOUT = 3   # seconds — how long we wait before giving up


class ValidationError(Exception):
    """Raised when the validator rejects a task."""
    pass


class ValidatorUnavailableError(Exception):
    """Raised when the validator service cannot be reached."""
    pass


class TaskService:
    """
    All business logic for the task manager.

    The only change from app2-layered:
    add_task() calls the validator service before creating a task.
    If the validator says no, the task is not created.
    If the validator is unreachable, we fail gracefully.
    """

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

    # ── commands ──────────────────────────────────────────────

    def add_task(self, title, priority="medium"):
        """
        Validate via the external validator service, then create.

        Three outcomes:
          1. Validator says valid      → task is created, returned
          2. Validator says invalid    → ValidationError raised
          3. Validator unreachable     → ValidatorUnavailableError raised,
                                         caller decides how to handle it
        """

        # ── call the validator service ────────────────────────
        # This is the new line. One HTTP call, one decision.
        # The rest of this method is unchanged from app2-layered.

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

        # ── validator approved — create the task ──────────────
        # From here down, identical to app2-layered

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

    # ── strategy control ──────────────────────────────────────

    def set_sort_strategy(self, strategy_name):
        strategy_class = self.SORT_STRATEGIES.get(strategy_name)
        if strategy_class:
            self._strategy = strategy_class()

    # ── observer management ───────────────────────────────────

    def _notify(self, event, task):
        for observer in self._observers:
            observer.update(event, task)

    def _rebuild_stats(self):
        for task in self.repository.get_all():
            self._stats_observer.update("added", task)
            if task.done:
                self._stats_observer.update("completed", task)
