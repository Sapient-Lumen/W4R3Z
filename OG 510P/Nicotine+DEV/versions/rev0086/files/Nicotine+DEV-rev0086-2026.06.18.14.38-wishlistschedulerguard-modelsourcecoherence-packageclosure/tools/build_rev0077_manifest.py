#!/usr/bin/env python3
"""Build the complete rev0077 SHA-256 manifest, excluding itself."""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

REVISION = "rev0077"
MANIFEST = Path("handoff/rev0077/MANIFEST.sha256")


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    target = root / MANIFEST
    target.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(root)
        if relative == MANIFEST:
            continue
        rows.append(f"{digest(path)}  {relative.as_posix()}")
    target.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"{REVISION}: wrote {len(rows)} rows to {MANIFEST}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
