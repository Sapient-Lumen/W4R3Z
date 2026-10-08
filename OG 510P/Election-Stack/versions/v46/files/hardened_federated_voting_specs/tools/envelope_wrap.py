#!/usr/bin/env python3
"""
tools/envelope_wrap.py

Wrap a JSON payload in an EvidenceEnvelope (schemas/EvidenceEnvelope.json).
Optionally detach the payload into a content-addressed object in --objects-dir.

This is a stdlib-only reference tool. Signatures are placeholders; it focuses on
digest binding + deterministic bytes-to-be-signed (tbs_digest).

Usage (inline payload):
  python tools/envelope_wrap.py --payload artifacts/examples/coverage_report_example.json \
    --kind hfv.coverage.report --track "A (Deployable core)" \
    --schema schemas/CoverageReport.json --issuer-id monitor:EXAMPLE \
    --subject-json '{"election_id":"E123","jurisdiction":"JX"}' \
    --out /tmp/coverage.envelope.json

Usage (detached payload):
  python tools/envelope_wrap.py ... --detach --objects-dir /tmp/objects
"""

from __future__ import annotations
import argparse, hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

def jcs_dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def canonical_payload_bytes(payload_obj: Any) -> bytes:
    # Approx JCS canonicalization (see docs/176). Keep payloads I-JSON to avoid float ambiguity.
    return jcs_dumps(payload_obj).encode("utf-8")

def build_tbs(envelope: Dict[str, Any]) -> Dict[str, Any]:
    t = {
        "envelope_version": envelope["envelope_version"],
        "kind": envelope["kind"],
        "track": envelope["track"],
        "issued_at": envelope["issued_at"],
        "issuer": envelope["issuer"],
        "subject": envelope["subject"],
        "payload_schema": envelope["payload_schema"],
        "payload_digest": envelope["payload_digest"],
        "canonicalization": envelope["canonicalization"],
    }
    if "attachments" in envelope:
        t["attachments"] = envelope["attachments"]
    return t

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--payload", required=True, help="JSON payload file")
    ap.add_argument("--kind", required=True)
    ap.add_argument("--track", required=True)
    ap.add_argument("--schema", required=True, help="Payload schema id/ref")
    ap.add_argument("--issuer-id", required=True)
    ap.add_argument("--issuer-key-ref", default="")
    ap.add_argument("--issuer-role", default="")
    ap.add_argument("--subject-json", required=True, help="JSON object for subject")
    ap.add_argument("--out", required=True, help="Output envelope path")
    ap.add_argument("--detach", action="store_true", help="Store payload as detached object")
    ap.add_argument("--objects-dir", default="", help="Directory for detached objects")
    args = ap.parse_args()

    payload_path = Path(args.payload)
    payload_obj = json.loads(payload_path.read_text(encoding="utf-8"))
    payload_bytes = canonical_payload_bytes(payload_obj)
    payload_hex = sha256_bytes(payload_bytes)
    payload_digest = f"sha256:{payload_hex}"

    issued_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

    issuer = {"issuer_id": args.issuer_id}
    if args.issuer_key_ref:
        issuer["public_key_ref"] = args.issuer_key_ref
    if args.issuer_role:
        issuer["role"] = args.issuer_role

    subject = json.loads(args.subject_json)

    env: Dict[str, Any] = {
        "envelope_version": "1.1.0",
        "kind": args.kind,
        "track": args.track,
        "issued_at": issued_at,
        "issuer": issuer,
        "subject": subject,
        "payload_schema": args.schema,
        "canonicalization": "RFC8785-JCS",
        "payload_digest": payload_digest,
    }

    if args.detach:
        if not args.objects_dir:
            raise SystemExit("--detach requires --objects-dir")
        od = Path(args.objects_dir)
        od.mkdir(parents=True, exist_ok=True)
        obj_path = od / f"sha256-{payload_hex}.json"
        if not obj_path.exists():
            obj_path.write_bytes(payload_bytes)
        env["payload_pointer"] = {
            "digest": payload_digest,
            "media_type": "application/json",
            "size_bytes": len(payload_bytes),
            "uri": str(obj_path.name),
        }
    else:
        env["payload_inline"] = payload_obj

    tbs = build_tbs(env)
    tbs_bytes = jcs_dumps(tbs).encode("utf-8")
    env["tbs_digest"] = f"sha256:{sha256_bytes(tbs_bytes)}"

    env["signatures"] = [{
        "signer_id": args.issuer_id,
        "alg": "none",
        "sig": "UNSIGNED",
        "sig_encoding": "base64"
    }]

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(env, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
