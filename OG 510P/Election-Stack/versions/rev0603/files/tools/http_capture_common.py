#!/usr/bin/env python3
"""tools/http_capture_common.py

Shared helpers for parsing bounded HTTP response captures.

Design constraints:
- stdlib-only
- evidence-minimizing: callers typically hash bodies and extract only small header subsets
- robust to common capture formats (`curl -i`, `wget -S`, proxies, redirects)

The core function, `split_last_http_response`, selects the *last* response block in a
concatenated capture (redirect chains, 100-continue), and returns:
  (status_code | None, headers: dict[str,str], body: bytes)

This module is internal glue used by operator helpers (e.g.,
`http_capture_to_observation.py`, `http_capture_to_parity_observation.py`).
"""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Tuple

try:
    from tools.publication_policy import (
        SAFE_FRESHNESS_HEADER_KEYS,
        REQ_CACHE_VALUES,
        REQ_COOKIE_VALUES,
        REQ_RESOLVER_VALUES,
    )
except Exception:
    from publication_policy import SAFE_FRESHNESS_HEADER_KEYS, REQ_CACHE_VALUES, REQ_COOKIE_VALUES, REQ_RESOLVER_VALUES


# Match common status lines: HTTP/1.1 200 OK, HTTP/2 200, HTTP/2.0 200, HTTP/3 200
# Note: some capture tools indent the status line (e.g., `wget -S`), so callers
# typically `.strip()` the line before matching.
STATUS_RE = re.compile(rb"^HTTP/(?:1\.\d|2(?:\.\d)?|3)\s+(\d{3})\b")


def sha256_hex(b: bytes) -> str:
    return "sha256:" + hashlib.sha256(b).hexdigest()


def iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def split_last_http_response(raw: bytes) -> Tuple[int | None, Dict[str, str], bytes]:
    """Return (status_code, headers, body) for the last HTTP response in a raw capture.

    - Supports concatenated response blocks (redirect chains, 100-continue).
    - Accepts CRLF or LF line endings.
    - If no plausible HTTP status line is found, returns (None, {}, raw).

    Note: This is intentionally *heuristic* (captures are not a strict wire format).
    """

    # Candidate status-line offsets (multiline: ^ matches after \n).
    # Some capture tools indent the status line; accept leading spaces/tabs.
    offsets = [m.start() for m in re.finditer(rb"(?m)^[ \t]*HTTP/", raw)]
    if not offsets:
        return None, {}, raw

    # Walk candidates from the end until a status line matches.
    start = None
    for off in reversed(offsets):
        chunk = raw[off:]
        first = chunk.splitlines()[0].strip() if chunk else b""
        if STATUS_RE.match(first):
            start = off
            break

    if start is None:
        return None, {}, raw

    chunk = raw[start:]

    # Header/body split (prefer CRLFCRLF, fall back to LFLF).
    sep = chunk.find(b"\r\n\r\n")
    if sep >= 0:
        header_blob = chunk[:sep]
        body = chunk[sep + 4 :]
        lines = header_blob.split(b"\r\n")
    else:
        sep = chunk.find(b"\n\n")
        if sep >= 0:
            header_blob = chunk[:sep]
            body = chunk[sep + 2 :]
            lines = header_blob.split(b"\n")
        else:
            # No clear separator; treat all as headers.
            lines = chunk.splitlines()
            body = b""

    status_code: int | None = None
    if lines:
        m = STATUS_RE.match(lines[0].strip())
        if m:
            try:
                status_code = int(m.group(1).decode("ascii", "ignore"))
            except Exception:
                status_code = None

    headers: Dict[str, str] = {}
    for ln in lines[1:]:
        if not ln.strip() or b":" not in ln:
            continue
        k, v = ln.split(b":", 1)
        key = k.decode("utf-8", "ignore").strip().lower()
        val = v.decode("utf-8", "ignore").strip()
        if key in headers:
            headers[key] = headers[key] + ", " + val
        else:
            headers[key] = val

    return status_code, headers, body


