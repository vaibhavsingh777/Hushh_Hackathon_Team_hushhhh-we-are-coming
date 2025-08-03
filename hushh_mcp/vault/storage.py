#!/usr/bin/env python3
"""
Hushh MCP - Vault Storage System
Secure storage for categorized emails and calendar events following MCP protocol.
"""

import json
import os
import sqlite3
from typing import Dict, List, Any, Optional
from datetime import datetime
from ..vault.encrypt import encrypt_data, decrypt_data
from ..config import VAULT_ENCRYPTION_KEY
from ..types import HushhConsentToken

class VaultStorage:
    """
    Secure storage system for user data following Hushh MCP protocols.
    All data is encrypted before storage and requires valid consent tokens.
    """
    
    def __init__(self, db_path: str = "vault_storage.db"):
        self.db_path = db_path
        self.encryption_key = VAULT_ENCRYPTION_KEY
        self._init_database()
    
    def _init_database(self):
        """Initialize the vault database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables for storing encrypted data
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vault_emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                email_id TEXT NOT NULL,
                encrypted_data TEXT NOT NULL,
                iv TEXT NOT NULL,
                tag TEXT NOT NULL,
                categories TEXT NOT NULL,
                confidence_scores TEXT NOT NULL,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, email_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vault_calendar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                event_id TEXT NOT NULL,
                encrypted_data TEXT NOT NULL,
                iv TEXT NOT NULL,
                tag TEXT NOT NULL,
                categories TEXT NOT NULL,
                confidence_scores TEXT NOT NULL,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, event_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vault_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                category_name TEXT NOT NULL,
                data_type TEXT NOT NULL,
                item_count INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, category_name, data_type)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consent_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                token_hash TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                scope TEXT NOT NULL,
                issued_at TIMESTAMP NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                revoked_at TIMESTAMP NULL,
                status TEXT DEFAULT 'active',
                UNIQUE(token_hash)
            )
        """)
        
        conn.commit()
        conn.close()
        print("✅ Vault storage database initialized")
    
    def store_email_data(
        self, 
        user_id: str, 
        email_id: str, 
        email_data: Dict[str, Any], 
        categories: List[str], 
        confidence_scores: Dict[str, float],
        consent_token: HushhConsentToken
    ) -> bool:
        """Store encrypted email data in the vault."""
        try:
            # Verify consent
            if consent_token.user_id != user_id:
                raise ValueError("User ID mismatch in consent token")
            
            # Encrypt the email data
            email_json = json.dumps(email_data)
            encrypted_payload = encrypt_data(email_json, self.encryption_key)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Store encrypted email data
            cursor.execute("""
                INSERT OR REPLACE INTO vault_emails 
                (user_id, email_id, encrypted_data, iv, tag, categories, confidence_scores)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                email_id,
                encrypted_payload.ciphertext,
                encrypted_payload.iv,
                encrypted_payload.tag,
                json.dumps(categories),
                json.dumps(confidence_scores)
            ))
            
            # Update category counts
            for category in categories:
                cursor.execute("""
                    INSERT OR REPLACE INTO vault_categories 
                    (user_id, category_name, data_type, item_count, last_updated)
                    VALUES (?, ?, ?, 
                        COALESCE((SELECT item_count FROM vault_categories 
                                WHERE user_id=? AND category_name=? AND data_type=?), 0) + 1,
                        CURRENT_TIMESTAMP)
                """, (user_id, category, "email", user_id, category, "email"))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Failed to store email data: {str(e)}")
            return False
    
    def store_calendar_data(
        self, 
        user_id: str, 
        event_id: str, 
        event_data: Dict[str, Any], 
        categories: List[str], 
        confidence_scores: Dict[str, float],
        consent_token: HushhConsentToken
    ) -> bool:
        """Store encrypted calendar data in the vault."""
        try:
            # Verify consent
            if consent_token.user_id != user_id:
                raise ValueError("User ID mismatch in consent token")
            
            # Encrypt the event data
            event_json = json.dumps(event_data)
            encrypted_payload = encrypt_data(event_json, self.encryption_key)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Store encrypted calendar data
            cursor.execute("""
                INSERT OR REPLACE INTO vault_calendar 
                (user_id, event_id, encrypted_data, iv, tag, categories, confidence_scores)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                event_id,
                encrypted_payload.ciphertext,
                encrypted_payload.iv,
                encrypted_payload.tag,
                json.dumps(categories),
                json.dumps(confidence_scores)
            ))
            
            # Update category counts
            for category in categories:
                cursor.execute("""
                    INSERT OR REPLACE INTO vault_categories 
                    (user_id, category_name, data_type, item_count, last_updated)
                    VALUES (?, ?, ?, 
                        COALESCE((SELECT item_count FROM vault_categories 
                                WHERE user_id=? AND category_name=? AND data_type=?), 0) + 1,
                        CURRENT_TIMESTAMP)
                """, (user_id, category, "calendar", user_id, category, "calendar"))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Failed to store calendar data: {str(e)}")
            return False
    
    def get_user_categories(self, user_id: str, data_type: Optional[str] = None) -> Dict[str, Any]:
        """Get user's categorization summary."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = """
                SELECT category_name, data_type, item_count, last_updated 
                FROM vault_categories 
                WHERE user_id = ?
            """
            params = [user_id]
            
            if data_type:
                query += " AND data_type = ?"
                params.append(data_type)
            
            query += " ORDER BY item_count DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            categories = {}
            for row in rows:
                category_name, dtype, item_count, last_updated = row
                if dtype not in categories:
                    categories[dtype] = {}
                categories[dtype][category_name] = {
                    "count": item_count,
                    "last_updated": last_updated
                }
            
            conn.close()
            return categories
            
        except Exception as e:
            print(f"❌ Failed to get user categories: {str(e)}")
            return {}
    
    def delete_user_data(self, user_id: str, data_types: List[str] = ["all"]) -> Dict[str, int]:
        """Delete user data (right to be forgotten)."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            deleted_counts = {}
            
            if "emails" in data_types or "all" in data_types:
                cursor.execute("DELETE FROM vault_emails WHERE user_id = ?", (user_id,))
                deleted_counts["emails"] = cursor.rowcount
                
                cursor.execute("DELETE FROM vault_categories WHERE user_id = ? AND data_type = 'email'", (user_id,))
            
            if "calendar" in data_types or "all" in data_types:
                cursor.execute("DELETE FROM vault_calendar WHERE user_id = ?", (user_id,))
                deleted_counts["calendar"] = cursor.rowcount
                
                cursor.execute("DELETE FROM vault_categories WHERE user_id = ? AND data_type = 'calendar'", (user_id,))
            
            if "all" in data_types:
                cursor.execute("DELETE FROM consent_tokens WHERE user_id = ?", (user_id,))
                deleted_counts["consent_tokens"] = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            return deleted_counts
            
        except Exception as e:
            print(f"❌ Failed to delete user data: {str(e)}")
            return {}
    
    def export_user_data(self, user_id: str, consent_token: HushhConsentToken) -> Dict[str, Any]:
        """Export all user data (data portability)."""
        try:
            if consent_token.user_id != user_id:
                raise ValueError("User ID mismatch in consent token")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            export_data = {
                "user_id": user_id,
                "exported_at": datetime.now().isoformat(),
                "emails": [],
                "calendar": [],
                "categories": self.get_user_categories(user_id)
            }
            
            # Export email data (decrypt for export)
            cursor.execute("""
                SELECT email_id, encrypted_data, iv, tag, categories, confidence_scores, processed_at
                FROM vault_emails WHERE user_id = ?
            """, (user_id,))
            
            for row in cursor.fetchall():
                email_id, ciphertext, iv, tag, categories, confidence, processed_at = row
                
                # Decrypt for export
                from ..types import EncryptedPayload
                encrypted_payload = EncryptedPayload(
                    ciphertext=ciphertext,
                    iv=iv,
                    tag=tag,
                    encoding="base64",
                    algorithm="aes-256-gcm"
                )
                
                decrypted_data = decrypt_data(encrypted_payload, self.encryption_key)
                email_data = json.loads(decrypted_data)
                
                export_data["emails"].append({
                    "email_id": email_id,
                    "data": email_data,
                    "categories": json.loads(categories),
                    "confidence_scores": json.loads(confidence),
                    "processed_at": processed_at
                })
            
            # Export calendar data (decrypt for export)
            cursor.execute("""
                SELECT event_id, encrypted_data, iv, tag, categories, confidence_scores, processed_at
                FROM vault_calendar WHERE user_id = ?
            """, (user_id,))
            
            for row in cursor.fetchall():
                event_id, ciphertext, iv, tag, categories, confidence, processed_at = row
                
                # Decrypt for export
                from ..types import EncryptedPayload
                encrypted_payload = EncryptedPayload(
                    ciphertext=ciphertext,
                    iv=iv,
                    tag=tag,
                    encoding="base64",
                    algorithm="aes-256-gcm"
                )
                
                decrypted_data = decrypt_data(encrypted_payload, self.encryption_key)
                event_data = json.loads(decrypted_data)
                
                export_data["calendar"].append({
                    "event_id": event_id,
                    "data": event_data,
                    "categories": json.loads(categories),
                    "confidence_scores": json.loads(confidence),
                    "processed_at": processed_at
                })
            
            conn.close()
            return export_data
            
        except Exception as e:
            print(f"❌ Failed to export user data: {str(e)}")
            return {}
    
    def record_consent_token(self, consent_token: HushhConsentToken) -> bool:
        """Record a consent token in the vault for audit purposes."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Hash the token for storage (don't store the actual token)
            import hashlib
            token_hash = hashlib.sha256(consent_token.token.encode()).hexdigest()
            
            cursor.execute("""
                INSERT OR REPLACE INTO consent_tokens 
                (user_id, token_hash, agent_id, scope, issued_at, expires_at, status)
                VALUES (?, ?, ?, ?, ?, ?, 'active')
            """, (
                consent_token.user_id,
                token_hash,
                consent_token.agent_id,
                consent_token.scope.value,
                datetime.fromtimestamp(consent_token.issued_at / 1000),
                datetime.fromtimestamp(consent_token.expires_at / 1000)
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Failed to record consent token: {str(e)}")
            return False


# Global vault storage instance
vault_storage = VaultStorage()
