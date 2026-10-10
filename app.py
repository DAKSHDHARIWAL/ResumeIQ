

import os
from flask import Flask, render_template, request, jsonify

from resume_parser.analyzer import extract_text, analyze_resume

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/analyze", methods=["POST"])
def analyze():
    if "resume" not in request.files:
        return jsonify({"error": "No resume file uploaded."}), 400

    file = request.files["resume"]
    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type. Please upload a PDF, DOCX, or TXT file."}), 400

    job_description = request.form.get("job_description", "")

    try:
        resume_text = extract_text(file.stream, file.filename)
    except Exception as exc:
        return jsonify({"error": f"Could not read that file: {exc}"}), 400

    if not resume_text or not resume_text.strip():
        return jsonify({"error": "We couldn't extract any text from that file. If it's a scanned image PDF, try a text-based export instead."}), 400

    result = analyze_resume(resume_text, job_description)
    result["filename"] = file.filename
    return jsonify(result)


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)