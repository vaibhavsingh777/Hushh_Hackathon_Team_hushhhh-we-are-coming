# Calendar Processor Agent Manifest - Hushh MCP Implementation

manifest = {
    "id": "agent_calendar_processor",
    "name": "Calendar Processor Agent",
    "description": "Privacy-first calendar data processing with AI insights",
    "version": "1.0.0",
    "scopes": [
        "vault.read.calendar",
        "custom.temporary",
        "custom.session_write"
    ],
    "privacy_level": "high",
    "data_types": [
        "calendar_events",
        "meeting_metadata", 
        "schedule_patterns"
    ],
    "capabilities": [
        "event_categorization",
        "schedule_analysis",
        "meeting_insights",
        "time_optimization"
    ]
}
