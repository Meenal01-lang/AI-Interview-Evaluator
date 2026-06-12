from sqlalchemy.orm import Session
from backend.database import models

def create_interview_session(
    db: Session, job_role: str, difficulty_level: str, interview_type: str, num_questions: int
) -> models.InterviewSession:
    """
    Creates a new interview session record.
    """
    session = models.InterviewSession(
        job_role=job_role,
        difficulty_level=difficulty_level,
        interview_type=interview_type,
        num_questions=num_questions
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def get_interview_session(db: Session, session_id: int) -> models.InterviewSession:
    """
    Retrieves a single interview session by ID.
    """
    return db.query(models.InterviewSession).filter(models.InterviewSession.id == session_id).first()

def get_interview_sessions(db: Session, limit: int = 100):
    """
    Retrieves all interview sessions ordered by creation date descending.
    """
    return (
        db.query(models.InterviewSession)
        .order_by(models.InterviewSession.created_at.desc())
        .limit(limit)
        .all()
    )

def create_question(db: Session, session_id: int, question_text: str, order_index: int) -> models.Question:
    """
    Inserts a question linked to an interview session.
    """
    question = models.Question(
        session_id=session_id,
        question_text=question_text,
        order_index=order_index
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question

def create_evaluation(
    db: Session,
    question_id: int,
    user_answer: str,
    time_taken_seconds: int,
    overall_score: float,
    relevance_score: float,
    accuracy_score: float,
    completeness_score: float,
    communication_score: float,
    problem_solving_score: float,
    strengths: str,
    weaknesses: str,
    suggested_answer: str
) -> models.AnswerEvaluation:
    """
    Creates and records a detailed answer evaluation.
    Overwrites previous entries for the same question if present.
    """
    # Delete any existing evaluation for the question first, to prevent duplicates
    existing_eval = db.query(models.AnswerEvaluation).filter(models.AnswerEvaluation.question_id == question_id).first()
    if existing_eval:
        db.delete(existing_eval)
        db.commit()

    evaluation = models.AnswerEvaluation(
        question_id=question_id,
        user_answer=user_answer,
        time_taken_seconds=time_taken_seconds,
        overall_score=overall_score,
        relevance_score=relevance_score,
        accuracy_score=accuracy_score,
        completeness_score=completeness_score,
        communication_score=communication_score,
        problem_solving_score=problem_solving_score,
        strengths=strengths,
        weaknesses=weaknesses,
        suggested_answer=suggested_answer
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)
    return evaluation

def update_session_final_score(db: Session, session_id: int) -> models.InterviewSession:
    """
    Calculates the average score of all evaluated questions in a session
    and saves it as the session's final_score.
    """
    session = get_interview_session(db, session_id)
    if not session:
        return None
    
    scores = []
    for question in session.questions:
        if question.evaluation:
            scores.append(question.evaluation.overall_score)
            
    if scores:
        session.final_score = round(sum(scores) / len(scores), 2)
    else:
        session.final_score = 0.0
        
    db.commit()
    db.refresh(session)
    return session

def update_session_summary(
    db: Session, session_id: int, top_strengths: str, improvement_areas: str
) -> models.InterviewSession:
    """
    Saves the final overall interview session strengths and improvement summaries.
    """
    session = get_interview_session(db, session_id)
    if not session:
        return None
    
    session.top_strengths = top_strengths
    session.improvement_areas = improvement_areas
    
    db.commit()
    db.refresh(session)
    return session
