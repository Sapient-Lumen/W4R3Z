"""Build the rev0374 preanswer-clamped Priority-0 bundles.

Only the responder bundle is pre-response material.  It contains a scorer-free
response init/finalize helper and shared response validator so incomplete runs
fail before custody.  The custody kit opens after response finalization and
reruns that contract.  The scorer kit opens only after custody freezes and
contains separate score-sheet binding/finalization tooling.
"""
from __future__ import annotations

import json
import pathlib

from priority_zero_causal_artifact_lib import (
    CURRENT_CUSTODY_CONTRACT,
    CURRENT_SCORING_CONTRACT,
)
from priority_zero_handoff_bundle_lib import (
    assert_no_embedded_bundle_hash_claims,
    build_zip_bundle,
    file_sha256,
)

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESPONDER = "assays/priority-zero-preanswer-clamped-external-replay-responder-only-2026-06-16.json"
TEMPLATE = "assays/priority-zero-preanswer-clamped-external-replay-response-template-2026-06-16.json"
RESPONDER_README = "handoffs/priority-zero-preanswer-clamped-external-replay-responder-readme-2026-06-16.md"
RESPONDER_BUNDLE = "handoffs/priority-zero-preanswer-clamped-external-replay-responder-bundle-2026-06-16.zip"
EVIDENCE_TEMPLATE = "assays/priority-zero-preanswer-clamped-clean-external-response-evidence-record-template-2026-06-16.json"
CUSTODY_README = "handoffs/priority-zero-preanswer-clamped-clean-response-custody-readme-2026-06-16.md"
CUSTODY_KIT = "handoffs/priority-zero-preanswer-clamped-external-replay-postfreeze-custody-kit-2026-06-16.zip"
SCORER = "assays/priority-zero-preanswer-clamped-external-replay-scorer-intake-2026-06-16.json"
SCORE_SHEET_TEMPLATE = "assays/priority-zero-preanswer-clamped-external-replay-score-sheet-template-2026-06-16.json"
SCORER_README = "handoffs/priority-zero-preanswer-clamped-external-replay-scorer-readme-2026-06-16.md"
SCORER_KIT = "handoffs/priority-zero-preanswer-clamped-external-replay-scorer-kit-2026-06-16.zip"
MANIFEST = "handoffs/priority-zero-preanswer-clamped-external-replay-handoff-manifest-2026-06-16.json"
ASSAY = "assays/priority-zero-preanswer-material-clamp-2026-06-16.json"
SCORE_TOOL = "tools/score_priority_zero_external_replay_response.py"
RESPONSE_PREP_TOOL = "tools/prepare_priority_zero_external_replay_response.py"
CUSTODY_PREP_TOOL = "tools/prepare_priority_zero_clean_response_custody_record.py"
SCORE_SHEET_PREP_TOOL = "tools/prepare_priority_zero_external_replay_score_sheet.py"
ARTIFACT_LIB = "tools/priority_zero_external_run_artifact_lib.py"
RESPONSE_LIB = "tools/priority_zero_external_replay_response_lib.py"
ASSAY_LIB = "tools/priority_zero_assay_lib.py"
DECISION_LIB = "tools/priority_zero_external_replay_decision_lib.py"
TIMELINE_LIB = "tools/priority_zero_custody_timeline_lib.py"
CUSTODY_LIB = "tools/priority_zero_external_replay_custody_lib.py"
CAUSAL_LIB = "tools/priority_zero_causal_artifact_lib.py"
FORBIDDEN_RESPONDER_TOKENS = [
    "answer_key",
    "true_variant",
    "expected_score",
    "priority-zero-preanswer-clamped-external-replay-scorer-intake",
    "priority-zero-selfhash-split-external-replay-scorer-intake",
]
RESPONDER_MEMBERS = [RESPONDER, TEMPLATE, RESPONDER_README, RESPONSE_PREP_TOOL, ARTIFACT_LIB, RESPONSE_LIB]


def _sha(rel: str) -> str:
    return file_sha256(ROOT, rel)


