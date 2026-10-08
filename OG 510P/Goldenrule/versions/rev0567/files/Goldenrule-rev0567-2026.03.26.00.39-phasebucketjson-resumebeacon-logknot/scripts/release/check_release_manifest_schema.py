#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


def fail(msg: str) -> None:
    print(f"release-schema: {msg}", file=sys.stderr)
    raise SystemExit(1)


def validate(path: Path) -> None:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if obj.get("schema_version") != 1:
        fail(f"{path}: schema_version must be 1")
    if not isinstance(obj.get("version"), str) or not obj["version"].strip():
        fail(f"{path}: version must be non-empty string")
    if not isinstance(obj.get("generated_at_utc"), str) or not obj["generated_at_utc"].strip():
        fail(f"{path}: generated_at_utc missing")
    entries = obj.get("entries")
    if not isinstance(entries, list) or not entries:
        fail(f"{path}: entries must be non-empty list")
    for idx, e in enumerate(entries):
        if not isinstance(e, dict):
            fail(f"{path}: entries[{idx}] must be object")
        if not isinstance(e.get("path"), str) or not e["path"].strip():
            fail(f"{path}: entries[{idx}].path invalid")
        if not isinstance(e.get("sha256"), str) or len(e["sha256"]) != 64:
            fail(f"{path}: entries[{idx}].sha256 invalid")


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    release_dir = root / "artifacts" / "release"
    manifests = sorted(release_dir.glob("*/manifest.json"))
    if not manifests:
        print("release-schema: ok (no release manifests found)")
        return 0

    for m in manifests:
        validate(m)

    print(f"release-schema: ok ({len(manifests)} manifests)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
