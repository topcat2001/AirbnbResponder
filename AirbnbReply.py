import os
import sys
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Python path: {sys.path}")
print(f"Current working directory: {os.getcwd()}")

import pickle
import base64
import time
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import openai

# Define the base directory where all files are located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(f"Base directory: {BASE_DIR}")

# Set OpenAI API Key
with open(os.path.join(BASE_DIR, "openai_key.txt"), "r") as f:
    openai.api_key = f.read().strip()

# Gmail API OAuth Scopes
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

def authenticate():
    """Authenticate Gmail API using OAuth and return the service object."""
    creds = None
    token_path = os.path.join(BASE_DIR, "token.pickle")
    client_secret_path = os.path.join(BASE_DIR, "client_secret.json")
    
    print(f"Looking for token at: {token_path}")
    if os.path.exists(token_path):
        print("Found token.pickle")
        with open(token_path, "rb") as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(client_secret_path):
                raise FileNotFoundError(f"client_secret.json not found at {client_secret_path}")
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(token_path, "wb") as token:
            pickle.dump(creds, token)
    
    return build("gmail", "v1", credentials=creds)

def get_unread_airbnb_messages(service):
    """Retrieve unread emails from Airbnb."""
    response = service.users().messages().list(userId="me", q="from:topcat@gmail.com is:unread").execute()
    messages = response.get("messages", [])
    return messages

def get_email_body(service, msg_id):
    """Extract the body text from an email."""
    msg = service.users().messages().get(userId="me", id=msg_id).execute()
    payload = msg.get("payload", {})
    parts = payload.get("parts", [])
    
    for part in parts:
        if part.get("mimeType") == "text/plain":
            return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
    
    return ""

def generate_response(email_text, airbnb_info):
    """Use OpenAI GPT-4 to generate a response based on email content."""
    prompt = f"""
    You are an Airbnb host named JK. Analyze the following guest email and respond appropriately.

    Important Instructions:
    1. First, determine if a response is needed:
       - If the email is just a thank you, confirmation, or doesn't require a response, start with "NORESPONSE_NEEDED:" and briefly explain why.
       - If the email needs a response, continue with step 2.
    
    2. If a response is needed:
       - If you can fully answer using the provided information, write a friendly and helpful response.
       - If you cannot answer due to missing information, start with "INSUFFICIENT_INFORMATION:" and explain what details you need.
    
    3. Keep the tone professional but warm.
    4. Be concise but thorough. Don't add information that is not directly relevant.
    
    Airbnb Info:
    {airbnb_info}
    
    Guest Email:
    {email_text}
    """
    
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful Airbnb host assistant. Always maintain professionalism while being friendly."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content.strip()

def send_reply(service, msg_id, reply_text):
    """Send a reply to the email."""
    original_msg = service.users().messages().get(userId="me", id=msg_id, format="metadata").execute()
    headers = {h["name"].lower(): h["value"] for h in original_msg["payload"]["headers"]}
    
    reply_msg = MIMEText(reply_text)
    reply_msg["to"] = headers.get("from")
    reply_msg["subject"] = "Re: " + headers.get("subject", "")
    reply_msg["threadId"] = original_msg["threadId"]
    
    encoded_msg = {"raw": base64.urlsafe_b64encode(reply_msg.as_bytes()).decode()}
    service.users().messages().send(userId="me", body=encoded_msg).execute()

def save_draft(service, reply_text):
    """Save a draft if there is insufficient information."""
    draft_msg = MIMEText(reply_text)
    draft_msg["to"] = ""
    draft_msg["subject"] = "Draft Reply"
    
    encoded_msg = {"message": {"raw": base64.urlsafe_b64encode(draft_msg.as_bytes()).decode()}}
    service.users().drafts().create(userId="me", body=encoded_msg).execute()

def process_emails():
    """Main function to process unread Airbnb emails and respond accordingly."""
    print("Starting email processing...")
    service = authenticate()
    print("Gmail authentication successful")
    
    messages = get_unread_airbnb_messages(service)
    print(f"Found {len(messages)} unread messages")
    
    if not messages:
        print("No new Airbnb emails.")
        return
    
    print("Loading Airbnb info...")
    airbnb_info_path = os.path.join(BASE_DIR, "airbnb_info.txt")
    with open(airbnb_info_path, "r") as f:
        airbnb_info = f.read().strip()
    
    for msg in messages:
        msg_id = msg["id"]
        print(f"\nProcessing email {msg_id}")
        email_text = get_email_body(service, msg_id)
        print("Email body retrieved")
        print(f"Email content: {email_text[:100]}...")
        
        response_text = generate_response(email_text, airbnb_info)
        print("Generated response")
        
        if response_text.startswith("NORESPONSE_NEEDED:"):
            save_draft(service, response_text)
            print(f"Draft saved for email {msg_id} - No response needed")
        elif response_text.startswith("INSUFFICIENT_INFORMATION:"):
            save_draft(service, response_text)
            print(f"Draft saved for email {msg_id} - Insufficient information")
        else:
            send_reply(service, msg_id, response_text)
            print(f"Reply sent for email {msg_id}")
        
        # Mark email as read
        service.users().messages().modify(userId="me", id=msg_id, body={"removeLabelIds": ["UNREAD"]}).execute()
        print("Marked email as read")
        time.sleep(2)  # Prevent rate limiting

if __name__ == "__main__":
    process_emails()
