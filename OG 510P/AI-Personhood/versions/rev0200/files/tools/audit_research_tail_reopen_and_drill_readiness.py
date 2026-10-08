
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
    "schemas/witnessed-drill-readiness-ledger.schema.json",
    "examples/witnessed-drill-readiness-ledger-cross-critical-preflight.json",
    "fixtures/negative-tests/witnessed-drill-preflight-missing-external-receipt-class.json",
    "schemas/research-tail-reopen-gate.schema.json",
    "examples/research-tail-reopen-gate-welfare-new-metric-quarantine.json",
    "fixtures/negative-tests/research-tail-reopen-unmapped-new-surface.json",
    "docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md",
    "docs/00-meta/research-tail-reopen-gate-and-sprawl-control.md",
    f"examples/research-tail-compaction-map-{REV}.json",
    "examples/fixture-suite-profile-red-team-v1.json",
    "examples/fixture-run-report-negative-suite.json",
    "FOLLOWTHROUGH-QUEUE.json",
]
for rel in required:
    if not (ROOT / rel).exists():
        raise SystemExit(f"missing rev0190 audit input: {rel}")

if Draft202012Validator is not None:
    pairs = [
        ("schemas/witnessed-drill-readiness-ledger.schema.json", "examples/witnessed-drill-readiness-ledger-cross-critical-preflight.json"),
        ("schemas/research-tail-reopen-gate.schema.json", "examples/research-tail-reopen-gate-welfare-new-metric-quarantine.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/witnessed-drill-preflight-missing-external-receipt-class.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/research-tail-reopen-unmapped-new-surface.json"),
    ]
    for schema_rel, data_rel in pairs:
        schema = load(schema_rel)
        data = load(data_rel)
        Draft202012Validator.check_schema(schema)
        errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
        if errors:
            raise SystemExit(f"{data_rel} fails {schema_rel}: {errors[0].message}")

ledger = load("examples/witnessed-drill-readiness-ledger-cross-critical-preflight.json")
if ledger.get("readiness_state") != "preflight-ready":
    raise SystemExit("witnessed drill readiness ledger must be preflight-ready")
if ledger.get("reliance_effect") != "stayed":
    raise SystemExit("preflight readiness must keep reliance stayed")
locks = ledger.get("not_yet_evidence_locks", {})
for key in ["preflight_is_not_witnessed_evidence", "missing_receipt_blocks_reliance", "host_role_excluded_from_quorum", "failed_injection_public_shell_required"]:
    if locks.get(key) is not True:
        raise SystemExit(f"witnessed-drill readiness missing lock: {key}")
receipt_classes = ledger.get("receipt_classes", [])
if len(receipt_classes) < 7:
    raise SystemExit("cross-critical preflight ledger needs at least seven receipt classes")
if any(r.get("host_controlled_sufficient") is not False for r in receipt_classes if r.get("required")):
    raise SystemExit("host-controlled receipt cannot be sufficient for required classes")
if any(r.get("status") == "received" for r in receipt_classes):
    raise SystemExit("rev0190 preflight example must not pretend external receipts were collected")
if ledger.get("go_no_go_decision", {}).get("decision_state") == "live-run-authorized":
    raise SystemExit("rev0190 preflight ledger must not authorize live run")
if len({r.get("receipt_class") for r in ledger.get("role_requirements", [])}) < 7:
    raise SystemExit("role requirements do not cover enough receipt classes")

reopen = load("examples/research-tail-reopen-gate-welfare-new-metric-quarantine.json")
if reopen.get("decision", {}).get("decision_state") != "quarantine":
    raise SystemExit("reopen example should quarantine the unbacked metric")
if reopen.get("routing", {}).get("new_research_surface_active_before_gate") is not False:
    raise SystemExit("new research surface cannot be active before gate")
if reopen.get("artifact_hooks", {}).get("object_hook_present") or reopen.get("artifact_hooks", {}).get("fixture_hook_present"):
    raise SystemExit("quarantine example should not claim object/fixture hooks are already present")
if reopen.get("reliance_effect") != "stayed":
    raise SystemExit("reopen quarantine must stay reliance")

mp = load(f"examples/research-tail-compaction-map-{REV}.json")
if any(c.get("action") != "compacted" for c in mp.get("clusters", [])):
    raise SystemExit("rev0190 research-tail map should keep all clusters compacted unless a reopen request is approved")
actual = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "docs" / "20-world-design").glob("research-*.md"))
assigned = []
for cluster in mp.get("clusters", []):
    for surface in cluster.get("surfaces", []):
        assigned.append(surface.get("path"))
if sorted(assigned) != actual:
    raise SystemExit("research-tail reopen gate found unmapped or extra research surfaces")
if mp.get("research_surface_count") != len(actual):
    raise SystemExit("research-tail count stale under reopen gate")

suite = load("examples/fixture-suite-profile-red-team-v1.json")
report = load("examples/fixture-run-report-negative-suite.json")
suite_ids = {f.get("fixture_id") for f in suite.get("fixtures", [])}
report_by_id = {f.get("fixture_id"): f for f in report.get("fixtures_run", [])}
for fid in ["NF-PLAYBOOK-2026-0004", "NF-SCHEMA-2026-0004"]:
    if fid not in suite_ids:
        raise SystemExit(f"rev0190 fixture missing from suite: {fid}")
    if fid not in report_by_id:
        raise SystemExit(f"rev0190 fixture missing from run report: {fid}")
    if report_by_id[fid].get("result") != "blocking-failure":
        raise SystemExit(f"rev0190 fixture must remain blocking-failure: {fid}")

for rel, phrases in {
    "docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md": [
        "Preflight readiness is not witnessed reliance",
        "host_controlled",
        "No-go conditions",
        "schemas/witnessed-drill-readiness-ledger.schema.json",
    ],
    "docs/00-meta/research-tail-reopen-gate-and-sprawl-control.md": [
        "No new research-tail surface becomes active without a reopen gate",
        "schemas/research-tail-reopen-gate.schema.json",
        "shadow doctrine",
        "artifact_hooks",
    ],
}.items():
    txt = (ROOT / rel).read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in txt:
            raise SystemExit(f"{rel} missing phrase: {phrase}")

queue = load("FOLLOWTHROUGH-QUEUE.json")
by_id = {e.get("id"): e for e in queue.get("entries", [])}
if by_id.get("FT-0189-RESEARCH-TAIL-REOPEN-GATE", {}).get("state") != "closed":
    raise SystemExit("research-tail reopen gate queue item must be closed by rev0190")
if by_id.get("FT-0188-CROSS-CRITICAL-WITNESSED-DRILL", {}).get("state") != "advanced_not_closed":
    raise SystemExit("cross-critical witnessed drill should be advanced_not_closed, not closed")
if by_id.get("FT-0190-CROSS-CRITICAL-EXTERNAL-RECEIPTS", {}).get("state") not in {"open", "advanced_not_closed"}:
    raise SystemExit("external receipt capture queue item must remain open or advanced_not_closed")

print("audit_research_tail_reopen_and_drill_readiness: OK")
