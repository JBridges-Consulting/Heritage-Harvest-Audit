import os
import streamlit as st
import pandas as pd
from openai import OpenAI
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- 1. BRANDED HEADER ---
st.set_page_config(page_title="Heritage Harvest | Field ROI", layout="wide")
st.title("Heritage Harvest | Field Intelligence 🥔")
st.markdown("### Executive Summary: Converting Competitor Voids to Harvest Volume")
st.divider()

if "report_text" not in st.session_state:
    st.session_state.report_text = None

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

# --- 2. EMAIL UTILITY ---
def send_email(recipient, buyer_name, content):
    try:
        sender = st.secrets["email"]["smtp_user"]
        pwd = st.secrets["email"]["smtp_pass"]
        
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipient
        msg['Subject'] = f"Strategic Category Opportunity for {buyer_name}"
        
        # EXACT SIGNATURE
        signature = "\n\nJenica\nHarvest Heritage\nNational Account Manager, Grocery"
        
        body = f"Hello {buyer_name},\n\nBased on today's shelf scan, we have identified significant revenue leakage. See the strategic plan below:\n\n{content}{signature}"
        
        # ENCODING FIX: Scrub ghost characters (\xa0) and force UTF-8
        clean_body = body.replace('\xa0', ' ').encode('utf-8', errors='ignore').decode('utf-8')
        msg.attach(MIMEText(clean_body, 'plain', 'utf-8'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, pwd)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Email Error: {e}")
        return False

# --- 3. DATA LOAD ---
def load_pricing():
    try:
        url = "https://raw.githubusercontent.com/JBridges-Consulting/CPG_AgenticWorkflows_Portfolio/main/03_Retail_Signal_Monitor/pricing_master_UPSPW.csv"
        df = pd.read_csv(url, skipinitialspace=True)
        df.columns = df.columns.str.lower().str.strip()
        df['list_price'] = pd.to_numeric(df['list_price'], errors='coerce')
        df['weekly_velocity'] = pd.to_numeric(df['weekly_velocity'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Cloud Data Error: {e}")
        return None

df_pricing = load_pricing()

# --- 4. THE INTERFACE ---
if df_pricing is not None:
    pricing_context = df_pricing[['product_name', 'list_price', 'weekly_velocity']].to_string(index=False)
    uploaded_file = st.file_uploader("Upload Shelf Scan", type=["jpg", "png"])

    if uploaded_file:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.image(uploaded_file, caption="Shelf Reality", use_container_width=True)
            if st.button("📈 Run Strategic Analysis"):
                base64_image = encode_image(uploaded_file)
                with st.spinner("Analyzing Shelf Efficiency..."):
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        temperature=0, 
                        messages=[{
                            "role": "user",
                            "content": [
                                {
                                    "type": "text", 
                                    "text": f"""
                                    System: Senior Category Manager. Use ONLY this data for velocity/price: {pricing_context}
                                    
                                    MISSION:
                                    1. START with a professional 3-sentence summary. Focus on category revenue leakage and "Overskewed" competitor products wasting shelf space. (DO NOT use a header).
                                    2. Identify exactly 6 empty or overskewed shelf facings.
                                    3. TABLE: [Competitor SKU, Status (OOS or Overskewed), Replacement SKU, Weekly Revenue Loss Calculation, Weekly Revenue Loss].
                                    
                                    MATH RULE: 
                                    - Weekly Revenue Loss = (list_price * 7 * weekly_velocity * number_of_facings). 
                                    - Show the FULL math in 'Weekly Revenue Loss Calculation' (e.g., $4.49 * 7 * 4 * 1).
                                    
                                    4. STRATEGIC PITCH: Write two bolded paragraphs on increasing category ROI by cutting slow-movers for Heritage Harvest. (DO NOT use a header).
                                    - BOLD the total aggregate weekly revenue loss.

                                    Format: Plain professional text and a Markdown table ONLY. NO "Visibility Scan" list.
                                    """
                                },
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}", "detail": "high"}}
                            ]
                        }]
                    )
                    st.session_state.report_text = response.choices[0].message.content

        with col2:
            if st.session_state.report_text:
                st.subheader("Strategic Growth Report")
                st.markdown(st.session_state.report_text)
                st.divider()
                st.write("### 📧 Deliver Plan to Buyer")
                b_name = st.text_input("Enter Buyer Name")
                b_email = st.text_input("Enter Buyer Email")
                if st.button("🚀 Send Strategic Plan"):
                    if b_name and b_email:
                        if send_email(b_email, b_name, st.session_state.report_text):
                            st.success(f"Strategy Plan sent to {b_name}!")
                            st.balloons()