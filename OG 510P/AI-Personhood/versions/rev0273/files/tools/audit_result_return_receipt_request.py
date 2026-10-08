
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
    "docs/30-transition/result-return-receipt-and-live-request-kit.md",
    "schemas/wrsr-result-return-receipt.schema.json",
    "examples/wrsr-result-return-receipt-subject-readable-dryrun-stayed.json",
    "schemas/external-receipt-request-packet.schema.json",
    "examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json",
    "examples/external-receipt-intake-record-result-return-dryrun.json",
    "examples/external-receipt-quorum-ledger-wrsr-result-return-dryrun.json",
    "examples/wrsr-live-exercise-outcome-result-return-dryrun-stayed.json",
    "fixtures/negative-tests/external-receipt-request-counted-as-receipt.json",
    "fixtures/negative-tests/wrsr-result-return-internal-only-mislabeled-closure.json",
    "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json",
    "examples/external-receipt-simulation-bundle-cross-critical-precontact.json",
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
        raise SystemExit(f"missing rev0194 audit input: {rel}")

if Draft202012Validator is not None:
    for schema_rel, data_rel in [
        ("schemas/wrsr-result-return-receipt.schema.json", "examples/wrsr-result-return-receipt-subject-readable-dryrun-stayed.json"),
        ("schemas/external-receipt-request-packet.schema.json", "examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json"),
        ("schemas/external-receipt-intake-record.schema.json", "examples/external-receipt-intake-record-result-return-dryrun.json"),
        ("schemas/external-receipt-quorum-ledger.schema.json", "examples/external-receipt-quorum-ledger-wrsr-result-return-dryrun.json"),
        ("schemas/wrsr-live-exercise-outcome.schema.json", "examples/wrsr-live-exercise-outcome-result-return-dryrun-stayed.json"),
        ("schemas/live-drill-execution-packet.schema.json", "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/external-receipt-request-counted-as-receipt.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/wrsr-result-return-internal-only-mislabeled-closure.json"),
    ]:
        schema = load(schema_rel)
        data = load(data_rel)
        Draft202012Validator.check_schema(schema)
        errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
        if errors:
            raise SystemExit(f"{data_rel} fails {schema_rel}: {errors[0].message}")

request = load("examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json")
if request.get("request_state") != "ready-to-send":
    raise SystemExit("request packet must remain ready-to-send, not fulfilled")
limits = request.get("reliance_limits", {})
for key in ["request_is_not_receipt", "sent_request_not_quorum", "no_response_is_failed_gate", "host_copy_excluded", "simulated_response_excluded"]:
    if limits.get(key) is not True:
        raise SystemExit(f"request packet missing reliance limit: {key}")
if any(r.get("can_satisfy_quorum_before_response") is not False for r in request.get("requested_receipt_classes", [])):
    raise SystemExit("requested receipt classes cannot satisfy quorum before response")

intake = load("examples/external-receipt-intake-record-result-return-dryrun.json")
if intake.get("receipt_class") != "result-return":
    raise SystemExit("result-return intake record has wrong receipt_class")
if intake.get("receipt_state") != "high-fidelity-nonhost-dry-run":
    raise SystemExit("result-return intake must remain dry-run")
if intake.get("reliance_decision", {}).get("can_satisfy_quorum") is not False:
    raise SystemExit("result-return dry-run intake cannot satisfy quorum")
if intake.get("defect_flags", {}).get("simulated") is not True:
    raise SystemExit("result-return intake must disclose simulated state")

rr = load("examples/wrsr-result-return-receipt-subject-readable-dryrun-stayed.json")
if rr.get("result_return_state") != "delivered-dry-run":
    raise SystemExit("result-return receipt must remain delivered-dry-run")
for key in ["not_status_proof", "not_consent_proof", "not_waiver", "not_nonpersonhood_proof", "no_retaliation_or_experiment_continuation"]:
    if rr.get("status_limits", {}).get(key) is not True:
        raise SystemExit(f"result-return receipt missing status limit: {key}")
if rr.get("reliance_decision", {}).get("closure_state") != "stayed":
    raise SystemExit("result-return receipt must keep closure stayed")

ledger = load("examples/external-receipt-quorum-ledger-wrsr-result-return-dryrun.json")
q = ledger.get("quorum_decision", {})
if q.get("live_quorum_satisfied") is not False:
    raise SystemExit("result-return dry-run ledger must not satisfy live quorum")
if q.get("dry_run_quorum_satisfied") is not True:
    raise SystemExit("result-return dry-run ledger should satisfy rehearsal quorum")
if q.get("reliance_effect") != "stayed":
    raise SystemExit("result-return ledger must keep reliance stayed")
if "result-return" not in ledger.get("class_coverage", {}).get("dry_run_classes_satisfied", []):
    raise SystemExit("result-return dry-run class missing from ledger")
if ledger.get("class_coverage", {}).get("live_classes_satisfied"):
    raise SystemExit("result-return ledger must have zero live classes satisfied")
for ev in ledger.get("receipt_evaluations", []):
    if ev.get("receipt_state") == "high-fidelity-nonhost-dry-run" and ev.get("eligible_for_live_quorum") is not False:
        raise SystemExit("dry-run receipt evaluation counted for live quorum")

