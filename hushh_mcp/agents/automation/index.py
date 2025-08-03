# hushh_mcp/agents/automation/index.py

from typing import Dict, List, Any, Optional
from hushh_mcp.consent.token import validate_token
from hushh_mcp.constants import ConsentScope
from hushh_mcp.types import UserID
from hushh_mcp.operons.schedule_event import create_calendar_event
from hushh_mcp.operons.create_note import generate_structured_note
from hushh_mcp.operons.manage_todos import create_todo_item, update_todo_status
import time


class AutomationAgent:
    """
    Specialized agent for automation stack operations.
    Handles event scheduling, note creation, and to-do list management.
    """

    def __init__(self, agent_id: str = "agent_automation"):
        self.agent_id = agent_id
        self.required_scope = ConsentScope.CUSTOM_SESSION_WRITE

    def create_event(self, user_id: UserID, token_str: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a calendar event with consent validation.
        
        Args:
            user_id: User requesting event creation
            token_str: Valid consent token
            event_data: Event details (title, datetime, duration, etc.)
            
        Returns:
            Dict with event creation results
        """
        # Validate consent
        valid, reason, token = validate_token(token_str, expected_scope=self.required_scope)
        
        if not valid:
            raise PermissionError(f"❌ Event creation denied: {reason}")
        
        if token.user_id != user_id:
            raise PermissionError("❌ Token user mismatch")

        print(f"📅 Automation Agent creating event for user {user_id}")
        
        # Validate event data
        required_fields = ["title", "start_time"]
        missing_fields = [field for field in required_fields if field not in event_data]
        
        if missing_fields:
            return {"error": f"Missing required fields: {missing_fields}"}

        try:
            # Use scheduling operon
            event_result = create_calendar_event(
                title=event_data["title"],
                start_time=event_data["start_time"],
                end_time=event_data.get("end_time"),
                description=event_data.get("description", ""),
                location=event_data.get("location", ""),
                attendees=event_data.get("attendees", [])
            )
            
            result = {
                "event_id": event_result["event_id"],
                "title": event_data["title"],
                "start_time": event_data["start_time"],
                "status": "created",
                "created_at": int(time.time() * 1000),
                "agent_id": self.agent_id,
                "automation_type": "event_scheduling"
            }
            
            print(f"✅ Event created: {event_data['title']}")
            return result
            
        except Exception as e:
            print(f"❌ Event creation failed: {str(e)}")
            return {"error": f"Event creation failed: {str(e)}"}

    def create_note(self, user_id: UserID, token_str: str, note_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a structured note with consent validation.
        """
        # Validate consent
        valid, reason, token = validate_token(token_str, expected_scope=self.required_scope)
        
        if not valid:
            raise PermissionError(f"❌ Note creation denied: {reason}")

        print(f"📝 Automation Agent creating note for user {user_id}")
        
        # Validate note data
        if "content" not in note_data:
            return {"error": "Note content is required"}

        try:
            # Use note creation operon
            note_result = generate_structured_note(
                content=note_data["content"],
                title=note_data.get("title", ""),
                tags=note_data.get("tags", []),
                category=note_data.get("category", "general")
            )
            
            result = {
                "note_id": note_result["note_id"],
                "title": note_result["title"],
                "content_preview": note_data["content"][:100] + "..." if len(note_data["content"]) > 100 else note_data["content"],
                "tags": note_result["tags"],
                "category": note_result["category"],
                "status": "created",
                "created_at": int(time.time() * 1000),
                "agent_id": self.agent_id,
                "automation_type": "note_creation"
            }
            
            print(f"✅ Note created: {note_result['title']}")
            return result
            
        except Exception as e:
            print(f"❌ Note creation failed: {str(e)}")
            return {"error": f"Note creation failed: {str(e)}"}

    def create_todo(self, user_id: UserID, token_str: str, todo_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a todo item with consent validation.
        """
        # Validate consent
        valid, reason, token = validate_token(token_str, expected_scope=self.required_scope)
        
        if not valid:
            raise PermissionError(f"❌ Todo creation denied: {reason}")

        print(f"✅ Automation Agent creating todo for user {user_id}")
        
        # Validate todo data
        if "task" not in todo_data:
            return {"error": "Task description is required"}

        try:
            # Use todo management operon
            todo_result = create_todo_item(
                task=todo_data["task"],
                priority=todo_data.get("priority", "medium"),
                due_date=todo_data.get("due_date"),
                category=todo_data.get("category", "general"),
                tags=todo_data.get("tags", [])
            )
            
            result = {
                "todo_id": todo_result["todo_id"],
                "task": todo_data["task"],
                "priority": todo_result["priority"],
                "due_date": todo_result.get("due_date"),
                "category": todo_result["category"],
                "status": "pending",
                "created_at": int(time.time() * 1000),
                "agent_id": self.agent_id,
                "automation_type": "todo_creation"
            }
            
            print(f"✅ Todo created: {todo_data['task']}")
            return result
            
        except Exception as e:
            print(f"❌ Todo creation failed: {str(e)}")
            return {"error": f"Todo creation failed: {str(e)}"}

    def update_todo_status(self, user_id: UserID, token_str: str, todo_id: str, new_status: str) -> Dict[str, Any]:
        """
        Update todo item status.
        """
        # Validate consent
        valid, reason, token = validate_token(token_str, expected_scope=self.required_scope)
        
        if not valid:
            raise PermissionError(f"❌ Todo update denied: {reason}")

        print(f"🔄 Automation Agent updating todo {todo_id} for user {user_id}")
        
        try:
            # Use todo management operon
            update_result = update_todo_status(todo_id, new_status)
            
            result = {
                "todo_id": todo_id,
                "old_status": update_result.get("old_status"),
                "new_status": new_status,
                "updated_at": int(time.time() * 1000),
                "agent_id": self.agent_id,
                "automation_type": "todo_update"
            }
            
            print(f"✅ Todo {todo_id} status updated to: {new_status}")
            return result
            
        except Exception as e:
            print(f"❌ Todo update failed: {str(e)}")
            return {"error": f"Todo update failed: {str(e)}"}

    def get_automation_summary(self, user_id: UserID, token_str: str, days: int = 7) -> Dict[str, Any]:
        """
        Get summary of automation activities for the user.
        """
        # Validate consent
        valid, reason, token = validate_token(token_str, expected_scope=ConsentScope.CUSTOM_TEMPORARY)
        
        if not valid:
            raise PermissionError(f"❌ Summary access denied: {reason}")

        print(f"📊 Generating automation summary for user {user_id}")
        
        # This would typically query a database or log files
        # For now, return a mock summary
        return {
            "user_id": user_id,
            "period_days": days,
            "events_created": 5,
            "notes_created": 12,
            "todos_created": 8,
            "todos_completed": 3,
            "most_active_day": "Monday",
            "top_categories": ["work", "personal", "health"],
            "agent_id": self.agent_id,
            "generated_at": int(time.time() * 1000)
        }
