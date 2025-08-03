# Persistent Storage for User Data - Hushh MCP Implementation
# Ensures data persistence across sessions with privacy controls

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from .encrypt import encrypt_data, decrypt_data
from ..config import VAULT_ENCRYPTION_KEY

logger = logging.getLogger(__name__)

class PersistentUserStorage:
    """
    Persistent storage system for user categorizations and data.
    Follows Hushh MCP protocols for privacy and consent management.
    """
    
    def __init__(self, storage_dir: str = "vault_data"):
        self.storage_dir = storage_dir
        self.ensure_storage_directory()
        
    def ensure_storage_directory(self):
        """Ensure storage directory exists"""
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
            logger.info(f"📁 Created persistent storage directory: {self.storage_dir}")
    
    def get_user_file_path(self, user_id: str, data_type: str) -> str:
        """Get the file path for user's specific data type"""
        safe_user_id = "".join(c for c in user_id if c.isalnum() or c in ['_', '-'])
        return os.path.join(self.storage_dir, f"{safe_user_id}_{data_type}.encrypted")
    
    def save_user_categories(self, user_id: str, categories: Dict[str, Any], data_type: str = "categories") -> bool:
        """Save user categories with encryption following Hushh MCP protocols"""
        try:
            file_path = self.get_user_file_path(user_id, data_type)
            
            # Add metadata
            data_to_save = {
                "user_id": user_id,
                "data_type": data_type,
                "categories": categories,
                "last_updated": datetime.now().isoformat(),
                "version": "1.0"
            }
            
            # Encrypt and save - fix for EncryptedPayload serialization
            encrypted_payload = encrypt_data(json.dumps(data_to_save), VAULT_ENCRYPTION_KEY)
            
            # Convert EncryptedPayload to dict for JSON serialization
            encrypted_dict = {
                "ciphertext": encrypted_payload.ciphertext,
                "iv": encrypted_payload.iv,
                "tag": encrypted_payload.tag,
                "encoding": encrypted_payload.encoding,
                "algorithm": encrypted_payload.algorithm
            }
            
            with open(file_path, 'w') as f:
                json.dump(encrypted_dict, f)
            
            logger.info(f"💾 Saved {data_type} for user {user_id[:8]}... ({len(categories)} categories)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save {data_type} for user {user_id}: {e}")
            return False
    
    def load_user_categories(self, user_id: str, data_type: str = "categories") -> Dict[str, Any]:
        """Load user categories with decryption following Hushh MCP protocols"""
        try:
            file_path = self.get_user_file_path(user_id, data_type)
            
            if not os.path.exists(file_path):
                logger.info(f"📂 No saved {data_type} found for user {user_id[:8]}...")
                return {}
            
            # Try to read as new JSON format first
            try:
                with open(file_path, 'r') as f:
                    encrypted_dict = json.load(f)
                
                # Convert back to EncryptedPayload object
                from hushh_mcp.types import EncryptedPayload
                encrypted_payload = EncryptedPayload(
                    ciphertext=encrypted_dict["ciphertext"],
                    iv=encrypted_dict["iv"],
                    tag=encrypted_dict["tag"],
                    encoding=encrypted_dict.get("encoding", "base64"),
                    algorithm=encrypted_dict.get("algorithm", "aes-256-gcm")
                )
                
                # Decrypt
                decrypted_str = decrypt_data(encrypted_payload, VAULT_ENCRYPTION_KEY)
                
            except (json.JSONDecodeError, UnicodeDecodeError, KeyError):
                # Fallback: try old binary format for backward compatibility
                logger.info(f"🔄 Attempting to migrate old format for user {user_id[:8]}...")
                with open(file_path, 'rb') as f:
                    encrypted_data = f.read()
                
                # For old format, the encrypted_data might be bytes
                if isinstance(encrypted_data, bytes):
                    # This will likely fail with current encrypt/decrypt functions
                    # but we'll handle it gracefully
                    logger.warning(f"⚠️  Old binary format detected for user {user_id[:8]}. Data migration needed.")
                    return {}
                else:
                    decrypted_str = decrypt_data(encrypted_data, VAULT_ENCRYPTION_KEY)
            
            # Parse the decrypted data
            data = json.loads(decrypted_str)
            
            # Validate data structure
            if data.get("user_id") != user_id:
                logger.warning(f"⚠️  User ID mismatch in saved data for {user_id}")
                return {}
            
            categories = data.get("categories", {})
            last_updated = data.get("last_updated", "")
            
            logger.info(f"📖 Loaded {data_type} for user {user_id[:8]}... ({len(categories)} categories, updated: {last_updated})")
            return categories
            
        except Exception as e:
            logger.error(f"❌ Failed to load {data_type} for user {user_id}: {e}")
            return {}
    
    def save_user_emails(self, user_id: str, emails: List[Dict[str, Any]]) -> bool:
        """Save user emails with categories"""
        return self.save_user_categories(user_id, {"emails": emails}, "emails")
    
    def load_user_emails(self, user_id: str) -> List[Dict[str, Any]]:
        """Load user emails"""
        data = self.load_user_categories(user_id, "emails")
        return data.get("emails", [])
    
    def save_user_calendar_events(self, user_id: str, events: List[Dict[str, Any]]) -> bool:
        """Save user calendar events with categories"""
        return self.save_user_categories(user_id, {"events": events}, "calendar")
    
    def load_user_calendar_events(self, user_id: str) -> List[Dict[str, Any]]:
        """Load user calendar events"""
        data = self.load_user_categories(user_id, "calendar")
        return data.get("events", [])
    
    def get_unified_categories(self, user_id: str) -> Dict[str, Any]:
        """Get unified categories from both email and calendar data"""
        try:
            # Load email categories
            email_data = self.load_user_emails(user_id)
            calendar_data = self.load_user_calendar_events(user_id)
            
            # Count categories
            unified_categories = {}
            
            # Process emails
            for email in email_data:
                category = email.get("category", "uncategorized")
                if category not in unified_categories:
                    unified_categories[category] = {
                        "total": 0,
                        "email_count": 0,
                        "calendar_count": 0,
                        "sources": []
                    }
                
                unified_categories[category]["total"] += 1
                unified_categories[category]["email_count"] += 1
                if "email" not in unified_categories[category]["sources"]:
                    unified_categories[category]["sources"].append("email")
            
            # Process calendar events
            for event in calendar_data:
                category = event.get("category", "uncategorized")
                if category not in unified_categories:
                    unified_categories[category] = {
                        "total": 0,
                        "email_count": 0,
                        "calendar_count": 0,
                        "sources": []
                    }
                
                unified_categories[category]["total"] += 1
                unified_categories[category]["calendar_count"] += 1
                if "calendar" not in unified_categories[category]["sources"]:
                    unified_categories[category]["sources"].append("calendar")
            
            logger.info(f"🔄 Generated unified categories for user {user_id[:8]}... ({len(unified_categories)} categories)")
            return unified_categories
            
        except Exception as e:
            logger.error(f"❌ Failed to get unified categories for user {user_id}: {e}")
            return {}
    
    def get_emails_by_category(self, user_id: str, category: str) -> List[Dict[str, Any]]:
        """Get emails filtered by category"""
        emails = self.load_user_emails(user_id)
        logger.info(f"🔍 Debug: Loaded {len(emails)} total emails for user {user_id[:8]}...")
        
        if emails:
            logger.info(f"🔍 Debug: Sample email categories: {[email.get('category') for email in emails[:3]]}")
            logger.info(f"🔍 Debug: Looking for category: '{category}'")
        
        filtered_emails = [email for email in emails if email.get("category") == category]
        logger.info(f"📧 Found {len(filtered_emails)} emails in category '{category}' for user {user_id[:8]}...")
        
        if filtered_emails:
            logger.info(f"🔍 Debug: First filtered email structure: {list(filtered_emails[0].keys())}")
        
        return filtered_emails
    
    def get_events_by_category(self, user_id: str, category: str) -> List[Dict[str, Any]]:
        """Get calendar events filtered by category"""
        events = self.load_user_calendar_events(user_id)
        filtered_events = [event for event in events if event.get("category") == category]
        logger.info(f"📅 Found {len(filtered_events)} events in category '{category}' for user {user_id[:8]}...")
        return filtered_events
    
    def delete_user_data(self, user_id: str, data_type: str = "all") -> bool:
        """Delete user data (for consent revocation)"""
        try:
            deleted_files = []
            
            if data_type == "all":
                # Delete all user data
                data_types = ["categories", "emails", "calendar"]
            else:
                data_types = [data_type]
            
            for dt in data_types:
                file_path = self.get_user_file_path(user_id, dt)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    deleted_files.append(dt)
            
            if deleted_files:
                logger.info(f"🗑️  Deleted {', '.join(deleted_files)} data for user {user_id[:8]}...")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to delete {data_type} data for user {user_id}: {e}")
            return False
    
    def user_has_data(self, user_id: str) -> Dict[str, bool]:
        """Check what data exists for a user"""
        data_types = ["emails", "calendar", "categories"]
        has_data = {}
        
        for data_type in data_types:
            file_path = self.get_user_file_path(user_id, data_type)
            has_data[data_type] = os.path.exists(file_path)
        
        return has_data

# Global instance
persistent_storage = PersistentUserStorage()
