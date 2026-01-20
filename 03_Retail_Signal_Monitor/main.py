import os
import streamlit as st
import pandas as pd
from openai import OpenAI
import base64

# --- 0. PAGE CONFIG ---
st.set_page_config(page_title="Heritage Harvest | Revenue Recovery", layout="wide")
st.title("Heritage Harvest | Field Intelligence 🥔")

# --- 1. RETAILER SELECTION ---
retailer_choice = st.selectbox(
    "Select Target Retailer:",
    ["Retailer A", "Retailer B", "Retailer C"],
    index=0
)

st.markdown(f"### 🛡️ {retailer_choice} | Executive Revenue Recovery Blueprint")
st.divider()

if "report_text" not in st.session_state:
    st.session_state.report_text = None

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- 2. DATA LOAD ---
def load_pricing():
    try:
        df = pd.read_csv("pricing_master_UPSPW.csv")
        df.columns = df.columns.str.lower().str.strip()
        return df
    except:
        return None

df_pricing = load_pricing()

# --- 3. INTERFACE ---
if df_pricing is not None:
    pricing_context = df_pricing[['product_name', 'list_price', 'weekly_velocity']].to_string(index=False)
    
    uploaded_file = st.file_uploader(f"Upload {retailer_choice} Shelf Scan", type=["jpg", "png"])

    if uploaded_file:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.image(uploaded_file, caption=f"{retailer_choice} Store Walk - Visual Audit", use_container_width=True)
            
            if st.button(f"🚀 Run {retailer_choice} OOS Analysis", type="primary"):
                base64_image = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
                with st.spinner(f"Quantifying Revenue Leakage for {retailer_choice}..."):
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        temperature=0, 
                        messages=[{
                            "role": "user",
                            "content": [
                                {
                                    "type": "text", 
                                    "text": f"""
                                    System: Senior Category Consultant for {retailer_choice} (1,200-store chain). 
                                    DATA: {pricing_context}
                                    
                                    MISSION: Analyze OOS gaps and overskewed items to calculate chain-wide loss.
                                    
                                    1. SECTION: ### Strategic Summary
                                       Analyze the image for overskewed items (excessive facings of slow-movers) that are actively causing OOS on Heritage Harvest faster-moving SKUs.
                                    
                                    2. TABLE: Create a Standard Markdown Table. 
                                       - REQUIREMENT: Identify EXACTLY 6 competitor OOS items.
                                       - DO NOT include the word "GRID", "TABLE", or "MATH" in any header.
                                       - FONT RULE: Use plain text only. DO NOT use backticks, code blocks, or special formatting for numbers.
                                       - Col 1: Competitor OOS Item
                                       - Col 2: Heritage Harvest Replacement (Must match DATA)
                                       - Col 3: ($Price * Velocity * 1,200 Stores)
                                       - Col 4: Weekly Chain Loss ($)
                                    
                                    3. TOTAL REVENUE: Calculate the sum of all 6 items.
                                       - Format: "**TOTAL WEEKLY CHAIN OPPORTUNITY: $X,XXX,XXX**"
                                    
                                    4. SECTION: ### Strategic Profit Recovery
                                       One bold paragraph focusing on shelf-optimization and revenue recovery for {retailer_choice}'s 1,200 locations.
                                    """
                                },
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}", "detail": "high"}}
                            ]
                        }]
                    )
                    st.session_state.report_text = response.choices[0].message.content

        with col2:
            if st.session_state.report_text:
                st.subheader(f"📊 {retailer_choice}: Executive Revenue Recovery Blueprint")
                st.markdown(st.session_state.report_text)
                st.divider()
                st.info(f"💡 **Analysis Complete:** {retailer_choice} national data is ready for JBP presentation.")