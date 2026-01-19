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
        
        signature = "\n\nJenica\nHarvest Heritage\nNational Account Manager, Grocery"
        
        # Clean technical headers from content
        clean_content = content.replace("**Quantifiable Buyer Pitch:**", "").replace("Quantifiable Buyer Pitch", "")
        
        body = f"Hello {buyer_name},\n\nBased on today's shelf scan, we have identified significant revenue leakage in your category. See the full strategic recovery plan below:\n\n{clean_content}{signature}"
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, pwd)
        server.sendmail(sender, recipient, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Email Error: {e}")
        return False

# --- 3. DATA LOAD (MANDATORY SOURCE OF TRUTH) ---
# --- 3. DATA LOAD (MANDATORY SOURCE OF TRUTH) ---
def load_pricing():
    try:
        # RAW GitHub URL for cloud reliability
        url = "https://raw.githubusercontent.com/JBridges-Consulting/CPG_AgenticWorkflows_Portfolio/main/03_Retail_Signal_Monitor/pricing_master_UPSPW.csv"
        
        df = pd.read_csv(url, skipinitialspace=True)
        df.columns = df.columns.str.lower().str.strip()
        
        # Numeric safety
        df['list_price'] = pd.to_numeric(df['list_price'], errors='coerce')
        df['weekly_velocity'] = pd.to_numeric(df['weekly_velocity'], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"Cloud Data Error: {e}")
        return None

# --- CALL THE FUNCTION HERE (Outside the def block) ---
df_pricing = load_pricing()

# --- 4. THE INTERFACE ---
if df_pricing is not None:
    # This will now work because df_pricing is defined above
    pricing_context = df_pricing[['product_name', 'list_price', 'weekly_velocity']].to_string(index=False)
    
    uploaded_file = st.file_uploader("Upload Shelf Scan", type=["jpg", "png"])

    if uploaded_file:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.image(uploaded_file, caption="Shelf Reality", use_container_width=True)
            
            if st.button("📈 Run Strategic Analysis"):
                base64_image = encode_image(uploaded_file)
                
                with st.spinner("Calculating Revenue Loss from Master Data..."):
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        temperature=0, # Forces absolute math accuracy
                        messages=[{
                            "role": "user",
                            "content": [
                                {
                                    "type": "text", 
                                    "text": f"""
                                    System: Zero-Refusal Mode. You are a Senior Category Manager.
                                    Constraint: You MUST use the provided CSV data. NEVER hallucinate prices like $1.99.
                                    
                                    REFERENCE PRICING DATA:
                                    {pricing_context}
                                    
                                    MISSION:
                                    1. STRATEGIC SUMMARY: Start with a professional paragraph on category decay.
                                    2. VISIBILITY SCAN: Identify exactly 6 empty shelf facings in the image.
                                    3. TABLE: Include 'Competitor OOS', 'Replacement SKU', 'OOS Quantity', 'Weekly Revenue Loss Calculation', 'Weekly Revenue Loss'.
                                    4. MATH: You MUST pull 'list_price' and 'weekly_velocity' from the REFERENCE PRICING DATA for each row.
                                       - Calculation: (list_price * 7 * weekly_velocity * 1).
                                    
                                    5. BUYER PITCH: Write professional bolded paragraphs immediately following the table.
                                       - NO 'Quantifiable Buyer Pitch' header.
                                       - BOLD the 6 facings and the Total Weekly Revenue Loss calculated from your table.

                                    Format: Start with 'Analysis of Available Shelf Space'.
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
                b_name = st.text_input("Enter Buyer Name", placeholder="e.g., Sarah Jenkins")
                b_email = st.text_input("Enter Buyer Email", placeholder="buyer@retailer.com")
                
                if st.button("🚀 Send Strategic Plan"):
                    if b_name and b_email:
                        if send_email(b_email, b_name, st.session_state.report_text):
                            st.success(f"Strategy Plan sent to {b_name}!")
                            st.balloons()
                    else:
                        st.warning("Please enter a name and email.")
