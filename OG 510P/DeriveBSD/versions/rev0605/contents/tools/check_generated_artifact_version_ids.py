#!/usr/bin/env python3
"""Ensure generated canonical examples bind durable IDs to their release token.

rev0502 found a serious stale-success pattern: generated r533 cube artifacts had
``generated_for_version = 2026-05-30r533`` while their durable IDs still ended in
r532, and the local checkers compared stale expected IDs against stale examples.
This guard scans canonical examples and makes that class of skew fail directly.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

from cube_check_lib import fail, generated_artifact_id_errors
from cube_digest_lib import load_json

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "spec" / "examples"
INVALID_DIR = EXAMPLES / "invalid" / "cube-generated-artifact-version-ids"

CHANGELOG_TOP_RE = re.compile(r"^##\s+(?P<version>\d{4}-\d{2}-\d{2}r\d{3,})\s*$", re.MULTILINE)
CURRENT_CUBE_GENERATED_KINDS = {
    "cube.schema.audit.report",
    "cube.schema.refactor.backlog",
    "cube.hygiene.checkset.manifest",
    "cube.hygiene.run.ledger",
}


def top_changelog_version() -> str:
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8", errors="replace")
    match = CHANGELOG_TOP_RE.search(text)
    if not match:
        fail("CHANGELOG.md has no top release heading shaped YYYY-MM-DDrNNN")
    return match.group("version")


def current_release_errors(obj: dict[str, Any], path: Path) -> list[str]:
    kind = obj.get("kind")
    if kind not in CURRENT_CUBE_GENERATED_KINDS:
        return []
    expected = top_changelog_version()
    observed = obj.get("generated_for_version")
    if observed != expected:
        return [
            f"{path.relative_to(ROOT).as_posix()}: generated_for_version={observed!r} must match latest CHANGELOG release {expected!r}"
        ]
    return []


def canonical_generated_examples() -> list[Path]:
    paths: list[Path] = []
    for path in sorted(EXAMPLES.glob("*.json")):
        obj = load_json(ROOT, path.relative_to(ROOT).as_posix())
        if isinstance(obj, dict) and "generated_for_version" in obj:
            paths.append(path)
    return paths


def semantic_errors_for_path(path: Path) -> list[str]:
    rel = path.relative_to(ROOT).as_posix()
    obj: Any = load_json(ROOT, rel)
    if not isinstance(obj, dict):
        return ["example root is not an object"]
    return generated_artifact_id_errors(obj) + current_release_errors(obj, path)


def check_positive_examples() -> list[str]:
    errors: list[str] = []
    examples = canonical_generated_examples()
    if not examples:
        return ["no canonical generated examples with generated_for_version found"]
    for path in examples:
        errs = semantic_errors_for_path(path)
        if errs:
            errors.append(f"{path.relative_to(ROOT).as_posix()}: " + "; ".join(errs))
    return errors


def check_negative_fixtures() -> list[str]:
    errors: list[str] = []
    if not INVALID_DIR.exists():
        return [f"missing negative fixture directory {INVALID_DIR.relative_to(ROOT).as_posix()}"]
    paths = sorted(INVALID_DIR.glob("*.json"))
    if not paths:
        return [f"no negative fixtures under {INVALID_DIR.relative_to(ROOT).as_posix()}"]
    for path in paths:
        errs = semantic_errors_for_path(path)
        if not errs:
            errors.append(f"{path.relative_to(ROOT).as_posix()}: expected release-id skew to fail")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true", help="list canonical generated examples covered by the guard")
    args = parser.parse_args()

    if args.list:
        for path in canonical_generated_examples():
            print(path.relative_to(ROOT).as_posix())
        return 0

    errors = check_positive_examples() + check_negative_fixtures()
    if errors:
        print("Generated artifact release-id check FAILED.")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Generated artifact release-id check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
