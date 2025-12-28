import os
import uuid
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from ..db import LocalSession
from ..models import Document
from ..core.extraction import extract_text_from_file

bp = Blueprint("documents", __name__, url_prefix="/api/documents")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@bp.route("/upload", methods=["POST"])
@login_required
def upload_document():
    """Upload file, extract text from it and save it in the database.
       The document is associated to the connected user
    """
    # Step 1 : Get and validate the file
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file sent"}), 400
    filename = secure_filename(file.filename)

    # Step 2: Save file
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    # Step 3: extract text
    try:
        content = extract_text_from_file(file_path)
    except Exception as e:
        return jsonify({"error": f"Could not extract text: {str(e)}"}), 500

    # Step 4: database operations
    try:
        with LocalSession() as session:
            document = Document(
                id=str(uuid.uuid4()),
                title=filename,
                content=content,
                user_id=current_user.id,
            )
            session.add(document)
            session.commit()

            return jsonify({
                "message": "Document loaded successfully",
                "document_id": document.id,
                "title": document.title
            }), 201

    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500


@bp.route("/<string:document_id>", methods=["DELETE"])
@login_required
def delete_document(document_id):
    session = LocalSession()
    try:
        document = session.get(Document, document_id)
        if not document:
            return jsonify({"error": f"Not found"}), 404
        if current_user.id != document.user_id:
            return jsonify({"error": "Not authorized"}), 403
        
        session.delete(document)
        session.commit()
        
        return jsonify({"message": f"Document deleted from database"}), 200

    except Exception as e:
        session.rollback()
        return jsonify({"error": f"{str(e)}"}), 500
    finally:
        session.close()