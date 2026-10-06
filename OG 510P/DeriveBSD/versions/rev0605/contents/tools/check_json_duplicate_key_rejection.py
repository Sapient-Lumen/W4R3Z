#!/usr/bin/env python3
"""Reject duplicate-key and non-JSON numeric drift in checked-in JSON.

The cube now has a shared restricted-JCS/I-JSON loader for hash-bound JSON, but
many older checkers still use plain ``json.loads`` for ordinary schema/example
reading.  This guard closes the dangerous gap at the repository boundary: every
checked-in JSON artifact under the active evidence/spec/doc surfaces must parse
with duplicate object members rejected and NaN/Infinity tokens refused.
"""
from __future__ import annotations

from pathlib import Path

from cube_digest_lib import CanonicalJsonError, load_json_strict_text

ROOT = Path(__file__).resolve().parents[1]
SCAN_ROOTS = [
    "docs/_generated",
    "session-reviews",
    "spec",
    "tools/baselines",
    "validation",
]
REQUIRED_STRICT_LOADERS = {
    "tools/lint_spec_schemas.py": ["load_json_strict_text", "duplicate-key"],
    "tools/validate_spec_examples.py": ["load_json_strict_text", "duplicate-key"],
    "tools/check_schema_kind_matches_filename.py": ["load_json_strict_text", "duplicate-key"],
}


def _repo_json_paths() -> list[Path]:
    paths: list[Path] = []
    for rel in SCAN_ROOTS:
        root = ROOT / rel
        if not root.exists():
            continue
        paths.extend(p for p in root.rglob("*.json") if p.is_file())
    return sorted(paths)


def _self_test_errors() -> list[str]:
    errors: list[str] = []
    bad_cases = {
        "duplicate object member": '{"a":1,"a":2}',
        "nan token": '{"a": NaN}',
        "infinity token": '{"a": Infinity}',
    }
    for label, payload in bad_cases.items():
        try:
            load_json_strict_text(payload)
        except CanonicalJsonError:
            continue
        errors.append(f"strict JSON loader failed to reject {label}")
    return errors


def _source_wiring_errors() -> list[str]:
    errors: list[str] = []
    for rel, tokens in REQUIRED_STRICT_LOADERS.items():
        text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        for token in tokens:
            if token not in text:
                errors.append(f"{rel} must document/use strict JSON loading token {token!r}")
    return errors


def main() -> int:
    errors = _self_test_errors() + _source_wiring_errors()
    scanned = 0
    for path in _repo_json_paths():
        scanned += 1
        try:
            load_json_strict_text(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001 - surface exact path in one guard
            errors.append(f"{path.relative_to(ROOT).as_posix()}: strict JSON parse failed: {exc}")
    if errors:
        print("Strict JSON duplicate-key guard FAILED.")
        for error in errors:
            print("-", error)
        return 1
    print(f"Strict JSON duplicate-key guard OK ({scanned} JSON files scanned)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
