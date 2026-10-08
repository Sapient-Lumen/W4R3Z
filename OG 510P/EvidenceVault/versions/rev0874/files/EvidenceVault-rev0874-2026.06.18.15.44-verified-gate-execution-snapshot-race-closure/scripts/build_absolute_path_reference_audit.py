#!/usr/bin/env python3
"""Build an audit of cloud/container absolute paths embedded in text payloads.

The filesystem policy validator catches unsafe shipped paths.  This audit catches
non-portable *content references* such as /mnt/data/... that can survive inside
JSON/YAML/prose payloads and mislead downstream replay or provenance review.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
JSON_OUT = ROOT / "AUDIT" / "ABSOLUTE_PATH_REFERENCE_AUDIT.json"
MD_OUT = ROOT / "AUDIT" / "ABSOLUTE_PATH_REFERENCE_AUDIT.md"
PATH_RE = re.compile(r"/(?:mnt/data|home/oai)/[^\s\"'\)\]\}\,<`]+")
SKIP_REL = {
    "AUDIT/ABSOLUTE_PATH_REFERENCE_AUDIT.json",
    "AUDIT/ABSOLUTE_PATH_REFERENCE_AUDIT.md",
    "AUDIT/PATH_NORMALIZATION_PATCH_REV0829.json",
    "AUDIT/PATH_NORMALIZATION_PATCH_REV0829.md",
    "AUDIT/PATH_PORTABILITY_REWRITE_REV0830.json",
    "AUDIT/PATH_PORTABILITY_REWRITE_REV0830.md",
    "AUDIT/RESIDUAL_PATH_PORTABILITY_REWRITE_REV0831.json",
    "AUDIT/RESIDUAL_PATH_PORTABILITY_REWRITE_REV0831.md",
    "scripts/build_absolute_path_reference_audit.py",
    "scripts/validate_absolute_path_reference_audit.py",
    "scripts/apply_path_portability_rewrites.py",
    "scripts/validate_path_portability_rewrite.py",
    "scripts/apply_residual_path_portability_rewrites.py",
    "scripts/validate_residual_path_portability_rewrite.py",
}
SKIP_DIR_PARTS = {".git", "__pycache__"}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def iter_text_files(root: Path = ROOT):
    for path in sorted(root.rglob("*")):
        if any(part in SKIP_DIR_PARTS for part in path.parts):
            continue
        if not path.is_file():
            continue
        r = rel(path)
        if r in SKIP_REL:
            continue
        try:
            path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        yield path


def family_for_path(r: str) -> str:
    parts = r.split("/")
    if len(parts) >= 3 and parts[0] == "sources":
        return f"sources/{parts[1]}"
    if len(parts) >= 3 and parts[0] in {"artifacts", "certs"} and parts[1] == "curated":
        return f"{parts[0]}/curated/{parts[2]}"
    if len(parts) >= 2:
        return "/".join(parts[:2])
    return parts[0]


def build(root: Path = ROOT) -> dict[str, Any]:
    global ROOT
    old_root = ROOT
    ROOT = root
    try:
        rows = []
        for path in iter_text_files(ROOT):
            r = rel(path)
            text = path.read_text(encoding="utf-8")
            matches = PATH_RE.findall(text)
            if not matches:
                continue
            unique = sorted(set(matches))
            rows.append({
                "path": r,
                "family": family_for_path(r),
                "match_count": len(matches),
                "unique_match_count": len(unique),
                "sample_matches": unique[:5],
                "suggested_action": "normalize_to_shipped_relative_path_when_target_is_shipped_else_ledger_as_historical_external_build_path",
            })
        rows.sort(key=lambda row: (row["family"], row["path"]))
        by_family = Counter()
        by_family_matches = Counter()
        for row in rows:
            by_family[row["family"]] += 1
            by_family_matches[row["family"]] += row["match_count"]
        summary_by_family = [
            {
                "family": fam,
                "files_with_references": by_family[fam],
                "reference_count": by_family_matches[fam],
            }
            for fam in sorted(by_family)
        ]
        return {
            "version": 1,
            "revision_context": "rev0831-session-patch-over-rev0830-over-rev0826",
            "purpose": "Inventory cloud/container absolute path references embedded in text payload content; these are not filesystem paths but can weaken portability and replay clarity.",
            "patterns": ["/mnt/data/...", "/home/oai/..."],
            "status": "portability_triage_required" if rows else "no_cloud_container_absolute_paths_found",
            "summary": {
                "files_scanned_as_utf8_text": sum(1 for _ in iter_text_files(ROOT)),
                "files_with_absolute_path_references": len(rows),
                "absolute_path_reference_count": sum(row["match_count"] for row in rows),
                "families_with_references": len(summary_by_family),
            },
            "summary_by_family": summary_by_family,
            "rows": rows,
            "builder": "scripts/build_absolute_path_reference_audit.py",
            "validator": "scripts/validate_absolute_path_reference_audit.py",
        }
    finally:
        ROOT = old_root


def render_markdown(data: dict[str, Any]) -> str:
    s = data["summary"]
    lines = [
        "# Absolute path reference audit",
        "",
        "This audit inventories cloud/container absolute paths embedded inside text payloads. It complements filesystem path validation: the shipped file names can be safe while the file contents still contain stale `/mnt/data/...` or `/home/oai/...` references.",
        "",
        f"- Status: `{data['status']}`",
        f"- UTF-8 text files scanned: **{s['files_scanned_as_utf8_text']}**",
        f"- Files with cloud/container absolute path references: **{s['files_with_absolute_path_references']}**",
        f"- Total matching references: **{s['absolute_path_reference_count']}**",
        f"- Families/areas with references: **{s['families_with_references']}**",
        "",
        "## By family/area",
        "",
        "| Family/area | Files | References |",
        "| --- | ---: | ---: |",
    ]
    for row in data["summary_by_family"]:
        lines.append(f"| `{row['family']}` | {row['files_with_references']} | {row['reference_count']} |")
    lines.extend([
        "",
        "## Highest-impact interpretation",
        "",
        "These references are not necessarily secrets and do not prove data loss. They do prove that some evidence payloads still carry build-host coordinates. For portability, replay, and publication, normalize references to shipped relative paths when the target exists in the archive; otherwise keep an explicit historical-external-path ledger so readers know the path is provenance context rather than an expected local file.",
        "",
        "## Files with references",
        "",
        "| Path | Matches | Unique | Sample |",
        "| --- | ---: | ---: | --- |",
    ])
    for row in data["rows"]:
        sample = "<br>".join(f"`{m}`" for m in row["sample_matches"])
        lines.append(f"| `{row['path']}` | {row['match_count']} | {row['unique_match_count']} | {sample} |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    data = build(ROOT)
    JSON_OUT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_OUT.write_text(render_markdown(data), encoding="utf-8")
    print(
        "absolute-path-reference-audit-build: OK "
        f"({data['summary']['files_with_absolute_path_references']} files, "
        f"{data['summary']['absolute_path_reference_count']} references)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
