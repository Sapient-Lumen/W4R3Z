#!/usr/bin/env python3
"""Minimal offline verifier for ObserverKit bundles.

Verifies:
- file SHA-256 hashes listed in manifest.json
- Ed25519 signatures over a deterministic canonicalization of the manifest (excluding signatures)

This is *not* a full cryptographic ballot verifier. It is an integrity/provenance checker
so that independent parties can rely on a stable evidence bundle before running full verifiers.
"""

import base64
import argparse
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

def is_safe_relpath(rel: Path) -> bool:
    if rel.is_absolute():
        return False
    # Prevent path traversal.
    return ".." not in rel.parts and ":" not in rel.as_posix()

def load_public_keys(pk_path: Path) -> dict:
    data = json.loads(pk_path.read_text(encoding="utf-8"))
    out = {}
    for k in data.get("keys", []):
        if k.get("alg") != "ed25519":
            continue
        try:
            raw = base64.b64decode(k["public_key_b64"])
            out[k["key_id"]] = ed25519.Ed25519PublicKey.from_public_bytes(raw)
        except Exception:
            # Skip malformed entries.
            continue
    return out

def main(root: Path, quiet: bool = False, show_payload: bool = False) -> int:
    manifest_path = root / "manifest.json"
    pk_path = root / "public_keys.json"
    if not manifest_path.exists() or not pk_path.exists():
        print("FAIL: missing manifest.json or public_keys.json")
        return 2

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    pubkeys = load_public_keys(pk_path)

    # Verify signatures
    payload = canonical_manifest_bytes(manifest)
    payload_sha256 = hashlib.sha256(payload).hexdigest()
    sigs = manifest.get("signatures", [])
    if not sigs:
        print("FAIL: no signatures in manifest")
        return 2

    sig_ok = 0
    sig_considered = 0
    unknown_key_ids = set()
    for s in sigs:
        key_id = s.get("key_id")
        alg = s.get("alg")
        sig_b64 = s.get("sig_b64")
        if alg != "ed25519" or key_id not in pubkeys:
            if key_id:
                unknown_key_ids.add(str(key_id))
            continue
        sig_considered += 1
        try:
            pubkeys[key_id].verify(base64.b64decode(sig_b64), payload)
            sig_ok += 1
        except Exception:
            pass

    if sig_ok == 0:
        print("FAIL: no valid signatures verified")
        if unknown_key_ids:
            print("  Unknown key_id(s) in manifest:")
            for k in sorted(unknown_key_ids):
                print("   -", k)
        return 2

    # Verify file hashes
    missing = []
    mismatched = []
    unsafe = []
    size_mismatch = []
    for f in manifest.get("files", []):
        rel = Path(f["path"])
        if not is_safe_relpath(rel):
            unsafe.append(str(rel))
            continue
        p = root / rel
        if not p.exists():
            missing.append(str(rel))
            continue
        if "bytes" in f:
            try:
                if int(p.stat().st_size) != int(f["bytes"]):
                    size_mismatch.append(str(rel))
            except Exception:
                pass
        digest = sha256_file(p)
        if digest.lower() != f["sha256"].lower():
            mismatched.append(str(rel))

    if unsafe or missing or size_mismatch or mismatched:
        print("FAIL: bundle contents did not match manifest")
        if unsafe:
            print("  Unsafe paths (possible traversal):")
            for x in unsafe:
                print("   -", x)
        if missing:
            print("  Missing:")
            for x in missing:
                print("   -", x)
        if size_mismatch:
            print("  Size mismatch (bytes field):")
            for x in size_mismatch:
                print("   -", x)
        if mismatched:
            print("  Hash mismatch:")
            for x in mismatched:
                print("   -", x)
        return 2

    if not quiet:
        print("PASS: ObserverKit bundle verified")
        print("  bundle_id:", manifest.get("bundle_id"))
        print("  election_id:", manifest.get("election_id"))
        print("  epb_hash:", manifest.get("epb_hash"))
        print("  checkpoint_id:", manifest.get("checkpoint_id"))
        print("  checkpoint_hash:", manifest.get("checkpoint_hash"))
        print("  manifest_payload_sha256:", payload_sha256)
        print("  signatures_ok:", sig_ok, "/", sig_considered, "(considered)")
        print("  signature_entries:", len(sigs))
        print("  files_ok:", len(manifest.get("files", [])))
        if unknown_key_ids:
            print("  note: manifest contains signature entries for unknown key_id(s)")
    if show_payload:
        sys.stdout.buffer.write(payload)
    return 0

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Verify an ObserverKit evidence bundle offline")
    ap.add_argument("root", nargs="?", default=str(Path(__file__).resolve().parents[1]), help="bundle root directory")
    ap.add_argument("--quiet", action="store_true", help="only emit failures")
    ap.add_argument("--show-manifest-payload", action="store_true", help="emit canonicalized manifest payload bytes to stdout")
    args = ap.parse_args()
    root = Path(args.root)
    raise SystemExit(main(root, quiet=args.quiet, show_payload=args.show_manifest_payload))
