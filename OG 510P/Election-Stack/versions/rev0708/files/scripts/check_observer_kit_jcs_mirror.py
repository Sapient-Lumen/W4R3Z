#!/usr/bin/env python3
"""Drift firewall: ensure ObserverKit embeds the same RFC8785-JCS implementation.

ObserverKit is meant to be copied out as a standalone offline bundle verifier.
If the embedded `observer-kit/tools/jcs.py` diverges from the archive's canonical
`tools/jcs.py`, signatures may validate in one context but fail in another.

This check keeps the two files byte-identical.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> int:
    a = ROOT / "tools" / "jcs.py"
    b = ROOT / "observer-kit" / "tools" / "jcs.py"
    if not a.exists() or not b.exists():
        print("FAIL: missing JCS implementation file(s)")
        return 2

    ha = sha256_bytes(a.read_bytes())
    hb = sha256_bytes(b.read_bytes())
    if ha != hb:
        print("FAIL: ObserverKit JCS implementation diverged from tools/jcs.py")
        print("  tools/jcs.py sha256:", ha)
        print("  observer-kit/tools/jcs.py sha256:", hb)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
