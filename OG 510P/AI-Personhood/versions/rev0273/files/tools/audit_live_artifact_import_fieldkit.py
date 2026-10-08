import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
FIELDKIT_REL = "examples/live-artifact-import-fieldkit-first-live-response.json"
REPORT_REL = f"examples/artifact-import-invariant-report-{REV}.json"
SNAP_REL = f"examples/live-receipt-floor-computed-snapshot-{REV}.json"
DOC_REL = "docs/30-transition/live-artifact-import-fieldkit-and-invariant-replay.md"

try:
    from jsonschema import Draft202012Validator
except Exception:
    Draft202012Validator = None


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

# Schema validation.
if Draft202012Validator is not None:
    for schema_rel, example_rel in [
        ("schemas/live-artifact-import-fieldkit.schema.json", FIELDKIT_REL),
        ("schemas/artifact-import-invariant-report.schema.json", REPORT_REL),
        ("schemas/live-receipt-floor-computed-snapshot.schema.json", SNAP_REL),
    ]:
        schema = load(schema_rel)
        data = load(example_rel)
        Draft202012Validator.check_schema(schema)
        errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
        if errors:
            raise SystemExit(f"{example_rel} fails {Path(schema_rel).name}: {errors[0].message}")

# Generated artifacts must be exact.
subprocess.run([sys.executable, str(ROOT / "tools/compute_live_receipt_floor.py"), "--check"], check=True)
subprocess.run([sys.executable, str(ROOT / "tools/build_artifact_import_invariant_report.py"), "--check"], check=True)

fieldkit = load(FIELDKIT_REL)
if fieldkit.get("fieldkit_state") != "ready-no-live-artifact":
    raise SystemExit("fieldkit must remain ready-no-live-artifact until raw evidence exists")
limits = fieldkit.get("reliance_limits", {})
if any(limits.get(key) is not False for key in ["fieldkit_is_receipt", "may_start_no_response_clock", "may_create_response_record", "may_increase_live_floor", "may_satisfy_cross_critical_quorum"]):
    raise SystemExit("fieldkit reliance limits must all be false")
slots = {slot.get("slot_id"): slot for slot in fieldkit.get("raw_artifact_slots", [])}
required_slots = {"raw-payload", "payload-hash", "independent-timestamp", "counterparty-identity", "class-specific-authority", "request-trace", "nonhost-retention", "sealed-public-parity", "dependency-group-map", "failed-gate-route"}
missing = required_slots - set(slots)
if missing:
    raise SystemExit(f"fieldkit missing raw artifact slots: {sorted(missing)}")
for sid in required_slots:
    slot = slots[sid]
    if slot.get("blocks_if_missing") is not True or slot.get("blocks_if_failed") is not True:
        raise SystemExit(f"fieldkit slot does not block on missing/failed: {sid}")

snap = load(SNAP_REL)
floor = snap.get("computed_floor", {})
if floor.get("independent_receipts_present") != 0 or floor.get("eligible_live_imports"):
    raise SystemExit("computed snapshot unexpectedly has live imports")
report = load(REPORT_REL)
if report.get("archive_floor", {}).get("independent_receipts_present") != 0:
    raise SystemExit("invariant report archive floor must remain zero")
if report.get("decision", {}).get("may_import_now") is not False or report.get("decision", {}).get("may_upgrade_reliance") is not False:
    raise SystemExit("invariant report cannot authorize import or reliance upgrade")
for check in report.get("invariant_checks", []):
    if check.get("passed") is not True:
        raise SystemExit(f"invariant check failed: {check.get('check_id')}")
if report.get("source_scans", {}).get("disallowed_positive_archive_paths"):
    raise SystemExit("invariant report found disallowed positive archive gates")

# Archive import gates must not contain live positive gates yet.
for p in sorted((ROOT / "examples").glob("actual-receipt-import-gate*.json")):
    data = json.loads(p.read_text(encoding="utf-8"))
    decision = data.get("import_decision", {})
    if decision.get("import_allowed_to_live_floor") is True:
        raise SystemExit(f"archive import gate grants live floor before actual artifact exists: {p.relative_to(ROOT)}")

# Documentation phrases.
doc = (ROOT / DOC_REL).read_text(encoding="utf-8")
for phrase in [
    "Raw artifact package precedes response creation",
    "Fieldkit readiness is not artifact admission",
    "Invariant replay beats narrative",
    "No response record, receipt-intake record, import gate",
]:
    if phrase not in doc:
        raise SystemExit(f"{DOC_REL} missing required phrase: {phrase}")

# Fixtures should be in suite/report.
suite = load("examples/fixture-suite-profile-red-team-v1.json")
report_run = load("examples/fixture-run-report-negative-suite.json")
suite_ids = {item.get("fixture_id") for item in suite.get("fixtures", [])}
report_ids = {item.get("fixture_id") for item in report_run.get("fixtures_run", [])}
required = {"NF-PLAYBOOK-2026-0038", "NF-PLAYBOOK-2026-0039", "NF-PLAYBOOK-2026-0040"}
if not required <= suite_ids:
    raise SystemExit(f"suite missing live artifact fieldkit fixtures: {sorted(required - suite_ids)}")
if not required <= report_ids:
    raise SystemExit(f"report missing live artifact fieldkit fixtures: {sorted(required - report_ids)}")

# Maps and queue.
registry = load(f"examples/schema-fixture-domain-registry-{REV}.json")
families = {f.get("family_id") for f in registry.get("families", [])}
for fam in ["LIVE-ARTIFACT-IMPORT-FIELDKIT", "ARTIFACT-IMPORT-INVARIANT-REPORT"]:
    if fam not in families:
        raise SystemExit(f"registry missing {fam}")
rights = load(f"examples/rights-domain-coverage-map-{REV}.json")
if "live-artifact-import-fieldkit" not in {d.get("domain_id") for d in rights.get("domains", [])}:
    raise SystemExit("rights map missing live-artifact-import-fieldkit")
queue = load("FOLLOWTHROUGH-QUEUE.json")
entries = {e.get("id"): e for e in queue.get("entries", [])}
if entries.get("FT-0205-LIVE-ARTIFACT-FIELDKIT-INVARIANTS", {}).get("state") != "closed":
    raise SystemExit("fieldkit invariant queue item must be closed")
first_drop = entries.get("FT-0205-FIRST-REAL-ARTIFACT-DROP", {})
if first_drop.get("state") not in {"open", "advanced_not_closed"}:
    raise SystemExit("first real artifact drop queue item must remain open or advanced_not_closed")
if "stage_live_evidence_drop.py" not in first_drop.get("next_action", ""):
    raise SystemExit("first real artifact drop queue item must route first through evidence-drop quarantine")

print("audit_live_artifact_import_fieldkit: OK")
