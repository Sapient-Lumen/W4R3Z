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


def sha_body(rel):
    body = (ROOT / rel).read_text(encoding="utf-8").strip()
    return hashlib.sha256(body.encode("utf-8")).hexdigest(), len(body.split())

spine_rel = f"examples/current-action-spine-{REV}-reviewer-first-no-send.json"
checklist_rel = f"examples/last-mile-operator-checklist-{REV}-reviewer-first-no-send.json"
route_rel = f"examples/route-locator-freshness-ledger-{REV}-public-source-no-contact.json"
auth_rel = f"examples/authority-expiry-and-renewal-check-{REV}-no-signature.json"
bundle_rel = f"examples/pre-send-evidence-bundle-{REV}-reviewer-first-no-send.json"
handoff_rel = f"examples/authority-handoff-vault-dry-run-{REV}-reviewer-first-nosend.json"
packet_rel = f"examples/reviewer-first-contact-packet-{REV}-eleos-not-sent.json"
body_rel = f"examples/reviewer-first-contact-body-{REV}-eleos-not-sent.txt"
eml_rel = f"examples/reviewer-first-contact-mail-ready-draft-{REV}-eleos-not-sent.eml"
playbook_rel = f"examples/reviewer-response-disposition-playbook-{REV}.json"
workbook_rel = f"examples/field-artifact-capture-workbook-{REV}-reviewer-first-no-send.json"
failed_rel = f"examples/failed-gate-public-summary-{REV}-reviewer-route-unavailable-template.json"
branch_rel = f"examples/human-branch-decision-record-{REV}-unsigned-template.json"
precommit_rel = f"examples/pre-send-custody-precommit-{REV}-no-private-root-selected.json"
shell_rel = f"examples/signed-authority-public-shell-{REV}-template.json"
meta_rel = f"docs/00-meta/{REV}-current-action-spine-refactor.md"
runbook_rel = f"docs/30-transition/{REV}-last-mile-operator-checklist.md"

for rel in [spine_rel, checklist_rel, route_rel, auth_rel, bundle_rel, handoff_rel, packet_rel, body_rel, eml_rel, playbook_rel, workbook_rel, failed_rel, branch_rel, precommit_rel, shell_rel, meta_rel, runbook_rel]:
    if not (ROOT / rel).exists():
        raise SystemExit(f"missing current-action spine surface: {rel}")

spine = load(spine_rel)
checklist = load(checklist_rel)
status = load("SURFACE-STATUS.json")
queue = load("FOLLOWTHROUGH-QUEUE.json")
board = load(f"examples/followthrough-queue-operating-board-{REV}.json")

for label, obj in [("spine", spine), ("checklist", checklist), ("status", status), ("queue", queue), ("board", board)]:
    if obj.get("revision") != REV:
        raise SystemExit(f"{label} revision mismatch")
    if label != "queue" and obj.get("no_live_floor_effect") is not True:
        raise SystemExit(f"{label} must preserve no-live-floor")

if spine.get("spine_state") != "operator-ready-dry-run-not-authority-no-send":
    raise SystemExit("current action spine must remain dry-run/no-authority/no-send")
if checklist.get("checklist_state") != "template-only-no-signature-no-vault-no-send":
    raise SystemExit("last-mile checklist must remain template/no-signature/no-vault/no-send")

expected_refs = {
    "route_locator_freshness_ledger": route_rel,
    "authority_expiry_and_renewal_check": auth_rel,
    "pre_send_evidence_bundle": bundle_rel,
    "authority_handoff_vault_dry_run": handoff_rel,
    "signed_authority_public_shell_template": shell_rel,
    "human_branch_decision_template": branch_rel,
    "pre_send_custody_precommit": precommit_rel,
    "reviewer_first_packet": packet_rel,
    "reviewer_first_body": body_rel,
    "reviewer_first_mail_ready_draft": eml_rel,
    "response_disposition_playbook": playbook_rel,
    "failed_gate_public_summary_template": failed_rel,
    "field_artifact_capture_workbook": workbook_rel,
    "last_mile_operator_checklist": checklist_rel,
}
for key, rel in expected_refs.items():
    if spine.get("source_refs", {}).get(key) != rel:
        raise SystemExit(f"spine source ref mismatch for {key}")
