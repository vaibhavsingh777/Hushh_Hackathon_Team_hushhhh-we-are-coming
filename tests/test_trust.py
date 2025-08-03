# tests/test_trust.py

import pytest
from hushh_mcp.trust.link import (
    create_trust_link,
    verify_trust_link,
    is_trusted_for_scope
)
from hushh_mcp.types import TrustLink
from hushh_mcp.constants import ConsentScope


USER_ID = "user_nyx"
DELEGATOR = "agent_identity"
DELEGATEE = "agent_shopper"
SCOPE_VALID = ConsentScope.VAULT_READ_EMAIL
SCOPE_INVALID = ConsentScope.VAULT_READ_PHONE


def test_create_and_verify_trust_link():
    link = create_trust_link(DELEGATOR, DELEGATEE, SCOPE_VALID, USER_ID)
    assert isinstance(link, TrustLink)

    assert verify_trust_link(link) is True
    assert is_trusted_for_scope(link, SCOPE_VALID) is True
    assert is_trusted_for_scope(link, SCOPE_INVALID) is False


def test_expired_trust_link():
    # Expire immediately
    expired = create_trust_link(
        from_agent=DELEGATOR,
        to_agent=DELEGATEE,
        scope=SCOPE_VALID,
        signed_by_user=USER_ID,
        expires_in_ms=-1000  # already expired
    )

    assert verify_trust_link(expired) is False
    assert is_trusted_for_scope(expired, SCOPE_VALID) is False


def test_signature_tampering():
    link = create_trust_link(DELEGATOR, DELEGATEE, SCOPE_VALID, USER_ID)

    tampered = link.copy(update={"signature": "bad_signature_here"})

    assert verify_trust_link(tampered) is False
    assert is_trusted_for_scope(tampered, SCOPE_VALID) is False
