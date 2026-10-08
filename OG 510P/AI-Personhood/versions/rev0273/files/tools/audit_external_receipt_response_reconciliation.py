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
    "docs/30-transition/external-receipt-response-and-quorum-reconciliation.md",
    "schemas/external-receipt-response-record.schema.json",
    "examples/external-receipt-response-record-result-return-steward-dryrun.json",
    "examples/external-receipt-response-record-continuity-witness-defective.json",
    "examples/external-receipt-quorum-ledger-response-reconciliation-dryrun.json",
    "examples/wrsr-live-exercise-outcome-response-reconciliation-stayed.json",
    "fixtures/negative-tests/external-receipt-response-unverified-counted-as-intake.json",
    "fixtures/negative-tests/external-receipt-single-class-counted-as-quorum.json",
    "examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json",
    "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json",
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
        raise SystemExit(f"missing rev0195 audit input: {rel}")

if Draft202012Validator is not None:
    pairs = [
        ("schemas/external-receipt-response-record.schema.json", "examples/external-receipt-response-record-result-return-steward-dryrun.json"),
        ("schemas/external-receipt-response-record.schema.json", "examples/external-receipt-response-record-continuity-witness-defective.json"),
        ("schemas/external-receipt-quorum-ledger.schema.json", "examples/external-receipt-quorum-ledger-response-reconciliation-dryrun.json"),
        ("schemas/wrsr-live-exercise-outcome.schema.json", "examples/wrsr-live-exercise-outcome-response-reconciliation-stayed.json"),
        ("schemas/external-receipt-request-packet.schema.json", "examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json"),
        ("schemas/live-drill-execution-packet.schema.json", "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/external-receipt-response-unverified-counted-as-intake.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/external-receipt-single-class-counted-as-quorum.json"),
    ]
    for schema_rel, data_rel in pairs:
        schema = load(schema_rel)
        data = load(data_rel)
        Draft202012Validator.check_schema(schema)
        errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
        if errors:
            raise SystemExit(f"{data_rel} fails {schema_rel}: {errors[0].message}")

resp = load("examples/external-receipt-response-record-result-return-steward-dryrun.json")
if resp.get("response_state") != "high-fidelity-dry-run-response":
    raise SystemExit("result-return response must remain high-fidelity dry-run")
qe = resp.get("quorum_effect", {})
for key in ["can_create_live_intake", "can_satisfy_quorum_by_itself", "can_increment_independent_receipts_present"]:
    if qe.get(key) is not False:
        raise SystemExit(f"dry-run response must not set {key}=true")
if qe.get("live_weight") != 0 or qe.get("dry_run_weight", 0) <= 0:
    raise SystemExit("dry-run response weights incorrect")
if resp.get("verification_result", {}).get("can_generate_actual_intake") is not False:
    raise SystemExit("dry-run response cannot generate actual intake")

bad = load("examples/external-receipt-response-record-continuity-witness-defective.json")
if bad.get("response_state") != "defective-response":
    raise SystemExit("defective response must stay defective")
if bad.get("resulting_intake_record_ref") is not None:
    raise SystemExit("defective response cannot point to resulting intake")
if bad.get("verification_result", {}).get("can_generate_actual_intake") is not False:
    raise SystemExit("defective response cannot generate intake")
if bad.get("quorum_effect", {}).get("reliance_effect") != "blocked":
    raise SystemExit("defective response should block response reliance")

ledger = load("examples/external-receipt-quorum-ledger-response-reconciliation-dryrun.json")
if resp["response_record_id"] not in ledger.get("response_record_refs", []):
    raise SystemExit("ledger missing dry-run response ref")
if bad["response_record_id"] not in ledger.get("response_record_refs", []):
    raise SystemExit("ledger missing defective response ref")
q = ledger.get("quorum_decision", {})
if q.get("live_quorum_satisfied") is not False or q.get("dry_run_quorum_satisfied") is not False:
    raise SystemExit("response reconciliation must not satisfy live or dry-run quorum")
if ledger.get("class_coverage", {}).get("live_classes_satisfied"):
    raise SystemExit("response reconciliation cannot satisfy live classes")
if ledger.get("class_coverage", {}).get("dry_run_classes_satisfied") != ["result-return"]:
    raise SystemExit("response reconciliation should satisfy only result-return dry-run class")
