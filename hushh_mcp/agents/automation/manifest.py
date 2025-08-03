# hushh_mcp/agents/automation/manifest.py

manifest = {
    "id": "agent_automation",
    "name": "Automation Agent",
    "description": "Specialized agent for automation stack operations including event scheduling, note creation, and todo management",
    "scopes": [
        "custom.session.write",
        "custom.temporary",
        "vault.read.email"
    ],
    "version": "1.0.0",
    "capabilities": [
        "event_scheduling",
        "note_creation",
        "todo_management",
        "task_tracking",
        "automation_analytics"
    ],
    "dependencies": [
        "schedule_event_operon",
        "create_note_operon",
        "manage_todos_operon"
    ],
    "automation_types": [
        "calendar_events",
        "structured_notes",
        "todo_lists",
        "reminders",
        "task_updates"
    ]
}
