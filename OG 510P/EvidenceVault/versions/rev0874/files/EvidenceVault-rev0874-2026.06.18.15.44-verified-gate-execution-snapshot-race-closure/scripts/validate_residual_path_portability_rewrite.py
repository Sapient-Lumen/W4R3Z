#!/usr/bin/env python3
"""Validate the rev0831 residual path portability rewrite ledger."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from apply_residual_path_portability_rewrites import REPLACEMENTS, render_markdown  # noqa: E402


def fail(msg: str) -> None:
    print(f"residual-path-portability-rewrite-validate: FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def superseded_by_rev0832_trace_regeneration(row: dict) -> bool:
    if row.get("classification") != "preserve_serialized_path_object_bug_without_cloud_root":
        return False
    audit = ROOT / "AUDIT" / "OCF_TRACE_REGENERATION_REV0832.json"
    if not audit.is_file():
        return False
    try:
        data = json.loads(audit.read_text(encoding="utf-8"))
    except Exception:
        return False
    return (
        data.get("status") == "trace_regenerated_and_replayable"
        and data.get("target_trace") == row.get("path")
        and (data.get("current") or {}).get("bad_pattern_total") == 0
    )


def main() -> None:
    json_path = ROOT / "AUDIT" / "RESIDUAL_PATH_PORTABILITY_REWRITE_REV0831.json"
    md_path = ROOT / "AUDIT" / "RESIDUAL_PATH_PORTABILITY_REWRITE_REV0831.md"
    if not json_path.is_file() or not md_path.is_file():
        fail("missing residual path rewrite JSON or Markdown ledger")
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid JSON ledger: {exc}")
    rows = data.get("rows", [])
    if len(rows) != len(REPLACEMENTS):
        fail(f"expected {len(REPLACEMENTS)} rewrite rows, found {len(rows)}")
    for row in rows:
        path = ROOT / row["path"]
        if not path.is_file():
            fail(f"rewritten file missing: {row['path']}")
        text = path.read_text(encoding="utf-8")
        if row["old"] in text:
            fail(f"old cloud/container path still present in {row['path']}: {row['old']}")
        if row["new"] not in text:
            if not superseded_by_rev0832_trace_regeneration(row):
                fail(f"new portable path missing in {row['path']}: {row['new']}")
        if row["occurrences_rewritten"] < 1:
            fail(f"non-positive occurrence count for {row['path']}")
    expected_summary = {
        "replacement_rules": len(REPLACEMENTS),
        "files_touched": len({row["path"] for row in rows}),
        "occurrences_rewritten": sum(row["occurrences_rewritten"] for row in rows),
        "classifications": sorted(set(row["classification"] for row in rows)),
    }
    if data.get("summary") != expected_summary:
        fail("ledger summary does not match row totals")
    if md_path.read_text(encoding="utf-8") != render_markdown(data):
        fail("Markdown ledger does not exactly mirror JSON ledger")
    print(
        "residual-path-portability-rewrite-validate: OK "
        f"({expected_summary['files_touched']} files, {expected_summary['occurrences_rewritten']} occurrences)"
    )


if __name__ == "__main__":
    main()
