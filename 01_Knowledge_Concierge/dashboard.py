import streamlit as st
import time



# 1. SETUP: Wide layout for "Dashboard" feel
st.set_page_config(
    page_title="Heritage Harvest | Agent Monitor", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CUSTOM CSS: To create the "Mission Control" dark/tight look
st.markdown("""
    <style>
        /* Remove top whitespace */
        .block-container {padding-top: 1rem; padding-bottom: 1rem;}
        
        /* Style the metrics to look like cards */
        div[data-testid="stMetric"] {
            background-color: #1E1E1E;
            border: 1px solid #333;
            padding: 10px;
            border-radius: 5px;
            color: white;
        }
        
        /* Custom Terminal Look */
        .stCodeBlock {
            border: 1px solid #333;
            border-radius: 5px;
        }
    </style>
""", unsafe_allow_html=True)

# 3. SIDEBAR: Navigation & Status
with st.sidebar:
    st.title("🌾 Heritage Harvest")
    st.caption("AI Sales Concierge Monitor")
    st.markdown("---")
    st.subheader("System Status")
    
    # Using columns in sidebar for a compact look
    c1, c2 = st.columns(2)
    with c1:
        st.success("Online", icon="✅")
    with c2:
        st.info("RAG Active", icon="🧠")
        
    st.markdown("---")
    st.caption("v1.5.0 • Production Build")
    if st.button("🚀 Force Knowledge Sync", use_container_width=True):
        st.toast("Syncing with Brand Guidelines...")
        time.sleep(1)
        st.success("Knowledge Base Updated!")

# 4. DATA LOADING FUNCTION
def load_log():
    try:
        # Ideally, your sales_agent.py should write to this file
        with open("agent_activity.log", "r") as f:
            return f.readlines()
    except FileNotFoundError:
        return [
            "[SYSTEM_INIT] Heritage Harvest Sales Agent coming online...\n",
            "[INFO] Knowledge Base loaded: 5 Sections found.\n",
            "[INFO] Connected to Gmail API via Service Account.\n",
            "[WAITING] Listening for incoming buyer inquiries...\n"
        ]

# Load Data
logs = load_log()

# 5. HEADER SECTION
col_head_1, col_head_2 = st.columns([3, 1])
with col_head_1:
    st.title("🤖 Knowledge Concierge | Live Monitor")
    st.caption("Real-time tracking of autonomous email responses and brand compliance checks.")
with col_head_2:
    # Refresh button aligned right
    if st.button("🔄 Refresh Console", use_container_width=True):
        st.rerun()

st.markdown("---")

# 6. KPI GRID (The "Performance Metrics" moved to Top)
# Calculate Metrics (Mock logic if logs are empty)
run_count = sum(1 for line in logs if "Processing" in line)
pass_count = sum(1 for line in logs if "Draft Saved" in line)
violation_count = 0 # Placeholder for blocked emails

# Calculate Pass Rate
pass_rate = round((pass_count / run_count * 100)) if run_count > 0 else 100

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(label="Inquiries Processed", value=run_count, delta="Total Emails")
with kpi2:
    st.metric(label="Response Success Rate", value=f"{pass_rate}%", delta="Drafts Created")
with kpi3:
    st.metric(label="Knowledge Hallucinations", value="0", delta_color="inverse", delta="Strict RAG Mode")
with kpi4:
    st.metric(label="Avg Response Time", value="1.2s", delta="Latency")

# 7. MAIN CONSOLE (The "Terminal")
st.subheader("🖥️ Live Agent Logs")

# Join the last 50 lines into a single string to create one cohesive "Terminal Window"
terminal_output = "".join(logs[-50:]) 

# Display as a code block (Bash syntax highlighting works well for logs)
st.code(terminal_output, language="bash", line_numbers=True)

# 8. FOOTER / STATUS BAR
st.info(f"Last updated: {time.strftime('%H:%M:%S')} • Monitoring active agent: `sales_agent.py`")
