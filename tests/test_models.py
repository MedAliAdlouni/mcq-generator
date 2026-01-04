"""
Tests for database models
"""
import pytest
from app.models import User, Document, Question, QuizSession, Result, QuestionType


class TestUserModel:
    """Tests for User model"""

    def test_user_creation(self, db_session):
        """Test creating a user"""
        user = User(
            username="testuser",
            email="test@example.com"
        )
        user.set_password("password123")
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password_hash != "password123"  # Should be hashed

    def test_user_password_hashing(self, db_session):
        """Test password hashing"""
        user = User(username="testuser", email="test@example.com")
        user.set_password("mypassword")
        db_session.add(user)
        db_session.commit()
        
        # Password should be hashed
        assert user.password_hash != "mypassword"
        assert len(user.password_hash) > 20  # Hashed passwords are long
        
        # Should verify correctly
        assert user.check_password("mypassword") is True
        assert user.check_password("wrongpassword") is False

    def test_user_unique_username(self, db_session, test_user):
        """Test username uniqueness constraint"""
        duplicate_user = User(
            username=test_user.username,  # Same username
            email="different@example.com"
        )
        duplicate_user.set_password("password123")
        db_session.add(duplicate_user)
        
        with pytest.raises(Exception):  # Should raise IntegrityError
            db_session.commit()

    def test_user_unique_email(self, db_session, test_user):
        """Test email uniqueness constraint"""
        duplicate_user = User(
            username="differentuser",
            email=test_user.email  # Same email
        )
        duplicate_user.set_password("password123")
        db_session.add(duplicate_user)
        
        with pytest.raises(Exception):  # Should raise IntegrityError
            db_session.commit()

    def test_user_documents_relationship(self, db_session, test_user):
        """Test user-documents relationship"""
        document = Document(
            title="Test Doc",
            content="Content",
            user_id=test_user.id
        )
        db_session.add(document)
        db_session.commit()
        
        assert len(test_user.documents) == 1
        assert test_user.documents[0].title == "Test Doc"

    def test_user_quiz_sessions_relationship(self, db_session, test_user, test_document):
        """Test user-quiz_sessions relationship"""
        quiz_session = QuizSession(
            user_id=test_user.id,
            document_id=test_document.id,
            score=85.5,
            total_questions=10
        )
        db_session.add(quiz_session)
        db_session.commit()
        
        assert len(test_user.quiz_sessions) == 1
        assert test_user.quiz_sessions[0].score == 85.5


class TestDocumentModel:
    """Tests for Document model"""

    def test_document_creation(self, db_session, test_user):
        """Test creating a document"""
        document = Document(
            title="My Document",
            content="Document content here",
            user_id=test_user.id
        )
        db_session.add(document)
        db_session.commit()
        
        assert document.id is not None
        assert document.title == "My Document"
        assert document.content == "Document content here"
        assert document.user_id == test_user.id

    def test_document_user_relationship(self, db_session, test_user):
        """Test document-user relationship"""
        document = Document(
            title="Test Doc",
            content="Content",
            user_id=test_user.id
        )
        db_session.add(document)
        db_session.commit()
        
        assert document.user.id == test_user.id
        assert document.user.username == test_user.username

    def test_document_questions_relationship(self, db_session, test_user):
        """Test document-questions relationship"""
        document = Document(
            title="Test Doc",
            content="Content",
            user_id=test_user.id
        )
        db_session.add(document)
        db_session.commit()
        
        question = Question(
            type=QuestionType.qcm,
            question="Test question?",
            choices=["A", "B", "C", "D"],
            answer="A",
            document_id=document.id
        )
        db_session.add(question)
        db_session.commit()
        
        assert len(document.questions) == 1
        assert document.questions[0].question == "Test question?"


class TestQuestionModel:
    """Tests for Question model"""

    def test_question_creation(self, db_session, test_document):
        """Test creating a question"""
        question = Question(
            type=QuestionType.qcm,
            question="What is 2+2?",
            choices=["3", "4", "5", "6"],
            answer="4",
            document_id=test_document.id
        )
        db_session.add(question)
        db_session.commit()
        
        assert question.id is not None
        assert question.type == QuestionType.qcm
        assert question.question == "What is 2+2?"
        assert question.choices == ["3", "4", "5", "6"]
        assert question.answer == "4"
        assert question.document_id == test_document.id

    def test_question_type_enum(self, db_session, test_document):
        """Test QuestionType enum"""
        qcm_question = Question(
            type=QuestionType.qcm,
            question="QCM question?",
            choices=["A", "B"],
            answer="A",
            document_id=test_document.id
        )
        db_session.add(qcm_question)
        db_session.commit()
        
        assert qcm_question.type == QuestionType.qcm
        assert qcm_question.type.value == "qcm"

    def test_question_choices_json(self, db_session, test_document):
        """Test that choices are stored as JSON"""
        choices = ["Option 1", "Option 2", "Option 3", "Option 4"]
        question = Question(
            type=QuestionType.qcm,
            question="Test?",
            choices=choices,
            answer="Option 1",
            document_id=test_document.id
        )
        db_session.add(question)
        db_session.commit()
        db_session.refresh(question)
        
        assert question.choices == choices
        assert isinstance(question.choices, list)

    def test_question_document_relationship(self, db_session, test_document):
        """Test question-document relationship"""
        question = Question(
            type=QuestionType.qcm,
            question="Test?",
            choices=["A", "B"],
            answer="A",
            document_id=test_document.id
        )
        db_session.add(question)
        db_session.commit()
        
        assert question.document.id == test_document.id
        assert question.document.title == test_document.title


class TestQuizSessionModel:
    """Tests for QuizSession model"""

    def test_quiz_session_creation(self, db_session, test_user, test_document):
        """Test creating a quiz session"""
        quiz_session = QuizSession(
            user_id=test_user.id,
            document_id=test_document.id,
            score=75.0,
            total_questions=10
        )
        db_session.add(quiz_session)
        db_session.commit()
        
        assert quiz_session.id is not None
        assert quiz_session.user_id == test_user.id
        assert quiz_session.document_id == test_document.id
        assert quiz_session.score == 75.0
        assert quiz_session.total_questions == 10

    def test_quiz_session_relationships(self, db_session, test_user, test_document):
        """Test quiz session relationships"""
        quiz_session = QuizSession(
            user_id=test_user.id,
            document_id=test_document.id,
            score=80.0,
            total_questions=10
        )
        db_session.add(quiz_session)
        db_session.commit()
        
        assert quiz_session.user.id == test_user.id
        assert quiz_session.document.id == test_document.id


class TestResultModel:
    """Tests for Result model"""

    def test_result_creation(self, db_session, test_user, test_questions):
        """Test creating a result"""
        question = test_questions[0]
        result = Result(
            question_id=question.id,
            user_id=test_user.id,
            user_answer="Option A",
            is_correct=True
        )
        db_session.add(result)
        db_session.commit()
        
        assert result.id is not None
        assert result.question_id == question.id
        assert result.user_id == test_user.id
        assert result.user_answer == "Option A"
        assert result.is_correct is True

    def test_result_relationships(self, db_session, test_user, test_questions):
        """Test result relationships"""
        question = test_questions[0]
        result = Result(
            question_id=question.id,
            user_id=test_user.id,
            user_answer="Option A",
            is_correct=True
        )
        db_session.add(result)
        db_session.commit()
        
        assert result.question.id == question.id
        assert result.question.question == question.question

