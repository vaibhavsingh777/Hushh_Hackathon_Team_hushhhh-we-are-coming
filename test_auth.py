#!/usr/bin/env python3
"""
Test Google OAuth authentication flow
Run this to test if your Google OAuth configuration is working correctly
"""

import os
import asyncio
from dotenv import load_dotenv
import aiohttp

# Load environment variables
load_dotenv()

# Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_OAUTH_REDIRECT_URI")

def test_env_variables():
    """Test if all required environment variables are set"""
    print("🔍 Testing Environment Variables...")
    print(f"GOOGLE_CLIENT_ID: {'✅ Set' if GOOGLE_CLIENT_ID else '❌ Missing'}")
    print(f"GOOGLE_CLIENT_SECRET: {'✅ Set' if GOOGLE_CLIENT_SECRET else '❌ Missing'}")
    print(f"GOOGLE_REDIRECT_URI: {'✅ Set' if GOOGLE_REDIRECT_URI else '❌ Missing'}")
    
    if GOOGLE_CLIENT_ID:
        print(f"Client ID: {GOOGLE_CLIENT_ID[:20]}...{GOOGLE_CLIENT_ID[-10:]}")
    if GOOGLE_REDIRECT_URI:
        print(f"Redirect URI: {GOOGLE_REDIRECT_URI}")
    
    return all([GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI])

def generate_auth_url():
    """Generate the Google OAuth URL"""
    if not test_env_variables():
        print("❌ Missing required environment variables")
        return None
    
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
        f"state=test_state_123"
    )
    
    print("\n🔗 Generated OAuth URL:")
    print("="*50)
    print(auth_url)
    print("="*50)
    
    return auth_url

async def test_oauth_endpoint():
    """Test if Google OAuth endpoint responds correctly"""
    print("\n🌐 Testing Google OAuth endpoint...")
    
    test_url = f"https://accounts.google.com/o/oauth2/auth?client_id={GOOGLE_CLIENT_ID}&response_type=code&scope=openid&redirect_uri={GOOGLE_REDIRECT_URI}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(test_url, allow_redirects=False) as response:
                print(f"Status: {response.status}")
                
                if response.status == 302:
                    print("✅ OAuth endpoint responding correctly (redirect to login)")
                    return True
                elif response.status == 400:
                    error_text = await response.text()
                    print(f"❌ OAuth configuration error: {error_text}")
                    
                    if "redirect_uri_mismatch" in error_text:
                        print("\n💡 SOLUTION: Redirect URI mismatch detected!")
                        print("Go to Google Cloud Console and add this exact URI:")
                        print(f"   {GOOGLE_REDIRECT_URI}")
                        print("\nMake sure:")
                        print("1. No trailing slash")
                        print("2. Exact case match") 
                        print("3. Use http:// for localhost")
                        print("4. No extra spaces")
                    
                    return False
                else:
                    print(f"❌ Unexpected response: {response.status}")
                    error_text = await response.text()
                    print(error_text[:500])
                    return False
                    
    except Exception as e:
        print(f"❌ Network error: {e}")
        return False

def print_setup_instructions():
    """Print setup instructions for Google Cloud Console"""
    print("\n📋 Google Cloud Console Setup Instructions:")
    print("="*60)
    print("1. Go to: https://console.cloud.google.com/")
    print("2. Select your project (or create one)")
    print("3. Go to APIs & Services > Credentials")
    print("4. Click 'Create Credentials' > 'OAuth 2.0 Client IDs'")
    print("5. Choose 'Web application'")
    print("6. Add this Authorized redirect URI:")
    print(f"   {GOOGLE_REDIRECT_URI}")
    print("7. Enable these APIs in 'APIs & Services > Library':")
    print("   - Gmail API")
    print("   - Google Calendar API")
    print("   - Google+ API")
    print("8. Copy Client ID and Client Secret to your .env file")
    print("="*60)

async def main():
    """Main test function"""
    print("🔐 Google OAuth Configuration Test")
    print("="*40)
    
    # Test environment variables
    if not test_env_variables():
        print_setup_instructions()
        return
    
    # Generate auth URL
    auth_url = generate_auth_url()
    if not auth_url:
        return
    
    # Test OAuth endpoint
    endpoint_ok = await test_oauth_endpoint()
    
    if endpoint_ok:
        print("\n✅ OAuth configuration looks good!")
        print("\n🚀 Next steps:")
        print("1. Open the generated URL in your browser")
        print("2. Complete the OAuth flow")
        print("3. Check if you get redirected back to your app")
    else:
        print("\n❌ OAuth configuration has issues")
        print_setup_instructions()

if __name__ == "__main__":
    asyncio.run(main())
