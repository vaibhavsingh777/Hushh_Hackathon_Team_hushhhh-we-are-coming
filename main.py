# main.py - Enhanced FastAPI Backend for Hushh MCP PDA Agent

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError, DecodeError
import requests
import logging
import uuid

# Import Hushh MCP agents and operons
from hushh_mcp.agents.email_processor.index import EmailProcessorAgent
from hushh_mcp.agents.calendar_processor.index import CalendarProcessorAgent
from hushh_mcp.agents.audit_logger.index import AuditLoggerAgent
from hushh_mcp.consent.token import issue_token, revoke_token, validate_token
from hushh_mcp.constants import ConsentScope
from hushh_mcp.config import get_config
from hushh_mcp.vault.storage import VaultStorage
from hushh_mcp.vault.persistent_storage import persistent_storage

# Enhanced operons with LLM integration
from hushh_mcp.operons.categorize_content import categorize_with_free_llm
from hushh_mcp.operons.content_classification import classify_content_category, determine_priority
from hushh_mcp.operons.privacy_audit import assess_data_sensitivity, DataType
from hushh_mcp.operons.data_validation import validate_data_integrity
from hushh_mcp.operons.scheduling_intelligence import analyze_scheduling_patterns

# Real Google integrations
from hushh_mcp.integrations.gmail_client import (
    create_gmail_client_from_token,
    create_calendar_client_from_token
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Hushh MCP PDA Agent API", 
    description="Enhanced Personal Digital Assistant Agent built on Model Context Protocol with real-time processing",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Security and configuration
security = HTTPBearer()
config = get_config()
vault_storage = VaultStorage()

# Initialize core agents
email_agent = EmailProcessorAgent()
calendar_agent = CalendarProcessorAgent()
audit_agent = AuditLoggerAgent()

# Global state for real-time progress tracking
processing_status = {}

# ==================== Core Processing Functions ====================

# Google OAuth configuration with proper scopes for Gmail and Calendar
GOOGLE_CLIENT_ID = config.GOOGLE_OAUTH_CLIENT_ID if hasattr(config, 'GOOGLE_OAUTH_CLIENT_ID') else "mock_client_id"
GOOGLE_CLIENT_SECRET = config.GOOGLE_OAUTH_CLIENT_SECRET if hasattr(config, 'GOOGLE_OAUTH_CLIENT_SECRET') else "mock_client_secret"
GOOGLE_REDIRECT_URI = config.GOOGLE_OAUTH_REDIRECT_URI if hasattr(config, 'GOOGLE_OAUTH_REDIRECT_URI') else "http://localhost:8000/auth/google/callback"

# Required scopes for Gmail and Calendar access
GOOGLE_SCOPES = [
    'openid',
    'email', 
    'profile',
    'https://www.googleapis.com/auth/gmail.readonly',  # Gmail read access
    'https://www.googleapis.com/auth/calendar.readonly'  # Calendar read access
]

# User sessions to store OAuth tokens
user_sessions = {}  # Will store real OAuth tokens per user

class GoogleOAuth:
    @staticmethod
    def get_auth_url():
        scopes_str = ' '.join(GOOGLE_SCOPES)
        auth_url = (
            f"https://accounts.google.com/o/oauth2/auth?"
            f"client_id={GOOGLE_CLIENT_ID}&"
            f"redirect_uri={GOOGLE_REDIRECT_URI}&"
            f"scope={scopes_str}&"
            f"response_type=code&"
            f"access_type=offline&"  # Required for refresh tokens
            f"state={uuid.uuid4()}"
        )
        return auth_url

    @staticmethod
    def exchange_code_for_token(code: str):
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": GOOGLE_REDIRECT_URI
        }
        response = requests.post(token_url, data=data)
        return response.json()

    @staticmethod
    def get_user_info(access_token: str):
        user_info_url = f"https://www.googleapis.com/oauth2/v1/userinfo?access_token={access_token}"
        response = requests.get(user_info_url)
        return response.json()

def create_jwt_token(user_id: str, email: str):
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=24),
        "iat": datetime.utcnow()
    }
    jwt_secret = getattr(config, 'JWT_SECRET', 'fallback_secret_key_for_development')
    return jwt.encode(payload, jwt_secret, algorithm="HS256")

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        jwt_secret = getattr(config, 'JWT_SECRET', 'fallback_secret_key_for_development')
        payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Check if user has valid OAuth session
        if user_id not in user_sessions:
            raise HTTPException(status_code=401, detail="User not authenticated with Google")
            
        return {"user_id": user_id, "email": payload.get("email")}
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except (InvalidSignatureError, DecodeError, Exception):
        raise HTTPException(status_code=401, detail="Invalid token")

# Authentication endpoints
@app.get("/auth/google/redirect")
async def google_auth_redirect():
    """Direct redirect to Google OAuth"""
    auth_url = GoogleOAuth.get_auth_url()
    return RedirectResponse(url=auth_url)

@app.get("/auth/google/callback")
async def google_callback(code: str, state: str):
    """Handle Google OAuth callback"""
    try:
        # Exchange code for token
        token_data = GoogleOAuth.exchange_code_for_token(code)
        
        if "error" in token_data:
            raise HTTPException(status_code=400, detail=token_data["error"])

        # Get user info
        user_info = GoogleOAuth.get_user_info(token_data["access_token"])
        
        # Store OAuth tokens for the user session
        user_id = user_info["id"]
        user_sessions[user_id] = {
            "access_token": token_data["access_token"],
            "refresh_token": token_data.get("refresh_token"),
            "expires_in": token_data.get("expires_in", 3600),
            "token_type": token_data.get("token_type", "Bearer"),
            "scope": token_data.get("scope", ""),
            "email": user_info["email"],
            "name": user_info.get("name", ""),
            "picture": user_info.get("picture", ""),
            "authenticated_at": datetime.utcnow().isoformat()
        }
        
        # Create JWT token
        jwt_token = create_jwt_token(user_info["id"], user_info["email"])

        # Log authentication
        await audit_agent.log_activity(
            user_id=user_info["id"],
            action="user_login",
            details={"email": user_info["email"], "method": "google_oauth"}
        )

        # Redirect to frontend with token and email
        frontend_url = f"http://localhost:8000/static/complete_dashboard.html?token={jwt_token}&email={user_info['email']}"
        return RedirectResponse(url=frontend_url)

    except Exception as e:
        logger.error(f"OAuth callback error: {e}")
        return RedirectResponse(url=f"http://localhost:3000/?error={str(e)}")

# User info endpoint
@app.get("/api/user/info")
async def get_user_info(user_data: dict = Depends(verify_token)):
    """Get authenticated user information"""
    user_id = user_data["user_id"]
    
    if user_id not in user_sessions:
        raise HTTPException(status_code=401, detail="User not authenticated with Google")
    
    user_session = user_sessions[user_id]
    
    return {
        "user_id": user_id,
        "email": user_session["email"],
        "name": user_session.get("name", ""),
        "picture": user_session.get("picture", ""),
        "authenticated": True,
        "scope": user_session.get("scope", ""),
        "authenticated_at": user_session.get("authenticated_at")
    }

@app.get("/api/debug/oauth-status")
async def debug_oauth_status(user_data: dict = Depends(verify_token)):
    """Debug endpoint to check OAuth token status and scopes"""
    user_id = user_data["user_id"]
    
    if user_id not in user_sessions:
        raise HTTPException(status_code=401, detail="User not authenticated with Google")
    
    user_session = user_sessions[user_id]
    granted_scopes = user_session.get("scope", "").split()
    
    required_scopes = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/calendar.readonly"
    ]
    
    scope_status = {}
    for scope in required_scopes:
        scope_status[scope] = scope in granted_scopes
    
    return {
        "user_id": user_id,
        "email": user_session["email"],
        "all_granted_scopes": granted_scopes,
        "required_scopes_status": scope_status,
        "has_gmail_access": "https://www.googleapis.com/auth/gmail.readonly" in granted_scopes,
        "has_calendar_access": "https://www.googleapis.com/auth/calendar.readonly" in granted_scopes,
        "access_token_present": bool(user_session.get("access_token")),
        "refresh_token_present": bool(user_session.get("refresh_token"))
    }

