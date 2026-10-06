"""Validate the historical rev0371 Priority-0 custody timeline/distinct-custodian stopgate.

This checker preserves the historical rev0371 fixture. It must not remain current-tail authority
after later revisions, and it must not force stale OQ-0263/current-canon posture.
"""
import pathlib, zipfile
from priority_zero_assay_lib import load_json, assert_metric_contract, assert_variant_score_integrity, assert_scorecard_integrity, assert_negative_canaries, assert_surface_exists, file_sha256
from score_priority_zero_external_replay_response import DEFAULT_SCORER_INTAKE, resolve_default_scorer_intake, validate_response_file, ResponseIntakeError

ROOT = pathlib.Path(__file__).resolve().parents[1]
ASSAY_REL = "assays/priority-zero-custody-timeline-gate-2026-06-16.json"
DOC_REL = "docs/40-session/priority-zero-custody-timeline-gate-2026-06-16.md"
CHECKER_REL = "tools/check_priority_zero_custody_timeline_gate_contract.py"
LIB_REL = "tools/priority_zero_custody_timeline_lib.py"
SCORE_TOOL_REL = "tools/score_priority_zero_external_replay_response.py"
PREP_TOOL_REL = "tools/prepare_priority_zero_clean_response_custody_record.py"
VALIDATION_LIB_REL = "tools/validation_toolchain_lib.py"
SCORER_REL = "assays/priority-zero-timeline-hardened-external-replay-scorer-intake-2026-06-16.json"
RESPONDER_REL = "assays/priority-zero-timeline-hardened-external-replay-responder-only-2026-06-16.json"
TEMPLATE_REL = "assays/priority-zero-timeline-hardened-external-replay-response-template-2026-06-16.json"
README_REL = "handoffs/priority-zero-timeline-hardened-external-replay-responder-readme-2026-06-16.md"
BUNDLE_REL = "handoffs/priority-zero-timeline-hardened-external-replay-responder-bundle-2026-06-16.zip"
EVIDENCE_TEMPLATE_REL = "assays/priority-zero-timeline-hardened-clean-external-response-evidence-record-template-2026-06-16.json"
CUSTODY_README_REL = "handoffs/priority-zero-timeline-hardened-clean-response-custody-readme-2026-06-16.md"
SUBMISSION_KIT_REL = "handoffs/priority-zero-timeline-hardened-external-replay-submission-kit-2026-06-16.zip"
MANIFEST_REL = "handoffs/priority-zero-timeline-hardened-external-replay-handoff-manifest-2026-06-16.json"
TIME_RESPONSE_REL = "assays/priority-zero-timeline-hardened-external-replay-time-inverted-response-canary-2026-06-16.json"
TIME_EVIDENCE_REL = "assays/priority-zero-timeline-hardened-external-replay-time-inverted-custody-canary-2026-06-16.json"
SELF_EVIDENCE_REL = "assays/priority-zero-timeline-hardened-external-replay-self-custodied-custody-canary-2026-06-16.json"
BUILDER_REL = "tools/build_priority_zero_timeline_hardened_handoff_bundle.py"
OLD_CHECKER_REL = "tools/check_priority_zero_clean_response_admission_gate_contract.py"
OLD_RELEASE_CHECKER_REL = "tools/check_release_validation_truth_gate_contract.py"
OLD_SCORER_REL = "assays/priority-zero-custody-hardened-external-replay-scorer-intake-2026-06-16.json"

receipt = load_json("REVISION-RECEIPT.json")
assay = load_json(ASSAY_REL)
frontier = load_json("FRONTIER-BACKLOG.json")
ledger = load_json("SELF-SUFFICIENCY-LEDGER.json")
scorer = load_json(SCORER_REL)
manifest = load_json(MANIFEST_REL)
if assay.get("revision") != "rev0371" or assay.get("resolved_question") != "OQ-0262" or assay.get("next_open_question") != "OQ-0263":
    raise SystemExit("custody timeline assay must remain the historical rev0371 fixture")
if assay.get("resolution_id") != "RS-0270":
    raise SystemExit("timeline gate must route through historical RS-0270")
for token in ["No further internal gate-hardening counts as external replay progress", "OQ-0263 must import a response", "custodian_id that differs"]:
    if token not in (ROOT / DOC_REL).read_text(encoding="utf-8") and token not in assay.get("risk_burned", ""):
        raise SystemExit(f"timeline gate missing stopgate token: {token}")
for rel in [ASSAY_REL,DOC_REL,CHECKER_REL,LIB_REL,SCORE_TOOL_REL,PREP_TOOL_REL,VALIDATION_LIB_REL,SCORER_REL,RESPONDER_REL,TEMPLATE_REL,README_REL,BUNDLE_REL,EVIDENCE_TEMPLATE_REL,CUSTODY_README_REL,SUBMISSION_KIT_REL,MANIFEST_REL,TIME_RESPONSE_REL,TIME_EVIDENCE_REL,SELF_EVIDENCE_REL,BUILDER_REL,OLD_CHECKER_REL,OLD_RELEASE_CHECKER_REL]:
    assert_surface_exists(rel)
if DEFAULT_SCORER_INTAKE != "auto:frontier":
    raise SystemExit("default scorer selector must remain auto:frontier")
if receipt.get("revision") == "rev0371":
    if resolve_default_scorer_intake(ROOT) != SCORER_REL:
        raise SystemExit("rev0371 frontier must resolve to the timeline-hardened scorer")
    if frontier.get("items", [{}])[0].get("id") != "OQ-0263" or frontier.get("queue_head") != "OQ-0263" or frontier.get("generated_from") != "REVISION-RECEIPT.json#rev0371":
        raise SystemExit("rev0371 frontier backlog must route to OQ-0263")
    if SCORER_REL not in frontier.get("items", [{}])[0].get("fanout", []):
        raise SystemExit("OQ-0263 fanout must include timeline scorer intake")
