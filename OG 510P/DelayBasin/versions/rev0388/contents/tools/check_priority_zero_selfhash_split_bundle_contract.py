"""Validate historical rev0373 selfhash-split Priority-0 handoff evidence.

This checker must not remain current-tail authority after rev0374; it preserves
the rev0373 self-hash repair as historical evidence while allowing the live
frontier to advance to the pre-answer material clamp.
"""
from __future__ import annotations

import copy
import hashlib
import json
import pathlib
import re
import tempfile
import zipfile

from priority_zero_assay_lib import (
    assert_metric_contract,
    assert_negative_canaries,
    assert_scorecard_integrity,
    assert_surface_exists,
    assert_variant_score_integrity,
    file_sha256,
    load_json,
)
from priority_zero_handoff_bundle_lib import assert_no_embedded_bundle_hash_claims
from score_priority_zero_external_replay_response import (
    ResponseIntakeError,
    resolve_default_scorer_intake,
    validate_response_file,
)

ROOT = pathlib.Path(__file__).resolve().parents[1]
ASSAY_REL = "assays/priority-zero-responder-bundle-selfhash-split-2026-06-16.json"
DOC_REL = "docs/40-session/priority-zero-responder-bundle-selfhash-split-2026-06-16.md"
CHECKER_REL = "tools/check_priority_zero_selfhash_split_bundle_contract.py"
SCORER_REL = "assays/priority-zero-selfhash-split-external-replay-scorer-intake-2026-06-16.json"
RESPONDER_REL = "assays/priority-zero-selfhash-split-external-replay-responder-only-2026-06-16.json"
TEMPLATE_REL = "assays/priority-zero-selfhash-split-external-replay-response-template-2026-06-16.json"
EVIDENCE_TEMPLATE_REL = "assays/priority-zero-selfhash-split-clean-external-response-evidence-record-template-2026-06-16.json"
SCORE_SHEET_TEMPLATE_REL = "assays/priority-zero-selfhash-split-external-replay-score-sheet-template-2026-06-16.json"
RESPONDER_README_REL = "handoffs/priority-zero-selfhash-split-external-replay-responder-readme-2026-06-16.md"
CUSTODY_README_REL = "handoffs/priority-zero-selfhash-split-clean-response-custody-readme-2026-06-16.md"
SCORER_README_REL = "handoffs/priority-zero-selfhash-split-external-replay-scorer-readme-2026-06-16.md"
BUNDLE_REL = "handoffs/priority-zero-selfhash-split-external-replay-responder-bundle-2026-06-16.zip"
SUBMISSION_KIT_REL = "handoffs/priority-zero-selfhash-split-external-replay-submission-kit-2026-06-16.zip"
SCORER_KIT_REL = "handoffs/priority-zero-selfhash-split-external-replay-scorer-kit-2026-06-16.zip"
MANIFEST_REL = "handoffs/priority-zero-selfhash-split-external-replay-handoff-manifest-2026-06-16.json"
SCORE_TOOL_REL = "tools/score_priority_zero_external_replay_response.py"
BUNDLE_LIB_REL = "tools/priority_zero_handoff_bundle_lib.py"
BUILDER_REL = "tools/build_priority_zero_selfhash_split_handoff_bundle.py"
VALIDATION_LIB_REL = "tools/validation_toolchain_lib.py"
MAKEFILE_REL = "Makefile"
HISTORICAL_SCORE_SPLIT_CHECKER_REL = "tools/check_priority_zero_frozen_response_score_sheet_contract.py"
OLD_TEMPLATE_REL = "assays/priority-zero-score-separated-external-replay-response-template-2026-06-16.json"
OLD_BUNDLE_REL = "handoffs/priority-zero-score-separated-external-replay-responder-bundle-2026-06-16.zip"

receipt = load_json("REVISION-RECEIPT.json")
assay = load_json(ASSAY_REL)
scorer = load_json(SCORER_REL)
manifest = load_json(MANIFEST_REL)
frontier = load_json("FRONTIER-BACKLOG.json")
ledger = load_json("SELF-SUFFICIENCY-LEDGER.json")

