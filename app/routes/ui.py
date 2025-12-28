from flask import Blueprint, render_template, jsonify, request
from sqlalchemy.orm import joinedload
from flask_login import login_required, current_user

from ..db import LocalSession
from ..models import Document, QuizSession, Question

bp = Blueprint("ui", __name__)

@bp.route("/")
def home():
    return render_template("home.html")

@bp.route("/documents")
@login_required
def show_documents():
    with LocalSession() as session:
        docs = (
            session.query(Document)
            .options(joinedload(Document.questions))
            .filter_by(user_id=current_user.id)
            .order_by(Document.created_at.desc())
            .all()
        )

        return render_template("documents.html", documents=docs)
    
@bp.route("/upload")
@login_required
def upload():
    return render_template("upload.html")

@bp.route("/quizzes/<string:document_id>")
@login_required
def show_quiz(document_id):
    with LocalSession() as session:
        document = session.get(Document, document_id)
        if not document:
            return render_template("404.html", message="Document unfound"), 404
        questions = session.query(Question).filter_by(document_id=document_id).all()

    return render_template("quiz.html", quiz_title=document.title, questions=questions)


@bp.route("/quizzes/play/<string:document_id>")
@login_required
def play_quiz(document_id):
    from random import sample

    with LocalSession() as session:
        document = session.get(Document, document_id)
        if not document:
            return render_template("404.html", message="Unfound document"), 404

        questions = session.query(Question).filter_by(document_id=document_id).all()

    if not questions:
        return render_template(
            "quiz_play.html",
            title=document.title,
            document=document,
            questions=[],
            message="No question has been generated for this document"
        )

    if len(questions) > 9:
        questions = sample(questions, 9)

    questions_data = [
        {
            "id": q.id,
            "question": q.question,
            "type": q.type.value if hasattr(q.type, "value") else q.type,
            "choices": q.choices,
            "answer": q.answer,
            "explanation": getattr(q, "explanation", None)
        }
        for q in questions
    ]

    return render_template(
        "quiz_play.html",
        title=document.title,
        document=document,
        questions=questions_data
    )


@bp.route("/results")
@login_required
def show_results():
    """HTML Page for results visualization
    """
    with LocalSession() as session:
        documents = (
            session.query(Document)
            .filter_by(user_id=current_user.id)
            .order_by(Document.created_at.desc())
            .all()
        )
    return render_template("results.html", documents=documents)


@bp.route("/api/results/data", methods=["GET"])
@login_required
def get_results_data():
    """Send scoring data per document (for graphic)
    """
    document_id = request.args.get("document_id")
    if not document_id:
        return jsonify({"error": "Document not found"}), 400
    with LocalSession() as session:
        sessions = (
            session.query(QuizSession)
            .filter_by(user_id=current_user.id, document_id=document_id)
            .order_by(QuizSession.played_at.asc())
            .all()
        )
    
    data = [
        {
            "played_at": s.played_at.strftime("%Y-%m-%d %H:%M"),
            "score": s.score
        }
        for s in sessions
    ]
    return jsonify(data)