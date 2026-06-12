import streamlit as st
from api_client import api_client
from components.setup import render_setup_page
from components.interview import render_interview_page, render_completion_page
from components.history import render_history_page

# 1. Page Config
st.set_page_config(
    page_title="AI Interview Simulator",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inject Custom Premium Styling (Dark-themed glassmorphism elements)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3, h4 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        letter-spacing: -0.02em;
    }

    .app-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 30px;
        border-radius: 12px;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
    }
    
    .app-header h1 {
        margin: 0;
        color: #ffffff;
        font-size: 2.5rem;
    }
    .app-header p {
        margin: 8px 0 0 0;
        color: #b0bec5;
        font-size: 1.1rem;
    }

    div.stButton > button {
        background: linear-gradient(90deg, #1565c0 0%, #1e88e5 100%);
        color: white;
        border: none;
        padding: 10px 24px;
        font-weight: 600;
        border-radius: 8px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(21, 101, 192, 0.2);
    }
    
    div.stButton > button:hover {
        background: linear-gradient(90deg, #1e88e5 0%, #42a5f5 100%);
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(30, 136, 229, 0.4);
    }

    section[data-testid="stSidebar"] {
        background-color: #090b0d;
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 3. Initialize Session States
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "New Mock Interview"
if "current_session" not in st.session_state:
    st.session_state.current_session = None
if "current_question_index" not in st.session_state:
    st.session_state.current_question_index = 0
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
if "evaluations" not in st.session_state:
    st.session_state.evaluations = {}
if "question_start_time" not in st.session_state:
    st.session_state.question_start_time = None
if "finished_session" not in st.session_state:
    st.session_state.finished_session = None

# 4. Sidebar Rendering
with st.sidebar:
    st.markdown(
        """
        <div style="text-align: center; padding: 20px 0;">
            <span style="font-size: 3rem;">🎙️</span>
            <h3 style="margin: 10px 0 0 0; color: #ffffff; font-family: 'Outfit';">AI Interviewer</h3>
            <p style="color: #666; font-size: 0.85rem; margin: 2px 0 0 0;">Version 1.0 (Gemini 2.5 Flash)</p>
        </div>
        <hr style="border: 0.5px solid rgba(255,255,255,0.05); margin-bottom: 20px;">
        """,
        unsafe_allow_html=True
    )
    
    # Navigation tabs (locked during active interview sessions)
    is_active_session = st.session_state.current_session is not None
    
    if is_active_session:
        st.info("⚠️ Interview session is active. Navigation is temporarily locked.")
        active_tab = "New Mock Interview"
    else:
        active_options = ["New Mock Interview", "Interview History"]
        # Safe default index loader
        default_index = active_options.index(st.session_state.active_tab) if st.session_state.active_tab in active_options else 0
        active_tab = st.radio(
            "Navigation",
            options=active_options,
            index=default_index,
            key="navigation_radio"
        )
        st.session_state.active_tab = active_tab

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### 🔧 Connection Settings")

    # Fetch backend state
    health = api_client.check_health()
    is_backend_online = health.get("status") != "offline"
    
    if is_backend_online:
        st.markdown("● **Backend**: <span style='color: #00e676;'>ONLINE</span>", unsafe_allow_html=True)
        if health.get("demo_mode"):
            st.markdown("● **Engine Mode**: <span style='color: #ffb300; font-weight:bold;'>DEMO (Seed Offline)</span>", unsafe_allow_html=True)
        else:
            st.markdown("● **Engine Mode**: <span style='color: #00e676; font-weight:bold;'>LIVE (Gemini API)</span>", unsafe_allow_html=True)
    else:
        st.markdown("● **Backend**: <span style='color: #ff1744;'>OFFLINE</span>", unsafe_allow_html=True)
        st.error("Please run the backend: `uvicorn backend.main:app --reload`")

    # Abandon active session option
    if is_active_session:
        st.markdown("<hr style='border: 0.5px solid rgba(255,255,255,0.05); margin-top: 20px;'>", unsafe_allow_html=True)
        if st.button("🚨 Abandon Interview", use_container_width=True):
            st.session_state.current_session = None
            st.session_state.finished_session = None
            st.session_state.current_question_index = 0
            st.session_state.user_answers = {}
            st.session_state.evaluations = {}
            st.session_state.question_start_time = None
            st.warning("Interview abandoned.")
            st.rerun()

# 5. Core Content Router
# Header Banner
st.markdown(
    """
    <div class="app-header">
        <h1>AI Interviewer & Evaluation System</h1>
        <p>Hone your interview skills with real-time AI feedback and performance tracking</p>
    </div>
    """,
    unsafe_allow_html=True
)

if st.session_state.finished_session is not None:
    render_completion_page()
elif st.session_state.current_session is not None:
    render_interview_page()
else:
    if st.session_state.active_tab == "New Mock Interview":
        render_setup_page()
    elif st.session_state.active_tab == "Interview History":
        render_history_page()
