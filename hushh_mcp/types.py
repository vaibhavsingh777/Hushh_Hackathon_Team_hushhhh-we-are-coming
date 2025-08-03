# hushh_mcp/types.py

from typing import Literal, TypedDict, Optional, NewType
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

# ==================== Aliases ====================

UserID = NewType("UserID", str)
AgentID = NewType("AgentID", str)

# Import shared scope type from constants
from hushh_mcp.constants import ConsentScope

# ==================== HushhConsentToken ====================

class HushhConsentToken(BaseModel):
    token: str
    user_id: UserID
    agent_id: AgentID
    scope: ConsentScope
    issued_at: int  # epoch ms
    expires_at: int  # epoch ms
    signature: str
    
    def is_valid(self) -> bool:
        """Check if the token is valid (not expired and not revoked)"""
        import time
        current_time = int(time.time() * 1000)
        if current_time > self.expires_at:
            return False
        
        # Check if token is revoked
        from hushh_mcp.consent.token import is_token_revoked
        return not is_token_revoked(self.token)

# ==================== TrustLink ====================

class TrustLink(BaseModel):
    from_agent: AgentID
    to_agent: AgentID
    scope: ConsentScope
    created_at: int
    expires_at: int
    signed_by_user: UserID
    signature: str

# ==================== Vault Structures ====================

class VaultKey(BaseModel):
    user_id: UserID
    scope: ConsentScope

class EncryptedPayload(BaseModel):
    ciphertext: str
    iv: str
    tag: str
    encoding: Literal["base64", "hex"]
    algorithm: Literal["aes-256-gcm", "chacha20-poly1305"]

class VaultRecord(BaseModel):
    key: VaultKey
    data: EncryptedPayload
    agent_id: AgentID
    created_at: int
    updated_at: Optional[int] = None
    expires_at: Optional[int] = None
    deleted: Optional[bool] = False
    metadata: Optional[dict] = None
