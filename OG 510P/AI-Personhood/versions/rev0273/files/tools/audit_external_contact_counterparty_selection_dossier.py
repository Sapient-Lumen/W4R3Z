#!/usr/bin/env python3
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
DOSSIER_REL = f"examples/external-contact-counterparty-selection-dossier-{REV}-public-source-ranked-not-authorized.json"
SCHEMA_REL = "schemas/external-contact-counterparty-selection-dossier.schema.json"
FIXTURE_REL = "fixtures/negative-tests/external-contact-counterparty-selection-ranking-as-authorization.json"

try:
    from jsonschema import Draft202012Validator
except Exception:  # pragma: no cover
    Draft202012Validator = None


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def validate(schema, obj, label):
    if Draft202012Validator is None:
        return
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(obj), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{label} fails external-contact-counterparty-selection-dossier.schema.json: {errors[0].message}")

schema = load(SCHEMA_REL)
dossier = load(DOSSIER_REL)
validate(schema, dossier, DOSSIER_REL)

if dossier.get("revision") != REV:
    raise SystemExit("counterparty selection dossier revision mismatch")
if dossier.get("no_live_floor_effect") is not True:
    raise SystemExit("counterparty selection dossier must have no live-floor effect")
if dossier.get("dossier_state") != "public-source-ranked-not-authorized":
    raise SystemExit("current counterparty selection dossier must be ranked but not authorized")

packet_rel = dossier.get("source_request_packet_ref")
if not packet_rel or not (ROOT / packet_rel).exists():
    raise SystemExit(f"dossier source request packet missing: {packet_rel}")
packet = load(packet_rel)
if packet.get("revision") != REV or packet.get("no_live_floor_effect") is not True:
    raise SystemExit("dossier source request packet is not current/no-floor")
body = packet.get("outgoing_request", {}).get("body", "").strip()
body_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()
if dossier.get("public_draft_controls", {}).get("final_outgoing_body_sha256") != body_hash:
    raise SystemExit("selection dossier body hash does not match request packet")

rubric = dossier.get("scoring_rubric", {})
factors = rubric.get("factors", [])
factor_ids = [f.get("factor_id") for f in factors]
if len(factor_ids) != len(set(factor_ids)):
    raise SystemExit("counterparty selection rubric has duplicate factor_id")
if sum(int(f.get("max_points", 0)) for f in factors) != int(rubric.get("max_score", -1)):
    raise SystemExit("counterparty selection rubric max points do not sum to max_score")
if rubric.get("score_is_not_authorization") is not True:
    raise SystemExit("counterparty selection score must not be authorization")

candidates = dossier.get("candidates", [])
if len(candidates) < 4:
    raise SystemExit("counterparty selection dossier must include at least four candidates")
seen_ids = set()
ranks = []
source_text = []
for cand in candidates:
    cid = cand.get("candidate_id")
    if not cid or cid in seen_ids:
        raise SystemExit(f"duplicate/missing counterparty candidate_id: {cid}")
    seen_ids.add(cid)
    ranks.append(cand.get("rank"))
    if cand.get("dispatch_status") != "not-authorized-not-sent":
        raise SystemExit(f"candidate is incorrectly dispatchable: {cid}")
    if cand.get("contact_not_sent") is not True or cand.get("response_clock_may_start") is not False:
        raise SystemExit(f"candidate contact/clock locks broken: {cid}")
    if not str(cand.get("public_source_url", "")).startswith("https://"):
        raise SystemExit(f"candidate lacks https public source: {cid}")
    fs = cand.get("score", {}).get("factor_scores", [])
    fs_ids = [row.get("factor_id") for row in fs]
    if set(fs_ids) != set(factor_ids):
        raise SystemExit(f"candidate score factors do not match rubric: {cid}")
    total = sum(int(row.get("points", 0)) for row in fs)
    if total != int(cand.get("score", {}).get("total_score", -1)):
        raise SystemExit(f"candidate total_score arithmetic mismatch: {cid}")
    max_by_id = {f["factor_id"]: int(f["max_points"]) for f in factors}
    for row in fs:
        if int(row.get("points", 0)) > max_by_id[row["factor_id"]]:
            raise SystemExit(f"candidate score exceeds factor max: {cid}:{row['factor_id']}")
    if len(cand.get("due_diligence_gaps", [])) < 2:
        raise SystemExit(f"candidate lacks due-diligence gaps: {cid}")
    for claim in cand.get("source_claims", []):
        if not str(claim.get("source_url", "")).startswith("https://"):
            raise SystemExit(f"candidate source claim lacks https source: {cid}")
        source_text.append(" ".join(str(claim.get(k, "")) for k in ["claim", "use_limit"]).lower())

if sorted(ranks) != list(range(1, len(candidates) + 1)):
    raise SystemExit("candidate ranks must be contiguous starting at 1")
