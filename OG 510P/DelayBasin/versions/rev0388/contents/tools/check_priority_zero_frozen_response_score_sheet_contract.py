"""Validate the historical rev0372 frozen-response / score-sheet split.

This checker preserves the rev0372 fixture as historical evidence.  It must not
remain current-tail authority after the rev0373 selfhash-split repair, and it
records the self-hash drift that made rev0373 necessary.
"""
from __future__ import annotations

import pathlib
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
from score_priority_zero_external_replay_response import resolve_default_scorer_intake

ROOT = pathlib.Path(__file__).resolve().parents[1]
ASSAY_REL = "assays/priority-zero-frozen-response-score-sheet-split-2026-06-16.json"
DOC_REL = "docs/40-session/priority-zero-frozen-response-score-sheet-split-2026-06-16.md"
CHECKER_REL = "tools/check_priority_zero_frozen_response_score_sheet_contract.py"
SCORER_REL = "assays/priority-zero-score-separated-external-replay-scorer-intake-2026-06-16.json"
RESPONDER_REL = "assays/priority-zero-score-separated-external-replay-responder-only-2026-06-16.json"
TEMPLATE_REL = "assays/priority-zero-score-separated-external-replay-response-template-2026-06-16.json"
EVIDENCE_TEMPLATE_REL = "assays/priority-zero-score-separated-clean-external-response-evidence-record-template-2026-06-16.json"
SCORE_SHEET_TEMPLATE_REL = "assays/priority-zero-score-separated-external-replay-score-sheet-template-2026-06-16.json"
RESPONDER_README_REL = "handoffs/priority-zero-score-separated-external-replay-responder-readme-2026-06-16.md"
CUSTODY_README_REL = "handoffs/priority-zero-score-separated-clean-response-custody-readme-2026-06-16.md"
SCORER_README_REL = "handoffs/priority-zero-score-separated-external-replay-scorer-readme-2026-06-16.md"
BUNDLE_REL = "handoffs/priority-zero-score-separated-external-replay-responder-bundle-2026-06-16.zip"
SUBMISSION_KIT_REL = "handoffs/priority-zero-score-separated-external-replay-submission-kit-2026-06-16.zip"
SCORER_KIT_REL = "handoffs/priority-zero-score-separated-external-replay-scorer-kit-2026-06-16.zip"
MANIFEST_REL = "handoffs/priority-zero-score-separated-external-replay-handoff-manifest-2026-06-16.json"
SCORE_TOOL_REL = "tools/score_priority_zero_external_replay_response.py"
BUNDLE_LIB_REL = "tools/priority_zero_handoff_bundle_lib.py"
BUILDER_REL = "tools/build_priority_zero_score_separated_handoff_bundle.py"
VALIDATION_LIB_REL = "tools/validation_toolchain_lib.py"

receipt = load_json("REVISION-RECEIPT.json")
assay = load_json(ASSAY_REL)
scorer = load_json(SCORER_REL)
manifest = load_json(MANIFEST_REL)
ledger = load_json("SELF-SUFFICIENCY-LEDGER.json")

def _current_rev() -> str:
    rev = receipt.get("revision")
    return rev if isinstance(rev, str) else ""

if assay.get("revision") != "rev0372" or assay.get("resolved_question") != "OQ-0263" or assay.get("next_open_question") != "OQ-0264":
    raise SystemExit("score-sheet split assay must remain the historical rev0372 fixture")
if assay.get("resolution_id") != "RS-0271":
    raise SystemExit("score-sheet split must route through historical RS-0271")
for rel in [ASSAY_REL,DOC_REL,CHECKER_REL,SCORER_REL,RESPONDER_REL,TEMPLATE_REL,EVIDENCE_TEMPLATE_REL,SCORE_SHEET_TEMPLATE_REL,RESPONDER_README_REL,CUSTODY_README_REL,SCORER_README_REL,BUNDLE_REL,SUBMISSION_KIT_REL,SCORER_KIT_REL,MANIFEST_REL,SCORE_TOOL_REL,BUNDLE_LIB_REL,BUILDER_REL,VALIDATION_LIB_REL]:
    assert_surface_exists(rel)
if _current_rev() == "rev0372":
    if resolve_default_scorer_intake(ROOT) != SCORER_REL:
        raise SystemExit("rev0372 frontier must resolve to the score-separated scorer")
else:
    if resolve_default_scorer_intake(ROOT) == SCORER_REL:
        raise SystemExit("historical rev0372 scorer must not remain current-tail authority")

# Historical defect preserved: the old response template embedded a concrete
# responder_bundle_sha256 that drifted from the actual bundle.  That drift is why
# rev0373 exists and why this checker is not current-tail authority.
old_template = load_json(TEMPLATE_REL)
if old_template.get("responder_bundle_sha256") == file_sha256(BUNDLE_REL):
    raise SystemExit("historical rev0372 self-hash drift unexpectedly disappeared")

