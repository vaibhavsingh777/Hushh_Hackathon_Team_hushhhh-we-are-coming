#!/usr/bin/env python3
"""
Hushh MCP - Scheduling Intelligence Operon
Smart scheduling and calendar optimization functions.
Open-source contribution for intelligent time management.
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta, timezone
from enum import Enum
import re


def analyze_scheduling_patterns(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze scheduling patterns and provide insights for optimization.
    
    Args:
        events: List of event dictionaries to analyze
        
    Returns:
        Dict containing scheduling analysis and optimization suggestions
        
    Example:
        >>> events = [{"title": "Meeting", "start_time": "2025-08-02T10:00:00", "end_time": "2025-08-02T11:00:00"}]
        >>> analyze_scheduling_patterns(events)
        {"total_hours": 1.0, "meeting_count": 1, "efficiency_score": 0.8, ...}
    """
    if not events:
        return {
            "total_hours": 0,
            "meeting_count": 0,
            "avg_duration": 0,
            "efficiency_score": 1.0,
            "busiest_day": "None",
            "optimization_count": 0,
            "suggestions": [],
            "patterns": {}
        }
    
    total_minutes = 0
    meeting_count = 0
    daily_counts = {}
    duration_distribution = []
    conflicts = []
    
    # Sort events by start time for conflict detection
    sorted_events = []
    for event in events:
        try:
            start_time = event.get("start_time", "")
            if isinstance(start_time, str):
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            else:
                start_dt = start_time
            
            end_time = event.get("end_time", "")
            if isinstance(end_time, str):
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            else:
                end_dt = end_time
            
            duration = (end_dt - start_dt).total_seconds() / 60  # minutes
            
            sorted_events.append({
                "title": event.get("title", ""),
                "start_dt": start_dt,
                "end_dt": end_dt,
                "duration": duration,
                "type": event.get("type", "meeting")
            })
            
            # Track daily distribution
            day_key = start_dt.strftime("%Y-%m-%d")
            daily_counts[day_key] = daily_counts.get(day_key, 0) + 1
            
            # Accumulate stats
            total_minutes += duration
            meeting_count += 1
            duration_distribution.append(duration)
            
        except (ValueError, TypeError, AttributeError) as e:
            # Skip invalid events
            continue
    
    # Sort by start time for conflict detection
    sorted_events.sort(key=lambda x: x["start_dt"])
    
    # Detect scheduling conflicts
    for i in range(len(sorted_events) - 1):
        current = sorted_events[i]
        next_event = sorted_events[i + 1]
        
        # Check for overlaps
        if current["end_dt"] > next_event["start_dt"]:
            conflicts.append({
                "type": "overlap",
                "event1": current["title"],
                "event2": next_event["title"],
                "overlap_minutes": (current["end_dt"] - next_event["start_dt"]).total_seconds() / 60
            })
        
        # Check for back-to-back meetings (potential issue)
        elif current["end_dt"] == next_event["start_dt"]:
            conflicts.append({
                "type": "back_to_back",
                "event1": current["title"],
                "event2": next_event["title"],
                "buffer_needed": 15  # Suggest 15-minute buffer
            })
    
    # Calculate metrics
    avg_duration = sum(duration_distribution) / len(duration_distribution) if duration_distribution else 0
    total_hours = total_minutes / 60
    
    # Find busiest day
    busiest_day = max(daily_counts, key=daily_counts.get) if daily_counts else "None"
    max_daily_events = max(daily_counts.values()) if daily_counts else 0
    
    # Calculate efficiency score (lower is better, based on conflicts and meeting density)
    efficiency_score = 1.0
    if conflicts:
        efficiency_score -= len(conflicts) * 0.1
    if max_daily_events > 8:  # Too many meetings per day
        efficiency_score -= 0.2
    if avg_duration > 90:  # Meetings too long on average
        efficiency_score -= 0.1
    
    efficiency_score = max(0.0, min(1.0, efficiency_score))
    
    # Generate optimization suggestions
    suggestions = []
    if len(conflicts) > 0:
        suggestions.append(f"Found {len(conflicts)} scheduling conflicts that need resolution")
    if max_daily_events > 6:
        suggestions.append(f"Consider spreading meetings across more days (max {max_daily_events} on {busiest_day})")
    if avg_duration > 60:
        suggestions.append(f"Average meeting duration is {avg_duration:.0f} minutes - consider shorter meetings")
    if len([e for e in sorted_events if e["type"] == "meeting"]) > len(sorted_events) * 0.8:
        suggestions.append("Schedule more focus time blocks between meetings")
    
    # Pattern analysis
    patterns = {
        "meeting_types": {},
        "time_distribution": {},
        "duration_patterns": {
            "short_meetings": len([d for d in duration_distribution if d <= 30]),
            "medium_meetings": len([d for d in duration_distribution if 30 < d <= 60]),
            "long_meetings": len([d for d in duration_distribution if d > 60])
        }
    }
    
    # Analyze meeting types
    for event in sorted_events:
        event_type = event["type"]
        patterns["meeting_types"][event_type] = patterns["meeting_types"].get(event_type, 0) + 1
    
    # Analyze time distribution (by hour of day)
    for event in sorted_events:
        hour = event["start_dt"].hour
        hour_key = f"{hour:02d}:00"
        patterns["time_distribution"][hour_key] = patterns["time_distribution"].get(hour_key, 0) + 1
    
    return {
        "total_hours": round(total_hours, 1),
        "meeting_count": meeting_count,
        "avg_duration": round(avg_duration, 1),
        "efficiency_score": round(efficiency_score, 2),
        "busiest_day": busiest_day,
        "max_daily_events": max_daily_events,
        "optimization_count": len(suggestions),
        "suggestions": suggestions,
        "conflicts": conflicts,
        "patterns": patterns,
        "daily_distribution": daily_counts
    }


