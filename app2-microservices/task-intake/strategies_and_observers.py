# =============================================================
#  strategies_and_observers.py — TaskFlow Microservices (task-intake)
#  Unchanged from app2-layered.
#  Strategy pattern for sorting, Observer pattern for events.
# =============================================================


# ── Strategy base and concrete classes ────────────────────────

class SortStrategy:
    def sort(self, tasks):
        return tasks


class SortByPriority(SortStrategy):
    PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}

    def sort(self, tasks):
        return sorted(
            tasks,
            key=lambda t: (t.done, self.PRIORITY_ORDER.get(t.priority, 99))
        )


class SortByDate(SortStrategy):
    def sort(self, tasks):
        return sorted(tasks, key=lambda t: (t.done, -t.id))


class SortAlphabetically(SortStrategy):
    def sort(self, tasks):
        return sorted(tasks, key=lambda t: (t.done, t.title.lower()))


# ── Observer base and concrete classes ───────────────────────

class Observer:
    def update(self, event, task):
        pass


class StatsObserver(Observer):
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
    def update(self, event, task):
        labels = {
            "added":     "TASK ADDED",
            "completed": "TASK DONE ",
            "deleted":   "TASK DEL  ",
        }
        label = labels.get(event, event.upper())
        print(f"  [{label}]  #{task.id} '{task.title}' ({task.priority})")
