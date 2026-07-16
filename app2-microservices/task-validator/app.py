# =============================================================
#  task-validator/app.py
#  TaskFlow Microservices — Validator Service
#
#  Runs on port 5002.
#  One job: receive a task and decide if it is valid.
#  Returns JSON. Knows nothing about the intake service.
#
#  This is a microservice. It has:
#    - One responsibility (validation only)
#    - Its own process and port
#    - No shared state with any other service
#    - A clean REST interface
# =============================================================

from flask import Flask, request, jsonify
import time
import os

app = Flask(__name__)

# ── Validation rules ──────────────────────────────────────────
# All business rules about what makes a task valid live here.
# If rules change, only this service changes.

MAX_TITLE_LENGTH = 120
VALID_PRIORITIES = ("high", "medium", "low")


@app.route("/health", methods=["GET"])
def health():
    """
    Health check endpoint.
    The intake service uses this to confirm the validator is alive.
    Standard practice for microservices — every service exposes /health.
    """
    return jsonify({"status": "ok", "service": "task-validator"}), 200


@app.route("/validate", methods=["POST"])
def validate():
    """
    Validates a task before it is created.

    Expects JSON:
        { "title": "...", "priority": "..." }

    Returns JSON:
        { "valid": true/false, "reason": "..." or null }
    """
    data = request.get_json()

    if not data:
        return jsonify({"valid": False, "reason": "No data provided"}), 400

    title    = data.get("title", "").strip()
    priority = data.get("priority", "medium")

    # ── validation rules ──────────────────────────────────────

    if not title:
        return jsonify({"valid": False, "reason": "Title cannot be empty"})

    if len(title) > MAX_TITLE_LENGTH:
        return jsonify({
            "valid": False,
            "reason": f"Title exceeds {MAX_TITLE_LENGTH} characters"
        })

    if priority not in VALID_PRIORITIES:
        return jsonify({
            "valid": False,
            "reason": f"Priority must be one of: {', '.join(VALID_PRIORITIES)}"
        })

    # ── all rules passed ──────────────────────────────────────
    return jsonify({"valid": True, "reason": None})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5002))
    print(f"\n  Task Validator running  →  http://localhost:{port}")
    print(f"  Endpoints:")
    print(f"    GET  /health    — confirm service is alive")
    print(f"    POST /validate  — validate a task\n")
    app.run(host="0.0.0.0", port=port, debug=True)
