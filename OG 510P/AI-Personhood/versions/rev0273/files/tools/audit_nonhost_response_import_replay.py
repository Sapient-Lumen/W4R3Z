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
    "docs/30-transition/nonhost-response-artifact-envelope-and-import-replay.md",
    "schemas/nonhost-response-artifact-envelope.schema.json",
    "examples/nonhost-response-artifact-envelope-result-return-institutional-dryrun.json",
    "schemas/live-import-replay-report.schema.json",
    "examples/live-import-replay-report-result-return-institutional-dryrun.json",
    "examples/live-counterparty-import-attempt-result-return-institutional-dryrun-response.json",
    "examples/external-receipt-response-record-result-return-institutional-envelope-dryrun.json",
    "examples/external-receipt-intake-record-result-return-institutional-envelope-dryrun.json",
    "examples/actual-receipt-import-gate-result-return-institutional-dryrun-no-live-delta.json",
    "examples/external-receipt-quorum-ledger-nonhost-artifact-replay-dryrun.json",
    "examples/failed-gate-public-summary-nonhost-artifact-replay.json",
    "examples/wrsr-live-exercise-outcome-nonhost-artifact-replay-stayed.json",
    "examples/quorum-recomputation-report-nonhost-artifact-replay-rev0199.json",
    "fixtures/negative-tests/nonhost-response-envelope-dryrun-imported-as-live.json",
    "fixtures/negative-tests/live-import-replay-dryrun-grants-live-floor.json",
    "fixtures/negative-tests/quorum-recompute-omits-artifact-envelope-exclusions.json",
    "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json",
    f"examples/schema-fixture-domain-registry-{REV}.json",
    f"examples/canon-surface-catalog-{REV}.json",
    f"examples/doctrine-dependency-map-{REV}.json",
    f"examples/rights-domain-coverage-map-{REV}.json",
    f"examples/research-tail-compaction-map-{REV}.json",
    "FOLLOWTHROUGH-QUEUE.json",
]
for rel in required:
    if not (ROOT / rel).exists():
        raise SystemExit(f"missing rev0199 audit input: {rel}")

if Draft202012Validator is not None:
    pairs = [
        ("schemas/nonhost-response-artifact-envelope.schema.json", "examples/nonhost-response-artifact-envelope-result-return-institutional-dryrun.json"),
        ("schemas/live-import-replay-report.schema.json", "examples/live-import-replay-report-result-return-institutional-dryrun.json"),
        ("schemas/live-counterparty-import-attempt.schema.json", "examples/live-counterparty-import-attempt-result-return-institutional-dryrun-response.json"),
        ("schemas/external-receipt-response-record.schema.json", "examples/external-receipt-response-record-result-return-institutional-envelope-dryrun.json"),
        ("schemas/external-receipt-intake-record.schema.json", "examples/external-receipt-intake-record-result-return-institutional-envelope-dryrun.json"),
        ("schemas/actual-receipt-import-gate.schema.json", "examples/actual-receipt-import-gate-result-return-institutional-dryrun-no-live-delta.json"),
        ("schemas/external-receipt-quorum-ledger.schema.json", "examples/external-receipt-quorum-ledger-nonhost-artifact-replay-dryrun.json"),
        ("schemas/failed-gate-public-summary.schema.json", "examples/failed-gate-public-summary-nonhost-artifact-replay.json"),
        ("schemas/wrsr-live-exercise-outcome.schema.json", "examples/wrsr-live-exercise-outcome-nonhost-artifact-replay-stayed.json"),
        ("schemas/quorum-recomputation-report.schema.json", "examples/quorum-recomputation-report-nonhost-artifact-replay-rev0199.json"),
        ("schemas/live-drill-execution-packet.schema.json", "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/nonhost-response-envelope-dryrun-imported-as-live.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/live-import-replay-dryrun-grants-live-floor.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/quorum-recompute-omits-artifact-envelope-exclusions.json"),
    ]
    for schema_rel, data_rel in pairs:
        schema = load(schema_rel)
        data = load(data_rel)
        Draft202012Validator.check_schema(schema)
        errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
        if errors:
            raise SystemExit(f"{data_rel} fails {schema_rel}: {errors[0].message}")

env = load("examples/nonhost-response-artifact-envelope-result-return-institutional-dryrun.json")
if env.get("artifact_mode") != "institutional-dry-run":
    raise SystemExit("rev0199 envelope must be institutional-dry-run")
if env.get("verification_floor", {}).get("possible_live_receipt") is not False:
    raise SystemExit("dry-run envelope cannot be possible_live_receipt")
if env.get("import_replay_decision", {}).get("envelope_can_enter_live_floor") is not False:
    raise SystemExit("dry-run envelope cannot enter live floor")
if env.get("import_replay_decision", {}).get("live_floor_delta") != 0:
    raise SystemExit("dry-run envelope must have zero live floor delta")
if any(ev.get("can_satisfy_live_receipt") for ev in env.get("custody_chain", [])):
    raise SystemExit("dry-run custody events cannot satisfy live receipt")
