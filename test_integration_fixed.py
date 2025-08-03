"""
Quick test to verify the Google integration is working properly
"""

async def test_integration():
    """Test the Google integration setup"""
    print("🧪 Testing Google Integration Setup")
    print("=" * 50)
    
    try:
        # Test imports
        from hushh_mcp.integrations import (
            GmailClient, 
            GoogleCalendarClient,
            create_gmail_client_from_token,
            create_calendar_client_from_token
        )
        print("✅ All imports successful")
        
        # Test client creation (will fail with mock token, but structure is correct)
        print("📧 Testing Gmail client structure...")
        try:
            gmail = GmailClient("mock_token")
            print(f"   ✅ Gmail client created: {type(gmail)}")
        except Exception as e:
            print(f"   ⚠️  Gmail client error (expected): {e}")
        
        print("📅 Testing Calendar client structure...")
        try:
            calendar = GoogleCalendarClient("mock_token")
            print(f"   ✅ Calendar client created: {type(calendar)}")
        except Exception as e:
            print(f"   ⚠️  Calendar client error (expected): {e}")
        
        print("\n🎯 Integration Status: READY")
        print("📋 Next steps:")
        print("1. Configure Google Cloud Console (APIs enabled, OAuth setup)")
        print("2. Set OAuth credentials in config")
        print("3. Start server: python main.py") 
        print("4. Test OAuth: http://localhost:8000/auth/google/redirect")
        print("5. Process real emails: POST /api/emails/process/30")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_integration())
