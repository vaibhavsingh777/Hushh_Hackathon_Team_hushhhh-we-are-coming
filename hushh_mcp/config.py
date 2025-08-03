# hushh_mcp/config.py

import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')

# Load .env file into environment
load_dotenv()

# ==================== Security Keys ====================

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY or len(SECRET_KEY) < 32:
    raise ValueError("❌ SECRET_KEY must be set in .env and at least 32 characters long")

VAULT_ENCRYPTION_KEY = os.getenv("VAULT_ENCRYPTION_KEY")
if not VAULT_ENCRYPTION_KEY or len(VAULT_ENCRYPTION_KEY) != 64:
    raise ValueError("❌ VAULT_ENCRYPTION_KEY must be a 64-character hex string (256-bit AES key)")

# ==================== Expiration Settings ====================

# Default expiry durations (in milliseconds)
# 7 days
DEFAULT_CONSENT_TOKEN_EXPIRY_MS = int(os.getenv("DEFAULT_CONSENT_TOKEN_EXPIRY_MS", 1000 * 60 * 60 * 24 * 7))  # 30 days
DEFAULT_TRUST_LINK_EXPIRY_MS = int(os.getenv("DEFAULT_TRUST_LINK_EXPIRY_MS", 1000 * 60 * 60 * 24 * 30))      

# ==================== Environment Info ====================

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
AGENT_ID = os.getenv("AGENT_ID", "agent_hushh_default")
HUSHH_HACKATHON = os.getenv("HUSHH_HACKATHON", "disabled").lower() == "enabled"

# ==================== Additional Configuration ====================

# Google OAuth Configuration
GOOGLE_OAUTH_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID", os.getenv("GOOGLE_OAUTH_CLIENT_ID"))
GOOGLE_OAUTH_CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", os.getenv("GOOGLE_OAUTH_CLIENT_SECRET"))
GOOGLE_OAUTH_REDIRECT_URI = os.getenv("GOOGLE_OAUTH_REDIRECT_URI", os.getenv("GOOGLE_OAUTH_REDIRECT_URI"))

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", SECRET_KEY)

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "./hushh_audit.db")

# LLM Configuration (Multiple providers for free alternatives)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# Free LLM Alternatives
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

# ==================== Configuration Class ====================

class Config:
    """Configuration class for easy access to all settings"""
    
    # Security
    SECRET_KEY = SECRET_KEY
    VAULT_ENCRYPTION_KEY = VAULT_ENCRYPTION_KEY
    JWT_SECRET = JWT_SECRET
    
    # OAuth
    GOOGLE_OAUTH_CLIENT_ID = GOOGLE_OAUTH_CLIENT_ID
    GOOGLE_OAUTH_CLIENT_SECRET = GOOGLE_OAUTH_CLIENT_SECRET
    GOOGLE_OAUTH_REDIRECT_URI = GOOGLE_OAUTH_REDIRECT_URI
    
    # Database
    DATABASE_URL = DATABASE_URL
    
    # AI/LLM
    # LLM Configuration
    OPENAI_API_KEY = OPENAI_API_KEY
    OPENAI_MODEL = OPENAI_MODEL
    HUGGINGFACE_API_KEY = HUGGINGFACE_API_KEY
    GROQ_API_KEY = GROQ_API_KEY
    OLLAMA_URL = OLLAMA_URL
    
    # Expiration
    DEFAULT_CONSENT_TOKEN_EXPIRY_MS = DEFAULT_CONSENT_TOKEN_EXPIRY_MS
    DEFAULT_TRUST_LINK_EXPIRY_MS = DEFAULT_TRUST_LINK_EXPIRY_MS
    
    # Environment
    ENVIRONMENT = ENVIRONMENT
    AGENT_ID = AGENT_ID
    HUSHH_HACKATHON = HUSHH_HACKATHON

def get_config():
    """Get configuration instance"""
    return Config()

# ==================== Defaults Export ====================

__all__ = [
    "SECRET_KEY",
    "VAULT_ENCRYPTION_KEY",
    "DEFAULT_CONSENT_TOKEN_EXPIRY_MS",
    "DEFAULT_TRUST_LINK_EXPIRY_MS",
    "ENVIRONMENT",
    "AGENT_ID",
    "HUSHH_HACKATHON",
    "GOOGLE_OAUTH_CLIENT_ID",
    "GOOGLE_OAUTH_CLIENT_SECRET", 
    "GOOGLE_OAUTH_REDIRECT_URI",
    "JWT_SECRET",
    "DATABASE_URL",
    "OPENAI_API_KEY",
    "OPENAI_MODEL",
    "HUGGINGFACE_API_KEY",
    "GROQ_API_KEY",
    "OLLAMA_URL",
    "Config",
    "get_config"
]