class EventType(str, Enum):
    MEETING = "meeting"
    APPOINTMENT = "appointment"
    DEADLINE = "deadline"
    REMINDER = "reminder"
    TASK = "task"
    PERSONAL = "personal"
    TRAVEL = "travel"
    BREAK = "break"
    FOCUS_TIME = "focus_time"


class ConflictType(str, Enum):
    OVERLAP = "overlap"
    BACK_TO_BACK = "back_to_back"
    TRAVEL_TIME = "travel_time"
    DOUBLE_BOOKING = "double_booking"
    OVERBOOKED = "overbooked"


class TimePreference(str, Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    ANY = "any"


def parse_natural_time(text: str, reference_date: datetime = None) -> Optional[Dict[str, Any]]:
    """
    Parse natural language time expressions into structured datetime.
    
    Args:
        text: Natural language time expression
        reference_date: Reference date for relative expressions
        
    Returns:
        Dict with parsed datetime information or None if not parseable
        
    Example:
        >>> parse_natural_time("tomorrow at 2pm")
        {"datetime": "2025-08-10T14:00:00", "confidence": 0.9, "type": "absolute"}
    """
    if not text or not isinstance(text, str):
        return None
    
    if reference_date is None:
        reference_date = datetime.now()
    
    text = text.lower().strip()
    
    # Time patterns
    time_patterns = {
        r'(\d{1,2}):?(\d{2})?\s*(am|pm)': 'time_12h',
        r'(\d{1,2}):(\d{2})': 'time_24h',
        r'(\d{1,2})\s*(am|pm)': 'time_12h_simple',
        r'noon': 'noon',
        r'midnight': 'midnight'
    }
    
    # Date patterns
    date_patterns = {
        r'today': 'today',
        r'tomorrow': 'tomorrow',
        r'yesterday': 'yesterday',
        r'next\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)': 'next_weekday',
        r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)': 'this_weekday',
        r'in\s+(\d+)\s+(day|days|week|weeks|month|months)': 'relative_future',
        r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})': 'date_numeric'
    }
    
    parsed_info = {
        "datetime": None,
        "confidence": 0.0,
        "type": "unknown",
        "components": {}
    }
    
    # Extract time component
    time_found = False
    hour, minute = None, None
    
    for pattern, time_type in time_patterns.items():
        match = re.search(pattern, text)
        if match:
            if time_type == 'time_12h':
                hour = int(match.group(1))
                minute = int(match.group(2)) if match.group(2) else 0
                if match.group(3) == 'pm' and hour != 12:
                    hour += 12
                elif match.group(3) == 'am' and hour == 12:
                    hour = 0
            elif time_type == 'time_24h':
                hour = int(match.group(1))
                minute = int(match.group(2))
            elif time_type == 'time_12h_simple':
                hour = int(match.group(1))
                minute = 0
                if match.group(2) == 'pm' and hour != 12:
                    hour += 12
                elif match.group(2) == 'am' and hour == 12:
                    hour = 0
            elif time_type == 'noon':
                hour, minute = 12, 0
            elif time_type == 'midnight':
                hour, minute = 0, 0
            
            time_found = True
            break
    
    # Extract date component
    date_found = False
    target_date = reference_date.date()
    
    for pattern, date_type in date_patterns.items():
        match = re.search(pattern, text)
        if match:
            if date_type == 'today':
                target_date = reference_date.date()
            elif date_type == 'tomorrow':
                target_date = reference_date.date() + timedelta(days=1)
            elif date_type == 'yesterday':
                target_date = reference_date.date() - timedelta(days=1)
            elif date_type == 'next_weekday':
                weekday_name = match.group(1)
                weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                target_weekday = weekdays.index(weekday_name)
                days_ahead = target_weekday - reference_date.weekday()
                if days_ahead <= 0:
                    days_ahead += 7
                target_date = reference_date.date() + timedelta(days=days_ahead)
            elif date_type == 'this_weekday':
                weekday_name = match.group(1)
                weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                target_weekday = weekdays.index(weekday_name)
                days_ahead = target_weekday - reference_date.weekday()
                if days_ahead < 0:
                    days_ahead += 7
                target_date = reference_date.date() + timedelta(days=days_ahead)
            elif date_type == 'relative_future':
                amount = int(match.group(1))
                unit = match.group(2)
                if 'day' in unit:
                    target_date = reference_date.date() + timedelta(days=amount)
                elif 'week' in unit:
                    target_date = reference_date.date() + timedelta(weeks=amount)
                elif 'month' in unit:
                    target_date = reference_date.date() + timedelta(days=amount * 30)  # Approximate
            
            date_found = True
            break
    
    # Combine date and time
    if date_found or time_found:
        if not time_found:
            hour, minute = 9, 0  # Default to 9 AM
        
        try:
            result_datetime = datetime.combine(target_date, datetime.min.time().replace(hour=hour, minute=minute))
            parsed_info["datetime"] = result_datetime.isoformat()
            parsed_info["confidence"] = 0.9 if (date_found and time_found) else 0.7
            parsed_info["type"] = "absolute" if date_found else "time_only"
            parsed_info["components"] = {
                "date_found": date_found,
                "time_found": time_found,
                "hour": hour,
                "minute": minute
            }
        except ValueError:
            return None
    
    return parsed_info if parsed_info["datetime"] else None


