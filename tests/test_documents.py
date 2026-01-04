"""
Tests for document routes
"""
import pytest
import os
from pathlib import Path


class TestUploadDocument:
    """Tests for POST /api/documents/upload"""

    def test_upload_success(self, authenticated_client, sample_pdf_file, mock_extract_text, db_session):
        """Test successful document upload"""
        with open(sample_pdf_file, "rb") as f:
            response = authenticated_client.post(
                "/api/documents/upload",
                data={"file": (f, "sample.pdf")},
                content_type="multipart/form-data"
            )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data["message"] == "Document loaded successfully"
        assert "document_id" in data
        assert data["title"] == "sample.pdf"
        
        # Verify document was saved in database
        from app.models import Document
        document = db_session.get(Document, data["document_id"])
        assert document is not None
        assert document.title == "sample.pdf"

    def test_upload_docx(self, authenticated_client, sample_docx_file, mock_extract_text, db_session):
        """Test uploading DOCX file"""
        with open(sample_docx_file, "rb") as f:
            response = authenticated_client.post(
                "/api/documents/upload",
                data={"file": (f, "sample.docx")},
                content_type="multipart/form-data"
            )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data["title"] == "sample.docx"

    def test_upload_missing_file(self, authenticated_client):
        """Test upload without file"""
        response = authenticated_client.post("/api/documents/upload")
        
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert "No file sent" in data["error"]

    def test_upload_unauthenticated(self, client, sample_pdf_file):
        """Test upload without authentication"""
        with open(sample_pdf_file, "rb") as f:
            response = client.post(
                "/api/documents/upload",
                data={"file": (f, "sample.pdf")},
                content_type="multipart/form-data",
                follow_redirects=False
            )
        
        assert response.status_code == 302  # Redirect to login

    def test_upload_extraction_error(self, authenticated_client, tmp_path):
        """Test upload when text extraction fails"""
        # Create an invalid file
        invalid_file = tmp_path / "invalid.txt"
        invalid_file.write_text("This might cause extraction issues")
        
        # Mock extraction to raise an error
        from unittest.mock import patch
        with patch("app.routes.documents.extract_text_from_file", side_effect=Exception("Extraction failed")):
            with open(invalid_file, "rb") as f:
                response = authenticated_client.post(
                    "/api/documents/upload",
                    data={"file": (f, "invalid.txt")},
                    content_type="multipart/form-data"
                )
            
            assert response.status_code == 500
            data = response.get_json()
            assert "error" in data
            assert "Could not extract text" in data["error"]


class TestDeleteDocument:
    """Tests for DELETE /api/documents/<document_id>"""

    def test_delete_success(self, authenticated_client, test_document, app):
        """Test successful document deletion"""
        document_id = test_document.id
        
        response = authenticated_client.delete(f"/api/documents/{document_id}")
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["message"] == "Document deleted from database"
        
        # Verify document was deleted using a new session
        from app.models import Document
        from app.db import LocalSession
        with app.app_context():
            session = LocalSession()
            try:
                document = session.get(Document, document_id)
                assert document is None
            finally:
                session.close()

    def test_delete_not_found(self, authenticated_client):
        """Test deletion of non-existent document"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = authenticated_client.delete(f"/api/documents/{fake_id}")
        
        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data
        assert "Not found" in data["error"]

    def test_delete_unauthorized(self, client, test_user2, test_document, db_session):
        """Test deletion of another user's document"""
        # Login as user2
        login_response = client.post("/auth/login", data={
            "email": test_user2.email,
            "password": "testpassword123"
        }, follow_redirects=False)
        assert login_response.status_code in [200, 302]
        
        # Try to delete user1's document
        response = client.delete(f"/api/documents/{test_document.id}")
        
        assert response.status_code == 403
        data = response.get_json()
        assert "error" in data
        assert "Not authorized" in data["error"]
        
        # Verify document still exists
        from app.models import Document
        document = db_session.get(Document, test_document.id)
        assert document is not None

    def test_delete_unauthenticated(self, client, test_document):
        """Test deletion without authentication"""
        response = client.delete(f"/api/documents/{test_document.id}", follow_redirects=False)
        
        assert response.status_code == 302  # Redirect to login

