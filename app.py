import streamlit as st
import google.generativeai as genai
import pdfplumber
import random

# --- 1. PREMIUM CYBERPUNK THEME ENGINE & CUSTOM CSS ---
st.set_page_config(page_title="View Prep - AI Hub", layout="wide")

st.markdown("""
    <style>
    /* Dark Terminal Background Override */
    .stApp { background-color: #0b0f19; color: #e2e8f0; }
    
    /* Neon Glassmorphism Form Containers */
    .auth-container { 
        max-width: 520px; 
        margin: 40px auto; 
        background: rgba(17, 24, 39, 0.7); 
        padding: 40px; 
        border-radius: 20px; 
        box-shadow: none; 
        border: 1px solid rgba(16, 185, 129, 0.2);
        text-align: center;
    }
    
    /* Futuristic Input Text Form Adjustments */
    .stTextInput>div>div>input {
        background-color: #1f2937 !important;
        color: #00ffcc !important;
        border: 1px solid #4b5563 !important;
        border-radius: 8px !important;
    }
    
    /* Neon Matrix Styled Buttons */
    .stButton>button { 
        background: #10b981 !important; 
        color: #0b0f19 !important; 
        border-radius: 10px !important; 
        border: none !important; 
        height: 3.2em !important; 
        width: 100% !important; 
        font-weight: bold !important;
        box-shadow: none !important;
        transition: none;
    }
    .stButton>button:hover {
        transform: none;
        box-shadow: none !important;
    }
    
    /* Dashboard Content Cards */
    .card { 
        background: #111827; 
        padding: 25px; 
        border-radius: 16px; 
        box-shadow: none; 
        margin-bottom: 20px; 
        border: 1px solid #1f2937; 
    }
    .question-box { 
        background-color: #1f2937; 
        padding: 20px; 
        border-radius: 12px; 
        border-left: 6px solid #00ffcc; 
        margin-bottom: 20px; 
        font-weight: bold; 
        font-size: 1.2em;
        color: #ffffff;
    }
    h1, h2, h3 { color: #ffffff !important; font-family: 'Space Grotesk', sans-serif; }
    p { color: #9ca3af !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. HOST API KEY SECURE INITIALIZATION ---
if "GEMINI_API_KEY" in st.secrets:
    api_key_available = True
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.5-flash')
else:
    api_key_available = False

# --- 3. SESSION STATE INITIALIZATION ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Interview variables
if 'questions_list' not in st.session_state:
    st.session_state['questions_list'] = []
if 'current_q_index' not in st.session_state:
    st.session_state['current_q_index'] = 0
if 'interview_started' not in st.session_state:
    st.session_state['interview_started'] = False

def reset_interview_session():
    st.session_state['interview_started'] = False
    st.session_state['questions_list'] = []
    st.session_state['current_q_index'] = 0
    for key in list(st.session_state.keys()):
        if key.startswith('feedback_'):
            del st.session_state[key]

# --- 4. TRENDING CYBER LOGIN ENGINE ---
if not st.session_state['logged_in']:
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    
    st.title("⚡ VIEW PREP")
    st.write("Initialize secure credentials to sync your training dashboard.")
    
    # Input Framework Fields
    user_name = st.text_input("🤖 Full Name", placeholder="e.g., Alex Mercer")
    user_field = st.text_input("💻 Target Work Field", placeholder="e.g., Cybersecurity, Web Dev")
    user_email = st.text_input("📧 Email ID", placeholder="e.g., operator@viewprep.com")
    
    # Extended Feature 1: Password visibility toggle framework
    show_pass = st.checkbox("Show plain-text password")
    pass_type = "default" if show_pass else "password"
    user_password = st.text_input("🔑 Create System Password", type=pass_type, placeholder="8-16 alphanumeric characters")
    
    # Optional Profile Resume Upload Node
    uploaded_login_resume = st.file_uploader("📂 Synchronize Current Resume (Optional PDF)", type="pdf")
    
    if uploaded_login_resume and 'original_resume' not in st.session_state:
        with pdfplumber.open(uploaded_login_resume) as pdf:
            st.session_state['original_resume'] = "".join(page.extract_text() or "" for page in pdf.pages)

    # Extended Feature 2: Strict Privacy/Terms validation field
    agree_terms = st.checkbox("I agree to allow AI systems to process my telemetry data for rehearsal evaluations.")

    if st.button("INITIALIZE CORE SYSTEM", type="primary"):
        if not (user_name and user_field and user_email and user_password):
            st.error("Operation Aborted: All credential parameter inputs are strictly mandatory.")
        elif not agree_terms:
            st.warning("Action Required: You must authorize data privacy tracking clauses to unlock terminal tools.")
        else:
            password_length = len(user_password)
            if password_length < 8 or password_length > 16:
                st.error(f"Security Alert: Password length restriction mismatch (8-16 letters required). Current length: {password_length}")
            else:
                st.session_state['user_profile_name'] = user_name
                st.session_state['user_profile_field'] = user_field
                st.session_state['user_profile_email'] = user_email
                st.session_state['logged_in'] = True
                st.success("System Linked! Loading terminal frames...")
                st.rerun()
                
    st.markdown('</div>', unsafe_allow_html=True)

# --- 5. MAIN POST-AUTH CORE INTERFACE CONTROL PANEL ---
else:
    with st.sidebar:
        st.markdown("<h2 style='color:#00ffcc !important;'>⚡ View Prep</h2>", unsafe_allow_html=True)
        st.write(f"🟢 **Active:** {st.session_state.get('user_profile_name', 'Operator')}")
        
        choice = st.radio("Navigate Terminal Track:", ["🏠 Dashboard Hub", "🎙️ Interview Core", "📄 Resume Matrix"])
        
        st.divider()
        if st.button("🚪 Disconnect Session"):
            st.session_state['logged_in'] = False
            reset_interview_session()
            st.rerun()

    if not api_key_available:
        st.error("🚨 Configuration Error: Key matrix config not discovered inside backend secrets storage protocols.")
    else:
        # --- TRACK: SYSTEM HOME DASHBOARD ---
        if choice == "🏠 Dashboard Hub":
            st.title(f"Terminal Active: Welcome back, operator {st.session_state.get('user_profile_name')}!")
            st.write(f"Current deployment vector target: **{st.session_state.get('user_profile_field')}**")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="card"><h3 style="color:#00ffcc !important;">📄 Resume Analysis Matrix</h3><p>Inject job description files and analyze structural keyword gaps using real-time parsing compilers.</p></div>', unsafe_allow_html=True)
            with col2:
                st.markdown('<div class="card"><h3 style="color:#10b981 !important;">🎙️ Simulation Rehearsal Core</h3><p>Launch technical prompts using customized voice inputs and eye contact validation loops.</p></div>', unsafe_allow_html=True)

        # --- TRACK: INTERVIEW REHEARSAL CORE ---
        elif choice == "🎙️ Interview Core":
            st.title("🎙️ Simulation Rehearsal Core")
            if not st.session_state['interview_started']:
                st.markdown('<div class="card"><h3>⚙️ Configure Simulation Parameters</h3></div>', unsafe_allow_html=True)
                
                field = st.text_input("Target work arena:", value=st.session_state.get('user_profile_field', ''))
                difficulty = st.selectbox("Complexity Parameter Level:", ["Easy", "Medium", "Hard"])
                mode = st.radio("Sourcing Mode Selector:", ["Map structure dynamically from my login profile resume", "Generate specialized field-wide prompts"])
                
                if st.button("Launch Evaluation Track", type="primary"):
                    with st.spinner("Compiling customized prompt structures..."):
                        if mode == "Map structure dynamically from my login profile resume" and 'original_resume' in st.session_state:
                            prompt = f"You are a technical interviewer. Sift through this text, look for matching indicators, and compile exactly 5 individual '{difficulty}' questions tailored for field '{field}'. Resume: {st.session_state['original_resume']}. Return output ONLY as lines numbers 1 to 5."
                        else:
                            prompt = f"You are a technical interviewer. Sift through generic domains and generate exactly 5 distinct engineering questions containing a difficulty setting of '{difficulty}' for field '{field}'. Return output ONLY as lines numbers 1 to 5."
                        
                        try:
                            response = model.generate_content(prompt)
                            raw_lines = response.text.strip().split("\n")
                            cleaned_questions = [line.split(".", 1)[1].strip() if "." in line else line.strip() for line in raw_lines if line.strip()]
                            
                            st.session_state['questions_list'] = cleaned_questions[:5]
                            st.session_state['current_q_index'] = 0
                            st.session_state['interview_started'] = True
                            st.rerun()
                        except Exception as e:
                            st.error(f"Matrix generation failure: {e}")
            else:
                q_list = st.session_state['questions_list']
                current_idx = st.session_state['current_q_index']
                
                col_header, col_nav = st.columns([4, 1])
                with col_header:
                    st.write(f"### Assessment Stage {current_idx + 1} of {len(q_list)}")
                with col_nav:
                    if st.button("🛑 Abort Operational Rehearsal"):
                        reset_interview_session()
                        st.rerun()
                
                if current_idx < len(q_list):
                    st.markdown(f'<div class="question-box">{q_list[current_idx]}</div>', unsafe_allow_html=True)
                    col_a, col_b = st.columns(2)
                    with col_a:
                        audio_input = st.audio_input("Feed system audio capture track:")
                    with col_b:
                        image_input = st.camera_input("Feed camera system image track:")
                    
                    if audio_input is not None and image_input is not None:
                        if st.button("Process Target Performance Frames", type="primary"):
                            with st.spinner("Processing framework evaluation vectors..."):
                                prompt = f"Perform precise interview evaluation for prompt statement text data: {q_list[current_idx]}"
                                response = model.generate_content([prompt, {"mime_type": "audio/wav", "data": audio_input.read()}, {"mime_type": "image/jpeg", "data": image_input.read()}])
                                st.session_state[f'feedback_{current_idx}'] = response.text
                                st.success("Matrix parameters mapped successfully!")
                    
                    if f'feedback_{current_idx}' in st.session_state:
                        st.markdown(st.session_state[f'feedback_{current_idx}'])
                        st.divider()
                        if st.button("Advance Terminal Track ➡️"):
                            st.session_state['current_q_index'] += 1
                            st.rerun()
                else:
                    st.balloons()
                    st.success("Session Track Fully Terminated!")
                    if st.button("Restart New Tracking Loop"):
                        reset_interview_session()
                        st.rerun()

        # --- TRACK: RESUME STUDIO MATRIX ---
        elif choice == "📄 Resume Matrix":
            st.title("Resume Compiling Matrix")
            tab1, tab2 = st.tabs(["🔍 ATS Diagnostics", "✍️ Override Syntax Editor"])
            
            with tab1:
                st.header("Upload Matrix & Scan")
                uploaded_file = st.file_uploader("Update local binary file source (PDF)", type="pdf")
                jd = st.text_area("Paste Target Job Requirements Data Structure (JD):", height=150)
                
                if st.button("Execute Compliance Vector Scan"):
                    if (uploaded_file or 'original_resume' in st.session_state) and jd:
                        with st.spinner("Evaluating compliance tracking gaps..."):
                            if uploaded_file:
                                with pdfplumber.open(uploaded_file) as pdf:
                                    st.session_state['original_resume'] = "".join(page.extract_text() or "" for page in pdf.pages)
                            
                            prompt = f"Perform clear keyword gap tracking matching rules. Text contents: {st.session_state['original_resume']} | Criteria requirements parameters: {jd}"
                            response = model.generate_content(prompt)
                            st.session_state['resume_analysis'] = response.text
                            st.success("Scan step executed! Open the compiler panel to adjust expressions.")
                            st.markdown(response.text)

            with tab2:
                st.header("Override Syntax Editor")
                if 'original_resume' in st.session_state:
                    if st.button("Suggest AI Optimization Fixes"):
                        with st.spinner("Refining character block frameworks..."):
                            prompt = f"Optimize wording structures layout block. Text: {st.session_state['original_resume']}"
                            correction = model.generate_content(prompt)
                            st.session_state['edited_version'] = correction.text

                    edited_text = st.text_area("Source Code Content Framework", value=st.session_state.get('edited_version', st.session_state['original_resume']), height=400)
                    st.download_button("Export Compiled Text Artifact", edited_text, file_name="viewprep_optimized.txt")
                else:
                    st.info("Execute automated scanner pipeline tracking stages inside the diagnostics layer first.")