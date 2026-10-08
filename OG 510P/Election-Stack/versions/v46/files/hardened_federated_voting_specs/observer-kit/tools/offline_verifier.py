#!/usr/bin/env python3
"""Minimal offline verifier for ObserverKit bundles.

Verifies:
- file SHA-256 hashes listed in manifest.json
- Ed25519 signatures over a deterministic canonicalization of the manifest (excluding signatures)

This is *not* a full cryptographic ballot verifier. It is an integrity/provenance checker
so that independent parties can rely on a stable evidence bundle before running full verifiers.
"""

import base64
import hashlib
import json
import sys
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def canonical_manifest_bytes(manifest: dict) -> bytes:
    # Deterministic subset; production should prefer RFC 8785 JCS.
    m2 = dict(manifest)
    m2["signatures"] = []
    return json.dumps(m2, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def load_public_keys(pk_path: Path) -> dict:
    data = json.loads(pk_path.read_text(encoding="utf-8"))
    out = {}
    for k in data.get("keys", []):
        if k.get("alg") != "ed25519":
            continue
        raw = base64.b64decode(k["public_key_b64"])
        out[k["key_id"]] = ed25519.Ed25519PublicKey.from_public_bytes(raw)
    return out

def main(root: Path) -> int:
    manifest_path = root / "manifest.json"
    pk_path = root / "public_keys.json"
    if not manifest_path.exists() or not pk_path.exists():
        print("FAIL: missing manifest.json or public_keys.json")
        return 2

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    pubkeys = load_public_keys(pk_path)

    # Verify signatures
    payload = canonical_manifest_bytes(manifest)
    sigs = manifest.get("signatures", [])
    if not sigs:
        print("FAIL: no signatures in manifest")
        return 2

    sig_ok = 0
    for s in sigs:
        key_id = s.get("key_id")
        alg = s.get("alg")
        sig_b64 = s.get("sig_b64")
        if alg != "ed25519" or key_id not in pubkeys:
            continue
        try:
            pubkeys[key_id].verify(base64.b64decode(sig_b64), payload)
            sig_ok += 1
        except Exception:
            pass

    if sig_ok == 0:
        print("FAIL: no valid signatures verified")
        return 2

    # Verify file hashes
    missing = []
    mismatched = []
    for f in manifest.get("files", []):
        rel = Path(f["path"])
        p = root / rel
        if not p.exists():
            missing.append(str(rel))
            continue
        digest = sha256_file(p)
        if digest.lower() != f["sha256"].lower():
            mismatched.append(str(rel))

    if missing or mismatched:
        print("FAIL: bundle contents did not match manifest")
        if missing:
            print("  Missing:")
            for x in missing:
                print("   -", x)
        if mismatched:
            print("  Hash mismatch:")
            for x in mismatched:
                print("   -", x)
        return 2

    print("PASS: ObserverKit bundle verified")
    print("  bundle_id:", manifest.get("bundle_id"))
    print("  election_id:", manifest.get("election_id"))
    print("  epb_hash:", manifest.get("epb_hash"))
    print("  checkpoint_id:", manifest.get("checkpoint_id"))
    print("  checkpoint_hash:", manifest.get("checkpoint_hash"))
    print("  signatures_ok:", sig_ok, "/", len(sigs))
    print("  files_ok:", len(manifest.get("files", [])))
    return 0

if __name__ == "__main__":
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    raise SystemExit(main(root))
