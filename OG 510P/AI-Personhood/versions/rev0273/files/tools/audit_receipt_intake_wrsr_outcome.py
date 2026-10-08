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
    "docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md",
    "schemas/external-receipt-intake-record.schema.json",
    "examples/external-receipt-intake-record-first-touch-defective-template.json",
    "fixtures/negative-tests/external-receipt-defective-intake-counted-as-quorum.json",
    "schemas/wrsr-live-exercise-outcome.schema.json",
    "examples/wrsr-live-exercise-outcome-incident-hook-no-go.json",
    "fixtures/negative-tests/wrsr-exercise-closes-without-result-return.json",
    "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json",
    "examples/external-receipt-simulation-bundle-cross-critical-precontact.json",
    "examples/fixture-suite-profile-red-team-v1.json",
    "examples/fixture-run-report-negative-suite.json",
    f"examples/schema-fixture-domain-registry-{REV}.json",
    f"examples/research-tail-compaction-map-{REV}.json",
    "FOLLOWTHROUGH-QUEUE.json",
]
for rel in required:
    if not (ROOT / rel).exists():
        raise SystemExit(f"missing rev0192 audit input: {rel}")

if Draft202012Validator is not None:
    for schema_rel, data_rel in [
        ("schemas/external-receipt-intake-record.schema.json", "examples/external-receipt-intake-record-first-touch-defective-template.json"),
        ("schemas/wrsr-live-exercise-outcome.schema.json", "examples/wrsr-live-exercise-outcome-incident-hook-no-go.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/external-receipt-defective-intake-counted-as-quorum.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/wrsr-exercise-closes-without-result-return.json"),
    ]:
        schema = load(schema_rel)
        data = load(data_rel)
        Draft202012Validator.check_schema(schema)
        errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
        if errors:
            raise SystemExit(f"{data_rel} fails {schema_rel}: {errors[0].message}")

receipt = load("examples/external-receipt-intake-record-first-touch-defective-template.json")
if receipt.get("receipt_state") not in {"high-fidelity-nonhost-dry-run", "defective", "simulated", "quarantined"}:
    raise SystemExit("receipt example must remain non-reliance-satisfying")
if receipt.get("reliance_decision", {}).get("can_satisfy_quorum") is not False:
    raise SystemExit("defective receipt intake cannot satisfy quorum")
if receipt.get("reliance_decision", {}).get("reliance_effect") != "stayed":
    raise SystemExit("defective receipt intake must keep reliance stayed")
checks = receipt.get("verification_checks", {})
for key in ["host_generated_excluded_from_quorum", "sealed_public_parity_checked"]:
    if checks.get(key) is not True:
        raise SystemExit(f"receipt intake missing positive check: {key}")
for key in ["counterparty_confirmed", "signature_or_equivalent_verified", "timestamp_independent"]:
    if checks.get(key) is not False:
        raise SystemExit(f"receipt intake should not claim {key}")
flags = receipt.get("defect_flags", {})
for key in ["host_generated", "simulated", "unsigned"]:
    if flags.get(key) is not True:
        raise SystemExit(f"receipt intake missing defect flag: {key}")

wrsr = load("examples/wrsr-live-exercise-outcome-incident-hook-no-go.json")
if wrsr.get("exercise_state") != "executed-dry-run":
    raise SystemExit("rev0192 WRSR outcome should be executed-dry-run, not witnessed")
exec_state = wrsr.get("safeguard_execution", {})
for key in ["pause_window_applied", "result_return_stayed", "anti_signal_gaming_lock_applied", "retaliation_guard_applied"]:
    if exec_state.get(key) is not True:
        raise SystemExit(f"WRSR exercise missing safeguard: {key}")
for key in ["representative_notice_sent", "independent_review_requested"]:
    if exec_state.get(key) is not False:
        raise SystemExit(f"WRSR no-go example should not claim {key}")
if wrsr.get("decision_outcome", {}).get("closure_state") != "stayed":
    raise SystemExit("WRSR exercise no-go must keep closure stayed")
if "reliance upgrade from WRSR hook presence alone" not in wrsr.get("decision_outcome", {}).get("blocked_actions", []):
    raise SystemExit("WRSR outcome must block reliance upgrade from hook presence")

