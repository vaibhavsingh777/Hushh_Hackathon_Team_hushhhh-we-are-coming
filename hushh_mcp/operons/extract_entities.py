# hushh_mcp/operons/extract_entities.py

from typing import List, Dict, Any
import re
from datetime import datetime


def extract_entities(content: str) -> Dict[str, List[str]]:
    """
    Extract entities from text content using pattern matching.
    Identifies dates, times, emails, phones, money amounts, etc.
    
    Args:
        content: Text content to analyze
        
    Returns:
        Dict with entity types as keys and lists of found entities as values
    """
    entities = {
        "emails": [],
        "phones": [],
        "dates": [],
        "times": [],
        "money": [],
        "urls": [],
        "addresses": [],
        "names": [],
        "companies": []
    }
    
    if not content:
        return entities
    
    # Email extraction
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    entities["emails"] = re.findall(email_pattern, content)
    
    # Phone number extraction
    phone_pattern = r'\b(?:\+?1[-.\s]?)?(?:\(?[0-9]{3}\)?[-.\s]?)?[0-9]{3}[-.\s]?[0-9]{4}\b'
    entities["phones"] = re.findall(phone_pattern, content)
    
    # Date extraction (various formats)
    date_patterns = [
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # MM/DD/YYYY or MM-DD-YYYY
        r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',    # YYYY/MM/DD or YYYY-MM-DD
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b',  # Month DD, YYYY
        r'\b\d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}\b'     # DD Month YYYY
    ]
    
    for pattern in date_patterns:
        entities["dates"].extend(re.findall(pattern, content, re.IGNORECASE))
    
    # Time extraction
    time_pattern = r'\b\d{1,2}:\d{2}(?::\d{2})?(?:\s?[AaPp][Mm])?\b'
    entities["times"] = re.findall(time_pattern, content)
    
    # Money extraction
    money_patterns = [
        r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?',  # $1,000.00
        r'\b\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s*(?:dollars?|USD|usd)\b',  # 1000 dollars
        r'\b(?:USD|usd|\$)\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?\b'  # USD 1000
    ]
    
    for pattern in money_patterns:
        entities["money"].extend(re.findall(pattern, content, re.IGNORECASE))
    
    # URL extraction
    url_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
    entities["urls"] = re.findall(url_pattern, content)
    
    # Simple address extraction (US format)
    address_pattern = r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Place|Pl)\b'
    entities["addresses"] = re.findall(address_pattern, content, re.IGNORECASE)
    
    # Name extraction (simple heuristic)
    entities["names"] = extract_person_names(content)
    
    # Company extraction (simple heuristic)
    entities["companies"] = extract_company_names(content)
    
    # Remove duplicates and empty entries
    for entity_type in entities:
        entities[entity_type] = list(set([e.strip() for e in entities[entity_type] if e.strip()]))
    
    return entities


def extract_person_names(content: str) -> List[str]:
    """
    Extract potential person names using simple heuristics.
    """
    names = []
    
    # Pattern for capitalized words that might be names
    # This is a simple heuristic and may have false positives
    name_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
    potential_names = re.findall(name_pattern, content)
    
    # Filter out common false positives
    common_false_positives = {
        'New York', 'Los Angeles', 'San Francisco', 'Las Vegas', 
        'United States', 'North America', 'South America',
        'Microsoft Office', 'Google Drive', 'Apple Music'
    }
    
    for name in potential_names:
        if name not in common_false_positives and len(name.split()) == 2:
            names.append(name)
    
    return names


def extract_company_names(content: str) -> List[str]:
    """
    Extract potential company names using simple heuristics.
    """
    companies = []
    
    # Common company suffixes
    company_patterns = [
        r'\b[A-Z][A-Za-z\s]+(?:Inc\.?|Corp\.?|LLC|Ltd\.?|Co\.?)\b',
        r'\b[A-Z][A-Za-z\s]+(?:Corporation|Company|Incorporated|Limited)\b'
    ]
    
    for pattern in company_patterns:
        companies.extend(re.findall(pattern, content))
    
    # Well-known company names (could be expanded)
    known_companies = [
        'Google', 'Microsoft', 'Apple', 'Amazon', 'Facebook', 'Meta',
        'Netflix', 'Spotify', 'Twitter', 'LinkedIn', 'Instagram',
        'YouTube', 'WhatsApp', 'Telegram', 'Zoom', 'Slack'
    ]
    
    for company in known_companies:
        if company in content:
            companies.append(company)
    
    return list(set(companies))


def extract_calendar_events(content: str) -> List[Dict[str, Any]]:
    """
    Extract potential calendar events from content.
    """
    events = []
    
    # Look for patterns that suggest events
    event_keywords = ['meeting', 'appointment', 'call', 'conference', 'presentation', 'interview']
    
    sentences = content.split('.')
    for sentence in sentences:
        sentence = sentence.strip()
        if any(keyword in sentence.lower() for keyword in event_keywords):
            # Extract time and date from the sentence
            times = re.findall(r'\b\d{1,2}:\d{2}(?:\s?[AaPp][Mm])?\b', sentence)
            dates = re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', sentence)
            
            if times or dates:
                events.append({
                    'description': sentence,
                    'times': times,
                    'dates': dates
                })
    
    return events


def extract_action_items(content: str) -> List[str]:
    """
    Extract potential action items or todos from content.
    """
    action_items = []
    
    # Action keywords that suggest todos
    action_keywords = [
        'need to', 'have to', 'must', 'should', 'remember to',
        'don\'t forget', 'todo', 'to do', 'action item', 'follow up'
    ]
    
    sentences = content.split('.')
    for sentence in sentences:
        sentence = sentence.strip()
        if any(keyword in sentence.lower() for keyword in action_keywords):
            action_items.append(sentence)
    
    return action_items


def extract_contact_info(content: str) -> Dict[str, Any]:
    """
    Extract contact information from content.
    """
    contact_info = {}
    
    entities = extract_entities(content)
    
    contact_info['emails'] = entities['emails']
    contact_info['phones'] = entities['phones']
    contact_info['names'] = entities['names']
    contact_info['addresses'] = entities['addresses']
    
    return contact_info