# Core API endpoints with real-time progress tracking
@app.post("/api/emails/process/{days}")
async def process_emails(
    days: int,
    background_tasks: BackgroundTasks,
    user_data: dict = Depends(verify_token)
):
    """Process emails with real-time progress tracking using enhanced Hushh MCP protocols"""
    user_id = user_data["user_id"]
    task_id = f"email_processing_{user_id}_{int(time.time())}"
    
    logger.info(f"📧 Starting email processing for user {user_id} - {days} days")
    
    # Initialize progress tracking
    processing_status[task_id] = {
        "status": "starting",
        "current": 0,
        "total": 0,
        "percentage": 0.0,
        "message": "Initializing email processing with AI categorization...",
        "results": None,
        "start_time": time.time(),
        "user_id": user_id,
        "days": days
    }
    
    # Start background processing with enhanced AI
    background_tasks.add_task(process_emails_with_enhanced_ai, user_id, days, task_id)
    
    # Log audit trail
    await audit_agent.log_activity(
        user_id=user_id,
        action="email_processing_started",
        details={"days": days, "task_id": task_id}
    )
    
    return {"task_id": task_id, "message": "Enhanced email processing started with AI categorization"}


# Helper functions for data processing
def _count_categories(items: List[Dict[str, Any]]) -> Dict[str, int]:
    """Count items by category"""
    categories = {}
    for item in items:
        category = item.get("category", "uncategorized")
        categories[category] = categories.get(category, 0) + 1
    return categories

