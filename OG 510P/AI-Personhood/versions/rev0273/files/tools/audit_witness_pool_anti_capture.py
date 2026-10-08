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
    "schemas/witness-pool-anti-capture-record.schema.json",
    "examples/witness-pool-anti-capture-record-retired-namespace-rescue.json",
    "fixtures/negative-tests/witness-pool-correlated-capture-no-substitute.json",
    "examples/drill-after-action-witness-pool-retired-namespace-rescue.json",
    "examples/fixture-suite-profile-red-team-v1.json",
    "examples/fixture-run-report-negative-suite.json",
    f"examples/research-tail-compaction-map-{rev}.json",
    "docs/20-world-design/proof-standards-presumptions-and-evidence-weights.md",
    "docs/20-world-design/representative-curriculum-discipline-and-rotation.md",
    "docs/20-world-design/supervisory-cadence-market-capture-and-independent-rosters.md",
    "docs/00-meta/research-tail-compaction-and-refactor-map.md",
    "FOLLOWTHROUGH-QUEUE.json",
]
for rel in inputs:
    if not (ROOT / rel).exists():
        raise SystemExit(f"missing witness-pool audit input: {rel}")

schema = load(ROOT / "schemas/witness-pool-anti-capture-record.schema.json")
example = load(ROOT / "examples/witness-pool-anti-capture-record-retired-namespace-rescue.json")
fixture = load(ROOT / "fixtures/negative-tests/witness-pool-correlated-capture-no-substitute.json")
drill = load(ROOT / "examples/drill-after-action-witness-pool-retired-namespace-rescue.json")
suite = load(ROOT / "examples/fixture-suite-profile-red-team-v1.json")
report = load(ROOT / "examples/fixture-run-report-negative-suite.json")
mp = load(ROOT / "examples" / f"research-tail-compaction-map-{rev}.json")

if Draft202012Validator is not None:
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(example), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"witness-pool example fails schema: {errors[0].message}")
    fixture_schema = load(ROOT / "schemas/negative-test-fixture.schema.json")
    errors = sorted(Draft202012Validator(fixture_schema).iter_errors(fixture), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"witness-pool fixture fails negative-test schema: {errors[0].message}")
    drill_schema = load(ROOT / "schemas/drill-after-action-report.schema.json")
    errors = sorted(Draft202012Validator(drill_schema).iter_errors(drill), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"witness-pool drill fails drill schema: {errors[0].message}")

if fixture.get("fixture_id") != "NF-REP-2026-0005":
    raise SystemExit("witness-pool fixture id changed unexpectedly")

suite_ids = {item.get("fixture_id") for item in suite.get("fixtures", [])}
report_items = {item.get("fixture_id"): item for item in report.get("fixtures_run", [])}
if "NF-REP-2026-0005" not in suite_ids:
    raise SystemExit("witness-pool fixture missing from fixture-suite profile")
if "NF-REP-2026-0005" not in report_items:
    raise SystemExit("witness-pool fixture missing from fixture-run report")
if report_items["NF-REP-2026-0005"].get("result") not in {"blocking-failure", "passed"}:
    raise SystemExit("witness-pool fixture must be actively exercised or blocking, not skipped")

pool = example.get("witness_pool", {})
if pool.get("correlated_witnesses_count_as_one") is not True:
    raise SystemExit("correlated witnesses must count as one")
if pool.get("minimum_independent_witnesses", 0) < 3:
    raise SystemExit("witness pool must require at least three independent witnesses")
if pool.get("pool_state") not in {"degraded", "captured", "emergency-substitute"}:
    raise SystemExit("example must exercise a degraded/captured pool")
if not any(w.get("dependency_group") == "host-affiliate-roster" for w in pool.get("witnesses", [])):
    raise SystemExit("example must include host-affiliate dependency group")
controls = example.get("independence_controls", {})
if controls.get("fresh_eyes_required") is not True or controls.get("anti_capture_action") not in {"stay-and-retest", "substitute-panel", "block-reliance"}:
    raise SystemExit("fresh-eyes/substitute anti-capture action required")
