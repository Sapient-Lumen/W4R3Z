"""Validate the historical rev0369 clean-response admission/custody gate.

This checker preserves the old fixture as evidence after later revisions. It must not force the
rev0369 custody scorer to remain the current tail; it is not current-tail authority and does not force current canon additions.
"""
import pathlib, zipfile
from priority_zero_assay_lib import load_json, assert_metric_contract, assert_variant_score_integrity, assert_scorecard_integrity, assert_negative_canaries, assert_surface_exists, file_sha256
from score_priority_zero_external_replay_response import validate_response_file, validate_response, ResponseIntakeError, resolve_default_scorer_intake
ASSAY_REL="assays/priority-zero-clean-response-admission-gate-2026-06-16.json"; DOC_REL="docs/40-session/priority-zero-clean-response-admission-gate-2026-06-16.md"; CHECKER_REL="tools/check_priority_zero_clean_response_admission_gate_contract.py"; SCORER_REL="assays/priority-zero-custody-hardened-external-replay-scorer-intake-2026-06-16.json"; BUNDLE_REL="handoffs/priority-zero-custody-hardened-external-replay-responder-bundle-2026-06-16.zip"; SUBMISSION_KIT_REL="handoffs/priority-zero-custody-hardened-external-replay-submission-kit-2026-06-16.zip"; RESPONDER_REL="assays/priority-zero-custody-hardened-external-replay-responder-only-2026-06-16.json"; TEMPLATE_REL="assays/priority-zero-custody-hardened-external-replay-response-template-2026-06-16.json"; README_REL="handoffs/priority-zero-custody-hardened-external-replay-responder-readme-2026-06-16.md"; CUSTODY_TEMPLATE_REL="assays/priority-zero-clean-external-response-evidence-record-template-2026-06-16.json"; CUSTODY_README_REL="handoffs/priority-zero-clean-response-custody-readme-2026-06-16.md"; HANDOFF_MANIFEST_REL="handoffs/priority-zero-custody-hardened-external-replay-handoff-manifest-2026-06-16.json"; SELF_ATTESTED_CANARY_REL="assays/priority-zero-custody-hardened-external-replay-self-attested-cleanlike-canary-2026-06-16.json"; OLD_SCORER_REL="assays/priority-zero-submit-hardened-external-replay-scorer-intake-2026-06-16.json"; OLD_DRYRUN_RESPONSE_REL="assays/priority-zero-submit-hardened-external-replay-contaminated-dryrun-response-2026-06-16.json"
ROOT=pathlib.Path(__file__).resolve().parents[1]
receipt=load_json("REVISION-RECEIPT.json"); assay=load_json(ASSAY_REL); ledger=load_json("SELF-SUFFICIENCY-LEDGER.json"); scorer=load_json(SCORER_REL)
if assay.get("revision")!="rev0369" or assay.get("resolved_question")!="OQ-0260" or assay.get("next_open_question")!="OQ-0261": raise SystemExit("admission assay must remain historical rev0369 fixture")
for rel in [ASSAY_REL,DOC_REL,CHECKER_REL,SCORER_REL,BUNDLE_REL,SUBMISSION_KIT_REL,RESPONDER_REL,TEMPLATE_REL,README_REL,CUSTODY_TEMPLATE_REL,CUSTODY_README_REL,HANDOFF_MANIFEST_REL,SELF_ATTESTED_CANARY_REL,OLD_SCORER_REL,OLD_DRYRUN_RESPONSE_REL]: assert_surface_exists(rel)
if receipt.get("revision") == "rev0369" and CHECKER_REL not in receipt.get("canon_additions", []): raise SystemExit("rev0369 checker must be current canon when emitted")
if receipt.get("revision") > "rev0369" and resolve_default_scorer_intake(ROOT) == SCORER_REL: raise SystemExit("historical rev0369 scorer must not remain current-tail authority")
for key, rel in [("responder_only_sha256",RESPONDER_REL),("response_template_sha256",TEMPLATE_REL),("responder_bundle_sha256",BUNDLE_REL),("submission_kit_sha256",SUBMISSION_KIT_REL),("evidence_record_template_sha256",CUSTODY_TEMPLATE_REL)]:
    if scorer.get(key)!=file_sha256(rel): raise SystemExit(f"historical custody scorer hash drifted for {key}")
try:
    validate_response_file(SELF_ATTESTED_CANARY_REL, scorer, scorer_intake=SCORER_REL)
except ResponseIntakeError as exc:
    if "separate custody evidence record" not in str(exc): raise SystemExit(f"self-attested canary wrong diagnostic: {exc}") from exc
else: raise SystemExit("self-attested rev0369 canary must fail")
old_summary=validate_response(load_json(OLD_DRYRUN_RESPONSE_REL), load_json(OLD_SCORER_REL), allow_contaminated_dryrun=True)
if old_summary.get("external_response_evidence") is not False: raise SystemExit("historical dry-run must remain non-external")
assert_metric_contract(assay, required={"live-scorer-default-currentness","custody-evidence-record-required","self-attested-cleanlike-canary-rejected","stale-oq-routing-rubric-fixed","responder-bundle-current-tail","scorer-after-response-boundary","clean-response-absence-honesty","successor-routing"}, count=8)
variants=assert_variant_score_integrity(assay, required_variants={"pre-custody-submit-strict-path","custody-hardened-current-admission-gate","self-attested-cleanlike-negative-canary","clean-response-plus-custody-evidence"})
scorecard=assert_scorecard_integrity(assay,variants)
if scorecard.get("clean_external_response_evidence") is not False: raise SystemExit("historical rev0369 must preserve absent clean evidence")
if not any(item.get("assay_fixture")==ASSAY_REL and item.get("frontier_id")=="OQ-0261" for item in ledger.get("items",[])): raise SystemExit("historical rev0369 self-sufficiency row missing")
assert_negative_canaries(assay,["self-attested-cleanlike-response-treated-as-clean-evidence","missing-response-treated-as-clean-evidence"],minimum=8)
print("check_priority_zero_clean_response_admission_gate_contract: OK")
