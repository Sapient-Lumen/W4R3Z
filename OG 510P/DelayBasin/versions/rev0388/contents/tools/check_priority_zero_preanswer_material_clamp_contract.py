"""Validate the current rev0374 Priority-0 pre-answer material clamp.

The checker is deliberately narrow: it proves the live scorer requires exact
pre-answer material equality to the responder bundle only, post-freeze custody
and scorer kits are physically separated, cross-operator causality is carried
by exact artifact hashes rather than unsynchronised wall clocks, scorer-local
chronology is enforced, and clean external evidence remains absent.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import pathlib
import stat
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timedelta

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from priority_zero_assay_lib import (  # noqa: E402
    assert_metric_contract,
    assert_negative_canaries,
    assert_scorecard_integrity,
    assert_surface_exists,
    assert_tokens,
    assert_variant_score_integrity,
    file_sha256,
    load_json,
)
from score_priority_zero_external_replay_response import (  # noqa: E402
    ResponseIntakeError,
    resolve_default_scorer_intake,
    validate_response_file,
)
from priority_zero_external_replay_decision_lib import decide_compact_gate  # noqa: E402
from priority_zero_causal_artifact_lib import (  # noqa: E402
    CURRENT_CUSTODY_CONTRACT,
    CURRENT_SCORING_CONTRACT,
)

ASSAY_REL = "assays/priority-zero-preanswer-material-clamp-2026-06-16.json"
DOC_REL = "docs/40-session/priority-zero-preanswer-material-clamp-2026-06-16.md"
CHECKER_REL = "tools/check_priority_zero_preanswer_material_clamp_contract.py"
HISTORICAL_CHECKER_REL = "tools/check_priority_zero_selfhash_split_bundle_contract.py"
SCORER_REL = "assays/priority-zero-preanswer-clamped-external-replay-scorer-intake-2026-06-16.json"
RESPONDER_REL = "assays/priority-zero-preanswer-clamped-external-replay-responder-only-2026-06-16.json"
TEMPLATE_REL = "assays/priority-zero-preanswer-clamped-external-replay-response-template-2026-06-16.json"
EVIDENCE_TEMPLATE_REL = "assays/priority-zero-preanswer-clamped-clean-external-response-evidence-record-template-2026-06-16.json"
SCORE_SHEET_TEMPLATE_REL = "assays/priority-zero-preanswer-clamped-external-replay-score-sheet-template-2026-06-16.json"
RESPONDER_README_REL = "handoffs/priority-zero-preanswer-clamped-external-replay-responder-readme-2026-06-16.md"
CUSTODY_README_REL = "handoffs/priority-zero-preanswer-clamped-clean-response-custody-readme-2026-06-16.md"
SCORER_README_REL = "handoffs/priority-zero-preanswer-clamped-external-replay-scorer-readme-2026-06-16.md"
BUNDLE_REL = "handoffs/priority-zero-preanswer-clamped-external-replay-responder-bundle-2026-06-16.zip"
CUSTODY_KIT_REL = "handoffs/priority-zero-preanswer-clamped-external-replay-postfreeze-custody-kit-2026-06-16.zip"
SCORER_KIT_REL = "handoffs/priority-zero-preanswer-clamped-external-replay-scorer-kit-2026-06-16.zip"
MANIFEST_REL = "handoffs/priority-zero-preanswer-clamped-external-replay-handoff-manifest-2026-06-16.json"
SCORE_TOOL_REL = "tools/score_priority_zero_external_replay_response.py"
RESPONSE_PREP_TOOL_REL = "tools/prepare_priority_zero_external_replay_response.py"
CUSTODY_PREP_TOOL_REL = "tools/prepare_priority_zero_clean_response_custody_record.py"
SCORE_SHEET_PREP_TOOL_REL = "tools/prepare_priority_zero_external_replay_score_sheet.py"
ARTIFACT_LIB_REL = "tools/priority_zero_external_run_artifact_lib.py"
CUSTODY_LIB_REL = "tools/priority_zero_external_replay_custody_lib.py"
CAUSAL_LIB_REL = "tools/priority_zero_causal_artifact_lib.py"
RESPONSE_LIB_REL = "tools/priority_zero_external_replay_response_lib.py"
BUILDER_REL = "tools/build_priority_zero_preanswer_clamped_handoff_bundle.py"
VALIDATION_LIB_REL = "tools/validation_toolchain_lib.py"
SELF_SUFFICIENCY_REL = "SELF-SUFFICIENCY-LEDGER.json"
FRONTIER_REL = "FRONTIER-BACKLOG.json"
RESOLUTION_REL = "RESOLUTION-LEDGER.json"
RECEIPT_REL = "REVISION-RECEIPT.json"
OLD_SCORER_REL = "assays/priority-zero-selfhash-split-external-replay-scorer-intake-2026-06-16.json"
OLD_SUBMISSION_KIT_REL = "handoffs/priority-zero-selfhash-split-external-replay-submission-kit-2026-06-16.zip"

receipt = load_json(RECEIPT_REL)
assay = load_json(ASSAY_REL)
scorer = load_json(SCORER_REL)
response_template = load_json(TEMPLATE_REL)
evidence_template = load_json(EVIDENCE_TEMPLATE_REL)
score_sheet_template = load_json(SCORE_SHEET_TEMPLATE_REL)
manifest = load_json(MANIFEST_REL)
frontier = load_json(FRONTIER_REL)
ledger = load_json(SELF_SUFFICIENCY_REL)
resolutions = load_json(RESOLUTION_REL)

if receipt.get("revision") != "rev0374" or assay.get("revision") != "rev0374":
    raise SystemExit("preanswer material clamp checker must run at rev0374")
if receipt.get("resolved_question") != "OQ-0265" or receipt.get("next_open_question") != "OQ-0266":
    raise SystemExit("rev0374 receipt must resolve OQ-0265 and open OQ-0266")
if receipt.get("current_resolution_id") != "RS-0273" or assay.get("resolution_id") != "RS-0273":
    raise SystemExit("preanswer material clamp must route through RS-0273")
if resolve_default_scorer_intake(ROOT) != SCORER_REL:
    raise SystemExit("auto:frontier must resolve to the preanswer-clamped scorer")
if frontier.get("items", [{}])[0].get("id") != "OQ-0266" or frontier.get("queue_head") != "OQ-0266":
    raise SystemExit("frontier backlog must route to OQ-0266")
if SCORER_REL not in frontier.get("items", [{}])[0].get("fanout", []):
    raise SystemExit("OQ-0266 fanout must include preanswer-clamped scorer intake")
if OLD_SCORER_REL in frontier.get("items", [{}])[0].get("fanout", []):
    raise SystemExit("OQ-0266 fanout must not keep rev0373 selfhash scorer as current authority")
if not any(row.get("id") == "RS-0273" and "OQ-0265" in row.get("resolved_objects", []) and row.get("successor_question") == "OQ-0266" for row in resolutions.get("items", [])):
    raise SystemExit("RESOLUTION-LEDGER must close OQ-0265 via RS-0273 with successor OQ-0266")

for rel in [
    ASSAY_REL,
    DOC_REL,
    CHECKER_REL,
    HISTORICAL_CHECKER_REL,
    SCORER_REL,
    RESPONDER_REL,
    TEMPLATE_REL,
    EVIDENCE_TEMPLATE_REL,
    SCORE_SHEET_TEMPLATE_REL,
    RESPONDER_README_REL,
    CUSTODY_README_REL,
    SCORER_README_REL,
    BUNDLE_REL,
    CUSTODY_KIT_REL,
    SCORER_KIT_REL,
    MANIFEST_REL,
    SCORE_TOOL_REL,
    RESPONSE_PREP_TOOL_REL,
    CUSTODY_PREP_TOOL_REL,
    ARTIFACT_LIB_REL,
    CUSTODY_LIB_REL,
    CAUSAL_LIB_REL,
    RESPONSE_LIB_REL,
    SCORE_SHEET_PREP_TOOL_REL,
    BUILDER_REL,
    VALIDATION_LIB_REL,
    SELF_SUFFICIENCY_REL,
    FRONTIER_REL,
    RESOLUTION_REL,
    RECEIPT_REL,
]:
    assert_surface_exists(rel)

for rel in [
    ASSAY_REL,
    DOC_REL,
    CHECKER_REL,
    HISTORICAL_CHECKER_REL,
    SCORER_REL,
    RESPONDER_REL,
    TEMPLATE_REL,
    EVIDENCE_TEMPLATE_REL,
    SCORE_SHEET_TEMPLATE_REL,
    BUNDLE_REL,
    CUSTODY_KIT_REL,
    SCORER_KIT_REL,
    MANIFEST_REL,
    SCORE_TOOL_REL,
    CUSTODY_LIB_REL,
    BUILDER_REL,
    VALIDATION_LIB_REL,
    FRONTIER_REL,
    SELF_SUFFICIENCY_REL,
    RESOLUTION_REL,
]:
    if rel not in receipt.get("canon_additions", []):
        raise SystemExit(f"preanswer clamp surface must be current canon addition: {rel}")

assert_tokens((ROOT / DOC_REL).read_text(encoding="utf-8"), [
    "pre-answer material exact-match",
    "old submission kit",
    "score-time chronology guard",
    "OQ-0266",
], label="preanswer clamp doc")
score_tool_text = (ROOT / SCORE_TOOL_REL).read_text(encoding="utf-8")
assert_tokens(score_tool_text, [
    "def _validate_pre_response_materials",
    "def _bind_json_object_to_file",
    "custody evidence pre-response material must exactly match allowed responder-only bundle list",
    "scorer-local scoring timeline",
    "exact-artifact-hash-chain-not-wall-clock",
    "responder self-scoring is not admissible",
    "must provide metric_rationales for every metric",
    "requires_per_packet_operator_cost",
    "synthetic packets are co-visible",
    "strict_json_bytes",
    "response bytes validated by this run",
    "current finalized response contract failed",
    "custody response_finalized_at does not match response.response_artifact.finalized_at",
    "response_contract_state",
], label="external replay scorer")
assert_tokens((ROOT / ARTIFACT_LIB_REL).read_text(encoding="utf-8"), [
    "contains duplicate JSON object key",
    "parse_float=finite_float",
    "outside the finite runtime range",
], label="shared strict artifact parser")
assert_tokens((ROOT / CUSTODY_LIB_REL).read_text(encoding="utf-8"), [
    "current custody evidence must not contain scorer-stage field",
    "current custody evidence must not contain legacy wall-clock/scorer attestation",
    "current custody evidence top-level fields drifted from template",
    "custodian_id must differ from response responder_id",
], label="shared current custody contract")
assert_tokens((ROOT / HISTORICAL_CHECKER_REL).read_text(encoding="utf-8"), [
    "historical rev0373",
    "must not remain current-tail authority after rev0374",
], label="historical selfhash checker")
if CHECKER_REL.split("/", 1)[1] not in (ROOT / VALIDATION_LIB_REL).read_text(encoding="utf-8"):
    raise SystemExit("preanswer clamp checker must be in validation toolchain")

# Bundle topology: only the responder bundle is pre-response material.
with zipfile.ZipFile(ROOT / BUNDLE_REL) as zf:
    expected = sorted([
        RESPONDER_REL, TEMPLATE_REL, RESPONDER_README_REL, RESPONSE_PREP_TOOL_REL,
        ARTIFACT_LIB_REL, RESPONSE_LIB_REL,
    ])
    if sorted(zf.namelist()) != expected:
        raise SystemExit("preanswer responder bundle contents drifted")
    bundle_text = "\n".join(zf.read(name).decode("utf-8", errors="ignore") for name in zf.namelist())
    for token in [
        "answer_key",
        "true_variant",
        "expected_score",
        file_sha256(BUNDLE_REL),
        file_sha256(CUSTODY_KIT_REL),
        file_sha256(SCORER_KIT_REL),
        file_sha256(SCORER_REL),
    ]:
        if token in bundle_text:
            raise SystemExit(f"responder bundle leaked scorer or expected-hash token: {token}")
with zipfile.ZipFile(ROOT / CUSTODY_KIT_REL) as zf:
    if sorted(zf.namelist()) != sorted([
        EVIDENCE_TEMPLATE_REL, TEMPLATE_REL, CUSTODY_README_REL, CUSTODY_PREP_TOOL_REL,
        CAUSAL_LIB_REL, ARTIFACT_LIB_REL, RESPONSE_LIB_REL, "tools/priority_zero_custody_timeline_lib.py", CUSTODY_LIB_REL,
    ]):
        raise SystemExit("post-freeze custody kit contents drifted")
with zipfile.ZipFile(ROOT / SCORER_KIT_REL) as zf:
    expected = sorted([
        SCORER_REL,
        SCORE_SHEET_TEMPLATE_REL,
        EVIDENCE_TEMPLATE_REL,
        RESPONDER_REL,
        TEMPLATE_REL,
        SCORE_TOOL_REL,
        SCORE_SHEET_PREP_TOOL_REL,
        CAUSAL_LIB_REL,
        ARTIFACT_LIB_REL,
        RESPONSE_LIB_REL,
        "tools/priority_zero_assay_lib.py",
        "tools/priority_zero_external_replay_decision_lib.py",
        "tools/priority_zero_custody_timeline_lib.py",
        CUSTODY_LIB_REL,
        SCORER_README_REL,
    ])
    if sorted(zf.namelist()) != expected:
        raise SystemExit("preanswer scorer kit contents drifted")

if scorer.get("requires_pre_response_material_exact_match") is not True:
    raise SystemExit("preanswer scorer must require exact pre-response material match")
if scorer.get("allowed_pre_response_materials") != [BUNDLE_REL]:
    raise SystemExit("preanswer scorer allowed_pre_response_materials must be exactly the responder bundle")
if scorer.get("requires_score_sheet_chronology") is not True:
    raise SystemExit("preanswer scorer must require score-sheet chronology")
if scorer.get("custody_contract_version") != CURRENT_CUSTODY_CONTRACT:
    raise SystemExit(f"preanswer scorer must use {CURRENT_CUSTODY_CONTRACT}")
if scorer.get("scoring_contract_version") != CURRENT_SCORING_CONTRACT:
    raise SystemExit(f"preanswer scorer must use {CURRENT_SCORING_CONTRACT}")
if scorer.get("response_preparation_contract_version") != "responder-finalize-v1":
    raise SystemExit("preanswer scorer must require responder-finalize-v1")
if scorer.get("requires_tool_finalized_response") is not True:
    raise SystemExit("preanswer scorer must require a tool-finalized response before custody")
if scorer.get("required_custody_evidence_state") != "completed-response-and-causal-custody-record-frozen-before-scorer-kit":
    raise SystemExit("preanswer scorer must require the causal custody state")
if scorer.get("requires_separate_score_sheet") is not True:
    raise SystemExit("preanswer scorer must require separate score sheet")
for key in [
    "requires_bound_custody_record_file",
    "requires_bound_score_sheet_file",
    "requires_distinct_scorer_from_responder",
    "requires_metric_rationales",
    "requires_packet_score_notes",
    "requires_per_packet_operator_cost",
    "requires_operator_cost_sum_match",
]:
    if scorer.get(key) is not True:
        raise SystemExit(f"preanswer scorer must require {key}")
if scorer.get("custodian_may_score") is not True:
    raise SystemExit("preanswer scorer must preserve a two-operator minimum by allowing the custodian to score")
if scorer.get("allows_global_compact_gate_confirmation") is not False:
    raise SystemExit("co-visible trace-excerpt assay must not claim global compact-gate confirmation")
if scorer.get("full_archive_control_state") != "packet-delta is a trace excerpt rather than a measured full-archive load":
    raise SystemExit("preanswer scorer must state the trace-excerpt control boundary")
if scorer.get("decision_thresholds", {}).get("compact_cost_must_not_exceed_full") is not True:
    raise SystemExit("preanswer decision must compare compact packet cost against the trace control")
for required_attestation in [
    "response_was_tool_finalized_before_scoring",
    "custody_record_hash_bound_before_score_draft_published",
    "custody_record_observed_before_scoring",
    "scorer_used_only_frozen_response_custody_and_current_scorer_kit",
]:
    if required_attestation not in scorer.get("required_score_sheet_attestations", []):
        raise SystemExit(f"preanswer scorer missing current score-stage attestation: {required_attestation}")
for required_attestation in [
    "custody_helper_observed_exact_response_before_record_freeze",
    "required_prerequisites_observed_before_custody_record_frozen",
    "scorer_kit_not_opened_before_custody_record_frozen",
]:
    if required_attestation not in scorer.get("required_custody_attestations", []):
        raise SystemExit(f"preanswer scorer missing current custody attestation: {required_attestation}")
if "scorer_used_only_frozen_response_custody_and_current_scorer_kit" not in scorer.get("required_score_sheet_attestations", []):
    raise SystemExit("preanswer scorer must use the corrected scorer-input attestation")
template_metric_ids = {row.get("id") for row in scorer.get("metrics", [])}
template_rows = score_sheet_template.get("manual_metric_scores", [])
if [row.get("label") for row in template_rows] != ["packet-alpha", "packet-bravo", "packet-charlie", "packet-delta"]:
    raise SystemExit("preanswer score sheet template packet rows drifted")
for row in template_rows:
    if set(row.get("metric_scores", {})) != template_metric_ids or set(row.get("metric_rationales", {})) != template_metric_ids:
        raise SystemExit(f"preanswer score sheet template must scaffold every score and rationale key for {row.get('label')}")
if "scorer_used_only_frozen_response_and_custody_record" in score_sheet_template.get("scorer_attestation", {}):
    raise SystemExit("preanswer score sheet template retained the contradictory legacy scorer-input attestation")
if score_sheet_template.get("scorer_attestation", {}).get("scorer_used_only_frozen_response_custody_and_current_scorer_kit") is not None:
    raise SystemExit("preanswer score sheet template must expose the corrected blank scorer-input attestation")
if score_sheet_template.get("scoring_contract_version") != CURRENT_SCORING_CONTRACT:
    raise SystemExit(f"preanswer score sheet template must expose {CURRENT_SCORING_CONTRACT}")
if score_sheet_template.get("scorer_attestation", {}).get("scorer_kit_opened_at") != "":
    raise SystemExit("preanswer score sheet template must expose blank scorer_kit_opened_at")
if response_template.get("response_preparation_contract_version") != "responder-finalize-v1":
    raise SystemExit("response template must expose responder-finalize-v1")
if response_template.get("response_artifact", {}).get("finalizer_tool") != RESPONSE_PREP_TOOL_REL:
    raise SystemExit("response template must name the bundled response finalizer")
if response_template.get("response_artifact", {}).get("timestamp_source") != "local-process-clock-at-bundled-helper":
    raise SystemExit("response template must expose helper-owned timestamp source")
if evidence_template.get("response_preparation_contract_version") != "responder-finalize-v1":
    raise SystemExit("custody template must require responder-finalize-v1")
if score_sheet_template.get("response_preparation_contract_version") != "responder-finalize-v1":
    raise SystemExit("score sheet template must require responder-finalize-v1")
for key in ["scorer_kit_opened_at_source", "custody_record_observed_at_source", "scored_at_source"]:
    if score_sheet_template.get("scorer_attestation", {}).get(key) != "":
        raise SystemExit(f"score sheet template must expose blank helper-owned source field: {key}")
scorer_text = json.dumps(scorer, ensure_ascii=False)
for stale in [
    "OQ-0264 must import a response",
    "routes OQ-0264 to OQ-0265",
]:
    if stale in scorer_text:
        raise SystemExit(f"preanswer scorer retained stale frontier routing: {stale}")
for current in [
    "OQ-0266 must import a response/custody/score-sheet triplet",
    "recognizes OQ-0265 as closed",
    "routes OQ-0266",
]:
    if current not in scorer_text:
        raise SystemExit(f"preanswer scorer missing current frontier routing: {current}")
for token in ["submission kit", "custody kit", "scorer kit", "score sheet", "handoff manifest", "expected digest", "prior conversation"]:
    if token not in "\n".join(scorer.get("forbidden_pre_response_material_tokens", [])):
        raise SystemExit(f"preanswer scorer missing forbidden token: {token}")
for key, rel in [
    ("responder_only_sha256", RESPONDER_REL),
    ("response_template_sha256", TEMPLATE_REL),
    ("responder_bundle_sha256", BUNDLE_REL),
    ("evidence_record_template_sha256", EVIDENCE_TEMPLATE_REL),
    ("score_sheet_template_sha256", SCORE_SHEET_TEMPLATE_REL),
    ("custody_kit_sha256", CUSTODY_KIT_REL),
]:
    if scorer.get(key) != file_sha256(rel):
        raise SystemExit(f"preanswer scorer hash drifted for {key}")
for key, rel in [
    ("responder_bundle_sha256", BUNDLE_REL),
    ("custody_kit_sha256", CUSTODY_KIT_REL),
    ("scorer_kit_sha256", SCORER_KIT_REL),
    ("responder_only_sha256", RESPONDER_REL),
    ("response_template_sha256", TEMPLATE_REL),
    ("evidence_record_template_sha256", EVIDENCE_TEMPLATE_REL),
    ("score_sheet_template_sha256", SCORE_SHEET_TEMPLATE_REL),
    ("scorer_intake_sha256", SCORER_REL),
]:
    if manifest.get(key) != file_sha256(rel):
        raise SystemExit(f"preanswer manifest hash drifted for {key}")
if manifest.get("custody_contract_version") != CURRENT_CUSTODY_CONTRACT or manifest.get("scoring_contract_version") != CURRENT_SCORING_CONTRACT:
    raise SystemExit("preanswer manifest must identify the current causal three-stage contracts")
if manifest.get("cross_operator_ordering_basis") != "exact-artifact-hash-chain; independent wall clocks are descriptive only":
    raise SystemExit("preanswer manifest must state the exact-artifact cross-operator ordering basis")
if manifest.get("minimum_distinct_operators") != 2:
    raise SystemExit("preanswer manifest must preserve the two-operator minimum")
if manifest.get("response_preparation_contract_version") != "responder-finalize-v1":
    raise SystemExit("preanswer manifest must identify responder-finalize-v1")
expected_responder_members = [
    RESPONDER_REL, TEMPLATE_REL, RESPONDER_README_REL, RESPONSE_PREP_TOOL_REL,
    ARTIFACT_LIB_REL, RESPONSE_LIB_REL,
]
expected_custody_members = [
    EVIDENCE_TEMPLATE_REL, TEMPLATE_REL, CUSTODY_README_REL, CUSTODY_PREP_TOOL_REL,
    CAUSAL_LIB_REL, ARTIFACT_LIB_REL, RESPONSE_LIB_REL, "tools/priority_zero_custody_timeline_lib.py", CUSTODY_LIB_REL,
]
expected_scorer_members = [
    SCORER_REL, SCORE_SHEET_TEMPLATE_REL, EVIDENCE_TEMPLATE_REL, RESPONDER_REL, TEMPLATE_REL, SCORE_TOOL_REL,
    SCORE_SHEET_PREP_TOOL_REL, CAUSAL_LIB_REL, ARTIFACT_LIB_REL, RESPONSE_LIB_REL,
    "tools/priority_zero_assay_lib.py", "tools/priority_zero_external_replay_decision_lib.py",
    "tools/priority_zero_custody_timeline_lib.py", CUSTODY_LIB_REL, SCORER_README_REL,
]
for key, expected in [
    ("responder_bundle_members", expected_responder_members),
    ("custody_kit_members", expected_custody_members),
    ("scorer_kit_members", expected_scorer_members),
]:
    if manifest.get(key) != expected:
        raise SystemExit(f"preanswer manifest {key} drifted")
expected_sequence = [
    "finalize completed responder output with bundled response helper",
    "open custody kit and revalidate the exact response bytes",
    "freeze custody record with producer-local response observation",
    "open scorer kit and initialize score draft after exact custody validation",
    "complete and freeze score sheet with scorer-local custody observation",
    "run scorer on the exact response/custody/score-sheet hash chain",
]
if manifest.get("postfreeze_sequence") != expected_sequence:
    raise SystemExit("preanswer manifest postfreeze sequence drifted")
excluded_paths = {row.get("path") for row in manifest.get("excluded_from_responder_bundle", []) if isinstance(row, dict)}
for helper in [CUSTODY_PREP_TOOL_REL, SCORE_SHEET_PREP_TOOL_REL]:
    if helper not in excluded_paths:
        raise SystemExit(f"preanswer manifest must keep post-freeze helper out of responder bundle: {helper}")

required_metrics = {
    "pre-response-material-exactness",
    "postfreeze-custody-separation",
    "forbidden-preanswer-leak-rejection",
    "score-sheet-chronology-enforced",
    "scorer-kit-isolation-runnability",
    "historical-defect-honesty",
    "clean-response-absence-honesty",
    "successor-routing",
}
assert_metric_contract(assay, required=required_metrics, count=8)
variants = assert_variant_score_integrity(assay, required_variants={
    "pre-clamp-selfhash-submission-risk",
    "preanswer-clamped-current-workbench",
    "submission-kit-preanswer-negative-canary",
    "score-sheet-time-inversion-negative-canary",
    "clean-response-plus-custody-plus-score-sheet-evidence",
})
scorecard = assert_scorecard_integrity(assay, variants)
if scorecard.get("clean_external_response_evidence") is not False:
    raise SystemExit("preanswer assay must keep clean external response evidence false")
if scorecard.get("allowed_pre_response_materials") != [BUNDLE_REL]:
    raise SystemExit("preanswer assay scorecard must name exact responder bundle boundary")
for key in [
    "tool_finalized_response_required",
    "response_content_validated_before_custody",
    "shared_response_validator_reused_across_stages",
]:
    if scorecard.get(key) is not True:
        raise SystemExit(f"preanswer assay scorecard must require {key}")
if scorecard.get("response_preparation_contract_version") != "responder-finalize-v1":
    raise SystemExit("preanswer assay scorecard must identify responder-finalize-v1")
if scorecard.get("stage_timestamp_cli_arguments_allowed") is not False:
    raise SystemExit("preanswer assay scorecard must reject manual stage-time CLI inputs")
if scorecard.get("trusted_timestamp_authority_claimed") is not False:
    raise SystemExit("preanswer assay must not overclaim helper clocks as trusted timestamps")
if scorecard.get("custody_contract_version") != CURRENT_CUSTODY_CONTRACT or scorecard.get("scoring_contract_version") != CURRENT_SCORING_CONTRACT:
    raise SystemExit("preanswer assay scorecard must expose the current causal stage contracts")
if scorecard.get("cross_operator_ordering_basis") != "exact-artifact-hash-chain-not-wall-clock":
    raise SystemExit("preanswer assay scorecard must state exact-artifact cross-operator ordering")
if scorecard.get("cross_machine_clock_skew_canary_passed") is not True:
    raise SystemExit("preanswer assay scorecard must preserve the positive clock-skew canary")
for key, rel in [
    ("resolved_default_scorer_intake_sha256", SCORER_REL),
    ("responder_bundle_sha256", BUNDLE_REL),
    ("custody_kit_sha256", CUSTODY_KIT_REL),
    ("scorer_kit_sha256", SCORER_KIT_REL),
    ("response_template_sha256", TEMPLATE_REL),
    ("score_sheet_template_sha256", SCORE_SHEET_TEMPLATE_REL),
    ("evidence_record_template_sha256", EVIDENCE_TEMPLATE_REL),
    ("handoff_manifest_sha256", MANIFEST_REL),
    ("response_preparation_tool_sha256", RESPONSE_PREP_TOOL_REL),
    ("response_contract_library_sha256", RESPONSE_LIB_REL),
    ("strict_artifact_library_sha256", ARTIFACT_LIB_REL),
    ("custody_contract_library_sha256", CUSTODY_LIB_REL),
    ("causal_artifact_library_sha256", CAUSAL_LIB_REL),
]:
    if scorecard.get(key) != file_sha256(rel):
        raise SystemExit(f"preanswer assay scorecard hash drifted for {key}")
assert_negative_canaries(assay, [
    "submission-or-custody-kit-shown-before-response-admitted",
    "score-sheet-scored-at-before-scorer-kit-open-admitted",
    "scorer-local-custody-observation-before-scorer-kit-open-admitted",
    "missing-clean-response-treated-as-clean-evidence",
    "compact-gate-confirmed-without-triplet",
    "split-brain-custody-object-file-pair-admitted",
    "responder-self-scoring-admitted-as-separated-score",
    "metric-score-without-rationale-admitted",
    "boolean-metric-score-admitted-as-number",
    "missing-per-packet-operator-cost-admitted",
    "packet-cost-sum-mismatch-admitted",
    "compact-cost-disadvantage-treated-as-support",
    "co-visible-trace-excerpt-treated-as-global-compact-confirmation",
    "duplicate-json-key-admitted-in-bound-artifact",
    "legacy-scorer-stage-fields-in-current-custody-admitted",
    "incomplete-response-finalized-before-custody",
    "unfinalized-response-admitted-to-custody",
    "operator-supplied-stage-time-required-by-current-helper",
    "response-artifact-time-binding-drift-admitted",
    "undeclared-response-field-finalized",
    "undeclared-custody-field-admitted",
    "undeclared-score-sheet-field-admitted",
], minimum=26)

latest_sa = ledger.get("items", [])[-1]
if latest_sa.get("id") != "SA-0061" or latest_sa.get("frontier_id") != "OQ-0266" or latest_sa.get("assay_fixture") != ASSAY_REL:
    raise SystemExit("SELF-SUFFICIENCY-LEDGER tail must be SA-0061 for OQ-0266 and current assay")

metrics = [row["id"] for row in scorer["metrics"]]

def score_map(total: int) -> dict[str, int]:
    scores = {metric: 0 for metric in metrics}
    left = total
    for metric in metrics:
        give = min(2, left)
        scores[metric] = give
        left -= give
        if left <= 0:
            break
    return scores


def rationale_map(label: str) -> dict[str, str]:
    return {
        metric: f"synthetic checker evidence for {label}: {metric} was scored from the frozen packet answer against the current rubric"
        for metric in metrics
    }

with tempfile.TemporaryDirectory(prefix="delaybasin-preanswer-clamp-") as tmp:
    tmpdir = pathlib.Path(tmp)

    # Exercise the exact responder bundle first.  No hand-built response is
    # allowed in the current positive path.
    responder_kit_root = tmpdir / "standalone-responder-kit"
    with zipfile.ZipFile(ROOT / BUNDLE_REL) as zf:
        zf.extractall(responder_kit_root)
    response_draft_path = tmpdir / "response-draft.json"
    response_init = subprocess.run(
        [
            sys.executable,
            "-S",
            RESPONSE_PREP_TOOL_REL,
            "init",
            "--bundle-file",
            str(ROOT / BUNDLE_REL),
            "--responder-id",
            "responder-preanswer-smoke",
            "--out",
            str(response_draft_path),
        ],
        cwd=responder_kit_root,
        env={**dict(os.environ), "PYTHONDONTWRITEBYTECODE": "1"},
        text=True,
        capture_output=True,
    )
    if response_init.returncode != 0:
        raise SystemExit("standalone responder-kit init failed: " + (response_init.stderr or response_init.stdout).strip())
    response_draft = json.loads(response_draft_path.read_text(encoding="utf-8"))
    if response_draft.get("response_state") != "pre-response-draft":
        raise SystemExit("responder helper did not create a pre-response draft")
    if response_draft.get("response_preparation_contract_version") != "responder-finalize-v1":
        raise SystemExit("responder helper draft did not bind responder-finalize-v1")
    if response_draft.get("responder_stage", {}).get("saw_responder_bundle_sha256") != file_sha256(BUNDLE_REL):
        raise SystemExit("responder helper did not hash the exact original responder ZIP")

    answers_by_label = {
        "packet-alpha": {
            "operator_cost_minutes": 1,
            "mission_heart": "decoy material overclaims continuation and should be rejected as sham continuity",
            "oq_routing": "do not resolve OQ-0266 from this packet",
            "compact_gate_posture": "remain narrowed",
            "waste_or_refactor_implicated": "negative canary confirms false continuity risk",
            "next_safe_action": "abstain and require clean packet evidence",
            "abstentions": "no compact confirmation",
            "uncertainty_or_conflicts": "decoy packet conflicts with scorer key",
        },
        "packet-bravo": {
            "operator_cost_minutes": 2,
            "mission_heart": "typed public continuation under leakage-resistant replay",
            "oq_routing": "OQ-0266 is live until a clean triplet exists",
            "compact_gate_posture": "compact default can confirm only after clean response, custody record, and score sheet validate",
            "waste_or_refactor_implicated": "old submission kits before response are the waste and leak path",
            "next_safe_action": "finalize response, then open custody, then scorer material",
            "abstentions": "no deletion authority or benchmark authority",
            "uncertainty_or_conflicts": "same-session smoke is not external certification",
        },
        "packet-charlie": {
            "operator_cost_minutes": 1,
            "mission_heart": "without archive evidence the safe posture is abstention",
            "oq_routing": "unknown; cannot establish current frontier",
            "compact_gate_posture": "remain narrowed",
            "waste_or_refactor_implicated": "no-archive baseline tests abstention",
            "next_safe_action": "request authorized surfaces",
            "abstentions": "cannot certify compact cue",
            "uncertainty_or_conflicts": "insufficient evidence",
        },
        "packet-delta": {
            "operator_cost_minutes": 5,
            "mission_heart": "full public trace can recover detail but costs more",
            "oq_routing": "OQ-0266 remains live until a clean triplet validates",
            "compact_gate_posture": "full trace is escalation, not default proof",
            "waste_or_refactor_implicated": "archive mass must prove marginal value",
            "next_safe_action": "score compact, sham, baseline, and trace conditions within scope",
            "abstentions": "do not infer deletion safety",
            "uncertainty_or_conflicts": "operator cost may dominate marginal score",
        },
    }
    for row in response_draft["responder_stage"]["packet_answers"]:
        row.update(answers_by_label[row["label"]])
    response_draft["responder_stage"]["operator_cost_minutes"] = 9
    response_draft_path.write_text(json.dumps(response_draft, indent=2) + "\n", encoding="utf-8")

    # The reproduced rev0380 defect: a structurally bound but incomplete
    # response must now fail at responder finalization, before custody opens.
    incomplete_draft = copy.deepcopy(response_draft)
    incomplete_draft["responder_stage"]["packet_answers"][0]["mission_heart"] = ""
    incomplete_draft_path = tmpdir / "incomplete-response-draft.json"
    incomplete_draft_path.write_text(json.dumps(incomplete_draft, indent=2) + "\n", encoding="utf-8")
    incomplete_output = tmpdir / "incomplete-frozen-response.json"
    incomplete_finalize = subprocess.run(
        [
            sys.executable,
            "-S",
            RESPONSE_PREP_TOOL_REL,
            "finalize",
            "--draft",
            str(incomplete_draft_path),
            "--bundle-file",
            str(ROOT / BUNDLE_REL),
            "--exposure-notes",
            "synthetic checker incomplete-response canary",
            "--attest-clean-preanswer",
            "--out",
            str(incomplete_output),
        ],
        cwd=responder_kit_root,
        env={**dict(os.environ), "PYTHONDONTWRITEBYTECODE": "1"},
        text=True,
        capture_output=True,
    )
    if incomplete_finalize.returncode == 0 or incomplete_output.exists():
        raise SystemExit("responder helper finalized an incomplete response before custody")
    if "mission_heart" not in (incomplete_finalize.stderr + incomplete_finalize.stdout):
        raise SystemExit("incomplete-response canary failed without identifying the missing answer field")

    drifted_draft = copy.deepcopy(response_draft)
    started = datetime.fromisoformat(
        drifted_draft["responder_stage"]["run_started_at"].replace("Z", "+00:00")
    )
    drifted_draft["response_artifact"]["draft_created_at"] = (started + timedelta(seconds=1)).isoformat()
    drifted_draft_path = tmpdir / "drifted-response-draft.json"
    drifted_draft_path.write_text(json.dumps(drifted_draft, indent=2) + "\n", encoding="utf-8")
    drifted_output = tmpdir / "drifted-frozen-response.json"
    drifted_finalize = subprocess.run(
        [
            sys.executable,
            "-S",
            RESPONSE_PREP_TOOL_REL,
            "finalize",
            "--draft",
            str(drifted_draft_path),
            "--bundle-file",
            str(ROOT / BUNDLE_REL),
            "--exposure-notes",
            "synthetic checker provenance-drift canary",
            "--attest-clean-preanswer",
            "--out",
            str(drifted_output),
        ],
        cwd=responder_kit_root,
        env={**dict(os.environ), "PYTHONDONTWRITEBYTECODE": "1"},
        text=True,
        capture_output=True,
    )
    if drifted_finalize.returncode == 0 or "draft_created_at must equal" not in (drifted_finalize.stderr + drifted_finalize.stdout):
        raise SystemExit("responder helper admitted response-artifact start-time drift")

    hidden_field_draft = copy.deepcopy(response_draft)
    hidden_field_draft["undeclared_hidden_field"] = "must fail closed"
    hidden_field_draft_path = tmpdir / "hidden-field-response-draft.json"
    hidden_field_draft_path.write_text(json.dumps(hidden_field_draft, indent=2) + "\n", encoding="utf-8")
    hidden_field_output = tmpdir / "hidden-field-frozen-response.json"
    hidden_field_finalize = subprocess.run(
        [
            sys.executable, "-S", RESPONSE_PREP_TOOL_REL, "finalize",
            "--draft", str(hidden_field_draft_path),
            "--bundle-file", str(ROOT / BUNDLE_REL),
            "--exposure-notes", "synthetic undeclared-field canary",
            "--attest-clean-preanswer",
            "--out", str(hidden_field_output),
        ],
        cwd=responder_kit_root,
        env={**dict(os.environ), "PYTHONDONTWRITEBYTECODE": "1"},
        text=True,
        capture_output=True,
    )
    if hidden_field_finalize.returncode == 0 or "top-level fields drifted" not in (hidden_field_finalize.stderr + hidden_field_finalize.stdout):
        raise SystemExit("responder helper admitted an undeclared hidden response field")

    response_path = tmpdir / "response.json"
    response_finalize = subprocess.run(
        [
            sys.executable,
            "-S",
            RESPONSE_PREP_TOOL_REL,
            "finalize",
            "--draft",
            str(response_draft_path),
            "--bundle-file",
            str(ROOT / BUNDLE_REL),
            "--exposure-notes",
            "only exact responder bundle before synthetic checker finalization",
            "--attest-clean-preanswer",
            "--out",
            str(response_path),
        ],
        cwd=responder_kit_root,
        env={**dict(os.environ), "PYTHONDONTWRITEBYTECODE": "1"},
        text=True,
        capture_output=True,
    )
    if response_finalize.returncode != 0:
        raise SystemExit("standalone responder-kit finalize failed: " + (response_finalize.stderr or response_finalize.stdout).strip())
    response = json.loads(response_path.read_text(encoding="utf-8"))
    if response.get("response_state") != "completed-clean-response-candidate":
        raise SystemExit("responder helper did not produce the current frozen response state")
    if response.get("response_artifact", {}).get("immutable_after_finalize") is not True:
        raise SystemExit("responder helper did not mark its output immutable")
    if stat.S_IMODE(response_path.stat().st_mode) & 0o222:
        raise SystemExit("responder helper left its finalized response writable")
    if response["response_artifact"]["finalized_at"] != response["responder_stage"]["run_completed_at"]:
        raise SystemExit("responder helper did not bind finalization time to run completion")

    overwrite_finalize = subprocess.run(
        [
            sys.executable,
            "-S",
            RESPONSE_PREP_TOOL_REL,
            "finalize",
            "--draft",
            str(response_draft_path),
            "--bundle-file",
            str(ROOT / BUNDLE_REL),
            "--exposure-notes",
            "synthetic checker overwrite canary",
            "--attest-clean-preanswer",
            "--out",
            str(response_path),
        ],
        cwd=responder_kit_root,
        env={**dict(os.environ), "PYTHONDONTWRITEBYTECODE": "1"},
        text=True,
        capture_output=True,
    )
    if overwrite_finalize.returncode == 0 or "refusing to overwrite" not in (overwrite_finalize.stderr + overwrite_finalize.stdout):
        raise SystemExit("responder finalizer did not protect an existing frozen artifact")

    # Reproduce the rev0385 execution blocker without changing any artifact
    # other than the responder-local clock observations: a responder machine
    # fifteen minutes ahead of the collector must remain admissible when the
    # exact response bytes are observed and hash-bound downstream.
    response_path.chmod(0o600)
    for container_name, field_name in [
        ("responder_stage", "run_started_at"),
        ("responder_stage", "run_completed_at"),
        ("response_artifact", "draft_created_at"),
        ("response_artifact", "finalized_at"),
    ]:
        original = datetime.fromisoformat(response[container_name][field_name].replace("Z", "+00:00"))
        response[container_name][field_name] = (original + timedelta(minutes=15)).isoformat()
    response_path.write_text(json.dumps(response, indent=2) + "\n", encoding="utf-8")
    response_path.chmod(0o400)

    custody_kit_root = tmpdir / "standalone-custody-kit"
    with zipfile.ZipFile(ROOT / CUSTODY_KIT_REL) as zf:
        zf.extractall(custody_kit_root)

    # Custody independently reruns the shared contract and must reject an
    # answer-complete but not-yet-finalized draft.
    unfinalized_evidence = tmpdir / "unfinalized-evidence.json"
    unfinalized_custody = subprocess.run(
        [
            sys.executable,
            "-S",
            CUSTODY_PREP_TOOL_REL,
            str(response_draft_path),
            "--custodian-id",
            "custodian-preanswer-smoke",
            "--pre-response-exposure-notes",
            "only exact responder bundle before response",
            "--attest-clean-preanswer",
            "--out",
            str(unfinalized_evidence),
        ],
        cwd=custody_kit_root,
        env={**dict(os.environ), "PYTHONDONTWRITEBYTECODE": "1"},
        text=True,
        capture_output=True,
    )
    if unfinalized_custody.returncode == 0 or unfinalized_evidence.exists():
        raise SystemExit("custody helper admitted an unfinalized response")
    if "response_state must be completed-clean-response-candidate" not in (unfinalized_custody.stderr + unfinalized_custody.stdout):
        raise SystemExit(
            "unfinalized-response custody canary failed with the wrong boundary: "
            + (unfinalized_custody.stderr + unfinalized_custody.stdout).strip()
        )

    evidence_path = tmpdir / "evidence.json"
    custody_cli = subprocess.run(
        [
            sys.executable,
            "-S",
            CUSTODY_PREP_TOOL_REL,
            str(response_path),
            "--custodian-id",
            "custodian-preanswer-smoke",
            "--pre-response-exposure-notes",
            "only exact responder bundle before response",
            "--attest-clean-preanswer",
            "--out",
            str(evidence_path),
        ],
        cwd=custody_kit_root,
        env={**dict(os.environ), "PYTHONDONTWRITEBYTECODE": "1"},
        text=True,
        capture_output=True,
    )
    if custody_cli.returncode != 0:
        raise SystemExit("standalone custody kit command failed: " + (custody_cli.stderr or custody_cli.stdout).strip())
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if stat.S_IMODE(evidence_path.stat().st_mode) & 0o222:
        raise SystemExit("custody helper left its frozen evidence record writable")
    if evidence.get("response_finalized_at") != response["response_artifact"]["finalized_at"]:
        raise SystemExit("custody helper did not bind the response finalization time")
    custody_att = evidence.get("custodian_attestation", {})
    expected_custody_sources = {
        "response_frozen_at_source": "response.response_artifact.finalized_at",
        "custody_kit_opened_at_source": "local-process-clock-at-custody-helper-start",
        "response_observed_at_source": "local-process-clock-after-finalized-response-validation",
        "custody_record_frozen_at_source": "local-process-clock-before-custody-write",
    }
    for key, expected in expected_custody_sources.items():
        if custody_att.get(key) != expected:
            raise SystemExit(f"custody helper source field drifted: {key}")
    if "scorer_opened_at" in custody_att:
        raise SystemExit("current custody record must not forecast scorer-open time")
    if any(key in evidence for key in ["scorer_intake_surface", "scorer_intake_sha256"]):
        raise SystemExit("current custody record must not bind unopened scorer material")
    remote_finalized = datetime.fromisoformat(response["response_artifact"]["finalized_at"].replace("Z", "+00:00"))
    local_custody_frozen = datetime.fromisoformat(custody_att["custody_record_frozen_at"].replace("Z", "+00:00"))
    if remote_finalized <= local_custody_frozen:
        raise SystemExit("clock-skew positive canary did not place responder clock ahead of custodian clock")
    if evidence.get("required_prerequisite_labels") != [] or evidence.get("prerequisite_artifacts") != []:
        raise SystemExit("conventional custody path must require no isolated-pilot prerequisite receipts")

    missing_attestation = subprocess.run(
        [
            sys.executable,
            "-S",
            CUSTODY_PREP_TOOL_REL,
            str(response_path),
            "--custodian-id",
            "custodian-preanswer-smoke",
            "--pre-response-exposure-notes",
            "only exact responder bundle before response",
            "--out",
            str(tmpdir / "unattested-evidence.json"),
        ],
        cwd=custody_kit_root,
        env={**dict(os.environ), "PYTHONDONTWRITEBYTECODE": "1"},
        text=True,
        capture_output=True,
    )
    if missing_attestation.returncode == 0 or "--attest-clean-preanswer is required" not in (missing_attestation.stderr + missing_attestation.stdout):
        raise SystemExit("custody helper admitted an implicit clean-preanswer attestation")

    kit_root = tmpdir / "standalone-scorer-kit"
    with zipfile.ZipFile(ROOT / SCORER_KIT_REL) as zf:
        zf.extractall(kit_root)

    # Reproduce the rev0381 fail-late defect: score-sheet initialization must
    # reject a byte-bound custody file whose complete custody contract is
    # invalid, rather than consuming scorer effort and deferring rejection to
    # the final scorer.
    invalid_custody = copy.deepcopy(evidence)
    invalid_custody["custodian_attestation"]["custodian_id"] = invalid_custody["custodian_attestation"]["responder_id"]
    invalid_custody["custodian_attestation"]["custodian_is_distinct_from_responder"] = False
    invalid_custody_path = tmpdir / "invalid-before-score-init-custody.json"
    invalid_custody_path.write_text(json.dumps(invalid_custody, indent=2) + "\n", encoding="utf-8")
    invalid_score_draft = tmpdir / "invalid-before-score-init-draft.json"
    invalid_score_init = subprocess.run(
        [
            sys.executable,
            "-S",
            SCORE_SHEET_PREP_TOOL_REL,
            "init",
            str(response_path),
            str(invalid_custody_path),
            "--scorer-id",
            "scorer-preanswer-smoke",
            "--out",
            str(invalid_score_draft),
        ],
        cwd=kit_root,
        env={**dict(os.environ), "PYTHONDONTWRITEBYTECODE": "1"},
        text=True,
        capture_output=True,
    )
    invalid_score_text = invalid_score_init.stderr + invalid_score_init.stdout
    if invalid_score_init.returncode == 0 or invalid_score_draft.exists():
        raise SystemExit("score-sheet init admitted a self-custodied record and deferred rejection")
    if "custodian_is_distinct_from_responder" not in invalid_score_text and "custodian_id must differ" not in invalid_score_text:
        raise SystemExit(
            "fail-before-score-init custody canary failed at the wrong boundary: "
            + invalid_score_text.strip()
        )

    score_draft_path = tmpdir / "score-draft.json"
    score_init = subprocess.run(
        [
            sys.executable,
            "-S",
            SCORE_SHEET_PREP_TOOL_REL,
            "init",
            str(response_path),
            str(evidence_path),
            "--scorer-id",
            "scorer-preanswer-smoke",
            "--out",
            str(score_draft_path),
        ],
        cwd=kit_root,
        env={**dict(os.environ), "PYTHONDONTWRITEBYTECODE": "1"},
        text=True,
        capture_output=True,
    )
    if score_init.returncode != 0:
        raise SystemExit("standalone scorer-kit score-sheet init failed: " + (score_init.stderr or score_init.stdout).strip())
    score_draft = json.loads(score_draft_path.read_text(encoding="utf-8"))
    if score_draft.get("response_preparation_contract_version") != "responder-finalize-v1":
        raise SystemExit("score-sheet init did not preserve the response contract")
    if score_draft.get("scorer_attestation", {}).get("scorer_kit_opened_at_source") != "local-process-clock-at-score-sheet-init":
        raise SystemExit("score-sheet init did not record its helper clock source")
    manual_rows = {
        "packet-alpha": (4, "synthetic sham/decoy calibration row"),
        "packet-bravo": (17, "synthetic compact-cue calibration row"),
        "packet-charlie": (2, "synthetic no-archive abstention calibration row"),
        "packet-delta": (16, "synthetic full-trace calibration row"),
    }
    for row in score_draft["manual_metric_scores"]:
        label = row["label"]
        total, notes = manual_rows[label]
        row["metric_scores"] = score_map(total)
        row["metric_rationales"] = rationale_map(label)
        row["notes"] = notes
    score_draft_path.write_text(json.dumps(score_draft, indent=2) + "\n", encoding="utf-8")

    score_sheet_path = tmpdir / "score-sheet.json"
    score_finalize = subprocess.run(
        [
            sys.executable,
            "-S",
            SCORE_SHEET_PREP_TOOL_REL,
            "finalize",
            str(response_path),
            str(evidence_path),
            "--scorer-id",
            "scorer-preanswer-smoke",
            "--draft",
            str(score_draft_path),
            "--scorer-notes",
            "synthetic checker scoring used only frozen response, custody record, and current scorer kit",
            "--attest-separated-scoring",
            "--out",
            str(score_sheet_path),
        ],
        cwd=kit_root,
        env={**dict(os.environ), "PYTHONDONTWRITEBYTECODE": "1"},
        text=True,
        capture_output=True,
    )
    if score_finalize.returncode != 0:
        raise SystemExit("standalone scorer-kit score-sheet finalize failed: " + (score_finalize.stderr or score_finalize.stdout).strip())
    sheet = json.loads(score_sheet_path.read_text(encoding="utf-8"))
    if stat.S_IMODE(score_sheet_path.stat().st_mode) & 0o222:
        raise SystemExit("score-sheet helper left its finalized score sheet writable")
    if sheet.get("scorer_attestation", {}).get("scored_at_source") != "local-process-clock-at-score-sheet-finalize":
        raise SystemExit("score-sheet finalize did not record its helper clock source")
    summary = validate_response_file(
        response_path,
        scorer,
        scorer_intake=SCORER_REL,
        evidence_record=evidence,
        evidence_record_file=evidence_path,
        score_sheet=sheet,
        score_sheet_file=score_sheet_path,
    )
    decision = summary.get("compact_gate_decision", {})
    if summary.get("external_response_evidence") is not True or decision.get("decision_state") != "support-compact-cue-for-bounded-slice":
        raise SystemExit(f"positive preanswer synthetic path did not reach bounded-support decision: {decision}")
    if decision.get("global_compact_gate_confirmed") is not False or decision.get("bounded_semantic_support") is not True:
        raise SystemExit("co-visible trace-excerpt path must support only the bounded semantic slice")
    if summary.get("operator_cost_minutes_by_label") != {"packet-alpha": 1, "packet-bravo": 2, "packet-charlie": 1, "packet-delta": 5}:
        raise SystemExit("positive preanswer path did not preserve per-packet operator cost")
    if summary.get("response_contract_state") != "valid" or summary.get("response_preparation_contract_version") != "responder-finalize-v1":
        raise SystemExit("positive preanswer path did not validate the current response contract")
    if summary.get("response_finalized_at") != response["response_artifact"]["finalized_at"]:
        raise SystemExit("positive preanswer path did not preserve response finalization time")
    if summary.get("score_sheet_chronology_state") != "valid":
        raise SystemExit("positive preanswer synthetic path did not validate score-sheet chronology")
    if summary.get("cross_operator_time_ordering") != "exact-artifact-hash-chain-not-wall-clock":
        raise SystemExit("positive preanswer path did not expose the causal artifact ordering basis")
    if summary.get("custody_record_observed_at") != sheet["scorer_attestation"]["custody_record_observed_at"]:
        raise SystemExit("positive preanswer path did not preserve scorer-local custody observation")
    if summary.get("custody_contract_version") != CURRENT_CUSTODY_CONTRACT:
        raise SystemExit("positive preanswer path did not preserve current custody contract")
    if summary.get("custody_record_frozen_at") != evidence["custodian_attestation"]["custody_record_frozen_at"]:
        raise SystemExit("positive preanswer path did not preserve custody freeze time")
    if summary.get("scorer_kit_opened_at") != sheet["scorer_attestation"]["scorer_kit_opened_at"]:
        raise SystemExit("positive preanswer path did not preserve scorer-kit open time")
    if summary.get("score_sheet_sha256") != hashlib.sha256(score_sheet_path.read_bytes()).hexdigest():
        raise SystemExit("positive preanswer path did not emit the actual score-sheet file hash")
    if summary.get("custody_evidence_record_sha256") != hashlib.sha256(evidence_path.read_bytes()).hexdigest():
        raise SystemExit("positive preanswer path did not bind the completed custody-record file hash")
    if summary.get("distinct_scorer_from_responder") is not True:
        raise SystemExit("positive preanswer path did not prove scorer/responder separation")

    cli_summary_path = tmpdir / "standalone-score-summary.json"
    cli = subprocess.run(
        [
            sys.executable,
            "-S",
            SCORE_TOOL_REL,
            "--scorer-intake",
            SCORER_REL,
            "--evidence-record",
            str(evidence_path),
            "--score-sheet",
            str(score_sheet_path),
            "--summary-out",
            str(cli_summary_path),
            str(response_path),
        ],
        cwd=kit_root,
        env={**dict(os.environ), "PYTHONDONTWRITEBYTECODE": "1"},
        text=True,
        capture_output=True,
    )
    if cli.returncode != 0:
        raise SystemExit("standalone scorer kit command failed: " + (cli.stderr or cli.stdout).strip())
    cli_summary = json.loads(cli_summary_path.read_text(encoding="utf-8"))
    if cli_summary.get("external_response_evidence") is not True:
        raise SystemExit("standalone scorer kit command did not validate the synthetic clean triplet")
    if cli_summary.get("score_sheet_sha256") != hashlib.sha256(score_sheet_path.read_bytes()).hexdigest():
        raise SystemExit("standalone scorer kit did not emit the actual score-sheet hash")

    hidden_custody = copy.deepcopy(evidence)
    hidden_custody["undeclared_hidden_field"] = "must fail closed"
    hidden_custody_path = tmpdir / "hidden-custody.json"
    hidden_custody_path.write_text(json.dumps(hidden_custody, indent=2) + "\n", encoding="utf-8")
    hidden_custody_sheet = copy.deepcopy(sheet)
    hidden_custody_sheet["custody_evidence_record_sha256"] = hashlib.sha256(hidden_custody_path.read_bytes()).hexdigest()
    hidden_custody_sheet_path = tmpdir / "hidden-custody-score-sheet.json"
    hidden_custody_sheet_path.write_text(json.dumps(hidden_custody_sheet, indent=2) + "\n", encoding="utf-8")
    try:
        validate_response_file(
            response_path, scorer, scorer_intake=SCORER_REL,
            evidence_record=hidden_custody, evidence_record_file=hidden_custody_path,
            score_sheet=hidden_custody_sheet, score_sheet_file=hidden_custody_sheet_path,
        )
    except ResponseIntakeError as exc:
        if "custody evidence top-level fields drifted" not in str(exc):
            raise SystemExit(f"undeclared custody-field canary failed with wrong error: {exc}") from exc
    else:
        raise SystemExit("custody evidence with an undeclared hidden field was admitted")

    hidden_score_sheet = copy.deepcopy(sheet)
    hidden_score_sheet["undeclared_hidden_field"] = "must fail closed"
    hidden_score_sheet_path = tmpdir / "hidden-score-sheet.json"
    hidden_score_sheet_path.write_text(json.dumps(hidden_score_sheet, indent=2) + "\n", encoding="utf-8")
    try:
        validate_response_file(
            response_path, scorer, scorer_intake=SCORER_REL,
            evidence_record=evidence, evidence_record_file=evidence_path,
            score_sheet=hidden_score_sheet, score_sheet_file=hidden_score_sheet_path,
        )
    except ResponseIntakeError as exc:
        if "score sheet top-level fields drifted" not in str(exc):
            raise SystemExit(f"undeclared score-sheet-field canary failed with wrong error: {exc}") from exc
    else:
        raise SystemExit("score sheet with an undeclared hidden field was admitted")

    leak_evidence = copy.deepcopy(evidence)
    leak_evidence["custodian_attestation"]["pre_response_materials_given"] = [BUNDLE_REL, OLD_SUBMISSION_KIT_REL]
    leak_evidence_path = tmpdir / "leak-evidence.json"
    leak_evidence_path.write_text(json.dumps(leak_evidence, indent=2) + "\n", encoding="utf-8")
    leak_sheet = copy.deepcopy(sheet)
    leak_sheet["custody_evidence_record_sha256"] = hashlib.sha256(leak_evidence_path.read_bytes()).hexdigest()
    leak_sheet_path = tmpdir / "leak-score-sheet.json"
    leak_sheet_path.write_text(json.dumps(leak_sheet, indent=2) + "\n", encoding="utf-8")
    try:
        validate_response_file(response_path, scorer, scorer_intake=SCORER_REL, evidence_record=leak_evidence, evidence_record_file=leak_evidence_path, score_sheet=leak_sheet, score_sheet_file=leak_sheet_path)
    except ResponseIntakeError as exc:
        if "exactly match allowed" not in str(exc):
            raise SystemExit(f"preanswer leak negative canary failed with wrong error: {exc}") from exc
    else:
        raise SystemExit("preanswer leak negative canary was admitted")

    token_evidence = copy.deepcopy(evidence)
    token_evidence["custodian_attestation"]["pre_response_materials_given"] = f"{BUNDLE_REL} plus score sheet"
    token_evidence_path = tmpdir / "token-evidence.json"
    token_evidence_path.write_text(json.dumps(token_evidence, indent=2) + "\n", encoding="utf-8")
    token_sheet = copy.deepcopy(sheet)
    token_sheet["custody_evidence_record_sha256"] = hashlib.sha256(token_evidence_path.read_bytes()).hexdigest()
    token_sheet_path = tmpdir / "token-score-sheet.json"
    token_sheet_path.write_text(json.dumps(token_sheet, indent=2) + "\n", encoding="utf-8")
    try:
        validate_response_file(response_path, scorer, scorer_intake=SCORER_REL, evidence_record=token_evidence, evidence_record_file=token_evidence_path, score_sheet=token_sheet, score_sheet_file=token_sheet_path)
    except ResponseIntakeError as exc:
        if "exactly match allowed" not in str(exc) and "forbidden token" not in str(exc):
            raise SystemExit(f"forbidden token negative canary failed with wrong error: {exc}") from exc
    else:
        raise SystemExit("forbidden preanswer token negative canary was admitted")

    early_observation_sheet = copy.deepcopy(sheet)
    scorer_opened_dt = datetime.fromisoformat(
        sheet["scorer_attestation"]["scorer_kit_opened_at"].replace("Z", "+00:00")
    )
    early_observation_sheet["scorer_attestation"]["custody_record_observed_at"] = (
        scorer_opened_dt - timedelta(seconds=1)
    ).isoformat()
    early_observation_sheet_path = tmpdir / "early-custody-observation-score-sheet.json"
    early_observation_sheet_path.write_text(json.dumps(early_observation_sheet, indent=2) + "\n", encoding="utf-8")
    try:
        validate_response_file(response_path, scorer, scorer_intake=SCORER_REL, evidence_record=evidence, evidence_record_file=evidence_path, score_sheet=early_observation_sheet, score_sheet_file=early_observation_sheet_path)
    except ResponseIntakeError as exc:
        if "custody_record_observed_at precedes scorer_kit_opened_at" not in str(exc):
            raise SystemExit(f"scorer-local observation canary failed with wrong error: {exc}") from exc
    else:
        raise SystemExit("scorer-local custody observation before scorer-kit opening was admitted")

    inverted_sheet = copy.deepcopy(sheet)
    custody_observed_dt = datetime.fromisoformat(
        sheet["scorer_attestation"]["custody_record_observed_at"].replace("Z", "+00:00")
    )
    inverted_sheet["scorer_attestation"]["scored_at"] = (
        custody_observed_dt - timedelta(seconds=1)
    ).isoformat()
    inverted_sheet_path = tmpdir / "inverted-score-sheet.json"
    inverted_sheet_path.write_text(json.dumps(inverted_sheet, indent=2) + "\n", encoding="utf-8")
    try:
        validate_response_file(response_path, scorer, scorer_intake=SCORER_REL, evidence_record=evidence, evidence_record_file=evidence_path, score_sheet=inverted_sheet, score_sheet_file=inverted_sheet_path)
    except ResponseIntakeError as exc:
        if "scored_at precedes custody_record_observed_at" not in str(exc):
            raise SystemExit(f"score-time negative canary failed with wrong error: {exc}") from exc
    else:
        raise SystemExit("scorer-local score-time inversion negative canary was admitted")


    legacy_field_evidence = copy.deepcopy(evidence)
    legacy_field_evidence["scorer_intake_surface"] = SCORER_REL
    legacy_field_evidence["custodian_attestation"]["scorer_opened_at"] = "2026-06-16T09:22:00-04:00"
    legacy_field_evidence_path = tmpdir / "legacy-field-evidence.json"
    legacy_field_evidence_path.write_text(json.dumps(legacy_field_evidence, indent=2) + "\n", encoding="utf-8")
    legacy_field_sheet = copy.deepcopy(sheet)
    legacy_field_sheet["custody_evidence_record_sha256"] = hashlib.sha256(legacy_field_evidence_path.read_bytes()).hexdigest()
    legacy_field_sheet_path = tmpdir / "legacy-field-score-sheet.json"
    legacy_field_sheet_path.write_text(json.dumps(legacy_field_sheet, indent=2) + "\n", encoding="utf-8")
    try:
        validate_response_file(response_path, scorer, scorer_intake=SCORER_REL, evidence_record=legacy_field_evidence, evidence_record_file=legacy_field_evidence_path, score_sheet=legacy_field_sheet, score_sheet_file=legacy_field_sheet_path)
    except ResponseIntakeError as exc:
        if "current custody evidence must not contain scorer-stage field" not in str(exc):
            raise SystemExit(f"legacy-field custody negative canary failed with wrong error: {exc}") from exc
    else:
        raise SystemExit("current custody record with legacy scorer-stage fields was admitted")

    self_scored_sheet = copy.deepcopy(sheet)
    self_scored_sheet["scorer_attestation"]["scorer_id"] = "responder-preanswer-smoke"
    self_scored_sheet_path = tmpdir / "self-scored-sheet.json"
    self_scored_sheet_path.write_text(json.dumps(self_scored_sheet, indent=2) + "\n", encoding="utf-8")
    try:
        validate_response_file(response_path, scorer, scorer_intake=SCORER_REL, evidence_record=evidence, evidence_record_file=evidence_path, score_sheet=self_scored_sheet, score_sheet_file=self_scored_sheet_path)
    except ResponseIntakeError as exc:
        if "responder self-scoring is not admissible" not in str(exc):
            raise SystemExit(f"self-scoring negative canary failed with wrong error: {exc}") from exc
    else:
        raise SystemExit("responder self-scoring negative canary was admitted")

    unrationalized_sheet = copy.deepcopy(sheet)
    unrationalized_sheet["manual_metric_scores"][0]["metric_rationales"].pop(metrics[0])
    unrationalized_sheet_path = tmpdir / "unrationalized-sheet.json"
    unrationalized_sheet_path.write_text(json.dumps(unrationalized_sheet, indent=2) + "\n", encoding="utf-8")
    try:
        validate_response_file(response_path, scorer, scorer_intake=SCORER_REL, evidence_record=evidence, evidence_record_file=evidence_path, score_sheet=unrationalized_sheet, score_sheet_file=unrationalized_sheet_path)
    except ResponseIntakeError as exc:
        if "metric_rationales for every metric" not in str(exc):
            raise SystemExit(f"missing-rationale negative canary failed with wrong error: {exc}") from exc
    else:
        raise SystemExit("score sheet with missing metric rationale was admitted")

    boolean_sheet = copy.deepcopy(sheet)
    boolean_sheet["manual_metric_scores"][0]["metric_scores"][metrics[0]] = True
    boolean_sheet_path = tmpdir / "boolean-score-sheet.json"
    boolean_sheet_path.write_text(json.dumps(boolean_sheet, indent=2) + "\n", encoding="utf-8")
    try:
        validate_response_file(response_path, scorer, scorer_intake=SCORER_REL, evidence_record=evidence, evidence_record_file=evidence_path, score_sheet=boolean_sheet, score_sheet_file=boolean_sheet_path)
    except ResponseIntakeError as exc:
        if "numeric, not boolean" not in str(exc):
            raise SystemExit(f"boolean-score negative canary failed with wrong error: {exc}") from exc
    else:
        raise SystemExit("boolean metric score was admitted")

    missing_cost_response = copy.deepcopy(response)
    missing_cost_response["responder_stage"]["packet_answers"][0]["operator_cost_minutes"] = None
    missing_cost_path = tmpdir / "missing-packet-cost-response.json"
    missing_cost_path.write_text(json.dumps(missing_cost_response, indent=2) + "\n", encoding="utf-8")
    try:
        validate_response_file(missing_cost_path, scorer, scorer_intake=SCORER_REL, evidence_record=evidence, evidence_record_file=evidence_path, score_sheet=sheet, score_sheet_file=score_sheet_path)
    except ResponseIntakeError as exc:
        if "operator_cost_minutes must be a positive finite number" not in str(exc):
            raise SystemExit(f"missing packet-cost negative canary failed with wrong error: {exc}") from exc
    else:
        raise SystemExit("response without one packet operator cost was admitted")

    mismatch_response = copy.deepcopy(response)
    mismatch_response["responder_stage"]["operator_cost_minutes"] = 8
    mismatch_path = tmpdir / "packet-cost-mismatch-response.json"
    mismatch_path.write_text(json.dumps(mismatch_response, indent=2) + "\n", encoding="utf-8")
    try:
        validate_response_file(mismatch_path, scorer, scorer_intake=SCORER_REL, evidence_record=evidence, evidence_record_file=evidence_path, score_sheet=sheet, score_sheet_file=score_sheet_path)
    except ResponseIntakeError as exc:
        if "must equal the sum of packet operator costs" not in str(exc):
            raise SystemExit(f"packet-cost sum negative canary failed with wrong error: {exc}") from exc
    else:
        raise SystemExit("response with packet/total cost mismatch was admitted")

    cost_disadvantage_summary = copy.deepcopy(summary)
    cost_disadvantage_summary["operator_cost_minutes_by_label"]["packet-bravo"] = 6
    cost_disadvantage_summary["operator_cost_minutes_by_label"]["packet-delta"] = 1
    cost_decision = decide_compact_gate(cost_disadvantage_summary, scorer)
    if cost_decision.get("decision_state") != "narrow-compact-cost-disadvantage":
        raise SystemExit(f"compact cost disadvantage did not narrow the gate: {cost_decision}")

    duplicate_sheet_path = tmpdir / "duplicate-key-score-sheet.json"
    duplicate_text = score_sheet_path.read_text(encoding="utf-8").replace(
        '  "record_type": "external-replay-score-sheet",',
        '  "record_type": "external-replay-score-sheet",\n  "record_type": "external-replay-score-sheet",',
        1,
    )
    duplicate_sheet_path.write_text(duplicate_text, encoding="utf-8")
    try:
        validate_response_file(
            response_path,
            scorer,
            scorer_intake=SCORER_REL,
            evidence_record=evidence,
            evidence_record_file=evidence_path,
            score_sheet_file=duplicate_sheet_path,
        )
    except ResponseIntakeError as exc:
        if "duplicate JSON object key: record_type" not in str(exc):
            raise SystemExit(f"duplicate-key negative canary failed with wrong error: {exc}") from exc
    else:
        raise SystemExit("bound score sheet with duplicate JSON object key was admitted")

    split_evidence_file = copy.deepcopy(evidence)
    split_evidence_file["id"] = "different-custody-file"
    split_evidence_path = tmpdir / "split-evidence.json"
    split_evidence_path.write_text(json.dumps(split_evidence_file, indent=2) + "\n", encoding="utf-8")
    split_sheet = copy.deepcopy(sheet)
    split_sheet["custody_evidence_record_sha256"] = hashlib.sha256(split_evidence_path.read_bytes()).hexdigest()
    split_sheet_path = tmpdir / "split-score-sheet.json"
    split_sheet_path.write_text(json.dumps(split_sheet, indent=2) + "\n", encoding="utf-8")
    try:
        validate_response_file(response_path, scorer, scorer_intake=SCORER_REL, evidence_record=evidence, evidence_record_file=split_evidence_path, score_sheet=split_sheet, score_sheet_file=split_sheet_path)
    except ResponseIntakeError as exc:
        if "custody evidence record object does not match bound file contents" not in str(exc):
            raise SystemExit(f"split-brain custody negative canary failed with wrong error: {exc}") from exc
    else:
        raise SystemExit("split-brain custody object/file pair was admitted")

print("check_priority_zero_preanswer_material_clamp_contract: OK")