else:
    if resolve_default_scorer_intake(ROOT) == SCORER_REL:
        raise SystemExit("historical rev0371 scorer must not remain current-tail authority")
with zipfile.ZipFile(ROOT / BUNDLE_REL) as zf:
    if sorted(zf.namelist()) != sorted([RESPONDER_REL, TEMPLATE_REL, README_REL]):
        raise SystemExit("timeline responder bundle contents drifted")
with zipfile.ZipFile(ROOT / SUBMISSION_KIT_REL) as zf:
    if sorted(zf.namelist()) != sorted([BUNDLE_REL, EVIDENCE_TEMPLATE_REL, CUSTODY_README_REL]):
        raise SystemExit("timeline submission kit contents drifted")
for key, rel in [("responder_only_sha256",RESPONDER_REL),("response_template_sha256",TEMPLATE_REL),("responder_bundle_sha256",BUNDLE_REL),("submission_kit_sha256",SUBMISSION_KIT_REL),("evidence_record_template_sha256",EVIDENCE_TEMPLATE_REL)]:
    if scorer.get(key) != file_sha256(rel):
        raise SystemExit(f"timeline scorer hash drifted for {key}")
for key in ["requires_custody_evidence_record","requires_custody_timeline_order","requires_responder_id_match","requires_distinct_custodian"]:
    if scorer.get(key) is not True:
        raise SystemExit(f"timeline scorer must require {key}")
if not isinstance(scorer.get("decision_thresholds"), dict):
    raise SystemExit("timeline scorer must configure decision thresholds")
if manifest.get("responder_bundle_sha256") != file_sha256(BUNDLE_REL) or manifest.get("submission_kit_sha256") != file_sha256(SUBMISSION_KIT_REL):
    raise SystemExit("timeline manifest bundle hash drifted")
for row in manifest.get("excluded_from_responder_bundle", []):
    if row.get("sha256") != file_sha256(row.get("path", "")):
        raise SystemExit(f"timeline manifest exclusion hash drifted for {row.get('path')}")
for rel, diagnostic in [(TIME_EVIDENCE_REL, "scorer_opened_at precedes response_frozen_at"), (SELF_EVIDENCE_REL, "custodian_id must differ")]:
    try:
        validate_response_file(TIME_RESPONSE_REL, scorer, scorer_intake=SCORER_REL, evidence_record=load_json(rel))
    except ResponseIntakeError as exc:
        if diagnostic not in str(exc):
            raise SystemExit(f"canary {rel} failed with wrong diagnostic: {exc}") from exc
    else:
        raise SystemExit(f"canary {rel} must fail closed")
if "validate_custody_timeline" not in (ROOT / SCORE_TOOL_REL).read_text(encoding="utf-8") or "requires_distinct_custodian" not in (ROOT / SCORE_TOOL_REL).read_text(encoding="utf-8"):
    raise SystemExit("score tool must use timeline validation")
if "custodian_id must differ" not in (ROOT / PREP_TOOL_REL).read_text(encoding="utf-8"):
    raise SystemExit("custody preparation helper must reject self-custody")
if pathlib.PurePosixPath(CHECKER_REL).name not in (ROOT / VALIDATION_LIB_REL).read_text(encoding="utf-8"):
    raise SystemExit("timeline checker must be in validation toolchain")
for token in ["historical rev0369", "not current-tail authority"]:
    if token not in (ROOT / OLD_CHECKER_REL).read_text(encoding="utf-8"):
        raise SystemExit("rev0369 checker must remain historical")
if "historical rev0370" not in (ROOT / OLD_RELEASE_CHECKER_REL).read_text(encoding="utf-8"):
    raise SystemExit("rev0370 release checker must be historical")
assert_metric_contract(assay, required={"custody-timeline-order-enforced", "responder-id-and-distinct-custodian-crosscheck", "decision-thresholds-configured", "default-scorer-currentness", "negative-canary-coverage", "historical-checker-refactor", "clean-response-absence-honesty", "successor-routing-stopgate"}, count=8)
variants = assert_variant_score_integrity(assay, required_variants={"pre-timeline-custody-admission","timeline-distinct-custodian-current-gate","time-inverted-custody-negative-canary","self-custodied-custody-negative-canary","clean-response-plus-timeline-custody-record"})
scorecard = assert_scorecard_integrity(assay, variants)
if variants["clean-response-plus-timeline-custody-record"].get("score") != 0 or scorecard.get("clean_external_response_evidence") is not False:
    raise SystemExit("clean external response evidence must remain absent")
for key, rel in [("resolved_default_scorer_intake_sha256",SCORER_REL),("responder_bundle_sha256",BUNDLE_REL),("submission_kit_sha256",SUBMISSION_KIT_REL),("time_inverted_evidence_sha256",TIME_EVIDENCE_REL),("self_custodied_evidence_sha256",SELF_EVIDENCE_REL)]:
    if scorecard.get(key) != file_sha256(rel):
        raise SystemExit(f"scorecard hash drifted for {key}")
assert_negative_canaries(assay,["time-inverted-custody-record-admitted-as-clean-evidence","self-custodied-custody-record-admitted-as-clean-evidence","gate-only-hardening-counted-as-external-progress"],minimum=10)
if not any(item.get("id") == "SA-0058" and item.get("frontier_id") == "OQ-0263" and item.get("assay_fixture") == ASSAY_REL for item in ledger.get("items", [])):
    raise SystemExit("historical rev0371 self-sufficiency row missing")
print("check_priority_zero_custody_timeline_gate_contract: OK")