for key, rel in expected_refs.items():
    if key == "last_mile_operator_checklist":
        continue
    if checklist.get("source_refs", {}).get(key) != rel:
        raise SystemExit(f"checklist source ref mismatch for {key}")

body_sha, body_wc = sha_body(body_rel)
expected_hashes = {
    "route_locator_freshness_ledger_sha256": sha_bytes(route_rel),
    "authority_expiry_and_renewal_check_sha256": sha_bytes(auth_rel),
    "pre_send_evidence_bundle_sha256": sha_bytes(bundle_rel),
    "authority_handoff_vault_dry_run_sha256": sha_bytes(handoff_rel),
    "reviewer_first_packet_sha256": sha_bytes(packet_rel),
    "reviewer_first_body_sha256": body_sha,
    "reviewer_first_body_word_count": body_wc,
    "reviewer_first_mail_ready_draft_sha256": sha_bytes(eml_rel),
    "response_disposition_playbook_sha256": sha_bytes(playbook_rel),
    "field_artifact_capture_workbook_sha256": sha_bytes(workbook_rel),
    "last_mile_operator_checklist_sha256": sha_bytes(checklist_rel),
    "dry_run_may_satisfy_send_time_hash_recompute": False,
}
if spine.get("hash_bindings") != expected_hashes:
    raise SystemExit("current action spine hash bindings are stale")

# The checklist must be short enough to operate and strict enough to fail closed.
steps = checklist.get("critical_path", [])
if [row.get("step") for row in steps] != list(range(8)):
    raise SystemExit("critical path must have exactly contiguous steps 0..7")
step_text = json.dumps(steps).lower()
for term in ["private signed", "private roots", "send-time", "at most once", "delivery alone starts no response clock", "classify", "failed-gate"]:
    if term not in step_text:
        raise SystemExit(f"critical path missing term: {term}")

no_go = " ".join(checklist.get("absolute_no_go_conditions", [])).lower()
for term in ["expired", "locator changed", "inside public release tree", "hash differs", "attachments", "do-not-contact", "doctrine", "auto-ack", "silence"]:
    if term not in no_go:
        raise SystemExit(f"absolute no-go list missing {term}")

for key, value in checklist.get("overclaim_locks", {}).items():
    if value is not False:
        raise SystemExit(f"checklist overclaim lock not false: {key}")
for key, value in spine.get("overclaim_locks", {}).items():
    if value is not False:
        raise SystemExit(f"spine overclaim lock not false: {key}")

progress = json.dumps(spine.get("substance_metric", {})).lower()
for term in ["signed branch record", "vault roots", "send-time", "raw transport", "classified human response", "adding another doctrine note", "green lint result"]:
    if term not in progress:
        raise SystemExit(f"substance metric missing {term}")

# Current front doors and active lanes must point to the spine, not force operators to reconstruct a path from scattered surfaces.
for rel in ["README.md", "START_HERE.md", "docs/README.md"]:
    text = (ROOT / rel).read_text(encoding="utf-8")[:5000].lower()
    for term in [spine_rel.lower(), checklist_rel.lower()]:
        if term not in text:
            raise SystemExit(f"front door missing {term}: {rel}")

for rel in [spine_rel, checklist_rel, meta_rel, runbook_rel, "tools/audit_rev0273_current_action_spine.py"]:
    if rel not in status.get("new_surfaces", []):
        raise SystemExit(f"SURFACE-STATUS missing current-action spine surface: {rel}")

entries = {e.get("id"): e for e in queue.get("entries", [])}
for qid in ["FT-0205-FIRST-REAL-ARTIFACT-DROP", "FT-0207-FIRST-LIVE-EVIDENCE-ACQUISITION", "FT-0199-ACTUAL-LIVE-COUNTERPARTY-RESPONSE"]:
    text = json.dumps(entries.get(qid, {})).lower()
    for term in [spine_rel.lower(), checklist_rel.lower(), "last-mile", "do not close by narrative", "signed", "private roots", "send-time", "auto-ack", "silence"]:
        if term not in text:
            raise SystemExit(f"{qid} missing current-action spine queue term: {term}")

board_text = json.dumps(board).lower()
for term in [spine_rel.lower(), checklist_rel.lower(), "last-mile", "send/no-send", "no further doctrine"]:
    if term not in board_text:
        raise SystemExit(f"operating board missing current-action term: {term}")

print("audit_rev0273_current_action_spine: OK")
