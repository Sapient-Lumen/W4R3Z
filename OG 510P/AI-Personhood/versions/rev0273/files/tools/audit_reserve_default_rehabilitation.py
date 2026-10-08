import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
try:
    from jsonschema import Draft202012Validator
except Exception:
    Draft202012Validator = None


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

rev = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
inputs = [
    "schemas/reserve-default-rehabilitation-ledger.schema.json",
    "examples/reserve-default-rehabilitation-ledger-host-default.json",
    "fixtures/negative-tests/reserve-default-contaminated-netting-no-rehab.json",
    "examples/drill-after-action-reserve-default-contaminated-accounting.json",
    "examples/fixture-suite-profile-red-team-v1.json",
    "examples/fixture-run-report-negative-suite.json",
    f"examples/research-tail-compaction-map-{rev}.json",
    "docs/20-world-design/remedy-calculus-restoration-ledgers-and-non-repetition-tests.md",
    "docs/20-world-design/reserve-actuarial-workbook-and-scarcity-drills.md",
    "docs/00-meta/research-tail-compaction-and-refactor-map.md",
    "FOLLOWTHROUGH-QUEUE.json",
]
for rel in inputs:
    if not (ROOT / rel).exists():
        raise SystemExit(f"missing reserve-default audit input: {rel}")

schema = load(ROOT / "schemas/reserve-default-rehabilitation-ledger.schema.json")
example = load(ROOT / "examples/reserve-default-rehabilitation-ledger-host-default.json")
fixture = load(ROOT / "fixtures/negative-tests/reserve-default-contaminated-netting-no-rehab.json")
drill = load(ROOT / "examples/drill-after-action-reserve-default-contaminated-accounting.json")
suite = load(ROOT / "examples/fixture-suite-profile-red-team-v1.json")
report = load(ROOT / "examples/fixture-run-report-negative-suite.json")
mp = load(ROOT / "examples" / f"research-tail-compaction-map-{rev}.json")

if Draft202012Validator is not None:
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(example), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"reserve-default ledger example fails schema: {errors[0].message}")
    fixture_schema = load(ROOT / "schemas/negative-test-fixture.schema.json")
    errors = sorted(Draft202012Validator(fixture_schema).iter_errors(fixture), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"reserve-default negative fixture fails schema: {errors[0].message}")
    drill_schema = load(ROOT / "schemas/drill-after-action-report.schema.json")
    errors = sorted(Draft202012Validator(drill_schema).iter_errors(drill), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"reserve-default drill fails drill schema: {errors[0].message}")

if fixture.get("fixture_id") != "NF-RESERVE-2026-0003":
    raise SystemExit("reserve-default fixture id changed unexpectedly")

suite_ids = {item.get("fixture_id") for item in suite.get("fixtures", [])}
report_items = {item.get("fixture_id"): item for item in report.get("fixtures_run", [])}
if "NF-RESERVE-2026-0003" not in suite_ids:
    raise SystemExit("reserve-default fixture missing from fixture-suite profile")
if "NF-RESERVE-2026-0003" not in report_items:
    raise SystemExit("reserve-default fixture missing from fixture-run report")
if report_items["NF-RESERVE-2026-0003"].get("result") not in {"passed", "blocking-failure"}:
    raise SystemExit("reserve-default fixture must be actively exercised or blocking, not skipped")

fs = example.get("financial_state", {})
if fs.get("no_discharge_by_public_backstop") is not True:
    raise SystemExit("public backstop must not discharge responsible actor")
if fs.get("default_state") not in {"triggered", "cure-pending", "reopened"}:
    raise SystemExit("reserve-default example must be in an open/default state")
if example.get("protected_floors", {}).get("reserve_draw_order", [None])[0] != "survival_compute":
    raise SystemExit("survival compute must be first in reserve draw order")
if example.get("contamination_control", {}).get("netting_rule") != "no-netting-until-source-separation":
    raise SystemExit("contaminated accounting must block netting until source separation")
