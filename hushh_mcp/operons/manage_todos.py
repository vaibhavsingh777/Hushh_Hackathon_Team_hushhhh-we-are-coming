# hushh_mcp/operons/manage_todos.py

from typing import Dict, Any, List, Optional
import uuid
import time
import json
from datetime import datetime, timedelta
from enum import Enum


class TodoStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class TodoPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


def create_todo_item(
    task: str,
    priority: str = "medium",
    due_date: Optional[str] = None,
    category: str = "general",
    tags: List[str] = None,
    description: str = ""
) -> Dict[str, Any]:
    """
    Create a new todo item with the provided details.
    
    Args:
        task: Main task description
        priority: Task priority level
        due_date: Due date (ISO format or readable format)
        category: Task category
        tags: List of tags
        description: Additional task description
        
    Returns:
        Dict with todo item data
    """
    if tags is None:
        tags = []
    
    # Generate unique todo ID
    todo_id = f"todo_{uuid.uuid4().hex[:8]}"
    
    # Validate and parse priority
    try:
        priority_enum = TodoPriority(priority.lower())
    except ValueError:
        priority_enum = TodoPriority.MEDIUM
    
    # Parse due date if provided
    parsed_due_date = None
    if due_date:
        parsed_due_date = parse_due_date(due_date)
    
    # Auto-generate tags from task content
    auto_tags = extract_todo_tags(task + " " + description)
    all_tags = list(set(tags + auto_tags))
    
    # Estimate effort and complexity
    effort_estimate = estimate_task_effort(task, description)
    
    # Create todo object
    todo = {
        "todo_id": todo_id,
        "task": task,
        "description": description,
        "status": TodoStatus.PENDING.value,
        "priority": priority_enum.value,
        "category": category,
        "tags": all_tags,
        "due_date": parsed_due_date.isoformat() if parsed_due_date else None,
        "created_at": int(time.time() * 1000),
        "updated_at": int(time.time() * 1000),
        "completed_at": None,
        "estimated_duration": effort_estimate["duration_minutes"],
        "complexity": effort_estimate["complexity"],
        "subtasks": [],
        "dependencies": [],
        "assignee": None,
        "progress_percentage": 0,
        "notes": [],
        "attachments": []
    }
    
    # Store todo
    store_todo(todo)
    
    print(f"✅ Todo created: {task} (Priority: {priority_enum.value})")
    return todo


def update_todo_status(todo_id: str, new_status: str) -> Dict[str, Any]:
    """
    Update the status of a todo item.
    
    Args:
        todo_id: ID of the todo to update
        new_status: New status value
        
    Returns:
        Dict with update results
    """
    # Validate status
    try:
        status_enum = TodoStatus(new_status.lower())
    except ValueError:
        raise ValueError(f"Invalid status: {new_status}")
    
    # Retrieve existing todo (simulated)
    existing_todo = get_todo_by_id(todo_id)
    if not existing_todo:
        raise ValueError(f"Todo not found: {todo_id}")
    
    old_status = existing_todo.get("status", "unknown")
    
    # Update todo
    existing_todo["status"] = status_enum.value
    existing_todo["updated_at"] = int(time.time() * 1000)
    
    # Set completion time if marking as completed
    if status_enum == TodoStatus.COMPLETED:
        existing_todo["completed_at"] = int(time.time() * 1000)
        existing_todo["progress_percentage"] = 100
    elif status_enum == TodoStatus.IN_PROGRESS:
        existing_todo["progress_percentage"] = 50
    
    # Store updated todo
    store_todo(existing_todo)
    
    result = {
        "todo_id": todo_id,
        "old_status": old_status,
        "new_status": status_enum.value,
        "updated_at": existing_todo["updated_at"]
    }
    
    print(f"🔄 Todo status updated: {todo_id} ({old_status} → {status_enum.value})")
    return result


