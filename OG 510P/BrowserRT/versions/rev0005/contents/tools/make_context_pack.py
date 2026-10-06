#!/usr/bin/env python3
from __future__ import annotations

# The baby cube keeps this intentionally tiny. Future versions may generate more
# of CONTEXT-PACK.md, but rev0005 verifies that the existing surface stays
# present and aligned.

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if __name__ == '__main__':
    path = ROOT / 'CONTEXT-PACK.md'
    if not path.exists():
        raise SystemExit('missing CONTEXT-PACK.md')
    print(path)
