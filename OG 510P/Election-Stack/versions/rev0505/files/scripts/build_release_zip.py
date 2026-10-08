#!/usr/bin/env python3
"""Build a deterministic release ZIP of the repository.

Why:
- makes releases reproducible (stable file order + stable timestamps)
- reduces noisy diffs in downstream distribution channels

This script is intentionally stdlib-only.

NOTE: This does not run the full release gate. Run `scripts/release_gate.py` first.
"""

from __future__ import annotations

import argparse
import os
import pathlib
import zipfile

FIXED_ZIP_DT = (1980, 1, 1, 0, 0, 0)

# Conservative excludes: anything non-normative or locally-generated.
EXCLUDE_DIR_PREFIXES = (
    ".git/",
    ".pytest_cache/",
    "__pycache__/",
    "evidence/cache/",
    "dist/",
)
EXCLUDE_BASENAMES = {
    ".DS_Store",
}
EXCLUDE_SUFFIXES = (
    ".pyc",
)


def _normalize_rel(p: pathlib.Path) -> str:
    return p.as_posix().lstrip("./")


def _should_include(rel_posix: str) -> bool:
    if not rel_posix or rel_posix.endswith("/"):
        return False

    # Exclude cache/build dirs anywhere in the tree (not just at repo root).
    parts = rel_posix.split("/")
    if "__pycache__" in parts or ".pytest_cache" in parts:
        return False

    for pref in EXCLUDE_DIR_PREFIXES:
        if rel_posix.startswith(pref):
            return False

    base = rel_posix.rsplit("/", 1)[-1]
    if base in EXCLUDE_BASENAMES:
        return False

    for suf in EXCLUDE_SUFFIXES:
        if rel_posix.endswith(suf):
            return False

    return True


def _zipinfo_for(rel_posix: str, src_path: pathlib.Path) -> zipfile.ZipInfo:
    zi = zipfile.ZipInfo(rel_posix)
    zi.compress_type = zipfile.ZIP_DEFLATED
    zi.date_time = FIXED_ZIP_DT

    # Normalize permissions to avoid cross-platform drift while preserving executability.
    try:
        mode = src_path.stat().st_mode
        is_executable = bool(mode & 0o111)
    except OSError:
        is_executable = False

    perm = 0o755 if is_executable else 0o644
    zi.external_attr = (perm & 0xFFFF) << 16
    return zi


def build_zip(repo_root: pathlib.Path, out_zip: pathlib.Path) -> None:
    repo_root = repo_root.resolve()
    out_zip = out_zip.resolve()

    if not repo_root.exists():
        raise SystemExit(f"Repo root does not exist: {repo_root}")

    out_zip.parent.mkdir(parents=True, exist_ok=True)

    # Collect files deterministically.
    rel_files: list[str] = []
    for p in sorted(repo_root.rglob("*")):
        if p.is_dir():
            continue
        rel = _normalize_rel(p.relative_to(repo_root))
        if not _should_include(rel):
            continue
        # Do not include the output ZIP if it lives under repo_root.
        if p.resolve() == out_zip:
            continue
        rel_files.append(rel)

    # Write ZIP deterministically.
    with zipfile.ZipFile(
        out_zip,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
        strict_timestamps=False,
    ) as zf:
        for rel in rel_files:
            src = repo_root / rel
            zi = _zipinfo_for(rel, src)
            with src.open("rb") as f:
                zf.writestr(zi, f.read())


def _default_out_zip(repo_root: pathlib.Path) -> pathlib.Path:
    version_file = repo_root / "VERSION"
    version = "unknown"
    if version_file.exists():
        version = version_file.read_text(encoding="utf-8").strip() or version
    return repo_root / "dist" / f"The-Election-Stack_{version}.zip"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="Repo root (default: .)")
    ap.add_argument("--out", default=None, help="Output zip path (default: dist/The-Election-Stack_<VERSION>.zip)")
    args = ap.parse_args()

    repo_root = pathlib.Path(args.root)
    out_zip = pathlib.Path(args.out) if args.out else _default_out_zip(repo_root)

    build_zip(repo_root, out_zip)
    print(out_zip)


if __name__ == "__main__":
    main()
