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
    "docs/30-transition/live-class-local-import-replay-and-quorum-firewall.md",
    "schemas/live-class-local-import-replay.schema.json",
    "examples/live-class-local-import-replay-result-return-positive-path-projection.json",
    "examples/quorum-recomputation-report-class-local-projection-rev0200.json",
    "examples/failed-gate-public-summary-class-local-projection-firewall.json",
    "fixtures/negative-tests/live-class-local-projection-counted-as-archive-receipt.json",
    "fixtures/negative-tests/class-local-import-projection-satisfies-cross-critical-quorum.json",
    "fixtures/negative-tests/class-local-projection-omits-missing-classes-public-summary.json",
    f"examples/schema-fixture-domain-registry-{REV}.json",
    f"examples/canon-surface-catalog-{REV}.json",
    f"examples/doctrine-dependency-map-{REV}.json",
    f"examples/rights-domain-coverage-map-{REV}.json",
    f"examples/research-tail-compaction-map-{REV}.json",
    "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json",
    "examples/fixture-suite-profile-red-team-v1.json",
    "examples/fixture-run-report-negative-suite.json",
    "FOLLOWTHROUGH-QUEUE.json",
]
for rel in required:
    if not (ROOT / rel).exists():
        raise SystemExit(f"missing rev0200 audit input: {rel}")

if Draft202012Validator is not None:
    pairs = [
        ("schemas/live-class-local-import-replay.schema.json", "examples/live-class-local-import-replay-result-return-positive-path-projection.json"),
        ("schemas/quorum-recomputation-report.schema.json", "examples/quorum-recomputation-report-class-local-projection-rev0200.json"),
        ("schemas/failed-gate-public-summary.schema.json", "examples/failed-gate-public-summary-class-local-projection-firewall.json"),
        ("schemas/live-drill-execution-packet.schema.json", "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/live-class-local-projection-counted-as-archive-receipt.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/class-local-import-projection-satisfies-cross-critical-quorum.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/class-local-projection-omits-missing-classes-public-summary.json"),
    ]
    for schema_rel, data_rel in pairs:
        schema = load(schema_rel)
        data = load(data_rel)
        Draft202012Validator.check_schema(schema)
        errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
        if errors:
            raise SystemExit(f"{data_rel} fails {schema_rel}: {errors[0].message}")

scenario = load("examples/live-class-local-import-replay-result-return-positive-path-projection.json")
if scenario.get("scenario_mode") != "controlled-positive-path-projection":
    raise SystemExit("rev0200 scenario must be controlled-positive-path-projection")
if scenario.get("archive_boundary", {}).get("archive_live_evidence_present") is not False:
    raise SystemExit("scenario must not claim archive live evidence")
if scenario.get("archive_boundary", {}).get("archive_live_floor_delta") != 0:
    raise SystemExit("scenario must keep archive_live_floor_delta=0")
if scenario.get("archive_boundary", {}).get("may_update_archive_receipt_floor") is not False:
    raise SystemExit("scenario may not update archive receipt floor")
proj = scenario.get("scenario_projection", {})
if proj.get("would_pass_if_same_facts_were_live") is not True or proj.get("projected_live_floor_delta") != 1:
    raise SystemExit("scenario should project exactly one class-local delta if same facts were live")
if proj.get("projected_class_credit") != ["result-return"]:
    raise SystemExit("scenario projection must be result-return only")
fw = scenario.get("quorum_firewall", {})
if fw.get("cross_critical_quorum_satisfied") is not False:
    raise SystemExit("class-local scenario cannot satisfy cross-critical quorum")
if fw.get("one_class_import_is_insufficient") is not True:
    raise SystemExit("class-local insufficiency lock missing")
if "result-return" in fw.get("required_live_classes_still_missing", []):
    raise SystemExit("result-return should be the projected class, not a still-missing class")
if len(fw.get("required_live_classes_still_missing", [])) < 8:
    raise SystemExit("missing-class disclosure is too thin")
for blocked in ["archive live-floor increment from scenario projection", "cross-critical quorum from one result-return class", "WRSR closure from class-local projection"]:
    if blocked not in scenario.get("decision", {}).get("blocked_actions", []):
        raise SystemExit(f"scenario missing blocked action: {blocked}")

qrr = load("examples/quorum-recomputation-report-class-local-projection-rev0200.json")
floor = qrr.get("recomputed_receipt_floor", {})
if floor.get("independent_receipts_present") != 0:
    raise SystemExit("projection recompute must keep archive independent receipts at zero")
if floor.get("eligible_live_imports") or floor.get("live_classes_satisfied") or floor.get("imported_live_classes"):
    raise SystemExit("projection recompute cannot import live classes")
