# hushh_mcp/operons/task_automator.py

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import uuid
import json


class Task:
    """Represents a task with all its properties."""
    
    def __init__(
        self,
        title: str,
        description: str = "",
        priority: str = "medium",
        due_date: Optional[str] = None,
        category: str = "general",
        status: str = "pending",
        estimated_duration: str = "30m",
        tags: List[str] = None
    ):
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.priority = priority  # low, medium, high, urgent
        self.due_date = due_date
        self.category = category
        self.status = status  # pending, in_progress, completed, cancelled
        self.estimated_duration = estimated_duration
        self.tags = tags or []
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "due_date": self.due_date,
            "category": self.category,
            "status": self.status,
            "estimated_duration": self.estimated_duration,
            "tags": self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


def create_task(
    title: str,
    description: str = "",
    priority: str = "medium",
    due_date: Optional[str] = None,
    category: str = "general",
    tags: List[str] = None
) -> Dict[str, Any]:
    """
    Create a new task with automatic categorization and prioritization.
    
    Args:
        title: Task title
        description: Task description
        priority: Priority level (low, medium, high, urgent)
        due_date: Due date in ISO format
        category: Task category
        tags: List of tags
        
    Returns:
        Dict containing task data
    """
    # Auto-enhance task based on content
    enhanced_priority = _enhance_priority(title, description, priority)
    enhanced_duration = _estimate_task_duration(title, description)
    enhanced_tags = _generate_smart_tags(title, description, tags or [])
    
    # Create task object
    task = Task(
        title=title,
        description=description,
        priority=enhanced_priority,
        due_date=due_date,
        category=category,
        estimated_duration=enhanced_duration,
        tags=enhanced_tags
    )
    
    # Generate automation suggestions
    automations = _generate_task_automations(task)
    
    return {
        "task": task.to_dict(),
        "automations": automations,
        "created_by": "task_automator_operon",
        "smart_enhancements": {
            "priority_enhanced": enhanced_priority != priority,
            "duration_estimated": enhanced_duration,
            "tags_generated": len(enhanced_tags) > len(tags or [])
        }
    }


