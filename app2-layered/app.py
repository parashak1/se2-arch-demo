# =============================================================
#  app.py — TaskFlow v2
#  Layer: Presentation (routes only)
#
#  Compare this file to app.py in app1-monolith.
#
#  This file has ONE job: handle HTTP.
#  Receive a request, call the service, return a response.
#  No business logic. No data access. No calculations.
#
#  If a route function does more than ~5 lines,
#  something is leaking from the wrong layer.
# =============================================================

from flask import Flask, request, redirect, url_for, render_template_string
from services import TaskService

app     = Flask(__name__)
service = TaskService()          # one shared service instance


# ── HTML template ─────────────────────────────────────────────
# Still here for demo simplicity.
# In a real app this moves to templates/ folder.

TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>TaskFlows</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: Arial, sans-serif; background: #f0f2f5; padding: 32px 16px; color: #222; }
    .wrap { max-width: 620px; margin: 0 auto; }
    h1 { font-size: 26px; color: #1a3a5c; margin-bottom: 4px; }
    .sub { font-size: 13px; color: #888; margin-bottom: 24px; }
    .badge-layer { display:inline-block; font-size:11px; padding:2px 8px;
                   border-radius:4px; background:#e8f5e9; color:#2e7d32;
                   border:1px solid #c8e6c9; margin-left:8px; font-weight:600; }
    .add-form { background:#fff; border-radius:8px; padding:20px; margin-bottom:24px;
                border:1px solid #dde3ed; }
    .add-form input[type=text] { width:100%; padding:10px 12px; border:1px solid #ccc;
                                  border-radius:6px; font-size:14px; margin-bottom:10px; }
    .add-form select { padding:8px 10px; border:1px solid #ccc; border-radius:6px;
                       font-size:14px; margin-right:8px; }
    .add-form button { background:#2E75B6; color:#fff; border:none; padding:9px 20px;
                       border-radius:6px; font-size:14px; cursor:pointer; }
    .controls { display:flex; gap:8px; margin-bottom:16px; flex-wrap:wrap; }
    .controls a { padding:6px 14px; border-radius:99px; font-size:13px; text-decoration:none;
                  background:#e8edf5; color:#444; border:1px solid #d0d7e3; }
    .controls a.active { background:#2E75B6; color:#fff; border-color:#2E75B6; }
    .task-list { list-style:none; }
    .task { background:#fff; border-radius:8px; padding:14px 16px; margin-bottom:10px;
            border:1px solid #dde3ed; display:flex; align-items:center; gap:12px; }
    .task.done { opacity:0.5; }
    .task.done .task-title { text-decoration:line-through; }
    .task-title { flex:1; font-size:15px; }
    .badge { font-size:11px; padding:3px 9px; border-radius:99px; font-weight:600; }
    .badge-high   { background:#fde8e8; color:#922; }
    .badge-medium { background:#fff3cd; color:#7a5000; }
    .badge-low    { background:#e8f5e9; color:#2e7d32; }
    .task-meta { font-size:11px; color:#aaa; }
    .btn-done   { background:#e8f5e9; color:#2e7d32; border:1px solid #c8e6c9;
                  padding:4px 12px; border-radius:6px; font-size:12px; text-decoration:none; }
    .btn-delete { background:#fde8e8; color:#922; border:1px solid #f5c6c6;
                  padding:4px 12px; border-radius:6px; font-size:12px; text-decoration:none; }
    .empty { text-align:center; padding:32px; color:#aaa; font-size:14px; }
    .stats { background:#fff; border-radius:8px; padding:14px 18px; margin-bottom:20px;
             border:1px solid #dde3ed; display:flex; gap:24px; }
    .stat { text-align:center; }
    .stat-num { font-size:22px; font-weight:700; color:#2E75B6; }
    .stat-lbl { font-size:11px; color:#888; }
    .arch-note { background:#f0f7ff; border:1px solid #b3d4f5; border-radius:6px;
                 padding:10px 14px; margin-bottom:16px; font-size:12px; color:#1a3a5c; }
    .arch-note strong { color:#2E75B6; }
  </style>
</head>
<body>
<div class="wrap">
  <h1>TaskFlow control <span class="badge-layer">v2 layered</span></h1>
  <p class="sub">Daniel's workflow. Hi world!!</p>

  <!-- Architecture note — visible during demo -->
  <div class="arch-note">
    <strong>This request was handled by:</strong>
    app.py (route) connected to TaskService (logic) connected to TaskRepository (data)
  </div>

  <!-- Stats: rendered from StatsObserver output, not calculated here -->
  <div class="stats">
    <div class="stat"><div class="stat-num">{{ stats.total }}</div><div class="stat-lbl">Total</div></div>
    <div class="stat"><div class="stat-num">{{ stats.done_count }}</div><div class="stat-lbl">Done</div></div>
    <div class="stat"><div class="stat-num">{{ stats.pending }}</div><div class="stat-lbl">Pending</div></div>
    <div class="stat"><div class="stat-num">{{ stats.high_count }}</div><div class="stat-lbl">High priority</div></div>
  </div>

  <!-- Add task -->
  <div class="add-form">
    <form method="POST" action="/add">
      <input type="text" name="title" placeholder="What needs to be done?" required>
      <div style="display:flex; align-items:center; gap:8px;">
        <select name="priority">
          <option value="high">High</option>
          <option value="medium" selected>Medium</option>
          <option value="low">Low</option>
        </select>
        <select name="sort">
          <option value="priority"    {{ 'selected' if sort == 'priority' }}>Sort: Priority</option>
          <option value="date"        {{ 'selected' if sort == 'date' }}>Sort: Newest first</option>
          <option value="alphabetical"{{ 'selected' if sort == 'alphabetical' }}>Sort: A to Z</option>
        </select>
        <button type="submit">Add Task</button>
      </div>
    </form>
  </div>

  <!-- Filters -->
  <div class="controls">
    <a href="/?filter=all"     class="{{ 'active' if filter == 'all' }}">All ({{ stats.total }})</a>
    <a href="/?filter=pending" class="{{ 'active' if filter == 'pending' }}">Pending ({{ stats.pending }})</a>
    <a href="/?filter=done"    class="{{ 'active' if filter == 'done' }}">Done ({{ stats.done_count }})</a>
    <a href="/?filter=high"    class="{{ 'active' if filter == 'high' }}">High ({{ stats.high_count }})</a>
  </div>

  <!-- Task list -->
  <ul class="task-list">
    {% for task in tasks %}
    <li class="task {{ 'done' if task.done }}">
      <span class="badge badge-{{ task.priority }}">{{ task.priority }}</span>
      <span class="task-title">{{ task.title }}</span>
      <span class="task-meta">{{ task.created_at }}</span>
      {% if not task.done %}
        <a href="/complete/{{ task.id }}" class="btn-done">Done</a>
      {% endif %}
      <a href="/delete/{{ task.id }}" class="btn-delete">Delete</a>
    </li>
    {% else %}
    <li class="empty">No tasks here.</li>
    {% endfor %}
  </ul>
</div>
</body>
</html>
"""


# ── Routes ────────────────────────────────────────────────────
#
#  Notice: each route does almost nothing.
#  It reads the request, calls the service, returns a response.
#  No logic. No calculations. No data access.
#
#  Compare each of these to the equivalent function in app1.

@app.route("/")
def index():
    filter_by = request.args.get("filter", "all")
    sort_by   = request.args.get("sort",   "priority")

    service.set_sort_strategy(sort_by)               # swap strategy

    tasks = service.get_filtered_tasks(filter_by)    # delegate to service
    stats = service.get_stats()                      # delegate to observer

    return render_template_string(
        TEMPLATE,
        tasks=tasks,
        stats=stats,
        filter=filter_by,
        sort=sort_by,
    )


@app.route("/add", methods=["POST"])
def add_task():
    title    = request.form.get("title", "")
    priority = request.form.get("priority", "medium")
    sort     = request.form.get("sort", "priority")

    service.add_task(title, priority)                # delegate to service

    return redirect(url_for("index", sort=sort))


@app.route("/complete/<int:task_id>")
def complete_task(task_id):
    service.complete_task(task_id)                   # delegate to service
    return redirect(url_for("index"))


@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    service.delete_task(task_id)                     # delegate to service
    return redirect(url_for("index"))


# ── Run ───────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n  TaskFlow v2 runningg  →  http://localhost:5000\n")
    print("  Files in this appp:")
    print("    appp.py        — routes only (you are here)")
    print("    servicess.py   — all business logic")
    print("    repositoryy.py — all data storage")
    print("    modelss.py     — Task class + TaskFactory")
    print("    strategies_and_observerss.py — patterns\n")
import os
app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
