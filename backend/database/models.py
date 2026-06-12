import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database.connection import Base

class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    job_role = Column(String(100), nullable=False)
    difficulty_level = Column(String(50), nullable=False)
    interview_type = Column(String(50), nullable=False)
    num_questions = Column(Integer, nullable=False)
    
    # Overall summary metrics calculated upon completion
    final_score = Column(Float, nullable=True)
    top_strengths = Column(Text, nullable=True)     # Semicolon-separated overall strengths
    improvement_areas = Column(Text, nullable=True)  # Semicolon-separated overall weaknesses

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    questions = relationship("Question", back_populates="session", cascade="all, delete-orphan", order_by="Question.order_index")

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False)
    order_index = Column(Integer, nullable=False)

    # Relationships
    session = relationship("InterviewSession", back_populates="questions")
    evaluation = relationship(
        "AnswerEvaluation", 
        back_populates="question", 
        uselist=False, 
        cascade="all, delete-orphan"
    )

class AnswerEvaluation(Base):
    __tablename__ = "answer_evaluations"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), unique=True, nullable=False)
    user_answer = Column(Text, nullable=False)
    time_taken_seconds = Column(Integer, nullable=False)  # Seconds spent answering
    overall_score = Column(Float, nullable=False)
    
    # Core dimension scores (0-10)
    relevance_score = Column(Float, nullable=False)
    accuracy_score = Column(Float, nullable=False)
    completeness_score = Column(Float, nullable=False)
    communication_score = Column(Float, nullable=False)
    problem_solving_score = Column(Float, nullable=False)
    
    # Structured verbal critique
    strengths = Column(Text, nullable=False)  # Semicolon-separated bullet strengths
    weaknesses = Column(Text, nullable=False) # Semicolon-separated bullet weaknesses
    suggested_answer = Column(Text, nullable=False)
    evaluated_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    question = relationship("Question", back_populates="evaluation")
