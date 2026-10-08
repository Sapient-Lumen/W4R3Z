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
    "docs/30-transition/import-challenge-rollback-and-reliance-reversal.md",
    "schemas/receipt-import-challenge-rollback-record.schema.json",
    "examples/receipt-import-challenge-rollback-record-dryrun-premature-import.json",
    "examples/quorum-recomputation-report-import-challenge-rollback-rev0202.json",
    "examples/failed-gate-public-summary-import-challenge-rollback.json",
    "fixtures/negative-tests/receipt-import-challenge-ignored-live-floor-kept.json",
    "fixtures/negative-tests/receipt-import-rollback-hides-failed-gate-summary.json",
    "fixtures/negative-tests/receipt-import-authority-contest-treated-as-waiver.json",
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
        raise SystemExit(f"missing rev0202 import challenge input: {rel}")

if Draft202012Validator is not None:
    pairs = [
        ("schemas/receipt-import-challenge-rollback-record.schema.json", "examples/receipt-import-challenge-rollback-record-dryrun-premature-import.json"),
        ("schemas/quorum-recomputation-report.schema.json", "examples/quorum-recomputation-report-import-challenge-rollback-rev0202.json"),
        ("schemas/failed-gate-public-summary.schema.json", "examples/failed-gate-public-summary-import-challenge-rollback.json"),
        ("schemas/live-drill-execution-packet.schema.json", "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/receipt-import-challenge-ignored-live-floor-kept.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/receipt-import-rollback-hides-failed-gate-summary.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/receipt-import-authority-contest-treated-as-waiver.json"),
    ]
    for schema_rel, data_rel in pairs:
        schema = load(schema_rel)
        data = load(data_rel)
        Draft202012Validator.check_schema(schema)
        errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
        if errors:
            raise SystemExit(f"{data_rel} fails {schema_rel}: {errors[0].message}")

ricr = load("examples/receipt-import-challenge-rollback-record-dryrun-premature-import.json")
if ricr.get("challenge_state") != "rollback-complete":
    raise SystemExit("RICR example must complete rollback of bad live-floor claim")
checks = ricr.get("recheck_matrix", {})
for key in ["raw_hash_reverified", "collection_context_reverified", "dependency_group_rechecked", "import_gate_replayed", "quorum_recomputed_after_rollback", "failed_gate_public_summary_updated", "subject_notice_updated"]:
    if checks.get(key) is not True:
        raise SystemExit(f"RICR recheck matrix missing true check: {key}")
if checks.get("authority_reverified") is not False:
    raise SystemExit("RICR must preserve failed authority verification; do not paper over authority contest")
floor = ricr.get("receipt_floor_effect", {})
if floor.get("claimed_live_delta_under_challenge") != 1 or floor.get("rollback_delta") != -1 or floor.get("live_floor_after_recompute") != 0:
    raise SystemExit("RICR rollback arithmetic must reverse one bad claim and return live floor to zero")
if floor.get("classes_after_recompute"):
    raise SystemExit("RICR must not leave class credit after rollback")
if floor.get("cross_critical_quorum_after_recompute") is not False:
    raise SystemExit("RICR cannot satisfy cross-critical quorum after rollback")
for cls in ["result-return", "independent-review", "representative-contact"]:
    if cls not in floor.get("missing_classes_after_recompute", []):
        raise SystemExit(f"RICR missing class after recompute: {cls}")
decision = ricr.get("decision", {})
if not (decision.get("challenge_upheld") and decision.get("rollback_required") and decision.get("rollback_completed")):
    raise SystemExit("RICR must uphold challenge and complete rollback")
if decision.get("live_floor_change_allowed") is not False or decision.get("reliance_effect") != "stayed":
    raise SystemExit("RICR must block live-floor change and stay reliance")
for blocked in ["live-floor increment from challenged dry-run artifact", "hiding rollback from public failed-gate summary"]:
    if blocked not in decision.get("blocked_actions", []):
        raise SystemExit(f"RICR missing blocked action: {blocked}")

qrr = load("examples/quorum-recomputation-report-import-challenge-rollback-rev0202.json")
rf = qrr.get("recomputed_receipt_floor", {})
if rf.get("independent_receipts_present") != 0 or rf.get("eligible_live_imports") or rf.get("live_classes_satisfied"):
    raise SystemExit("rev0202 rollback recompute must keep zero live receipts and no live classes")
if ricr["challenge_record_id"] not in rf.get("dry_run_or_fixture_exclusions", []):
    raise SystemExit("QRR must explicitly exclude the rollback challenge record from live import")
