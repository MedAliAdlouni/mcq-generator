"""
Tests for quiz routes
"""
import pytest


class TestGenerateQuiz:
    """Tests for POST /api/quizzes/generate"""

    def test_generate_success(self, authenticated_client, test_document_no_questions, mock_generate_mcq, db_session):
        """Test successful quiz generation"""
        document_id = test_document_no_questions.id
        
        response = authenticated_client.post(
            f"/api/quizzes/generate?document_id={document_id}"
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert "message" in data
        assert "MCQs generated" in data["message"]
        
        # Verify questions were created in database
        from app.models import Question
        questions = db_session.query(Question).filter_by(document_id=document_id).all()
        assert len(questions) == 2  # Mock returns 2 questions
        assert questions[0].question == "What is the capital of France?"

    def test_generate_missing_document_id(self, authenticated_client):
        """Test generation without document_id parameter"""
        response = authenticated_client.post("/api/quizzes/generate")
        
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert "document_id" in data["error"].lower()

    def test_generate_document_not_found(self, authenticated_client):
        """Test generation for non-existent document"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = authenticated_client.post(
            f"/api/quizzes/generate?document_id={fake_id}"
        )
        
        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data
        assert "Document not found" in data["error"]

    def test_generate_already_exists(self, authenticated_client, test_document, mock_generate_mcq):
        """Test generation when questions already exist"""
        document_id = test_document.id
        
        # First generation should work
        response = authenticated_client.post(
            f"/api/quizzes/generate?document_id={document_id}"
        )
        
        # Second generation should fail
        response = authenticated_client.post(
            f"/api/quizzes/generate?document_id={document_id}"
        )
        
        assert response.status_code == 409
        data = response.get_json()
        assert "error" in data
        assert "Already generated" in data["error"]

    def test_generate_empty_questions(self, authenticated_client, test_document_no_questions, mock_generate_mcq_empty):
        """Test generation when LLM returns empty questions"""
        document_id = test_document_no_questions.id
        
        response = authenticated_client.post(
            f"/api/quizzes/generate?document_id={document_id}"
        )
        
        assert response.status_code == 500
        data = response.get_json()
        assert "error" in data
        assert "No question has been generated" in data["error"]

    def test_generate_unauthenticated(self, client, test_document_no_questions):
        """Test generation without authentication"""
        document_id = test_document_no_questions.id
        
        response = client.post(
            f"/api/quizzes/generate?document_id={document_id}",
            follow_redirects=False
        )
        
        assert response.status_code == 302  # Redirect to login

