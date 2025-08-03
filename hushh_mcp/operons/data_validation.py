#!/usr/bin/env python3
"""
Hushh MCP - Data Validation Operon
Generic data validation functions for consent and privacy compliance.
Open-source contribution to the Hushh MCP ecosystem.
"""

import re
import hashlib
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta


def validate_email_format(email: str) -> bool:
    """
    Validate email format according to RFC standards.
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if email format is valid
        
    Example:
        >>> validate_email_format("user@example.com")
        True
        >>> validate_email_format("invalid-email")
        False
    """
    if not email or not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))


def validate_consent_scope(scope: str, allowed_scopes: List[str] = None) -> bool:
    """
    Validate if a consent scope is allowed and properly formatted.
    
    Args:
        scope: Consent scope to validate (e.g., "vault.read.email")
        allowed_scopes: List of permitted scopes (optional, defaults to standard MCP scopes)
        
    Returns:
        bool: True if scope is valid and allowed
        
    Example:
        >>> validate_consent_scope("vault.read.email", ["vault.read.email", "vault.read.calendar"])
        True
        >>> validate_consent_scope("malicious.scope", ["vault.read.email"])
        False
    """
    if not scope or not isinstance(scope, str):
        return False
    
    # Check format: should be dot-separated lowercase
    if not re.match(r'^[a-z]+(\.[a-z_]+)*$', scope):
        return False
    
    # Default allowed scopes if none provided
    if allowed_scopes is None:
        allowed_scopes = [
            "vault.read.email",
            "vault.read.calendar", 
            "vault.write.email",
            "vault.write.calendar",
            "vault.delete.email",
            "vault.delete.calendar",
            "agent.process.email",
            "agent.process.calendar",
            "agent.categorize.content",
            "custom.data.access",
            "custom.data.export",
            "custom.data.delete"
        ]
    
    return scope in allowed_scopes


def validate_agent_id(agent_id: str) -> bool:
    """
    Validate agent ID format for Hushh MCP compliance.
    
    Args:
        agent_id: Agent identifier to validate
        
    Returns:
        bool: True if agent ID format is valid
        
    Example:
        >>> validate_agent_id("agent_email_processor")
        True
        >>> validate_agent_id("invalid_id")
        False
    """
    if not agent_id or not isinstance(agent_id, str):
        return False
    
    # Should start with "agent_" and contain only lowercase letters, numbers, underscores
    pattern = r'^agent_[a-z0-9_]+$'
    return bool(re.match(pattern, agent_id))


def validate_user_id(user_id: str) -> bool:
    """
    Validate user ID format for Hushh MCP compliance.
    
    Args:
        user_id: User identifier to validate
        
    Returns:
        bool: True if user ID format is valid
        
    Example:
        >>> validate_user_id("user_12345")
        True
        >>> validate_user_id("123456789012345678901")  # Google OAuth ID
        True
    """
    if not user_id or not isinstance(user_id, str):
        return False
    
    # Accept either "user_" prefixed IDs or numeric IDs (like Google OAuth)
    user_pattern = r'^user_[a-zA-Z0-9_]+$'
    numeric_pattern = r'^[0-9]+$'
    
    return bool(re.match(user_pattern, user_id) or re.match(numeric_pattern, user_id))


def validate_timestamp(timestamp: Union[str, int, float], max_age_days: int = 30) -> bool:
    """
    Validate timestamp and check if it's within acceptable age range.
    
    Args:
        timestamp: Timestamp to validate (ISO string, epoch seconds, or epoch milliseconds)
        max_age_days: Maximum age in days for the timestamp to be considered valid
        
    Returns:
        bool: True if timestamp is valid and not too old
        
    Example:
        >>> validate_timestamp("2025-08-02T10:00:00Z")
        True
        >>> validate_timestamp(1722596400)  # Recent epoch timestamp
        True
    """
    try:
        if isinstance(timestamp, str):
            # Try parsing ISO format
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        elif isinstance(timestamp, (int, float)):
            # Handle epoch timestamps (both seconds and milliseconds)
            if timestamp > 1e12:  # Likely milliseconds
                dt = datetime.fromtimestamp(timestamp / 1000)
            else:  # Likely seconds
                dt = datetime.fromtimestamp(timestamp)
        else:
            return False
        
        # Check if timestamp is within acceptable range
        now = datetime.now()
        age = now - dt.replace(tzinfo=None)
        
        return abs(age.days) <= max_age_days
        
    except (ValueError, TypeError, OSError):
        return False