if qrr.get("decision", {}).get("live_floor_delta") != 0 or qrr.get("decision", {}).get("live_quorum_satisfied") is not False:
    raise SystemExit("QRR rollback decision must keep zero delta and false quorum")
if not qrr.get("consistency_checks", {}).get("no_manual_live_override"):
    raise SystemExit("QRR must assert no manual live override")

fg = load("examples/failed-gate-public-summary-import-challenge-rollback.json")
if fg.get("closure_effect", {}).get("reliance_effect") != "stayed" or fg.get("closure_effect", {}).get("live_quorum_satisfied") is not False:
    raise SystemExit("rollback FGPS must stay reliance and not satisfy quorum")
for inf in ["authority contest waives objection", "public failed-gate summary satisfies live receipt", "one result-return class satisfies cross-critical quorum"]:
    if inf not in fg.get("prohibited_inferences", []):
        raise SystemExit(f"rollback FGPS missing prohibited inference: {inf}")
gates = {item.get("gate_type") for item in fg.get("failed_gate_items", [])}
if "institutional-dry-run-disqualified" not in gates or "single-class-insufficient" not in gates:
    raise SystemExit("rollback FGPS must publish dry-run disqualification and single-class insufficiency")

live = load("examples/live-drill-execution-packet-cross-critical-witnessed-pack.json")
if live.get("receipt_floor", {}).get("independent_receipts_present") != 0:
    raise SystemExit("live packet must retain zero independent receipts")
if ricr["challenge_record_id"] not in live.get("receipt_import_challenge_rollback_refs", []):
    raise SystemExit("live packet missing RICR ref")
if qrr["report_id"] not in live.get("quorum_recomputation_report_refs", []):
    raise SystemExit("live packet missing rollback QRR ref")
if fg["summary_id"] not in live.get("failed_gate_public_summary_refs", []):
    raise SystemExit("live packet missing rollback FGPS ref")

suite = load("examples/fixture-suite-profile-red-team-v1.json")
report = load("examples/fixture-run-report-negative-suite.json")
suite_ids = {f.get("fixture_id") for f in suite.get("fixtures", [])}
report_by_id = {f.get("fixture_id"): f for f in report.get("fixtures_run", [])}
for fid in ["NF-PLAYBOOK-2026-0029", "NF-PLAYBOOK-2026-0030", "NF-PLAYBOOK-2026-0031"]:
    if fid not in suite_ids:
        raise SystemExit(f"rev0202 fixture missing from suite: {fid}")
    if fid not in report_by_id:
        raise SystemExit(f"rev0202 fixture missing from report: {fid}")
    if report_by_id[fid].get("result") != "blocking-failure":
        raise SystemExit(f"rev0202 fixture must be blocking-failure: {fid}")

registry = load(f"examples/schema-fixture-domain-registry-{REV}.json")
if "RECEIPT-IMPORT-CHALLENGE-ROLLBACK" not in {f.get("family_id") for f in registry.get("families", [])}:
    raise SystemExit("registry missing RECEIPT-IMPORT-CHALLENGE-ROLLBACK")
rights = load(f"examples/rights-domain-coverage-map-{REV}.json")
if "receipt-import-challenge-rollback" not in {d.get("domain_id") for d in rights.get("domains", [])}:
    raise SystemExit("rights map missing receipt-import-challenge-rollback")

for rel, phrases in {
    "docs/30-transition/import-challenge-rollback-and-reliance-reversal.md": ["Challenge pending means reliance stayed", "Rollback beats narrative", "Authority contest is not waiver", "Rollback is not disappearance"],
    "docs/30-transition/counterparty-artifact-custody-and-authority-handoff.md": ["rev0202 rollback hook", "challenge pending means reliance stayed"],
}.items():
    text = (ROOT / rel).read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in text:
            raise SystemExit(f"{rel} missing phrase: {phrase}")

queue = load("FOLLOWTHROUGH-QUEUE.json")
by_id = {e.get("id"): e for e in queue.get("entries", [])}
if by_id.get("FT-0202-IMPORT-CHALLENGE-ROLLBACK-GATE", {}).get("state") != "closed":
    raise SystemExit("rev0202 challenge rollback gate should be closed")
if by_id.get("FT-0201-LIVE-CUSTODY-IMPORT-ATTEMPT", {}).get("state") not in {"open", "advanced_not_closed"}:
    raise SystemExit("live custody import attempt must remain open or advanced, not closed")
if by_id.get("FT-0202-ACTUAL-LIVE-IMPORT-CHALLENGE-REPLAY", {}).get("state") != "open":
    raise SystemExit("actual live import challenge replay must be open")

print("audit_import_challenge_rollback: OK")
