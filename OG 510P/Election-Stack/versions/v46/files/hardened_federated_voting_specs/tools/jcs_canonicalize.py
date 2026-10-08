#!/usr/bin/env python3
"""
tools/jcs_canonicalize.py

Reference JSON Canonicalization (RFC 8785 / JCS) *approximation*.

This tool intentionally uses Python stdlib only. It performs:
- recursive key sorting
- no extra whitespace
- UTF-8 output

NOTE: Full RFC 8785 number formatting matches ECMAScript's JSON.stringify().
Python's float rendering may differ. To avoid ambiguity, keep payloads in the
I-JSON subset and represent identifiers as strings.

Usage:
  python tools/jcs_canonicalize.py --in payload.json > canonical.json
"""

from __future__ import annotations
import argparse, json, sys
from typing import Any

def loads(path: str) -> Any:
    if path == "-":
        return json.load(sys.stdin)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def dumps(obj: Any) -> str:
    # sort_keys=True gives deterministic ordering.
    # separators removes whitespace.
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default="-", help="Input JSON file or - for stdin")
    args = ap.parse_args()
    obj = loads(args.inp)
    sys.stdout.write(dumps(obj))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