def load_pair(headers_path: Path, body_path: Path) -> Tuple[int | None, Dict[str, str], bytes]:
    hb = headers_path.read_bytes()
    status, headers, _ = split_last_http_response(hb)
    body = body_path.read_bytes()
    return status, headers, body


def get_header(headers: Dict[str, str], name: str) -> str:
    return str(headers.get(name.lower()) or "").strip()


def safe_freshness_headers(h: Dict[str, str]) -> Dict[str, object]:
    """Extract a deliberately small, evidence-safe header subset."""

    out: Dict[str, object] = {}

    etag = get_header(h, "etag")
    if etag:
        out["etag"] = etag

    cc = get_header(h, "cache-control")
    if cc:
        out["cache_control"] = cc

    lm = get_header(h, "last-modified")
    if lm:
        out["last_modified"] = lm

    age = get_header(h, "age")
    if age:
        try:
            out["age_seconds"] = int(age.split(",", 1)[0].strip())
        except Exception:
            pass

    # If the allowlist evolves, ensure we don't accidentally drift.
    # (We keep this module internal, but it's still useful as a sanity check.)
    for k in list(out.keys()):
        if str(k) not in SAFE_FRESHNESS_HEADER_KEYS:
            out.pop(k, None)

    return out


_REQ_SANITIZE_RE = re.compile(r"[\[\];\r\n\t]")


def _sanitize_note_value(v: str, maxlen: int = 64) -> str:
    s = str(v or "").strip()
    if not s:
        return ""
    # Prevent delimiter/structure injection into compact notes.
    s = _REQ_SANITIZE_RE.sub("_", s)
    s = re.sub(r"\s+", "_", s)
    return s[:maxlen]


def _normalize_accept_language(v: str) -> str:
    """Normalize Accept-Language hint to a primary BCP47 tag (no q-weights).

    Examples:
      - "en-US,en;q=0.9" -> "en-US"
      - " none " -> "none"

    This is a *hint*, not a verifier requirement; keep it coarse.
    """

    s = str(v or "").strip()
    if not s:
        return ""
    if s.lower() in {"none", "unknown"}:
        return "none"

    # Keep only the first language-range and drop parameters.
    s = s.split(",", 1)[0].strip()
    s = s.split(";", 1)[0].strip()
    s = re.sub(r"\s+", "", s)

    # Best-effort canonical casing: language lower, region upper.
    parts = [p for p in s.split("-") if p]
    if not parts:
        return ""
    parts[0] = parts[0].lower()
    for i in range(1, len(parts)):
        if len(parts[i]) == 2:
            parts[i] = parts[i].upper()
        elif len(parts[i]) == 4:
            parts[i] = parts[i].title()
    return "-".join(parts)


def _normalize_cache_bypass(v: str) -> str:
    s = str(v or "").strip().lower().replace("_", "-")
    if not s or s in {"unknown"}:
        return ""
    if s in {"default", "normal"}:
        s = "none"
    if s in {"nocache", "no-cache"}:
        s = "no-cache"
    if s in {"force", "refresh", "force-refresh"}:
        s = "force-refresh"
    return s


def _normalize_resolver_hint(v: str) -> str:
    s = str(v or "").strip().lower().replace("-", "_")
    if not s or s in {"unknown"}:
        return ""
    if s in {"system", "system_resolver"}:
        return "system_resolver"
    if s in {"public", "public_resolver"}:
        return "public_resolver"
    if s in {"pinned", "pinned_resolver"}:
        return "pinned_resolver"
    return s


def _normalize_geo_hint(v: str) -> str:
    s = str(v or "").strip()
    if not s:
        return ""
    if s.lower() in {"unknown", "none"}:
        return ""

    s0 = re.sub(r"\s+", "", s)

    # Best-effort canonicalization for common forms.
    if re.fullmatch(r"[A-Za-z]{2}", s0):
        return f"country={s0.upper()}"
    if s0.lower().startswith("country="):
        cc = s0.split("=", 1)[1]
        if re.fullmatch(r"[A-Za-z]{2}", cc):
            return f"country={cc.upper()}"
        return s0
    if s0.lower().startswith("region="):
        rv = s0.split("=", 1)[1]
        # Prefer ISO 3166-2 style: US-CA.
        if re.fullmatch(r"[A-Za-z]{2}-[A-Za-z0-9]{1,3}", rv):
            left, right = rv.split("-", 1)
            return f"region={left.upper()}-{right.upper()}"
        return s0

    return s0


