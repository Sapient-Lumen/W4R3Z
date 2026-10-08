#!/usr/bin/env python3
"""Build MANIFEST.json, MANIFEST.sha256, and CHECKSUMS.sha256 safely."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from release_tree import MANIFEST_EXCLUDE, collect_files, sha256_file


def build(root: Path):
    root = root.resolve()
    entries = []
    for path, rel in collect_files(root, exclude=MANIFEST_EXCLUDE):
        entries.append({"path": rel, "size": path.stat().st_size, "sha256": sha256_file(path)})
    manifest = {
        "project": "LLMPoetry",
        "manifest_schema": "llmpoetry-manifest-v2",
        "note": "MANIFEST.json, MANIFEST.sha256, CHECKSUMS.sha256, and reports/validation_report.json are excluded to avoid self/generated-report loops. Symlinks, unsafe or non-canonical paths, case-fold collisions, Python caches, and turn-local do_rev*.py constructors are rejected or excluded by the shared release-tree policy.",
        "excluded_paths": sorted(MANIFEST_EXCLUDE),
        "excluded_patterns": [".git/", "__pycache__/", "do_rev####*.py at release root"],
        "file_count_excluding_manifest_surfaces": len(entries),
        "files": entries,
    }
    (root / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    manifest_hash = sha256_file(root / "MANIFEST.json")
    (root / "MANIFEST.sha256").write_text(f"{manifest_hash}  MANIFEST.json\n", encoding="utf-8")
    (root / "CHECKSUMS.sha256").write_text(
        "\n".join(f"{entry['sha256']}  {entry['path']}" for entry in entries) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    try:
        manifest = build(Path(args.root))
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 1
    print(json.dumps({"ok": True, "file_count": manifest["file_count_excluding_manifest_surfaces"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
