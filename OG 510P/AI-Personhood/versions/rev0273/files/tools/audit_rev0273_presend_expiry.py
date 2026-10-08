#!/usr/bin/env python3
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()

def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

def sha_bytes(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()

def sha_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def parse_z(ts):
    if not isinstance(ts, str) or not ts.endswith("Z"):
        raise SystemExit(f"timestamp is not UTC Z: {ts}")
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(timezone.utc)

route_rel = f"examples/route-locator-freshness-ledger-{REV}-public-source-no-contact.json"
auth_rel = f"examples/authority-expiry-and-renewal-check-{REV}-no-signature.json"
bundle_rel = f"examples/pre-send-evidence-bundle-{REV}-reviewer-first-no-send.json"
handoff_rel = f"examples/authority-handoff-vault-dry-run-{REV}-reviewer-first-nosend.json"
packet_rel = f"examples/reviewer-first-contact-packet-{REV}-eleos-not-sent.json"
body_rel = f"examples/reviewer-first-contact-body-{REV}-eleos-not-sent.txt"
eml_rel = f"examples/reviewer-first-contact-mail-ready-draft-{REV}-eleos-not-sent.eml"
playbook_rel = f"examples/reviewer-response-disposition-playbook-{REV}.json"
failed_rel = f"examples/failed-gate-public-summary-{REV}-reviewer-route-unavailable-template.json"
field_rel = f"examples/field-artifact-capture-workbook-{REV}-reviewer-first-no-send.json"
precommit_rel = f"examples/pre-send-custody-precommit-{REV}-no-private-root-selected.json"
shell_rel = f"examples/signed-authority-public-shell-{REV}-template.json"

for rel in [route_rel, auth_rel, bundle_rel, handoff_rel, packet_rel, body_rel, eml_rel, playbook_rel, failed_rel, field_rel, precommit_rel, shell_rel]:
    if not (ROOT / rel).exists():
        raise SystemExit(f"missing pre-send expiry surface: {rel}")

route = load(route_rel)
auth = load(auth_rel)
bundle = load(bundle_rel)
handoff = load(handoff_rel)
packet = load(packet_rel)
playbook = load(playbook_rel)
status = load("SURFACE-STATUS.json")
queue = load("FOLLOWTHROUGH-QUEUE.json")
board = load(f"examples/followthrough-queue-operating-board-{REV}.json")

for label, obj in [("route", route), ("auth", auth), ("bundle", bundle), ("handoff", handoff), ("packet", packet), ("playbook", playbook), ("status", status), ("queue", queue), ("board", board)]:
    if obj.get("revision") != REV:
        raise SystemExit(f"{label} revision mismatch")
    if obj.get("no_live_floor_effect") is not True and label not in {"queue"}:
        raise SystemExit(f"{label} must preserve no-live-floor")

if route.get("ledger_state") != "public-source-no-contact-freshness-window-open-but-not-authority":
    raise SystemExit("route freshness ledger state overclaims or is stale")
policy = route.get("freshness_policy", {})
checked = parse_z(policy.get("checked_at_utc"))
expires = parse_z(policy.get("freshness_expires_at_utc"))
if not (expires > checked):
    raise SystemExit("route freshness expiry is not after check time")
if policy.get("expiry_hours") != 4:
    raise SystemExit("route freshness window must be short/fail-closed")
for key in ["must_recheck_immediately_before_send", "stale_route_facts_fail_closed", "public_locator_is_not_consent", "route_score_is_not_authority"]:
    if policy.get(key) is not True:
        raise SystemExit(f"route freshness policy missing true flag: {key}")
for route_id in ["ROUTE-ELEOS-PRIMARY", "ROUTE-AIID-SECONDARY", "ROUTE-CONSCIUM-FALLBACK"]:
    rows = [r for r in route.get("observed_public_route_facts", []) if r.get("route_id") == route_id]
    if len(rows) != 1:
        raise SystemExit(f"route freshness ledger missing exactly one {route_id}")
    row = rows[0]
    if row.get("authorized_now") is not False or row.get("counterparty_contacted") is not False:
        raise SystemExit(f"route row overclaims authorization/contact: {route_id}")
    if not row.get("public_source_url") or not row.get("source_checked_at_utc"):
        raise SystemExit(f"route row lacks public source/check timestamp: {route_id}")
route_text = json.dumps(route).lower()
for term in ["info@eleosai.org", "moral-patienthood", "harm or near-harm", "fallback", "not consent", "not authority"]:
    if term not in route_text:
        raise SystemExit(f"route freshness ledger missing risk/fit term: {term}")
for key, value in route.get("overclaim_locks", {}).items():
    if value is not False:
        raise SystemExit(f"route ledger overclaim lock must be false: {key}")

if auth.get("check_state") != "no-signature-no-send-window-no-authority":
    raise SystemExit("authority expiry check must remain unsigned/no-window")
for key, value in auth.get("source_refs", {}).items():
    if not value or not (ROOT / value).exists():
        raise SystemExit(f"authority expiry missing source {key}: {value}")
unsigned = auth.get("unsigned_state", {})
for key in ["signature_present", "signer_role_present", "private_signature_record_sha256_present", "branch_value_present", "send_window_open", "send_permitted_now"]:
    if unsigned.get(key) is not False:
        raise SystemExit(f"authority expiry unsigned field overclaims: {key}")
future = auth.get("future_signature_window_policy", {})
if future.get("validity_minutes_after_signature") != 30:
    raise SystemExit("future signature window must be limited to 30 minutes")
for key in ["must_expire_on_any_message_hash_change", "must_expire_on_route_ledger_expiry", "must_expire_on_private_root_change", "must_expire_on_recipient_or_subject_change", "must_expire_if_sender_account_differs_from_signed_record", "renewal_requires_new_private_signature"]:
    if future.get(key) is not True:
        raise SystemExit(f"authority expiry missing true renewal control: {key}")
if future.get("public_shell_alone_can_renew") is not False:
    raise SystemExit("public shell must not renew authority")
renewal_text = json.dumps(auth.get("renewal_decision_table", [])).lower()
for term in ["no-send", "renew-or-no-send", "one-shot-send-window", "private roots", "hash recompute"]:
    if term not in renewal_text:
        raise SystemExit(f"authority renewal table missing {term}")
for key, value in auth.get("overclaim_locks", {}).items():
    if value is not False:
        raise SystemExit(f"authority expiry overclaim lock must be false: {key}")

if bundle.get("bundle_state") != "compiled-no-authority-no-private-root-no-send":
    raise SystemExit("pre-send bundle must remain no-authority/no-root/no-send")
refs = bundle.get("source_refs", {})
required_refs = {
    "route_locator_freshness_ledger": route_rel,
    "authority_expiry_and_renewal_check": auth_rel,
    "authority_handoff_vault_dry_run": handoff_rel,
    "signed_authority_public_shell_template": shell_rel,
    "pre_send_custody_precommit": precommit_rel,
    "reviewer_first_packet": packet_rel,
    "reviewer_first_body": body_rel,
    "reviewer_first_mail_ready_draft": eml_rel,
    "response_disposition_playbook": playbook_rel,
    "failed_gate_public_summary_template": failed_rel,
    "field_artifact_capture_workbook": field_rel,
}
for key, rel in required_refs.items():
    if refs.get(key) != rel:
        raise SystemExit(f"bundle source ref mismatch for {key}: {refs.get(key)}")
body = (ROOT / body_rel).read_text(encoding="utf-8").strip()
computed = {
    "reviewer_first_body_sha256": sha_text(body),
    "reviewer_first_body_word_count": len(body.split()),
    "reviewer_first_mail_ready_draft_sha256": sha_bytes(eml_rel),
    "reviewer_first_packet_sha256": sha_bytes(packet_rel),
    "authority_handoff_vault_dry_run_sha256": sha_bytes(handoff_rel),
    "route_locator_freshness_ledger_sha256": sha_bytes(route_rel),
    "authority_expiry_and_renewal_check_sha256": sha_bytes(auth_rel),
    "response_disposition_playbook_sha256": sha_bytes(playbook_rel),
    "failed_gate_public_summary_template_sha256": sha_bytes(failed_rel),
    "field_artifact_capture_workbook_sha256": sha_bytes(field_rel),
    "dry_run_may_satisfy_send_time_hash_recompute": False,
}
if bundle.get("hash_bindings") != computed:
    raise SystemExit("pre-send evidence bundle hash bindings stale")
blockers = bundle.get("blocking_status", {})
for key in ["private_signature_missing", "public_authority_shell_template_only", "private_vault_roots_missing", "send_time_locator_recheck_missing", "send_time_hash_recompute_missing", "transport_proof_missing", "response_clock_not_started"]:
    if blockers.get(key) is not True:
        raise SystemExit(f"pre-send bundle blocker must remain true: {key}")
if blockers.get("send_permitted_now") is not False:
    raise SystemExit("pre-send bundle must not permit send now")
controls = bundle.get("one_shot_send_controls", {})
if controls.get("max_sends_authorized_by_future_signature") != 1:
    raise SystemExit("future authority must be one-shot only")
for key in ["attachments_allowed", "stage_two_payload_allowed"]:
    if controls.get(key) is not False:
        raise SystemExit(f"pre-send bundle overclaims branch scope: {key}")
for key in ["resend_requires_new_authority", "retarget_requires_new_route_ledger_and_exact_packet", "decline_or_do_not_contact_stops_branch"]:
    if controls.get(key) is not True:
        raise SystemExit(f"pre-send bundle missing true one-shot control: {key}")
expiry = bundle.get("expiry_controls", {})
if expiry.get("route_freshness_expires_at_utc") != policy.get("freshness_expires_at_utc"):
    raise SystemExit("bundle route freshness expiry does not mirror route ledger")
if expiry.get("future_signature_validity_minutes") != future.get("validity_minutes_after_signature"):
    raise SystemExit("bundle signature validity does not mirror authority check")
if expiry.get("stale_bundle_decision") != "NO-SEND-UNTIL-RENEWED":
    raise SystemExit("stale bundle must fail closed")
for key, value in bundle.get("overclaim_locks", {}).items():
    if value is not False:
        raise SystemExit(f"bundle overclaim lock must be false: {key}")
if bundle.get("anti_bureaucracy_lock", {}).get("progress_requires_signed_branch_or_real_outcome") is not True:
    raise SystemExit("bundle anti-bureaucracy lock missing")

for rel in [route_rel, auth_rel, bundle_rel, f"docs/00-meta/{REV}-authority-expiry-presend-evidence-refactor.md", f"docs/30-transition/{REV}-pre-send-expiry-and-evidence-runbook.md", "tools/audit_rev0273_presend_expiry.py"]:
    if rel not in status.get("new_surfaces", []):
        raise SystemExit(f"SURFACE-STATUS missing pre-send expiry surface: {rel}")
    if not (ROOT / rel).exists():
        raise SystemExit(f"SURFACE-STATUS names missing pre-send expiry path: {rel}")

queue_text = json.dumps(queue).lower()
for term in [bundle_rel.lower(), route_rel.lower(), auth_rel.lower(), "stale readiness", "no further doctrine"]:
    if term not in queue_text:
        raise SystemExit(f"queue missing pre-send expiry discipline term: {term}")
board_text = json.dumps(board).lower()
for term in [bundle_rel.lower(), "stale readiness", "send/no-send"]:
    if term not in board_text:
        raise SystemExit(f"operating board missing pre-send expiry term: {term}")
for rel in ["README.md", "START_HERE.md", "docs/README.md"]:
    text = (ROOT / rel).read_text(encoding="utf-8")[:4000].lower()
    if bundle_rel.lower() not in text:
        raise SystemExit(f"front door missing pre-send bundle: {rel}")

print("audit_rev0273_presend_expiry: OK")
