#!/usr/bin/env python3
from __future__ import annotations

import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXCLUDE_DIRS = {
    "__pycache__",
    ".git",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}

EXCLUDE_SUFFIXES = {".zip", ".pyc", ".pyo"}

def should_skip(path: Path) -> bool:
    for part in path.parts:
        if part in EXCLUDE_DIRS:
            return True
    if path.name.startswith(".") and path.name not in {
        ".editorconfig",
        ".gitignore",
        ".gitattributes",
        ".markdownlint.json",
        ".yamllint.yml",
        ".pre-commit-config.yaml",
    }:
        return False
    if path.suffix in EXCLUDE_SUFFIXES:
        return True
    if "artifacts" in path.parts and path.name != ".gitkeep":
        return True
    return False

def main() -> int:
    manifest = json.loads((ROOT / "metadata" / "archive-manifest.json").read_text(encoding="utf-8"))
    output = ROOT.parent / f"{manifest['archive_basename']}.zip"

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(ROOT.rglob("*")):
            if path.is_dir() or should_skip(path):
                continue
            arcname = Path(ROOT.name) / path.relative_to(ROOT)
            zf.write(path, arcname.as_posix())

    print(output)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
