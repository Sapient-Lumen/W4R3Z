#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


REQUIRED_PATHS = {
    "Cargo.toml",
    "Cargo.lock",
    "pyproject.toml",
    "README.md",
    "docs/PROJECT_CHARTER.md",
    "docs/SCIENCE_PLAN.md",
    "examples/gauntlet/gauntlet_v2.json",
    "specs/spec_ledger.yaml",
}


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    ver = sys.argv[1] if len(sys.argv) > 1 else "dev"
    manifest = root / "artifacts" / "release" / ver / "manifest.json"

    if not manifest.exists():
        print(f"release-entries: ok (missing {manifest}, skip)")
        return 0

    obj = json.loads(manifest.read_text(encoding="utf-8"))
    entries = obj.get("entries", [])
    paths = {str(e.get("path", "")) for e in entries if isinstance(e, dict)}

    missing = sorted(REQUIRED_PATHS - paths)
    if missing:
        for p in missing:
            print(f"release-entries: missing required path {p}", file=sys.stderr)
        return 1

    print(f"release-entries: ok ({len(REQUIRED_PATHS)} required paths present)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
