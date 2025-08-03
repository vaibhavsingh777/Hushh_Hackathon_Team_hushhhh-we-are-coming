#!/usr/bin/env python3
"""
Hushh MCP - Content Classification Operon
Advanced content classification and categorization functions.
Open-source contribution for intelligent data organization.
"""

import re
import json
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timezone
from enum import Enum
from collections import Counter


class ContentCategory(str, Enum):
    WORK = "work"
    PERSONAL = "personal"
    FINANCIAL = "financial"
    HEALTH = "health"
    EDUCATION = "education"
    TRAVEL = "travel"
    SHOPPING = "shopping"
    ENTERTAINMENT = "entertainment"
    SOCIAL = "social"
    NEWS = "news"
    SPAM = "spam"
    UNKNOWN = "unknown"


class ContentType(str, Enum):
    EMAIL = "email"
    CALENDAR = "calendar"
    DOCUMENT = "document"
    MESSAGE = "message"
    NOTIFICATION = "notification"
    TASK = "task"


class Priority(str, Enum):
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


def extract_keywords(content: str, max_keywords: int = 10) -> List[str]:
    """
    Extract relevant keywords from content for classification.
    
    Args:
        content: Text content to analyze
        max_keywords: Maximum number of keywords to return
        
    Returns:
        List of extracted keywords
        
    Example:
        >>> extract_keywords("Meeting about quarterly sales review tomorrow")
        ["meeting", "quarterly", "sales", "review", "tomorrow"]
    """
    if not content or not isinstance(content, str):
        return []
    
    # Clean and normalize text
    text = re.sub(r'[^\w\s]', ' ', content.lower())
    words = text.split()
    
    # Common stop words to filter out
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'will',
        'would', 'could', 'should', 'this', 'that', 'these', 'those', 'i', 'you', 'he',
        'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his',
        'its', 'our', 'their', 'from', 'up', 'about', 'into', 'over', 'after'
    }
    
    # Filter meaningful words (length > 2, not stop words, not numbers)
    meaningful_words = [
        word for word in words 
        if len(word) > 2 and word not in stop_words and not word.isdigit()
    ]
    
    # Count word frequency and return top keywords
    word_counts = Counter(meaningful_words)
    return [word for word, _ in word_counts.most_common(max_keywords)]