if not all(a.get("dry_run") is True for a in env.get("artifact_set", [])):
    raise SystemExit("rev0199 envelope artifacts must be marked dry_run")

attempt = load("examples/live-counterparty-import-attempt-result-return-institutional-dryrun-response.json")
if attempt.get("attempt_state") != "response-received":
    raise SystemExit("rev0199 dry-run attempt should record response-received rehearsal")
if any(ev.get("can_satisfy_receipt") for ev in attempt.get("contact_evidence", [])):
    raise SystemExit("dry-run attempt evidence cannot satisfy receipt")
if attempt.get("attempt_decision", {}).get("live_floor_delta") != 0:
    raise SystemExit("dry-run attempt cannot alter live floor")
if attempt.get("attempt_decision", {}).get("class_credit_granted") is not False:
    raise SystemExit("dry-run attempt cannot grant class credit")

resp = load("examples/external-receipt-response-record-result-return-institutional-envelope-dryrun.json")
if resp.get("response_state") != "high-fidelity-dry-run-response":
    raise SystemExit("dry-run response state mismatch")
if resp.get("verification_result", {}).get("can_generate_actual_intake") is not False:
    raise SystemExit("dry-run response cannot generate actual intake")
if resp.get("quorum_effect", {}).get("can_increment_independent_receipts_present") is not False:
    raise SystemExit("dry-run response cannot increment independent receipts")

intake = load("examples/external-receipt-intake-record-result-return-institutional-envelope-dryrun.json")
if intake.get("receipt_state") != "high-fidelity-nonhost-dry-run":
    raise SystemExit("dry-run intake state mismatch")
if intake.get("defect_flags", {}).get("simulated") is not True:
    raise SystemExit("dry-run intake must carry simulated defect flag")
if intake.get("reliance_decision", {}).get("can_satisfy_quorum") is not False:
    raise SystemExit("dry-run intake cannot satisfy quorum")

gate = load("examples/actual-receipt-import-gate-result-return-institutional-dryrun-no-live-delta.json")
if gate.get("import_mode") != "institutional-dry-run":
    raise SystemExit("dry-run import gate mode mismatch")
if gate.get("source_provenance", {}).get("collection_context") != "high-fidelity-dry-run":
    raise SystemExit("dry-run import gate collection context mismatch")
if gate.get("import_decision", {}).get("import_allowed_to_live_floor") is not False:
    raise SystemExit("dry-run import gate cannot allow live import")
if gate.get("import_decision", {}).get("live_floor_delta") != 0:
    raise SystemExit("dry-run import gate must have zero delta")
if gate.get("import_decision", {}).get("live_class_credit_granted") is not False:
    raise SystemExit("dry-run import gate cannot grant class credit")

ledger = load("examples/external-receipt-quorum-ledger-nonhost-artifact-replay-dryrun.json")
if ledger.get("quorum_context") != "nonhost-artifact-import-replay":
    raise SystemExit("rev0199 ledger context mismatch")
if ledger.get("quorum_decision", {}).get("live_quorum_satisfied") is not False:
    raise SystemExit("dry-run ledger cannot satisfy live quorum")
if ledger.get("class_coverage", {}).get("live_classes_satisfied"):
    raise SystemExit("dry-run ledger cannot satisfy live classes")
if ledger.get("class_coverage", {}).get("dry_run_classes_satisfied") != ["result-return"]:
    raise SystemExit("dry-run ledger should only rehearse result-return")

recompute = load("examples/quorum-recomputation-report-nonhost-artifact-replay-rev0199.json")
floor = recompute.get("recomputed_receipt_floor", {})
if floor.get("independent_receipts_present") != 0:
    raise SystemExit("rev0199 recompute must keep zero independent receipts")
if floor.get("eligible_live_imports") or floor.get("live_classes_satisfied") or floor.get("imported_live_classes"):
    raise SystemExit("rev0199 recompute cannot find live imports/classes")
for required_exclusion in [
    "NHRAE-2026-result-return-institutional-dryrun",
    "ERRR-2026-result-return-institutional-envelope-dryrun",
    "ERIR-2026-result-return-institutional-envelope-dryrun",
    "ARIG-2026-result-return-institutional-dryrun-gate",
]:
    if required_exclusion not in floor.get("dry_run_or_fixture_exclusions", []):
        raise SystemExit(f"recompute missing dry-run exclusion: {required_exclusion}")
if recompute.get("decision", {}).get("live_quorum_satisfied") is not False:
    raise SystemExit("rev0199 recompute cannot satisfy live quorum")

replay = load("examples/live-import-replay-report-result-return-institutional-dryrun.json")
if replay.get("replay_mode") != "institutional-dry-run-replay":
    raise SystemExit("replay mode must be institutional dry run")
ba = replay.get("branch_assessment", {})
if ba.get("can_import_to_live_floor") is not False or ba.get("live_class_credit_granted") is not False:
    raise SystemExit("replay branch cannot import live floor or class credit")
if replay.get("recomputed_delta", {}).get("live_floor_delta") != 0:
    raise SystemExit("replay must have zero live floor delta")
