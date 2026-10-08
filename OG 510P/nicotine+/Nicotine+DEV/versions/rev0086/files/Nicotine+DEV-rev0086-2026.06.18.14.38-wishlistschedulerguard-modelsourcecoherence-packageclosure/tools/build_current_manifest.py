#!/usr/bin/env python3
"""Build the current revision's complete SHA-256 manifest, excluding itself."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from cube_runtime import derive_revision, sha256_path  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.root.resolve()
    revision = derive_revision(root)
    relative_manifest = Path(f"handoff/{revision}/MANIFEST.sha256")
    manifest = root / relative_manifest
    manifest.parent.mkdir(parents=True, exist_ok=True)

    rows: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(root)
        if relative == relative_manifest:
            continue
        rows.append(f"{sha256_path(path)}  {relative.as_posix()}")
    manifest.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"{revision}: wrote {len(rows)} rows to {relative_manifest.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
