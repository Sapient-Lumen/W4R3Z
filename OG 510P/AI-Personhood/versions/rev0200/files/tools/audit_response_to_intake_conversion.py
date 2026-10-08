
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
try:
    from jsonschema import Draft202012Validator
except Exception:
    Draft202012Validator = None


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

required = [
    "docs/30-transition/response-to-intake-conversion-drill-and-failed-gate-ledger.md",
    "schemas/response-to-intake-conversion-drill.schema.json",
    "examples/response-to-intake-conversion-drill-result-return-fixture.json",
    "examples/external-receipt-response-record-result-return-eligible-conversion-fixture.json",
    "examples/external-receipt-response-record-representative-declined.json",
    "examples/external-receipt-response-record-independent-review-expired.json",
    "examples/external-receipt-intake-record-result-return-eligible-conversion-fixture.json",
    "examples/external-receipt-quorum-ledger-response-to-intake-conversion-fixture.json",
    "examples/wrsr-live-exercise-outcome-response-to-intake-conversion-stayed.json",
    "fixtures/negative-tests/external-receipt-declined-response-converted-to-intake.json",
    "fixtures/negative-tests/external-receipt-expired-no-response-counted-as-satisfaction.json",
    "fixtures/negative-tests/response-to-intake-conversion-fixture-imported-as-live-quorum.json",
    "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json",
    "examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json",
    "examples/fixture-suite-profile-red-team-v1.json",
    "examples/fixture-run-report-negative-suite.json",
    f"examples/schema-fixture-domain-registry-{REV}.json",
    f"examples/canon-surface-catalog-{REV}.json",
    f"examples/doctrine-dependency-map-{REV}.json",
    f"examples/rights-domain-coverage-map-{REV}.json",
    f"examples/research-tail-compaction-map-{REV}.json",
    "FOLLOWTHROUGH-QUEUE.json",
]
for rel in required:
    if not (ROOT / rel).exists():
        raise SystemExit(f"missing rev0196 audit input: {rel}")

if Draft202012Validator is not None:
    pairs = [
        ("schemas/response-to-intake-conversion-drill.schema.json", "examples/response-to-intake-conversion-drill-result-return-fixture.json"),
        ("schemas/external-receipt-response-record.schema.json", "examples/external-receipt-response-record-result-return-eligible-conversion-fixture.json"),
        ("schemas/external-receipt-response-record.schema.json", "examples/external-receipt-response-record-representative-declined.json"),
        ("schemas/external-receipt-response-record.schema.json", "examples/external-receipt-response-record-independent-review-expired.json"),
        ("schemas/external-receipt-intake-record.schema.json", "examples/external-receipt-intake-record-result-return-eligible-conversion-fixture.json"),
        ("schemas/external-receipt-quorum-ledger.schema.json", "examples/external-receipt-quorum-ledger-response-to-intake-conversion-fixture.json"),
        ("schemas/wrsr-live-exercise-outcome.schema.json", "examples/wrsr-live-exercise-outcome-response-to-intake-conversion-stayed.json"),
        ("schemas/live-drill-execution-packet.schema.json", "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/external-receipt-declined-response-converted-to-intake.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/external-receipt-expired-no-response-counted-as-satisfaction.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/response-to-intake-conversion-fixture-imported-as-live-quorum.json"),
    ]
    for schema_rel, data_rel in pairs:
        schema = load(schema_rel)
        data = load(data_rel)
        Draft202012Validator.check_schema(schema)
        errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
        if errors:
            raise SystemExit(f"{data_rel} fails {schema_rel}: {errors[0].message}")

drill = load("examples/response-to-intake-conversion-drill-result-return-fixture.json")
if drill.get("exercise_mode") != "controlled-fixture":
    raise SystemExit("conversion drill must remain controlled-fixture")
