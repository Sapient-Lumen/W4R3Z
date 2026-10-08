#!/usr/bin/env python3
"""Compute SHA-256 of a file or directory tree and output a notarization stub.

Usage:
  python3 bundle_hash_report.py <path>

If <path> is a directory, hashes all files and produces a single root hash by hashing
the sorted list of 'sha256  path' lines (simple deterministic construction).
For production, prefer a Merkle tree with explicit proofs.
"""

import hashlib
import os
import sys
from pathlib import Path
import json
from datetime import datetime, timezone

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def dir_digest(root: Path):
    entries = []
    for p in sorted(root.rglob("*")):
        if p.is_file():
            rel = str(p.relative_to(root)).replace(os.sep, "/")
            entries.append(f"{sha256_file(p)}  {rel}")
    h = hashlib.sha256()
    joined = "\n".join(entries).encode("utf-8")
    h.update(joined)
    return h.hexdigest(), entries

def main():
    if len(sys.argv) < 2:
        print("Usage: bundle_hash_report.py <path>")
        return 2
    target = Path(sys.argv[1])
    if not target.exists():
        print("FAIL: path does not exist")
        return 2
    if target.is_file():
        digest = sha256_file(target)
        meta = {"type":"file","path":str(target)}
    else:
        digest, entries = dir_digest(target)
        meta = {"type":"directory","path":str(target),"file_count":len(entries)}
    report = {
        "hash_alg":"sha256",
        "artifact_hash":digest,
        "created_at":datetime.now(timezone.utc).isoformat(),
        "note":"Use this digest as input to RFC3161 timestamping or transparency-log anchoring.",
        "meta":meta,
        "notarizations":[]
    }
    print(json.dumps(report, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
