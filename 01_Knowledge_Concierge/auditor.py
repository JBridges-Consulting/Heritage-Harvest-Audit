import os
import base64
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    creds = None
    # Check current folder first, then parent folder for token
    token_path = 'token.json'
    if not os.path.exists(token_path):
        token_path = '../token.json'

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Check current folder first, then parent folder for credentials
            cred_path = 'credentials.json'
            if not os.path.exists(cred_path):
                cred_path = '../credentials.json'
                
            flow = InstalledAppFlow.from_client_secrets_file(cred_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
            
    return build('gmail', 'v1', credentials=creds)

def get_latest_draft(service):
    """Gets the most recent draft from Gmail."""
    try:
        results = service.users().drafts().list(userId='me', maxResults=1).execute()
        drafts = results.get('drafts', [])
        if not drafts:
            print("No drafts found.")
            return None
        
        draft_id = drafts[0]['id']
        full_draft = service.users().drafts().get(userId='me', id=draft_id, format='full').execute()
        return full_draft
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def decode_body(payload):
    """Decodes the email body from base64."""
    parts = payload.get('parts')
    data = ""
    if parts:
        for part in parts:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data')
    else:
        data = payload['body'].get('data')

    if data:
        return base64.urlsafe_b64decode(data).decode('utf-8')
    return ""

def audit_content(email_text):
    """Sends the email text to OpenAI to check against rules."""
    try:
        with open("compliance_rules.txt", "r") as f:
            rules = f.read()
    except FileNotFoundError:
        print("Error: compliance_rules.txt not found!")
        return "Error: Rules file missing."

    prompt = f"""
    You are a strict Compliance Auditor. 
    Here are the laws you must enforce:
    {rules}

    Here is a draft email written by a sales agent:
    "{email_text}"

    Task:
    1. Does this email violate any rules? 
    2. If YES, explain exactly which rule and suggest a fix.
    3. If NO, simply output "PASSED".
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content

def main():
    service = get_gmail_service()
    
    # --- DIAGNOSTIC CHECK: WHO AM I? ---
    profile = service.users().getProfile(userId='me').execute()
    email_address = profile.get('emailAddress')
    print(f"🔐 Authenticated as: {email_address}")
    # -----------------------------------
    
    print("🔍 Looking for latest draft...")
    draft = get_latest_draft(service)
    
    if draft:
        try:
            email_body = decode_body(draft['message']['payload'])
            print(f"\n📄 Analyzing Draft Content:\n{email_body[:100]}...\n")
            
            print("⚖️  Auditing...")
            audit_result = audit_content(email_body)
            
            print("\n" + "="*30)
            print("AUDIT REPORT")
            print("="*30)
            print(audit_result)
        except KeyError:
            print("Error: Could not read email payload. The draft structure might be empty.")
    else:
        print(f"❌ No drafts found for user: {email_address}")
        print("   (Check if you are logged into the correct account)")

if __name__ == '__main__':
    main()