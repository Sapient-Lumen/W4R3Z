#!/usr/bin/env python3
"""Create a filename-disciplined MTGSim linked-revision zip.

The helper intentionally does only packaging hygiene: it never changes engine
semantics, and it excludes cloud-container build/cache payloads that are useful
locally but wasteful or misleading in a linked revision artifact.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import os
import pathlib
import re
import sys
import time
import zipfile
from dataclasses import dataclass

os.environ.setdefault("TZ", "America/New_York")
if hasattr(time, "tzset"):
    time.tzset()

GLOBAL_EXCLUDED_DIR_NAMES = {".git", "__pycache__", ".pytest_cache"}
ROOT_EXCLUDED_DIR_NAMES = {"build"}
EXCLUDED_FILE_SUFFIXES = {".pyc", ".pyo", ".o", ".a", ".so", ".dylib", ".dll", ".exe"}
ROOT_EXCLUDED_DIR_GLOBS = {"cmake-build*"}
REPORT_DUPLICATE_SUFFIXES = (".stdout.json", "_stdout.json", ".stdout.txt", ".xml")
REPORT_BULK_SUFFIXES = ("_history.jsonl", ".sqlite", ".log")


def is_stale_generated_report(path: pathlib.Path, root: pathlib.Path, revision: str) -> bool:
    """Return True for bulky generated report artifacts that should not ride every zip.

    Linked revisions should carry source, docs, metadata, current/curated evidence, and
    the current revision's named reports. Historical per-revision report dumps, JUnit
    XML, stdout mirrors, SQLite metric stores, and JSONL histories are useful in the
    cloud container but become wasteful and easy to misread when copied forward in
    every linked artifact.
    """
    try:
        rel = path.relative_to(root)
    except ValueError:
        return False
    if not path.is_file() or not rel.parts or rel.parts[0] != "reports":
        return False
    name = path.name
    if name.endswith(REPORT_DUPLICATE_SUFFIXES) or name.endswith(REPORT_BULK_SUFFIXES):
        return True
    refs = sorted(set(re.findall(r"rev\d{4}", rel.as_posix())))
    return bool(refs and revision and revision not in refs)


@dataclass(frozen=True)
class PackagePlan:
    root: pathlib.Path
    output_dir: pathlib.Path
    archive_name: str
    revision: str


def should_exclude(path: pathlib.Path, root: pathlib.Path, archive_name: str, revision: str = "") -> bool:
    rel_parts = path.relative_to(root).parts
    if rel_parts:
        first = rel_parts[0]
        if first in ROOT_EXCLUDED_DIR_NAMES:
            return True
        if any(fnmatch.fnmatch(first, pattern) for pattern in ROOT_EXCLUDED_DIR_GLOBS):
            return True
    for part in rel_parts:
        if part in GLOBAL_EXCLUDED_DIR_NAMES:
            return True
    if path.is_file() and path.suffix in EXCLUDED_FILE_SUFFIXES:
        return True
    if path.name in {archive_name, f"{archive_name}.sha256"}:
        return True
    if is_stale_generated_report(path, root, revision):
        return True
    if path.as_posix().startswith((root / "data" / "rules" / "official" / "cache").as_posix() + "/"):
        return True
    return False


def collect_files(root: pathlib.Path, archive_name: str, revision: str = "") -> tuple[list[pathlib.Path], list[pathlib.Path]]:
    files: list[pathlib.Path] = []
    excluded: list[pathlib.Path] = []
    for path in sorted(root.rglob("*")):
        if path.is_dir():
            if should_exclude(path, root, archive_name, revision):
                excluded.append(path)
            continue
        if should_exclude(path, root, archive_name, revision):
            excluded.append(path)
            continue
        files.append(path)
    return files, excluded


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_integrity_report(plan: PackagePlan, files: list[pathlib.Path], excluded: list[pathlib.Path], zip_sha: str | None = None) -> pathlib.Path:
    report_dir = plan.root / "reports" / "package"
    report_dir.mkdir(parents=True, exist_ok=True)
    file_bytes = sum(path.stat().st_size for path in files)
    forbidden_cache_dirs = [p for p in excluded if p.is_dir() and p.name in {"__pycache__", ".pytest_cache"}]
    forbidden_build_dirs = [p for p in excluded if p.is_dir() and (p.relative_to(plan.root).parts[:1] == ("build",) or fnmatch.fnmatch(p.relative_to(plan.root).parts[0] if p.relative_to(plan.root).parts else "", "cmake-build*"))]
    text = "\n".join([
        f"# Zip integrity preflight — {plan.revision}",
        "",
        "Status: source tree ready for packaging.",
        f"Archive: {plan.archive_name}",
        f"Root: {plan.root.name}",
        f"Files: {len(files)}",
        f"Bytes: {file_bytes}",
        f"Excluded paths: {len(excluded)}",
        f"Forbidden cache dirs excluded: {len(forbidden_cache_dirs)}",
        f"Forbidden build dirs excluded: {len(forbidden_build_dirs)}",
        "Official rules cache excluded: True",
        f"SHA256: {zip_sha or 'emitted in sidecar after final zip creation'}",
        "",
        "Packaging policy: include source, docs, metadata, and curated current reports; exclude build outputs, object files, Python caches, private fetched official-rules cache payloads, stale per-revision report dumps, stdout/JUnit mirrors, JSONL histories, and SQLite metric stores.",
        "",
    ])
    rev_report = report_dir / f"zip_integrity_{plan.revision}.txt"
    latest_report = report_dir / "zip_integrity_latest.txt"
    rev_report.write_text(text, encoding="utf-8")
    latest_report.write_text(text, encoding="utf-8")
    return rev_report


def make_zip(plan: PackagePlan) -> tuple[pathlib.Path, str, int]:
    archive_path = plan.output_dir / plan.archive_name
    if archive_path.exists():
        archive_path.unlink()
    files, excluded = collect_files(plan.root, plan.archive_name, plan.revision)
    write_integrity_report(plan, files, excluded)
    files, excluded = collect_files(plan.root, plan.archive_name, plan.revision)
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in files:
            arcname = pathlib.PurePosixPath(plan.root.name) / path.relative_to(plan.root).as_posix()
            zf.write(path, arcname.as_posix())
    with zipfile.ZipFile(archive_path) as zf:
        bad = zf.testzip()
        if bad:
            raise RuntimeError(f"zip integrity test failed at {bad}")
    digest = sha256_file(archive_path)
    sidecar = archive_path.with_suffix(archive_path.suffix + ".sha256")
    sidecar.write_text(f"{digest}  {archive_path.name}\n", encoding="utf-8")
    return archive_path, digest, len(files)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path.cwd(), help="Source root to package")
    parser.add_argument("--out-dir", type=pathlib.Path, default=pathlib.Path.cwd().parent, help="Directory for the zip and .sha256 sidecar")
    parser.add_argument("--revision", required=True, help="Revision string such as rev0169")
    parser.add_argument("--archive-name", default=None, help="Archive filename; defaults to <root.name>.zip")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"root does not exist or is not a directory: {root}")
    archive_name = args.archive_name or f"{root.name}.zip"
    if not archive_name.endswith(".zip"):
        raise SystemExit("archive name must end in .zip")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    plan = PackagePlan(root=root, output_dir=args.out_dir.resolve(), archive_name=archive_name, revision=args.revision)
    archive_path, digest, file_count = make_zip(plan)
    print(f"archive={archive_path}")
    print(f"files={file_count}")
    print(f"sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