def detect_event_conflicts(events: List[Dict[str, Any]], buffer_minutes: int = 15) -> List[Dict[str, Any]]:
    """
    Detect scheduling conflicts between events.
    
    Args:
        events: List of events with start_time and end_time
        buffer_minutes: Buffer time between events in minutes
        
    Returns:
        List of detected conflicts
        
    Example:
        >>> events = [{"id": "1", "start_time": "2025-08-09T10:00:00", "end_time": "2025-08-09T11:00:00"}]
        >>> detect_event_conflicts(events)
        [{"type": "overlap", "events": ["1", "2"], "severity": "high"}]
    """
    if not events or len(events) < 2:
        return []
    
    conflicts = []
    
    # Sort events by start time
    sorted_events = sorted(events, key=lambda e: e.get('start_time', ''))
    
    for i in range(len(sorted_events)):
        for j in range(i + 1, len(sorted_events)):
            event_a = sorted_events[i]
            event_b = sorted_events[j]
            
            try:
                start_a = datetime.fromisoformat(event_a['start_time'].replace('Z', ''))
                end_a = datetime.fromisoformat(event_a['end_time'].replace('Z', ''))
                start_b = datetime.fromisoformat(event_b['start_time'].replace('Z', ''))
                end_b = datetime.fromisoformat(event_b['end_time'].replace('Z', ''))
            except (ValueError, KeyError):
                continue
            
            # Check for overlap
            if start_a < end_b and start_b < end_a:
                conflict_type = ConflictType.OVERLAP
                severity = "high"
                
                # Check if it's a complete overlap (double booking)
                if start_a == start_b and end_a == end_b:
                    conflict_type = ConflictType.DOUBLE_BOOKING
                    severity = "critical"
                
                conflicts.append({
                    "type": conflict_type,
                    "events": [event_a.get('id', i), event_b.get('id', j)],
                    "severity": severity,
                    "details": {
                        "overlap_start": max(start_a, start_b).isoformat(),
                        "overlap_end": min(end_a, end_b).isoformat(),
                        "overlap_duration": str(min(end_a, end_b) - max(start_a, start_b))
                    }
                })
            
            # Check for back-to-back scheduling (within buffer)
            elif abs((start_b - end_a).total_seconds()) <= buffer_minutes * 60:
                conflicts.append({
                    "type": ConflictType.BACK_TO_BACK,
                    "events": [event_a.get('id', i), event_b.get('id', j)],
                    "severity": "medium",
                    "details": {
                        "gap_minutes": abs((start_b - end_a).total_seconds()) / 60,
                        "recommended_buffer": buffer_minutes
                    }
                })
    
    return conflicts


