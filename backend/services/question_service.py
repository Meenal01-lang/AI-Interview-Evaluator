import json
import random
from typing import List
from pydantic import BaseModel, Field
import google.generativeai as genai
from backend.config import settings

class QuestionListSchema(BaseModel):
    questions: List[str] = Field(..., description="List of generated interview questions")

def get_seed_questions(job_role: str, difficulty_level: str, interview_type: str, num_questions: int) -> List[str]:
    """
    Returns realistic, high-quality interview questions for Demo Mode.
    Covers all 5 job roles and 3 interview types.
    """
    # 1. Database of high-quality mock questions
    seed_db = {
        "Software Engineer": {
            "Technical": [
                "Explain the difference between a process and a thread, and how threads share memory resource context.",
                "How do you design a RESTful API to handle high write rates? What strategies would you use for concurrency control?",
                "What is cache invalidation, and what are the trade-offs between Write-Through and Write-Back caching strategies?",
                "Explain the concepts of Time and Space complexity. Can you walk through a scenario where optimizing space over time was necessary?",
                "What are database indexes? Explain how a B-Tree index improves read performance and its impact on write performance."
            ],
            "Behavioral": [
                "Describe a situation in a past project where you had to make a critical technical trade-off. What was the outcome?",
                "Tell me about a time you worked on a project with vague or changing requirements. How did you ensure successful delivery?",
                "Explain a scenario where you made a mistake on a release. How did you handle it and what steps did you take to prevent it from happening again?",
                "Describe a time you had a technical disagreement with a senior teammate. How did you resolve it and arrive at a consensus?"
            ],
            "HR": [
                "Why are you interested in joining our development team, and how do you align with our technical vision?",
                "Where do you see yourself technically in the next 3 to 5 years, and how do you plan to achieve those goals?",
                "What is your approach to maintaining work-life balance while ensuring critical project deadlines are successfully met?"
            ]
        },
        "AIML Engineer": {
            "Technical": [
                "Explain the difference between L1 and L2 regularization. How do they affect the model weights mathematically?",
                "What is the vanishing gradient problem in deep neural networks? What architectures or activation functions mitigate it?",
                "Explain the architecture of a Transformer model. Specifically, how does the Self-Attention mechanism work?",
                "What is overfitting? Explain three different methods you would use to prevent overfitting in a deep learning model.",
                "How do you handle highly imbalanced datasets when training a classification model? Compare resampling vs class weighting."
            ],
            "Behavioral": [
                "Describe a project where your machine learning model did not perform well in production despite high validation scores. How did you debug it?",
                "Tell me about a time you had to explain a complex ML model's decision (e.g., explaining feature importances or model output) to non-technical stake holders.",
                "Describe a time you had to deploy an ML model under tight latency constraints. What optimization methods did you apply?"
            ],
            "HR": [
                "What inspired you to specialize in Artificial Intelligence and Machine Learning? How do you keep up with the fast-evolving literature?",
                "How do you approach ethical considerations, such as bias mitigation, when designing and training datasets?"
            ]
        },
        "Data Analyst": {
            "Technical": [
                "What is the difference between an Inner Join, Left Join, and Outer Join in SQL? Provide a scenario for using a Left Join.",
                "How do you explain the concept of a P-value to a business stakeholder? What does statistical significance mean in practice?",
                "What are the differences between dimension tables and fact tables in a star schema design?",
                "Explain the difference between correlation and causation. How would you test if a correlation is indeed causal?",
                "Describe how you would clean a dataset that has a significant amount of missing data and outliers."
            ],
            "Behavioral": [
                "Describe a time when you found an unexpected, high-value insight in a dataset. How did you present it to lead business changes?",
                "Tell me about a project where your analysis was challenged by a manager. How did you validate your data and handle the feedback?"
            ],
            "HR": [
                "Why do you enjoy working with data, and how do you translate technical insights into simple business recommendations?",
                "How do you organize your tasks when multiple departments request urgent data reports simultaneously?"
            ]
        },
        "Cloud Engineer": {
            "Technical": [
                "Explain the difference between Horizontal Scaling (Scaling Out) and Vertical Scaling (Scaling Up). When would you choose which?",
                "What is Infrastructure as Code (IaC)? What are the advantages of using Terraform over manual cloud console configurations?",
                "Describe how a CDN (Content Delivery Network) works. How does it improve performance and reduce load on origin servers?",
                "Explain the difference between a public subnet and a private subnet in a VPC. How does an instance in a private subnet access the internet?",
                "What is a serverless architecture? What are the key benefits and limitations of using AWS Lambda or Google Cloud Functions?"
            ],
            "Behavioral": [
                "Describe a major cloud infrastructure outage you experienced. How did you diagnose the root cause and restore operations?",
                "Tell me about a time you successfully optimized cloud architecture expenses. What metrics did you use to evaluate cost efficiency?"
            ],
            "HR": [
                "Why is cloud engineering your target field, and what certifications or cloud architectures do you specialize in?",
                "How do you handle situations where developer requirements conflict with security compliance and budget limits?"
            ]
        },
        "Full Stack Developer": {
            "Technical": [
                "Explain the difference between client-side rendering (CSR) and server-side rendering (SSR). What are the SEO and performance trade-offs?",
                "What is CORS (Cross-Origin Resource Sharing)? How do you configure a backend server to resolve CORS issues safely?",
                "Describe state management in modern frontend frameworks. When is a global state manager (like Redux or Context API) preferred over local state?",
                "How do you prevent security vulnerabilities like SQL Injection and Cross-Site Scripting (XSS) in a full-stack application?",
                "Compare REST APIs and GraphQL. In what scenarios would you choose GraphQL over REST?"
            ],
            "Behavioral": [
                "Tell me about a full-stack feature you built from database schema to frontend UI. What design choices did you make?",
                "Describe a time you had to debug a bottleneck that was lagging the application. Was it a database query, a server issue, or frontend rendering?"
            ],
            "HR": [
                "How do you balance learning both frontend design trends and backend database developments as a full-stack developer?",
                "Why do you want to work on a full-stack code base rather than specializing in purely frontend or backend?"
            ]
        }
    }

    # 2. Get questions for role and type
    role_db = seed_db.get(job_role, seed_db["Software Engineer"])
    questions = role_db.get(interview_type, role_db["Technical"])
    
    # Shuffle and slice
    shuffled = list(questions)
    random.shuffle(shuffled)
    
    selected_questions = shuffled[:num_questions]
    
    # 3. Dynamic filler generator if not enough questions
    while len(selected_questions) < num_questions:
        idx = len(selected_questions) + 1
        selected_questions.append(
            f"As a {difficulty_level} {job_role}, how do you ensure reliability and quality on your {interview_type.lower()}-related tasks (Reference Case {idx})?"
        )
        
    return selected_questions

