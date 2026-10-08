#!/usr/bin/env python3
"""Drift tripwire for EvidenceEnvelope digest rules.

Validates that the reference implementation still matches tiny, known-good vectors.

Why tiny?
- We can't afford archive bloat; this is a tripwire, not a full conformance suite.

See:
- docs/176-canonicalization-and-signing-rules-for-evidence-envelopes.md
- artifacts/test-vectors/envelope_vectors.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from envelope_common import payload_digest_for_json_value, tbs_digest_for_envelope  # noqa: E402


def fail(msg: str) -> None:
    print("FAIL", msg, file=sys.stderr)
    raise SystemExit(2)


def main() -> int:
    vec_path = ROOT / "artifacts" / "test-vectors" / "envelope_vectors.json"
    if not vec_path.exists():
        fail(f"missing vectors file: {vec_path}")

    data = json.loads(vec_path.read_text(encoding="utf-8"))
    if data.get("format") != "hfv.envelope_vectors.v1":
        fail("unexpected vectors format")

    vectors = data.get("vectors", [])
    if not isinstance(vectors, list) or not vectors:
        fail("no vectors")

    for v in vectors:
        name = v.get("name", "?")
        env_fields = v.get("envelope_fields")
        payload = v.get("payload_json")
        payload_path = v.get("payload_path")
        expect = v.get("expect")
        if not isinstance(env_fields, dict) or not isinstance(expect, dict):
            fail(f"{name}: malformed vector")

        env = dict(env_fields)
        # Optional sanity: schema-path refs should exist.
        ps = env.get("payload_schema")
        if isinstance(ps, str) and ps.startswith("schemas/"):
            if not (ROOT / ps).exists():
                fail(f"{name}: missing payload_schema path: {ps}")

        if payload is None and isinstance(payload_path, str) and payload_path:
            pp = (ROOT / payload_path)
            if not pp.exists():
                fail(f"{name}: payload_path not found: {payload_path}")
            try:
                payload = json.loads(pp.read_text(encoding="utf-8"))
            except Exception as e:
                fail(f"{name}: payload_path invalid JSON: {payload_path} ({e})")
        if payload is None:
            fail(f"{name}: vector must include payload_json or payload_path")

        got_payload_digest = payload_digest_for_json_value(payload)
        env["payload_digest"] = got_payload_digest
        got_tbs_digest = tbs_digest_for_envelope(env)

        if got_payload_digest != expect.get("payload_digest"):
            fail(f"{name}: payload_digest mismatch\n  expected {expect.get('payload_digest')}\n  got      {got_payload_digest}")
        if got_tbs_digest != expect.get("tbs_digest"):
            fail(f"{name}: tbs_digest mismatch\n  expected {expect.get('tbs_digest')}\n  got      {got_tbs_digest}")

    print("PASS: envelope vectors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
