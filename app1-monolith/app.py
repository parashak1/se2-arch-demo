# ============================================================
#  TaskFlow — v1  (The Monolith)
#  SE-II Session 2 Demo App
#  Everything lives in this one file: routes, logic, and data.
# ============================================================

from flask import Flask, request, redirect, url_for, render_template_string
from datetime import datetime

import os
# import json
# TASKS_FILE = "tasks.json"

# def load_tasks():
#     if not os.path.exists(TASKS_FILE):
#         return [], 1
    
#     with open(TASKS_FILE) as f:
#         data = json.load(f)

#     return data['tasks'], data['next_id']

# def save_tasks():
#     with open(TASKS_FILE, 'w') as f:
#          json.dump({'tasks': tasks, 'next_id': next_id}, f)


app = Flask(__name__)

# ── "Database" ── just a Python list in memory ──────────────
tasks = []
next_id = 1

# ── HTML template ── lives right here in the app file ───────
TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>TaskFlow</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: Arial, sans-serif; background: #f0f2f5; padding: 32px 16px; color: #222; }
    .wrap { max-width: 620px; margin: 0 auto; }
    h1 { font-size: 26px; color: #1a3a5c; margin-bottom: 6px; }
    .sub { font-size: 13px; color: #888; margin-bottom: 24px; }
    .add-form { background: #fff; border-radius: 8px; padding: 20px; margin-bottom: 24px;
                border: 1px solid #dde3ed; }
    .add-form input[type=text] { width: 100%; padding: 10px 12px; border: 1px solid #ccc;
                                  border-radius: 6px; font-size: 14px; margin-bottom: 10px; }
    .add-form select { padding: 8px 10px; border: 1px solid #ccc; border-radius: 6px;
                       font-size: 14px; margin-right: 8px; }
    .add-form button { background: #2E75B6; color: #fff; border: none; padding: 9px 20px;
                       border-radius: 6px; font-size: 14px; cursor: pointer; }
    .filters { display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; }
    .filters a { padding: 6px 14px; border-radius: 99px; font-size: 13px; text-decoration: none;
                 background: #e8edf5; color: #444; border: 1px solid #d0d7e3; }
    .filters a.active { background: #2E75B6; color: #fff; border-color: #2E75B6; }
    .task-list { list-style: none; }
    .task { background: #fff; border-radius: 8px; padding: 14px 16px; margin-bottom: 10px;
            border: 1px solid #dde3ed; display: flex; align-items: center; gap: 12px; }
    .task.done { opacity: 0.5; }
    .task.done .task-title { text-decoration: line-through; }
    .task-title { flex: 1; font-size: 15px; }
    .badge { font-size: 11px; padding: 3px 9px; border-radius: 99px; font-weight: 600; }
    .badge-high   { background: #fde8e8; color: #922; }
    .badge-medium { background: #fff3cd; color: #7a5000; }
    .badge-low    { background: #e8f5e9; color: #2e7d32; }
    .task-meta { font-size: 11px; color: #aaa; }
    .btn-done { background: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9;
                padding: 4px 12px; border-radius: 6px; font-size: 12px; cursor: pointer;
                text-decoration: none; }
    .btn-delete { background: #fde8e8; color: #922; border: 1px solid #f5c6c6;
                  padding: 4px 12px; border-radius: 6px; font-size: 12px; cursor: pointer;
                  text-decoration: none; }
    .empty { text-align: center; padding: 32px; color: #aaa; font-size: 14px; }
    .stats { background: #fff; border-radius: 8px; padding: 14px 18px; margin-bottom: 20px;
             border: 1px solid #dde3ed; display: flex; gap: 24px; }
    .stat { text-align: center; }
    .stat-num { font-size: 22px; font-weight: 700; color: #2E75B6; }
    .stat-lbl { font-size: 11px; color: #888; }
  </style>
</head>
<body>
<div class="wrap">
  <h1>📝 TaskFlow</h1>
  <p class="sub">A simple task manager &nbsp;·&nbsp; v1 (monolith)</p>

  <!-- Stats -->
  <div class="stats">
    <div class="stat">
      <div class="stat-num">{{ total }}</div>
      <div class="stat-lbl">Total</div>
    </div>
    <div class="stat">
      <div class="stat-num">{{ done_count }}</div>
      <div class="stat-lbl">Done</div>
    </div>
    <div class="stat">
      <div class="stat-num">{{ pending }}</div>
      <div class="stat-lbl">Pending</div>
    </div>
    <div class="stat">
      <div class="stat-num">{{ high_count }}</div>
      <div class="stat-lbl">High priority</div>
    </div>
  </div>

  <!-- Add task -->
  <div class="add-form">
    <form method="POST" action="/add">
      <input type="text" name="title" placeholder="What needs to be done?" required>
      <div style="display:flex; align-items:center; gap:8px;">
        <select name="priority">
          <option value="high">🔴 High</option>
          <option value="medium" selected>🟡 Medium</option>
          <option value="low">🟢 Low</option>
        </select>
        <button type="submit">Add Task</button>
      </div>
    </form>
  </div>

  <!-- Filters -->
  <div class="filters">
    <a href="/" class="{{ 'active' if filter == 'all' }}">All ({{ total }})</a>
    <a href="/?filter=pending" class="{{ 'active' if filter == 'pending' }}">Pending ({{ pending }})</a>
    <a href="/?filter=done" class="{{ 'active' if filter == 'done' }}">Done ({{ done_count }})</a>
    <a href="/?filter=high" class="{{ 'active' if filter == 'high' }}">🔴 High ({{ high_count }})</a>
  </div>

  <!-- Task list -->
  <ul class="task-list">
    {% for task in visible_tasks %}
    <li class="task {{ 'done' if task.done }}">
      <div>
        <span class="badge badge-{{ task.priority }}">{{ task.priority }}</span>
      </div>
      <div class="task-title">{{ task.title }}</div>
      <div class="task-meta">{{ task.created_at }}</div>
      {% if not task.done %}
        <a href="/complete/{{ task.id }}" class="btn-done">✓ Done</a>
      {% endif %}
      <a href="/delete/{{ task.id }}" class="btn-delete">✕</a>
    </li>
    {% else %}
    <li class="empty">No tasks here. Add one above.</li>
    {% endfor %}
  </ul>
</div>
</body>
</html>
"""

# ── Routes — AND logic — AND data access — all right here ───

@app.route("/")
def index():
    global tasks

    filter_by = request.args.get("filter", "all")

    PRIORITY_ORDER = {'high': 0, 'medium': 1, 'low': 2}

    # ⚠️  LOGIC MIXED INTO ROUTE — filtering happens here in the route

    
    if filter_by == "pending":
        visible_tasks = [t for t in tasks if not t["done"]]

 #   if filter_by == "pending":
 #       visible_tasks = sorted(
  #          [t for t in tasks if not t['done']], key=lambda t: PRIORITY_ORDER.get(t['priority'], 99)
  #      )

    elif filter_by == "done":
        visible_tasks = [t for t in tasks if t["done"]]
    elif filter_by == "high":
        visible_tasks = [t for t in tasks if t["priority"] == "high"]
    else:
        visible_tasks = tasks

    # ⚠️  STATS LOGIC ALSO IN ROUTE
    total      = len(tasks)
    done_count = len([t for t in tasks if t["done"]])
    pending    = total - done_count
    high_count = len([t for t in tasks if t["priority"] == "high" and not t["done"]])

    return render_template_string(
        TEMPLATE,
        visible_tasks=visible_tasks,
        filter=filter_by,
        total=total,
        done_count=done_count,
        pending=pending,
        high_count=high_count,
    )


@app.route("/add", methods=["POST"])
def add_task():
    global tasks, next_id

    title    = request.form.get("title", "").strip()
    priority = request.form.get("priority", "medium")

    # ⚠️  VALIDATION LOGIC IN ROUTE
    if not title:
        return redirect(url_for("index"))

    if len(title) > 120:
        title = title[:120]

    # ⚠️  DATA CREATION IN ROUTE
    task = {
        "id":         next_id,
        "title":      title,
        "priority":   priority,
        "done":       False,
        "created_at": datetime.now().strftime("%b %d, %H:%M"),
    }
    tasks.append(task)
    next_id += 1
    #save_tasks()

    return redirect(url_for("index"))


@app.route("/complete/<int:task_id>")
def complete_task(task_id):
    global tasks

    # ⚠️  BUSINESS LOGIC (marking done) IN ROUTE
    for task in tasks:
        if task["id"] == task_id:
            task["done"] = True
            break
    
    #save_tasks()

    return redirect(url_for("index"))


@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    global tasks

    # ⚠️  DATA MUTATION IN ROUTE
    tasks = [t for t in tasks if t["id"] != task_id]

    #save_tasks()

    return redirect(url_for("index"))


# ── Seed some sample data so class doesn't start with empty app
def seed():
    global tasks, next_id
    samples = [
        ("Submit Sprint 0 deliverables",  "high"),
        ("Set up GitHub org and repo",    "high"),
        ("Write 10 user stories",         "medium"),
        ("Choose tech stack",             "medium"),
        ("Read the project document",     "low"),
    ]
    for title, priority in samples:
        tasks.append({
            "id":         next_id,
            "title":      title,
            "priority":   priority,
            "done":       False,
            "created_at": datetime.now().strftime("%b %d, %H:%M"),
        })
        next_id += 1
    tasks[2]["done"] = True   # mark one done for visual variety


if __name__ == "__main__":
    seed()
    
    # tasks, next_id = load_tasks()

    print("\n  TaskFlow v1 running →  http://localhost:5000\n")
    app.run(debug=True)
