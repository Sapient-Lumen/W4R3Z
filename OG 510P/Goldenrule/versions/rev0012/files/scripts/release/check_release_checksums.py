#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import sys
from pathlib import Path


def fail(msg: str) -> None:
    print(f"release-checksums: {msg}", file=sys.stderr)
    raise SystemExit(1)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    ver = sys.argv[1] if len(sys.argv) > 1 else "dev"
    sums = root / "artifacts" / "release" / ver / "checksums.txt"

    if not sums.exists():
        print(f"release-checksums: ok (missing {sums}, skip)")
        return 0

    lines = [ln for ln in sums.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if not lines:
        fail(f"{sums}: empty")

    checked = 0
    for ln in lines:
        parts = ln.split("  ", 1)
        if len(parts) != 2:
            fail(f"malformed line: {ln}")
        expected, rel = parts
        fpath = root / rel
        if not fpath.exists():
            fail(f"missing file listed in checksums: {rel}")
        actual = sha256_file(fpath)
        if actual != expected:
            fail(f"checksum mismatch for {rel}")
        checked += 1

    print(f"release-checksums: ok ({checked} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