for token in ["frozen response", "separate score sheet", "must not be edited", "OQ-0264"]:
    if token not in (ROOT / DOC_REL).read_text(encoding="utf-8"):
        raise SystemExit(f"score-sheet split doc missing token: {token}")
score_tool_text = (ROOT / SCORE_TOOL_REL).read_text(encoding="utf-8")
if "--score-sheet" not in score_tool_text or "frozen response must not carry manual_metric_scores" not in score_tool_text:
    raise SystemExit("score tool must preserve score-sheet and embedded-score rejection")
if "build_zip_bundle" not in (ROOT / BUNDLE_LIB_REL).read_text(encoding="utf-8"):
    raise SystemExit("handoff bundle lib must expose generic build_zip_bundle")
if pathlib.PurePosixPath(CHECKER_REL).name not in (ROOT / VALIDATION_LIB_REL).read_text(encoding="utf-8"):
    raise SystemExit("historical score-sheet split checker must remain in validation toolchain")

with zipfile.ZipFile(ROOT / BUNDLE_REL) as zf:
    names = sorted(zf.namelist())
    if names != sorted([RESPONDER_REL, TEMPLATE_REL, RESPONDER_README_REL]):
        raise SystemExit(f"score-separated responder bundle contents drifted: {names}")
with zipfile.ZipFile(ROOT / SUBMISSION_KIT_REL) as zf:
    if sorted(zf.namelist()) != sorted([BUNDLE_REL, EVIDENCE_TEMPLATE_REL, CUSTODY_README_REL]):
        raise SystemExit("score-separated submission kit contents drifted")
with zipfile.ZipFile(ROOT / SCORER_KIT_REL) as zf:
    expected = sorted([SCORER_REL, SCORE_SHEET_TEMPLATE_REL, SCORE_TOOL_REL, "tools/priority_zero_assay_lib.py", "tools/priority_zero_external_replay_decision_lib.py", "tools/priority_zero_custody_timeline_lib.py", SCORER_README_REL])
    if sorted(zf.namelist()) != expected:
        raise SystemExit("score-separated scorer kit contents drifted")
for key, rel in [
    ("responder_only_sha256", RESPONDER_REL),
    ("response_template_sha256", TEMPLATE_REL),
    ("responder_bundle_sha256", BUNDLE_REL),
    ("submission_kit_sha256", SUBMISSION_KIT_REL),
    ("evidence_record_template_sha256", EVIDENCE_TEMPLATE_REL),
    ("score_sheet_template_sha256", SCORE_SHEET_TEMPLATE_REL),
]:
    if scorer.get(key) != file_sha256(rel):
        raise SystemExit(f"score-separated scorer hash drifted for {key}")
for key, rel in [
    ("responder_bundle_sha256", BUNDLE_REL),
    ("submission_kit_sha256", SUBMISSION_KIT_REL),
    ("scorer_kit_sha256", SCORER_KIT_REL),
    ("score_sheet_template_sha256", SCORE_SHEET_TEMPLATE_REL),
    ("scorer_intake_sha256", SCORER_REL),
]:
    if manifest.get(key) != file_sha256(rel):
        raise SystemExit(f"score-separated manifest hash drifted for {key}")
assert_metric_contract(assay, required={
    "frozen-response-immutability",
    "separate-score-sheet-required",
    "scorer-kit-separation",
    "responder-bundle-uncontaminated",
    "custody-score-hash-chain",
    "historical-checker-burden-cut",
    "clean-response-absence-honesty",
    "successor-routing",
}, count=8)
variants = assert_variant_score_integrity(assay, required_variants={
    "pre-split-in-response-scoring-collision",
    "score-separated-current-workbench",
    "embedded-manual-score-negative-canary",
    "separate-score-sheet-path-smoke",
    "clean-response-plus-custody-plus-score-sheet-evidence",
})
scorecard = assert_scorecard_integrity(assay, variants)
if variants["clean-response-plus-custody-plus-score-sheet-evidence"].get("score") != 0 or scorecard.get("clean_external_response_evidence") is not False:
    raise SystemExit("historical clean external response evidence must remain absent")
assert_negative_canaries(assay, [
    "manual-scores-embedded-in-frozen-response-admitted-as-clean",
    "score-sheet-response-hash-mismatch-admitted",
    "missing-clean-response-treated-as-clean-evidence",
], minimum=8)
if not any(item.get("id") == "SA-0059" and item.get("frontier_id") == "OQ-0264" and item.get("assay_fixture") == ASSAY_REL for item in ledger.get("items", [])):
    raise SystemExit("historical rev0372 self-sufficiency row missing")
print("check_priority_zero_frozen_response_score_sheet_contract: OK")