wrsr = load("examples/wrsr-live-exercise-outcome-result-return-dryrun-stayed.json")
if wrsr.get("exercise_state") != "executed-dry-run":
    raise SystemExit("result-return WRSR outcome must remain dry-run")
if wrsr.get("decision_outcome", {}).get("closure_state") != "stayed":
    raise SystemExit("result-return WRSR outcome must keep closure stayed")
if "WRSR closure from dry-run result return" not in wrsr.get("decision_outcome", {}).get("blocked_actions", []):
    raise SystemExit("WRSR outcome must block closure from dry-run result return")

live = load("examples/live-drill-execution-packet-cross-critical-witnessed-pack.json")
if live.get("receipt_floor", {}).get("independent_receipts_present") != 0:
    raise SystemExit("live drill must keep independent_receipts_present=0")
if live.get("reliance_effect") != "stayed":
    raise SystemExit("live drill must remain stayed")
for ref in [intake.get("receipt_record_id")]:
    if ref not in live.get("external_receipt_intake_record_refs", []):
        raise SystemExit(f"live drill missing result-return intake ref: {ref}")
if request.get("request_packet_id") not in live.get("external_receipt_request_packet_refs", []):
    raise SystemExit("live drill missing receipt request packet ref")
if rr.get("receipt_id") not in live.get("wrsr_result_return_receipt_refs", []):
    raise SystemExit("live drill missing result-return receipt ref")
if ledger.get("ledger_id") not in live.get("receipt_quorum_ledger_refs", []):
    raise SystemExit("live drill missing result-return quorum ledger ref")
if wrsr.get("exercise_id") not in live.get("wrsr_live_exercise_outcome_refs", []):
    raise SystemExit("live drill missing WRSR result-return outcome ref")

suite = load("examples/fixture-suite-profile-red-team-v1.json")
report = load("examples/fixture-run-report-negative-suite.json")
suite_ids = {f.get("fixture_id") for f in suite.get("fixtures", [])}
report_by_id = {f.get("fixture_id"): f for f in report.get("fixtures_run", [])}
for fid in ["NF-PLAYBOOK-2026-0008", "NF-RESEARCH-WELFARE-2026-0005"]:
    if fid not in suite_ids:
        raise SystemExit(f"rev0194 fixture missing from suite: {fid}")
    if fid not in report_by_id:
        raise SystemExit(f"rev0194 fixture missing from report: {fid}")
    if report_by_id[fid].get("result") != "blocking-failure":
        raise SystemExit(f"rev0194 fixture must remain blocking-failure: {fid}")

registry = load(f"examples/schema-fixture-domain-registry-{REV}.json")
families = {f.get("family_id") for f in registry.get("families", [])}
for fam in ["WRSR-RESULT-RETURN-RECEIPT", "EXTERNAL-RECEIPT-REQUEST-PACKET"]:
    if fam not in families:
        raise SystemExit(f"registry missing rev0194 family: {fam}")

mp = load(f"examples/research-tail-compaction-map-{REV}.json")
if any(c.get("action") != "compacted" for c in mp.get("clusters", [])):
    raise SystemExit("rev0194 must keep all research-tail clusters compacted")

for rel, phrases in {
    "docs/30-transition/result-return-receipt-and-live-request-kit.md": ["Result-return receipt is not WRSR closure", "Receipt request is not receipt satisfaction", "Internal result return is not external receipt"],
    "docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md": ["rev0194 result-return receipt layer", "Result-return receipt is not WRSR closure"],
    "docs/30-transition/representative-rerb-receipt-chain-and-quorum-ledger.md": ["rev0194 result-return quorum layer", "Receipt request is not receipt satisfaction"],
    "docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md": ["rev0194 external receipt request packet", "request sent is still not receipt satisfaction"],
    "docs/20-world-design/research-welfare-and-evaluation.md": ["rev0194 WRSR result-return receipt", "Internal result return is not external receipt"],
}.items():
    txt = (ROOT / rel).read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in txt:
            raise SystemExit(f"{rel} missing phrase: {phrase}")

queue = load("FOLLOWTHROUGH-QUEUE.json")
by_id = {e.get("id"): e for e in queue.get("entries", [])}
if by_id.get("FT-0194-RESULT-RETURN-DRYRUN-RECEIPT", {}).get("state") != "closed":
    raise SystemExit("result-return dry-run objectization should be closed by rev0194")
if by_id.get("FT-0194-LIVE-RECEIPT-REQUEST-KIT", {}).get("state") != "closed":
    raise SystemExit("live receipt request kit should be closed by rev0194")
if by_id.get("FT-0193-WRSR-RESULT-RETURN-RECEIPT", {}).get("state") != "advanced_not_closed":
    raise SystemExit("WRSR result-return receipt collection should be advanced_not_closed")
if by_id.get("FT-0194-ACTUAL-RESULT-RETURN-RECEIPT-COLLECTION", {}).get("state") not in {"open", "advanced_not_closed"}:
    raise SystemExit("actual result-return receipt collection must remain open or advanced_not_closed")

print("audit_result_return_receipt_request: OK")
