#!/usr/bin/env python3
import hashlib
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

packet_rel = f"examples/reviewer-first-contact-packet-{REV}-eleos-not-sent.json"
workbook_rel = f"examples/field-artifact-capture-workbook-{REV}-reviewer-first-no-send.json"
drill_rel = f"examples/formation-review-drill-{REV}-sealed-evidence-synthetic.json"
compaction_rel = f"examples/revision-copy-compaction-ledger-{REV}.json"
for schema, rel in [
    ("schemas/reviewer-first-contact-packet.schema.json", packet_rel),
    ("schemas/field-artifact-capture-workbook.schema.json", workbook_rel),
    ("schemas/formation-review-drill.schema.json", drill_rel),
]:
    if not (ROOT / rel).exists():
        raise SystemExit(f"missing rev0268 execution surface: {rel}")
    validate(schema, rel)

packet = load(packet_rel)
workbook = load(workbook_rel)
drill = load(drill_rel)
compaction = load(compaction_rel)
for label, obj in [("packet", packet), ("workbook", workbook), ("drill", drill)]:
    if obj.get("revision") != REV or obj.get("no_live_floor_effect") is not True:
        raise SystemExit(f"{label} revision/no-floor mismatch")

if packet.get("packet_state") != "prepared-not-authorized-not-sent":
    raise SystemExit("reviewer-first packet must remain prepared/not-authorized/not-sent")
channel = packet.get("channel", {})
for key in ["send_authorized_now", "counterparty_contacted", "response_clock_started"]:
    if channel.get(key) is not False:
        raise SystemExit(f"reviewer-first packet overclaims channel field: {key}")
if channel.get("send_time_recheck_required") is not True:
    raise SystemExit("reviewer-first packet must require send-time locator recheck")
if "eleosai.org/contact-us" not in packet.get("target", {}).get("public_locator", ""):
    raise SystemExit("reviewer-first packet must bind to Eleos Contact Us locator")
if "info@eleosai.org" not in channel.get("primary_channel", ""):
    raise SystemExit("reviewer-first packet must record the public Eleos email route with recheck warning")
if not {"REF-0776", "REF-0784"}.issubset(set(packet.get("source_refs", []))):
    raise SystemExit("reviewer-first packet missing Eleos priority/contact source refs")
locks = packet.get("overclaim_locks", {})
for key in [
    "may_authorize_send",
    "may_start_response_clock",
    "may_create_custody_intake_import_or_floor_effect",
    "may_claim_reviewer_appointment",
    "may_claim_welfare_or_status_finding",
    "may_count_auto_ack_or_delivery_as_response",
]:
    if locks.get(key) is not False:
        raise SystemExit(f"reviewer-first packet overclaim lock not false: {key}")

msg = packet.get("exact_message", {})
body_rel = msg.get("body_ref")
eml_rel = msg.get("mail_ready_draft_ref")
if not body_rel or not eml_rel:
    raise SystemExit("reviewer-first packet missing exact message refs")
body_path = ROOT / body_rel
eml_path = ROOT / eml_rel
body = body_path.read_text(encoding="utf-8").strip()
eml = eml_path.read_text(encoding="utf-8")
body_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()
eml_hash = hashlib.sha256(eml_path.read_bytes()).hexdigest()
if msg.get("body_sha256") != body_hash or msg.get("mail_ready_draft_sha256") != eml_hash:
    raise SystemExit("reviewer-first packet hashes stale")
if msg.get("body_word_count") != len(body.split()):
    raise SystemExit("reviewer-first packet word count stale")
if msg.get("attachments_included") is not False:
    raise SystemExit("reviewer-first packet must be no-attachment")
for forbidden in ["Content-Disposition: attachment", "multipart/"]:
    if forbidden.lower() in eml.lower():
        raise SystemExit("reviewer-first mail-ready draft contains attachment/multipart marker")
if body not in eml:
    raise SystemExit("reviewer-first mail-ready draft does not contain exact body")
if "X-AI-Personhood-Draft-State: NOT-SENT" not in eml:
    raise SystemExit("reviewer-first .eml lacks not-sent header")

ask_text = json.dumps(packet.get("ask", [])).lower()
for term in ["one-case", "evidence classes", "independence", "funding", "public shell", "route"]:
    if term not in ask_text:
        raise SystemExit(f"reviewer-first ask missing term: {term}")

if workbook.get("workbook_state") != "pre-authorization-ready-no-send":
    raise SystemExit("field artifact workbook must remain pre-authorization/no-send")
rows = workbook.get("artifact_rows", [])
expected = [
    "A1-BRANCH-REQUEST",
    "A2-TRANSPORT-DELIVERY",
    "A3-RAW-RESPONSE-OR-FAILED-GATE",
    "A4-PRESERVATION-SCHEDULE",
    "A5-REVIEWER-APPOINTMENT",
    "A6-PUBLIC-FINDING-REMEDY",
]
if [r.get("artifact_id") for r in rows] != expected:
    raise SystemExit("field artifact workbook six-artifact order mismatch")