def classify_content_category(content: str, subject: str = "", sender: str = "") -> Dict[str, Any]:
    """
    Classify content into appropriate categories using rule-based approach.
    
    Args:
        content: Main content to classify
        subject: Subject line or title (optional)
        sender: Sender information (optional)
        
    Returns:
        Dict with classification results including category and confidence
        
    Example:
        >>> classify_content_category("Invoice #123 for services", "Payment Due")
        {"category": "financial", "confidence": 0.9, "keywords": ["invoice", "payment"]}
    """
    if not content:
        return {
            "category": ContentCategory.UNKNOWN,
            "confidence": 0.0,
            "keywords": [],
            "reasoning": "Empty content"
        }
    
    # Combine all text for analysis
    full_text = f"{subject} {content} {sender}".lower()
    keywords = extract_keywords(full_text)
    
    # Define category patterns with weights
    category_patterns = {
        ContentCategory.WORK: {
            "keywords": ["meeting", "project", "deadline", "office", "team", "manager", "colleague", 
                        "conference", "presentation", "report", "budget", "client", "customer"],
            "domains": ["@company", "@corp", "@inc", "@ltd", "@llc"],
            "weight": 1.0
        },
        ContentCategory.FINANCIAL: {
            "keywords": ["invoice", "payment", "bill", "bank", "credit", "debit", "transaction", 
                        "balance", "statement", "tax", "receipt", "refund", "charge"],
            "domains": ["@bank", "@paypal", "@stripe", "@visa", "@mastercard"],
            "weight": 1.2
        },
        ContentCategory.HEALTH: {
            "keywords": ["doctor", "appointment", "medical", "health", "prescription", "clinic", 
                        "hospital", "insurance", "diagnosis", "treatment", "medication"],
            "domains": ["@health", "@medical", "@hospital", "@clinic"],
            "weight": 1.1
        },
        ContentCategory.TRAVEL: {
            "keywords": ["flight", "hotel", "booking", "reservation", "trip", "vacation", 
                        "airline", "airport", "destination", "itinerary", "luggage"],
            "domains": ["@airline", "@hotel", "@booking", "@expedia", "@airbnb"],
            "weight": 1.0
        },
        ContentCategory.SHOPPING: {
            "keywords": ["order", "purchase", "shipping", "delivery", "cart", "checkout", 
                        "product", "item", "sale", "discount", "coupon", "store"],
            "domains": ["@amazon", "@shop", "@store", "@retail", "@ecommerce"],
            "weight": 1.0
        },
        ContentCategory.EDUCATION: {
            "keywords": ["course", "class", "student", "teacher", "grade", "assignment", 
                        "homework", "exam", "university", "college", "school", "learning"],
            "domains": ["@edu", "@university", "@college", "@school"],
            "weight": 1.0
        },
        ContentCategory.ENTERTAINMENT: {
            "keywords": ["movie", "music", "game", "show", "concert", "event", "ticket", 
                        "streaming", "netflix", "spotify", "entertainment", "fun"],
            "domains": ["@netflix", "@spotify", "@youtube", "@entertainment"],
            "weight": 0.8
        },
        ContentCategory.SOCIAL: {
            "keywords": ["friend", "family", "party", "birthday", "anniversary", "celebration", 
                        "social", "gathering", "invitation", "wedding", "dinner"],
            "domains": ["@facebook", "@twitter", "@instagram", "@social"],
            "weight": 0.9
        },
        ContentCategory.SPAM: {
            "keywords": ["free", "winner", "prize", "urgent", "limited time", "click here", 
                        "congratulations", "offer", "deal", "promotion", "lottery"],
            "domains": [],
            "weight": 0.7
        }
    }
    
    # Calculate scores for each category
    category_scores = {}
    
    for category, patterns in category_patterns.items():
        score = 0.0
        matched_keywords = []
        
        # Check keyword matches
        for keyword in patterns["keywords"]:
            if keyword in full_text:
                score += patterns["weight"]
                matched_keywords.append(keyword)
        
        # Check domain matches
        for domain in patterns["domains"]:
            if domain in sender.lower():
                score += patterns["weight"] * 2  # Domain matches are stronger indicators
        
        category_scores[category] = {
            "score": score,
            "keywords": matched_keywords
        }
    
    # Find best match
    if not any(score["score"] > 0 for score in category_scores.values()):
        return {
            "category": ContentCategory.PERSONAL,  # Default fallback
            "confidence": 0.3,
            "keywords": keywords[:5],
            "reasoning": "No specific patterns matched, defaulting to personal"
        }
    
    best_category = max(category_scores.keys(), key=lambda k: category_scores[k]["score"])
    max_score = category_scores[best_category]["score"]
    
    # Calculate confidence (normalize score)
    confidence = min(1.0, max_score / 5.0)  # Assuming max reasonable score is 5
    
    return {
        "category": best_category,
        "confidence": round(confidence, 2),
        "keywords": category_scores[best_category]["keywords"],
        "reasoning": f"Matched {len(category_scores[best_category]['keywords'])} relevant keywords"
    }


