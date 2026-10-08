#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def sha(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()

route_rel = f"examples/current-route-head-normalization-{REV}-eleos-primary-aiid-secondary.json"
intake_rel = f"examples/human-decision-intake-form-{REV}-unsigned-no-send.json"
meta_rel = f"docs/00-meta/{REV}-route-head-and-human-decision-intake-refactor.md"
runbook_rel = f"docs/30-transition/{REV}-human-decision-intake-and-route-head-runbook.md"

for rel in [route_rel, intake_rel, meta_rel, runbook_rel, "tools/audit_rev0273_route_head_decision_intake.py"]:
    if not (ROOT / rel).exists():
        raise SystemExit(f"missing rev0273 route-head/intake surface: {rel}")

route = load(route_rel)
intake = load(intake_rel)
status = load("SURFACE-STATUS.json")
queue = load("FOLLOWTHROUGH-QUEUE.json")
board = load(f"examples/followthrough-queue-operating-board-{REV}.json")

for label, obj in [("route", route), ("intake", intake), ("status", status), ("queue", queue), ("board", board)]:
    if obj.get("revision") != REV:
        raise SystemExit(f"{label} revision mismatch")
    if label != "queue" and obj.get("no_live_floor_effect") is not True:
        raise SystemExit(f"{label} must preserve no-live-floor")

if route.get("normalization_state") != "single-current-route-head-no-contact":
    raise SystemExit("route head must be single-current/no-contact")
head = route.get("single_current_action_head", {})
if head.get("route_id") != "ROUTE-ELEOS-PRIMARY":
    raise SystemExit("Eleos must be the single current action head")
for key in ["authorized_now", "contacted_now", "response_clock_started"]:
    if head.get(key) is not False:
        raise SystemExit(f"route head overclaims {key}")

legacy_text = json.dumps(route.get("legacy_secondary_routes", [])).lower()
for term in ["route-aiid-secondary", "secondary-noncurrent", "may_send_from_legacy_surface", "false", "new explicit signed human branch"]:
    if term not in legacy_text:
        raise SystemExit(f"legacy route quarantine missing term: {term}")
for finding in route.get("legacy_conflict_findings", []):
    if finding.get("current_action_allowed") is not False:
        raise SystemExit("legacy conflict finding must not allow current action")
conflict_text = json.dumps(route.get("legacy_conflict_findings", [])).lower()
for term in ["counterparty-selection", "ready-to-dispatch", "legacy-secondary", "cannot override"]:
    if term not in conflict_text:
        raise SystemExit(f"route head conflict findings missing {term}")

for key, rel in route.get("source_refs", {}).items():
    if not (ROOT / rel).exists():
        raise SystemExit(f"route head missing source ref {key}: {rel}")
    expected = sha(rel)
    if route.get("hash_bindings", {}).get(f"{key}_sha256") != expected:
        raise SystemExit(f"route head hash binding stale for {key}")
for key, value in route.get("overclaim_locks", {}).items():
    if value is not False:
        raise SystemExit(f"route head overclaim lock must be false: {key}")
for key in ["message_sent", "counterparty_contacted", "response_clock_started", "raw_inbound_artifact_exists"]:
    if route.get("no_contact_state", {}).get(key) is not False:
        raise SystemExit(f"route head no-contact field must be false: {key}")
if route.get("no_contact_state", {}).get("live_floor_effect") != 0:
    raise SystemExit("route head live-floor effect must be zero")

if intake.get("intake_state") != "public-template-unsigned-no-authority-no-send":
    raise SystemExit("human-decision intake must be unsigned/no-authority/no-send")
if intake.get("current_public_result") != "NO-PRIVATE-DECISION-INTAKE-UNSIGNED":
    raise SystemExit("human-decision intake result must be unsigned")
branches = {row.get("branch"): row for row in intake.get("allowed_decision_branches", [])}
if set(branches) != {"NO-SEND", "DEFER", "STOP", "ONE-SHOT-REVIEWER-FIRST-SEND"}:
    raise SystemExit("human-decision intake branch set is wrong")
