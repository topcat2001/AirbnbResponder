import os
import pickle
import google.auth
import google.auth.transport.requests
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Define OAuth scopes (Read/Send Gmail)
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def authenticate():
    print("Starting authentication process...")
    creds = None

    # Load existing token if available
    if os.path.exists("token.pickle"):
        print("Found existing token.pickle file")
        with open("token.pickle", "rb") as token_file:
            creds = pickle.load(token_file)
            print("Loaded existing credentials")

    # If no valid credentials, request login
    if not creds or not creds.valid:
        print("Need new credentials or refresh...")
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired token...")
            creds.refresh(Request())  # Refresh token automatically
        else:
            print("Starting new OAuth flow...")
            print("Looking for client_secret.json...")
            if not os.path.exists('client_secret.json'):
                print("Error: client_secret.json not found in current directory!")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES  # Load OAuth credentials file
            )
            print("Opening browser for authentication...")
            creds = flow.run_local_server(port=0)  # Open browser for login
            print("Browser authentication completed")

        # Save credentials for future use
        print("Saving new credentials to token.pickle...")
        with open("token.pickle", "wb") as token_file:
            pickle.dump(creds, token_file)

    return creds

# Run authentication
print(f"Current working directory: {os.getcwd()}")
result = authenticate()
if result:
    print("Authentication successful. Token saved!")
else:
    print("Authentication failed!")