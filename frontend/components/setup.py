import streamlit as st
from api_client import api_client

def render_setup_page():
    """
    Renders the setup form for configuring and launching a new interview session.
    Also displays a banner if Demo Mode is active.
    """
    st.markdown("## 🎯 Set Up Your Mock Interview")
    st.write("Configure your target role and parameters below to generate custom, AI-powered questions.")

    # Check backend state for Demo Mode notice
    health = api_client.check_health()
    if health.get("status") == "offline":
        st.error("⚠️ The backend API server is offline. Please ensure uvicorn is running: `uvicorn backend.main:app`")
        return
        
    if health.get("demo_mode"):
        st.info(
            "💡 **Demo Mode Active**: No `GEMINI_API_KEY` was found or `DEMO_MODE=true` is set. "
            "The app will generate high-quality realistic questions and evaluation metrics locally. "
            "To connect to the live Gemini API, configure a `GEMINI_API_KEY` in your `.env` file."
        )

    # Form parameters
    roles = ["Software Engineer", "AIML Engineer", "Data Analyst", "Cloud Engineer", "Full Stack Developer"]
    levels = ["Entry-Level", "Mid-Level", "Senior", "Lead"]
    types = ["Technical", "Behavioral", "HR"]

    col1, col2 = st.columns(2)
    with col1:
        job_role = st.selectbox("Job Role", roles, index=0)
        difficulty_level = st.selectbox("Difficulty Level", levels, index=1)
    with col2:
        interview_type = st.selectbox("Interview Type", types, index=0)
        num_questions = st.slider("Number of Questions", min_value=1, max_value=10, value=3)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Start button
    if st.button("🚀 Start Interview", use_container_width=True):
        with st.spinner("🧠 Preparing interview questions..."):
            session = api_client.start_interview(
                job_role=job_role,
                difficulty_level=difficulty_level,
                interview_type=interview_type,
                num_questions=num_questions
            )

        if session:
            # Initialize session states
            st.session_state.current_session = session
            st.session_state.current_question_index = 0
            st.session_state.user_answers = {}
            st.session_state.evaluations = {}
            # Reset timer for the first question
            st.session_state.question_start_time = None
            
            st.success("🎉 Interview initialized successfully! Redirecting...")
            st.rerun()
        else:
            st.error("❌ Failed to start the interview session. Please check backend server logs.")
