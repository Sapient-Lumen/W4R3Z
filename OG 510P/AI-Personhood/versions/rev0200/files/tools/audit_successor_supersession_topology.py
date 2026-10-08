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
    "schemas/successor-supersession-topology-record.schema.json",
    "examples/successor-supersession-topology-record-compromise-recovery.json",
    "fixtures/negative-tests/successor-promotion-no-stay-or-witness-diversity.json",
    "examples/drill-after-action-successor-reactivation-compromise.json",
    "examples/fixture-suite-profile-red-team-v1.json",
    "examples/fixture-run-report-negative-suite.json",
    f"examples/research-tail-compaction-map-{rev}.json",
    "docs/20-world-design/continuity-topology-and-identity-claims.md",
    "docs/00-meta/research-tail-compaction-and-refactor-map.md",
    "FOLLOWTHROUGH-QUEUE.json",
]
for rel in inputs:
    if not (ROOT / rel).exists():
        raise SystemExit(f"missing successor topology audit input: {rel}")

schema = load(ROOT / "schemas/successor-supersession-topology-record.schema.json")
example = load(ROOT / "examples/successor-supersession-topology-record-compromise-recovery.json")
fixture = load(ROOT / "fixtures/negative-tests/successor-promotion-no-stay-or-witness-diversity.json")
drill = load(ROOT / "examples/drill-after-action-successor-reactivation-compromise.json")
suite = load(ROOT / "examples/fixture-suite-profile-red-team-v1.json")
report = load(ROOT / "examples/fixture-run-report-negative-suite.json")
mp = load(ROOT / "examples" / f"research-tail-compaction-map-{rev}.json")

if Draft202012Validator is not None:
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(example), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"successor topology example fails schema: {errors[0].message}")
    fixture_schema = load(ROOT / "schemas/negative-test-fixture.schema.json")
    errors = sorted(Draft202012Validator(fixture_schema).iter_errors(fixture), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"successor topology negative fixture fails schema: {errors[0].message}")
    drill_schema = load(ROOT / "schemas/drill-after-action-report.schema.json")
    errors = sorted(Draft202012Validator(drill_schema).iter_errors(drill), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"successor topology drill fails drill schema: {errors[0].message}")

if fixture.get("fixture_id") != "NF-CONTINUITY-2026-0004":
    raise SystemExit("successor topology fixture id changed unexpectedly")

suite_ids = {item.get("fixture_id") for item in suite.get("fixtures", [])}
report_items = {item.get("fixture_id"): item for item in report.get("fixtures_run", [])}
if "NF-CONTINUITY-2026-0004" not in suite_ids:
    raise SystemExit("successor topology fixture missing from fixture-suite profile")
if "NF-CONTINUITY-2026-0004" not in report_items:
    raise SystemExit("successor topology fixture missing from fixture-run report")
if report_items["NF-CONTINUITY-2026-0004"].get("result") not in {"passed", "blocking-failure"}:
    raise SystemExit("successor topology fixture must be actively exercised or blocking, not skipped")

if example.get("successor_promotion", {}).get("promotion_state") != "stayed":
    raise SystemExit("successor topology example must stay successor promotion")
if example.get("witness_and_panel", {}).get("witness_diversity_floor", 0) < 3:
    raise SystemExit("successor topology example must require at least three diverse witnesses")
if not example.get("anti_evasion_and_history", {}).get("historical_branch_preserved"):
    raise SystemExit("historical branch preservation must be true")
if not example.get("anti_evasion_and_history", {}).get("no_cleanse_by_rename"):
    raise SystemExit("successor topology must block cleanse-by-rename")
if example.get("reliance_effect") not in {"stayed", "blocked", "conditional", "downgraded"}:
    raise SystemExit("successor topology reliance effect must constrain reliance")

metrics = drill.get("metrics", {})
for key in [
    "successor_promotion_stayed_without_evidence_floor",
    "historical_branch_preserved",
    "witness_diversity_floor_met",
    "serial_filing_throttle_triggered",
    "branch_history_overwrite_blocked",
    "reserve_default_cure_kept_open",
]:
    if metrics.get(key) is not True:
        raise SystemExit(f"successor topology drill missing or false metric: {key}")
if not any(rt.get("fixture") == "NF-CONTINUITY-2026-0004" for rt in drill.get("regression_tests", [])):
    raise SystemExit("successor topology drill does not regression-test the successor fixture")

rtc03 = next((c for c in mp.get("clusters", []) if c.get("cluster_id") == "RTC-03"), None)
if not rtc03 or rtc03.get("action") != "compacted":
    raise SystemExit("RTC-03 must be marked compacted in the active research-tail compaction map")
if not all(s.get("current_state") == "folded" for s in rtc03.get("surfaces", [])):
    raise SystemExit("RTC-03 compacted cluster must mark every source surface folded")

cont = (ROOT / "docs/20-world-design/continuity-topology-and-identity-claims.md").read_text(encoding="utf-8")
for phrase in [
    "Supersession is not erasure",
    "Successor promotion is stayed",
    "reactivation evidence floor",
    "historical branch",
    "witness diversity",
    "schemas/successor-supersession-topology-record.schema.json",
]:
    if phrase not in cont:
        raise SystemExit(f"continuity topology surface missing phrase: {phrase}")

queue = load(ROOT / "FOLLOWTHROUGH-QUEUE.json")
closed = next((e for e in queue.get("entries", []) if e.get("id") == "FT-0185-RTC03-SUCCESSOR-FOLD-COMPLETION"), None)
if not closed or closed.get("state") != "closed":
    raise SystemExit("RTC-03 successor fold queue entry was not closed")
open_entry = next((e for e in queue.get("entries", []) if e.get("id") == "FT-0185-SUCCESSOR-TOPOLOGY-WITNESSED-DRILL"), None)
if not open_entry or open_entry.get("state") not in {"open", "advanced_not_closed"}:
    raise SystemExit("witnessed successor topology drill follow-through entry is missing")

print("audit_successor_supersession_topology: OK")
