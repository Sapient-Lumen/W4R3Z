"""Validate the historical rev0370 release-validation truth gate and currentness repair.

This checker preserves the rev0370 validation-truth fixture without forcing the rev0370 scorer or OQ-0262 to remain the current tail and does not force current canon additions.
"""
import pathlib
from priority_zero_assay_lib import load_json, assert_metric_contract, assert_variant_score_integrity, assert_scorecard_integrity, assert_negative_canaries, assert_surface_exists
from score_priority_zero_external_replay_response import resolve_default_scorer_intake
ROOT=pathlib.Path(__file__).resolve().parents[1]
ASSAY_REL="assays/release-validation-truth-gate-2026-06-16.json"; DOC_REL="docs/40-session/release-validation-truth-gate-2026-06-16.md"; CHECKER_REL="tools/check_release_validation_truth_gate_contract.py"; HISTORICAL_ADMISSION_CHECKER_REL="tools/check_priority_zero_clean_response_admission_gate_contract.py"; VALIDATION_LIB_REL="tools/validation_toolchain_lib.py"; SCORE_TOOL_REL="tools/score_priority_zero_external_replay_response.py"; SCORER_REL="assays/priority-zero-custody-hardened-external-replay-scorer-intake-2026-06-16.json"
receipt=load_json("REVISION-RECEIPT.json"); assay=load_json(ASSAY_REL); ledger=load_json("SELF-SUFFICIENCY-LEDGER.json")
if assay.get("revision")!="rev0370" or assay.get("resolved_question")!="OQ-0261" or assay.get("next_open_question")!="OQ-0262" or assay.get("resolution_id")!="RS-0269": raise SystemExit("release-validation truth assay must remain the historical rev0370 fixture")
for rel in [ASSAY_REL,DOC_REL,CHECKER_REL,HISTORICAL_ADMISSION_CHECKER_REL,VALIDATION_LIB_REL,SCORE_TOOL_REL,"PACKAGE-IDENTITY-AUDIT.json"]: assert_surface_exists(rel)
if receipt.get("revision") == "rev0370" and CHECKER_REL not in receipt.get("canon_additions", []): raise SystemExit("rev0370 release checker must be current canon when emitted")
if receipt.get("revision") > "rev0370" and resolve_default_scorer_intake(ROOT) == SCORER_REL: raise SystemExit("historical rev0370 scorer must not remain current-tail default")
for token in ["not clean external replay success","not independent certification","not deletion authority","not compact-cue confirmation","not a review court"]:
    if token not in assay.get("non_claim", ""): raise SystemExit(f"release-validation assay non_claim missing {token}")
if "--summary-out" not in (ROOT/SCORE_TOOL_REL).read_text(encoding="utf-8"): raise SystemExit("score tool must keep --summary-out")
assert_metric_contract(assay,count=8,two_point=True)
variants=assert_variant_score_integrity(assay, required_variants={"released-rev0369-fresh-lint-regression","current-static-currentness-resync","release-claim-truth-gate","clean-response-plus-custody-evidence"})
scorecard=assert_scorecard_integrity(assay,variants)
if scorecard.get("clean_external_response_evidence") is not False: raise SystemExit("rev0370 must preserve absent clean response evidence")
if not any(item.get("assay_fixture")==ASSAY_REL and item.get("frontier_id")=="OQ-0262" for item in ledger.get("items",[])): raise SystemExit("historical rev0370 self-sufficiency row missing")
assert_negative_canaries(assay,["receipt-claims-full-validation-while-fresh-lint-fails","static-root-json-current-revision-stale","OQ-0262-successor-omitted"], minimum=8)
print("check_release_validation_truth_gate_contract: OK")
