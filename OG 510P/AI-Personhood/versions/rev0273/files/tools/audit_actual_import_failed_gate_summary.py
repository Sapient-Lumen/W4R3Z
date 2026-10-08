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
    "docs/30-transition/actual-intake-import-gate-and-failed-gate-public-summary.md",
    "schemas/actual-receipt-import-gate.schema.json",
    "examples/actual-receipt-import-gate-result-return-fixture-no-live-delta.json",
    "schemas/failed-gate-public-summary.schema.json",
    "examples/failed-gate-public-summary-response-conversion-batch.json",
    "examples/external-receipt-quorum-ledger-actual-intake-import-gate-fixture.json",
    "examples/wrsr-live-exercise-outcome-actual-intake-import-gate-stayed.json",
    "fixtures/negative-tests/actual-external-state-field-imported-without-provenance-gate.json",
    "fixtures/negative-tests/failed-gate-summary-omits-declined-or-expired.json",
    "fixtures/negative-tests/failed-gate-summary-treats-no-response-as-waiver.json",
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
        raise SystemExit(f"missing rev0197 audit input: {rel}")

if Draft202012Validator is not None:
    pairs = [
        ("schemas/actual-receipt-import-gate.schema.json", "examples/actual-receipt-import-gate-result-return-fixture-no-live-delta.json"),
        ("schemas/failed-gate-public-summary.schema.json", "examples/failed-gate-public-summary-response-conversion-batch.json"),
        ("schemas/external-receipt-quorum-ledger.schema.json", "examples/external-receipt-quorum-ledger-actual-intake-import-gate-fixture.json"),
        ("schemas/wrsr-live-exercise-outcome.schema.json", "examples/wrsr-live-exercise-outcome-actual-intake-import-gate-stayed.json"),
        ("schemas/live-drill-execution-packet.schema.json", "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/actual-external-state-field-imported-without-provenance-gate.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/failed-gate-summary-omits-declined-or-expired.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/failed-gate-summary-treats-no-response-as-waiver.json"),
    ]
    for schema_rel, data_rel in pairs:
        schema = load(schema_rel)
        data = load(data_rel)
        Draft202012Validator.check_schema(schema)
        errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
        if errors:
            raise SystemExit(f"{data_rel} fails {schema_rel}: {errors[0].message}")

import_gate = load("examples/actual-receipt-import-gate-result-return-fixture-no-live-delta.json")
if import_gate.get("import_mode") != "controlled-fixture-rehearsal":
    raise SystemExit("import gate example must be controlled-fixture-rehearsal")
prov = import_gate.get("source_provenance", {})
if prov.get("collection_context") != "controlled-fixture":
    raise SystemExit("import gate must identify controlled-fixture collection context")
if "controlled conversion fixture" not in " ".join(prov.get("provenance_disqualifiers", [])):
    raise SystemExit("import gate missing controlled-fixture disqualifier")
checks = import_gate.get("gate_checks", {})
if checks.get("response_state_actual") is not True or checks.get("intake_state_actual_external") is not True:
    raise SystemExit("rev0197 must test actual-shaped state fields")
if checks.get("fixture_or_dry_run_excluded_from_live_floor") is not True:
    raise SystemExit("fixture/dry-run exclusion gate must be active")
decision = import_gate.get("import_decision", {})
if decision.get("import_allowed_to_live_floor") is not False:
    raise SystemExit("controlled fixture cannot import to live floor")
if decision.get("live_floor_delta") != 0:
    raise SystemExit("controlled fixture must keep live_floor_delta=0")
if decision.get("independent_receipts_present_after") != decision.get("independent_receipts_present_before"):
    raise SystemExit("independent_receipts_present must not change")
if decision.get("live_class_credit_granted") is not False or decision.get("cross_critical_quorum_satisfied") is not False:
    raise SystemExit("fixture import cannot grant class credit or cross-critical quorum")
for phrase in ["live receipt-floor increment from a controlled fixture", "public failed-gate summary treated as receipt satisfaction"]:
    if phrase not in decision.get("blocked_actions", []):
        raise SystemExit(f"import gate missing blocked action: {phrase}")

summary = load("examples/failed-gate-public-summary-response-conversion-batch.json")
gates = {g.get("gate_type"): g for g in summary.get("failed_gate_items", [])}
for gate_type in ["fixture-disqualified", "defective-response", "declined-response", "expired-no-response"]:
    if gate_type not in gates:
        raise SystemExit(f"failed-gate summary missing {gate_type}")
    if "waiv" not in gates[gate_type].get("non_waiver_statement", "").lower() and gate_type in {"declined-response", "expired-no-response"}:
        raise SystemExit(f"{gate_type} lacks non-waiver statement")
    if not gates[gate_type].get("cure_or_substitute_action"):
        raise SystemExit(f"{gate_type} lacks cure/substitute action")
for bad in ["no-response means waiver", "actual-shaped fixture fields satisfy live receipt quorum", "one result-return class satisfies cross-critical reliance"]:
    if bad not in summary.get("prohibited_inferences", []):
        raise SystemExit(f"summary missing prohibited inference: {bad}")
closure = summary.get("closure_effect", {})
if closure.get("live_quorum_satisfied") is not False or closure.get("public_failed_gate_satisfies_receipt") is not False or closure.get("reliance_effect") != "stayed":
    raise SystemExit("failed-gate summary must not satisfy receipt or live quorum")

