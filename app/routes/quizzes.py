import uuid
from flask import Blueprint, request, jsonify
from flask_login import login_required
from ..db import LocalSession
from ..models import Document, Question, QuestionType
from ..core.llm import generate_mcq

bp = Blueprint("quizzes", __name__, url_prefix="/api/quizzes")


@bp.route("/generate", methods=["POST"])
@login_required
def generate_quiz():
    document_id = request.args.get("document_id")
    if not document_id:
        return jsonify({"error": "Parameter 'document_id' required!"}), 400

    session = LocalSession()
    try:
        document = session.get(Document, document_id)
        if not document:
            return jsonify({"error": "Document not found"}), 404

        existing = session.query(Question).filter_by(document_id=document_id).first()
        if existing:
            return jsonify({"error": "Already generated MCQs for this document."}), 409

        # call with correct kwarg name
        questions = generate_mcq(document.content, nb_questions=10)
        if not questions:
            return jsonify({"error": "No question has been generated"}), 500

        for q in questions:
            question = Question(
                id=str(uuid.uuid4()),
                type=QuestionType.qcm,
                document_id=document.id,
                question=q.get("question", "") or "",
                choices=q.get("answers"),
                answer=q.get("correct_answer"),
            )
            session.add(question)
        session.commit()
        return jsonify({"message": f"{len(questions)} MCQs generated"}), 201

    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        session.close()