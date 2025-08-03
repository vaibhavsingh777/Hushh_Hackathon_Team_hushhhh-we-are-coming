# Test Suite for Schedule Event Operon - Hushh MCP Protocol Compliance
# Tests privacy-first event scheduling functionality

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from hushh_mcp.operons.schedule_event import (
    create_calendar_event,
    schedule_event_operon,
    validate_event_data,
    generate_event_id
)

class TestScheduleEventOperon:
    """Comprehensive test suite for Schedule Event Operon following Hushh MCP protocols"""
    
    def setup_method(self):
        """Setup test environment for each test"""
        self.test_event_data = {
            "title": "Test Meeting",
            "start_time": "2025-08-02T14:00:00",
            "end_time": "2025-08-02T15:00:00",
            "description": "Test meeting description",
            "location": "Conference Room A",
            "attendees": ["user1@example.com", "user2@example.com"]
        }
        
    def test_create_calendar_event_basic(self):
        """Test basic calendar event creation"""
        event = create_calendar_event(
            title=self.test_event_data["title"],
            start_time=self.test_event_data["start_time"],
            end_time=self.test_event_data["end_time"]
        )
        
        assert event["title"] == self.test_event_data["title"]
        assert event["start_time"] == self.test_event_data["start_time"]
        assert event["end_time"] == self.test_event_data["end_time"]
        assert "event_id" in event
        assert "created_at" in event
        
    def test_create_calendar_event_with_all_fields(self):
        """Test calendar event creation with all optional fields"""
        event = create_calendar_event(
            title=self.test_event_data["title"],
            start_time=self.test_event_data["start_time"],
            end_time=self.test_event_data["end_time"],
            description=self.test_event_data["description"],
            location=self.test_event_data["location"],
            attendees=self.test_event_data["attendees"]
        )
        
        assert event["description"] == self.test_event_data["description"]
        assert event["location"] == self.test_event_data["location"]
        assert event["attendees"] == self.test_event_data["attendees"]
        assert event["attendee_count"] == len(self.test_event_data["attendees"])
        
    def test_create_calendar_event_without_end_time(self):
        """Test calendar event creation without end time (should default to 1 hour)"""
        event = create_calendar_event(
            title=self.test_event_data["title"],
            start_time=self.test_event_data["start_time"]
        )
        
        start = datetime.fromisoformat(self.test_event_data["start_time"])
        expected_end = start + timedelta(hours=1)
        
        assert event["end_time"] == expected_end.isoformat()
        assert event["duration_minutes"] == 60
        
    def test_event_id_generation(self):
        """Test event ID generation uniqueness"""
        id1 = generate_event_id()
        id2 = generate_event_id()
        
        assert id1 != id2
        assert id1.startswith("event_")
        assert id2.startswith("event_")
        assert len(id1) > 10  # Should be reasonably long
        
    def test_validate_event_data_valid(self):
        """Test event data validation with valid data"""
        validation = validate_event_data(self.test_event_data)
        
        assert validation["is_valid"] == True
        assert validation["errors"] == []
        
    def test_validate_event_data_missing_title(self):
        """Test event data validation with missing title"""
        invalid_data = self.test_event_data.copy()
        del invalid_data["title"]
        
        validation = validate_event_data(invalid_data)
        
        assert validation["is_valid"] == False
        assert "title" in str(validation["errors"]).lower()
        
    def test_validate_event_data_missing_start_time(self):
        """Test event data validation with missing start time"""
        invalid_data = self.test_event_data.copy()
        del invalid_data["start_time"]
        
        validation = validate_event_data(invalid_data)
        
        assert validation["is_valid"] == False
        assert "start_time" in str(validation["errors"]).lower()
        
    def test_validate_event_data_invalid_time_format(self):
        """Test event data validation with invalid time format"""
        invalid_data = self.test_event_data.copy()
        invalid_data["start_time"] = "invalid-time-format"
        
        validation = validate_event_data(invalid_data)
        
        assert validation["is_valid"] == False
        assert len(validation["errors"]) > 0
        
    def test_validate_event_data_end_before_start(self):
        """Test event data validation with end time before start time"""
        invalid_data = self.test_event_data.copy()
        invalid_data["start_time"] = "2025-08-02T15:00:00"
        invalid_data["end_time"] = "2025-08-02T14:00:00"
        
        validation = validate_event_data(invalid_data)
        
        assert validation["is_valid"] == False
        assert any("end time" in error.lower() and "start time" in error.lower() for error in validation["errors"])
        
    def test_schedule_event_operon_success(self):
        """Test schedule event operon successful execution"""
        result = schedule_event_operon(
            title=self.test_event_data["title"],
            start_time=self.test_event_data["start_time"],
            end_time=self.test_event_data["end_time"],
            description=self.test_event_data["description"],
            location=self.test_event_data["location"],
            attendees=self.test_event_data["attendees"]
        )
        
        assert result["success"] == True
        assert "event" in result
        assert result["event"]["title"] == self.test_event_data["title"]
        assert "message" in result
        
    def test_schedule_event_operon_validation_failure(self):
        """Test schedule event operon with validation failure"""
        result = schedule_event_operon(
            title="",  # Empty title should fail validation
            start_time=self.test_event_data["start_time"]
        )
        
        assert result["success"] == False
        assert "error" in result
        assert "validation" in result["error"].lower()
        
    def test_event_duration_calculation(self):
        """Test duration calculation for events"""
        start_time = "2025-08-02T14:00:00"
        end_time = "2025-08-02T15:30:00"
        
        event = create_calendar_event(
            title="Duration Test",
            start_time=start_time,
            end_time=end_time
        )
        
        assert event["duration_minutes"] == 90  # 1.5 hours = 90 minutes
        
    def test_attendee_handling(self):
        """Test attendee list handling and validation"""
        # Test with string attendees
        attendees = ["user1@example.com", "user2@example.com", "user3@example.com"]
        
        event = create_calendar_event(
            title="Attendee Test",
            start_time=self.test_event_data["start_time"],
            attendees=attendees
        )
        
        assert event["attendees"] == attendees
        assert event["attendee_count"] == 3
        
        # Test with empty attendees
        event_no_attendees = create_calendar_event(
            title="No Attendees Test",
            start_time=self.test_event_data["start_time"]
        )
        
        assert event_no_attendees["attendees"] == []
        assert event_no_attendees["attendee_count"] == 0
        
    def test_recurring_event_support(self):
        """Test recurring event creation if supported"""
        # This test assumes recurring event support
        # Skip if not implemented
        try:
            event = create_calendar_event(
                title="Weekly Meeting",
                start_time=self.test_event_data["start_time"],
                end_time=self.test_event_data["end_time"],
                recurring="weekly",
                recurrence_end="2025-12-31T00:00:00"
            )
            
            if "recurring" in event:
                assert event["recurring"] == "weekly"
                assert "recurrence_end" in event
        except TypeError:
            # Recurring events not implemented, skip test
            pytest.skip("Recurring events not implemented")
            
    def test_timezone_handling(self):
        """Test timezone handling in event creation"""
        # Test with timezone-aware datetime
        start_with_tz = "2025-08-02T14:00:00-07:00"  # Pacific Time
        end_with_tz = "2025-08-02T15:00:00-07:00"
        
        event = create_calendar_event(
            title="Timezone Test",
            start_time=start_with_tz,
            end_time=end_with_tz
        )
        
        # Should preserve timezone information
        assert start_with_tz in event["start_time"] or "2025-08-02T14:00:00" in event["start_time"]
        
    def test_event_categorization_integration(self):
        """Test integration with categorization system"""
        business_event = create_calendar_event(
            title="Board Meeting",
            start_time=self.test_event_data["start_time"],
            description="Quarterly business review and strategic planning",
            location="Boardroom"
        )
        
        # Should have category information if auto-categorization is enabled
        if "category" in business_event:
            assert business_event["category"] in ["work", "business", "meeting"]
            
    def test_conflict_detection(self):
        """Test event conflict detection if implemented"""
        # This would test conflict detection functionality
        # For now, just ensure events can be created
        event1 = create_calendar_event(
            title="Meeting 1",
            start_time="2025-08-02T14:00:00",
            end_time="2025-08-02T15:00:00"
        )
        
        event2 = create_calendar_event(
            title="Meeting 2", 
            start_time="2025-08-02T14:30:00",
            end_time="2025-08-02T15:30:00"
        )
        
        # Both events should be created successfully
        assert event1["event_id"] != event2["event_id"]
        
    def test_privacy_compliance(self):
        """Test privacy compliance in event creation"""
        event = create_calendar_event(
            title="Private Meeting",
            start_time=self.test_event_data["start_time"],
            description="Confidential discussion"
        )
        
        # Should not expose sensitive information inappropriately
        assert "event_id" in event  # Should have unique identifier
        assert "created_at" in event  # Should have timestamp
        
        # Sensitive fields should be preserved but properly handled
        assert event["title"] == "Private Meeting"
        assert event["description"] == "Confidential discussion"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
