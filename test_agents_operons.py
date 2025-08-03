import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hushh_mcp.agents.email_processor.index import EmailProcessorAgent
from hushh_mcp.agents.calendar_processor.index import CalendarProcessorAgent
from hushh_mcp.agents.audit_logger.index import AuditLoggerAgent
from hushh_mcp.operons.categorize_content import categorize_with_free_llm

async def test_all_agents_and_operons():
    """Test all agents and operons to ensure they're working"""
    
    print("🧪 Testing All Hushh MCP Agents and Operons")
    print("=" * 60)
    
    # Test Email Processor Agent
    print("\n📧 Testing Email Processor Agent...")
    try:
        email_agent = EmailProcessorAgent()
        print(f"✅ Email Agent initialized: {email_agent.agent_id}")
        
        # Test status check
        status = email_agent.get_processing_status("test_user")
        print(f"✅ Status check works: {status['user_id']}")
        
    except Exception as e:
        print(f"❌ Email Agent error: {e}")
    
    # Test Calendar Processor Agent
    print("\n📅 Testing Calendar Processor Agent...")
    try:
        calendar_agent = CalendarProcessorAgent()
        print(f"✅ Calendar Agent initialized: {calendar_agent.agent_id}")
        
    except Exception as e:
        print(f"❌ Calendar Agent error: {e}")
    
    # Test Audit Logger Agent
    print("\n� Testing Audit Logger Agent...")
    try:
        audit_agent = AuditLoggerAgent()
        print(f"✅ Audit Agent initialized: {audit_agent.agent_id}")
        
        # Test audit logging
        await audit_agent.log_activity(
            user_id="test_user",
            action="test_action",
            details={"test": "data"}
        )
        print("✅ Audit logging works")
        
    except Exception as e:
        print(f"❌ Audit Agent error: {e}")
    
    # Test LLM Categorization Operon
    print("\n🤖 Testing LLM Categorization Operon...")
    try:
        test_content = "Meeting with the development team to discuss project roadmap"
        result = await categorize_with_free_llm(test_content, "email")
        print(f"✅ LLM Categorization works: {result['categories']}")
        print(f"   Confidence: {result['confidence']}")
        print(f"   Method: {result['processing_method']}")
        
    except Exception as e:
        print(f"❌ LLM Categorization error: {e}")
    
    # Test other operons
    print("\n🔧 Testing Other Operons...")
    try:
        from hushh_mcp.operons.content_classification import classify_content_category
        from hushh_mcp.operons.privacy_audit import assess_data_sensitivity, DataType
        
        # Test content classification
        classification = classify_content_category(
            "Urgent: Please review the quarterly financial report",
            "email"
        )
        print(f"✅ Content Classification: {classification}")
        
        # Test privacy audit
        privacy_result = assess_data_sensitivity(
            "john.doe@company.com sent a budget spreadsheet",
            DataType.EMAIL
        )
        print(f"✅ Privacy Audit: {privacy_result['risk_level']}")
        
    except Exception as e:
        print(f"❌ Other Operons error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Agent and Operon Testing Complete!")
    
    return True

if __name__ == "__main__":
    asyncio.run(test_all_agents_and_operons())