def suggest_optimal_meeting_time(
    participants_availability: List[Dict[str, Any]], 
    duration_minutes: int = 60,
    preferred_times: List[TimePreference] = None,
    date_range: Tuple[datetime, datetime] = None
) -> List[Dict[str, Any]]:
    """
    Suggest optimal meeting times based on participant availability.
    
    Args:
        participants_availability: List of participant availability windows
        duration_minutes: Required meeting duration in minutes
        preferred_times: Preferred time slots
        date_range: Date range to search within
        
    Returns:
        List of suggested meeting time slots
        
    Example:
        >>> availability = [{"name": "John", "free_slots": ["2025-08-09T10:00:00/2025-08-09T12:00:00"]}]
        >>> suggest_optimal_meeting_time(availability, 60)
        [{"start_time": "2025-08-09T10:00:00", "end_time": "2025-08-09T11:00:00", "score": 0.9}]
    """
    if not participants_availability:
        return []
    
    if preferred_times is None:
        preferred_times = [TimePreference.MORNING, TimePreference.AFTERNOON]
    
    if date_range is None:
        now = datetime.now()
        date_range = (now, now + timedelta(days=14))  # Next 2 weeks
    
    # Parse availability slots
    all_free_slots = []
    for participant in participants_availability:
        participant_slots = []
        for slot_str in participant.get('free_slots', []):
            try:
                if '/' in slot_str:
                    start_str, end_str = slot_str.split('/')
                    start_time = datetime.fromisoformat(start_str.replace('Z', ''))
                    end_time = datetime.fromisoformat(end_str.replace('Z', ''))
                    participant_slots.append((start_time, end_time))
            except ValueError:
                continue
        all_free_slots.append(participant_slots)
    
    if not all_free_slots:
        return []
    
    # Find overlapping free time slots
    common_slots = []
    duration_delta = timedelta(minutes=duration_minutes)
    
    # Generate potential time slots (every 30 minutes)
    current_time = date_range[0].replace(minute=0, second=0, microsecond=0)
    end_search = date_range[1]
    
    while current_time + duration_delta <= end_search:
        slot_end = current_time + duration_delta
        
        # Check if this slot is available for all participants
        available_for_all = True
        for participant_slots in all_free_slots:
            participant_available = False
            for start_free, end_free in participant_slots:
                if start_free <= current_time and slot_end <= end_free:
                    participant_available = True
                    break
            if not participant_available:
                available_for_all = False
                break
        
        if available_for_all:
            # Calculate score based on preferences
            score = calculate_time_slot_score(current_time, preferred_times)
            common_slots.append({
                "start_time": current_time.isoformat(),
                "end_time": slot_end.isoformat(),
                "score": score,
                "participants_count": len(participants_availability)
            })
        
        current_time += timedelta(minutes=30)  # Move to next 30-minute slot
    
    # Sort by score and return top suggestions
    common_slots.sort(key=lambda x: x['score'], reverse=True)
    return common_slots[:10]  # Return top 10 suggestions


