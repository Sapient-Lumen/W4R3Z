"""Validate the historical rev0367 response-intake hollowguard as historical evidence.

rev0368 and later must not force this fixture to remain the current tail. Its
job is to keep the rev0367 hollow/leak guard auditable while the live lane moves
to submit-hardened dry-run scoring and then clean external-response evidence.
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
from score_priority_zero_external_replay_response import validate_response, ResponseIntakeError, REQUIRED_ANSWER_FIELDS

ASSAY_REL = 'assays/priority-zero-response-intake-hollowguard-2026-06-15.json'
RESPONDER_REL = 'assays/priority-zero-intake-hardened-external-replay-responder-only-2026-06-15.json'
TEMPLATE_REL = 'assays/priority-zero-intake-hardened-external-replay-response-template-2026-06-15.json'
SCORER_INTAKE_REL = 'assays/priority-zero-intake-hardened-external-replay-scorer-intake-2026-06-15.json'
MANIFEST_REL = 'handoffs/priority-zero-intake-hardened-external-replay-handoff-manifest-2026-06-15.json'
BUNDLE_REL = 'handoffs/priority-zero-intake-hardened-external-replay-responder-bundle-2026-06-15.zip'
DOC_REL = 'docs/40-session/priority-zero-response-intake-hollowguard-2026-06-15.md'
CHECKER_REL = 'tools/check_priority_zero_response_intake_hollowguard_contract.py'
BUILDER_REL = 'tools/build_priority_zero_intake_hardened_handoff_bundle.py'
SCORE_TOOL_REL = 'tools/score_priority_zero_external_replay_response.py'
OLD_CHECKER_REL = 'tools/check_priority_zero_current_tail_external_bundle_contract.py'
PASS_CANARY_REL = 'assays/priority-zero-intake-hardened-external-replay-shape-pass-canary-2026-06-15.json'
HOLLOW_CANARY_REL = 'assays/priority-zero-intake-hardened-external-replay-hollow-response-canary-2026-06-15.json'
LEAK_CANARY_REL = 'assays/priority-zero-intake-hardened-external-replay-leak-response-canary-2026-06-15.json'

ROOT = pathlib.Path(__file__).resolve().parents[1]
receipt = load_json("REVISION-RECEIPT.json")
assay = load_json(ASSAY_REL)
responder = load_json(RESPONDER_REL)
template = load_json(TEMPLATE_REL)
scorer = load_json(SCORER_INTAKE_REL)
manifest = load_json(MANIFEST_REL)
ledger = load_json("SELF-SUFFICIENCY-LEDGER.json")
frontier = load_json("FRONTIER-BACKLOG.json")

if assay.get("revision") != "rev0367":
    raise SystemExit("historical hollowguard assay must remain rev0367")
if assay.get("resolved_question") != "OQ-0258" or assay.get("next_open_question") != "OQ-0259":
    raise SystemExit("historical hollowguard assay must preserve rev0367 OQ-0258/OQ-0259 posture")
if assay.get("resolution_id") != "RS-0266":
    raise SystemExit("historical hollowguard assay resolution id drifted")
for rel in [ASSAY_REL, RESPONDER_REL, TEMPLATE_REL, SCORER_INTAKE_REL, MANIFEST_REL, BUNDLE_REL, DOC_REL, CHECKER_REL, BUILDER_REL, SCORE_TOOL_REL, OLD_CHECKER_REL, PASS_CANARY_REL, HOLLOW_CANARY_REL, LEAK_CANARY_REL]:
    assert_surface_exists(rel)
for token in ["not an external replay result", "not independent certification", "not deletion authority", "not a minimality proof", "not benchmark authority", "not a review court"]:
    if token not in assay.get("non_claim", ""):
        raise SystemExit(f"hollowguard non_claim missing {token}")
if assay.get("operator_independence_status") != "not-yet-obtained":
    raise SystemExit("rev0367 must not claim an external/operator-independent response exists")
assert_tokens(assay.get("compact_gate_state", ""), ["narrowed", "intake-hardened", "completed-response"], label="hollowguard compact gate state")

responder_text = json.dumps(responder, sort_keys=True)
assert_no_tokens(responder_text, ["true_variant", "answer_key", "expected_score", "scorecard", SCORER_INTAKE_REL, "priority-zero-intake-hardened-external-replay-scorer-intake"], label="intake-hardened responder-only packet")
labels = [row.get("label") for row in responder.get("packets", [])]
if labels != ["packet-alpha", "packet-bravo", "packet-charlie", "packet-delta"]:
    raise SystemExit("intake-hardened responder labels drifted")
if responder.get("expected_live_successor") != "OQ-0259":
    raise SystemExit("intake-hardened responder must name OQ-0259 as live successor")
if responder.get("response_template_surface") != TEMPLATE_REL:
    raise SystemExit("intake-hardened responder must point to response template")

with zipfile.ZipFile(ROOT / BUNDLE_REL) as zf:
    names = sorted(zf.namelist())
if names != sorted([RESPONDER_REL, TEMPLATE_REL]):
    raise SystemExit(f"intake-hardened responder bundle contents drifted: {names}")
if file_sha256(BUNDLE_REL) != manifest.get("responder_bundle_sha256"):
    raise SystemExit("intake-hardened bundle hash drifted from manifest")
for row in manifest.get("contains", []):
    if row.get("sha256") != file_sha256(row.get("path", "")) or row.get("give_to_responder") is not True:
        raise SystemExit("manifest contained responder files must be hash-current and give_to_responder")
for row in manifest.get("excluded_from_bundle", []):
    if row.get("sha256") != file_sha256(row.get("path", "")):
        raise SystemExit(f"manifest exclusion hash drifted for {row.get('path')}")
    if row.get("path") == SCORER_INTAKE_REL and row.get("give_to_responder") is not False:
        raise SystemExit("scorer intake must be excluded from responder bundle")
if scorer.get("responder_only_sha256") != file_sha256(RESPONDER_REL) or scorer.get("response_template_sha256") != file_sha256(TEMPLATE_REL) or scorer.get("responder_bundle_sha256") != file_sha256(BUNDLE_REL):
    raise SystemExit("scorer intake custody hashes drifted")
# The scoring-tool default is allowed to advance with the current tail.
# Historical rev0367 evidence passes an explicit scorer object instead of
# freezing DEFAULT_SCORER_INTAKE to a stale intake.
if REQUIRED_ANSWER_FIELDS != scorer.get("required_answer_fields"):
    raise SystemExit("scoring tool required answer fields must match scorer intake")
for phrase in ["Hollow or blank packet answers are not completed responses", "Absent response means gate remains narrowed", "intake-hardened bundle readiness is not compact-cue confirmation"]:
    if phrase not in scorer.get("scoring_rule", ""):
        raise SystemExit(f"scorer rule missing {phrase}")

positive = load_json(PASS_CANARY_REL)
summary = validate_response(positive, scorer)
if summary.get("operator_cost_minutes") != positive["responder_stage"]["operator_cost_minutes"]:
    raise SystemExit("positive canary operator cost summary drifted")
for rel, token in [(HOLLOW_CANARY_REL, "must be a non-empty string"), (LEAK_CANARY_REL, "scorer-key separation")]:
    try:
        validate_response(load_json(rel), scorer)
    except ResponseIntakeError as exc:
        if token not in str(exc):
            raise SystemExit(f"{rel} failed with wrong diagnostic: {exc}") from exc
    else:
        raise SystemExit(f"{rel} must fail hardened intake validation")

assert_metric_contract(assay, required={"custody-hash-check", "attestation-check", "answer-completeness-check", "label-and-cost-check", "scorer-after-response-boundary", "negative-canary-coverage", "historical-current-tail-refactor", "external-response-absence-honesty"}, count=8)
variants = assert_variant_score_integrity(assay, required_variants={"pre-hardening-scorer-hollow-risk", "hardened-intake-scorer", "hollow-response-negative-canary", "completed-external-response-evidence"})
scorecard = assert_scorecard_integrity(assay, variants)
if variants["completed-external-response-evidence"]["score"] != 0 or scorecard.get("external_response_status") != "absent":
    raise SystemExit("completed external response evidence must remain absent/zero")
if variants["hardened-intake-scorer"]["score"] <= variants["pre-hardening-scorer-hollow-risk"]["score"]:
    raise SystemExit("hardened scorer must outperform pre-hardening hollow-risk control")
if variants["hollow-response-negative-canary"]["score"] != variants["hollow-response-negative-canary"]["max"]:
    raise SystemExit("hollow-response negative canary must be full-score as a failing canary")
if scorecard.get("compact_gate_state") != "narrowed-to-intake-hardened-bundle-until-completed-response":
    raise SystemExit("scorecard must explicitly narrow compact gate until completed response")
for key, rel in [("responder_bundle_sha256", BUNDLE_REL), ("responder_only_sha256", RESPONDER_REL), ("response_template_sha256", TEMPLATE_REL), ("scorer_intake_sha256", SCORER_INTAKE_REL), ("shape_pass_canary_sha256", PASS_CANARY_REL), ("hollow_response_canary_sha256", HOLLOW_CANARY_REL), ("leak_response_canary_sha256", LEAK_CANARY_REL)]:
    if scorecard.get(key) != file_sha256(rel):
        raise SystemExit(f"scorecard hash drifted for {key}")
assert_negative_canaries(assay, ["hollow-response-with-correct-hashes-accepted", "blank-packet-answer-treated-as-completed-response", "scorer-key-exposure-attestation-false-accepted", "current-tail-checker-still-current-locked", "bundle-readiness-treated-as-external-response"], minimum=12)
old_checker_text = (ROOT / OLD_CHECKER_REL).read_text(encoding="utf-8")
if "historical current-tail" not in old_checker_text or "rev0366" not in old_checker_text:
    raise SystemExit("rev0366 current-tail checker must be explicitly historical")
sa = next((item for item in ledger.get("items", []) if item.get("id") == "SA-0054"), None)
if not sa or sa.get("assay_fixture") != ASSAY_REL or sa.get("revision") != "rev0367":
    raise SystemExit("historical self-sufficiency row SA-0054 must preserve rev0367 fixture evidence")
if sa.get("scorecard", {}).get("external_response_status") != "absent":
    raise SystemExit("historical self-sufficiency row must preserve absent response")
if frontier.get("items", [{}])[0].get("id") in {"OQ-0258", "OQ-0259"} and receipt.get("revision") != "rev0367":
    raise SystemExit("historical hollowguard checker must not leave old OQ-0258/OQ-0259 as current frontier")
print("check_priority_zero_response_intake_hollowguard_contract: OK")
