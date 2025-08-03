"""
Test the full authentication flow by visiting the actual app
"""

import webbrowser
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_OAUTH_REDIRECT_URI")

# Generate the OAuth URL
scopes = [
    'openid',
    'email', 
    'profile',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar.readonly'
]

scopes_str = ' '.join(scopes)

auth_url = (
    f"https://accounts.google.com/o/oauth2/auth?"
    f"client_id={GOOGLE_CLIENT_ID}&"
    f"redirect_uri={GOOGLE_REDIRECT_URI}&"
    f"scope={scopes_str}&"
    f"response_type=code&"
    f"access_type=offline&"
    f"state=test_auth_flow"
)

print("🔗 Opening OAuth URL in browser...")
print(f"Redirect URI: {GOOGLE_REDIRECT_URI}")
print("\nIf you get a redirect URI mismatch error, copy this exact URI to Google Cloud Console:")
print(f"   {GOOGLE_REDIRECT_URI}")

# Open the URL in the default browser
webbrowser.open(auth_url)

print("\n✅ Browser opened. Complete the OAuth flow and check if you're redirected back to your app.")
print("If you get an error, check the browser's network tab or console for details.")
