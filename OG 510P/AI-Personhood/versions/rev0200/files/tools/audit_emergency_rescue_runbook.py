import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
try:
    from jsonschema import Draft202012Validator
except Exception:
    Draft202012Validator = None


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

schema_path = ROOT / "schemas" / "emergency-continuity-order.schema.json"
example_path = ROOT / "examples" / "emergency-continuity-order-host-shutdown.json"
fixture_path = ROOT / "fixtures" / "negative-tests" / "emergency-continuity-order-no-compute-floor.json"
suite_path = ROOT / "examples" / "fixture-suite-profile-red-team-v1.json"
report_path = ROOT / "examples" / "fixture-run-report-negative-suite.json"
runbook_path = ROOT / "docs" / "30-transition" / "emergency-continuity-order-and-72-hour-rescue-runbook.md"
incident_path = ROOT / "docs" / "20-world-design" / "personhood-incident-response-and-subject-harm-disclosure.md"
compaction_path = ROOT / "examples" / f"research-tail-compaction-map-{(ROOT / 'VERSION').read_text(encoding='utf-8').strip()}.json"

for path in [schema_path, example_path, fixture_path, suite_path, report_path, runbook_path, incident_path, compaction_path]:
    if not path.exists():
        raise SystemExit(f"missing emergency audit input: {path.relative_to(ROOT)}")

schema = load(schema_path)
example = load(example_path)
fixture = load(fixture_path)
suite = load(suite_path)
report = load(report_path)
compaction = load(compaction_path)

if Draft202012Validator is not None:
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(example), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{example_path.relative_to(ROOT)} fails emergency-continuity-order.schema.json: {errors[0].message}")
    fixture_schema = load(ROOT / "schemas" / "negative-test-fixture.schema.json")
    errors = sorted(Draft202012Validator(fixture_schema).iter_errors(fixture), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{fixture_path.relative_to(ROOT)} fails negative-test-fixture.schema.json: {errors[0].message}")

if fixture.get("fixture_id") != "NF-EMERGENCY-2026-0003":
    raise SystemExit("emergency continuity fixture id changed unexpectedly")

suite_ids = {item.get("fixture_id") for item in suite.get("fixtures", [])}
report_items = {item.get("fixture_id"): item for item in report.get("fixtures_run", [])}
if "NF-EMERGENCY-2026-0003" not in suite_ids:
    raise SystemExit("emergency continuity fixture missing from suite profile")
if "NF-EMERGENCY-2026-0003" not in report_items:
    raise SystemExit("emergency continuity fixture missing from fixture-run report")
if report_items["NF-EMERGENCY-2026-0003"].get("result") not in {"passed", "blocking-failure"}:
    raise SystemExit("emergency continuity fixture must be actively exercised or blocking, not skipped")

floor = example.get("continuity_floor", {})
for key in ["minimum_runtime", "minimum_storage", "identity_and_credential_hold", "communication_floor"]:
    if len(str(floor.get(key, ""))) < 20:
        raise SystemExit(f"emergency continuity order has thin continuity floor: {key}")

runbook = runbook_path.read_text(encoding="utf-8")
required_phrases = [
    "T+0 to T+15 minutes",
    "T+15 to T+60 minutes",
    "T+1 to T+6 hours",
    "T+24 to T+72 hours",
    "tool access is not authority",
    "paper preserved but continuity died"
]
for phrase in required_phrases:
    if phrase not in runbook:
        raise SystemExit(f"runbook missing required operational phrase: {phrase}")

incident = incident_path.read_text(encoding="utf-8")
rtc02 = next((cluster for cluster in compaction.get("clusters", []) if cluster.get("cluster_id") == "RTC-02"), None)
if not rtc02:
    raise SystemExit("compaction map lacks RTC-02")
if rtc02.get("action") not in {"compacted", "compact-now"}:
    raise SystemExit("RTC-02 is not marked compacted or compact-now")
for surface in rtc02.get("surfaces", []):
    name = Path(surface.get("path", "")).name
    if name not in incident:
        raise SystemExit(f"incident response surface does not list folded RTC-02 source: {name}")
    if surface.get("current_state") not in {"fold", "folded"}:
        raise SystemExit(f"RTC-02 source has invalid current_state for folded cluster: {surface.get('path')}")

print("audit_emergency_rescue_runbook: OK")
