# hushh_mcp/agents/audit_logger/manifest.py

manifest = {
    "id": "agent_audit_logger",
    "name": "Audit Logger Agent",
    "description": "Specialized agent for audit logging and compliance tracking with SQLite database",
    "scopes": [
        "custom.temporary",
        "vault.read.email"
    ],
    "version": "1.0.0",
    "capabilities": [
        "activity_logging",
        "compliance_tracking",
        "audit_trail_generation",
        "violation_detection",
        "data_export",
        "compliance_reporting"
    ],
    "dependencies": [
        "sqlite3",
        "json",
        "datetime"
    ],
    "database": {
        "type": "sqlite",
        "path": "./pda_audit.db",
        "tables": ["audit_logs", "compliance_events"]
    },
    "retention_policy": {
        "audit_logs": "365 days",
        "compliance_events": "730 days"
    }
}
