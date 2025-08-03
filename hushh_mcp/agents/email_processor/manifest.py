# hushh_mcp/agents/email_processor/manifest.py
# Following Hushh MCP Protocol for Email Processing Agent

manifest = {
    "id": "agent_email_processor",
    "name": "Email Processor Agent",
    "description": "Privacy-first email processing agent with AI categorization and automation following Hushh MCP protocols",
    "scopes": [
        "vault.read.email",
        "custom.temporary",
        "custom.session.write"
    ],
    "version": "1.0.0",
    "capabilities": [
        "email_fetching",
        "ai_categorization", 
        "privacy_filtering",
        "automation_suggestions",
        "consent_management",
        "llm_integration"
    ],
    "dependencies": [
        "categorize_content_operon",
        "semantic_categorizer_agent",
        "automation_agent",
        "audit_logger_agent"
    ],
    "privacy_controls": {
        "local_processing": True,
        "data_retention": "user_controlled",
        "consent_granular": True,
        "audit_trail": True,
        "encryption_required": True
    }
}