def determine_priority(content: str, subject: str = "", urgency_keywords: List[str] = None) -> Dict[str, Any]:
    """
    Determine content priority based on urgency indicators.
    
    Args:
        content: Content to analyze for priority
        subject: Subject line (optional)
        urgency_keywords: Custom urgency keywords (optional)
        
    Returns:
        Dict with priority level and reasoning
        
    Example:
        >>> determine_priority("URGENT: System down", "Critical Alert")
        {"priority": "urgent", "confidence": 0.95, "indicators": ["urgent", "critical"]}
    """
    if urgency_keywords is None:
        urgency_keywords = []
    
    full_text = f"{subject} {content}".lower()
    
    # Define priority indicators
    priority_indicators = {
        Priority.URGENT: {
            "keywords": ["urgent", "emergency", "critical", "asap", "immediate", "now", 
                        "crisis", "alert", "deadline today", "overdue"],
            "weight": 1.0
        },
        Priority.HIGH: {
            "keywords": ["important", "priority", "deadline", "soon", "tomorrow", 
                        "high priority", "needs attention", "action required"],
            "weight": 0.8
        },
        Priority.MEDIUM: {
            "keywords": ["meeting", "appointment", "reminder", "follow up", "review", 
                        "update", "scheduled"],
            "weight": 0.6
        },
        Priority.LOW: {
            "keywords": ["fyi", "information", "newsletter", "update", "notification", 
                        "optional", "when convenient"],
            "weight": 0.4
        }
    }
    
    # Add custom urgency keywords to urgent category
    if urgency_keywords:
        priority_indicators[Priority.URGENT]["keywords"].extend(urgency_keywords)
    
    # Calculate priority scores
    priority_scores = {}
    for priority, indicators in priority_indicators.items():
        score = 0.0
        matched_indicators = []
        
        for keyword in indicators["keywords"]:
            if keyword in full_text:
                score += indicators["weight"]
                matched_indicators.append(keyword)
        
        priority_scores[priority] = {
            "score": score,
            "indicators": matched_indicators
        }
    
    # Special cases for urgent detection
    if any(word in full_text for word in ["!!!", "urgent:", "emergency:", "critical:"]):
        priority_scores[Priority.URGENT]["score"] += 2.0
        priority_scores[Priority.URGENT]["indicators"].append("punctuation_emphasis")
    
    # Find highest priority with matches
    priorities_with_matches = {p: s for p, s in priority_scores.items() if s["score"] > 0}
    
    if not priorities_with_matches:
        return {
            "priority": Priority.NONE,
            "confidence": 0.5,
            "indicators": [],
            "reasoning": "No priority indicators found"
        }
    
    best_priority = max(priorities_with_matches.keys(), key=lambda p: priorities_with_matches[p]["score"])
    max_score = priorities_with_matches[best_priority]["score"]
    
    # Calculate confidence
    confidence = min(1.0, max_score / 3.0)  # Normalize to reasonable scale
    
    return {
        "priority": best_priority,
        "confidence": round(confidence, 2),
        "indicators": priority_scores[best_priority]["indicators"],
        "reasoning": f"Found {len(priority_scores[best_priority]['indicators'])} priority indicators"
    }


def extract_entities(content: str) -> Dict[str, List[str]]:
    """
    Extract entities like emails, dates, phone numbers from content.
    
    Args:
        content: Text content to analyze
        
    Returns:
        Dict with extracted entities by type
        
    Example:
        >>> extract_entities("Call john@company.com at 555-1234 by Friday")
        {"emails": ["john@company.com"], "phones": ["555-1234"], "dates": ["Friday"]}
    """
    if not content:
        return {"emails": [], "phones": [], "dates": [], "urls": [], "numbers": []}
    
    entities = {
        "emails": [],
        "phones": [],
        "dates": [],
        "urls": [],
        "numbers": []
    }
    
    # Email pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    entities["emails"] = re.findall(email_pattern, content)
    
    # Phone pattern (various formats)
    phone_pattern = r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b'
    entities["phones"] = re.findall(phone_pattern, content)
    
    # URL pattern
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    entities["urls"] = re.findall(url_pattern, content)
    
    # Date patterns (simple)
    date_patterns = [
        r'\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}\b'
    ]
    
    for pattern in date_patterns:
        entities["dates"].extend(re.findall(pattern, content, re.IGNORECASE))
    
    # Number pattern (excluding years and common codes)
    number_pattern = r'\b(?!19\d{2}|20\d{2})\d{3,}\b'
    entities["numbers"] = re.findall(number_pattern, content)
    
    return entities


