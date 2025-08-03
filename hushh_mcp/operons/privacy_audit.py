#!/usr/bin/env python3
"""
Hushh MCP - Privacy Audit Operon
Privacy compliance and audit functions for Hushh MCP ecosystem.
Open-source contribution for privacy-first data handling.
"""

import json
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum


class PrivacyRiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DataType(str, Enum):
    EMAIL = "email"
    CALENDAR = "calendar"
    CONTACT = "contact"
    FINANCIAL = "financial"
    PERSONAL = "personal"
    SENSITIVE = "sensitive"


def assess_data_sensitivity(content: str, data_type: DataType) -> Dict[str, Any]:
    """
    Assess the sensitivity level of data content.
    
    Args:
        content: Data content to assess
        data_type: Type of data being assessed
        
    Returns:
        Dict with sensitivity assessment results
        
    Example:
        >>> assess_data_sensitivity("Meeting about salary review", DataType.EMAIL)
        {"risk_level": "high", "reasons": ["financial_keywords"], "score": 0.8}
    """
    if not content or not isinstance(content, str):
        return {"risk_level": PrivacyRiskLevel.LOW, "reasons": [], "score": 0.0}
    
    content_lower = content.lower()
    risk_factors = []
    risk_score = 0.0
    
    # Define sensitive keywords by category
    sensitive_patterns = {
        "financial": ["salary", "income", "bank", "credit card", "ssn", "tax", "payment", "invoice"],
        "personal": ["birthday", "address", "phone number", "personal", "private", "confidential"],
        "medical": ["doctor", "medical", "health", "diagnosis", "prescription", "hospital"],
        "legal": ["legal", "lawsuit", "court", "attorney", "contract", "agreement"],
        "security": ["password", "token", "key", "secret", "authentication", "login"],
        "biometric": ["fingerprint", "face", "voice", "dna", "biometric", "scan"]
    }
    
    # Check for sensitive patterns
    for category, keywords in sensitive_patterns.items():
        matches = sum(1 for keyword in keywords if keyword in content_lower)
        if matches > 0:
            risk_factors.append(f"{category}_keywords")
            risk_score += matches * 0.2
    
    # Additional risk factors
    if any(char.isdigit() for char in content) and len([c for c in content if c.isdigit()]) > 8:
        risk_factors.append("potential_id_numbers")
        risk_score += 0.3
    
    if "@" in content and "." in content:
        risk_factors.append("email_addresses")
        risk_score += 0.2
    
    if any(pattern in content_lower for pattern in ["urgent", "immediate", "confidential", "private"]):
        risk_factors.append("urgency_markers")
        risk_score += 0.1
    
    # Determine risk level
    if risk_score >= 0.8:
        risk_level = PrivacyRiskLevel.CRITICAL
    elif risk_score >= 0.6:
        risk_level = PrivacyRiskLevel.HIGH
    elif risk_score >= 0.3:
        risk_level = PrivacyRiskLevel.MEDIUM
    else:
        risk_level = PrivacyRiskLevel.LOW
    
    return {
        "risk_level": risk_level,
        "reasons": risk_factors,
        "score": min(1.0, risk_score),
        "data_type": data_type.value,
        "content_length": len(content)
    }


