#!/usr/bin/env python3
"""Drift-tripwire for results hashing semantics (docs/235 + docs/236).

We keep this deliberately small:
- A CRO vector that exercises TBS(CRO) hashing (cro_hash omitted).
- A RESULTS leaf vector that exercises payload_hash_b64 derivation from a manifest JSON.

This is not a full conformance suite. It is a safety rail against silent regressions.
"""

from __future__ import annotations

import base64
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from jcs import dump_bytes as jcs_bytes  # noqa: E402


def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def fail(msg: str) -> None:
    print("ERROR:", msg, file=sys.stderr)
    raise SystemExit(2)


def main() -> int:
    vec_path = ROOT / "artifacts" / "test-vectors" / "results_hash_vectors.json"
    if not vec_path.exists():
        fail("missing results_hash_vectors.json")

    vectors = json.loads(vec_path.read_text(encoding="utf-8"))
    if not isinstance(vectors, list) or not vectors:
        fail("results_hash_vectors.json must be a non-empty list")

    for v in vectors:
        vid = v.get("vector_id", "<missing vector_id>")
        kind = v.get("kind")

        if kind == "CRO_TBS_SHA256":
            cro = v.get("cro")
            exp = v.get("expected_cro_hash")
            if not isinstance(cro, dict):
                fail(f"{vid}: cro must be object")
            if not isinstance(exp, str) or not exp.startswith("sha256:"):
                fail(f"{vid}: expected_cro_hash must be sha256:<hex>")

            tbs = dict(cro)
            tbs.pop("cro_hash", None)
            got_hex = sha256_hex(jcs_bytes(tbs))
            got = f"sha256:{got_hex}"
            if got != exp:
                fail(f"{vid}: CRO TBS hash mismatch: expected {exp} got {got}")

            # Optional: also require cro.cro_hash matches.
            if cro.get("cro_hash") != exp:
                fail(f"{vid}: cro.cro_hash field does not match expected_cro_hash")

        elif kind == "RESULTS_LEAF_PAYLOAD_HASH":
            m = v.get("rrp_manifest")
            exp_b64 = v.get("expected_payload_hash_b64")
            if not isinstance(m, dict):
                fail(f"{vid}: rrp_manifest must be object")
            if not isinstance(exp_b64, str) or not exp_b64:
                fail(f"{vid}: expected_payload_hash_b64 missing")

            h_hex = sha256_hex(jcs_bytes(m))
            got_b64 = base64.b64encode(bytes.fromhex(h_hex)).decode("ascii")
            if got_b64 != exp_b64:
                fail(f"{vid}: payload_hash_b64 mismatch: expected {exp_b64} got {got_b64}")

            exp_sha = v.get("expected_payload_sha256")
            if isinstance(exp_sha, str) and exp_sha.startswith("sha256:"):
                got_sha = f"sha256:{h_hex}"
                if got_sha != exp_sha:
                    fail(f"{vid}: payload sha256 mismatch: expected {exp_sha} got {got_sha}")
        else:
            fail(f"{vid}: unknown kind {kind!r}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
