"""
Google Gmail and Calendar API integration for Hushh MCP
Provides real data access replacing mock data functionality
"""

import asyncio
import logging
import base64
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from email.utils import parsedate_to_datetime

try:
    import aiohttp
except ImportError:
    aiohttp = None

logger = logging.getLogger(__name__)

class GmailClient:
    """Gmail API client for fetching real email data"""
    
    def __init__(self, access_token: str, refresh_token: Optional[str] = None):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.base_url = "https://www.googleapis.com/gmail/v1/users/me"
        
        if aiohttp is None:
            raise ImportError("aiohttp is required for Gmail API access. Install with: pip install aiohttp")
    
    async def get_user_profile(self) -> Dict[str, Any]:
        """Get user's Gmail profile to validate token"""
        try:
            url = f"{self.base_url}/profile"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 401:
                        raise Exception("Invalid or expired access token")
                    elif response.status == 403:
                        error_text = await response.text()
                        raise Exception(f"Gmail API access forbidden: {error_text}. Check: 1) Gmail API enabled in Google Cloud Console, 2) OAuth token has gmail.readonly scope, 3) User granted Gmail permissions")
                    else:
                        error_text = await response.text()
                        raise Exception(f"Gmail API error: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"Failed to get user profile: {e}")
            raise e
    
    async def fetch_emails(self, days_back: int = 30, max_results: int = None) -> List[Dict[str, Any]]:
        """
        Fetch real emails from user's Gmail account with pagination support.
        
        Args:
            days_back: Number of days to look back for emails
            max_results: Maximum number of emails to fetch (None for unlimited)
            
        Returns:
            List of email data dictionaries
        """
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Format date for Gmail search query
            start_date_str = start_date.strftime("%Y/%m/%d")
            
            # Build Gmail search query
            query = f"after:{start_date_str}"
            
            # Collect all message IDs with pagination
            all_message_ids = []
            next_page_token = None
            page_size = 500  # Gmail API max per page
            
            async with aiohttp.ClientSession() as session:
                # Get all message IDs with pagination
                while True:
                    messages_url = f"{self.base_url}/messages"
                    headers = {"Authorization": f"Bearer {self.access_token}"}
                    params = {
                        "q": query,
                        "maxResults": page_size
                    }
                    
                    if next_page_token:
                        params["pageToken"] = next_page_token
                    
                    async with session.get(messages_url, headers=headers, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            messages = data.get("messages", [])
                            message_ids = [msg["id"] for msg in messages]
                            all_message_ids.extend(message_ids)
                            
                            # Check if there are more pages
                            next_page_token = data.get("nextPageToken")
                            if not next_page_token:
                                break
                                
                            # Apply max_results limit if specified
                            if max_results and len(all_message_ids) >= max_results:
                                all_message_ids = all_message_ids[:max_results]
                                break
                                
                        elif response.status == 401:
                            raise Exception("Invalid or expired access token")
                        elif response.status == 403:
                            error_text = await response.text()
                            raise Exception(f"Gmail API access forbidden: {error_text}")
                        else:
                            error_text = await response.text()
                            raise Exception(f"Gmail API error: {response.status} - {error_text}")
                
                logger.info(f"📧 Found {len(all_message_ids)} emails to process")
                
                # Fetch full email details for each message
                emails = []
                for i, msg_id in enumerate(all_message_ids):
                    try:
                        msg_url = f"{self.base_url}/messages/{msg_id}"
                        async with session.get(msg_url, headers=headers) as msg_response:
                            if msg_response.status == 200:
                                email_data = await msg_response.json()
                                processed_email = self._process_email_data(email_data)
                                emails.append(processed_email)
                                
                                # Add small delay to avoid rate limiting
                                if i % 10 == 0:
                                    await asyncio.sleep(0.1)
                                    
                                # Progress logging for large batches
                                if (i + 1) % 50 == 0:
                                    logger.info(f"📧 Processed {i + 1}/{len(all_message_ids)} emails...")
                                    
                            else:
                                logger.warning(f"Failed to fetch message {msg_id}: {msg_response.status}")
                                
                    except Exception as e:
                        logger.warning(f"Error processing message {msg_id}: {e}")
                        continue
                
                logger.info(f"Successfully fetched {len(emails)} emails from Gmail API")
                return emails
                
        except Exception as e:
            logger.error(f"Failed to fetch emails: {e}")
            raise e
    
    def _process_email_data(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw Gmail API response into standardized format"""
        try:
            payload = email_data.get("payload", {})
            headers = payload.get("headers", [])
            
            # Extract headers
            header_dict = {h["name"].lower(): h["value"] for h in headers}
            
            # Get email body
            body = self._extract_email_body(payload)
            
            # Parse date
            date_str = header_dict.get("date", "")
            try:
                # Gmail date format parsing
                date_obj = parsedate_to_datetime(date_str)
                formatted_date = date_obj.isoformat()
            except:
                formatted_date = datetime.now().isoformat()
            
            return {
                "id": email_data["id"],
                "thread_id": email_data.get("threadId", ""),
                "subject": header_dict.get("subject", "No Subject"),
                "sender": header_dict.get("from", "Unknown Sender"),
                "recipient": header_dict.get("to", ""),
                "date": formatted_date,
                "body": body,
                "content": body,  # Add content field for AI processing compatibility
                "snippet": email_data.get("snippet", ""),
                "labels": email_data.get("labelIds", []),
                "size_estimate": email_data.get("sizeEstimate", 0),
                "unread": "UNREAD" in email_data.get("labelIds", []),
                "important": "IMPORTANT" in email_data.get("labelIds", []),
                "category": self._determine_category_from_labels(email_data.get("labelIds", [])),
                "source": "gmail_api"
            }
            
        except Exception as e:
            logger.error(f"Error processing email data: {e}")
            return {
                "id": email_data.get("id", "unknown"),
                "subject": "Error processing email",
                "sender": "unknown",
                "date": datetime.now().isoformat(),
                "body": "Failed to process email content",
                "content": "Failed to process email content",  # Add content field for compatibility
                "source": "gmail_api"
            }
    
    def _extract_email_body(self, payload: Dict[str, Any]) -> str:
        """Extract email body from Gmail payload"""
        try:
            # Handle multipart messages
            if payload.get("parts"):
                for part in payload["parts"]:
                    if part.get("mimeType") == "text/plain":
                        body_data = part.get("body", {}).get("data", "")
                        if body_data:
                            return base64.urlsafe_b64decode(body_data + "===").decode('utf-8', errors='ignore')
                    elif part.get("mimeType") == "text/html":
                        body_data = part.get("body", {}).get("data", "")
                        if body_data:
                            html_content = base64.urlsafe_b64decode(body_data + "===").decode('utf-8', errors='ignore')
                            # Simple HTML to text conversion
                            return re.sub('<[^<]+?>', '', html_content)
            
            # Handle single part messages
            elif payload.get("body", {}).get("data"):
                body_data = payload["body"]["data"]
                return base64.urlsafe_b64decode(body_data + "===").decode('utf-8', errors='ignore')
            
            return ""
            
        except Exception as e:
            logger.error(f"Error extracting email body: {e}")
            return "Failed to extract email content"
    
    def _determine_category_from_labels(self, labels: List[str]) -> str:
        """Determine email category from Gmail labels"""
        if "CATEGORY_SOCIAL" in labels:
            return "social"
        elif "CATEGORY_PROMOTIONS" in labels:
            return "marketing"
        elif "CATEGORY_UPDATES" in labels:
            return "updates"
        elif "CATEGORY_FORUMS" in labels:
            return "forums"
        elif "IMPORTANT" in labels:
            return "important"
        elif "STARRED" in labels:
            return "starred"
        else:
            return "primary"


class GoogleCalendarClient:
    """Google Calendar API client for fetching real calendar data"""
    
    def __init__(self, access_token: str, refresh_token: Optional[str] = None):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.base_url = "https://www.googleapis.com/calendar/v3"
        
        if aiohttp is None:
            raise ImportError("aiohttp is required for Calendar API access. Install with: pip install aiohttp")
    
    async def fetch_calendar_events(
        self, 
        days_back: int = 30, 
        days_forward: int = 30,
        max_results: int = 250
    ) -> List[Dict[str, Any]]:
        """
        Fetch real calendar events from user's Google Calendar.
        
        Args:
            days_back: Number of days to look back
            days_forward: Number of days to look forward
            max_results: Maximum number of events to fetch
            
        Returns:
            List of calendar event dictionaries
        """
        try:
            # Calculate date range
            start_date = datetime.now() - timedelta(days=days_back)
            end_date = datetime.now() + timedelta(days=days_forward)
            
            # Format dates for API
            time_min = start_date.isoformat() + 'Z'
            time_max = end_date.isoformat() + 'Z'
            
            url = f"{self.base_url}/calendars/primary/events"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            params = {
                "timeMin": time_min,
                "timeMax": time_max,
                "maxResults": max_results,
                "singleEvents": True,
                "orderBy": "startTime"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        events = [self._process_calendar_event(event) for event in data.get("items", [])]
                        logger.info(f"Successfully fetched {len(events)} calendar events")
                        return events
                    elif response.status == 401:
                        raise Exception("Invalid or expired access token")
                    elif response.status == 403:
                        error_text = await response.text()
                        raise Exception(f"Calendar API access forbidden: {error_text}")
                    else:
                        error_text = await response.text()
                        raise Exception(f"Calendar API error: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"Failed to fetch calendar events: {e}")
            raise e
    
    def _process_calendar_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw Calendar API response into standardized format"""
        try:
            # Extract start and end times
            start = event_data.get("start", {})
            end = event_data.get("end", {})
            
            start_time = start.get("dateTime", start.get("date", ""))
            end_time = end.get("dateTime", end.get("date", ""))
            
            # Calculate duration
            try:
                if "T" in start_time and "T" in end_time:
                    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                    duration = int((end_dt - start_dt).total_seconds() / 60)  # minutes
                else:
                    duration = 1440  # All day event = 1440 minutes
            except:
                duration = 60  # Default 1 hour
            
            return {
                "id": event_data.get("id", ""),
                "title": event_data.get("summary", "No Title"),
                "description": event_data.get("description", ""),
                "start_time": start_time,
                "end_time": end_time,
                "duration_minutes": duration,
                "location": event_data.get("location", ""),
                "attendees": [
                    attendee.get("email", "") 
                    for attendee in event_data.get("attendees", [])
                ],
                "organizer": event_data.get("organizer", {}).get("email", ""),
                "status": event_data.get("status", "confirmed"),
                "visibility": event_data.get("visibility", "default"),
                "all_day": "date" in start and "dateTime" not in start,
                "recurring": "recurringEventId" in event_data,
                "meeting_link": event_data.get("hangoutLink", ""),
                "calendar_id": event_data.get("calendarId", "primary"),
                "source": "google_calendar_api"
            }
            
        except Exception as e:
            logger.error(f"Error processing calendar event: {e}")
            return {
                "id": event_data.get("id", "unknown"),
                "title": "Error processing event",
                "start_time": datetime.now().isoformat(),
                "end_time": datetime.now().isoformat(),
                "source": "google_calendar_api"
            }


# Factory functions for creating authenticated clients
async def create_gmail_client_from_token(access_token: str, refresh_token: Optional[str] = None) -> GmailClient:
    """
    Create and validate Gmail client with access token.
    
    Args:
        access_token: Google OAuth access token
        refresh_token: Optional refresh token
        
    Returns:
        Initialized and validated Gmail client
    """
    client = GmailClient(access_token, refresh_token)
    
    try:
        # Validate token by fetching user profile
        profile = await client.get_user_profile()
        logger.info(f"Gmail client initialized for user: {profile.get('emailAddress', 'unknown')}")
        return client
        
    except Exception as e:
        logger.error(f"Failed to initialize Gmail client: {e}")
        raise e


async def create_calendar_client_from_token(access_token: str, refresh_token: Optional[str] = None) -> GoogleCalendarClient:
    """
    Create and validate Calendar client with access token.
    
    Args:
        access_token: Google OAuth access token
        refresh_token: Optional refresh token
        
    Returns:
        Initialized Calendar client
    """
    client = GoogleCalendarClient(access_token, refresh_token)
    
    # Calendar client doesn't need validation call since it's simpler
    logger.info("Calendar client initialized successfully")
    return client
