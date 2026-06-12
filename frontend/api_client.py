import requests
from typing import Dict, Any, List, Optional

class APIClient:
    def __init__(self, base_url: str = "https://ai-interview-evaluator.onrender.com/api"):
        self.base_url = base_url

    def check_health(self) -> Dict[str, Any]:
        """
        Pings backend health endpoint to verify server status, demo mode, and configuration.
        """
        try:
            response = requests.get(f"{self.base_url}/health", timeout=3)
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        return {"status": "offline", "demo_mode": True, "gemini_api_configured": False}

    def start_interview(
        self, job_role: str, difficulty_level: str, interview_type: str, num_questions: int
    ) -> Optional[Dict[str, Any]]:
        """
        Calls POST /api/interviews to initialize session and generate questions.
        """
        url = f"{self.base_url}/interviews"
        payload = {
            "job_role": job_role,
            "difficulty_level": difficulty_level,
            "interview_type": interview_type,
            "num_questions": num_questions
        }
        try:
            response = requests.post(url, json=payload, timeout=60)  # High timeout for Gemini generation
            if response.status_code == 201:
                return response.json()
            else:
                print(f"Error {response.status_code}: {response.text}")
        except Exception as e:
            print(f"Connection failed: {e}")
        return None

    def get_interview(self, session_id: int) -> Optional[Dict[str, Any]]:
        """
        Calls GET /api/interviews/{session_id} to fetch full session details.
        """
        url = f"{self.base_url}/interviews/{session_id}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Failed to fetch session {session_id}: {e}")
        return None

    def get_all_interviews(self) -> List[Dict[str, Any]]:
        """
        Calls GET /api/interviews to retrieve past interview histories.
        """
        url = f"{self.base_url}/interviews"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Failed to retrieve interviews list: {e}")
        return []

    def submit_answer(
        self, session_id: int, question_id: int, user_answer: str, time_taken_seconds: int
    ) -> Optional[Dict[str, Any]]:
        """
        Calls POST /api/interviews/{session_id}/questions/{question_id}/answer
        to submit a response, duration, and fetch the AI evaluation.
        """
        url = f"{self.base_url}/interviews/{session_id}/questions/{question_id}/answer"
        payload = {
            "user_answer": user_answer,
            "time_taken_seconds": time_taken_seconds
        }
        try:
            response = requests.post(url, json=payload, timeout=60)  # High timeout for Gemini evaluation
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error {response.status_code}: {response.text}")
        except Exception as e:
            print(f"Failed to submit answer: {e}")
        return None

api_client = APIClient()
