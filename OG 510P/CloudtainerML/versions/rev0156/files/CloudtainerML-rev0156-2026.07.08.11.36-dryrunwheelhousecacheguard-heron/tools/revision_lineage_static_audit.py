#!/usr/bin/env python3
"""Static revision-lineage audit for CloudtainerML runnable Python surfaces.

The audit detects a subtle provenance hazard: historical experiment scripts that
read the *current* CUBE-META revision and use it in artifact paths. Re-running
such a script can mint a current-revision filename from historical code, often
while retaining a hard-coded historical timestamp. That is revision laundering,
not a valid new scientific run.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = str(META.get("revision", "rev0076"))
REVUP = REV.upper()
STAMP = str(META.get("generated_at") or META.get("created_at") or "unknown")
OUT_JSON = ROOT / "artifacts" / "audit" / f"{REVUP}_REVISION_LINEAGE_STATIC_AUDIT.json"
OUT_MD = ROOT / "artifacts" / "audit" / f"{REVUP}_REVISION_LINEAGE_STATIC_AUDIT.md"

DYNAMIC_REV_RE = re.compile(
    r"\bREV\s*=\s*META\.get\(\s*['\"]revision['\"]\s*,\s*['\"](rev\d{4})['\"]\s*\)"
)
PINNED_REV_RE = re.compile(r"\b(?:ORIGINAL_REV|REV)\s*=\s*['\"](rev\d{4})['\"]")
STAMP_RE = re.compile(r"\bSTAMP\s*=\s*['\"](\d{4}-\d{2}-\d{2}T[^'\"]+)['\"]")
REV_LITERAL_RE = re.compile(r"rev(\d{4})")

PROTECTED_HISTORICAL = {
    "experiments/public_trace_capture_kit/public_trace_capture_kit.py": "rev0074",
    "experiments/public_trace_e2e_ingest_contract/public_trace_e2e_ingest_contract.py": "rev0073",
    "experiments/public_trace_claim_contract/public_trace_claim_contract.py": "rev0072",
    "tools/public_trace_capture_kit_audit.py": "rev0074",
    "tools/public_trace_e2e_ingest_contract_audit.py": "rev0073",
    "tools/public_trace_claim_contract_audit.py": "rev0072",
}


def revision_int(value: str | None) -> int | None:
    if not value:
        return None
    match = REV_LITERAL_RE.fullmatch(value)
    return int(match.group(1)) if match else None


def scan_file(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    rel = path.relative_to(ROOT).as_posix()
    dynamic_match = DYNAMIC_REV_RE.search(text)
    pinned_matches = PINNED_REV_RE.findall(text)
    hardcoded_stamp = STAMP_RE.search(text)
    dynamic = dynamic_match is not None
    fallback = dynamic_match.group(1) if dynamic_match else None
    pinned = None
    if not dynamic:
        # Prefer a literal REV assignment over an ORIGINAL_REV declaration when
        # both exist; they should agree, but the list is retained for review.
        pinned = pinned_matches[-1] if pinned_matches else None
    writes_artifacts = bool(
        "artifacts" in text
        and (
            "write_text(" in text
            or "json.dump" in text
            or "np.save" in text
            or "open(" in text
            or "subprocess.run" in text
        )
    )
    revision_in_output_path = bool("REVUP" in text or re.search(r"f['\"][^'\"]*\{REV\}", text))
    executable = "if __name__" in text
    scope = rel.split("/", 1)[0]
    historical_marker = any(
        marker in text
        for marker in [
            "HISTORICAL_RUNNER = True",
            "HISTORICAL_AUDIT = True",
            "frozen historical",
            "historical-only",
        ]
    )
    current_n = revision_int(REV)
    fallback_n = revision_int(fallback)
    dynamic_historical = bool(
        dynamic
        and fallback_n is not None
        and current_n is not None
        and fallback_n not in {0, current_n}
    )
    output_minting_risk = bool(dynamic_historical and writes_artifacts and revision_in_output_path)
    timestamp_contradiction_risk = bool(output_minting_risk and hardcoded_stamp)
    reasons: list[str] = []
    if output_minting_risk:
        reasons.append("historical runner inherits current CUBE-META revision in artifact paths")
    if timestamp_contradiction_risk:
        reasons.append("dynamic revision is paired with a hard-coded historical timestamp")
    if scope == "tools" and output_minting_risk:
        reasons.append("legacy audit/report can write current-labelled output for historical logic")
    severity = "none"
    if timestamp_contradiction_risk:
        severity = "high"
    elif output_minting_risk and scope == "experiments":
        severity = "high"
    elif output_minting_risk:
        severity = "medium"
    return {
        "path": rel,
        "scope": scope,
        "executable": executable,
        "dynamic_current_revision": dynamic,
        "fallback_revision": fallback,
        "pinned_revision": pinned,
        "pinned_revision_literals": pinned_matches,
        "hardcoded_timestamp": hardcoded_stamp.group(1) if hardcoded_stamp else None,
        "writes_artifacts": writes_artifacts,
        "revision_in_output_path": revision_in_output_path,
        "historical_marker": historical_marker,
        "dynamic_historical": dynamic_historical,
        "output_minting_risk": output_minting_risk,
        "timestamp_contradiction_risk": timestamp_contradiction_risk,
        "severity": severity,
        "reasons": reasons,
    }


def scan_revision_lineage() -> dict[str, Any]:
    rows = [
        scan_file(path)
        for base in (ROOT / "experiments", ROOT / "tools")
        for path in sorted(base.rglob("*.py"))
    ]
    dynamic = [row for row in rows if row["dynamic_current_revision"]]
    hazards = [row for row in rows if row["output_minting_risk"]]
    experiment_hazards = [row for row in hazards if row["scope"] == "experiments"]
    tool_hazards = [row for row in hazards if row["scope"] == "tools"]
    timestamp_hazards = [row for row in hazards if row["timestamp_contradiction_risk"]]

    protected: list[dict[str, Any]] = []
    protected_errors: list[str] = []
    by_path = {row["path"]: row for row in rows}
    for rel, expected_revision in PROTECTED_HISTORICAL.items():
        row = by_path.get(rel)
        safe = bool(
            row
            and not row["dynamic_current_revision"]
            and expected_revision in row["pinned_revision_literals"]
            and row["historical_marker"]
        )
        protected.append({
            "path": rel,
            "expected_revision": expected_revision,
            "safe_from_current_revision_inheritance": safe,
            "observed": row,
        })
        if not safe:
            protected_errors.append(f"{rel} is not pinned and marked as frozen {expected_revision} history")

    status = "fail" if protected_errors else ("pass_with_debt" if hazards else "pass")
    return {
        "project": "CloudtainerML",
        "revision": REV,
        "report": "revision_lineage_static_audit",
        "generated_at": STAMP,
        "status": status,
        "promotion_allowed": False,
        "errors": protected_errors,
        "summary": {
            "python_files_scanned": len(rows),
            "dynamic_current_revision_scripts": len(dynamic),
            "historical_dynamic_artifact_minting_hazards": len(hazards),
            "historical_experiment_hazards": len(experiment_hazards),
            "historical_tool_hazards": len(tool_hazards),
            "dynamic_revision_hardcoded_timestamp_hazards": len(timestamp_hazards),
            "protected_public_trace_surfaces": len(protected),
            "protected_public_trace_surfaces_safe": sum(
                1 for item in protected if item["safe_from_current_revision_inheritance"]
            ),
            "remaining_migration_debt": len(hazards),
        },
        "protected_historical_surfaces": protected,
        "remaining_hazards": hazards,
        "all_scanned_dynamic_revision_scripts": dynamic,
        "policy": {
            "historical_runner": "Pin the original revision and run only in a scratch copy; never inherit current CUBE-META silently.",
            "new_run": "Require an explicit run revision and generate the execution timestamp at runtime; output into a new run namespace.",
            "historical_evidence": "Do not overwrite retained artifacts. Record a rerun as a new artifact with explicit source_revision, code hash, dependency hashes, and executed_at.",
        },
        "interpretation": (
            "The three historical public-trace experiments and their audits are now pinned to their original revisions, "
            "so they cannot silently mint rev0076 artifacts. Other legacy runners still inherit the current revision and "
            "must be migrated incrementally; this is integrity debt, not evidence for promotion."
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        f"# Revision lineage static audit — {REV}",
        "",
        f"**Status:** {report['status']}  ",
        "**Promotion:** blocked",
        "",
        report["interpretation"],
        "",
        "## Counts",
        "",
        f"- Python files scanned: {summary['python_files_scanned']}",
        f"- Dynamic current-revision scripts: {summary['dynamic_current_revision_scripts']}",
        f"- Historical artifact-minting hazards still present: {summary['historical_dynamic_artifact_minting_hazards']}",
        f"- Of those, experiment runners: {summary['historical_experiment_hazards']}",
        f"- Of those, audits/reports: {summary['historical_tool_hazards']}",
        f"- Dynamic revision plus hard-coded timestamp hazards: {summary['dynamic_revision_hardcoded_timestamp_hazards']}",
        f"- Protected public-trace surfaces pinned safely: {summary['protected_public_trace_surfaces_safe']}/{summary['protected_public_trace_surfaces']}",
        "",
        "## Why this matters",
        "",
        "A historical script that reads the live cube revision can write a current-revision artifact even though its assumptions, timestamp, and experiment contract belong to an older revision. That creates a plausible but false lineage surface and can waste later work debugging evidence that never belonged to the stated run.",
        "",
        "## Migration rule",
        "",
        "Historical runners should pin their original revision and remain immutable. A genuine rerun should use an explicit new run revision, a runtime execution timestamp, source/code/dependency hashes, and a separate output namespace.",
        "",
        "## Remaining high-risk experiment runners",
        "",
    ]
    experiment_rows = [row for row in report["remaining_hazards"] if row["scope"] == "experiments"]
    if experiment_rows:
        for row in experiment_rows:
            stamp = f"; hard-coded {row['hardcoded_timestamp']}" if row["hardcoded_timestamp"] else ""
            lines.append(f"- `{row['path']}` (fallback {row['fallback_revision']}{stamp})")
    else:
        lines.append("- None.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    report = scan_revision_lineage()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps({"status": report["status"], **report["summary"]}, indent=2))
    return 1 if report["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
