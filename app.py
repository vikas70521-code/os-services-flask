"""
OS Services Dashboard - Flask web app (Operating System micro project)
Author : G. Vikas Kumar | B.Tech CSE (AI/ML), Sandip University, Nashik

Run:  python app.py   ->  open http://127.0.0.1:5000
"""
import io
import threading
import traceback
from contextlib import redirect_stdout

from flask import Flask, jsonify, render_template

import services

app = Flask(__name__)
_lock = threading.Lock()          # redirect_stdout is global, so run one demo at a time
_by_id = {s["id"]: s for s in services.SERVICES}


def run_service(sid):
    buf = io.StringIO()
    with _lock, redirect_stdout(buf):
        try:
            _by_id[sid]["fn"]()
            ok = True
        except Exception:
            print(traceback.format_exc())
            ok = False
    return {"id": sid, "title": _by_id[sid]["title"], "ok": ok, "output": buf.getvalue().strip()}


@app.route("/")
def index():
    cards = [{k: v for k, v in s.items() if k != "fn"} for s in services.SERVICES]
    return render_template("index.html", services=cards)


@app.route("/api/run/<sid>")
def api_run(sid):
    if sid not in _by_id:
        return jsonify({"error": "Unknown service"}), 404
    return jsonify(run_service(sid))


@app.route("/api/run-all")
def api_run_all():
    return jsonify([run_service(s["id"]) for s in services.SERVICES])


if __name__ == "__main__":
    try:
        # use_reloader=False: the IPC demo spawns a child process
        app.run(debug=False, use_reloader=False, threaded=True)
    finally:
        services.cleanup()
