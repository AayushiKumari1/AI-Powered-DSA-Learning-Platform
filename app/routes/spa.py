"""Serves the built React frontend (frontend/dist) at /app/*.

Build it with:  cd frontend && npm install && npm run build
During development run `npm run dev` instead (Vite on :5173 proxies API calls to Flask).
"""
import os
from flask import Blueprint, send_from_directory, abort

DIST = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
spa_bp = Blueprint("spa", __name__)


@spa_bp.route("/app/", defaults={"path": ""})
@spa_bp.route("/app/<path:path>")
def react_app(path):
    if not os.path.isdir(DIST):
        return ("React build not found. Run: cd frontend && npm install && npm run build "
                "(or use `npm run dev` and open http://localhost:5173/app/).", 503)
    full = os.path.join(DIST, path)
    if path and os.path.isfile(full):
        return send_from_directory(DIST, path)
    if "." in os.path.basename(path):
        abort(404)
    return send_from_directory(DIST, "index.html")   # client-side routes
