"""Shared source-byte acquisition priority policy.

Keep this tiny and stdlib-only. The source-byte queue, intake manifest, and
external-cache receipt scanner all need the same ordering semantics; duplicating
those tag sets made it too easy for batch handoffs and reports to drift while
still looking internally plausible.
"""
from __future__ import annotations

from typing import Any

HIGH_IMPACT_TAGS = frozenset(
    {
        "eac",
        "nist",
        "cisa",
        "cdf",
        "vvsg",
        "voter_information",
        "official_websites",
        "accessibility",
        "language_access",
        "remote_return",
        "ai",
        "audit",
        "rla",
        "certification",
        "public_comms",
        "communications",
    }
)

PROTOCOL_TAGS = frozenset(
    {
        "rfc",
        "ietf_draft",
        "http",
        "dns",
        "tls",
        "email",
        "scitt",
        "in_toto",
        "slsa",
        "c2pa",
        "time",
        "ed25519",
        "signature",
        "jcs",
    }
)

HIGH_IMPACT_PREFIXES = ("eac_", "nist_", "cisa_")
PROTOCOL_PREFIXES = ("rfc", "draft_ietf_", "intoto_")


def _tags(row: dict[str, Any]) -> set[str]:
    return {str(t) for t in (row.get("tags") or [])}


def source_byte_priority_tier(row: dict[str, Any], *, has_receipt: bool = False) -> str:
    """Return the deterministic source-byte acquisition priority tier.

    ``has_receipt`` is part of the policy because receipt-present rows must sort
    to the end of queue-style surfaces, while receipt-missing surfaces only call
    this with the default ``False``.
    """

    if has_receipt:
        return "Z-receipt-present"
    tags = _tags(row)
    sid = str(row.get("id") or "")
    if tags & HIGH_IMPACT_TAGS or sid.startswith(HIGH_IMPACT_PREFIXES):
        return "A-high-impact-unreceipted"
    if tags & PROTOCOL_TAGS or sid.startswith(PROTOCOL_PREFIXES):
        return "B-protocol-unreceipted"
    return "C-background-unreceipted"


def source_byte_priority_sort_key(row: dict[str, Any], *, has_receipt: bool = False) -> tuple[str, str]:
    """Small shared sort key for policy smoke tests and helper surfaces."""

    return (source_byte_priority_tier(row, has_receipt=has_receipt), str(row.get("id") or ""))
