#!/usr/bin/env python3
"""Validate the mission-kernel live-evidence intake status pack."""
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
TOOL = ROOT / "tools" / "mission_kernel_live_evidence_intake.py"
COMMON = ROOT / "tools" / "mission_kernel_common.py"
SUBMITTER = ROOT / "tools" / "mission_kernel_evidence_submitter.py"
SCHEMA = ROOT / "schemas" / "MissionKernelEvidenceSubmission.json"
STATUS_SCHEMA = ROOT / "schemas" / "MissionKernelLiveEvidenceIntake.json"
SUBMISSION = OUTDIR / "live-closeout-evidence-submission-empty.json"
STATUS_JSON = OUTDIR / "live-closeout-evidence-intake-status.json"
STATUS_CSV = OUTDIR / "live-closeout-evidence-intake-status.csv"
PUBLIC_MD = OUTDIR / "public-live-closeout-intake-status.md"
REPORT = ROOT / "artifacts" / "reports" / f"mission-kernel-live-evidence-intake-rev{REV}.json"
REQUIRED = [COMMON, TOOL, SUBMITTER, SCHEMA, STATUS_SCHEMA, SUBMISSION, STATUS_JSON, STATUS_CSV, PUBLIC_MD, REPORT]
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return [{k: (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]


def run_tool_json() -> dict[str, object]:
    proc = subprocess.run([sys.executable, str(TOOL), "--json"], cwd=ROOT, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False, timeout=120)
    if proc.returncode != 0:
        raise RuntimeError(f"mission_kernel_live_evidence_intake.py --json failed rc={proc.returncode}: {proc.stdout} {proc.stderr}")
    return json.loads(proc.stdout)


def main() -> int:
    errors: list[str] = []
    for p in REQUIRED:
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

    shipped_submission = load_json(SUBMISSION)
    shipped_status = load_json(STATUS_JSON)
    shipped_report = load_json(REPORT)
    if shipped_submission != generated.get("submission"):
        errors.append("live-closeout-evidence-submission-empty.json is stale; run tools/mission_kernel_live_evidence_intake.py --write")
    if shipped_status != generated.get("status"):
        errors.append("live-closeout-evidence-intake-status.json is stale; run tools/mission_kernel_live_evidence_intake.py --write")
    if shipped_report != generated.get("report"):
        errors.append("mission-kernel-live-evidence-intake report is stale; run tools/mission_kernel_live_evidence_intake.py --write")

    for obj, label in [(shipped_submission, "submission"), (shipped_status, "status"), (shipped_report, "report")]:
        if obj.get("archive_version") != VERSION:
            errors.append(f"{label} archive_version mismatch")

    # Validate the current status shape when jsonschema is available.  The
    # archive still supports parse-only operation in minimal environments.
    try:
        import jsonschema  # type: ignore
        from jsonschema import FormatChecker  # type: ignore
        jsonschema.Draft202012Validator(load_json(STATUS_SCHEMA), format_checker=FormatChecker()).validate(shipped_status)
    except ImportError:
        pass
    except Exception as exc:
        errors.append(f"live evidence intake status does not validate against schema: {exc}")

    if shipped_submission.get("decision") != "UNFILLED_TEMPLATE_NOT_EVIDENCE":
        errors.append("empty submission must remain explicitly unfilled/not evidence")
    if shipped_submission.get("synthetic_only") is not True or shipped_submission.get("no_live_deployment_claim") is not True:
        errors.append("empty submission missing synthetic/no-live flags")
    if shipped_status.get("decision") != "NO_GO_NO_LIVE_EVIDENCE_SUBMITTED":
        errors.append("status decision must remain no-go/no-live-evidence-submitted")
    if shipped_status.get("synthetic_archive_report") is not True or shipped_status.get("no_live_deployment_claim") is not True:
        errors.append("status missing synthetic archive/no-live flags")
    if int(shipped_status.get("work_item_count") or 0) != 7:
        errors.append("intake status must cover seven workqueue items")
    if int(shipped_status.get("live_evidence_object_count") if shipped_status.get("live_evidence_object_count") is not None else -1) != 0:
        errors.append("shipped archive must contain zero live evidence objects")
    if int(shipped_status.get("valid_live_evidence_object_count") if shipped_status.get("valid_live_evidence_object_count") is not None else -1) != 0:
        errors.append("shipped archive must contain zero authenticated live evidence objects")
    if int(shipped_status.get("shape_valid_live_candidate_object_count") if shipped_status.get("shape_valid_live_candidate_object_count") is not None else -1) != 0:
        errors.append("shipped empty archive must contain zero shape-valid live candidates")
    if int(shipped_status.get("drill_evidence_object_count") if shipped_status.get("drill_evidence_object_count") is not None else -1) != 0:
        errors.append("shipped archive must contain zero non-production drill evidence objects")
    if int(shipped_status.get("valid_drill_evidence_object_count") if shipped_status.get("valid_drill_evidence_object_count") is not None else -1) != 0:
        errors.append("shipped archive must contain zero valid non-production drill evidence objects")
    if int(shipped_status.get("missing_live_evidence_item_count") or 0) != 7:
        errors.append("all seven work items must remain missing live evidence in the shipped archive")
    if int(shipped_status.get("error_count") if shipped_status.get("error_count") is not None else -1) != 0:
        errors.append("empty submission should not have validation errors; it should be a clean no-go")

    item_ids = {str(r.get("work_item_id") or "") for r in shipped_status.get("rows") or [] if isinstance(r, dict)}
    if item_ids != {f"LWC-{i:03d}" for i in range(1, 8)}:
        errors.append(f"intake status work item ids mismatch: {sorted(item_ids)}")
    for row in shipped_status.get("rows") or []:
        if not isinstance(row, dict):
            errors.append("status row is not an object")
            continue
        wid = row.get("work_item_id")
        if row.get("status") != "MISSING_LIVE_EVIDENCE":
            errors.append(f"{wid} must remain MISSING_LIVE_EVIDENCE")
        if int(row.get("live_evidence_object_count") or 0) != 0 or int(row.get("valid_live_evidence_object_count") or 0) != 0:
            errors.append(f"{wid} must not contain live evidence objects")
        if int(row.get("drill_evidence_object_count") or 0) != 0 or int(row.get("valid_drill_evidence_object_count") or 0) != 0:
            errors.append(f"{wid} must not contain drill evidence objects in the shipped empty status")
        if len(row.get("missing_evidence_classes") or []) < 3:
            errors.append(f"{wid} must enumerate missing evidence classes")

    csv_rows = read_csv(STATUS_CSV)
    if len(csv_rows) != 7:
        errors.append("live-closeout-evidence-intake-status.csv must have seven rows")
    if {r.get("work_item_id") for r in csv_rows} != item_ids:
        errors.append("intake status CSV work_item_id set drift")
    if not all(r.get("status") == "MISSING_LIVE_EVIDENCE" for r in csv_rows):
        errors.append("intake status CSV rows must remain missing live evidence")

    common_text = COMMON.read_text(encoding="utf-8")
    tool_text = TOOL.read_text(encoding="utf-8")
    if common_text.count("INTAKE_CLASSES =") != 1:
        errors.append("mission_kernel_common.py must own exactly one INTAKE_CLASSES map")
    if "INTAKE_CLASSES =" in tool_text:
        errors.append("mission_kernel_live_evidence_intake.py must not duplicate the evidence-class map")
    submitter_text = SUBMITTER.read_text(encoding="utf-8")
    if "INTAKE_CLASSES =" in submitter_text:
        errors.append("mission_kernel_evidence_submitter.py must not duplicate the evidence-class map")
    refactor = shipped_status.get("refactor_audit") or {}
    if refactor.get("status") != "PASS" or int(refactor.get("duplicated_evidence_class_maps_after_refactor") if refactor.get("duplicated_evidence_class_maps_after_refactor") is not None else -1) != 0:
        errors.append("intake refactor audit must pass with zero duplicated evidence-class maps")
    if int(refactor.get("bare_digest_live_promotion_paths_after_refactor") if refactor.get("bare_digest_live_promotion_paths_after_refactor") is not None else -1) != 0:
        errors.append("intake must report zero bare-digest live-promotion paths")
    auth_boundary = str(shipped_status.get("authentication_boundary") or "").lower().replace("-", " ")
    for phrase in ["does not authenticate", "signed evidenceenvelope", "trust profile", "remain candidates"]:
        if phrase not in auth_boundary:
            errors.append(f"authentication boundary missing phrase {phrase!r}")
    prohibited_terminal = "STAGED_PENDING_AUTHORITY_REVIEW_NOT_LIVE_READY"
    if prohibited_terminal in tool_text or prohibited_terminal in STATUS_SCHEMA.read_text(encoding="utf-8"):
        errors.append("deprecated bare-digest live staging terminal remains reachable in tool/schema")

    public = PUBLIC_MD.read_text(encoding="utf-8", errors="replace").lower()
    for phrase in ["not live election evidence", "does not authorize", "no-go", "not certification", "not legal advice", "non-production drill"]:
        if phrase not in public:
            errors.append(f"public-live-closeout-intake-status.md missing boundary phrase {phrase!r}")
    if "certifies" in public or "proves fraud" in public:
        errors.append("public-live-closeout-intake-status.md contains prohibited overclaiming language")

    # The shipped empty template must not sneak in digest-looking live records.
    raw_submission = SUBMISSION.read_text(encoding="utf-8")
    if DIGEST_RE.search(raw_submission):
        errors.append("empty submission must not contain digest-shaped live evidence")
    if shipped_submission.get("non_production_drill") is not False:
        errors.append("empty submission must not be marked as a non-production drill")

    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2
    print(f"PASS: mission-kernel live evidence intake ({VERSION}, live_objects=0, drill_objects=0, items=7)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
