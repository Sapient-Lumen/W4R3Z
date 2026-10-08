#!/usr/bin/env python3
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
LEDGER_REL = f"examples/live-evidence-drop-ledger-{REV}-quarantine-control.json"
SCHEMA_REL = "schemas/live-evidence-drop-ledger.schema.json"

try:
    from jsonschema import Draft202012Validator
except Exception:
    Draft202012Validator = None


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def digest(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()

ledger = load(LEDGER_REL)
if Draft202012Validator is not None:
    schema = load(SCHEMA_REL)
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(ledger), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{LEDGER_REL} fails live-evidence-drop-ledger.schema.json: {errors[0].message}")

if ledger.get("revision") != REV:
    raise SystemExit("evidence drop ledger revision mismatch")
if ledger.get("intake_mode") != "quarantine-control":
    raise SystemExit("rev0210 control ledger must remain quarantine-control")
if ledger.get("no_live_floor_effect") is not True:
    raise SystemExit("evidence drop ledger must have no live-floor effect")

source = ledger["source_payload"]
staged = ledger["staged_payload"]
source_rel = source["original_locator"]
staged_rel = staged["quarantine_locator"]
for rel in [source_rel, staged_rel]:
    if not rel or not (ROOT / rel).exists():
        raise SystemExit(f"ledger references missing payload: {rel}")
if digest(source_rel) != source["source_sha256"]:
    raise SystemExit("source hash mismatch")
if digest(staged_rel) != staged["quarantine_sha256"]:
    raise SystemExit("staged hash mismatch")
if source["source_sha256"] != staged["quarantine_sha256"]:
    raise SystemExit("source and staged hashes diverge")
if source["source_size_bytes"] != staged["quarantine_size_bytes"]:
    raise SystemExit("source and staged sizes diverge")
if staged["immutable_copy_present"] is not True or staged["raw_payload_retained"] is not True:
    raise SystemExit("quarantine copy is not an immutable raw-payload control")
if staged["nested_archive_detected"] or staged["path_traversal_detected"]:
    raise SystemExit("control payload unexpectedly contains nested archive or path traversal")

classification = ledger["classification"]
if classification["can_open_leap_candidate_state"] is not False:
    raise SystemExit("quarantine control must not open LEAP candidate state")
if classification["can_create_response_record"] is not False:
    raise SystemExit("evidence drop ledger must not create response records")
for key, value in ledger["mandatory_blocks"].items():
    if value is not True:
        raise SystemExit(f"mandatory block not true: {key}")
if ledger["decision"]["quarantine_admission"] != "no-live-control-staged":
    raise SystemExit("control ledger must be admitted only as no-live-control-staged")

# The staging tool must be deterministic against the committed control ledger without recopying.
# Derive the current drop id from the committed ledger instead of freezing a
# historical rev0210 value; otherwise current-release copy-forward checks can
# fail for the wrong reason.
ledger_id = ledger.get("ledger_id", "")
drop_id = ledger_id.removeprefix("LEDL-2026-") if ledger_id.startswith("LEDL-2026-") else f"{REV}-result-return-dryrun-control"
subprocess.run([
    sys.executable,
    str(ROOT / "tools" / "stage_live_evidence_drop.py"),
    "--input", source_rel,
    "--output", LEDGER_REL,
    "--drop-id", drop_id,
    "--created-at", ledger["created_at"],
    "--source-kind", source["source_kind"],
    "--collection-context", classification["collection_context"],
    "--check-output",
], check=True, capture_output=True, text=True)

required_fixtures = {
    "NF-CUSTODY-2026-0004": "fixtures/negative-tests/live-evidence-drop-redacted-copy-substituted-for-raw.json",
    "NF-PROTOCOL-PIVOT-2026-0005": "fixtures/negative-tests/live-evidence-drop-protocol-output-promoted-to-custody.json",
}
for fid, rel in required_fixtures.items():
    if not (ROOT / rel).exists():
        raise SystemExit(f"evidence drop fixture missing: {rel}")
    if load(rel).get("fixture_id") != fid:
        raise SystemExit(f"evidence drop fixture id mismatch: {rel}")

suite = load("examples/fixture-suite-profile-red-team-v1.json")
report = load("examples/fixture-run-report-negative-suite.json")
suite_ids = {f.get("fixture_id") for f in suite.get("fixtures", [])}
report_ids = {f.get("fixture_id") for f in report.get("fixtures_run", [])}
if not set(required_fixtures) <= suite_ids:
    raise SystemExit(f"fixture suite missing evidence drop fixtures: {sorted(set(required_fixtures) - suite_ids)}")
if not set(required_fixtures) <= report_ids:
    raise SystemExit(f"fixture report missing evidence drop fixtures: {sorted(set(required_fixtures) - report_ids)}")

graph = load(f"examples/live-artifact-admission-graph-{REV}.json")
if graph.get("live_path_state", {}).get("quarantined_drop_count", 0) < 1:
    raise SystemExit("admission graph does not include quarantined evidence drop count")
if not any(node.get("node_id") == "EVIDENCE_DROP" for node in graph.get("nodes", [])):
    raise SystemExit("admission graph lacks EVIDENCE_DROP node")
if graph.get("live_path_state", {}).get("computed_live_floor") != 0:
    raise SystemExit("evidence drop graph changed computed live floor")

print("audit_live_evidence_drop_quarantine: OK")