for branch, row in branches.items():
    if row.get("requires_private_signature") is not True:
        raise SystemExit(f"branch must require private signature: {branch}")
    if branch != "ONE-SHOT-REVIEWER-FIRST-SEND" and row.get("may_contact") is not False:
        raise SystemExit(f"non-send branch may not contact: {branch}")
values = intake.get("current_values", {})
for key in ["private_operator_identity_record_present", "private_signature_record_present", "private_signature_record_sha256_public_shell_present", "sender_account_bound", "selected_recipient_confirmed_at_send_time", "send_time_hash_recompute_performed", "transport_capture_method_selected", "response_disposition_owner_selected", "send_permitted_now"]:
    if values.get(key) is not False:
        raise SystemExit(f"human-decision intake current value must be false: {key}")
if values.get("decision_branch_selected") is not None:
    raise SystemExit("human-decision intake must not select a branch")
if values.get("selected_private_roots_count") != 0:
    raise SystemExit("human-decision intake must not claim private roots")
if values.get("selected_public_route_head") != "ROUTE-ELEOS-PRIMARY":
    raise SystemExit("human-decision intake selected route head must be Eleos")
for key, rel in intake.get("source_refs", {}).items():
    if not (ROOT / rel).exists():
        raise SystemExit(f"intake missing source ref {key}: {rel}")
    if intake.get("hash_bindings", {}).get(f"{key}_sha256") != sha(rel):
        raise SystemExit(f"intake hash binding stale for {key}")
for key, value in intake.get("overclaim_locks", {}).items():
    if value is not False:
        raise SystemExit(f"intake overclaim lock must be false: {key}")
reporting = intake.get("public_reporting_rules", {})
for key in ["private_signature_material_may_be_published_raw", "private_root_paths_may_be_published_raw", "delivery_or_auto_ack_may_be_reported_as_human_response", "silence_may_be_reported_as_waiver_or_adverse_inference", "decline_or_referral_may_be_reported_as_reviewer_appointment"]:
    if reporting.get(key) is not False:
        raise SystemExit(f"intake reporting rule must be false: {key}")

# The legacy AIID dossier is retained, but route-head normalization must explicitly override it.
legacy_dossier = load(f"examples/external-contact-counterparty-selection-dossier-{REV}-public-source-ranked-not-authorized.json")
if legacy_dossier.get("recommendation", {}).get("recommended_candidate_id") == "CP-RAC-AIID-001":
    if "legacy_aiid_counterparty_selection_dossier" not in route.get("source_refs", {}):
        raise SystemExit("AIID legacy dossier is still ranked first but not quarantined by route head")
    if "current action head" not in json.dumps(route).lower():
        raise SystemExit("route head must explicitly name the current action head")

status_text = json.dumps(status).lower()
for term in [route_rel.lower(), intake_rel.lower(), "eleos", "legacy aiid", "not-actionable-no-private-authority", "no-send-fail-closed"]:
    if term not in status_text:
        raise SystemExit(f"SURFACE-STATUS missing route/intake term: {term}")
for rel in [route_rel, intake_rel, meta_rel, runbook_rel, "tools/audit_rev0273_route_head_decision_intake.py"]:
    if rel not in status.get("new_surfaces", []):
        raise SystemExit(f"SURFACE-STATUS missing route/intake new surface: {rel}")

for rel in ["README.md", "START_HERE.md", "docs/README.md"]:
    text = (ROOT / rel).read_text(encoding="utf-8")[:8000].lower()
    for term in [route_rel.lower(), intake_rel.lower(), "eleos", "legacy aiid", "not-actionable-no-private-authority", "no-send-fail-closed"]:
        if term not in text:
            raise SystemExit(f"front door missing route/intake term {term}: {rel}")

queue_text = json.dumps(queue).lower()
board_text = json.dumps(board).lower()
for term in [route_rel.lower(), intake_rel.lower(), "route-head", "human-decision", "no further doctrine", "auto-ack", "silence"]:
    if term not in queue_text:
        raise SystemExit(f"queue missing route/intake term: {term}")
for term in [route_rel.lower(), intake_rel.lower(), "route-head", "human-decision", "no further doctrine"]:
    if term not in board_text:
        raise SystemExit(f"operating board missing route/intake term: {term}")

print("audit_rev0273_route_head_decision_intake: OK")