def add_subtask(todo_id: str, subtask: str) -> Dict[str, Any]:
    """
    Add a subtask to an existing todo.
    """
    # Retrieve existing todo
    existing_todo = get_todo_by_id(todo_id)
    if not existing_todo:
        raise ValueError(f"Todo not found: {todo_id}")
    
    # Create subtask
    subtask_id = f"subtask_{uuid.uuid4().hex[:6]}"
    subtask_obj = {
        "subtask_id": subtask_id,
        "task": subtask,
        "status": TodoStatus.PENDING.value,
        "created_at": int(time.time() * 1000),
        "completed_at": None
    }
    
    # Add to todo
    existing_todo["subtasks"].append(subtask_obj)
    existing_todo["updated_at"] = int(time.time() * 1000)
    
    # Store updated todo
    store_todo(existing_todo)
    
    print(f"➕ Subtask added to {todo_id}: {subtask}")
    return subtask_obj


def update_todo_progress(todo_id: str, progress_percentage: int) -> Dict[str, Any]:
    """
    Update the progress percentage of a todo.
    """
    if not 0 <= progress_percentage <= 100:
        raise ValueError("Progress percentage must be between 0 and 100")
    
    # Retrieve existing todo
    existing_todo = get_todo_by_id(todo_id)
    if not existing_todo:
        raise ValueError(f"Todo not found: {todo_id}")
    
    old_progress = existing_todo.get("progress_percentage", 0)
    existing_todo["progress_percentage"] = progress_percentage
    existing_todo["updated_at"] = int(time.time() * 1000)
    
    # Auto-update status based on progress
    if progress_percentage == 0:
        existing_todo["status"] = TodoStatus.PENDING.value
    elif progress_percentage == 100:
        existing_todo["status"] = TodoStatus.COMPLETED.value
        existing_todo["completed_at"] = int(time.time() * 1000)
    elif progress_percentage > 0:
        existing_todo["status"] = TodoStatus.IN_PROGRESS.value
    
    # Store updated todo
    store_todo(existing_todo)
    
    result = {
        "todo_id": todo_id,
        "old_progress": old_progress,
        "new_progress": progress_percentage,
        "status": existing_todo["status"]
    }
    
    print(f"📊 Todo progress updated: {todo_id} ({old_progress}% → {progress_percentage}%)")
    return result


def parse_due_date(date_str: str) -> Optional[datetime]:
    """
    Parse various due date formats.
    """
    now = datetime.now()
    date_str_lower = date_str.lower().strip()
    
    # Handle relative dates
    if date_str_lower in ["today"]:
        return now.replace(hour=23, minute=59, second=59, microsecond=0)
    elif date_str_lower in ["tomorrow"]:
        return (now + timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=0)
    elif date_str_lower in ["this week", "end of week"]:
        days_until_sunday = 6 - now.weekday()
        return (now + timedelta(days=days_until_sunday)).replace(hour=23, minute=59, second=59, microsecond=0)
    elif date_str_lower in ["next week"]:
        days_until_next_sunday = 13 - now.weekday()
        return (now + timedelta(days=days_until_next_sunday)).replace(hour=23, minute=59, second=59, microsecond=0)
    elif date_str_lower in ["this month", "end of month"]:
        import calendar
        last_day = calendar.monthrange(now.year, now.month)[1]
        return now.replace(day=last_day, hour=23, minute=59, second=59, microsecond=0)
    
    # Handle specific date formats
    formats_to_try = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%Y-%m-%d %H:%M",
        "%m/%d/%Y %H:%M"
    ]
    
    for fmt in formats_to_try:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None


def extract_todo_tags(text: str) -> List[str]:
    """
    Extract tags from todo text content.
    """
    tags = []
    text_lower = text.lower()
    
    # Priority-based tags
    if any(word in text_lower for word in ["urgent", "asap", "emergency"]):
        tags.append("urgent")
    
    # Category-based tags
    category_keywords = {
        "work": ["work", "office", "meeting", "project", "client"],
        "personal": ["personal", "family", "friend", "home"],
        "health": ["health", "doctor", "exercise", "gym", "medical"],
        "finance": ["pay", "bill", "money", "bank", "budget"],
        "shopping": ["buy", "purchase", "shop", "order"],
        "learning": ["learn", "study", "read", "course", "research"],
        "communication": ["call", "email", "message", "contact"],
        "maintenance": ["fix", "repair", "clean", "maintain", "update"]
    }
    
    for category, keywords in category_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            tags.append(category)
    
    # Time-based tags
    if any(word in text_lower for word in ["daily", "routine", "habit"]):
        tags.append("recurring")
    
    return list(set(tags))


