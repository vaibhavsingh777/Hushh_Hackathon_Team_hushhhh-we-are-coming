# tests/test_token.py

import pytest
import time
from hushh_mcp.consent.token import (
    issue_token,
    validate_token,
    revoke_token,
    is_token_revoked
)
from hushh_mcp.constants import ConsentScope
from hushh_mcp.types import HushhConsentToken


USER_ID = "user_test"
AGENT_ID = "agent_alpha"
VALID_SCOPE = ConsentScope.VAULT_READ_EMAIL


def test_issue_and_validate_token():
    token_obj: HushhConsentToken = issue_token(USER_ID, AGENT_ID, VALID_SCOPE)
    assert token_obj.token.startswith("HCT:")

    valid, reason, parsed = validate_token(token_obj.token, VALID_SCOPE)
    assert valid is True
    assert reason is None
    assert parsed is not None
    assert parsed.user_id == USER_ID
    assert parsed.scope == VALID_SCOPE


def test_token_scope_mismatch():
    token_obj = issue_token(USER_ID, AGENT_ID, VALID_SCOPE)
    valid, reason, _ = validate_token(token_obj.token, ConsentScope.VAULT_READ_PHONE)
    assert valid is False
    assert reason == "Scope mismatch"


def test_token_expiry():
    token_obj = issue_token(USER_ID, AGENT_ID, VALID_SCOPE, expires_in_ms=-1000)
    valid, reason, _ = validate_token(token_obj.token, VALID_SCOPE)
    assert valid is False
    assert reason == "Token expired"


def test_token_revocation():
    token_obj = issue_token(USER_ID, AGENT_ID, VALID_SCOPE)
    revoke_token(token_obj.token)
    assert is_token_revoked(token_obj.token) is True

    valid, reason, _ = validate_token(token_obj.token, VALID_SCOPE)
    assert valid is False
    assert reason == "Token has been revoked"


def test_signature_tampering():
    token_obj = issue_token(USER_ID, AGENT_ID, VALID_SCOPE)
    tampered = token_obj.token.replace("HCT:", "HCT_TAMPERED:")
    valid, reason, _ = validate_token(tampered, VALID_SCOPE)
    assert valid is False
    assert "Malformed token" in reason or "Invalid token prefix" in reason
