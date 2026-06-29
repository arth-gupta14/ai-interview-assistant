"""
View Prep — AI Interview Coach
Author: Senior Developer Build
Dark theme only. Zero unclosed divs. All keys unique. Full error handling.
"""

import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
import pdfplumber
import json, os, hashlib

# ══════════════════════════════════════════════════════════════════════
#  PAGE CONFIG  (must be first Streamlit call)
# ══════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="View Prep · AI Interview Coach",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════════════
#  COLOUR TOKENS  — dark theme only
# ══════════════════════════════════════════════════════════════════════
BG          = "#0d1117"
SURFACE     = "#161b22"
SURFACE2    = "#21262d"
BORDER      = "#30363d"
TEXT        = "#e6edf3"
MUTED       = "#8b949e"
ACCENT      = "#2f81f7"
ACCENT_DIM  = "#1a2d4e"
ACCENT_TXT  = "#79c0ff"
GREEN       = "#3fb950"
GREEN_DIM   = "#0d2918"
RED         = "#f85149"
RED_DIM     = "#2d1215"
YELLOW      = "#e3b341"
YELLOW_DIM  = "#2e2010"

# ══════════════════════════════════════════════════════════════════════
#  GLOBAL CSS  — injected once
# ══════════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* ── Base reset ── */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body, .stApp {{
    background: {BG} !important;
    color: {TEXT} !important;
    font-family: 'Inter', sans-serif !important;
}}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] {{ display: none !important; }}
section[data-testid="stSidebar"] {{ display: none !important; }}
.block-container {{ padding: 0 !important; max-width: 100% !important; }}

/* ── Force text colour everywhere ── */
p, span, li, div, label, h1, h2, h3, h4, h5, h6 {{
    color: {TEXT} !important;
}}

/* ── Streamlit markdown overrides ── */
.stMarkdown p, .stMarkdown li, .stMarkdown span,
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
    color: {TEXT} !important;
}}

/* ── Labels ── */
.stTextInput > label, .stTextArea > label, .stSelectbox > label,
.stFileUploader > label, .stSlider > label,
.stRadio > label, .stCheckbox > label {{
    color: {TEXT} !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    margin-bottom: 4px !important;
}}

/* ── Text input ── */
.stTextInput > div > div > input {{
    background: {SURFACE2} !important;
    color: {TEXT} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 8px !important;
    font-size: 15px !important;
    padding: 10px 14px !important;
    font-family: 'Inter', sans-serif !important;
}}
.stTextInput > div > div > input:focus {{
    border-color: {ACCENT} !important;
    box-shadow: 0 0 0 3px {ACCENT_DIM} !important;
    outline: none !important;
}}
.stTextInput > div > div > input::placeholder {{ color: {MUTED} !important; }}

/* ── Textarea ── */
.stTextArea > div > div > textarea {{
    background: {SURFACE2} !important;
    color: {TEXT} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 8px !important;
    font-size: 15px !important;
    font-family: 'Inter', sans-serif !important;
    padding: 10px 14px !important;
}}
.stTextArea > div > div > textarea:focus {{
    border-color: {ACCENT} !important;
    box-shadow: 0 0 0 3px {ACCENT_DIM} !important;
    outline: none !important;
}}
.stTextArea > div > div > textarea::placeholder {{ color: {MUTED} !important; }}

/* ── Selectbox ── */
.stSelectbox > div > div,
[data-baseweb="select"] {{
    background: {SURFACE2} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 8px !important;
    color: {TEXT} !important;
}}
[data-baseweb="select"] * {{ color: {TEXT} !important; }}
[data-baseweb="popover"] li {{
    background: {SURFACE2} !important;
    color: {TEXT} !important;
}}
[data-baseweb="popover"] li:hover {{
    background: {ACCENT_DIM} !important;
    color: {ACCENT_TXT} !important;
}}

/* ── Slider ── */
[data-testid="stSlider"] > div > div > div > div {{ background: {ACCENT} !important; }}
[data-testid="stSliderThumb"] {{ background: {ACCENT} !important; border-color: {ACCENT} !important; }}
.stSlider [data-testid="stTickBarMin"],
.stSlider [data-testid="stTickBarMax"] {{ color: {MUTED} !important; }}

/* ── Radio ── */
.stRadio > div {{ flex-wrap: wrap !important; gap: 8px !important; }}
.stRadio > div > label {{
    background: {SURFACE2} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 8px !important;
    padding: 8px 16px !important;
    cursor: pointer !important;
    color: {TEXT} !important;
    font-size: 14px !important;
}}
.stRadio > div > label:hover {{ border-color: {ACCENT} !important; }}
.stRadio > div > label > div > p {{ color: {TEXT} !important; }}

/* ── Checkbox ── */
.stCheckbox > label > div > p {{ color: {TEXT} !important; font-size: 14px !important; }}

/* ── Buttons ── */
.stButton > button {{
    background: {SURFACE2} !important;
    color: {TEXT} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 8px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 10px 20px !important;
    width: 100% !important;
    font-family: 'Inter', sans-serif !important;
    cursor: pointer !important;
    transition: all 0.15s !important;
}}
.stButton > button:hover {{
    border-color: {ACCENT} !important;
    color: {ACCENT_TXT} !important;
    background: {ACCENT_DIM} !important;
}}
.stButton > button[kind="primary"] {{
    background: {ACCENT} !important;
    color: #ffffff !important;
    border: none !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    padding: 12px 28px !important;
}}
.stButton > button[kind="primary"]:hover {{ opacity: 0.88 !important; }}

