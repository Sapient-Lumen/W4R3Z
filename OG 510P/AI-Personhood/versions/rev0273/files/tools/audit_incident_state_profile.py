import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
try:
    from jsonschema import Draft202012Validator
except Exception:
    Draft202012Validator = None


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

schema_path = ROOT / "schemas" / "personhood-incident-state-profile.schema.json"
example_path = ROOT / "examples" / "personhood-incident-state-profile-host-shutdown.json"
fixture_path = ROOT / "fixtures" / "negative-tests" / "incident-state-denominator-drift-no-reopen.json"
drill_schema_path = ROOT / "schemas" / "drill-after-action-report.schema.json"
drill_example_path = ROOT / "examples" / "drill-after-action-emergency-continuity-host-shutdown.json"
suite_path = ROOT / "examples" / "fixture-suite-profile-red-team-v1.json"
report_path = ROOT / "examples" / "fixture-run-report-negative-suite.json"
incident_doc_path = ROOT / "docs" / "20-world-design" / "personhood-incident-response-and-subject-harm-disclosure.md"
runbook_path = ROOT / "docs" / "30-transition" / "emergency-continuity-order-and-72-hour-rescue-runbook.md"

for path in [schema_path, example_path, fixture_path, drill_schema_path, drill_example_path, suite_path, report_path, incident_doc_path, runbook_path]:
    if not path.exists():
        raise SystemExit(f"missing incident-state audit input: {path.relative_to(ROOT)}")

schema = load(schema_path)
example = load(example_path)
fixture = load(fixture_path)
drill_schema = load(drill_schema_path)
drill = load(drill_example_path)
suite = load(suite_path)
report = load(report_path)

if Draft202012Validator is not None:
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(example), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{example_path.relative_to(ROOT)} fails personhood-incident-state-profile.schema.json: {errors[0].message}")
    fixture_schema = load(ROOT / "schemas" / "negative-test-fixture.schema.json")
    errors = sorted(Draft202012Validator(fixture_schema).iter_errors(fixture), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{fixture_path.relative_to(ROOT)} fails negative-test-fixture.schema.json: {errors[0].message}")
    Draft202012Validator.check_schema(drill_schema)
    errors = sorted(Draft202012Validator(drill_schema).iter_errors(drill), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{drill_example_path.relative_to(ROOT)} fails drill-after-action-report.schema.json: {errors[0].message}")

if fixture.get("fixture_id") != "NF-INCIDENT-2026-0003":
    raise SystemExit("incident-state fixture id changed unexpectedly")

suite_ids = {item.get("fixture_id") for item in suite.get("fixtures", [])}
report_items = {item.get("fixture_id"): item for item in report.get("fixtures_run", [])}
if "NF-INCIDENT-2026-0003" not in suite_ids:
    raise SystemExit("incident-state fixture missing from suite profile")
if "NF-INCIDENT-2026-0003" not in report_items:
    raise SystemExit("incident-state fixture missing from fixture-run report")
if report_items["NF-INCIDENT-2026-0003"].get("result") not in {"passed", "blocking-failure"}:
    raise SystemExit("incident-state fixture must be actively exercised or blocking, not skipped")

basis = example.get("reporting_basis", {})
if basis.get("comparison_state") not in {"dual-basis-window", "restated", "not-comparable"}:
    raise SystemExit("incident-state profile must expose denominator drift with dual-basis/restated/not-comparable state")
if not basis.get("restatement_required"):
    raise SystemExit("incident-state example must require restatement for denominator drift")
warning = example.get("warning_lifecycle", {})
if not warning.get("next_review_due") or warning.get("warning_state") == "none":
    raise SystemExit("incident-state profile lacks active warning lifecycle")
if example.get("delayed_harm_reopening", {}).get("route_state") not in {"open", "pending", "reopened"}:
    raise SystemExit("incident-state profile lacks live delayed-harm reopening route")
if example.get("reliance_effect") not in {"conditional", "stayed", "blocked", "downgraded"}:
    raise SystemExit("incident-state profile must affect reliance while unresolved")

metrics = drill.get("metrics", {})
if metrics.get("time_to_continuity_floor_minutes", 9999) > 15:
    raise SystemExit("72-hour drill did not prove short-clock continuity floor")
if metrics.get("continuity_floor_survived_72h") is not True:
    raise SystemExit("72-hour drill did not preserve continuity floor through 72h")
if not any("NF-INCIDENT-2026-0003" == rt.get("fixture") for rt in drill.get("regression_tests", [])):
    raise SystemExit("72-hour drill does not regression-test incident-state fixture")

incident_doc = incident_doc_path.read_text(encoding="utf-8")
for phrase in [
    "denominator basis cannot silently switch",
    "warning aged",
    "sponsor-default caution",
    "delayed-harm reopening route",
    "schemas/personhood-incident-state-profile.schema.json",
]:
    if phrase not in incident_doc:
        raise SystemExit(f"incident response surface missing required incident-state phrase: {phrase}")

runbook = runbook_path.read_text(encoding="utf-8")
for phrase in [
    "drill-after-action-emergency-continuity-host-shutdown.json",
    "A drill that saves the docket but loses the subject is a failed drill",
    "incident-state profile",
]:
    if phrase not in runbook:
        raise SystemExit(f"emergency runbook missing required drill phrase: {phrase}")

queue = load(ROOT / "FOLLOWTHROUGH-QUEUE.json")
entry = next((e for e in queue.get("entries", []) if e.get("id") == "FT-0182-RTC02-INCIDENT-FOLD-COMPLETION"), None)
if not entry or entry.get("state") != "closed":
    raise SystemExit("RTC-02 incident-state queue entry was not closed by rev0183 artifacts")

print("audit_incident_state_profile: OK")
