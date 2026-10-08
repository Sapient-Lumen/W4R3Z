#!/usr/bin/env python3
"""tools/jcs_canonicalize.py

CLI wrapper for RFC 8785 JSON Canonicalization Scheme (JCS).

Usage:
  python tools/jcs_canonicalize.py --in payload.json > canonical.json
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from jcs import dumps


def loads(path: str) -> Any:
    if path == "-":
        return json.load(sys.stdin)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default="-", help="Input JSON file or - for stdin")
    args = ap.parse_args()
    obj = loads(args.inp)
    sys.stdout.write(dumps(obj))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
