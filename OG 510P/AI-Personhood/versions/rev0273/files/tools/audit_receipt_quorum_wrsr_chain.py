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
    "docs/30-transition/representative-rerb-receipt-chain-and-quorum-ledger.md",
    "schemas/external-receipt-quorum-ledger.schema.json",
    "examples/external-receipt-quorum-ledger-wrsr-representative-rerb-dryrun.json",
    "examples/external-receipt-intake-record-representative-notice-dryrun.json",
    "examples/external-receipt-intake-record-rerb-review-dryrun.json",
    "examples/wrsr-live-exercise-outcome-representative-rerb-dryrun-stayed.json",
    "fixtures/negative-tests/external-receipt-quorum-dryrun-counted-as-live.json",
    "fixtures/negative-tests/wrsr-rerb-dryrun-mislabeled-closure.json",
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
        raise SystemExit(f"missing rev0193 audit input: {rel}")

if Draft202012Validator is not None:
    for schema_rel, data_rel in [
        ("schemas/external-receipt-intake-record.schema.json", "examples/external-receipt-intake-record-representative-notice-dryrun.json"),
        ("schemas/external-receipt-intake-record.schema.json", "examples/external-receipt-intake-record-rerb-review-dryrun.json"),
        ("schemas/external-receipt-quorum-ledger.schema.json", "examples/external-receipt-quorum-ledger-wrsr-representative-rerb-dryrun.json"),
        ("schemas/wrsr-live-exercise-outcome.schema.json", "examples/wrsr-live-exercise-outcome-representative-rerb-dryrun-stayed.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/external-receipt-quorum-dryrun-counted-as-live.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/wrsr-rerb-dryrun-mislabeled-closure.json"),
    ]:
        schema = load(schema_rel)
        data = load(data_rel)
        Draft202012Validator.check_schema(schema)
        errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
        if errors:
            raise SystemExit(f"{data_rel} fails {schema_rel}: {errors[0].message}")

rep = load("examples/external-receipt-intake-record-representative-notice-dryrun.json")
rerb = load("examples/external-receipt-intake-record-rerb-review-dryrun.json")
for rel, rec, cls in [
    ("representative", rep, "representative-contact"),
    ("rerb", rerb, "independent-review"),
]:
    if rec.get("receipt_state") != "high-fidelity-nonhost-dry-run":
        raise SystemExit(f"{rel} receipt must remain high-fidelity dry-run")
    if rec.get("receipt_class") != cls:
        raise SystemExit(f"{rel} receipt_class mismatch")
    if rec.get("source_external_to_host") is not True:
        raise SystemExit(f"{rel} receipt must be external-to-host role")
    if rec.get("reliance_decision", {}).get("can_satisfy_quorum") is not False:
        raise SystemExit(f"{rel} dry-run receipt cannot satisfy live quorum")
    if rec.get("verification_checks", {}).get("dependency_group_checked") is not True:
        raise SystemExit(f"{rel} receipt missing dependency check")
    if rec.get("defect_flags", {}).get("simulated") is not True:
        raise SystemExit(f"{rel} receipt must disclose simulated/dry-run state")

ledger = load("examples/external-receipt-quorum-ledger-wrsr-representative-rerb-dryrun.json")
q = ledger.get("quorum_decision", {})
if q.get("dry_run_quorum_satisfied") is not True:
    raise SystemExit("rev0193 ledger should satisfy dry-run choreography")
if q.get("live_quorum_satisfied") is not False:
    raise SystemExit("rev0193 ledger must not satisfy live quorum")
if q.get("reliance_effect") != "stayed":
    raise SystemExit("rev0193 ledger must keep reliance stayed")
classes = set(ledger.get("class_coverage", {}).get("dry_run_classes_satisfied", []))
if {"representative-contact", "independent-review"} - classes:
    raise SystemExit("rev0193 ledger missing representative/RERB dry-run classes")
if ledger.get("class_coverage", {}).get("live_classes_satisfied"):
    raise SystemExit("rev0193 ledger must have zero live classes satisfied")
for ev in ledger.get("receipt_evaluations", []):
    if ev.get("receipt_state") == "high-fidelity-nonhost-dry-run" and ev.get("eligible_for_live_quorum") is not False:
        raise SystemExit("dry-run receipt evaluation counted for live quorum")

deps = set(ledger.get("dependency_group_coverage", {}).get("unique_dry_run_dependency_groups", []))
if {"independent-representative-clinic", "independent-rerb-panel"} - deps:
    raise SystemExit("ledger missing dry-run dependency group separation")

wrsr = load("examples/wrsr-live-exercise-outcome-representative-rerb-dryrun-stayed.json")
if wrsr.get("exercise_state") != "executed-dry-run":
    raise SystemExit("WRSR representative/RERB outcome must remain dry-run")
