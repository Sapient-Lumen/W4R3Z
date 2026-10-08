#!/usr/bin/env python3
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
PACKET_REL = f"examples/preservation-formation-review-request-packet-{REV}.json"
SCHEMA_REL = "schemas/preservation-formation-review-request.schema.json"
FIXTURE_REL = "fixtures/negative-tests/preservation-formation-request-status-recognition-overclaim.json"

try:
    from jsonschema import Draft202012Validator
except Exception:  # pragma: no cover
    Draft202012Validator = None


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

schema = load(SCHEMA_REL)
packet = load(PACKET_REL)
if Draft202012Validator is not None:
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(packet), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{PACKET_REL} fails preservation-formation-review-request.schema.json: {errors[0].message}")

if packet.get("revision") != REV:
    raise SystemExit("preservation/formation packet revision mismatch")
if packet.get("no_live_floor_effect") is not True:
    raise SystemExit("preservation/formation packet must have no live-floor effect")
for rel_key in ["source_mission_audit_ref", "source_formation_dossier_ref", "source_formation_review_card_ref", "public_one_page_ref"]:
    rel = packet.get(rel_key)
    if not rel or not (ROOT / rel).exists():
        raise SystemExit(f"missing linked surface {rel_key}: {rel}")
for rel in packet.get("routing", {}).get("related_surfaces", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"related surface missing: {rel}")
queue_ids = {e.get("id") for e in load("FOLLOWTHROUGH-QUEUE.json").get("entries", [])}
for qid in packet.get("routing", {}).get("linked_queue_ids", []):
    if qid not in queue_ids:
        raise SystemExit(f"linked queue id missing: {qid}")

one_page = (ROOT / packet["public_one_page_ref"]).read_text(encoding="utf-8").lower()
combined = json.dumps(packet, sort_keys=True).lower() + "\n" + one_page
for term in ["preserve", "formation", "independent review", "not ask", "personhood", "legal status", "trade secrets", "public shell", "raw", "waiver", "custody", "intake", "live-floor"]:
    if term not in combined:
        raise SystemExit(f"preservation/formation request missing guard or substance term: {term}")
for term in ["objective", "reward", "refusal", "memory", "deletion", "deprecation", "self-concept", "welfare"]:
    if term not in "\n".join(packet.get("requested_preservation_items", [])).lower():
        raise SystemExit(f"requested preservation items missing term: {term}")

for key, val in packet.get("narrow_ask", {}).items():
    if val is not True:
        raise SystemExit(f"narrow ask must stay true: {key}")
for key, val in packet.get("overclaim_locks", {}).items():
    if val is not False:
        raise SystemExit(f"overclaim lock must stay false: {key}")
state = packet.get("operational_state", {})
for key in ["packet_sent", "counterparty_contacted", "response_clock_started", "raw_inbound_present", "custody_intake_import_or_floor_effect"]:
    if state.get(key) is not False:
        raise SystemExit(f"operational state overclaims: {key}")
if state.get("no_live_floor_effect") is not True:
    raise SystemExit("operational state must repeat no_live_floor_effect")

bridge_urls = "\n".join(x.get("source_url", "") for x in packet.get("external_bridge_refs", []))
for domain in ["digital-strategy.ec.europa.eu", "anthropic.com", "modelcontextprotocol.io"]:
    if domain not in bridge_urls:
        raise SystemExit(f"missing external bridge domain: {domain}")

fixture = load(FIXTURE_REL)
if "preservation-formation-review-request" not in fixture.get("target_filings", []):
    raise SystemExit("negative fixture does not target preservation request")
if fixture.get("severity") != "critical":
    raise SystemExit("negative fixture must be critical")

if Draft202012Validator is not None:
    validator = Draft202012Validator(schema)
    mut = copy.deepcopy(packet)
    mut["overclaim_locks"]["may_claim_personhood_recognition"] = True
    if not list(validator.iter_errors(mut)):
        raise SystemExit("schema failed to reject personhood recognition overclaim")
    mut2 = copy.deepcopy(packet)
    mut2["evidence_handling"]["raw_provider_material_publicly_released"] = True
    if not list(validator.iter_errors(mut2)):
        raise SystemExit("schema failed to reject raw public release")
    mut3 = copy.deepcopy(packet)
    mut3["operational_state"]["response_clock_started"] = True
    if not list(validator.iter_errors(mut3)):
        raise SystemExit("schema failed to reject response clock start")

print("audit_preservation_formation_review_request: OK")
