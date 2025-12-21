import sys
from io import BytesIO
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from flask import Flask, request, jsonify
from core.extraction import extract_text_from_file
from core.llm import generate_mcq


app = Flask(__name__)

# -------------------------
# Endpoint 1: Generate MCQs from raw text
# -------------------------
@app.route("/generate_mcq", methods=["POST"])
def generate_mcq_from_text():
    data = request.get_json(silent=True)
    if not data or "text" not in data:
        return jsonify({"error": "Missing 'text' in request body"}), 400

    text = data["text"]
    nb_questions = data.get("nb_questions", 5)

    mcqs = generate_mcq(text, nb_questions=nb_questions)
    return jsonify({"mcqs": mcqs})


# -------------------------
# Endpoint 2: Generate MCQs from uploaded file
# -------------------------
@app.route("/generate_mcq_file", methods=["POST"])
def generate_mcq_from_file():
    if "file" not in request.files:
        return jsonify({"error": "Missing file in request"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Emtpy filename"}), 400
    
    # Ensure it's a readable binary stream
    binary_stream = BytesIO(file.read())
    binary_stream.seek(0)

    text = extract_text_from_file(binary_stream)
    nb_questions = int(request.form.get("nb_questions", 5))

    mcqs = generate_mcq(text, nb_questions=nb_questions)
    return jsonify({"mcqs": mcqs})


# -------------------------
# Health check endpoint
# -------------------------
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})


# -------------------------
# Run the app
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
