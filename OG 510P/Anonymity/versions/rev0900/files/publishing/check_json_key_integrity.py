#!/usr/bin/env python3
"""Reject ambiguous JSON parser behavior across the shipped archive.

Python's json loader silently keeps the last value for duplicate object keys and
accepts non-finite numeric constants unless told otherwise.  Both behaviors are
unsafe for governance surfaces: two readers may see different intent, or a value
may not be valid portable JSON.  This checker parses every JSON file with
duplicate-key and non-finite constants rejected.
"""

from __future__ import annotations

import argparse
import json
import pathlib
from collections import Counter
from typing import Any


def load_release(root: pathlib.Path) -> dict[str, Any]:
    return json.loads((root / "RELEASE_MANIFEST.json").read_text(encoding="utf-8"))


def duplicate_rejecting_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    counts = Counter(key for key, _ in pairs)
    duplicates = sorted(key for key, count in counts.items() if count > 1)
    if duplicates:
        raise ValueError("duplicate JSON object keys: " + ", ".join(duplicates))
    return dict(pairs)


def reject_nonfinite_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON numeric literal rejected: {value}")


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_release(root)
    rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    duplicate_failures = 0
    nonfinite_failures = 0
    other_failures = 0
    for path in sorted(root.rglob("*.json"), key=lambda p: p.relative_to(root).as_posix()):
        rel = path.relative_to(root).as_posix()
        try:
            json.loads(
                path.read_text(encoding="utf-8"),
                object_pairs_hook=duplicate_rejecting_hook,
                parse_constant=reject_nonfinite_constant,
            )
            row = {"path": rel, "status": "pass"}
        except Exception as exc:  # noqa: BLE001 - diagnostics belong in the report
            error = str(exc)
            category = "json_parse_policy_failure"
            if "duplicate JSON object keys" in error:
                duplicate_failures += 1
                category = "duplicate_object_key"
            elif "non-finite JSON numeric literal" in error:
                nonfinite_failures += 1
                category = "non_finite_numeric_literal"
            else:
                other_failures += 1
            row = {"path": rel, "status": "fail", "category": category, "error": error}
            failures.append(row)
        rows.append(row)

    summary = {
        "checks_failed": len(failures),
        "json_file_count": len(rows),
        "duplicate_key_failure_count": duplicate_failures,
        "non_finite_numeric_literal_failure_count": nonfinite_failures,
        "other_json_parse_failure_count": other_failures,
        "checked_with_duplicate_rejecting_parser": True,
        "checked_with_nonfinite_rejecting_parser": True,
    }
    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "parser_policy": "reject_duplicate_object_keys_and_nonfinite_numeric_literals_for_every_json_file",
        "json_file_count": len(rows),
        "failures": failures[:100],
        "sample_checked_paths": [row["path"] for row in rows[:10]],
        "summary": summary,
        "fail_closed_rule": "If any JSON file contains duplicate keys or non-finite numeric literals, default to no publication and rewrite the surface so every JSON parser sees one unambiguous portable object value per key.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--write-report", default="")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    report = check(root)
    text = json.dumps(report, indent=2) + "\n"
    if args.write_report:
        out = root / args.write_report
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