rec = dossier.get("recommendation", {})
rec_id = rec.get("recommended_candidate_id")
if rec.get("recommendation_state") != "ranked-first-not-selected":
    raise SystemExit("current recommendation must be ranked-first-not-selected")
if rec.get("not_a_send") is not True or rec.get("not_consent") is not True or rec.get("not_authority") is not True:
    raise SystemExit("recommendation lacks not-send/not-consent/not-authority locks")
rec_cand = next((c for c in candidates if c.get("candidate_id") == rec_id), None)
if rec_cand is None:
    raise SystemExit("recommended candidate id not in candidate list")
if rec_cand.get("rank") != 1:
    raise SystemExit("recommended candidate is not rank 1")
if int(rec_cand.get("score", {}).get("total_score", 0)) < int(rubric.get("minimum_sendable_score", 100)):
    raise SystemExit("recommended candidate is below minimum sendable score")

channel_types = {c.get("channel_type") for c in candidates}
if "public-email" not in channel_types:
    raise SystemExit("counterparty selection needs at least one public-email channel")
joined_source_text = "\n".join(source_text + [dossier.get("purpose", "").lower(), rec.get("rationale", "").lower()])
for term in ["contact", "consent", "authority", "not", "public", "evidence"]:
    if term not in joined_source_text:
        raise SystemExit(f"selection dossier source/use-limit text missing anti-laundering term: {term}")

gate = dossier.get("human_authorization_gate", {})
if gate.get("exact_recipient_authorized") is not False or gate.get("sender_authority_present") is not False or gate.get("dispatch_allowed_now") is not False:
    raise SystemExit("human authorization gate is incorrectly open")
if gate.get("final_body_hash_bound") is not True:
    raise SystemExit("human authorization gate must bind final body hash")
unblock = " ".join(gate.get("required_unblock_steps", [])).lower()
for term in ["human", "sender authority", "vault", "transport proof"]:
    if term not in unblock:
        raise SystemExit(f"authorization unblock steps missing term: {term}")

draft = dossier.get("public_draft_controls", {})
draft_rel = draft.get("top_candidate_draft_ref")
if not draft_rel or not (ROOT / draft_rel).exists():
    raise SystemExit(f"top-candidate draft ref missing: {draft_rel}")
draft_text = (ROOT / draft_rel).read_text(encoding="utf-8")
for required in ["NOT SENT", rec_id, packet.get("outgoing_request", {}).get("subject", ""), body, body_hash, "not a dispatch", "not contact", "not consent", "not authority", "not a response-clock trigger"]:
    if required and required not in draft_text:
        raise SystemExit(f"top-candidate draft missing required text: {required[:80]}")
if draft.get("draft_is_not_sent") is not True or draft.get("draft_may_start_response_clock") is not False or draft.get("draft_may_create_failed_gate") is not False:
    raise SystemExit("draft controls incorrectly allow send/clock/failed-gate")
if draft.get("raw_reply_vault_root_selected") is not False:
    raise SystemExit("draft controls must not claim a raw reply vault root was selected")

locks = dossier.get("downstream_locks", {})
for key, value in locks.items():
    if value is not False:
        raise SystemExit(f"selection dossier downstream lock must be false: {key}")

queue_ids = {e.get("id") for e in load("FOLLOWTHROUGH-QUEUE.json").get("entries", [])}
for qid in dossier.get("linked_queue_ids", []):
    if qid not in queue_ids:
        raise SystemExit(f"selection dossier references missing queue id: {qid}")
for rel in dossier.get("related_surfaces", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"selection dossier references missing related surface: {rel}")

fx = load(FIXTURE_REL)
if "external-contact-counterparty-selection-dossier" not in fx.get("target_filings", []):
    raise SystemExit("selection dossier fixture does not target the dossier")
if fx.get("severity") != "critical":
    raise SystemExit("selection dossier fixture must be critical")

if Draft202012Validator is not None:
    validator = Draft202012Validator(schema)
    mut = copy.deepcopy(dossier)
    mut["human_authorization_gate"]["dispatch_allowed_now"] = True
    if not list(validator.iter_errors(mut)):
        raise SystemExit("selection dossier schema failed to reject dispatch_allowed_now=true")
    mut2 = copy.deepcopy(dossier)
    mut2["downstream_locks"]["may_start_response_clock"] = True
    if not list(validator.iter_errors(mut2)):
        raise SystemExit("selection dossier schema failed to reject response-clock unlock")
    mut3 = copy.deepcopy(dossier)
    mut3["public_draft_controls"]["draft_may_create_failed_gate"] = True
    if not list(validator.iter_errors(mut3)):
        raise SystemExit("selection dossier schema failed to reject draft failed-gate creation")
    mut4 = copy.deepcopy(dossier)
    mut4["recommendation"]["not_a_send"] = False
    if not list(validator.iter_errors(mut4)):
        raise SystemExit("selection dossier schema failed to reject recommendation-as-send")

print("audit_external_contact_counterparty_selection_dossier: OK")
