import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()

try:
    from jsonschema import Draft202012Validator
except Exception:
    Draft202012Validator = None


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

schema_rel = "schemas/counterparty-artifact-custody-record.schema.json"
example_rel = "examples/counterparty-artifact-custody-record-result-return-dryrun.json"
schema = load(schema_rel)
record = load(example_rel)
if Draft202012Validator is not None:
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(record), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{example_rel} fails counterparty-artifact-custody-record.schema.json: {errors[0].message}")

artifact = record["raw_artifacts"][0]
artifact_path = ROOT / artifact["path_or_locator"]
if not artifact_path.exists():
    raise SystemExit("custody raw artifact path missing")
actual_hash = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
if artifact["sha256"] != actual_hash:
    raise SystemExit("custody raw artifact sha256 mismatch")
if artifact["size_bytes"] != artifact_path.stat().st_size:
    raise SystemExit("custody raw artifact size mismatch")

if record["artifact_state"] != "institutional-dry-run-artifact":
    raise SystemExit("rev0201 custody example must remain dry-run")
if record["import_readiness"]["live_import_floor_delta"] != 0:
    raise SystemExit("dry-run custody record changed live floor")
if artifact["may_be_used_for_live_import"]:
    raise SystemExit("dry-run artifact marked usable for live import")
if record["decision"]["live_reliance_effect"] != "stayed":
    raise SystemExit("dry-run custody did not keep reliance stayed")
for phrase in ["institutional-dry-run", "no live dispatch/response event", "no non-host live storage confirmation"]:
    if phrase not in " ".join(record["import_readiness"].get("disqualification_reasons", [])):
        raise SystemExit(f"custody disqualification missing phrase: {phrase}")

nh_schema = load("schemas/nonhost-response-artifact-envelope.schema.json")
if "linked_custody_record" not in nh_schema.get("properties", {}):
    raise SystemExit("NHRAE schema lacks linked_custody_record")
nh = load("examples/nonhost-response-artifact-envelope-result-return-institutional-dryrun.json")
if nh.get("linked_custody_record") != record["custody_record_id"]:
    raise SystemExit("NHRAE example does not link the custody record")
if nh.get("verification_floor", {}).get("possible_live_receipt") is not False:
    raise SystemExit("NHRAE dry-run possible_live_receipt drifted")

arig_schema = load("schemas/actual-receipt-import-gate.schema.json")
if "custody_record_ref" not in arig_schema["properties"]["source_provenance"].get("properties", {}):
    raise SystemExit("ARIG schema lacks custody_record_ref")
arig = load("examples/actual-receipt-import-gate-result-return-institutional-dryrun-no-live-delta.json")
if arig["source_provenance"].get("custody_record_ref") != record["custody_record_id"]:
    raise SystemExit("ARIG example lacks custody_record_ref")
if arig["import_decision"].get("live_floor_delta") != 0:
    raise SystemExit("ARIG dry-run changed live floor")

ld_schema = load("schemas/live-drill-execution-packet.schema.json")
if "counterparty_artifact_custody_record_refs" not in ld_schema.get("properties", {}):
    raise SystemExit("live drill schema lacks custody refs")
packet = load("examples/live-drill-execution-packet-cross-critical-witnessed-pack.json")
if record["custody_record_id"] not in packet.get("counterparty_artifact_custody_record_refs", []):
    raise SystemExit("live drill packet does not reference custody record")
if packet.get("receipt_floor", {}).get("independent_receipts_present") != 0:
    raise SystemExit("live drill independent receipts drifted above zero")

for rel in [
    "examples/quorum-recomputation-report-nonhost-artifact-replay-rev0199.json",
    "examples/quorum-recomputation-report-class-local-projection-rev0200.json",
]:
    q = load(rel)
    exclusions = q.get("recomputed_receipt_floor", {}).get("dry_run_or_fixture_exclusions", [])
    if record["custody_record_id"] not in exclusions:
        raise SystemExit(f"{rel} does not exclude custody record from live floor")
    if q.get("decision", {}).get("live_floor_delta") != 0:
        raise SystemExit(f"{rel} changed live floor")

suite = load("examples/fixture-suite-profile-red-team-v1.json")
report = load("examples/fixture-run-report-negative-suite.json")
required = {
    "NF-PLAYBOOK-2026-0026",
    "NF-PLAYBOOK-2026-0027",
    "NF-PLAYBOOK-2026-0028",
}
suite_ids = {f["fixture_id"] for f in suite.get("fixtures", [])}
report_ids = {f["fixture_id"] for f in report.get("fixtures_run", [])}
missing = required - suite_ids
if missing:
    raise SystemExit(f"custody fixtures missing from suite: {sorted(missing)}")
missing = required - report_ids
if missing:
    raise SystemExit(f"custody fixtures missing from report: {sorted(missing)}")

status = load("SURFACE-STATUS.json")
if status.get("revision") != REV:
    raise SystemExit("SURFACE-STATUS revision mismatch")
# rev0201 introduced the custody surface. Later revisions must keep it indexed,
# but should not have to mislabel it as a current-release new surface.
index_text = (ROOT / "ARCHIVE_INDEX.md").read_text(encoding="utf-8")
if "docs/30-transition/counterparty-artifact-custody-and-authority-handoff.md" not in index_text:
    raise SystemExit("custody operational surface missing from archive index")

text = (ROOT / "docs/30-transition/counterparty-artifact-custody-and-authority-handoff.md").read_text(encoding="utf-8")
for phrase in [
    "Artifact received is not artifact admitted",
    "Hash match is necessary but not sufficient",
    "Authority proof is class-specific",
    "Redacted copies are not raw custody",
    "No live counterparty artifact exists",
]:
    if phrase not in text:
        raise SystemExit(f"custody doctrine phrase missing: {phrase}")

print("audit_counterparty_artifact_custody: OK")
