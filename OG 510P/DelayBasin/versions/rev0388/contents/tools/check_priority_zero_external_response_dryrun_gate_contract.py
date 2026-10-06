"""Validate the historical rev0368 Priority-0 dry-run gate as historical evidence.

rev0369 and later must not force the rev0368 dry-run fixture to remain the
current tail. The rev0368 dry-run fixture is historical evidence. Its job is to keep contaminated-response rejection and dry-run
score coverage auditable while the live lane moves to custody evidence.
"""
import json
import pathlib
import zipfile

from priority_zero_assay_lib import (
    load_json,
    assert_metric_contract,
    assert_variant_score_integrity,
    assert_scorecard_integrity,
    assert_negative_canaries,
    assert_surface_exists,
    assert_tokens,
    assert_no_tokens,
    file_sha256,
)
from score_priority_zero_external_replay_response import validate_response, ResponseIntakeError

ASSAY_REL = "assays/priority-zero-external-response-dryrun-gate-2026-06-16.json"
RESPONDER_REL = "assays/priority-zero-submit-hardened-external-replay-responder-only-2026-06-16.json"
TEMPLATE_REL = "assays/priority-zero-submit-hardened-external-replay-response-template-2026-06-16.json"
README_REL = "handoffs/priority-zero-submit-hardened-external-replay-responder-readme-2026-06-16.md"
SCORER_REL = "assays/priority-zero-submit-hardened-external-replay-scorer-intake-2026-06-16.json"
MANIFEST_REL = "handoffs/priority-zero-submit-hardened-external-replay-handoff-manifest-2026-06-16.json"
BUNDLE_REL = "handoffs/priority-zero-submit-hardened-external-replay-responder-bundle-2026-06-16.zip"
RESPONSE_REL = "assays/priority-zero-submit-hardened-external-replay-contaminated-dryrun-response-2026-06-16.json"
SUMMARY_REL = "assays/priority-zero-submit-hardened-external-replay-contaminated-dryrun-score-summary-2026-06-16.json"
DOC_REL = "docs/40-session/priority-zero-external-response-dryrun-gate-2026-06-16.md"
CHECKER_REL = "tools/check_priority_zero_external_response_dryrun_gate_contract.py"
BUILDER_REL = "tools/build_priority_zero_submit_hardened_handoff_bundle.py"
SCORE_TOOL_REL = "tools/score_priority_zero_external_replay_response.py"
OLD_CHECKER_REL = "tools/check_priority_zero_response_intake_hollowguard_contract.py"
OLD_ASSAY_REL = "assays/priority-zero-response-intake-hollowguard-2026-06-15.json"

ROOT = pathlib.Path(__file__).resolve().parents[1]
receipt = load_json("REVISION-RECEIPT.json")
assay = load_json(ASSAY_REL)
responder = load_json(RESPONDER_REL)
template = load_json(TEMPLATE_REL)
scorer = load_json(SCORER_REL)
manifest = load_json(MANIFEST_REL)
response = load_json(RESPONSE_REL)
summary = load_json(SUMMARY_REL)
ledger = load_json("SELF-SUFFICIENCY-LEDGER.json")
frontier = load_json("FRONTIER-BACKLOG.json")

if assay.get("revision") != "rev0368":
    raise SystemExit("historical dry-run gate assay must remain rev0368")
if assay.get("resolved_question") != "OQ-0259" or assay.get("next_open_question") != "OQ-0260":
    raise SystemExit("historical dry-run gate assay must preserve OQ-0259/OQ-0260 posture")
if assay.get("resolution_id") != "RS-0267":
    raise SystemExit("historical dry-run gate assay resolution id drifted")
for rel in [ASSAY_REL, RESPONDER_REL, TEMPLATE_REL, README_REL, SCORER_REL, MANIFEST_REL, BUNDLE_REL, RESPONSE_REL, SUMMARY_REL, DOC_REL, CHECKER_REL, BUILDER_REL, SCORE_TOOL_REL, OLD_CHECKER_REL, OLD_ASSAY_REL]:
    assert_surface_exists(rel)
