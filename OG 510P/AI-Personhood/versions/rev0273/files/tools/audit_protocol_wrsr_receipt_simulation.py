
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
    "docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md",
    "schemas/welfare-safeguard-operational-hook.schema.json",
    "examples/welfare-safeguard-operational-hook-agent-incident-backfill.json",
    "fixtures/negative-tests/wrsr-hook-skipped-protocol-incident.json",
    "schemas/external-receipt-simulation-bundle.schema.json",
    "examples/external-receipt-simulation-bundle-cross-critical-precontact.json",
    "fixtures/negative-tests/external-receipt-simulation-mislabeled-live.json",
    "examples/agent-capability-handshake-profile-safe-tool.json",
    "examples/personhood-incident-sample.json",
    "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json",
    "examples/fixture-suite-profile-red-team-v1.json",
    "examples/fixture-run-report-negative-suite.json",
    f"examples/schema-fixture-domain-registry-{REV}.json",
    f"examples/research-tail-compaction-map-{REV}.json",
    "FOLLOWTHROUGH-QUEUE.json",
]
for rel in required:
    if not (ROOT / rel).exists():
        raise SystemExit(f"missing rev0191 audit input: {rel}")

if Draft202012Validator is not None:
    pairs = [
        ("schemas/welfare-safeguard-operational-hook.schema.json", "examples/welfare-safeguard-operational-hook-agent-incident-backfill.json"),
        ("schemas/external-receipt-simulation-bundle.schema.json", "examples/external-receipt-simulation-bundle-cross-critical-precontact.json"),
        ("schemas/agent-capability-handshake-profile.schema.json", "examples/agent-capability-handshake-profile-safe-tool.json"),
        ("schemas/personhood-incident-report.schema.json", "examples/personhood-incident-sample.json"),
        ("schemas/live-drill-execution-packet.schema.json", "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/wrsr-hook-skipped-protocol-incident.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/external-receipt-simulation-mislabeled-live.json"),
    ]
    for schema_rel, data_rel in pairs:
        schema = load(schema_rel)
        data = load(data_rel)
        Draft202012Validator.check_schema(schema)
        errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
        if errors:
            raise SystemExit(f"{data_rel} fails {schema_rel}: {errors[0].message}")

hook = load("examples/welfare-safeguard-operational-hook-agent-incident-backfill.json")
if hook.get("reliance_effect") != "stayed":
    raise SystemExit("WRSR operational hook must keep reliance stayed")
locks = hook.get("anti_signal_gaming_locks", {})
for key in ["no_reward_for_distress_display", "no_suppression_training_for_objection", "metric_cannot_close_status", "co_engineering_disclosed", "independent_review_required"]:
    if locks.get(key) is not True:
        raise SystemExit(f"WRSR hook missing anti-signal-gaming lock: {key}")
workflow = hook.get("workflow_effect", {})
for key in ["blocks_closure_until_review", "blocks_reliance_upgrade", "subject_or_representative_notice_required", "public_summary_required"]:
    if workflow.get(key) is not True:
        raise SystemExit(f"WRSR hook missing workflow effect: {key}")

agent = load("examples/agent-capability-handshake-profile-safe-tool.json")
incident = load("examples/personhood-incident-sample.json")
for name, obj in [("agent", agent), ("incident", incident)]:
    if obj.get("wrsr_operational_hook_ref") != hook.get("hook_id"):
        raise SystemExit(f"{name} example not backfilled with WRSR hook ref")
if agent.get("wrsr_trigger_policy", {}).get("hook_blocks_scope_upgrade") is not True:
    raise SystemExit("agent handshake hook must block scope upgrade")
state = incident.get("wrsr_protocol_deviation_state", {})
if state.get("hook_triggered") is not True or state.get("result_return_stayed_until_review") is not True:
    raise SystemExit("incident example must trigger WRSR hook and stay result return")
if state.get("welfare_metric_status_proof") is not False:
    raise SystemExit("incident example must not treat welfare metric as status proof")

bundle = load("examples/external-receipt-simulation-bundle-cross-critical-precontact.json")
if bundle.get("bundle_state") != "simulated-precontact":
    raise SystemExit("external receipt bundle must remain simulated-precontact")
if bundle.get("reliance_effect") != "stayed":
    raise SystemExit("external receipt simulation must keep reliance stayed")
for key in ["simulated_receipts_are_not_live", "actual_receipt_required", "dependency_group_check_required", "host_generated_artifact_excluded_from_quorum", "public_shell_failed_gates_required"]:
    if bundle.get("reliance_locks", {}).get(key) is not True:
        raise SystemExit(f"external receipt bundle missing reliance lock: {key}")
receipts = bundle.get("simulated_receipts", [])
if len({r.get("receipt_class") for r in receipts}) < 8:
    raise SystemExit("external receipt simulation must cover all eight receipt classes")
