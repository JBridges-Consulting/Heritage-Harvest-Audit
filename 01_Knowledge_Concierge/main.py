import os
import base64
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# SCOPES: Updated to ensure we can Read, Write Drafts, and Modify Labels
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.modify"
]

def load_knowledge_base():
    """Reads the policies/info from the text file."""
    try:
        with open("knowledge_base.txt", "r") as f:
            return f.read()
    except FileNotFoundError:
        print("⚠️ Warning: knowledge_base.txt not found! Using empty context.")
        return "No internal documents available."

def get_gmail_service():
    """Authenticates with Gmail and returns the service."""
    creds = None
    token_path = 'token.json'
    
    # Check parent directory if not in current
    if not os.path.exists(token_path) and os.path.exists('../token.json'):
        token_path = '../token.json'

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            cred_path = 'credentials.json'
            if not os.path.exists(cred_path):
                cred_path = '../credentials.json'
            flow = InstalledAppFlow.from_client_secrets_file(cred_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def create_draft(service, user_id, message_payload):
    """Creates a draft email in the user's mailbox."""
    try:
        draft = service.users().drafts().create(userId=user_id, body=message_payload).execute()
        print(f"✅ SUCCESS! Draft created. ID: {draft['id']}")
        return draft
    except Exception as e:
        print(f"❌ Error creating draft: {e}")
        return None

def main():
    service = get_gmail_service()
    knowledge_text = load_knowledge_base()
    
    # Find unread emails
    print("🔎 Heritage Harvest Concierge: Scanning Inbox...")
    results = service.users().messages().list(userId='me', q='is:unread', maxResults=5).execute()
    messages = results.get('messages', [])

    if not messages:
        print("No new emails found.")
    else:
        for msg in messages:
            msg_detail = service.users().messages().get(userId='me', id=msg['id']).execute()
            headers = msg_detail['payload']['headers']

            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            snippet = msg_detail.get('snippet', '')
            thread_id = msg['threadId'] # <--- CRITICAL: Keeps reply in the same thread

            print(f"📩 Processing: '{subject}' from {sender}")

            # ---------------------------------------------------------
            # THE BRAIN: Heritage Harvest Persona
            # ---------------------------------------------------------
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": """
                        You are the Senior Sales Support Specialist for Heritage Harvest Snacks.
                        Your goal is to assist retail buyers and internal sales reps with accurate, brand-compliant information.
                        
                        BRAND VOICE & TONE:
                        - Warm, professional, and helpful (like a trusted partner).
                        - Use clear, commercial language (CPG industry standard).
                        - Prioritize accuracy: If the answer isn't in the Knowledge Base, admit it politely.

                        IMPORTANT FORMATTING:
                        1. Keep the email concise and scannable.
                        2. Always sign off as:
                           "Jenica Bridges
                           National Sales Manager | Heritage Harvest Snacks"
                        3. If you propose a meeting, use this format: "https://calendly.com/bridges-jenica/30min"
                     """},
                    {"role": "user", "content": f"Here is the incoming email: {snippet}\n\nReference Knowledge Base:\n{knowledge_text}"}
                ]
            )
            
            email_draft_body = response.choices[0].message.content

            # ---------------------------------------------------------
            # THE HANDS: Create Gmail Draft with Threading
            # ---------------------------------------------------------
            message = EmailMessage()
            message.set_content(email_draft_body)
            message["To"] = sender
            # Safety check to avoid "Re: Re:"
            message["Subject"] = subject if subject.startswith("Re:") else f"Re: {subject}"
            
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            create_message_payload = {
                'message': {
                    'threadId': thread_id, # <--- Links to original email
                    'raw': encoded_message
                }
            }

            create_draft(service, 'me', create_message_payload)

            # ---------------------------------------------------------
            # CLEANUP: Mark as Processed
            # ---------------------------------------------------------
            service.users().messages().modify(
                userId='me',
                id=msg['id'],
                body={
                    'removeLabelIds': ['UNREAD'], 
                    'addLabelIds': ['STARRED'] 
                }
            ).execute()
            
            print("🌟 Inquiry Processed & Draft Saved to 'Drafts'")

if __name__ == '__main__':
    main()