def generate_questions(job_role: str, difficulty_level: str, interview_type: str, num_questions: int) -> List[str]:
    """
    Generates structured interview questions. 
    Triggers Demo Mode (seed generation) or falls back to it if the Gemini API fails.
    """
    if settings.DEMO_MODE or not settings.GEMINI_API_KEY:
        print(f"ℹ️ Demo Mode active. Fetching seed questions for {job_role} ({interview_type})...")
        return get_seed_questions(job_role, difficulty_level, interview_type, num_questions)

    try:
        # Initialize Google GenAI SDK
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        
        prompt = (
            f"You are a elite hiring manager conducting a mock interview.\n"
            f"Generate exactly {num_questions} unique, challenging, and domain-specific interview questions "
            f"for a candidate applying as a {difficulty_level} {job_role}.\n"
            f"The focus area for this interview session is: {interview_type}.\n\n"
            f"Ensure the questions test core fundamentals, problem-solving, and practical design scenarios appropriate for a {difficulty_level} candidate."
        )
        
        # Call SDK directly using response_schema for guaranteed JSON matching structure
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=QuestionListSchema,
                temperature=0.7
            )
        )
        
        parsed = json.loads(response.text)
        questions = parsed.get("questions", [])
        
        if isinstance(questions, list) and len(questions) > 0:
            return [str(q).strip() for q in questions[:num_questions]]
            
    except Exception as e:
        print(f"⚠️ Gemini API question generation failed: {e}. Falling back to Demo Mode seeds.")
        
    # Final robust fallback to seed data
    return get_seed_questions(job_role, difficulty_level, interview_type, num_questions)
