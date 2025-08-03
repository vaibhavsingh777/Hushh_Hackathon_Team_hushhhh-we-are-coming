# hushh_mcp/operons/schedule_event.py

from typing import Dict, Any, List, Optional
import uuid
import json
from datetime import datetime, timedelta
import time


def create_calendar_event(
    title: str,
    start_time: str,
    end_time: Optional[str] = None,
    description: str = "",
    location: str = "",
    attendees: List[str] = None
) -> Dict[str, Any]:
    """
    Create a calendar event with the provided details.
    
    Args:
        title: Event title
        start_time: Start time (ISO format or readable format)
        end_time: End time (optional, defaults to 1 hour after start)
        description: Event description
        location: Event location
        attendees: List of attendee emails
        
    Returns:
        Dict with event creation results
    """
    if attendees is None:
        attendees = []
    
    # Generate unique event ID
    event_id = f"event_{uuid.uuid4().hex[:8]}"
    
    # Parse and validate start time
    parsed_start = parse_datetime_string(start_time)
    if not parsed_start:
        raise ValueError(f"Invalid start time format: {start_time}")
    
    # Parse or calculate end time
    if end_time:
        parsed_end = parse_datetime_string(end_time)
        if not parsed_end:
            raise ValueError(f"Invalid end time format: {end_time}")
    else:
        # Default to 1 hour duration
        parsed_end = parsed_start + timedelta(hours=1)
    
    # Validate event timing
    if parsed_end <= parsed_start:
        raise ValueError("End time must be after start time")
    
    # Create event object
    event = {
        "event_id": event_id,
        "title": title,
        "description": description,
        "start_time": parsed_start.isoformat(),
        "end_time": parsed_end.isoformat(),
        "location": location,
        "attendees": attendees,
        "status": "scheduled",
        "created_at": int(time.time() * 1000),
        "duration_minutes": int((parsed_end - parsed_start).total_seconds() / 60),
        "all_day": False,
        "recurring": False,
        "reminders": [
            {"type": "notification", "minutes_before": 15},
            {"type": "email", "minutes_before": 60}
        ]
    }
    
    # Store event (in real implementation, this would save to calendar service)
    store_event(event)
    
    print(f"✅ Calendar event created: {title} on {parsed_start.strftime('%Y-%m-%d %H:%M')}")
    
    return event


def parse_datetime_string(datetime_str: str) -> Optional[datetime]:
    """
    Parse various datetime string formats into datetime object.
    """
    formats_to_try = [
        "%Y-%m-%d %H:%M:%S",      # 2024-01-15 14:30:00
        "%Y-%m-%d %H:%M",         # 2024-01-15 14:30
        "%Y-%m-%dT%H:%M:%S",      # ISO format
        "%Y-%m-%dT%H:%M",         # ISO format without seconds
        "%m/%d/%Y %H:%M",         # 01/15/2024 14:30
        "%m/%d/%Y %I:%M %p",      # 01/15/2024 2:30 PM
        "%d/%m/%Y %H:%M",         # 15/01/2024 14:30
        "%B %d, %Y %H:%M",        # January 15, 2024 14:30
        "%B %d, %Y %I:%M %p",     # January 15, 2024 2:30 PM
    ]
    
    for fmt in formats_to_try:
        try:
            return datetime.strptime(datetime_str, fmt)
        except ValueError:
            continue
    
    # Try to parse relative time expressions
    relative_time = parse_relative_time(datetime_str)
    if relative_time:
        return relative_time
    
    return None


def parse_relative_time(time_str: str) -> Optional[datetime]:
    """
    Parse relative time expressions like 'tomorrow at 2pm', 'next Monday', etc.
    """
    now = datetime.now()
    time_str_lower = time_str.lower().strip()
    
    # Handle "tomorrow" expressions
    if "tomorrow" in time_str_lower:
        tomorrow = now + timedelta(days=1)
        if "at" in time_str_lower:
            time_part = time_str_lower.split("at")[1].strip()
            hour = extract_hour_from_string(time_part)
            if hour is not None:
                return tomorrow.replace(hour=hour, minute=0, second=0, microsecond=0)
        return tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)  # Default to 9 AM
    
    # Handle "today" expressions
    if "today" in time_str_lower:
        if "at" in time_str_lower:
            time_part = time_str_lower.split("at")[1].strip()
            hour = extract_hour_from_string(time_part)
            if hour is not None:
                return now.replace(hour=hour, minute=0, second=0, microsecond=0)
        return now.replace(hour=9, minute=0, second=0, microsecond=0)
    
    # Handle "next week" expressions
    if "next week" in time_str_lower:
        next_week = now + timedelta(days=7)
        return next_week.replace(hour=9, minute=0, second=0, microsecond=0)
    
    return None