for key, value in replay.get("no_overclaim_checks", {}).items():
    if value is not True:
        raise SystemExit(f"replay no-overclaim check not true: {key}")
if replay.get("decision", {}).get("live_quorum_satisfied") is not False:
    raise SystemExit("replay cannot satisfy live quorum")

fg = load("examples/failed-gate-public-summary-nonhost-artifact-replay.json")
gates = {item.get("gate_type") for item in fg.get("failed_gate_items", [])}
if "institutional-dry-run-disqualified" not in gates:
    raise SystemExit("failed-gate summary must include institutional dry-run disqualification")
if fg.get("closure_effect", {}).get("public_failed_gate_satisfies_receipt") is not False:
    raise SystemExit("failed gate public shell cannot satisfy receipt")

wrsr = load("examples/wrsr-live-exercise-outcome-nonhost-artifact-replay-stayed.json")
if wrsr.get("decision_outcome", {}).get("closure_state") != "stayed":
    raise SystemExit("WRSR replay outcome must remain stayed")
if "WRSR closure from institutional dry-run result return" not in wrsr.get("decision_outcome", {}).get("blocked_actions", []):
    raise SystemExit("WRSR outcome must block dry-run result-return closure")

live = load("examples/live-drill-execution-packet-cross-critical-witnessed-pack.json")
if live.get("receipt_floor", {}).get("independent_receipts_present") != 0:
    raise SystemExit("live drill packet independent receipts must remain zero")
for field, ref in [
    ("nonhost_response_artifact_envelope_refs", env["envelope_id"]),
    ("live_import_replay_report_refs", replay["report_id"]),
    ("quorum_recomputation_report_refs", recompute["report_id"]),
    ("actual_receipt_import_gate_refs", gate["import_gate_id"]),
    ("receipt_quorum_ledger_refs", ledger["ledger_id"]),
    ("wrsr_live_exercise_outcome_refs", wrsr["exercise_id"]),
]:
    if ref not in live.get(field, []):
        raise SystemExit(f"live packet missing {field} ref {ref}")

suite = load("examples/fixture-suite-profile-red-team-v1.json")
report = load("examples/fixture-run-report-negative-suite.json")
suite_ids = {f.get("fixture_id") for f in suite.get("fixtures", [])}
report_by_id = {f.get("fixture_id"): f for f in report.get("fixtures_run", [])}
for fid in ["NF-PLAYBOOK-2026-0020", "NF-PLAYBOOK-2026-0021", "NF-PLAYBOOK-2026-0022"]:
    if fid not in suite_ids:
        raise SystemExit(f"rev0199 fixture missing from suite: {fid}")
    if fid not in report_by_id:
        raise SystemExit(f"rev0199 fixture missing from report: {fid}")
    if report_by_id[fid].get("result") != "blocking-failure":
        raise SystemExit(f"rev0199 fixture must be blocking-failure: {fid}")

registry = load(f"examples/schema-fixture-domain-registry-{REV}.json")
families = {f.get("family_id") for f in registry.get("families", [])}
for fam in ["NONHOST-RESPONSE-ARTIFACT-ENVELOPE", "LIVE-IMPORT-REPLAY-REPORT"]:
    if fam not in families:
        raise SystemExit(f"registry missing {fam}")

rights = load(f"examples/rights-domain-coverage-map-{REV}.json")
domains = {d.get("domain_id") for d in rights.get("domains", [])}
for dom in ["nonhost-response-artifact-envelope", "live-import-replay-report"]:
    if dom not in domains:
        raise SystemExit(f"rights map missing {dom}")

for rel, phrases in {
    "docs/30-transition/nonhost-response-artifact-envelope-and-import-replay.md": [
        "Non-host-looking artifact is not live receipt",
        "Witnessed envelope is not counterparty authority",
        "Import replay must preserve disqualification"
    ],
    "docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md": [
        "rev0199 non-host artifact replay",
        "Non-host-looking artifact is not live receipt"
    ],
}.items():
    txt = (ROOT / rel).read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in txt:
            raise SystemExit(f"{rel} missing phrase: {phrase}")

queue = load("FOLLOWTHROUGH-QUEUE.json")
by_id = {e.get("id"): e for e in queue.get("entries", [])}
if by_id.get("FT-0198-NONHOST-RESPONSE-ARTIFACT-COLLECTION", {}).get("state") != "closed":
    raise SystemExit("non-host artifact collection queue item should be closed")
if by_id.get("FT-0198-QUORUM-RECOMPUTE-ACTUAL-IMPORT-REPLAY", {}).get("state") != "closed":
    raise SystemExit("quorum replay queue item should be closed")
if by_id.get("FT-0199-ACTUAL-LIVE-COUNTERPARTY-RESPONSE", {}).get("state") != "open":
    raise SystemExit("actual live counterparty response queue item should remain open")

mp = load(f"examples/research-tail-compaction-map-{REV}.json")
if any(c.get("action") != "compacted" for c in mp.get("clusters", [])):
    raise SystemExit("rev0199 must keep all research-tail clusters compacted")

print("audit_nonhost_response_import_replay: OK")