def calculate_time_slot_score(slot_time: datetime, preferred_times: List[TimePreference]) -> float:
    """
    Calculate score for a time slot based on preferences.
    
    Args:
        slot_time: Time slot to score
        preferred_times: List of preferred time periods
        
    Returns:
        float: Score between 0 and 1
    """
    base_score = 0.5
    hour = slot_time.hour
    
    # Time preference scoring
    time_scores = {
        TimePreference.MORNING: 1.0 if 8 <= hour < 12 else 0.3,
        TimePreference.AFTERNOON: 1.0 if 13 <= hour < 17 else 0.3,
        TimePreference.EVENING: 1.0 if 17 <= hour < 20 else 0.2,
        TimePreference.ANY: 0.8
    }
    
    max_time_score = max(time_scores.get(pref, 0.5) for pref in preferred_times)
    
    # Day of week bonus (weekdays preferred for business meetings)
    weekday_bonus = 0.2 if slot_time.weekday() < 5 else 0.0
    
    # Avoid very early or very late times
    if hour < 8 or hour > 18:
        time_penalty = 0.3
    else:
        time_penalty = 0.0
    
    final_score = min(1.0, max_time_score + weekday_bonus - time_penalty)
    return round(final_score, 2)


def extract_meeting_details(content: str) -> Dict[str, Any]:
    """
    Extract meeting details from natural language content.
    
    Args:
        content: Text content describing a meeting
        
    Returns:
        Dict with extracted meeting details
        
    Example:
        >>> extract_meeting_details("Team standup tomorrow at 9am for 30 minutes")
        {"type": "meeting", "duration": 30, "participants": ["team"], "time": "..."}
    """
    if not content:
        return {}
    
    content_lower = content.lower()
    details = {
        "type": None,
        "duration": None,
        "participants": [],
        "location": None,
        "agenda_items": [],
        "urgency": "normal"
    }
    
    # Detect meeting type
    meeting_types = {
        "standup": ["standup", "daily", "scrum"],
        "review": ["review", "retrospective", "feedback"],
        "planning": ["planning", "strategy", "roadmap"],
        "interview": ["interview", "screening", "candidate"],
        "presentation": ["presentation", "demo", "showcase"],
        "training": ["training", "workshop", "session"],
        "one-on-one": ["1:1", "one on one", "1-on-1", "one-on-one"]
    }
    
    for meeting_type, keywords in meeting_types.items():
        if any(keyword in content_lower for keyword in keywords):
            details["type"] = meeting_type
            break
    
    if not details["type"]:
        details["type"] = "meeting"  # Default
    
    # Extract duration
    duration_patterns = [
        r'(\d+)\s*(?:minute|min|minutes|mins)',
        r'(\d+)\s*(?:hour|hr|hours|hrs)',
        r'(\d+\.5|\d+)\s*(?:hour|hr|hours|hrs)'
    ]
    
    for pattern in duration_patterns:
        match = re.search(pattern, content_lower)
        if match:
            duration_value = float(match.group(1))
            if 'hour' in match.group(0) or 'hr' in match.group(0):
                details["duration"] = int(duration_value * 60)
            else:
                details["duration"] = int(duration_value)
            break
    
    # Extract participants
    participant_patterns = [
        r'with\s+([a-zA-Z\s,]+?)(?:\s+at|\s+in|\s+for|$)',
        r'team\s+([a-zA-Z\s]+?)(?:\s+at|\s+in|\s+for|$)',
        r'([a-zA-Z]+)\s+(?:and|,)\s+([a-zA-Z]+)'
    ]
    
    for pattern in participant_patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            if isinstance(match, tuple):
                details["participants"].extend([p.strip() for p in match if p.strip()])
            else:
                participants = [p.strip() for p in match.split(',') if p.strip()]
                details["participants"].extend(participants)
    
    # Extract location
    location_patterns = [
        r'(?:in|at)\s+([a-zA-Z0-9\s]+?)\s+(?:at|for|to|$)',
        r'room\s+([a-zA-Z0-9]+)',
        r'conference\s+room\s+([a-zA-Z0-9]+)'
    ]
    
    for pattern in location_patterns:
        match = re.search(pattern, content_lower)
        if match:
            details["location"] = match.group(1).strip()
            break
    
    # Detect urgency
    urgency_keywords = {
        "urgent": ["urgent", "asap", "immediately", "critical"],
        "high": ["important", "priority", "soon"],
        "normal": []
    }
    
    for urgency_level, keywords in urgency_keywords.items():
        if any(keyword in content_lower for keyword in keywords):
            details["urgency"] = urgency_level
            break
    
    return {k: v for k, v in details.items() if v}  # Remove None values


