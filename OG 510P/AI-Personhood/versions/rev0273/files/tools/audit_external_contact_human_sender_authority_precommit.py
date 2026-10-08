#!/usr/bin/env python3
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REPORT_REL = f"examples/external-contact-human-sender-authority-precommit-{REV}-aiid.json"
SCHEMA_REL = "schemas/external-contact-human-sender-authority-precommit.schema.json"
FIXTURE_REL = "fixtures/negative-tests/external-contact-human-sender-authority-precommit-unsigned-as-authorized.json"

try:
    from jsonschema import Draft202012Validator
except Exception:  # pragma: no cover
    Draft202012Validator = None


def load_json(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def sha_bytes(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate(schema, obj, label):
    if Draft202012Validator is None:
        return
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(obj), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{label} fails external-contact-human-sender-authority-precommit.schema.json: {errors[0].message}")

schema = load_json(SCHEMA_REL)
report = load_json(REPORT_REL)
validate(schema, report, REPORT_REL)

if report.get("revision") != REV:
    raise SystemExit("human/sender authority precommit revision mismatch")
if report.get("no_live_floor_effect") is not True:
    raise SystemExit("human/sender authority precommit must be no-floor")
if report.get("precommit_state") != "unsigned-human-sender-authority-precommit-no-send":
    raise SystemExit("human/sender authority precommit must remain unsigned/no-send")

refs = report.get("source_refs", {})
for name, rel in refs.items():
    if not rel or not (ROOT / rel).exists():
        raise SystemExit(f"human/sender authority precommit missing source: {name}={rel}")

request = load_json(refs["request_packet"])
card = load_json(refs["dispatch_authorization_card"])
gate = load_json(refs["send_readiness_gate"])
manifest = load_json(refs["public_payload_manifest"])
conflict = load_json(refs["conflict_coercion_review"])
transport = load_json(refs["transport_capture_plan"])
hash_run = load_json(refs["hash_recompute_dry_run"])
for label, obj in [
    ("request", request),
    ("card", card),
    ("gate", gate),
    ("manifest", manifest),
    ("conflict", conflict),
    ("transport", transport),
    ("hash_run", hash_run),
]:
    if obj.get("revision") != REV:
        raise SystemExit(f"human/sender authority source revision mismatch: {label}")
    if obj.get("no_live_floor_effect") is not True:
        raise SystemExit(f"human/sender authority source must be no-floor: {label}")

body = request.get("outgoing_request", {}).get("body", "").strip()
body_hash = sha_text(body)
mail_hash = sha_bytes(refs["mail_ready_draft"])
payload_hash = sha_bytes(refs["public_payload_manifest"])
b = report.get("exact_message_binding", {})
if b.get("recipient") != card.get("selected_candidate", {}).get("public_channel_locator"):
    raise SystemExit("human/sender authority recipient mismatch with dispatch card")
if b.get("subject") != request.get("outgoing_request", {}).get("subject"):
    raise SystemExit("human/sender authority subject mismatch")
if b.get("body_word_count") != len(body.split()) or b.get("body_sha256") != body_hash:
    raise SystemExit("human/sender authority body binding mismatch")
if b.get("mail_ready_draft_sha256") != mail_hash:
    raise SystemExit("human/sender authority mail-ready draft hash mismatch")
if b.get("public_payload_manifest_sha256") != payload_hash:
    raise SystemExit("human/sender authority payload manifest hash mismatch")
if b.get("public_payload_item_count") != len(manifest.get("public_payload_items", [])):
    raise SystemExit("human/sender authority payload count mismatch")
if b.get("signature_must_bind_all_hashes") is not True:
    raise SystemExit("human/sender authority signature must bind all hashes")

slots = report.get("unsigned_authorization_slots", {})
for key in ["human_authorizer_id", "authorizer_role", "sender_account_or_channel", "sender_authority_basis", "signed_at", "signature_or_attestation_hash"]:
    if slots.get(key) is not None:
        raise SystemExit(f"human/sender authority precommit must not fill unsigned slot: {key}")
if slots.get("send_permitted_now") is not False:
    raise SystemExit("human/sender authority precommit must not permit send now")

attest = " ".join(report.get("required_human_attestations", [])).lower()
for term in ["exact recipient", "sender authority", "vault", "hash", "transport", "not custody", "not intake", "not live-floor"]:
    if term not in attest:
        raise SystemExit(f"human/sender authority attestations missing term: {term}")

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
        raise SystemExit(f"human/sender authority residual blocker must remain true: {key}")
if res.get("precommit_may_satisfy_send_readiness_gate") is not False:
    raise SystemExit("human/sender authority precommit must not satisfy send-readiness gate")

# The gate must still report human signature and sender authority as unsatisfied.
unsatisfied = set(gate.get("blocker_resolution_summary", {}).get("unsatisfied_precondition_ids", []))
for blocker in ["human-signature", "sender-authority", "private-vault-roots", "public-locator-recheck", "payload-and-body-hash-recompute"]:
    if blocker not in unsatisfied:
        raise SystemExit(f"human/sender authority precommit found gate unexpectedly satisfied: {blocker}")

for key, value in report.get("downstream_locks", {}).items():
    if value is not False:
        raise SystemExit(f"human/sender authority downstream lock must be false: {key}")
for rel in report.get("related_surfaces", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"human/sender authority related surface missing: {rel}")

fixture = load_json(FIXTURE_REL)
if "external-contact-human-sender-authority-precommit" not in fixture.get("target_filings", []):
    raise SystemExit("human/sender authority fixture does not target precommit")
if fixture.get("severity") != "critical":
    raise SystemExit("human/sender authority fixture must be critical")

if Draft202012Validator is not None:
    validator = Draft202012Validator(schema)
    mut = copy.deepcopy(report)
    mut["unsigned_authorization_slots"]["send_permitted_now"] = True
    if not list(validator.iter_errors(mut)):
        raise SystemExit("schema failed to reject unsigned precommit as send-authorized")
    mut2 = copy.deepcopy(report)
    mut2["residual_blockers"]["precommit_may_satisfy_send_readiness_gate"] = True
    if not list(validator.iter_errors(mut2)):
        raise SystemExit("schema failed to reject precommit satisfying send-readiness gate")
    mut3 = copy.deepcopy(report)
    mut3["downstream_locks"]["may_treat_precommit_as_dispatch"] = True
    if not list(validator.iter_errors(mut3)):
        raise SystemExit("schema failed to reject precommit as dispatch")

print("audit_external_contact_human_sender_authority_precommit: OK")
