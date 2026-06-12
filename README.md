# 🎯 AI Interview Evaluator

An AI-powered interview preparation platform that simulates real interview experiences by generating role-specific questions, evaluating responses, and providing detailed feedback using Google's Gemini AI.

## 🚀 Overview

Preparing for technical interviews can be challenging without personalized feedback. AI Interview Evaluator helps candidates practice interviews in a realistic environment by generating intelligent questions and evaluating answers instantly.

The system acts as a virtual interviewer, providing structured assessments and helping users identify areas for improvement before real interviews.

---

## ✨ Key Features

### 🤖 AI-Powered Question Generation

* Generates interview questions dynamically using Gemini AI
* Role-specific interview experience
* Multiple difficulty levels

### 📊 Intelligent Answer Evaluation

* Evaluates answers based on relevance, clarity, and completeness
* Provides constructive feedback
* Generates detailed performance insights

### 📈 Interview Scoring System

* Calculates overall interview score
* Tracks individual question performance
* Highlights strengths and improvement areas

### 📝 Interview History

* Stores previous interview sessions
* Saves questions, answers, evaluations, and scores
* Allows users to review past performance

### 💾 Persistent Storage

* SQLite database integration
* Secure storage of interview records
* Fast and lightweight data management

---

## 🏗️ System Architecture

```text
User
  │
  ▼
Streamlit Frontend
  │
  ▼
FastAPI Backend
  │
  ▼
Gemini AI Services
  │
  ▼
SQLite Database
```

---

## 🛠️ Tech Stack

| Component | Technology       |
| --------- | ---------------- |
| Frontend  | Streamlit        |
| Backend   | FastAPI          |
| Database  | SQLite           |
| ORM       | SQLAlchemy       |
| AI Model  | Gemini 2.5 Flash |
| Language  | Python           |

---

## 📂 Project Structure

```text
AI-Interview-Evaluator/
│
├── backend/
│   ├── database/
│   ├── services/
│   ├── main.py
│   └── schemas.py
│
├── frontend/
│   ├── components/
│   ├── api_client.py
│   └── app.py
│
├── requirements.txt
├── README.md
└── .env.example
```

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/Meenal01-lang/AI-Interview-Evaluator.git
cd AI-Interview-Evaluator
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

```bash
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file:

```env
GEMINI_API_KEY=your_api_key_here
```

---

## ▶️ Run the Application

### Start Backend

```bash
uvicorn backend.main:app --reload
```

Backend runs on:

```text
http://localhost:8000
```

### Start Frontend

```bash
streamlit run frontend/app.py
```

Frontend runs on:

```text
http://localhost:8501
```

---

## 🎯 Future Enhancements

* Resume-Based Interview Generation
* PDF Resume Upload
* Personalized Question Recommendations
* Performance Analytics Dashboard
* Multi-Round Interview Simulation
* Voice-Based Interviews
* Cloud Deployment

---

## 📸 Screenshots

<img width="1920" height="850" alt="Screenshot (513)" src="https://github.com/user-attachments/assets/965c7bc7-e766-44e4-b0f1-7badb5be2ef5" />


---

## 👩‍💻 Author

**Meenal**

B.Tech CSE (AI) | AI & Machine Learning Enthusiast

Passionate about building intelligent applications that solve real-world problems using Artificial Intelligence and Large Language Models.

---

## ⭐ If you found this project interesting, consider giving it a star!

