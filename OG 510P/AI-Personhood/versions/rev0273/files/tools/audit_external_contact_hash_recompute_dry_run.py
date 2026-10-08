#!/usr/bin/env python3
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REPORT_REL = f"examples/external-contact-hash-recompute-dry-run-{REV}-aiid.json"
SCHEMA_REL = "schemas/external-contact-hash-recompute-dry-run.schema.json"
FIXTURE_REL = "fixtures/negative-tests/external-contact-hash-recompute-dry-run-as-sendtime.json"

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
        raise SystemExit(f"{label} fails external-contact-hash-recompute-dry-run.schema.json: {errors[0].message}")

schema = load_json(SCHEMA_REL)
report = load_json(REPORT_REL)
validate(schema, report, REPORT_REL)

if report.get("revision") != REV:
    raise SystemExit("hash recompute dry-run revision mismatch")
if report.get("no_live_floor_effect") is not True:
    raise SystemExit("hash recompute dry-run must be no-floor")
if report.get("dry_run_state") != "current-public-tree-hashes-recomputed-no-send":
    raise SystemExit("hash recompute dry-run must remain current/no-send")

refs = report.get("source_refs", {})
for name, rel in refs.items():
    if not rel or not (ROOT / rel).exists():
        raise SystemExit(f"hash recompute missing source: {name}={rel}")
request = load_json(refs["request_packet"])
manifest = load_json(refs["public_payload_manifest"])
if request.get("revision") != REV or request.get("no_live_floor_effect") is not True:
    raise SystemExit("hash recompute request packet not current/no-floor")
if manifest.get("revision") != REV or manifest.get("no_live_floor_effect") is not True:
    raise SystemExit("hash recompute payload manifest not current/no-floor")

body = request.get("outgoing_request", {}).get("body", "").strip()
computed = {
    "body_word_count": len(body.split()),
    "body_sha256": sha_text(body),
    "mail_ready_draft_sha256": sha_bytes(refs["mail_ready_draft"]),
    "public_payload_manifest_sha256": sha_bytes(refs["public_payload_manifest"]),
    "one_page_ask_sha256": sha_bytes(refs["one_page_ask"]),
    "one_page_ask_size_bytes": (ROOT / refs["one_page_ask"]).stat().st_size,
    "machine_checkable_request_packet_sha256": sha_bytes(refs["machine_checkable_request_packet"]),
    "machine_checkable_request_packet_size_bytes": (ROOT / refs["machine_checkable_request_packet"]).stat().st_size,
    "payload_manifest_matches_files_now": True,
}
if report.get("computed_bindings") != computed:
    raise SystemExit("hash recompute dry-run computed bindings are stale")

manifest_items = {item["rel_path"]: item for item in manifest.get("public_payload_items", [])}
for rel in [refs["one_page_ask"], refs["machine_checkable_request_packet"]]:
    item = manifest_items.get(rel)
    if not item:
        raise SystemExit(f"payload manifest missing hash dry-run item: {rel}")
    if item.get("sha256") != sha_bytes(rel):
        raise SystemExit(f"payload manifest item sha stale: {rel}")
    if item.get("size_bytes") != (ROOT / rel).stat().st_size:
        raise SystemExit(f"payload manifest item size stale: {rel}")

policy = report.get("send_time_policy", {})
if policy.get("dry_run_may_satisfy_send_time_recompute") is not False:
    raise SystemExit("hash dry-run must not satisfy send-time recompute")
for key in ["must_rerun_immediately_before_send", "must_rerun_after_any_edit_or_attachment_change", "human_signature_must_bind_recomputed_hashes"]:
    if policy.get(key) is not True:
        raise SystemExit(f"hash dry-run policy missing true flag: {key}")
if policy.get("hashes_may_substitute_for_transport_proof_or_raw_custody") is not False:
    raise SystemExit("hash dry-run must not substitute for proof/custody")
for section in ["operational_state", "downstream_locks"]:
    for key, val in report.get(section, {}).items():
        if val is not False:
            raise SystemExit(f"hash dry-run {section} overclaims: {key}")
for rel in report.get("related_surfaces", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"hash dry-run related surface missing: {rel}")

fixture = load_json(FIXTURE_REL)
if "external-contact-hash-recompute-dry-run" not in fixture.get("target_filings", []):
    raise SystemExit("hash dry-run fixture does not target report")
if fixture.get("severity") != "critical":
    raise SystemExit("hash dry-run fixture must be critical")

if Draft202012Validator is not None:
    validator = Draft202012Validator(schema)
    mut = copy.deepcopy(report)
    mut["send_time_policy"]["dry_run_may_satisfy_send_time_recompute"] = True
    if not list(validator.iter_errors(mut)):
        raise SystemExit("schema failed to reject dry-run as send-time recompute")
    mut2 = copy.deepcopy(report)
    mut2["downstream_locks"]["may_treat_hashes_as_transport_proof"] = True
    if not list(validator.iter_errors(mut2)):
        raise SystemExit("schema failed to reject hash-as-proof")

print("audit_external_contact_hash_recompute_dry_run: OK")
