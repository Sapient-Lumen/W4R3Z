#!/usr/bin/env python3
"""Scan shipped component payloads for rights/license evidence.

The scan does not infer a license grant. It gathers mechanical evidence that a
human rights decision needs: license-like files, SPDX identifiers, package
metadata license fields, copyright statements, and natural-language license
phrases inside the component payloads.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
JSON_OUT = ROOT / "RIGHTS" / "license_evidence_scan.json"
MD_OUT = ROOT / "RIGHTS" / "license_evidence_scan.md"
SKIP_DIR_PARTS = {".git", "__pycache__"}
MAX_SNIPPET = 220
SKIP_SCAN_REL = {
    "scripts/build_rights_evidence_scan.py",
    "scripts/validate_rights_evidence_scan.py",
    # This rev0834 script embeds a missing-license phrase as audit evidence;
    # it must not be reclassified as a rights claim for the scripts component.
    "scripts/build_external_license_evidence_candidates_rev0834.py",
    "scripts/validate_external_license_evidence_candidates_rev0834.py",
}

# Kept in sync with build_rights_readiness.COMPONENTS by importing at runtime in
# build(); this fallback makes the script easy to read in isolation.

LICENSE_FILE_RE = re.compile(
    r"(^|/)(license|licence|copying|notice|copyright|authors|contributors)(\.|$|[-_])",
    re.IGNORECASE,
)
SPDX_RE = re.compile(r"SPDX-License-Identifier:\s*([^\n\r*#;]+)", re.IGNORECASE)
COPYRIGHT_RE = re.compile(r"(?mi)^\s*(?:#\s*)?(?:Copyright(?::|\s*(?:\(c\)|©|\d{4})?)|©)\b[^\n\r]{0,180}")
LICENSE_PHRASE_RE = re.compile(
    r"\b(?:licensed under|released under|distributed under)\b[^\n\r]{0,180}",
    re.IGNORECASE,
)
LICENSE_LINK_RE = re.compile(
    r"\[(?:LICENSE|License|LICENCE|Licence)\]\((?P<md>[^)]+)\)|see\s+the\s+(?:\[(?:LICENSE|License|LICENCE|Licence)\]\((?P<see_md>[^)]+)\)|(?:LICENSE|License|LICENCE|Licence)\s+file)",
    re.IGNORECASE,
)
METADATA_FILENAMES = {
    "package.json", "pyproject.toml", "setup.cfg", "setup.py", "Cargo.toml",
    "go.mod", "pom.xml", "Gemfile", "DESCRIPTION", "METADATA", "PKG-INFO",
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def iter_files_under(paths: list[str]) -> set[Path]:
    files: set[Path] = set()
    for path_s in paths:
        path = ROOT / path_s.rstrip("/")
        if not path.exists():
            continue
        if path.is_file():
            files.add(path)
        else:
            for child in path.rglob("*"):
                if any(part in SKIP_DIR_PARTS for part in child.parts):
                    continue
                if child.is_file():
                    files.add(child)
    return files


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def snippet(value: str) -> str:
    compact = " ".join(value.strip().split())
    if len(compact) > MAX_SNIPPET:
        return compact[: MAX_SNIPPET - 1] + "…"
    return compact


def package_license_fields(path: Path, text: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    name = path.name
    if name == "package.json":
        try:
            obj = json.loads(text)
        except Exception:
            return out
        for key in ("license", "licenses"):
            if key in obj:
                out.append({"field": key, "value": obj[key]})
    elif name in {"pyproject.toml", "Cargo.toml"}:
        for m in re.finditer(r"(?m)^\s*license\s*=\s*([^#\n]+)", text):
            out.append({"field": "license", "value": snippet(m.group(1))})
    elif name == "setup.cfg":
        for m in re.finditer(r"(?mi)^\s*license\s*=\s*([^\n]+)", text):
            out.append({"field": "license", "value": snippet(m.group(1))})
    elif name in {"METADATA", "PKG-INFO"}:
        for m in re.finditer(r"(?mi)^License:\s*([^\n]+)", text):
            out.append({"field": "License", "value": snippet(m.group(1))})
    return out


def referenced_license_findings(path: Path, text: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for m in LICENSE_LINK_RE.finditer(text):
        target = m.group("md") or m.group("see_md") or "LICENSE"
        target = target.strip()
        # Ignore external URLs and anchors; this scan only checks shipped local evidence.
        if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.IGNORECASE) or target.startswith("#"):
            continue
        target_path = (path.parent / target).resolve()
        try:
            target_rel = target_path.relative_to(ROOT.resolve()).as_posix()
        except ValueError:
            target_rel = target
        key = target_rel.lower()
        if key in seen:
            continue
        seen.add(key)
        if target_path.is_file():
            out.append({"kind": "referenced_license_file_present", "value": target_rel})
        else:
            out.append({"kind": "referenced_license_file_missing", "value": target_rel})
    return out


def scan_file(path: Path) -> dict[str, Any] | None:
    r = rel(path)
    if r in SKIP_SCAN_REL:
        return None
    text = read_text(path)
    license_file = bool(LICENSE_FILE_RE.search(r))
    metadata_file = path.name in METADATA_FILENAMES
    findings: list[dict[str, Any]] = []
    if license_file:
        findings.append({"kind": "license_like_filename", "value": path.name})
    if text is not None:
        for m in SPDX_RE.finditer(text):
            findings.append({"kind": "spdx_license_identifier", "value": snippet(m.group(1))})
        for field in package_license_fields(path, text):
            findings.append({"kind": "package_metadata_license_field", **field})
        for m in LICENSE_PHRASE_RE.finditer(text):
            findings.append({"kind": "license_phrase", "value": snippet(m.group(0))})
        findings.extend(referenced_license_findings(path, text))
        for m in COPYRIGHT_RE.finditer(text):
            findings.append({"kind": "copyright_statement", "value": snippet(m.group(0))})
    elif license_file or metadata_file:
        findings.append({"kind": "non_utf8_candidate", "value": "candidate file could not be decoded as UTF-8"})
    if not findings:
        return None
    # Deduplicate while preserving order.
    seen: set[str] = set()
    unique_findings: list[dict[str, Any]] = []
    for finding in findings:
        key = json.dumps(finding, sort_keys=True)
        if key in seen:
            continue
        seen.add(key)
        unique_findings.append(finding)
    return {"path": r, "findings": unique_findings}


def build(root: Path = ROOT) -> dict[str, Any]:
    global ROOT
    old_root = ROOT
    ROOT = root
    try:
        from build_rights_readiness import COMPONENTS  # type: ignore

        component_rows = []
        totals = Counter()
        for component in COMPONENTS:
            files = sorted(iter_files_under(component["paths"]), key=rel)
            scan_rows = []
            finding_counts = Counter()
            for path in files:
                scanned = scan_file(path)
                if scanned is None:
                    continue
                scan_rows.append(scanned)
                for finding in scanned["findings"]:
                    finding_counts[finding["kind"]] += 1
            row = {
                "component_id": component["component_id"],
                "paths": component["paths"],
                "files_examined": len(files),
                "files_with_rights_evidence": len(scan_rows),
                "finding_counts": dict(sorted(finding_counts.items())),
                "sample_rows": scan_rows[:40],
            }
            component_rows.append(row)
            totals["files_examined"] += len(files)
            totals["files_with_rights_evidence"] += len(scan_rows)
            for kind, count in finding_counts.items():
                totals[f"finding:{kind}"] += count
        aggregate_finding_counts = {
            key.removeprefix("finding:"): value
            for key, value in sorted(totals.items())
            if key.startswith("finding:")
        }
        return {
            "version": 1,
            "revision_context": "rev0831-session-patch-over-rev0830-over-rev0826",
            "status": "evidence_scan_complete_license_conclusions_still_noassertion",
            "purpose": "Gather mechanically discoverable rights/license evidence without concluding redistribution rights.",
            "summary": {
                "components_examined": len(component_rows),
                "files_examined": totals["files_examined"],
                "files_with_rights_evidence": totals["files_with_rights_evidence"],
                "aggregate_finding_counts": aggregate_finding_counts,
            },
            "interpretation": {
                "does_not_grant_license": True,
                "license_conclusion_policy": "retain NOASSERTION until an owner/upstream rights decision adds a root LICENSE/NOTICE and component conclusions",
                "highest_risk_current_result": "no root license-like file was found by the readiness validator; component evidence is sparse, and one detected license phrase points to a LICENSE file that is not shipped beside the phrase",
            },
            "components": component_rows,
            "builder": "scripts/build_rights_evidence_scan.py",
            "validator": "scripts/validate_rights_evidence_scan.py",
        }
    finally:
        ROOT = old_root


def render_markdown(data: dict[str, Any]) -> str:
    s = data["summary"]
    lines = [
        "# Rights evidence scan",
        "",
        "This scan gathers license/rights clues from shipped component payloads. It does **not** grant a license and does **not** replace the component license ledger.",
        "",
        f"- Status: `{data['status']}`",
        f"- Components examined: **{s['components_examined']}**",
        f"- Files examined: **{s['files_examined']}**",
        f"- Files with rights evidence: **{s['files_with_rights_evidence']}**",
        "",
        "## Aggregate finding counts",
        "",
        "| Finding kind | Count |",
        "| --- | ---: |",
    ]
    for kind, count in s["aggregate_finding_counts"].items():
        lines.append(f"| `{kind}` | {count} |")
    if not s["aggregate_finding_counts"]:
        lines.append("| none | 0 |")
    lines.extend([
        "",
        "## Interpretation",
        "",
        f"- Does not grant license: `{str(data['interpretation']['does_not_grant_license']).lower()}`",
        f"- License conclusion policy: {data['interpretation']['license_conclusion_policy']}",
        f"- Highest-risk current result: {data['interpretation']['highest_risk_current_result']}",
        "",
        "## Component results",
        "",
        "| Component | Files examined | Files with evidence | Finding counts |",
        "| --- | ---: | ---: | --- |",
    ])
    for row in data["components"]:
        counts = ", ".join(f"`{k}`={v}" for k, v in row["finding_counts"].items()) or "none"
        lines.append(f"| `{row['component_id']}` | {row['files_examined']} | {row['files_with_rights_evidence']} | {counts} |")
    lines.extend(["", "## Evidence samples", ""])
    for row in data["components"]:
        if not row["sample_rows"]:
            continue
        lines.extend([f"### `{row['component_id']}`", "", "| Path | Findings |", "| --- | --- |"])
        for sample in row["sample_rows"]:
            finding_text = "<br>".join(
                f"`{finding['kind']}`: {finding.get('value', finding.get('field', ''))}"
                for finding in sample["findings"][:6]
            )
            lines.append(f"| `{sample['path']}` | {finding_text} |")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    data = build(ROOT)
    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_OUT.write_text(render_markdown(data), encoding="utf-8")
    print(
        "rights-evidence-scan-build: OK "
        f"({data['summary']['files_with_rights_evidence']} evidence files / "
        f"{data['summary']['files_examined']} examined)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
