#!/usr/bin/env python3
"""Validate the mission-kernel live-closeout workqueue pack."""
from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REV = VERSION.removeprefix("v").zfill(4)
OUTDIR = ROOT / "artifacts" / "examples" / "example_county_2026_municipal_pilot"
TOOL = ROOT / "tools" / "mission_kernel_live_workqueue.py"
WORKQUEUE_JSON = OUTDIR / "live-closeout-workqueue.json"
WORKQUEUE_CSV = OUTDIR / "live-closeout-workqueue.csv"
INTAKE_TEMPLATE = OUTDIR / "live-closeout-intake-template.json"
PUBLIC_MD = OUTDIR / "public-live-closeout-workqueue.md"
REPORT = ROOT / "artifacts" / "reports" / f"mission-kernel-live-workqueue-rev{REV}.json"
REQUIRED_BLOCKERS = {f"MKB-{i:03d}" for i in range(1, 8)}
REQUIRED_OUTPUTS = [WORKQUEUE_JSON, WORKQUEUE_CSV, INTAKE_TEMPLATE, PUBLIC_MD, REPORT]
BOUNDARY_PHRASES = ["not live election evidence", "does not authorize", "no-go", "not legal advice"]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return [{k: (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]


def run_tool_json() -> dict[str, object]:
    proc = subprocess.run([sys.executable, str(TOOL), "--json"], cwd=ROOT, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False, timeout=120)
    if proc.returncode != 0:
        raise RuntimeError(f"mission_kernel_live_workqueue.py --json failed rc={proc.returncode}: {proc.stdout} {proc.stderr}")
    return json.loads(proc.stdout)


def main() -> int:
    errors: list[str] = []
    for p in [TOOL, *REQUIRED_OUTPUTS]:
        if not p.exists():
            errors.append(f"missing {p.relative_to(ROOT)}")
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2

    try:
        generated = run_tool_json()
    except Exception as exc:
        print("ERROR:", exc, file=sys.stderr)
        return 2

    shipped_wq = load_json(WORKQUEUE_JSON)
    shipped_intake = load_json(INTAKE_TEMPLATE)
    shipped_report = load_json(REPORT)
    if shipped_wq != generated.get("workqueue"):
        errors.append("live-closeout-workqueue.json is stale; run tools/mission_kernel_live_workqueue.py --write")
    if shipped_intake != generated.get("intake_template"):
        errors.append("live-closeout-intake-template.json is stale; run tools/mission_kernel_live_workqueue.py --write")
    if shipped_report != generated.get("report"):
        errors.append("mission-kernel-live-workqueue report is stale; run tools/mission_kernel_live_workqueue.py --write")

    if shipped_wq.get("archive_version") != VERSION or shipped_report.get("archive_version") != VERSION:
        errors.append("workqueue/report archive_version mismatch")
    if not str(shipped_wq.get("scenario_id") or "").endswith(VERSION):
        errors.append("workqueue scenario_id is stale")
    if shipped_wq.get("synthetic_only") is not True or shipped_wq.get("no_live_deployment_claim") is not True:
        errors.append("workqueue missing synthetic/no-live flags")
    if shipped_wq.get("decision") != "NO_GO_LIVE_CLOSEOUT_EVIDENCE_INCOMPLETE":
        errors.append("workqueue decision must remain live-closeout no-go")
    if shipped_wq.get("readiness_verdict") != "SYNTHETIC_REPLAY_PASS_LIVE_NO_GO":
        errors.append("workqueue must preserve closeout readiness verdict")

    rows = shipped_wq.get("rows") or []
    if len(rows) != 7 or int(shipped_wq.get("work_item_count") or 0) != 7:
        errors.append("workqueue must contain exactly seven blocker-derived work items")
    blocker_ids = {str(r.get("blocker_id") or "") for r in rows if isinstance(r, dict)}
    if blocker_ids != REQUIRED_BLOCKERS:
        errors.append(f"workqueue blocker ids mismatch: {sorted(blocker_ids)}")
    work_ids = [str(r.get("work_item_id") or "") for r in rows if isinstance(r, dict)]
    if len(work_ids) != len(set(work_ids)) or not all(re.fullmatch(r"LWC-\d{3}", wid) for wid in work_ids):
        errors.append("work_item_id values must be unique LWC-### ids")
    if int(shipped_wq.get("critical_work_item_count") or 0) != 5:
        errors.append("workqueue must retain five critical work items")
    if int(shipped_wq.get("high_work_item_count") or 0) != 2:
        errors.append("workqueue must retain two high work items")

    for row in rows:
        if not isinstance(row, dict):
            errors.append("workqueue row is not an object")
            continue
        wid = str(row.get("work_item_id") or "?")
        for field in ["blocker_id", "priority", "owner_role", "status", "next_artifact", "missing_evidence", "closure_test", "acceptance_gate", "non_claims"]:
            if not row.get(field):
                errors.append(f"{wid} missing {field}")
        if str(row.get("owner_role") or "").upper() == "TBD":
            errors.append(f"{wid} owner_role must not be TBD")
        if row.get("status") != "BLOCKED_PENDING_LIVE_EVIDENCE":
            errors.append(f"{wid} must remain blocked pending live evidence")
        if len(row.get("minimum_evidence_classes") or []) < 3:
            errors.append(f"{wid} must have at least three minimum evidence classes")
        if len(row.get("source_kernel_elements") or []) < 1:
            errors.append(f"{wid} must include source kernel element context")
        boundary = (row.get("non_claims") or "").lower()
        for phrase in ["not live election evidence", "not authorization", "not legal advice"]:
            if phrase not in boundary:
                errors.append(f"{wid} non_claims missing {phrase!r}")

    csv_rows = read_csv(WORKQUEUE_CSV)
    if len(csv_rows) != len(rows):
        errors.append("live-closeout-workqueue.csv row count must match JSON")
    if {r.get("work_item_id") for r in csv_rows} != set(work_ids):
        errors.append("live-closeout-workqueue.csv work_item_id set drift")
    if not all((r.get("non_claims") or "") for r in csv_rows):
        errors.append("live-closeout-workqueue.csv rows must carry non_claims")

    intake_items = shipped_intake.get("work_items") or []
    if shipped_intake.get("archive_version") != VERSION:
        errors.append("intake template archive_version mismatch")
    if shipped_intake.get("synthetic_only") is not True or shipped_intake.get("no_live_deployment_claim") is not True:
        errors.append("intake template missing synthetic/no-live flags")
    if len(intake_items) != len(rows):
        errors.append("intake template work_items must match workqueue rows")
    for item in intake_items:
        if not isinstance(item, dict):
            errors.append("intake work item is not an object")
            continue
        if item.get("status") != "UNFILLED_TEMPLATE_NOT_EVIDENCE":
            errors.append(f"intake {item.get('work_item_id')} must remain unfilled template/not evidence")
        for obj in item.get("evidence_objects_to_record") or []:
            if not isinstance(obj, dict):
                errors.append(f"intake {item.get('work_item_id')} evidence object is not an object")
                continue
            if obj.get("sha256") or obj.get("local_path_or_record_locator"):
                errors.append(f"intake {item.get('work_item_id')} must not contain fabricated live evidence locators or digests")

    if shipped_report.get("work_item_count") != 7 or shipped_report.get("critical_work_item_count") != 5:
        errors.append("live workqueue report summary mismatch")
    if (shipped_report.get("refactor_audit") or {}).get("status") != "PASS":
        errors.append("live workqueue refactor audit must pass")
    refactor_count = (shipped_wq.get("refactor_audit") or {}).get("duplicated_blocker_list_after_refactor")
    if refactor_count is None or int(refactor_count) != 0:
        errors.append("workqueue must be generated from closeout blocker list, not a duplicated blocker list")

    public = PUBLIC_MD.read_text(encoding="utf-8", errors="replace").lower()
    for phrase in BOUNDARY_PHRASES:
        if phrase not in public:
            errors.append(f"public-live-closeout-workqueue.md missing boundary phrase: {phrase!r}")
    if "certifies" in public or "proves fraud" in public:
        errors.append("public-live-closeout-workqueue.md contains prohibited overclaiming language")

    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2
    print(f"PASS: mission-kernel live workqueue ({VERSION}, items={len(rows)}, critical=5)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
