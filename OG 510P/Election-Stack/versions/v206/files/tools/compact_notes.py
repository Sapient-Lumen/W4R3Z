#!/usr/bin/env python3
"""tools/compact_notes.py

Parse + canonicalize the bounded compact request-context notation used in publishable artifacts:

  req[...] vary[...] age[...]

Design constraints:
- stdlib-only
- evidence-safe: extracts only the compact tokens (ignores other note content)
- canonicalization is for comparison/display (not itself an evidence requirement)
- conservative normalization: known keys are coerced toward coarse, publishable-friendly values

This module exists to reduce drift between tools that need to:
- extract request-context hints from `observations[].notes`
- compare/diff parity snapshots and liveness beacons

See:
- docs/224.2a (usage)
- docs/232 (syntax + normalization contract + test vectors)
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple

try:
    from tools.publication_policy import REQ_CACHE_VALUES, REQ_COOKIE_VALUES, REQ_RESOLVER_VALUES
except Exception:
    try:
        from publication_policy import REQ_CACHE_VALUES, REQ_COOKIE_VALUES, REQ_RESOLVER_VALUES
    except Exception:
        # Fallback for standalone use; keep conservative defaults.
        REQ_CACHE_VALUES = {"none", "no-cache", "force-refresh"}
        REQ_COOKIE_VALUES = {"none", "present_redacted"}
        REQ_RESOLVER_VALUES = {"system_resolver", "public_resolver", "pinned_resolver"}


# Extract compact tokens anywhere in a notes string.
_CONTEXT_RE = re.compile(r"(req\[[^\]]*\]|vary\[[^\]]*\]|age\[[^\]]*\])")

# Canonical key order for req[] compact notes.
_REQ_KEY_ORDER = ["ua", "lang", "cache", "cookie", "geo", "asn", "resolver"]

# Conservative header-name token pattern (tight, publishable-friendly).
# Note: RFC 9110 `token` allows more characters; we keep this deliberately narrower.
_RE_VARY_FIELD = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]*$")

_REQ_SANITIZE_RE = re.compile(r"[\[\];\r\n\t]")


def _norm_str(v: Any) -> str:
    return str(v or "").strip()


def _sanitize_value(v: str, maxlen: int = 64) -> str:
    """Sanitize a compact-note value to avoid delimiter injection / accidental bloat."""

    s = _norm_str(v)
    if not s:
        return ""
    s = _REQ_SANITIZE_RE.sub("_", s)
    s = re.sub(r"\s+", "_", s)
    return s[:maxlen]


def _normalize_lang(v: str) -> str:
    """Normalize Accept-Language hint to a primary BCP47-ish tag (no q-weights).

    This is a *hint*, not a verifier requirement; keep it coarse and publishable.
    """

    s = _norm_str(v)
    if not s:
        return ""
    if s.lower() in {"none", "unknown"}:
        return "none"

    # Keep only the first language-range and drop parameters.
    s = s.split(",", 1)[0].strip()
    s = s.split(";", 1)[0].strip()
    s = re.sub(r"\s+", "", s)

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


def _normalize_cache(v: str) -> str:
    s = _norm_str(v).lower().replace("_", "-")
    if not s or s in {"unknown"}:
        return ""
    if s in {"default", "normal"}:
        s = "none"
    if s in {"nocache", "no-cache"}:
        s = "no-cache"
    if s in {"force", "refresh", "force-refresh"}:
        s = "force-refresh"
    return s


def _normalize_cookie(v: str) -> str:
    s = _norm_str(v).lower()
    if not s or s in {"unknown"}:
        return ""
    if s not in REQ_COOKIE_VALUES:
        return "present_redacted"
    return s


def _normalize_resolver(v: str) -> str:
    s = _norm_str(v).lower().replace("-", "_")
    if not s or s in {"unknown"}:
        return ""
    if s in {"system", "system_resolver"}:
        return "system_resolver"
    if s in {"public", "public_resolver"}:
        return "public_resolver"
    if s in {"pinned", "pinned_resolver"}:
        return "pinned_resolver"
    return s


def _normalize_asn(v: str) -> str:
    s = _norm_str(v)
    if not s:
        return ""
    if s.lower().startswith("asn="):
        s = s.split("=", 1)[1].strip()
    return s if re.fullmatch(r"\d{1,10}", s) else ""


def _normalize_geo(v: str) -> str:
    """Best-effort canonicalization for coarse geo hints."""

    s = _norm_str(v)
    if not s or s.lower() in {"unknown", "none"}:
        return ""
    s0 = re.sub(r"\s+", "", s)

    # Common shorthands.
    if re.fullmatch(r"[A-Za-z]{2}", s0):
        return f"country={s0.upper()}"

    if s0.lower().startswith("country="):
        cc = s0.split("=", 1)[1]
        if re.fullmatch(r"[A-Za-z]{2}", cc):
            return f"country={cc.upper()}"
        return s0

    if s0.lower().startswith("region="):
        rv = s0.split("=", 1)[1]
        if re.fullmatch(r"[A-Za-z]{2}-[A-Za-z0-9]{1,3}", rv):
            left, right = rv.split("-", 1)
            return f"region={left.upper()}-{right.upper()}"
        return s0

    return s0


def parse_req_token(tok: str) -> Dict[str, str]:
    """Parse a `req[...]` token into a kv map (with conservative normalization)."""

    out: Dict[str, str] = {}
    s = _norm_str(tok)
    if not s.startswith("req[") or not s.endswith("]"):
        return out
    inner = s[len("req[") : -1].strip()
    if not inner:
        return out
    for part in inner.split(";"):
        part = part.strip()
        if not part or "=" not in part:
            continue
        k, v = part.split("=", 1)
        k = _norm_str(k).lower()
        v = _norm_str(v)
        if not k or v == "":
            continue
        out[k] = v

    # Coerce known keys toward publishable-friendly forms.
    if "ua" in out:
        out["ua"] = _sanitize_value(out["ua"], 32)

    if "lang" in out:
        lang = _normalize_lang(out["lang"])
        out["lang"] = _sanitize_value(lang or out["lang"], 32)

    if "cache" in out:
        cache = _normalize_cache(out["cache"])
        # Keep unknown values (sanitized) for diffs, but prefer canonical spellings.
        out["cache"] = _sanitize_value(cache or out["cache"], 24)

    if "cookie" in out:
        cookie = _normalize_cookie(out["cookie"])
        out["cookie"] = _sanitize_value(cookie or out["cookie"], 24)

    if "geo" in out:
        geo = _normalize_geo(out["geo"])
        out["geo"] = _sanitize_value(geo or out["geo"], 32)

    if "asn" in out:
        asn = _normalize_asn(out["asn"])
        if asn:
            out["asn"] = _sanitize_value(asn, 20)
        else:
            out.pop("asn", None)

    if "resolver" in out:
        rh = _normalize_resolver(out["resolver"])
        out["resolver"] = _sanitize_value(rh or out["resolver"], 32)

    # Sanitize unknown keys to keep canonicalization bounded/publishable.
    for k in list(out.keys()):
        if k not in _REQ_KEY_ORDER:
            out[k] = _sanitize_value(out[k], 64)
            if out[k] == "":
                out.pop(k, None)

    # Drop empty values post-sanitize.
    for k in list(out.keys()):
        if out.get(k, "") == "":
            out.pop(k, None)

    return out


def canonicalize_req(req: Dict[str, str]) -> str:
    """Return a canonical `req[...]` token for a req kv map."""

    if not req:
        return ""

    keys = [k for k in _REQ_KEY_ORDER if k in req]
    keys += sorted([k for k in req.keys() if k not in _REQ_KEY_ORDER])
    kv = [f"{k}={req.get(k,'')}" for k in keys if req.get(k, "") != ""]
    return ("req[" + ";".join(kv) + "]") if kv else ""


def canonicalize_vary(vary: str) -> str:
    """Canonicalize a `Vary` hint.

    - lower-case
    - split on commas
    - remove whitespace
    - dedupe + sort (order is not evidence-bearing for our use)

    If a token does not match the conservative field-name pattern, fall back to a
    whitespace-stripped, lower-cased string (keeps comparisons stable without claiming validity).
    """

    s = _norm_str(vary)
    if not s:
        return ""

    # Strip whitespace and normalize case.
    s0 = re.sub(r"\s+", "", s).strip()
    if not s0:
        return ""

    parts = [p.lower() for p in s0.split(",") if p]
    if not parts:
        return ""

    if all(_RE_VARY_FIELD.fullmatch(p) for p in parts):
        return ",".join(sorted(set(parts)))

    return ",".join(parts)


def canonicalize_age(age: str) -> str:
    """Canonicalize an `Age` hint to integer seconds (string) when possible."""

    s = _norm_str(age)
    if not s:
        return ""
    try:
        return str(int(s.split(",", 1)[0].strip()))
    except Exception:
        return _sanitize_value(s, 16)


def canonicalize_context(req: Dict[str, str], vary: str, age: str) -> str:
    parts: List[str] = []

    r = canonicalize_req(req)
    if r:
        parts.append(r)

    v = canonicalize_vary(vary)
    if v:
        parts.append(f"vary[{v}]")

    a = canonicalize_age(age)
    if a:
        parts.append(f"age[{a}]")

    return " ".join(parts).strip()


def extract_compact_context(notes: Any) -> Tuple[str, Dict[str, str], str, str]:
    """Return (canonical_context, req_dict, vary, age) extracted from notes.

    If multiple tokens appear, the last occurrence of each token type wins.
    """

    s = _norm_str(notes)
    if not s:
        return "", {}, "", ""

    toks = _CONTEXT_RE.findall(s)
    req: Dict[str, str] = {}
    vary = ""
    age = ""

    for t in toks:
        if t.startswith("req["):
            req = parse_req_token(t)
        elif t.startswith("vary[") and t.endswith("]"):
            vary = t[len("vary[") : -1]
        elif t.startswith("age[") and t.endswith("]"):
            age = t[len("age[") : -1]

    canon = canonicalize_context(req, vary, age)
    return canon, req, vary, age


def diff_req(a: Dict[str, str], b: Dict[str, str]) -> List[Dict[str, str]]:
    """Return a tight per-key diff list for req kv maps."""

    out: List[Dict[str, str]] = []
    keys = sorted(set(a.keys()) | set(b.keys()))
    for k in keys:
        va = a.get(k, "")
        vb = b.get(k, "")
        if va != vb:
            out.append({"k": k, "a": va, "b": vb})
    return out
