# hushh_mcp/operons/create_note.py

from typing import Dict, Any, List, Optional
import uuid
import time
import json
import re
from datetime import datetime


def generate_structured_note(
    content: str,
    title: str = "",
    tags: List[str] = None,
    category: str = "general"
) -> Dict[str, Any]:
    """
    Generate a structured note from content with auto-enhancement.
    
    Args:
        content: Note content
        title: Note title (auto-generated if empty)
        tags: List of tags (auto-generated if empty)
        category: Note category
        
    Returns:
        Dict with structured note data
    """
    if tags is None:
        tags = []
    
    # Generate unique note ID
    note_id = f"note_{uuid.uuid4().hex[:8]}"
    
    # Auto-generate title if not provided
    if not title.strip():
        title = auto_generate_title(content)
    
    # Auto-generate tags if not provided
    if not tags:
        tags = auto_generate_tags(content)
    
    # Extract metadata from content
    metadata = extract_note_metadata(content)
    
    # Structure the content
    structured_content = structure_content(content)
    
    # Create note object
    note = {
        "note_id": note_id,
        "title": title,
        "content": content,
        "structured_content": structured_content,
        "tags": tags,
        "category": category,
        "metadata": metadata,
        "created_at": int(time.time() * 1000),
        "updated_at": int(time.time() * 1000),
        "word_count": len(content.split()),
        "char_count": len(content),
        "estimated_read_time": calculate_read_time(content),
        "format": "markdown" if is_markdown_content(content) else "plain_text"
    }
    
    # Store note
    store_note(note)
    
    print(f"📝 Structured note created: {title}")
    return note


def auto_generate_title(content: str, max_length: int = 50) -> str:
    """
    Auto-generate a title from content.
    """
    if not content.strip():
        return "Untitled Note"
    
    # Try to find an obvious title (first line if it looks like a title)
    lines = content.strip().split('\n')
    first_line = lines[0].strip()
    
    # Check if first line looks like a title
    if (len(first_line) < 100 and 
        not first_line.endswith('.') and 
        len(lines) > 1):
        return first_line[:max_length]
    
    # Extract first sentence
    sentences = re.split(r'[.!?]+', content)
    if sentences:
        first_sentence = sentences[0].strip()
        if len(first_sentence) <= max_length:
            return first_sentence
        else:
            # Truncate to word boundary
            words = first_sentence.split()
            title_words = []
            char_count = 0
            
            for word in words:
                if char_count + len(word) + 1 > max_length:
                    break
                title_words.append(word)
                char_count += len(word) + 1
            
            return ' '.join(title_words) + '...' if title_words else "Note"
    
    return "Note"


def auto_generate_tags(content: str, max_tags: int = 5) -> List[str]:
    """
    Auto-generate tags from content.
    """
    tags = []
    content_lower = content.lower()
    
    # Predefined tag patterns
    tag_patterns = {
        "meeting": ["meeting", "call", "conference", "discussion"],
        "idea": ["idea", "concept", "thought", "brainstorm"],
        "todo": ["todo", "task", "action", "need to", "must do"],
        "personal": ["personal", "private", "family", "friend"],
        "work": ["work", "project", "business", "office", "client"],
        "research": ["research", "study", "analysis", "investigate"],
        "finance": ["money", "budget", "expense", "income", "financial"],
        "health": ["health", "medical", "doctor", "exercise", "wellness"],
        "travel": ["travel", "trip", "vacation", "flight", "hotel"],
        "learning": ["learn", "course", "tutorial", "education", "skill"]
    }
    
    # Check for pattern matches
    for tag, keywords in tag_patterns.items():
        if any(keyword in content_lower for keyword in keywords):
            tags.append(tag)
    
    # Extract potential tags from content (capitalized words)
    capitalized_words = re.findall(r'\b[A-Z][a-z]+\b', content)
    for word in capitalized_words:
        if (word.lower() not in ["the", "and", "but", "or", "so", "yet"] and
            len(word) > 2 and
            word.lower() not in [t.lower() for t in tags]):
            tags.append(word.lower())
    
    # Limit number of tags
    return tags[:max_tags]


