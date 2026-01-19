import streamlit as st
import pandas as pd
import smtplib
from email.message import EmailMessage
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- PAGE CONFIG ---
st.set_page_config(page_title="Heritage Harvest | Audit Portal", page_icon="📊", layout="wide")
st.title("Heritage Harvest 📊")
st.markdown("### Automated Sales & Trade Audit Portal")

# --- 1. SSL-HARDENED AUTH ---
@st.cache_resource
def get_gspread_client():
    try:
        creds_info = st.secrets["gcp_service_account"]
        credentials = service_account.Credentials.from_service_account_info(
            creds_info, scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
        )
        return build('sheets', 'v4', credentials=credentials, 
                     discoveryServiceUrl="https://sheets.googleapis.com/$discovery/rest?version=v4")
    except Exception as e:
        st.error(f"Auth Error: {e}")
        return None

# --- 2. DATA LOAD WITH STRICT 50% TARGET ---
def load_data():
    service = get_gspread_client()
    if not service: return pd.DataFrame()
    SPREADSHEET_ID = '1aX-RfPcICG1H6llj9TeKJ9E3UeXnkOW02HARDnqUlvY'
    try:
        result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range='A:I').execute()
        values = result.get('values', [])
        if not values: return pd.DataFrame()
        
        df = pd.DataFrame(values[1:], columns=values[0])
        for col in ['list_price', 'cogs']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # MATH: Calculate Margin
        df['Calculated_Margin'] = (df['list_price'] - df['cogs']) / df['list_price']
        
        # STRICT TARGET: Must be >= 50% to be APPROVED
        df['Audit_Status'] = df['Calculated_Margin'].apply(
            lambda x: "APPROVED" if x >= 0.50 else "REJECTED"
        )
        
        df['Margin_Display'] = df['Calculated_Margin'].apply(lambda x: f"{x*100:.1f}%")
        return df
    except Exception as e:
        st.error(f"Data Load Error: {e}")
        return pd.DataFrame()

# --- 3. EMAIL ENGINE ---
def send_buyer_approval_email(approved_df, recipient_name, recipient_email):
    sender_email = "jbconsultingdemo@gmail.com"
    app_password = "hryfpqvirwvxjkhc" 
    msg = EmailMessage()
    msg['Subject'] = "✔️ Approval: Heritage Harvest Items Cleared"
    msg['From'] = f"Jenica Bridges <{sender_email}>"
    msg['To'] = f"{recipient_name} <{recipient_email}>"
    
    item_rows = [f"- SKU ID: {row['sku_id']} | {row['product_name']}" for _, row in approved_df.iterrows()]
    body = (
        f"Hi {recipient_name},\n\n"
        "We are pleased to inform you that the following items are approved. You may move forward with planning for these SKUs:\n\n"
        + "\n".join(item_rows) +
        "\n\nBest regards,\n\n"
        "Jenica\n"
        "Harvest Heritage\n"
        "National Account Manager, Grocery"
    )
    msg.set_content(body)
    
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login(sender_email, app_password)
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.sidebar.error(f"Email failure: {e}")
        return False

# --- 4. INTERFACE ---
df = load_data()
if not df.empty:
    # Sidebar Ordering
    st.sidebar.header("Audit Controls")
    
    # 1. View Filter
    show_rejected = st.sidebar.checkbox("Show Rejected Items (Audit View)")
    
    # Apply Filtering
    if show_rejected:
        display_df = df
    else:
        display_df = df[df['Audit_Status'] == "APPROVED"]

    # 2. Product Selection
    product_list = sorted(display_df['product_name'].unique())
    selected = st.sidebar.multiselect("Select Products:", options=["SELECT ALL"] + product_list, default=["SELECT ALL"])
    final_df = display_df if "SELECT ALL" in selected else display_df[display_df['product_name'].isin(selected)]

    # 3. Buyer Info
    recipient_name = st.sidebar.text_input("Buyer Name", "Buyer Name")
    recipient_email = st.sidebar.text_input("Buyer Email", "buyer@heritageharvest.com")
    
    # 4. Action Buttons
    if st.sidebar.button("📧 Send Approval Email"):
        approved_only = final_df[final_df['Audit_Status'] == "APPROVED"]
        if not approved_only.empty:
            if send_buyer_approval_email(approved_only, recipient_name, recipient_email):
                st.sidebar.success(f"Sent to {recipient_name}!")

    csv_data = final_df[['sku_id', 'upc', 'product_name', 'Audit_Status']].to_csv(index=False).encode('utf-8-sig')
    st.sidebar.download_button(label="📥 Download Excel Audit", data=csv_data, file_name=f"Heritage_Audit.csv")

    # Main Dashboard Display
    st.success(f"✅ Audit Active: Showing {len(final_df)} items meeting 50% Margin")
    st.dataframe(
        final_df[['Audit_Status', 'sku_id', 'upc', 'product_name', 'list_price', 'Margin_Display']], 
        use_container_width=True, hide_index=True,
        column_config={"list_price": st.column_config.NumberColumn("Price", format="$%.2f")}
    )