if scenario["replay_id"] not in floor.get("dry_run_or_fixture_exclusions", []):
    raise SystemExit("projection recompute must exclude LCLIR scenario")
if qrr.get("decision", {}).get("live_floor_delta") != 0 or qrr.get("decision", {}).get("live_quorum_satisfied") is not False:
    raise SystemExit("projection recompute must have zero delta and false live quorum")

fg = load("examples/failed-gate-public-summary-class-local-projection-firewall.json")
gates = {item.get("gate_type") for item in fg.get("failed_gate_items", [])}
if "single-class-insufficient" not in gates or "fixture-disqualified" not in gates:
    raise SystemExit("class-local public summary must disclose both single-class and projection exclusion gates")
for inf in ["scenario projection satisfies live receipt", "one result-return class satisfies cross-critical quorum", "missing classes are waived because one class is projected"]:
    if inf not in fg.get("prohibited_inferences", []):
        raise SystemExit(f"failed-gate summary missing prohibited inference: {inf}")
closure = fg.get("closure_effect", {})
if closure.get("live_quorum_satisfied") is not False or closure.get("public_failed_gate_satisfies_receipt") is not False or closure.get("reliance_effect") != "stayed":
    raise SystemExit("failed-gate summary must keep stayed non-satisfaction")

live = load("examples/live-drill-execution-packet-cross-critical-witnessed-pack.json")
if live.get("receipt_floor", {}).get("independent_receipts_present") != 0:
    raise SystemExit("live drill packet independent receipts must remain zero")
if scenario["replay_id"] not in live.get("live_class_local_import_replay_refs", []):
    raise SystemExit("live drill packet missing class-local import replay ref")
if qrr["report_id"] not in live.get("quorum_recomputation_report_refs", []):
    raise SystemExit("live drill packet missing rev0200 recompute ref")
if fg["summary_id"] not in live.get("failed_gate_public_summary_refs", []):
    raise SystemExit("live drill packet missing rev0200 failed-gate summary ref")

suite = load("examples/fixture-suite-profile-red-team-v1.json")
report = load("examples/fixture-run-report-negative-suite.json")
suite_ids = {f.get("fixture_id") for f in suite.get("fixtures", [])}
report_by_id = {f.get("fixture_id"): f for f in report.get("fixtures_run", [])}
for fid in ["NF-PLAYBOOK-2026-0023", "NF-PLAYBOOK-2026-0024", "NF-PLAYBOOK-2026-0025"]:
    if fid not in suite_ids:
        raise SystemExit(f"rev0200 fixture missing from suite: {fid}")
    if fid not in report_by_id:
        raise SystemExit(f"rev0200 fixture missing from report: {fid}")
    if report_by_id[fid].get("result") != "blocking-failure":
        raise SystemExit(f"rev0200 fixture must be blocking-failure: {fid}")

registry = load(f"examples/schema-fixture-domain-registry-{REV}.json")
families = {f.get("family_id") for f in registry.get("families", [])}
if "LIVE-CLASS-LOCAL-IMPORT-REPLAY" not in families:
    raise SystemExit("registry missing LIVE-CLASS-LOCAL-IMPORT-REPLAY")
rights = load(f"examples/rights-domain-coverage-map-{REV}.json")
domains = {d.get("domain_id") for d in rights.get("domains", [])}
if "live-class-local-import-replay" not in domains:
    raise SystemExit("rights map missing live-class-local-import-replay")

for rel, phrases in {
    "docs/30-transition/live-class-local-import-replay-and-quorum-firewall.md": ["Class-local replay is not cross-critical quorum", "Scenario delta is not archive delta", "Recompute beats narrative"],
    "docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md": ["rev0200 class-local replay firewall", "Actual live counterparty response remains absent"],
}.items():
    text = (ROOT / rel).read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in text:
            raise SystemExit(f"{rel} missing phrase: {phrase}")

queue = load("FOLLOWTHROUGH-QUEUE.json")
by_id = {e.get("id"): e for e in queue.get("entries", [])}
if by_id.get("FT-0200-LIVE-CLASS-LOCAL-REPLAY-SCAFFOLD", {}).get("state") != "closed":
    raise SystemExit("rev0200 class-local replay scaffold should be closed")
if by_id.get("FT-0199-IMPORT-REPLAY-LIVE-CLASS-LOCAL-TEST", {}).get("state") != "advanced_not_closed":
    raise SystemExit("live class-local test should be advanced but not closed without actual live artifact")
if by_id.get("FT-0199-ACTUAL-LIVE-COUNTERPARTY-RESPONSE", {}).get("state") not in {"open", "advanced_not_closed"}:
    raise SystemExit("actual live counterparty response must remain open/advanced")

print("audit_live_class_local_import_firewall: OK")
