"""REST API endpoints."""
from flask import Blueprint, jsonify, request

from config import Config
from nlp.analyzer import analyze_resume
from nlp.data_store import store
from nlp.extractor import extract_text

api = Blueprint("api", __name__)


@api.get("/health")
def health():
    return jsonify({"status": "ok", "service": "ai-resume-analyzer"})


@api.get("/stats")
def stats():
    """Dataset statistics for the dashboard/landing page."""
    return jsonify(store.stats())


@api.get("/roles")
def roles():
    """Distinct target roles the user can select for gap analysis."""
    return jsonify({"roles": store.roles()})


@api.post("/analyze")
def analyze():
    """Analyze a resume supplied as a file upload or raw text.

    Accepts either:
      - multipart/form-data with a `resume` file (and optional `target_role`)
      - application/json with `{ "text": "...", "target_role": "..." }`
    """
    target_role = None
    text = ""

    if "resume" in request.files:
        f = request.files["resume"]
        if not f.filename:
            return jsonify({"error": "No file selected."}), 400
        ext = f.filename.rsplit(".", 1)[-1].lower()
        if ext not in Config.ALLOWED_EXTENSIONS:
            return jsonify({"error": "Unsupported file type. Use PDF, DOCX or TXT."}), 400
        try:
            text = extract_text(f.stream, f.filename)
        except Exception as exc:  # noqa: BLE001
            return jsonify({"error": f"Could not read file: {exc}"}), 400
        target_role = request.form.get("target_role") or None
    else:
        data = request.get_json(silent=True) or {}
        text = (data.get("text") or "").strip()
        target_role = data.get("target_role") or None

    if not text or len(text) < 30:
        return jsonify({"error": "Resume text is empty or too short to analyze."}), 400

    result = analyze_resume(text, target_role=target_role)
    return jsonify(result)
