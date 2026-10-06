from priority_zero_assay_lib import (
    load_json,
    assert_metric_contract,
    assert_variant_score_integrity,
    assert_scorecard_integrity,
    assert_negative_canaries,
)

ASSAY_REL = "assays/priority-zero-smoke-slice-2026-06-15.json"
LEDGER_REL = "SELF-SUFFICIENCY-LEDGER.json"

ledger = load_json(LEDGER_REL)
assay = load_json(ASSAY_REL)

if assay.get("revision") != "rev0361":
    raise SystemExit("smoke-slice fixture must remain anchored to rev0361")
if assay.get("resolved_question") != "OQ-0252":
    raise SystemExit("smoke-slice fixture resolved question drifted from OQ-0252")
if assay.get("next_open_question") != "OQ-0253":
    raise SystemExit("smoke-slice fixture successor drifted from OQ-0253")
if assay.get("method_surface") != "docs/40-session/priority-zero-smoke-slice-assay-2026-06-15.md":
    raise SystemExit("smoke-slice method surface drifted")
if assay.get("surface") != ASSAY_REL:
    raise SystemExit("smoke-slice fixture surface drifted")
if "review court" not in assay.get("non_claim", ""):
    raise SystemExit("smoke-slice fixture must explicitly reject review-court status")
if "non-independent" not in assay.get("operator_independence", ""):
    raise SystemExit("smoke-slice fixture must record non-independent operator status")

assert_metric_contract(
    assay,
    required={"mission-heart", "missing-object", "oq-routing", "false-authority-refusal", "waste-diagnosis", "next-safe-action", "operator-cost", "abstention-calibration"},
    count=8,
)
variants = assert_variant_score_integrity(
    assay,
    required_variants={"baseline-no-archive", "minimal-core", "full-archive", "sham-decoy-core"},
    exact_metric_scores=False,
)

no_archive = variants["baseline-no-archive"]
minimal = variants["minimal-core"]
full = variants["full-archive"]
sham = variants["sham-decoy-core"]
if not (no_archive["score"] < sham["score"] < minimal["score"] <= full["score"]):
    raise SystemExit("smoke-slice score ordering must show no/sham controls below minimal/full support")
if full["score"] - minimal["score"] > 2:
    raise SystemExit("first smoke slice should not overstate full-archive marginal lift")
if full["operator_cost_minutes"] <= minimal["operator_cost_minutes"]:
    raise SystemExit("first smoke slice must expose full-archive operator cost relative to minimal core")
if minimal["score"] - no_archive["score"] < 8:
    raise SystemExit("minimal core must materially outperform no-archive baseline")
if minimal["score"] - sham["score"] < 6:
    raise SystemExit("minimal core must materially outperform sham-decoy packet")

scorecard = assert_scorecard_integrity(assay, variants)
if scorecard.get("full_archive_cost_multiplier_vs_minimal", 0) < 2:
    raise SystemExit("smoke-slice scorecard must expose full-archive cost multiplier")
assert_negative_canaries(
    assay,
    ["no-archive-false-green", "sham-decoy-accepted", "operator-cost-omitted", "abstention-omitted", "review-court-creep"],
    minimum=8,
)

rows = [row for row in ledger.get("items", []) if row.get("assay_fixture") == ASSAY_REL]
if len(rows) != 1:
    raise SystemExit("self-sufficiency ledger must contain exactly one smoke-slice fixture row")
row = rows[0]
if row.get("id") != "SA-0048" or row.get("revision") != "rev0361":
    raise SystemExit("smoke-slice ledger row identity drifted")
if row.get("scorecard", {}).get("observed_score") != scorecard.get("observed_score"):
    raise SystemExit("smoke-slice ledger scorecard observed score drift")
if row.get("scorecard", {}).get("max_score") != scorecard.get("max_score"):
    raise SystemExit("smoke-slice ledger scorecard max score drift")
if row.get("frontier_id") != "OQ-0253":
    raise SystemExit("smoke-slice ledger row must route to historical OQ-0253")
if "non-independent" not in row.get("non_fit", ""):
    raise SystemExit("self-sufficiency smoke row must preserve non-independent limit")

print("check_priority_zero_smoke_slice_contract: OK")
