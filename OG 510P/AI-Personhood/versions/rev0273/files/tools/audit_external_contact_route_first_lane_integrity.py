#!/usr/bin/env python3
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REPORT_REL = f"examples/external-contact-route-first-lane-integrity-report-{REV}-aiid.json"
SCHEMA_REL = "schemas/external-contact-route-first-lane-integrity-report.schema.json"
FIXTURE_REL = "fixtures/negative-tests/external-contact-route-first-lane-integrity-report-branch-unsafe.json"

try:
    from jsonschema import Draft202012Validator
except Exception:  # pragma: no cover
    Draft202012Validator = None


def load_json(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha_bytes(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def validate(schema, obj, label):
    if Draft202012Validator is None:
        return
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(obj), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{label} fails external-contact-route-first-lane-integrity-report.schema.json: {errors[0].message}")

schema = load_json(SCHEMA_REL)
report = load_json(REPORT_REL)
validate(schema, report, REPORT_REL)

if report.get("revision") != REV:
    raise SystemExit("route-first lane integrity report revision mismatch")
if report.get("report_state") != "blocked-current-route-first-lane-integrity-clean-no-send":
    raise SystemExit("route-first lane integrity report must remain blocked/current/no-send")
if report.get("no_live_floor_effect") is not True:
    raise SystemExit("route-first lane integrity report must be no-floor")

refs = report.get("source_refs", {})
for name, rel in refs.items():
    if not rel or not (ROOT / rel).exists():
        raise SystemExit(f"lane integrity report source missing: {name}={rel}")

preflight = load_json(refs["route_first_preflight"])
send_gate = load_json(refs["route_first_send_capture_gate"])
reply = load_json(refs["route_first_reply_disposition"])
stage_two = load_json(refs["stage_two_authorization_gate"])
hold = load_json(refs["route_first_branch_hold"])
pack = load_json(refs["route_first_operator_execution_pack"])
route_first_authority = load_json(refs["route_first_human_sender_authority_precommit"])
locator = load_json(refs["current_public_locator_recheck"])
transport = load_json(refs["transport_capture_plan"])
trace = load_json(refs["send_trace_shell"])
proof = load_json(refs["send_proof_record"])
delivery = load_json(refs["delivery_status_record"])
inbound_precommit = load_json(refs["inbound_vault_precommit"])
inbound_capture = load_json(refs["inbound_capture_shell"])
board = load_json(refs["operating_board"])

for label, obj in {
    "preflight": preflight,
    "send_gate": send_gate,
    "reply": reply,
    "stage_two": stage_two,
    "hold": hold,
    "pack": pack,
    "route_first_authority": route_first_authority,
    "locator": locator,
    "transport": transport,
    "trace": trace,
    "proof": proof,
    "delivery": delivery,
    "inbound_precommit": inbound_precommit,
    "inbound_capture": inbound_capture,
    "board": board,
}.items():
    if obj.get("revision") != REV:
        raise SystemExit(f"lane integrity source {label} not current revision")

msg = report.get("message_recompute", {})
body_rel = msg.get("body_ref")
eml_rel = msg.get("mail_ready_draft_ref")
if body_rel != refs.get("route_first_body") or eml_rel != refs.get("route_first_mail_ready_draft"):
    raise SystemExit("lane integrity report message refs disagree with source refs")
body = (ROOT / body_rel).read_text(encoding="utf-8").strip()
eml = (ROOT / eml_rel).read_text(encoding="utf-8")
body_hash = sha_text(body)
eml_hash = sha_bytes(eml_rel)
if msg.get("body_word_count") != len(body.split()):
    raise SystemExit("lane integrity route-first word count stale")
if msg.get("body_sha256") != body_hash or msg.get("mail_ready_draft_sha256") != eml_hash:
    raise SystemExit("lane integrity route-first hashes stale")
if msg.get("attachments_included") is not False or msg.get("payload_item_count_attached") != 0:
    raise SystemExit("lane integrity report must remain no-attachment")
if "Content-Disposition: attachment" in eml or "multipart/" in eml.lower():
    raise SystemExit("lane integrity .eml contains attachment/multipart markers")
if body not in eml:
    raise SystemExit("lane integrity .eml does not contain exact body")

bindings = [
    ("preflight", preflight.get("route_first_message", {})),
    ("send_gate", send_gate.get("message_binding", {})),
    ("reply", reply.get("route_first_binding", {})),
    ("operator_pack", pack.get("exact_route_first_message", {})),
    ("route_first_authority", route_first_authority.get("exact_route_first_binding", {})),
]
for label, bind in bindings:
    if bind.get("body_sha256") != body_hash:
        raise SystemExit(f"lane integrity body hash disagrees with {label}")
    if bind.get("mail_ready_draft_sha256") != eml_hash:
        raise SystemExit(f"lane integrity .eml hash disagrees with {label}")
    if bind.get("body_word_count") != len(body.split()):
        raise SystemExit(f"lane integrity word count disagrees with {label}")
for key in ["hashes_match_preflight", "hashes_match_send_gate", "hashes_match_reply_disposition", "hashes_match_operator_pack", "mail_ready_contains_no_attachment_headers"]:
    if msg.get(key) is not True:
        raise SystemExit(f"lane integrity message recompute missing true flag: {key}")

states = report.get("lane_gate_states", {})
expected = {
    "preflight_state": preflight.get("preflight_state"),
    "send_capture_gate_state": send_gate.get("gate_state"),
    "reply_disposition_state": reply.get("disposition_state"),
    "stage_two_gate_state": stage_two.get("gate_state"),
    "branch_hold_state": hold.get("hold_state"),
    "operator_pack_state": pack.get("pack_state"),
    "route_first_authority_precommit_state": route_first_authority.get("precommit_state"),
    "current_public_locator_recheck_state": locator.get("recheck_state"),
    "transport_plan_state": transport.get("plan_state"),
    "send_trace_state": trace.get("send_trace_state"),
    "send_proof_state": proof.get("send_proof_state"),
    "delivery_status_state": delivery.get("delivery_status_state"),
    "inbound_precommit_state": inbound_precommit.get("precommit_state"),
    "inbound_capture_state": inbound_capture.get("capture_state"),
    "operating_board_active_count": board.get("queue_counts", {}).get("active_entries"),
}
for key, observed in expected.items():
    if states.get(key) != observed:
        raise SystemExit(f"lane integrity state mismatch for {key}: report={states.get(key)!r}, observed={observed!r}")
if states.get("operating_board_active_count") != 7:
    raise SystemExit("lane integrity report must preserve seven active operating-board entries")

if send_gate.get("blocker_resolution_summary", {}).get("gate_remains_blocked") is not True:
    raise SystemExit("lane integrity send/capture gate must remain blocked")
if stage_two.get("blocker_resolution_summary", {}).get("gate_remains_blocked") is not True:
    raise SystemExit("lane integrity stage-two gate must remain blocked")
if hold.get("decision", {}).get("route_first_send_permitted_now") is not False:
    raise SystemExit("lane integrity cannot bind a hold that permits send")
if pack.get("pack_state") != "prepared-not-authorized-not-sent":
    raise SystemExit("lane integrity operator pack must remain prepared/not-authorized/not-sent")
if route_first_authority.get("precommit_state") != "unsigned-route-first-human-sender-authority-precommit-no-send":
    raise SystemExit("lane integrity route-first authority precommit must remain unsigned/no-send")
if route_first_authority.get("scope_controls", {}).get("full_payload_precommit_may_substitute_for_route_first_signature") is not False:
    raise SystemExit("lane integrity cannot permit legacy full-payload precommit to substitute for route-first signature")

required_blockers = {"human-signature", "sender-authority", "send-time-public-locator-recheck", "private-vault-roots", "final-route-first-hash-recompute", "actual-transport-proof"}
observed_blockers = {b.get("blocker_id") for b in report.get("remaining_blockers", [])}
if not required_blockers.issubset(observed_blockers):
    raise SystemExit(f"lane integrity missing blockers: {sorted(required_blockers - observed_blockers)}")
for blocker in report.get("remaining_blockers", []):
    if blocker.get("required_before_send") is not True or blocker.get("satisfied_now") is not False:
        raise SystemExit(f"lane integrity blocker overclaimed: {blocker.get('blocker_id')}")
    if blocker.get("may_be_satisfied_inside_public_release") is not False:
        raise SystemExit(f"lane integrity blocker wrongly satisfiable inside public release: {blocker.get('blocker_id')}")

policy = report.get("finalization_policy", {})
for key in ["report_may_authorize_send", "operator_pack_may_authorize_send", "stage_two_may_auto_send_after_willing_reply"]:
    if policy.get(key) is not False:
        raise SystemExit(f"lane integrity finalization policy overclaims {key}")
for key in ["must_rerun_hashes_after_any_edit", "must_recheck_public_locator_at_send_time", "must_select_private_vault_roots_before_send", "must_capture_transport_proof_if_sent", "route_first_must_remain_no_attachment"]:
    if policy.get(key) is not True:
        raise SystemExit(f"lane integrity finalization policy missing {key}")

nonclosure = report.get("nonclosure_controls", {})
if nonclosure.get("lane_report_may_close_first_artifact_tasks") is not False:
    raise SystemExit("lane integrity report cannot close first-artifact tasks")
needed = {"FT-0205-FIRST-REAL-ARTIFACT-DROP", "FT-0207-FIRST-LIVE-EVIDENCE-ACQUISITION", "FT-0199-ACTUAL-LIVE-COUNTERPARTY-RESPONSE"}
if not needed.issubset(set(nonclosure.get("do_not_close_by_narrative", []))):
    raise SystemExit("lane integrity missing do-not-close task controls")
if nonclosure.get("operating_board_active_count_observed") != 7:
    raise SystemExit("lane integrity nonclosure must preserve seven active board entries")

for section in ["operational_state", "downstream_locks"]:
    for key, val in report.get(section, {}).items():
        if val is not False:
            raise SystemExit(f"lane integrity {section} overclaims: {key}")

fixture = load_json(FIXTURE_REL)
if "external-contact-route-first-lane-integrity-report" not in fixture.get("target_filings", []):
    raise SystemExit("lane integrity negative fixture does not target report")
if fixture.get("severity") != "critical":
    raise SystemExit("lane integrity negative fixture must be critical")

if Draft202012Validator is not None:
    validator = Draft202012Validator(schema)
    mut = copy.deepcopy(report)
    mut["message_recompute"]["attachments_included"] = True
    if not list(validator.iter_errors(mut)):
        raise SystemExit("schema failed to reject route-first attachment overclaim")
    mut2 = copy.deepcopy(report)
    mut2["finalization_policy"]["report_may_authorize_send"] = True
    if not list(validator.iter_errors(mut2)):
        raise SystemExit("schema failed to reject lane report as authorization")
    mut3 = copy.deepcopy(report)
    mut3["downstream_locks"]["may_treat_lane_integrity_as_authorization"] = True
    if not list(validator.iter_errors(mut3)):
        raise SystemExit("schema failed to reject lane report downstream overclaim")
    mut4 = copy.deepcopy(report)
    mut4["remaining_blockers"][0]["satisfied_now"] = True
    if not list(validator.iter_errors(mut4)):
        raise SystemExit("schema failed to reject satisfied blocker in public report")

print("audit_external_contact_route_first_lane_integrity: OK")
