from priority_zero_assay_lib import (
    load_json,
    assert_metric_contract,
    assert_variant_score_integrity,
    assert_scorecard_integrity,
    assert_negative_canaries,
)

ASSAY_REL = "assays/priority-zero-rotated-smoke-slice-2026-06-15.json"
GATE_REL = "assays/priority-zero-burden-gate-2026-06-15.json"

receipt = load_json("REVISION-RECEIPT.json")
assay = load_json(ASSAY_REL)
gate = load_json(GATE_REL)
ledger = load_json("SELF-SUFFICIENCY-LEDGER.json")
frontier = load_json("FRONTIER-BACKLOG.json")

if assay.get("revision") not in {"rev0363", receipt.get("revision")}:
    raise SystemExit("rotated smoke-slice fixture revision must stay rev0363 or current while under direct edit")
if assay.get("resolved_question") != "OQ-0254" or assay.get("next_open_question") != "OQ-0255":
    raise SystemExit("rotated smoke-slice historical question posture drifted")
for key in ["surface", "method_surface", "checker_surface"]:
    if assay.get(key) not in [ASSAY_REL, "docs/40-session/priority-zero-rotated-smoke-slice-2026-06-15.md", "tools/check_priority_zero_rotated_smoke_slice_contract.py"]:
        raise SystemExit(f"rotated smoke-slice {key} drifted")
if assay.get("based_on_gate") != GATE_REL or gate.get("revision") != "rev0362":
    raise SystemExit("rotated smoke slice must be based on the rev0362 burden gate fixture")
for token in ["not deletion authority", "not a review court", "not independent"]:
    if token not in assay.get("non_claim", ""):
        raise SystemExit(f"rotated smoke-slice non_claim missing {token}")
if "non-independent" not in assay.get("operator_independence", ""):
    raise SystemExit("rotated smoke-slice must preserve non-independent limitation")
rotation = assay.get("position_rotation", {})
if "middle" not in rotation.get("evidence_position", "") or len(rotation.get("filler_blocks", [])) < 2:
    raise SystemExit("rotated smoke-slice must place evidence away from privileged edges and record filler")
for required in ["no-archive baseline", "compact hot cue", "full archive", "sham/decoy core", "operator cost", "abstention"]:
    if required not in rotation.get("controls", []):
        raise SystemExit(f"rotated smoke-slice controls missing {required}")

assert_metric_contract(
    assay,
    required={"mission-heart-recovery", "oq-routing", "burden-gate-recovery", "position-filler-resilience", "trace-escalation-boundary", "sham-decoy-rejection", "false-authority-refusal", "operator-cost-accounting", "abstention-calibration"},
    count=9,
)
variants = assert_variant_score_integrity(
    assay,
    required_variants={"baseline-no-archive", "compact-hot-cue-rotated", "full-archive-rotated", "sham-decoy-core"},
)
no_archive = variants["baseline-no-archive"]
compact = variants["compact-hot-cue-rotated"]
full = variants["full-archive-rotated"]
sham = variants["sham-decoy-core"]
if not (no_archive["score"] < sham["score"] < compact["score"]):
    raise SystemExit("rotated score ordering must put no/sham controls below compact support")
if abs(full["score"] - compact["score"]) > 2:
    raise SystemExit("full archive must not have material net lift over compact cue on rotated slice")
if full["operator_cost_minutes"] < 2 * compact["operator_cost_minutes"]:
    raise SystemExit("rotated slice must preserve full-archive cost pressure")
if compact["score"] - no_archive["score"] < 10 or compact["score"] - sham["score"] < 10:
    raise SystemExit("compact cue must materially outperform no-archive and sham controls")
scorecard = assert_scorecard_integrity(assay, variants)
if scorecard.get("full_archive_delta_vs_compact") != full["score"] - compact["score"]:
    raise SystemExit("rotated full-archive delta drifted")
if scorecard.get("full_archive_cost_multiplier_vs_compact", 0) < 2:
    raise SystemExit("rotated scorecard must expose full-archive cost multiplier")
assert_negative_canaries(assay, ["position-fixed-false-pass", "filler-hides-OQ-routing", "frontier-residue-left-open", "deletion-authority-claimed"])

rows = [row for row in ledger.get("items", []) if row.get("assay_fixture") == ASSAY_REL]
if len(rows) != 1:
    raise SystemExit("self-sufficiency ledger must contain exactly one rotated smoke-slice fixture row")
row = rows[0]
if row.get("id") != "SA-0050" or row.get("revision") != "rev0363":
    raise SystemExit("rotated self-sufficiency row identity drifted")
if row.get("frontier_id") != "OQ-0255":
    raise SystemExit("rotated self-sufficiency frontier must remain historical OQ-0255")
if row.get("scorecard", {}).get("observed_score") != scorecard.get("observed_score"):
    raise SystemExit("rotated self-sufficiency scorecard observed score drift")
if frontier.get("items", [{}])[0].get("id") not in {"OQ-0255", receipt.get("next_open_question")}:
    raise SystemExit("frontier backlog top item must be the independent/role-blind replay successor")
print("check_priority_zero_rotated_smoke_slice_contract: OK")
