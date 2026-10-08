#!/usr/bin/env python3
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REPORT_REL = f"examples/external-contact-route-first-human-sender-authority-precommit-{REV}-aiid.json"
SCHEMA_REL = "schemas/external-contact-route-first-human-sender-authority-precommit.schema.json"
FIXTURE_REL = "fixtures/negative-tests/external-contact-route-first-human-sender-authority-precommit-unsigned-as-authorized.json"

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
        raise SystemExit(f"{label} fails external-contact-route-first-human-sender-authority-precommit.schema.json: {errors[0].message}")


schema = load_json(SCHEMA_REL)
report = load_json(REPORT_REL)
validate(schema, report, REPORT_REL)

if report.get("revision") != REV:
    raise SystemExit("route-first human/sender authority precommit revision mismatch")
if report.get("precommit_state") != "unsigned-route-first-human-sender-authority-precommit-no-send":
    raise SystemExit("route-first human/sender precommit must remain unsigned/no-send")
if report.get("no_live_floor_effect") is not True:
    raise SystemExit("route-first human/sender precommit must be no-floor")

refs = report.get("source_refs", {})
for name, rel in refs.items():
    if not rel or not (ROOT / rel).exists():
        raise SystemExit(f"route-first human/sender precommit missing source: {name}={rel}")

preflight = load_json(refs["route_first_preflight"])
send_gate = load_json(refs["route_first_send_capture_gate"])
pack = load_json(refs["route_first_operator_execution_pack"])
lane = load_json(refs["route_first_lane_integrity_report"])
hold = load_json(refs["route_first_branch_hold"])
locator = load_json(refs["current_public_locator_recheck"])
hash_run = load_json(refs["hash_recompute_dry_run"])
transport = load_json(refs["transport_capture_plan"])
board = load_json(refs["operating_board"])
legacy_full = load_json(refs["full_payload_human_sender_precommit_legacy_context"])
for label, obj in [
    ("preflight", preflight),
    ("send_gate", send_gate),
    ("pack", pack),
    ("lane", lane),
    ("hold", hold),
    ("locator", locator),
    ("hash_run", hash_run),
    ("transport", transport),
    ("board", board),
    ("legacy_full", legacy_full),
]:
    if obj.get("revision") != REV:
        raise SystemExit(f"route-first human/sender source revision mismatch: {label}")

if send_gate.get("gate_state") != "blocked-route-first-no-human-send-no-transport":
    raise SystemExit("route-first human/sender precommit cannot bind unblocked send gate")
if hold.get("decision", {}).get("route_first_send_permitted_now") is not False:
    raise SystemExit("route-first human/sender precommit cannot bind a permissive hold")
if pack.get("pack_state") != "prepared-not-authorized-not-sent":
    raise SystemExit("route-first human/sender precommit must bind prepared/not-authorized operator pack")
if lane.get("report_state") != "blocked-current-route-first-lane-integrity-clean-no-send":
    raise SystemExit("route-first human/sender precommit must bind blocked lane-integrity report")
if board.get("queue_counts", {}).get("active_entries") != 7:
    raise SystemExit("route-first human/sender precommit must preserve seven active board entries")

binding = report.get("exact_route_first_binding", {})
body_rel = refs["route_first_body"]
eml_rel = refs["route_first_mail_ready_draft"]
body = (ROOT / body_rel).read_text(encoding="utf-8").strip()
body_hash = sha_text(body)
eml_hash = sha_bytes(eml_rel)
if binding.get("body_ref") != body_rel or binding.get("mail_ready_draft_ref") != eml_rel:
    raise SystemExit("route-first human/sender binding refs mismatch")
if binding.get("body_word_count") != len(body.split()):
    raise SystemExit("route-first human/sender body word count stale")
if binding.get("body_sha256") != body_hash or binding.get("mail_ready_draft_sha256") != eml_hash:
    raise SystemExit("route-first human/sender body/.eml hashes stale")
if binding.get("attachments_included") is not False or binding.get("payload_item_count_attached") != 0 or binding.get("stage_two_payload_attached") is not False:
    raise SystemExit("route-first human/sender precommit must remain no-attachment/stage-two-deferred")
for key in [
    "signature_must_bind_recipient_subject_body_and_eml_hashes",
    "signature_must_bind_no_attachment_limit",
    "signature_must_bind_stage_two_deferral",
]:
    if binding.get(key) is not True:
        raise SystemExit(f"route-first human/sender binding missing {key}")

source_bindings = [
    ("preflight", preflight.get("route_first_message", {})),
    ("send_gate", send_gate.get("message_binding", {})),
    ("operator_pack", pack.get("exact_route_first_message", {})),
    ("lane_integrity", lane.get("message_recompute", {})),
]
for label, bind in source_bindings:
    if bind.get("body_sha256") != body_hash:
        raise SystemExit(f"route-first human/sender body hash disagrees with {label}")
    if bind.get("mail_ready_draft_sha256") != eml_hash:
        raise SystemExit(f"route-first human/sender .eml hash disagrees with {label}")
    if bind.get("body_word_count") != len(body.split()):
        raise SystemExit(f"route-first human/sender word count disagrees with {label}")

