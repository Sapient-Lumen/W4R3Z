#!/usr/bin/env python3
"""tools/policy_profile_digest.py

Compute a stable digest pin for a VerifierPolicyProfile JSON file.

Output:
- prints `sha256:<hex>` of the RFC8785-JCS canonical bytes of the JSON value

Rationale:
- verifiers SHOULD publish a policy profile alongside publishable reports
- PacketVerificationReport.policy_profile_sha256 SHOULD pin a comparable digest
  independent of whitespace/key-order formatting (docs/176; RFC8785-JCS)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from typing import Any

from jcs import dump_bytes as jcs_bytes


def load_json(path: str) -> Any:
    if path == "-":
        return json.load(sys.stdin)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default="-", help="Input VerifierPolicyProfile JSON file (or - for stdin)")
    args = ap.parse_args()

    obj = load_json(args.inp)
    b = jcs_bytes(obj)
    sys.stdout.write("sha256:" + hashlib.sha256(b).hexdigest() + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