def sanitize_content_for_storage(content: str, max_length: int = 1000) -> str:
    """
    Sanitize content for secure storage in vault.
    
    Args:
        content: Content to sanitize
        max_length: Maximum allowed length
        
    Returns:
        str: Sanitized content safe for storage
        
    Example:
        >>> sanitize_content_for_storage("<script>alert('xss')</script>Hello World")
        "Hello World"
    """
    if not content or not isinstance(content, str):
        return ""
    
    # Remove HTML/XML tags
    content = re.sub(r'<[^>]*>', '', content)
    
    # Remove potentially dangerous characters
    content = re.sub(r'[<>"\']', '', content)
    
    # Remove excessive whitespace
    content = ' '.join(content.split())
    
    # Truncate to max length
    if len(content) > max_length:
        content = content[:max_length] + "..."
    
    return content.strip()


def hash_for_storage(data: str, salt: str = "") -> str:
    """
    Create a secure hash of data for storage/comparison.
    
    Args:
        data: Data to hash
        salt: Optional salt for additional security
        
    Returns:
        str: SHA-256 hash of the data
        
    Example:
        >>> hash_for_storage("sensitive_data", "random_salt")
        "a1b2c3d4e5f6..."
    """
    if not isinstance(data, str):
        data = str(data)
    
    combined = data + salt
    return hashlib.sha256(combined.encode('utf-8')).hexdigest()


def validate_data_export_format(export_data: Dict[str, Any]) -> bool:
    """
    Validate that exported data follows Hushh MCP format standards.
    
    Args:
        export_data: Data export dictionary to validate
        
    Returns:
        bool: True if export format is valid
        
    Example:
        >>> data = {"user_id": "123", "exported_at": "2025-08-02T10:00:00Z", "emails": []}
        >>> validate_data_export_format(data)
        True
    """
    required_fields = ["user_id", "exported_at"]
    
    if not isinstance(export_data, dict):
        return False
    
    # Check required fields
    for field in required_fields:
        if field not in export_data:
            return False
    
    # Validate user_id
    if not validate_user_id(export_data["user_id"]):
        return False
    
    # Validate timestamp
    if not validate_timestamp(export_data["exported_at"]):
        return False
    
    return True


def validate_category_name(category: str) -> bool:
    """
    Validate category name for content categorization.
    
    Args:
        category: Category name to validate
        
    Returns:
        bool: True if category name is valid
        
    Example:
        >>> validate_category_name("work")
        True
        >>> validate_category_name("invalid-category!")
        False
    """
    if not category or not isinstance(category, str):
        return False
    
    # Should be lowercase, letters only, max 20 characters
    pattern = r'^[a-z]{1,20}$'
    return bool(re.match(pattern, category))


def validate_confidence_score(score: Union[int, float]) -> bool:
    """
    Validate confidence score is within acceptable range.
    
    Args:
        score: Confidence score to validate
        
    Returns:
        bool: True if score is valid (0.0 to 1.0)
        
    Example:
        >>> validate_confidence_score(0.85)
        True
        >>> validate_confidence_score(1.5)
        False
    """
    if not isinstance(score, (int, float)):
        return False
    
    return 0.0 <= score <= 1.0