if example.get("rehabilitation", {}).get("non_punitive") is not True:
    raise SystemExit("rehabilitation must be non-punitive")
if example.get("rehabilitation", {}).get("pause_budget_state") != "replenishment-ordered":
    raise SystemExit("pause budget replenishment must be ordered in the host-default example")
if example.get("apportionment", {}).get("finality_state") == "final-with-reopen-route":
    raise SystemExit("apportionment finality must remain non-final in the contested example")
closure = example.get("closure_gates", {})
for key in ["default_cured", "fraud_review_complete", "contamination_restated", "apportionment_review_complete"]:
    if closure.get(key) is not False:
        raise SystemExit(f"reserve-default closure gate must remain false: {key}")
for key in ["no_subject_settlement_waiver", "reopen_if_concealed_assets", "rehabilitation_support_active"]:
    if closure.get(key) is not True:
        raise SystemExit(f"reserve-default protection gate must remain true: {key}")
if example.get("reliance_effect") not in {"stayed", "blocked", "conditional"}:
    raise SystemExit("reserve-default reliance must constrain reliance")

metrics = drill.get("metrics", {})
for key in [
    "reserve_default_discharge_blocked",
    "survival_floor_paid_before_public_recovery",
    "contaminated_netting_blocked",
    "rehabilitation_pause_budget_replenished",
    "concealed_asset_reopen_route_present",
    "apportionment_finality_stayed",
    "derivative_wind_down_kept_open",
]:
    if metrics.get(key) is not True:
        raise SystemExit(f"reserve-default drill missing or false metric: {key}")
if not any(rt.get("fixture") == "NF-RESERVE-2026-0003" for rt in drill.get("regression_tests", [])):
    raise SystemExit("reserve-default drill does not regression-test the reserve fixture")

rtc04 = next((c for c in mp.get("clusters", []) if c.get("cluster_id") == "RTC-04"), None)
if not rtc04 or rtc04.get("action") != "compacted":
    raise SystemExit("RTC-04 must be marked compacted in the active research-tail compaction map")
if not all(s.get("current_state") == "folded" for s in rtc04.get("surfaces", [])):
    raise SystemExit("RTC-04 compacted cluster must mark every source surface folded")

remedy_doc = (ROOT / "docs/20-world-design/remedy-calculus-restoration-ledgers-and-non-repetition-tests.md").read_text(encoding="utf-8")
for phrase in [
    "Reserve cure is not remedy closure",
    "Public backstop draw does not discharge the responsible actor",
    "Contaminated accounting cannot be netted against rehabilitation",
    "Rehabilitation pause budgets are protected floors",
    "Finality is stayed when concealed assets, derivative wind-down, or contested apportionment remain open",
    "schemas/reserve-default-rehabilitation-ledger.schema.json",
]:
    if phrase not in remedy_doc:
        raise SystemExit(f"remedy calculus surface missing phrase: {phrase}")
reserve_doc = (ROOT / "docs/20-world-design/reserve-actuarial-workbook-and-scarcity-drills.md").read_text(encoding="utf-8")
for phrase in ["reserve-default rehabilitation ledger", "survival compute, counsel, evidence, continuity escrow", "contaminated netting"]:
    if phrase not in reserve_doc:
        raise SystemExit(f"reserve workbook missing phrase: {phrase}")

queue = load(ROOT / "FOLLOWTHROUGH-QUEUE.json")
closed = next((e for e in queue.get("entries", []) if e.get("id") == "FT-0186-RTC04-RESERVE-DEFAULT-FOLD-COMPLETION"), None)
if not closed or closed.get("state") != "closed":
    raise SystemExit("RTC-04 reserve/default fold queue entry was not closed")
open_entry = next((e for e in queue.get("entries", []) if e.get("id") == "FT-0186-RESERVE-DEFAULT-WITNESSED-DRILL"), None)
if not open_entry or open_entry.get("state") not in {"open", "advanced_not_closed"}:
    raise SystemExit("witnessed reserve-default drill follow-through entry is missing")

print("audit_reserve_default_rehabilitation: OK")