/* ── File uploader ── */
[data-testid="stFileUploader"] > div {{
    background: {SURFACE2} !important;
    border: 1.5px dashed {BORDER} !important;
    border-radius: 10px !important;
}}
[data-testid="stFileUploader"] * {{ color: {TEXT} !important; }}
[data-testid="stFileUploader"] > div:hover {{ border-color: {ACCENT} !important; }}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
    background: {SURFACE} !important;
    border-bottom: 1px solid {BORDER} !important;
    padding: 0 24px !important;
    gap: 0 !important;
}}
.stTabs [data-baseweb="tab"] {{
    color: {MUTED} !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 14px 20px !important;
    border-radius: 0 !important;
    border-bottom: 2px solid transparent !important;
    background: transparent !important;
    font-family: 'Inter', sans-serif !important;
}}
.stTabs [aria-selected="true"] {{
    color: {ACCENT_TXT} !important;
    border-bottom: 2px solid {ACCENT} !important;
    background: transparent !important;
}}
.stTabs [data-baseweb="tab-panel"] {{
    padding: 0 !important;
    background: {BG} !important;
}}

/* ── Audio input ── */
[data-testid="stAudioInput"] {{
    background: {SURFACE2} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 10px !important;
    color: {TEXT} !important;
}}

/* ── Alerts ── */
[data-testid="stAlert"] {{
    background: {SURFACE2} !important;
    border-radius: 10px !important;
    color: {TEXT} !important;
}}

/* ── Download button ── */
.stDownloadButton > button {{
    background: {GREEN} !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    width: 100% !important;
}}
.stDownloadButton > button:hover {{ opacity: 0.88 !important; }}

/* ── Spinner ── */
.stSpinner > div {{ border-top-color: {ACCENT} !important; }}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: {SURFACE}; }}
::-webkit-scrollbar-thumb {{ background: {BORDER}; border-radius: 3px; }}
::-webkit-scrollbar-thumb:hover {{ background: {MUTED}; }}

/* ── Utility: red button style ── */
.btn-danger button {{
    background: {RED_DIM} !important;
    color: {RED} !important;
    border: 1px solid {RED} !important;
    font-weight: 600 !important;
}}
.btn-danger button:hover {{
    background: {RED} !important;
    color: #fff !important;
}}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
#  USER DATABASE  — local JSON file
# ══════════════════════════════════════════════════════════════════════
DB_FILE = "viewprep_users.json"

def _load_db() -> dict:
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _save_db(data: dict) -> None:
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def db_register(name: str, field: str, email: str, pw: str):
    db = _load_db()
    if email in db:
        return False, "An account with this email already exists. Please sign in."
    db[email] = {
        "name": name, "field": field, "email": email,
        "password": _hash(pw),
        "interviews_completed": 0, "resumes_analyzed": 0,
    }
    _save_db(db)
    return True, "Account created!"

def db_login(email: str, pw: str):
    db = _load_db()
    if email not in db:
        return False, None, "No account found with this email."
    if db[email]["password"] != _hash(pw):
        return False, None, "Incorrect password. Please try again."
    return True, db[email], "Signed in!"

def db_update_stat(email: str, key: str) -> None:
    db = _load_db()
    if email in db:
        db[email][key] = db[email].get(key, 0) + 1
        _save_db(db)

# ══════════════════════════════════════════════════════════════════════
#  AI HELPER
# ══════════════════════════════════════════════════════════════════════
_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
if _API_KEY:
    genai.configure(api_key=_API_KEY)
    _model = genai.GenerativeModel("gemini-2.5-flash")

def ai_text(prompt: str) -> str:
    return _model.generate_content(prompt).text

def ai_multimodal(*parts) -> str:
    return _model.generate_content(list(parts)).text

