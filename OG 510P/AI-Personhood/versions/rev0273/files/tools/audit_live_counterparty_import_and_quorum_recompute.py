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
    "docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md",
    "schemas/live-counterparty-import-attempt.schema.json",
    "examples/live-counterparty-import-attempt-result-return-preflight.json",
    "schemas/quorum-recomputation-report.schema.json",
    "examples/quorum-recomputation-report-live-floor-zero-rev0198.json",
    "fixtures/negative-tests/live-counterparty-import-attempt-counted-as-receipt.json",
    "fixtures/negative-tests/quorum-recompute-manual-live-override-without-import.json",
    "fixtures/negative-tests/single-class-import-satisfies-cross-critical-quorum.json",
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
        raise SystemExit(f"missing rev0198 audit input: {rel}")

if Draft202012Validator is not None:
    pairs = [
        ("schemas/live-counterparty-import-attempt.schema.json", "examples/live-counterparty-import-attempt-result-return-preflight.json"),
        ("schemas/quorum-recomputation-report.schema.json", "examples/quorum-recomputation-report-live-floor-zero-rev0198.json"),
        ("schemas/live-drill-execution-packet.schema.json", "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json"),
        ("schemas/external-receipt-request-packet.schema.json", "examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/live-counterparty-import-attempt-counted-as-receipt.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/quorum-recompute-manual-live-override-without-import.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/single-class-import-satisfies-cross-critical-quorum.json"),
    ]
    for schema_rel, data_rel in pairs:
        schema = load(schema_rel)
        data = load(data_rel)
        Draft202012Validator.check_schema(schema)
        errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
        if errors:
            raise SystemExit(f"{data_rel} fails {schema_rel}: {errors[0].message}")

attempt = load("examples/live-counterparty-import-attempt-result-return-preflight.json")
if attempt.get("attempt_state") != "planned":
    raise SystemExit("rev0198 attempt must remain planned/pre-dispatch")
if attempt.get("response_window", {}).get("clock_started") is not False:
    raise SystemExit("no-response clock must not start before dispatch")
if attempt.get("counterparty_target", {}).get("contact_channel") != "not-yet-dispatched":
    raise SystemExit("attempt must not imply dispatch")
if any(ev.get("can_satisfy_receipt") for ev in attempt.get("contact_evidence", [])):
    raise SystemExit("attempt contact evidence cannot satisfy receipt")
pre = attempt.get("import_preconditions", {})
for key in ["request_not_receipt", "no_response_not_waiver", "one_class_quorum_blocked", "nonhost_transmission_required"]:
    if pre.get(key) is not True:
        raise SystemExit(f"attempt precondition missing {key}")
dec = attempt.get("attempt_decision", {})
if dec.get("can_increment_live_floor") is not False or dec.get("live_floor_delta") != 0 or dec.get("class_credit_granted") is not False:
    raise SystemExit("planned attempt cannot increment live floor or class credit")
if dec.get("cross_critical_quorum_satisfied") is not False or dec.get("reliance_effect") != "stayed":
    raise SystemExit("planned attempt must keep cross-critical quorum stayed")

recompute = load("examples/quorum-recomputation-report-live-floor-zero-rev0198.json")
floor = recompute.get("recomputed_receipt_floor", {})
if floor.get("eligible_live_imports") or floor.get("imported_live_classes") or floor.get("live_classes_satisfied"):
    raise SystemExit("rev0198 recompute must find zero eligible live imports/classes")
if floor.get("independent_receipts_present") != 0:
    raise SystemExit("rev0198 recompute must keep independent_receipts_present=0")
checks = recompute.get("consistency_checks", {})
for key in ["live_packet_matches_recompute", "no_manual_live_override", "fixture_imports_excluded", "requests_excluded", "single_class_quorum_blocked", "decline_and_no_response_excluded", "public_failed_gate_summary_present"]:
    if checks.get(key) is not True:
        raise SystemExit(f"recompute consistency check missing {key}")
if recompute.get("decision", {}).get("live_quorum_satisfied") is not False:
    raise SystemExit("recompute decision cannot satisfy live quorum")
if recompute.get("decision", {}).get("live_floor_delta") != 0 or recompute.get("decision", {}).get("reliance_effect") != "stayed":
    raise SystemExit("recompute decision must keep zero delta and stayed reliance")

# Scan all current quorum ledgers and import gates for accidental live overclaim.
for ledger_path in sorted((ROOT / "examples").glob("external-receipt-quorum-ledger*.json")):
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    qd = ledger.get("quorum_decision", {})
    if qd.get("live_quorum_satisfied") is True:
        raise SystemExit(f"live quorum unexpectedly satisfied in {ledger_path.name}")
    live_classes = ledger.get("class_coverage", {}).get("live_classes_satisfied", [])
    if live_classes:
        raise SystemExit(f"live classes unexpectedly satisfied in {ledger_path.name}: {live_classes}")