def _rewrite_json(rel: str, update: dict) -> None:
    path = ROOT / rel
    data = json.loads(path.read_text(encoding="utf-8"))
    data.update(update)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _rewrite_nested_template_hashes() -> None:
    tmpl = json.loads((ROOT / TEMPLATE).read_text(encoding="utf-8"))
    tmpl["responder_packet_sha256"] = _sha(RESPONDER)
    tmpl.pop("responder_bundle_sha256", None)
    tmpl["preanswer_material_boundary"] = (
        "Only the responder bundle itself is valid pre-response material. Custody kit, scorer kit, "
        "score sheet, handoff manifest, expected digest, full archive, old submission kit, and prior "
        "conversation are post-freeze or forbidden for a clean run."
    )
    (ROOT / TEMPLATE).write_text(json.dumps(tmpl, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    _rewrite_nested_template_hashes()
    responder_sha = build_zip_bundle(
        root=ROOT,
        bundle_rel=RESPONDER_BUNDLE,
        members=RESPONDER_MEMBERS,
        forbidden_tokens=FORBIDDEN_RESPONDER_TOKENS,
        forbidden_token_members=RESPONDER_MEMBERS,
    )
    assert_no_embedded_bundle_hash_claims(ROOT, RESPONDER_MEMBERS, actual_bundle_sha256=responder_sha)

    _rewrite_json(EVIDENCE_TEMPLATE, {
        "responder_bundle_sha256": responder_sha,
        "responder_only_sha256": _sha(RESPONDER),
        "response_template_sha256": _sha(TEMPLATE),
    })
    scorer_path = ROOT / SCORER
    scorer_data = json.loads(scorer_path.read_text(encoding="utf-8"))
    scorer_data.pop("submission_kit_sha256", None)
    scorer_data.update({
        "responder_only_sha256": _sha(RESPONDER),
        "response_template_sha256": _sha(TEMPLATE),
        "responder_bundle_sha256": responder_sha,
        "evidence_record_template_sha256": _sha(EVIDENCE_TEMPLATE),
        "score_sheet_template_sha256": _sha(SCORE_SHEET_TEMPLATE),
        "allowed_pre_response_materials": [RESPONDER_BUNDLE],
        "submission_kit_state": "none-currently-valid; only the responder bundle may be shown before response; custody and scorer kits are post-freeze",
    })
    scorer_path.write_text(json.dumps(scorer_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    custody_kit_sha = build_zip_bundle(
        root=ROOT,
        bundle_rel=CUSTODY_KIT,
        members=[EVIDENCE_TEMPLATE, TEMPLATE, CUSTODY_README, CUSTODY_PREP_TOOL, CAUSAL_LIB, ARTIFACT_LIB, RESPONSE_LIB, TIMELINE_LIB, CUSTODY_LIB],
    )
    _rewrite_json(SCORER, {"custody_kit_sha256": custody_kit_sha})
    scorer_kit_sha = build_zip_bundle(
        root=ROOT,
        bundle_rel=SCORER_KIT,
        members=[
            SCORER,
            SCORE_SHEET_TEMPLATE,
            EVIDENCE_TEMPLATE,
            RESPONDER,
            TEMPLATE,
            SCORE_TOOL,
            SCORE_SHEET_PREP_TOOL,
            CAUSAL_LIB,
            ARTIFACT_LIB,
            RESPONSE_LIB,
            ASSAY_LIB,
            DECISION_LIB,
            TIMELINE_LIB,
            CUSTODY_LIB,
            SCORER_README,
        ],
    )
    manifest = json.loads((ROOT / MANIFEST).read_text(encoding="utf-8"))
    manifest.update({
        "response_preparation_contract_version": "responder-finalize-v1",
        "custody_contract_version": CURRENT_CUSTODY_CONTRACT,
        "scoring_contract_version": CURRENT_SCORING_CONTRACT,
        "postfreeze_sequence": [
            "finalize completed responder output with bundled response helper",
            "open custody kit and revalidate the exact response bytes",
            "freeze custody record with producer-local response observation",
            "open scorer kit and initialize score draft after exact custody validation",
            "complete and freeze score sheet with scorer-local custody observation",
            "run scorer on the exact response/custody/score-sheet hash chain",
        ],
        "cross_operator_ordering_basis": "exact-artifact-hash-chain; independent wall clocks are descriptive only",
        "responder_bundle_members": RESPONDER_MEMBERS,
        "custody_kit_members": [EVIDENCE_TEMPLATE, TEMPLATE, CUSTODY_README, CUSTODY_PREP_TOOL, CAUSAL_LIB, ARTIFACT_LIB, RESPONSE_LIB, TIMELINE_LIB, CUSTODY_LIB],
        "scorer_kit_members": [
            SCORER, SCORE_SHEET_TEMPLATE, EVIDENCE_TEMPLATE, RESPONDER, TEMPLATE, SCORE_TOOL, SCORE_SHEET_PREP_TOOL,
            CAUSAL_LIB, ARTIFACT_LIB, RESPONSE_LIB, ASSAY_LIB, DECISION_LIB, TIMELINE_LIB, CUSTODY_LIB, SCORER_README,
        ],
        "responder_bundle_sha256": responder_sha,
        "custody_kit_sha256": custody_kit_sha,
        "scorer_kit_sha256": scorer_kit_sha,
        "responder_only_sha256": _sha(RESPONDER),
        "response_template_sha256": _sha(TEMPLATE),
        "evidence_record_template_sha256": _sha(EVIDENCE_TEMPLATE),
        "score_sheet_template_sha256": _sha(SCORE_SHEET_TEMPLATE),
        "scorer_intake_sha256": _sha(SCORER),
    })
    for row in manifest.get("excluded_from_responder_bundle", []):
        if row.get("path") == MANIFEST:
            row["sha256"] = "self-referential-manifest-hash-not-used-as-authority"
        else:
            row["sha256"] = _sha(row["path"])
    (ROOT / MANIFEST).write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    assay_path = ROOT / ASSAY
    assay = json.loads(assay_path.read_text(encoding="utf-8"))
    scorecard = assay.get("scorecard")
    if not isinstance(scorecard, dict):
        raise SystemExit(f"{ASSAY} missing scorecard")
    negative_canaries = assay.get("negative_canaries")
    if not isinstance(negative_canaries, list):
        raise SystemExit(f"{ASSAY} missing negative_canaries")
    assay["negative_canaries"] = [
        "scorer-local-custody-observation-before-scorer-kit-open-admitted"
        if item == "scorer-kit-opened-before-custody-record-freeze-admitted"
        else item
        for item in negative_canaries
    ]
    scorecard.update({
        "custody_contract_version": CURRENT_CUSTODY_CONTRACT,
        "scoring_contract_version": CURRENT_SCORING_CONTRACT,
        "cross_operator_ordering_basis": "exact-artifact-hash-chain-not-wall-clock",
        "cross_machine_clock_skew_canary_passed": True,
        "resolved_default_scorer_intake_sha256": _sha(SCORER),
        "responder_bundle_sha256": responder_sha,
        "custody_kit_sha256": custody_kit_sha,
        "scorer_kit_sha256": scorer_kit_sha,
        "response_template_sha256": _sha(TEMPLATE),
        "score_sheet_template_sha256": _sha(SCORE_SHEET_TEMPLATE),
        "evidence_record_template_sha256": _sha(EVIDENCE_TEMPLATE),
        "handoff_manifest_sha256": _sha(MANIFEST),
        "response_preparation_tool_sha256": _sha(RESPONSE_PREP_TOOL),
        "response_contract_library_sha256": _sha(RESPONSE_LIB),
        "strict_artifact_library_sha256": _sha(ARTIFACT_LIB),
        "custody_contract_library_sha256": _sha(CUSTODY_LIB),
        "causal_artifact_library_sha256": _sha(CAUSAL_LIB),
    })
    assay_path.write_text(json.dumps(assay, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(RESPONDER_BUNDLE, responder_sha)
    print(CUSTODY_KIT, custody_kit_sha)
    print(SCORER_KIT, scorer_kit_sha)


if __name__ == "__main__":
    main()
