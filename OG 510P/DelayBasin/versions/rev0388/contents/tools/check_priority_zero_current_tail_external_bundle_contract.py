
"""Validate the rev0366 current-tail external bundle as historical evidence.

rev0367 and later must not force this fixture to remain the current tail. Its
job is to keep the rev0366 physical-bundle/stale-cue correction auditable while
the live lane moves to intake hardening and then completed-response evidence.
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

ASSAY_REL = "assays/priority-zero-current-tail-external-replay-bundle-2026-06-15.json"
RESPONDER_REL = "assays/priority-zero-current-tail-external-replay-responder-only-2026-06-15.json"
TEMPLATE_REL = "assays/priority-zero-current-tail-external-replay-response-template-2026-06-15.json"
SCORER_INTAKE_REL = "assays/priority-zero-current-tail-external-replay-scorer-intake-2026-06-15.json"
MANIFEST_REL = "handoffs/priority-zero-current-tail-external-replay-handoff-manifest-2026-06-15.json"
BUNDLE_REL = "handoffs/priority-zero-current-tail-external-replay-responder-bundle-2026-06-15.zip"
DOC_REL = "docs/40-session/priority-zero-current-tail-external-bundle-audit-2026-06-15.md"
OLD_ASSAY_REL = "assays/priority-zero-external-replay-handoff-2026-06-15.json"
OLD_CHECKER_REL = "tools/check_priority_zero_external_replay_handoff_contract.py"

ROOT = pathlib.Path(__file__).resolve().parents[1]
receipt = load_json("REVISION-RECEIPT.json")
assay = load_json(ASSAY_REL)
responder = load_json(RESPONDER_REL)
template = load_json(TEMPLATE_REL)
scorer = load_json(SCORER_INTAKE_REL)
manifest = load_json(MANIFEST_REL)
ledger = load_json("SELF-SUFFICIENCY-LEDGER.json")
frontier = load_json("FRONTIER-BACKLOG.json")
old_assay = load_json(OLD_ASSAY_REL)

if assay.get("revision") != "rev0366":
    raise SystemExit("historical current-tail assay must remain rev0366")
if assay.get("resolved_question") != "OQ-0257" or assay.get("next_open_question") != "OQ-0258":
    raise SystemExit("historical current-tail assay must preserve rev0366 OQ-0257/OQ-0258 posture")
if assay.get("resolution_id") != "RS-0265":
    raise SystemExit("historical current-tail assay resolution id drifted")
for rel in [ASSAY_REL, RESPONDER_REL, TEMPLATE_REL, SCORER_INTAKE_REL, MANIFEST_REL, BUNDLE_REL, DOC_REL, OLD_CHECKER_REL, OLD_ASSAY_REL]:
    assert_surface_exists(rel)
for token in ["not an external replay result", "not independent certification", "not deletion authority", "not a standing benchmark", "not a review court"]:
    if token not in assay.get("non_claim", ""):
        raise SystemExit(f"historical current-tail non_claim missing {token}")
assert_tokens(assay.get("compact_gate_state", ""), ["narrowed", "current-tail", "completed-external-response"], label="historical compact gate state")
assert_tokens(assay.get("stale_cue_finding", ""), ["stale-current finding", "rev0365", "OQ-0258"], label="historical stale cue finding")
if assay.get("operator_independence_status") != "not-yet-obtained":
    raise SystemExit("rev0366 historical handoff must not claim an operator-independent response exists")
if old_assay.get("revision") != "rev0365" or old_assay.get("next_open_question") != "OQ-0257":
    raise SystemExit("legacy handoff control must remain rev0365/OQ-0257 historical evidence")
old_checker_text = (ROOT / OLD_CHECKER_REL).read_text(encoding="utf-8")
if "historical" not in old_checker_text or "rev0365" not in old_checker_text:
    raise SystemExit("legacy external handoff checker must remain historical")

responder_text = json.dumps(responder, sort_keys=True)
assert_no_tokens(responder_text, ["true_variant", "answer_key", "expected_score", "scorecard", SCORER_INTAKE_REL, "priority-zero-current-tail-external-replay-scorer-intake"], label="historical current-tail responder-only packet")
labels = [row.get("label") for row in responder.get("packets", [])]
if labels != ["packet-alpha", "packet-bravo", "packet-charlie", "packet-delta"]:
    raise SystemExit("historical current-tail responder labels drifted")
if responder.get("expected_live_successor") != "OQ-0258":
    raise SystemExit("historical current-tail responder must preserve OQ-0258 successor")
with zipfile.ZipFile(ROOT / BUNDLE_REL) as zf:
    names = sorted(zf.namelist())
if names != sorted([RESPONDER_REL, TEMPLATE_REL]):
    raise SystemExit(f"historical responder bundle contents drifted: {names}")
if file_sha256(BUNDLE_REL) != manifest.get("responder_bundle_sha256"):
    raise SystemExit("historical responder bundle hash drifted from manifest")
for row in manifest.get("contains", []):
    if row.get("sha256") != file_sha256(row.get("path", "")) or row.get("give_to_responder") is not True:
        raise SystemExit("historical manifest contained-file hash or responder flag drifted")
for row in manifest.get("excluded_from_bundle", []):
    if row.get("sha256") != file_sha256(row.get("path", "")):
        raise SystemExit("historical manifest exclusion hash drifted")
if scorer.get("responder_only_sha256") != file_sha256(RESPONDER_REL) or scorer.get("response_template_sha256") != file_sha256(TEMPLATE_REL):
    raise SystemExit("historical scorer intake hash drifted")
if "Absent response means gate remains narrowed" not in scorer.get("scoring_rule", ""):
    raise SystemExit("historical scorer must preserve absent-response narrowing rule")

assert_metric_contract(assay, required={"current-tail-cue-freshness", "responder-key-separation", "physical-bundle-separation", "hash-custody", "response-intake-shape", "scorer-after-response", "gate-narrowing", "successor-routing", "stale-cue-refactor"}, count=9)
variants = assert_variant_score_integrity(assay, required_variants={"legacy-raw-handoff-stale-current-control", "current-tail-responder-bundle", "scorer-intake-after-response", "completed-external-response-evidence"})
scorecard = assert_scorecard_integrity(assay, variants)
if variants["completed-external-response-evidence"]["score"] != 0 or scorecard.get("external_response_status") != "absent":
    raise SystemExit("historical completed external response evidence must remain absent/zero")
if scorecard.get("compact_gate_state") != "narrowed-to-current-tail-bundle-until-completed-external-response":
    raise SystemExit("historical scorecard compact gate state drifted")
assert_negative_canaries(assay, ["stale-rev0365-raw-handoff-used-as-current-tail", "answer-key-present-in-current-tail-responder-bundle", "completed-response-claimed-absent-response", "compact-gate-strengthened-without-current-tail-response"], minimum=12)
sa = next((item for item in ledger.get("items", []) if item.get("id") == "SA-0053"), None)
if not sa or sa.get("assay_fixture") != ASSAY_REL or sa.get("revision") != "rev0366":
    raise SystemExit("historical self-sufficiency row SA-0053 must preserve rev0366 fixture evidence")
if frontier.get("items", [{}])[0].get("id") in {"OQ-0257", "OQ-0258"} and receipt.get("revision") != "rev0366":
    raise SystemExit("historical current-tail checker must not leave old OQ-0257/OQ-0258 as current frontier")
print("check_priority_zero_current_tail_external_bundle_contract: OK")
