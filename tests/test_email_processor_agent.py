# Test Suite for Email Processor Agent - Hushh MCP Protocol Compliance
# Tests privacy-first email processing with consent management

import pytest
import asyncio
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from hushh_mcp.agents.email_processor.index import EmailProcessorAgent
from hushh_mcp.consent.token import issue_token, validate_token
from hushh_mcp.constants import ConsentScope
from hushh_mcp.types import HushhConsentToken

class TestEmailProcessorAgent:
    """Comprehensive test suite for EmailProcessorAgent following Hushh MCP protocols"""
    
    def setup_method(self):
        """Setup test environment for each test"""
        self.agent = EmailProcessorAgent()
        self.test_user_id = "test_user_123"
        self.test_consent_token = self._create_test_consent_token()
        
    def _create_test_consent_token(self) -> HushhConsentToken:
        """Create a valid test consent token"""
        return issue_token(
            user_id=self.test_user_id,
            agent_id="agent_email_processor",
            scope=ConsentScope.VAULT_READ_EMAIL,
            expires_in_ms=3600000  # 1 hour
        )
    
    def test_agent_initialization(self):
        """Test that agent initializes correctly with required properties"""
        assert self.agent.agent_id == "agent_email_processor"
        assert self.agent.required_scope == ConsentScope.VAULT_READ_EMAIL
        assert hasattr(self.agent, 'processed_emails')
        assert hasattr(self.agent, 'category_stats')
        
    @pytest.mark.asyncio
    async def test_consent_validation(self):
        """Test that agent properly validates consent tokens"""
        # Test valid consent
        valid, reason, parsed = validate_token(self.test_consent_token.token)
        assert valid == True
        assert parsed.user_id == self.test_user_id
        
        # Test invalid consent
        invalid_token = "invalid_token_string"
        valid, reason, parsed = validate_token(invalid_token)
        assert valid == False
        assert "Invalid token" in reason
        
    @pytest.mark.asyncio
    async def test_handle_method_with_valid_consent(self):
        """Test agent handle method with valid consent token"""
        mock_emails = [
            {
                "id": "email_1",
                "subject": "Team Meeting Tomorrow",
                "body": "Please attend the team meeting at 3 PM",
                "sender": "manager@company.com",
                "received_date": datetime.now().isoformat()
            }
        ]
        
        with patch.object(self.agent, '_fetch_emails_secure', return_value=mock_emails):
            result = await self.agent.handle(
                user_id=self.test_user_id,
                token=self.test_consent_token.token,
                action="process_emails",
                days=7
            )
            
        assert result["success"] == True
        assert "emails" in result
        assert len(result["emails"]) > 0
        
    @pytest.mark.asyncio
    async def test_handle_method_with_invalid_consent(self):
        """Test agent handle method with invalid consent token"""
        with pytest.raises(PermissionError) as exc_info:
            await self.agent.handle(
                user_id=self.test_user_id,
                token="invalid_token",
                action="process_emails"
            )
        
        assert "Invalid consent token" in str(exc_info.value)
        
    @pytest.mark.asyncio
    async def test_email_categorization(self):
        """Test email categorization with AI operons"""
        test_email = {
            "id": "test_email_1",
            "subject": "Budget Review Meeting",
            "body": "Please review the quarterly budget and join the meeting",
            "sender": "finance@company.com",
            "received_date": datetime.now().isoformat()
        }
        
        # Mock the categorization operon
        with patch('hushh_mcp.operons.categorize_content.categorize_with_free_llm') as mock_categorize:
            mock_categorize.return_value = ["work", "finance"]
            
            categorized = await self.agent._categorize_email_with_ai(test_email)
            
            assert categorized["category"] in ["work", "finance"]
            assert "confidence" in categorized
            assert categorized["confidence"] > 0
            
    @pytest.mark.asyncio
    async def test_privacy_assessment(self):
        """Test privacy assessment of email content"""
        sensitive_email = {
            "id": "sensitive_1",
            "subject": "SSN: 123-45-6789 for tax forms",
            "body": "Your Social Security Number is 123-45-6789",
            "sender": "hr@company.com"
        }
        
        privacy_assessment = await self.agent._assess_email_privacy(sensitive_email)
        
        assert "privacy_risk" in privacy_assessment
        assert privacy_assessment["privacy_risk"] in ["low", "medium", "high"]
        
    @pytest.mark.asyncio
    async def test_data_revocation(self):
        """Test user data revocation following Hushh protocol"""
        # First process some emails
        await self.agent.handle(
            user_id=self.test_user_id,
            token=self.test_consent_token.token,
            action="process_emails",
            days=1
        )
        
        # Verify data exists
        assert self.test_user_id in self.agent.processed_emails
        
        # Revoke consent
        revocation_success = await self.agent.revoke_consent(self.test_user_id)
        
        assert revocation_success == True
        assert self.test_user_id not in self.agent.processed_emails
        
    def test_processing_status_tracking(self):
        """Test processing status tracking functionality"""
        status = self.agent.get_processing_status(self.test_user_id)
        
        assert "user_id" in status
        assert "has_processed_emails" in status
        assert "last_updated" in status
        
    @pytest.mark.asyncio
    async def test_email_filtering_by_category(self):
        """Test filtering emails by category"""
        # Mock some processed emails
        self.agent.processed_emails[self.test_user_id] = [
            {"id": "1", "category": "work", "subject": "Meeting"},
            {"id": "2", "category": "personal", "subject": "Appointment"},
            {"id": "3", "category": "work", "subject": "Report"}
        ]
        
        work_emails = self.agent.get_emails_by_category(self.test_user_id, "work")
        personal_emails = self.agent.get_emails_by_category(self.test_user_id, "personal")
        
        assert len(work_emails) == 2
        assert len(personal_emails) == 1
        assert all(email["category"] == "work" for email in work_emails)
        
    @pytest.mark.asyncio
    async def test_concurrent_processing(self):
        """Test concurrent email processing safety"""
        # Create multiple concurrent processing tasks
        tasks = []
        for i in range(3):
            task = self.agent.handle(
                user_id=f"user_{i}",
                token=self.test_consent_token.token,
                action="process_emails",
                days=1
            )
            tasks.append(task)
        
        # All tasks should complete without errors
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            assert not isinstance(result, Exception)
            
    def test_consent_scope_validation(self):
        """Test that agent validates correct consent scope"""
        # Test with wrong scope
        wrong_scope_token = issue_token(
            user_id=self.test_user_id,
            agent_id="agent_email_processor",
            scope=ConsentScope.VAULT_READ_CALENDAR,  # Wrong scope
            expires_in_ms=3600000
        )
        
        # Should reject wrong scope
        with pytest.raises(PermissionError):
            asyncio.run(self.agent.handle(
                user_id=self.test_user_id,
                token=wrong_scope_token.token,
                action="process_emails"
            ))
            
    @pytest.mark.asyncio
    async def test_audit_trail_generation(self):
        """Test that agent generates proper audit trails"""
        with patch('hushh_mcp.agents.audit_logger.index.audit_logger') as mock_audit:
            await self.agent.handle(
                user_id=self.test_user_id,
                token=self.test_consent_token.token,
                action="process_emails",
                days=1
            )
            
            # Verify audit logging was called
            mock_audit.log_activity.assert_called()
            
    def test_hushh_protocol_compliance(self):
        """Test overall Hushh MCP protocol compliance"""
        # Agent should have required MCP properties
        assert hasattr(self.agent, 'agent_id')
        assert hasattr(self.agent, 'required_scope')
        assert hasattr(self.agent, 'handle')
        assert hasattr(self.agent, 'revoke_consent')
        
        # Agent ID should follow naming convention
        assert self.agent.agent_id.startswith("agent_")
        
        # Required scope should be valid
        assert isinstance(self.agent.required_scope, ConsentScope)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
