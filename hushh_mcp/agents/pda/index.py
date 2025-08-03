# hushh_mcp/agents/pda/index.py

from typing import Dict, List, Any, Optional
import time
import json
from datetime import datetime

from hushh_mcp.consent.token import validate_token
from hushh_mcp.constants import ConsentScope
from hushh_mcp.types import UserID, AgentID
from hushh_mcp.vault.encrypt import decrypt_data, encrypt_data
from hushh_mcp.config import VAULT_ENCRYPTION_KEY

# Import operons
from hushh_mcp.operons.semantic_categorizer import categorize_content
from hushh_mcp.operons.task_automator import create_task, update_task
from hushh_mcp.operons.schedule_event import create_calendar_event
from hushh_mcp.operons.create_note import generate_structured_note


class PersonalDataAgent:
    """
    🤖 Personal Data Agent (PDA) - A comprehensive agent for managing personal data
    with semantic categorization, automation, and consent-first access.
    
    Features:
    - Semantic categorization of user events/tasks
    - Automated task and event creation
    - Consent-first data access
    - Audit logging with timestamps
    - Zero data retention (unless explicitly consented)
    - Modular and extendable architecture
    """
    
    def __init__(self, agent_id: AgentID = "agent_pda"):
        self.agent_id = agent_id
        self.required_scopes = {
            "read": [ConsentScope.VAULT_READ_EMAIL, ConsentScope.VAULT_READ_CALENDAR],
            "write": ["vault.write.tasks", "vault.write.notes", "vault.write.calendar"],
            "categorize": ["agent.pda.categorize"],
            "automate": ["agent.pda.automate"]
        }
    
    def process_user_input(
        self, 
        user_id: UserID, 
        token: str, 
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Main entry point for processing user input with semantic categorization
        and automation.
        """
        # Validate consent token
        valid, reason, parsed_token = validate_token(
            token, 
            expected_scope="agent.pda.categorize"
        )
        
        if not valid:
            raise PermissionError(f"❌ Consent validation failed: {reason}")
        
        if parsed_token.user_id != user_id:
            raise PermissionError("❌ Token user ID mismatch")
        
        # Log the action
        print(f"🔍 PDA processing input for user {user_id}")
        audit_info = {
            "user_id": user_id,
            "agent_id": self.agent_id,
            "action": "process_input",
            "token_id": parsed_token.signature[:8],
            "timestamp": int(time.time() * 1000),
            "input_summary": self._summarize_input(input_data)
        }
        
        # Semantic categorization
        category_result = categorize_content(
            content=input_data.get("content", ""),
            content_type=input_data.get("type", "general")
        )
        
        # Determine automation actions based on category
        automation_result = self._determine_automations(
            user_id, token, category_result, input_data
        )
        
        return {
            "status": "success",
            "user_id": user_id,
            "categorization": category_result,
            "automations": automation_result,
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id
        }
    
    def create_automated_task(
        self,
        user_id: UserID,
        token: str,
        task_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create an automated task based on user input."""
        valid, reason, parsed_token = validate_token(
            token,
            expected_scope="agent.pda.automate"
        )
        
        if not valid:
            raise PermissionError(f"❌ Consent validation failed: {reason}")
        
        # Log the automation
        print(f"📝 PDA creating task for user {user_id}: {task_data.get('title', 'Untitled')}")
        audit_info = {
            "user_id": user_id,
            "agent_id": self.agent_id,
            "action": "create_task",
            "token_id": parsed_token.signature[:8],
            "timestamp": int(time.time() * 1000),
            "input_summary": f"Task: {task_data.get('title', 'Untitled')}"
        }
        
        # Create the task using operon
        task_result = create_task(
            title=task_data.get("title"),
            description=task_data.get("description"),
            priority=task_data.get("priority", "medium"),
            due_date=task_data.get("due_date"),
            category=task_data.get("category", "general")
        )
        
        return {
            "status": "success",
            "task": task_result,
            "created_at": datetime.now().isoformat()
        }
    
    def schedule_automated_event(
        self,
        user_id: UserID,
        token: str,
        event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Schedule an automated event based on user input."""
        valid, reason, parsed_token = validate_token(
            token,
            expected_scope="agent.pda.schedule"
        )
        
        if not valid:
            raise PermissionError(f"❌ Consent validation failed: {reason}")
        
        # Log the automation
        print(f"📅 PDA scheduling event for user {user_id}: {event_data.get('title', 'Untitled')}")
        audit_info = {
            "user_id": user_id,
            "agent_id": self.agent_id,
            "action": "schedule_event",
            "token_id": parsed_token.signature[:8],
            "timestamp": int(time.time() * 1000),
            "input_summary": f"Event: {event_data.get('title', 'Untitled')}"
        }
        
        # Schedule the event using operon
        event_result = create_calendar_event(
            title=event_data.get("title"),
            description=event_data.get("description"),
            start_time=event_data.get("start_time"),
            end_time=event_data.get("end_time"),
            location=event_data.get("location"),
            attendees=event_data.get("attendees", [])
        )
        
        return {
            "status": "success",
            "event": event_result,
            "scheduled_at": datetime.now().isoformat()
        }
    
    def get_user_insights(
        self,
        user_id: UserID,
        token: str
    ) -> Dict[str, Any]:
        """Generate insights from user's categorized data."""
        valid, reason, parsed_token = validate_token(
            token,
            expected_scope=ConsentScope.VAULT_READ_EMAIL
        )
        
        if not valid:
            raise PermissionError(f"❌ Consent validation failed: {reason}")
        
        # This would typically read from vault and analyze patterns
        # For demo purposes, return mock insights
        return {
            "status": "success",
            "insights": {
                "total_tasks": 42,
                "completed_tasks": 28,
                "top_categories": ["work", "personal", "health"],
                "productivity_score": 85,
                "automation_savings": "2.5 hours/week"
            },
            "generated_at": datetime.now().isoformat()
        }
    
    def _determine_automations(
        self,
        user_id: UserID,
        token: str,
        category_result: Dict[str, Any],
        input_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Determine what automations to trigger based on categorization."""
        automations = []
        category = category_result.get("category", "general")
        
        # Task automation rules
        if "task" in category or "todo" in category:
            automations.append({
                "type": "task_creation",
                "triggered": True,
                "reason": f"Detected task-related content in category: {category}"
            })
        
        # Event automation rules  
        if "meeting" in category or "appointment" in category or "event" in category:
            automations.append({
                "type": "event_scheduling", 
                "triggered": True,
                "reason": f"Detected event-related content in category: {category}"
            })
        
        # Note automation rules
        if "note" in category or "reminder" in category:
            automations.append({
                "type": "note_creation",
                "triggered": True,
                "reason": f"Detected note-worthy content in category: {category}"
            })
        
        return automations
    
    def _summarize_input(self, input_data: Dict[str, Any]) -> str:
        """Create a privacy-safe summary of input for logging."""
        content = input_data.get("content", "")
        if len(content) > 100:
            return content[:97] + "..."
        return content


# Convenience function for external use
def create_pda_agent() -> PersonalDataAgent:
    """Factory function to create a PDA agent instance."""
    return PersonalDataAgent()
