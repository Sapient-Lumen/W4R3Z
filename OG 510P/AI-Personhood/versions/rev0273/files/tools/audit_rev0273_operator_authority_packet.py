#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
sys.path.insert(0, str(ROOT / "tools"))
from build_operator_authority_packet import build  # noqa: E402


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

packet_rel = f"examples/operator-authority-packet-compiler-{REV}-reviewer-first-no-signature.json"
required = [
    packet_rel,
    "tools/build_operator_authority_packet.py",
    "tools/audit_rev0273_operator_authority_packet.py",
    f"docs/00-meta/{REV}-operator-authority-packet-compiler-refactor.md",
    f"docs/30-transition/{REV}-operator-authority-packet-runbook.md",
]
for rel in required:
    if not (ROOT / rel).exists():
        raise SystemExit(f"missing operator-authority packet surface: {rel}")

packet = load(packet_rel)
expected = build(packet.get("created_at"))
if packet != expected:
    raise SystemExit("operator authority packet compiler output is stale relative to current source hashes")

if packet.get("revision") != REV or packet.get("no_live_floor_effect") is not True:
    raise SystemExit("operator authority packet revision/no-floor mismatch")
if packet.get("packet_state") != "compiled-public-dryrun-no-private-authority-no-send":
    raise SystemExit("operator authority packet must remain a public dry-run no-authority packet")
if packet.get("current_compile_result") != "NOT-ACTIONABLE-NO-PRIVATE-AUTHORITY":
    raise SystemExit("operator authority packet must fail closed without private authority")

refs = packet.get("source_refs", {})
for key in [
    "send_attempt_transaction_ledger",
    "current_action_spine",
    "last_mile_operator_checklist",
    "pre_send_evidence_bundle",
    "operator_identity_signature_template",
    "private_root_selection_dryrun_shell",
    "route_locator_freshness_ledger",
    "reviewer_first_packet",
    "response_disposition_playbook",
]:
    rel = refs.get(key)
    if not rel or not (ROOT / rel).exists():
        raise SystemExit(f"operator authority packet missing source ref {key}: {rel}")
    if REV not in rel:
        raise SystemExit(f"operator authority packet source ref is not current revision: {key}={rel}")

hashes = packet.get("hash_bindings", {})
for key in refs:
    if f"{key}_sha256" not in hashes:
        raise SystemExit(f"missing hash binding for source ref: {key}")
if hashes.get("reviewer_first_body_word_count", 0) <= 0:
    raise SystemExit("operator authority packet must bind reviewer body word count")
if hashes.get("reviewer_first_body_normalized_sha256") != hashes.get("reviewer_first_body_sha256"):
    raise SystemExit("reviewer body normalized hash and raw file hash should match for plain text body")

private_state = packet.get("private_input_state", {})
for key in [
    "operator_identity_record_present",
    "private_signature_record_present",
    "branch_value_present",
    "signature_window_open",
    "public_release_contains_private_identity_material",
    "public_tree_contains_private_root_paths",
]:
    if private_state.get(key) is not False:
        raise SystemExit(f"private input state must be false: {key}")
if private_state.get("selected_private_roots_count") != 0:
    raise SystemExit("operator authority packet must not claim private roots")

gates = packet.get("gate_results", [])
expected_gate_ids = [
    "C0-COMPILE-CURRENT-SOURCES",
    "C1-OPERATOR-AUTHORITY",
    "C2-PRIVATE-ROOTS",
    "C3-ROUTE-FRESHNESS",
    "C4-EXACT-MESSAGE-HASHES",
    "C5-TRANSACTION-LEDGER",
]
if [g.get("gate_id") for g in gates] != expected_gate_ids:
    raise SystemExit("operator authority gate order changed or is incomplete")
for gate in gates:
    if gate.get("may_authorize_action") is not False:
        raise SystemExit(f"operator authority gate may not authorize action: {gate.get('gate_id')}")
results = {g.get("gate_id"): g.get("result") for g in gates}
for gate in ["C1-OPERATOR-AUTHORITY", "C2-PRIVATE-ROOTS", "C4-EXACT-MESSAGE-HASHES", "C5-TRANSACTION-LEDGER"]:
    if not results.get(gate, "").startswith("fail-closed"):
        raise SystemExit(f"{gate} must fail closed in public release")
if results.get("C3-ROUTE-FRESHNESS") != "pass-for-routing-orientation-only":
    raise SystemExit("route freshness must remain routing orientation only")

for key, value in packet.get("overclaim_locks", {}).items():
    if value is not False:
        raise SystemExit(f"operator authority overclaim lock must be false: {key}")
for key in ["message_sent", "counterparty_contacted", "response_clock_started", "raw_inbound_artifact_exists"]:
    if packet.get("no_contact_state", {}).get(key) is not False:
        raise SystemExit(f"operator authority no-contact state must be false: {key}")
if packet.get("no_contact_state", {}).get("live_floor_effect") != 0:
    raise SystemExit("operator authority packet must have zero live-floor effect")

# The current public transaction must still abort; a compiler must not supersede it.
transaction = load(refs["send_attempt_transaction_ledger"])
if transaction.get("current_result") != "NO-SEND-FAIL-CLOSED":
    raise SystemExit("operator authority packet source transaction must remain NO-SEND-FAIL-CLOSED")

# Front doors must lead with the compiler layer and avoid treating it as an action.
for rel in ["README.md", "START_HERE.md", "docs/README.md"]:
    text = (ROOT / rel).read_text(encoding="utf-8")[:8000].lower()
    for term in [packet_rel.lower(), "operator-authority", "not-actionable-no-private-authority", "no-send-fail-closed"]:
        if term not in text:
            raise SystemExit(f"front door missing operator-authority term {term}: {rel}")

status = load("SURFACE-STATUS.json")
if status.get("revision") != REV or status.get("no_live_floor_effect") is not True:
    raise SystemExit("SURFACE-STATUS revision/no-floor mismatch")
for rel in required:
    if rel not in status.get("new_surfaces", []):
        raise SystemExit(f"SURFACE-STATUS missing operator-authority surface: {rel}")
status_text = json.dumps(status).lower()
for term in [packet_rel.lower(), "not-actionable-no-private-authority", "no-send-fail-closed"]:
    if term not in status_text:
        raise SystemExit(f"SURFACE-STATUS missing operator-authority term: {term}")

queue = load("FOLLOWTHROUGH-QUEUE.json")
for entry in queue.get("entries", []):
    if entry.get("id") in ["FT-0205-FIRST-REAL-ARTIFACT-DROP", "FT-0207-FIRST-LIVE-EVIDENCE-ACQUISITION", "FT-0199-ACTUAL-LIVE-COUNTERPARTY-RESPONSE"]:
        text = json.dumps(entry).lower()
        for term in [packet_rel.lower(), "operator-authority", "no-send-fail-closed", "private authority"]:
            if term not in text:
                raise SystemExit(f"{entry.get('id')} missing operator-authority term: {term}")

print("audit_rev0273_operator_authority_packet: OK")
