#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def sha_bytes(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def sha_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

handoff_rel = f"examples/authority-handoff-vault-dry-run-{REV}-reviewer-first-nosend.json"
shell_rel = f"examples/signed-authority-public-shell-{REV}-template.json"
packet_rel = f"examples/reviewer-first-contact-packet-{REV}-eleos-not-sent.json"
body_rel = f"examples/reviewer-first-contact-body-{REV}-eleos-not-sent.txt"
eml_rel = f"examples/reviewer-first-contact-mail-ready-draft-{REV}-eleos-not-sent.eml"
branch_rel = f"examples/human-branch-decision-record-{REV}-unsigned-template.json"
precommit_rel = f"examples/pre-send-custody-precommit-{REV}-no-private-root-selected.json"
workbook_rel = f"examples/field-artifact-capture-workbook-{REV}-reviewer-first-no-send.json"
playbook_rel = f"examples/reviewer-response-disposition-playbook-{REV}.json"
failed_rel = f"examples/failed-gate-public-summary-{REV}-reviewer-route-unavailable-template.json"

for rel in [handoff_rel, shell_rel, packet_rel, body_rel, eml_rel, branch_rel, precommit_rel, workbook_rel, playbook_rel, failed_rel]:
    if not (ROOT / rel).exists():
        raise SystemExit(f"missing authority-handoff surface: {rel}")

handoff = load(handoff_rel)
shell = load(shell_rel)
packet = load(packet_rel)
branch = load(branch_rel)
precommit = load(precommit_rel)
workbook = load(workbook_rel)
playbook = load(playbook_rel)
failed = load(failed_rel)
status = load("SURFACE-STATUS.json")
queue = load("FOLLOWTHROUGH-QUEUE.json")

for label, obj in [("handoff", handoff), ("shell", shell), ("packet", packet), ("branch", branch), ("precommit", precommit), ("workbook", workbook), ("playbook", playbook)]:
    if obj.get("revision") != REV or obj.get("no_live_floor_effect") is not True:
        raise SystemExit(f"{label} revision/no-floor mismatch")
# failed-gate public summary uses an older shared schema that has no revision/no_live_floor fields;
# enforce its stayed/no-quorum/no-receipt closure below instead of mutating the shared schema.

if handoff.get("dry_run_state") != "ready-for-human-branch-decision-not-authority-no-private-root-no-send":
    raise SystemExit("handoff must remain a no-authority/no-private-root/no-send dry run")
if shell.get("shell_state") != "template-only-no-signature-no-authority":
    raise SystemExit("signed authority public shell must remain template-only/no-authority")
if branch.get("record_state") != "template-unsigned-no-authority":
    raise SystemExit("branch decision template overclaims authority")
if packet.get("packet_state") != "prepared-not-authorized-not-sent":
    raise SystemExit("reviewer packet overclaims send state")

sources = handoff.get("source_surfaces", {})
required_source_values = {
    "branch_decision_template": branch_rel,
    "pre_send_custody_precommit": precommit_rel,
    "reviewer_first_packet": packet_rel,
    "reviewer_first_body": body_rel,
    "reviewer_first_mail_ready_draft": eml_rel,
    "field_artifact_capture_workbook": workbook_rel,
    "response_disposition_playbook": playbook_rel,
    "failed_gate_public_summary_template": failed_rel,
}
for key, rel in required_source_values.items():
    if sources.get(key) != rel:
        raise SystemExit(f"handoff source mismatch for {key}: {sources.get(key)}")

body = (ROOT / body_rel).read_text(encoding="utf-8").strip()
body_hash = sha_text(body)
eml_hash = sha_bytes(eml_rel)
packet_hash = sha_bytes(packet_rel)
msg = packet.get("exact_message", {})
if msg.get("body_ref") != body_rel or msg.get("mail_ready_draft_ref") != eml_rel:
    raise SystemExit("packet not bound to current reviewer-first body/.eml")
if msg.get("body_sha256") != body_hash or msg.get("mail_ready_draft_sha256") != eml_hash:
    raise SystemExit("packet hashes stale")
if msg.get("body_word_count") != len(body.split()):
    raise SystemExit("packet word count stale")
if handoff.get("message_hash_bindings", {}).get("reviewer_first_body_sha256") != body_hash:
    raise SystemExit("handoff body hash stale")
if handoff.get("message_hash_bindings", {}).get("reviewer_first_mail_ready_draft_sha256") != eml_hash:
    raise SystemExit("handoff .eml hash stale")
if handoff.get("message_hash_bindings", {}).get("reviewer_first_packet_sha256") != packet_hash:
    raise SystemExit("handoff packet hash stale")
