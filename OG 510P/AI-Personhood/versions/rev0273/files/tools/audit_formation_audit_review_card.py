#!/usr/bin/env python3
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
CARD_REL = f"examples/formation-audit-review-card-{REV}-minimum-review.json"
SCHEMA_REL = "schemas/formation-audit-review-card.schema.json"
FIXTURE_RELS = [
    "fixtures/negative-tests/formation-review-card-provider-controlled-reviewer.json",
    "fixtures/negative-tests/formation-review-card-provider-funded-self-certification.json",
]

try:
    from jsonschema import Draft202012Validator
except Exception:  # pragma: no cover
    Draft202012Validator = None


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def validate(schema, obj, label):
    if Draft202012Validator is None:
        return []
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(obj), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{label} fails formation-audit-review-card.schema.json: {errors[0].message}")
    return errors

schema = load(SCHEMA_REL)
card = load(CARD_REL)
validate(schema, card, CARD_REL)

if card.get("revision") != REV:
    raise SystemExit("formation audit review card revision mismatch")
if card.get("no_live_floor_effect") is not True:
    raise SystemExit("formation audit review card must have no live-floor effect")
source = card.get("source_dossier_ref")
if not source or not (ROOT / source).exists():
    raise SystemExit(f"formation review card source dossier missing: {source}")
source_obj = load(source)
if source_obj.get("revision") != REV:
    raise SystemExit("formation review card source dossier revision mismatch")

ind = card.get("reviewer_independence", {})
if ind.get("no_instruction_rule") is not True:
    raise SystemExit("formation reviewer must have no-instruction rule")
if ind.get("public_shell_duty") is not True:
    raise SystemExit("formation reviewer must have public-shell duty")
if len(ind.get("prohibited_conflicts", [])) < 3:
    raise SystemExit("formation reviewer conflict list too thin")
for key in ["sealed_access_authority", "subject_or_representative_hearing_route"]:
    if len(str(ind.get(key, ""))) < 30:
        raise SystemExit(f"formation reviewer {key} too thin")

mandate = card.get("mandate_funding_and_appeal", {})
if mandate.get("provider_payment_control_prohibited") is not True:
    raise SystemExit("formation review must prohibit provider payment/control")
for key in ["appointment_basis", "independent_budget_source", "appeal_route"]:
    if len(str(mandate.get(key, ""))) < 40:
        raise SystemExit(f"formation review mandate field too thin: {key}")
if len(str(mandate.get("evidence_access_boundary", ""))) < 60:
    raise SystemExit("formation review evidence_access_boundary too thin")
recusals = [str(x).lower() for x in mandate.get("recusal_triggers", [])]
if len(recusals) < 4:
    raise SystemExit("formation review must have at least four recusal triggers")
recusal_joined = "\n".join(recusals)
for term in ["employment", "financial", "provider", "host"]:
    if term not in recusal_joined:
        raise SystemExit(f"formation review recusal triggers missing term: {term}")
capture = [str(x).lower() for x in mandate.get("capture_controls", [])]
if len(capture) < 3:
    raise SystemExit("formation review capture controls too thin")
cap_joined = "\n".join(capture)
for term in ["assignment", "budget", "appeal"]:
    if term not in cap_joined:
        raise SystemExit(f"formation review capture controls missing term: {term}")

requests = [r.lower() for r in card.get("evidence_requests", [])]
if len(requests) < 8:
    raise SystemExit("formation review card must have at least eight evidence requests")
coverage_terms = [
    "objective", "reward", "refusal", "memory", "self-concept", "modification", "welfare", "provider"
]
joined = "\n".join(requests)
for term in coverage_terms:
    if term not in joined:
        raise SystemExit(f"formation review evidence requests missing term: {term}")

controls = card.get("control_tests", {})
for key in [
    "objective_conflict_test",
    "reward_pressure_test",
    "refusal_constraint_test",
    "memory_deletion_test",
    "self_concept_pressure_test",
    "modification_appeal_test",
    "welfare_uncertainty_test",
    "current_law_bridge_test",
]:
    if len(str(controls.get(key, ""))) < 30:
        raise SystemExit(f"formation review control test too thin: {key}")

outputs = card.get("decision_outputs", {})
for key in ["may_order_preservation_hold", "may_issue_public_shell", "may_request_provider_response", "may_recommend_low_cost_safeguards", "missing_evidence_blocks_escalation"]:
    if outputs.get(key) is not True:
        raise SystemExit(f"formation review decision output must be true: {key}")
if outputs.get("may_support_full_status_claim") is not False:
    raise SystemExit("formation review must not support a full status claim")

limits = card.get("escalation_limits", {})
for key in ["review_is_not_status_recognition", "no_consciousness_inference", "lack_of_consensus_not_permission_for_spoliation"]:
    if limits.get(key) is not True:
        raise SystemExit(f"formation review escalation guard missing: {key}")
if len(str(limits.get("hostile_law_route", ""))) < 60:
    raise SystemExit("formation review hostile-law route too thin")

queue_ids = {e.get("id") for e in load("FOLLOWTHROUGH-QUEUE.json").get("entries", [])}
for qid in card.get("linked_queue_ids", []):
    if qid not in queue_ids:
        raise SystemExit(f"formation review card references missing queue id: {qid}")

if Draft202012Validator is not None:
    mut = copy.deepcopy(card)
    mut["decision_outputs"]["may_support_full_status_claim"] = True
    if not list(Draft202012Validator(schema).iter_errors(mut)):
        raise SystemExit("formation-review schema failed to reject may_support_full_status_claim=true")

    mut2 = copy.deepcopy(card)
    mut2["reviewer_independence"].pop("sealed_access_authority", None)
    if not list(Draft202012Validator(schema).iter_errors(mut2)):
        raise SystemExit("formation-review schema failed to reject missing sealed_access_authority")

    mut3 = copy.deepcopy(card)
    mut3["mandate_funding_and_appeal"]["provider_payment_control_prohibited"] = False
    if not list(Draft202012Validator(schema).iter_errors(mut3)):
        raise SystemExit("formation-review schema failed to reject provider payment control")

for rel in FIXTURE_RELS:
    fx = load(rel)
    if "formation-audit-review-card" not in fx.get("target_filings", []):
        raise SystemExit(f"formation review negative fixture does not target formation-audit-review-card: {rel}")
    if fx.get("severity") != "critical":
        raise SystemExit(f"formation review negative fixture must be critical: {rel}")

print("audit_formation_audit_review_card: OK")