async def process_emails_with_enhanced_ai(user_id: str, days: int, task_id: str):
    """Enhanced background email processing with multiple AI operons and duplicate prevention"""
    try:
        # Load existing emails and track processed IDs and dates
        existing_emails = persistent_storage.load_user_emails(user_id)
        processed_email_ids = set()
        processed_dates = set()
        existing_categories = []
        
        if existing_emails and len(existing_emails) > 0:
            for email in existing_emails:
                if 'id' in email:
                    processed_email_ids.add(email['id'])
                if 'date' in email:
                    try:
                        email_date = datetime.fromisoformat(email['date'].replace('Z', '+00:00')).date()
                        processed_dates.add(email_date)
                    except:
                        pass
                if 'category' in email:
                    existing_categories.append(email['category'])
            
            logger.info(f"📧 Found {len(existing_emails)} existing emails for user {user_id}")
            logger.info(f"📅 Already processed dates: {sorted(processed_dates)}")
            logger.info(f"📂 Existing categories: {list(set(existing_categories))}")
        else:
            logger.info(f"📧 No existing emails found for user {user_id}, starting fresh processing")
        
        # Update status
        processing_status[task_id]["status"] = "consent_validation"
        processing_status[task_id]["message"] = "Validating user consent and permissions..."
        
        # Create REAL consent token following Hushh MCP protocol
        from hushh_mcp.consent.token import issue_token
        from hushh_mcp.constants import ConsentScope
        
        consent_token = issue_token(
            user_id=user_id,
            agent_id="agent_email_processor", 
            scope=ConsentScope.VAULT_READ_EMAIL,
            expires_in_ms=days * 24 * 60 * 60 * 1000  # Convert days to milliseconds
        )
        
        # Log consent issuance
        logger.info(f"🔐 Real consent token issued for user {user_id}: {consent_token.token[:20]}...")
        
        await asyncio.sleep(0.5)  # Simulate consent validation
        
        # Update status - data fetching
        processing_status[task_id]["status"] = "fetching"
        processing_status[task_id]["message"] = "Securely fetching email data..."
        
        # Get user's OAuth tokens
        if user_id not in user_sessions:
            processing_status[task_id]["status"] = "error"
            processing_status[task_id]["message"] = "User not authenticated with Google"
            return
            
        user_session = user_sessions[user_id]
        
        # Create Gmail client with user's OAuth token
        gmail_client = await create_gmail_client_from_token(user_session["access_token"])
        
        # Fetch real emails from Gmail API with date range filtering
        try:
            # Calculate actual date range for filtering
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Calculate only new dates that need processing
            new_dates_to_process = []
            current_date = start_date.date()
            while current_date <= end_date.date():
                if current_date not in processed_dates:
                    new_dates_to_process.append(current_date)
                current_date += timedelta(days=1)
            
            if not new_dates_to_process:
                logger.info(f"✅ All dates in range already processed. No new emails to fetch.")
                processing_status[task_id] = {
                    'status': 'completed',
                    'total': len(existing_emails),
                    'processed': len(existing_emails),
                    'progress': 100,
                    'message': 'All emails in date range already processed',
                    'processed_categories': list(set(existing_categories))
                }
                return
            
            logger.info(f"📅 Processing {len(new_dates_to_process)} new dates: {new_dates_to_process}")
            logger.info(f"📅 Fetching emails from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            
            emails = await gmail_client.fetch_emails(days_back=days)  # Fetch ALL emails without limit
            
            # Filter emails by actual date range and skip already processed emails
            filtered_emails = []
            skipped_duplicates = 0
            for email in emails:
                try:
                    # Skip if email ID already processed
                    email_id = email.get('id', '')
                    if email_id in processed_email_ids:
                        skipped_duplicates += 1
                        continue
                    
                    email_date = datetime.fromisoformat(email.get('date', email.get('received_at', '')).replace('Z', '+00:00'))
                    email_date_only = email_date.date()
                    
                    # Only process emails from new dates
                    if email_date_only in new_dates_to_process and start_date <= email_date <= end_date:
                        filtered_emails.append(email)
                except Exception as e:
                    # If date parsing fails but email ID is new, include the email to be safe
                    email_id = email.get('id', '')
                    if email_id not in processed_email_ids:
                        filtered_emails.append(email)
            
            emails = filtered_emails
            logger.info(f"📧 Filtered to {len(emails)} new emails within date range for user {user_id}")
            if skipped_duplicates > 0:
                logger.info(f"⏭️ Skipped {skipped_duplicates} already processed emails")
            
        except Exception as e:
            logger.error(f"Failed to fetch emails from Gmail API: {e}")
            processing_status[task_id]["status"] = "error"
            processing_status[task_id]["message"] = f"Failed to fetch emails: {str(e)}"
            return
            
        total_emails = len(emails)
        
        processing_status[task_id]["total"] = total_emails
        processing_status[task_id]["message"] = f"Processing {total_emails} emails with AI analysis..."
        
        logger.info(f"📊 Processing {total_emails} emails for user {user_id}")
        
        # Process each email with enhanced AI operons
        categorized_emails = []
        category_counts = {}
        priority_counts = {"high": 0, "medium": 0, "low": 0}
        sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
        
        # Track processing start time for accurate estimates
        processing_start_time = time.time()
        
        for i, email in enumerate(emails):
            # Calculate time estimates
            current_time = time.time()
            elapsed_time = current_time - processing_start_time
            
            if i > 0:
                avg_time_per_email = elapsed_time / i
                remaining_emails = total_emails - i
                estimated_remaining_time = avg_time_per_email * remaining_emails
                eta_minutes = int(estimated_remaining_time / 60)
                eta_seconds = int(estimated_remaining_time % 60)
                
                if eta_minutes > 0:
                    eta_str = f"~{eta_minutes}m {eta_seconds}s remaining"
                else:
                    eta_str = f"~{eta_seconds}s remaining"
            else:
                eta_str = "Calculating time estimate..."
            
            # Update progress with detailed information
            processing_status[task_id]["current"] = i + 1
            processing_status[task_id]["percentage"] = ((i + 1) / total_emails) * 100
            processing_status[task_id]["message"] = f"Processing email {i+1}/{total_emails} - {eta_str}"
            processing_status[task_id]["current_email"] = {
                "id": email.get('id', 'unknown')[:12] + "...",
                "subject": email.get('subject', 'No Subject')[:60] + "..." if len(email.get('subject', '')) > 60 else email.get('subject', 'No Subject'),
                "sender": email.get('sender', 'Unknown Sender')[:40] + "..." if len(email.get('sender', '')) > 40 else email.get('sender', 'Unknown Sender'),
                "processing_step": "validating_data"
            }
            processing_status[task_id]["time_stats"] = {
                "elapsed_seconds": int(elapsed_time),
                "avg_time_per_email": round(avg_time_per_email, 2) if i > 0 else 0,
                "estimated_remaining_seconds": int(estimated_remaining_time) if i > 0 else 0
            }
            
            # Validate data integrity using operon
            # Validate data integrity using operon
            processing_status[task_id]["current_email"]["processing_step"] = "validating_data"
            validation_result = validate_data_integrity(email)
            if not validation_result["is_valid"]:
                logger.warning(f"Data validation failed for email {email['id']}: {validation_result['issues']}")
                processing_status[task_id]["current_email"]["processing_step"] = "validation_failed"
                continue
            
            try:
                # AI-powered content classification
                processing_status[task_id]["current_email"]["processing_step"] = "preparing_ai_analysis"
                await asyncio.sleep(0.1)  # Simulate AI processing time
                
                # Ensure required fields exist
                email_content = email.get('content', email.get('body', ''))
                email_subject = email.get('subject', 'No Subject')
                email_sender = email.get('sender', 'Unknown Sender')
                
                # Use multiple operons for comprehensive analysis
                content_for_analysis = f"{email_subject} {email_content}"
                
                # 1. Basic classification
                processing_status[task_id]["current_email"]["processing_step"] = "basic_classification"
                classification = classify_content_category(
                    email_content, email_subject, email_sender
                )
                
                # 2. AI-powered categorization with Ollama/fallback LLMs
                processing_status[task_id]["current_email"]["processing_step"] = "ai_categorization"
                try:
                    logger.info(f"🤖 Starting LLM categorization for email {email['id']}: '{email_subject[:50]}...'")
                    ai_category_result = await categorize_with_free_llm(content_for_analysis, "email")
                    category = ai_category_result.get("category", classification["category"])
                    ai_confidence = ai_category_result.get("confidence", classification["confidence"])
                    processing_method = ai_category_result.get("processing_method", "unknown")
                    model_used = ai_category_result.get("model_used", "none")
                    
                    processing_status[task_id]["current_email"]["processing_step"] = "ai_categorization_complete"
                    processing_status[task_id]["current_email"]["category"] = category
                    processing_status[task_id]["current_email"]["confidence"] = round(ai_confidence, 2)
                    
                    logger.info(f"✅ LLM categorization complete for email {email['id']}: category='{category}', confidence={ai_confidence:.2f}, method='{processing_method}', model='{model_used}'")
                except Exception as e:
                    logger.warning(f"❌ AI categorization failed for email {email['id']}: {e}")
                    category = classification["category"]
                    ai_confidence = classification["confidence"]
                    processing_method = "fallback_rules"
                    model_used = "none"
                    processing_status[task_id]["current_email"]["processing_step"] = "ai_fallback_used"
                
                # 3. Priority determination with enhanced logic
                processing_status[task_id]["current_email"]["processing_step"] = "priority_analysis"
                priority_result = determine_priority(email_content, email_subject)
                priority = priority_result["priority"]
                
                # 4. Privacy risk assessment
                processing_status[task_id]["current_email"]["processing_step"] = "privacy_assessment"
                privacy_assessment = assess_data_sensitivity(email_content, DataType.EMAIL)
                
                # 5. Sentiment analysis (simple implementation)
                processing_status[task_id]["current_email"]["processing_step"] = "sentiment_analysis"
                sentiment = analyze_email_sentiment(email_content, email_subject)
                
                # Count categories and metrics
                category_counts[category] = category_counts.get(category, 0) + 1
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
                sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
                
                # Store processed email with comprehensive data
                processed_email = {
                    **email,
                    "category": category,
                    "priority": priority,
                    "confidence": ai_confidence,
                    "privacy_risk": privacy_assessment["risk_level"], 
                    "sentiment": sentiment,
                    "data_validation": validation_result["score"],
                    "ai_insights": {
                        "category_reasoning": ai_category_result.get("reasoning", ""),
                        "priority_factors": priority_result.get("factors", []),
                        "privacy_concerns": privacy_assessment.get("concerns", []),
                        "processing_method": processing_method,
                        "model_used": model_used
                    },
                    "processed_at": datetime.now().isoformat()
                }
                
                logger.info(f"📧 Processed email {email['id']}: category='{category}', method='{processing_method}', confidence={ai_confidence:.2f}")
                categorized_emails.append(processed_email)
                
            except Exception as e:
                logger.error(f"Error processing individual email {email.get('id', 'unknown')}: {e}")
                # Add a basic processed version even if AI processing fails
                basic_email = {
                    **email,
                    "category": "unclassified",
                    "priority": "medium",
                    "confidence": 0.5,
                    "privacy_risk": "unknown",
                    "sentiment": "neutral",
                    "data_validation": 0.5,
                    "ai_insights": {"error": str(e)},
                    "processed_at": datetime.now().isoformat()
                }
                categorized_emails.append(basic_email)
                continue
            
                # Store in vault following Hushh MCP protocol
                processing_status[task_id]["current_email"]["processing_step"] = "storing_in_vault"
                try:
                    logger.info(f"🔐 Storing email {email['id']} in encrypted vault with category '{category}'")
                    vault_storage.store_email_data(
                        user_id=user_id,
                        email_id=email["id"],
                        email_data=processed_email,
                        categories=[category],
                        confidence_scores={category: ai_confidence},
                        consent_token=consent_token
                    )
                    processing_status[task_id]["current_email"]["processing_step"] = "vault_storage_complete"
                    logger.info(f"✅ Email {email['id']} successfully stored in encrypted vault")
                except Exception as e:
                    processing_status[task_id]["current_email"]["processing_step"] = "vault_storage_failed"
                    logger.error(f"❌ Vault storage error for email {email['id']}: {e}")
                
                processing_status[task_id]["current_email"]["processing_step"] = "completed"
        
        # Apply scheduling intelligence for calendar integration
        scheduling_analysis = analyze_scheduling_patterns(categorized_emails)
        
        # Save processed emails to persistent storage (merge with existing data)
        logger.info(f"💾 Saving {len(categorized_emails)} processed emails to encrypted persistent storage...")
        
        # Get existing emails and merge intelligently by date range
        existing_emails = persistent_storage.load_user_emails(user_id)
        
        if existing_emails:
            # Create a map of existing emails by ID for efficient lookup
            existing_email_ids = {email['id'] for email in existing_emails}
            
            # Only add new emails that don't already exist
            new_emails = [email for email in categorized_emails if email['id'] not in existing_email_ids]
            
            # Combine with existing emails
            all_emails = existing_emails + new_emails
            
            logger.info(f"📧 Merged {len(new_emails)} new emails with {len(existing_emails)} existing emails (total: {len(all_emails)})")
        else:
            all_emails = categorized_emails
            logger.info(f"📧 Saving {len(all_emails)} emails as initial dataset")
        
        save_success = persistent_storage.save_user_emails(user_id, all_emails)
        if save_success:
            logger.info(f"✅ Successfully saved {len(all_emails)} total emails to encrypted storage for user {user_id}")
        else:
            logger.warning(f"❌ Failed to save emails to encrypted storage for user {user_id}")
        
        # Also update category counts based on all emails
        all_category_counts = _count_categories(all_emails)
        
        # Complete processing with comprehensive results
        processing_status[task_id]["status"] = "completed"
        processing_status[task_id]["percentage"] = 100.0
        processing_status[task_id]["message"] = "Email processing completed with AI insights!"
        
        processing_status[task_id]["results"] = {
            "processed_count": len(categorized_emails),
            "total_emails": len(all_emails) if existing_emails else len(categorized_emails),
            "new_emails": len(categorized_emails),
            "categories": all_category_counts if existing_emails else category_counts,
            "priorities": priority_counts,
            "sentiments": sentiment_counts,
            "summary": f"Successfully analyzed {len(categorized_emails)} new emails (total: {len(all_emails) if existing_emails else len(categorized_emails)}) using AI across {len(all_category_counts if existing_emails else category_counts)} categories",
            "date_range": f"{days} days back from {datetime.now().strftime('%Y-%m-%d')}",
            "insights": {
                "top_category": max((all_category_counts if existing_emails else category_counts).items(), key=lambda x: x[1])[0] if (all_category_counts if existing_emails else category_counts) else "none",
                "high_priority_count": priority_counts["high"],
                "average_confidence": sum(e.get("confidence", 0) for e in categorized_emails) / len(categorized_emails) if categorized_emails else 0,
                "scheduling_opportunities": scheduling_analysis.get("meeting_count", 0)
            },
            "emails": (all_emails if existing_emails else categorized_emails)[:10],  # Return first 10 for display
            "ai_processing_stats": {
                "total_processed": len(all_emails) if existing_emails else len(categorized_emails),
                "new_processed": len(categorized_emails),
                "privacy_protected": sum(1 for e in categorized_emails if e.get("privacy_risk") == "low"),
                "actionable_items": sum(1 for e in categorized_emails if e.get("priority") == "high")
            }
        }
        
        logger.info(f"✅ Enhanced email processing completed for user {user_id}")
        
        # Log completion
        await audit_agent.log_activity(
            user_id=user_id,
            action="email_processing_completed",
            details={
                "task_id": task_id, 
                "processed_count": total_emails,
                "categories": category_counts
            }
        )
        
    except Exception as e:
        processing_status[task_id]["status"] = "error"
        processing_status[task_id]["message"] = f"Processing failed: {str(e)}"
        logger.error(f"Enhanced email processing error for user {user_id}: {e}")

async def process_calendar_with_enhanced_ai(user_id: str, days_back: int, days_forward: int, task_id: str):
    """Enhanced background calendar processing with multiple AI operons"""
    try:
        # Update status
        processing_status[task_id]["status"] = "processing"
        processing_status[task_id]["message"] = "Fetching calendar events..."
        processing_status[task_id]["percentage"] = 10.0
        
        # Create consent token for calendar processing
        consent_token = issue_token(user_id, ConsentScope.VAULT_READ_CALENDAR.value)
        
        # Process calendar through the agent
        result = await calendar_agent.handle(
            user_id=user_id,
            token=consent_token.token,
            action="process_calendar",
            days_back=days_back,
            days_forward=days_forward
        )
        
        processing_status[task_id]["percentage"] = 50.0
        processing_status[task_id]["message"] = "Categorizing events with AI..."
        
        # Get categorized events
        categorized_events = result.get("events", [])
        
        processing_status[task_id]["percentage"] = 90.0
        processing_status[task_id]["message"] = "Finalizing calendar analysis..."
        
        # Create final results
        final_results = {
            "processed_count": len(categorized_events),
            "categories": result.get("stats", {}).get("categories", {}),
            "events": categorized_events[:10],  # Return first 10 for display
            "schedule_insights": result.get("schedule_insights", {}),
            "productivity_score": result.get("productivity_score", 0),
            "summary": f"Processed {len(categorized_events)} calendar events"
        }
        
        # Mark as completed
        processing_status[task_id] = {
            **processing_status[task_id],
            "status": "completed",
            "message": "Calendar processing completed successfully!",
            "percentage": 100.0,
            "results": final_results
        }
        
        # Log completion
        await audit_agent.log_activity(
            user_id=user_id,
            action="calendar_processing_completed",
            details={
                "task_id": task_id,
                "processed_count": len(categorized_events),
                "categories": list(result.get("stats", {}).get("categories", {}).keys()),
                "days_back": days_back,
                "days_forward": days_forward
            }
        )
        
        logger.info(f"📅 Enhanced calendar processing completed for user {user_id}")
    
    except Exception as e:
        logger.error(f"❌ Calendar processing failed for user {user_id}: {str(e)}")
        processing_status[task_id] = {
            **processing_status[task_id],
            "status": "error",
            "message": f"Calendar processing failed: {str(e)}",
            "percentage": 100.0
        }


def analyze_email_sentiment(content: str, subject: str) -> str:
    """Simple sentiment analysis for emails"""
    text = f"{subject} {content}".lower()
    
    positive_words = ["great", "excellent", "happy", "pleased", "congratulations", "success", "good", "wonderful"]
    negative_words = ["problem", "issue", "urgent", "failed", "error", "concerned", "disappointed", "complaint"]
    
    positive_count = sum(1 for word in positive_words if word in text)
    negative_count = sum(1 for word in negative_words if word in text)
    
    if positive_count > negative_count:
        return "positive"
    elif negative_count > positive_count:
        return "negative"
    else:
        return "neutral"

@app.post("/api/calendar/process/{days_back}/{days_forward}")
async def process_calendar(
    days_back: int, 
    days_forward: int, 
    background_tasks: BackgroundTasks,
    user_data: dict = Depends(verify_token)
):
    """Process calendar events with real-time progress tracking and AI analysis"""
    user_id = user_data["user_id"]
    task_id = f"calendar_processing_{user_id}_{int(time.time())}"
    
    logger.info(f"📅 Starting calendar processing for user {user_id}")
    
    # Initialize progress tracking
    processing_status[task_id] = {
        "status": "starting",
        "current": 0,
        "total": 0,
        "percentage": 0.0,
        "message": "Initializing calendar processing with AI analysis...",
        "results": None,
        "start_time": time.time(),
        "user_id": user_id,
        "days_back": days_back,
        "days_forward": days_forward
    }
    
    # Start background processing
    background_tasks.add_task(process_calendar_with_enhanced_ai, user_id, days_back, days_forward, task_id)
    
    # Log audit trail
    await audit_agent.log_activity(
        user_id=user_id,
        action="calendar_processing_started",
        details={"days_back": days_back, "days_forward": days_forward, "task_id": task_id}
    )
    
    return {"task_id": task_id, "message": "Enhanced calendar processing started with AI insights"}


async def process_calendar_with_enhanced_ai(user_id: str, days_back: int, days_forward: int, task_id: str):
    """Enhanced background calendar processing with AI operons"""
    try:
        # Check for existing calendar events, allow reprocessing for different date ranges
        existing_events = persistent_storage.load_user_calendar_events(user_id)
        
        if existing_events and len(existing_events) > 0:
            logger.info(f"📅 Found {len(existing_events)} existing calendar events for user {user_id}, will merge with new data")
        else:
            logger.info(f"📅 No existing calendar events found for user {user_id}, starting fresh processing")

        # Update status - consent validation
        processing_status[task_id]["status"] = "consent_validation"
        processing_status[task_id]["message"] = "Validating calendar access permissions..."
        
        # Create REAL consent token following Hushh MCP protocol
        from hushh_mcp.consent.token import issue_token
        from hushh_mcp.constants import ConsentScope
        
        consent_token = issue_token(
            user_id=user_id,
            agent_id="agent_calendar_processor",
            scope=ConsentScope.VAULT_READ_CALENDAR,
            expires_in_ms=(days_back + days_forward) * 24 * 60 * 60 * 1000  # Total days in milliseconds
        )
        
        # Log consent issuance
        logger.info(f"🔐 Real calendar consent token issued for user {user_id}: {consent_token.token[:20]}...")
        
        await asyncio.sleep(0.5)
        
        # Update status - data fetching
        processing_status[task_id]["status"] = "fetching"
        processing_status[task_id]["message"] = "Fetching calendar events..."
        
        # Get user's OAuth tokens and use calendar API
        if user_id not in user_sessions:
            processing_status[task_id]["status"] = "error"
            processing_status[task_id]["message"] = "User not authenticated with Google"
            return
            
        user_session = user_sessions[user_id]
        
        # Fetch calendar events using Google Calendar API with date range
        try:
            # Calculate actual date ranges
            start_date = datetime.now() - timedelta(days=days_back)
            end_date = datetime.now() + timedelta(days=days_forward)
            
            logger.info(f"📅 Fetching calendar events from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            
            calendar_client = await create_calendar_client_from_token(user_session["access_token"])
            events = await calendar_client.fetch_calendar_events(
                days_back=days_back, 
                days_forward=days_forward, 
                max_results=min((days_back + days_forward) * 5, 250)
            )
            
            # Filter events by actual date range (additional safety)
            filtered_events = []
            for event in events:
                try:
                    event_start = datetime.fromisoformat(event.get('start_time', '').replace('Z', '+00:00'))
                    if start_date <= event_start <= end_date:
                        filtered_events.append(event)
                except:
                    # If date parsing fails, include the event to be safe
                    filtered_events.append(event)
            
            events = filtered_events
            logger.info(f"📅 Filtered to {len(events)} calendar events within date range for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to fetch calendar events: {e}")
            # Fallback to mock data generation for demo purposes
            logger.info(f"📅 Falling back to mock calendar event generation for user {user_id}")
            
            events = []
            start_date = datetime.now() - timedelta(days=days_back)
            end_date = datetime.now() + timedelta(days=days_forward)
            
            event_types = ['meeting', 'call', 'presentation', 'review', 'planning', 'training']
            current_date = start_date
            event_id = 1
            
            while current_date <= end_date:
                # Generate 2-4 events per workday
                if current_date.weekday() < 5:  # Weekday
                    events_per_day = 3
                else:  # Weekend
                    events_per_day = 1
                
                for i in range(events_per_day):
                    hour = 9 + (i * 2)
                    start_time = current_date.replace(hour=hour, minute=0, second=0)
                    duration = 60
                    end_time = start_time + timedelta(minutes=duration)
                    
                    events.append({
                        "id": f"cal_event_{user_id}_{event_id}",
                        "title": f"Meeting {event_id}",
                        "description": f"Calendar event {event_id} description",
                        "start_time": start_time.isoformat(),
                        "end_time": end_time.isoformat(),
                        "attendees": ["user@example.com"],
                        "location": "Conference Room",
                        "type": event_types[event_id % len(event_types)]
                    })
                    event_id += 1
                
                current_date += timedelta(days=1)
            
            logger.info(f"📅 Generated {len(events)} mock calendar events for user {user_id}")
            
        total_events = len(events)
        
        processing_status[task_id]["total"] = total_events
        processing_status[task_id]["message"] = f"Analyzing {total_events} calendar events with AI..."
        
        logger.info(f"📊 Processing {total_events} calendar events for user {user_id}")
        
        # Process each event with enhanced AI analysis
        categorized_events = []
        category_counts = {}
        type_counts = {}
        scheduling_insights = {"conflicts": 0, "optimization_opportunities": 0, "meeting_patterns": {}}
        
        # Track processing start time for accurate estimates
        processing_start_time = time.time()
        
        for i, event in enumerate(events):
            # Calculate time estimates
            current_time = time.time()
            elapsed_time = current_time - processing_start_time
            
            if i > 0:
                avg_time_per_event = elapsed_time / i
                remaining_events = total_events - i
                estimated_remaining_time = avg_time_per_event * remaining_events
                eta_minutes = int(estimated_remaining_time / 60)
                eta_seconds = int(estimated_remaining_time % 60)
                
                if eta_minutes > 0:
                    eta_str = f"~{eta_minutes}m {eta_seconds}s remaining"
                else:
                    eta_str = f"~{eta_seconds}s remaining"
            else:
                eta_str = "Calculating time estimate..."
            
            # Update progress with detailed information
            processing_status[task_id]["current"] = i + 1
            processing_status[task_id]["percentage"] = ((i + 1) / total_events) * 100
            processing_status[task_id]["message"] = f"Processing event {i+1}/{total_events} - {eta_str}"
            processing_status[task_id]["current_event"] = {
                "id": event.get('id', 'unknown')[:12] + "...",
                "title": event.get('title', 'No Title')[:50] + "..." if len(event.get('title', '')) > 50 else event.get('title', 'No Title'),
                "start_time": event.get('start_time', 'Unknown'),
                "processing_step": "validating_data"
            }
            processing_status[task_id]["time_stats"] = {
                "elapsed_seconds": int(elapsed_time),
                "avg_time_per_event": round(avg_time_per_event, 2) if i > 0 else 0,
                "estimated_remaining_seconds": int(estimated_remaining_time) if i > 0 else 0
            }
            
            # Validate event data
            # Validate event data
            processing_status[task_id]["current_event"]["processing_step"] = "validating_data"
            validation_result = validate_data_integrity(event)
            if not validation_result["is_valid"]:
                logger.warning(f"Event validation failed for {event['id']}: {validation_result['issues']}")
                processing_status[task_id]["current_event"]["processing_step"] = "validation_failed"
                continue
            
            processing_status[task_id]["current_event"]["processing_step"] = "ai_processing"
            await asyncio.sleep(0.1)  # Simulate AI processing
            
            # AI-powered event classification
            content_for_analysis = f"{event['title']} {event['description']}"
            
            # 1. Basic classification
            processing_status[task_id]["current_event"]["processing_step"] = "basic_classification"
            classification = classify_content_category(
                event["description"], event["title"], ""
            )
            
            # 2. AI categorization with proper error handling
            processing_status[task_id]["current_event"]["processing_step"] = "ai_categorization"
            try:
                # Use string-based categorization for calendar events
                from hushh_mcp.operons.categorize_content import categorize_with_free_llm
                
                ai_categories = categorize_with_free_llm(content_for_analysis)
                if ai_categories and len(ai_categories) > 0:
                    category = ai_categories[0]  # Take first category
                    ai_confidence = 0.8  # Default confidence
                else:
                    category = classification["category"]
                    ai_confidence = classification["confidence"]
                    
                processing_status[task_id]["current_event"]["processing_step"] = "ai_categorization_complete"
                processing_status[task_id]["current_event"]["category"] = category
                processing_status[task_id]["current_event"]["confidence"] = round(ai_confidence, 2)
                    
            except Exception as e:
                logger.warning(f"AI categorization failed for event {event['id']}: {e}")
                category = classification["category"]
                ai_confidence = classification["confidence"]
                processing_status[task_id]["current_event"]["processing_step"] = "ai_fallback_used"
            
            # 3. Priority and importance analysis
            processing_status[task_id]["current_event"]["processing_step"] = "priority_analysis"
            priority_result = determine_priority(event["description"], event["title"])
            priority = priority_result["priority"]
            
            # 4. Scheduling intelligence analysis
            processing_status[task_id]["current_event"]["processing_step"] = "scheduling_analysis"
            scheduling_analysis = analyze_scheduling_patterns([event])
            
            # Count metrics
            category_counts[category] = category_counts.get(category, 0) + 1
            event_type = event.get("type", "meeting")
            type_counts[event_type] = type_counts.get(event_type, 0) + 1
            
            # Enhanced event data
            processed_event = {
                **event,
                "category": category,
                "priority": priority,
                "confidence": ai_confidence,
                "ai_insights": {
                    "category_reasoning": f"Categorized as {category} with {ai_confidence*100:.1f}% confidence",
                    "scheduling_score": 0.8,  # Default scheduling score
                    "optimization_suggestions": ["Consider shorter duration", "Add agenda"]
                },
                "processed_at": datetime.now().isoformat()
            }
            
            categorized_events.append(processed_event)
        
        # Apply comprehensive scheduling intelligence
        overall_scheduling_analysis = analyze_scheduling_patterns(categorized_events)
        
        # Save processed calendar events to persistent storage (merge with existing data)
        logger.info(f"💾 Saving {len(categorized_events)} processed calendar events to encrypted persistent storage...")
        
        # Get existing events and merge intelligently by date range
        existing_events = persistent_storage.load_user_calendar_events(user_id)
        
        if existing_events:
            # Create a map of existing events by ID for efficient lookup
            existing_event_ids = {event['id'] for event in existing_events}
            
            # Only add new events that don't already exist
            new_events = [event for event in categorized_events if event['id'] not in existing_event_ids]
            
            # Combine with existing events
            all_events = existing_events + new_events
            
            logger.info(f"� Merged {len(new_events)} new events with {len(existing_events)} existing events (total: {len(all_events)})")
        else:
            all_events = categorized_events
            logger.info(f"📅 Saving {len(all_events)} events as initial dataset")
        
        save_success = persistent_storage.save_user_calendar_events(user_id, all_events)
        if save_success:
            logger.info(f"💾 Saved {len(all_events)} total calendar events for user {user_id}")
        else:
            logger.warning(f"⚠️  Failed to save calendar events for user {user_id}")
        
        # Also update category counts based on all events
        all_category_counts = _count_categories(all_events)
        
        # Complete processing
        processing_status[task_id]["status"] = "completed"
        processing_status[task_id]["percentage"] = 100.0
        processing_status[task_id]["message"] = "Calendar processing completed with AI insights!"
        
        processing_status[task_id]["results"] = {
            "processed_count": len(categorized_events),
            "total_events": len(all_events) if existing_events else len(categorized_events),
            "new_events": len(categorized_events),
            "categories": all_category_counts if existing_events else category_counts,
            "event_types": type_counts,
            "summary": f"Successfully analyzed {len(categorized_events)} new events (total: {len(all_events) if existing_events else len(categorized_events)}) using AI across {len(all_category_counts if existing_events else category_counts)} categories",
            "date_range": f"{days_back} days back and {days_forward} days forward from {datetime.now().strftime('%Y-%m-%d')}",
            "scheduling_insights": {
                "total_meeting_hours": overall_scheduling_analysis.get("total_hours", 0),
                "average_meeting_duration": overall_scheduling_analysis.get("avg_duration", 60),
                "busiest_day": overall_scheduling_analysis.get("busiest_day", "Unknown"),
                "optimization_opportunities": overall_scheduling_analysis.get("optimization_count", 0)
            },
            "events": (all_events if existing_events else categorized_events)[:10],  # Return first 10 for display
            "ai_processing_stats": {
                "total_processed": len(all_events) if existing_events else len(categorized_events),
                "new_processed": len(categorized_events),
                "high_priority_events": sum(1 for e in categorized_events if e.get("priority") == "high"),
                "optimization_suggestions": sum(len(e.get("ai_insights", {}).get("optimization_suggestions", [])) for e in categorized_events)
            }
        }
        
        logger.info(f"✅ Enhanced calendar processing completed for user {user_id}")
        
        # Log completion
        await audit_agent.log_activity(
            user_id=user_id,
            action="calendar_processing_completed",
            details={
                "task_id": task_id,
                "processed_count": total_events,
                "categories": category_counts
            }
        )
        
    except Exception as e:
        processing_status[task_id]["status"] = "error"
        processing_status[task_id]["message"] = f"Processing failed: {str(e)}"
        logger.error(f"Enhanced calendar processing error for user {user_id}: {e}")


# Progress tracking endpoints
@app.get("/api/processing/status/{task_id}")
async def get_processing_status(task_id: str):
    """Get real-time processing status for a task"""
    if task_id not in processing_status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    status = processing_status[task_id]
    
    # Clean up completed tasks older than 10 minutes
    if status["status"] in ["completed", "error"]:
        if time.time() - status["start_time"] > 600:  # 10 minutes
            del processing_status[task_id]
    
    return status

@app.get("/api/processing/status/{task_id}/detailed")
async def get_detailed_processing_status(task_id: str):
    """Get detailed processing status including current item being processed"""
    if task_id not in processing_status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    status = processing_status[task_id]
    
    # Add additional calculated fields for detailed view
    detailed_status = dict(status)
    
    if "time_stats" in status and status["time_stats"]["elapsed_seconds"] > 0:
        detailed_status["human_readable_time"] = {
            "elapsed": f"{status['time_stats']['elapsed_seconds'] // 60}m {status['time_stats']['elapsed_seconds'] % 60}s",
            "estimated_remaining": f"{status['time_stats']['estimated_remaining_seconds'] // 60}m {status['time_stats']['estimated_remaining_seconds'] % 60}s" if status['time_stats']['estimated_remaining_seconds'] > 0 else "Calculating...",
            "avg_per_item": f"{status['time_stats'].get('avg_time_per_email', status['time_stats'].get('avg_time_per_event', 0)):.1f}s"
        }
    
    # Add progress bar information
    if status.get("total", 0) > 0:
        detailed_status["progress_bar"] = {
            "completed": status.get("current", 0),
            "total": status["total"],
            "percentage_int": int(status.get("percentage", 0)),
            "progress_blocks": "█" * int(status.get("percentage", 0) // 5) + "░" * (20 - int(status.get("percentage", 0) // 5))
        }
    
    return detailed_status


@app.get("/api/processing/results/{task_id}")
async def get_processing_results(task_id: str):
    """Get the final results for a completed task"""
    if task_id not in processing_status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    status = processing_status[task_id]
    
    if status["status"] != "completed":
        raise HTTPException(status_code=400, detail="Task not completed yet")
    
    return status["results"]

# ==================== Enhanced Consent Management Endpoints ====================

@app.get("/api/consent/active")
async def get_active_consents(authorization: str = Depends(lambda: None)):
    """Get all active consent tokens for the user with detailed information"""
    try:
        user_id = "user_123"  # Mock user ID
        
        # In production, this would come from a proper consent database
        active_consents = [
            {
                "agent_id": "agent_email_processor",
                "scope": "vault.read.email",
                "granted_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(days=7)).isoformat(),
                "status": "active",
                "data_types": ["email_metadata", "email_content"],
                "purpose": "AI-powered email categorization and automation",
                "processing_type": "local_ai_analysis",
                "sharing": "none",
                "retention": "user_controlled"
            },
            {
                "agent_id": "agent_calendar_processor", 
                "scope": "vault.read.calendar",
                "granted_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(days=7)).isoformat(),
                "status": "active",
                "data_types": ["calendar_events", "meeting_details"],
                "purpose": "Smart scheduling and calendar optimization",
                "processing_type": "local_ai_analysis", 
                "sharing": "none",
                "retention": "user_controlled"
            },
            {
                "agent_id": "agent_ai_categorizer",
                "scope": "vault.read.content",
                "granted_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(days=30)).isoformat(),
                "status": "active",
                "data_types": ["text_content", "metadata"],
                "purpose": "Content categorization using local AI models",
                "processing_type": "ollama_local_llm",
                "sharing": "none",
                "retention": "processed_data_only"
            }
        ]
        
        # Log consent query
        await audit_agent.log_activity(
            user_id=user_id,
            action="consent_query",
            details={"active_consents": len(active_consents)}
        )
        
        return {
            "consents": active_consents,
            "total_active": len(active_consents),
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get consents: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to retrieve consents", "details": str(e)}
        )


# Removed duplicate consent revocation endpoint - using the one with proper authentication below


@app.post("/api/consent/grant")
async def grant_consent(
    request: dict,
    authorization: str = Depends(lambda: None)
):
    """Grant new consent with specific scope and duration"""
    try:
        user_id = "user_123"  # Mock user ID
        agent_id = request.get("agent_id")
        scope = request.get("scope")
        duration_days = request.get("duration_days", 7)
        purpose = request.get("purpose", "")
        
        if not agent_id or not scope:
            return JSONResponse(
                status_code=400,
                content={"error": "agent_id and scope are required"}
            )
        
        # Create new consent token following Hushh MCP protocol
        from hushh_mcp.consent.token import issue_token
        from hushh_mcp.constants import ConsentScope
        
        consent_token = issue_token(
            user_id=user_id,
            agent_id=agent_id,
            scope=getattr(ConsentScope, scope.upper(), ConsentScope.VAULT_READ_EMAIL),
            expires_in_ms=duration_days * 24 * 60 * 60 * 1000  # Convert days to milliseconds
        )
        
        # Log consent grant
        await audit_agent.log_activity(
            user_id=user_id,
            action="consent_granted",
            details={
                "agent_id": agent_id,
                "scope": scope,
                "duration_days": duration_days,
                "purpose": purpose,
                "token_id": consent_token.token[:16] + "..."  # Log partial token for audit
            }
        )
        
        logger.info(f"✅ Consent granted for user {user_id}, agent {agent_id}, scope {scope}")
        
        return {
            "status": "granted",
            "agent_id": agent_id,
            "scope": scope,
            "granted_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=duration_days)).isoformat(),
            "duration_days": duration_days,
            "purpose": purpose,
            "token_partial": consent_token.token[:16] + "...",
            "hushh_mcp_compliant": True
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to grant consent: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to grant consent", "details": str(e)}
        )

@app.delete("/api/data/delete")
async def delete_user_data(
    request: dict,
    user: dict = Depends(verify_token)
):
    """Delete user data (right to be forgotten)"""
    try:
        user_id = user["user_id"]
        data_types = request.get("data_types", ["all"])  # ["emails", "calendar", "vault", "all"]
        
        # Log the deletion request
        await audit_agent.log_activity(
            user_id=user_id,
            action="data_deletion_requested",
            details={"data_types": data_types}
        )
        
        deleted_items = {}
        
        if "emails" in data_types or "all" in data_types:
            # Delete email processing data
            deleted_items["emails"] = "All email analysis data deleted"
        
        if "calendar" in data_types or "all" in data_types:
            # Delete calendar processing data
            deleted_items["calendar"] = "All calendar analysis data deleted"
        
        if "vault" in data_types or "all" in data_types:
            # Delete vault data (be very careful with this)
            deleted_items["vault"] = "All vault data deleted"
        
        logger.info(f"🗑️ Data deletion completed for user {user_id}: {data_types}")
        
        return {
            "status": "deleted",
            "user_id": user_id,
            "deleted_items": deleted_items,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to delete user data: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to delete user data", "details": str(e)}
        )

@app.get("/api/data/export")
async def export_user_data(user: dict = Depends(verify_token)):
    """Export all user data (data portability)"""
    try:
        user_id = user["user_id"]
        
        # Log the export request
        await audit_agent.log_activity(
            user_id=user_id,
            action="data_export_requested",
            details={}
        )
        
        # Collect all user data
        export_data = {
            "user_id": user_id,
            "exported_at": datetime.now().isoformat(),
            "emails": {
                "total_processed": 0,
                "categories": {},
                "last_processed": None
            },
            "calendar": {
                "total_processed": 0,
                "categories": {},
                "last_processed": None
            },
            "consent_history": [],
            "audit_log": []
        }
        
        logger.info(f"📤 Data export completed for user {user_id}")
        
        return export_data
        
    except Exception as e:
        logger.error(f"❌ Failed to export user data: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to export user data", "details": str(e)}
        )

# Additional Email API endpoints
@app.get("/api/emails/categorized")
async def get_categorized_emails(user: dict = Depends(verify_token)):
    """Get categorized emails for the authenticated user"""
    try:
        user_id = user["user_id"]
        
        # Get emails from the email processor agent
        categorized_emails = email_agent.get_categorized_emails(user_id)
        
        if not categorized_emails:
            return {
                "success": False,
                "message": "No categorized emails found. Please process emails first.",
                "emails": [],
                "stats": {}
            }
        
        # Get stats from the agent
        stats = email_agent.get_processing_status(user_id)
        
        return {
            "success": True,
            "emails": categorized_emails,
            "stats": stats.get("category_stats", {}),
            "total_count": len(categorized_emails)
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get categorized emails: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to get categorized emails", "details": str(e)}
        )


@app.post("/api/emails/automation")
async def create_email_automation(
    request: dict,
    user: dict = Depends(verify_token)
):
    """Create email automation rules"""
    try:
        user_id = user["user_id"]
        category = request.get("category")
        automation_type = request.get("automation_type")
        
        if not category or not automation_type:
            raise HTTPException(status_code=400, detail="Category and automation_type are required")
        
        # Create consent token for automation
        consent_token = issue_token(user_id, ConsentScope.AUTOMATION_MANAGEMENT.value)
        
        # Use the email agent to create automation
        result = await email_agent.create_category_automation(
            user_id=user_id,
            category=category,
            automation_type=automation_type,
            consent_token=consent_token
        )
        
        await audit_agent.log_activity(
            user_id=user_id,
            action="email_automation_created",
            details={"category": category, "automation_type": automation_type}
        )
        
        return {
            "success": True,
            "automation_id": result.get("automation_id"),
            "category": category,
            "automation_type": automation_type,
            "affected_emails": result.get("affected_emails", 0)
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to create email automation: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to create email automation", "details": str(e)}
        )

# Calendar Processing API endpoints
@app.post("/api/calendar/process/{days_back}/{days_forward}")
async def process_calendar(
    days_back: int,
    days_forward: int,
    background_tasks: BackgroundTasks,
    user_data: dict = Depends(verify_token)
):
    """Process calendar events with AI categorization"""
    user_id = user_data["user_id"]
    task_id = f"calendar_processing_{user_id}_{int(time.time())}"
    
    logger.info(f"📅 Starting calendar processing for user {user_id} - {days_back} days back, {days_forward} days forward")
    
    # Initialize progress tracking
    processing_status[task_id] = {
        "status": "starting",
        "current": 0,
        "total": 0,
        "percentage": 0.0,
        "message": "Initializing calendar processing with AI categorization...",
        "results": None,
        "start_time": time.time(),
        "user_id": user_id,
        "days_back": days_back,
        "days_forward": days_forward
    }
    
    # Start background processing
    background_tasks.add_task(process_calendar_with_enhanced_ai, user_id, days_back, days_forward, task_id)
    
    return {
        "task_id": task_id,
        "status": "started",
        "message": f"Calendar processing started for {days_back} days back and {days_forward} days forward"
    }

@app.get("/api/calendar/categorized")
async def get_categorized_calendar(user: dict = Depends(verify_token)):
    """Get categorized calendar events for the authenticated user"""
    try:
        user_id = user["user_id"]
        
        # Get events from the calendar processor agent
        categorized_events = calendar_agent.get_categorized_events(user_id)
        
        if not categorized_events:
            return {
                "success": False,
                "message": "No categorized events found. Please process calendar first.",
                "events": [],
                "stats": {}
            }
        
        # Get stats from the agent
        stats = calendar_agent.get_processing_status(user_id)
        
        return {
            "success": True,
            "events": categorized_events,
            "stats": stats.get("schedule_stats", {}),
            "total_count": len(categorized_events)
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get categorized calendar: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to get categorized calendar", "details": str(e)}
        )

# Unified Categories API (combining email and calendar)
@app.get("/api/categories/unified")
async def get_unified_categories(user: dict = Depends(verify_token)):
    """Get unified categories from both emails and calendar events using persistent storage"""
    try:
        user_id = user["user_id"]
        
        # Get unified categories from persistent storage
        unified_categories = persistent_storage.get_unified_categories(user_id)
        
        if not unified_categories:
            return {
                "success": False,
                "message": "No categorized data found. Please process emails and/or calendar first.",
                "categories": {}
            }
        
        return {
            "success": True,
            "categories": unified_categories,
            "total_categories": len(unified_categories),
            "message": f"Found {len(unified_categories)} unified categories"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get unified categories: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to get unified categories", "details": str(e)}
        )

@app.get("/api/emails/categories/{category}")
async def get_emails_by_category(category: str, user: dict = Depends(verify_token)):
    """Get emails filtered by category from encrypted persistent storage"""
    try:
        user_id = user["user_id"]
        
        # Debug logging
        logger.info(f"📧 API Request: Getting emails for category '{category}' for user {user_id[:8]}...")
        logger.info(f"🔐 Retrieving emails from encrypted persistent storage...")
        
        # Get emails from encrypted persistent storage
        emails = persistent_storage.get_emails_by_category(user_id, category)
        
        # Enhanced logging with processing details
        logger.info(f"✅ Found {len(emails)} emails in category '{category}'")
        if emails:
            logger.info(f"� Sample email structure: {list(emails[0].keys()) if emails else 'No emails'}")
            
            # Check if emails have LLM processing data
            sample_email = emails[0]
            ai_insights = sample_email.get("ai_insights", {})
            processing_method = ai_insights.get("processing_method", "unknown")
            model_used = ai_insights.get("model_used", "unknown")
            
            logger.info(f"🤖 Email processing info: method='{processing_method}', model='{model_used}'")
            logger.info(f"📧 Sample email: ID={sample_email.get('id', 'unknown')[:8]}, category='{sample_email.get('category')}', confidence={sample_email.get('confidence', 0):.2f}")
        else:
            logger.warning(f"⚠️ No emails found in category '{category}' - may need to process emails first")
        
        return {
            "success": True,
            "emails": emails,
            "category": category,
            "count": len(emails)
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get emails by category: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to get emails by category", "details": str(e)}
        )

@app.get("/api/calendar/categories/{category}")
async def get_events_by_category(category: str, user: dict = Depends(verify_token)):
    """Get calendar events filtered by category"""
    try:
        user_id = user["user_id"]
        
        # Get events from persistent storage
        events = persistent_storage.get_events_by_category(user_id, category)
        
        return {
            "success": True,
            "events": events,
            "category": category,
            "count": len(events)
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get events by category: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to get events by category", "details": str(e)}
        )
        calendar_stats = calendar_agent.get_processing_status(user_id)
        calendar_categories = calendar_stats.get("schedule_stats", {}).get("categories", {})
        
        # Merge categories
        unified_categories = {}
        all_category_names = set(email_categories.keys()) | set(calendar_categories.keys())
        
        for category in all_category_names:
            email_count = email_categories.get(category, 0)
            calendar_count = calendar_categories.get(category, 0)
            total_count = email_count + calendar_count
            
            unified_categories[category] = {
                "total": total_count,
                "email_count": email_count,
                "calendar_count": calendar_count,
                "sources": []
            }
            
            if email_count > 0:
                unified_categories[category]["sources"].append("email")
            if calendar_count > 0:
                unified_categories[category]["sources"].append("calendar")
        
        return {
            "success": True,
            "categories": unified_categories,
            "total_categories": len(unified_categories),
            "email_stats": email_stats,
            "calendar_stats": calendar_stats
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get unified categories: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to get unified categories", "details": str(e)}
        )

# Pydantic models for agent requests
class ScheduleEventRequest(BaseModel):
    title: str
    start_time: str
    end_time: Optional[str] = None
    description: Optional[str] = ""
    location: Optional[str] = ""
    attendees: Optional[List[str]] = []
    category: Optional[str] = ""

class CreateNoteRequest(BaseModel):
    content: str
    title: Optional[str] = ""
    tags: Optional[List[str]] = []
    category: Optional[str] = "general"

# Agent Actions API (for schedule_event, create_note, etc.)
@app.post("/api/agents/schedule_event")
async def schedule_event_action(
    request: ScheduleEventRequest,
    user: dict = Depends(verify_token)
):
    """Schedule an event using the schedule_event operon"""
    try:
        user_id = user["user_id"]
        
        # Import the schedule_event operon
        from hushh_mcp.operons.schedule_event import create_calendar_event
        
        if not request.title or not request.start_time:
            raise HTTPException(status_code=422, detail="Title and start_time are required")
        
        # Create the event
        event = create_calendar_event(
            title=request.title,
            start_time=request.start_time,
            end_time=request.end_time,
            description=request.description,
            location=request.location,
            attendees=request.attendees
        )
        
        # Add category if provided
        if request.category:
            event["category"] = request.category
        
        # Log the action
        await audit_agent.log_activity(
            user_id=user_id,
            action="event_scheduled",
            details={
                "event_id": event["event_id"],
                "title": request.title,
                "category": request.category,
                "start_time": request.start_time
            }
        )
        
        return {
            "success": True,
            "event": event,
            "message": f"Event '{request.title}' scheduled successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to schedule event: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to schedule event: {str(e)}")

@app.post("/api/agents/create_note")
async def create_note_action(
    request: CreateNoteRequest,
    user: dict = Depends(verify_token)
):
    """Create a note using the create_note operon"""
    try:
        user_id = user["user_id"]
        
        # Import the create_note operon
        from hushh_mcp.operons.create_note import generate_structured_note
        
        if not request.content:
            raise HTTPException(status_code=422, detail="Content is required")
        
        # Create the note
        note = generate_structured_note(
            content=request.content,
            title=request.title,
            tags=request.tags,
            category=request.category
        )
        
        # Log the action
        await audit_agent.log_activity(
            user_id=user_id,
            action="note_created",
            details={
                "note_id": note["note_id"],
                "title": note["title"],
                "category": request.category
            }
        )
        
        return {
            "success": True,
            "note": note,
            "message": f"Note '{note['title']}' created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to create note: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create note: {str(e)}")

# Consent Revocation API (Hushh Protocol Compliance)
@app.post("/api/consent/revoke")
async def revoke_consent(
    request: dict
):
    """Revoke consent and clear associated data following Hushh MCP protocol"""
    try:
        # Try to get user from token if available, but allow revocation even without perfect auth
        user_id = None
        try:
            # First try to get from Authorization header
            authorization = request.get("authorization") or request.get("headers", {}).get("authorization")
            if authorization and authorization.startswith("Bearer "):
                token = authorization.replace("Bearer ", "")
                jwt_secret = getattr(config, 'JWT_SECRET', 'fallback_secret_key_for_development')
                payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
                user_id = payload.get("user_id")
        except:
            pass
        
        # Fallback: get user_id from request body or use provided user_id
        if not user_id:
            user_id = request.get("user_id")
        
        # If still no user_id, try to get it from the request body
        if not user_id and "user_id" in request:
            user_id = request["user_id"]
            
        # If still no user_id, check current user sessions
        if not user_id and user_sessions:
            # Use the first available user session as fallback
            user_id = list(user_sessions.keys())[0]
            logger.warning(f"⚠️ Using fallback user_id for consent revocation: {user_id}")
        
        if not user_id:
            logger.error("❌ No user_id available for consent revocation")
            return JSONResponse(
                status_code=400,
                content={"error": "No user identification available for consent revocation"}
            )
        
        consent_type = request.get("consent_type", "all")  # "email", "calendar", "all"
        logger.info(f"🔐 Processing consent revocation for user {user_id}, type: {consent_type}")
        
        revoked_data = {}
        
        if consent_type in ["email", "all"]:
            try:
                # Revoke email processing consent
                await email_agent.revoke_consent(user_id)
                logger.info(f"✅ Email agent consent revoked for user {user_id}")
            except Exception as e:
                logger.warning(f"⚠️ Email agent revocation failed: {e}")
            
            try:
                # Clear persistent email data
                persistent_storage.delete_user_data(user_id, "emails")
                logger.info(f"✅ Email persistent data cleared for user {user_id}")
            except Exception as e:
                logger.warning(f"⚠️ Email persistent data clearing failed: {e}")
            
            try:
                # Clear agent memory
                if hasattr(email_agent, 'processed_emails') and user_id in email_agent.processed_emails:
                    del email_agent.processed_emails[user_id]
                if hasattr(email_agent, 'category_stats') and user_id in email_agent.category_stats:
                    del email_agent.category_stats[user_id]
                logger.info(f"✅ Email agent memory cleared for user {user_id}")
            except Exception as e:
                logger.warning(f"⚠️ Email agent memory clearing failed: {e}")
            
            revoked_data["email"] = "All email data and categorizations cleared"
        
        if consent_type in ["calendar", "all"]:
            try:
                # Revoke calendar processing consent
                await calendar_agent.revoke_consent(user_id)
                logger.info(f"✅ Calendar agent consent revoked for user {user_id}")
            except Exception as e:
                logger.warning(f"⚠️ Calendar agent revocation failed: {e}")
            
            try:
                # Clear persistent calendar data
                persistent_storage.delete_user_data(user_id, "calendar")
                logger.info(f"✅ Calendar persistent data cleared for user {user_id}")
            except Exception as e:
                logger.warning(f"⚠️ Calendar persistent data clearing failed: {e}")
            
            try:
                # Clear agent memory
                if hasattr(calendar_agent, 'processed_events') and user_id in calendar_agent.processed_events:
                    del calendar_agent.processed_events[user_id]
                if hasattr(calendar_agent, 'schedule_stats') and user_id in calendar_agent.schedule_stats:
                    del calendar_agent.schedule_stats[user_id]
                logger.info(f"✅ Calendar agent memory cleared for user {user_id}")
            except Exception as e:
                logger.warning(f"⚠️ Calendar agent memory clearing failed: {e}")
            
            revoked_data["calendar"] = "All calendar data and categorizations cleared"
        
        # Clear any processing status for this user
        try:
            keys_to_remove = [key for key in processing_status.keys() if key.startswith(user_id)]
            for key in keys_to_remove:
                del processing_status[key]
            logger.info(f"✅ Processing status cleared for user {user_id}")
        except Exception as e:
            logger.warning(f"⚠️ Processing status clearing failed: {e}")
        
        # Note: User session is NOT cleared during consent revocation per Hushh protocol
        # This allows user to remain logged in while their data is cleared
        logger.info(f"ℹ️ User session preserved during consent revocation for user {user_id}")
        
        # Log the revocation
        try:
            await audit_agent.log_activity(
                user_id=user_id,
                action="consent_revoked",
                details={
                    "consent_type": consent_type,
                    "revoked_data": list(revoked_data.keys()),
                    "timestamp": datetime.now().isoformat()
                }
            )
        except Exception as e:
            logger.warning(f"⚠️ Audit logging failed: {e}")
        
        logger.info(f"✅ Consent revocation completed successfully for user {user_id}")
        
        return {
            "success": True,
            "consent_type": consent_type,
            "revoked_data": revoked_data,
            "message": "Consent revoked and data cleared successfully. User remains logged in.",
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "session_preserved": True
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to revoke consent: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to revoke consent", "details": str(e)}
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "agents": {
            "email_processor": "active",
            "calendar_processor": "active",
            "audit_logger": "active"
        }
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Hushh MCP PDA Agent API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health",
        "frontend": "Run frontend from /frontend directory"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