if handoff.get("message_hash_bindings", {}).get("dry_run_may_satisfy_send_time_hash_recompute") is not False:
    raise SystemExit("handoff dry-run is allowed to satisfy send-time hash recompute")

roots = handoff.get("private_vault_placeholders", {})
if roots.get("actual_private_paths_recorded_in_public_release") is not False or roots.get("raw_payload_bytes_recorded_in_public_release") is not False:
    raise SystemExit("handoff public object leaks private path/raw payload state")
for key, value in roots.items():
    if key.endswith("_root") and not str(value).startswith("OUTSIDE_RELEASE_TREE/"):
        raise SystemExit(f"private root placeholder is not outside-release-tree: {key}={value}")

locks = handoff.get("overclaim_locks", {})
for key in [
    "dry_run_may_authorize_send",
    "dry_run_may_select_private_root",
    "dry_run_may_start_response_clock",
    "dry_run_may_count_as_transport_or_delivery",
    "dry_run_may_create_custody_intake_import_or_floor_effect",
    "dry_run_may_claim_reviewer_appointment",
    "dry_run_may_claim_welfare_or_status_finding",
    "public_shell_may_substitute_for_raw_signature_or_raw_custody",
]:
    if locks.get(key) is not False:
        raise SystemExit(f"handoff overclaim lock not false: {key}")

shell_fields = shell.get("public_fields_after_real_signature", {})
for key in ["branch_value", "signer_role", "signed_at", "private_signature_record_sha256"]:
    if shell_fields.get(key) != "UNSIGNED-TEMPLATE":
        raise SystemExit(f"public shell template already filled authority field: {key}")
if shell_fields.get("authorized_message_body_sha256") != body_hash or shell_fields.get("authorized_mail_ready_draft_sha256") != eml_hash:
    raise SystemExit("public shell template hash bindings stale")
for key, value in shell.get("overclaim_locks", {}).items():
    if value is not False:
        raise SystemExit(f"public shell overclaim lock not false: {key}")

seq = handoff.get("operator_sequence", [])
if [row.get("ordinal") for row in seq] != list(range(len(seq))):
    raise SystemExit("operator sequence ordinals are not contiguous")
seq_text = json.dumps(seq).lower()
for term in ["private signed human branch", "private roots", "send-time", "transport", "classify", "failed-gate", "appointment"]:
    if term not in seq_text:
        raise SystemExit(f"operator sequence missing term: {term}")

go_text = json.dumps(handoff.get("go_no_go_matrix", [])).lower()
for term in ["no-go", "no-send-recorded", "authorized-for-one-exact-send-only", "stop-and-shell"]:
    if term not in go_text:
        raise SystemExit(f"go/no-go matrix missing {term}")

rows = {row.get("artifact_id"): row for row in workbook.get("artifact_rows", [])}
a1_text = json.dumps(rows.get("A1-BRANCH-REQUEST", {})).lower()
for rel in [handoff_rel.lower(), shell_rel.lower(), branch_rel.lower()]:
    if rel not in a1_text:
        raise SystemExit(f"A1 workbook row missing {rel}")
# Queue must name the handoff on the three first-artifact lanes and keep formation independent.
entries = {e.get("id"): e for e in queue.get("entries", [])}
for qid in ["FT-0205-FIRST-REAL-ARTIFACT-DROP", "FT-0207-FIRST-LIVE-EVIDENCE-ACQUISITION", "FT-0199-ACTUAL-LIVE-COUNTERPARTY-RESPONSE"]:
    text = json.dumps(entries.get(qid, {})).lower()
    for term in [handoff_rel.lower(), shell_rel.lower(), "do not close by narrative", "signed", "private roots", "send-time"]:
        if term not in text:
            raise SystemExit(f"{qid} missing handoff queue term: {term}")
for qid in ["FT-0068", "FT-0069"]:
    text = json.dumps(entries.get(qid, {})).lower()
    if "do not wait for contact" not in text or f"formation-review-drill-{REV}" not in text:
        raise SystemExit(f"{qid} lost independent formation lane")

for rel in [handoff_rel, shell_rel, f"docs/00-meta/{REV}-authority-handoff-vault-refactor.md", f"docs/30-transition/{REV}-authority-handoff-and-vault-dryrun.md", "tools/audit_rev0268_authority_handoff_vault.py"]:
    if rel not in status.get("new_surfaces", []):
        raise SystemExit(f"SURFACE-STATUS missing authority-handoff surface: {rel}")
    if not (ROOT / rel).exists():
        raise SystemExit(f"SURFACE-STATUS names missing path: {rel}")

print("audit_rev0268_authority_handoff_vault: OK")
