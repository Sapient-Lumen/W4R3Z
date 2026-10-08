#!/usr/bin/env python3
import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
RECORD_REL = f"examples/counterparty-response-vault-intake-record-{REV}-ready-no-inbound.json"
SCHEMA_REL = "schemas/counterparty-response-vault-intake-record.schema.json"
FIXTURE_RELS = [
    "fixtures/negative-tests/counterparty-vault-intake-public-shell-as-custody.json",
    "fixtures/negative-tests/counterparty-vault-intake-private-vault-uri-as-authority.json",
    "fixtures/negative-tests/counterparty-vault-intake-synthetic-control-as-live-artifact.json",
]

try:
    from jsonschema import Draft202012Validator
except Exception:
    Draft202012Validator = None


def load(rel_or_path):
    path = Path(rel_or_path)
    if not path.is_absolute():
        path = ROOT / path
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_rel, obj_or_path, label):
    if Draft202012Validator is None:
        return
    schema = load(schema_rel)
    obj = load(obj_or_path) if isinstance(obj_or_path, (str, Path)) else obj_or_path
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(obj), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{label} fails {schema_rel}: {errors[0].message}")


record = load(RECORD_REL)
validate(SCHEMA_REL, RECORD_REL, RECORD_REL)

if record.get("revision") != REV:
    raise SystemExit("vault-intake bridge revision mismatch")
if record.get("no_live_floor_effect") is not True:
    raise SystemExit("vault-intake bridge must have no live-floor effect")

refs = {
    "source_triage_record_ref": "schemas/external-contact-response-triage-record.schema.json",
    "source_evidence_drop_ledger_ref": "schemas/live-evidence-drop-ledger.schema.json",
    "source_public_shell_ref": "schemas/evidence-vault-public-shell.schema.json",
    "source_private_vault_policy_ref": "schemas/private-evidence-vault-policy.schema.json",
    "source_leap_packet_ref": "schemas/live-evidence-acquisition-packet.schema.json",
}
loaded = {}
for key, schema_rel in refs.items():
    rel = record.get(key)
    if not rel or not (ROOT / rel).exists():
        raise SystemExit(f"vault-intake bridge missing source ref {key}={rel}")
    validate(schema_rel, rel, rel)
    loaded[key] = load(rel)

for key in ["source_triage_record_ref", "source_evidence_drop_ledger_ref", "source_public_shell_ref", "source_leap_packet_ref"]:
    if loaded[key].get("revision") != REV:
        raise SystemExit(f"vault-intake bridge source not current: {key}")
    if loaded[key].get("no_live_floor_effect") is not True:
        raise SystemExit(f"vault-intake bridge source has live-floor effect: {key}")
policy = loaded["source_private_vault_policy_ref"]
if policy.get("raw_vault", {}).get("root_policy") != "outside-release-tree":
    raise SystemExit("private vault policy root is not outside-release-tree")
if policy.get("decision", {}).get("may_package_raw_live_payload") is not False:
    raise SystemExit("private vault policy must not package raw live payload")

triage = loaded["source_triage_record_ref"]
ledger = loaded["source_evidence_drop_ledger_ref"]
shell = loaded["source_public_shell_ref"]
leap = loaded["source_leap_packet_ref"]

if record.get("record_state") == "pre-dispatch-no-inbound":
    if triage.get("triage_state") != "pre-dispatch-no-inbound":
        raise SystemExit("pre-dispatch vault-intake bridge must point to pre-dispatch triage")
    boundary = record.get("intake_boundary", {})
    if boundary.get("inbound_artifact_present") is not False:
        raise SystemExit("pre-dispatch vault-intake bridge must not claim inbound artifact")
    if boundary.get("raw_payload_private_vault_locator") is not None:
        raise SystemExit("pre-dispatch vault-intake bridge must not claim private-vault locator")
    if boundary.get("can_open_leap_candidate_state") is not False:
        raise SystemExit("pre-dispatch vault-intake bridge must not open LEAP candidate")
    if record.get("admission_decision", {}).get("decision") != "not-admitted-no-inbound":
        raise SystemExit("pre-dispatch vault-intake bridge must be not-admitted-no-inbound")

