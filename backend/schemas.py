from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

# Requests
class InterviewSetupRequest(BaseModel):
    job_role: str = Field(..., description="Target job role for the interview")
    difficulty_level: str = Field(..., description="Experience/difficulty level")
    interview_type: str = Field(..., description="Interview focus area (Technical, HR, Behavioral)")
    num_questions: int = Field(default=3, ge=1, le=10, description="Total questions to generate")

class AnswerSubmitRequest(BaseModel):
    user_answer: str = Field(..., min_length=1, description="The user's response to the question (cannot be empty)")
    time_taken_seconds: int = Field(..., ge=1, description="Time in seconds the user spent on this question")

# DB Representations
class AnswerEvaluationBase(BaseModel):
    id: int
    question_id: int
    user_answer: str
    time_taken_seconds: int
    overall_score: float
    relevance_score: float
    accuracy_score: float
    completeness_score: float
    communication_score: float
    problem_solving_score: float
    strengths: str
    weaknesses: str
    suggested_answer: str
    evaluated_at: datetime

    class Config:
        from_attributes = True

class QuestionBase(BaseModel):
    id: int
    session_id: int
    question_text: str
    order_index: int
    evaluation: Optional[AnswerEvaluationBase] = None

    class Config:
        from_attributes = True

class InterviewSessionBase(BaseModel):
    id: int
    job_role: str
    difficulty_level: str
    interview_type: str
    num_questions: int
    final_score: Optional[float] = None
    top_strengths: Optional[str] = None
    improvement_areas: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Detailed response schemas (including nested details)
class DetailedSessionResponse(InterviewSessionBase):
    questions: List[QuestionBase] = []

    class Config:
        from_attributes = True
