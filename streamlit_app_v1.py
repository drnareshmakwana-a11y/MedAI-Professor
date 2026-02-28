import streamlit as st
import base64
from io import BytesIO
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
from backend.llm_engine import get_llm_response, get_llm_json_response
from backend.rag_engine import get_retriever, build_vector_store

# --- 1. CONFIGURATION & AGGRESSIVE CSS FIX ---
st.set_page_config(page_title="MedAI Professor Pro", page_icon="🩺", layout="wide")

st.markdown("""
    <style>
    /* 1. Eliminate top padding from Streamlit's default layout */
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        max-width: 1000px;
    }
    
    /* 2. Global Background */
    .stApp {
        background: linear-gradient(rgba(15, 23, 42, 0.95), rgba(15, 23, 42, 0.95)), 
                    url('https://www.toptal.com/designers/subtlepatterns/patterns/medical_pattern.png');
        background-attachment: fixed;
    }
    
    /* 3. Hero Header - No top margin, flush with top */
    .hero-header {
        background: linear-gradient(90deg, #0ea5e9, #2563eb);
        padding: 25px;
        border-radius: 0px 0px 25px 25px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        z-index: 1000;
    }
    .hero-header h1 { color: white !important; margin: 0; font-size: 2.5rem; }
    .hero-header p { color: #e0f2fe; margin: 0; font-size: 1rem; opacity: 0.8; }

    /* 4. THE GAP FIX: Negative margin pulls this card up to meet the header */
    .content-container {
        background: rgba(30, 41, 59, 0.8);
        backdrop-filter: blur(12px);
        padding: 30px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-top: -20px; /* This removes the circled gap */
        position: relative;
    }

    .prof-name { color: #38bdf8; font-size: 1.3rem; font-weight: 700; }
    .stAudio { display: none; }
    
    /* Remove unnecessary spacing around columns */
    [data-testid="stHorizontalBlock"] {
        gap: 0rem;
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

# --- 3. STATE MACHINE ---
if "step" not in st.session_state:
    st.session_state.step = "ASKING"
if "current_q" not in st.session_state:
    st.session_state.current_q = "Let's begin. Describe the classical triad of symptoms in a patient with a Brain Abscess."
if "last_feedback" not in st.session_state:
    st.session_state.last_feedback = None

# --- 4. SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/144/stethoscope.png")
    st.markdown("### 🏥 Faculty Admin")
    if st.button("🔄 Sync Medical Knowledge"):
        st.success(build_vector_store())
    st.divider()
    if st.button("🏁 End & Reset"):
        st.session_state.clear()
        st.rerun()

# --- 5. MAIN UI ---
# HERO HEADER
st.markdown("""
    <div class="hero-header">
        <h1>🩺 MedAI Professor</h1>
        <p>Expert Clinical Viva Examiner & Case Simulator</p>
    </div>
    """, unsafe_allow_html=True)

retriever = get_retriever()

# CONTENT CONTAINER
# Note: We use the div inside a single container to prevent Streamlit from adding margin
st.markdown('<div class="content-container">', unsafe_allow_html=True)

# Split Layout for Professor Image and Question
col_img, col_main = st.columns([0.8, 3])

with col_img:
    # Switched to a reliable static medical image link to avoid "Content Not Available"
    st.image("https://cdn-icons-png.flaticon.com/512/3304/3304567.png", width=120)

with col_main:
    st.markdown('<div class="prof-name">👨‍🏫 Senior Professor</div>', unsafe_allow_html=True)
    st.markdown(f"#### {st.session_state.current_q}")

st.markdown("<hr style='border: 0.5px solid rgba(255,255,255,0.1); margin: 20px 0;'>", unsafe_allow_html=True)

# Interaction Logic
if st.session_state.step == "ASKING":
    st.write("#### 🎙️ Provide your clinical reasoning:")
    ca, cb = st.columns([1, 5])
    with ca:
        v_inp = speech_to_text(language='en', start_prompt="⏺️ Record", stop_prompt="⏹️ Stop", key='viva_mic')
    with cb:
        t_inp = st.chat_input("Type your response...")
    
    user_input = v_inp if v_inp else t_inp

    if user_input:
        with st.spinner("Analyzing response..."):
            docs = retriever.invoke(user_input)
            context = "\n".join([d.page_content for d in docs])
            query = f"Question: {st.session_state.current_q}\nAnswer: {user_input}\nContext: {context}"
            st.session_state.last_feedback = get_llm_json_response(query)
            speak_text(st.session_state.last_feedback.get('feedback'))
            st.session_state.step = "GRADING"
            st.rerun()

elif st.session_state.step == "GRADING":
    f = st.session_state.last_feedback
    st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.1); padding: 20px; border-radius: 15px; border-left: 6px solid #10b981;">
            <h3 style="color: #10b981; margin-top:0;">📈 Evaluation: {f.get('score', 0)}/10</h3>
            <p style="font-size: 1.1rem;"><b>Justification:</b> {f.get('feedback', '')}</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("Proceed to Next Case ➡️", use_container_width=True):
        with st.spinner("Next question..."):
            new_q = get_llm_response(f"Ask a new final year MBBS viva question. Previous: {st.session_state.current_q}")
            st.session_state.current_q = new_q
            st.session_state.last_feedback = None
            st.session_state.step = "ASKING"
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# --- 6. LEGAL DISCLAIMER (INDIAN LAW COMPLIANCE) ---
st.markdown("""
    <style>
    .legal-footer {
        font-size: 6px;
        color: rgba(255, 255, 255, 0.2);
        text-align: justify;
        line-height: 1.1;
        margin-top: 50px;
        padding: 10px;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
    }
    </style>
    <div class="legal-footer">
        DISCLAIMER: This AI-powered platform is strictly for educational and simulation purposes for MBBS students in India and does not constitute medical advice, diagnosis, or treatment. 
        In accordance with the Information Technology Act, 2000 and the National Medical Commission (NMC) guidelines, users are advised that the responses generated are 
        produced by an Artificial Intelligence model and may contain errors or hallucinations. This tool should not be used in clinical decision-making. 
        The developers disclaim all liability for actions taken based on this content. All drug dosages and clinical protocols must be verified against 
        Standard Treatment Guidelines (STG) issued by the Ministry of Health and Family Welfare, Government of India. 
        By using this app, you acknowledge that no doctor-patient relationship is established.
    </div>
    """, unsafe_allow_html=True)