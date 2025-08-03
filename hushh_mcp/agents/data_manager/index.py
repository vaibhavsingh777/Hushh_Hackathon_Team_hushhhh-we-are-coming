# hushh_mcp/agents/data_manager/index.py

from typing import Dict, Any, List, Optional
from hushh_mcp.consent.token import validate_token
from hushh_mcp.constants import ConsentScope
from hushh_mcp.types import UserID, VaultRecord, VaultKey, EncryptedPayload
from hushh_mcp.vault.encrypt import encrypt_data, decrypt_data
from hushh_mcp.config import VAULT_ENCRYPTION_KEY
import time
import json


class DataManagerAgent:
    """
    Specialized agent for vault operations and data management.
    Handles encrypted storage and retrieval of user data with zero data retention.
    """

    def __init__(self, agent_id: str = "agent_data_manager"):
        self.agent_id = agent_id
        self.encryption_key = VAULT_ENCRYPTION_KEY
        # In-memory storage for demo (production would use secure database)
        self.vault_storage: Dict[str, VaultRecord] = {}

    def store_data(self, user_id: UserID, token_str: str, data: Any, scope: str) -> Dict[str, Any]:
        """
        Store encrypted data in vault with consent validation.
        
        Args:
            user_id: User requesting storage
            token_str: Valid consent token
            data: Data to store (will be encrypted)
            scope: Data scope for access control
            
        Returns:
            Dict with storage results
        """
        # Validate consent for data writing
        valid, reason, token = validate_token(token_str, expected_scope=ConsentScope.CUSTOM_SESSION_WRITE)
        
        if not valid:
            raise PermissionError(f"❌ Data storage denied: {reason}")
        
        if token.user_id != user_id:
            raise PermissionError("❌ Token user mismatch")

        print(f"🔒 Data Manager storing data for user {user_id} with scope {scope}")
        
        try:
            # Convert data to JSON string for encryption
            data_str = json.dumps(data) if not isinstance(data, str) else data
            
            # Encrypt the data
            encrypted_payload = encrypt_data(data_str, self.encryption_key)
            
            # Create vault key
            vault_key = VaultKey(user_id=user_id, scope=scope)
            
            # Create vault record
            vault_record = VaultRecord(
                key=vault_key,
                data=encrypted_payload,
                agent_id=self.agent_id,
                created_at=int(time.time() * 1000),
                expires_at=None,  # Set based on consent token expiry
                deleted=False,
                metadata={
                    "token_id": token.signature[:8],
                    "data_type": type(data).__name__,
                    "size_bytes": len(data_str),
                    "encrypted_at": int(time.time() * 1000)
                }
            )
            
            # Store in vault
            storage_key = f"{user_id}:{scope}"
            self.vault_storage[storage_key] = vault_record
            
            result = {
                "storage_key": storage_key,
                "user_id": user_id,
                "scope": scope,
                "data_size": len(data_str),
                "encrypted": True,
                "stored_at": vault_record.created_at,
                "agent_id": self.agent_id,
                "status": "stored"
            }
            
            print(f"✅ Data stored securely with key: {storage_key}")
            return result
            
        except Exception as e:
            print(f"❌ Data storage failed: {str(e)}")
            return {"error": f"Data storage failed: {str(e)}"}

    def retrieve_data(self, user_id: UserID, token_str: str, scope: str) -> Dict[str, Any]:
        """
        Retrieve and decrypt data from vault with consent validation.
        """
        # Determine required scope for reading
        read_scope = self._map_to_read_scope(scope)
        
        # Validate consent for data reading
        valid, reason, token = validate_token(token_str, expected_scope=read_scope)
        
        if not valid:
            raise PermissionError(f"❌ Data retrieval denied: {reason}")

        print(f"🔓 Data Manager retrieving data for user {user_id} with scope {scope}")
        
        try:
            # Find vault record
            storage_key = f"{user_id}:{scope}"
            vault_record = self.vault_storage.get(storage_key)
            
            if not vault_record:
                return {"error": f"No data found for scope: {scope}"}
            
            if vault_record.deleted:
                return {"error": f"Data has been deleted for scope: {scope}"}
            
            # Check if data has expired
            if vault_record.expires_at and vault_record.expires_at < int(time.time() * 1000):
                return {"error": f"Data has expired for scope: {scope}"}
            
            # Decrypt the data
            decrypted_data = decrypt_data(vault_record.data, self.encryption_key)
            
            # Try to parse as JSON, fallback to string
            try:
                parsed_data = json.loads(decrypted_data)
            except json.JSONDecodeError:
                parsed_data = decrypted_data
            
            result = {
                "user_id": user_id,
                "scope": scope,
                "data": parsed_data,
                "metadata": vault_record.metadata,
                "created_at": vault_record.created_at,
                "retrieved_at": int(time.time() * 1000),
                "agent_id": self.agent_id,
                "status": "retrieved"
            }
            
            print(f"✅ Data retrieved successfully for scope: {scope}")
            return result
            
        except Exception as e:
            print(f"❌ Data retrieval failed: {str(e)}")
            return {"error": f"Data retrieval failed: {str(e)}"}

    def delete_data(self, user_id: UserID, token_str: str, scope: str) -> Dict[str, Any]:
        """
        Delete data from vault with consent validation.
        """
        # Validate consent for data deletion
        valid, reason, token = validate_token(token_str, expected_scope=ConsentScope.CUSTOM_SESSION_WRITE)
        
        if not valid:
            raise PermissionError(f"❌ Data deletion denied: {reason}")

        print(f"🗑️ Data Manager deleting data for user {user_id} with scope {scope}")
        
        try:
            storage_key = f"{user_id}:{scope}"
            vault_record = self.vault_storage.get(storage_key)
            
            if not vault_record:
                return {"error": f"No data found for scope: {scope}"}
            
            # Mark as deleted (soft delete for audit trail)
            vault_record.deleted = True
            vault_record.updated_at = int(time.time() * 1000)
            vault_record.metadata["deleted_at"] = int(time.time() * 1000)
            vault_record.metadata["deleted_by_token"] = token.signature[:8]
            
            result = {
                "user_id": user_id,
                "scope": scope,
                "deleted_at": vault_record.updated_at,
                "agent_id": self.agent_id,
                "status": "deleted"
            }
            
            print(f"✅ Data deleted for scope: {scope}")
            return result
            
        except Exception as e:
            print(f"❌ Data deletion failed: {str(e)}")
            return {"error": f"Data deletion failed: {str(e)}"}

    def list_user_data(self, user_id: UserID, token_str: str) -> Dict[str, Any]:
        """
        List all data scopes for a user.
        """
        # Validate consent
        valid, reason, token = validate_token(token_str, expected_scope=ConsentScope.CUSTOM_TEMPORARY)
        
        if not valid:
            raise PermissionError(f"❌ Data listing denied: {reason}")

        print(f"📋 Data Manager listing data for user {user_id}")
        
        try:
            user_data = []
            
            for storage_key, vault_record in self.vault_storage.items():
                record_user_id, scope = storage_key.split(":", 1)
                
                if record_user_id == user_id and not vault_record.deleted:
                    user_data.append({
                        "scope": scope,
                        "created_at": vault_record.created_at,
                        "size_bytes": vault_record.metadata.get("size_bytes", 0),
                        "data_type": vault_record.metadata.get("data_type", "unknown"),
                        "expires_at": vault_record.expires_at
                    })
            
            result = {
                "user_id": user_id,
                "total_scopes": len(user_data),
                "data_scopes": user_data,
                "total_size_bytes": sum(item["size_bytes"] for item in user_data),
                "listed_at": int(time.time() * 1000)
            }
            
            print(f"✅ Found {len(user_data)} data scopes for user")
            return result
            
        except Exception as e:
            print(f"❌ Data listing failed: {str(e)}")
            return {"error": f"Data listing failed: {str(e)}"}

    def cleanup_expired_data(self) -> Dict[str, Any]:
        """
        Clean up expired data entries.
        """
        print("🧹 Data Manager cleaning up expired data")
        
        current_time = int(time.time() * 1000)
        expired_count = 0
        
        for storage_key, vault_record in self.vault_storage.items():
            if (vault_record.expires_at and 
                vault_record.expires_at < current_time and 
                not vault_record.deleted):
                
                vault_record.deleted = True
                vault_record.updated_at = current_time
                vault_record.metadata["auto_deleted_at"] = current_time
                vault_record.metadata["deletion_reason"] = "expired"
                expired_count += 1
        
        result = {
            "cleaned_count": expired_count,
            "cleaned_at": current_time,
            "agent_id": self.agent_id
        }
        
        print(f"✅ Cleaned up {expired_count} expired data entries")
        return result

    def get_storage_statistics(self, user_id: UserID, token_str: str) -> Dict[str, Any]:
        """
        Get storage statistics for a user.
        """
        # Validate consent
        valid, reason, token = validate_token(token_str, expected_scope=ConsentScope.CUSTOM_TEMPORARY)
        
        if not valid:
            raise PermissionError(f"❌ Storage statistics denied: {reason}")

        print(f"📊 Data Manager generating storage statistics for user {user_id}")
        
        try:
            total_size = 0
            active_scopes = 0
            deleted_scopes = 0
            expired_scopes = 0
            current_time = int(time.time() * 1000)
            
            scope_breakdown = {}
            
            for storage_key, vault_record in self.vault_storage.items():
                record_user_id, scope = storage_key.split(":", 1)
                
                if record_user_id == user_id:
                    size = vault_record.metadata.get("size_bytes", 0)
                    
                    if vault_record.deleted:
                        deleted_scopes += 1
                    elif vault_record.expires_at and vault_record.expires_at < current_time:
                        expired_scopes += 1
                    else:
                        active_scopes += 1
                        total_size += size
                        
                        scope_category = scope.split(".")[0] if "." in scope else "other"
                        scope_breakdown[scope_category] = scope_breakdown.get(scope_category, 0) + size
            
            result = {
                "user_id": user_id,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "active_scopes": active_scopes,
                "deleted_scopes": deleted_scopes,
                "expired_scopes": expired_scopes,
                "scope_breakdown": scope_breakdown,
                "storage_efficiency": round(active_scopes / (active_scopes + deleted_scopes) * 100, 2) if (active_scopes + deleted_scopes) > 0 else 100,
                "generated_at": current_time
            }
            
            print(f"✅ Storage statistics generated for user {user_id}")
            return result
            
        except Exception as e:
            print(f"❌ Storage statistics failed: {str(e)}")
            return {"error": f"Storage statistics failed: {str(e)}"}

    def _map_to_read_scope(self, scope: str) -> ConsentScope:
        """
        Map data scope to appropriate read consent scope.
        """
        scope_mapping = {
            "email": ConsentScope.VAULT_READ_EMAIL,
            "finance": ConsentScope.VAULT_READ_FINANCE,
            "phone": ConsentScope.VAULT_READ_PHONE,
            "contacts": ConsentScope.VAULT_READ_CONTACTS
        }
        
        # Extract base scope
        base_scope = scope.split(".")[0] if "." in scope else scope
        
        return scope_mapping.get(base_scope, ConsentScope.CUSTOM_TEMPORARY)

    def backup_user_data(self, user_id: UserID, token_str: str) -> Dict[str, Any]:
        """
        Create encrypted backup of all user data.
        """
        # Validate consent
        valid, reason, token = validate_token(token_str, expected_scope=ConsentScope.CUSTOM_TEMPORARY)
        
        if not valid:
            raise PermissionError(f"❌ Data backup denied: {reason}")

        print(f"💾 Data Manager creating backup for user {user_id}")
        
        try:
            user_data = {}
            
            for storage_key, vault_record in self.vault_storage.items():
                record_user_id, scope = storage_key.split(":", 1)
                
                if record_user_id == user_id and not vault_record.deleted:
                    # Include encrypted data and metadata
                    user_data[scope] = {
                        "encrypted_data": {
                            "ciphertext": vault_record.data.ciphertext,
                            "iv": vault_record.data.iv,
                            "tag": vault_record.data.tag,
                            "encoding": vault_record.data.encoding,
                            "algorithm": vault_record.data.algorithm
                        },
                        "metadata": vault_record.metadata,
                        "created_at": vault_record.created_at,
                        "expires_at": vault_record.expires_at
                    }
            
            backup_data = {
                "user_id": user_id,
                "backup_created_at": int(time.time() * 1000),
                "data_count": len(user_data),
                "vault_data": user_data,
                "agent_id": self.agent_id
            }
            
            # Encrypt the entire backup
            backup_str = json.dumps(backup_data)
            encrypted_backup = encrypt_data(backup_str, self.encryption_key)
            
            result = {
                "user_id": user_id,
                "backup_size": len(backup_str),
                "data_count": len(user_data),
                "encrypted_backup": encrypted_backup,
                "created_at": backup_data["backup_created_at"]
            }
            
            print(f"✅ Backup created for user {user_id} with {len(user_data)} data entries")
            return result
            
        except Exception as e:
            print(f"❌ Data backup failed: {str(e)}")
            return {"error": f"Data backup failed: {str(e)}"}
