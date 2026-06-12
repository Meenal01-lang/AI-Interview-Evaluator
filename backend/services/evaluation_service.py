import json
from typing import Dict, Any, List
from pydantic import BaseModel, Field
import google.generativeai as genai
from backend.config import settings

# 1. Pydantic Schemas for Gemini Structured JSON Outputs
class EvaluationSchema(BaseModel):
    overall_score: float = Field(..., description="Overall score between 0.0 and 10.0")
    relevance_score: float = Field(..., description="Relevance score between 0.0 and 10.0")
    accuracy_score: float = Field(..., description="Technical accuracy score between 0.0 and 10.0")
    completeness_score: float = Field(..., description="Completeness score between 0.0 and 10.0")
    communication_score: float = Field(..., description="Communication quality score between 0.0 and 10.0")
    problem_solving_score: float = Field(..., description="Problem solving ability score between 0.0 and 10.0")
    strengths: List[str] = Field(..., description="List of specific strengths observed in the response (2-3 items)")
    weaknesses: List[str] = Field(..., description="List of concrete areas for improvement (2-3 items)")
    suggested_answer: str = Field(..., description="High-quality professional response showcasing how to answer this question perfectly")

class SessionSummarySchema(BaseModel):
    top_strengths: List[str] = Field(..., description="Top 3 overall key strengths shown across all questions")
    improvement_areas: List[str] = Field(..., description="Top 3 key improvement areas highlight across all responses")

# 2. Heuristic Mock Evaluator for Demo Mode
def get_mock_evaluation(question_text: str, user_answer: str) -> Dict[str, Any]:
    """
    Generates a realistic mock evaluation dynamically based on answer characteristics.
    Ensures Demo Mode feels interactive and logical.
    """
    clean_ans = user_answer.strip()
    ans_length = len(clean_ans)
    
    # 1. Extreme Case: Empty or default evasions
    if ans_length < 15 or clean_ans.lower() in ("i don't know", "idk", "skip", "no idea", "pass"):
        return {
            "overall_score": 1.5,
            "relevance_score": 1.0,
            "accuracy_score": 1.0,
            "completeness_score": 1.0,
            "communication_score": 2.0,
            "problem_solving_score": 1.0,
            "strengths": ["Answered the question session promptly."],
            "weaknesses": ["Did not attempt to construct a relevant explanation.", "Lacked technical substance and terminology."],
            "suggested_answer": f"To answer this question effectively, address the query structure directly: Define the concept briefly, elaborate on implementation details, and mention a quick real-world example."
        }

    # 2. Case: Too Short
    if ans_length < 80:
        return {
            "overall_score": 5.0,
            "relevance_score": 6.5,
            "accuracy_score": 5.0,
            "completeness_score": 3.5,
            "communication_score": 5.5,
            "problem_solving_score": 4.0,
            "strengths": ["Stayed relevant to the topic.", "Concise response delivery."],
            "weaknesses": [
                "Too brief to establish technical proficiency or demonstrate problem-solving.",
                "Missed details on implementation, trade-offs, and architecture."
            ],
            "suggested_answer": f"Expand this answer. For example, explain the 'how' and 'why', cite a technology or framework, and describe how you'd manage edge-cases."
        }

    # 3. Case: Medium Answer
    if ans_length < 250:
        return {
            "overall_score": 7.5,
            "relevance_score": 8.0,
            "accuracy_score": 7.5,
            "completeness_score": 7.0,
            "communication_score": 8.0,
            "problem_solving_score": 7.0,
            "strengths": ["Structured flow with clear sentence syntax.", "Includes appropriate technical keywords and context."],
            "weaknesses": [
                "Could detail architectural trade-offs or performance concerns.",
                "Could provide a clearer production-grade example."
            ],
            "suggested_answer": f"Make the answer standout by structuring it using the STAR method: Situation (setup context), Task (what was needed), Action (your specific solution), and Result (outcomes and metrics)."
        }

    # 4. Case: Long, comprehensive answer
    return {
        "overall_score": 8.8,
        "relevance_score": 9.0,
        "accuracy_score": 9.0,
        "completeness_score": 8.5,
        "communication_score": 8.5,
        "problem_solving_score": 9.0,
        "strengths": [
            "Comprehensive, detailed response showing deep technical domain knowledge.",
            "Demonstrated strong problem-solving capabilities with structured methodology."
        ],
        "weaknesses": [
            "Slight optimization opportunities in detailing code styling or performance scaling.",
            "Could refine verbal delivery flow to be even more concise."
        ],
        "suggested_answer": f"This is an excellent response. To elevate it further to a Lead level, contrast this solution against alternative architectures (e.g. comparing cache invalidation patterns) and list specific performance metrics."
    }

