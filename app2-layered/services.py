# =============================================================
#  services.py — TaskFlow v2
#  Layer: Business Logic
#
#  What lives here:
#    - TaskService  (all decisions about tasks)
#
#  What does NOT live here:
#    - Storage mechanics     → repository.py
#    - HTTP / routing        → app.py
#    - Task definition       → models.py
#    - Sort implementations  → strategies_and_observers.py
#
#  TaskService is the coordinator:
#    - Uses TaskRepository  to persist data
#    - Uses SortStrategy    to sort results
#    - Notifies Observer[]  when state changes
# =============================================================

from models import TaskFactory
from repository import TaskRepository
from strategies_and_observers import (
    SortByPriority, SortByDate, SortAlphabetically,
    StatsObserver, LogObserver
)


class TaskService:
    """
    All business logic for the task manager.

    The route layer (app.py) calls methods on this class.
    It never touches the repository, strategies, or observers directly.

    Think of this as the brain of the app.
    The routes are just messengers that hand off to this brain.
    """

    # available sort strategies by name
    SORT_STRATEGIES = {
        "priority":      SortByPriority,
        "date":          SortByDate,
        "alphabetical":  SortAlphabetically,
    }

    def __init__(self):
        # ── wire up the layers ────────────────────────────────
        self.repository = TaskRepository()

        # Strategy: default sort is by priority
        self._strategy  = SortByPriority()

        # Observers: anyone who cares about task events
        self._stats_observer = StatsObserver()
        self._observers = [
            self._stats_observer,
            LogObserver(),
        ]

        # sync stats observer with tasks already in storage
        self._rebuild_stats()

    # ── commands (change state) ───────────────────────────────

    def add_task(self, title, priority="medium"):
        """
        Validate, create, and store a new task.
        Notify observers that a task was added.
        """
        # validation lives here — not in the route
        title = title.strip()
        if not title:
            raise ValueError("Task title cannot be empty.")
        if len(title) > 120:
            title = title[:120]
        if priority not in ("high", "medium", "low"):
            priority = "medium"

        task = TaskFactory.create(title, priority)
        self.repository.add(task)
        self._notify("added", task)
        return task

    def complete_task(self, task_id):
        """
        Mark a task as done.
        Notify observers that a task was completed.
        """
        task = self.repository.find_by_id(task_id)
        if task and not task.done:
            task.mark_done()
            self.repository.update(task)
            self._notify("completed", task)
        return task

    def delete_task(self, task_id):
        """
        Remove a task.
        Notify observers that a task was deleted.
        """
        task = self.repository.find_by_id(task_id)
        if task:
            self._notify("deleted", task)
            self.repository.delete(task_id)
        return task

    # ── queries (read state) ──────────────────────────────────

    def get_filtered_tasks(self, filter_by="all"):
        """
        Return tasks matching the filter, sorted by active strategy.
        Filtering and sorting logic lives here — not in the route.
        """
        all_tasks = self.repository.get_all()

        # filter
        if filter_by == "pending":
            tasks = [t for t in all_tasks if not t.done]
        elif filter_by == "done":
            tasks = [t for t in all_tasks if t.done]
        elif filter_by == "high":
            tasks = [t for t in all_tasks if t.priority == "high" and not t.done]
        else:
            tasks = all_tasks

        # sort via plugged-in strategy
        return self._strategy.sort(tasks)

    def get_stats(self):
        """Return current task counts from the stats observer."""
        return self._stats_observer.get_stats()

    # ── strategy control ──────────────────────────────────────

    def set_sort_strategy(self, strategy_name):
        """
        Swap the active sort strategy at runtime.
        Strategy Pattern: the caller just names what they want.
        This method handles which class to instantiate.
        """
        strategy_class = self.SORT_STRATEGIES.get(strategy_name)
        if strategy_class:
            self._strategy = strategy_class()

    # ── observer management ───────────────────────────────────

    def add_observer(self, observer):
        """Register a new observer. Open/Closed: no existing code changes."""
        self._observers.append(observer)

    def _notify(self, event, task):
        """Tell every observer something happened."""
        for observer in self._observers:
            observer.update(event, task)

    # ── private helpers ───────────────────────────────────────

    def _rebuild_stats(self):
        """
        Rebuild stats from existing tasks on startup.
        Fires a synthetic 'added' event for each stored task
        so StatsObserver counts stay accurate.
        """
        for task in self.repository.get_all():
            self._stats_observer.update("added", task)
            if task.done:
                self._stats_observer.update("completed", task)
