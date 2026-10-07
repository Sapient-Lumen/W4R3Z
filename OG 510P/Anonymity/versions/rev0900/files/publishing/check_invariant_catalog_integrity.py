#!/usr/bin/env python3
"""Validate the invariant catalog, its Markdown mirror, and checked IDs."""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import sys
from typing import Any

INV_RE = re.compile(r"^INV-(\d{4})$")
MD_HEADING_RE = re.compile(r"^#{2,3} (INV-\d{4})\b", re.MULTILINE)


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def duplicate_values(values: list[str]) -> list[str]:
    counts = collections.Counter(values)
    return sorted([value for value, count in counts.items() if count > 1])


def render_markdown(catalog: dict[str, Any]) -> str:
    lines = ["# Archive Invariants", "", str(catalog.get("purpose", "Declare semantic archive invariants that should remain stable across future refactors, then check them directly rather than leaving them implicit.")), ""]
    for inv in catalog.get("invariants", []):
        lines.append(f"## {inv.get('id')} — {inv.get('title', '')}")
        lines.append("")
        lines.append(str(inv.get("statement", "")))
        lines.append("")
        anchors = inv.get("anchor_surfaces", [])
        lines.append("**Anchor surfaces:** " + ", ".join(f"`{p}`" for p in anchors))
        lines.append("")
        checked_by = inv.get("checked_by", [])
        lines.append("**Checked by:** " + ", ".join(f"`{p}`" for p in checked_by))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    catalog_path = root / "publishing" / "archive_invariants.json"
    report_path = root / "reports" / "archive_invariants.json"
    md_path = root / "publishing" / "ARCHIVE_INVARIANTS.md"
    catalog = load_json(catalog_path)
    inv_report = load_json(report_path)
    md_text = md_path.read_text(encoding="utf-8") if md_path.exists() else ""

    declared_ids = [str(inv.get("id", "")) for inv in catalog.get("invariants", [])]
    checked_ids = [str(row.get("id", "")) for row in inv_report.get("checks", [])]
    md_ids = MD_HEADING_RE.findall(md_text)
    declared_nums = [int(m.group(1)) for inv_id in declared_ids if (m := INV_RE.match(inv_id))]
    expected_nums = list(range(1, max(declared_nums or [0]) + 1))
    expected_md = render_markdown(catalog)

    checks: list[dict[str, Any]] = []

    def rec(name: str, ok: bool, details: Any) -> None:
        checks.append({"name": name, "status": "pass" if ok else "fail", "details": details})

    rec("catalog_revision_bound", isinstance(catalog.get("version"), int) and catalog.get("version", 0) >= 1 and bool(catalog.get("owner")) and bool(catalog.get("purpose")), {"version": catalog.get("version"), "owner": catalog.get("owner"), "purpose_present": bool(catalog.get("purpose"))})
    rec("declared_ids_unique", not duplicate_values(declared_ids), {"duplicates": duplicate_values(declared_ids)})
    rec("checked_ids_unique", not duplicate_values(checked_ids), {"duplicates": duplicate_values(checked_ids)})
    rec("declared_ids_well_formed", all(INV_RE.match(inv_id) for inv_id in declared_ids), {"bad_ids": [x for x in declared_ids if not INV_RE.match(x)]})
    rec("declared_ids_contiguous", declared_nums == expected_nums, {"declared_numbers": declared_nums, "expected_numbers": expected_nums})
    rec("declared_ids_match_checked_ids", set(declared_ids) == set(checked_ids), {"declared_not_checked": sorted(set(declared_ids) - set(checked_ids)), "checked_not_declared": sorted(set(checked_ids) - set(declared_ids))})
    rec("markdown_ids_match_declared_ids", md_ids == declared_ids, {"markdown_ids": md_ids, "declared_ids": declared_ids})
    rec("markdown_is_rendered_from_json", md_text == expected_md, {"matches": md_text == expected_md, "expected_length": len(expected_md), "actual_length": len(md_text)})
    rec("archive_invariant_report_passes", inv_report.get("status") == "pass" and inv_report.get("generated_for_revision") == release["revision"] and inv_report.get("checked_bundle") == release["bundle"], {"status": inv_report.get("status"), "revision": inv_report.get("generated_for_revision"), "bundle": inv_report.get("checked_bundle")})

    failures = [c for c in checks if c["status"] == "fail"]
    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "catalog": "publishing/archive_invariants.json",
        "markdown": "publishing/ARCHIVE_INVARIANTS.md",
        "archive_invariants_report": "reports/archive_invariants.json",
        "checks": checks,
        "summary": {
            "checks_passed": len(checks) - len(failures),
            "checks_failed": len(failures),
            "declared_invariant_count": len(declared_ids),
            "checked_invariant_count": len(checked_ids),
            "markdown_invariant_count": len(md_ids),
            "duplicate_declared_id_count": len(duplicate_values(declared_ids)),
            "duplicate_checked_id_count": len(duplicate_values(checked_ids)),
        },
        "failures": failures,
        "fail_closed_rule": "If the invariant catalog, checker report, or Markdown mirror disagree, default to no publication and repair invariant governance first.",
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
    sys.stdout.write(text)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
