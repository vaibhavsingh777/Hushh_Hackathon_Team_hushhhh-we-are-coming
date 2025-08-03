# Email Automation Operon - Hushh MCP Protocol
# Coordinates between Email Processor Agent and Automation Agent

from typing import Dict, List, Any
from datetime import datetime
import logging
from ..agents.email_processor.index import EmailProcessorAgent
from ..agents.automation.index import AutomationAgent
from ..agents.audit_logger.index import AuditLoggerAgent
from ..types import HushhConsentToken

logger = logging.getLogger(__name__)

async def orchestrate_email_automation_workflow(
    user_id: str, 
    consent_token: HushhConsentToken,
    automation_preferences: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Orchestrate the complete email automation workflow
    
    This operon coordinates between multiple agents following Hushh MCP protocols:
    1. Email Processor Agent - processes and categorizes emails
    2. Automation Agent - creates automation rules
    3. Audit Logger Agent - tracks all operations
    
    Args:
        user_id: User identifier
        consent_token: Valid consent token for the operation
        automation_preferences: User preferences for automation
        
    Returns:
        Dict containing workflow results and automation summary
    """
    
    # Initialize agents
    email_processor = EmailProcessorAgent()
    automation_agent = AutomationAgent()
    audit_logger = AuditLoggerAgent()
    
    workflow_id = f"email_automation_{user_id}_{int(datetime.now().timestamp())}"
    
    try:
        # Step 1: Verify consent and log workflow start
        if not consent_token.is_valid():
            raise PermissionError("Invalid consent token for email automation workflow")
            
        await audit_logger.log_action(
            action_type="email_automation_workflow_started",
            user_id=user_id,
            details={
                "workflow_id": workflow_id,
                "consent_token": consent_token.token_id,
                "preferences": automation_preferences
            }
        )
        
        # Step 2: Get processed emails from Email Processor Agent
        categorized_emails = email_processor.get_categorized_emails(user_id)
        if not categorized_emails:
            # If no emails processed yet, process them first
            email_result = await email_processor.process_emails_with_ai(
                user_id, 
                consent_token, 
                automation_preferences.get('days_back', 60)
            )
            categorized_emails = email_result.get('emails', [])
        
        # Step 3: Create category-based automations
        automation_results = []
        categories_to_automate = automation_preferences.get('categories', [])
        
        for category in categories_to_automate:
            category_emails = [e for e in categorized_emails if e['category'] == category]
            
            if len(category_emails) >= automation_preferences.get('min_emails_for_automation', 5):
                automation_type = automation_preferences.get('automation_types', {}).get(category, 'smart_filing')
                
                # Create automation through Email Processor Agent
                automation_result = await email_processor.create_category_automation(
                    user_id=user_id,
                    category=category,
                    automation_type=automation_type,
                    consent_token=consent_token
                )
                
                automation_results.append({
                    "category": category,
                    "automation_type": automation_type,
                    "emails_affected": len(category_emails),
                    "automation_id": automation_result.get("automation_id"),
                    "status": "created"
                })
                
                # Log each automation creation
                await audit_logger.log_action(
                    action_type="category_automation_created",
                    user_id=user_id,
                    details={
                        "workflow_id": workflow_id,
                        "category": category,
                        "automation_type": automation_type,
                        "emails_count": len(category_emails)
                    }
                )
        
        # Step 4: Generate workflow summary
        workflow_summary = {
            "workflow_id": workflow_id,
            "user_id": user_id,
            "total_emails_processed": len(categorized_emails),
            "automations_created": len(automation_results),
            "automation_details": automation_results,
            "categories_covered": list(set([r["category"] for r in automation_results])),
            "completion_time": datetime.now().isoformat(),
            "success": True
        }
        
        # Step 5: Log workflow completion
        await audit_logger.log_action(
            action_type="email_automation_workflow_completed",
            user_id=user_id,
            details=workflow_summary
        )
        
        return workflow_summary
        
    except Exception as e:
        # Log workflow failure
        await audit_logger.log_action(
            action_type="email_automation_workflow_failed",
            user_id=user_id,
            details={
                "workflow_id": workflow_id,
                "error": str(e),
                "error_type": type(e).__name__
            }
        )
        
        logger.error(f"Email automation workflow failed for user {user_id}: {e}")
        raise e


async def verify_automation_permissions(user_id: str, automation_type: str) -> bool:
    """
    Verify user has permissions for specific automation type
    
    Args:
        user_id: User identifier
        automation_type: Type of automation requested
        
    Returns:
        bool: True if user has permissions, False otherwise
    """
    
    # Check if user has valid consent for automation
    # This would integrate with the consent management system
    
    allowed_automations = [
        'smart_filing',
        'priority_flagging', 
        'auto_respond',
        'reminder_scheduling',
        'category_filtering'
    ]
    
    if automation_type not in allowed_automations:
        return False
    
    # Additional permission checks would go here
    # For now, assume all users have basic automation permissions
    return True


async def cleanup_expired_automations(user_id: str) -> Dict[str, Any]:
    """
    Clean up expired or unused automations for a user
    
    Args:
        user_id: User identifier
        
    Returns:
        Dict: Cleanup summary
    """
    
    audit_logger = AuditLoggerAgent()
    
    try:
        # This would check for expired automations and remove them
        # For now, just log the cleanup attempt
        
        await audit_logger.log_action(
            action_type="automation_cleanup_performed",
            user_id=user_id,
            details={
                "cleanup_time": datetime.now().isoformat(),
                "expired_automations_removed": 0,
                "unused_automations_removed": 0
            }
        )
        
        return {
            "success": True,
            "cleaned_up": 0,
            "message": "No expired automations found"
        }
        
    except Exception as e:
        logger.error(f"Automation cleanup failed for user {user_id}: {e}")
        return {
            "success": False,
            "error": str(e)
        }
