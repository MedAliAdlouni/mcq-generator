import uuid
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user  # type: ignore[import-untyped]

from ..db import LocalSession
from ..models import Result, QuizSession

bp = Blueprint("results", __name__, url_prefix="/api/results")

@bp.route("/save", methods=["POST"])
@login_required
def save_results():
    """Save detailed results of the quiz and create new gloabl QuizSession
    """
    data = request.get_json() or {}
    document_id = data.get("document_id")
    answers = data.get("answers", [])
    score = data.get("score")

    if not answers or not document_id or not score:
        return jsonify({"error": "Incomplete data"}), 400
    
    session = LocalSession()
    try:
        # create gloabl quiz session
        quiz_session = QuizSession(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            document_id=document_id,
            score=score,
            total_questions=len(answers)
        )
        session.add(quiz_session)
        session.flush()

        # save each result individually
        for item in answers:
            question_id = item.get("question_id")
            user_answer = item.get("user_answer", "")
            is_correct = item.get("is_correct", False)

            if not question_id:
                continue
            
            result = Result(
                id=str(uuid.uuid4()),
                question_id=question_id,
                user_id= current_user.id,
                user_answer=user_answer,
                is_correct=is_correct,
            )
            session.add(result)
        session.commit()

        return jsonify({
            "message": "Saved results",
            "score": score,
            "document_id": document_id,
            "quiz_session_id": quiz_session.id
            }), 201
    
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()
    
