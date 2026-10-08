#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()

try:
    from jsonschema import Draft202012Validator
except Exception:  # pragma: no cover
    Draft202012Validator = None


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def validate(schema_rel, data_rel):
    if Draft202012Validator is None:
        return
    schema = load(schema_rel)
    data = load(data_rel)
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{data_rel} fails {schema_rel}: {errors[0].message}")

branch_rel = f"examples/human-branch-decision-record-{REV}-unsigned-template.json"
matrix_rel = f"examples/reviewer-route-due-diligence-matrix-{REV}-public-source-no-contact.json"
precommit_rel = f"examples/pre-send-custody-precommit-{REV}-no-private-root-selected.json"
packet_rel = f"examples/reviewer-first-contact-packet-{REV}-eleos-not-sent.json"
workbook_rel = f"examples/field-artifact-capture-workbook-{REV}-reviewer-first-no-send.json"
six_rel = f"examples/six-artifact-pilot-state-{REV}-preservation-review.json"
route_rel = f"examples/route-decision-card-{REV}-send-nosend-retarget.json"

for schema, rel in [
    ("schemas/human-branch-decision-record.schema.json", branch_rel),
    ("schemas/reviewer-route-due-diligence-matrix.schema.json", matrix_rel),
    ("schemas/pre-send-custody-precommit.schema.json", precommit_rel),
    ("schemas/reviewer-first-contact-packet.schema.json", packet_rel),
    ("schemas/field-artifact-capture-workbook.schema.json", workbook_rel),
    ("schemas/six-artifact-pilot-state.schema.json", six_rel),
    ("schemas/route-decision-card.schema.json", route_rel),
]:
    if not (ROOT / rel).exists():
        raise SystemExit(f"missing authority-to-artifact surface: {rel}")
    validate(schema, rel)

branch = load(branch_rel)
matrix = load(matrix_rel)
precommit = load(precommit_rel)
packet = load(packet_rel)
workbook = load(workbook_rel)
six = load(six_rel)
route = load(route_rel)
for label, obj in [
    ("branch", branch), ("matrix", matrix), ("precommit", precommit),
    ("packet", packet), ("workbook", workbook), ("six", six), ("route", route),
]:
    if obj.get("revision") != REV or obj.get("no_live_floor_effect") is not True:
        raise SystemExit(f"{label} revision/no-floor mismatch")

if branch.get("record_state") != "template-unsigned-no-authority":
    raise SystemExit("human branch decision record must remain an unsigned template in this release")
authorizer = branch.get("authorizer", {})
if authorizer.get("signature_present") is not False or authorizer.get("timestamp_present") is not False:
    raise SystemExit("unsigned template must not contain signature/timestamp authority")
selected = branch.get("selected_choice", {})
if selected.get("selected_now") is not False or selected.get("choice_id") != "NONE":
    raise SystemExit("branch template must not select a branch")
branch_locks = branch.get("overclaim_locks", {})
for key in [
    "may_authorize_send_without_signature",
    "may_treat_template_as_authority",
    "may_start_response_clock",
    "may_claim_counterparty_contacted",
    "may_create_custody_intake_import_or_floor_effect",
]:
    if branch_locks.get(key) is not False:
        raise SystemExit(f"branch overclaim lock not false: {key}")

bindings = branch.get("bindings", {})
expected_bindings = {
    "route_matrix_ref": matrix_rel,
    "reviewer_packet_ref": packet_rel,
    "capture_workbook_ref": workbook_rel,
    "custody_precommit_ref": precommit_rel,
    "six_artifact_pilot_ref": six_rel,
}
if bindings != expected_bindings:
    raise SystemExit(f"branch binding mismatch: {bindings}")

routes = {r.get("route_id"): r for r in matrix.get("candidate_routes", [])}
for required in ["ROUTE-ELEOS-PRIMARY", "ROUTE-AIID-SECONDARY", "ROUTE-PROVIDER-DEPRECATION", "ROUTE-CONSCIUM-FALLBACK"]:
    if required not in routes:
        raise SystemExit(f"route due-diligence matrix missing {required}")
if matrix.get("recommendation", {}).get("primary_route_id") != "ROUTE-ELEOS-PRIMARY":
    raise SystemExit("route due-diligence primary must remain Eleos")
if routes["ROUTE-ELEOS-PRIMARY"].get("fit_score", 0) <= routes["ROUTE-AIID-SECONDARY"].get("fit_score", 0):
    raise SystemExit("Eleos must outrank AIID for this non-incident preservation/review ask")
if routes["ROUTE-ELEOS-PRIMARY"].get("fit_score", 0) <= routes["ROUTE-CONSCIUM-FALLBACK"].get("fit_score", 0):
    raise SystemExit("Eleos must outrank fallback routes unless a new human retarget decision exists")
if any(r.get("authorized_now") is not False for r in routes.values()):
    raise SystemExit("route matrix must not authorize contact")
for key, value in matrix.get("send_locks", {}).items():
    if value is not False:
        raise SystemExit(f"route matrix send lock must be false: {key}")
source_refs = set()
for r in routes.values():
    source_refs.update(r.get("source_refs", []))
for ref in ["REF-0776", "REF-0783", "REF-0784", "REF-0785"]:
    if ref not in source_refs:
        raise SystemExit(f"route matrix missing source ref {ref}")

if precommit.get("precommit_state") != "template-no-private-root-selected":
    raise SystemExit("pre-send custody precommit must remain no-private-root-selected")
