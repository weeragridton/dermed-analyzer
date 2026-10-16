import streamlit as st
import google.generativeai as genai
from PIL import Image
from fpdf import FPDF
import plotly.graph_objects as go
import json
import re
import os

# -------------------------------------------------------------
# 1. การตั้งค่าหน้าเว็บ & CUSTOM CSS
# -------------------------------------------------------------
st.set_page_config(page_title="DERMED CLINIC | AI Facial Analysis", page_icon="✨", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"]  { font-family: 'Montserrat', sans-serif; }
    .stButton>button {
        background-color: #1E1E1E; color: #FFFFFF; border-radius: 4px;
        border: 1px solid #1E1E1E; padding: 10px 24px; font-weight: 500;
        letter-spacing: 1px; transition: all 0.3s ease 0s; width: 100%;
    }
    .stButton>button:hover { background-color: #C5A880; color: white; border: 1px solid #C5A880; }
    .score-box {
        text-align: center; padding: 20px; border-radius: 10px; 
        background-color: #f8f9fa; border: 1px solid #e9ecef; margin-bottom: 20px;
    }
    .score-title { font-size: 14px; color: #666; text-transform: uppercase; letter-spacing: 2px; }
    .score-value { font-size: 48px; font-weight: 700; color: #1E1E1E; line-height: 1.2; }
    .score-projected { color: #C5A880; }
    hr { margin-top: 1rem; margin-bottom: 2rem; border: 0; border-top: 1px solid rgba(0,0,0,.1); }
    </style>
""", unsafe_allow_html=True)

col_logo, col_title = st.columns([1, 5])
with col_logo:
    try:
        st.image("logo.png", width=120)
    except:
        st.markdown("*(Logo)*")
with col_title:
    st.markdown("<h1 style='color: #1E1E1E; margin-bottom: 0px;'>DERMED CLINIC</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 18px; color: #666; letter-spacing: 1px;'>ADVANCED FACIAL ARCHITECTURE & AESTHETIC ANALYSIS</p>", unsafe_allow_html=True)
st.markdown("---")

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
# 2. ฟังก์ชันวาดกราฟ
# -------------------------------------------------------------
def draw_radar_chart(scores_dict):
    categories = ["Midface Volume", "Jawline & Chin", "Eye Area", "Skin Quality", "Overall Symmetry"]
    values = [scores_dict.get(c, 0) for c in categories]
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
# 3. ฟังก์ชันสร้าง PDF 
# -------------------------------------------------------------
def create_pdf(report_text, eth, age, scores_data, radar_fig):
    pdf = FPDF()
    pdf.add_page()
    
    try:
        pdf.image("logo.png", x=85, y=8, w=40)
        pdf.ln(35)
    except:
        pdf.set_font("Helvetica", style="B", size=16)
        pdf.cell(0, 10, "DERMED CLINIC", ln=True, align="C")
        pdf.ln(5)
        
    pdf.set_font("Helvetica", style="B", size=12)
    pdf.cell(0, 10, "Personalized Facial Architecture Report", ln=True, align="C")
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    pdf.set_font("Helvetica", style="I", size=10)
    pdf.cell(0, 10, f"Patient Profile: {age} years old | {eth} descent", ln=True)
    pdf.ln(5)
    
    if scores_data:
        pdf.set_font("Helvetica", style="B", size=16)
        pdf.cell(95, 15, f"CURRENT SCORE: {scores_data.get('CurrentScore', '')}", border=1, align="C")
        pdf.set_text_color(197, 168, 128)
        pdf.cell(95, 15, f"PROJECTED SCORE: {scores_data.get('ProjectedScore', '')}", border=1, align="C", ln=True)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)
        
    if radar_fig:
        try:
            radar_fig.write_image("temp_radar.png", width=500, height=350)
            pdf.image("temp_radar.png", x=50, w=110)
            os.remove("temp_radar.png")
        except:
            pass
            
    clean_text = report_text.replace('*', '') 
    replacements = {'“': '"', '”': '"', "‘": "'", "’": "'", '–': '-', '—': '-', '…': '...'}
    for old_char, new_char in replacements.items():
        clean_text = clean_text.replace(old_char, new_char)
    clean_text = clean_text.encode('latin-1', 'ignore').decode('latin-1')
    
    for line in clean_text.split('\n'):
        line = line.strip()
        if not line: continue
        
        if re.match(r'^[1-5]\.', line):
            pdf.ln(3)
            pdf.set_font("Helvetica", style="B", size=11)
            pdf.multi_cell(0, 6, line)
            pdf.set_font("Helvetica", size=10)
        else:
            pdf.multi_cell(0, 6, line)
            
    pdf.ln(10)
    
    current_y = pdf.get_y()
    try:
        pdf.image("qr.png", x=15, y=current_y, w=25)
        pdf.set_xy(45, current_y + 2)
    except:
        pdf.set_x(15)
        
    pdf.set_font("Helvetica", style="B", size=10)
    pdf.cell(0, 5, "Location & Contact Details", ln=True)
    try:
        pdf.set_x(45)
    except:
        pdf.set_x(15)
    pdf.set_font("Helvetica", size=9)
    pdf.multi_cell(0, 5, "6th Floor, MBK Center (Room B003005)\n444 Phayathai Road, Wang Mai, Pathum Wan, Bangkok 10330\nOpening Hours: Daily from 11:00 AM - 8:00 PM")
    
    return bytes(pdf.output())

# -------------------------------------------------------------
# 4. PROMPT 
# -------------------------------------------------------------
system_prompt = f"""
You are a world-class aesthetic physician at DERMED CLINIC in Thailand. 
Analyze the facial images of a {age_group} year old {ethnicity} patient.
Focus ONLY on non-surgical injectable treatments. 
CRITICAL RULE: You MUST ONLY recommend products legally approved by the THAI FDA (e.g., Juvéderm, Restylane, Belotero, Teosyal, Sculptra, Radiesse, Gouri, Botox Allergan, Dysport, Xeomin, Nabota, Aestox).

Output EXACTLY in this format:

===JSON_SCORES===
{{
    "Midface Volume": 80,
    "Jawline & Chin": 75,
    "Eye Area": 70,
    "Skin Quality": 85,
    "Overall Symmetry": 80,
    "CurrentScore": "78/100",
    "ProjectedScore": "88-90/100"
}}
===END_JSON===

===REPORT===
1. Core Problem Identification: (Root causes).
2. Prioritized Action Plan (The DERMED Protocol): Priority 1, 2, 3.
3. Medical Evidence Note: (Brief rationale).
"""

st.write("")
if st.button("EXECUTE CLINICAL ANALYSIS"):
    if not pdpa_consent:
        st.error("⚠️ Action Required: Please confirm patient consent (PDPA box).")
    elif len(uploaded_files) == 0:
        st.warning("⚠️ Action Required: Please upload diagnostic images.")
    else:
        with st.spinner('Initiating deep anatomical scan and rendering charts...'):
            
            # --- ระบบย่อรูปอัตโนมัติ (ป้องกันไฟล์ใหญ่เกินลิมิต) ---
            def resize_image(img_file, max_size=1024):
                img = Image.open(img_file)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img.thumbnail((max_size, max_size))
                return img
                
            images = [resize_image(f) for f in uploaded_files]
            request_content = [system_prompt] + images
            
            # ดึง API Key แบบอันเดียว
            try:
                API_KEY = st.secrets["GEMINI_API_KEY"]
                genai.configure(api_key=API_KEY)
                model = genai.GenerativeModel('gemini-3.8-flash')
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
                
                fig = None
                if scores_data:
                    col_score1, col_score2 = st.columns(2)
                    with col_score1:
                        st.markdown(f"<div class='score-box'><div class='score-title'>Current Anatomical Score</div><div class='score-value'>{scores_data.get('CurrentScore', '')}</div></div>", unsafe_allow_html=True)
                    with col_score2:
                        st.markdown(f"<div class='score-box'><div class='score-title'>Projected Post-Treatment Score</div><div class='score-value score-projected'>{scores_data.get('ProjectedScore', '')}</div></div>", unsafe_allow_html=True)
                    
                    col_chart, col_text = st.columns([1, 1.5])
                    with col_chart:
                        st.markdown("<h4 style='text-align: center; color: #1E1E1E;'>Facial Harmony Radar</h4>", unsafe_allow_html=True)
                        fig = draw_radar_chart(scores_data)
                        st.plotly_chart(fig, use_container_width=True)
                    with col_text:
                        clean_web_text = report_text.replace('*', '')
                        st.markdown(clean_web_text)
                else:
                    st.markdown(report_text)
                
                pdf_bytes = create_pdf(report_text, ethnicity, age_group, scores_data, fig)
                st.markdown("---")
                st.download_button(
                    label="📥 EXPORT CLINICAL REPORT (PDF)",
                    data=pdf_bytes,
                    file_name="Dermed_Assessment.pdf",
                    mime="application/pdf",
                )
                
            except Exception as e:
                st.error(f"❌ System Error: API connection failed. \n\nDetail: {str(e)}")
