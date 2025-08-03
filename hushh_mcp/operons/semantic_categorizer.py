# hushh_mcp/operons/semantic_categorizer.py

import re
from typing import Dict, List, Any
import json

# Mock LLM categorization - in production, use OpenAI API
CATEGORY_PATTERNS = {
    "work": [
        "meeting", "deadline", "project", "task", "work", "office", "colleague",
        "presentation", "report", "email", "conference", "client"
    ],
    "personal": [
        "family", "friend", "personal", "home", "hobby", "vacation", "weekend",
        "birthday", "anniversary", "social", "fun", "leisure"
    ],
    "health": [
        "doctor", "appointment", "medical", "health", "exercise", "gym", "diet",
        "medication", "checkup", "wellness", "fitness", "therapy"
    ],
    "finance": [
        "bank", "money", "payment", "bill", "budget", "investment", "savings",
        "credit", "loan", "expense", "income", "financial"
    ],
    "shopping": [
        "buy", "purchase", "order", "shopping", "store", "product", "delivery",
        "amazon", "cart", "checkout", "sale", "discount"
    ],
    "travel": [
        "flight", "hotel", "trip", "vacation", "travel", "booking", "airport",
        "destination", "itinerary", "reservation", "visa", "passport"
    ],
    "education": [
        "course", "study", "learn", "school", "university", "class", "homework",
        "exam", "assignment", "lecture", "tutorial", "certification"
    ],
    "event": [
        "event", "party", "celebration", "gathering", "meetup", "conference",
        "workshop", "seminar", "concert", "show", "festival"
    ],
    "task": [
        "todo", "task", "complete", "finish", "deadline", "priority", "urgent",
        "important", "reminder", "action", "follow-up"
    ],
    "note": [
        "note", "remember", "idea", "thought", "inspiration", "journal", "memo",
        "observation", "reflection", "insight"
    ]
}