roots = precommit.get("private_roots", {})
for key in ["raw_sent_copy_root_selected", "transport_proof_root_selected", "raw_inbound_root_selected", "sealed_evidence_root_selected"]:
    if roots.get(key) is not False:
        raise SystemExit(f"private root unexpectedly selected: {key}")
if roots.get("current_public_tree_contains_raw_private_material") is not False:
    raise SystemExit("public tree may not contain raw private material")
for key, value in precommit.get("overclaim_locks", {}).items():
    if value is not False:
        raise SystemExit(f"precommit overclaim lock must be false: {key}")
if len(precommit.get("blocked_until", [])) < 5:
    raise SystemExit("precommit does not block enough send preconditions")

if packet.get("packet_state") != "prepared-not-authorized-not-sent":
    raise SystemExit("reviewer-first packet must stay prepared/not-authorized/not-sent")
channel = packet.get("channel", {})
for key in ["send_authorized_now", "counterparty_contacted", "response_clock_started"]:
    if channel.get(key) is not False:
        raise SystemExit(f"packet channel overclaims {key}")
packet_text = json.dumps(packet).lower()
for term in ["human branch-decision", "route due-diligence", "private vault roots", "final hash recompute"]:
    if term not in packet_text:
        raise SystemExit(f"packet missing pre-send capture term: {term}")

rows = {r.get("artifact_id"): r for r in workbook.get("artifact_rows", [])}
if rows.get("A1-BRANCH-REQUEST", {}).get("state") != "prepared-not-authorized":
    raise SystemExit("A1 must remain prepared/not-authorized")
if rows.get("A2-TRANSPORT-DELIVERY", {}).get("state") != "missing":
    raise SystemExit("A2 must remain missing before send")
for rel in [branch_rel, matrix_rel, packet_rel]:
    if rel not in rows["A1-BRANCH-REQUEST"].get("current_evidence", []):
        raise SystemExit(f"A1 workbook evidence missing {rel}")
if precommit_rel not in rows["A2-TRANSPORT-DELIVERY"].get("current_evidence", []):
    raise SystemExit("A2 workbook must cite custody precommit as blocker, not proof")

if six.get("pilot_state") != "prepared-not-authorized":
    raise SystemExit("six-artifact pilot must remain prepared-not-authorized")
a1 = next((a for a in six.get("artifact_chain", []) if a.get("artifact_id") == "A1-BRANCH-REQUEST"), None)
if not a1 or a1.get("current_state") != "prepared-not-authorized":
    raise SystemExit("six-artifact A1 must remain prepared/not-authorized")
if not any(branch_rel in x for x in a1.get("completion_evidence", [])):
    raise SystemExit("six-artifact A1 must bind to signed branch record template")
if "file_count_not_a_measure" not in json.dumps(six):
    raise SystemExit("six-artifact dashboard must reject symbolic outcome measures")

route_text = json.dumps(route).lower()
for term in ["human authority", "private custody", "no route score", "authorizes contact"]:
    if term not in route_text:
        raise SystemExit(f"route decision card missing authority/custody term: {term}")

queue = load("FOLLOWTHROUGH-QUEUE.json")
if queue.get("revision") != REV:
    raise SystemExit("queue revision mismatch")
entries = {e.get("id"): e for e in queue.get("entries", [])}
for qid in ["FT-0205-FIRST-REAL-ARTIFACT-DROP", "FT-0207-FIRST-LIVE-EVIDENCE-ACQUISITION", "FT-0199-ACTUAL-LIVE-COUNTERPARTY-RESPONSE"]:
    e = entries.get(qid)
    if not e:
        raise SystemExit(f"missing queue item {qid}")
    text = " ".join(str(e.get(k, "")) for k in ["receiving_surface", "next_action", "closure_condition", "why"]).lower()
    for term in ["human-branch-decision-record", "pre-send-custody-precommit", "no-send", "route score"]:
        if term not in text:
            raise SystemExit(f"{qid} does not bind to authority/custody anti-laundering term: {term}")
    if f"six-artifact-pilot-state-{REV}" not in e.get("receiving_surface", ""):
        raise SystemExit(f"{qid} must receive into current six-artifact pilot")

status = load("SURFACE-STATUS.json")
for rel in [branch_rel, matrix_rel, precommit_rel, f"docs/30-transition/{REV}-authority-to-artifact-runbook.md", f"docs/00-meta/{REV}-authority-to-artifact-refactor.md", "schemas/human-branch-decision-record.schema.json", "schemas/reviewer-route-due-diligence-matrix.schema.json", "schemas/pre-send-custody-precommit.schema.json"]:
    if rel not in status.get("new_surfaces", []):
        raise SystemExit(f"SURFACE-STATUS missing new authority-to-artifact surface: {rel}")
    if not (ROOT / rel).exists():
        raise SystemExit(f"SURFACE-STATUS names missing authority-to-artifact path: {rel}")
status_text = json.dumps(status).lower()
for term in ["unsigned", "custody", "no-contact", "zero-floor"]:
    if term not in status_text:
        raise SystemExit(f"SURFACE-STATUS missing state term: {term}")

for rel in ["README.md", "START_HERE.md", "docs/README.md"]:
    text = (ROOT / rel).read_text(encoding="utf-8")[:2500].lower()
    for term in [REV, "authority-to-artifact", "no organization has been contacted"] if rel != "docs/README.md" else [REV, "authority-to-artifact"]:
        if term not in text:
            raise SystemExit(f"{rel} opening missing {term}")

print("audit_rev0273_authority_to_artifact: OK")
