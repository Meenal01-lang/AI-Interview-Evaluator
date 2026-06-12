import time
import streamlit as st
import streamlit.components.v1 as components
from api_client import api_client

def render_timer():
    """
    Renders a client-side JavaScript stopwatch inside an iframe.
    Runs in real-time in the user's browser without blocking Streamlit execution.
    """
    html_code = """
    <div style="
        font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
        text-align: center;
        padding: 8px;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    ">
        <span style="font-size: 0.85rem; color: #888; text-transform: uppercase; letter-spacing: 0.05em;">Timer Elapsed</span>
        <div id="stopwatch" style="font-size: 1.8rem; font-weight: 700; color: #00e676; margin-top: 2px;">00:00</div>
    </div>
    <script>
        let seconds = 0;
        const display = document.getElementById('stopwatch');
        setInterval(() => {
            seconds++;
            const mins = String(Math.floor(seconds / 60)).padStart(2, '0');
            const secs = String(seconds % 60).padStart(2, '0');
            display.innerText = `${mins}:${secs}`;
        }, 1000);
    </script>
    """
    components.html(html_code, height=90)

def get_score_color(score: float) -> str:
    """
    Returns a hexadecimal color string based on the score threshold.
    """
    if score >= 8.0:
        return "#00e676"  # Bright Green
    elif score >= 5.0:
        return "#ffb300"  # Amber/Orange
    else:
        return "#ff1744"  # Red

def format_duration(seconds: int) -> str:
    """
    Formats seconds into a human-readable mm:ss format.
    """
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins:02d}:{secs:02d}"