ledger = load("examples/external-receipt-quorum-ledger-actual-intake-import-gate-fixture.json")
if ledger.get("quorum_context") != "actual-intake-import-gate":
    raise SystemExit("import-gate ledger context mismatch")
if ledger.get("quorum_decision", {}).get("live_quorum_satisfied") is not False:
    raise SystemExit("import-gate ledger cannot satisfy live quorum")
if ledger.get("class_coverage", {}).get("live_classes_satisfied"):
    raise SystemExit("import-gate fixture cannot satisfy live class coverage")
if ledger.get("receipt_evaluations", [])[0].get("eligible_for_live_quorum") is not False:
    raise SystemExit("import-gate evaluation must be excluded from live quorum")

wrsr = load("examples/wrsr-live-exercise-outcome-actual-intake-import-gate-stayed.json")
if wrsr.get("decision_outcome", {}).get("closure_state") != "stayed":
    raise SystemExit("WRSR import-gate outcome must remain stayed")
for phrase in ["WRSR closure from actual-shaped fixture state fields", "no-response or declination treated as waiver"]:
    if phrase not in wrsr.get("decision_outcome", {}).get("blocked_actions", []):
        raise SystemExit(f"WRSR import-gate missing blocked action: {phrase}")

live = load("examples/live-drill-execution-packet-cross-critical-witnessed-pack.json")
if live.get("receipt_floor", {}).get("independent_receipts_present") != 0:
    raise SystemExit("live packet must still keep independent_receipts_present=0")
if import_gate["import_gate_id"] not in live.get("actual_receipt_import_gate_refs", []):
    raise SystemExit("live packet missing actual import gate ref")
if summary["summary_id"] not in live.get("failed_gate_public_summary_refs", []):
    raise SystemExit("live packet missing failed-gate public summary ref")
if ledger["ledger_id"] not in live.get("receipt_quorum_ledger_refs", []):
    raise SystemExit("live packet missing import-gate quorum ledger ref")

suite = load("examples/fixture-suite-profile-red-team-v1.json")
report = load("examples/fixture-run-report-negative-suite.json")
suite_ids = {f.get("fixture_id") for f in suite.get("fixtures", [])}
report_by_id = {f.get("fixture_id"): f for f in report.get("fixtures_run", [])}
for fid in ["NF-PLAYBOOK-2026-0014", "NF-PLAYBOOK-2026-0015", "NF-PLAYBOOK-2026-0016"]:
    if fid not in suite_ids:
        raise SystemExit(f"rev0197 fixture missing from suite: {fid}")
    if fid not in report_by_id:
        raise SystemExit(f"rev0197 fixture missing from report: {fid}")
    if report_by_id[fid].get("result") != "blocking-failure":
        raise SystemExit(f"rev0197 fixture must be blocking-failure: {fid}")

registry = load(f"examples/schema-fixture-domain-registry-{REV}.json")
families = {f.get("family_id") for f in registry.get("families", [])}
for fam in ["ACTUAL-RECEIPT-IMPORT-GATE", "FAILED-GATE-PUBLIC-SUMMARY"]:
    if fam not in families:
        raise SystemExit(f"registry missing {fam}")

rights = load(f"examples/rights-domain-coverage-map-{REV}.json")
domains = {d.get("domain_id") for d in rights.get("domains", [])}
for dom in ["actual-receipt-import-gate", "failed-gate-public-summary"]:
    if dom not in domains:
        raise SystemExit(f"rights map missing {dom}")

for rel, phrases in {
    "docs/30-transition/actual-intake-import-gate-and-failed-gate-public-summary.md": ["Actual-shaped is not actual", "Public failed-gate summary is not receipt satisfaction", "No-response and declination are not waiver"],
    "docs/30-transition/response-to-intake-conversion-drill-and-failed-gate-ledger.md": ["rev0197 import-gate hardening", "actual-shaped state fields are not enough"],
}.items():
    txt = (ROOT / rel).read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in txt:
            raise SystemExit(f"{rel} missing phrase: {phrase}")

queue = load("FOLLOWTHROUGH-QUEUE.json")
by_id = {e.get("id"): e for e in queue.get("entries", [])}
if by_id.get("FT-0197-ACTUAL-IMPORT-GATE-OBJECTIZATION", {}).get("state") != "closed":
    raise SystemExit("actual import gate objectization should be closed")
if by_id.get("FT-0196-FAILED-GATE-PUBLIC-SUMMARY-CANON", {}).get("state") != "closed":
    raise SystemExit("failed-gate public summary canon should be closed")
def assert_open_or_explicitly_deferred(queue_id, allowed_active_states):
    entry = by_id.get(queue_id, {})
    state = entry.get("state")
    if state in allowed_active_states:
        return
    if state == "deferred" and "deferred-by-rev0250" in entry.get("source_state", ""):
        return
    raise SystemExit(f"{queue_id} should remain active or be explicitly deferred by the rev0250 compact operating-board policy")

assert_open_or_explicitly_deferred("FT-0196-ACTUAL-INTAKE-IMPORT-DRILL", {"advanced_not_closed"})
assert_open_or_explicitly_deferred("FT-0197-LIVE-COUNTERPARTY-IMPORT-ATTEMPT", {"open", "advanced_not_closed"})

mp = load(f"examples/research-tail-compaction-map-{REV}.json")
if any(c.get("action") != "compacted" for c in mp.get("clusters", [])):
    raise SystemExit("rev0197 must keep all research-tail clusters compacted")

print("audit_actual_import_failed_gate_summary: OK")