for token in ["not a clean external replay result", "not independent certification", "not deletion authority", "not a minimality proof", "not benchmark authority", "not a compact-cue confirmation", "not a review court"]:
    if token not in assay.get("non_claim", ""):
        raise SystemExit(f"dry-run gate non_claim missing {token}")
if assay.get("operator_independence_status") != "not-yet-obtained-clean-response":
    raise SystemExit("rev0368 must not claim a clean external/operator-independent response exists")
assert_tokens(assay.get("compact_gate_state", ""), ["narrowed", "submit-hardened", "clean-external-response"], label="dry-run compact gate state")

responder_text = json.dumps(responder, sort_keys=True)
assert_no_tokens(responder_text, ["true_variant", "answer_key", "expected_score", "scorecard", SCORER_REL, "priority-zero-submit-hardened-external-replay-scorer-intake"], label="submit-hardened responder-only packet")
labels = [row.get("label") for row in responder.get("packets", [])]
if labels != ["packet-alpha", "packet-bravo", "packet-charlie", "packet-delta"]:
    raise SystemExit("submit-hardened responder labels drifted")
if responder.get("expected_live_successor") != "OQ-0260":
    raise SystemExit("historical submit-hardened responder must name OQ-0260")
if template.get("responder_packet_surface") != RESPONDER_REL or template.get("responder_packet_sha256") != file_sha256(RESPONDER_REL):
    raise SystemExit("submit-hardened template responder pointer/hash drifted")
readme_text = (ROOT / README_REL).read_text(encoding="utf-8")
for token in ["Do not open scorer-only material", "Fill every packet answer field", "Record positive operator cost", "not independent certification"]:
    if token not in readme_text:
        raise SystemExit(f"responder README missing {token}")
assert_no_tokens(readme_text, ["answer_key", "true_variant", "expected_score", "scorecard"], label="submit-hardened responder README")

with zipfile.ZipFile(ROOT / BUNDLE_REL) as zf:
    names = sorted(zf.namelist())
if names != sorted([RESPONDER_REL, TEMPLATE_REL, README_REL]):
    raise SystemExit(f"submit-hardened responder bundle contents drifted: {names}")
if file_sha256(BUNDLE_REL) != manifest.get("responder_bundle_sha256"):
    raise SystemExit("submit-hardened bundle hash drifted from manifest")
for row in manifest.get("contains", []):
    if row.get("sha256") != file_sha256(row.get("path", "")) or row.get("give_to_responder") is not True:
        raise SystemExit("manifest contained responder files must be hash-current and give_to_responder")
for row in manifest.get("excluded_from_bundle", []):
    if row.get("sha256") != file_sha256(row.get("path", "")):
        raise SystemExit(f"manifest exclusion hash drifted for {row.get('path')}")
    if row.get("path") == SCORER_REL and row.get("give_to_responder") is not False:
        raise SystemExit("submit-hardened scorer intake must be excluded from responder bundle")
if scorer.get("responder_only_sha256") != file_sha256(RESPONDER_REL) or scorer.get("response_template_sha256") != file_sha256(TEMPLATE_REL) or scorer.get("responder_bundle_sha256") != file_sha256(BUNDLE_REL):
    raise SystemExit("submit-hardened scorer intake custody hashes drifted")
for phrase in ["Contaminated same-session dry-runs", "do not confirm compact reentry", "Absent clean response means gate remains narrowed"]:
    if phrase not in scorer.get("scoring_rule", ""):
        raise SystemExit(f"submit-hardened scorer rule missing {phrase}")

try:
    validate_response(response, scorer)
except ResponseIntakeError as exc:
    message = str(exc)
    if "scorer-key separation" not in message and "separate score sheet" not in message:
        raise SystemExit(f"strict mode rejected contaminated response with wrong diagnostic: {exc}") from exc