def extract_note_metadata(content: str) -> Dict[str, Any]:
    """
    Extract metadata from note content.
    """
    metadata = {
        "has_links": bool(re.search(r'https?://', content)),
        "has_emails": bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)),
        "has_phone_numbers": bool(re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', content)),
        "has_dates": bool(re.search(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', content)),
        "has_times": bool(re.search(r'\b\d{1,2}:\d{2}(?:\s?[AaPp][Mm])?\b', content)),
        "has_money": bool(re.search(r'\$\d+', content)),
        "language": detect_language(content),
        "tone": detect_tone(content),
        "urgency": detect_urgency(content)
    }
    
    return metadata


def structure_content(content: str) -> Dict[str, Any]:
    """
    Structure content into logical sections.
    """
    structured = {
        "sections": [],
        "bullet_points": [],
        "numbered_lists": [],
        "quotes": [],
        "code_blocks": [],
        "links": []
    }
    
    lines = content.split('\n')
    current_section = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Detect section headers
        if line.startswith('#') or (len(line) < 50 and ':' in line):
            if current_section:
                structured["sections"].append(current_section)
            current_section = {
                "header": line,
                "content": []
            }
        
        # Detect bullet points
        elif line.startswith(('-', '*', '•')):
            structured["bullet_points"].append(line[1:].strip())
            if current_section:
                current_section["content"].append(line)
        
        # Detect numbered lists
        elif re.match(r'^\d+\.', line):
            structured["numbered_lists"].append(line)
            if current_section:
                current_section["content"].append(line)
        
        # Detect quotes
        elif line.startswith('>'):
            structured["quotes"].append(line[1:].strip())
        
        # Detect code blocks
        elif line.startswith('```') or line.startswith('    '):
            structured["code_blocks"].append(line)
        
        else:
            if current_section:
                current_section["content"].append(line)
    
    # Add last section
    if current_section:
        structured["sections"].append(current_section)
    
    # Extract links
    links = re.findall(r'https?://[^\s]+', content)
    structured["links"] = links
    
    return structured


def calculate_read_time(content: str, words_per_minute: int = 200) -> int:
    """
    Calculate estimated reading time in minutes.
    """
    word_count = len(content.split())
    read_time = max(1, round(word_count / words_per_minute))
    return read_time


def is_markdown_content(content: str) -> bool:
    """
    Detect if content is in Markdown format.
    """
    markdown_indicators = [
        r'^#+\s',  # Headers
        r'^\*\s',  # Bullet points
        r'^\d+\.\s',  # Numbered lists
        r'`[^`]+`',  # Inline code
        r'```',  # Code blocks
        r'\[.*\]\(.*\)',  # Links
        r'^\>',  # Quotes
    ]
    
    for pattern in markdown_indicators:
        if re.search(pattern, content, re.MULTILINE):
            return True
    
    return False


def detect_language(content: str) -> str:
    """
    Simple language detection (placeholder).
    """
    # This is a placeholder - in production, use a proper language detection library
    # like langdetect or TextBlob
    
    # Simple heuristic based on common words
    english_words = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'this', 'that']
    content_words = content.lower().split()
    
    english_score = sum(1 for word in content_words if word in english_words)
    
    if len(content_words) > 0 and (english_score / len(content_words)) > 0.1:
        return "english"
    else:
        return "unknown"


def detect_tone(content: str) -> str:
    """
    Detect tone of the content.
    """
    content_lower = content.lower()
    
    # Positive tone indicators
    positive_words = ['great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'good', 'happy', 'excited']
    positive_score = sum(1 for word in positive_words if word in content_lower)
    
    # Negative tone indicators
    negative_words = ['bad', 'terrible', 'awful', 'horrible', 'sad', 'angry', 'frustrated', 'disappointed']
    negative_score = sum(1 for word in negative_words if word in content_lower)
    
    # Urgent tone indicators
    urgent_words = ['urgent', 'asap', 'immediately', 'emergency', 'critical', 'important']
    urgent_score = sum(1 for word in urgent_words if word in content_lower)
    
    if urgent_score > 0:
        return "urgent"
    elif positive_score > negative_score:
        return "positive"
    elif negative_score > positive_score:
        return "negative"
    else:
        return "neutral"


def detect_urgency(content: str) -> str:
    """
    Detect urgency level of the content.
    """
    content_lower = content.lower()
    
    high_urgency = ['urgent', 'asap', 'immediately', 'emergency', 'critical', 'deadline today']
    medium_urgency = ['important', 'soon', 'deadline', 'priority', 'quick']
    
    if any(word in content_lower for word in high_urgency):
        return "high"
    elif any(word in content_lower for word in medium_urgency):
        return "medium"
    else:
        return "low"


def store_note(note: Dict[str, Any]) -> bool:
    """
    Store note in persistent storage.
    """
    # For demo purposes - in production, integrate with:
    # - Note-taking apps (Notion, Evernote, OneNote)
    # - Local database
    # - Cloud storage
    
    print(f"📝 Storing note: {note['note_id']}")
    return True


def update_note(note_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update an existing note.
    """
    # Retrieve existing note (simulated)
    existing_note = get_note_by_id(note_id)
    if not existing_note:
        raise ValueError(f"Note not found: {note_id}")
    
    # Apply updates
    updated_note = existing_note.copy()
    updated_note.update(updates)
    updated_note["updated_at"] = int(time.time() * 1000)
    
    # Re-process if content changed
    if "content" in updates:
        updated_note["tags"] = auto_generate_tags(updates["content"])
        updated_note["metadata"] = extract_note_metadata(updates["content"])
        updated_note["structured_content"] = structure_content(updates["content"])
    
    # Store updated note
    store_note(updated_note)
    
    print(f"✅ Note updated: {note_id}")
    return updated_note


def get_note_by_id(note_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve note by ID.
    """
    # Placeholder for production implementation
    return {
        "note_id": note_id,
        "title": "Sample Note",
        "content": "Sample content",
        "created_at": int(time.time() * 1000)
    }
