import streamlit as st
import google.generativeai as genai
import pdfplumber
import json
import os
import hashlib
import base64
import streamlit.components.v1 as components

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="View Prep · AI Interview Coach", layout="wide", page_icon="🎯")

# ─── USER DATABASE (local JSON) ──────────────────────────────────────────────────
USERS_FILE = "viewprep_users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def register_user(name, field, email, password):
    users = load_users()
    if email in users:
        return False, "An account with this email already exists. Please log in."
    users[email] = {
        "name": name,
        "field": field,
        "email": email,
        "password": hash_password(password),
        "interviews_completed": 0,
        "resumes_analyzed": 0,
    }
    save_users(users)
    return True, "Account created!"

def login_user(email, password):
    users = load_users()
    if email not in users:
        return False, None, "No account found with this email."
    if users[email]["password"] != hash_password(password):
        return False, None, "Incorrect password."
    return True, users[email], "Welcome back!"

def update_user_stats(email, key, delta=1):
    users = load_users()
    if email in users:
        users[email][key] = users[email].get(key, 0) + delta
        save_users(users)

# ─── THEME STATE ────────────────────────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False

# ─── COLOR SYSTEM ───────────────────────────────────────────────────────────────
if st.session_state["dark_mode"]:
    BG          = "#0f1623"
    SURFACE     = "#1a2235"
    SURFACE2    = "#212d42"
    BORDER      = "#2e3f5c"
    TEXT        = "#e8edf5"
    TEXT_MUTED  = "#8fa3c0"
    ACCENT      = "#4a90d9"
    ACCENT_SOFT = "#1e3a5f"
    ACCENT_TEXT = "#7db8f0"
    SUCCESS     = "#22c55e"
    SUCCESS_BG  = "#0d2e1a"
    DANGER      = "#f87171"
    DANGER_BG   = "#2d1515"
else:
    BG          = "#f0f4fa"
    SURFACE     = "#ffffff"
    SURFACE2    = "#e8f0fd"
    BORDER      = "#c8d8f0"
    TEXT        = "#1a2740"
    TEXT_MUTED  = "#5a7399"
    ACCENT      = "#2563eb"
    ACCENT_SOFT = "#dbeafe"
    ACCENT_TEXT = "#1d4ed8"
    SUCCESS     = "#16a34a"
    SUCCESS_BG  = "#dcfce7"
    DANGER      = "#dc2626"
    DANGER_BG   = "#fee2e2"