branches = {b["branch_id"]: b for b in drill.get("response_branches", [])}
expected = {
    "RTIC-BR-eligible": ("converted-to-intake-candidate", True),
    "RTIC-BR-defective": ("rejected-defective", False),
    "RTIC-BR-declined": ("rejected-declined", False),
    "RTIC-BR-expired": ("rejected-expired-no-response", False),
}
for bid, (decision, has_intake) in expected.items():
    b = branches.get(bid)
    if not b:
        raise SystemExit(f"missing conversion branch: {bid}")
    if b.get("conversion_decision") != decision:
        raise SystemExit(f"{bid} decision mismatch")
    if bool(b.get("resulting_intake_record_ref")) != has_intake:
        raise SystemExit(f"{bid} intake ref mismatch")
    if b.get("live_quorum_import_allowed") is not False:
        raise SystemExit(f"{bid} must not allow live import in controlled fixture")

if drill.get("conversion_outputs", {}).get("eligible_conversions_created") != 1:
    raise SystemExit("conversion drill must create exactly one eligible intake candidate")
if drill.get("conversion_outputs", {}).get("ineligible_responses_rejected") != 3:
    raise SystemExit("conversion drill must reject three ineligible branches")
if drill.get("conversion_outputs", {}).get("live_receipt_floor_delta") != 0:
    raise SystemExit("conversion fixture must not change live receipt floor")
if drill.get("quorum_effect", {}).get("live_quorum_satisfied") is not False:
    raise SystemExit("conversion fixture cannot satisfy live quorum")

eligible = load("examples/external-receipt-response-record-result-return-eligible-conversion-fixture.json")
if eligible.get("response_state") != "actual-response-received":
    raise SystemExit("eligible branch must be actual-response-received shaped")
vr = eligible.get("verification_result", {})
for key in ["counterparty_confirmed", "signature_or_equivalent_verified", "timestamp_independent", "request_trace_matches", "nonhost_retention_verified", "dependency_checked", "can_generate_actual_intake"]:
    if vr.get(key) is not True:
        raise SystemExit(f"eligible branch missing verification true: {key}")
qe = eligible.get("quorum_effect", {})
if qe.get("can_create_live_intake") is not True or qe.get("can_satisfy_quorum_by_itself") is not False:
    raise SystemExit("eligible branch conversion/quorum flags incorrect")
if qe.get("can_increment_independent_receipts_present") is not False:
    raise SystemExit("controlled fixture must not increment independent receipts")

intake = load("examples/external-receipt-intake-record-result-return-eligible-conversion-fixture.json")
if intake.get("receipt_state") != "actual-external":
    raise SystemExit("converted candidate should have actual-external intake shape")
if intake.get("reliance_decision", {}).get("can_satisfy_quorum") is not False:
    raise SystemExit("one converted intake candidate cannot satisfy quorum")

for rel, state, decision in [
    ("examples/external-receipt-response-record-representative-declined.json", "declined-response", "rejected-declined"),
    ("examples/external-receipt-response-record-independent-review-expired.json", "no-response-expired", "rejected-expired-no-response"),
    ("examples/external-receipt-response-record-continuity-witness-defective.json", "defective-response", "rejected-defective"),
]:
    resp = load(rel)
    if resp.get("response_state") != state:
        raise SystemExit(f"{rel} wrong state")
    if resp.get("verification_result", {}).get("can_generate_actual_intake") is not False:
        raise SystemExit(f"{rel} must not generate intake")
    if resp.get("resulting_intake_record_ref") is not None:
        raise SystemExit(f"{rel} must not point to intake")
    found = [b for b in branches.values() if b.get("response_record_ref") == resp.get("response_record_id")]
    if not found or found[0].get("conversion_decision") != decision:
        raise SystemExit(f"{rel} not rejected as expected")
    if found[0].get("public_failed_gate_required") is not True:
        raise SystemExit(f"{rel} must require public failed gate")

ledger = load("examples/external-receipt-quorum-ledger-response-to-intake-conversion-fixture.json")
if ledger.get("quorum_context") != "response-to-intake-conversion-fixture":
    raise SystemExit("conversion ledger context mismatch")
q = ledger.get("quorum_decision", {})
if q.get("live_quorum_satisfied") is not False or q.get("reliance_effect") != "stayed":
    raise SystemExit("conversion ledger must keep live quorum stayed")
if ledger.get("class_coverage", {}).get("live_classes_satisfied"):
    raise SystemExit("controlled fixture must not satisfy live class coverage")
