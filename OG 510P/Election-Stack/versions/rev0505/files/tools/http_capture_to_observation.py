#!/usr/bin/env python3
"""tools/http_capture_to_observation.py

Convert a bounded HTTP response capture into a LivenessBeacon-style observation snippet.

Why this exists:
- Cache/split-view disputes often hinge on "who saw which pointer when".
- Operators commonly capture surfaces with curl/wget and share only safe signals
  (status code, small header subset, payload digest) to avoid bloat / secrets.

This tool:
- parses a raw HTTP capture that includes headers + body (e.g., `curl -i` output)
- selects the LAST response block (handles redirects / proxy 100-continue)
- computes sha256(body) (as `sha256:<hex>`) and extracts only evidence-safe freshness headers
- prints a JSON object shaped like `observations[]` entries used by
  `hfv.coverage.liveness_beacon` (docs/210).

It is stdlib-only and does NOT perform network fetches.

Example capture commands (write capture to a file):

  curl -sS -i https://elections.example/.well-known/election-stack.json > capture.txt
  # or (explicitly separate files):
  curl -sS -D headers.txt -o body.bin https://elections.example/.well-known/election-stack.json

Usage:
  python tools/http_capture_to_observation.py --capture capture.txt \
    --surface well_known_discovery --observed-at 2026-02-25T12:34:56Z

  python tools/http_capture_to_observation.py --headers headers.txt --body body.bin \
    --surface public_notice_feed --url-hint https://…/feed.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict

try:
    from tools.http_capture_common import iso_now, load_pair, safe_freshness_headers, sha256_hex, split_last_http_response, get_header, build_request_context_note
except Exception:
    from http_capture_common import iso_now, load_pair, safe_freshness_headers, sha256_hex, split_last_http_response, get_header, build_request_context_note


def main() -> int:
    ap = argparse.ArgumentParser(description="Convert a bounded HTTP capture into an observation snippet")

    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--capture", default="", help="Path to raw capture (headers + body), e.g. curl -i output")
    src.add_argument("--headers", default="", help="Path to response headers file (curl -D)")

    ap.add_argument("--body", default="", help="Path to response body file (curl -o). Required with --headers")

    ap.add_argument("--surface", required=True, help="Surface key (e.g., well_known_discovery)")
    ap.add_argument("--observed-at", default="", help="RFC3339 timestamp for observed_at (default: now, UTC)")
    ap.add_argument("--url-hint", default="", help="Short public URL hint (avoid long URLs)")
    ap.add_argument("--result", default="ok", help="Observation result string (default: ok)")
    ap.add_argument("--ua-class", default="", help="Optional coarse UA class for notes (e.g., desktop_chrome, cli_curl)")
    ap.add_argument("--accept-language", default="", help="Optional Accept-Language hint for notes (e.g., en-US, none)")
    ap.add_argument("--cache-bypass", default="", help="Optional cache-bypass attempt for notes (none|no-cache|force-refresh)")
    ap.add_argument("--cookies", default="", help="Optional cookie presence for notes (none|present_redacted)")
    ap.add_argument("--geo-hint", default="", help="Optional coarse geo hint for notes (e.g., country=US)")
    ap.add_argument("--asn-hint", default="", help="Optional coarse ASN hint for notes (e.g., asn=15169)")
    ap.add_argument("--resolver-hint", default="", help="Optional resolver hint for notes (system_resolver|public_resolver|pinned_resolver)")
    ap.add_argument("--emit-variance-hints", action="store_true", help="If set, include response Vary/Age hints in notes")
    ap.add_argument("--pretty", action="store_true", help="Pretty-print JSON")

    args = ap.parse_args()

    if args.headers and not args.body:
        raise SystemExit("--body is required when using --headers")

    status: int | None
    headers: Dict[str, str]
    body: bytes

    if args.capture:
        raw = Path(args.capture).read_bytes()
        status, headers, body = split_last_http_response(raw)
    else:
        status, headers, body = load_pair(Path(args.headers), Path(args.body))

    obs: Dict[str, object] = {
        "surface": str(args.surface).strip(),
        "result": str(args.result).strip() or "ok",
        "observed_at": args.observed_at.strip() or iso_now(),
        "payload_sha256": sha256_hex(body),
    }

    if args.url_hint.strip():
        obs["url_hint"] = args.url_hint.strip()
    if status is not None:
        obs["http_status"] = status

    safe = safe_freshness_headers(headers)
    if safe:
        obs["headers"] = safe

    # Optional compact request-context / variance hints (docs/224).
    vary = get_header(headers, "vary") if args.emit_variance_hints else ""
    age = get_header(headers, "age") if args.emit_variance_hints else ""
    note = build_request_context_note(
        ua_class=args.ua_class,
        accept_language=args.accept_language,
        cache_bypass=args.cache_bypass,
        cookies=args.cookies,
        geo_hint=args.geo_hint,
        asn_hint=args.asn_hint,
        resolver_hint=args.resolver_hint,
        vary=vary,
        age=age,
    )
    if note:
        obs["notes"] = note

    if args.pretty:
        print(json.dumps(obs, indent=2, sort_keys=True))
    else:
        print(json.dumps(obs, separators=(",", ":"), sort_keys=True))

    # If we couldn't find a status line, this is still a usable digest, but warn via exit code.
    return 0 if status is not None else 1


if __name__ == "__main__":
    raise SystemExit(main())