# 3. Evaluation Service Implementation
def evaluate_answer(
    job_role: str,
    difficulty_level: str,
    interview_type: str,
    question_text: str,
    user_answer: str
) -> Dict[str, Any]:
    """
    Evaluates the candidate's answer using the Gemini 2.5 Flash API with a Pydantic schema constraint.
    Falls back to dynamic heuristic mock evaluation if Demo Mode is active or API fails.
    """
    if settings.DEMO_MODE or not settings.GEMINI_API_KEY:
        return get_mock_evaluation(question_text, user_answer)

    try:
        # Configure Gemini Client
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        
        prompt = (
            f"You are a strict technical interviewer evaluating a response.\n\n"
            f"Context:\n"
            f"- Role: {job_role}\n"
            f"- Level: {difficulty_level}\n"
            f"- Segment: {interview_type}\n"
            f"- Question: {question_text}\n"
            f"- User Answer: {user_answer}\n\n"
            f"Perform a professional assessment. Score all scores on a 0.0 - 10.0 scale.\n"
            f"Produce 2-3 specific strengths, 2-3 areas for improvement, and a suggested exemplary response suitable for a {difficulty_level} candidate."
        )

        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=EvaluationSchema,
                temperature=0.2
            )
        )
        
        # Load and parse output
        eval_data = json.loads(response.text)
        return eval_data
        
    except Exception as e:
        print(f"⚠️ Gemini evaluation failed: {e}. Falling back to dynamic mock evaluation.")
        return get_mock_evaluation(question_text, user_answer)

# 4. Overall Session Summarizer Implementation
def generate_overall_summary(session_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates a high-level summary of the candidate's performance across the entire interview session.
    Lists top strengths and improvement areas.
    """
    questions = session_data.get("questions", [])
    
    # Heuristic fallback if in Demo Mode or if API fails
    mock_summary = {
        "top_strengths": [
            "Demonstrated active awareness of the core job domain requirements.",
            "Strong willingness to articulate solutions and address structured topics.",
            "Responded to all interview prompts with appropriate context."
        ],
        "improvement_areas": [
            "Should focus on providing deeper technical implementation details.",
            "Needs to practice structured delivery methodologies (like the STAR method).",
            "Can improve time management to maximize technical depth under constraints."
        ]
    }

    if settings.DEMO_MODE or not settings.GEMINI_API_KEY or not questions:
        return mock_summary

    try:
        # Construct summary payload
        transcript_lines = []
        for idx, q in enumerate(questions):
            q_text = q["question_text"]
            eval_node = q.get("evaluation")
            if eval_node:
                ans_text = eval_node["user_answer"]
                score = eval_node["overall_score"]
                strengths = eval_node["strengths"]
                weaknesses = eval_node["weaknesses"]
                transcript_lines.append(
                    f"Q{idx+1}: {q_text}\nAnswer: {ans_text}\nScore: {score}/10\nStrengths: {strengths}\nWeaknesses: {weaknesses}\n"
                )
        
        transcript = "\n".join(transcript_lines)
        
        # Configure Gemini client
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        
        prompt = (
            f"You are a recruitment lead reviewing a candidate's complete mock interview session.\n"
            f"Role: {session_data['job_role']} ({session_data['difficulty_level']})\n"
            f"Interview Focus: {session_data['interview_type']}\n\n"
            f"Complete Session Transcript & Evaluation:\n"
            f"{transcript}\n\n"
            f"Analyze all questions and answers. Identify the top 3 overall key strengths "
            f"and the top 3 primary areas of improvement across the entire interview session."
        )

        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=SessionSummarySchema,
                temperature=0.3
            )
        )
        
        summary_data = json.loads(response.text)
        return summary_data
        
    except Exception as e:
        print(f"⚠️ Gemini overall summary generation failed: {e}. Falling back to default summaries.")
        return mock_summary
