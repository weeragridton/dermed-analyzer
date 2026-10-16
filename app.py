import streamlit as st
import google.generativeai as genai
from PIL import Image
from fpdf import FPDF
import io

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="DERMED CLINIC | AI Facial Analysis", layout="wide")
st.title("✨ DERMED CLINIC: Advanced Facial Architecture Analysis")

# 2. ใส่ API Key
API_KEY = "ใส่_API_KEY_ของคุณที่นี่"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-3.8-flash')

# 3. รับข้อมูล
col1, col2 = st.columns(2)
with col1:
    ethnicity = st.selectbox("Patient Ethnicity:", ["Asian", "Caucasian", "Middle Eastern", "African", "Hispanic/Latino", "Mixed/Other"])
with col2:
    age_group = st.selectbox("Age Range:", ["20-29", "30-39", "40-49", "50-59", "60+"])

uploaded_files = st.file_uploader("📸 Upload Patient Photos (Front, 45°, 90°)", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

# 4. PDPA Consent Checkbox (สำคัญมาก)
st.markdown("---")
pdpa_consent = st.checkbox("☑️ I confirm that the patient has provided explicit consent to process their images for clinical AI analysis. (PDPA Compliant: Images are not stored on our servers).")

# 5. ฟังก์ชันสร้าง PDF
def create_pdf(report_text, eth, age):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Helvetica", style="B", size=16)
    pdf.cell(0, 10, "DERMED CLINIC", ln=True, align="C")
    pdf.set_font("Helvetica", style="B", size=12)
    pdf.cell(0, 10, "Advanced Facial Architecture & Aesthetic Report", ln=True, align="C")
    pdf.line(10, 30, 200, 30)
    pdf.ln(10)
    
    # Patient Info
    pdf.set_font("Helvetica", style="I", size=10)
    pdf.cell(0, 10, f"Patient Profile: {age} years old | {eth} descent", ln=True)
    pdf.ln(5)
    
    # Body Text (ทำความสะอาดตัวหนาของ Markdown ออกเพื่อให้ PDF อ่านได้)
    clean_text = report_text.replace('**', '')
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(0, 6, clean_text)
    
    # Footer
    pdf.ln(15)
    pdf.set_font("Helvetica", style="I", size=9)
    pdf.cell(0, 10, "Disclaimer: This analysis is an AI-assisted tool and should be verified by a Dermed Clinic physician.", ln=True)
    
    return bytes(pdf.output())

# 6. ประมวลผล
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

if st.button("🔍 Generate AI Clinical Assessment"):
    if not pdpa_consent:
        st.error("⚠️ Please check the PDPA consent box before proceeding.")
    elif len(uploaded_files) == 0:
        st.warning("⚠️ Please upload photos first.")
    else:
        with st.spinner('Analyzing facial architecture...'):
            images = [Image.open(f) for f in uploaded_files]
            
            # ส่งให้ AI ประมวลผล
            request_content = [system_prompt] + images
            response = model.generate_content(request_content)
            
            # แสดงผลบนหน้าจอ
            st.success("✅ Analysis Complete")
            st.markdown("---")
            st.markdown(response.text)
            
            # สร้างปุ่ม Download PDF
            pdf_bytes = create_pdf(response.text, ethnicity, age_group)
            
            st.markdown("---")
            st.download_button(
                label="📥 Download Clinical Report (PDF) for Patient",
                data=pdf_bytes,
                file_name="Dermed_Clinical_Assessment.pdf",
                mime="application/pdf",
                type="primary"
            )
