# hushh_mcp/agents/data_manager/manifest.py

manifest = {
    "id": "agent_data_manager",
    "name": "Data Manager Agent",
    "description": "Specialized agent for vault operations and encrypted data management with zero data retention",
    "scopes": [
        "vault.read.email",
        "vault.read.finance",
        "vault.read.phone", 
        "vault.read.contacts",
        "custom.session.write",
        "custom.temporary"
    ],
    "version": "1.0.0",
    "capabilities": [
        "encrypted_storage",
        "secure_retrieval", 
        "data_deletion",
        "backup_creation",
        "storage_analytics",
        "expiry_management",
        "scope_mapping"
    ],
    "dependencies": [
        "vault_encrypt_operon",
        "aes_256_gcm_encryption"
    ],
    "security_features": [
        "zero_data_retention",
        "scope_based_access",
        "automatic_expiry",
        "soft_deletion",
        "audit_trail",
        "encrypted_backups"
    ],
    "storage": {
        "type": "in_memory",
        "encryption": "AES-256-GCM",
        "retention_policy": "consent_based",
        "backup_support": True
    }
}