def categorize_content(content: str, content_type: str = "general") -> Dict[str, Any]:
    """
    Semantic categorization of user content using pattern matching.
    In production, this would use a free-tier LLM API.
    
    Args:
        content (str): The content to categorize
        content_type (str): Type hint for the content
        
    Returns:
        Dict[str, Any]: Categorization result with confidence scores
    """
    if not content or not isinstance(content, str):
        return {
            "category": "unknown",
            "subcategories": [],
            "confidence": 0.0,
            "keywords": [],
            "suggestions": []
        }
    
    content_lower = content.lower()
    
    # Calculate scores for each category
    category_scores = {}
    matched_keywords = {}
    
    for category, keywords in CATEGORY_PATTERNS.items():
        score = 0
        matched = []
        
        for keyword in keywords:
            if keyword in content_lower:
                score += 1
                matched.append(keyword)
        
        if score > 0:
            category_scores[category] = score / len(keywords)  # Normalize
            matched_keywords[category] = matched
    
    # Determine primary category
    if category_scores:
        primary_category = max(category_scores.keys(), key=lambda k: category_scores[k])
        confidence = category_scores[primary_category]
        
        # Get top 3 categories as subcategories
        sorted_categories = sorted(
            category_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        subcategories = [cat for cat, score in sorted_categories[1:4]]
        
    else:
        primary_category = "general"
        confidence = 0.1
        subcategories = []
    
    # Generate automation suggestions
    suggestions = _generate_suggestions(primary_category, content)
    
    return {
        "category": primary_category,
        "subcategories": subcategories,
        "confidence": round(confidence, 2),
        "keywords": matched_keywords.get(primary_category, []),
        "suggestions": suggestions,
        "all_scores": category_scores,
        "processed_at": "semantic_categorizer_operon"
    }


def categorize_batch(contents: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    Batch categorization for multiple content items.
    
    Args:
        contents: List of dicts with 'content' and optional 'type' keys
        
    Returns:
        List of categorization results
    """
    results = []
    
    for item in contents:
        content = item.get("content", "")
        content_type = item.get("type", "general")
        
        result = categorize_content(content, content_type)
        result["original_item"] = item
        results.append(result)
    
    return results


def extract_action_items(content: str) -> List[Dict[str, Any]]:
    """
    Extract actionable items from content for automation.
    
    Args:
        content (str): Content to analyze
        
    Returns:
        List of action items with suggested automations
    """
    action_items = []
    
    # Pattern matching for action items
    task_patterns = [
        r"(?:need to|have to|must|should|remember to)\s+(.+?)(?:\.|$)",
        r"(?:todo|task):\s*(.+?)(?:\.|$)",
        r"(?:deadline|due)\s+(.+?)(?:\.|$)"
    ]
    
    for pattern in task_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            action_text = match.group(1).strip()
            if len(action_text) > 3:  # Filter out very short matches
                action_items.append({
                    "text": action_text,
                    "type": "task",
                    "automation_suggestion": "create_task",
                    "priority": _infer_priority(action_text),
                    "estimated_duration": _estimate_duration(action_text)
                })
    
    return action_items


def _generate_suggestions(category: str, content: str) -> List[str]:
    """Generate automation suggestions based on category."""
    suggestions = []
    
    suggestion_map = {
        "task": ["Create a task in your to-do list", "Set a reminder", "Add to calendar"],
        "event": ["Add to calendar", "Set reminder", "Invite attendees"],
        "work": ["Add to work calendar", "Create project task", "Set deadline reminder"],
        "health": ["Schedule appointment", "Set medication reminder", "Add to health log"],
        "finance": ["Add to budget tracker", "Set payment reminder", "Update expense log"],
        "travel": ["Add to travel itinerary", "Set booking reminders", "Check weather"],
        "shopping": ["Add to shopping list", "Set price alert", "Compare prices"],
        "personal": ["Add to personal calendar", "Set reminder", "Create note"]
    }
    
    return suggestion_map.get(category, ["Categorize and store", "Create reminder"])


def _infer_priority(text: str) -> str:
    """Infer priority level from text content."""
    text_lower = text.lower()
    
    if any(word in text_lower for word in ["urgent", "asap", "immediately", "critical"]):
        return "high"
    elif any(word in text_lower for word in ["important", "soon", "priority"]):
        return "medium"
    else:
        return "low"


def _estimate_duration(text: str) -> str:
    """Estimate task duration from text content."""
    text_lower = text.lower()
    
    if any(word in text_lower for word in ["quick", "fast", "briefly", "short"]):
        return "15m"
    elif any(word in text_lower for word in ["long", "detailed", "thorough", "complete"]):
        return "2h"
    else:
        return "30m"


# Advanced categorization with context
def categorize_with_context(
    content: str, 
    user_history: List[str] = None,
    time_context: str = None
) -> Dict[str, Any]:
    """
    Enhanced categorization considering user history and time context.
    
    Args:
        content: Content to categorize
        user_history: Previous user interactions for context
        time_context: Time-based context (morning, evening, weekend, etc.)
        
    Returns:
        Enhanced categorization result
    """
    # Get basic categorization
    base_result = categorize_content(content)
    
    # Enhance with context
    if time_context:
        base_result["time_context"] = time_context
        base_result["suggestions"] = _enhance_suggestions_with_time(
            base_result["suggestions"], 
            time_context
        )
    
    if user_history:
        base_result["historical_patterns"] = _analyze_user_patterns(user_history)
    
    return base_result


def _enhance_suggestions_with_time(suggestions: List[str], time_context: str) -> List[str]:
    """Enhance suggestions based on time context."""
    time_enhancements = {
        "morning": ["Add to today's priorities", "Schedule for this morning"],
        "evening": ["Add to tomorrow's agenda", "Set morning reminder"],
        "weekend": ["Add to weekend activities", "Schedule for next week"]
    }
    
    enhanced = suggestions.copy()
    enhanced.extend(time_enhancements.get(time_context, []))
    return enhanced


def _analyze_user_patterns(history: List[str]) -> Dict[str, Any]:
    """Analyze user patterns from history."""
    # Simple pattern analysis
    categories = [categorize_content(item)["category"] for item in history]
    
    from collections import Counter
    category_counts = Counter(categories)
    
    return {
        "frequent_categories": dict(category_counts.most_common(3)),
        "total_interactions": len(history),
        "diversity_score": len(set(categories)) / len(categories) if categories else 0
    }
