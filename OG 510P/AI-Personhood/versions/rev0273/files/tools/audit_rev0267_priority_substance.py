#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()

try:
    from jsonschema import Draft202012Validator
except Exception:  # pragma: no cover
    Draft202012Validator = None


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def validate(schema_rel, data_rel):
    if Draft202012Validator is None:
        return
    schema = load(schema_rel)
    data = load(data_rel)
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{data_rel} fails {schema_rel}: {errors[0].message}")

route_rel = f"examples/route-decision-card-{REV}-send-nosend-retarget.json"
six_rel = f"examples/six-artifact-pilot-state-{REV}-preservation-review.json"
inst_rel = f"examples/minimum-review-institution-pilot-{REV}-one-case-formation-review.json"
for schema, rel in [
    ("schemas/route-decision-card.schema.json", route_rel),
    ("schemas/six-artifact-pilot-state.schema.json", six_rel),
    ("schemas/minimum-review-institution-pilot.schema.json", inst_rel),
]:
    if not (ROOT / rel).exists():
        raise SystemExit(f"missing rev0264 priority substance surface: {rel}")
    validate(schema, rel)

route = load(route_rel)
six = load(six_rel)
inst = load(inst_rel)

if route.get("revision") != REV or six.get("revision") != REV or inst.get("revision") != REV:
    raise SystemExit("rev0264 priority surfaces revision mismatch")
for name, obj in [("route", route), ("six", six), ("institution", inst)]:
    if obj.get("no_live_floor_effect") is not True:
        raise SystemExit(f"{name} surface lacks no-live-floor guard")

if route.get("decision_state") != "decision-required-no-contact-authorized":
    raise SystemExit("route decision card must remain decision-required/no-contact-authorized")
locks = route.get("overclaim_locks", {})
for key in [
    "may_authorize_send",
    "may_start_response_clock",
    "may_claim_counterparty_selection",
    "may_create_custody_intake_import_or_floor_effect",
    "may_treat_route_score_as_authority",
]:
    if locks.get(key) is not False:
        raise SystemExit(f"route decision card overclaim lock not false: {key}")

routes = {r.get("route_id"): r for r in route.get("candidate_routes", [])}
if "ROUTE-ELEOS-WELFARE-REVIEW" not in routes or "ROUTE-RAIC-AIID-ROUTING" not in routes:
    raise SystemExit("route decision card must include reviewer-first and AIID routing branches")
if routes["ROUTE-ELEOS-WELFARE-REVIEW"].get("score", 0) <= routes["ROUTE-RAIC-AIID-ROUTING"].get("score", 0):
    raise SystemExit("reviewer-first route must outrank AIID for the preservation/formation pilot")
if any(r.get("authorized_now") is not False for r in routes.values()):
    raise SystemExit("route decision card must not authorize any candidate now")
joined_route_text = json.dumps(route).lower()
for term in ["non-incident", "no contact", "no-send", "retarget", "response clock"]:
    if term not in joined_route_text:
        raise SystemExit(f"route decision card missing operational term: {term}")

expected_artifacts = [
    "A1-BRANCH-REQUEST",
    "A2-TRANSPORT-DELIVERY",
    "A3-RAW-RESPONSE-OR-FAILED-GATE",
    "A4-PRESERVATION-SCHEDULE",
    "A5-REVIEWER-APPOINTMENT",
    "A6-PUBLIC-FINDING-REMEDY",
]
actual_artifacts = [a.get("artifact_id") for a in six.get("artifact_chain", [])]
if actual_artifacts != expected_artifacts:
    raise SystemExit(f"six-artifact pilot chain mismatch: {actual_artifacts}")
if len({a.get("ordinal") for a in six.get("artifact_chain", [])}) != 6:
    raise SystemExit("six-artifact pilot ordinals not unique")
if six.get("pilot_state") != "prepared-not-authorized":
    raise SystemExit("six-artifact pilot must remain prepared-not-authorized")
six_locks = six.get("overclaim_locks", {})
for key in [
    "may_substitute_internal_draft_for_artifact",
    "may_close_first_artifact_by_narrative",
    "may_start_response_clock",
    "may_create_custody_intake_import_or_floor_effect",
    "may_claim_status_or_welfare_finding",
]:
    if six_locks.get(key) is not False:
        raise SystemExit(f"six-artifact overclaim lock not false: {key}")
dashboard = six.get("outcome_dashboard", {})
if dashboard.get("file_count_not_a_measure") is not True or dashboard.get("gate_count_not_a_measure") is not True:
    raise SystemExit("six-artifact dashboard must reject file count and gate count as outcome measures")
if len(dashboard.get("measures", [])) < 8:
    raise SystemExit("six-artifact dashboard too thin")

if inst.get("pilot_state") != "designed-not-appointed":
    raise SystemExit("minimum institution pilot must remain designed-not-appointed")
if len(inst.get("roles", [])) < 5:
    raise SystemExit("minimum institution pilot lacks enough roles")
role_text = " ".join(r.get("role", "") + " " + r.get("independence_requirement", "") for r in inst.get("roles", [])).lower()
for term in ["independent reviewer", "special advocate", "provider records liaison", "evidence custodian", "public-shell"]:
    if term not in role_text:
        raise SystemExit(f"minimum institution pilot missing role term: {term}")
if len(inst.get("sealed_evidence_schedule", [])) < 8:
    raise SystemExit("minimum institution pilot sealed evidence schedule too thin")
if len(inst.get("conflict_and_funding_controls", [])) < 5:
    raise SystemExit("minimum institution pilot conflict/funding controls too thin")

queue = load("FOLLOWTHROUGH-QUEUE.json")
if queue.get("revision") != REV:
    raise SystemExit("queue revision mismatch in priority-substance audit")
entries = {e.get("id"): e for e in queue.get("entries", [])}
for qid in ["FT-0068", "FT-0069"]:
    e = entries.get(qid)
    if not e:
        raise SystemExit(f"queue missing {qid}")
    text = " ".join(str(e.get(k, "")) for k in ["why", "need", "next_action", "closure_condition", "receiving_surface"]).lower()
    if "do not expand formation doctrine while first-contact execution remains blocked" in text:
        raise SystemExit(f"{qid} still freezes formation work behind contact execution")
    if "reviewer" not in text or "sealed" not in text:
        raise SystemExit(f"{qid} must now point at reviewer/sealed-access substance")
for qid in ["FT-0205-FIRST-REAL-ARTIFACT-DROP", "FT-0207-FIRST-LIVE-EVIDENCE-ACQUISITION", "FT-0199-ACTUAL-LIVE-COUNTERPARTY-RESPONSE"]:
    e = entries.get(qid)
    if e and f"six-artifact-pilot-state-{REV}" not in e.get("receiving_surface", ""):
        raise SystemExit(f"{qid} must receive into the six-artifact pilot state")

status = load("SURFACE-STATUS.json")
for rel in [route_rel, six_rel, inst_rel]:
    if rel not in status.get("new_surfaces", []):
        raise SystemExit(f"SURFACE-STATUS missing priority substance surface: {rel}")
    if not (ROOT / rel).exists():
        raise SystemExit(f"SURFACE-STATUS names missing path: {rel}")
if status.get("no_live_floor_effect") is not True:
    raise SystemExit("SURFACE-STATUS must preserve no live floor effect")

print("audit_rev0267_priority_substance: OK")
