"""Build the rev0373 selfhash-split Priority-0 responder/submission/scorer bundles.

The responder bundle must not embed the expected SHA256 of the bundle that
contains it.  The responder records the observed bundle digest; scorer/custody
material verifies that digest after the response is frozen.
"""
from __future__ import annotations

import json
import pathlib

from priority_zero_handoff_bundle_lib import (
    assert_no_embedded_bundle_hash_claims,
    build_zip_bundle,
    file_sha256,
)

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESPONDER = "assays/priority-zero-selfhash-split-external-replay-responder-only-2026-06-16.json"
TEMPLATE = "assays/priority-zero-selfhash-split-external-replay-response-template-2026-06-16.json"
RESPONDER_README = "handoffs/priority-zero-selfhash-split-external-replay-responder-readme-2026-06-16.md"
RESPONDER_BUNDLE = "handoffs/priority-zero-selfhash-split-external-replay-responder-bundle-2026-06-16.zip"
EVIDENCE_TEMPLATE = "assays/priority-zero-selfhash-split-clean-external-response-evidence-record-template-2026-06-16.json"
CUSTODY_README = "handoffs/priority-zero-selfhash-split-clean-response-custody-readme-2026-06-16.md"
SUBMISSION_KIT = "handoffs/priority-zero-selfhash-split-external-replay-submission-kit-2026-06-16.zip"
SCORER = "assays/priority-zero-selfhash-split-external-replay-scorer-intake-2026-06-16.json"
SCORE_SHEET_TEMPLATE = "assays/priority-zero-selfhash-split-external-replay-score-sheet-template-2026-06-16.json"
SCORER_README = "handoffs/priority-zero-selfhash-split-external-replay-scorer-readme-2026-06-16.md"
SCORER_KIT = "handoffs/priority-zero-selfhash-split-external-replay-scorer-kit-2026-06-16.zip"
MANIFEST = "handoffs/priority-zero-selfhash-split-external-replay-handoff-manifest-2026-06-16.json"
SCORE_TOOL = "tools/score_priority_zero_external_replay_response.py"
ASSAY_LIB = "tools/priority_zero_assay_lib.py"
DECISION_LIB = "tools/priority_zero_external_replay_decision_lib.py"
TIMELINE_LIB = "tools/priority_zero_custody_timeline_lib.py"
FORBIDDEN_RESPONDER_TOKENS = [
    "answer_key",
    "true_variant",
    "expected_score",
    "scorecard",
    "priority-zero-selfhash-split-external-replay-scorer-intake",
    "priority-zero-score-separated-external-replay-scorer-intake",
]
RESPONDER_MEMBERS = [RESPONDER, TEMPLATE, RESPONDER_README]


def _sha(rel: str) -> str:
    return file_sha256(ROOT, rel)


def _rewrite_json(rel: str, update: dict) -> None:
    path = ROOT / rel
    data = json.loads(path.read_text(encoding="utf-8"))
    data.update(update)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _rewrite_nested_template_hashes() -> None:
    # Safe hashes of non-containing surfaces may be embedded before bundling.
    tmpl = json.loads((ROOT / TEMPLATE).read_text(encoding="utf-8"))
    tmpl["responder_packet_sha256"] = _sha(RESPONDER)
    tmpl.pop("responder_bundle_sha256", None)
    tmpl["self_hash_boundary"] = (
        "The expected responder_bundle_sha256 is intentionally not embedded in this responder-visible template "
        "because the template is a member of the bundle whose digest would be changed by such embedding. "
        "The responder records the observed bundle digest; scorer/custody material verify it afterward."
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
    _rewrite_json(SCORER, {
        "responder_only_sha256": _sha(RESPONDER),
        "response_template_sha256": _sha(TEMPLATE),
        "responder_bundle_sha256": responder_sha,
        "evidence_record_template_sha256": _sha(EVIDENCE_TEMPLATE),
        "score_sheet_template_sha256": _sha(SCORE_SHEET_TEMPLATE),
    })

    submission_sha = build_zip_bundle(
        root=ROOT,
        bundle_rel=SUBMISSION_KIT,
        members=[RESPONDER_BUNDLE, EVIDENCE_TEMPLATE, CUSTODY_README],
    )
    _rewrite_json(SCORER, {"submission_kit_sha256": submission_sha})
    scorer_kit_sha = build_zip_bundle(
        root=ROOT,
        bundle_rel=SCORER_KIT,
        members=[SCORER, SCORE_SHEET_TEMPLATE, SCORE_TOOL, ASSAY_LIB, DECISION_LIB, TIMELINE_LIB, SCORER_README],
    )
    manifest = json.loads((ROOT / MANIFEST).read_text(encoding="utf-8"))
    manifest.update({
        "responder_bundle_sha256": responder_sha,
        "submission_kit_sha256": submission_sha,
        "scorer_kit_sha256": scorer_kit_sha,
        "responder_only_sha256": _sha(RESPONDER),
        "response_template_sha256": _sha(TEMPLATE),
        "evidence_record_template_sha256": _sha(EVIDENCE_TEMPLATE),
        "score_sheet_template_sha256": _sha(SCORE_SHEET_TEMPLATE),
        "scorer_intake_sha256": _sha(SCORER),
    })
    # Update excluded row hashes after scorer/evidence/template surfaces settle.  The
    # manifest row for itself is intentionally marked as a post-freeze material;
    # after the write below its self-hash is not stable enough to be authoritative.
    for row in manifest.get("excluded_from_responder_bundle", []):
        if row.get("path") == MANIFEST:
            row["sha256"] = "self-referential-manifest-hash-not-used-as-authority"
        else:
            row["sha256"] = _sha(row["path"])
    (ROOT / MANIFEST).write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(RESPONDER_BUNDLE, responder_sha)
    print(SUBMISSION_KIT, submission_sha)
    print(SCORER_KIT, scorer_kit_sha)


if __name__ == "__main__":
    main()