else:
    raise SystemExit("strict external scorer must reject same-session contaminated dry-run response")
dryrun_summary = validate_response(response, scorer, allow_contaminated_dryrun=True)
if dryrun_summary.get("validation_mode") != "contaminated-dryrun" or dryrun_summary.get("external_response_evidence") is not False:
    raise SystemExit("dry-run summary must mark contaminated-dryrun and external_response_evidence=false")
if dryrun_summary.get("manual_score_total") != 39 or dryrun_summary.get("manual_score_max") != 72:
    raise SystemExit("dry-run manual score total must remain 39/72")
if dryrun_summary.get("manual_scores_by_label") != summary.get("manual_scores_by_label"):
    raise SystemExit("persisted dry-run score summary drifted from scoring tool output")
if response.get("dryrun_mode", {}).get("external_response_evidence") is not False:
    raise SystemExit("dry-run response must explicitly mark external_response_evidence false")

assert_metric_contract(assay, required={"strict-contamination-rejection", "dryrun-score-summary", "manual-score-label-coverage", "responder-kit-usability", "scorer-after-response-boundary", "historical-hollowguard-refactor", "clean-response-absence-honesty", "successor-routing"}, count=8)
variants = assert_variant_score_integrity(assay, required_variants={"pre-dryrun-hollowguard-only", "submit-hardened-responder-kit", "contaminated-dryrun-score-path", "clean-external-response-evidence"})
scorecard = assert_scorecard_integrity(assay, variants)
if variants["clean-external-response-evidence"]["score"] != 0 or scorecard.get("external_response_status") != "clean-response-absent":
    raise SystemExit("historical clean external response evidence must remain absent/zero")
if scorecard.get("dryrun_validation_mode") != "contaminated-dryrun" or scorecard.get("dryrun_external_response_evidence") is not False:
    raise SystemExit("scorecard must preserve contaminated dry-run non-evidence boundary")
for key, rel in [("responder_bundle_sha256", BUNDLE_REL), ("responder_only_sha256", RESPONDER_REL), ("response_template_sha256", TEMPLATE_REL), ("responder_readme_sha256", README_REL), ("scorer_intake_sha256", SCORER_REL), ("contaminated_dryrun_response_sha256", RESPONSE_REL), ("contaminated_dryrun_score_summary_sha256", SUMMARY_REL)]:
    if scorecard.get(key) != file_sha256(rel):
        raise SystemExit(f"scorecard hash drifted for {key}")
assert_negative_canaries(assay, ["contaminated-dryrun-treated-as-clean-external-response", "strict-scorer-accepts-scorer-key-exposed-response", "manual-score-label-drift-accepted", "responder-readme-leaks-answer-key", "compact-gate-confirmed-by-dryrun", "OQ-0260-successor-omitted"], minimum=12)
old_checker_text = (ROOT / OLD_CHECKER_REL).read_text(encoding="utf-8")
if "historical rev0367" not in old_checker_text or "rev0367" not in old_checker_text:
    raise SystemExit("rev0367 hollowguard checker must be explicitly historical")
sa = next((item for item in ledger.get("items", []) if item.get("id") == "SA-0055"), None)
if not sa or sa.get("assay_fixture") != ASSAY_REL or sa.get("revision") != "rev0368":
    raise SystemExit("historical self-sufficiency row SA-0055 must preserve rev0368 fixture evidence")
if sa.get("scorecard", {}).get("external_response_status") != "clean-response-absent":
    raise SystemExit("historical self-sufficiency row must preserve absent clean response")
if receipt.get("revision") != "rev0368" and frontier.get("items", [{}])[0].get("id") == "OQ-0260":
    raise SystemExit("historical dry-run checker must not leave old OQ-0260 as current frontier after rev0368")
print("check_priority_zero_external_response_dryrun_gate_contract: OK")
