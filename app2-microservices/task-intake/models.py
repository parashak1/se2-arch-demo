# =============================================================
#  models.py — TaskFlow Microservices (task-intake)
#  Unchanged from app2-layered.
#  Task class + TaskFactory live here.
# =============================================================

from datetime import datetime


class Task:
    def __init__(self, task_id, title, priority="medium"):
        self.id         = task_id
        self.title      = title
        self.priority   = priority
        self.done       = False
        self.created_at = datetime.now().strftime("%b %d, %H:%M")

    def mark_done(self):
        self.done = True

    def to_dict(self):
        return {
            "id":         self.id,
            "title":      self.title,
            "priority":   self.priority,
            "done":       self.done,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data):
        task            = cls(data["id"], data["title"], data["priority"])
        task.done       = data["done"]
        task.created_at = data["created_at"]
        return task

    def __repr__(self):
        status = "done" if self.done else "pending"
        return f"Task({self.id}, '{self.title}', {self.priority}, {status})"


class TaskFactory:
    _next_id = 1

    @classmethod
    def create(cls, title, priority="medium"):
        task = Task(cls._next_id, title, priority)
        cls._next_id += 1
        return task

    @classmethod
    def set_next_id(cls, next_id):
        cls._next_id = next_id
