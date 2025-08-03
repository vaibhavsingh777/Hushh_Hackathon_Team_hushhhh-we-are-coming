# hushh_mcp/agents/pda/manifest.py

manifest = {
    "id": "agent_pda",
    "name": "Personal Data Agent",
    "description": "Comprehensive PDA with semantic categorization, automation, and consent-first access",
    "scopes": [
        "vault.read.email",
        "vault.read.calendar", 
        "vault.read.tasks",
        "vault.read.notes",
        "vault.write.tasks",
        "vault.write.notes",
        "vault.write.calendar",
        "agent.pda.categorize",
        "agent.pda.automate",
        "agent.pda.schedule"
    ],
    "version": "1.0.0",
    "features": [
        "semantic_categorization",
        "automation_stack", 
        "consent_first_access",
        "audit_logging",
        "zero_data_retention",
        "modular_extensible"
    ],
    "author": "Team Hushh Hackathon",
    "dependencies": [
        "operons.semantic_categorizer",
        "operons.task_automator", 
        "operons.schedule_event",
        "operons.create_note"
    ]
}