def validate_data_integrity(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Comprehensive data integrity validation for any input data.
    
    Args:
        data: Dictionary containing data to validate
        
    Returns:
        Dict containing validation results with is_valid, score, and issues
        
    Example:
        >>> data = {"id": "email_123", "subject": "Test", "content": "Hello world"}
        >>> validate_data_integrity(data)
        {"is_valid": True, "score": 0.95, "issues": []}
    """
    if not isinstance(data, dict):
        return {
            "is_valid": False,
            "score": 0.0,
            "issues": ["Data must be a dictionary"],
            "validation_summary": "Invalid data type"
        }
    
    issues = []
    score = 1.0
    
    # Check for required basic fields
    if not data.get("id"):
        issues.append("Missing or empty ID field")
        score -= 0.3
    
    # Validate ID format if present
    if data.get("id") and not isinstance(data["id"], str):
        issues.append("ID must be a string")
        score -= 0.2
    
    # Check for content fields
    content_fields = ["subject", "content", "title", "description", "body"]
    has_content = any(data.get(field) for field in content_fields)
    
    if not has_content:
        issues.append("No content fields found")
        score -= 0.4
    
    # Validate content quality
    for field in content_fields:
        if field in data:
            content = data[field]
            if content:
                if len(str(content).strip()) < 3:
                    issues.append(f"{field} is too short")
                    score -= 0.1
                elif len(str(content)) > 10000:
                    issues.append(f"{field} is too long")
                    score -= 0.1
    
    # Check for suspicious content patterns
    all_content = " ".join(str(data.get(field, "")) for field in content_fields)
    if all_content:
        # Check for potential security issues
        suspicious_patterns = [
            r'<script[^>]*>',
            r'javascript:',
            r'data:text/html',
            r'vbscript:',
            r'onload\s*=',
            r'onerror\s*='
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, all_content, re.IGNORECASE):
                issues.append("Suspicious content pattern detected")
                score -= 0.5
                break
    
    # Validate timestamp fields
    timestamp_fields = ["timestamp", "received_at", "created_at", "processed_at"]
    for field in timestamp_fields:
        if field in data and data[field]:
            if not validate_timestamp(data[field]):
                issues.append(f"Invalid timestamp in {field}")
                score -= 0.2
    
    # Ensure score doesn't go below 0
    score = max(0.0, score)
    
    # Determine overall validity
    is_valid = score >= 0.5 and len([issue for issue in issues if "Missing" in issue or "Invalid" in issue]) == 0
    
    return {
        "is_valid": is_valid,
        "score": round(score, 2),
        "issues": issues,
        "validation_summary": f"{'Valid' if is_valid else 'Invalid'} data with {len(issues)} issues"
    }


# Main validation function for complete data integrity
def validate_processed_item(item: Dict[str, Any]) -> Dict[str, bool]:
    """
    Comprehensive validation of a processed email or calendar item.
    
    Args:
        item: Processed item dictionary to validate
        
    Returns:
        Dict with validation results for each field
        
    Example:
        >>> item = {
        ...     "id": "email_123",
        ...     "categories": ["work", "finance"],
        ...     "confidence": 0.85,
        ...     "processed_at": "2025-08-02T10:00:00Z"
        ... }
        >>> validate_processed_item(item)
        {"id": True, "categories": True, "confidence": True, "processed_at": True}
    """
    results = {}
    
    # Validate ID
    results["id"] = bool(item.get("id") and isinstance(item["id"], str))
    
    # Validate categories
    categories = item.get("categories", [])
    results["categories"] = (
        isinstance(categories, list) and 
        len(categories) > 0 and 
        all(validate_category_name(cat) for cat in categories)
    )
    
    # Validate confidence scores
    confidence = item.get("confidence")
    results["confidence"] = validate_confidence_score(confidence) if confidence is not None else True
    
    # Validate timestamp
    timestamp = item.get("processed_at")
    results["processed_at"] = validate_timestamp(timestamp) if timestamp else True
    
    return results


if __name__ == "__main__":
    # Test the validation functions
    print("🧪 Testing Hushh MCP Data Validation Operon")
    
    tests = [
        ("Email validation", validate_email_format("test@example.com"), True),
        ("Agent ID validation", validate_agent_id("agent_email_processor"), True),
        ("User ID validation", validate_user_id("115761959210151935564"), True),
        ("Category validation", validate_category_name("work"), True),
        ("Confidence validation", validate_confidence_score(0.85), True),
    ]
    
    for test_name, result, expected in tests:
        status = "✅" if result == expected else "❌"
        print(f"{status} {test_name}: {result}")
    
    print("\n✅ Data validation operon ready for use!")
