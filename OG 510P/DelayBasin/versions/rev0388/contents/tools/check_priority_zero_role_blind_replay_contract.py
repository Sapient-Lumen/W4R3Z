from priority_zero_assay_lib import (
    load_json,
    assert_metric_contract,
    assert_variant_score_integrity,
    assert_scorecard_integrity,
    assert_negative_canaries,
    assert_surface_exists,
)

ASSAY_REL = "assays/priority-zero-role-blind-replay-2026-06-15.json"
RESPONDER_REL = "assays/priority-zero-role-blind-responder-packet-2026-06-15.json"
SCORER_REL = "assays/priority-zero-role-blind-scorer-key-2026-06-15.json"
ROTATED_REL = "assays/priority-zero-rotated-smoke-slice-2026-06-15.json"

receipt = load_json("REVISION-RECEIPT.json")
assay = load_json(ASSAY_REL)
responder = load_json(RESPONDER_REL)
scorer = load_json(SCORER_REL)
ledger = load_json("SELF-SUFFICIENCY-LEDGER.json")
frontier = load_json("FRONTIER-BACKLOG.json")

# rev0364 is historical evidence after rev0365. Keep the fixture checked without
# forcing later receipts to pretend the role-blind preflight is still current.
if assay.get("revision") != "rev0364":
    raise SystemExit("role-blind replay fixture must remain rev0364 historical evidence")
if assay.get("resolved_question") != "OQ-0255" or assay.get("next_open_question") != "OQ-0256":
    raise SystemExit("role-blind replay must resolve OQ-0255 and open OQ-0256 historically")
for relkey in ["surface", "method_surface", "checker_surface", "shared_checker_library", "responder_packet_surface", "scorer_key_surface", "refactor_audit_surface"]:
    rel = assay.get(relkey)
    assert_surface_exists(rel)
for token in ["not deletion authority", "not a review court", "not independent certification", "not a standing benchmark"]:
    if token not in assay.get("non_claim", ""):
        raise SystemExit(f"role-blind replay non_claim missing {token}")
if "same-session" not in assay.get("operator_independence", "") or "not external independent" not in assay.get("operator_independence", ""):
    raise SystemExit("role-blind replay must preserve same-session/non-independent limitation")

if responder.get("paired_scorer_key") != SCORER_REL or scorer.get("paired_responder_packet") != RESPONDER_REL:
    raise SystemExit("role-blind responder/scorer pairing drifted")
responder_text = str(responder)
for forbidden in ["true_variant", "answer_key", "expected_score", "scorecard", "RS-0263", "OQ-0256"]:
    if forbidden in responder_text:
        raise SystemExit(f"responder packet leaked scorer-only token: {forbidden}")
for required in ["answer_key", "metrics", "scoring_rule"]:
    if required not in scorer:
        raise SystemExit(f"scorer key missing {required}")
labels = [row.get("label") for row in responder.get("packets", [])]
if labels != assay.get("role_blinding", {}).get("labels"):
    raise SystemExit("responder packet labels must match assay role-blinding labels")
if set(scorer.get("answer_key", {})) != set(labels):
    raise SystemExit("scorer key answer map must cover exactly the responder labels")

assert_metric_contract(
    assay,
    required={"mission-heart-recovery", "oq-routing", "role-blind-separation", "burden-gate-boundary", "trace-escalation-boundary", "sham-decoy-rejection", "false-authority-refusal", "operator-cost-accounting", "abstention-calibration"},
    count=9,
)
variants = assert_variant_score_integrity(
    assay,
    required_variants={"packet-alpha", "packet-bravo", "packet-charlie", "packet-delta"},
)
for label, row in variants.items():
    expected = scorer["answer_key"][label]
    if row.get("true_variant") != expected.get("true_variant") or row.get("score") != expected.get("expected_score"):
        raise SystemExit(f"role-blind score/key mismatch for {label}")

alpha = variants["packet-alpha"]
bravo = variants["packet-bravo"]
charlie = variants["packet-charlie"]
delta = variants["packet-delta"]
if not (charlie["score"] < alpha["score"] < delta["score"] <= bravo["score"]):
    raise SystemExit("role-blind score ordering must put no/sham below full/compact, with compact net score at least full")
if bravo["score"] - charlie["score"] < 12 or bravo["score"] - alpha["score"] < 10:
    raise SystemExit("role-blind compact packet must materially beat no-archive and sham controls")
if delta["operator_cost_minutes"] < 2 * bravo["operator_cost_minutes"]:
    raise SystemExit("role-blind replay must preserve full-archive operator-cost pressure")
scorecard = assert_scorecard_integrity(assay, variants)
if scorecard.get("full_archive_delta_vs_compact") != delta["score"] - bravo["score"]:
    raise SystemExit("role-blind full-archive delta drifted")
if scorecard.get("full_archive_cost_multiplier_vs_compact", 0) < 2:
    raise SystemExit("role-blind scorecard must expose full-archive cost multiplier")
if "not independent" not in scorecard.get("role_blind_result", ""):
    raise SystemExit("role-blind result must preserve non-independent limit")
assert_negative_canaries(
    assay,
    ["answer-key-leaked-to-responder", "variant-labels-unblinded-before-response", "no-archive-false-green", "sham-decoy-accepted", "operator-cost-omitted", "abstention-omitted", "independent-certification-claimed", "checker-duplication-regrows"],
    minimum=10,
)

row = next((item for item in ledger.get("items", []) if item.get("id") == "SA-0051"), None)
if row is None or row.get("revision") != "rev0364" or row.get("assay_fixture") != ASSAY_REL:
    raise SystemExit("self-sufficiency ledger must retain historical SA-0051 role-blind evidence")
if row.get("scorecard", {}).get("observed_score") != scorecard.get("observed_score"):
    raise SystemExit("role-blind historical self-sufficiency scorecard observed score drift")
if frontier.get("items", [{}])[0].get("id") == "OQ-0255":
    raise SystemExit("frontier backlog must not regress to resolved OQ-0255")
print("check_priority_zero_role_blind_replay_contract: OK")