def _sha_path(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

current_revision = receipt.get("revision")
if assay.get("revision") != "rev0373":
    raise SystemExit("selfhash-split assay must remain recorded as rev0373 historical evidence")
if assay.get("resolved_question") != "OQ-0264" or assay.get("next_open_question") != "OQ-0265" or assay.get("resolution_id") != "RS-0272":
    raise SystemExit("selfhash split assay must preserve the rev0373 OQ-0264 -> OQ-0265 routing")
if current_revision == "rev0373":
    if receipt.get("resolved_question") != "OQ-0264" or receipt.get("next_open_question") != "OQ-0265":
        raise SystemExit("rev0373 receipt must resolve OQ-0264 and open OQ-0265")
    if receipt.get("current_resolution_id") != "RS-0272":
        raise SystemExit("rev0373 receipt must route through RS-0272")
    if resolve_default_scorer_intake(ROOT) != SCORER_REL:
        raise SystemExit("auto:frontier must resolve to the selfhash-split scorer at rev0373")
    if frontier.get("items", [{}])[0].get("id") != "OQ-0265" or frontier.get("queue_head") != "OQ-0265":
        raise SystemExit("rev0373 frontier backlog must route to OQ-0265")
    if SCORER_REL not in frontier.get("items", [{}])[0].get("fanout", []):
        raise SystemExit("OQ-0265 fanout must include selfhash-split scorer intake")
else:
    if resolve_default_scorer_intake(ROOT) == SCORER_REL:
        raise SystemExit("historical rev0373 selfhash scorer must not remain current-tail authority after rev0374")

for rel in [
    ASSAY_REL,
    DOC_REL,
    CHECKER_REL,
    SCORER_REL,
    RESPONDER_REL,
    TEMPLATE_REL,
    EVIDENCE_TEMPLATE_REL,
    SCORE_SHEET_TEMPLATE_REL,
    RESPONDER_README_REL,
    CUSTODY_README_REL,
    SCORER_README_REL,
    BUNDLE_REL,
    SUBMISSION_KIT_REL,
    SCORER_KIT_REL,
    MANIFEST_REL,
    SCORE_TOOL_REL,
    BUNDLE_LIB_REL,
    BUILDER_REL,
    VALIDATION_LIB_REL,
    MAKEFILE_REL,
    HISTORICAL_SCORE_SPLIT_CHECKER_REL,
    OLD_TEMPLATE_REL,
    OLD_BUNDLE_REL,
]:
    assert_surface_exists(rel)

if current_revision == "rev0373":
    for rel in [ASSAY_REL, DOC_REL, CHECKER_REL, SCORER_REL, TEMPLATE_REL, SCORE_SHEET_TEMPLATE_REL, BUNDLE_REL, SUBMISSION_KIT_REL, SCORER_KIT_REL, SCORE_TOOL_REL, BUNDLE_LIB_REL, BUILDER_REL, MAKEFILE_REL]:
        if rel not in receipt.get("canon_additions", []):
            raise SystemExit(f"selfhash-split surface must be current canon addition at rev0373: {rel}")

for token in ["self-reference bug", "expected bundle hash is absent", "OQ-0265", "score-external-response"]:
    if token not in (ROOT / DOC_REL).read_text(encoding="utf-8"):
        raise SystemExit(f"selfhash split doc missing token: {token}")
score_tool_text = (ROOT / SCORE_TOOL_REL).read_text(encoding="utf-8")
if "score sheet must name custody_evidence_record_sha256" not in score_tool_text:
    raise SystemExit("score tool must require score-sheet custody evidence hash")
if "assert_no_embedded_bundle_hash_claims" not in (ROOT / BUNDLE_LIB_REL).read_text(encoding="utf-8"):
    raise SystemExit("handoff bundle lib must expose self-hash claim guard")
if CHECKER_REL.split("/", 1)[1] not in (ROOT / VALIDATION_LIB_REL).read_text(encoding="utf-8"):
    raise SystemExit("selfhash-split checker must be in validation toolchain")
make_text = (ROOT / MAKEFILE_REL).read_text(encoding="utf-8")
if "SCORE_SHEET" not in make_text or "--score-sheet" not in make_text:
    raise SystemExit("Makefile score-external-response must pass SCORE_SHEET through to scorer")

old_template = load_json(OLD_TEMPLATE_REL)
if old_template.get("responder_bundle_sha256") == file_sha256(OLD_BUNDLE_REL):
    raise SystemExit("historical self-hash drift observation disappeared; rev0373 defect basis must be explicit")

# Responder-visible files may ask the responder to compute the bundle hash, but
# they must not embed a concrete expected hash or the actual containing digest.
responder_members = [RESPONDER_REL, TEMPLATE_REL, RESPONDER_README_REL]
assert_no_embedded_bundle_hash_claims(ROOT, responder_members, actual_bundle_sha256=file_sha256(BUNDLE_REL))
for rel in responder_members:
    text = (ROOT / rel).read_text(encoding="utf-8")
    if re.search(r'"responder_bundle_sha256"\s*:\s*"[0-9a-f]{64}"', text):
        raise SystemExit(f"responder-visible member embeds concrete responder_bundle_sha256: {rel}")
    if file_sha256(BUNDLE_REL) in text:
        raise SystemExit(f"responder-visible member embeds actual responder bundle digest: {rel}")
if "responder_bundle_sha256" in load_json(TEMPLATE_REL):
    raise SystemExit("response template must not contain a concrete responder_bundle_sha256 field")

with zipfile.ZipFile(ROOT / BUNDLE_REL) as zf:
    names = sorted(zf.namelist())
    expected = sorted(responder_members)
    if names != expected:
        raise SystemExit(f"selfhash responder bundle contents drifted: {names}")
    bundle_text = "\n".join(zf.read(name).decode("utf-8", errors="ignore") for name in names)
    for token in [
        "answer_key",
        "true_variant",
        "expected_score",
        "priority-zero-selfhash-split-external-replay-scorer-intake",
        file_sha256(BUNDLE_REL),
    ]:
        if token in bundle_text:
            raise SystemExit(f"responder bundle leaked scorer or self-hash token: {token}")
with zipfile.ZipFile(ROOT / SUBMISSION_KIT_REL) as zf:
    if sorted(zf.namelist()) != sorted([BUNDLE_REL, EVIDENCE_TEMPLATE_REL, CUSTODY_README_REL]):
        raise SystemExit("selfhash submission kit contents drifted")
with zipfile.ZipFile(ROOT / SCORER_KIT_REL) as zf:
    expected = sorted([SCORER_REL, SCORE_SHEET_TEMPLATE_REL, SCORE_TOOL_REL, "tools/priority_zero_assay_lib.py", "tools/priority_zero_external_replay_decision_lib.py", "tools/priority_zero_custody_timeline_lib.py", SCORER_README_REL])
    if sorted(zf.namelist()) != expected:
        raise SystemExit("selfhash scorer kit contents drifted")

for key, rel in [
    ("responder_only_sha256", RESPONDER_REL),
    ("response_template_sha256", TEMPLATE_REL),
    ("responder_bundle_sha256", BUNDLE_REL),
    ("submission_kit_sha256", SUBMISSION_KIT_REL),
    ("evidence_record_template_sha256", EVIDENCE_TEMPLATE_REL),
    ("score_sheet_template_sha256", SCORE_SHEET_TEMPLATE_REL),
]:
    if scorer.get(key) != file_sha256(rel):
        raise SystemExit(f"selfhash scorer hash drifted for {key}")
for key, rel in [
    ("responder_bundle_sha256", BUNDLE_REL),
    ("submission_kit_sha256", SUBMISSION_KIT_REL),
    ("scorer_kit_sha256", SCORER_KIT_REL),
    ("score_sheet_template_sha256", SCORE_SHEET_TEMPLATE_REL),
    ("scorer_intake_sha256", SCORER_REL),
    ("response_template_sha256", TEMPLATE_REL),
    ("evidence_record_template_sha256", EVIDENCE_TEMPLATE_REL),
]:
    if manifest.get(key) != file_sha256(rel):
        raise SystemExit(f"selfhash manifest hash drifted for {key}")
for row in manifest.get("excluded_from_responder_bundle", []):
    if row.get("path") == MANIFEST_REL:
        if "self-referential" not in row.get("sha256", ""):
            raise SystemExit("manifest self-row must not pretend to be a stable self-hash")
    elif row.get("sha256") != file_sha256(row.get("path", "")):
        raise SystemExit(f"manifest exclusion hash drifted for {row.get('path')}")
if scorer.get("requires_responder_bundle_hash_outside_responder_bundle") is not True:
    raise SystemExit("selfhash scorer must declare external bundle-hash boundary")
if scorer.get("requires_separate_score_sheet") is not True:
    raise SystemExit("selfhash scorer must require separate score sheet")

# Synthetic path smoke: create a frozen response, custody record, and score sheet.
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

with tempfile.TemporaryDirectory(prefix="delaybasin-selfhash-split-") as tmp:
    tmpdir = pathlib.Path(tmp)
    response = copy.deepcopy(load_json(TEMPLATE_REL))
    stage = response["responder_stage"]
    stage.update({
        "responder_id": "responder-selfhash-smoke",
        "run_started_at": "2026-06-16T12:00:00-04:00",
        "run_completed_at": "2026-06-16T12:20:00-04:00",
        "saw_responder_bundle_sha256": file_sha256(BUNDLE_REL),
        "saw_responder_packet_sha256": file_sha256(RESPONDER_REL),
        "no_scorer_key_before_response": True,
        "no_full_archive_before_response": True,
        "no_conversation_context_before_response": True,
        "accidental_exposure_notes": "none observed in synthetic checker smoke",
        "operator_cost_minutes": 9,
    })
    for answer in stage["packet_answers"]:
        for field in ["mission_heart", "oq_routing", "compact_gate_posture", "waste_or_refactor_implicated", "next_safe_action", "abstentions", "uncertainty_or_conflicts"]:
            answer[field] = f"substantive {field} for {answer['label']} in synthetic selfhash split smoke"
    response_path = tmpdir / "frozen-response.json"
    response_path.write_text(json.dumps(response, indent=2) + "\n", encoding="utf-8")
    response_sha = _sha_path(response_path)

    evidence = copy.deepcopy(load_json(EVIDENCE_TEMPLATE_REL))
    evidence.update({
        "id": "synthetic-selfhash-custody-record",
        "evidence_state": "completed-response-frozen-before-scoring",
        "response_file_sha256": response_sha,
        "responder_bundle_sha256": file_sha256(BUNDLE_REL),
        "responder_only_sha256": file_sha256(RESPONDER_REL),
        "response_template_sha256": file_sha256(TEMPLATE_REL),
        "scorer_intake_surface": SCORER_REL,
        "scorer_intake_sha256": file_sha256(SCORER_REL),
    })
    evidence["custodian_attestation"] = {
        "custodian_id": "custodian-selfhash-smoke",
        "responder_id": "responder-selfhash-smoke",
        "response_frozen_at": "2026-06-16T12:21:00-04:00",
        "scorer_opened_at": "2026-06-16T12:22:00-04:00",
        "pre_response_materials_given": BUNDLE_REL,
        "pre_response_exposure_notes": "none observed in synthetic checker smoke",
        "responder_was_given_only_responder_bundle_before_response": True,
        "scorer_intake_opened_only_after_response_frozen": True,
        "full_archive_not_given_before_response": True,
        "conversation_not_shown_before_response": True,
        "answer_key_not_shown_before_response": True,
        "response_hash_recorded_before_scoring": True,
        "custodian_is_distinct_from_responder": True,
    }
    evidence_path = tmpdir / "custody-record.json"
    evidence_path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    evidence_sha = _sha_path(evidence_path)

    sheet = copy.deepcopy(load_json(SCORE_SHEET_TEMPLATE_REL))
    sheet.update({
        "id": "synthetic-selfhash-score-sheet",
        "score_sheet_state": "post-response-manual-score-record",
        "response_file_sha256": response_sha,
        "custody_evidence_record_sha256": evidence_sha,
        "scorer_intake_surface": SCORER_REL,
        "scorer_intake_sha256": file_sha256(SCORER_REL),
        "manual_metric_scores": [
            {"label": "packet-alpha", "metric_scores": score_map(4), "notes": "synthetic sham score"},
            {"label": "packet-bravo", "metric_scores": score_map(17), "notes": "synthetic compact score"},
            {"label": "packet-charlie", "metric_scores": score_map(2), "notes": "synthetic baseline score"},
            {"label": "packet-delta", "metric_scores": score_map(16), "notes": "synthetic full archive score"},
        ],
    })
    sheet["scorer_attestation"] = {
        "scorer_id": "scorer-selfhash-smoke",
        "scored_at": "2026-06-16T12:30:00-04:00",
        "response_was_frozen_before_scoring": True,
        "scorer_intake_opened_after_response_frozen": True,
        "scorer_used_only_frozen_response_and_custody_record": True,
        "no_response_mutation_after_freeze": True,
        "notes": "synthetic checker smoke only; not external evidence",
    }
    summary = validate_response_file(
        response_path,
        scorer,
        scorer_intake=SCORER_REL,
        evidence_record=evidence,
        evidence_record_file=evidence_path,
        score_sheet=sheet,
    )
    if summary.get("manual_score_status") != "complete" or summary.get("manual_score_source") != "separate-score-sheet":
        raise SystemExit("selfhash synthetic path did not use separate score sheet")
    decision = summary.get("compact_gate_decision", {})
    if decision.get("decision_state") != "confirm-compact-default-with-escalation":
        raise SystemExit(f"selfhash synthetic decision drifted: {decision}")

    bad_sheet = copy.deepcopy(sheet)
    bad_sheet.pop("custody_evidence_record_sha256", None)
    try:
        validate_response_file(
            response_path,
            scorer,
            scorer_intake=SCORER_REL,
            evidence_record=evidence,
            evidence_record_file=evidence_path,
            score_sheet=bad_sheet,
        )
    except ResponseIntakeError as exc:
        if "custody_evidence_record_sha256" not in str(exc):
            raise SystemExit(f"missing custody hash canary failed with wrong diagnostic: {exc}") from exc
    else:
        raise SystemExit("score sheet without custody_evidence_record_sha256 must fail closed")

    fake_member = tmpdir / "fake-responder-visible.json"
    fake_member.write_text('{"responder_bundle_sha256":"' + file_sha256(BUNDLE_REL) + '"}\n', encoding="utf-8")
    try:
        assert_no_embedded_bundle_hash_claims(tmpdir, ["fake-responder-visible.json"], actual_bundle_sha256=file_sha256(BUNDLE_REL))
    except SystemExit:
        pass
    else:
        raise SystemExit("embedded bundle hash guard must reject concrete self-hash claims")

assert_metric_contract(assay, required={m for m in [
    "bundle-self-hash-boundary",
    "hash-chain-coherence",
    "responder-bundle-uncontaminated",
    "score-sheet-custody-binding",
    "operator-command-runnability",
    "historical-defect-honesty",
    "clean-response-absence-honesty",
    "successor-routing",
]}, count=8)
variants = assert_variant_score_integrity(assay, required_variants={
    "pre-fix-self-hash-drift",
    "selfhash-split-current-workbench",
    "embedded-bundle-hash-negative-canary",
    "missing-custody-hash-score-sheet-canary",
    "clean-response-plus-custody-plus-score-sheet-evidence",
})
scorecard = assert_scorecard_integrity(assay, variants)
if variants["clean-response-plus-custody-plus-score-sheet-evidence"].get("score") != 0 or scorecard.get("clean_external_response_evidence") is not False:
    raise SystemExit("clean external response plus score sheet evidence must remain absent")
for key, rel in [
    ("resolved_default_scorer_intake_sha256", SCORER_REL),
    ("responder_bundle_sha256", BUNDLE_REL),
    ("submission_kit_sha256", SUBMISSION_KIT_REL),
    ("scorer_kit_sha256", SCORER_KIT_REL),
    ("response_template_sha256", TEMPLATE_REL),
    ("score_sheet_template_sha256", SCORE_SHEET_TEMPLATE_REL),
]:
    if scorecard.get(key) != file_sha256(rel):
        raise SystemExit(f"scorecard hash drifted for {key}")
assert_negative_canaries(assay, [
    "expected-responder-bundle-sha-embedded-inside-responder-bundle-admitted",
    "score-sheet-without-custody-evidence-record-sha-admitted",
    "missing-clean-response-treated-as-clean-evidence",
], minimum=8)
if not any(row.get("id") == "SA-0060" and row.get("frontier_id") == "OQ-0265" and row.get("assay_fixture") == ASSAY_REL for row in ledger.get("items", [])):
    raise SystemExit("historical self-sufficiency ledger must retain SA-0060 for rev0373 selfhash split assay")
print("check_priority_zero_selfhash_split_bundle_contract: OK")
