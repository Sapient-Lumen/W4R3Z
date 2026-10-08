#!/usr/bin/env python3
"""Build shipped-retention coverage from the upstream diff report and SOURCE_INDEX.

This surface is intentionally narrower than AUDIT/UPSTREAM_DIFF_REPORT.md.  The
upstream diff report may preserve historical upstream ZIP comparison context;
this builder answers one current-release boundary question only:

    What source material is actually retained in the shipped sources/ tree?

It therefore catches the class of drift where an audit report says that files are
present in sources/ after later pruning or representation decisions removed those
retained source roots.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROJECT_TO_SOURCE_INDEX_FAMILY = {
    "ctg": "ctg",
    "docf": "docf",
    "pact": "pact",
    "ocf_llm": "ocf_llm",
    "streamfold": "streamfold",
    "zkrtp_portfolio": "zkrtp",
    "zkrtp_v2": "zkrtp",
}
PROJECT_TO_EXPECTED_ROOT = {
    "ctg": "sources/ctg",
    "docf": "sources/docf",
    "pact": "sources/pact",
    "ocf_llm": "sources/ocf_llm",
    "streamfold": "sources/streamfold",
    "zkrtp_portfolio": "sources/zkrtp_portfolio",
    "zkrtp_v2": "sources/zkrtp_v2",
}
PROJECT_ORDER = list(PROJECT_TO_SOURCE_INDEX_FAMILY)
SECTION_RE = re.compile(r"^##\s+(?P<project>[A-Za-z0-9_]+)\s*$")
UPSTREAM_RE = re.compile(r"^- Upstream: `(?P<name>[^`]+)`$")
ZIP_FILES_RE = re.compile(r"^- Files in zip: \*\*(?P<count>\d+)\*\*$")
HISTORICAL_PRESENT_RE = re.compile(
    r"^- (?:Historical/audit-workspace files matched at source destination|Present in `sources/`): \*\*(?P<count>\d+)\*\*$"
)
RELOCATION_RE = re.compile(r"^- Present via relocation: \*\*(?P<count>\d+)\*\*$")
OMITTED_RE = re.compile(r"^- Omitted: \*\*(?P<count>\d+)\*\*$")


def file_count(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for p in path.rglob("*") if p.is_file())


def load_source_index(root: Path) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    idx = json.loads((root / "SOURCE_INDEX.json").read_text(encoding="utf-8"))
    retained = {entry["id"]: entry for entry in idx.get("source_roots", [])}
    represented = {entry["family"]: entry for entry in idx.get("represented_without_retained_source_root", [])}
    return retained, represented


def parse_upstream_report(root: Path) -> dict[str, dict[str, Any]]:
    path = root / "AUDIT" / "UPSTREAM_DIFF_REPORT.md"
    out: dict[str, dict[str, Any]] = {}
    current: str | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        m = SECTION_RE.match(line)
        if m:
            current = m.group("project")
            out.setdefault(current, {"project": current})
            continue
        if current is None:
            continue
        for key, regex in [
            ("upstream_zip", UPSTREAM_RE),
            ("upstream_file_count", ZIP_FILES_RE),
            ("historical_audit_workspace_present_in_sources", HISTORICAL_PRESENT_RE),
            ("present_via_relocation", RELOCATION_RE),
            ("omitted_by_governed_policy", OMITTED_RE),
        ]:
            m = regex.match(line)
            if m:
                value: str | int = m.groupdict().get("name") or m.groupdict().get("count") or ""
                if key != "upstream_zip":
                    value = int(value)
                out[current][key] = value
                break
    return out


def build(root: Path = ROOT) -> dict[str, Any]:
    retained, represented = load_source_index(root)
    report = parse_upstream_report(root)
    rows: list[dict[str, Any]] = []
    total_historical = 0
    total_actual = 0
    total_drift = 0
    for project in PROJECT_ORDER:
        family = PROJECT_TO_SOURCE_INDEX_FAMILY[project]
        expected_root = PROJECT_TO_EXPECTED_ROOT[project]
        report_row = report.get(project, {})
        retained_entry = retained.get(family)
        represented_entry = represented.get(family)
        if retained_entry:
            retention_status = "retained_source_root"
            shipped_root = retained_entry["retained_root"]
            source_index_file_count = int(retained_entry["file_count"])
            source_index_note = retained_entry.get("note", "")
        elif represented_entry:
            retention_status = "represented_without_retained_source_root"
            shipped_root = expected_root
            source_index_file_count = 0
            source_index_note = represented_entry.get("note", "")
        else:
            retention_status = "missing_from_SOURCE_INDEX"
            shipped_root = expected_root
            source_index_file_count = None
            source_index_note = ""
        actual_count = file_count(root / shipped_root)
        historical = int(report_row.get("historical_audit_workspace_present_in_sources", 0))
        drift = historical - actual_count
        total_historical += historical
        total_actual += actual_count
        total_drift += drift
        rows.append({
            "project": project,
            "source_index_family": family,
            "retention_status": retention_status,
            "upstream_zip": report_row.get("upstream_zip"),
            "upstream_file_count": report_row.get("upstream_file_count"),
            "historical_audit_workspace_present_in_sources": historical,
            "shipped_retained_source_root": shipped_root,
            "shipped_retained_source_file_count": actual_count,
            "source_index_file_count": source_index_file_count,
            "present_via_relocation": report_row.get("present_via_relocation"),
            "omitted_by_governed_policy": report_row.get("omitted_by_governed_policy"),
            "retention_drift_files": drift,
            "boundary_action": "ok" if drift == 0 else "relabel_historical_report_or_regenerate_from_shipped_tree",
            "source_index_note": source_index_note,
        })
    return {
        "version": 1,
        "revision_context": "rev0828-session-patch-over-rev0826",
        "purpose": "Current shipped retained-source coverage boundary check derived from SOURCE_INDEX.json, AUDIT/UPSTREAM_DIFF_REPORT.md, and the actual sources/ filesystem.",
        "inputs": ["SOURCE_INDEX.json", "AUDIT/UPSTREAM_DIFF_REPORT.md", "sources/"],
        "summary": {
            "projects_checked": len(rows),
            "historical_audit_workspace_present_in_sources_total": total_historical,
            "shipped_retained_source_file_count_total": total_actual,
            "retention_drift_files_total": total_drift,
            "projects_with_retention_drift": [row["project"] for row in rows if row["retention_drift_files"] != 0],
        },
        "projects": rows,
    }


def render_markdown(data: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Upstream retention coverage")
    lines.append("")
    lines.append("This is the current-release boundary surface for shipped retained sources. It deliberately separates historical upstream-diff matching from what is actually present under the shipped `sources/` tree.")
    lines.append("")
    lines.append("Inputs: `SOURCE_INDEX.json`, `AUDIT/UPSTREAM_DIFF_REPORT.md`, and the actual `sources/` filesystem.")
    lines.append("")
    s = data["summary"]
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Projects checked: **{s['projects_checked']}**")
    lines.append(f"- Historical/audit-workspace source matches: **{s['historical_audit_workspace_present_in_sources_total']}**")
    lines.append(f"- Shipped retained source files: **{s['shipped_retained_source_file_count_total']}**")
    lines.append(f"- Retention drift files: **{s['retention_drift_files_total']}**")
    drift_projects = s["projects_with_retention_drift"]
    lines.append("- Projects with retention drift: " + (", ".join(f"`{p}`" for p in drift_projects) if drift_projects else "none"))
    lines.append("")
    lines.append("## Project table")
    lines.append("")
    lines.append("| Project | Status | Historical source matches | Shipped retained root | Shipped retained files | Drift | Action |")
    lines.append("| --- | --- | ---: | --- | ---: | ---: | --- |")
    for row in data["projects"]:
        lines.append(
            "| "
            f"`{row['project']}` | `{row['retention_status']}` | "
            f"{row['historical_audit_workspace_present_in_sources']} | "
            f"`{row['shipped_retained_source_root']}` | "
            f"{row['shipped_retained_source_file_count']} | "
            f"{row['retention_drift_files']} | `{row['boundary_action']}` |"
        )
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("A nonzero drift value does not by itself prove data loss. It proves that an upstream-diff matching count is not the same thing as current shipped retained-source coverage. For represented families such as StreamFold and zk-RTP, the correct shipped count can be zero if the family is intentionally represented by curated artifacts, certificates, papers, and legacy renders instead of a retained `sources/` root.")
    lines.append("")
    lines.append("The release gate should fail if this file stops exactly matching the current filesystem or if `AUDIT/UPSTREAM_DIFF_REPORT.md` reintroduces the ambiguous old present-in-sources claim without the historical/audit-workspace qualifier.")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    root = Path(argv[1]) if len(argv) > 1 else ROOT
    data = build(root)
    audit = root / "AUDIT"
    audit.mkdir(parents=True, exist_ok=True)
    (audit / "UPSTREAM_RETENTION_COVERAGE.json").write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (audit / "UPSTREAM_RETENTION_COVERAGE.md").write_text(render_markdown(data), encoding="utf-8")
    print(
        "upstream-retention-coverage-build: OK "
        f"({data['summary']['projects_checked']} projects, "
        f"{data['summary']['retention_drift_files_total']} drift files)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
