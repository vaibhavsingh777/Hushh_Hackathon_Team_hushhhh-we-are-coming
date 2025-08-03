# hushh_mcp/agents/pda_orchestrator/manifest.py

manifest = {
    "id": "agent_pda_orchestrator",
    "name": "PDA Orchestrator Agent",
    "description": "Main orchestrator that coordinates specialized PDA agents following bacteria-like modular architecture",
    "scopes": [
        "vault.read.email",
        "vault.read.finance", 
        "agent.identity.verify",
        "custom.temporary",
        "custom.session.write"
    ],
    "version": "1.0.0",
    "capabilities": [
        "task_routing",
        "agent_coordination", 
        "consent_validation",
        "audit_logging",
        "trust_delegation"
    ],
    "specialized_agents": [
        "agent_semantic_categorizer",
        "agent_automation", 
        "agent_audit_logger",
        "agent_data_manager",
        "agent_notification",
        "agent_file_parser"
    ]
}