for ev in ledger.get("receipt_evaluations", []):
    if ev.get("eligible_for_live_quorum") is not False:
        raise SystemExit("response reconciliation evaluation cannot be live-eligible")

request = load("examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json")
if request.get("request_state") != "ready-to-send":
    raise SystemExit("request packet must remain ready-to-send")
for rid in [resp["response_record_id"], bad["response_record_id"]]:
    if rid not in request.get("linked_response_records", []):
        raise SystemExit(f"request missing response record ref: {rid}")

live = load("examples/live-drill-execution-packet-cross-critical-witnessed-pack.json")
if live.get("receipt_floor", {}).get("independent_receipts_present") != 0:
    raise SystemExit("response records cannot increment independent_receipts_present")
for rid in [resp["response_record_id"], bad["response_record_id"]]:
    if rid not in live.get("external_receipt_response_record_refs", []):
        raise SystemExit(f"live packet missing response record ref: {rid}")
if ledger.get("ledger_id") not in live.get("receipt_quorum_ledger_refs", []):
    raise SystemExit("live packet missing response reconciliation ledger ref")

wrsr = load("examples/wrsr-live-exercise-outcome-response-reconciliation-stayed.json")
if wrsr.get("decision_outcome", {}).get("closure_state") != "stayed":
    raise SystemExit("response reconciliation WRSR outcome must stay closure")
for phrase in ["WRSR closure from response receipt alone", "actual intake from defective or dry-run response"]:
    if phrase not in wrsr.get("decision_outcome", {}).get("blocked_actions", []):
        raise SystemExit(f"WRSR outcome missing blocked action: {phrase}")

suite = load("examples/fixture-suite-profile-red-team-v1.json")
report = load("examples/fixture-run-report-negative-suite.json")
suite_ids = {f.get("fixture_id") for f in suite.get("fixtures", [])}
report_by_id = {f.get("fixture_id"): f for f in report.get("fixtures_run", [])}
for fid in ["NF-PLAYBOOK-2026-0009", "NF-PLAYBOOK-2026-0010"]:
    if fid not in suite_ids:
        raise SystemExit(f"rev0195 fixture missing from suite: {fid}")
    if fid not in report_by_id:
        raise SystemExit(f"rev0195 fixture missing from report: {fid}")
    if report_by_id[fid].get("result") != "blocking-failure":
        raise SystemExit(f"rev0195 fixture must be blocking-failure: {fid}")

registry = load(f"examples/schema-fixture-domain-registry-{REV}.json")
families = {f.get("family_id") for f in registry.get("families", [])}
if "EXTERNAL-RECEIPT-RESPONSE-RECORD" not in families:
    raise SystemExit("registry missing response-record family")

for rel, phrases in {
    "docs/30-transition/external-receipt-response-and-quorum-reconciliation.md": ["Response received is not quorum", "One verified class is not live reliance", "Declined or no-response is evidence, not satisfaction"],
    "docs/30-transition/result-return-receipt-and-live-request-kit.md": ["rev0195 response reconciliation", "Response received is not quorum"],
    "docs/30-transition/representative-rerb-receipt-chain-and-quorum-ledger.md": ["rev0195 response reconciliation"],
}.items():
    txt = (ROOT / rel).read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in txt:
            raise SystemExit(f"{rel} missing phrase: {phrase}")

mp = load(f"examples/research-tail-compaction-map-{REV}.json")
if any(c.get("action") != "compacted" for c in mp.get("clusters", [])):
    raise SystemExit("rev0195 must keep all research-tail clusters compacted")

queue = load("FOLLOWTHROUGH-QUEUE.json")
by_id = {e.get("id"): e for e in queue.get("entries", [])}
if by_id.get("FT-0195-RESPONSE-RECORD-OBJECTIZATION", {}).get("state") != "closed":
    raise SystemExit("response record objectization should be closed")
if by_id.get("FT-0194-ACTUAL-RESULT-RETURN-RECEIPT-COLLECTION", {}).get("state") != "advanced_not_closed":
    raise SystemExit("actual result-return receipt collection should be advanced_not_closed")
if by_id.get("FT-0195-ACTUAL-RESPONSE-COUNTERPARTY-COLLECTION", {}).get("state") not in {"open", "advanced_not_closed"}:
    raise SystemExit("actual response counterparty collection should remain open or advanced_not_closed")

print("audit_external_receipt_response_reconciliation: OK")
