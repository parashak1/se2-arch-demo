# =============================================================
#  strategies.py — TaskFlow v2
#  Layer: Business Logic (pluggable sorting behaviors)
#
#  Pattern: Strategy
#  Principle: Open / Closed
#
#  Add a new sort order → add a new class below.
#  The service layer never changes.
#  The routes never change.
# =============================================================


# ── Base strategy ─────────────────────────────────────────────

class SortStrategy:
    """
    Base class for all sort strategies.
    Subclasses override sort() with their own logic.

    Strategy Pattern: the TaskService holds ONE strategy at a time.
    Swap the strategy → behavior changes, everything else stays.
    """

    def sort(self, tasks):
        # subclasses override this
        return tasks


# ── Concrete strategies ───────────────────────────────────────

class SortByPriority(SortStrategy):
    """
    Sort tasks: high → medium → low.
    Done tasks always sink to the bottom.
    """

    PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}

    def sort(self, tasks):
        return sorted(
            tasks,
            key=lambda t: (t.done, self.PRIORITY_ORDER.get(t.priority, 99))
        )


class SortByDate(SortStrategy):
    """
    Sort tasks by creation order (newest first).
    Done tasks always sink to the bottom.
    """

    def sort(self, tasks):
        return sorted(
            tasks,
            key=lambda t: (t.done, -t.id)
        )


class SortAlphabetically(SortStrategy):
    """
    Sort tasks A → Z by title.
    Done tasks always sink to the bottom.
    """

    def sort(self, tasks):
        return sorted(
            tasks,
            key=lambda t: (t.done, t.title.lower())
        )


# =============================================================
#  observers.py — TaskFlow v2
#  Layer: Business Logic (event reactions)
#
#  Pattern: Observer
#  Principle: Single Responsibility
#
#  TaskService fires events. Observers react.
#  Add a new reaction → add a new Observer class.
#  The service never changes. The routes never change.
# =============================================================


# ── Base observer ─────────────────────────────────────────────

class Observer:
    """
    Base class for all observers.
    Subclasses override update() to react to task events.

    Observer Pattern: TaskService holds a LIST of observers.
    When something happens, it calls update() on all of them.
    Each observer handles its own concern independently.
    """

    def update(self, event, task):
        # subclasses override this
        pass


# ── Concrete observers ────────────────────────────────────────

class StatsObserver(Observer):
    """
    Tracks running counts: total, done, pending, high-priority.
    The service layer does not calculate stats — this class does.

    Single Responsibility: one job — maintain counts.
    """

    def __init__(self):
        self.total      = 0
        self.done_count = 0
        self.high_count = 0

    @property
    def pending(self):
        return self.total - self.done_count

    def update(self, event, task):
        if event == "added":
            self.total += 1
            if task.priority == "high" and not task.done:
                self.high_count += 1

        elif event == "completed":
            self.done_count += 1
            if task.priority == "high":
                self.high_count -= 1

        elif event == "deleted":
            self.total -= 1
            if task.done:
                self.done_count -= 1
            elif task.priority == "high":
                self.high_count -= 1

    def get_stats(self):
        return {
            "total":      self.total,
            "done_count": self.done_count,
            "pending":    self.pending,
            "high_count": self.high_count,
        }


class LogObserver(Observer):
    """
    Logs task events to the console.
    In production this would write to a log file or
    send to a logging service.

    Single Responsibility: one job — record what happened.
    """

    def update(self, event, task):
        labels = {
            "added":     "TASK ADDED",
            "completed": "TASK DONE ",
            "deleted":   "TASK DEL  ",
        }
        label = labels.get(event, event.upper())
        print(f"  [{label}]  #{task.id} '{task.title}' ({task.priority})")