def render_interview_page():
    """
    Walks the candidate through the questions step-by-step,
    calculates response duration, and submits to the evaluation endpoint.
    """
    session = st.session_state.current_session
    q_idx = st.session_state.current_question_index
    questions = session.get("questions", [])
    
    if not questions:
        st.error("No questions were generated for this session.")
        if st.button("Back to Setup"):
            st.session_state.current_session = None
            st.rerun()
        return

    # Header details
    st.markdown(
        f"### 🎙️ {session['job_role']} — {session['difficulty_level']} ({session['interview_type']})"
    )
    
    # Progress Bar
    progress_val = float(q_idx) / float(len(questions))
    st.progress(progress_val)
    st.write(f"Question **{q_idx + 1}** of **{len(questions)}**")

    # Current question details
    current_question = questions[q_idx]
    q_id = current_question["id"]

    # Initialize question start time
    if st.session_state.question_start_time is None:
        st.session_state.question_start_time = time.time()

    # Question text card
    st.markdown(
        f"""
        <div style="
            background-color: rgba(255, 255, 255, 0.05);
            border-left: 5px solid #1e88e5;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        ">
            <h4 style="margin: 0; font-weight: 500; color: #e0e0e0;">Question:</h4>
            <p style="font-size: 1.15rem; line-height: 1.6; margin-top: 10px; color: #ffffff;">
                {current_question['question_text']}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Render Timer & Answer form
    col1, col2 = st.columns([1, 4])
    with col1:
        # Show visual stopwatch if not yet evaluated
        if q_id not in st.session_state.evaluations:
            render_timer()
        else:
            # If evaluated, show duration
            eval_node = st.session_state.evaluations[q_id]
            dur = eval_node.get("time_taken_seconds", 0)
            st.markdown(
                f"""
                <div style="text-align: center; padding: 12px; background: rgba(255,255,255,0.02); border-radius: 8px; border: 1px solid rgba(255,255,255,0.05);">
                    <span style="font-size: 0.8rem; color: #777;">TIME SPENT</span><br>
                    <span style="font-weight: bold; color: #00e676; font-size: 1.1rem;">{format_duration(dur)}</span>
                </div>
                """,
                unsafe_allow_html=True
            )

    with col2:
        # User answer text area
        disabled = q_id in st.session_state.evaluations
        user_answer = st.text_area(
            "Your Answer:",
            value=st.session_state.user_answers.get(q_id, ""),
            height=150,
            placeholder="Type your response here... Be detailed and structure your solution.",
            disabled=disabled,
            key=f"ans_input_{q_id}"
        )

    # Submission actions
    if not disabled:
        if st.button("Submit Answer", use_container_width=True):
            if not user_answer.strip():
                st.warning("⚠️ Please provide an answer before submitting.")
                return

            with st.spinner("🔍 Analyzing response..."):
                # Track duration
                time_spent = int(time.time() - st.session_state.question_start_time)
                if time_spent < 1:
                    time_spent = 1
                
                # Submit to backend
                evaluation = api_client.submit_answer(
                    session_id=session["id"],
                    question_id=q_id,
                    user_answer=user_answer,
                    time_taken_seconds=time_spent
                )
                
                if evaluation:
                    st.session_state.evaluations[q_id] = evaluation
                    st.session_state.user_answers[q_id] = user_answer
                    st.rerun()
                else:
                    st.error("❌ Failed to process evaluation. Please check server logs.")

    # Show feedback if evaluated
    if q_id in st.session_state.evaluations:
        eval_data = st.session_state.evaluations[q_id]
        score_color = get_score_color(eval_data["overall_score"])

        st.markdown("<hr style='border: 0.5px solid rgba(255,255,255,0.1); margin: 25px 0;'>", unsafe_allow_html=True)
        st.markdown("### 📊 AI Evaluation Feedback")

        # Overall Score Metric
        st.markdown(
            f"""
            <div style="
                background: rgba(255, 255, 255, 0.02);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 12px;
                padding: 15px;
                display: flex;
                align-items: center;
                margin-bottom: 20px;
            ">
                <div style="
                    font-size: 2.2rem;
                    font-weight: 800;
                    color: {score_color};
                    background: rgba(0,0,0,0.2);
                    width: 70px;
                    height: 70px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border: 2px solid {score_color};
                    margin-right: 20px;
                ">
                    {eval_data['overall_score']}
                </div>
                <div>
                    <h4 style="margin: 0; color: #ffffff;">Overall Score</h4>
                    <p style="margin: 3px 0 0 0; color: #888; font-size: 0.9rem;">Scored out of 10 points based on model evaluation</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Dimension Breakdown Grid
        st.write("**Criteria Dimension Scores (0-10):**")
        d_cols = st.columns(5)
        dimensions = [
            ("Relevance", "relevance_score"),
            ("Accuracy", "accuracy_score"),
            ("Completeness", "completeness_score"),
            ("Communication", "communication_score"),
            ("Problem Solving", "problem_solving_score")
        ]
        for idx, (label, key) in enumerate(dimensions):
            with d_cols[idx]:
                d_score = eval_data.get(key, 0.0)
                st.metric(label=label, value=f"{d_score}/10")

        st.markdown("<br>", unsafe_allow_html=True)

        # Strengths & Weaknesses columns
        col_s, col_w = st.columns(2)
        with col_s:
            strengths_list = eval_data.get("strengths", "").split(";")
            strengths_items = "".join([f"<li>{s.strip()}</li>" for s in strengths_list if s.strip()])
            st.markdown(
                f"""
                <div style="background-color: rgba(76, 175, 80, 0.1); padding: 15px; border-radius: 8px; border-left: 4px solid #4caf50; min-height: 150px; color: #ffffff;">
                    <h5 style="margin-top: 0; margin-bottom: 8px; color: #81c784; font-weight: 600;">🌟 Strengths</h5>
                    <ul style="margin: 0; padding-left: 20px; color: #e8f5e9;">
                        {strengths_items}
                    </ul>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col_w:
            weaknesses_list = eval_data.get("weaknesses", "").split(";")
            weaknesses_items = "".join([f"<li>{w.strip()}</li>" for w in weaknesses_list if w.strip()])
            st.markdown(
                f"""
                <div style="background-color: rgba(244, 67, 54, 0.1); padding: 15px; border-radius: 8px; border-left: 4px solid #f44336; min-height: 150px; color: #ffffff;">
                    <h5 style="margin-top: 0; margin-bottom: 8px; color: #e57373; font-weight: 600;">⚠️ Areas for Improvement</h5>
                    <ul style="margin: 0; padding-left: 20px; color: #ffebee;">
                        {weaknesses_items}
                    </ul>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # Suggested Answer
        with st.expander("💡 Suggested Improved Response"):
            st.write(eval_data.get("suggested_answer", "No suggestions provided."))

        st.markdown("<br>", unsafe_allow_html=True)

        # Session transitions
        nav_cols = st.columns([2, 1, 2])
        with nav_cols[1]:
            if q_idx < len(questions) - 1:
                if st.button("Next Question ➡️", use_container_width=True):
                    st.session_state.current_question_index += 1
                    st.session_state.question_start_time = None
                    st.rerun()
            else:
                if st.button("🏁 Finish Interview", use_container_width=True):
                    # Fetch finalized scores and overall summaries from backend
                    finalized_session = api_client.get_interview(session["id"])
                    
                    st.session_state.finished_session = finalized_session
                    st.session_state.current_session = None
                    st.rerun()

def render_completion_page():
    """
    Renders the overall performance summary and metrics upon completing all questions.
    """
    session = st.session_state.finished_session
    st.balloons()
    
    st.markdown("## 🎓 Mock Interview Completed!")
    st.markdown("Excellent job finishing your mock interview. Here is your overall performance summary:")
    
    score = session.get("final_score", 0.0)
    score_color = get_score_color(score)
    
    st.markdown(
        f"""
        <div style="
            text-align: center;
            background: rgba(255,255,255,0.02);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 16px;
            padding: 30px;
            margin: 20px 0 30px 0;
        ">
            <h4 style="margin: 0; color: #888; text-transform: uppercase; font-size: 0.95rem;">Average Final Score</h4>
            <div style="font-size: 4.5rem; font-weight: 900; color: {score_color}; margin: 10px 0;">
                {score} <span style="font-size: 1.5rem; color: #666;">/ 10</span>
            </div>
            <p style="margin: 0; color: #bbb; font-size: 1.1rem;">
                Target Role: <strong>{session['job_role']}</strong> ({session['difficulty_level']})
            </p>
            <p style="margin: 5px 0 0 0; color: #888; font-size: 0.9rem;">
                Interview Focus: {session['interview_type']} | Questions Completed: {session['num_questions']}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Render overall strengths & weaknesses generated upon completion
    col_str, col_imp = st.columns(2)
    with col_str:
        strengths = session.get("top_strengths", "")
        if strengths:
            strengths_items = "".join([f"<li>{s.strip()}</li>" for s in strengths.split(";") if s.strip()])
            content = f'<ul style="margin: 0; padding-left: 20px; color: #e8f5e9;">{strengths_items}</ul>'
        else:
            content = '<p style="color: #bbb; margin: 0;">Summary analysis is loading or was not compiled.</p>'
        st.markdown(
            f"""
            <div style="background-color: rgba(76, 175, 80, 0.1); padding: 20px; border-radius: 12px; border-left: 4px solid #4caf50; min-height: 220px; color: #ffffff;">
                <h4 style="margin-top: 0; margin-bottom: 12px; color: #81c784; font-weight: 600;">🌟 Session Key Strengths</h4>
                {content}
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_imp:
        improvements = session.get("improvement_areas", "")
        if improvements:
            improvements_items = "".join([f"<li>{i.strip()}</li>" for i in improvements.split(";") if i.strip()])
            content = f'<ul style="margin: 0; padding-left: 20px; color: #ffebee;">{improvements_items}</ul>'
        else:
            content = '<p style="color: #bbb; margin: 0;">Summary analysis is loading or was not compiled.</p>'
        st.markdown(
            f"""
            <div style="background-color: rgba(244, 67, 54, 0.1); padding: 20px; border-radius: 12px; border-left: 4px solid #f44336; min-height: 220px; color: #ffffff;">
                <h4 style="margin-top: 0; margin-bottom: 12px; color: #e57373; font-weight: 600;">⚠️ Key Focus Areas</h4>
                {content}
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Start New Interview", use_container_width=True):
            st.session_state.finished_session = None
            st.session_state.current_session = None
            st.rerun()
    with col2:
        if st.button("📜 View Interview History", use_container_width=True):
            st.session_state.finished_session = None
            st.session_state.current_session = None
            st.session_state.active_tab = "Interview History"
            st.rerun()
