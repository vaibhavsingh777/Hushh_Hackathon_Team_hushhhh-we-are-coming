# hushh_mcp/agents/notification/manifest.py

manifest = {
    "id": "agent_notification",
    "name": "Notification Agent",
    "description": "Specialized agent for multi-channel notification delivery including WhatsApp, email, SMS, and more",
    "scopes": [
        "custom.session.write",
        "custom.temporary",
        "vault.read.email",
        "vault.read.phone"
    ],
    "version": "1.0.0",
    "capabilities": [
        "email_notifications",
        "whatsapp_notifications",
        "sms_notifications",
        "push_notifications",
        "slack_notifications",
        "discord_notifications",
        "notification_scheduling",
        "preference_management",
        "delivery_tracking"
    ],
    "supported_channels": [
        "email",
        "whatsapp",
        "sms", 
        "push",
        "slack",
        "discord"
    ],
    "dependencies": [
        "send_notification_operon",
        "email_service",
        "whatsapp_api",
        "sms_service"
    ],
    "integrations": {
        "email": "SMTP/SendGrid",
        "whatsapp": "WhatsApp Business API",
        "sms": "Twilio/AWS SNS",
        "push": "Firebase/APNs",
        "slack": "Slack Web API",
        "discord": "Discord API"
    }
}