def estimate_task_effort(task: str, description: str = "") -> Dict[str, Any]:
    """
    Estimate the effort required for a task.
    """
    combined_text = (task + " " + description).lower()
    
    # Simple heuristics for effort estimation
    complexity_keywords = {
        "simple": ["simple", "quick", "easy", "small", "minor"],
        "medium": ["medium", "moderate", "normal", "standard"],
        "complex": ["complex", "difficult", "major", "large", "comprehensive"]
    }
    
    # Duration keywords
    duration_keywords = {
        15: ["quick", "fast", "brief", "short"],
        30: ["small", "minor", "simple"],
        60: ["medium", "normal", "standard"],
        120: ["large", "big", "major"],
        240: ["complex", "comprehensive", "detailed"]
    }
    
    # Determine complexity
    complexity = "medium"  # default
    for comp_level, keywords in complexity_keywords.items():
        if any(keyword in combined_text for keyword in keywords):
            complexity = comp_level
            break
    
    # Determine duration
    duration_minutes = 60  # default
    for duration, keywords in duration_keywords.items():
        if any(keyword in combined_text for keyword in keywords):
            duration_minutes = duration
            break
    
    # Adjust based on word count
    word_count = len(combined_text.split())
    if word_count > 20:
        duration_minutes = min(duration_minutes * 1.5, 480)  # max 8 hours
        complexity = "complex"
    elif word_count < 5:
        duration_minutes = max(duration_minutes * 0.5, 15)  # min 15 minutes
        complexity = "simple"
    
    return {
        "duration_minutes": int(duration_minutes),
        "complexity": complexity,
        "confidence": 0.7  # estimation confidence
    }


def get_todos_by_category(category: str) -> List[Dict[str, Any]]:
    """
    Get all todos in a specific category.
    """
    # Placeholder - in production, query from database
    return []


def get_todos_by_status(status: str) -> List[Dict[str, Any]]:
    """
    Get all todos with a specific status.
    """
    # Placeholder - in production, query from database
    return []


def get_overdue_todos() -> List[Dict[str, Any]]:
    """
    Get all overdue todos.
    """
    # Placeholder - in production, query from database
    now = datetime.now()
    # Return todos where due_date < now and status != completed
    return []


def store_todo(todo: Dict[str, Any]) -> bool:
    """
    Store todo in persistent storage.
    """
    # For demo purposes - in production, integrate with:
    # - Todo apps (Todoist, Any.do, Microsoft To Do)
    # - Local database
    # - Cloud storage
    
    print(f"✅ Storing todo: {todo['todo_id']}")
    return True


def get_todo_by_id(todo_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve todo by ID.
    """
    # Placeholder for production implementation
    return {
        "todo_id": todo_id,
        "task": "Sample Task",
        "status": TodoStatus.PENDING.value,
        "created_at": int(time.time() * 1000),
        "subtasks": [],
        "progress_percentage": 0
    }


def delete_todo(todo_id: str) -> bool:
    """
    Delete a todo item.
    """
    print(f"🗑️ Deleting todo: {todo_id}")
    return True


def get_todo_analytics(user_id: str, days: int = 30) -> Dict[str, Any]:
    """
    Get analytics for user's todo activity.
    """
    # Placeholder analytics
    return {
        "total_todos": 25,
        "completed_todos": 18,
        "pending_todos": 5,
        "overdue_todos": 2,
        "completion_rate": 0.72,
        "avg_completion_time_hours": 24,
        "most_productive_day": "Tuesday",
        "top_categories": ["work", "personal", "health"],
        "period_days": days
    }
