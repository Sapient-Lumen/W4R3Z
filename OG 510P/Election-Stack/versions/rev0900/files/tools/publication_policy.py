#!/usr/bin/env python3
"""tools/publication_policy.py

Centralized, *bounded* publication hygiene constants.

Why this exists:
The archive has multiple operator helpers that need to agree on what is safe to
publish (e.g., which freshness headers are permissible in a public artifact).
Duplicating allowlists across tools is a drift risk.

Design goals:
- stdlib-only
- small surface area
- safe-by-default

This module is intentionally not a "policy engine"; it is a tiny shared
constants bundle used by tools like `public_artifact_lint.py` and the bounded
HTTP capture helpers.
"""

from __future__ import annotations

# Keep tight: these are the only observation header keys encouraged for
# publication across cache/freshness disputes.
SAFE_FRESHNESS_HEADER_KEYS = {
    "etag",
    "cache_control",
    "last_modified",
    "age_seconds",
}

# Disallowed keys that commonly embed bodies/captures/secrets.
# Note: this is a *heuristic* guardrail; other checks (e.g., string-length bounds)
# still apply.
DISALLOWED_KEYS_EXACT = {
    # Raw captures / bodies.
    "raw_capture",
    "raw_http_capture",
    "raw_response",
    "response_body",
    "raw_body",
    "body_b64",
    "body_base64",
    "payload_b64",
    "payload_base64",
    "html",
    "full_text",
    # Secrets.
    "private_key",
    "private_key_pem",
    "secret",
    "api_key",
}

# Default maximum string length allowed in publishable packets.
DEFAULT_MAX_STRING = 8192

# Request-context compact notes (docs/224.2a) are intentionally bounded.
# These small allowlists help tools/lints stay aligned while the notation evolves.
REQ_KV_KEYS = {"ua", "lang", "cache", "cookie", "geo", "asn", "resolver"}
REQ_COOKIE_VALUES = {"none", "present_redacted"}
REQ_CACHE_VALUES = {"none", "no-cache", "force-refresh"}
REQ_RESOLVER_VALUES = {"system_resolver", "public_resolver", "pinned_resolver"}

# Patterns (used only for lint/warn): keep conservative.
REQ_LANG_PATTERN = r"^[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$"  # primary BCP47 tag (no q-weights)
REQ_COUNTRY_PATTERN = r"^country=[A-Z]{2}$"  # ISO 3166-1 alpha-2
REQ_REGION_PATTERN = r"^region=[A-Z]{2}-[A-Z0-9]{1,3}$"  # ISO 3166-2 (coarse)


def is_safe_freshness_header_key(k: str) -> bool:
    return str(k or "").strip().lower() in SAFE_FRESHNESS_HEADER_KEYS


def is_allowed_req_cookie(v: str) -> bool:
    return str(v or "").strip().lower() in REQ_COOKIE_VALUES


def is_allowed_req_cache(v: str) -> bool:
    return str(v or "").strip().lower() in REQ_CACHE_VALUES


def is_allowed_req_resolver(v: str) -> bool:
    return str(v or "").strip().lower() in REQ_RESOLVER_VALUES
