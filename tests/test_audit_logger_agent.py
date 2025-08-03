# Test Suite for Audit Logger Agent - Hushh MCP Protocol Compliance
# Tests privacy-first audit logging with consent management

import pytest
import asyncio
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from hushh_mcp.agents.audit_logger.index import AuditLoggerAgent
from hushh_mcp.consent.token import issue_token, validate_token
from hushh_mcp.constants import ConsentScope
from hushh_mcp.types import HushhConsentToken

class TestAuditLoggerAgent:
    """Comprehensive test suite for AuditLoggerAgent following Hushh MCP protocols"""
    
    def setup_method(self):
        """Setup test environment for each test"""
        self.agent = AuditLoggerAgent()
        self.test_user_id = "test_user_789"
        
    def test_agent_initialization(self):
        """Test that agent initializes correctly with required properties"""
        assert self.agent.agent_id == "agent_audit_logger"
        assert hasattr(self.agent, 'db_path')
        assert hasattr(self.agent, 'log_activity')
        assert hasattr(self.agent, 'get_audit_trail')
        
    @pytest.mark.asyncio
    async def test_activity_logging(self):
        """Test logging of user activities"""
        test_activity = {
            "action": "email_processed",
            "timestamp": datetime.now().isoformat(),
            "details": {
                "email_count": 10,
                "categories": ["work", "personal"],
                "processing_time": 5.2
            }
        }
        
        # Log the activity
        log_success = await self.agent.log_activity(
            user_id=self.test_user_id,
            action=test_activity["action"],
            details=test_activity["details"]
        )
        
        assert log_success == True
        
        # Verify it was stored
        audit_trail = await self.agent.get_audit_trail(self.test_user_id)
        assert len(audit_trail) > 0
        
        logged_entry = audit_trail[-1]  # Get most recent entry
        assert logged_entry["user_id"] == self.test_user_id
        assert logged_entry["action"] == test_activity["action"]
        assert logged_entry["details"] == test_activity["details"]
        
    @pytest.mark.asyncio
    async def test_privacy_audit_logging(self):
        """Test logging of privacy-related activities"""
        privacy_activities = [
            {
                "action": "consent_granted",
                "details": {
                    "scope": "email_processing",
                    "agent": "email_processor",
                    "duration": "24_hours"
                }
            },
            {
                "action": "data_accessed",
                "details": {
                    "data_type": "emails",
                    "count": 50,
                    "purpose": "categorization"
                }
            },
            {
                "action": "consent_revoked",
                "details": {
                    "scope": "all",
                    "data_cleared": True
                }
            }
        ]
        
        for activity in privacy_activities:
            log_success = await self.agent.log_activity(
                user_id=self.test_user_id,
                action=activity["action"],
                details=activity["details"]
            )
            assert log_success == True
            
        # Verify all activities were logged
        audit_trail = await self.agent.get_audit_trail(self.test_user_id)
        assert len(audit_trail) >= len(privacy_activities)
        
        # Check that privacy actions are properly recorded
        privacy_actions = [entry["action"] for entry in audit_trail]
        for activity in privacy_activities:
            assert activity["action"] in privacy_actions
            
    @pytest.mark.asyncio        
    async def test_audit_trail_retrieval(self):
        """Test retrieval of audit trails"""
        # Initially should be empty or minimal
        initial_trail = await self.agent.get_audit_trail(self.test_user_id)
        assert isinstance(initial_trail, list)
        
        # Test with limit
        limited_trail = await self.agent.get_audit_trail(self.test_user_id, limit=5)
        assert len(limited_trail) <= 5
        
    @pytest.mark.asyncio
    async def test_audit_trail_filtering(self):
        """Test filtering audit trails by action type"""
        # This would test filtering functionality if implemented
        # For now, verify the basic structure
        trail = await self.agent.get_audit_trail(self.test_user_id)
        
        # Each entry should have required fields
        for entry in trail:
            assert "user_id" in entry
            assert "action" in entry
            assert "timestamp" in entry
            assert "details" in entry
            
    @pytest.mark.asyncio
    async def test_concurrent_logging(self):
        """Test concurrent audit logging safety"""
        # Create multiple concurrent logging tasks
        tasks = []
        for i in range(10):
            task = self.agent.log_activity(
                user_id=f"user_{i}",
                action=f"test_action_{i}",
                details={"test": f"data_{i}"}
            )
            tasks.append(task)
        
        # All tasks should complete without errors
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            assert not isinstance(result, Exception)
            assert result == True
            
    @pytest.mark.asyncio
    async def test_error_logging(self):
        """Test logging of error conditions"""
        error_details = {
            "error_type": "processing_failure",
            "error_message": "Failed to categorize email",
            "affected_items": ["email_123", "email_456"],
            "recovery_action": "retry_processing"
        }
        
        log_success = await self.agent.log_activity(
            user_id=self.test_user_id,
            action="error_occurred",
            details=error_details
        )
        
        assert log_success == True
        
        # Verify error was logged with all details
        audit_trail = await self.agent.get_audit_trail(self.test_user_id)
        error_entry = next((entry for entry in audit_trail if entry["action"] == "error_occurred"), None)
        
        assert error_entry is not None
        assert error_entry["details"] == error_details
        
    @pytest.mark.asyncio
    async def test_audit_storage_integrity(self):
        """Test audit storage data integrity"""
        # Test that audit entries maintain integrity
        test_details = {
            "sensitive_data": "should_be_preserved",
            "numeric_data": 42,
            "list_data": ["item1", "item2"],
            "nested_data": {"key": "value"}
        }
        
        await self.agent.log_activity(
            user_id=self.test_user_id,
            action="integrity_test",
            details=test_details
        )
        
        # Retrieve and verify
        audit_trail = await self.agent.get_audit_trail(self.test_user_id)
        test_entry = next((entry for entry in audit_trail if entry["action"] == "integrity_test"), None)
        
        assert test_entry is not None
        assert test_entry["details"] == test_details
        
    @pytest.mark.asyncio
    async def test_timestamp_accuracy(self):
        """Test timestamp accuracy and format"""
        start_time = datetime.now()
        
        await self.agent.log_activity(
            user_id=self.test_user_id,
            action="timestamp_test",
            details={"test": "timing"}
        )
        
        end_time = datetime.now()
        
        # Get the logged entry
        audit_trail = await self.agent.get_audit_trail(self.test_user_id)
        test_entry = next((entry for entry in audit_trail if entry["action"] == "timestamp_test"), None)
        
        assert test_entry is not None
        
        # Parse timestamp and verify it's within expected range
        logged_time = datetime.fromisoformat(test_entry["timestamp"].replace('Z', '+00:00'))
        
        assert start_time <= logged_time <= end_time
        
    @pytest.mark.asyncio
    async def test_high_volume_logging(self):
        """Test performance with high volume logging"""
        start_time = datetime.now()
        
        # Log 100 activities
        tasks = []
        for i in range(100):
            task = self.agent.log_activity(
                user_id=self.test_user_id,
                action=f"bulk_test_{i}",
                details={"index": i, "timestamp": datetime.now().isoformat()}
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # All should succeed
        assert all(result == True for result in results)
        
        # Should complete in reasonable time (< 5 seconds for 100 operations)
        assert processing_time < 5.0
        
        # Verify all entries were logged
        audit_trail = await self.agent.get_audit_trail(self.test_user_id)
        bulk_entries = [entry for entry in audit_trail if entry["action"].startswith("bulk_test_")]
        assert len(bulk_entries) == 100
        
    @pytest.mark.asyncio
    async def test_user_isolation(self):
        """Test that audit logs are properly isolated by user"""
        user1_id = "user_1"
        user2_id = "user_2"
        
        # Log activities for different users
        await self.agent.log_activity(user1_id, "user1_action", {"data": "user1"})
        await self.agent.log_activity(user2_id, "user2_action", {"data": "user2"})
        
        # Verify isolation
        user1_trail = await self.agent.get_audit_trail(user1_id)
        user2_trail = await self.agent.get_audit_trail(user2_id)
        
        # Each user should only see their own activities
        user1_actions = [entry["action"] for entry in user1_trail]
        user2_actions = [entry["action"] for entry in user2_trail]
        
        assert "user1_action" in user1_actions
        assert "user2_action" not in user1_actions
        assert "user2_action" in user2_actions
        assert "user1_action" not in user2_actions
        
    def test_hushh_protocol_compliance(self):
        """Test overall Hushh MCP protocol compliance"""
        # Agent should have required MCP properties
        assert hasattr(self.agent, 'agent_id')
        assert hasattr(self.agent, 'log_activity')
        assert hasattr(self.agent, 'get_audit_trail')
        
        # Agent ID should follow naming convention
        assert self.agent.agent_id.startswith("agent_")
        
        # Should support audit-specific operations
        assert hasattr(self.agent, 'db_path')

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