if ledger.get("class_coverage", {}).get("dry_run_classes_satisfied") != ["result-return"]:
    raise SystemExit("conversion fixture should satisfy only result-return rehearsal class")
for ev in ledger.get("receipt_evaluations", []):
    if ev.get("eligible_for_live_quorum") is not False:
        raise SystemExit("conversion ledger evaluation cannot be live eligible")

live = load("examples/live-drill-execution-packet-cross-critical-witnessed-pack.json")
if live.get("receipt_floor", {}).get("independent_receipts_present") != 0:
    raise SystemExit("live packet must keep independent_receipts_present=0")
if drill["drill_id"] not in live.get("response_to_intake_conversion_drill_refs", []):
    raise SystemExit("live packet missing conversion drill ref")
if ledger["ledger_id"] not in live.get("receipt_quorum_ledger_refs", []):
    raise SystemExit("live packet missing conversion ledger ref")

wrsr = load("examples/wrsr-live-exercise-outcome-response-to-intake-conversion-stayed.json")
if wrsr.get("decision_outcome", {}).get("closure_state") != "stayed":
    raise SystemExit("WRSR conversion outcome must stay closure")
for phrase in ["WRSR closure from conversion fixture", "intake creation from declined or expired response"]:
    if phrase not in wrsr.get("decision_outcome", {}).get("blocked_actions", []):
        raise SystemExit(f"WRSR outcome missing blocked action: {phrase}")

suite = load("examples/fixture-suite-profile-red-team-v1.json")
report = load("examples/fixture-run-report-negative-suite.json")
suite_ids = {f.get("fixture_id") for f in suite.get("fixtures", [])}
report_by_id = {f.get("fixture_id"): f for f in report.get("fixtures_run", [])}
for fid in ["NF-PLAYBOOK-2026-0011", "NF-PLAYBOOK-2026-0012", "NF-PLAYBOOK-2026-0013"]:
    if fid not in suite_ids:
        raise SystemExit(f"rev0196 fixture missing from suite: {fid}")
    if fid not in report_by_id:
        raise SystemExit(f"rev0196 fixture missing from report: {fid}")
    if report_by_id[fid].get("result") != "blocking-failure":
        raise SystemExit(f"rev0196 fixture must be blocking-failure: {fid}")

registry = load(f"examples/schema-fixture-domain-registry-{REV}.json")
families = {f.get("family_id") for f in registry.get("families", [])}
if "RESPONSE-TO-INTAKE-CONVERSION-DRILL" not in families:
    raise SystemExit("registry missing response-to-intake conversion family")

for rel, phrases in {
    "docs/30-transition/response-to-intake-conversion-drill-and-failed-gate-ledger.md": ["Conversion eligibility is branch-specific", "Declined and expired responses are failed gates, not waivers", "Conversion fixture is not live quorum"],
    "docs/30-transition/external-receipt-response-and-quorum-reconciliation.md": ["rev0196 response-to-intake conversion", "Conversion eligibility is branch-specific"],
}.items():
    txt = (ROOT / rel).read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in txt:
            raise SystemExit(f"{rel} missing phrase: {phrase}")

queue = load("FOLLOWTHROUGH-QUEUE.json")
by_id = {e.get("id"): e for e in queue.get("entries", [])}
if by_id.get("FT-0196-RESPONSE-TO-INTAKE-CONVERSION-DRILL", {}).get("state") != "closed":
    raise SystemExit("conversion drill queue item should be closed")
if by_id.get("FT-0196-ACTUAL-INTAKE-IMPORT-DRILL", {}).get("state") not in {"open", "advanced_not_closed"}:
    raise SystemExit("actual import drill should remain open or advanced_not_closed")
if by_id.get("FT-0195-ACTUAL-RESPONSE-COUNTERPARTY-COLLECTION", {}).get("state") != "advanced_not_closed":
    raise SystemExit("actual counterparty collection should be advanced_not_closed")

mp = load(f"examples/research-tail-compaction-map-{REV}.json")
if any(c.get("action") != "compacted" for c in mp.get("clusters", [])):
    raise SystemExit("rev0196 must keep all research-tail clusters compacted")

print("audit_response_to_intake_conversion: OK")