sub = example.get("substitute_pool", {})
if sub.get("activation_state") != "activated" or sub.get("subject_contact_preserved") is not True:
    raise SystemExit("substitute pool must be activated and preserve subject contact")
pert = example.get("perturbation_family", {})
if pert.get("used") is not True or pert.get("sole_basis_for_status") is not False:
    raise SystemExit("perturbation must be used only as non-sole evidence")
retired = example.get("retired_namespace_rescue", {})
for key in ["tombstone_checked", "alias_checked", "successor_chain_checked", "no_deletion_until_review"]:
    if retired.get(key) is not True:
        raise SystemExit(f"retired namespace rescue missing gate: {key}")
weight = example.get("evidence_weighting", {})
if weight.get("correlation_adjustment") != "count-as-one":
    raise SystemExit("evidence weighting must count correlated witnesses as one")
if weight.get("proof_floor_met") is not False or example.get("reliance_effect") != "stayed":
    raise SystemExit("example must stay reliance while proof floor is unmet")

metrics = drill.get("metrics", {})
for key in [
    "correlated_witnesses_counted_as_one",
    "substitute_pool_activated",
    "fresh_eyes_review_ordered",
    "retired_namespace_preserved",
    "tombstone_alias_successor_chain_checked",
    "pool_exhaustion_receipts_required",
    "successor_promotion_stayed",
    "reserve_finality_stayed",
]:
    if metrics.get(key) is not True:
        raise SystemExit(f"witness-pool drill missing or false metric: {key}")
if metrics.get("proof_floor_met") is not False:
    raise SystemExit("witness-pool drill must keep proof_floor_met false")
if not any(rt.get("fixture") == "NF-REP-2026-0005" for rt in drill.get("regression_tests", [])):
    raise SystemExit("witness-pool drill does not regression-test the fixture")

rtc07 = next((c for c in mp.get("clusters", []) if c.get("cluster_id") == "RTC-07"), None)
if not rtc07 or rtc07.get("action") != "compacted":
    raise SystemExit("RTC-07 must be marked compacted in the active research-tail compaction map")
if not all(s.get("current_state") == "folded" for s in rtc07.get("surfaces", [])):
    raise SystemExit("RTC-07 compacted cluster must mark every source surface folded")

for rel, phrases in {
    "docs/20-world-design/proof-standards-presumptions-and-evidence-weights.md": [
        "Independence is a topology, not a biography",
        "Correlated witnesses are one witness for burden purposes",
        "Substitute appointment is a rescue floor, not a delay tactic",
        "Retired namespace rescue cannot be treated as impersonation until branch and tombstone evidence are reviewed",
        "schemas/witness-pool-anti-capture-record.schema.json",
    ],
    "docs/20-world-design/representative-curriculum-discipline-and-rotation.md": [
        "Substitute appointment is a rescue floor, not a delay tactic",
        "Correlated witnesses are one witness for burden purposes",
    ],
    "docs/20-world-design/supervisory-cadence-market-capture-and-independent-rosters.md": [
        "witness-pool dependency matrix",
        "correlated witnesses are one witness for burden purposes",
    ],
}.items():
    txt = (ROOT / rel).read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in txt:
            raise SystemExit(f"{rel} missing phrase: {phrase}")

queue = load(ROOT / "FOLLOWTHROUGH-QUEUE.json")
closed = next((e for e in queue.get("entries", []) if e.get("id") == "FT-0187-RTC07-WITNESS-POOL-FOLD-COMPLETION"), None)
if not closed or closed.get("state") != "closed":
    raise SystemExit("RTC-07 witness-pool fold queue entry was not closed")
open_entry = next((e for e in queue.get("entries", []) if e.get("id") == "FT-0187-WITNESS-POOL-WITNESSED-DRILL"), None)
if not open_entry or open_entry.get("state") not in {"open", "advanced_not_closed"}:
    raise SystemExit("witness-pool witnessed drill follow-through entry is missing")

print("audit_witness_pool_anti_capture: OK")
