#test_tasks.py
#Tests for TaskFlow v2; models, strategy, and observer

from models import Task, TaskFactory
from strategies_and_observers import SortByPriority, StatsObserver

def test_task_factory_creates_task():
    task = TaskFactory.create("Write tests", "high")
    assert task.title == "Write tests"
    assert task.priority == "high"
    assert task.done == False

def test_sort_by_priority_orders_correctly():
    t1 = TaskFactory.create("Low task", "low")
    t2 = TaskFactory.create("Medium task", "medium")
    t3 = TaskFactory.create("High task", "high")
    strategy = SortByPriority()
    sorted_tasks = strategy.sort([t1, t2, t3])
    assert sorted_tasks[0].priority == "high"
    assert sorted_tasks[1].priority == "medium"
    assert sorted_tasks[2].priority == "low"

def test_stats_observer_counts_correctly():
    observer = StatsObserver()
    task = TaskFactory.create("Count me", "high")
    observer.update("added", task)
    assert observer.total == 1
    assert observer.high_count == 1
    assert observer.pending == 1
