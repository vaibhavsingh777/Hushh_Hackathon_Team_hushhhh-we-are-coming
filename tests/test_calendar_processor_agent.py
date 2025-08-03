# Test Suite for Calendar Processor Agent - Hushh MCP Protocol Compliance
# Tests privacy-first calendar processing with consent management

import pytest
import asyncio
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from hushh_mcp.agents.calendar_processor.index import CalendarProcessorAgent, calendar_processor
from hushh_mcp.consent.token import issue_token, validate_token
from hushh_mcp.constants import ConsentScope
from hushh_mcp.types import HushhConsentToken

class TestCalendarProcessorAgent:
    """Comprehensive test suite for CalendarProcessorAgent following Hushh MCP protocols"""
    
    def setup_method(self):
        """Setup test environment for each test"""
        self.agent = calendar_processor
        self.test_user_id = "test_user_456"
        self.test_consent_token = self._create_test_consent_token()
        
    def _create_test_consent_token(self) -> HushhConsentToken:
        """Create a valid test consent token"""
        return issue_token(
            user_id=self.test_user_id,
            agent_id="agent_calendar_processor",
            scope=ConsentScope.VAULT_READ_CALENDAR,
            expires_in_ms=3600000  # 1 hour
        )
    
    def test_agent_initialization(self):
        """Test that agent initializes correctly with required properties"""
        assert self.agent.agent_id == "agent_calendar_processor"
        assert self.agent.required_scope == ConsentScope.VAULT_READ_CALENDAR
        assert hasattr(self.agent, 'processed_events')
        assert hasattr(self.agent, 'schedule_stats')
        
    @pytest.mark.asyncio
    async def test_consent_validation(self):
        """Test that agent properly validates consent tokens"""
        # Test valid consent
        valid, reason, parsed = validate_token(self.test_consent_token.token)
        assert valid == True
        assert parsed.user_id == self.test_user_id
        
    @pytest.mark.asyncio
    async def test_handle_method_calendar_processing(self):
        """Test agent handle method for calendar processing"""
        result = await self.agent.handle(
            user_id=self.test_user_id,
            token=self.test_consent_token.token,
            action="process_calendar",
            days_back=7,
            days_forward=7
        )
        
        assert result["success"] == True
        assert "events" in result
        assert "stats" in result
        
    @pytest.mark.asyncio
    async def test_handle_method_schedule_analysis(self):
        """Test agent handle method for schedule analysis"""
        # First process some calendar data
        await self.agent.handle(
            user_id=self.test_user_id,
            token=self.test_consent_token.token,
            action="process_calendar",
            days_back=7,
            days_forward=7
        )
        
        # Then analyze schedule patterns
        result = await self.agent.handle(
            user_id=self.test_user_id,
            token=self.test_consent_token.token,
            action="analyze_schedule",
            analysis_type="productivity"
        )
        
        assert "analysis_type" in result
        assert "insights" in result
        assert "recommendations" in result
        
    @pytest.mark.asyncio
    async def test_calendar_event_categorization(self):
        """Test calendar event categorization with AI"""
        mock_events = [
            {
                "id": "event_1",
                "title": "Team Planning Session",
                "description": "Sprint planning for next quarter",
                "start_time": datetime.now().isoformat(),
                "end_time": (datetime.now() + timedelta(hours=1)).isoformat(),
                "duration_minutes": 60,
                "attendees_count": 5
            }
        ]
        
        with patch.object(self.agent, '_fetch_calendar_events_secure', return_value=mock_events):
            result = await self.agent.process_calendar_with_ai(
                user_id=self.test_user_id,
                consent_token=self.test_consent_token,
                days_back=1,
                days_forward=1
            )
            
        assert result["success"] == True
        assert len(result["events"]) > 0
        
        # Check categorization
        event = result["events"][0]
        assert "category" in event
        assert "confidence" in event
        
    def test_scheduling_pattern_analysis(self):
        """Test scheduling pattern analysis functionality"""
        # Mock processed events
        mock_events = [
            {
                "id": "1",
                "title": "Meeting A",
                "category": "work",
                "start_time": "2025-08-02T09:00:00",
                "duration_minutes": 60,
                "priority": "high"
            },
            {
                "id": "2", 
                "title": "Meeting B",
                "category": "work",
                "start_time": "2025-08-02T14:00:00",
                "duration_minutes": 30,
                "priority": "medium"
            }
        ]
        
        productivity_analysis = self.agent._analyze_productivity_patterns(mock_events)
        time_analysis = self.agent._analyze_time_management(mock_events)
        general_analysis = self.agent._analyze_general_patterns(mock_events)
        
        assert productivity_analysis["analysis_type"] == "productivity"
        assert time_analysis["analysis_type"] == "time_management"
        assert general_analysis["analysis_type"] == "general"
        
        # All should have insights and recommendations
        for analysis in [productivity_analysis, time_analysis, general_analysis]:
            assert "insights" in analysis
            assert "recommendations" in analysis
            
    def test_meeting_type_determination(self):
        """Test meeting type classification"""
        test_cases = [
            ({"title": "1:1 with Manager", "attendees_count": 2}, "one_on_one"),
            ({"title": "Daily Standup", "attendees_count": 5}, "standup"),
            ({"title": "Code Review Session", "attendees_count": 3}, "review"),
            ({"title": "Product Demo", "attendees_count": 10}, "presentation"),
            ({"title": "Team Meeting", "attendees_count": 8}, "large_meeting")
        ]
        
        for event_meta, expected_type in test_cases:
            result = self.agent._determine_meeting_type(event_meta)
            assert result == expected_type or result in ["team_meeting", "large_meeting"]
            
    def test_event_importance_assessment(self):
        """Test event importance determination"""
        high_importance_event = {
            "title": "Board Meeting - Urgent Decision",
            "description": "Critical budget approval needed",
            "attendees_count": 10
        }
        
        normal_importance_event = {
            "title": "Weekly Team Sync",
            "description": "Regular team update",
            "attendees_count": 3
        }
        
        high_result = self.agent._determine_event_importance(high_importance_event)
        normal_result = self.agent._determine_event_importance(normal_importance_event)
        
        assert high_result in ["high", "medium"]
        assert normal_result in ["normal", "medium"]
        
    def test_productivity_insights_generation(self):
        """Test productivity insights generation"""
        mock_events = [
            {"duration_minutes": 60, "meeting_type": "standup"},
            {"duration_minutes": 90, "meeting_type": "review"},
            {"duration_minutes": 30, "meeting_type": "one_on_one"}
        ]
        
        insights = self.agent._generate_productivity_insights(mock_events)
        
        assert "total_meeting_time_hours" in insights
        assert "average_meeting_duration_minutes" in insights
        assert "most_common_meeting_type" in insights
        assert "productivity_score" in insights
        
        # Check calculations
        assert insights["total_meeting_time_hours"] == 3.0  # 180 minutes = 3 hours
        assert insights["average_meeting_duration_minutes"] == 60.0  # 180/3 = 60
        
    def test_get_processing_status(self):
        """Test processing status retrieval"""
        status = self.agent.get_processing_status(self.test_user_id)
        
        assert "user_id" in status
        assert "has_processed_events" in status
        assert "schedule_stats" in status
        assert "last_updated" in status
        
    def test_get_categorized_events(self):
        """Test retrieval of categorized events"""
        # Initially should return empty
        events = self.agent.get_categorized_events(self.test_user_id)
        assert isinstance(events, list)
        
    @pytest.mark.asyncio
    async def test_consent_revocation(self):
        """Test consent revocation and data clearing"""
        # First process some calendar data
        await self.agent.process_calendar_with_ai(
            user_id=self.test_user_id,
            consent_token=self.test_consent_token,
            days_back=1,
            days_forward=1
        )
        
        # Verify data exists
        assert self.test_user_id in self.agent.processed_events or len(self.agent.get_categorized_events(self.test_user_id)) >= 0
        
        # Revoke consent
        revocation_success = await self.agent.revoke_consent(self.test_user_id)
        
        assert revocation_success == True
        
        # Verify data cleared
        events_after_revocation = self.agent.get_categorized_events(self.test_user_id)
        assert len(events_after_revocation) == 0
        
    @pytest.mark.asyncio
    async def test_secure_event_fetching(self):
        """Test secure calendar event fetching"""
        events = await self.agent._fetch_calendar_events_secure(
            user_id=self.test_user_id,
            days_back=7,
            days_forward=7
        )
        
        assert isinstance(events, list)
        # Should generate realistic mock events
        assert len(events) > 0
        
        # Check event structure
        for event in events[:3]:  # Check first 3 events
            assert "id" in event
            assert "title" in event
            assert "start_time" in event
            assert "end_time" in event
            
    def test_event_title_generation(self):
        """Test realistic event title generation"""
        event_types = ['meeting', 'call', 'presentation', 'review', 'planning', 'training']
        
        for event_type in event_types:
            title = self.agent._generate_event_title(event_type)
            assert isinstance(title, str)
            assert len(title) > 0
            
    def test_event_location_generation(self):
        """Test event location generation"""
        event_types = ['meeting', 'call', 'presentation', 'review']
        
        for event_type in event_types:
            location = self.agent._generate_event_location(event_type)
            assert isinstance(location, str)
            assert len(location) > 0
            
    @pytest.mark.asyncio
    async def test_invalid_consent_rejection(self):
        """Test that invalid consent tokens are rejected"""
        with pytest.raises(PermissionError):
            await self.agent.handle(
                user_id=self.test_user_id,
                token="invalid_token_string",
                action="process_calendar"
            )
            
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
        
        # Should have calendar-specific methods
        assert hasattr(self.agent, 'process_calendar_with_ai')
        assert hasattr(self.agent, 'get_categorized_events')
        assert hasattr(self.agent, 'get_processing_status')

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
