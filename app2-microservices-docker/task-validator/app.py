# =============================================================
#  task-validator/app.py
#  TaskFlow Microservices — Validator Service
#
#  Unchanged from the plain Python version.
#  PORT is read from the environment so docker-compose
#  can configure it without touching this file.
# =============================================================

from flask import Flask, request, jsonify
import os

app = Flask(__name__)

MAX_TITLE_LENGTH = 120
VALID_PRIORITIES = ("high", "medium", "low")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "task-validator", "version": "2.0"}), 200


@app.route("/validate", methods=["POST"])
def validate():
    data = request.get_json()

    if not data:
        return jsonify({"valid": False, "reason": "No data provided"}), 400

    title    = data.get("title", "").strip()
    priority = data.get("priority", "medium")

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

    return jsonify({"valid": True, "reason": None})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5002))
    print(f"\n  Task Validator running  →  http://localhost:{port}")
    print(f"  Endpoints:")
    print(f"    GET  /health")
    print(f"    POST /validate\n")
    app.run(host="0.0.0.0", port=port, debug=False)
