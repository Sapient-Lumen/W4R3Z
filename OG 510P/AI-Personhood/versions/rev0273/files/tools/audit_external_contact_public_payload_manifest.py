#!/usr/bin/env python3
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
MANIFEST_REL = f"examples/external-contact-public-payload-manifest-{REV}-aiid.json"
SCHEMA_REL = "schemas/external-contact-public-payload-manifest.schema.json"
FIXTURE_REL = "fixtures/negative-tests/external-contact-public-payload-manifest-body-drift.json"

try:
    from jsonschema import Draft202012Validator
except Exception:  # pragma: no cover
    Draft202012Validator = None


def load_json(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

def sha_bytes(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()

def sha_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

schema = load_json(SCHEMA_REL)
manifest = load_json(MANIFEST_REL)
if Draft202012Validator is not None:
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(manifest), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{MANIFEST_REL} fails external-contact-public-payload-manifest.schema.json: {errors[0].message}")

if manifest.get("revision") != REV:
    raise SystemExit("payload manifest revision mismatch")
if manifest.get("no_live_floor_effect") is not True:
    raise SystemExit("payload manifest must be no-live-floor")
for rel_key in ["source_request_packet_ref", "source_send_branch_handoff_ref", "source_mail_ready_draft_ref"]:
    rel = manifest.get(rel_key)
    if not rel or not (ROOT / rel).exists():
        raise SystemExit(f"payload manifest missing linked surface: {rel_key}")
request = load_json(manifest["source_request_packet_ref"])
body = request.get("outgoing_request", {}).get("body", "").strip()
body_hash = sha_text(body)
if manifest["message_binding"]["final_outgoing_body_sha256"] != body_hash:
    raise SystemExit("payload manifest body hash does not match request packet body")
if manifest["message_binding"]["body_word_count"] != len(body.split()):
    raise SystemExit("payload manifest word count does not match request body")
if len(body.split()) > 260:
    raise SystemExit("payload-bound body is too long for first-send route")
mail_rel = manifest["source_mail_ready_draft_ref"]
mail_text = (ROOT / mail_rel).read_text(encoding="utf-8")
mail_hash = sha_bytes(mail_rel)
if manifest["message_binding"]["mail_ready_draft_sha256"] != mail_hash:
    raise SystemExit("payload manifest mail-ready hash mismatch")
if f"X-AI-Personhood-Body-SHA256: {body_hash}" not in mail_text:
    raise SystemExit("mail-ready draft body header does not match payload manifest")
if body not in mail_text:
    raise SystemExit("mail-ready draft does not contain exact request body")
roles = {item["role"] for item in manifest.get("public_payload_items", [])}
if roles != {"one-page-preservation-formation-ask", "machine-checkable-request-packet"}:
    raise SystemExit(f"payload manifest roles incorrect: {roles}")
for item in manifest.get("public_payload_items", []):
    rel = item["rel_path"]
    path = ROOT / rel
    if not path.exists():
        raise SystemExit(f"payload item missing: {rel}")
    if item["sha256"] != sha_bytes(rel):
        raise SystemExit(f"payload item sha mismatch: {rel}")
    if item["size_bytes"] != path.stat().st_size:
        raise SystemExit(f"payload item size mismatch: {rel}")
    for key in ["include_if_sent"]:
        if item.get(key) is not True:
            raise SystemExit(f"payload item must keep {key}=true: {rel}")
    for key in ["raw_private_evidence", "hash_may_substitute_for_raw_custody", "attachment_may_create_status_or_floor"]:
        if item.get(key) is not False:
            raise SystemExit(f"payload item overclaims {key}: {rel}")
for key, value in manifest.get("pre_send_requires", {}).items():
    if value is not True:
        raise SystemExit(f"pre-send requirement not true: {key}")
for key, value in manifest.get("operational_state", {}).items():
    if value is not False:
        raise SystemExit(f"payload manifest operational state overclaims: {key}")
for key, value in manifest.get("downstream_locks", {}).items():
    if value is not False:
        raise SystemExit(f"payload manifest downstream lock overclaims: {key}")
for rel in manifest.get("related_surfaces", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"payload manifest related surface missing: {rel}")

fixture = load_json(FIXTURE_REL)
if "external-contact-public-payload-manifest" not in fixture.get("target_filings", []):
    raise SystemExit("payload manifest fixture does not target the manifest")
if fixture.get("severity") != "critical":
    raise SystemExit("payload manifest fixture must be critical")

if Draft202012Validator is not None:
    validator = Draft202012Validator(schema)
    mut = copy.deepcopy(manifest)
    mut["message_binding"]["payload_manifest_may_substitute_for_send_proof"] = True
    if not list(validator.iter_errors(mut)):
        raise SystemExit("schema failed to reject payload-as-send-proof overclaim")
    mut2 = copy.deepcopy(manifest)
    mut2["public_payload_items"][0]["hash_may_substitute_for_raw_custody"] = True
    if not list(validator.iter_errors(mut2)):
        raise SystemExit("schema failed to reject attachment hash as raw custody")
    mut3 = copy.deepcopy(manifest)
    mut3["operational_state"]["message_sent"] = True
    if not list(validator.iter_errors(mut3)):
        raise SystemExit("schema failed to reject message_sent=true")

print("audit_external_contact_public_payload_manifest: OK")
