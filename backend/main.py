import json
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

# Database imports
from backend.database.connection import engine, Base, get_db
from backend.database import crud, models
from backend import schemas
from backend.services.question_service import generate_questions
from backend.services.evaluation_service import evaluate_answer, generate_overall_summary
from backend.config import settings

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Interview & Evaluation API",
    description="Backend API powering the AI Interview Question Generator and Evaluation System",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health", status_code=status.HTTP_200_OK)
def health_check():
    """
    Checks backend server availability, database state, and mode configurations.
    """
    return {
        "status": "healthy",
        "service": "interview-evaluation-api",
        "demo_mode": settings.DEMO_MODE,
        "gemini_api_configured": bool(settings.GEMINI_API_KEY)
    }

@app.post("/api/interviews", response_model=schemas.DetailedSessionResponse, status_code=status.HTTP_201_CREATED)
def start_interview_session(
    request: schemas.InterviewSetupRequest, 
    db: Session = Depends(get_db)
):
    """
    Sets up a new interview session.
    Generates questions using Gemini SDK (or seeds in Demo mode) and stores them in DB.
    """
    # Validation checks
    valid_roles = ["Software Engineer", "AIML Engineer", "Data Analyst", "Cloud Engineer", "Full Stack Developer"]
    if request.job_role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported job role. Supported roles: {', '.join(valid_roles)}"
        )

    valid_types = ["Technical", "Behavioral", "HR"]
    if request.interview_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported interview type. Supported types: {', '.join(valid_types)}"
        )

    try:
        # 1. Create the session record
        session = crud.create_interview_session(
            db=db,
            job_role=request.job_role,
            difficulty_level=request.difficulty_level,
            interview_type=request.interview_type,
            num_questions=request.num_questions
        )
        
        # 2. Generate questions based on session criteria
        questions = generate_questions(
            job_role=session.job_role,
            difficulty_level=session.difficulty_level,
            interview_type=session.interview_type,
            num_questions=session.num_questions
        )
        
        if not questions:
            raise Exception("Failed to generate questions.")

        # 3. Save questions to DB
        for idx, q_text in enumerate(questions):
            crud.create_question(
                db=db,
                session_id=session.id,
                question_text=q_text,
                order_index=idx
            )
            
        # 4. Refresh session to include new questions
        db.refresh(session)
        return session
    except Exception as e:
        # Clean up session if question generation crashed during startup
        if 'session' in locals():
            db.delete(session)
            db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize interview session: {str(e)}"
        )

@app.get("/api/interviews", response_model=List[schemas.InterviewSessionBase])
def list_interviews(db: Session = Depends(get_db)):
    """
    Lists past interview session headers for history logs.
    """
    return crud.get_interview_sessions(db=db)

@app.get("/api/interviews/{session_id}", response_model=schemas.DetailedSessionResponse)
def get_interview_details(session_id: int, db: Session = Depends(get_db)):
    """
    Retrieves full details of a session, including questions, answers, and evaluations.
    """
    session = crud.get_interview_session(db=db, session_id=session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview session with ID {session_id} not found."
        )
    return session

@app.post("/api/interviews/{session_id}/questions/{question_id}/answer", response_model=schemas.AnswerEvaluationBase)
def submit_question_answer(
    session_id: int,
    question_id: int,
    payload: schemas.AnswerSubmitRequest,
    db: Session = Depends(get_db)
):
    """
    Submits an answer for a specific question.
    Runs evaluation, updates score, checks if interview is complete, and if so,
    auto-generates the overall interview strengths and weaknesses summary.
    """
    # 1. Error checking: Empty answers
    if not payload.user_answer.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Answer cannot be empty or solely whitespace."
        )

    # 2. Error checking: Valid session
    session = crud.get_interview_session(db=db, session_id=session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview session with ID {session_id} not found."
        )
        
    # 3. Error checking: Valid question under session
    question = next((q for q in session.questions if q.id == question_id), None)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {question_id} not found under session {session_id}."
        )
        
    try:
        # 4. Trigger Answer Evaluation Service
        eval_res = evaluate_answer(
            job_role=session.job_role,
            difficulty_level=session.difficulty_level,
            interview_type=session.interview_type,
            question_text=question.question_text,
            user_answer=payload.user_answer
        )
        
        # 5. Format strengths and weaknesses lists to semicolon-delimited strings
        strengths_str = "; ".join(eval_res.get("strengths", []))
        weaknesses_str = "; ".join(eval_res.get("weaknesses", []))
        
        # 6. Save evaluation record
        evaluation = crud.create_evaluation(
            db=db,
            question_id=question_id,
            user_answer=payload.user_answer,
            time_taken_seconds=payload.time_taken_seconds,
            overall_score=eval_res["overall_score"],
            relevance_score=eval_res["relevance_score"],
            accuracy_score=eval_res["accuracy_score"],
            completeness_score=eval_res["completeness_score"],
            communication_score=eval_res["communication_score"],
            problem_solving_score=eval_res["problem_solving_score"],
            strengths=strengths_str,
            weaknesses=weaknesses_str,
            suggested_answer=eval_res["suggested_answer"]
        )
        
        # 7. Recalculate and update session average final score
        crud.update_session_final_score(db=db, session_id=session_id)
        
        # 8. Check if this is the final question of the session
        # Check how many questions now have evaluations
        db.refresh(session)
        evaluated_count = sum(1 for q in session.questions if q.evaluation is not None)
        
        if evaluated_count == session.num_questions:
            # Generate the overall session summary
            # We serialize the session details into a helper dictionary to avoid session mapping errors
            session_summary_payload = {
                "job_role": session.job_role,
                "difficulty_level": session.difficulty_level,
                "interview_type": session.interview_type,
                "questions": [
                    {
                        "question_text": q.question_text,
                        "evaluation": {
                            "user_answer": q.evaluation.user_answer,
                            "overall_score": q.evaluation.overall_score,
                            "strengths": q.evaluation.strengths,
                            "weaknesses": q.evaluation.weaknesses
                        }
                    } for q in session.questions
                ]
            }
            
            summary_res = generate_overall_summary(session_summary_payload)
            
            # Save summaries
            top_strengths_str = "; ".join(summary_res.get("top_strengths", []))
            improvement_areas_str = "; ".join(summary_res.get("improvement_areas", []))
            
            crud.update_session_summary(
                db=db,
                session_id=session_id,
                top_strengths=top_strengths_str,
                improvement_areas=improvement_areas_str
            )
        
        return evaluation
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to evaluate answer and score: {str(e)}"
        )
