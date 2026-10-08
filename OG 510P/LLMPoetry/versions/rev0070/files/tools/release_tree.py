#!/usr/bin/env python3
"""Canonical release-tree and deterministic ZIP safety primitives.

Manifesting, packaging, and post-package inspection all import this module so
path policy cannot silently diverge. Root ``do_rev*.py`` files are turn-local,
parent-dependent scaffolds and are excluded from release artifacts.
"""
from __future__ import annotations

import hashlib
import posixpath
import re
import stat
import zipfile
from pathlib import Path
from typing import Iterable

FIXED_DT = (1980, 1, 1, 0, 0, 0)
MANIFEST_EXCLUDE = {"MANIFEST.json", "MANIFEST.sha256", "CHECKSUMS.sha256", "reports/validation_report.json"}
PACKAGE_EXCLUDE = {"reports/validation_report.json"}
REVISION_CONSTRUCTOR_RE = re.compile(r"^do_rev\d{4}(?:_[A-Za-z0-9_-]+)?\.py$")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def is_revision_constructor(rel: str) -> bool:
    return "/" not in rel and bool(REVISION_CONSTRUCTOR_RE.fullmatch(rel))


def should_skip(rel: str, exclude: set[str] | frozenset[str]) -> bool:
    return (
        rel in exclude
        or rel.startswith(".git/")
        or rel.startswith("__pycache__/")
        or "/__pycache__/" in rel
        or is_revision_constructor(rel)
    )


def validate_rel(rel: str) -> None:
    norm = posixpath.normpath(rel)
    if (
        not rel
        or rel.startswith("/")
        or "\\" in rel
        or norm in {".", ".."}
        or norm.startswith("../")
        or norm != rel
        or any(ord(ch) < 32 or ord(ch) == 127 for ch in rel)
    ):
        raise ValueError(f"unsafe or non-canonical release path: {rel!r}")


def collect_files(root: Path, *, exclude: set[str] | frozenset[str]) -> list[tuple[Path, str]]:
    root = root.resolve()
    rows: list[tuple[Path, str]] = []
    casefold_owner: dict[str, str] = {}
    for path in sorted(root.rglob("*"), key=lambda p: p.relative_to(root).as_posix()):
        rel = path.relative_to(root).as_posix()
        if path.is_symlink():
            raise ValueError(f"symlink forbidden in release tree: {rel}")
        if not path.is_file() or should_skip(rel, exclude):
            continue
        validate_rel(rel)
        folded = rel.casefold()
        prior = casefold_owner.get(folded)
        if prior is not None and prior != rel:
            raise ValueError(f"case-fold path collision: {prior!r} vs {rel!r}")
        casefold_owner[folded] = rel
        rows.append((path, rel))
    return rows


def verify_release_zip(path: Path, expected: dict[str, str] | None = None) -> dict:
    failures: list[str] = []
    with zipfile.ZipFile(path, "r") as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if len(names) != len(set(names)):
            failures.append("duplicate member names")
        folded: dict[str, str] = {}
        for info in infos:
            name = info.filename
            try:
                validate_rel(name)
            except Exception as exc:
                failures.append(str(exc))
            if is_revision_constructor(name):
                failures.append(f"turn-local revision constructor packaged: {name}")
            prior = folded.get(name.casefold())
            if prior is not None and prior != name:
                failures.append(f"case-fold collision: {prior!r} vs {name!r}")
            folded[name.casefold()] = name
            mode = (info.external_attr >> 16) & 0o170000
            if mode != stat.S_IFREG:
                failures.append(f"non-regular member mode: {name} mode={oct(mode)}")
            if info.date_time != FIXED_DT:
                failures.append(f"non-deterministic timestamp: {name} {info.date_time}")
        if expected is not None:
            if set(names) != set(expected):
                failures.append(
                    "member set mismatch "
                    f"missing={sorted(set(expected) - set(names))[:5]} "
                    f"extra={sorted(set(names) - set(expected))[:5]}"
                )
            for name in sorted(set(names) & set(expected)):
                if sha256_bytes(archive.read(name)) != expected[name]:
                    failures.append(f"content hash mismatch: {name}")
    return {"ok": not failures, "member_count": len(names), "failures": failures}
