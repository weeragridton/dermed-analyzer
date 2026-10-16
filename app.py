import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. ตั้งค่าหน้าเว็บให้ดูพรีเมียม
st.set_page_config(page_title="DERMED CLINIC | AI Facial Analysis", layout="wide")

st.title("✨ DERMED CLINIC: Advanced Facial Architecture Analysis")
st.markdown("Precision injectables tailored to your unique anatomical structure.")

# 2. ใส่ API Key ของคุณตรงนี้
API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

# 3. ส่วนรับข้อมูลคนไข้
col1, col2 = st.columns(2)
with col1:
    ethnicity = st.selectbox("Patient Ethnicity:", ["Asian", "Caucasian", "Middle Eastern", "African", "Hispanic/Latino", "Mixed/Other"])
with col2:
    age_group = st.selectbox("Age Range:", ["20-29", "30-39", "40-49", "50-59", "60+"])

st.subheader("📸 Upload Patient Photos (5 Angles)")
uploaded_files = st.file_uploader("Upload Front, 45° (Left/Right), 90° (Left/Right)", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

# 4. Master Prompt สำหรับให้ AI วิเคราะห์แบบแพทย์ผู้เชี่ยวชาญ
system_prompt = f"""
You are a world-class aesthetic physician and anti-aging expert at DERMED CLINIC. 
Analyze the provided facial images of a {age_group} year old {ethnicity} patient.
Focus ONLY on non-surgical injectable treatments (Botox, Dermal Fillers, Skin Boosters, Biostimulators).

Provide a highly professional, clinical, and evidence-based analysis in English formatted as follows:

1. **Current Anatomical Score (0-100):** Give a starting score based on facial harmony, volume loss, skin quality, and structural support.
2. **Core Problem Identification:** Do not just list wrinkles. Identify the TRUE root causes of aging for this specific patient (e.g., bone resorption in the maxilla, deep fat pad deflation, ligament laxity).
3. **Prioritized Action Plan (The DERMED Protocol):** 
   - Priority 1 (Foundation): What MUST be fixed first for the biggest impact? (e.g., Structural filler at the zygomatic arch).
   - Priority 2 (Refinement): (e.g., Botox for dynamic lines).
   - Priority 3 (Skin Quality): (e.g., Skin boosters).
   Explain *WHY* each step is needed and *WHAT* product category is used.
4. **Projected Score & Expected Outcome:** What score (0-100) can they achieve after completing the prioritized plan? What visible changes will occur?
5. **Medical Evidence Note:** Briefly cite the anatomical rationale (e.g., "According to facial aging consensus, midface volume restoration lifts the lower face indirectly").

Keep the tone highly persuasive, scientific, yet accessible to a smart patient. Make them feel they are getting a bespoke, expert-level assessment.
"""

if st.button("🔍 Generate AI Clinical Assessment") and uploaded_files:
    if len(uploaded_files) > 0:
        with st.spinner('Analyzing facial architecture, skin quality, and proportions...'):
            images = [Image.open(f) for f in uploaded_files]
            
            # ส่งรูปและ prompt ให้ Gemini วิเคราะห์
            request_content = [system_prompt] + images
            response = model.generate_content(request_content)
            
            st.success("Analysis Complete")
            st.markdown("---")
            st.markdown(response.text)
    else:
        st.warning("Please upload at least one photo.")
