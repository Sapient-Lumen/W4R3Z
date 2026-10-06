"""Validate the rev0365 external replay handoff as historical evidence.

rev0366 and later must not force this fixture to remain the current tail. Its
job is to keep the rev0365 leak-sealed handoff auditable while the current-tail
bundle owns the live OQ-0258 handoff.
"""
import json

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

ASSAY_REL = "assays/priority-zero-external-replay-handoff-2026-06-15.json"
RESPONDER_REL = "assays/priority-zero-external-replay-responder-only-2026-06-15.json"
TEMPLATE_REL = "assays/priority-zero-external-replay-response-template-2026-06-15.json"
SCORER_INTAKE_REL = "assays/priority-zero-external-replay-scorer-intake-2026-06-15.json"
ROLE_BLIND_RESPONDER = "assays/priority-zero-role-blind-responder-packet-2026-06-15.json"
ROLE_BLIND_SCORER = "assays/priority-zero-role-blind-scorer-key-2026-06-15.json"
ROLE_BLIND_ASSAY = "assays/priority-zero-role-blind-replay-2026-06-15.json"

assay = load_json(ASSAY_REL)
responder = load_json(RESPONDER_REL)
template = load_json(TEMPLATE_REL)
scorer = load_json(SCORER_INTAKE_REL)
source_responder = load_json(ROLE_BLIND_RESPONDER)
source_scorer = load_json(ROLE_BLIND_SCORER)

if assay.get("revision") != "rev0365":
    raise SystemExit("historical external replay handoff fixture must remain rev0365")
if assay.get("resolved_question") != "OQ-0256" or assay.get("next_open_question") != "OQ-0257":
    raise SystemExit("historical external replay handoff must preserve rev0365 question posture")
if assay.get("source_role_blind_assay") != ROLE_BLIND_ASSAY:
    raise SystemExit("historical external replay handoff must build from the role-blind replay assay")
for rel in [ASSAY_REL, RESPONDER_REL, TEMPLATE_REL, SCORER_INTAKE_REL, ROLE_BLIND_RESPONDER, ROLE_BLIND_SCORER, ROLE_BLIND_ASSAY]:
    assert_surface_exists(rel)
for token in ["not an external replay result", "not independent certification", "not deletion authority", "not a standing benchmark", "not a review court"]:
    if token not in assay.get("non_claim", ""):
        raise SystemExit(f"historical external handoff non_claim missing {token}")
if assay.get("operator_independence_status") != "not-yet-obtained":
    raise SystemExit("rev0365 historical handoff must not claim an operator-independent response exists")
assert_tokens(assay.get("compact_gate_state", ""), ["narrowed", "external response"], label="historical compact gate state")

responder_text = json.dumps(responder, sort_keys=True)
assert_no_tokens(
    responder_text,
    ["true_variant", "answer_key", "expected_score", "scorecard", "compact-hot-cue-role-blind", "sham-decoy-core", "full-archive-role-blind", "baseline-no-archive"],
    label="historical external responder-only packet",
)
labels = [row.get("label") for row in responder.get("packets", [])]
source_labels = [row.get("label") for row in source_responder.get("packets", [])]
if labels != source_labels or labels != ["packet-alpha", "packet-bravo", "packet-charlie", "packet-delta"]:
    raise SystemExit("historical responder-only packet labels drifted from role-blind responder source")
if responder.get("response_template_surface") != TEMPLATE_REL:
    raise SystemExit("historical responder-only packet must point to the response template")
if responder.get("source_role_blind_responder_packet_sha256") != file_sha256(ROLE_BLIND_RESPONDER):
    raise SystemExit("source role-blind responder hash drifted")

if template.get("responder_packet_surface") != RESPONDER_REL:
    raise SystemExit("historical response template must name the responder-only packet")
if template.get("responder_packet_sha256") != file_sha256(RESPONDER_REL):
    raise SystemExit("historical response template responder packet hash drifted")
if scorer.get("responder_only_sha256") != file_sha256(RESPONDER_REL):
    raise SystemExit("historical scorer intake responder hash drifted")
if scorer.get("response_template_sha256") != file_sha256(TEMPLATE_REL):
    raise SystemExit("historical scorer intake template hash drifted")
if scorer.get("source_role_blind_scorer_key_sha256") != file_sha256(ROLE_BLIND_SCORER):
    raise SystemExit("source role-blind scorer hash drifted")
if scorer.get("answer_key") != source_scorer.get("answer_key") or scorer.get("metrics") != source_scorer.get("metrics"):
    raise SystemExit("historical scorer intake drifted from role-blind scorer source")

assert_metric_contract(
    assay,
    required={"responder-key-separation", "handoff-completeness", "hash-custody", "response-intake-shape", "scorer-after-response", "public-archive-leak-caveat", "gate-narrowing", "successor-routing"},
    count=8,
)
variants = assert_variant_score_integrity(
    assay,
    required_variants={"main-archive-as-blind-input", "responder-only-handoff", "scorer-intake-after-response", "external-response-evidence"},
)
scorecard = assert_scorecard_integrity(assay, variants)
if variants["external-response-evidence"]["score"] != 0 or scorecard.get("external_response_status") != "absent":
    raise SystemExit("historical external response evidence must remain absent/zero in rev0365")
if scorecard.get("compact_gate_state") != "narrowed-to-preflight-until-external-response":
    raise SystemExit("historical scorecard compact gate state drifted")
assert_negative_canaries(
    assay,
    ["answer-key-present-in-responder-only-file", "true-variant-present-in-responder-only-file", "external-pass-claimed-without-response", "compact-gate-strengthened-without-external-response", "OQ-0257-successor-omitted"],
    minimum=14,
)
print("check_priority_zero_external_replay_handoff_contract: OK")
