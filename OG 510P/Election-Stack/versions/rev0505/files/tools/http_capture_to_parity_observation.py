#!/usr/bin/env python3
"""tools/http_capture_to_parity_observation.py

Convert a bounded HTTP response capture into a PublicSurfaceParitySnapshot-style
`observations[]` entry (docs/201).

Why this exists:
- Parity snapshots are meant to be small and comparable: mostly digests + status codes.
- Operators often capture surfaces with `curl -i` and need a safe, copy/paste snippet
  without shipping response bodies.

This tool:
- parses a raw HTTP capture that includes headers + body (e.g., `curl -i` output)
- selects the LAST response block (handles redirects / proxy 100-continue)
- computes sha256(body) as `sha256:<hex>` and extracts a minimal subset of parseable
  envelope fields when the body is an EvidenceEnvelope JSON.

It is stdlib-only and does NOT perform network fetches.

Example:
  curl -sS -i https://elections.example/notices/feed/latest.json > capture.txt

  python tools/http_capture_to_parity_observation.py \
    --capture capture.txt \
    --channel-id web_primary \
    --url https://elections.example/notices/feed/latest.json \
    --fetched-at 2026-02-25T12:34:56Z

Output: a single JSON object shaped like PublicSurfaceParitySnapshot.observations[]

NOTE: This tool intentionally does not emit the response body or an EvidencePointer.
Use hashes-first; attach bodies only when crucial (docs/201.3).
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, Tuple

try:
    from tools.http_capture_common import get_header, iso_now, load_pair, sha256_hex, split_last_http_response, build_request_context_note
except Exception:
    from http_capture_common import get_header, iso_now, load_pair, sha256_hex, split_last_http_response, build_request_context_note


def _maybe_parse_envelope(body: bytes) -> Tuple[Dict[str, str], str]:
    """Attempt to parse body as an EvidenceEnvelope and extract bounded fields.

    Returns (fields, parse_error). fields may include:
      - envelope_kind
      - envelope_payload_sha256
      - envelope_tbs_sha256
    """

    fields: Dict[str, str] = {}

    # Be permissive about whitespace/encoding.
    try:
        txt = body.decode("utf-8", "strict")
    except Exception as e:
        return fields, f"body_not_utf8: {type(e).__name__}"

    try:
        obj = json.loads(txt)
    except Exception as e:
        return fields, f"json_parse_failed: {type(e).__name__}"

    if not isinstance(obj, dict):
        return fields, "json_not_object"

    # Heuristic: EvidenceEnvelope has kind + payload_digest.
    kind = str(obj.get("kind") or "").strip()
    if kind:
        fields["envelope_kind"] = kind

    pd = str(obj.get("payload_digest") or "").strip()
    if re.fullmatch(r"sha256:[0-9a-f]{64}", pd):
        fields["envelope_payload_sha256"] = pd

    tbs = str(obj.get("tbs_digest") or "").strip()
    if re.fullmatch(r"sha256:[0-9a-f]{64}", tbs):
        fields["envelope_tbs_sha256"] = tbs

    # If it doesn't look like an envelope, treat as not-an-envelope.
    if not kind and not pd and not tbs:
        return {}, "not_evidence_envelope"

    return fields, ""


def main() -> int:
    ap = argparse.ArgumentParser(description="Convert an HTTP capture into a parity observation snippet")

    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--capture", default="", help="Raw capture (headers + body), e.g. curl -i output")
    src.add_argument("--headers", default="", help="Response headers file (curl -D)")

    ap.add_argument("--body", default="", help="Response body file (curl -o). Required with --headers")

    ap.add_argument("--channel-id", required=True, help="Official channel id (from registries)")
    ap.add_argument("--url", required=True, help="Fetch location used for this observation")
    ap.add_argument("--fetched-at", default="", help="RFC3339 timestamp (default: now, UTC)")
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

    if args.capture:
        raw = Path(args.capture).read_bytes()
        status, headers, body = split_last_http_response(raw)
    else:
        status, headers, body = load_pair(Path(args.headers), Path(args.body))

    obs: Dict[str, object] = {
        "channel_id": str(args.channel_id).strip(),
        "url": str(args.url).strip(),
        "fetched_at": args.fetched_at.strip() or iso_now(),
    }

    if status is not None:
        obs["http_status"] = status

    ct = get_header(headers, "content-type")
    if ct:
        # Keep it bounded: strip parameters beyond the first ';'.
        obs["content_type"] = ct.split(";", 1)[0].strip()

    obs["body_sha256"] = sha256_hex(body)

    env_fields, parse_err = _maybe_parse_envelope(body)
    for k, v in env_fields.items():
        obs[k] = v

    if parse_err:
        obs["parse_error"] = parse_err

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

    # If no status line is found, this is still a usable digest, but warn via exit code.
    return 0 if status is not None else 1


if __name__ == "__main__":
    raise SystemExit(main())
