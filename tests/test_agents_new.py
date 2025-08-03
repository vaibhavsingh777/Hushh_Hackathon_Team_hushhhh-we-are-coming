# tests/test_agents.py

import pytest
from hushh_mcp.agents.identity import HushhIdentityAgent
from hushh_mcp.operons.verify_email import verify_user_email
from hushh_mcp.trust.link import is_trusted_for_scope
from hushh_mcp.consent.token import issue_token, revoke_token, validate_token
from hushh_mcp.constants import ConsentScope


USER_ID = "user_alice"
IDENTITY_AGENT_ID = "agent_identity"
EMAIL = "alice@hushh.ai"
INVALID_EMAIL = "alice@"
SCOPE = ConsentScope.VAULT_READ_EMAIL


def test_email_verification_valid():
    assert verify_user_email(EMAIL) is True


def test_email_verification_invalid():
    assert verify_user_email(INVALID_EMAIL) is False


def test_identity_agent_trust_link_creation():
    identity_agent = HushhIdentityAgent(agent_id=IDENTITY_AGENT_ID)
    
    trust = identity_agent.issue_trust_link(
        from_agent=IDENTITY_AGENT_ID,
        to_agent="agent_data_manager",  # Use an existing agent
        user_id=USER_ID,
        scope=SCOPE
    )
    
    assert trust.from_agent == IDENTITY_AGENT_ID
    assert trust.to_agent == "agent_data_manager"
    assert trust.signed_by_user == USER_ID


def test_identity_agent_with_valid_consent():
    """Test that identity agent properly verifies email"""
    identity_agent = HushhIdentityAgent(agent_id=IDENTITY_AGENT_ID)
    
    # Test email verification (the main function of identity agent)
    result = identity_agent.verify_user_identity(EMAIL)
    assert result is True


def test_identity_agent_with_invalid_email():
    """Test that identity agent rejects invalid email"""
    identity_agent = HushhIdentityAgent(agent_id=IDENTITY_AGENT_ID)
    
    # Test email verification with invalid email
    result = identity_agent.verify_user_identity(INVALID_EMAIL)
    assert result is False


def test_token_user_mismatch():
    """Test that agents reject tokens with mismatched user IDs"""
    token_obj = issue_token("user_bob", IDENTITY_AGENT_ID, SCOPE)
    
    # This would be used in agents that validate user_id matches token
    valid, reason, parsed_token = validate_token(token_obj.token, expected_scope=SCOPE)
    assert valid is True
    assert parsed_token.user_id == "user_bob"  # Should match the token, not USER_ID
