#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
sys.path.insert(0, str(ROOT / "tools"))
from build_send_attempt_transaction_ledger import build  # noqa: E402


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

transaction_rel = f"examples/send-attempt-transaction-ledger-{REV}-no-signature-aborted.json"
identity_rel = f"examples/operator-identity-signature-capture-template-{REV}-no-signature.json"
roots_rel = f"examples/private-root-selection-dryrun-shell-{REV}-no-private-root.json"
spine_rel = f"examples/current-action-spine-{REV}-reviewer-first-no-send.json"
checklist_rel = f"examples/last-mile-operator-checklist-{REV}-reviewer-first-no-send.json"
bundle_rel = f"examples/pre-send-evidence-bundle-{REV}-reviewer-first-no-send.json"
route_rel = f"examples/route-locator-freshness-ledger-{REV}-public-source-no-contact.json"

for rel in [transaction_rel, identity_rel, roots_rel, spine_rel, checklist_rel, bundle_rel, route_rel, "tools/build_send_attempt_transaction_ledger.py"]:
    if not (ROOT / rel).exists():
        raise SystemExit(f"missing send-attempt transaction surface: {rel}")

ledger = load(transaction_rel)
expected = build(ledger.get("created_at"))
if ledger != expected:
    raise SystemExit("send-attempt transaction ledger is stale relative to current source hashes")

if ledger.get("revision") != REV or ledger.get("no_live_floor_effect") is not True:
    raise SystemExit("send-attempt ledger revision/no-floor mismatch")
if ledger.get("transaction_state") != "aborted-before-send-no-signature-no-private-root-no-contact":
    raise SystemExit("send-attempt ledger must remain aborted before send")
if ledger.get("current_result") != "NO-SEND-FAIL-CLOSED":
    raise SystemExit("send-attempt ledger must fail closed as NO-SEND")

# The ledger must not smuggle live evidence or private roots into a public release.
private_status = ledger.get("private_input_status", {})
for key in ["private_signature_present", "signed_branch_value_present", "signature_window_open", "public_tree_contains_private_root_paths"]:
    if private_status.get(key) is not False:
        raise SystemExit(f"private input status must be false: {key}")
if private_status.get("selected_private_roots_count") != 0:
    raise SystemExit("public ledger must not claim selected private roots")

no_contact = ledger.get("no_contact_state", {})
for key in ["message_sent", "counterparty_contacted", "response_clock_started", "raw_inbound_artifact_exists"]:
    if no_contact.get(key) is not False:
        raise SystemExit(f"no-contact state must remain false: {key}")
if no_contact.get("live_floor_effect") != 0:
    raise SystemExit("send-attempt ledger must have zero live-floor effect")

# Gate order and results must explicitly distinguish pass-for-orientation from abort/not-reached.
gates = ledger.get("gate_results", [])
if [g.get("gate_id") for g in gates] != [
    "G0-CURRENT-HEAD",
    "G1-OPERATOR-IDENTITY-AND-SIGNATURE",
    "G2-PRIVATE-ROOT-SELECTION",
    "G3-ROUTE-FRESHNESS",
    "G4-AUTHORITY-EXPIRY",
    "G5-SEND-TIME-HASH-RECOMPUTE",
    "G6-TRANSPORT-CAPTURE",
    "G7-RESPONSE-DISPOSITION",
]:
    raise SystemExit("send-attempt gate order changed or is incomplete")
results = {g.get("gate_id"): g.get("result") for g in gates}
for gate in ["G1-OPERATOR-IDENTITY-AND-SIGNATURE", "G2-PRIVATE-ROOT-SELECTION", "G4-AUTHORITY-EXPIRY", "G5-SEND-TIME-HASH-RECOMPUTE"]:
    if results.get(gate) != "abort-no-send":
        raise SystemExit(f"{gate} must abort no-send")
if results.get("G3-ROUTE-FRESHNESS") != "pass-for-routing-only-not-authority":
    raise SystemExit("route freshness must not become authority")
for gate in ["G6-TRANSPORT-CAPTURE", "G7-RESPONSE-DISPOSITION"]:
    if not results.get(gate, "").startswith("not-reached"):
        raise SystemExit(f"{gate} must remain not reached")

locks = ledger.get("overclaim_locks", {})
for key, value in locks.items():
    if value is not False:
        raise SystemExit(f"send-attempt overclaim lock must be false: {key}")

spine = load(spine_rel)
checklist = load(checklist_rel)
bundle = load(bundle_rel)
for obj_name, obj in [("spine", spine), ("checklist", checklist), ("bundle", bundle)]:
    refs = obj.get("source_refs", {})
    for key, rel in {
        "send_attempt_transaction_ledger": transaction_rel,
        "operator_identity_signature_template": identity_rel,
        "private_root_selection_dryrun_shell": roots_rel,
    }.items():
        if refs.get(key) != rel:
            raise SystemExit(f"{obj_name} missing source ref {key}")

identity = load(identity_rel)
roots = load(roots_rel)
if identity.get("template_state") != "public-template-only-no-private-operator-proof-no-signature":
    raise SystemExit("identity template must remain public/no-signature")
if identity.get("current_values", {}).get("private_signature_record_present") is not False:
    raise SystemExit("identity template must not claim private signature")
if roots.get("shell_state") != "public-shell-no-private-root-selected-no-paths-disclosed":
    raise SystemExit("private-root shell must remain no-root/no-path")
for row in roots.get("required_private_roots", []):
    if row.get("selected") is not False or row.get("must_be_outside_public_release_tree") is not True:
        raise SystemExit(f"private root row invalid: {row.get('root_id')}")
for key, value in roots.get("public_tree_checks", {}).items():
    if value is not False:
        raise SystemExit(f"public tree private-material check must be false: {key}")

status = load("SURFACE-STATUS.json")
if status.get("revision") != REV or status.get("no_live_floor_effect") is not True:
    raise SystemExit("SURFACE-STATUS revision/no-floor mismatch")
for rel in [transaction_rel, identity_rel, roots_rel, "tools/build_send_attempt_transaction_ledger.py", "tools/audit_rev0273_send_attempt_transaction.py", f"docs/00-meta/{REV}-send-attempt-transaction-refactor.md", f"docs/30-transition/{REV}-send-attempt-abort-proof-runbook.md"]:
    if rel not in status.get("new_surfaces", []):
        raise SystemExit(f"SURFACE-STATUS missing send-attempt surface: {rel}")

for rel in ["README.md", "START_HERE.md", "docs/README.md"]:
    text = (ROOT / rel).read_text(encoding="utf-8")[:6000].lower()
    for term in [transaction_rel.lower(), "send-attempt", "no-send-fail-closed"]:
        if term not in text:
            raise SystemExit(f"front door missing send-attempt term {term}: {rel}")

queue = load("FOLLOWTHROUGH-QUEUE.json")
entries = {e.get("id"): e for e in queue.get("entries", [])}
for qid in ["FT-0205-FIRST-REAL-ARTIFACT-DROP", "FT-0207-FIRST-LIVE-EVIDENCE-ACQUISITION", "FT-0199-ACTUAL-LIVE-COUNTERPARTY-RESPONSE"]:
    text = json.dumps(entries.get(qid, {})).lower()
    for term in [transaction_rel.lower(), "operator identity", "private roots", "no-send-fail-closed", "not-reached"]:
        if term not in text:
            raise SystemExit(f"{qid} missing send-attempt transaction term: {term}")

print("audit_rev0273_send_attempt_transaction: OK")