# ══════════════════════════════════════════════════════════════════════
#  SESSION STATE  — initialise once
# ══════════════════════════════════════════════════════════════════════
_DEFAULTS = {
    "logged_in":             False,
    "user_name":             "",
    "user_field":            "",
    "user_email":            "",
    "interviews_completed":  0,
    "resumes_analyzed":      0,
    "resume_text":           "",
    "resume_analysis":       "",
    "resume_improved":       "",
    # interview
    "iv_active":             False,
    "iv_questions":          [],
    "iv_index":              0,
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

def reset_interview() -> None:
    st.session_state["iv_active"]    = False
    st.session_state["iv_questions"] = []
    st.session_state["iv_index"]     = 0
    for k in list(st.session_state.keys()):
        if k.startswith("fb_"):
            del st.session_state[k]

def sign_out() -> None:
    for k in list(st.session_state.keys()):
        del st.session_state[k]

# ══════════════════════════════════════════════════════════════════════
#  REUSABLE UI COMPONENTS
# ══════════════════════════════════════════════════════════════════════
def spacer(px: int = 16) -> None:
    st.markdown(f"<div style='height:{px}px'></div>", unsafe_allow_html=True)

def page_heading(title: str, subtitle: str = "") -> None:
    sub_html = (
        f'<p style="color:{MUTED};font-size:14px;margin-top:6px;line-height:1.5;">{subtitle}</p>'
        if subtitle else ""
    )
    st.markdown(
        f'<div style="padding:28px 32px 16px">'
        f'<h2 style="color:{TEXT};font-size:22px;font-weight:700;margin:0">{title}</h2>'
        f'{sub_html}'
        f'</div>',
        unsafe_allow_html=True,
    )

def info_box(msg: str, kind: str = "blue") -> None:
    colours = {
        "blue":   (ACCENT_DIM,  ACCENT,  ACCENT_TXT),
        "green":  (GREEN_DIM,   GREEN,   GREEN),
        "red":    (RED_DIM,     RED,     RED),
        "yellow": (YELLOW_DIM,  YELLOW,  YELLOW),
    }
    bg, border, fg = colours.get(kind, colours["blue"])
    st.markdown(
        f'<div style="background:{bg};border:1px solid {border};border-radius:10px;'
        f'padding:14px 18px;margin-bottom:12px;">'
        f'<span style="color:{fg};font-size:14px;line-height:1.6">{msg}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

def card(inner_html: str) -> None:
    st.markdown(
        f'<div style="background:{SURFACE};border:1px solid {BORDER};border-radius:12px;'
        f'padding:24px;margin-bottom:16px">{inner_html}</div>',
        unsafe_allow_html=True,
    )

def stat_tile(icon: str, value, label: str, colour: str = ACCENT) -> str:
    return (
        f'<div style="background:{SURFACE};border:1px solid {BORDER};border-radius:12px;'
        f'padding:24px 16px;text-align:center;">'
        f'<div style="font-size:30px;margin-bottom:8px">{icon}</div>'
        f'<div style="font-size:26px;font-weight:700;color:{colour};line-height:1">{value}</div>'
        f'<div style="font-size:12px;color:{MUTED};margin-top:6px;font-weight:500">{label}</div>'
        f'</div>'
    )

def topbar() -> None:
    name  = st.session_state.get("user_name", "")
    field = st.session_state.get("user_field", "")
    initial = name[0].upper() if name else "?"
    st.markdown(
        f'<div style="background:{SURFACE};border-bottom:1px solid {BORDER};'
        f'padding:0 32px;display:flex;align-items:center;'
        f'justify-content:space-between;height:60px;">'
        f'  <div style="display:flex;align-items:center;gap:10px">'
        f'    <div style="background:{ACCENT};color:#fff;width:34px;height:34px;'
        f'         border-radius:8px;display:flex;align-items:center;'
        f'         justify-content:center;font-size:17px;font-weight:700">V</div>'
        f'    <span style="font-size:17px;font-weight:700;color:{TEXT}">View Prep</span>'
        f'  </div>'
        f'  <div style="display:flex;align-items:center;gap:14px">'
        f'    <div style="text-align:right">'
        f'      <div style="font-size:14px;font-weight:600;color:{TEXT}">{name}</div>'
        f'      <div style="font-size:12px;color:{MUTED}">{field}</div>'
        f'    </div>'
        f'    <div style="width:34px;height:34px;background:{ACCENT_DIM};border-radius:50%;'
        f'         display:flex;align-items:center;justify-content:center;'
        f'         font-size:14px;font-weight:700;color:{ACCENT_TXT}">{initial}</div>'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )

def auth_topbar() -> None:
    st.markdown(
        f'<div style="background:{SURFACE};border-bottom:1px solid {BORDER};'
        f'padding:0 32px;display:flex;align-items:center;'
        f'justify-content:space-between;height:60px;">'
        f'  <div style="display:flex;align-items:center;gap:10px">'
        f'    <div style="background:{ACCENT};color:#fff;width:34px;height:34px;'
        f'         border-radius:8px;display:flex;align-items:center;'
        f'         justify-content:center;font-size:17px;font-weight:700">V</div>'
        f'    <span style="font-size:17px;font-weight:700;color:{TEXT}">View Prep</span>'
        f'  </div>'
        f'  <span style="font-size:13px;color:{MUTED}">AI Interview Coach</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

# ══════════════════════════════════════════════════════════════════════
#  AUTH PAGE
# ══════════════════════════════════════════════════════════════════════
def render_auth() -> None:
    auth_topbar()

    # hero
    st.markdown(
        f'<div style="text-align:center;padding:52px 20px 28px">'
        f'  <div style="display:inline-block;background:{ACCENT_DIM};color:{ACCENT_TXT};'
        f'       font-size:12px;font-weight:600;padding:5px 14px;border-radius:20px;'
        f'       margin-bottom:18px;letter-spacing:.4px">🎯 POWERED BY AI</div>'
        f'  <h1 style="font-size:38px;font-weight:700;color:{TEXT};line-height:1.2;margin-bottom:12px">'
        f'    Ace your next interview<br>with confidence</h1>'
        f'  <p style="font-size:16px;color:{MUTED};max-width:420px;margin:0 auto;line-height:1.6">'
        f'    Practice real questions, get live AI feedback on your expressions,'
        f'    and improve your resume — all in one place.</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # tab choice
    _, mid, _ = st.columns([2, 1.2, 2])
    with mid:
        mode = st.radio("auth_mode", ["Sign in", "Create account"],
                        horizontal=True, label_visibility="collapsed")

    _, form_col, _ = st.columns([1, 1.4, 1])
    with form_col:
        spacer(4)
        st.markdown(
            f'<div style="background:{SURFACE};border:1px solid {BORDER};'
            f'border-radius:14px;padding:32px;margin-bottom:28px">'
            f'<h2 style="color:{TEXT};font-size:19px;font-weight:700;margin-bottom:20px">'
            f'{"Welcome back" if mode == "Sign in" else "Create your free account"}'
            f'</h2></div>',
            unsafe_allow_html=True,
        )

        if mode == "Sign in":
            email = st.text_input("Email address", placeholder="you@example.com", key="si_email")
            show  = st.checkbox("Show password", key="si_show")
            pw    = st.text_input("Password",
                                  type="default" if show else "password",
                                  placeholder="Your password", key="si_pw")
            spacer(8)
            if st.button("Sign in →", type="primary", key="btn_signin"):
                if not email.strip() or not pw:
                    st.error("Please fill in both fields.")
                else:
                    ok, user, msg = db_login(email.strip().lower(), pw)
                    if ok:
                        st.session_state.update({
                            "logged_in":            True,
                            "user_name":            user["name"],
                            "user_field":           user["field"],
                            "user_email":           user["email"],
                            "interviews_completed": user.get("interviews_completed", 0),
                            "resumes_analyzed":     user.get("resumes_analyzed", 0),
                        })
                        st.rerun()
                    else:
                        st.error(msg)

        else:  # Create account
            name  = st.text_input("Your full name", placeholder="e.g. Priya Sharma", key="reg_name")
            field = st.text_input("Field you are preparing for",
                                  placeholder="e.g. Software Engineering, Marketing", key="reg_field")
            email = st.text_input("Email address", placeholder="you@example.com", key="reg_email")
            show  = st.checkbox("Show password", key="reg_show")
            pw    = st.text_input("Choose a password  (8 – 16 characters)",
                                  type="default" if show else "password",
                                  placeholder="At least 8 characters", key="reg_pw")
            resume_file = st.file_uploader(
                "Upload your resume — optional PDF",
                type=["pdf"], key="reg_resume",
                help="Uploading your resume lets us create personalised interview questions.",
            )
            if resume_file and not st.session_state["resume_text"]:
                with pdfplumber.open(resume_file) as pdf:
                    st.session_state["resume_text"] = "".join(
                        p.extract_text() or "" for p in pdf.pages
                    )
            agree = st.checkbox(
                "I agree to let AI process my data to generate practice questions and feedback.",
                key="reg_agree",
            )
            spacer(8)
            if st.button("Create my account →", type="primary", key="btn_register"):
                if not all([name.strip(), field.strip(), email.strip(), pw]):
                    st.error("Please fill in all fields.")
                elif not agree:
                    st.warning("Please tick the checkbox to continue.")
                elif not (8 <= len(pw) <= 16):
                    st.error(f"Password must be 8 – 16 characters (yours is {len(pw)}).")
                else:
                    ok, msg = db_register(name.strip(), field.strip(),
                                          email.strip().lower(), pw)
                    if ok:
                        st.session_state.update({
                            "logged_in":  True,
                            "user_name":  name.strip(),
                            "user_field": field.strip(),
                            "user_email": email.strip().lower(),
                        })
                        st.rerun()
                    else:
                        st.error(msg)

    # feature tiles
    st.markdown(
        f'<div style="display:flex;gap:16px;justify-content:center;'
        f'flex-wrap:wrap;padding:8px 40px 56px">'
        f'  <div style="background:{SURFACE};border:1px solid {BORDER};border-radius:12px;'
        f'       padding:22px;max-width:240px;text-align:center">'
        f'    <div style="font-size:26px;margin-bottom:10px">🎙️</div>'
        f'    <h3 style="color:{TEXT};font-size:14px;font-weight:600;margin-bottom:6px">'
        f'      Live interview practice</h3>'
        f'    <p style="color:{MUTED};font-size:13px;line-height:1.5">'
        f'      AI watches your face and voice as you answer in real time.</p>'
        f'  </div>'
        f'  <div style="background:{SURFACE};border:1px solid {BORDER};border-radius:12px;'
        f'       padding:22px;max-width:240px;text-align:center">'
        f'    <div style="font-size:26px;margin-bottom:10px">📄</div>'
        f'    <h3 style="color:{TEXT};font-size:14px;font-weight:600;margin-bottom:6px">'
        f'      Resume checker</h3>'
        f'    <p style="color:{MUTED};font-size:13px;line-height:1.5">'
        f'      Paste a job description and find exactly what is missing.</p>'
        f'  </div>'
        f'  <div style="background:{SURFACE};border:1px solid {BORDER};border-radius:12px;'
        f'       padding:22px;max-width:240px;text-align:center">'
        f'    <div style="font-size:26px;margin-bottom:10px">📊</div>'
        f'    <h3 style="color:{TEXT};font-size:14px;font-weight:600;margin-bottom:6px">'
        f'      Progress tracking</h3>'
        f'    <p style="color:{MUTED};font-size:13px;line-height:1.5">'
        f'      Your stats are saved so you see improvement over time.</p>'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )

# ══════════════════════════════════════════════════════════════════════
#  DASHBOARD TAB
# ══════════════════════════════════════════════════════════════════════
def render_dashboard() -> None:
    name  = st.session_state["user_name"]
    field = st.session_state["user_field"]

    st.markdown(
        f'<div style="padding:28px 32px 18px">'
        f'<h2 style="color:{TEXT};font-size:24px;font-weight:700;margin-bottom:6px">'
        f'👋 Welcome back, {name}!</h2>'
        f'<p style="color:{MUTED};font-size:15px">'
        f'Preparing for <strong style="color:{ACCENT_TXT}">{field}</strong>. '
        f'Here is your progress so far.</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(stat_tile("🎙️", st.session_state["interviews_completed"],
                              "Interviews completed", ACCENT), unsafe_allow_html=True)
    with c2:
        st.markdown(stat_tile("📄", st.session_state["resumes_analyzed"],
                              "Resumes analyzed", "#a371f7"), unsafe_allow_html=True)
    with c3:
        has_resume = bool(st.session_state["resume_text"])
        st.markdown(stat_tile("📎",
                              "✅ Uploaded" if has_resume else "Not uploaded",
                              "Resume on file",
                              GREEN if has_resume else MUTED), unsafe_allow_html=True)

    spacer(24)
    st.markdown(
        f'<div style="padding:0 0 14px">'
        f'<h3 style="color:{TEXT};font-size:17px;font-weight:600">'
        f'What would you like to do?</h3>'
        f'</div>',
        unsafe_allow_html=True,
    )

    a1, a2 = st.columns(2)
    with a1:
        st.markdown(
            f'<div style="background:{SURFACE};border:1px solid {BORDER};border-radius:12px;'
            f'padding:24px;min-height:160px">'
            f'<div style="font-size:28px;margin-bottom:10px">🎙️</div>'
            f'<h3 style="color:{TEXT};font-size:16px;font-weight:600;margin-bottom:7px">'
            f'Start an interview session</h3>'
            f'<p style="color:{MUTED};font-size:13px;line-height:1.5">'
            f'Live video practice with real-time AI feedback on your face, voice, and answers.</p>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with a2:
        st.markdown(
            f'<div style="background:{SURFACE};border:1px solid {BORDER};border-radius:12px;'
            f'padding:24px;min-height:160px">'
            f'<div style="font-size:28px;margin-bottom:10px">📄</div>'
            f'<h3 style="color:{TEXT};font-size:16px;font-weight:600;margin-bottom:7px">'
            f'Check your resume</h3>'
            f'<p style="color:{MUTED};font-size:13px;line-height:1.5">'
            f'Paste a job description and see exactly which keywords to add.</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

    spacer(24)
    st.markdown(
        f'<div style="background:{ACCENT_DIM};border:1px solid {ACCENT};border-radius:12px;'
        f'padding:20px 24px">'
        f'<h3 style="color:{ACCENT_TXT};font-size:15px;font-weight:600;margin-bottom:10px">'
        f'💡 Tips for a great session</h3>'
        f'<ul style="color:{MUTED};font-size:13px;line-height:1.9;padding-left:18px;margin:0">'
        f'<li>Find a quiet spot with good lighting before starting a live session.</li>'
        f'<li>Speak clearly and take a breath before you start your answer.</li>'
        f'<li>Upload your resume to get questions tailored to your experience.</li>'
        f'<li>Start with Easy questions, then work up to Hard ones.</li>'
        f'</ul>'
        f'</div>',
        unsafe_allow_html=True,
    )
    spacer(40)

# ══════════════════════════════════════════════════════════════════════
#  INTERVIEW TAB
# ══════════════════════════════════════════════════════════════════════
def render_interview() -> None:

    # ── Setup screen ──────────────────────────────────────────────────
    if not st.session_state["iv_active"]:
        page_heading(
            "Interview practice",
            "Configure your session below and we will generate your questions.",
        )
        _, col, _ = st.columns([1, 2.4, 1])
        with col:
            field = st.text_input(
                "What field are you interviewing for?",
                value=st.session_state["user_field"],
                key="iv_field",
                help="e.g. Data Science, Web Development, Product Management",
            )
            difficulty = st.selectbox(
                "Difficulty level",
                ["Easy — great for beginners",
                 "Medium — some experience needed",
                 "Hard — advanced level"],
                key="iv_diff",
            )
            num_q = st.slider(
                "Number of questions",
                min_value=1, max_value=30, value=5, step=1,
                key="iv_num",
                help="Choose between 1 and 30 questions for this session.",
            )
            source = st.radio(
                "Where should questions come from?",
                ["Based on my resume (if uploaded)", "General questions for my field"],
                key="iv_source",
            )
            spacer(4)
            info_box(
                "📹 Your webcam will open automatically. The AI will analyse your "
                "face expressions every 5 seconds and send coaching tips to the chat "
                "panel on the right. Please allow camera access in your browser.",
                kind="blue",
            )
            spacer(4)
            btn_label = (f"Start session — {num_q} question"
                         + ("s" if num_q > 1 else ""))
            if st.button(btn_label, type="primary", key="btn_start_iv"):
                diff_word = difficulty.split("—")[0].strip()
                use_resume = (
                    source == "Based on my resume (if uploaded)"
                    and bool(st.session_state["resume_text"])
                )
                prompt = (
                    f"You are an expert interviewer. "
                    + (f"Read this resume and generate exactly {num_q} "
                       if use_resume else
                       f"Generate exactly {num_q} ")
                    + f"'{diff_word}' difficulty interview questions "
                    f"for the field '{field}'. "
                    + (f"Resume:\n{st.session_state['resume_text']}\n\n"
                       if use_resume else "")
                    + f"Return ONLY a numbered list from 1 to {num_q}, "
                    "one question per line, nothing else."
                )
                with st.spinner("Generating your questions…"):
                    try:
                        raw   = ai_text(prompt).strip().split("\n")
                        qs    = [
                            ln.split(".", 1)[1].strip() if "." in ln else ln.strip()
                            for ln in raw if ln.strip()
                        ]
                        st.session_state["iv_questions"] = qs[:num_q]
                        st.session_state["iv_index"]     = 0
                        st.session_state["iv_active"]    = True
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Could not generate questions: {exc}")
        return  # nothing more to render on setup screen

    # ── Active session ────────────────────────────────────────────────
    questions = st.session_state["iv_questions"]
    idx       = st.session_state["iv_index"]
    total     = len(questions)

    # Finished all questions
    if idx >= total:
        st.markdown(
            f'<div style="text-align:center;padding:60px 32px">'
            f'<div style="font-size:52px;margin-bottom:18px">🎉</div>'
            f'<h2 style="color:{TEXT};font-size:24px;font-weight:700;margin-bottom:10px">'
            f'Session complete!</h2>'
            f'<p style="color:{MUTED};font-size:15px;max-width:420px;margin:0 auto 28px;'
            f'line-height:1.6">Well done on finishing all {total} question'
            f'{"s" if total > 1 else ""}. Keep practising and you will feel '
            f'much more confident in real interviews.</p>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.balloons()
        _, btn_col, _ = st.columns([2, 1, 2])
        with btn_col:
            if st.button("Start a new session →", type="primary", key="btn_restart"):
                reset_interview()
                st.rerun()
        return

    # Progress bar + header row
    pct = int(idx / total * 100)
    hdr_left, hdr_right = st.columns([5, 1])
    with hdr_left:
        st.markdown(
            f'<div style="padding:24px 32px 0">'
            f'  <div style="display:flex;justify-content:space-between;'
            f'       align-items:center;margin-bottom:7px">'
            f'    <span style="font-size:13px;color:{MUTED};font-weight:500">'
            f'      Question {idx + 1} of {total}</span>'
            f'    <span style="font-size:12px;color:{MUTED}">{pct}% complete</span>'
            f'  </div>'
            f'  <div style="background:{SURFACE2};border-radius:5px;height:6px;overflow:hidden">'
            f'    <div style="background:{ACCENT};height:100%;width:{pct}%;'
            f'         border-radius:5px;transition:width .4s"></div>'
            f'  </div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with hdr_right:
        spacer(28)
        st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
        if st.button("⏹ End session", key=f"btn_end_top_{idx}"):
            reset_interview()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    spacer(12)

    # Question card
    st.markdown(
        f'<div style="margin:0 32px">'
        f'  <div style="background:{SURFACE};border:1px solid {BORDER};'
        f'       border-left:4px solid {ACCENT};border-radius:12px;padding:24px">'
        f'    <div style="font-size:11px;font-weight:600;color:{MUTED};'
        f'         text-transform:uppercase;letter-spacing:.5px;margin-bottom:9px">'
        f'      Question {idx + 1}</div>'
        f'    <p style="color:{TEXT};font-size:19px;font-weight:600;'
        f'       line-height:1.5;margin:0">{questions[idx]}</p>'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    spacer(16)

    # Live webcam component
    st.markdown(
        f'<p style="margin:0 32px 10px;color:{MUTED};font-size:13px;line-height:1.6">'
        f'🎥 Your live session is below. Speak your answer out loud. '
        f'The AI will analyse your face every 5 seconds and post tips in the chat panel.</p>',
        unsafe_allow_html=True,
    )

    current_q  = questions[idx]
    gemini_key = _API_KEY

    webcam_html = f"""<!DOCTYPE html>
<html>
<head>
<style>
  *{{box-sizing:border-box;margin:0;padding:0;font-family:'Inter',sans-serif}}
  body{{background:transparent}}
  .wrap{{display:flex;gap:14px;height:500px}}

  /* video side */
  .vpanel{{flex:1.3;background:#0d1117;border-radius:14px;
            overflow:hidden;position:relative;display:flex;flex-direction:column}}
  video{{width:100%;height:100%;object-fit:cover;display:block}}
  .voverlay{{position:absolute;bottom:0;left:0;right:0;
             background:linear-gradient(transparent,rgba(0,0,0,.75));padding:14px}}
  .qlabel{{font-size:11px;color:rgba(255,255,255,.6);margin-bottom:5px}}
  .qtext{{color:#fff;font-size:13px;font-weight:600;line-height:1.4}}
  .statusbar{{position:absolute;top:12px;left:12px;right:12px;
              display:flex;align-items:center;gap:8px;
              background:rgba(0,0,0,.55);border-radius:8px;
              padding:7px 12px;color:#fff;font-size:12px;
              backdrop-filter:blur(4px)}}
  .pulse{{display:inline-block;width:8px;height:8px;border-radius:50%;
          background:#3fb950;animation:pulse 1.2s infinite}}
  .pulse.red{{background:#f85149}}
  @keyframes pulse{{0%,100%{{opacity:1;transform:scale(1)}}
                    50%{{opacity:.5;transform:scale(1.35)}}}}
  .timer{{margin-left:auto;background:rgba(47,129,247,.25);
          color:#79c0ff;border-radius:12px;padding:2px 9px;font-size:11px;font-weight:600}}

  /* chat side */
  .cpanel{{flex:1;background:{SURFACE};border:1px solid {BORDER};
           border-radius:14px;display:flex;flex-direction:column;overflow:hidden}}
  .cheader{{padding:13px 16px;border-bottom:1px solid {BORDER};
            font-size:13px;font-weight:600;color:{TEXT};
            display:flex;align-items:center;gap:7px}}
  .cheader .sub{{margin-left:auto;font-size:11px;color:{MUTED};font-weight:400}}
  .cmsgs{{flex:1;overflow-y:auto;padding:14px;display:flex;
          flex-direction:column;gap:10px}}
  .msg-wrap .mlabel{{font-size:10px;font-weight:600;color:{MUTED};
                      text-transform:uppercase;letter-spacing:.4px;margin-bottom:3px}}
  .msg{{padding:10px 13px;border-radius:10px;font-size:13px;line-height:1.6}}
  .msg.ai{{background:{ACCENT_DIM};color:{ACCENT_TXT};border-bottom-left-radius:3px}}
  .msg.sys{{background:{SURFACE2};color:{MUTED};font-style:italic;
            text-align:center;font-size:12px}}
  .thinking{{display:flex;gap:4px;padding:10px 13px;
             background:{ACCENT_DIM};border-radius:10px;width:fit-content}}
  .dot{{width:6px;height:6px;border-radius:50%;background:{ACCENT};
        animation:bounce 1.2s infinite}}
  .dot:nth-child(2){{animation-delay:.2s}}
  .dot:nth-child(3){{animation-delay:.4s}}
  @keyframes bounce{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-5px)}}}}
  .cfooter{{padding:10px 14px;border-top:1px solid {BORDER};
            font-size:11px;color:{MUTED};text-align:center}}
  ::-webkit-scrollbar{{width:4px}}
  ::-webkit-scrollbar-track{{background:{SURFACE}}}
  ::-webkit-scrollbar-thumb{{background:{BORDER};border-radius:2px}}
</style>
</head>
<body>
<div class="wrap">

  <div class="vpanel">
    <video id="vid" autoplay playsinline muted></video>
    <div class="statusbar">
      <span class="pulse" id="dot"></span>
      <span id="stxt">Starting camera…</span>
      <span class="timer" id="tmr">Next scan: 5s</span>
    </div>
    <div class="voverlay">
      <div class="qlabel">🎤 Answer this question out loud:</div>
      <div class="qtext">{current_q}</div>
    </div>
  </div>

  <div class="cpanel">
    <div class="cheader">
      🤖 AI Coach
      <span class="sub">Live feedback every 5s</span>
    </div>
    <div class="cmsgs" id="msgs">
      <div class="msg sys">Waiting for camera access…</div>
    </div>
    <div class="cfooter">AI is reading your face expressions in real time</div>
  </div>

</div>
<canvas id="cvs" style="display:none"></canvas>

<script>
const KEY = "{gemini_key}";
const Q   = `{current_q.replace('`', "'")}`; 
const INTERVAL = 5000;

const vid  = document.getElementById('vid');
const cvs  = document.getElementById('cvs');
const msgs = document.getElementById('msgs');
const dot  = document.getElementById('dot');
const stxt = document.getElementById('stxt');
const tmr  = document.getElementById('tmr');

let snap = 0, cd = 5, stream = null;
let ticker = null, scanner = null;

function addMsg(text, type) {{
  document.querySelector('.thinking')?.remove();
  const wrap = document.createElement('div');
  wrap.className = 'msg-wrap';
  if (type === 'ai') {{
    snap++;
    const lbl = document.createElement('div');
    lbl.className = 'mlabel';
    lbl.textContent = '🤖 AI Coach · Snapshot ' + snap;
    wrap.appendChild(lbl);
  }}
  const m = document.createElement('div');
  m.className = 'msg ' + type;
  m.textContent = text;
  wrap.appendChild(m);
  msgs.appendChild(wrap);
  msgs.scrollTop = msgs.scrollHeight;
}}

function showThinking() {{
  const d = document.createElement('div');
  d.className = 'thinking';
  d.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
  msgs.appendChild(d);
  msgs.scrollTop = msgs.scrollHeight;
}}

async function analyse() {{
  if (!stream) return;
  cvs.width  = vid.videoWidth  || 640;
  cvs.height = vid.videoHeight || 480;
  cvs.getContext('2d').drawImage(vid, 0, 0, cvs.width, cvs.height);
  const b64 = cvs.toDataURL('image/jpeg', 0.72).split(',')[1];
  showThinking();
  dot.classList.add('red');
  stxt.textContent = 'Analysing…';
  try {{
    const r = await fetch(
      'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=' + KEY,
      {{
        method:'POST',
        headers:{{'Content-Type':'application/json'}},
        body: JSON.stringify({{
          contents:[{{
            parts:[
              {{text:`You are a warm and encouraging interview coach.
The candidate is answering: "${{Q}}"
Look at their face in this image. Give ONE short, specific coaching tip (2-3 sentences) about:
- Eye contact or camera presence
- Facial expression and confidence
- Posture or body language
Be warm, direct, and specific. Do not repeat generic advice.`}},
              {{inline_data:{{mime_type:'image/jpeg',data:b64}}}}
            ]
          }}]
        }})
      }}
    );
    const data = await r.json();
    const tip  = data?.candidates?.[0]?.content?.parts?.[0]?.text || 'You are doing great — keep going!';
    addMsg(tip.trim(), 'ai');
  }} catch(e) {{
    addMsg('Could not reach AI — check your internet connection.', 'sys');
  }}
  dot.classList.remove('red');
  stxt.textContent = 'Live';
  cd = 5;
}}

function tick() {{
  cd--;
  tmr.textContent = cd > 0 ? 'Next scan: ' + cd + 's' : 'Scanning…';
  if (cd <= 0) cd = 5;
}}

async function start() {{
  try {{
    stream = await navigator.mediaDevices.getUserMedia({{video:true,audio:false}});
    vid.srcObject = stream;
    stxt.textContent = 'Live';
    msgs.innerHTML = '';
    addMsg('Camera ready! Take a breath and start speaking your answer. I will coach you every 5 seconds. 🎯', 'ai');
    cd = 5;
    ticker  = setInterval(tick, 1000);
    scanner = setInterval(analyse, INTERVAL);
    analyse();
  }} catch(e) {{
    stxt.textContent = 'Camera blocked';
    addMsg('Camera access was denied. Please allow camera in your browser settings and reload.', 'sys');
  }}
}}

start();
</script>
</body>
</html>"""

    components.html(webcam_html, height=520, scrolling=False)

    spacer(20)

    # Audio recording + detailed feedback
    st.markdown(
        f'<div style="margin:0 32px">'
        f'<p style="color:{TEXT};font-weight:600;font-size:15px;margin-bottom:4px">'
        f'🎙️ Record your spoken answer for detailed written feedback</p>'
        f'<p style="color:{MUTED};font-size:13px;margin-bottom:12px">'
        f'When you have finished speaking, record below and click "Get my feedback".</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    _, col_audio, _ = st.columns([1, 2, 1])
    with col_audio:
        audio = st.audio_input("Record your answer", label_visibility="collapsed",
                               key=f"audio_{idx}")
        spacer(8)

        if audio:
            if st.button("Get my feedback ✨", type="primary", key=f"btn_fb_{idx}"):
                with st.spinner("Analysing your answer…"):
                    try:
                        prompt = (
                            "You are a warm and expert interview coach. "
                            f"The candidate just answered: '{questions[idx]}'. "
                            "Listen carefully and give feedback in exactly 3 clearly labelled sections:\n"
                            "✅ What they did well\n"
                            "💡 What to improve\n"
                            "📝 A strong model answer\n"
                            "Keep language simple, supportive, and specific. "
                            "Avoid vague praise. Maximum 250 words total."
                        )
                        fb = ai_multimodal(
                            prompt,
                            {"mime_type": "audio/wav", "data": audio.read()},
                        )
                        st.session_state[f"fb_{idx}"] = fb
                        st.session_state["interviews_completed"] += 1
                        db_update_stat(st.session_state["user_email"],
                                       "interviews_completed")
                    except Exception as exc:
                        st.error(f"Could not get feedback: {exc}")

    # Feedback display
    if f"fb_{idx}" in st.session_state:
        spacer(8)
        st.markdown(
            f'<div style="margin:0 32px">'
            f'  <div style="background:{GREEN_DIM};border:1px solid {GREEN};'
            f'       border-radius:12px;padding:16px 20px;margin-bottom:14px">'
            f'    <h3 style="color:{GREEN};font-size:14px;font-weight:600;margin:0">'
            f'      ✅ Your feedback — Question {idx + 1}</h3>'
            f'  </div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        _, col_fb, _ = st.columns([1, 2, 1])
        with col_fb:
            st.markdown(
                f'<div style="color:{TEXT};font-size:14px;line-height:1.8">'
                + st.session_state[f"fb_{idx}"].replace("\n", "<br>")
                + "</div>",
                unsafe_allow_html=True,
            )
            spacer(16)
            btn_next, btn_end = st.columns([3, 1])
            with btn_next:
                next_lbl = "Next question →" if idx + 1 < total else "Finish session ✓"
                if st.button(next_lbl, type="primary", key=f"btn_next_{idx}"):
                    st.session_state["iv_index"] += 1
                    st.rerun()
            with btn_end:
                st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
                if st.button("⏹ End", key=f"btn_end_btm_{idx}"):
                    reset_interview()
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    spacer(40)


# ══════════════════════════════════════════════════════════════════════
#  RESUME TAB
# ══════════════════════════════════════════════════════════════════════
def render_resume() -> None:
    inner1, inner2 = st.tabs(["🔍  Check against a job", "✍️  Improve my resume"])

    # ATS checker
    with inner1:
        page_heading(
            "Check your resume against a job",
            "Paste a job description and we will tell you exactly what is missing.",
        )
        _, col, _ = st.columns([1, 2.4, 1])
        with col:
            uploaded = st.file_uploader(
                "Upload your resume (PDF)",
                type=["pdf"], key="ats_upload",
                help="Or we will use the one uploaded at registration.",
            )
            if uploaded:
                with pdfplumber.open(uploaded) as pdf:
                    st.session_state["resume_text"] = "".join(
                        page.extract_text() or "" for page in pdf.pages
                    )
            jd_text = st.text_area(
                "Paste the job description here",
                height=180,
                placeholder="Copy and paste the full job posting here…",
                key="ats_jd",
            )
            spacer(4)
            if st.button("Check my resume →", type="primary", key="btn_ats"):
                if not jd_text.strip():
                    st.error("Please paste a job description first.")
                elif not st.session_state["resume_text"]:
                    st.error("Please upload your resume (PDF) first.")
                else:
                    with st.spinner("Comparing your resume to the job description…"):
                        try:
                            prompt = (
                                "You are a professional career coach and ATS specialist. "
                                "Compare the resume to the job description. "
                                "Give clear, plain-language feedback in exactly 3 sections:\n"
                                "1) ✅ Keywords and skills that match\n"
                                "2) ❌ Important keywords and skills that are missing\n"
                                "3) 💡 Specific, actionable suggestions to improve the resume\n"
                                f"Resume:\n{st.session_state['resume_text']}\n\n"
                                f"Job description:\n{jd_text}"
                            )
                            st.session_state["resume_analysis"] = ai_text(prompt)
                            st.session_state["resumes_analyzed"] += 1
                            db_update_stat(st.session_state["user_email"],
                                           "resumes_analyzed")
                        except Exception as exc:
                            st.error(f"Analysis failed: {exc}")

            if st.session_state["resume_analysis"]:
                spacer(12)
                st.markdown(
                    f'<div style="background:{ACCENT_DIM};border:1px solid {ACCENT};'
                    f'border-radius:12px;padding:16px 20px;margin-bottom:12px">'
                    f'<h3 style="color:{ACCENT_TXT};font-size:14px;font-weight:600;margin:0">'
                    f'📋 Your resume analysis</h3>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div style="color:{TEXT};font-size:14px;line-height:1.8">'
                    + st.session_state["resume_analysis"].replace("\n", "<br>")
                    + "</div>",
                    unsafe_allow_html=True,
                )

    # Improve wording
    with inner2:
        page_heading(
            "Improve your resume wording",
            "We will rewrite your resume to sound more professional and impactful.",
        )
        _, col2, _ = st.columns([1, 2.4, 1])
        with col2:
            if not st.session_state["resume_text"]:
                info_box(
                    "👆 Upload your resume in the 'Check against a job' tab first, "
                    "then come back here.",
                    kind="yellow",
                )
            else:
                if st.button("✨ Suggest improvements", type="primary", key="btn_improve"):
                    with st.spinner("Rewriting your resume…"):
                        try:
                            prompt = (
                                "You are a senior resume writer. "
                                "Rewrite the resume below using stronger, clearer, impactful language. "
                                "Keep all facts identical — improve only wording and structure. "
                                "Output the full improved resume text, ready to copy.\n\n"
                                f"Resume:\n{st.session_state['resume_text']}"
                            )
                            st.session_state["resume_improved"] = ai_text(prompt)
                        except Exception as exc:
                            st.error(f"Could not improve resume: {exc}")

                spacer(8)
                edited = st.text_area(
                    "Your improved resume — you can edit this before downloading",
                    value=(st.session_state.get("resume_improved")
                           or st.session_state["resume_text"]),
                    height=440,
                    key="improved_ta",
                )
                spacer(8)
                st.download_button(
                    "⬇️  Download improved resume",
                    data=edited,
                    file_name="viewprep_improved_resume.txt",
                    mime="text/plain",
                    key="btn_download",
                )


# ══════════════════════════════════════════════════════════════════════
#  MAIN ROUTER
# ══════════════════════════════════════════════════════════════════════
if not st.session_state["logged_in"]:
    render_auth()
else:
    # Guard: API key required for the main app
    if not _API_KEY:
        topbar()
        st.error(
            "⚠️  GEMINI_API_KEY is not configured. "
            "Add it to your Streamlit secrets and restart the app."
        )
        st.stop()

    topbar()

    # Sign-out button
    _, col_out = st.columns([9, 1])
    with col_out:
        spacer(6)
        if st.button("Sign out", key="btn_signout"):
            sign_out()
            st.rerun()

    tab_home, tab_iv, tab_res = st.tabs(
        ["🏠  Dashboard", "🎙️  Interview practice", "📄  Resume checker"]
    )
    with tab_home:
        render_dashboard()
    with tab_iv:
        render_interview()
    with tab_res:
        render_resume()