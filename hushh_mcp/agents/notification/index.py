# hushh_mcp/agents/notification/index.py

from typing import Dict, Any, List, Optional
from hushh_mcp.consent.token import validate_token
from hushh_mcp.constants import ConsentScope
from hushh_mcp.types import UserID
from hushh_mcp.operons.send_notification import send_email_notification, send_whatsapp_notification
import time


class NotificationAgent:
    """
    Specialized agent for notification delivery.
    Supports WhatsApp, email, and other notification channels.
    """

    def __init__(self, agent_id: str = "agent_notification"):
        self.agent_id = agent_id
        self.required_scope = ConsentScope.CUSTOM_SESSION_WRITE
        
        # Supported notification channels
        self.supported_channels = [
            "email",
            "whatsapp", 
            "sms",
            "push",
            "slack",
            "discord"
        ]

    def send_notification(self, user_id: UserID, token_str: str, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send notification through specified channel with consent validation.
        
        Args:
            user_id: User to send notification to
            token_str: Valid consent token
            notification_data: Notification details (channel, message, etc.)
            
        Returns:
            Dict with notification results
        """
        # Validate consent
        valid, reason, token = validate_token(token_str, expected_scope=self.required_scope)
        
        if not valid:
            raise PermissionError(f"❌ Notification sending denied: {reason}")
        
        if token.user_id != user_id:
            raise PermissionError("❌ Token user mismatch")

        print(f"📢 Notification Agent sending notification for user {user_id}")
        
        # Validate notification data
        required_fields = ["channel", "message"]
        missing_fields = [field for field in required_fields if field not in notification_data]
        
        if missing_fields:
            return {"error": f"Missing required fields: {missing_fields}"}
        
        channel = notification_data["channel"].lower()
        
        if channel not in self.supported_channels:
            return {"error": f"Unsupported channel: {channel}. Supported: {self.supported_channels}"}

        try:
            # Route to appropriate notification handler
            if channel == "email":
                result = self._send_email(user_id, notification_data)
            elif channel == "whatsapp":
                result = self._send_whatsapp(user_id, notification_data)
            elif channel == "sms":
                result = self._send_sms(user_id, notification_data)
            elif channel == "push":
                result = self._send_push(user_id, notification_data)
            elif channel == "slack":
                result = self._send_slack(user_id, notification_data)
            elif channel == "discord":
                result = self._send_discord(user_id, notification_data)
            else:
                return {"error": f"Handler not implemented for channel: {channel}"}
            
            # Add metadata
            result.update({
                "user_id": user_id,
                "channel": channel,
                "sent_at": int(time.time() * 1000),
                "agent_id": self.agent_id,
                "token_id": token.signature[:8]
            })
            
            print(f"✅ Notification sent via {channel}")
            return result
            
        except Exception as e:
            print(f"❌ Notification sending failed: {str(e)}")
            return {"error": f"Notification failed: {str(e)}"}

    def _send_email(self, user_id: UserID, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send email notification."""
        try:
            result = send_email_notification(
                recipient=notification_data.get("recipient", user_id),
                subject=notification_data.get("subject", "Notification from PDA"),
                message=notification_data["message"],
                sender=notification_data.get("sender", "noreply@pda.local"),
                html=notification_data.get("html", False)
            )
            
            return {
                "notification_id": result["notification_id"],
                "status": "sent",
                "channel_response": result
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def _send_whatsapp(self, user_id: UserID, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send WhatsApp notification."""
        try:
            result = send_whatsapp_notification(
                phone_number=notification_data.get("phone_number", ""),
                message=notification_data["message"],
                media_url=notification_data.get("media_url", "")
            )
            
            return {
                "notification_id": result["notification_id"],
                "status": "sent",
                "channel_response": result
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def _send_sms(self, user_id: UserID, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send SMS notification."""
        # Mock SMS implementation
        phone_number = notification_data.get("phone_number", "")
        message = notification_data["message"]
        
        if not phone_number:
            return {"status": "failed", "error": "Phone number required for SMS"}
        
        # In production, integrate with Twilio, AWS SNS, etc.
        notification_id = f"sms_{int(time.time() * 1000)}"
        
        return {
            "notification_id": notification_id,
            "status": "sent",
            "phone_number": phone_number,
            "message_length": len(message)
        }

    def _send_push(self, user_id: UserID, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send push notification."""
        # Mock push notification implementation
        device_token = notification_data.get("device_token", "")
        title = notification_data.get("title", "PDA Notification")
        message = notification_data["message"]
        
        # In production, integrate with Firebase, APNs, etc.
        notification_id = f"push_{int(time.time() * 1000)}"
        
        return {
            "notification_id": notification_id,
            "status": "sent",
            "title": title,
            "message": message,
            "device_token": device_token[:10] + "..." if device_token else "unknown"
        }

    def _send_slack(self, user_id: UserID, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send Slack notification."""
        # Mock Slack implementation
        channel = notification_data.get("slack_channel", "#general")
        message = notification_data["message"]
        webhook_url = notification_data.get("webhook_url", "")
        
        # In production, use Slack Web API or webhooks
        notification_id = f"slack_{int(time.time() * 1000)}"
        
        return {
            "notification_id": notification_id,
            "status": "sent",
            "channel": channel,
            "message": message
        }

    def _send_discord(self, user_id: UserID, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send Discord notification."""
        # Mock Discord implementation
        channel_id = notification_data.get("discord_channel", "")
        message = notification_data["message"]
        
        # In production, use Discord API
        notification_id = f"discord_{int(time.time() * 1000)}"
        
        return {
            "notification_id": notification_id,
            "status": "sent",
            "channel_id": channel_id,
            "message": message
        }

    def schedule_notification(self, user_id: UserID, token_str: str, schedule_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Schedule a notification for future delivery.
        """
        # Validate consent
        valid, reason, token = validate_token(token_str, expected_scope=self.required_scope)
        
        if not valid:
            raise PermissionError(f"❌ Notification scheduling denied: {reason}")

        print(f"⏰ Notification Agent scheduling notification for user {user_id}")
        
        # Validate schedule data
        required_fields = ["notification_data", "schedule_time"]
        missing_fields = [field for field in required_fields if field not in schedule_data]
        
        if missing_fields:
            return {"error": f"Missing required fields: {missing_fields}"}

        try:
            # In production, this would integrate with a job scheduler like Celery, AWS Lambda, etc.
            schedule_id = f"schedule_{int(time.time() * 1000)}"
            
            result = {
                "schedule_id": schedule_id,
                "user_id": user_id,
                "notification_data": schedule_data["notification_data"],
                "schedule_time": schedule_data["schedule_time"],
                "created_at": int(time.time() * 1000),
                "status": "scheduled",
                "agent_id": self.agent_id
            }
            
            print(f"✅ Notification scheduled with ID: {schedule_id}")
            return result
            
        except Exception as e:
            print(f"❌ Notification scheduling failed: {str(e)}")
            return {"error": f"Scheduling failed: {str(e)}"}

    def get_notification_history(self, user_id: UserID, token_str: str, days: int = 7) -> Dict[str, Any]:
        """
        Get notification history for user.
        """
        # Validate consent
        valid, reason, token = validate_token(token_str, expected_scope=ConsentScope.CUSTOM_TEMPORARY)
        
        if not valid:
            raise PermissionError(f"❌ Notification history denied: {reason}")

        print(f"📊 Notification Agent retrieving history for user {user_id}")
        
        # Mock history data - in production, query from database
        mock_history = [
            {
                "notification_id": "email_123456789",
                "channel": "email",
                "status": "sent",
                "sent_at": int(time.time() * 1000) - 3600000,  # 1 hour ago
                "subject": "PDA Task Reminder"
            },
            {
                "notification_id": "whatsapp_987654321",
                "channel": "whatsapp",
                "status": "delivered",
                "sent_at": int(time.time() * 1000) - 7200000,  # 2 hours ago
                "message_preview": "Your meeting starts in 15..."
            }
        ]
        
        return {
            "user_id": user_id,
            "period_days": days,
            "total_notifications": len(mock_history),
            "notifications": mock_history,
            "channel_breakdown": {
                "email": 1,
                "whatsapp": 1
            },
            "success_rate": 100.0,
            "retrieved_at": int(time.time() * 1000)
        }

    def update_notification_preferences(self, user_id: UserID, token_str: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user's notification preferences.
        """
        # Validate consent
        valid, reason, token = validate_token(token_str, expected_scope=self.required_scope)
        
        if not valid:
            raise PermissionError(f"❌ Preference update denied: {reason}")

        print(f"⚙️ Notification Agent updating preferences for user {user_id}")
        
        # Mock preference update - in production, save to database
        updated_preferences = {
            "user_id": user_id,
            "email_enabled": preferences.get("email_enabled", True),
            "whatsapp_enabled": preferences.get("whatsapp_enabled", True),
            "push_enabled": preferences.get("push_enabled", True),
            "quiet_hours": preferences.get("quiet_hours", {"start": "22:00", "end": "08:00"}),
            "preferred_channels": preferences.get("preferred_channels", ["email", "push"]),
            "updated_at": int(time.time() * 1000),
            "agent_id": self.agent_id
        }
        
        print(f"✅ Notification preferences updated for user {user_id}")
        return updated_preferences

    def test_notification_channel(self, user_id: UserID, token_str: str, channel: str) -> Dict[str, Any]:
        """
        Test a notification channel to verify it's working.
        """
        # Validate consent
        valid, reason, token = validate_token(token_str, expected_scope=self.required_scope)
        
        if not valid:
            raise PermissionError(f"❌ Channel test denied: {reason}")

        print(f"🧪 Notification Agent testing {channel} for user {user_id}")
        
        if channel not in self.supported_channels:
            return {"error": f"Unsupported channel: {channel}"}
        
        # Send test notification
        test_notification = {
            "channel": channel,
            "message": f"Test notification from PDA - {int(time.time())}",
            "subject": "PDA Test Notification" if channel == "email" else None
        }
        
        result = self.send_notification(user_id, token_str, test_notification)
        
        if "error" not in result:
            result["test_status"] = "success"
            result["test_message"] = f"{channel.title()} channel is working correctly"
        else:
            result["test_status"] = "failed"
            result["test_message"] = f"{channel.title()} channel test failed"
        
        return result
