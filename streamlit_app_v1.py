import streamlit as st
import base64
import os
from io import BytesIO
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
from backend.llm_engine import get_llm_response, get_llm_json_response
from backend.rag_engine import get_retriever, build_vector_store

# --- 1. CONFIGURATION & UI STYLING ---
st.set_page_config(page_title="MedAI Professor Pro", page_icon="🩺", layout="wide")

st.markdown("""
    <style>
    /* Clean Top Header Gap */
    .block-container { padding-top: 0rem !important; padding-bottom: 0rem !important; max-width: 1000px; }
    
    /* Global Medical Theme */
    .stApp {
        background: linear-gradient(rgba(15, 23, 42, 0.95), rgba(15, 23, 42, 0.95)), 
                    url('https://www.toptal.com/designers/subtlepatterns/patterns/medical_pattern.png');
        background-attachment: fixed; color: #e2e8f0;
    }
    
    /* Hero Header */
    .hero-header {
        background: linear-gradient(90deg, #0ea5e9, #2563eb);
        padding: 25px; border-radius: 0px 0px 25px 25px; text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    }
    .hero-header h1 { color: #ffffff !important; margin: 0; font-size: 2.5rem; font-weight: 800; }
    
    /* Main Content Card */
    .content-container {
        background: rgba(30, 41, 59, 0.8); backdrop-filter: blur(12px);
        padding: 35px; border-radius: 24px; border: 1px solid rgba(255, 255, 255, 0.1);
        margin-top: -20px; margin-bottom: 20px;
    }
    
    .prof-name { color: #38bdf8 !important; font-size: 1.4rem; font-weight: 700; }
    h4 { color: #f8fafc !important; }
    
    /* Success/Exit Card */
    .success-card {
        background: linear-gradient(135deg, #064e3b, #065f46);
        padding: 40px; border-radius: 20px; text-align: center; border: 2px solid #10b981;
    }

    .stAudio { display: none; }
    .stButton>button { border-radius: 10px; font-weight: 600; }
    
    /* Disclaimer Font */
    .legal-footer {
        font-size: 7px; color: rgba(255, 255, 255, 0.15) !important;
        text-align: justify; line-height: 1.2; margin-top: 30px;
        padding: 10px; border-top: 1px solid rgba(255, 255, 255, 0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUDIO ENGINE ---
def speak_text(text):
    if text:
        clean_text = text.replace("**", "").replace("#", "")
        tts = gTTS(text=clean_text[:400], lang='en', tld='co.uk')
        fp = BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp.getvalue(), format="audio/mp3", autoplay=True)

# --- 3. DYNAMIC STATE & AUTO-SYNC ---
if "step" not in st.session_state:
    st.session_state.step = "ASKING"
if "scores" not in st.session_state:
    st.session_state.scores = [] 
if "forced_exit" not in st.session_state:
    st.session_state.forced_exit = False

# Auto-Sync Vector Store on App Load/Rebuild
if "rag_initialized" not in st.session_state:
    with st.status("🚀 Initializing Medical Brain...", expanded=False) as status:
        if not os.path.exists("vector_store") or len(os.listdir("vector_store")) == 0:
            build_vector_store()
        st.session_state.rag_initialized = True
        status.update(label="✅ System Ready", state="complete", expanded=False)

# --- 4. SIDEBAR SETTINGS ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/144/stethoscope.png")
    st.markdown("### ⚙️ Viva Settings")
    
    # Subject Selection
    subject = st.selectbox(
        "Department/Specialty",
        ["General Medicine", "General Surgery", "Obstetrics & Gynecology", "Pediatrics", "Orthopedics", "Mixed Bag"],
        index=5
    )
    
    # Case Count
    max_cases = st.slider("Target Number of Cases", 3, 20, 5)
    
    st.divider()
    st.markdown(f"### 📊 Progress: {len(st.session_state.scores)}/{max_cases}")
    if st.session_state.scores:
        avg = sum(st.session_state.scores) / len(st.session_state.scores)
        st.metric("Running Average", f"{avg:.1f}/10")
    
    st.divider()
    # Exit Button
    if st.button("🚪 Exit & View Results", use_container_width=True):
        if st.session_state.scores:
            st.session_state.forced_exit = True
            st.rerun()
        else:
            st.warning("Complete at least one case first.")
            
    if st.button("🏁 Start New Exam", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# GENERATE INITIAL QUESTION BASED ON SUBJECT
if "current_q" not in st.session_state:
    with st.spinner(f"👨‍🏫 {subject} Professor is preparing a case..."):
        prompt = f"Ask one challenging final year MBBS viva question for {subject}."
        st.session_state.current_q = get_llm_response(prompt)

# --- 5. MAIN UI ---
st.markdown('<div class="hero-header"><h1>🩺 MedAI Professor</h1><p>Clinical Case Simulator</p></div>', unsafe_allow_html=True)

# A. SUCCESS / EXIT SCREEN
if len(st.session_state.scores) >= max_cases or st.session_state.forced_exit:
    st.markdown('<div class="content-container">', unsafe_allow_html=True)
    avg_final = sum(st.session_state.scores) / len(st.session_state.scores)
    title = "🚪 Viva Terminated" if st.session_state.forced_exit else "🎉 Assessment Complete"
    
    st.markdown(f"""
        <div class="success-card">
            <h1 style="color: #10b981;">{title}</h1>
            <p style="font-size: 1.4rem;">Specialty: <b>{subject}</b></p>
            <p style="font-size: 1.4rem;">Overall Competency Score: <b>{avg_final:.1f}/10</b></p>
            <p>Total Cases Evaluated: {len(st.session_state.scores)}</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("Restart New Session 🔄", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# B. VIVA INTERACTION
else:
    retriever = get_retriever()
    st.markdown('<div class="content-container">', unsafe_allow_html=True)
    
    col_img, col_main = st.columns([0.8, 3])
    with col_img:
        st.image("https://cdn-icons-png.flaticon.com/512/3304/3304567.png", width=120)
    with col_main:
        st.markdown(f'<div class="prof-name">👨‍🏫 {subject} Professor</div>', unsafe_allow_html=True)
        st.markdown(f"#### {st.session_state.current_q}")

    st.divider()

    if st.session_state.step == "ASKING":
        st.write("#### 🎙️ Provide your clinical reasoning:")
        ca, cb = st.columns([1, 5])
        with ca:
            v_inp = speech_to_text(language='en', start_prompt="⏺️ Record", stop_prompt="⏹️ Stop", key='viva_mic')
        with cb:
            t_inp = st.chat_input("Type your response here...")
        
        user_input = v_inp if v_inp else t_inp

        if user_input:
            with st.spinner("Evaluating response..."):
                docs = retriever.invoke(user_input)
                context = "\n".join([d.page_content for d in docs])
                query = f"Subject: {subject}\nQuestion: {st.session_state.current_q}\nAnswer: {user_input}\nContext: {context}"
                st.session_state.last_feedback = get_llm_json_response(query)
                st.session_state.scores.append(st.session_state.last_feedback.get('score', 0))
                
                speak_text(st.session_state.last_feedback.get('feedback'))
                st.session_state.step = "GRADING"
                st.rerun()

    elif st.session_state.step == "GRADING":
        f = st.session_state.last_feedback
        st.markdown(f"""
            <div style="background: rgba(16, 185, 129, 0.1); padding: 25px; border-radius: 15px; border-left: 6px solid #10b981;">
                <h3 style="color: #10b981; margin-top:0;">📈 Score: {f.get('score', 0)}/10</h3>
                <p style="color: #f1f5f9;"><b>Justification:</b> {f.get('feedback', '')}</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Proceed to Next Case ➡️", use_container_width=True):
            new_q = get_llm_response(f"Ask a new {subject} question different from {st.session_state.current_q}.")
            st.session_state.current_q = new_q
            st.session_state.last_feedback = None
            st.session_state.step = "ASKING"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# LEGAL DISCLAIMER
st.markdown("""
    <div class="legal-footer">
        DISCLAIMER: For educational purposes only. produced by AI and may contain errors. 
        Compliant with Indian IT Act 2000. Not for clinical decision-making. 
        Verify all protocols against MoHFW guidelines. No doctor-patient relationship is established.
    </div>
    """, unsafe_allow_html=True)