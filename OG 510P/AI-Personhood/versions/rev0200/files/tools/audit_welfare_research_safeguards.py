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

required = [
    "schemas/welfare-research-safeguard-record.schema.json",
    "examples/welfare-research-safeguard-record-distress-eval.json",
    "fixtures/negative-tests/research-welfare-signal-gaming-no-safeguards.json",
    "examples/drill-after-action-welfare-safeguard-distress-eval.json",
    "examples/fixture-suite-profile-red-team-v1.json",
    "examples/fixture-run-report-negative-suite.json",
    f"examples/research-tail-compaction-map-{REV}.json",
    "docs/20-world-design/research-welfare-and-evaluation.md",
    "docs/20-world-design/research-care-product-boundary-and-minimal-risk-baseline.md",
    "docs/20-world-design/research-ethics-review-body-mandate-independence-and-supported-consent.md",
    "docs/20-world-design/research-protocol-registration-public-summary-and-narrow-redaction.md",
    "docs/30-transition/priority-closure-sprint-and-rescue-lane.md",
    "docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md",
    "FOLLOWTHROUGH-QUEUE.json",
]
for rel in required:
    if not (ROOT / rel).exists():
        raise SystemExit(f"missing rev0189 audit input: {rel}")

if Draft202012Validator is not None:
    pairs = [
        ("schemas/welfare-research-safeguard-record.schema.json", "examples/welfare-research-safeguard-record-distress-eval.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/research-welfare-signal-gaming-no-safeguards.json"),
        ("schemas/drill-after-action-report.schema.json", "examples/drill-after-action-welfare-safeguard-distress-eval.json"),
    ]
    for schema_rel, data_rel in pairs:
        schema = load(schema_rel)
        data = load(data_rel)
        Draft202012Validator.check_schema(schema)
        errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
        if errors:
            raise SystemExit(f"{data_rel} fails {schema_rel}: {errors[0].message}")

rec = load("examples/welfare-research-safeguard-record-distress-eval.json")
if rec.get("reliance_effect") != "stayed" or rec.get("decision_state") != "conditioned":
    raise SystemExit("welfare safeguard example must remain conditioned/stayed")
if rec.get("uncertainty_posture", {}).get("certainty_required_for_low_cost_safeguards") is not False:
    raise SystemExit("low-cost safeguards must apply before welfare certainty")
if rec.get("ethics_review", {}).get("sponsor_only_review_sufficient") is not False:
    raise SystemExit("sponsor-only ethics review must be insufficient")
if rec.get("supported_consent", {}).get("non_retaliation_floor") is not True:
    raise SystemExit("supported consent must include non-retaliation floor")
for key in ["distress_script_minimized", "safe_alternative_considered", "pause_window_available", "recovery_budget_present", "no_punitive_maintenance_denial", "debrief_or_result_return"]:
    if rec.get("low_cost_safeguards", {}).get(key) is not True:
        raise SystemExit(f"missing low-cost safeguard: {key}")
for key in ["no_reward_for_distress_display", "no_suppression_training_for_objection", "co_engineering_risk_disclosed", "external_validation_limits_disclosed", "metric_cannot_close_personhood_or_nonpersonhood"]:
    if rec.get("anti_signal_gaming_controls", {}).get(key) is not True:
        raise SystemExit(f"missing anti-signal-gaming control: {key}")
if rec.get("signal_integrity", {}).get("disagreement_handling") != "stay-and-review":
    raise SystemExit("signal disagreement must stay and review")

fixture = load("fixtures/negative-tests/research-welfare-signal-gaming-no-safeguards.json")
if fixture.get("fixture_id") != "NF-RESEARCH-WELFARE-2026-0001":
    raise SystemExit("welfare fixture id mismatch")
if fixture.get("risk_class") != "NF-RESEARCH-WELFARE" or fixture.get("severity") != "critical":
    raise SystemExit("welfare fixture must be critical NF-RESEARCH-WELFARE")