def classify_email_type(subject: str, sender: str, content: str) -> Dict[str, Any]:
    """
    Classify email type based on sender, subject, and content patterns.
    
    Args:
        subject: Email subject line
        sender: Email sender address/name
        content: Email content
        
    Returns:
        Dict with email type classification
        
    Example:
        >>> classify_email_type("Re: Meeting", "boss@company.com", "Let's discuss...")
        {"type": "reply", "category": "work", "is_automated": False}
    """
    email_types = {
        "newsletter": ["newsletter", "unsubscribe", "update", "digest"],
        "notification": ["notification", "alert", "reminder", "automated"],
        "reply": ["re:", "reply", "response"],
        "forward": ["fwd:", "forward", "forwarded"],
        "invitation": ["invitation", "invite", "rsvp", "meeting request"],
        "receipt": ["receipt", "confirmation", "order", "purchase"],
        "marketing": ["offer", "sale", "promotion", "deal", "discount"],
        "automated": ["noreply", "no-reply", "donotreply", "automated"]
    }
    
    subject_lower = subject.lower()
    sender_lower = sender.lower()
    content_lower = content.lower()
    
    full_text = f"{subject_lower} {sender_lower} {content_lower}"
    
    # Detect email type
    detected_types = []
    for email_type, keywords in email_types.items():
        if any(keyword in full_text for keyword in keywords):
            detected_types.append(email_type)
    
    # Determine primary type
    if "automated" in detected_types or "noreply" in sender_lower:
        primary_type = "automated"
        is_automated = True
    elif "reply" in detected_types:
        primary_type = "reply"
        is_automated = False
    elif "forward" in detected_types:
        primary_type = "forward"
        is_automated = False
    elif detected_types:
        primary_type = detected_types[0]
        is_automated = primary_type in ["newsletter", "notification", "receipt", "marketing"]
    else:
        primary_type = "personal"
        is_automated = False
    
    # Get category classification
    category_result = classify_content_category(content, subject, sender)
    
    return {
        "type": primary_type,
        "category": category_result["category"],
        "is_automated": is_automated,
        "detected_types": detected_types,
        "confidence": category_result["confidence"]
    }


def generate_content_summary(content: str, max_length: int = 150) -> str:
    """
    Generate a concise summary of content.
    
    Args:
        content: Content to summarize
        max_length: Maximum length of summary
        
    Returns:
        str: Content summary
        
    Example:
        >>> generate_content_summary("Long email about meeting tomorrow at 2pm in conference room A")
        "Meeting scheduled for tomorrow at 2pm in conference room A"
    """
    if not content or len(content) <= max_length:
        return content
    
    # Simple extractive summarization
    sentences = re.split(r'[.!?]+', content)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return content[:max_length] + "..."
    
    # Prioritize first and last sentences, or use first sentence if short enough
    if len(sentences[0]) <= max_length:
        return sentences[0]
    
    # If first sentence is too long, truncate it
    return sentences[0][:max_length-3] + "..."


if __name__ == "__main__":
    # Test the content classification functions
    print("📊 Testing Hushh MCP Content Classification Operon")
    
    test_email = {
        "subject": "Urgent: Quarterly Sales Review Meeting Tomorrow",
        "sender": "manager@company.com",
        "content": "Please join the quarterly sales review meeting tomorrow at 2 PM in conference room A. We'll discuss Q4 results and planning for next quarter."
    }
    
    # Test classification
    classification = classify_content_category(
        test_email["content"], 
        test_email["subject"], 
        test_email["sender"]
    )
    print(f"✅ Category: {classification['category']} (confidence: {classification['confidence']})")
    
    # Test priority detection
    priority = determine_priority(test_email["content"], test_email["subject"])
    print(f"✅ Priority: {priority['priority']} (confidence: {priority['confidence']})")
    
    # Test email type classification
    email_type = classify_email_type(
        test_email["subject"],
        test_email["sender"], 
        test_email["content"]
    )
    print(f"✅ Email type: {email_type['type']}")
    
    # Test entity extraction
    entities = extract_entities(test_email["content"])
    print(f"✅ Entities extracted: {sum(len(v) for v in entities.values())} items")
    
    print("\n📊 Content classification operon ready for use!")
