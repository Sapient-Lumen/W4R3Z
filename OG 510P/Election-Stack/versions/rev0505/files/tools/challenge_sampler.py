#!/usr/bin/env python3
"""
challenge_sampler.py — deterministic sampling for Public Inspection challenges.

This is a *reference skeleton* intended to make sampling reproducible:
given (seed, round_id, watcher_id, quota_policy, allowlist), it returns
a stable list of targets.

Security goals:
- prevent challenge grinding (sampling is deterministic from public seed)
- make watcher behavior auditable (anyone can recompute targets)
"""

import argparse
import hashlib
import json
from typing import List, Dict, Any


def h(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def expand_seed(seed_hex: str, watcher_id: str, round_id: int) -> bytes:
    seed = bytes.fromhex(seed_hex)
    return h(seed + watcher_id.encode("utf-8") + str(round_id).encode("utf-8"))


def sample_targets(derived: bytes, targets: List[str], k: int) -> List[str]:
    # deterministic shuffle via hashing
    scored = []
    for t in targets:
        score = hashlib.sha256(derived + t.encode("utf-8")).hexdigest()
        scored.append((score, t))
    scored.sort()
    return [t for _, t in scored[:k]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed-hex", required=True, help="seed bytes in hex (e.g., NIST pulse output)")
    ap.add_argument("--watcher-id", required=True)
    ap.add_argument("--round-id", type=int, required=True)
    ap.add_argument("--targets-json", required=True, help="JSON array of target strings")
    ap.add_argument("--k", type=int, required=True, help="number of targets to sample")
    args = ap.parse_args()

    targets = json.loads(open(args.targets_json, "r").read())
    assert isinstance(targets, list) and all(isinstance(x, str) for x in targets)

    derived = expand_seed(args.seed_hex, args.watcher_id, args.round_id)
    picked = sample_targets(derived, targets, args.k)
    print(json.dumps({"round_id": args.round_id, "watcher_id": args.watcher_id, "targets": picked}, indent=2))


if __name__ == "__main__":
    main()
