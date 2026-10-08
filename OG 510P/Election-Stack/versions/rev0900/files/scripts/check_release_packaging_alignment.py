#!/usr/bin/env python3
"""Check that manifest scope and deterministic ZIP scope stay aligned.

This is a packaging drift firewall. ``MANIFEST.sha256`` intentionally excludes
itself, while the release ZIP intentionally includes it. Apart from that one
file, the manifest builder and deterministic ZIP builder must select the same
release payload. If their exclude rules drift apart, a local cache/transcript may
ship without being sealed, or a sealed file may be omitted from the archive.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.dont_write_bytecode = True

import build_manifest
import build_release_zip


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_NAME = "MANIFEST.sha256"


SYNTHETIC_EXCLUDES = [
    ".git/config",
    ".DS_Store",
    "debug.log",
    "dist/The-Election-Stack_v999.zip",
    "evidence/cache/downloaded-source.html",
    "tmp_emit_pvr/report.json",
    "__pycache__/tool.cpython-311.pyc",
    "docs/__pycache__/x.py",
    "scripts/check.pyc",
    "node_modules/pkg/index.js",
    "docs/name with space.md",
    "docs/newline\nname.md",
    "docs/nonascii-é.md",
]

SYNTHETIC_INCLUDES = [
    "README.md",
    "docs/162-release-and-ci-evidence-pipeline.md",
    "artifacts/examples/readme.log",  # nested logs are normative only if placed under governed dirs
]


def fail(msg: str) -> None:
    print("ERROR:", msg, file=sys.stderr)
    raise SystemExit(2)


def manifest_files_from_builder() -> set[str]:
    out: set[str] = set()
    for line in build_manifest.build_manifest_text().splitlines():
        if not line.strip():
            continue
        try:
            _sha, rel = line.split("  ", 1)
        except ValueError:
            fail(f"unparseable manifest line: {line!r}")
        out.add(rel)
    return out


def zip_files_from_builder_rules() -> set[str]:
    out: set[str] = set()
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(ROOT).as_posix()
        if build_release_zip._should_include(rel):  # intentional: compare the builder's actual predicate
            out.add(rel)
    return out


def main() -> int:
    manifest_files = manifest_files_from_builder()
    zip_files = zip_files_from_builder_rules()

    expected_zip_files = set(manifest_files)
    expected_zip_files.add(MANIFEST_NAME)

    missing_from_zip = sorted(expected_zip_files - zip_files)
    unsealed_in_zip = sorted(zip_files - expected_zip_files)

    if missing_from_zip or unsealed_in_zip:
        if missing_from_zip:
            print("ERROR: files sealed by MANIFEST.sha256 but omitted by build_release_zip.py:", file=sys.stderr)
            for rel in missing_from_zip[:50]:
                print(f"  - {rel}", file=sys.stderr)
            if len(missing_from_zip) > 50:
                print(f"  ... {len(missing_from_zip) - 50} more", file=sys.stderr)
        if unsealed_in_zip:
            print("ERROR: files selected by build_release_zip.py but not sealed by MANIFEST.sha256:", file=sys.stderr)
            for rel in unsealed_in_zip[:50]:
                print(f"  - {rel}", file=sys.stderr)
            if len(unsealed_in_zip) > 50:
                print(f"  ... {len(unsealed_in_zip) - 50} more", file=sys.stderr)
        return 2

    # Synthetic firewall: the two predicates must agree on known local-only
    # paths even when those files are not present in the maintainer tree.
    for rel in SYNTHETIC_EXCLUDES:
        m = build_manifest.should_include_rel(rel)
        z = build_release_zip._should_include(rel)
        if m or z:
            fail(f"synthetic local-only path should be excluded by both predicates: {rel!r} (manifest={m}, zip={z})")

    for rel in SYNTHETIC_INCLUDES:
        if rel == MANIFEST_NAME:
            continue
        m = build_manifest.should_include_rel(rel)
        z = build_release_zip._should_include(rel)
        if not (m and z):
            fail(f"synthetic normative path should be included by both predicates: {rel!r} (manifest={m}, zip={z})")

    print(f"PASS: release packaging scope aligned ({len(manifest_files)} manifest files + {MANIFEST_NAME})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