def generate_calendar_summary(events: List[Dict[str, Any]], date: datetime = None) -> Dict[str, Any]:
    """
    Generate a summary of calendar events for a specific date.
    
    Args:
        events: List of calendar events
        date: Date to summarize (defaults to today)
        
    Returns:
        Dict with calendar summary
        
    Example:
        >>> events = [{"title": "Meeting", "start_time": "2025-08-09T10:00:00"}]
        >>> generate_calendar_summary(events)
        {"total_events": 1, "busy_hours": 1, "free_slots": [...]}
    """
    if date is None:
        date = datetime.now().date()
    
    if not events:
        return {
            "date": date.isoformat(),
            "total_events": 0,
            "busy_hours": 0,
            "free_hours": 8,  # Assuming 8-hour workday
            "events_by_type": {},
            "conflicts": [],
            "recommendations": ["No events scheduled - great day for deep work!"]
        }
    
    # Filter events for the specific date
    date_events = []
    for event in events:
        try:
            event_start = datetime.fromisoformat(event.get('start_time', '').replace('Z', ''))
            if event_start.date() == date:
                date_events.append(event)
        except ValueError:
            continue
    
    if not date_events:
        return {
            "date": date.isoformat(),
            "total_events": 0,
            "busy_hours": 0,
            "free_hours": 8,
            "events_by_type": {},
            "conflicts": [],
            "recommendations": ["No events scheduled for this date"]
        }
    
    # Calculate busy time
    total_busy_minutes = 0
    events_by_type = {}
    
    for event in date_events:
        try:
            start_time = datetime.fromisoformat(event.get('start_time', '').replace('Z', ''))
            end_time = datetime.fromisoformat(event.get('end_time', '').replace('Z', ''))
            duration = (end_time - start_time).total_seconds() / 60
            total_busy_minutes += duration
            
            event_type = event.get('type', 'other')
            events_by_type[event_type] = events_by_type.get(event_type, 0) + 1
            
        except ValueError:
            continue
    
    busy_hours = total_busy_minutes / 60
    
    # Detect conflicts
    conflicts = detect_event_conflicts(date_events)
    
    # Generate recommendations
    recommendations = []
    if len(conflicts) > 0:
        recommendations.append(f"Found {len(conflicts)} scheduling conflicts - consider rescheduling")
    
    if busy_hours > 6:
        recommendations.append("Very busy day - ensure to schedule breaks")
    elif busy_hours < 2:
        recommendations.append("Light schedule - good opportunity for focused work")
    
    if not recommendations:
        recommendations.append("Well-balanced schedule")
    
    return {
        "date": date.isoformat(),
        "total_events": len(date_events),
        "busy_hours": round(busy_hours, 1),
        "free_hours": round(8 - busy_hours, 1) if busy_hours <= 8 else 0,
        "events_by_type": events_by_type,
        "conflicts": len(conflicts),
        "recommendations": recommendations
    }


if __name__ == "__main__":
    # Test the scheduling intelligence functions
    print("📅 Testing Hushh MCP Scheduling Intelligence Operon")
    
    # Test natural time parsing
    time_result = parse_natural_time("tomorrow at 2pm")
    print(f"✅ Parsed time: {time_result['datetime'] if time_result else 'None'}")
    
    # Test meeting details extraction
    meeting_text = "Team standup tomorrow at 9am for 30 minutes with John and Sarah"
    meeting_details = extract_meeting_details(meeting_text)
    print(f"✅ Meeting type: {meeting_details.get('type', 'unknown')}")
    print(f"✅ Duration: {meeting_details.get('duration', 'unknown')} minutes")
    
    # Test conflict detection
    test_events = [
        {"id": "1", "start_time": "2025-08-09T10:00:00", "end_time": "2025-08-09T11:00:00"},
        {"id": "2", "start_time": "2025-08-09T10:30:00", "end_time": "2025-08-09T11:30:00"}
    ]
    conflicts = detect_event_conflicts(test_events)
    print(f"✅ Conflicts detected: {len(conflicts)}")
    
    print("\n📅 Scheduling intelligence operon ready for use!")
