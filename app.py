import streamlit as st
import google.generativeai as genai
from PIL import Image
from fpdf import FPDF
import io

# -------------------------------------------------------------
# 1. การตั้งค่าหน้าเว็บ & CUSTOM CSS (LUXURY THEME)
# -------------------------------------------------------------
st.set_page_config(page_title="DERMED CLINIC | AI Facial Analysis", page_icon="✨", layout="wide")

st.markdown("""
    <style>
    /* นำเข้าฟอนต์สากลที่ดูพรีเมียม */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Montserrat', sans-serif;
    }
    
    /* ปรับแต่งปุ่มกดให้ดูหรูหรา (โทนดำ-ทอง) */
    .stButton>button {
        background-color: #1E1E1E; 
        color: #FFFFFF;
        border-radius: 4px;
        border: 1px solid #1E1E1E;
        padding: 10px 24px;
        font-weight: 500;
        letter-spacing: 1px;
        transition: all 0.3s ease 0s;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #C5A880; /* สีทอง/แชมเปญ */
        color: white;
        border: 1px solid #C5A880;
    }
    
    /* สีของ Checkbox PDPA */
    .st-cx { background-color: #C5A880; }
    
    /* เส้นคั่น */
    hr {
        margin-top: 1rem;
        margin-bottom: 2rem;
        border: 0;
        border-top: 1px solid rgba(0,0,0,.1);
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. ส่วน HEADER (LOGO & TITLE)
# -------------------------------------------------------------
col_logo, col_title = st.columns([1, 5])
with col_logo:
    try:
        # ระบบจะดึงรูป logo.png ที่คุณอัปโหลดไว้มาแสดง
        st.image("logo.png", width=120)
    except:
        st.markdown("*(Logo)*") # เผื่อกรณีหารูปไม่เจอ

with col_title:
    st.markdown("<h1 style='color: #1E1E1E; margin-bottom: 0px;'>DERMED CLINIC</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 18px; color: #666; letter-spacing: 1px;'>ADVANCED FACIAL ARCHITECTURE & AESTHETIC ANALYSIS</p>", unsafe_allow_html=True)

st.markdown("---")

# -------------------------------------------------------------
# 3. ใส่ API Key อย่างปลอดภัย
# -------------------------------------------------------------
API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-3.8-flash')

# -------------------------------------------------------------
# 4. ส่วนรับข้อมูลผู้ป่วย (PATIENT PROFILE)
# -------------------------------------------------------------
st.markdown("<h3 style='color: #1E1E1E;'>1. Patient Profile Formulation</h3>", unsafe_allow_html=True)
col_eth, col_age = st.columns(2)
with col_eth:
    ethnicity = st.selectbox("Ethnicity & Craniofacial Baseline:", ["Asian", "Caucasian", "Middle Eastern", "African", "Hispanic/Latino", "Mixed/Other"])
with col_age:
    age_group = st.selectbox("Age Range (Physiological):", ["20-29", "30-39", "40-49", "50-59", "60+"])

st.write("") # เว้นบรรทัด
st.markdown("<h3 style='color: #1E1E1E;'>2. Image Acquisition</h3>", unsafe_allow_html=True)
uploaded_files = st.file_uploader("Upload Medical Photos (Frontal, 45° Oblique, 90° Profile)", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

# -------------------------------------------------------------
# 5. PDPA & CONSENT
# -------------------------------------------------------------
st.write("")
st.info("🔒 **Data Privacy (PDPA Compliant):** All images are processed securely in-memory and are never stored on our servers.")
pdpa_consent = st.checkbox("I verify that explicit patient consent has been obtained for AI-assisted clinical analysis.")

# -------------------------------------------------------------
# 6. ฟังก์ชันสร้าง PDF (คงเดิม แต่ปรับ Font)
# -------------------------------------------------------------
def create_pdf(report_text, eth, age):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", style="B", size=16)
    pdf.cell(0, 10, "DERMED CLINIC", ln=True, align="C")
    pdf.set_font("Helvetica", style="B", size=12)
    pdf.cell(0, 10, "Personalized Facial Architecture Report", ln=True, align="C")
    pdf.line(10, 30, 200, 30)
    pdf.ln(10)
    pdf.set_font("Helvetica", style="I", size=10)
    pdf.cell(0, 10, f"Patient Profile: {age} years old | {eth} descent", ln=True)
    pdf.ln(5)
    clean_text = report_text.replace('**', '')
    pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(0, 6, clean_text)
    pdf.ln(15)
    pdf.set_font("Helvetica", style="I", size=8)
    pdf.cell(0, 10, "Disclaimer: This analysis is an AI-assisted tool and should be verified by a Dermed Clinic physician.", ln=True)
    return bytes(pdf.output())

# -------------------------------------------------------------
# 7. PROMPT & GENERATION
# -------------------------------------------------------------
system_prompt = f"""
You are a world-class aesthetic physician at DERMED CLINIC. 
Analyze the provided facial images of a {age_group} year old {ethnicity} patient.
Focus ONLY on non-surgical injectable treatments. Provide analysis in English.
1. Current Anatomical Score (0-100).
2. Core Problem Identification (Root cause like bone/fat pad).
3. Prioritized Action Plan (The DERMED Protocol): Priority 1, 2, 3.
4. Projected Score.
5. Medical Evidence Note.
"""

st.write("")
if st.button("EXECUTE CLINICAL ANALYSIS"):
    if not pdpa_consent:
        st.error("⚠️ Action Required: Please confirm patient consent (PDPA box).")
    elif len(uploaded_files) == 0:
        st.warning("⚠️ Action Required: Please upload diagnostic images.")
    else:
        with st.spinner('Initiating deep anatomical scan...'):
            images = [Image.open(f) for f in uploaded_files]
            request_content = [system_prompt] + images
            response = model.generate_content(request_content)
            
            st.success("✅ Analysis Complete")
            st.markdown("---")
            st.markdown(response.text)
            
            pdf_bytes = create_pdf(response.text, ethnicity, age_group)
            
            st.markdown("---")
            st.download_button(
                label="📥 EXPORT CLINICAL REPORT (PDF)",
                data=pdf_bytes,
                file_name="Dermed_Assessment.pdf",
                mime="application/pdf",
            )
