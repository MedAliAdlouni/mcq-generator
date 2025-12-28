from flask import Flask, jsonify, request
from io import BytesIO

from core.extraction import extract_text_from_file
from core.llm import generate_mcq

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/generate_mcq", methods=["POST"])
def generate_mcq_from_text():
    data = request.get_json(silent=True)

    if not data or "text" not in data:
        return jsonify({"error": "Missing 'text' in request body"}), 400

    text = data["text"]
    nb_questions = data.get("nb_questions", 5)

    mcqs = generate_mcq(text, nb_questions)

    return jsonify({"mcqs": mcqs})



@app.route("/generate_mcq_file", methods=["POST"])
def generate_mcq_from_file():
    if "file" not in request.files:
        return jsonify({"error": "Missing file in request"}), 400

    file = request.files["file"]

    if not file.filename:
        return jsonify({"error": "Empty filename"}), 400
    
    binary_stream = BytesIO(file.filename.read())
    text = extract_text_from_file(binary_stream)

    nb_questions = request.form.get("nb_questions", 5)

    mcqs = generate_mcq(text, nb_questions)

    return jsonify({"mcqs": mcqs})


if __name__ == "__main__":
    app.run(debug=True)