def generate_privacy_report(processed_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate a comprehensive privacy assessment report.
    
    Args:
        processed_items: List of processed data items to audit
        
    Returns:
        Dict with privacy assessment report
        
    Example:
        >>> items = [{"content": "salary info", "type": "email"}]
        >>> generate_privacy_report(items)
        {"total_items": 1, "risk_distribution": {...}, "recommendations": [...]}
    """
    if not processed_items:
        return {
            "total_items": 0,
            "risk_distribution": {},
            "recommendations": ["No data to audit"],
            "generated_at": datetime.now().isoformat()
        }
    
    risk_counts = {level.value: 0 for level in PrivacyRiskLevel}
    high_risk_items = []
    data_type_counts = {}
    total_score = 0.0
    
    for item in processed_items:
        content = item.get("content", "")
        data_type_str = item.get("type", "personal")
        
        # Convert string to DataType enum if needed
        if isinstance(data_type_str, str):
            try:
                data_type = DataType(data_type_str)
            except ValueError:
                data_type = DataType.PERSONAL  # fallback
        else:
            data_type = data_type_str
        
        assessment = assess_data_sensitivity(content, data_type)
        risk_level = assessment["risk_level"]
        
        risk_counts[risk_level] += 1
        total_score += assessment["score"]
        
        if risk_level in [PrivacyRiskLevel.HIGH, PrivacyRiskLevel.CRITICAL]:
            high_risk_items.append({
                "item_id": item.get("id", "unknown"),
                "risk_level": risk_level,
                "reasons": assessment["reasons"],
                "content_preview": content[:50] + "..." if len(content) > 50 else content
            })
        
        data_type_counts[data_type.value] = data_type_counts.get(data_type.value, 0) + 1
    
    # Generate recommendations
    recommendations = []
    avg_risk_score = total_score / len(processed_items)
    
    if avg_risk_score > 0.7:
        recommendations.append("High overall risk detected - consider additional encryption")
    
    if risk_counts[PrivacyRiskLevel.CRITICAL] > 0:
        recommendations.append("Critical risk items found - immediate review required")
    
    if risk_counts[PrivacyRiskLevel.HIGH] > len(processed_items) * 0.3:
        recommendations.append("High proportion of sensitive data - enable stricter access controls")
    
    if not recommendations:
        recommendations.append("Privacy risk levels are within acceptable ranges")
    
    return {
        "total_items": len(processed_items),
        "average_risk_score": round(avg_risk_score, 3),
        "risk_distribution": risk_counts,
        "data_type_distribution": data_type_counts,
        "high_risk_items": high_risk_items[:10],  # Limit to 10 for report size
        "recommendations": recommendations,
        "generated_at": datetime.now().isoformat(),
        "compliance_status": "compliant" if avg_risk_score < 0.5 else "needs_review"
    }


def audit_consent_compliance(consent_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Audit consent token compliance with Hushh MCP standards.
    
    Args:
        consent_records: List of consent token records to audit
        
    Returns:
        Dict with consent compliance audit results
        
    Example:
        >>> records = [{"scope": "vault.read.email", "expires_at": "2025-08-09", "status": "active"}]
        >>> audit_consent_compliance(records)
        {"total_consents": 1, "active_consents": 1, "compliance_issues": []}
    """
    if not consent_records:
        return {
            "total_consents": 0,
            "active_consents": 0,
            "expired_consents": 0,
            "compliance_issues": [],
            "audit_passed": True
        }
    
    active_count = 0
    expired_count = 0
    compliance_issues = []
    
    now = datetime.now()
    
    for record in consent_records:
        status = record.get("status", "unknown")
        expires_at = record.get("expires_at")
        scope = record.get("scope", "")
        agent_id = record.get("agent_id", "")
        
        # Check if consent is active
        if status == "active":
            active_count += 1
            
            # Check expiration
            if expires_at:
                try:
                    exp_date = datetime.fromisoformat(expires_at.replace('Z', ''))
                    if exp_date < now:
                        expired_count += 1
                        compliance_issues.append(f"Expired consent still marked as active: {agent_id}")
                except ValueError:
                    compliance_issues.append(f"Invalid expiration date format: {expires_at}")
        
        # Validate scope format
        if scope and not scope.startswith(("vault.", "agent.", "custom.")):
            compliance_issues.append(f"Non-standard scope format: {scope}")
        
        # Validate agent ID format
        if agent_id and not agent_id.startswith("agent_"):
            compliance_issues.append(f"Non-standard agent ID format: {agent_id}")
    
    audit_passed = len(compliance_issues) == 0
    
    return {
        "total_consents": len(consent_records),
        "active_consents": active_count,
        "expired_consents": expired_count,
        "compliance_issues": compliance_issues,
        "audit_passed": audit_passed,
        "audit_timestamp": now.isoformat()
    }


def generate_deletion_audit_log(user_id: str, deleted_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate an audit log for data deletion (right to be forgotten).
    
    Args:
        user_id: User ID whose data was deleted
        deleted_data: Details of what data was deleted
        
    Returns:
        Dict with deletion audit log
        
    Example:
        >>> generate_deletion_audit_log("user_123", {"emails": 50, "calendar": 25})
        {"user_id": "user_123", "deletion_summary": {...}, "verification_hash": "abc123..."}
    """
    deletion_log = {
        "user_id": user_id,
        "deletion_timestamp": datetime.now().isoformat(),
        "deletion_summary": deleted_data,
        "total_items_deleted": sum(v for v in deleted_data.values() if isinstance(v, int)),
        "deletion_method": "user_requested",
        "compliance_standard": "GDPR_Article_17"
    }
    
    # Create verification hash
    log_string = json.dumps(deletion_log, sort_keys=True)
    verification_hash = hashlib.sha256(log_string.encode()).hexdigest()
    deletion_log["verification_hash"] = verification_hash
    
    return deletion_log


def check_data_retention_compliance(data_items: List[Dict[str, Any]], max_retention_days: int = 90) -> Dict[str, Any]:
    """
    Check if data items comply with retention policies.
    
    Args:
        data_items: List of data items with timestamps
        max_retention_days: Maximum allowed retention period in days
        
    Returns:
        Dict with retention compliance results
        
    Example:
        >>> items = [{"id": "1", "created_at": "2025-07-01T10:00:00Z"}]
        >>> check_data_retention_compliance(items, 30)
        {"compliant_items": 1, "violation_items": 0, "cleanup_required": False}
    """
    if not data_items:
        return {
            "total_items": 0,
            "compliant_items": 0,
            "violation_items": 0,
            "cleanup_required": False,
            "violations": []
        }
    
    now = datetime.now()
    cutoff_date = now - timedelta(days=max_retention_days)
    
    compliant_count = 0
    violation_count = 0
    violations = []
    
    for item in data_items:
        created_at = item.get("created_at") or item.get("processed_at")
        item_id = item.get("id", "unknown")
        
        if not created_at:
            violations.append({
                "item_id": item_id,
                "issue": "missing_timestamp",
                "action_required": "add_timestamp_or_delete"
            })
            violation_count += 1
            continue
        
        try:
            created_date = datetime.fromisoformat(created_at.replace('Z', ''))
            
            if created_date < cutoff_date:
                violations.append({
                    "item_id": item_id,
                    "age_days": (now - created_date).days,
                    "action_required": "delete_or_obtain_extended_consent"
                })
                violation_count += 1
            else:
                compliant_count += 1
                
        except ValueError:
            violations.append({
                "item_id": item_id,
                "issue": "invalid_timestamp_format",
                "action_required": "fix_timestamp_or_delete"
            })
            violation_count += 1
    
    return {
        "total_items": len(data_items),
        "compliant_items": compliant_count,
        "violation_items": violation_count,
        "cleanup_required": violation_count > 0,
        "violations": violations[:20],  # Limit for report size
        "max_retention_days": max_retention_days,
        "audit_timestamp": now.isoformat()
    }


def anonymize_for_analytics(content: str) -> str:
    """
    Anonymize content while preserving analytical value.
    
    Args:
        content: Content to anonymize
        
    Returns:
        str: Anonymized content safe for analytics
        
    Example:
        >>> anonymize_for_analytics("Meeting with john.doe@company.com about salary")
        "Meeting with [EMAIL] about [FINANCIAL_TERM]"
    """
    import re
    
    if not content:
        return ""
    
    # Replace emails
    content = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', content)
    
    # Replace phone numbers
    content = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', content)
    
    # Replace potential SSNs
    content = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', content)
    
    # Replace financial terms with generic markers
    financial_terms = ['salary', 'income', 'payment', 'invoice', 'bill', 'cost', 'price']
    for term in financial_terms:
        content = re.sub(rf'\b{term}\b', '[FINANCIAL_TERM]', content, flags=re.IGNORECASE)
    
    # Replace names (simple pattern - can be enhanced)
    content = re.sub(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', '[NAME]', content)
    
    return content


if __name__ == "__main__":
    # Test the privacy audit functions
    print("🔒 Testing Hushh MCP Privacy Audit Operon")
    
    # Test data sensitivity assessment
    test_content = "Meeting with john@company.com about salary review and credit card processing"
    assessment = assess_data_sensitivity(test_content, DataType.EMAIL)
    print(f"✅ Sensitivity assessment: {assessment['risk_level']} (score: {assessment['score']})")
    
    # Test anonymization
    anonymized = anonymize_for_analytics(test_content)
    print(f"✅ Anonymized content: {anonymized}")
    
    print("\n🔒 Privacy audit operon ready for use!")