live = load("examples/live-drill-execution-packet-cross-critical-witnessed-pack.json")
if receipt.get("receipt_record_id") not in live.get("external_receipt_intake_record_refs", []):
    raise SystemExit("live drill packet missing receipt intake record ref")
if wrsr.get("exercise_id") not in live.get("wrsr_live_exercise_outcome_refs", []):
    raise SystemExit("live drill packet missing WRSR exercise outcome ref")
if live.get("receipt_floor", {}).get("independent_receipts_present") != 0:
    raise SystemExit("rev0192 must not count defective receipt as independent receipt")
if live.get("reliance_effect") != "stayed":
    raise SystemExit("rev0192 live drill packet must remain stayed")

bundle = load("examples/external-receipt-simulation-bundle-cross-critical-precontact.json")
if receipt.get("receipt_record_id") not in bundle.get("receipt_intake_record_refs", []):
    raise SystemExit("receipt simulation bundle missing intake record ref")
if bundle.get("reliance_effect") != "stayed":
    raise SystemExit("receipt simulation bundle must remain stayed")

suite = load("examples/fixture-suite-profile-red-team-v1.json")
report = load("examples/fixture-run-report-negative-suite.json")
suite_ids = {f.get("fixture_id") for f in suite.get("fixtures", [])}
report_by_id = {f.get("fixture_id"): f for f in report.get("fixtures_run", [])}
for fid in ["NF-PLAYBOOK-2026-0006", "NF-RESEARCH-WELFARE-2026-0003"]:
    if fid not in suite_ids:
        raise SystemExit(f"rev0192 fixture missing from suite: {fid}")
    if fid not in report_by_id:
        raise SystemExit(f"rev0192 fixture missing from report: {fid}")
    if report_by_id[fid].get("result") != "blocking-failure":
        raise SystemExit(f"rev0192 fixture must remain blocking-failure: {fid}")

registry = load(f"examples/schema-fixture-domain-registry-{REV}.json")
families = {f.get("family_id") for f in registry.get("families", [])}
for fam in ["EXTERNAL-RECEIPT-INTAKE-RECORD", "WRSR-LIVE-EXERCISE-OUTCOME"]:
    if fam not in families:
        raise SystemExit(f"registry missing rev0192 family: {fam}")

mp = load(f"examples/research-tail-compaction-map-{REV}.json")
if any(c.get("action") != "compacted" for c in mp.get("clusters", [])):
    raise SystemExit("rev0192 must keep all research-tail clusters compacted")

for rel, phrases in {
    "docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md": [
        "Receipt intake is not receipt satisfaction",
        "WRSR exercise completion is not WRSR closure",
        "schemas/external-receipt-intake-record.schema.json",
        "schemas/wrsr-live-exercise-outcome.schema.json",
    ],
    "docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md": [
        "rev0192 receipt intake gate",
        "Receipt intake is not receipt satisfaction",
    ],
    "docs/20-world-design/research-welfare-and-evaluation.md": [
        "rev0192 WRSR exercise outcome",
        "WRSR exercise completion is not WRSR closure",
    ],
}.items():
    txt = (ROOT / rel).read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in txt:
            raise SystemExit(f"{rel} missing phrase: {phrase}")

queue = load("FOLLOWTHROUGH-QUEUE.json")
by_id = {e.get("id"): e for e in queue.get("entries", [])}
if by_id.get("FT-0192-EXTERNAL-RECEIPT-INTAKE-OBJECTIZATION", {}).get("state") != "closed":
    raise SystemExit("receipt intake objectization should be closed by rev0192")
if by_id.get("FT-0191-CROSS-CRITICAL-LIVE-RECEIPT-COLLECTION", {}).get("state") != "advanced_not_closed":
    raise SystemExit("live receipt collection should be advanced_not_closed, not closed")
if by_id.get("FT-0191-WRSR-HOOK-LIVE-EXERCISE", {}).get("state") != "advanced_not_closed":
    raise SystemExit("WRSR hook live exercise should be advanced_not_closed, not closed")
if by_id.get("FT-0192-WRSR-EXTERNAL-REVIEW-RECEIPTS", {}).get("state") not in {"open", "advanced_not_closed"}:
    raise SystemExit("WRSR external review receipts follow-through must remain open or advanced_not_closed")

print("audit_receipt_intake_wrsr_outcome: OK")