def extract_hour_from_string(time_str: str) -> Optional[int]:
    """
    Extract hour from time string like '2pm', '14:00', '2:30'.
    """
    import re
    
    # Handle PM/AM format
    pm_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*pm', time_str.lower())
    if pm_match:
        hour = int(pm_match.group(1))
        if hour != 12:
            hour += 12
        return hour
    
    am_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*am', time_str.lower())
    if am_match:
        hour = int(am_match.group(1))
        if hour == 12:
            hour = 0
        return hour
    
    # Handle 24-hour format
    hour_match = re.search(r'(\d{1,2})(?::(\d{2}))?', time_str)
    if hour_match:
        hour = int(hour_match.group(1))
        if 0 <= hour <= 23:
            return hour
    
    return None


def store_event(event: Dict[str, Any]) -> bool:
    """
    Store event in persistent storage.
    In real implementation, this would integrate with calendar services.
    """
    # For demo purposes, we'll simulate storage
    print(f"📅 Storing event: {event['event_id']}")
    
    # In production, integrate with:
    # - Google Calendar API
    # - Microsoft Outlook API
    # - Local calendar database
    # - iCal format files
    
    return True


def update_event(event_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update an existing calendar event.
    """
    # Retrieve existing event (simulated)
    existing_event = get_event_by_id(event_id)
    if not existing_event:
        raise ValueError(f"Event not found: {event_id}")
    
    # Apply updates
    updated_event = existing_event.copy()
    updated_event.update(updates)
    updated_event["updated_at"] = int(time.time() * 1000)
    
    # Store updated event
    store_event(updated_event)
    
    print(f"✅ Event updated: {event_id}")
    return updated_event


def delete_event(event_id: str) -> bool:
    """
    Delete a calendar event.
    """
    # In real implementation, this would delete from calendar service
    print(f"🗑️ Deleting event: {event_id}")
    return True


def get_event_by_id(event_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve event by ID.
    For demo purposes, returns a mock event.
    """
    # In production, this would query the actual calendar service
    return {
        "event_id": event_id,
        "title": "Sample Event",
        "start_time": datetime.now().isoformat(),
        "end_time": (datetime.now() + timedelta(hours=1)).isoformat(),
        "status": "scheduled"
    }


def create_recurring_event(
    title: str,
    start_time: str,
    recurrence_pattern: str,
    end_date: Optional[str] = None,
    **kwargs
) -> List[Dict[str, Any]]:
    """
    Create a recurring calendar event.
    
    Args:
        title: Event title
        start_time: First occurrence start time
        recurrence_pattern: 'daily', 'weekly', 'monthly', 'yearly'
        end_date: When to stop creating occurrences
        **kwargs: Additional event parameters
        
    Returns:
        List of created event objects
    """
    events = []
    
    # Parse start time
    parsed_start = parse_datetime_string(start_time)
    if not parsed_start:
        raise ValueError(f"Invalid start time: {start_time}")
    
    # Parse end date
    parsed_end_date = None
    if end_date:
        parsed_end_date = parse_datetime_string(end_date)
    
    # Calculate recurrence delta
    recurrence_deltas = {
        'daily': timedelta(days=1),
        'weekly': timedelta(weeks=1),
        'monthly': timedelta(days=30),  # Approximate
        'yearly': timedelta(days=365)   # Approximate
    }
    
    delta = recurrence_deltas.get(recurrence_pattern.lower())
    if not delta:
        raise ValueError(f"Invalid recurrence pattern: {recurrence_pattern}")
    
    # Create recurring events (limit to reasonable number)
    current_start = parsed_start
    max_occurrences = 52  # Maximum 1 year of weekly events
    
    for i in range(max_occurrences):
        if parsed_end_date and current_start > parsed_end_date:
            break
        
        event = create_calendar_event(
            title=f"{title} (#{i+1})",
            start_time=current_start.isoformat(),
            **kwargs
        )
        event["recurring"] = True
        event["recurrence_pattern"] = recurrence_pattern
        event["occurrence_number"] = i + 1
        
        events.append(event)
        current_start += delta
    
    print(f"✅ Created {len(events)} recurring events")
    return events