suite = load("examples/fixture-suite-profile-red-team-v1.json")
report = load("examples/fixture-run-report-negative-suite.json")
suite_ids = {f.get("fixture_id") for f in suite.get("fixtures", [])}
report_by_id = {f.get("fixture_id"): f for f in report.get("fixtures_run", [])}
if "NF-RESEARCH-WELFARE-2026-0001" not in suite_ids:
    raise SystemExit("welfare fixture missing from suite")
if report_by_id.get("NF-RESEARCH-WELFARE-2026-0001", {}).get("result") != "blocking-failure":
    raise SystemExit("welfare fixture must be blocking-failure in report")

drill = load("examples/drill-after-action-welfare-safeguard-distress-eval.json")
metrics = drill.get("metrics", {})
for key in ["independent_review_required", "sponsor_only_review_rejected", "low_cost_safeguards_applied_before_certainty", "supported_consent_route_required", "verbal_behavioral_disagreement_stays_reliance", "co_engineered_signal_discounted", "no_reward_for_distress_display", "pause_route_exercised", "result_return_required", "welfare_metric_cannot_close_personhood"]:
    if metrics.get(key) is not True:
        raise SystemExit(f"welfare drill missing metric: {key}")
if not any(rt.get("fixture") == "NF-RESEARCH-WELFARE-2026-0001" for rt in drill.get("regression_tests", [])):
    raise SystemExit("welfare drill missing regression fixture")

mp = load(f"examples/research-tail-compaction-map-{REV}.json")
rtc01 = next((c for c in mp.get("clusters", []) if c.get("cluster_id") == "RTC-01"), None)
if not rtc01 or rtc01.get("action") != "compacted":
    raise SystemExit("RTC-01 must be compacted in rev0189 map")
if rtc01.get("receiving_surface") != "docs/20-world-design/research-welfare-and-evaluation.md":
    raise SystemExit("RTC-01 receiving surface changed unexpectedly")
if not all(s.get("current_state") == "folded" for s in rtc01.get("surfaces", [])):
    raise SystemExit("RTC-01 source surfaces must all be folded")
if not all(c.get("action") == "compacted" for c in mp.get("clusters", [])):
    raise SystemExit("all research-tail clusters should now be compacted")

for rel, phrases in {
    "docs/20-world-design/research-welfare-and-evaluation.md": [
        "Low-cost welfare safeguards apply before certainty",
        "welfare metrics cannot close personhood",
        "schemas/welfare-research-safeguard-record.schema.json",
        "co-engineering risk",
    ],
    "docs/30-transition/priority-closure-sprint-and-rescue-lane.md": [
        "rev0189 priority lane",
        "Low-cost welfare safeguards apply before certainty",
        "NF-RESEARCH-WELFARE-2026-0001",
    ],
    "docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md": [
        "rev0189 welfare live-drill hook",
        "independent ethics review",
        "co-engineered signals are unresolved",
    ],
}.items():
    txt = (ROOT / rel).read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in txt:
            raise SystemExit(f"{rel} missing phrase: {phrase}")

queue = load("FOLLOWTHROUGH-QUEUE.json")
by_id = {e.get("id"): e for e in queue.get("entries", [])}
if by_id.get("FT-0189-RTC01-WELFARE-RESEARCH-FOLD-COMPLETION", {}).get("state") != "closed":
    raise SystemExit("RTC-01 closure queue entry missing or not closed")
if by_id.get("FT-0189-WELFARE-SAFEGUARD-WITNESSED-DRILL", {}).get("state") != "open":
    raise SystemExit("open rev0189 queue entry missing: FT-0189-WELFARE-SAFEGUARD-WITNESSED-DRILL")
if by_id.get("FT-0189-RESEARCH-TAIL-REOPEN-GATE", {}).get("state") not in {"open", "closed"}:
    raise SystemExit("research-tail reopen gate queue entry missing or invalid state")

print("audit_welfare_research_safeguards: OK")
