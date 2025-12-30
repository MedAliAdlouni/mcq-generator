import uuid
import enum

from sqlalchemy import Column, Text, Boolean, DateTime as DateTimeType, ForeignKey, Enum, JSON, Float, Integer
from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from .db import Base


# Enum for the type of questions
class QuestionType(str, enum.Enum):
    qcm = "qcm"
    open_question = "open_question"


# Users Table
class User(Base, UserMixin):
    __tablename__ = "users"

    # Primary key
    id: Mapped[str] = mapped_column(Text, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Other keys
    username: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTimeType, server_default=func.now())

    # Relationships
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    quiz_sessions = relationship("QuizSession", back_populates = "user", cascade="all, delete-orphan")

    # Password setter and checker during registration/login
    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
    

# Document Table
class Document(Base):
    __tablename__ = "documents"

    # Primary key
    id: Mapped[str] = mapped_column(Text, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Other keys
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTimeType, server_default=func.now())

    # Foreign Keys
    user_id = Column(Text, ForeignKey("users.id"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="documents")
    questions = relationship("Question", back_populates="document", cascade="all, delete-orphan")


# Question Table
class Question(Base):
    __tablename__ = "questions"

    # Primary key
    id: Mapped[str] = mapped_column(Text, primary_key=True, default= lambda: str(uuid.uuid4()))

    # Other keys
    type: Mapped[QuestionType] = mapped_column(Enum(QuestionType), nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    choices = Column(JSON, nullable=True)
    answer = Column(Text, nullable=True)

    # Foreign Keys
    document_id = Column(Text, ForeignKey("documents.id"), nullable=False)

    # Relationships
    document = relationship("Document", back_populates="questions")
    results = relationship("Result", back_populates="question", cascade="all, delete-orphan")


# Result Table
class Result(Base):
    __tablename__ = "results"
    
    # Primary key
    id: Mapped[str] = mapped_column(Text, primary_key=True, default= lambda: str(uuid.uuid4()))

    # Other keys
    user_answer = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=True)
    evaluation = Column(Text, nullable=True)
    reviewed_at = Column(DateTimeType, server_default=func.now())

    # Foreign Keys
    question_id = Column(Text, ForeignKey("questions.id"), nullable=False)
    user_id = Column(Text, ForeignKey("users.id"), nullable=True)
    quiz_session_id = Column(Text, ForeignKey("quiz_sessions.id"), nullable=True)

    # Relationships
    question = relationship("Question", back_populates="results")
    quiz_session = relationship("QuizSession", back_populates="results")


# QuizSession Table
class QuizSession(Base):
    __tablename__ = "quiz_sessions"

    # Primary key
    id: Mapped[str] = mapped_column(Text, primary_key=True, default= lambda: str(uuid.uuid4()))

    # Other keys
    score = Column(Float, nullable=False)
    total_questions = Column(Integer, nullable=False)
    played_at = Column(DateTimeType, server_default=func.now())

    # Foreign Keys
    user_id = Column(Text, ForeignKey("users.id"), nullable=True)
    document_id = Column(Text, ForeignKey("documents.id"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="quiz_sessions")
    document = relationship("Document")
    results = relationship("Result", back_populates="quiz_session", cascade="all, delete-orphan") 