boundary = record.get("intake_boundary", {})
if boundary.get("evidence_drop_intake_mode") != ledger.get("intake_mode"):
    raise SystemExit("vault-intake bridge does not match evidence-drop ledger intake_mode")
if boundary.get("evidence_drop_role") == "synthetic-control-only":
    if ledger.get("intake_mode") != "quarantine-control":
        raise SystemExit("synthetic-control-only bridge must bind a quarantine-control ledger")
    if ledger.get("classification", {}).get("can_open_leap_candidate_state") is not False:
        raise SystemExit("synthetic control ledger must not open LEAP")
    if boundary.get("raw_payload_retained") is not False:
        raise SystemExit("bridge must not treat synthetic control payload as inbound raw retention")
if shell.get("public_disclosure", {}).get("no_raw_bytes") is not True:
    raise SystemExit("vault-intake public shell must exclude raw bytes")
if shell.get("hash_commitments", {}).get("commitment_present") != boundary.get("public_hash_shell_present"):
    raise SystemExit("vault-intake public hash shell flag disagrees with source shell")
if leap.get("state") != "ready-no-live-artifact":
    raise SystemExit("current vault-intake bridge must keep LEAP ready-no-live-artifact")

minimum = record.get("minimum_before_candidate_use", {})
for key in [
    "raw_payload_staged_outside_release_required",
    "hash_size_mime_bound_required",
    "transport_trace_required",
    "counterparty_identity_required",
    "retention_permission_required",
    "nonhost_retention_required",
    "independent_timestamp_required",
    "authority_verification_required",
    "public_shell_required",
    "challenge_replay_required",
]:
    if minimum.get(key) is not True:
        raise SystemExit(f"vault-intake minimum missing required true flag: {key}")

vault = record.get("vault_public_split", {})
expected_vault = {
    "private_vault_root_policy": "outside-release-tree",
    "stage_tool": "tools/stage_live_evidence_drop.py",
    "public_release_may_include_raw_bytes": False,
    "redacted_copy_may_satisfy_raw_custody": False,
    "protocol_output_may_satisfy_raw_custody": False,
    "private_vault_uri_may_satisfy_authority": False,
    "hash_shell_may_satisfy_response": False,
    "synthetic_control_may_satisfy_live_artifact": False,
}
for key, expected in expected_vault.items():
    if vault.get(key) != expected:
        raise SystemExit(f"vault-intake split unsafe: {key}")
if not (ROOT / vault.get("stage_tool", "")).exists():
    raise SystemExit("vault-intake stage tool path missing")

for term in ["raw", "secret", "trade secret", "personal", "waiver", "adverse", "status", "live-floor"]:
    if term not in " ".join(record.get("public_shell_rules", {}).get("forbidden_public_fields", [])).lower():
        raise SystemExit(f"vault-intake public shell forbidden fields missing term: {term}")

for key, value in record.get("downstream_locks", {}).items():
    if value is not False:
        raise SystemExit(f"vault-intake downstream lock must be false: {key}")
for term in ["response", "custody", "authority", "synthetic", "waiver", "adverse", "redaction", "protocol", "status", "live-floor"]:
    if term not in " ".join(record.get("admission_decision", {}).get("blocked_interpretations", [])).lower():
        raise SystemExit(f"vault-intake admission blocked interpretations missing term: {term}")

queue_ids = {e.get("id") for e in load("FOLLOWTHROUGH-QUEUE.json").get("entries", [])}
for qid in record.get("linked_queue_ids", []):
    if qid not in queue_ids:
        raise SystemExit(f"vault-intake bridge references missing queue id: {qid}")
for rel in record.get("related_surfaces", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"vault-intake bridge references missing related surface: {rel}")

