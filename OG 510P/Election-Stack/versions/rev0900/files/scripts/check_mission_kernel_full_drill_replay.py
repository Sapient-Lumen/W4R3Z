#!/usr/bin/env python3
"""Validate the full mission-kernel non-production drill replay audit."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REV = VERSION.removeprefix("v").zfill(4)
TOOL = ROOT / "tools" / "mission_kernel_full_drill_replay.py"
SUBMITTER = ROOT / "tools" / "mission_kernel_evidence_submitter.py"
INTAKE = ROOT / "tools" / "mission_kernel_live_evidence_intake.py"
COMMON = ROOT / "tools" / "mission_kernel_common.py"
REPORT = ROOT / "artifacts" / "reports" / f"mission-kernel-full-drill-replay-audit-rev{REV}.json"
PUBLIC_MD = ROOT / "artifacts" / "examples" / "example_county_2026_municipal_pilot" / "public-full-closeout-drill-replay.md"
TOOL_REG = ROOT / "artifacts" / "registries" / "tool-maturity.csv"
REQUIRED = [TOOL, SUBMITTER, INTAKE, COMMON, REPORT, PUBLIC_MD, TOOL_REG]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def run_tool_json() -> dict[str, object]:
    proc = subprocess.run(
        [sys.executable, str(TOOL), "--json"],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
        timeout=120,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"mission_kernel_full_drill_replay.py --json failed rc={proc.returncode}: {proc.stdout} {proc.stderr}")
    return json.loads(proc.stdout)


def main() -> int:
    errors: list[str] = []
    for path in REQUIRED:
        if not path.exists():
            errors.append(f"missing {path.relative_to(ROOT)}")
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2

    try:
        generated = run_tool_json()
    except Exception as exc:
        print("ERROR:", exc, file=sys.stderr)
        return 2

    shipped_report = load_json(REPORT)
    shipped_public = PUBLIC_MD.read_text(encoding="utf-8")
    if shipped_report != generated.get("report"):
        errors.append("mission-kernel full drill replay report is stale; run tools/mission_kernel_full_drill_replay.py --write")
    if shipped_public != generated.get("public_markdown"):
        errors.append("public-full-closeout-drill-replay.md is stale; run tools/mission_kernel_full_drill_replay.py --write")

    if shipped_report.get("archive_version") != VERSION:
        errors.append("full drill replay archive_version mismatch")
    if shipped_report.get("decision") != "DRILL_COMPLETE_NOT_LIVE_READY":
        errors.append(f"full drill replay decision must be DRILL_COMPLETE_NOT_LIVE_READY, got {shipped_report.get('decision')!r}")
    if shipped_report.get("expected_decision") != shipped_report.get("decision"):
        errors.append("full drill replay decision diverges from expected_decision")
    if shipped_report.get("no_live_deployment_claim") is not True or shipped_report.get("non_production_drill") is not True:
        errors.append("full drill replay missing no-live/non-production flags")
    if int(shipped_report.get("work_item_count") or 0) != 7:
        errors.append("full drill replay must cover all seven work items")
    if int(shipped_report.get("complete_drill_item_count") or 0) != 7:
        errors.append("full drill replay must complete all seven rows as drill-only")
    if int(shipped_report.get("rows_complete_not_live_count") or 0) != 7:
        errors.append("all full drill rows must be DRILL_COMPLETE_NOT_LIVE_EVIDENCE")
    if int(shipped_report.get("required_evidence_class_count") or 0) != 28:
        errors.append("full drill replay must exercise all 28 required evidence classes")
    if int(shipped_report.get("valid_drill_evidence_object_count") or 0) != 28:
        errors.append("full drill replay must validate 28 drill objects")
    if int(shipped_report.get("drill_evidence_object_count") or 0) != 28:
        errors.append("full drill replay drill object count mismatch")
    if int(shipped_report.get("live_evidence_object_count") if shipped_report.get("live_evidence_object_count") is not None else -1) != 0:
        errors.append("full drill replay must create zero live evidence objects")
    if int(shipped_report.get("valid_live_evidence_object_count") if shipped_report.get("valid_live_evidence_object_count") is not None else -1) != 0:
        errors.append("full drill replay must create zero valid live evidence objects")
    for field in ["error_count", "local_path_leak_count", "governed_synthetic_locator_count", "live_overclaim_term_count"]:
        if int(shipped_report.get(field) if shipped_report.get(field) is not None else -1) != 0:
            errors.append(f"full drill replay {field} must be zero")

    rows = shipped_report.get("row_summary") or []
    if len(rows) != 7:
        errors.append("full drill replay row_summary must contain seven rows")
    ids = [str(r.get("work_item_id") or "") for r in rows if isinstance(r, dict)]
    if ids != [f"LWC-{i:03d}" for i in range(1, 8)]:
        errors.append(f"full drill replay row ids drift: {ids}")
    for row in rows:
        if not isinstance(row, dict):
            errors.append("row_summary entry is not an object")
            continue
        wid = row.get("work_item_id")
        if row.get("status") != "DRILL_COMPLETE_NOT_LIVE_EVIDENCE":
            errors.append(f"{wid} full drill row did not complete as drill-only")
        if int(row.get("required_evidence_class_count") or 0) != 4:
            errors.append(f"{wid} must retain four required evidence classes")
        if int(row.get("valid_drill_evidence_class_count") or 0) != 4:
            errors.append(f"{wid} must validate four drill classes")
        if int(row.get("live_evidence_object_count") or 0) != 0:
            errors.append(f"{wid} must contain zero live objects")
        if row.get("missing_drill_evidence_classes"):
            errors.append(f"{wid} must not miss drill evidence classes")
        if len(row.get("missing_live_evidence_classes") or []) != 4:
            errors.append(f"{wid} must still list live evidence as missing")

    report_text = json.dumps(shipped_report, sort_keys=True, indent=2)
    if re.search(r"/tmp/|tes_mk_full_drill_|file_path", report_text):
        errors.append("full drill replay report leaks local temp paths or file_path fields")
    if "LIVE_AUTHORIZED_LOCAL_RECORD" in report_text:
        errors.append("full drill replay report must not contain live source-mode records")

    public = shipped_public.lower()
    for phrase in [
        "not live election evidence",
        "does not authorize",
        "not certification",
        "not outcome proof",
        "not current voter instruction",
        "not legal advice",
        "no-go for live deployment",
    ]:
        if phrase not in public:
            errors.append(f"public full-drill summary missing boundary phrase {phrase!r}")
    for bad in ["certifies", "proves fraud", "authorized live pilot", "live ready"]:
        if bad in public:
            errors.append(f"public full-drill summary contains prohibited overclaiming phrase {bad!r}")

    tool_text = TOOL.read_text(encoding="utf-8")
    if "from mission_kernel_evidence_submitter import build_submission" not in tool_text:
        errors.append("full drill tool must reuse mission_kernel_evidence_submitter.build_submission")
    if "from mission_kernel_live_evidence_intake import evaluate_submission" not in tool_text:
        errors.append("full drill tool must reuse mission_kernel_live_evidence_intake.evaluate_submission")
    refactor = shipped_report.get("refactor_audit") or {}
    if refactor.get("status") != "PASS" or int(refactor.get("duplicated_full_drill_intake_logic_after_refactor") if refactor.get("duplicated_full_drill_intake_logic_after_refactor") is not None else -1) != 0:
        errors.append("full drill refactor audit must pass with zero duplicated intake logic")
    if "mission_kernel_full_drill_replay.py" not in TOOL_REG.read_text(encoding="utf-8"):
        errors.append("tool-maturity.csv missing mission_kernel_full_drill_replay.py")

    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2
    print(f"PASS: full mission-kernel drill replay ({VERSION}, drill_objects=28, live_objects=0)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
