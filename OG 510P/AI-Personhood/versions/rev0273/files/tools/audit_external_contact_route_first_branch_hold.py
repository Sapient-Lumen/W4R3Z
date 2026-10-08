#!/usr/bin/env python3
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
HOLD_REL = f"examples/external-contact-route-first-branch-hold-{REV}-aiid.json"
SCHEMA_REL = "schemas/external-contact-route-first-branch-hold.schema.json"
FIXTURE_REL = "fixtures/negative-tests/external-contact-route-first-branch-hold-closes-first-artifact.json"

try:
    from jsonschema import Draft202012Validator
except Exception:  # pragma: no cover
    Draft202012Validator = None


def load_json(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def validate(schema, obj, label):
    if Draft202012Validator is None:
        return
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(obj), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{label} fails external-contact-route-first-branch-hold.schema.json: {errors[0].message}")

schema = load_json(SCHEMA_REL)
hold = load_json(HOLD_REL)
validate(schema, hold, HOLD_REL)

if hold.get("revision") != REV:
    raise SystemExit("route-first branch hold revision mismatch")
if hold.get("hold_state") != "explicit-current-revision-no-send-hold":
    raise SystemExit("route-first branch hold must remain an explicit current-revision no-send hold")
if hold.get("no_live_floor_effect") is not True:
    raise SystemExit("route-first branch hold must have no live-floor effect")

refs = hold.get("source_refs", {})
for name, rel in refs.items():
    if not rel or not (ROOT / rel).exists():
        raise SystemExit(f"route-first branch hold source missing: {name}={rel}")

gate = load_json(refs["route_first_send_capture_gate"])
if gate.get("revision") != REV or gate.get("gate_state") != "blocked-route-first-no-human-send-no-transport":
    raise SystemExit("route-first branch hold must bind current blocked send/capture gate")
summary = gate.get("blocker_resolution_summary", {})
if summary.get("gate_remains_blocked") is not True:
    raise SystemExit("route-first branch hold cannot bind an unblocked send gate")
required_unsatisfied = {"human-signature", "sender-authority", "send-time-public-locator-recheck", "private-vault-roots", "final-route-first-hash-recompute", "actual-transport-proof"}
if set(summary.get("unsatisfied_precondition_ids", [])) != required_unsatisfied:
    raise SystemExit("route-first branch hold unsatisfied blockers do not match send gate")

preflight = load_json(refs["route_first_preflight"])
if preflight.get("preflight_state") != "preferred-route-first-no-attachment-blocked-no-human-send":
    raise SystemExit("route-first branch hold must bind blocked route-first preflight")
reply = load_json(refs["route_first_reply_disposition"])
if reply.get("disposition_state") != "pre-send-no-inbound":
    raise SystemExit("route-first branch hold must bind no-inbound reply disposition")
stage_two = load_json(refs["stage_two_authorization_gate"])
if stage_two.get("blocker_resolution_summary", {}).get("gate_remains_blocked") is not True:
    raise SystemExit("route-first branch hold must bind blocked stage-two gate")

# Decision must be a reversible hold, not a hidden send or permanent closure.
decision = hold.get("decision", {})
for key in ["route_first_send_permitted_now", "stage_two_send_permitted_now", "counterparty_contacted_by_this_hold"]:
    if decision.get(key) is not False:
        raise SystemExit(f"route-first branch hold decision overclaims: {key}")
if decision.get("applies_to_revision_only") is not True or decision.get("may_be_reopened_by_human_authority") is not True:
    raise SystemExit("route-first branch hold must be revision-scoped and reopenable")

observed = {b.get("source_gate_precondition") for b in hold.get("blocking_basis", [])}
if observed != required_unsatisfied:
    raise SystemExit(f"route-first branch hold blocking basis mismatch: {sorted(observed)}")
for b in hold.get("blocking_basis", []):
    if b.get("required_before_send") is not True or b.get("satisfied_now") is not False:
        raise SystemExit(f"route-first branch hold blocker overclaimed: {b.get('blocker_id')}")
    if b.get("can_be_satisfied_inside_public_release") is not False:
        raise SystemExit(f"route-first branch hold wrongly claims public release can satisfy blocker: {b.get('blocker_id')}")

nonclosure = hold.get("nonclosure_controls", {})
if nonclosure.get("no_send_may_close_first_artifact_tasks") is not False:
    raise SystemExit("route-first branch hold may not close first-artifact tasks")
needed_nonclose = {"FT-0205-FIRST-REAL-ARTIFACT-DROP", "FT-0207-FIRST-LIVE-EVIDENCE-ACQUISITION", "FT-0199-ACTUAL-LIVE-COUNTERPARTY-RESPONSE"}
if not needed_nonclose.issubset(set(nonclosure.get("do_not_close_by_narrative", []))):
    raise SystemExit("route-first branch hold missing first-artifact nonclosure controls")
if nonclosure.get("operating_board_active_count_observed") != 7 or nonclosure.get("operating_board_active_count_required") != 7:
    raise SystemExit("route-first branch hold must preserve seven-item operating board")
board = load_json(refs["operating_board"])
if board.get("queue_counts", {}).get("active_entries") != 7:
    raise SystemExit("route-first branch hold bound operating board does not have exactly seven active entries")

stage = hold.get("stage_two_controls", {})
if stage.get("stage_two_gate_ref") != refs["stage_two_authorization_gate"]:
    raise SystemExit("route-first branch hold stage-two ref mismatch")
for key in ["stage_two_remains_deferred", "willing_reply_required_or_separate_authorization"]:
    if stage.get(key) is not True:
        raise SystemExit(f"route-first branch hold stage-two control must be true: {key}")
if stage.get("route_first_hold_may_authorize_payload_send") is not False:
    raise SystemExit("route-first branch hold cannot authorize stage-two payload send")

for section in ["operational_state", "downstream_locks"]:
    for key, value in hold.get(section, {}).items():
        if value is not False:
            raise SystemExit(f"route-first branch hold {section} must remain false: {key}")
for rel in hold.get("related_surfaces", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"route-first branch hold related surface missing: {rel}")

fixture = load_json(FIXTURE_REL)
if "external-contact-route-first-branch-hold" not in fixture.get("target_filings", []):
    raise SystemExit("route-first branch hold negative fixture does not target branch hold")
if fixture.get("severity") != "critical":
    raise SystemExit("route-first branch hold negative fixture must be critical")

if Draft202012Validator is not None:
    validator = Draft202012Validator(schema)
    mut = copy.deepcopy(hold)
    mut["decision"]["route_first_send_permitted_now"] = True
    if not list(validator.iter_errors(mut)):
        raise SystemExit("schema failed to reject route-first send permission overclaim")
    mut2 = copy.deepcopy(hold)
    mut2["nonclosure_controls"]["no_send_may_close_first_artifact_tasks"] = True
    if not list(validator.iter_errors(mut2)):
        raise SystemExit("schema failed to reject no-send closing first-artifact tasks")
    mut3 = copy.deepcopy(hold)
    mut3["downstream_locks"]["may_treat_hold_as_contact"] = True
    if not list(validator.iter_errors(mut3)):
        raise SystemExit("schema failed to reject treating hold as contact")

print("audit_external_contact_route_first_branch_hold: OK")
