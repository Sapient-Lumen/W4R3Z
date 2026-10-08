#!/usr/bin/env python3
"""tools/public_artifact_lint.py

Lightweight, evidence-safe linter for *publishable* artifacts.

Rationale:
The archive encourages publishing small, hash-forward artifacts (cards, parity snapshots,
beacons) while avoiding large bodies, raw captures, secrets, or unbounded headers.

This tool provides a conservative drift firewall that can be run on an evidence packet
(or any packet-shaped directory) before publication.

It is intentionally:
- stdlib-only
- conservative (prefers false negatives over false positives)
- bounded (does not print bodies)

What it checks (tight + salient):
- no obviously disallowed fields that commonly embed bodies/captures/secrets
- bounded string lengths
- bounded freshness headers (only the allowlist in docs/205/210)
- token/private-key markers and obvious secret patterns (conservative)
- WARN on likely PII literals (IP addresses, email addresses, phone numbers, lat/long coordinates)
- surface anomaly-note codes that begin with `surface_` must be in the registry

Exit codes:
- 0: no FAIL findings
- 2: one or more FAIL findings

Output:
- default: human readable summary
- --json: machine readable
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

try:
    from tools.surface_anomaly_codes import is_known as is_known_surface_code
except Exception:
    from surface_anomaly_codes import is_known as is_known_surface_code

try:
    from tools.publication_policy import (
        DEFAULT_MAX_STRING,
        DISALLOWED_KEYS_EXACT,
        SAFE_FRESHNESS_HEADER_KEYS,
        REQ_CACHE_VALUES,
        REQ_COOKIE_VALUES,
        REQ_RESOLVER_VALUES,
        REQ_LANG_PATTERN,
        REQ_COUNTRY_PATTERN,
        REQ_REGION_PATTERN,
    )
except Exception:
    from publication_policy import (
        DEFAULT_MAX_STRING,
        DISALLOWED_KEYS_EXACT,
        SAFE_FRESHNESS_HEADER_KEYS,
        REQ_CACHE_VALUES,
        REQ_COOKIE_VALUES,
        REQ_RESOLVER_VALUES,
        REQ_LANG_PATTERN,
        REQ_COUNTRY_PATTERN,
        REQ_REGION_PATTERN,
    )


ROOT = Path(__file__).resolve().parents[1]

# Conservative red-flag patterns.
RE_PRIVATE_KEY = re.compile(r"BEGIN\s+(?:(?:RSA|EC|OPENSSH)\s+)?PRIVATE\s+KEY", re.IGNORECASE)

# Common secret token markers (conservative; prefer false negatives over false positives).
RE_AWS_ACCESS_KEY_ID = re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")
RE_GITHUB_TOKEN = re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}\b|\bgithub_pat_[A-Za-z0-9_]{20,}\b")
RE_SLACK_TOKEN = re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")
RE_GENERIC_TOKEN_WORD = re.compile(r"\b(?:api[_-]?key|secret[_-]?key|access[_-]?token|refresh[_-]?token)\b", re.IGNORECASE)

# Additional high-signal token markers (conservative).
RE_GOOGLE_API_KEY = re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b")
RE_STRIPE_LIVE_KEY = re.compile(r"\bsk_live_[0-9a-zA-Z]{20,}\b")

# Likely-PII literals (WARN only; sometimes publishing a resolver IP is acceptable, but it is rarely necessary).
RE_EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
RE_IPV6 = re.compile(r"\b(?:[0-9A-F]{0,4}:){2,7}[0-9A-F]{0,4}\b", re.IGNORECASE)

# Conservative phone/coordinate literals (WARN only; prefer coarse hints).
RE_PHONE = re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")
RE_LATLON = re.compile(r"\b[-+]?(?:[0-8]?\d(?:\.\d+)?|90(?:\.0+)?)\s*,\s*[-+]?(?:1[0-7]\d(?:\.\d+)?|\d{1,2}(?:\.\d+)?|180(?:\.0+)?)\b")

# Request-context compact notes (docs/224.2a). Keep publication-safe.
REQ_NOTE_RE = re.compile(r"req\[([^\]]*)\]")
VARY_NOTE_RE = re.compile(r"vary\[([^\]]*)\]")
AGE_NOTE_RE = re.compile(r"age\[([^\]]*)\]")
RE_HEADER_LEAK = re.compile(r"(?:^|\b)(authorization:|cookie:|set-cookie:|bearer\s+|x-api-key:)", re.IGNORECASE)

RE_IP = re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b")
RE_LANG = re.compile(REQ_LANG_PATTERN)
RE_COUNTRY = re.compile(REQ_COUNTRY_PATTERN)
RE_REGION = re.compile(REQ_REGION_PATTERN)

try:
    from tools.compact_notes import canonicalize_vary as _canon_vary, canonicalize_age as _canon_age
except Exception:
    from compact_notes import canonicalize_vary as _canon_vary, canonicalize_age as _canon_age

# Text surfaces to scan in packet-shaped directories.
# Rationale: publishable bundles often ship README/capture-note/redaction-log markdown
# outside JSON objects; scan these small files for the same obvious leak patterns.
TEXT_SCAN_MAX_BYTES = 64 * 1024

# Optional suppression directives for WARN-only findings.
# These live in packet root `redaction-log.md` so publication exceptions are explicit.
RE_LINT_ALLOW = re.compile(r"^\s*lint-allow:\s*([A-Za-z0-9_]+)\b", re.IGNORECASE | re.MULTILINE)

# Reserved / documentation identifiers (warn suppression via classification, not directives).
# Rationale: these are intentionally non-identifying placeholders for examples/tests.
_DOC_EMAIL_DOMAINS = {"example.com", "example.org", "example.net", "invalid"}

def _line_for_regex(text: str, regex: re.Pattern[str]) -> int:
    m = regex.search(text)
    if not m:
        return 0
    return text.count('\n', 0, m.start()) + 1


def _load_warn_suppressions(packet_dir: Path) -> set[str]:
    """Load WARN suppression directives from `redaction-log.md`.

    Format (one per line, anywhere in the file):
      - lint-allow: <code>

    Philosophy:
      - suppressions are WARN-only (FAIL is never suppressed)
      - suppressions are packet-scoped (no per-field complexity)
      - suppressions must be explicit and reviewable
    """

    p = packet_dir / "redaction-log.md"
    if not p.exists() or not p.is_file():
        return set()
    try:
        text = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return set()
    out: set[str] = set()
    for m in RE_LINT_ALLOW.finditer(text):
        code = str(m.group(1) or "").strip()
        if code:
            out.add(code)
    return out


def _is_doc_ipv4(ip: str) -> bool:
    """Return True if ip is a non-identifying documentation placeholder.

    - RFC 5737: 192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24
    - Common local placeholders: 127.0.0.1, 0.0.0.0
    """

    s = (ip or "").strip()
    if s in {"127.0.0.1", "0.0.0.0"}:
        return True
    try:
        a, b, c, d = [int(x) for x in s.split(".")]
        if not all(0 <= x <= 255 for x in [a, b, c, d]):
            return False
    except Exception:
        return False
    if (a, b, c) == (192, 0, 2):
        return True
    if (a, b, c) == (198, 51, 100):
        return True
    if (a, b, c) == (203, 0, 113):
        return True
    return False


def _is_doc_ipv6(tok: str) -> bool:
    """Return True for documentation IPv6 tokens (RFC 3849) or loopback."""

    s = (tok or "").strip().lower()
    if s in {"::1"}:
        return True

    # RFC 3849 documentation prefix.
    if s.startswith("2001:db8:") or s.startswith("2001:db8::"):
        return True

    # RFC 9637 expands the documentation space with 3fff::/20.
    if s.startswith("3fff:"):
        rest = s[len("3fff:") :]
        if rest.startswith(":"):
            return True  # 3fff::...
        hextet = rest.split(":", 1)[0]
        try:
            if hextet and int(hextet, 16) <= 0x0FFF:
                return True
        except Exception:
            pass

    return False


def _contains_non_doc_email(text: str) -> bool:
    for m in RE_EMAIL.finditer(text or ""):
        addr = m.group(0)
        dom = addr.split("@", 1)[-1].strip().lower()
        if dom and dom not in _DOC_EMAIL_DOMAINS:
            return True
    return False


def _line_for_non_doc_email(text: str) -> int:
    for m in RE_EMAIL.finditer(text or ""):
        addr = m.group(0)
        dom = addr.split("@", 1)[-1].strip().lower()
        if dom and dom not in _DOC_EMAIL_DOMAINS:
            return text.count("\n", 0, m.start()) + 1
    return 0


def _contains_non_doc_ip(text: str) -> bool:
    # IPv4: ignore documentation ranges.
    for m in RE_IP.finditer(text or ""):
        if not _is_doc_ipv4(m.group(0)):
            return True
    # IPv6: ignore documentation prefix.
    for m in RE_IPV6.finditer(text or ""):
        if not _is_doc_ipv6(m.group(0)):
            return True
    return False


def _line_for_non_doc_ip(text: str) -> int:
    for m in RE_IP.finditer(text or ""):
        if not _is_doc_ipv4(m.group(0)):
            return text.count("\n", 0, m.start()) + 1
    for m in RE_IPV6.finditer(text or ""):
        if not _is_doc_ipv6(m.group(0)):
            return text.count("\n", 0, m.start()) + 1
    return 0



@dataclass
class Finding:
    severity: str  # FAIL | WARN
    code: str
    file: str
    path: str
    message: str


# Tight, operator-facing explanations for common findings.
# This exists to keep publication workflows fast without expanding docs.
CODE_EXPLAIN: dict[str, str] = {
    "lint_disallowed_key": "A disallowed key (often a body/capture/secret field) appears in a publishable object. Remove it or replace with a digest pointer (see docs/173, docs/189).",
    "lint_headers_key_disallowed": "Observation headers include keys outside the freshness allowlist (etag/cache_control/last_modified/age_seconds). Keep only bounded freshness metadata (docs/205, docs/210).",
    "lint_string_too_long": "A string exceeds the bounded publication limit. Replace large blobs with digests + citations; keep publishable artifacts small.",
    "lint_private_key_marker": "A private key marker was detected. This is catastrophic for a public archive—delete immediately (docs/189).",
    "lint_cloud_access_key_marker": "A cloud access key ID marker was detected. Treat as a secret leak; remove immediately (docs/189).",
    "lint_token_marker": "A likely API token marker was detected. Treat as a secret leak; remove immediately (docs/189).",
    "lint_req_header_leak": "Notes contain raw Authorization/Cookie/Set-Cookie/Bearer/X-Api-Key header markers. Publish only compact req[] hints (docs/224.2a) or digest-pinned captures (docs/223).",
    "lint_req_cookie_value": "req[] cookie must be none|present_redacted. Never publish cookie values (docs/224.2a, docs/189).",
    "lint_vary_noncanonical": "vary[] should be a canonical, bounded list of response Vary header names (lower-case, comma-separated, no spaces). Prefer tool-emitted forms (docs/224.2a).",
    "lint_vary_unbounded": "vary[] looks unbounded or overly long for a publishable hint. Keep only header names; omit if too large (docs/224.2a, docs/189).",
    "lint_age_nonint": "age[] should be integer seconds from the response Age header. Omit or normalize to an int (docs/224.2a).",
    "lint_unknown_surface_anomaly_code": "A surface_* anomaly code in notes is not in the registry. Use an existing code or add one via the registry process (scripts/gen_surface_anomaly_codes.py).",
    "lint_email_literal_present": "A non-example email address literal was detected (WARN). Prefer coarse/non-identifying examples; if publication requires it, justify in redaction-log.md with a lint-allow directive.",
    "lint_ip_literal_present": "A non-documentation IP literal was detected (WARN). Prefer coarse geo/asn/resolver classes; if crucial, justify in redaction-log.md with lint-allow.",
    "lint_phone_literal_present": "A phone-number-like literal was detected (WARN). Avoid publishing contact identifiers.",
    "lint_latlon_literal_present": "A coordinate literal was detected (WARN). Prefer coarse geo hints (country/region).",
    "lint_text_header_leak": "A packet text surface contains raw auth/cookie header markers. Remove or move to private raw capture bytes and pin by digest.",
    "lint_token_word_present": "A token/secret keyword appears in text (WARN). Usually harmless prose; double-check no secrets are embedded.",
    "lint_json_parse_failed": "A JSON file could not be parsed. Fix or remove the malformed file before publishing.",
}


def _iter_json_files(packet_dir: Path) -> Iterable[Path]:
    # Packet convention: objects/*.json and envelopes/*.json are the main surfaces,
    # but we scan all json under the packet dir to keep it simple.
    for p in packet_dir.rglob("*.json"):
        if p.is_file():
            yield p


def _iter_text_files(packet_dir: Path) -> Iterable[Path]:
    """Yield small text-ish packet surfaces.

    We intentionally avoid scanning content-addressed objects (objects/...) because
    those can contain pinned third-party bytes or large local artifacts.

    We scan:
    - packet root README.* and redaction-log.md
    - notes/**/*.md|txt
    """

    # Root-level small notes.
    for name in ["README.txt", "README.md", "redaction-log.md", "capture-note.md"]:
        p = packet_dir / name
        if p.exists() and p.is_file():
            yield p

    notes_dir = packet_dir / "notes"
    if notes_dir.exists() and notes_dir.is_dir():
        for p in notes_dir.rglob("*"):
            if not p.is_file():
                continue
            if p.suffix.lower() in {".md", ".txt"}:
                yield p


def _is_observation_headers_path(path: list[str]) -> bool:
    # Heuristic: ...observations.[i].headers
    if not path or path[-1] != "headers":
        return False
    return "observations" in path


def _path_str(path: list[str]) -> str:
    if not path:
        return "$"
    # Preserve [i] tokens already in keys when present.
    out: list[str] = ["$"]
    for tok in path:
        if tok.startswith("["):
            out.append(tok)
        else:
            out.append("." + tok)
    return "".join(out)


def _collect_surface_codes_from_notes(obj: Any) -> list[tuple[str, str]]:
    """Return list of (note, code) for note strings starting with surface_."""
    out: list[tuple[str, str]] = []

    def add_note(n: str) -> None:
        s = (n or "").strip()
        if not s.startswith("surface_"):
            return
        code = s.split(":", 1)[0].strip()
        out.append((s, code))

    # Notes appear in different shapes across objects.
    if isinstance(obj, str):
        add_note(obj)
    elif isinstance(obj, list):
        for x in obj:
            if isinstance(x, str):
                add_note(x)

    return out


def _iter_note_strings(v: Any) -> list[str]:
    if isinstance(v, str):
        return [v]
    if isinstance(v, list):
        return [x for x in v if isinstance(x, str)]
    return []


def _extract_req_kvs(note: str) -> dict[str, str]:
    """Parse `req[...]` compact notes into a kv map.

    This is deliberately small and forgiving; it exists to catch accidental leaks
    (e.g., cookie values) in publishable packets.
    """

    m = REQ_NOTE_RE.search(note or "")
    if not m:
        return {}

    inner = (m.group(1) or "").strip()
    if not inner:
        return {}

    kv: dict[str, str] = {}
    for part in inner.split(";"):
        part = part.strip()
        if not part or "=" not in part:
            continue
        k, v = part.split("=", 1)
        k = k.strip().lower()
        v = v.strip()
        if not k or not v:
            continue
        # Bounded keys only; ignore unknown keys so the notation can evolve.
        if k in {"ua", "lang", "cache", "cookie", "geo", "asn", "resolver"}:
            kv[k] = v
    return kv


def _ua_looks_full(val: str) -> bool:
    s = (val or "").lower()
    return any(tok in s for tok in ["mozilla", "applewebkit", "gecko", "chrome/", "safari/"])


def _lang_looks_full_header(val: str) -> bool:
    s = (val or "").lower()
    return any(tok in s for tok in [",", ";", "q="])


def _geo_looks_too_specific(val: str) -> bool:
    s = (val or "").lower()
    if any(tok in s for tok in ["lat", "lon", "lng", "ip="]):
        return True
    if RE_IP.search(val or ""):
        return True
    # Heuristic: long digit runs or decimal points often mean coordinates.
    if re.search(r"\d{3,}", s) and "." in s:
        return True
    return False


def lint_packet(packet_dir: Path, max_string: int) -> list[Finding]:
    findings: list[Finding] = []

    suppress_warn_codes = _load_warn_suppressions(packet_dir)

    for jf in _iter_json_files(packet_dir):
        rel = str(jf.relative_to(packet_dir))
        try:
            data = json.loads(jf.read_text(encoding="utf-8"))
        except Exception as e:
            findings.append(
                Finding(
                    severity="FAIL",
                    code="lint_json_parse_failed",
                    file=rel,
                    path="$",
                    message=f"JSON parse failed: {e}",
                )
            )
            continue

        kind = data.get("kind") if isinstance(data, dict) else None
        kind = str(kind) if isinstance(kind, str) else ""

        def walk(x: Any, path: list[str]) -> None:
            # Key-level checks.
            if isinstance(x, dict):
                for k, v in x.items():
                    key = str(k)
                    p2 = path + [key]

                    if key in DISALLOWED_KEYS_EXACT:
                        findings.append(
                            Finding(
                                severity="FAIL",
                                code="lint_disallowed_key",
                                file=rel,
                                path=_path_str(p2),
                                message=f"Disallowed key present: {key!r}",
                            )
                        )

                    if key == "headers" and isinstance(v, dict) and _is_observation_headers_path(p2):
                        extra = sorted(set(v.keys()) - SAFE_FRESHNESS_HEADER_KEYS)
                        if extra:
                            findings.append(
                                Finding(
                                    severity="FAIL",
                                    code="lint_headers_key_disallowed",
                                    file=rel,
                                    path=_path_str(p2),
                                    message=f"Observation headers include non-allowlisted keys: {extra}",
                                )
                            )

                    # Surface anomaly note codes: only for the two monitoring object kinds.
                    if (
                        key == "notes"
                        and kind in {"hfv.public.surface_parity_snapshot", "hfv.coverage.liveness_beacon"}
                        and "observations" in path
                    ):
                        for note, code in _collect_surface_codes_from_notes(v):
                            if not is_known_surface_code(code):
                                findings.append(
                                    Finding(
                                        severity="FAIL",
                                        code="lint_unknown_surface_anomaly_code",
                                        file=rel,
                                        path=_path_str(p2),
                                        message=f"Unknown surface anomaly code in notes: {code!r} (note={note!r})",
                                    )
                                )

                        # Request-context compact notes: catch obvious publication leaks.
                        for note_str in _iter_note_strings(v):
                            if RE_HEADER_LEAK.search(note_str or ""):
                                findings.append(
                                    Finding(
                                        severity="FAIL",
                                        code="lint_req_header_leak",
                                        file=rel,
                                        path=_path_str(p2),
                                        message="Notes contain a raw auth/cookie header marker (Authorization/Cookie/Set-Cookie/Bearer/X-Api-Key)",
                                    )
                                )

                            kv = _extract_req_kvs(note_str)

                            # Also lint vary[] / age[] tokens in notes (docs/224.2a).
                            for vm in VARY_NOTE_RE.finditer(note_str or ""):
                                raw_v = (vm.group(1) or "").strip()
                                if not raw_v:
                                    continue
                                canon_v = _canon_vary(raw_v)
                                if len(raw_v) > 96:
                                    findings.append(
                                        Finding(
                                            severity="WARN",
                                            code="lint_vary_unbounded",
                                            file=rel,
                                            path=_path_str(p2),
                                            message=f"vary[] looks long for a publishable hint (len={len(raw_v)}); prefer bounded header-name list",
                                        )
                                    )
                                raw_norm = re.sub(r"\s+", "", raw_v).lower()
                                if canon_v and raw_norm != canon_v:
                                    findings.append(
                                        Finding(
                                            severity="WARN",
                                            code="lint_vary_noncanonical",
                                            file=rel,
                                            path=_path_str(p2),
                                            message=f"vary[] is non-canonical; prefer vary[{canon_v}] (got {raw_v!r})",
                                        )
                                    )

                            for am in AGE_NOTE_RE.finditer(note_str or ""):
                                raw_a = (am.group(1) or "").strip()
                                if not raw_a:
                                    continue
                                canon_a = _canon_age(raw_a)
                                if not raw_a.isdigit() and not (canon_a and canon_a.isdigit()):
                                    findings.append(
                                        Finding(
                                            severity="WARN",
                                            code="lint_age_nonint",
                                            file=rel,
                                            path=_path_str(p2),
                                            message=f"age[] should be integer seconds (got {raw_a!r})",
                                        )
                                    )

                            if "cookie" in kv and kv["cookie"].lower() not in REQ_COOKIE_VALUES:
                                findings.append(
                                    Finding(
                                        severity="FAIL",
                                        code="lint_req_cookie_value",
                                        file=rel,
                                        path=_path_str(p2),
                                        message=f"req[] cookie must be none|present_redacted (got {kv['cookie']!r})",
                                    )
                                )

                            if "ua" in kv and _ua_looks_full(kv["ua"]):
                                findings.append(
                                    Finding(
                                        severity="WARN",
                                        code="lint_req_full_user_agent_suspected",
                                        file=rel,
                                        path=_path_str(p2),
                                        message=f"req[] ua value looks like a full UA string; prefer coarse ua_class (got {kv['ua']!r})",
                                    )
                                )

                            if "cache" in kv and kv["cache"].lower() not in REQ_CACHE_VALUES:
                                findings.append(
                                    Finding(
                                        severity="WARN",
                                        code="lint_req_cache_unrecognized",
                                        file=rel,
                                        path=_path_str(p2),
                                        message=f"req[] cache value is not in allowlist {sorted(REQ_CACHE_VALUES)} (got {kv['cache']!r})",
                                    )
                                )

                            if "resolver" in kv and kv["resolver"].lower() not in REQ_RESOLVER_VALUES:
                                findings.append(
                                    Finding(
                                        severity="WARN",
                                        code="lint_req_resolver_unrecognized",
                                        file=rel,
                                        path=_path_str(p2),
                                        message=f"req[] resolver value is not in allowlist {sorted(REQ_RESOLVER_VALUES)} (got {kv['resolver']!r})",
                                    )
                                )

                            if "lang" in kv:
                                lv = kv["lang"].strip()
                                if _lang_looks_full_header(lv):
                                    findings.append(
                                        Finding(
                                            severity="WARN",
                                            code="lint_req_lang_looks_unbounded",
                                            file=rel,
                                            path=_path_str(p2),
                                            message=f"req[] lang looks like a full Accept-Language header; prefer a single primary tag or 'none' (got {lv!r})",
                                        )
                                    )
                                if lv.lower() != "none" and not RE_LANG.fullmatch(lv):
                                    findings.append(
                                        Finding(
                                            severity="WARN",
                                            code="lint_req_lang_not_primary_tag",
                                            file=rel,
                                            path=_path_str(p2),
                                            message=f"req[] lang is not a primary BCP47 tag (got {lv!r})",
                                        )
                                    )

                            if "asn" in kv:
                                av = kv["asn"].strip()
                                if not re.fullmatch(r"\d{1,10}", av):
                                    findings.append(
                                        Finding(
                                            severity="WARN",
                                            code="lint_req_asn_not_digits",
                                            file=rel,
                                            path=_path_str(p2),
                                            message=f"req[] asn should be digits only (got {av!r})",
                                        )
                                    )

                            if "geo" in kv:
                                gv = kv["geo"].strip()
                                if _geo_looks_too_specific(gv):
                                    findings.append(
                                        Finding(
                                            severity="WARN",
                                            code="lint_req_geo_too_specific",
                                            file=rel,
                                            path=_path_str(p2),
                                            message=f"req[] geo looks too specific (coords/IP); keep to country/region only (got {gv!r})",
                                        )
                                    )
                                elif not (RE_COUNTRY.fullmatch(gv) or RE_REGION.fullmatch(gv)):
                                    findings.append(
                                        Finding(
                                            severity="WARN",
                                            code="lint_req_geo_noncanonical",
                                            file=rel,
                                            path=_path_str(p2),
                                            message=f"req[] geo is non-canonical; prefer country=XX or region=CC-SS (got {gv!r})",
                                        )
                                    )

                    walk(v, p2)

            elif isinstance(x, list):
                for i, v in enumerate(x):
                    walk(v, path + [f"[{i}]"])

            elif isinstance(x, str):
                if len(x) > max_string:
                    findings.append(
                        Finding(
                            severity="FAIL",
                            code="lint_string_too_long",
                            file=rel,
                            path=_path_str(path),
                            message=f"String length {len(x)} exceeds max_string={max_string}",
                        )
                    )
                if RE_PRIVATE_KEY.search(x):
                    findings.append(
                        Finding(
                            severity="FAIL",
                            code="lint_private_key_marker",
                            file=rel,
                            path=_path_str(path),
                            message="Private key marker detected in string value",
                        )
                    )
                # Conservative token/secret markers.
                if RE_AWS_ACCESS_KEY_ID.search(x):
                    findings.append(
                        Finding(
                            severity="FAIL",
                            code="lint_cloud_access_key_marker",
                            file=rel,
                            path=_path_str(path),
                            message="Cloud access key ID marker detected in string value",
                        )
                    )
                if RE_GOOGLE_API_KEY.search(x) or RE_STRIPE_LIVE_KEY.search(x):
                    findings.append(
                        Finding(
                            severity="FAIL",
                            code="lint_token_marker",
                            file=rel,
                            path=_path_str(path),
                            message="Likely API token marker detected in string value",
                        )
                    )
                if RE_GITHUB_TOKEN.search(x) or RE_SLACK_TOKEN.search(x):
                    findings.append(
                        Finding(
                            severity="FAIL",
                            code="lint_token_marker",
                            file=rel,
                            path=_path_str(path),
                            message="Likely API token marker detected in string value",
                        )
                    )
                # Weak-signal words are WARN-only; they are often harmless prose.
                if RE_GENERIC_TOKEN_WORD.search(x):
                    findings.append(
                        Finding(
                            severity="WARN",
                            code="lint_token_word_present",
                            file=rel,
                            path=_path_str(path),
                            message="Token/secret keyword present; verify no secrets are embedded",
                        )
                    )

                # Likely-PII literals (WARN only).
                if _contains_non_doc_email(x):
                    findings.append(
                        Finding(
                            severity="WARN",
                            code="lint_email_literal_present",
                            file=rel,
                            path=_path_str(path),
                            message="Email address literal detected; verify it is safe/necessary to publish",
                        )
                    )
                if _contains_non_doc_ip(x):
                    findings.append(
                        Finding(
                            severity="WARN",
                            code="lint_ip_literal_present",
                            file=rel,
                            path=_path_str(path),
                            message="IP address literal detected; prefer coarse geo/asn/resolver classes unless crucial",
                        )
                    )
                if RE_PHONE.search(x):
                    findings.append(
                        Finding(
                            severity="WARN",
                            code="lint_phone_literal_present",
                            file=rel,
                            path=_path_str(path),
                            message="Phone-number-like literal detected; avoid publishing identifying contact info",
                        )
                    )
                if RE_LATLON.search(x):
                    findings.append(
                        Finding(
                            severity="WARN",
                            code="lint_latlon_literal_present",
                            file=rel,
                            path=_path_str(path),
                            message="Lat/long coordinate literal detected; prefer coarse geo hints (country/region)",
                        )
                    )

        walk(data, [])

    # Scan small text surfaces (README/capture-notes/redaction logs) for obvious leaks.
    for tf in _iter_text_files(packet_dir):
        rel = str(tf.relative_to(packet_dir))
        try:
            sz = int(tf.stat().st_size)
        except Exception:
            sz = -1

        if sz >= 0 and sz > TEXT_SCAN_MAX_BYTES:
            findings.append(
                Finding(
                    severity="WARN",
                    code="lint_text_file_large",
                    file=rel,
                    path="$",
                    message=f"Text file size {sz} exceeds scan limit {TEXT_SCAN_MAX_BYTES}; verify it is safe to publish",
                )
            )
            # Still scan the prefix; size alone is not a leak.

        try:
            raw = tf.read_bytes()[:TEXT_SCAN_MAX_BYTES]
            text = raw.decode("utf-8", errors="ignore")
        except Exception as e:
            findings.append(
                Finding(
                    severity="WARN",
                    code="lint_text_read_failed",
                    file=rel,
                    path="$",
                    message=f"Could not read text file for linting: {e}",
                )
            )
            continue

        if RE_PRIVATE_KEY.search(text):
            findings.append(
                Finding(
                    severity="FAIL",
                    code="lint_private_key_marker",
                    file=rel,
                    path=f"line:{_line_for_regex(text, RE_PRIVATE_KEY)}",
                    message="Private key marker detected in text file",
                )
            )

        if RE_HEADER_LEAK.search(text):
            findings.append(
                Finding(
                    severity="FAIL",
                    code="lint_text_header_leak",
                    file=rel,
                    path=f"line:{_line_for_regex(text, RE_HEADER_LEAK)}",
                    message="Text file contains a raw auth/cookie header marker (Authorization/Cookie/Set-Cookie/Bearer/X-Api-Key)",
                )
            )

        # Conservative token/secret markers in text surfaces.
        if RE_AWS_ACCESS_KEY_ID.search(text):
            findings.append(
                Finding(
                    severity="FAIL",
                    code="lint_cloud_access_key_marker",
                    file=rel,
                    path=f"line:{_line_for_regex(text, RE_AWS_ACCESS_KEY_ID)}",
                    message="Cloud access key ID marker detected in text file",
                )
            )

        if RE_GOOGLE_API_KEY.search(text) or RE_STRIPE_LIVE_KEY.search(text):
            ln = _line_for_regex(text, RE_GOOGLE_API_KEY) or _line_for_regex(text, RE_STRIPE_LIVE_KEY)
            findings.append(
                Finding(
                    severity="FAIL",
                    code="lint_token_marker",
                    file=rel,
                    path=f"line:{ln}",
                    message="Likely API token marker detected in text file",
                )
            )

        if RE_GITHUB_TOKEN.search(text) or RE_SLACK_TOKEN.search(text):
            ln = _line_for_regex(text, RE_GITHUB_TOKEN) or _line_for_regex(text, RE_SLACK_TOKEN)
            findings.append(
                Finding(
                    severity="FAIL",
                    code="lint_token_marker",
                    file=rel,
                    path=f"line:{ln}",
                    message="Likely API token marker detected in text file",
                )
            )

        if RE_GENERIC_TOKEN_WORD.search(text):
            findings.append(
                Finding(
                    severity="WARN",
                    code="lint_token_word_present",
                    file=rel,
                    path=f"line:{_line_for_regex(text, RE_GENERIC_TOKEN_WORD)}",
                    message="Token/secret keyword present in text; verify no secrets are embedded",
                )
            )

        # Likely-PII literals (WARN only).
        if _contains_non_doc_email(text):
            findings.append(
                Finding(
                    severity="WARN",
                    code="lint_email_literal_present",
                    file=rel,
                    path=f"line:{_line_for_non_doc_email(text)}",
                    message="Email address literal detected in text; verify it is safe/necessary to publish",
                )
            )

        if _contains_non_doc_ip(text):
            ln = _line_for_non_doc_ip(text)
            findings.append(
                Finding(
                    severity="WARN",
                    code="lint_ip_literal_present",
                    file=rel,
                    path=f"line:{ln}",
                    message="IP address literal detected in text; prefer coarse geo/asn/resolver classes unless crucial",
                )
            )

        if RE_PHONE.search(text):
            findings.append(
                Finding(
                    severity="WARN",
                    code="lint_phone_literal_present",
                    file=rel,
                    path=f"line:{_line_for_regex(text, RE_PHONE)}",
                    message="Phone-number-like literal detected; avoid publishing identifying contact info",
                )
            )

        if RE_LATLON.search(text):
            findings.append(
                Finding(
                    severity="WARN",
                    code="lint_latlon_literal_present",
                    file=rel,
                    path=f"line:{_line_for_regex(text, RE_LATLON)}",
                    message="Lat/long coordinate literal detected in text; prefer coarse geo hints (country/region)",
                )
            )





        # Also lint vary[] / age[] tokens in text surfaces (docs/224.2a).
        for vm in VARY_NOTE_RE.finditer(text):
            raw_v = (vm.group(1) or "").strip()
            if not raw_v:
                continue
            canon_v = _canon_vary(raw_v)
            if len(raw_v) > 96:
                findings.append(
                    Finding(
                        severity="WARN",
                        code="lint_vary_unbounded",
                        file=rel,
                        path="$",
                        message=f"vary[] looks long for a publishable hint (len={len(raw_v)}); prefer bounded header-name list",
                    )
                )
            raw_norm = re.sub(r"\s+", "", raw_v).lower()
            if canon_v and raw_norm != canon_v:
                findings.append(
                    Finding(
                        severity="WARN",
                        code="lint_vary_noncanonical",
                        file=rel,
                        path="$",
                        message=f"vary[] is non-canonical; prefer vary[{canon_v}] (got {raw_v!r})",
                    )
                )

        for am in AGE_NOTE_RE.finditer(text):
            raw_a = (am.group(1) or "").strip()
            if not raw_a:
                continue
            canon_a = _canon_age(raw_a)
            if not raw_a.isdigit() and not (canon_a and canon_a.isdigit()):
                findings.append(
                    Finding(
                        severity="WARN",
                        code="lint_age_nonint",
                        file=rel,
                        path="$",
                        message=f"age[] should be integer seconds (got {raw_a!r})",
                    )
                )
        # Reuse req[] compact notation checks on any req[...] occurrences.
        for m in REQ_NOTE_RE.finditer(text):
            note_str = f"req[{m.group(1) or ''}]"
            kv = _extract_req_kvs(note_str)

            if "cookie" in kv and kv["cookie"].lower() not in REQ_COOKIE_VALUES:
                findings.append(
                    Finding(
                        severity="FAIL",
                        code="lint_req_cookie_value",
                        file=rel,
                        path="$",
                        message=f"req[] cookie must be none|present_redacted (got {kv['cookie']!r})",
                    )
                )

            if "ua" in kv and _ua_looks_full(kv["ua"]):
                findings.append(
                    Finding(
                        severity="WARN",
                        code="lint_req_full_user_agent_suspected",
                        file=rel,
                        path="$",
                        message=f"req[] ua value looks like a full UA string; prefer coarse ua_class (got {kv['ua']!r})",
                    )
                )

            if "cache" in kv and kv["cache"].lower() not in REQ_CACHE_VALUES:
                findings.append(
                    Finding(
                        severity="WARN",
                        code="lint_req_cache_unrecognized",
                        file=rel,
                        path="$",
                        message=f"req[] cache value is not in allowlist {sorted(REQ_CACHE_VALUES)} (got {kv['cache']!r})",
                    )
                )

            if "resolver" in kv and kv["resolver"].lower() not in REQ_RESOLVER_VALUES:
                findings.append(
                    Finding(
                        severity="WARN",
                        code="lint_req_resolver_unrecognized",
                        file=rel,
                        path="$",
                        message=f"req[] resolver value is not in allowlist {sorted(REQ_RESOLVER_VALUES)} (got {kv['resolver']!r})",
                    )
                )

            if "lang" in kv:
                lv = kv["lang"].strip()
                if _lang_looks_full_header(lv):
                    findings.append(
                        Finding(
                            severity="WARN",
                            code="lint_req_lang_looks_unbounded",
                            file=rel,
                            path="$",
                            message=f"req[] lang looks like a full Accept-Language header; prefer a single primary tag or 'none' (got {lv!r})",
                        )
                    )
                if lv.lower() != "none" and not RE_LANG.fullmatch(lv):
                    findings.append(
                        Finding(
                            severity="WARN",
                            code="lint_req_lang_not_primary_tag",
                            file=rel,
                            path="$",
                            message=f"req[] lang is not a primary BCP47 tag (got {lv!r})",
                        )
                    )

            if "asn" in kv:
                av = kv["asn"].strip()
                if not re.fullmatch(r"\d{1,10}", av):
                    findings.append(
                        Finding(
                            severity="WARN",
                            code="lint_req_asn_not_digits",
                            file=rel,
                            path="$",
                            message=f"req[] asn should be digits only (got {av!r})",
                        )
                    )

            if "geo" in kv:
                gv = kv["geo"].strip()
                if _geo_looks_too_specific(gv):
                    findings.append(
                        Finding(
                            severity="WARN",
                            code="lint_req_geo_too_specific",
                            file=rel,
                            path="$",
                            message=f"req[] geo looks too specific (coords/IP); keep to country/region only (got {gv!r})",
                        )
                    )
                elif not (RE_COUNTRY.fullmatch(gv) or RE_REGION.fullmatch(gv)):
                    findings.append(
                        Finding(
                            severity="WARN",
                            code="lint_req_geo_noncanonical",
                            file=rel,
                            path="$",
                            message=f"req[] geo is non-canonical; prefer country=XX or region=CC-SS (got {gv!r})",
                        )
                    )

    # Apply WARN-only suppressions (FAIL is never suppressed).
    if suppress_warn_codes:
        findings = [f for f in findings if not (f.severity == "WARN" and f.code in suppress_warn_codes)]

    return findings


def main() -> int:
    ap = argparse.ArgumentParser(description="Lint an evidence packet for publishable redaction hygiene")
    ap.add_argument("--packet", default=None, help="Path to packet directory")
    ap.add_argument(
        "--max-string",
        type=int,
        default=int(DEFAULT_MAX_STRING),
        help="Maximum allowed string length",
    )
    ap.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    ap.add_argument("--list-codes", action="store_true", help="List known lint codes (tight) and exit")
    ap.add_argument("--explain", default=None, help="Explain a lint code and exit")
    args = ap.parse_args()

    if args.list_codes:
        for c in sorted(CODE_EXPLAIN.keys()):
            print(c)
        return 0

    if args.explain:
        code = str(args.explain).strip()
        msg = CODE_EXPLAIN.get(code)
        if msg:
            print(f"{code}: {msg}")
            return 0
        print(f"{code}: (no explanation; search in tools/public_artifact_lint.py)")
        return 0

    if not args.packet:
        raise SystemExit("--packet is required (or use --list-codes / --explain)")

    pkt = Path(args.packet)
    if not pkt.exists() or not pkt.is_dir():
        raise SystemExit(f"--packet must be a directory: {pkt}")

    suppress_warn_codes = _load_warn_suppressions(pkt)

    findings = lint_packet(pkt, max_string=int(args.max_string))

    fail = sum(1 for f in findings if f.severity == "FAIL")
    warn = sum(1 for f in findings if f.severity == "WARN")

    if args.json:
        out = {
            "packet": str(pkt),
            "suppressed_warn_codes": sorted(suppress_warn_codes),
            "summary": {"fail": fail, "warn": warn},
            "findings": [f.__dict__ for f in findings],
        }
        print(json.dumps(out, indent=2, sort_keys=True))
    else:
        print(f"Public artifact lint: {pkt}")
        print(f"FAIL={fail} WARN={warn}")
        if suppress_warn_codes:
            print(f"WARN suppressions active (redaction-log.md): {sorted(suppress_warn_codes)}")
        for f in findings[:50]:
            print(f"{f.severity} {f.code} {f.file} {f.path} - {f.message}")
        if len(findings) > 50:
            print(f"... ({len(findings) - 50} more)")

    return 0 if fail == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
