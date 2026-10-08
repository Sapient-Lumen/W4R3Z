#!/usr/bin/env python3
"""Check the release path policy used by manifest, ZIP, and extraction probes.

This is a maintainer-control firewall.  Release members are newline-oriented in
MANIFEST.sha256 and POSIX-style in the deterministic ZIP, so ambiguous names
such as whitespace-bearing paths, control characters, traversal components, and
backslash paths are not allowed to enter release scope.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.dont_write_bytecode = True

import build_manifest
import build_release_zip
import release_path_policy

ROOT = Path(__file__).resolve().parents[1]

SYNTHETIC_BAD_PATHS = [
    "",
    "../outside.txt",
    "docs/../outside.txt",
    "/absolute/path.txt",
    "C:/windows-drive.txt",
    "docs/name:colon.md",
    "docs/name?.md",
    "docs/name*.md",
    "docs/name|pipe.md",
    "docs/con.txt",
    "docs/AUX.json",
    "docs/trailing-dot.",
    "docs//double-slash.md",
    "docs/./current.md",
    "docs/name with space.md",
    " leading-space.md",
    "trailing-space.md ",
    "docs/trailing-component /x.md",
    "docs/newline\nname.md",
    "docs/tab\tname.md",
    "docs/back\\slash.md",
    "docs/nonascii-é.md",
]

SYNTHETIC_GOOD_PATHS = [
    "README.md",
    "./README.md",
    "docs/162-release-and-ci-evidence-pipeline.md",
    "artifacts/examples/evidence_packet_minimal/manifest.json",
]


def fail(msg: str) -> None:
    print("ERROR:", msg, file=sys.stderr)
    raise SystemExit(2)


def iter_existing_paths() -> list[str]:
    out: list[str] = []
    for p in ROOT.rglob("*"):
        rel = p.relative_to(ROOT).as_posix()
        if build_manifest.is_local_only_rel(rel):
            continue
        out.append(rel)
    return sorted(out)


def main() -> int:
    problems: list[str] = []

    existing_paths = iter_existing_paths()
    for rel in existing_paths:
        problem = release_path_policy.release_path_problem(rel)
        if problem:
            problems.append(f"{rel!r}: {problem}")

    collisions = release_path_policy.find_portable_path_collisions(existing_paths)
    for key, vals in sorted(collisions.items()):
        problems.append(f"portable path collision for {key!r}: {vals}")

    synthetic_collisions = release_path_policy.find_portable_path_collisions([
        "docs/Portable-Name.md",
        "docs/portable-name.md",
    ])
    if not synthetic_collisions:
        problems.append("synthetic case-insensitive path collision unexpectedly passed")

    synthetic_shape_conflicts = release_path_policy.find_extraction_shape_conflicts([
        "objects/prefix",
        "objects/prefix/child.json",
    ])
    if not synthetic_shape_conflicts:
        problems.append("synthetic file/directory extraction shape conflict unexpectedly passed")

    for rel in SYNTHETIC_BAD_PATHS:
        problem = release_path_policy.release_path_problem(rel)
        m = build_manifest.should_include_rel(rel)
        z = build_release_zip._should_include(rel)
        if problem is None:
            problems.append(f"synthetic bad path unexpectedly passed policy: {rel!r}")
        if m or z:
            problems.append(f"synthetic bad path selected by package predicates: {rel!r} (manifest={m}, zip={z})")

    for rel in SYNTHETIC_GOOD_PATHS:
        problem = release_path_policy.release_path_problem(rel)
        m = build_manifest.should_include_rel(rel)
        z = build_release_zip._should_include(rel)
        if problem is not None:
            problems.append(f"synthetic good path rejected by policy: {rel!r}: {problem}")
        if not (m and z):
            problems.append(f"synthetic good path rejected by package predicates: {rel!r} (manifest={m}, zip={z})")

    root = Path("/tmp/tes_extract_root")
    safe = release_path_policy.safe_extract_destination(root, "docs/ok.md")
    unsafe = release_path_policy.safe_extract_destination(root, "../outside.md")
    sibling = release_path_policy.safe_extract_destination(root, "/tmp/tes_extract_root_sibling/evil.md")
    if safe is None or safe.name != "ok.md":
        problems.append("safe_extract_destination rejected a safe relative member")
    if unsafe is not None:
        problems.append("safe_extract_destination accepted traversal member")
    if sibling is not None:
        problems.append("safe_extract_destination accepted sibling-prefix escape")

    if problems:
        print("FAIL: release path policy drift")
        for p in problems[:50]:
            print("  -", p)
        if len(problems) > 50:
            print(f"  ... {len(problems) - 50} more")
        return 2

    print(f"PASS: release path policy ({len(existing_paths)} governed paths checked; portable namespace and extraction tree shape unique)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
