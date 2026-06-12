# AI Interview Question Generator & Answer Evaluation System

A production-quality, modular, and deployment-ready mock interview simulator built with **FastAPI**, **Streamlit**, **SQLAlchemy** (SQLite), and **Gemini 2.5 Flash API** using **LangChain**.

## Features

1. **Interview Setup**: Select Job Role (AIML Engineer, Software Engineer, Data Analyst, Cloud Engineer, Full Stack Developer), Difficulty Level (Entry-Level, Mid-Level, Senior, Lead), Interview Type (Technical, HR, Behavioral), and the number of questions.
2. **AI Question Generation**: Context-aware interview questions generated dynamically using Gemini 2.5 Flash.
3. **Interactive Simulation**: Step-by-step interview experience with an integrated countdown timer.
4. **AI Answer Evaluation**: Reviews responses based on:
   - Relevance
   - Technical Accuracy
   - Completeness
   - Communication Quality
   - Problem Solving Ability
5. **Real-time Feedback**: Displays overall scores, criteria breakdown, strengths, weaknesses, and a suggested professional answer immediately after submission.
6. **SQLite Storage & History**: Saves all mock interviews and individual question feedback to a local SQLite database, accessible through a structured "Interview History" dashboard.

## Directory Structure

```text
ai_interview_generator/
├── backend/
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   ├── models.py
│   │   └── crud.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── question_service.py
│   │   └── evaluation_service.py
│   ├── __init__.py
│   ├── config.py
│   ├── main.py
│   └── schemas.py
├── frontend/
│   ├── components/
│   │   ├── __init__.py
│   │   ├── history.py
│   │   ├── interview.py
│   │   └── setup.py
│   ├── __init__.py
│   ├── api_client.py
│   └── app.py
├── requirements.txt
├── README.md
└── .env
```

## Setup & Running Instructions

### 1. Prerequisite Configuration
Create a `.env` file in the root of the project:
```env
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=sqlite:///./interview_system.db
GEMINI_MODEL=gemini-2.5-flash
```

### 2. Install Dependencies
It is recommended to run within a python virtual environment:
```bash
python -m venv venv
venv\Scripts\activate      # On Windows
source venv/bin/activate    # On macOS/Linux

pip install -r requirements.txt
```

### 3. Launch Backend (FastAPI Server)
From the root of the project:
```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
The documentation is available locally at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 4. Launch Frontend (Streamlit App)
In a new terminal window:
```bash
streamlit run frontend/app.py
```
Open your browser and navigate to the local URL displayed (usually `http://localhost:8501`).
