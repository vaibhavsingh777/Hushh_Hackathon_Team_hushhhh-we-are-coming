# hushh_mcp/agents/pda_orchestrator/index.py

from typing import Dict, List, Any, Optional
from hushh_mcp.consent.token import validate_token
from hushh_mcp.trust.link import create_trust_link, verify_trust_link
from hushh_mcp.constants import ConsentScope
from hushh_mcp.types import UserID, AgentID, TrustLink
import time


class PDAOrchestratorAgent:
    """
    Main PDA orchestrator that coordinates specialized agents.
    Follows bacteria-like modular architecture principles.
    """

    def __init__(self, agent_id: str = "agent_pda_orchestrator"):
        self.agent_id = agent_id
        self.required_scopes = [
            ConsentScope.VAULT_READ_EMAIL,
            ConsentScope.AGENT_IDENTITY_VERIFY,
            ConsentScope.CUSTOM_TEMPORARY
        ]
        
        # Registry of specialized agents
        self.specialized_agents = {
            "semantic_categorizer": "agent_semantic_categorizer",
            "automation": "agent_automation",
            "audit_logger": "agent_audit_logger", 
            "data_manager": "agent_data_manager",
            "notification": "agent_notification",
            "file_parser": "agent_file_parser"
        }

    def handle_request(self, user_id: UserID, token_str: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for PDA requests.
        Validates consent and delegates to appropriate specialized agents.
        """
        # Validate master consent token
        valid, reason, token = validate_token(token_str, expected_scope=ConsentScope.CUSTOM_TEMPORARY)
        
        if not valid:
            raise PermissionError(f"❌ Invalid consent token: {reason}")
        
        if token.user_id != user_id:
            raise PermissionError("❌ Token user mismatch")

        print(f"✅ PDA Orchestrator authorized for user {user_id}")
        print(f"🎯 Processing task: {task.get('type', 'unknown')}")

        # Route to appropriate specialized agent
        task_type = task.get("type")
        result = self._route_task(user_id, token_str, task_type, task)
        
        # Log the orchestration
        self._log_orchestration(user_id, token.signature[:8], task_type, result)
        
        return result

    def _route_task(self, user_id: UserID, token_str: str, task_type: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Route tasks to specialized agents based on type."""
        
        routing_map = {
            "categorize": self._delegate_to_categorizer,
            "schedule": self._delegate_to_automation,
            "note": self._delegate_to_automation,
            "todo": self._delegate_to_automation,
            "parse_file": self._delegate_to_file_parser,
            "send_notification": self._delegate_to_notification,
            "vault_operation": self._delegate_to_data_manager
        }
        
        handler = routing_map.get(task_type)
        if not handler:
            return {"error": f"Unknown task type: {task_type}"}
        
        return handler(user_id, token_str, task)

    def _delegate_to_categorizer(self, user_id: UserID, token_str: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate semantic categorization tasks."""
        from hushh_mcp.agents.semantic_categorizer.index import SemanticCategorizerAgent
        
        categorizer = SemanticCategorizerAgent()
        return categorizer.categorize_content(user_id, token_str, task.get("content", ""))

    def _delegate_to_automation(self, user_id: UserID, token_str: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate automation tasks (schedule, notes, todos)."""
        from hushh_mcp.agents.automation.index import AutomationAgent
        
        automation = AutomationAgent()
        task_type = task.get("type")
        
        if task_type == "schedule":
            return automation.create_event(user_id, token_str, task.get("event_data"))
        elif task_type == "note":
            return automation.create_note(user_id, token_str, task.get("note_data"))
        elif task_type == "todo":
            return automation.create_todo(user_id, token_str, task.get("todo_data"))
        
        return {"error": "Unknown automation task"}

    def _delegate_to_file_parser(self, user_id: UserID, token_str: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate file parsing tasks."""
        from hushh_mcp.agents.file_parser.index import FileParserAgent
        
        parser = FileParserAgent()
        return parser.parse_file(user_id, token_str, task.get("file_path"), task.get("file_type"))

    def _delegate_to_notification(self, user_id: UserID, token_str: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate notification tasks."""
        from hushh_mcp.agents.notification.index import NotificationAgent
        
        notifier = NotificationAgent()
        return notifier.send_notification(user_id, token_str, task.get("notification_data"))

    def _delegate_to_data_manager(self, user_id: UserID, token_str: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate vault operations."""
        from hushh_mcp.agents.data_manager.index import DataManagerAgent
        
        data_manager = DataManagerAgent()
        operation = task.get("operation")
        
        if operation == "store":
            return data_manager.store_data(user_id, token_str, task.get("data"), task.get("scope"))
        elif operation == "retrieve":
            return data_manager.retrieve_data(user_id, token_str, task.get("scope"))
        elif operation == "delete":
            return data_manager.delete_data(user_id, token_str, task.get("scope"))
        
        return {"error": "Unknown vault operation"}

    def _log_orchestration(self, user_id: UserID, token_id: str, task_type: str, result: Dict[str, Any]):
        """Log orchestration activity for audit trail."""
        from hushh_mcp.agents.audit_logger.index import AuditLoggerAgent
        
        logger = AuditLoggerAgent()
        log_entry = {
            "timestamp": int(time.time() * 1000),
            "user_id": user_id,
            "token_id": token_id,
            "agent_id": self.agent_id,
            "task_type": task_type,
            "status": "success" if "error" not in result else "error",
            "result_summary": str(result)[:200]  # Truncated summary
        }
        
        logger.log_activity(log_entry)

    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all specialized agents."""
        return {
            "orchestrator_id": self.agent_id,
            "specialized_agents": self.specialized_agents,
            "status": "active",
            "capabilities": [
                "semantic_categorization",
                "automation_stack", 
                "file_parsing",
                "notification_system",
                "vault_management",
                "audit_logging"
            ]
        }
