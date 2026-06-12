import sys
import os

# Set Python path to project root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database.connection import engine, Base, SessionLocal
from backend.database import crud
from backend.services.question_service import generate_questions
from backend.services.evaluation_service import evaluate_answer, generate_overall_summary

def run_tests():
    print("🚀 Starting AI Interview System self-check...")
    
    # 1. Initialize Tables
    print("1. Initializing SQLite tables...")
    try:
        # Create all tables (will drop/overwrite if necessary, but here we just create them)
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables successfully created.")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

    # 2. Test DB write & read operations
    print("2. Testing DB CRUD operations...")
    db = SessionLocal()
    try:
        # Create session
        session = crud.create_interview_session(
            db=db,
            job_role="Software Engineer",
            difficulty_level="Senior",
            interview_type="Technical",
            num_questions=3
        )
        print(f"✅ Session created in DB with ID: {session.id}")

        # Add a question
        question = crud.create_question(
            db=db,
            session_id=session.id,
            question_text="Explain database transactions and ACID properties.",
            order_index=0
        )
        print(f"✅ Question linked to session. ID: {question.id}")

        # Add evaluation with time_taken_seconds
        evaluation = crud.create_evaluation(
            db=db,
            question_id=question.id,
            user_answer="ACID stands for Atomicity, Consistency, Isolation, and Durability...",
            time_taken_seconds=45,
            overall_score=8.5,
            relevance_score=9.0,
            accuracy_score=9.0,
            completeness_score=8.0,
            communication_score=8.5,
            problem_solving_score=8.0,
            strengths="Correct explanation of each letter in ACID; structured flow.",
            weaknesses="Lacked concrete code examples of transaction isolation levels.",
            suggested_answer="A complete answer defines transaction bounds, explains the ACID constraints, and mentions isolation overheads."
        )
        print(f"✅ Evaluation recorded in DB. ID: {evaluation.id}, time_taken_seconds: {evaluation.time_taken_seconds}")

        # Recalculate session final score
        crud.update_session_final_score(db=db, session_id=session.id)
        
        # Save session summaries
        crud.update_session_summary(
            db=db,
            session_id=session.id,
            top_strengths="Clear database foundational concept understanding; strong communication skills.",
            improvement_areas="Needs to elaborate on database scaling; could provide concrete STAR format examples."
        )
        
        # Verify read
        session_verify = crud.get_interview_session(db=db, session_id=session.id)
        print(f"✅ Session final score retrieved: {session_verify.final_score}")
        print(f"✅ Session top strengths: {session_verify.top_strengths}")
        assert session_verify.final_score == 8.5, "Score calculation mismatch!"
        assert "ACID" in session_verify.questions[0].evaluation.user_answer, "Verification content read mismatch!"
        
        print("✅ CRUD operations verify successfully.")
    except Exception as e:
        print(f"❌ CRUD operations verification failed: {e}")
        return False
    finally:
        db.close()

    # 3. Test Service Logic fallbacks
    print("3. Testing Service Logic and Fallbacks...")
    try:
        # Question generation seed check
        qs = generate_questions("AIML Engineer", "Senior", "Technical", 2)
        print(f"✅ Generated questions count: {len(qs)}")
        print(f"   Q1: {qs[0]}")
        print(f"   Q2: {qs[1]}")
        assert len(qs) == 2, "Failed to generate correct number of questions."

        # Evaluation check
        eval_res = evaluate_answer(
            job_role="AIML Engineer",
            difficulty_level="Senior",
            interview_type="Technical",
            question_text="What is gradient descent?",
            user_answer="It is an optimization algorithm used to minimize a cost function by iteratively moving in the direction of steepest descent."
        )
        print(f"✅ Evaluated overall score: {eval_res['overall_score']}")
        print(f"   Strengths: {eval_res['strengths']}")
        assert isinstance(eval_res["overall_score"], float) or isinstance(eval_res["overall_score"], int), "Score is not numeric."
        
        # Summary generator check
        mock_session_payload = {
            "job_role": "AIML Engineer",
            "difficulty_level": "Senior",
            "interview_type": "Technical",
            "questions": [
                {
                    "question_text": "What is gradient descent?",
                    "evaluation": {
                        "user_answer": "An optimization algorithm.",
                        "overall_score": 7.0,
                        "strengths": "Simple and correct",
                        "weaknesses": "Too short"
                    }
                }
            ]
        }
        summary = generate_overall_summary(mock_session_payload)
        print(f"✅ Overall session summary strengths count: {len(summary['top_strengths'])}")
        print("   Strengths: ", summary['top_strengths'])
        print("✅ Service logic fallbacks verify successfully.")
    except Exception as e:
        print(f"❌ Service logic verification failed: {e}")
        return False

    print("\n🎉 All local checks passed successfully! Ready for launch.")
    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
