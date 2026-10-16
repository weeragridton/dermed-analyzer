import os
import streamlit as st
import google.generativeai as genai
from PIL import Image
from fpdf import FPDF
import plotly.graph_objects as go
import json
import re
import qrcode
import tempfile

# -------------------------------------------------------------
# 1. การตั้งค่าหน้าเว็บ & CUSTOM CSS 
# -------------------------------------------------------------
st.set_page_config(page_title="DERMED CLINIC | AI Facial Analysis", page_icon="✨", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600&display=swap');
    html, body, [class*="css"]  { font-family: 'Montserrat', sans-serif; }
    .stButton>button {
        background-color: #1E1E1E; color: #FFFFFF; border-radius: 4px;
        border: 1px solid #1E1E1E; padding: 10px 24px; font-weight: 500;
        letter-spacing: 1px; transition: all 0.3s ease 0s; width: 100%;
    }
    .stButton>button:hover { background-color: #C5A880; color: white; border: 1px solid #C5A880; }
    .st-cx { background-color: #C5A880; }
    hr { margin-top: 1rem; margin-bottom: 2rem; border: 0; border-top: 1px solid rgba(0,0,0,.1); }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. ส่วน HEADER (LOGO & TITLE) ของแอปบนจอ iPad
# -------------------------------------------------------------
col_logo, col_title = st.columns([1, 5])
with col_logo:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=120)
    else:
        st.markdown("*(Logo)*")
with col_title:
    st.markdown("<h1 style='color: #1E1E1E; margin-bottom: 0px;'>DERMED CLINIC</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 18px; color: #666; letter-spacing: 1px;'>ADVANCED FACIAL ARCHITECTURE & AESTHETIC ANALYSIS</p>", unsafe_allow_html=True)

st.markdown("---")

API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-3.8-flash')

st.markdown("<h3 style='color: #1E1E1E;'>1. Patient Profile Formulation</h3>", unsafe_allow_html=True)
col_eth, col_age = st.columns(2)
with col_eth:
    ethnicity = st.selectbox("Ethnicity & Craniofacial Baseline:", ["Asian", "Caucasian", "Middle Eastern", "African", "Hispanic/Latino", "Mixed/Other"])
with col_age:
    age_group = st.selectbox("Age Range (Physiological):", ["20-29", "30-39", "40-49", "50-59", "60+"])

st.write("") 
st.markdown("<h3 style='color: #1E1E1E;'>2. Image Acquisition</h3>", unsafe_allow_html=True)
uploaded_files = st.file_uploader("Upload Medical Photos (Frontal, 45° Oblique, 90° Profile)", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

st.write("")
st.info("🔒 **Data Privacy (PDPA Compliant):** All images are processed securely in-memory and are never stored on our servers.")
pdpa_consent = st.checkbox("I verify that explicit patient consent has been obtained for AI-assisted clinical analysis.")

# -------------------------------------------------------------
# 3. ฟังก์ชันสร้าง PDF (เพิ่ม Logo, Contact, QR Code)
# -------------------------------------------------------------
def create_pdf(report_text, eth, age):
    pdf = FPDF()
    pdf.add_page()
    
    # --- PDF HEADER ---
    # ใส่ Logo ใน PDF (ถ้ามีไฟล์อัปโหลดไว้ใน GitHub)
    if os.path.exists("logo.png"):
        pdf.image("logo.png", x=10, y=8, w=25)
        
    pdf.set_y(12)
    pdf.set_font("Helvetica", style="B", size=16)
    pdf.cell(0, 10, "DERMED CLINIC", ln=True, align="C")
    pdf.set_font("Helvetica", style="B", size=12)
    pdf.cell(0, 10, "Personalized Facial Architecture Report", ln=True, align="C")
    pdf.line(10, 32, 200, 32)
    
    # --- PATIENT INFO ---
    pdf.set_y(35)
    pdf.set_font("Helvetica", style="I", size=10)
    pdf.cell(0, 10, f"Patient Profile: {age} years old | {eth} descent", ln=True)
    pdf.ln(3)
    
    # --- BODY TEXT ---
    clean_text = report_text.replace('**', '')
    replacements = {'“': '"', '”': '"', "‘": "'", "’": "'", '–': '-', '—': '-', '…': '...', '•': '-', '·': '-', '°': ' degrees'}
    for old_char, new_char in replacements.items():
        clean_text = clean_text.replace(old_char, new_char)
    clean_text = clean_text.encode('latin-1', 'ignore').decode('latin-1')
    
    pdf.set_font("Helvetica", size=9)
    pdf.multi_cell(0, 5.5, clean_text)
    pdf.ln(5)
    
    # --- FOOTER & CONTACT SECTION ---
    # วาดเส้นคั่น
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    # จำตำแหน่งแกน Y เพื่อให้ข้อความกับ QR Code อยู่บรรทัดเดียวกัน (ซ้าย-ขวา)
    current_y = pdf.get_y()
    
    # ส่วนข้อความด้านซ้าย
    pdf.set_font("Helvetica", style="B", size=10)
    pdf.cell(150, 6, "Location & Contact Details", ln=True)
    pdf.set_font("Helvetica", size=9)
    pdf.cell(150, 5, "Address: 6th Floor, MBK Center (Room B003005)", ln=True)
    pdf.cell(150, 5, "444 Phayathai Road, Wang Mai, Pathum Wan, Bangkok 10330", ln=True)
    pdf.cell(150, 5, "Opening Hours: Daily from 11:00 AM - 8:00 PM", ln=True)
    
    # สร้างรูป QR Code และวางด้านขวา
    qr = qrcode.QRCode(box_size=10, border=1)
    qr.add_data("https://linktr.ee/dermed.clinic")
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # เซฟ QR Code ชั่วคราวเพื่อแปะลง PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        qr_img.save(tmp.name)
        pdf.image(tmp.name, x=165, y=current_y, w=28)
    
    pdf.ln(10)
    pdf.set_font("Helvetica", style="I", size=8)
    pdf.cell(0, 10, "Disclaimer: This analysis is an AI-assisted tool and should be verified by a Dermed Clinic physician.", ln=True)
    
    return bytes(pdf.output())

# -------------------------------------------------------------
# 4. ฟังก์ชันวาดกราฟ Radar
# -------------------------------------------------------------
def draw_radar_chart(scores_dict):
    categories = list(scores_dict.keys())
    values = list(scores_dict.values())
    categories.append(categories[0]) 
    values.append(values[0])

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values, theta=categories, fill='toself',
        fillcolor='rgba(197, 168, 128, 0.4)', line_color='#C5A880', name='Facial Harmony Score'
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False, margin=dict(l=40, r=40, t=30, b=30), height=400
    )
    return fig

# -------------------------------------------------------------
# 5. PROMPT
# -------------------------------------------------------------
system_prompt = f"""
You are a world-class aesthetic physician at DERMED CLINIC in Thailand. 
Analyze the facial images of a {age_group} year old {ethnicity} patient.
Focus ONLY on non-surgical injectable treatments. 
CRITICAL RULE: You MUST ONLY recommend products, brands, and injectables that are legally available and approved by the THAI FDA (e.g., Juvéderm, Restylane, Belotero, Teosyal, Sculptra, Radiesse, Gouri, Botox Allergan, Dysport, Xeomin, Nabota, Aestox). Do not mention products unavailable in Thailand.

Output your response EXACTLY in this format with TWO parts:

===JSON_SCORES===
{{
    "Midface Volume": 80,
    "Jawline & Chin": 75,
    "Eye Area": 70,
    "Skin Quality": 85,
    "Overall Symmetry": 80
}}
===END_JSON===

===REPORT===
1. Current Anatomical Score (0-100).
2. Core Problem Identification (Root cause like bone/fat pad).
3. Prioritized Action Plan (The DERMED Protocol): Priority 1, 2, 3 (Mention specific Thai FDA approved brands).
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
        with st.spinner('Initiating deep anatomical scan and rendering charts...'):
            images = [Image.open(f) for f in uploaded_files]
            request_content = [system_prompt] + images
            response = model.generate_content(request_content)
            
            raw_text = response.text
            
            try:
                json_str = re.search(r'===JSON_SCORES===(.*?)===END_JSON===', raw_text, re.DOTALL).group(1)
                scores_data = json.loads(json_str)
                report_text = raw_text.split('===REPORT===')[1].strip()
            except:
                scores_data = None
                report_text = raw_text 
            
            st.success("✅ Analysis Complete")
            st.markdown("---")
            
            if scores_data:
                col_chart, col_text = st.columns([1, 1.5])
                with col_chart:
                    st.markdown("<h4 style='text-align: center; color: #1E1E1E;'>Facial Harmony Radar</h4>", unsafe_allow_html=True)
                    fig = draw_radar_chart(scores_data)
                    st.plotly_chart(fig, use_container_width=True)
                with col_text:
                    st.markdown(report_text)
            else:
                st.markdown(report_text)
            
            pdf_bytes = create_pdf(report_text, ethnicity, age_group)
            st.markdown("---")
            st.download_button(
                label="📥 EXPORT CLINICAL REPORT (PDF)",
                data=pdf_bytes,
                file_name="Dermed_Assessment.pdf",
                mime="application/pdf",
            )