def update_task(
    task_id: str,
    updates: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Update an existing task with new information.
    
    Args:
        task_id: ID of the task to update
        updates: Dictionary of fields to update
        
    Returns:
        Updated task data
    """
    # In a real implementation, this would fetch from storage
    # For demo purposes, return a mock updated task
    
    updated_task = {
        "id": task_id,
        "title": updates.get("title", "Updated Task"),
        "status": updates.get("status", "in_progress"),
        "updated_at": datetime.now().isoformat(),
        "update_summary": f"Updated {len(updates)} fields"
    }
    
    return {
        "task": updated_task,
        "updated_fields": list(updates.keys()),
        "updated_by": "task_automator_operon"
    }


def create_recurring_task(
    title: str,
    description: str = "",
    recurrence_pattern: str = "weekly",
    priority: str = "medium",
    category: str = "general"
) -> Dict[str, Any]:
    """
    Create a recurring task with automatic scheduling.
    
    Args:
        title: Task title
        description: Task description
        recurrence_pattern: daily, weekly, monthly, yearly
        priority: Priority level
        category: Task category
        
    Returns:
        Recurring task data with schedule
    """
    base_task = create_task(title, description, priority, None, category)
    
    # Generate recurrence schedule
    schedule = _generate_recurrence_schedule(recurrence_pattern)
    
    return {
        "recurring_task": base_task["task"],
        "recurrence_pattern": recurrence_pattern,
        "schedule": schedule,
        "next_occurrence": schedule[0] if schedule else None,
        "created_by": "task_automator_operon"
    }


def break_down_complex_task(
    title: str,
    description: str = "",
    estimated_hours: float = 2.0
) -> Dict[str, Any]:
    """
    Break down a complex task into smaller, manageable subtasks.
    
    Args:
        title: Main task title
        description: Task description
        estimated_hours: Estimated time to complete
        
    Returns:
        Main task with subtasks
    """
    # Generate subtasks based on task analysis
    subtasks = _generate_subtasks(title, description, estimated_hours)
    
    main_task = create_task(
        title=title,
        description=description,
        category="complex",
        tags=["parent-task", "breakdown"]
    )
    
    return {
        "main_task": main_task["task"],
        "subtasks": subtasks,
        "breakdown_strategy": "time-based" if estimated_hours > 2 else "complexity-based",
        "total_subtasks": len(subtasks),
        "estimated_completion": _calculate_completion_time(subtasks)
    }


def get_task_suggestions(
    current_context: str,
    user_history: List[Dict] = None
) -> List[Dict[str, Any]]:
    """
    Generate intelligent task suggestions based on context and history.
    
    Args:
        current_context: Current user context or input
        user_history: Previous user tasks and patterns
        
    Returns:
        List of suggested tasks
    """
    suggestions = []
    
    # Context-based suggestions
    context_suggestions = _analyze_context_for_tasks(current_context)
    suggestions.extend(context_suggestions)
    
    # History-based suggestions
    if user_history:
        history_suggestions = _analyze_history_for_patterns(user_history)
        suggestions.extend(history_suggestions)
    
    return suggestions[:5]  # Return top 5 suggestions


def _enhance_priority(title: str, description: str, original_priority: str) -> str:
    """Enhance priority based on content analysis."""
    text = f"{title} {description}".lower()
    
    urgent_keywords = ["urgent", "asap", "critical", "emergency", "deadline", "due today"]
    high_keywords = ["important", "priority", "soon", "deadline", "meeting"]
    
    if any(keyword in text for keyword in urgent_keywords):
        return "urgent"
    elif any(keyword in text for keyword in high_keywords):
        return "high"
    else:
        return original_priority


def _estimate_task_duration(title: str, description: str) -> str:
    """Estimate task duration based on content."""
    text = f"{title} {description}".lower()
    
    quick_keywords = ["quick", "fast", "brief", "short", "call", "email"]
    long_keywords = ["design", "develop", "research", "analysis", "presentation", "report"]
    
    if any(keyword in text for keyword in quick_keywords):
        return "15m"
    elif any(keyword in text for keyword in long_keywords):
        return "2h"
    else:
        return "30m"


def _generate_smart_tags(title: str, description: str, existing_tags: List[str]) -> List[str]:
    """Generate smart tags based on task content."""
    text = f"{title} {description}".lower()
    smart_tags = existing_tags.copy()
    
    tag_keywords = {
        "meeting": ["meeting", "call", "discussion"],
        "coding": ["code", "develop", "programming", "debug"],
        "communication": ["email", "call", "message", "contact"],
        "creative": ["design", "creative", "brainstorm", "ideate"],
        "research": ["research", "analyze", "study", "investigate"],
        "admin": ["admin", "paperwork", "filing", "organize"]
    }
    
    for tag, keywords in tag_keywords.items():
        if any(keyword in text for keyword in keywords) and tag not in smart_tags:
            smart_tags.append(tag)
    
    return smart_tags


def _generate_task_automations(task: Task) -> List[Dict[str, Any]]:
    """Generate automation suggestions for a task."""
    automations = []
    
    # Calendar integration
    if task.due_date:
        automations.append({
            "type": "calendar_event",
            "action": "schedule_work_time",
            "description": f"Block time for: {task.title}",
            "suggested_duration": task.estimated_duration
        })
    
    # Reminder automation
    if task.priority in ["high", "urgent"]:
        automations.append({
            "type": "reminder",
            "action": "set_reminder",
            "description": f"Reminder for high-priority task: {task.title}",
            "timing": "1 hour before due date"
        })
    
    # Dependency tracking
    if "meeting" in task.tags:
        automations.append({
            "type": "dependency",
            "action": "check_attendee_availability",
            "description": "Verify all attendees are available"
        })
    
    return automations


def _generate_recurrence_schedule(pattern: str) -> List[str]:
    """Generate upcoming dates for recurring tasks."""
    now = datetime.now()
    schedule = []
    
    if pattern == "daily":
        for i in range(7):  # Next 7 days
            date = now + timedelta(days=i)
            schedule.append(date.isoformat())
    elif pattern == "weekly":
        for i in range(4):  # Next 4 weeks
            date = now + timedelta(weeks=i)
            schedule.append(date.isoformat())
    elif pattern == "monthly":
        for i in range(3):  # Next 3 months
            date = now + timedelta(days=30*i)
            schedule.append(date.isoformat())
    
    return schedule


def _generate_subtasks(title: str, description: str, estimated_hours: float) -> List[Dict]:
    """Generate subtasks for complex tasks."""
    subtasks = []
    
    # Generic subtask breakdown
    if estimated_hours > 2:
        subtasks = [
            {"title": f"Plan and research for: {title}", "duration": "30m"},
            {"title": f"Execute main work: {title}", "duration": f"{estimated_hours-1}h"},
            {"title": f"Review and finalize: {title}", "duration": "30m"}
        ]
    else:
        subtasks = [
            {"title": f"Prepare: {title}", "duration": "15m"},
            {"title": f"Complete: {title}", "duration": f"{estimated_hours-0.25}h"}
        ]
    
    return subtasks


def _calculate_completion_time(subtasks: List[Dict]) -> str:
    """Calculate estimated completion time for all subtasks."""
    # Simple calculation - in real implementation would be more sophisticated
    total_minutes = len(subtasks) * 30  # Assume 30min average per subtask
    hours = total_minutes // 60
    minutes = total_minutes % 60
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"


def _analyze_context_for_tasks(context: str) -> List[Dict[str, Any]]:
    """Analyze current context to suggest relevant tasks."""
    suggestions = []
    context_lower = context.lower()
    
    if "meeting" in context_lower:
        suggestions.append({
            "title": "Prepare for meeting",
            "description": "Review agenda and prepare materials",
            "priority": "medium",
            "category": "work"
        })
    
    if "email" in context_lower:
        suggestions.append({
            "title": "Process inbox",
            "description": "Review and respond to important emails",
            "priority": "low",
            "category": "communication"
        })
    
    return suggestions


def _analyze_history_for_patterns(history: List[Dict]) -> List[Dict[str, Any]]:
    """Analyze user history to suggest recurring or similar tasks."""
    # Simple pattern analysis - in real implementation would use ML
    suggestions = []
    
    # Look for recurring patterns
    if len(history) > 5:
        suggestions.append({
            "title": "Weekly planning session",
            "description": "Review and plan upcoming tasks",
            "priority": "medium",
            "category": "planning",
            "reason": "Based on your regular task creation pattern"
        })
    
    return suggestions
