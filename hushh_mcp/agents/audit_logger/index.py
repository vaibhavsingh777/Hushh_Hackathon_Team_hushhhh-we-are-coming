# hushh_mcp/agents/audit_logger/index.py

from typing import Dict, Any, List, Optional
import time
import json
import sqlite3
import os
from datetime import datetime, timedelta
from hushh_mcp.consent.token import validate_token
from hushh_mcp.constants import ConsentScope
from hushh_mcp.types import UserID


class AuditLoggerAgent:
    """
    Specialized agent for audit logging and compliance tracking.
    Records every automation with timestamp and token ID for trust verification.
    """

    def __init__(self, agent_id: str = "agent_audit_logger"):
        self.agent_id = agent_id
        self.db_path = os.getenv("DATABASE_URL", "sqlite:///./pda_audit.db").replace("sqlite:///", "")
        self.init_database()

    def init_database(self):
        """Initialize SQLite database for audit logs."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create audit logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp INTEGER NOT NULL,
                    user_id TEXT NOT NULL,
                    token_id TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    action_details TEXT,
                    status TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    session_id TEXT,
                    data_accessed TEXT,
                    consent_scope TEXT,
                    created_at INTEGER DEFAULT (strftime('%s', 'now') * 1000)
                )
            ''')
            
            # Create compliance events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS compliance_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    compliance_status TEXT NOT NULL,
                    violation_details TEXT,
                    resolution_status TEXT DEFAULT 'pending',
                    created_at INTEGER DEFAULT (strftime('%s', 'now') * 1000)
                )
            ''')
            
            # Create indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_user_id ON audit_logs(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_agent_id ON audit_logs(agent_id)')
            
            conn.commit()
            conn.close()
            print("✅ Audit database initialized")
            
        except Exception as e:
            print(f"❌ Failed to initialize audit database: {str(e)}")

    async def log_activity(self, user_id: str = None, action: str = None, details: Dict[str, Any] = None, log_entry: Dict[str, Any] = None) -> bool:
        """
        Log agent activity for audit trail.
        
        Args:
            user_id: User ID for the activity (compatibility mode)
            action: Action type (compatibility mode)
            details: Action details (compatibility mode)
            log_entry: Dict containing complete log details (MCP protocol mode)
            
        Returns:
            Bool indicating success
        """
        # Support both calling styles for compatibility
        if log_entry is None:
            # Compatibility mode - convert parameters to log_entry format
            log_entry = {
                "user_id": user_id or "unknown",
                "action_type": action or "unknown_action",
                "action_details": details or {},
                "status": "logged",
                "agent_id": self.agent_id,
                "timestamp": int(time.time() * 1000)
            }
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Ensure required fields
            timestamp = log_entry.get("timestamp", int(time.time() * 1000))
            user_id = log_entry.get("user_id", "unknown")
            token_id = log_entry.get("token_id", "unknown")
            agent_id = log_entry.get("agent_id", "unknown")
            action_type = log_entry.get("action_type", "unknown")
            status = log_entry.get("status", "unknown")
            
            cursor.execute('''
                INSERT INTO audit_logs 
                (timestamp, user_id, token_id, agent_id, action_type, action_details, 
                 status, ip_address, user_agent, session_id, data_accessed, consent_scope)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp,
                user_id,
                token_id,
                agent_id,
                action_type,
                json.dumps(log_entry.get("action_details", {})),
                status,
                log_entry.get("ip_address", "unknown"),
                log_entry.get("user_agent", "unknown"),
                log_entry.get("session_id", "unknown"),
                json.dumps(log_entry.get("data_accessed", [])),
                log_entry.get("consent_scope", "unknown")
            ))
            
            conn.commit()
            conn.close()
            
            print(f"📝 Activity logged: {action_type} by {agent_id} for {user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to log activity: {str(e)}")
            return False

    def log_consent_event(self, user_id: UserID, token_str: str, event_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Log consent-related events with validation.
        """
        # Validate consent for logging (meta-logging)
        valid, reason, token = validate_token(token_str, expected_scope=ConsentScope.CUSTOM_TEMPORARY)
        
        if not valid:
            raise PermissionError(f"❌ Audit logging denied: {reason}")

        log_entry = {
            "timestamp": int(time.time() * 1000),
            "user_id": user_id,
            "token_id": token.signature[:8] if token else "invalid",
            "agent_id": self.agent_id,
            "action_type": "consent_event",
            "action_details": event_details,
            "status": "logged",
            "consent_scope": token.scope if token else "none"
        }
        
        success = self.log_activity(log_entry)
        
        return {
            "logged": success,
            "log_id": f"log_{int(time.time() * 1000)}",
            "timestamp": log_entry["timestamp"]
        }

    def log_compliance_violation(self, violation_details: Dict[str, Any]) -> bool:
        """
        Log compliance violations for review.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO compliance_events 
                (timestamp, event_type, user_id, agent_id, compliance_status, violation_details)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                int(time.time() * 1000),
                violation_details.get("event_type", "unknown_violation"),
                violation_details.get("user_id", "unknown"),
                violation_details.get("agent_id", "unknown"),
                "violation",
                json.dumps(violation_details)
            ))
            
            conn.commit()
            conn.close()
            
            print(f"🚨 Compliance violation logged: {violation_details.get('event_type', 'unknown')}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to log compliance violation: {str(e)}")
            return False

    async def get_audit_trail(self, user_id: str, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Retrieve audit trail for a user (simplified version for main.py compatibility).
        
        Args:
            user_id: User ID to get audit trail for
            limit: Maximum number of entries to return
            offset: Number of entries to skip
            
        Returns:
            List of audit entries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT timestamp, agent_id, action_type, status, action_details, consent_scope
                FROM audit_logs 
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
            ''', (user_id, limit, offset))
            
            rows = cursor.fetchall()
            conn.close()
            
            # Format results
            audit_entries = []
            for row in rows:
                audit_entries.append({
                    "timestamp": row[0],
                    "datetime": datetime.fromtimestamp(row[0] / 1000).isoformat(),
                    "agent_id": row[1],
                    "action_type": row[2],
                    "status": row[3],
                    "action_details": json.loads(row[4]) if row[4] else {},
                    "consent_scope": row[5]
                })
            
            return audit_entries
            
        except Exception as e:
            print(f"❌ Failed to retrieve audit trail: {str(e)}")
            return []

    def get_audit_trail_with_token(self, user_id: UserID, token_str: str, days: int = 7) -> Dict[str, Any]:
        """
        Retrieve audit trail for a user with token validation (MCP protocol version).
        """
        # Validate consent
        valid, reason, token = validate_token(token_str, expected_scope=ConsentScope.CUSTOM_TEMPORARY)
        
        if not valid:
            raise PermissionError(f"❌ Audit trail access denied: {reason}")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Calculate time range
            end_time = int(time.time() * 1000)
            start_time = end_time - (days * 24 * 60 * 60 * 1000)
            
            cursor.execute('''
                SELECT timestamp, agent_id, action_type, status, action_details, consent_scope
                FROM audit_logs 
                WHERE user_id = ? AND timestamp BETWEEN ? AND ?
                ORDER BY timestamp DESC
                LIMIT 100
            ''', (user_id, start_time, end_time))
            
            rows = cursor.fetchall()
            conn.close()
            
            # Format results
            audit_entries = []
            for row in rows:
                audit_entries.append({
                    "timestamp": row[0],
                    "datetime": datetime.fromtimestamp(row[0] / 1000).isoformat(),
                    "agent_id": row[1],
                    "action_type": row[2],
                    "status": row[3],
                    "action_details": json.loads(row[4]) if row[4] else {},
                    "consent_scope": row[5]
                })
            
            # Generate summary
            summary = self._generate_audit_summary(audit_entries)
            
            return {
                "user_id": user_id,
                "period_days": days,
                "total_entries": len(audit_entries),
                "audit_entries": audit_entries,
                "summary": summary,
                "generated_at": int(time.time() * 1000)
            }
            
        except Exception as e:
            print(f"❌ Failed to retrieve audit trail: {str(e)}")
            return {"error": f"Audit trail retrieval failed: {str(e)}"}

    def get_compliance_report(self, user_id: UserID, token_str: str) -> Dict[str, Any]:
        """
        Generate compliance report for a user.
        """
        # Validate consent
        valid, reason, token = validate_token(token_str, expected_scope=ConsentScope.CUSTOM_TEMPORARY)
        
        if not valid:
            raise PermissionError(f"❌ Compliance report access denied: {reason}")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get compliance events
            cursor.execute('''
                SELECT event_type, compliance_status, violation_details, timestamp
                FROM compliance_events 
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT 50
            ''', (user_id,))
            
            compliance_events = cursor.fetchall()
            
            # Get consent token usage
            cursor.execute('''
                SELECT consent_scope, COUNT(*) as usage_count
                FROM audit_logs 
                WHERE user_id = ? AND timestamp > ?
                GROUP BY consent_scope
            ''', (user_id, int(time.time() * 1000) - (30 * 24 * 60 * 60 * 1000)))  # Last 30 days
            
            scope_usage = cursor.fetchall()
            conn.close()
            
            # Format compliance events
            events = []
            violations_count = 0
            for event in compliance_events:
                event_data = {
                    "event_type": event[0],
                    "status": event[1],
                    "details": json.loads(event[2]) if event[2] else {},
                    "timestamp": event[3],
                    "datetime": datetime.fromtimestamp(event[3] / 1000).isoformat()
                }
                events.append(event_data)
                
                if event[1] == "violation":
                    violations_count += 1
            
            # Format scope usage
            scope_stats = {}
            for scope, count in scope_usage:
                scope_stats[scope] = count
            
            # Calculate compliance score
            total_events = len(events)
            compliance_score = max(0, (total_events - violations_count) / total_events * 100) if total_events > 0 else 100
            
            return {
                "user_id": user_id,
                "compliance_score": round(compliance_score, 2),
                "total_events": total_events,
                "violations_count": violations_count,
                "compliance_events": events,
                "consent_scope_usage": scope_stats,
                "recommendations": self._generate_compliance_recommendations(compliance_score, violations_count),
                "generated_at": int(time.time() * 1000)
            }
            
        except Exception as e:
            print(f"❌ Failed to generate compliance report: {str(e)}")
            return {"error": f"Compliance report generation failed: {str(e)}"}

    def _generate_audit_summary(self, audit_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics from audit entries."""
        if not audit_entries:
            return {"message": "No audit entries found"}
        
        # Count by action type
        action_counts = {}
        agent_counts = {}
        status_counts = {}
        
        for entry in audit_entries:
            action_type = entry["action_type"]
            agent_id = entry["agent_id"]
            status = entry["status"]
            
            action_counts[action_type] = action_counts.get(action_type, 0) + 1
            agent_counts[agent_id] = agent_counts.get(agent_id, 0) + 1
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Find most active period
        daily_counts = {}
        for entry in audit_entries:
            date = datetime.fromtimestamp(entry["timestamp"] / 1000).date().isoformat()
            daily_counts[date] = daily_counts.get(date, 0) + 1
        
        most_active_day = max(daily_counts.items(), key=lambda x: x[1]) if daily_counts else None
        
        return {
            "total_actions": len(audit_entries),
            "unique_action_types": len(action_counts),
            "action_type_breakdown": action_counts,
            "agent_activity": agent_counts,
            "status_breakdown": status_counts,
            "most_active_day": most_active_day[0] if most_active_day else None,
            "success_rate": round(status_counts.get("success", 0) / len(audit_entries) * 100, 2)
        }

    def _generate_compliance_recommendations(self, compliance_score: float, violations_count: int) -> List[str]:
        """Generate compliance recommendations based on score and violations."""
        recommendations = []
        
        if compliance_score < 70:
            recommendations.append("Consider reviewing consent token usage patterns")
            recommendations.append("Implement additional validation checks before agent actions")
        
        if violations_count > 0:
            recommendations.append("Review recent compliance violations and implement fixes")
            recommendations.append("Consider stricter consent scope validation")
        
        if compliance_score >= 90:
            recommendations.append("Excellent compliance! Maintain current practices")
        
        if not recommendations:
            recommendations.append("Good compliance score. Continue monitoring regularly")
        
        return recommendations

    def export_audit_data(self, user_id: UserID, token_str: str, format: str = "json") -> Dict[str, Any]:
        """
        Export audit data for user in specified format.
        """
        # Validate consent
        valid, reason, token = validate_token(token_str, expected_scope=ConsentScope.CUSTOM_TEMPORARY)
        
        if not valid:
            raise PermissionError(f"❌ Audit data export denied: {reason}")

        # Get complete audit trail
        audit_data = self.get_audit_trail(user_id, token_str, days=365)  # Full year
        
        if format.lower() == "csv":
            # Convert to CSV format (simplified)
            csv_data = "timestamp,agent_id,action_type,status,consent_scope\n"
            for entry in audit_data.get("audit_entries", []):
                csv_data += f"{entry['timestamp']},{entry['agent_id']},{entry['action_type']},{entry['status']},{entry['consent_scope']}\n"
            
            return {
                "format": "csv",
                "data": csv_data,
                "exported_at": int(time.time() * 1000)
            }
        
        # Default JSON format
        return {
            "format": "json",
            "data": audit_data,
            "exported_at": int(time.time() * 1000)
        }