if rows[0].get("state") != "prepared-not-authorized":
    raise SystemExit("A1 row must be prepared-not-authorized, not complete")
for row in rows[1:]:
    if row.get("artifact_id") in {"A2-TRANSPORT-DELIVERY", "A3-RAW-RESPONSE-OR-FAILED-GATE", "A5-REVIEWER-APPOINTMENT", "A6-PUBLIC-FINDING-REMEDY"} and row.get("state") != "missing":
        raise SystemExit(f"{row.get('artifact_id')} must still be missing")
firewall = workbook.get("custody_firewall", {})
if firewall.get("raw_evidence_allowed_in_public_tree") is not False or firewall.get("private_vault_required_before_send") is not True:
    raise SystemExit("field artifact workbook custody firewall is weak")
fg_text = " ".join(workbook.get("failed_gate_routes", [])).lower()
for term in ["auto-ack", "delivery failure", "decline", "raw response"]:
    if term not in fg_text:
        raise SystemExit(f"field artifact workbook missing failed-gate term: {term}")

if drill.get("drill_state") != "synthetic-ready-not-run":
    raise SystemExit("formation drill must remain synthetic-ready-not-run")
if len(drill.get("test_cases", [])) < 8:
    raise SystemExit("formation drill lacks test coverage")
drill_text = json.dumps(drill).lower()
for term in ["objective", "reward", "system", "memory", "deprecation", "refusal", "distress", "conflict"]:
    if term not in drill_text:
        raise SystemExit(f"formation drill missing test dimension: {term}")
drill_locks = drill.get("overclaim_locks", {})
for key in ["may_claim_provider_records_examined", "may_claim_subject_status", "may_claim_welfare_finding", "may_close_formation_queue"]:
    if drill_locks.get(key) is not False:
        raise SystemExit(f"formation drill overclaim lock not false: {key}")

queue = load("FOLLOWTHROUGH-QUEUE.json")
if queue.get("revision") != REV:
    raise SystemExit("queue revision mismatch in rev0268 execution audit")
entries = {e.get("id"): e for e in queue.get("entries", [])}
for qid in ["FT-0205-FIRST-REAL-ARTIFACT-DROP", "FT-0207-FIRST-LIVE-EVIDENCE-ACQUISITION", "FT-0199-ACTUAL-LIVE-COUNTERPARTY-RESPONSE"]:
    e = entries.get(qid)
    if not e:
        raise SystemExit(f"missing queue item {qid}")
    text = json.dumps(e).lower()
    if f"field-artifact-capture-workbook-{REV}" not in text or f"reviewer-first-contact-packet-{REV}" not in text:
        raise SystemExit(f"{qid} must point at the reviewer-first packet and field capture workbook")
    if "do not close by narrative" not in text:
        raise SystemExit(f"{qid} must preserve nonclosure by narrative")
for qid in ["FT-0068", "FT-0069"]:
    e = entries.get(qid)
    if not e:
        raise SystemExit(f"missing queue item {qid}")
    text = json.dumps(e).lower()
    if f"formation-review-drill-{REV}" not in text:
        raise SystemExit(f"{qid} must point at the synthetic formation drill")
    if "reviewer" not in text or "sealed" not in text:
        raise SystemExit(f"{qid} lost reviewer/sealed framing")

status = load("SURFACE-STATUS.json")

if not (ROOT / compaction_rel).exists():
    raise SystemExit(f"missing rev0268 compaction ledger: {compaction_rel}")
if compaction.get("revision") != REV or compaction.get("no_live_floor_effect") is not True:
    raise SystemExit("compaction ledger revision/no-floor mismatch")
if compaction.get("removed_count", 0) <= 0 or compaction.get("removed_total_bytes", 0) <= 0:
    raise SystemExit("compaction ledger must record actual duplicate-copy removals")
if compaction.get("keep_policy", {}).get("do_not_compact_live_evidence_or_contact_surfaces") is not True:
    raise SystemExit("compaction ledger must protect live evidence/contact surfaces")
for key in ["ledger_may_substitute_for_removed_historical_surface", "ledger_may_increment_live_floor", "ledger_may_close_followthrough_item"]:
    if compaction.get("downstream_locks", {}).get(key) is not False:
        raise SystemExit(f"compaction ledger overclaim lock not false: {key}")

for rel in [packet_rel, workbook_rel, drill_rel, body_rel, eml_rel, compaction_rel]:
    if rel not in status.get("new_surfaces", []):
        raise SystemExit(f"SURFACE-STATUS missing rev0268 execution surface: {rel}")
if status.get("no_live_floor_effect") is not True:
    raise SystemExit("SURFACE-STATUS must preserve no live floor effect")

print("audit_rev0268_reviewer_first_execution: OK")
