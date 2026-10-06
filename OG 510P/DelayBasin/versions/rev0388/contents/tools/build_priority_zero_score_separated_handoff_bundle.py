"""Build the rev0372 score-separated Priority-0 responder/submission/scorer bundles."""
from __future__ import annotations

import json
import pathlib

from priority_zero_handoff_bundle_lib import build_zip_bundle, file_sha256

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESPONDER = "assays/priority-zero-score-separated-external-replay-responder-only-2026-06-16.json"
TEMPLATE = "assays/priority-zero-score-separated-external-replay-response-template-2026-06-16.json"
RESPONDER_README = "handoffs/priority-zero-score-separated-external-replay-responder-readme-2026-06-16.md"
RESPONDER_BUNDLE = "handoffs/priority-zero-score-separated-external-replay-responder-bundle-2026-06-16.zip"
EVIDENCE_TEMPLATE = "assays/priority-zero-score-separated-clean-external-response-evidence-record-template-2026-06-16.json"
CUSTODY_README = "handoffs/priority-zero-score-separated-clean-response-custody-readme-2026-06-16.md"
SUBMISSION_KIT = "handoffs/priority-zero-score-separated-external-replay-submission-kit-2026-06-16.zip"
SCORER = "assays/priority-zero-score-separated-external-replay-scorer-intake-2026-06-16.json"
SCORE_SHEET_TEMPLATE = "assays/priority-zero-score-separated-external-replay-score-sheet-template-2026-06-16.json"
SCORER_README = "handoffs/priority-zero-score-separated-external-replay-scorer-readme-2026-06-16.md"
SCORER_KIT = "handoffs/priority-zero-score-separated-external-replay-scorer-kit-2026-06-16.zip"
MANIFEST = "handoffs/priority-zero-score-separated-external-replay-handoff-manifest-2026-06-16.json"
SCORE_TOOL = "tools/score_priority_zero_external_replay_response.py"
ASSAY_LIB = "tools/priority_zero_assay_lib.py"
DECISION_LIB = "tools/priority_zero_external_replay_decision_lib.py"
TIMELINE_LIB = "tools/priority_zero_custody_timeline_lib.py"
FORBIDDEN_RESPONDER_TOKENS = [
    "answer_key",
    "true_variant",
    "expected_score",
    "scorecard",
    "priority-zero-score-separated-external-replay-scorer-intake",
]


def _sha(rel: str) -> str:
    return file_sha256(ROOT, rel)


def _rewrite_json(rel: str, update: dict) -> None:
    path = ROOT / rel
    data = json.loads(path.read_text(encoding="utf-8"))
    data.update(update)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    responder_sha = build_zip_bundle(
        root=ROOT,
        bundle_rel=RESPONDER_BUNDLE,
        members=[RESPONDER, TEMPLATE, RESPONDER_README],
        forbidden_tokens=FORBIDDEN_RESPONDER_TOKENS,
        forbidden_token_members=[RESPONDER, TEMPLATE, RESPONDER_README],
    )
    # Now that the responder bundle exists, stamp template/evidence/scorer hashes.
    _rewrite_json(TEMPLATE, {
        "responder_packet_sha256": _sha(RESPONDER),
        "responder_bundle_sha256": responder_sha,
    })
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
    # Rebuild responder bundle after template hash stamping so the ZIP contains the final template.
    responder_sha = build_zip_bundle(
        root=ROOT,
        bundle_rel=RESPONDER_BUNDLE,
        members=[RESPONDER, TEMPLATE, RESPONDER_README],
        forbidden_tokens=FORBIDDEN_RESPONDER_TOKENS,
        forbidden_token_members=[RESPONDER, TEMPLATE, RESPONDER_README],
    )
    _rewrite_json(SCORER, {"responder_bundle_sha256": responder_sha})
    _rewrite_json(EVIDENCE_TEMPLATE, {"responder_bundle_sha256": responder_sha})
    _rewrite_json(SCORER, {"evidence_record_template_sha256": _sha(EVIDENCE_TEMPLATE)})
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
    for row in manifest.get("excluded_from_responder_bundle", []):
        row["sha256"] = _sha(row["path"])
    (ROOT / MANIFEST).write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(RESPONDER_BUNDLE, responder_sha)
    print(SUBMISSION_KIT, submission_sha)
    print(SCORER_KIT, scorer_kit_sha)


if __name__ == "__main__":
    main()
