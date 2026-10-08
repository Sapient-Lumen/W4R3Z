import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
CONTROL_REL = "examples/live-receipt-floor-control-case-positive-controls.json"
SNAP_REL = f"examples/live-receipt-floor-computed-snapshot-{REV}.json"
DOC_REL = "docs/30-transition/computed-floor-positive-control-and-import-smoke-tests.md"

try:
    from jsonschema import Draft202012Validator
except Exception:
    Draft202012Validator = None


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

# Schema validation.
if Draft202012Validator is not None:
    control_schema = load("schemas/live-receipt-floor-control-case.schema.json")
    control = load(CONTROL_REL)
    Draft202012Validator.check_schema(control_schema)
    errors = sorted(Draft202012Validator(control_schema).iter_errors(control), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{CONTROL_REL} fails live-receipt-floor-control-case.schema.json: {errors[0].message}")
    gate_schema = load("schemas/actual-receipt-import-gate.schema.json")
    Draft202012Validator.check_schema(gate_schema)
    gate_validator = Draft202012Validator(gate_schema)
    for case in control.get("cases", []):
        for gate in case.get("import_gate_records", []):
            errors = sorted(gate_validator.iter_errors(gate), key=lambda e: list(e.path))
            if errors:
                raise SystemExit(f"embedded control gate in {case.get('case_id')} fails actual-receipt-import-gate.schema.json: {errors[0].message}")

# The archive snapshot itself must match the generated result and remain zero.
subprocess.run([sys.executable, str(ROOT / "tools/compute_live_receipt_floor.py"), "--check"], check=True)
snap = load(SNAP_REL)
cf = snap.get("computed_floor", {})
if cf.get("independent_receipts_present") != 0 or cf.get("eligible_live_imports"):
    raise SystemExit("archive computed-floor snapshot gained live imports from control or stale data")
if any("control" in x for x in cf.get("eligible_live_imports", [])):
    raise SystemExit("control gate leaked into archive eligible_live_imports")

# Control harness must prove both positive and rollback behavior.
proc = subprocess.run(
    [sys.executable, str(ROOT / "tools/compute_live_receipt_floor.py"), "--control-case", str(ROOT / CONTROL_REL)],
    check=True,
    capture_output=True,
    text=True,
)
results = {row["case_id"]: row for row in json.loads(proc.stdout).get("results", [])}
expected_cases = {
    "class-local-positive-one-result-return",
    "full-vector-positive-all-required-classes",
    "challenged-positive-rollback-exclusion",
    "correlated-positive-duplicate-dependency-discount",
}
missing = expected_cases - set(results)
if missing:
    raise SystemExit(f"control harness missing cases: {sorted(missing)}")
class_local = results["class-local-positive-one-result-return"]["observed"]
if class_local.get("independent_receipts_present") != 1 or class_local.get("cross_critical_quorum_satisfied") is not False:
    raise SystemExit("class-local positive control did not produce exactly one class-local non-quorum import")
full = results["full-vector-positive-all-required-classes"]["observed"]
if full.get("independent_receipts_present") < 10 or full.get("cross_critical_quorum_satisfied") is not True:
    raise SystemExit("full-vector positive control did not prove quorum-capable computation")
challenged = results["challenged-positive-rollback-exclusion"]["observed"]
if challenged.get("independent_receipts_present") != 0 or challenged.get("live_classes_satisfied"):
    raise SystemExit("challenged positive control was not excluded")

correlated = results["correlated-positive-duplicate-dependency-discount"]["observed"]
if correlated.get("independent_receipts_present") != 1 or not any(row.get("status") == "discounted" for row in correlated.get("independence_discount_register", [])):
    raise SystemExit("correlated positive control did not discount duplicate dependency/counterparty candidate")

# Documentation and public failed-gate posture.
doc = (ROOT / DOC_REL).read_text(encoding="utf-8")
for phrase in [
    "Positive control is not archive receipt",
    "archive_effect=none-control-only",
    "not hardcoded to reject every import",
    "challenged control import",
]:
    if phrase not in doc:
        raise SystemExit(f"{DOC_REL} missing required phrase: {phrase}")

# Required fixtures should be present in suite/report.
suite = load("examples/fixture-suite-profile-red-team-v1.json")
report = load("examples/fixture-run-report-negative-suite.json")
suite_ids = {item.get("fixture_id") for item in suite.get("fixtures", [])}
report_ids = {item.get("fixture_id") for item in report.get("fixtures_run", [])}
required_fixtures = {
    "NF-PLAYBOOK-2026-0035",
    "NF-PLAYBOOK-2026-0036",
    "NF-PLAYBOOK-2026-0037",
}
if not required_fixtures <= suite_ids:
    raise SystemExit(f"suite missing positive-control fixtures: {sorted(required_fixtures - suite_ids)}")
if not required_fixtures <= report_ids:
    raise SystemExit(f"report missing positive-control fixtures: {sorted(required_fixtures - report_ids)}")

# Queue should close the control harness task and keep actual import open.
queue = load("FOLLOWTHROUGH-QUEUE.json")
entries = {e.get("id"): e for e in queue.get("entries", [])}
if entries.get("FT-0204-COMPUTED-FLOOR-POSITIVE-CONTROLS", {}).get("state") != "closed":
    raise SystemExit("positive control followthrough entry is not closed")
actual_replay = entries.get("FT-0204-ACTUAL-LIVE-ARTIFACT-POSITIVE-REPLAY", {})
first_live = entries.get("FT-0207-FIRST-LIVE-EVIDENCE-ACQUISITION", {})
if actual_replay.get("state") != "open" and first_live.get("state") not in {"open", "queued", "advanced_not_closed"}:
    raise SystemExit("actual live artifact followthrough lane is not open after positive-control closure")

print("audit_computed_floor_positive_controls: OK")