exec_state = wrsr.get("safeguard_execution", {})
for key in ["pause_window_applied", "representative_notice_sent", "independent_review_requested", "result_return_stayed", "anti_signal_gaming_lock_applied", "retaliation_guard_applied"]:
    if exec_state.get(key) is not True:
        raise SystemExit(f"WRSR representative/RERB outcome missing safeguard: {key}")
if wrsr.get("decision_outcome", {}).get("closure_state") != "stayed":
    raise SystemExit("WRSR representative/RERB outcome must keep closure stayed")
if "live WRSR closure from dry-run representative/RERB receipts" not in wrsr.get("decision_outcome", {}).get("blocked_actions", []):
    raise SystemExit("WRSR outcome must block live closure from dry-run receipts")
if wrsr.get("receipt_quorum_ledger_ref") != ledger.get("ledger_id"):
    raise SystemExit("WRSR outcome missing receipt quorum ledger ref")

live = load("examples/live-drill-execution-packet-cross-critical-witnessed-pack.json")
if ledger.get("ledger_id") not in live.get("receipt_quorum_ledger_refs", []):
    raise SystemExit("live drill missing receipt quorum ledger ref")
if live.get("receipt_floor", {}).get("independent_receipts_present") != 0:
    raise SystemExit("live drill must keep independent_receipts_present=0")
if live.get("reliance_effect") != "stayed":
    raise SystemExit("live drill must remain stayed")
for ref in [rep.get("receipt_record_id"), rerb.get("receipt_record_id")]:
    if ref not in live.get("external_receipt_intake_record_refs", []):
        raise SystemExit(f"live drill missing intake ref: {ref}")
if wrsr.get("exercise_id") not in live.get("wrsr_live_exercise_outcome_refs", []):
    raise SystemExit("live drill missing WRSR representative/RERB outcome ref")

bundle = load("examples/external-receipt-simulation-bundle-cross-critical-precontact.json")
if ledger.get("ledger_id") not in bundle.get("receipt_quorum_ledger_refs", []):
    raise SystemExit("simulation bundle missing receipt quorum ledger ref")

suite = load("examples/fixture-suite-profile-red-team-v1.json")
report = load("examples/fixture-run-report-negative-suite.json")
suite_ids = {f.get("fixture_id") for f in suite.get("fixtures", [])}
report_by_id = {f.get("fixture_id"): f for f in report.get("fixtures_run", [])}
for fid in ["NF-PLAYBOOK-2026-0007", "NF-RESEARCH-WELFARE-2026-0004"]:
    if fid not in suite_ids:
        raise SystemExit(f"rev0193 fixture missing from suite: {fid}")
    if fid not in report_by_id:
        raise SystemExit(f"rev0193 fixture missing from report: {fid}")
    if report_by_id[fid].get("result") != "blocking-failure":
        raise SystemExit(f"rev0193 fixture must remain blocking-failure: {fid}")

registry = load(f"examples/schema-fixture-domain-registry-{REV}.json")
families = {f.get("family_id") for f in registry.get("families", [])}
if "EXTERNAL-RECEIPT-QUORUM-LEDGER" not in families:
    raise SystemExit("registry missing EXTERNAL-RECEIPT-QUORUM-LEDGER")

mp = load(f"examples/research-tail-compaction-map-{REV}.json")
if any(c.get("action") != "compacted" for c in mp.get("clusters", [])):
    raise SystemExit("rev0193 must keep all research-tail clusters compacted")

for rel, phrases in {
    "docs/30-transition/representative-rerb-receipt-chain-and-quorum-ledger.md": [
        "Receipt chain is not live quorum", "Dry-run quorum is rehearsal only", "Representative/RERB participation is not WRSR closure"
    ],
    "docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md": ["rev0193 receipt chain layer", "Receipt chain is not live quorum"],
    "docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md": ["rev0193 quorum ledger", "Dry-run quorum is rehearsal only"],
    "docs/20-world-design/research-welfare-and-evaluation.md": ["rev0193 representative/RERB dry-run outcome"],
}.items():
    txt = (ROOT / rel).read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in txt:
            raise SystemExit(f"{rel} missing phrase: {phrase}")

queue = load("FOLLOWTHROUGH-QUEUE.json")
by_id = {e.get("id"): e for e in queue.get("entries", [])}
if by_id.get("FT-0193-REPRESENTATIVE-RERB-RECEIPT-CHAIN", {}).get("state") != "closed":
    raise SystemExit("representative/RERB receipt chain should be closed by rev0193")
if by_id.get("FT-0192-WRSR-EXTERNAL-REVIEW-RECEIPTS", {}).get("state") != "advanced_not_closed":
    raise SystemExit("WRSR external review receipts should be advanced_not_closed")
if by_id.get("FT-0193-ACTUAL-RECEIPT-QUORUM-COLLECTION", {}).get("state") not in {"open", "advanced_not_closed"}:
    raise SystemExit("actual receipt quorum collection follow-through must remain open or advanced_not_closed")

print("audit_receipt_quorum_wrsr_chain: OK")
