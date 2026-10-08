#!/usr/bin/env python3
"""Smoke the mission-kernel evidence submitter with an external drill.

The check creates temporary records outside the governed tree, hashes them into a
submission, proves the intake validator treats them as a non-live drill, and
confirms both the submitter and intake validator reject governed synthetic-tree
paths as evidence.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REV = VERSION.removeprefix("v").zfill(4)
EXAMPLE = ROOT / "artifacts" / "examples" / "example_county_2026_municipal_pilot"
WORKQUEUE = EXAMPLE / "live-closeout-workqueue.json"
SUBMITTER = ROOT / "tools" / "mission_kernel_evidence_submitter.py"
INTAKE = ROOT / "tools" / "mission_kernel_live_evidence_intake.py"
SCHEMA = ROOT / "schemas" / "MissionKernelEvidenceSubmission.json"
TOOL_REG = ROOT / "artifacts" / "registries" / "tool-maturity.csv"


def run(args: list[str], *, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False, timeout=timeout)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []
    for path in [WORKQUEUE, SUBMITTER, INTAKE, SCHEMA, TOOL_REG]:
        if not path.exists():
            errors.append(f"missing {path.relative_to(ROOT)}")
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2

    workqueue = load_json(WORKQUEUE)
    if workqueue.get("archive_version") != VERSION:
        errors.append("live-closeout-workqueue.json is stale for current VERSION")
    first = (workqueue.get("rows") or [None])[0]
    if not isinstance(first, dict) or first.get("work_item_id") != "LWC-001":
        errors.append("expected first workqueue row LWC-001")
    required = [str(x) for x in (first or {}).get("minimum_evidence_classes") or []]
    if len(required) < 3:
        errors.append("LWC-001 must have at least three required evidence classes for the drill")
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory(prefix="tes_mk_submitter_drill_") as td:
        tdir = Path(td).resolve()
        evidence_objects: list[dict[str, str]] = []
        for idx, cls in enumerate(required, start=1):
            ep = tdir / f"lwc001-class{idx}.txt"
            ep.write_text(f"non-production drill record for {VERSION} / {cls}\n", encoding="utf-8")
            slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in cls).strip("-")[:48]
            evidence_objects.append({
                "evidence_class": cls,
                "file_path": str(ep),
                "record_locator": f"operator-drill://example-county/LWC-001/{slug}",
                "approving_role": "jurisdiction authority liaison drill approver",
                "redaction_status": "APPROVED_PRIVATE",
                "public_private_boundary": "PRIVATE_SOURCE_RECORD",
                "records_retention_rule_ref": "DRILL-RETENTION-NONPRODUCTION-001",
                "captured_at_utc": "2026-06-18T00:00:00Z",
                "drill_scope": "non-production submitter smoke test; not live election evidence",
            })
        plan = {
            "submission_id": f"MK-EVIDENCE-SUBMITTER-DRILL-rev{REV}",
            "source_mode": "AUTHORIZED_NONPRODUCTION_DRILL_RECORD",
            "synthetic_only": False,
            "no_live_deployment_claim": True,
            "common_fields": {
                "jurisdiction_name": "Example County drill workspace",
                "election_id": "NONPRODUCTION-DRILL-ONLY",
                "election_date": "2026-06-18",
                "local_authority_contact_role": "jurisdiction authority liaison drill approver",
                "redaction_review_status": "APPROVED_PRIVATE",
                "public_release_approval_status": "NOT_REQUESTED_DRILL_ONLY",
                "records_retention_rule_ref": "DRILL-RETENTION-NONPRODUCTION-001",
            },
            "work_items": [{"work_item_id": "LWC-001", "evidence_objects": evidence_objects}],
        }
        plan_path = tdir / "plan.json"
        submission_path = tdir / "submission.json"
        plan_path.write_text(json.dumps(plan, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        proc = run([sys.executable, str(SUBMITTER), "--plan", str(plan_path), "--out", str(submission_path)])
        if proc.returncode != 0:
            errors.append(f"submitter failed for external drill: {proc.stdout} {proc.stderr}")
        elif not submission_path.exists():
            errors.append("submitter did not write submission.json")
        else:
            submission = load_json(submission_path)
            raw = submission_path.read_text(encoding="utf-8")
            if submission.get("source_mode") != "AUTHORIZED_NONPRODUCTION_DRILL_RECORD":
                errors.append("submission source_mode drift")
            if submission.get("no_live_deployment_claim") is not True or submission.get("non_production_drill") is not True:
                errors.append("submission missing no-live/non-production drill flags")
            if "file_path" in raw or str(tdir) in raw:
                errors.append("submission leaked local file_path or temp directory")
            objects = ((submission.get("work_items") or [{}])[0].get("evidence_objects") or [])
            if len(objects) != len(required):
                errors.append("submission object count does not match LWC-001 required class count")
            for obj in objects:
                if not str(obj.get("sha256") or "").startswith("sha256:"):
                    errors.append("submission object missing sha256: digest")
                if int(obj.get("byte_count") or 0) <= 0:
                    errors.append("submission object missing positive byte_count")
                if obj.get("source_mode") != "AUTHORIZED_NONPRODUCTION_DRILL_RECORD":
                    errors.append("submission object source_mode drift")
            intake = run([sys.executable, str(INTAKE), "--submission", str(submission_path), "--json"])
            if intake.returncode != 0:
                errors.append(f"intake failed for submitter drill: {intake.stdout} {intake.stderr}")
            else:
                payload = json.loads(intake.stdout)
                status = payload.get("status") or {}
                if status.get("decision") != "DRILL_PARTIAL_NOT_LIVE_EVIDENCE":
                    errors.append(f"unexpected drill decision {status.get('decision')!r}")
                if int(status.get("live_evidence_object_count") if status.get("live_evidence_object_count") is not None else -1) != 0:
                    errors.append("drill submission must not create live evidence objects")
                if int(status.get("valid_drill_evidence_object_count") if status.get("valid_drill_evidence_object_count") is not None else -1) != len(required):
                    errors.append("valid drill evidence object count mismatch")
                rows = {r.get("work_item_id"): r for r in status.get("rows") or [] if isinstance(r, dict)}
                if (rows.get("LWC-001") or {}).get("status") != "DRILL_COMPLETE_NOT_LIVE_EVIDENCE":
                    errors.append("LWC-001 drill row did not complete as non-live evidence")
                missing_rows = [r for wid, r in rows.items() if wid != "LWC-001" and r.get("status") == "MISSING_LIVE_EVIDENCE"]
                if len(missing_rows) != 6:
                    errors.append("all six non-drilled rows must remain missing live evidence")

            bad = submission
            bad["work_items"][0]["evidence_objects"][0]["record_locator"] = "artifacts/examples/fake-local-record.json"
            bad_path = tdir / "bad-governed-locator.json"
            bad_path.write_text(json.dumps(bad, sort_keys=True, indent=2) + "\n", encoding="utf-8")
            bad_intake = run([sys.executable, str(INTAKE), "--submission", str(bad_path), "--json"])
            if bad_intake.returncode != 0:
                errors.append(f"intake crashed on governed-locator negative fixture: {bad_intake.stderr}")
            else:
                bad_status = (json.loads(bad_intake.stdout).get("status") or {})
                if bad_status.get("decision") != "NO_GO_DRILL_VALIDATION_FAILED_NOT_LIVE_EVIDENCE":
                    errors.append("governed-locator negative fixture did not fail closed")
                if not any("governed synthetic archive" in e for e in bad_status.get("errors") or []):
                    errors.append("governed-locator negative fixture missing explicit error")

            # A bare-digest live submission may be shape-valid, but it must never
            # become authenticated live evidence or a staged live-readiness result.
            live_objects = json.loads(json.dumps(evidence_objects))
            for obj in live_objects:
                obj["record_locator"] = obj["record_locator"].replace("operator-drill://", "operator-live://")
                obj.pop("drill_scope", None)
            live_plan = {
                "submission_id": f"MK-EVIDENCE-SUBMITTER-LIVE-CANDIDATE-rev{REV}",
                "source_mode": "LIVE_AUTHORIZED_LOCAL_RECORD",
                "synthetic_only": False,
                "no_live_deployment_claim": True,
                "common_fields": {
                    "jurisdiction_name": "Example County candidate workspace",
                    "election_id": "EXAMPLE-CANDIDATE-ELECTION",
                    "election_date": "2026-06-18",
                    "local_authority_contact_role": "jurisdiction authority liaison",
                    "authority_scope_record_sha256": "sha256:" + "1" * 64,
                    "evidence_capture_datetime_utc": "2026-06-18T00:00:00Z",
                    "redaction_review_status": "APPROVED_PRIVATE",
                    "public_release_approval_status": "NOT_APPROVED_PRIVATE_SOURCE",
                    "records_retention_rule_ref": "EXAMPLE-RETENTION-001",
                },
                "work_items": [{"work_item_id": "LWC-001", "evidence_objects": live_objects}],
            }
            live_plan_path = tdir / "live-candidate-plan.json"
            live_submission_path = tdir / "live-candidate-submission.json"
            live_plan_path.write_text(json.dumps(live_plan, sort_keys=True, indent=2) + "\n", encoding="utf-8")
            live_proc = run([sys.executable, str(SUBMITTER), "--plan", str(live_plan_path), "--out", str(live_submission_path)])
            if live_proc.returncode != 0:
                errors.append(f"submitter failed for live candidate negative control: {live_proc.stdout} {live_proc.stderr}")
            else:
                live_submission = load_json(live_submission_path)
                if live_submission.get("authentication_state") != "UNAUTHENTICATED_CANDIDATE_REQUIRES_SIGNED_EVIDENCE_ENVELOPE":
                    errors.append("live candidate submission missing explicit unauthenticated state")
                live_intake = run([sys.executable, str(INTAKE), "--submission", str(live_submission_path), "--json"])
                if live_intake.returncode != 0:
                    errors.append(f"intake crashed on live candidate negative control: {live_intake.stderr}")
                else:
                    live_status = (json.loads(live_intake.stdout).get("status") or {})
                    if live_status.get("decision") != "NO_GO_LIVE_EVIDENCE_AUTHENTICATION_REQUIRED":
                        errors.append(f"bare live candidate did not fail closed: {live_status.get('decision')!r}")
                    if int(live_status.get("valid_live_evidence_object_count") or 0) != 0:
                        errors.append("bare live candidate incorrectly incremented authenticated live evidence")
                    if int(live_status.get("shape_valid_live_candidate_object_count") or 0) != len(required):
                        errors.append("live candidate shape-valid count mismatch")
                    live_rows = {r.get("work_item_id"): r for r in live_status.get("rows") or [] if isinstance(r, dict)}
                    if (live_rows.get("LWC-001") or {}).get("status") != "CANDIDATE_COMPLETE_AUTHENTICATION_REQUIRED":
                        errors.append("live candidate row did not remain authentication-blocked")

            duplicate_item_plan = json.loads(json.dumps(plan))
            duplicate_item_plan["work_items"].append(json.loads(json.dumps(duplicate_item_plan["work_items"][0])))
            duplicate_item_path = tdir / "duplicate-item-plan.json"
            duplicate_item_path.write_text(json.dumps(duplicate_item_plan, sort_keys=True, indent=2) + "\n", encoding="utf-8")
            duplicate_item_proc = run([sys.executable, str(SUBMITTER), "--plan", str(duplicate_item_path), "--json"])
            if duplicate_item_proc.returncode == 0 or "duplicate work_item_id" not in duplicate_item_proc.stderr:
                errors.append("submitter did not reject duplicate work_item_id values")

            duplicate_class_plan = json.loads(json.dumps(plan))
            duplicate_class_plan["work_items"][0]["evidence_objects"].append(
                json.loads(json.dumps(duplicate_class_plan["work_items"][0]["evidence_objects"][0]))
            )
            duplicate_class_path = tdir / "duplicate-class-plan.json"
            duplicate_class_path.write_text(json.dumps(duplicate_class_plan, sort_keys=True, indent=2) + "\n", encoding="utf-8")
            duplicate_class_proc = run([sys.executable, str(SUBMITTER), "--plan", str(duplicate_class_path), "--json"])
            if duplicate_class_proc.returncode == 0 or "duplicate evidence_class" not in duplicate_class_proc.stderr:
                errors.append("submitter did not reject duplicate evidence_class values")

        bad_plan = {
            "submission_id": f"MK-EVIDENCE-SUBMITTER-BAD-rev{REV}",
            "source_mode": "AUTHORIZED_NONPRODUCTION_DRILL_RECORD",
            "work_items": [{
                "work_item_id": "LWC-001",
                "evidence_objects": [{
                    "evidence_class": required[0],
                    "file_path": str(ROOT / "README.md"),
                    "approving_role": "jurisdiction authority liaison drill approver",
                    "redaction_status": "APPROVED_PRIVATE",
                    "public_private_boundary": "PRIVATE_SOURCE_RECORD",
                }],
            }],
        }
        bad_plan_path = tdir / "bad-plan.json"
        bad_plan_path.write_text(json.dumps(bad_plan, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        bad_proc = run([sys.executable, str(SUBMITTER), "--plan", str(bad_plan_path), "--json"])
        if bad_proc.returncode == 0:
            errors.append("submitter accepted a governed synthetic-tree file_path")
        if "inside governed synthetic archive" not in bad_proc.stderr:
            errors.append("submitter negative fixture missing governed-tree error")

    registry_text = TOOL_REG.read_text(encoding="utf-8")
    if "mission_kernel_evidence_submitter.py" not in registry_text:
        errors.append("tool-maturity.csv missing mission_kernel_evidence_submitter.py")
    if not SCHEMA.read_text(encoding="utf-8").strip().startswith("{"):
        errors.append("MissionKernelEvidenceSubmission schema is not JSON-looking")

    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2
    print(f"PASS: mission-kernel evidence submitter drill ({VERSION}, drill_classes={len(required)}, live_objects=0)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