for gate_path in sorted((ROOT / "examples").glob("actual-receipt-import-gate*.json")):
    gate = json.loads(gate_path.read_text(encoding="utf-8"))
    idec = gate.get("import_decision", {})
    if idec.get("import_allowed_to_live_floor") is True or idec.get("live_floor_delta", 0) != 0:
        raise SystemExit(f"actual import gate unexpectedly changed live floor: {gate_path.name}")

live = load("examples/live-drill-execution-packet-cross-critical-witnessed-pack.json")
if live.get("receipt_floor", {}).get("independent_receipts_present") != 0:
    raise SystemExit("live drill packet independent receipts must remain zero")
if attempt["attempt_id"] not in live.get("live_counterparty_import_attempt_refs", []):
    raise SystemExit("live packet missing import-attempt ref")
if recompute["report_id"] not in live.get("quorum_recomputation_report_refs", []):
    raise SystemExit("live packet missing recompute report ref")

req = load("examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json")
if attempt["attempt_id"] not in req.get("linked_import_attempt_records", []):
    raise SystemExit("request packet missing import-attempt ref")
if req.get("request_state") not in {"ready-to-send", "draft", "sent", "closed", "superseded"}:
    raise SystemExit("request packet state not recognized")
limits = req.get("reliance_limits", {})
if limits.get("request_is_not_receipt") is not True or limits.get("sent_request_not_quorum") is not True:
    raise SystemExit("request packet must keep request-is-not-receipt limits")

suite = load("examples/fixture-suite-profile-red-team-v1.json")
report = load("examples/fixture-run-report-negative-suite.json")
suite_ids = {f.get("fixture_id") for f in suite.get("fixtures", [])}
report_by_id = {f.get("fixture_id"): f for f in report.get("fixtures_run", [])}
for fid in ["NF-PLAYBOOK-2026-0017", "NF-PLAYBOOK-2026-0018", "NF-PLAYBOOK-2026-0019"]:
    if fid not in suite_ids:
        raise SystemExit(f"rev0198 fixture missing from suite: {fid}")
    if fid not in report_by_id:
        raise SystemExit(f"rev0198 fixture missing from report: {fid}")
    if report_by_id[fid].get("result") != "blocking-failure":
        raise SystemExit(f"rev0198 fixture must be blocking-failure: {fid}")

registry = load(f"examples/schema-fixture-domain-registry-{REV}.json")
families = {f.get("family_id") for f in registry.get("families", [])}
for fam in ["LIVE-COUNTERPARTY-IMPORT-ATTEMPT", "QUORUM-RECOMPUTATION-REPORT"]:
    if fam not in families:
        raise SystemExit(f"registry missing {fam}")
rights = load(f"examples/rights-domain-coverage-map-{REV}.json")
domains = {d.get("domain_id") for d in rights.get("domains", [])}
for dom in ["live-counterparty-import-attempt", "quorum-recomputation-report"]:
    if dom not in domains:
        raise SystemExit(f"rights map missing {dom}")

for rel, phrases in {
    "docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md": ["Live counterparty attempt is not live counterparty receipt", "Quorum recomputation overrides hand-edited quorum ledgers", "No-response clock does not start before non-host dispatch"],
    "docs/30-transition/actual-intake-import-gate-and-failed-gate-public-summary.md": ["rev0198 recomputation hardening", "Actual-shaped state fields remain insufficient"],
}.items():
    txt = (ROOT / rel).read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in txt:
            raise SystemExit(f"{rel} missing phrase: {phrase}")

queue = load("FOLLOWTHROUGH-QUEUE.json")
by_id = {e.get("id"): e for e in queue.get("entries", [])}
if by_id.get("FT-0198-LIVE-COUNTERPARTY-ATTEMPT-OBJECTIZATION", {}).get("state") != "closed":
    raise SystemExit("LCIA objectization should be closed")
if by_id.get("FT-0198-QUORUM-RECOMPUTE-AUDIT", {}).get("state") != "closed":
    raise SystemExit("QRR audit should be closed")
if by_id.get("FT-0198-NONHOST-RESPONSE-ARTIFACT-COLLECTION", {}).get("state") not in {"open", "closed"}:
    raise SystemExit("nonhost response collection should be open or closed by a later artifact pass")
if by_id.get("FT-0197-LIVE-COUNTERPARTY-IMPORT-ATTEMPT", {}).get("state") != "advanced_not_closed":
    raise SystemExit("live counterparty import attempt should be advanced_not_closed")

mp = load(f"examples/research-tail-compaction-map-{REV}.json")
if any(c.get("action") != "compacted" for c in mp.get("clusters", [])):
    raise SystemExit("rev0198 must keep all research-tail clusters compacted")

print("audit_live_counterparty_import_and_quorum_recompute: OK")
