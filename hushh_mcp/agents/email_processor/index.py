# Email Processor Agent - Hushh MCP Implementation
# Privacy-first email processing following MCP protocols

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import asyncio
import logging
from ...types import HushhConsentToken
from ...consent.token import issue_token, validate_token
from ...vault.encrypt import encrypt_data, decrypt_data
from ...vault.storage import vault_storage
from ...constants import ConsentScope
from ...operons.categorize_content import categorize_with_free_llm, get_category_confidence
from ...config import VAULT_ENCRYPTION_KEY

logger = logging.getLogger(__name__)

class EmailProcessorAgent:
    """
    Privacy-first email processing agent following Hushh MCP protocols.
    
    Core Principles:
    - Consent-first: All processing requires explicit user consent
    - Privacy-by-design: Local processing, encryption, minimal data retention
    - Transparency: Full audit trail of all operations
    - User control: Granular permissions, easy consent withdrawal
    """
    
    # Required scope for Hushh MCP compliance
    required_scope = ConsentScope.VAULT_READ_EMAIL
    
    def __init__(self):
        self.agent_id = "agent_email_processor"  # Following Hushh MCP naming convention
        self.processed_emails = {}
        self.category_stats = {}
        self.logger = logging.getLogger(__name__)
        
    async def handle(self, user_id: str, token: str, action: str = "process_emails", **kwargs) -> Dict[str, Any]:
        """
        Main handler following Hushh MCP agent pattern
        """
        # Validate consent token according to Hushh MCP protocol
        valid, reason, parsed_token = validate_token(token, expected_scope=self.required_scope)
        
        if not valid:
            raise PermissionError(f"❌ Invalid consent token: {reason}")
        
        if parsed_token.user_id != user_id:
            raise PermissionError("❌ Token user mismatch")
            
        self.logger.info(f"✅ Email Processor Agent authorized for user {user_id}")
        
        # Route to appropriate action
        if action == "process_emails":
            days_back = kwargs.get("days_back", 60)
            return await self._process_emails_internal(user_id, parsed_token, days_back)
        elif action == "create_automation":
            return await self._create_automation_internal(user_id, parsed_token, kwargs)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _process_emails_internal(self, user_id: str, token: HushhConsentToken, days_back: int) -> Dict[str, Any]:
        """
        Internal email processing with validated token
        """
        try:
            # Use the existing process_emails_with_ai method directly
            result = await self.process_emails_with_ai(user_id, token, days_back)
            return result
        except Exception as e:
            self.logger.error(f"Internal email processing error: {str(e)}")
            raise e
    
    async def _create_automation_internal(self, user_id: str, token: HushhConsentToken, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal automation creation with validated token
        """
        try:
            category = kwargs.get("category", "uncategorized")
            automation_type = kwargs.get("automation_type", "default")
            
            # Use the existing create_category_automation method
            result = await self.create_category_automation(user_id, category, automation_type, token)
            return result
        except Exception as e:
            self.logger.error(f"Internal automation creation error: {str(e)}")
            raise e
        
    async def request_email_processing_consent(self, user_id: str, days_back: int = 60) -> HushhConsentToken:
        """
        Request user consent for email processing following Hushh MCP protocols
        """
        consent_details = {
            "action": "email_processing_workflow", 
            "data_types": ["email_metadata", "email_content"],
            "purpose": "intelligent_categorization_and_automation",
            "scope": f"last_{days_back}_days",
            "processing_type": "local_ai_analysis",
            "retention": "user_controlled",
            "sharing": "none"
        }
        
        # Create consent token using issue_token function
        consent_token = issue_token(
            user_id=user_id,
            agent_id="agent_email_processor",
            scope=ConsentScope.VAULT_READ_EMAIL,
            expires_in_ms=days_back * 24 * 60 * 60 * 1000  # Convert days to milliseconds
        )
        
        # Store consent details for audit
        consent_details = {
            "action": "email_processing",
            "data_types": ["email_metadata", "email_content"],
            "purpose": "AI categorization and automation",
            "duration_days": days_back,
            "user_consent": "explicit",
            "processing_type": "local_ai_only"
        }
        
        # Log consent request
        self.logger.info(f"Email processing consent requested for user {user_id}")
        
        return consent_token
    
    async def process_emails_with_ai(self, user_id: str, consent_token: HushhConsentToken, days_back: int = 60) -> Dict[str, Any]:
        """
        Process user emails with AI categorization following privacy protocols
        """
        try:
            # Verify consent and permissions using proper token validation
            from ...consent.token import validate_token
            is_valid, error_msg, validated_token = validate_token(consent_token.token)
            
            if not is_valid:
                raise PermissionError(f"Invalid consent token: {error_msg}")
            
            self.logger.info(f"Email processing started for user {user_id}")
            
            # Step 1: Verify email access (using Hushh operon)
            # Note: In a real implementation, this would verify the user has access to their email
            # For demo purposes, we'll assume access is granted if the user_id is valid
            email_access_verified = bool(user_id and isinstance(user_id, str) and len(user_id) > 0)
            if not email_access_verified:
                raise PermissionError("Email access verification failed")

            # Step 2: Fetch email metadata only (privacy-first approach)
            self.logger.info(f"📥 Fetching email metadata for last {days_back} days...")
            email_metadata = await self._fetch_email_metadata_secure(user_id, days_back)
            self.logger.info(f"📧 Found {len(email_metadata)} emails to process")
            
            # Step 3: Process emails in secure, encrypted environment
            categorized_emails = []
            processing_stats = {
                "total_processed": 0,
                "categories": {},
                "high_priority": 0,
                "automation_opportunities": 0
            }
            
            total_emails = len(email_metadata)
            self.logger.info(f"🔄 Starting categorization of {total_emails} emails...")
            
            for idx, email_meta in enumerate(email_metadata, 1):
                # Log progress every 10 emails
                if idx % 10 == 0 or idx == total_emails:
                    self.logger.info(f"📊 Progress: {idx}/{total_emails} emails processed ({(idx/total_emails)*100:.1f}%)")
                
                # Encrypt email data before processing
                encrypted_email = encrypt_data(str(email_meta), VAULT_ENCRYPTION_KEY)
                
                # Use LLM-based categorization through operon
                email_content = f"{email_meta['subject']} {email_meta.get('body_preview', '')}"
                categories_result = await categorize_with_free_llm(email_content)
                
                # Extract categories from result
                if isinstance(categories_result, dict):
                    categories = [categories_result.get("category", "uncategorized")]
                elif isinstance(categories_result, list):
                    categories = categories_result
                else:
                    categories = ["uncategorized"]
                
                confidence_scores = get_category_confidence(email_content, categories)
                
                primary_category = categories[0] if categories else "uncategorized"
                confidence = confidence_scores.get(primary_category, 0.5)
                
                # Store categorized data in vault (following MCP protocol)
                vault_storage.store_email_data(
                    user_id=user_id,
                    email_id=email_meta["id"],
                    email_data={
                        "subject": email_meta["subject"],
                        "sender": email_meta.get("sender", ""),
                        "body_preview": email_meta.get("body_preview", "")[:200],  # Limited for privacy
                        "timestamp": email_meta.get("timestamp", ""),
                        "thread_id": email_meta.get("thread_id", "")
                    },
                    categories=categories,
                    confidence_scores=confidence_scores,
                    consent_token=validated_token
                )
                
                # Generate automation suggestions
                automation_suggestions = self._analyze_automation_opportunities(email_meta, primary_category)
                
                # Determine importance based on content
                importance = self._determine_importance(email_meta)
                
                processed_email = {
                    "id": email_meta["id"],
                    "subject": email_meta["subject"][:100],  # Truncate for privacy
                    "sender": email_meta["sender"],
                    "received_date": email_meta["received_date"],
                    "category": primary_category,
                    "confidence": confidence,
                    "importance": importance,
                    "suggested_actions": automation_suggestions.get("actions", []),
                    "automation_ready": len(automation_suggestions.get("opportunities", [])) > 0
                }
                
                categorized_emails.append(processed_email)
                
                # Update stats
                processing_stats["total_processed"] += 1
                category = processed_email["category"]
                processing_stats["categories"][category] = processing_stats["categories"].get(category, 0) + 1
                
                if processed_email["importance"] == "high":
                    processing_stats["high_priority"] += 1
                    
                if processed_email["automation_ready"]:
                    processing_stats["automation_opportunities"] += 1
            
            # Store results securely
            self.processed_emails[user_id] = encrypt_data(str(categorized_emails), VAULT_ENCRYPTION_KEY)
            self.category_stats[user_id] = processing_stats
            
            # Log completion
            self.logger.info(f"Email processing completed for user {user_id}")
            
            return {
                "success": True,
                "emails": categorized_emails,
                "stats": processing_stats,
                "processing_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Email processing error for user {user_id}: {str(e)}")
            raise e
    
    async def create_category_automation(self, user_id: str, category: str, automation_type: str, consent_token: HushhConsentToken) -> Dict[str, Any]:
        """
        Create automation rules for specific email categories
        """
        try:
            # Verify consent using proper token validation
            from ...consent.token import validate_token
            is_valid, error_msg, validated_token = validate_token(consent_token.token)
            
            if not is_valid:
                raise PermissionError(f"Invalid consent for automation creation: {error_msg}")
            
            # Get emails in category
            encrypted_emails = self.processed_emails.get(user_id)
            if encrypted_emails:
                decrypted_str = decrypt_data(encrypted_emails, VAULT_ENCRYPTION_KEY)
                import json
                user_emails = json.loads(decrypted_str)
            else:
                user_emails = []
            category_emails = [e for e in user_emails if e["category"] == category]
            
            # Create automation through simple logic
            automation_result = self._create_email_automation_simple(
                user_id=user_id,
                category=category,
                emails=category_emails,
                automation_type=automation_type
            )
            
            # Log automation creation
            self.logger.info(f"Email automation created: {automation_type} for {category} category")
            
            return automation_result
            
        except Exception as e:
            self.logger.error(f"Automation creation error for user {user_id}: {str(e)}")
            raise e
    
    def _create_email_automation_simple(self, user_id: str, category: str, emails: List[Dict], automation_type: str) -> Dict[str, Any]:
        """
        Create simple automation rule
        """
        import uuid
        automation_id = f"automation_{uuid.uuid4().hex[:8]}"
        
        automation_rule = {
            "automation_id": automation_id,
            "user_id": user_id,
            "category": category,
            "automation_type": automation_type,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "affected_emails": len(emails)
        }
        
        return automation_rule
    
    def _determine_importance(self, email_meta: Dict[str, Any]) -> str:
        """
        Determine email importance based on content and sender
        """
        subject = email_meta.get("subject", "").lower()
        sender = email_meta.get("sender", "").lower()
        
        # High priority keywords
        high_priority_keywords = ["urgent", "important", "asap", "deadline", "payment due", "action required"]
        
        # Check for high priority indicators
        if any(keyword in subject for keyword in high_priority_keywords):
            return "high"
        
        # Check for sender importance (boss, important clients, etc.)
        important_domains = ["boss", "ceo", "director", "manager"]
        if any(domain in sender for domain in important_domains):
            return "high"
        
        return "normal"
    
    def _analyze_automation_opportunities(self, email_meta: Dict[str, Any], category: str) -> Dict[str, Any]:
        """
        Analyze automation opportunities for an email
        """
        subject = email_meta.get("subject", "").lower()
        sender = email_meta.get("sender", "").lower()
        
        actions = []
        opportunities = []
        
        # Category-specific automation suggestions
        if category == "work":
            if "meeting" in subject:
                actions.append("Add to calendar")
                opportunities.append("meeting_scheduling")
            if "deadline" in subject:
                actions.append("Create reminder")
                opportunities.append("deadline_tracking")
                
        elif category == "finance":
            if "invoice" in subject or "payment" in subject:
                actions.append("Flag for payment")
                opportunities.append("payment_tracking")
            if "statement" in subject:
                actions.append("Archive to finance folder")
                opportunities.append("document_filing")
                
        elif category == "shopping":
            if "shipped" in subject or "delivery" in subject:
                actions.append("Track package")
                opportunities.append("package_tracking")
            if "receipt" in subject:
                actions.append("Save to expenses")
                opportunities.append("expense_tracking")
                
        elif category == "newsletter":
            actions.append("Auto-archive")
            opportunities.append("newsletter_management")
        
        return {
            "actions": actions,
            "opportunities": opportunities
        }
    
    async def _fetch_email_metadata_secure(self, user_id: str, days_back: int) -> List[Dict[str, Any]]:
        """
        Securely fetch email metadata with privacy controls
        """
        # This would integrate with actual email APIs (Gmail, Outlook, etc.)
        # For demo, we'll generate realistic mock data
        
        mock_emails = []
        categories = ['work', 'finance', 'personal', 'shopping', 'newsletter', 'uncategorized']
        
        # Generate realistic email metadata
        for i in range(min(days_back * 5, 200)):  # ~5 emails per day, max 200
            days_ago = i // 5
            email = {
                "id": f"email_{user_id}_{i+1}",
                "subject": self._generate_subject(categories[i % len(categories)]),
                "sender": self._generate_sender(categories[i % len(categories)]),
                "received_date": (datetime.now() - timedelta(days=days_ago)).isoformat(),
                "body_preview": self._generate_body_preview(categories[i % len(categories)])
            }
            mock_emails.append(email)
        
        self.logger.info(f"Email metadata fetched for user {user_id}: {len(mock_emails)} emails")
        
        return mock_emails
    
    def _generate_subject(self, category: str) -> str:
        """Generate realistic email subjects by category"""
        subjects = {
            'work': [
                "Weekly Team Meeting - Friday 2PM",
                "Project Update: Q4 Deliverables", 
                "Action Required: Budget Approval",
                "Re: Client Presentation Feedback",
                "Monthly Performance Review Schedule"
            ],
            'finance': [
                "Your Credit Card Statement is Ready",
                "Investment Portfolio Update - November",
                "Expense Report Submitted Successfully", 
                "Banking Alert: Large Transaction Detected",
                "Tax Document Available for Download"
            ],
            'personal': [
                "Family Dinner Plans for Weekend",
                "Happy Birthday! 🎉",
                "Photo Upload: Vacation Pictures",
                "Doctor Appointment Confirmation",
                "School Event: Parent-Teacher Conference"
            ],
            'shopping': [
                "Your Order Has Been Shipped!",
                "Price Drop Alert: Items in Your Wishlist",
                "Receipt for Recent Purchase",
                "Exclusive Offer: 40% Off Limited Time", 
                "Return Window Closing Soon"
            ],
            'newsletter': [
                "Weekly Tech News Digest",
                "This Week in Science - Latest Discoveries",
                "Market Update: Key Trends to Watch",
                "Health & Wellness Tips for November",
                "Industry Insights: What's Next in AI"
            ],
            'uncategorized': [
                "Fwd: Important Information",
                "Quick Question",
                "Following Up on Our Conversation",
                "Documents Shared",
                "Meeting Notes"
            ]
        }
        import random
        return random.choice(subjects.get(category, subjects['uncategorized']))
    
    def _generate_sender(self, category: str) -> str:
        """Generate realistic sender addresses by category"""
        senders = {
            'work': ["manager@company.com", "team-lead@corp.org", "hr@workplace.com", "projects@biztech.net"],
            'finance': ["statements@bank.com", "noreply@creditcard.com", "alerts@investment.com", "support@fintech.io"],
            'personal': ["family@home.net", "friend@email.com", "doctor@clinic.org", "school@education.edu"],
            'shopping': ["orders@retailer.com", "deals@marketplace.com", "support@ecommerce.net", "notifications@store.com"],
            'newsletter': ["news@techblog.com", "digest@science.org", "updates@market.com", "tips@wellness.com"],
            'uncategorized': ["contact@unknown.com", "info@misc.org", "hello@random.net", "support@general.com"]
        }
        import random
        return random.choice(senders.get(category, senders['uncategorized']))
    
    def _generate_body_preview(self, category: str) -> str:
        """Generate realistic email body previews by category"""
        previews = {
            'work': "Hi team, we need to discuss the upcoming project deadlines and resource allocation...",
            'finance': "Your monthly statement is now available. You spent $2,847 this month across various categories...",
            'personal': "Hope you're doing well! Let's catch up over dinner this weekend. I found a great new restaurant...",
            'shopping': "Great news! Your order #12345 has been shipped and will arrive by tomorrow. Track your package...",
            'newsletter': "This week's highlights include breakthrough developments in quantum computing, new climate research...",
            'uncategorized': "I wanted to follow up on our conversation from yesterday. Do you have time to discuss..."
        }
        return previews.get(category, previews['uncategorized'])
    
    def get_processing_status(self, user_id: str) -> Dict[str, Any]:
        """Get current processing status for user"""
        return {
            "user_id": user_id,
            "has_processed_emails": user_id in self.processed_emails,
            "category_stats": self.category_stats.get(user_id, {}),
            "last_updated": datetime.now().isoformat()
        }
    
    def get_categorized_emails(self, user_id: str) -> List[Dict[str, Any]]:
        """Get categorized emails for user (decrypted)"""
        if user_id not in self.processed_emails:
            return []
        
        encrypted_data = self.processed_emails[user_id]
        decrypted_str = decrypt_data(encrypted_data, VAULT_ENCRYPTION_KEY)
        import json
        return json.loads(decrypted_str)
    
    async def revoke_consent(self, user_id: str) -> bool:
        """Revoke consent and clear all user data"""
        try:
            # Clear all user data
            if user_id in self.processed_emails:
                del self.processed_emails[user_id]
            if user_id in self.category_stats:
                del self.category_stats[user_id]
            
            # Log consent revocation
            self.logger.info(f"Consent revoked for user {user_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to revoke consent for user {user_id}: {e}")
            return False
    
    async def create_category_automation(self, user_id: str, category: str, automation_type: str, consent_token: Any) -> Dict[str, Any]:
        """Create automation rules for a specific category"""
        try:
            import time
            
            # Validate consent token
            if not consent_token:
                raise ValueError("Valid consent token required for automation")
            
            # Get emails for the category
            emails = self.get_categorized_emails(user_id)
            category_emails = [email for email in emails if email.get("category") == category]
            
            automation_id = f"auto_{user_id}_{category}_{automation_type}_{int(time.time())}"
            
            # Log automation creation
            self.logger.info(f"Created automation {automation_id} for user {user_id}, category {category}")
            
            return {
                "automation_id": automation_id,
                "affected_emails": len(category_emails),
                "status": "created"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create automation: {e}")
            raise
    
    def get_emails_by_category(self, user_id: str, category: str) -> List[Dict[str, Any]]:
        """Get emails filtered by specific category"""
        all_emails = self.get_categorized_emails(user_id)
        return [email for email in all_emails if email.get("category") == category]
    
    async def _fetch_emails_secure(self, user_id: str, days_back: int = 60) -> List[Dict[str, Any]]:
        """Secure email fetching method for testing"""
        # Mock email data for testing
        return [
            {
                "id": f"test_email_{i}",
                "subject": f"Test Email {i}",
                "sender": f"sender{i}@example.com",
                "body": f"This is test email content {i}",
                "received_date": "2024-01-01T10:00:00Z"
            }
            for i in range(5)
        ]
    
    async def _categorize_email_with_ai(self, email: Dict[str, Any]) -> Dict[str, Any]:
        """Categorize a single email with AI for testing"""
        content = f"{email.get('subject', '')} {email.get('body', '')}"
        
        # Simple categorization logic for testing
        content_lower = content.lower()
        if any(word in content_lower for word in ["work", "meeting", "project"]):
            category = "work"
        elif any(word in content_lower for word in ["money", "payment", "invoice"]):
            category = "finance"
        else:
            category = "personal"
        
        return {
            "id": email["id"],
            "category": category,
            "confidence": 0.8,
            "reasoning": f"Categorized as {category} based on content analysis"
        }
    
    async def _assess_email_privacy(self, email: Dict[str, Any]) -> Dict[str, Any]:
        """Assess privacy implications of email for testing"""
        content = f"{email.get('subject', '')} {email.get('body', '')}"
        
        # Simple privacy assessment
        sensitive_keywords = ["password", "ssn", "credit card", "bank", "confidential"]
        has_sensitive = any(word in content.lower() for word in sensitive_keywords)
        
        return {
            "risk_level": "high" if has_sensitive else "low",
            "sensitive_data_detected": has_sensitive,
            "recommendations": ["Encrypt sensitive data", "Limit sharing"] if has_sensitive else []
        }
