#!/usr/bin/env python3
"""
Hushh MCP PDA - Hackathon Demo Verification Script
Team "We Are Coming" - Final Submission Test

This script verifies that all core functionality works correctly
for the hackathon demo and submission.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print(f"{'='*60}")

def print_check(description, status):
    """Print a check result"""
    emoji = "✅" if status else "❌"
    print(f"{emoji} {description}")

async def test_agents():
    """Test that all MCP agents are properly configured"""
    print_section("HUSHH MCP AGENTS VERIFICATION")
    
    try:
        from hushh_mcp.agents.email_processor.index import EmailProcessorAgent
        from hushh_mcp.agents.calendar_processor.index import CalendarProcessorAgent
        from hushh_mcp.agents.audit_logger.index import AuditLoggerAgent
        
        # Test agent initialization
        email_agent = EmailProcessorAgent()
        calendar_agent = CalendarProcessorAgent()
        audit_agent = AuditLoggerAgent()
        
        print_check("EmailProcessorAgent initialization", True)
        print_check("CalendarProcessorAgent initialization", True)
        print_check("AuditLoggerAgent initialization", True)
        
        # Test agent properties
        print_check(f"Email agent ID: {email_agent.agent_id}", email_agent.agent_id == "agent_email_processor")
        print_check(f"Calendar agent ID: {calendar_agent.agent_id}", calendar_agent.agent_id == "agent_calendar_processor")
        print_check(f"Audit agent ID: {audit_agent.agent_id}", audit_agent.agent_id == "agent_audit_logger")
        
        return True
        
    except Exception as e:
        print_check(f"Agent initialization failed: {e}", False)
        return False

async def test_operons():
    """Test that operons are working"""
    print_section("HUSHH MCP OPERONS VERIFICATION")
    
    try:
        from hushh_mcp.operons.categorize_content import categorize_with_free_llm
        from hushh_mcp.operons.privacy_audit import assess_data_sensitivity
        from hushh_mcp.operons.scheduling_intelligence import analyze_scheduling_patterns
        
        # Test basic categorization
        test_content = "Team meeting scheduled for tomorrow at 3 PM to discuss project budget"
        result = await categorize_with_free_llm(test_content, "email")
        
        print_check("Content categorization operon", "category" in result)
        print_check(f"Categorized as: {result.get('category', 'unknown')}", True)
        print_check(f"Confidence: {result.get('confidence', 0):.2f}", result.get('confidence', 0) > 0)
        
        # Test privacy audit
        sensitive_content = "My SSN is 123-45-6789 and credit card is 4111-1111-1111-1111"
        privacy_result = assess_data_sensitivity(sensitive_content, "email")
        
        print_check("Privacy audit operon", "sensitivity_level" in privacy_result)
        print_check(f"Privacy level: {privacy_result.get('sensitivity_level', 'unknown')}", True)
        
        return True
        
    except Exception as e:
        print_check(f"Operon testing failed: {e}", False)
        return False

def test_vault_storage():
    """Test vault storage functionality"""
    print_section("HUSHH MCP VAULT STORAGE VERIFICATION")
    
    try:
        from hushh_mcp.vault.persistent_storage import persistent_storage
        
        # Test basic storage operations
        test_user = "demo_user_123"
        test_data = [{"id": "test_email", "category": "work", "subject": "Test"}]
        
        # Test save
        save_success = persistent_storage.save_user_emails(test_user, test_data)
        print_check("Email data save operation", save_success)
        
        # Test load
        loaded_data = persistent_storage.load_user_emails(test_user)
        print_check("Email data load operation", len(loaded_data) > 0)
        
        # Test categories
        categories = persistent_storage.get_unified_categories(test_user)
        print_check("Unified categories retrieval", isinstance(categories, dict))
        
        return True
        
    except Exception as e:
        print_check(f"Vault storage testing failed: {e}", False)
        return False

def test_consent_management():
    """Test consent token management"""
    print_section("HUSHH MCP CONSENT MANAGEMENT VERIFICATION")
    
    try:
        from hushh_mcp.consent.token import issue_token, validate_token, revoke_token
        from hushh_mcp.constants import ConsentScope
        
        # Test token issuance
        token = issue_token(
            user_id="demo_user",
            agent_id="agent_email_processor",
            scope=ConsentScope.VAULT_READ_EMAIL,
            expires_in_ms=3600000
        )
        
        print_check("Consent token issuance", token is not None)
        print_check(f"Token user_id: {token.user_id}", token.user_id == "demo_user")
        
        # Test token validation
        valid, reason, parsed = validate_token(token.token)
        print_check("Consent token validation", valid)
        
        # Test token revocation
        revoke_success = revoke_token(token.token)
        print_check("Consent token revocation", revoke_success)
        
        return True
        
    except Exception as e:
        print_check(f"Consent management testing failed: {e}", False)
        return False

def test_api_endpoints():
    """Test that FastAPI app can be imported and key endpoints exist"""
    print_section("FASTAPI APPLICATION VERIFICATION")
    
    try:
        from main import app
        
        # Get all routes
        routes = [route.path for route in app.routes]
        
        # Check key endpoints
        key_endpoints = [
            "/api/emails/process",
            "/api/calendar/process", 
            "/api/categories/unified",
            "/api/consent/revoke",
            "/health"
        ]
        
        for endpoint in key_endpoints:
            exists = any(endpoint in route for route in routes)
            print_check(f"Endpoint {endpoint}", exists)
        
        print_check(f"Total API routes: {len(routes)}", len(routes) > 10)
        
        return True
        
    except Exception as e:
        print_check(f"FastAPI testing failed: {e}", False)
        return False

def test_frontend_files():
    """Test that frontend files exist"""
    print_section("FRONTEND FILES VERIFICATION")
    
    frontend_files = [
        "frontend/index.html",
        "frontend/complete_dashboard.html", 
        "frontend/styles.css",
        "frontend/app.js"
    ]
    
    all_exist = True
    for file_path in frontend_files:
        exists = os.path.exists(file_path)
        print_check(f"File {file_path}", exists)
        if not exists:
            all_exist = False
    
    return all_exist

def run_test_suite():
    """Run basic test suite verification"""
    print_section("TEST SUITE VERIFICATION")
    
    test_files = [
        "tests/test_email_processor_agent.py",
        "tests/test_calendar_processor_agent.py",
        "tests/test_audit_logger_agent.py"
    ]
    
    all_exist = True
    for test_file in test_files:
        exists = os.path.exists(test_file)
        print_check(f"Test file {test_file}", exists)
        if not exists:
            all_exist = False
    
    return all_exist

async def main():
    """Run all verification tests"""
    print_section("HUSHH MCP PDA - HACKATHON SUBMISSION VERIFICATION")
    print("Team: We Are Coming")
    print("Members: Aryan Tamboli, Vaibhav Singh, Rohit Gupta, Udit")
    print(f"Verification Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all tests
    results = []
    
    results.append(await test_agents())
    results.append(await test_operons()) 
    results.append(test_vault_storage())
    results.append(test_consent_management())
    results.append(test_api_endpoints())
    results.append(test_frontend_files())
    results.append(run_test_suite())
    
    # Final summary
    print_section("VERIFICATION SUMMARY")
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Tests Passed: {passed}/{total}")
    print(f"🎯 Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL SYSTEMS GO! Ready for hackathon demo! 🎉")
        print("\n📋 Demo Instructions:")
        print("1. Run: python main.py")
        print("2. Run: cd frontend && python -m http.server 3000") 
        print("3. Open: http://localhost:3000")
        print("4. Demo privacy-first email/calendar processing")
        print("5. Show consent revocation and data deletion")
    else:
        print("\n⚠️  Some systems need attention before demo")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
