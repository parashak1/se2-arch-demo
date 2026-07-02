# =============================================================
#  models.py — TaskFlow v2
#  Layer: Data Model
#
#  What lives here:
#    - The Task class  (what a task IS)
#    - TaskFactory     (how a task is CREATED)
#
#  What does NOT live here:
#    - Storage logic  → repository.py
#    - Business rules → services.py
#    - HTTP handling  → app.py
# =============================================================

from datetime import datetime


class Task:
    """
    Represents a single task.
    Knows about its own data. Nothing else.
    Does not know how it is stored, sorted, or displayed.
    """

    def __init__(self, task_id, title, priority="medium"):
        self.id         = task_id
        self.title      = title
        self.priority   = priority          # "high" | "medium" | "low"
        self.done       = False
        self.created_at = datetime.now().strftime("%b %d, %H:%M")

    def mark_done(self):
        """Mark this task as complete."""
        self.done = True

    def to_dict(self):
        """Serialize to a plain dict (for JSON storage)."""
        return {
            "id":         self.id,
            "title":      self.title,
            "priority":   self.priority,
            "done":       self.done,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data):
        """Rebuild a Task from a stored dict."""
        task            = cls(data["id"], data["title"], data["priority"])
        task.done       = data["done"]
        task.created_at = data["created_at"]
        return task

    def __repr__(self):
        status = "done" if self.done else "pending"
        return f"Task({self.id}, '{self.title}', {self.priority}, {status})"


# -------------------------------------------------------------

class TaskFactory:
    """
    Factory Pattern — centralizes Task creation.

    Why: callers never call Task(...) directly.
    If the Task constructor changes, only this class changes.
    Every caller stays the same.
    """

    _next_id = 1   # simple auto-increment counter

    @classmethod
    def create(cls, title, priority="medium"):
        """Create and return a new Task with a unique ID."""
        task = Task(cls._next_id, title, priority)
        cls._next_id += 1
        return task

    @classmethod
    def set_next_id(cls, next_id):
        """
        Sync the counter after loading tasks from storage.
        Called by TaskRepository after it loads saved tasks.
        """
        cls._next_id = next_id
