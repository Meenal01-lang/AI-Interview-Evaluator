import streamlit as st
import pandas as pd
from datetime import datetime
from api_client import api_client
from components.interview import get_score_color, format_duration

def format_iso_timestamp(iso_str: str) -> str:
    """
    Helper that formats ISO timestamps into friendly dates.
    """
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return iso_str[:16].replace("T", " ")

def render_history_page():
    """
    Renders the past interview sessions list.
    """
    st.markdown("## 📜 Mock Interview History")
    
    # Check if a specific history session is selected
    selected_id = st.session_state.get("selected_history_session_id", None)
    
    if selected_id is not None:
        render_session_details(selected_id)
        return

    # Index page showing all sessions
    with st.spinner("Loading history logs..."):
        sessions = api_client.get_all_interviews()
        
    if not sessions:
        st.info("💡 You haven't completed any mock interviews yet! Go to the 'New Mock Interview' tab to begin.")
        return

    st.write("Browse and review your previous performance logs below:")
    
    # Render interactive drilldowns
    for s in sessions:
        score_str = f"{s['final_score']}/10" if s["final_score"] is not None else "In Progress"
        score_val = s["final_score"] or 0.0
        s_color = get_score_color(score_val) if s["final_score"] is not None else "#777"
        
        st.markdown(
            f"""
            <div style="
                background: rgba(255,255,255,0.02);
                border: 1px solid rgba(255,255,255,0.05);
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 12px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            ">
                <div>
                    <h5 style="margin: 0; font-size: 1.05rem; color: #ffffff;">{s['job_role']} — <span style="color: #bbb;">{s['difficulty_level']}</span></h5>
                    <p style="margin: 4px 0 0 0; color: #666; font-size: 0.85rem;">
                        Focus: {s['interview_type']} | Questions: {s['num_questions']} | Date: {format_iso_timestamp(s['created_at'])}
                    </p>
                </div>
                <div style="text-align: right; display: flex; align-items: center; gap: 15px;">
                    <div style="
                        font-weight: 800;
                        color: {s_color};
                        font-size: 1.15rem;
                        background: rgba(0,0,0,0.15);
                        padding: 6px 12px;
                        border-radius: 6px;
                        border: 1px solid {s_color};
                    ">
                        {score_str}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Display the View button on the right
        col_space, col_btn = st.columns([5, 1])
        with col_btn:
            if st.button("👁️ View Details", key=f"btn_details_{s['id']}", use_container_width=True):
                st.session_state.selected_history_session_id = s["id"]
                st.rerun()

def render_session_details(session_id: int):
    """
    Renders overall summaries and details of a selected historical session.
    """
    if st.button("⬅️ Back to History List"):
        st.session_state.selected_history_session_id = None
        st.rerun()

    with st.spinner("Fetching details..."):
        session = api_client.get_interview(session_id)

    if not session:
        st.error("Failed to load interview session details.")
        return

    score = session.get("final_score", 0.0)
    score_color = get_score_color(score) if score is not None else "#777"
    score_str = f"{score}/10" if score is not None else "Incomplete"

    # Header Card
    st.markdown(
        f"""
        <div style="
            background: rgba(255,255,255,0.01);
            border: 1px solid rgba(255,255,255,0.04);
            border-radius: 12px;
            padding: 20px;
            margin: 15px 0 25px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        ">
            <div>
                <h3 style="margin: 0; color: #ffffff;">{session['job_role']} Mock Session</h3>
                <p style="margin: 5px 0 0 0; color: #888;">
                    Difficulty: <strong>{session['difficulty_level']}</strong> | Focus: <strong>{session['interview_type']}</strong>
                </p>
                <p style="margin: 2px 0 0 0; color: #555; font-size: 0.85rem;">
                    Completed: {format_iso_timestamp(session['created_at'])}
                </p>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 0.8rem; color: #777; text-transform: uppercase;">Average Score</div>
                <div style="font-size: 2.2rem; font-weight: 800; color: {score_color}; margin-top: 3px;">
                    {score_str}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 1. Overall Session Summaries (Strengths and Focus Areas)
    st.markdown("### 📊 Session Performance Review")
    col_str, col_imp = st.columns(2)
    with col_str:
        strengths = session.get("top_strengths", "")
        if strengths:
            strengths_items = "".join([f"<li>{s.strip()}</li>" for s in strengths.split(";") if s.strip()])
            content = f'<ul style="margin: 0; padding-left: 20px; color: #e8f5e9;">{strengths_items}</ul>'
        else:
            content = '<p style="color: #bbb; margin: 0;">*Not compiled for incomplete sessions.*</p>'
        st.markdown(
            f"""
            <div style="background-color: rgba(76, 175, 80, 0.1); padding: 15px; border-radius: 8px; border-left: 4px solid #4caf50; min-height: 150px; color: #ffffff;">
                <h5 style="margin-top: 0; margin-bottom: 8px; color: #81c784; font-weight: 600;">🌟 Session Key Strengths</h5>
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
            content = '<p style="color: #bbb; margin: 0;">*Not compiled for incomplete sessions.*</p>'
        st.markdown(
            f"""
            <div style="background-color: rgba(244, 67, 54, 0.1); padding: 15px; border-radius: 8px; border-left: 4px solid #f44336; min-height: 150px; color: #ffffff;">
                <h5 style="margin-top: 0; margin-bottom: 8px; color: #e57373; font-weight: 600;">⚠️ Key Focus Areas</h5>
                {content}
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br><br>", unsafe_allow_html=True)

    # 2. Detailed Q&A Transcript
    questions = session.get("questions", [])
    if not questions:
        st.warning("No questions found for this session.")
        return

    st.markdown("### 💬 Detailed Q&A Transcript")
    
    for idx, q in enumerate(questions):
        st.markdown(f"#### Question {idx + 1}")
        
        # Display question
        st.info(q["question_text"])
        
        # Check if evaluated
        eval_data = q.get("evaluation")
        if not eval_data:
            st.warning("This question was not answered or evaluated.")
            st.markdown("<br>", unsafe_allow_html=True)
            continue
            
        # Display user response and duration
        duration_formatted = format_duration(eval_data.get("time_taken_seconds", 0))
        st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span style="font-weight: bold; color: #ccc;">Your Response:</span>
                <span style="font-size: 0.85rem; color: #888;">⏱️ Time spent: {duration_formatted}</span>
            </div>
            <div style="background: rgba(255,255,255,0.03); padding: 12px; border-radius: 6px; border-left: 3px solid #777; margin-bottom: 15px; font-size: 0.95rem;">
                {eval_data['user_answer']}
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Detail feedback cards
        eval_score_color = get_score_color(eval_data["overall_score"])
        
        st.markdown(f"**AI Score: <span style='color:{eval_score_color}; font-weight:bold;'>{eval_data['overall_score']}/10</span>**", unsafe_allow_html=True)
        
        # Sub-scores
        metrics_cols = st.columns(5)
        metrics = [
            ("Relevance", "relevance_score"),
            ("Accuracy", "accuracy_score"),
            ("Completeness", "completeness_score"),
            ("Communication", "communication_score"),
            ("Problem Solving", "problem_solving_score")
        ]
        for m_idx, (m_label, m_key) in enumerate(metrics):
            with metrics_cols[m_idx]:
                st.metric(label=m_label, value=f"{eval_data.get(m_key, 0.0)}/10")
        
        col_st, col_we = st.columns(2)
        with col_st:
            strengths_list = eval_data.get("strengths", "").split(";")
            strengths_items = "".join([f"<li>{s.strip()}</li>" for s in strengths_list if s.strip()])
            st.markdown(
                f"""
                <div style="background-color: rgba(76, 175, 80, 0.1); padding: 15px; border-radius: 8px; border-left: 4px solid #4caf50; min-height: 120px; color: #ffffff; margin-bottom: 15px;">
                    <h5 style="margin-top: 0; margin-bottom: 8px; color: #81c784; font-weight: 600;">🌟 Question Strengths</h5>
                    <ul style="margin: 0; padding-left: 20px; color: #e8f5e9; font-size: 0.9rem;">
                        {strengths_items}
                    </ul>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col_we:
            weaknesses_list = eval_data.get("weaknesses", "").split(";")
            weaknesses_items = "".join([f"<li>{w.strip()}</li>" for w in weaknesses_list if w.strip()])
            st.markdown(
                f"""
                <div style="background-color: rgba(244, 67, 54, 0.1); padding: 15px; border-radius: 8px; border-left: 4px solid #f44336; min-height: 120px; color: #ffffff; margin-bottom: 15px;">
                    <h5 style="margin-top: 0; margin-bottom: 8px; color: #e57373; font-weight: 600;">⚠️ Focus Areas</h5>
                    <ul style="margin: 0; padding-left: 20px; color: #ffebee; font-size: 0.9rem;">
                        {weaknesses_items}
                    </ul>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("💡 Suggested Improved Response"):
            st.write(eval_data.get("suggested_answer", "No suggestions provided."))
            
        st.markdown("<hr style='border: 0.5px solid rgba(255,255,255,0.05); margin: 30px 0;'>", unsafe_allow_html=True)
