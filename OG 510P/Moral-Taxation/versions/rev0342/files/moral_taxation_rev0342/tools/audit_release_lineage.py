#!/usr/bin/env python3
"""Audit semantic release lineage, canonical naming, and timestamp agreement."""
from __future__ import annotations

import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
sys.path.insert(0, str(root / "tools"))
import release_lineage  # noqa: E402

errors, details = release_lineage.collect_lineage_errors(root)
cube = json.loads((root / "cube-index.json").read_text(encoding="utf-8"))
expected_summary = {
    "release_lineage_valid": not errors,
    "release_lineage_current_revision": details["revision"],
    "release_lineage_previous_revision": details["previous_revision"],
    "release_lineage_canonical_zip": details["canonical_zip"],
    "release_lineage_canonical_root": details["canonical_root"],
    "release_lineage_source_count": details["source_count"],
    "release_lineage_context_route_revisions": details["context_route_revisions"],
}
for key, value in expected_summary.items():
    if cube.get("audit_summary", {}).get(key) != value:
        errors.append(f"cube audit_summary {key} is stale")

report_rel = cube.get("release_lineage_audit_report_path")
report = root / report_rel if report_rel else None
if not report_rel or report is None or not report.exists():
    errors.append("cube-index.json release_lineage_audit_report_path must point to an existing file")
else:
    report_text = report.read_text(encoding="utf-8")
    expected_lines = [
        "Release lineage status: valid",
        f"Active revision: {details['revision']}",
        f"Previous revision: {details['previous_revision']}",
        f"Canonical output zip: {details['canonical_zip']}",
        f"Canonical archive root: {details['canonical_root']}",
        "Metadata timestamp agreement: yes",
        "Context routes carry active revision only: yes",
        f"Source count agreement: {details['source_count']}/{details['source_count']}",
    ]
    for line in expected_lines:
        if line not in report_text:
            errors.append(f"release lineage audit report missing line: {line}")

if errors:
    raise SystemExit("\n".join(errors))
print("release lineage audit: ok")