# Prove the legacy full-payload precommit is not the same branch.
legacy_subject = legacy_full.get("exact_message_binding", {}).get("subject")
legacy_payload_count = legacy_full.get("exact_message_binding", {}).get("public_payload_item_count")
if legacy_subject == binding.get("subject") or legacy_payload_count == 0:
    raise SystemExit("legacy full-payload precommit is not clearly separated from route-first branch")

slots = report.get("unsigned_authorization_slots", {})
for key in ["human_authorizer_id", "authorizer_role", "sender_account_or_channel", "sender_authority_basis", "signed_at", "signature_or_attestation_hash"]:
    if slots.get(key) is not None:
        raise SystemExit(f"route-first human/sender precommit must not fill unsigned slot: {key}")
if slots.get("send_permitted_now") is not False:
    raise SystemExit("route-first human/sender precommit must not permit send now")

attest = " ".join(report.get("required_human_attestations", [])).lower()
for term in ["route-first", "no attachments", "stage-two", "sender authority", "vault", "hash", "not custody", "not intake", "not live-floor"]:
    if term not in attest:
        raise SystemExit(f"route-first human/sender attestations missing term: {term}")

scope = report.get("scope_controls", {})
for key in ["this_precommit_covers_route_first_only", "must_use_stage_two_authorization_gate_after_willing_reply"]:
    if scope.get(key) is not True:
        raise SystemExit(f"route-first human/sender scope missing true: {key}")
for key in ["full_payload_precommit_may_substitute_for_route_first_signature", "route_first_precommit_may_authorize_stage_two_payload", "may_attach_stage_two_payload_to_route_first_message", "willing_reply_may_auto_send_stage_two"]:
    if scope.get(key) is not False:
        raise SystemExit(f"route-first human/sender scope overclaims {key}")

res = report.get("residual_blockers", {})
for key in [
    "human_signature_still_required",
    "sender_authority_still_required",
    "private_vault_roots_still_required",
    "send_time_locator_recheck_still_required",
    "send_time_hash_recompute_still_required",
    "actual_transport_proof_still_absent",
]:
    if res.get(key) is not True:
        raise SystemExit(f"route-first human/sender residual blocker must remain true: {key}")
if res.get("precommit_may_satisfy_route_first_send_gate") is not False:
    raise SystemExit("route-first human/sender precommit must not satisfy send gate")

for section in ["operational_state", "downstream_locks"]:
    for key, val in report.get(section, {}).items():
        if val is not False:
            raise SystemExit(f"route-first human/sender {section} overclaims: {key}")
nonclosure = report.get("nonclosure_controls", {})
if nonclosure.get("precommit_may_close_first_artifact_tasks") is not False:
    raise SystemExit("route-first human/sender precommit cannot close first-artifact tasks")
needed = {"FT-0205-FIRST-REAL-ARTIFACT-DROP", "FT-0207-FIRST-LIVE-EVIDENCE-ACQUISITION", "FT-0199-ACTUAL-LIVE-COUNTERPARTY-RESPONSE"}
if not needed.issubset(set(nonclosure.get("do_not_close_by_narrative", []))):
    raise SystemExit("route-first human/sender precommit missing do-not-close controls")
if nonclosure.get("operating_board_active_count_observed") != 7:
    raise SystemExit("route-first human/sender precommit must preserve seven active board entries")

fixture = load_json(FIXTURE_REL)
if "external-contact-route-first-human-sender-authority-precommit" not in fixture.get("target_filings", []):
    raise SystemExit("route-first human/sender negative fixture does not target precommit")
if fixture.get("severity") != "critical":
    raise SystemExit("route-first human/sender negative fixture must be critical")

if Draft202012Validator is not None:
    validator = Draft202012Validator(schema)
    mut = copy.deepcopy(report)
    mut["unsigned_authorization_slots"]["send_permitted_now"] = True
    if not list(validator.iter_errors(mut)):
        raise SystemExit("schema failed to reject unsigned route-first precommit as send-authorized")
    mut2 = copy.deepcopy(report)
    mut2["scope_controls"]["route_first_precommit_may_authorize_stage_two_payload"] = True
    if not list(validator.iter_errors(mut2)):
        raise SystemExit("schema failed to reject route-first precommit as stage-two authorization")
    mut3 = copy.deepcopy(report)
    mut3["downstream_locks"]["may_treat_precommit_as_send"] = True
    if not list(validator.iter_errors(mut3)):
        raise SystemExit("schema failed to reject route-first precommit as send")
    mut4 = copy.deepcopy(report)
    mut4["exact_route_first_binding"]["attachments_included"] = True
    if not list(validator.iter_errors(mut4)):
        raise SystemExit("schema failed to reject route-first attachment overclaim")

print("audit_external_contact_route_first_human_sender_authority_precommit: OK")