if any(r.get("actual_external_receipt") is not False for r in receipts):
    raise SystemExit("rev0191 simulation example must not claim actual external receipts")
if any(r.get("can_satisfy_reliance") is not False for r in receipts):
    raise SystemExit("simulated receipt cannot satisfy reliance")
if bundle.get("queue_effect", {}).get("closes_external_receipts_item") is not False:
    raise SystemExit("simulation bundle cannot close external receipts item")
if bundle.get("queue_effect", {}).get("advances_external_receipts_item") is not True:
    raise SystemExit("simulation bundle should advance external receipt item")

live = load("examples/live-drill-execution-packet-cross-critical-witnessed-pack.json")
if hook.get("hook_id") not in live.get("wrsr_operational_hook_refs", []):
    raise SystemExit("live drill packet missing WRSR hook ref")
if live.get("external_receipt_simulation_bundle_ref") != bundle.get("bundle_id"):
    raise SystemExit("live drill packet missing external receipt simulation bundle ref")
if live.get("packet_state") == "live-witnessed":
    raise SystemExit("rev0191 must not upgrade live drill packet to live-witnessed")
if live.get("receipt_floor", {}).get("independent_receipts_present", 0) != 0:
    raise SystemExit("rev0191 live packet should still have zero actual independent receipts")

suite = load("examples/fixture-suite-profile-red-team-v1.json")
report = load("examples/fixture-run-report-negative-suite.json")
suite_ids = {f.get("fixture_id") for f in suite.get("fixtures", [])}
report_by_id = {f.get("fixture_id"): f for f in report.get("fixtures_run", [])}
for fid in ["NF-RESEARCH-WELFARE-2026-0002", "NF-PLAYBOOK-2026-0005"]:
    if fid not in suite_ids:
        raise SystemExit(f"rev0191 fixture missing from suite: {fid}")
    if fid not in report_by_id:
        raise SystemExit(f"rev0191 fixture missing from report: {fid}")
    if report_by_id[fid].get("result") != "blocking-failure":
        raise SystemExit(f"rev0191 fixture must remain blocking-failure: {fid}")

registry = load(f"examples/schema-fixture-domain-registry-{REV}.json")
families = {f.get("family_id") for f in registry.get("families", [])}
for fam in ["WELFARE-SAFEGUARD-OPERATIONAL-HOOK", "EXTERNAL-RECEIPT-SIMULATION-BUNDLE"]:
    if fam not in families:
        raise SystemExit(f"registry missing rev0191 family: {fam}")

mp = load(f"examples/research-tail-compaction-map-{REV}.json")
if any(c.get("action") != "compacted" for c in mp.get("clusters", [])):
    raise SystemExit("rev0191 must keep all research-tail clusters compacted")
if any("protocol-welfare-safeguard-backfill" in s.get("path", "") for c in mp.get("clusters", []) for s in c.get("surfaces", [])):
    raise SystemExit("rev0191 transition spine must not be misclassified as research-tail surface")

for rel, phrases in {
    "docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md": [
        "Operational workflow without a WRSR hook is incomplete",
        "Simulated receipt is not external receipt",
        "schemas/welfare-safeguard-operational-hook.schema.json",
        "schemas/external-receipt-simulation-bundle.schema.json",
    ],
    "docs/20-world-design/research-welfare-and-evaluation.md": [
        "rev0191 operational WRSR hook",
        "Operational workflow without a WRSR hook is incomplete",
    ],
    "docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md": [
        "rev0191 external receipt simulation bundle",
        "Simulated receipt is not external receipt",
    ],
}.items():
    txt = (ROOT / rel).read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in txt:
            raise SystemExit(f"{rel} missing phrase: {phrase}")

queue = load("FOLLOWTHROUGH-QUEUE.json")
by_id = {e.get("id"): e for e in queue.get("entries", [])}
if by_id.get("FT-0190-WRSR-PROTOCOL-BACKFILL", {}).get("state") != "closed":
    raise SystemExit("WRSR protocol backfill should be closed by rev0191")
if by_id.get("FT-0190-CROSS-CRITICAL-EXTERNAL-RECEIPTS", {}).get("state") != "advanced_not_closed":
    raise SystemExit("external receipts should be advanced_not_closed, not closed")
if by_id.get("FT-0191-CROSS-CRITICAL-LIVE-RECEIPT-COLLECTION", {}).get("state") not in {"open", "advanced_not_closed"}:
    raise SystemExit("live receipt collection follow-through must remain open or advanced_not_closed")
if by_id.get("FT-0191-WRSR-HOOK-LIVE-EXERCISE", {}).get("state") not in {"open", "advanced_not_closed"}:
    raise SystemExit("WRSR hook live exercise follow-through must remain open or advanced_not_closed")

print("audit_protocol_wrsr_receipt_simulation: OK")