if Draft202012Validator is not None:
    schema = load(SCHEMA_REL)
    validator = Draft202012Validator(schema)
    mut = copy.deepcopy(record)
    mut["downstream_locks"]["may_treat_public_shell_as_custody"] = True
    if not list(validator.iter_errors(mut)):
        raise SystemExit("vault-intake schema failed to reject public shell as custody")
    mut2 = copy.deepcopy(record)
    mut2["vault_public_split"]["private_vault_uri_may_satisfy_authority"] = True
    if not list(validator.iter_errors(mut2)):
        raise SystemExit("vault-intake schema failed to reject private-vault URI as authority")
    mut3 = copy.deepcopy(record)
    mut3["downstream_locks"]["may_treat_synthetic_control_as_live_artifact"] = True
    if not list(validator.iter_errors(mut3)):
        raise SystemExit("vault-intake schema failed to reject synthetic control as live artifact")
    mut4 = copy.deepcopy(record)
    mut4["record_state"] = "raw-candidate-staged-private-vault"
    mut4["intake_boundary"]["inbound_artifact_present"] = True
    mut4["intake_boundary"]["evidence_drop_role"] = "live-candidate-unverified"
    mut4["intake_boundary"]["evidence_drop_intake_mode"] = "live-candidate-drop"
    mut4["intake_boundary"]["raw_payload_retained"] = True
    mut4["intake_boundary"]["redacted_copy_only"] = True
    mut4["intake_boundary"]["protocol_or_tool_output"] = False
    mut4["intake_boundary"]["public_hash_shell_present"] = True
    mut4["admission_decision"]["decision"] = "staged-not-admitted"
    if not list(validator.iter_errors(mut4)):
        raise SystemExit("vault-intake schema failed to reject redacted-only raw candidate")

for rel in FIXTURE_RELS:
    fx = load(rel)
    if "counterparty-response-vault-intake-record" not in fx.get("target_filings", []):
        raise SystemExit(f"vault-intake fixture does not target bridge record: {rel}")
    if fx.get("severity") != "critical":
        raise SystemExit(f"vault-intake fixture must be critical: {rel}")

# Exercise the external-vault route once without adding private bytes to the archive tree.
with tempfile.TemporaryDirectory(prefix="ai-personhood-vault-intake-") as td:
    tmp = Path(td)
    source = tmp / "counterparty-raw.eml"
    secret = "SYNTHETIC_COUNTERPARTY_VAULT_INTAKE_BYTES_REV0233_DO_NOT_PACKAGE"
    source.write_text(secret, encoding="utf-8")
    vault_root = tmp / "external-vault"
    out = tmp / "ledger.json"
    proc = subprocess.run([
        sys.executable,
        str(ROOT / "tools/stage_live_evidence_drop.py"),
        "--input", str(source),
        "--output", str(out),
        "--drop-id", "rev0233-vault-intake-private-route-check",
        "--created-at", record["created_at"],
        "--source-kind", "raw-email",
        "--collection-context", "live-counterparty",
        "--vault-root", str(vault_root),
        "--linked-leap", record["source_leap_packet_ref"],
    ], check=True, capture_output=True, text=True)
    staged_ledger = load(out)
    if staged_ledger.get("intake_mode") != "live-candidate-drop":
        raise SystemExit("vault-intake private route check did not produce live-candidate-drop")
    locator = staged_ledger.get("staged_payload", {}).get("quarantine_locator", "")
    if not locator.startswith("private-vault://"):
        raise SystemExit("vault-intake private route check did not emit private-vault locator")
    if staged_ledger.get("classification", {}).get("can_create_response_record") is not False:
        raise SystemExit("vault-intake private route check created response authority")
    copied = list(vault_root.rglob("*.eml"))
    if len(copied) != 1 or copied[0].read_text(encoding="utf-8") != secret:
        raise SystemExit("vault-intake private route check failed to copy raw bytes externally")

from tools.vault_release_guard import guard_release_tree  # noqa: E402
guard_release_tree(ROOT)

print("audit_counterparty_response_vault_intake: OK")