def _normalize_asn_hint(v: str) -> str:
    s = str(v or "").strip()
    if not s:
        return ""
    if s.lower() in {"unknown", "none"}:
        return ""
    if s.lower().startswith("asn="):
        s = s.split("=", 1)[1].strip()
    # Only allow digits in publishable hints.
    return s if re.fullmatch(r"\d{1,10}", s) else ""

def _normalize_vary_hint(v: str) -> str:
    """Normalize a Vary hint to a stable, comparable form.

    - split on commas
    - strip whitespace
    - lower-case
    - dedupe + sort (order is not evidence-bearing for our use)
    """

    s = str(v or "").strip()
    if not s:
        return ""
    s0 = re.sub(r"\s+", "", s)
    if not s0:
        return ""
    toks = [t.lower() for t in s0.split(",") if t]
    if not toks:
        return ""
    return ",".join(sorted(set(toks)))



def build_request_context_note(
    *,
    ua_class: str = "",
    accept_language: str = "",
    cache_bypass: str = "",
    cookies: str = "",
    geo_hint: str = "",
    asn_hint: str = "",
    resolver_hint: str = "",
    vary: str = "",
    age: str = "",
) -> str:
    """Build a compact, publishable notes string for request-context / variance hints.

    Format (bounded):
      req[ua=...;lang=...;cache=...;cookie=...;geo=...;asn=...;resolver=...] vary[...] age[...]

    Callers SHOULD pass coarse, non-identifying values only.
    This function intentionally sanitizes delimiters to avoid leaking headers/tokens by accident.
    """

    parts: list[str] = []

    kv: list[str] = []

    if ua_class.strip():
        kv.append(f"ua={_sanitize_note_value(ua_class, 32)}")

    al = _normalize_accept_language(accept_language)
    if al:
        kv.append(f"lang={_sanitize_note_value(al, 32)}")

    cb = _normalize_cache_bypass(cache_bypass)
    if cb:
        # Keep the canonical spellings when possible.
        cb0 = cb if cb in REQ_CACHE_VALUES else cb
        kv.append(f"cache={_sanitize_note_value(cb0, 24)}")

    if cookies.strip():
        c = str(cookies).strip().lower()
        # Safety: never allow raw cookie values to slip into publishable notes.
        if c not in REQ_COOKIE_VALUES:
            c = "present_redacted"
        kv.append(f"cookie={_sanitize_note_value(c, 24)}")

    gh = _normalize_geo_hint(geo_hint)
    if gh:
        kv.append(f"geo={_sanitize_note_value(gh, 32)}")

    ah = _normalize_asn_hint(asn_hint)
    if ah:
        kv.append(f"asn={_sanitize_note_value(ah, 20)}")

    rh = _normalize_resolver_hint(resolver_hint)
    if rh:
        rh0 = rh if rh in REQ_RESOLVER_VALUES else rh
        kv.append(f"resolver={_sanitize_note_value(rh0, 32)}")

    if kv:
        parts.append("req[" + ";".join(kv) + "]")

    if vary.strip():
        v0 = _normalize_vary_hint(str(vary))
        v = _sanitize_note_value(v0, 96)
        if v:
            parts.append(f"vary[{v}]")

    if age.strip():
        a_raw = str(age).strip()
        # Age is defined as seconds; keep the compact note deterministic.
        try:
            a_raw = str(int(a_raw.split(",", 1)[0].strip()))
        except Exception:
            pass
        a = _sanitize_note_value(a_raw, 16)
        if a:
            parts.append(f"age[{a}]")

    return " ".join(parts).strip()
