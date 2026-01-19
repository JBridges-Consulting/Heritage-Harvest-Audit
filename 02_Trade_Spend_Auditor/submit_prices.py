import pandas as pd
from googleapiclient.discovery import build
from google.oauth2 import service_account
import streamlit as st

# Load your local pricing file (assuming it's named pricing.csv)
def submit_to_dashboard():
    try:
        df = pd.read_csv("pricing.csv") # Your sales rep updates this file
        
        # Authenticate using the same secrets as your app
        creds_info = st.secrets["gcp_service_account"]
        credentials = service_account.Credentials.from_service_account_info(creds_info)
        service = build('sheets', 'v4', credentials=credentials)
        
        SPREADSHEET_ID = '1aX-RfPcICG1H6llj9TeKJ9E3UeXnkOW02HARDnqUlvY'
        RANGE_NAME = 'A2' # Start overwriting from the first data row
        
        # Convert DF to list format for Google API
        values = [df.columns.tolist()] + df.values.tolist()
        body = {'values': values}
        
        service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID, range="A1",
            valueInputOption="USER_ENTERED", body=body
        ).execute()
        
        print("🚀 Prices Submitted! Dashboard updated.")
    except Exception as e:
        print(f"❌ Submission failed: {e}")

if __name__ == "__main__":
    submit_to_dashboard()