# ─── CSS ────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
.stApp {{ background: {BG}; font-family: 'Inter', sans-serif; color: {TEXT}; }}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding: 0 !important; max-width: 100% !important; }}
section[data-testid="stSidebar"] {{ display: none; }}
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div {{
    background: {SURFACE} !important; color: {TEXT} !important;
    border: 1.5px solid {BORDER} !important; border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important; font-size: 15px !important;
    padding: 10px 14px !important;
}}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {{
    border-color: {ACCENT} !important;
    box-shadow: 0 0 0 3px {ACCENT_SOFT} !important; outline: none !important;
}}
.stTextInput label, .stTextArea label, .stSelectbox label,
.stFileUploader label, .stRadio label, .stCheckbox label,
.stSlider label {{
    color: {TEXT} !important; font-weight: 500 !important;
    font-size: 14px !important; font-family: 'Inter', sans-serif !important;
}}
.stRadio > div {{ flex-direction: row !important; gap: 12px !important; flex-wrap: wrap !important; }}
.stRadio > div > label {{
    background: {SURFACE} !important; border: 1.5px solid {BORDER} !important;
    border-radius: 10px !important; padding: 8px 16px !important;
    cursor: pointer !important; font-size: 14px !important;
}}
.stRadio > div > label:hover {{ border-color: {ACCENT} !important; background: {ACCENT_SOFT} !important; }}
.stButton > button[kind="primary"] {{
    background: {ACCENT} !important; color: white !important; border: none !important;
    border-radius: 10px !important; font-weight: 600 !important; font-size: 15px !important;
    padding: 12px 28px !important; width: 100% !important;
    font-family: 'Inter', sans-serif !important; cursor: pointer !important;
}}
.stButton > button[kind="primary"]:hover {{ opacity: 0.88 !important; }}
.stButton > button {{
    background: {SURFACE} !important; color: {TEXT} !important;
    border: 1.5px solid {BORDER} !important; border-radius: 10px !important;
    font-weight: 500 !important; font-size: 14px !important; padding: 10px 20px !important;
    width: 100% !important; font-family: 'Inter', sans-serif !important; cursor: pointer !important;
}}
.stButton > button:hover {{ border-color: {ACCENT} !important; color: {ACCENT} !important; }}
.stFileUploader > div {{
    background: {SURFACE} !important; border: 2px dashed {BORDER} !important; border-radius: 12px !important;
}}
.stFileUploader > div:hover {{ border-color: {ACCENT} !important; }}
.stTabs [data-baseweb="tab-list"] {{
    background: {SURFACE} !important; border-bottom: 2px solid {BORDER} !important;
    gap: 0 !important; padding: 0 24px !important;
}}
.stTabs [data-baseweb="tab"] {{
    color: {TEXT_MUTED} !important; font-weight: 500 !important; font-size: 15px !important;
    padding: 14px 20px !important; border-radius: 0 !important;
    border-bottom: 2px solid transparent !important; font-family: 'Inter', sans-serif !important;
}}
.stTabs [aria-selected="true"] {{
    color: {ACCENT} !important; border-bottom: 2px solid {ACCENT} !important; background: transparent !important;
}}
.stTabs [data-baseweb="tab-panel"] {{ padding: 0 !important; background: {BG} !important; }}
.stSlider > div > div > div {{ background: {ACCENT} !important; }}
.stSlider > div > div > div > div {{ background: {ACCENT} !important; }}
hr {{ border-color: {BORDER} !important; margin: 20px 0 !important; }}
.stCheckbox > label > span {{ color: {TEXT} !important; font-size: 14px !important; }}
.stDownloadButton > button {{
    background: {ACCENT} !important; color: white !important;
    border: none !important; border-radius: 10px !important; font-weight: 600 !important; width: 100% !important;
}}
.end-session-btn > button {{
    background: {DANGER_BG} !important; color: {DANGER} !important;
    border: 1.5px solid {DANGER} !important; border-radius: 10px !important;
    font-weight: 600 !important;
}}
.end-session-btn > button:hover {{ opacity: 0.85 !important; }}
</style>
""", unsafe_allow_html=True)

# ─── API SETUP ──────────────────────────────────────────────────────────────────
if "GEMINI_API_KEY" in st.secrets:
    api_key_available = True
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.5-flash')
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    api_key_available = False
    GEMINI_API_KEY = ""

# ─── SESSION STATE ───────────────────────────────────────────────────────────────
defaults = {
    "logged_in": False,
    "auth_mode": "login",  # "login" or "register"
    "questions_list": [],
    "current_q_index": 0,
    "interview_started": False,
    "live_session_active": False,
    "interviews_completed": 0,
    "resumes_analyzed": 0,
    "user_profile_name": "",
    "user_profile_field": "",
    "user_profile_email": "",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def reset_interview():
    st.session_state["interview_started"] = False
    st.session_state["questions_list"] = []
    st.session_state["current_q_index"] = 0
    st.session_state["live_session_active"] = False
    for k in list(st.session_state.keys()):
        if k.startswith("feedback_"):
            del st.session_state[k]

# ─── HELPERS ────────────────────────────────────────────────────────────────────
def stat_card(icon, value, label, color=None):
    c = color or ACCENT
    return f"""
    <div style="background:{SURFACE}; border:1.5px solid {BORDER}; border-radius:14px;
                padding:24px 20px; text-align:center;">
        <div style="font-size:32px; margin-bottom:8px;">{icon}</div>
        <div style="font-size:28px; font-weight:700; color:{c}; line-height:1;">{value}</div>
        <div style="font-size:13px; color:{TEXT_MUTED}; margin-top:6px; font-weight:500;">{label}</div>
    </div>"""

def section_header(title, subtitle=None):
    sub = f'<p style="color:{TEXT_MUTED}; font-size:15px; margin-top:6px; font-weight:400;">{subtitle}</p>' if subtitle else ""
    st.markdown(f"""
    <div style="padding: 32px 32px 20px 32px;">
        <h2 style="color:{TEXT}; font-size:24px; font-weight:700; margin:0;">{title}</h2>
        {sub}
    </div>""", unsafe_allow_html=True)

def top_bar():
    name  = st.session_state.get("user_profile_name", "")
    field = st.session_state.get("user_profile_field", "")
    st.markdown(f"""
    <div style="background:{SURFACE}; border-bottom:1.5px solid {BORDER};
                padding:0 32px; display:flex; align-items:center;
                justify-content:space-between; height:64px;">
        <div style="display:flex; align-items:center; gap:10px;">
            <div style="background:{ACCENT}; color:white; width:36px; height:36px;
                        border-radius:9px; display:flex; align-items:center;
                        justify-content:center; font-size:18px; font-weight:700;">V</div>
            <span style="font-size:18px; font-weight:700; color:{TEXT};">View Prep</span>
        </div>
        <div style="display:flex; align-items:center; gap:16px;">
            <div style="text-align:right;">
                <div style="font-size:14px; font-weight:600; color:{TEXT};">{name}</div>
                <div style="font-size:12px; color:{TEXT_MUTED};">{field}</div>
            </div>
            <div style="width:36px; height:36px; background:{ACCENT_SOFT}; border-radius:50%;
                        display:flex; align-items:center; justify-content:center;
                        font-size:15px; font-weight:700; color:{ACCENT_TEXT};">
                {name[0].upper() if name else "?"}
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# AUTH PAGE  (Login / Register — persists across visits via JSON)
# ════════════════════════════════════════════════════════════════════════════════
if not st.session_state["logged_in"]:

    # Top bar
    st.markdown(f"""
    <div style="background:{SURFACE}; border-bottom:1.5px solid {BORDER};
                padding:0 32px; display:flex; align-items:center;
                justify-content:space-between; height:64px;">
        <div style="display:flex; align-items:center; gap:10px;">
            <div style="background:{ACCENT}; color:white; width:36px; height:36px;
                        border-radius:9px; display:flex; align-items:center;
                        justify-content:center; font-size:18px; font-weight:700;">V</div>
            <span style="font-size:18px; font-weight:700; color:{TEXT};">View Prep</span>
        </div>
        <span style="font-size:13px; color:{TEXT_MUTED};">AI Interview Coach</span>
    </div>""", unsafe_allow_html=True)

    # Dark toggle
    _, tog = st.columns([9, 1])
    with tog:
        st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
        if st.button("🌙" if not st.session_state["dark_mode"] else "☀️"):
            st.session_state["dark_mode"] = not st.session_state["dark_mode"]
            st.rerun()

    # Hero
    st.markdown(f"""
    <div style="text-align:center; padding:50px 20px 30px;">
        <div style="display:inline-block; background:{ACCENT_SOFT}; color:{ACCENT_TEXT};
                    font-size:13px; font-weight:600; padding:6px 14px; border-radius:20px; margin-bottom:20px;">
            🎯 Powered by AI
        </div>
        <h1 style="font-size:40px; font-weight:700; color:{TEXT}; line-height:1.2; margin-bottom:14px;">
            Ace your next interview<br/>with confidence
        </h1>
        <p style="font-size:16px; color:{TEXT_MUTED}; max-width:460px; margin:0 auto 32px; line-height:1.6;">
            Practice real questions, get live AI feedback, and improve your resume — all in one place.
        </p>
    </div>""", unsafe_allow_html=True)

    # Auth mode toggle
    _, col_toggle, _ = st.columns([2, 1, 2])
    with col_toggle:
        auth_choice = st.radio("", ["Sign in", "Create account"], horizontal=True, label_visibility="collapsed")

    _, col_form, _ = st.columns([1, 1.4, 1])
    with col_form:
        st.markdown(f"""
        <div style="background:{SURFACE}; border:1.5px solid {BORDER};
                    border-radius:18px; padding:36px; margin-top:12px; margin-bottom:32px;">
            <h2 style="color:{TEXT}; font-size:20px; font-weight:700; margin-bottom:20px;">
                {'Welcome back' if auth_choice == 'Sign in' else 'Create your free account'}
            </h2>
        </div>""", unsafe_allow_html=True)

        if auth_choice == "Sign in":
            email_in    = st.text_input("Email address", placeholder="you@example.com", key="li_email")
            show_p      = st.checkbox("Show password", key="li_show")
            password_in = st.text_input("Password", type="default" if show_p else "password",
                                        placeholder="Your password", key="li_pass")
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            if st.button("Sign in →", type="primary"):
                ok, user_data, msg = login_user(email_in, password_in)
                if ok:
                    st.session_state["logged_in"]           = True
                    st.session_state["user_profile_name"]   = user_data["name"]
                    st.session_state["user_profile_field"]  = user_data["field"]
                    st.session_state["user_profile_email"]  = user_data["email"]
                    st.session_state["interviews_completed"]= user_data.get("interviews_completed", 0)
                    st.session_state["resumes_analyzed"]    = user_data.get("resumes_analyzed", 0)
                    st.success(f"Welcome back, {user_data['name']}! Loading your dashboard...")
                    st.rerun()
                else:
                    st.error(msg)
        else:
            name_in     = st.text_input("Your full name", placeholder="e.g. Priya Sharma", key="reg_name")
            field_in    = st.text_input("Field you're preparing for", placeholder="e.g. Software Engineering", key="reg_field")
            email_in2   = st.text_input("Email address", placeholder="you@example.com", key="reg_email")
            show_p2     = st.checkbox("Show password", key="reg_show")
            password_in2= st.text_input("Choose a password (8–16 characters)",
                                         type="default" if show_p2 else "password",
                                         placeholder="At least 8 characters", key="reg_pass")
            uploaded_resume = st.file_uploader("Upload your resume (optional PDF)", type="pdf")
            if uploaded_resume and "original_resume" not in st.session_state:
                with pdfplumber.open(uploaded_resume) as pdf:
                    st.session_state["original_resume"] = "".join(p.extract_text() or "" for p in pdf.pages)
            agree = st.checkbox("I agree to let AI process my data for interview practice and feedback.")
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            if st.button("Create my account →", type="primary"):
                if not (name_in and field_in and email_in2 and password_in2):
                    st.error("Please fill in all fields.")
                elif not agree:
                    st.warning("Please tick the checkbox to continue.")
                elif len(password_in2) < 8 or len(password_in2) > 16:
                    st.error(f"Password must be 8–16 characters (yours is {len(password_in2)}).")
                else:
                    ok, msg = register_user(name_in, field_in, email_in2, password_in2)
                    if ok:
                        st.session_state["logged_in"]           = True
                        st.session_state["user_profile_name"]   = name_in
                        st.session_state["user_profile_field"]  = field_in
                        st.session_state["user_profile_email"]  = email_in2
                        st.session_state["interviews_completed"]= 0
                        st.session_state["resumes_analyzed"]    = 0
                        st.success("Account created! Taking you to your dashboard...")
                        st.rerun()
                    else:
                        st.error(msg)

    # Feature highlights
    st.markdown(f"""
    <div style="display:flex; gap:20px; justify-content:center; flex-wrap:wrap; padding:8px 40px 60px;">
        <div style="background:{SURFACE}; border:1.5px solid {BORDER}; border-radius:14px;
                    padding:24px; max-width:260px; text-align:center;">
            <div style="font-size:28px; margin-bottom:10px;">🎙️</div>
            <h3 style="color:{TEXT}; font-size:15px; font-weight:600; margin-bottom:7px;">Live interview practice</h3>
            <p style="color:{TEXT_MUTED}; font-size:13px; line-height:1.5;">Real-time AI coach watches your face and voice as you answer.</p>
        </div>
        <div style="background:{SURFACE}; border:1.5px solid {BORDER}; border-radius:14px;
                    padding:24px; max-width:260px; text-align:center;">
            <div style="font-size:28px; margin-bottom:10px;">📄</div>
            <h3 style="color:{TEXT}; font-size:15px; font-weight:600; margin-bottom:7px;">Resume checker</h3>
            <p style="color:{TEXT_MUTED}; font-size:13px; line-height:1.5;">Paste a job description and find exactly what's missing.</p>
        </div>
        <div style="background:{SURFACE}; border:1.5px solid {BORDER}; border-radius:14px;
                    padding:24px; max-width:260px; text-align:center;">
            <div style="font-size:28px; margin-bottom:10px;">📊</div>
            <h3 style="color:{TEXT}; font-size:15px; font-weight:600; margin-bottom:7px;">Progress tracking</h3>
            <p style="color:{TEXT_MUTED}; font-size:13px; line-height:1.5;">Your stats are saved so you can see improvement over time.</p>
        </div>
    </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ════════════════════════════════════════════════════════════════════════════════
else:
    top_bar()

    # Top controls row
    c1, c2, c3 = st.columns([8, 1, 1])
    with c2:
        st.markdown("<div style='margin-top:6px;'></div>", unsafe_allow_html=True)
        if st.button("🌙" if not st.session_state["dark_mode"] else "☀️", help="Toggle dark/light mode"):
            st.session_state["dark_mode"] = not st.session_state["dark_mode"]
            st.rerun()
    with c3:
        st.markdown("<div style='margin-top:6px;'></div>", unsafe_allow_html=True)
        if st.button("Sign out"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

    if not api_key_available:
        st.error("⚠️  API key not found. Add GEMINI_API_KEY to your Streamlit secrets.")
        st.stop()

    tab_dashboard, tab_interview, tab_resume = st.tabs(
        ["🏠  Dashboard", "🎙️  Interview practice", "📄  Resume checker"]
    )

    # ══════════════════════════════════════════════════════════════════════════════
    # DASHBOARD
    # ══════════════════════════════════════════════════════════════════════════════
    with tab_dashboard:
        name  = st.session_state.get("user_profile_name", "")
        field = st.session_state.get("user_profile_field", "")

        st.markdown(f"""
        <div style="padding:32px 32px 20px;">
            <h2 style="color:{TEXT}; font-size:26px; font-weight:700; margin-bottom:6px;">
                👋 Welcome back, {name}!
            </h2>
            <p style="color:{TEXT_MUTED}; font-size:15px;">
                Preparing for <strong style="color:{ACCENT};">{field}</strong>. Here's your progress so far.
            </p>
        </div>""", unsafe_allow_html=True)

        st.markdown("<div style='padding:0 32px;'>", unsafe_allow_html=True)
        s1, s2, s3 = st.columns(3)
        with s1:
            st.markdown(stat_card("🎙️", st.session_state["interviews_completed"], "Interview sessions done", ACCENT), unsafe_allow_html=True)
        with s2:
            st.markdown(stat_card("📄", st.session_state["resumes_analyzed"], "Resumes analyzed", "#7c3aed"), unsafe_allow_html=True)
        with s3:
            rs = "✅ Uploaded" if "original_resume" in st.session_state else "Not uploaded"
            rc = SUCCESS if "original_resume" in st.session_state else TEXT_MUTED
            st.markdown(stat_card("📎", rs, "Resume on file", rc), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

        st.markdown(f"<div style='padding:0 32px;'><h3 style='color:{TEXT}; font-size:18px; font-weight:600; margin-bottom:16px;'>What would you like to do?</h3></div>", unsafe_allow_html=True)

        a1, a2 = st.columns(2)
        with a1:
            st.markdown(f"""
            <div style="background:{SURFACE}; border:1.5px solid {BORDER}; border-radius:14px;
                        padding:28px; margin-left:32px; min-height:180px;">
                <div style="font-size:32px; margin-bottom:12px;">🎙️</div>
                <h3 style="color:{TEXT}; font-size:17px; font-weight:600; margin-bottom:8px;">Start an interview session</h3>
                <p style="color:{TEXT_MUTED}; font-size:14px; line-height:1.5;">
                    Live video practice with real-time AI feedback on your face, voice, and answers.
                </p>
            </div>""", unsafe_allow_html=True)
        with a2:
            st.markdown(f"""
            <div style="background:{SURFACE}; border:1.5px solid {BORDER}; border-radius:14px;
                        padding:28px; margin-right:32px; min-height:180px;">
                <div style="font-size:32px; margin-bottom:12px;">📄</div>
                <h3 style="color:{TEXT}; font-size:17px; font-weight:600; margin-bottom:8px;">Check your resume</h3>
                <p style="color:{TEXT_MUTED}; font-size:14px; line-height:1.5;">
                    Paste a job description and see exactly which keywords and skills to add.
                </p>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="padding:0 32px 40px;">
            <div style="background:{ACCENT_SOFT}; border:1.5px solid {BORDER}; border-radius:14px; padding:24px;">
                <h3 style="color:{ACCENT_TEXT}; font-size:16px; font-weight:600; margin-bottom:12px;">💡 Tips for a great session</h3>
                <ul style="color:{TEXT_MUTED}; font-size:14px; line-height:1.9; padding-left:20px; margin:0;">
                    <li>Find a quiet spot with good lighting before starting a live session.</li>
                    <li>Speak clearly and take a breath before you start answering.</li>
                    <li>Upload your resume to get questions tailored to your experience.</li>
                    <li>Try Easy questions first, then work up to Hard ones.</li>
                </ul>
            </div>
        </div>""", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════════
    # INTERVIEW PRACTICE
    # ══════════════════════════════════════════════════════════════════════════════
    with tab_interview:

        # ── SETUP SCREEN ────────────────────────────────────────────────────────
        if not st.session_state["interview_started"]:
            section_header("Interview practice", "Set up your session below. We'll generate questions and coach you in real time.")

            _, col_setup, _ = st.columns([1, 3, 1])
            with col_setup:
                st.markdown(f"""
                <div style="background:{SURFACE}; border:1.5px solid {BORDER};
                            border-radius:16px; padding:32px; margin-bottom:24px;">
                """, unsafe_allow_html=True)

                field = st.text_input("What field are you interviewing for?",
                                      value=st.session_state.get("user_profile_field", ""),
                                      help="e.g. Data Science, Web Development, Marketing")

                difficulty = st.selectbox("How hard should the questions be?",
                                          ["Easy — great for beginners", "Medium — some experience needed", "Hard — advanced level"],
                                          help="Start with Easy if you haven't practised before.")

                num_questions = st.slider("How many questions do you want?", min_value=1, max_value=30, value=5,
                                          help="Drag to choose between 1 and 30 questions.")

                mode = st.radio("Where should questions come from?",
                                ["Based on my resume (if uploaded)", "General questions for my field"])

                st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
                st.markdown(f"""
                <div style="background:{ACCENT_SOFT}; border-radius:10px; padding:14px 16px; margin-bottom:16px;">
                    <p style="color:{ACCENT_TEXT}; font-size:13px; margin:0; line-height:1.6;">
                        📹 <strong>Live video session</strong> — your webcam will open and AI will watch your
                        face expressions every 5 seconds and give you real-time tips in a chat popup.
                        Make sure your camera and microphone are allowed in your browser.
                    </p>
                </div>""", unsafe_allow_html=True)

                if st.button(f"Start session with {num_questions} question{'s' if num_questions > 1 else ''} →", type="primary"):
                    diff_label = difficulty.split("—")[0].strip()
                    with st.spinner("Creating your questions... ⏳"):
                        if mode == "Based on my resume (if uploaded)" and "original_resume" in st.session_state:
                            prompt = (f"You are an expert interviewer. Read this resume and generate exactly {num_questions} "
                                      f"'{diff_label}' difficulty interview questions for the field '{field}'. "
                                      f"Resume: {st.session_state['original_resume']}. "
                                      f"Return ONLY a numbered list from 1 to {num_questions}, one question per line.")
                        else:
                            prompt = (f"You are an expert interviewer. Generate exactly {num_questions} '{diff_label}' "
                                      f"difficulty interview questions for the field '{field}'. "
                                      f"Return ONLY a numbered list from 1 to {num_questions}, one question per line.")
                        try:
                            response = model.generate_content(prompt)
                            lines = response.text.strip().split("\n")
                            questions = [l.split(".", 1)[1].strip() if "." in l else l.strip()
                                         for l in lines if l.strip()]
                            st.session_state["questions_list"]    = questions[:num_questions]
                            st.session_state["current_q_index"]   = 0
                            st.session_state["interview_started"] = True
                            st.session_state["live_session_active"] = True
                            st.rerun()
                        except Exception as e:
                            st.error(f"Could not generate questions: {e}")

                st.markdown("</div>", unsafe_allow_html=True)

        # ── LIVE SESSION SCREEN ──────────────────────────────────────────────────
        else:
            q_list      = st.session_state["questions_list"]
            current_idx = st.session_state["current_q_index"]

            if current_idx < len(q_list):

                # ── Header row: progress + END SESSION button ──────────────────
                progress_pct = int(current_idx / len(q_list) * 100)

                hdr_left, hdr_right = st.columns([4, 1])
                with hdr_left:
                    st.markdown(f"""
                    <div style="padding:24px 0 0 32px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                            <span style="font-size:14px; font-weight:500; color:{TEXT_MUTED};">
                                Question {current_idx + 1} of {len(q_list)}
                            </span>
                            <span style="font-size:13px; color:{TEXT_MUTED};">{progress_pct}% done</span>
                        </div>
                        <div style="background:{SURFACE2}; border-radius:6px; height:8px; overflow:hidden; margin-right:32px;">
                            <div style="background:{ACCENT}; height:100%; width:{progress_pct}%; border-radius:6px;"></div>
                        </div>
                    </div>""", unsafe_allow_html=True)
                with hdr_right:
                    st.markdown("<div style='margin-top:28px; padding-right:32px;'>", unsafe_allow_html=True)
                    st.markdown('<div class="end-session-btn">', unsafe_allow_html=True)
                    if st.button("⏹ End session"):
                        reset_interview()
                        st.rerun()
                    st.markdown("</div></div>", unsafe_allow_html=True)

                # ── Question card ──────────────────────────────────────────────
                st.markdown(f"""
                <div style="padding:20px 32px 0;">
                    <div style="background:{SURFACE}; border:1.5px solid {BORDER};
                                border-left:5px solid {ACCENT}; border-radius:14px; padding:28px;">
                        <div style="font-size:12px; font-weight:600; color:{ACCENT_TEXT};
                                    text-transform:uppercase; letter-spacing:0.5px; margin-bottom:10px;">
                            Question {current_idx + 1}
                        </div>
                        <p style="color:{TEXT}; font-size:20px; font-weight:600; line-height:1.5; margin:0;">
                            {q_list[current_idx]}
                        </p>
                    </div>
                </div>""", unsafe_allow_html=True)

                # ── LIVE VIDEO COMPONENT ───────────────────────────────────────
                st.markdown(f"""
                <div style="padding:20px 32px 0;">
                    <p style="color:{TEXT_MUTED}; font-size:14px; line-height:1.6; margin-bottom:16px;">
                        🎥 Your live interview session is below. The AI will analyse your face expressions every 5 seconds
                        and show coaching tips in the chat panel on the right. Speak your answer out loud.
                    </p>
                </div>""", unsafe_allow_html=True)

                current_question = q_list[current_idx]
                live_component_html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }}
  body {{ background: transparent; }}
  .session-wrap {{
    display: flex; gap: 16px; height: 520px; padding: 0;
  }}
  .video-panel {{
    flex: 1.2; background: #0f1623; border-radius: 16px; overflow: hidden;
    position: relative; display: flex; flex-direction: column;
  }}
  video {{
    width: 100%; height: 100%; object-fit: cover; display: block;
  }}
  .video-overlay {{
    position: absolute; bottom: 0; left: 0; right: 0;
    background: linear-gradient(transparent, rgba(0,0,0,0.7));
    padding: 16px;
  }}
  .mic-btn {{
    display: flex; align-items: center; gap: 8px; background: rgba(255,255,255,0.15);
    border: 1.5px solid rgba(255,255,255,0.3); color: white; border-radius: 10px;
    padding: 10px 18px; cursor: pointer; font-size: 14px; font-weight: 500;
    backdrop-filter: blur(4px);
  }}
  .mic-btn.recording {{ background: rgba(220,38,38,0.7); border-color: #f87171; }}
  .pulse {{ display: inline-block; width: 10px; height: 10px; border-radius: 50%;
            background: #22c55e; animation: pulse 1.2s infinite; }}
  .pulse.red {{ background: #f87171; }}
  @keyframes pulse {{ 0%,100%{{ opacity:1; transform:scale(1); }} 50%{{ opacity:0.5; transform:scale(1.3); }} }}
  .status-bar {{
    position: absolute; top: 14px; left: 14px; right: 14px;
    display: flex; align-items: center; gap: 8px;
    background: rgba(0,0,0,0.5); border-radius: 8px; padding: 8px 12px;
    color: white; font-size: 13px; backdrop-filter: blur(4px);
  }}
  .chat-panel {{
    flex: 1; background: {SURFACE}; border: 1.5px solid {BORDER}; border-radius: 16px;
    display: flex; flex-direction: column; overflow: hidden;
  }}
  .chat-header {{
    padding: 14px 18px; border-bottom: 1.5px solid {BORDER};
    font-size: 14px; font-weight: 600; color: {TEXT};
    display: flex; align-items: center; gap: 8px;
  }}
  .chat-messages {{
    flex: 1; overflow-y: auto; padding: 16px; display: flex;
    flex-direction: column; gap: 12px;
  }}
  .msg {{
    padding: 12px 14px; border-radius: 12px; font-size: 13px; line-height: 1.6;
    max-width: 100%;
  }}
  .msg.ai {{
    background: {ACCENT_SOFT}; color: {ACCENT_TEXT};
    border-bottom-left-radius: 4px;
  }}
  .msg.system {{
    background: {SURFACE2}; color: {TEXT_MUTED};
    font-style: italic; text-align: center; font-size: 12px;
  }}
  .msg-label {{
    font-size: 11px; font-weight: 600; color: {TEXT_MUTED}; margin-bottom: 4px;
    text-transform: uppercase; letter-spacing: 0.4px;
  }}
  .thinking {{
    display: flex; gap: 4px; padding: 12px 14px;
    background: {ACCENT_SOFT}; border-radius: 12px; width: fit-content;
  }}
  .dot {{ width: 7px; height: 7px; border-radius: 50%; background: {ACCENT};
          animation: bounce 1.2s infinite; }}
  .dot:nth-child(2) {{ animation-delay: 0.2s; }}
  .dot:nth-child(3) {{ animation-delay: 0.4s; }}
  @keyframes bounce {{ 0%,100%{{ transform:translateY(0); }} 50%{{ transform:translateY(-5px); }} }}
  .chat-footer {{
    padding: 12px 16px; border-top: 1.5px solid {BORDER};
    font-size: 12px; color: {TEXT_MUTED}; text-align: center;
  }}
  .timer-badge {{
    display: inline-block; background: {ACCENT_SOFT}; color: {ACCENT_TEXT};
    border-radius: 20px; padding: 2px 10px; font-size: 12px; font-weight: 600;
  }}
</style>
</head>
<body>
<div class="session-wrap">

  <!-- VIDEO PANEL -->
  <div class="video-panel">
    <video id="videoEl" autoplay playsinline muted></video>
    <div class="status-bar">
      <span class="pulse" id="liveDot"></span>
      <span id="statusText">Starting camera...</span>
      <span style="margin-left:auto;" class="timer-badge" id="timerBadge">Next scan: 5s</span>
    </div>
    <div class="video-overlay">
      <div style="font-size:12px; color:rgba(255,255,255,0.7); margin-bottom:8px;">
        🎤 Speak your answer out loud to this question:
      </div>
      <div style="color:white; font-size:14px; font-weight:600; line-height:1.4;">
        {current_question}
      </div>
    </div>
  </div>

  <!-- CHAT PANEL -->
  <div class="chat-panel">
    <div class="chat-header">
      🤖 AI Coach
      <span style="margin-left:auto; font-size:12px; color:{TEXT_MUTED}; font-weight:400;">
        Live feedback every 5s
      </span>
    </div>
    <div class="chat-messages" id="chatMessages">
      <div class="msg system">Session started. Allow camera access to begin.</div>
    </div>
    <div class="chat-footer">
      AI is watching your face expressions and giving real-time coaching tips
    </div>
  </div>

</div>

<canvas id="snapCanvas" style="display:none;"></canvas>

<script>
const GEMINI_KEY = "{GEMINI_API_KEY}";
const QUESTION   = `{current_question}`;
const INTERVAL_MS = 5000;

const video      = document.getElementById('videoEl');
const canvas     = document.getElementById('snapCanvas');
const chat       = document.getElementById('chatMessages');
const statusText = document.getElementById('statusText');
const liveDot    = document.getElementById('liveDot');
const timerBadge = document.getElementById('timerBadge');

let frameCount  = 0;
let countdown   = 5;
let timerHandle = null;
let analyseHandle = null;
let stream      = null;

function addMsg(text, type='ai') {{
  const thinking = document.querySelector('.thinking');
  if (thinking) thinking.remove();
  const wrap = document.createElement('div');
  if (type === 'ai') {{
    const label = document.createElement('div');
    label.className = 'msg-label';
    label.textContent = '🤖 AI Coach · Snap ' + frameCount;
    wrap.appendChild(label);
  }}
  const msg = document.createElement('div');
  msg.className = 'msg ' + type;
  msg.textContent = text;
  wrap.appendChild(msg);
  chat.appendChild(wrap);
  chat.scrollTop = chat.scrollHeight;
}}

function showThinking() {{
  const d = document.createElement('div');
  d.className = 'thinking';
  d.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
  chat.appendChild(d);
  chat.scrollTop = chat.scrollHeight;
}}

async function analyseFrame() {{
  if (!stream) return;
  frameCount++;
  canvas.width  = video.videoWidth  || 640;
  canvas.height = video.videoHeight || 480;
  canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
  const b64 = canvas.toDataURL('image/jpeg', 0.7).split(',')[1];
  showThinking();
  statusText.textContent = 'Analysing...';
  liveDot.classList.add('red');

  try {{
    const res = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${{GEMINI_KEY}}`,
      {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{
          contents: [{{
            parts: [
              {{ text: `You are a friendly interview coach watching a candidate answer this question: "${{QUESTION}}".
Look at their face expression, posture, and confidence level in this image.
Give ONE short, specific, encouraging coaching tip (2-3 sentences max) about:
- Eye contact / looking at camera
- Facial expression (smile, nervousness, confidence)
- Body language
- Or general encouragement
Be warm, specific, and constructive. Do NOT repeat previous generic advice.` }},
              {{ inline_data: {{ mime_type: 'image/jpeg', data: b64 }} }}
            ]
          }}]
        }})
      }}
    );
    const data = await res.json();
    const tip  = data?.candidates?.[0]?.content?.parts?.[0]?.text || 'Keep going, you are doing great!';
    addMsg(tip.trim(), 'ai');
  }} catch(e) {{
    addMsg('Could not reach AI — check your connection.', 'system');
  }}

  statusText.textContent = 'Live';
  liveDot.classList.remove('red');
  countdown = 5;
}}

function startCountdown() {{
  timerHandle = setInterval(() => {{
    countdown--;
    timerBadge.textContent = countdown > 0 ? `Next scan: ${{countdown}}s` : 'Scanning...';
    if (countdown <= 0) countdown = 5;
  }}, 1000);
}}

async function startCamera() {{
  try {{
    stream = await navigator.mediaDevices.getUserMedia({{ video: true, audio: false }});
    video.srcObject = stream;
    statusText.textContent = 'Live';
    addMsg(`Camera ready! I'll watch your expressions as you answer. Take a breath and start speaking whenever you're ready. 🎯`, 'ai');
    frameCount = 0;
    countdown  = 5;
    startCountdown();
    analyseFrame();
    analyseHandle = setInterval(analyseFrame, INTERVAL_MS);
  }} catch(e) {{
    statusText.textContent = 'Camera blocked';
    addMsg('Camera access was denied. Please allow camera in your browser settings and refresh.', 'system');
  }}
}}

startCamera();
</script>
</body>
</html>"""

                components.html(live_component_html, height=560, scrolling=False)

                # ── Audio answer + feedback ────────────────────────────────────
                st.markdown(f"""
                <div style="padding:20px 32px 0;">
                    <p style="color:{TEXT}; font-weight:600; font-size:15px; margin-bottom:4px;">
                        🎙️ Record your spoken answer for detailed feedback
                    </p>
                    <p style="color:{TEXT_MUTED}; font-size:13px; margin-bottom:12px;">
                        When you've finished speaking, record your answer below and tap "Get detailed feedback".
                    </p>
                </div>""", unsafe_allow_html=True)

                _, col_audio, _ = st.columns([1, 3, 1])
                with col_audio:
                    audio_input = st.audio_input("Record your answer", label_visibility="collapsed")
                    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
                    if audio_input:
                        if st.button("Get detailed feedback on this answer ✨", type="primary"):
                            with st.spinner("Analysing your answer... ⏳"):
                                prompt = (f"You are a friendly and encouraging interview coach. "
                                          f"The candidate just answered this interview question: '{q_list[current_idx]}'. "
                                          f"Listen to their audio and give feedback in 3 clear sections: "
                                          f"1) ✅ What they did well, "
                                          f"2) 💡 What to improve, "
                                          f"3) 📝 A strong model answer. "
                                          f"Keep language simple, warm, and constructive.")
                                try:
                                    response = model.generate_content([
                                        prompt,
                                        {"mime_type": "audio/wav", "data": audio_input.read()}
                                    ])
                                    st.session_state[f"feedback_{current_idx}"] = response.text
                                    st.session_state["interviews_completed"] += 1
                                    update_user_stats(st.session_state["user_profile_email"], "interviews_completed")
                                except Exception as e:
                                    st.error(f"Could not get feedback: {e}")

                if f"feedback_{current_idx}" in st.session_state:
                    st.markdown(f"""
                    <div style="padding:0 32px;">
                        <div style="background:{SUCCESS_BG}; border:1.5px solid {SUCCESS};
                                    border-radius:14px; padding:20px; margin-top:16px;">
                            <h3 style="color:{SUCCESS}; font-size:15px; font-weight:600; margin-bottom:10px;">
                                ✅ Your feedback for question {current_idx + 1}
                            </h3>
                        </div>
                    </div>""", unsafe_allow_html=True)
                    _, col_fb, _ = st.columns([1, 3, 1])
                    with col_fb:
                        st.markdown(st.session_state[f"feedback_{current_idx}"])
                        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
                        col_next, col_end = st.columns([3, 1])
                        with col_next:
                            if st.button("Next question →", type="primary"):
                                st.session_state["current_q_index"] += 1
                                st.rerun()
                        with col_end:
                            st.markdown('<div class="end-session-btn">', unsafe_allow_html=True)
                            if st.button("⏹ End session"):
                                reset_interview()
                                st.rerun()
                            st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("<div style='height:32px;'></div>", unsafe_allow_html=True)

            else:
                # ── All done ──────────────────────────────────────────────────
                st.markdown(f"""
                <div style="text-align:center; padding:60px 32px;">
                    <div style="font-size:56px; margin-bottom:20px;">🎉</div>
                    <h2 style="color:{TEXT}; font-size:26px; font-weight:700; margin-bottom:10px;">
                        Session complete!
                    </h2>
                    <p style="color:{TEXT_MUTED}; font-size:16px; max-width:440px; margin:0 auto 32px; line-height:1.6;">
                        Great work finishing all {len(q_list)} question{'s' if len(q_list) > 1 else ''}.
                        Keep practising regularly and you'll feel much more confident in real interviews.
                    </p>
                </div>""", unsafe_allow_html=True)
                st.balloons()
                _, col_btn, _ = st.columns([2, 1, 2])
                with col_btn:
                    if st.button("Start a new session →", type="primary"):
                        reset_interview()
                        st.rerun()

    # ══════════════════════════════════════════════════════════════════════════════
    # RESUME CHECKER
    # ══════════════════════════════════════════════════════════════════════════════
    with tab_resume:
        inner_tab1, inner_tab2 = st.tabs(["🔍  Check against a job", "✍️  Improve my resume"])

        with inner_tab1:
            section_header("Check your resume against a job", "We'll tell you which keywords and skills are missing.")
            _, col_r, _ = st.columns([1, 3, 1])
            with col_r:
                uploaded_file = st.file_uploader("Upload your resume (PDF)", type="pdf")
                jd = st.text_area("Paste the job description here", height=180,
                                   placeholder="Copy and paste the full job posting text here...")
                st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
                if st.button("Check my resume →", type="primary"):
                    if not jd:
                        st.warning("Please paste the job description first.")
                    elif not (uploaded_file or "original_resume" in st.session_state):
                        st.warning("Please upload your resume first.")
                    else:
                        if uploaded_file:
                            with pdfplumber.open(uploaded_file) as pdf:
                                st.session_state["original_resume"] = "".join(p.extract_text() or "" for p in pdf.pages)
                        with st.spinner("Comparing your resume to the job description... ⏳"):
                            prompt = (f"You are a helpful career coach. Compare this resume to the job description. "
                                      f"Give clear, simple feedback in 3 sections: "
                                      f"1) ✅ Keywords and skills that match, "
                                      f"2) ❌ Important keywords that are missing, "
                                      f"3) 💡 Specific suggestions to improve the resume for this job. "
                                      f"Keep language plain and easy to understand. "
                                      f"Resume: {st.session_state['original_resume']} "
                                      f"Job description: {jd}")
                            response = model.generate_content(prompt)
                            st.session_state["resume_analysis"] = response.text
                            st.session_state["resumes_analyzed"] += 1
                            update_user_stats(st.session_state["user_profile_email"], "resumes_analyzed")

                if "resume_analysis" in st.session_state:
                    st.markdown(f"""
                    <div style="background:{ACCENT_SOFT}; border:1.5px solid {BORDER};
                                border-radius:14px; padding:20px; margin-top:20px;">
                        <h3 style="color:{ACCENT_TEXT}; font-size:15px; font-weight:600; margin-bottom:10px;">
                            📋 Your resume analysis
                        </h3>
                    </div>""", unsafe_allow_html=True)
                    st.markdown(st.session_state["resume_analysis"])

        with inner_tab2:
            section_header("Improve your resume wording", "We'll rewrite it to sound more professional and impactful.")
            _, col_e, _ = st.columns([1, 3, 1])
            with col_e:
                if "original_resume" not in st.session_state:
                    st.info("👆 Upload your resume in the 'Check against a job' tab first, then come back here.")
                else:
                    if st.button("✨ Suggest improvements", type="primary"):
                        with st.spinner("Improving your resume wording... ⏳"):
                            prompt = (f"You are a professional resume writer. "
                                      f"Rewrite and improve this resume to use stronger, clearer language. "
                                      f"Keep all the facts the same — only improve the wording and structure. "
                                      f"Resume: {st.session_state['original_resume']}")
                            correction = model.generate_content(prompt)
                            st.session_state["edited_version"] = correction.text
                    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
                    edited_text = st.text_area("Your improved resume (you can edit this)",
                                               value=st.session_state.get("edited_version",
                                                                           st.session_state.get("original_resume", "")),
                                               height=440)
                    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
                    st.download_button("⬇️ Download improved resume", edited_text,
                                       file_name="my_improved_resume.txt", mime="text/plain")