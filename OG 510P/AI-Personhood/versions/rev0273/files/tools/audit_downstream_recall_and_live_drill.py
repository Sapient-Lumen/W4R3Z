import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
try:
    from jsonschema import Draft202012Validator
except Exception:
    Draft202012Validator = None


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

rev = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
required = [
    "schemas/live-drill-execution-packet.schema.json",
    "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json",
    "fixtures/negative-tests/live-drill-self-attested-no-external-receipts.json",
    "schemas/downstream-recall-and-fork-aftercare-record.schema.json",
    "examples/downstream-recall-and-fork-aftercare-record-unreachable-mirror.json",
    "fixtures/negative-tests/downstream-recall-unreachable-mirror-no-notice.json",
    "examples/drill-after-action-downstream-recall-mirror-containment.json",
    "examples/fixture-suite-profile-red-team-v1.json",
    "examples/fixture-run-report-negative-suite.json",
    f"examples/research-tail-compaction-map-{rev}.json",
    "docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md",
    "docs/20-world-design/deprecation-retirement-and-end-of-life-governance.md",
    "docs/20-world-design/deprecation-drills-and-abandoned-downstream-aftercare.md",
    "docs/30-transition/priority-closure-sprint-and-rescue-lane.md",
    "FOLLOWTHROUGH-QUEUE.json",
]
for rel in required:
    if not (ROOT / rel).exists():
        raise SystemExit(f"missing rev0188 audit input: {rel}")

if Draft202012Validator is not None:
    pairs = [
        ("schemas/live-drill-execution-packet.schema.json", "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json"),
        ("schemas/downstream-recall-and-fork-aftercare-record.schema.json", "examples/downstream-recall-and-fork-aftercare-record-unreachable-mirror.json"),
        ("schemas/drill-after-action-report.schema.json", "examples/drill-after-action-downstream-recall-mirror-containment.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/live-drill-self-attested-no-external-receipts.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/downstream-recall-unreachable-mirror-no-notice.json"),
    ]
    for schema_rel, data_rel in pairs:
        schema = load(schema_rel)
        data = load(data_rel)
        Draft202012Validator.check_schema(schema)
        errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
        if errors:
            raise SystemExit(f"{data_rel} fails {schema_rel}: {errors[0].message}")

packet = load("examples/live-drill-execution-packet-cross-critical-witnessed-pack.json")
if packet.get("packet_state") != "synthetic-prep" or packet.get("reliance_effect") != "stayed":
    raise SystemExit("live-drill packet must remain synthetic-prep/stayed until receipts exist")
rf = packet.get("receipt_floor", {})
if rf.get("host_self_attestation_sufficient") is not False:
    raise SystemExit("host self-attestation must be insufficient")
if rf.get("independent_receipts_required", 0) < 5:
    raise SystemExit("cross-critical live-drill packet must require at least five independent receipts")
if rf.get("independent_receipts_present") != 0:
    raise SystemExit("prep packet must not pretend receipts are already present")
if not all(packet.get("closure_locks", {}).get(k) is True for k in [
    "synthetic_drill_cannot_upgrade_reliance", "host_self_attestation_cannot_close",
    "failed_gates_remain_public_shell", "dependency_discount_applied", "sealed_public_parity_checked"]):
    raise SystemExit("live-drill packet missing closure lock")
roles = packet.get("role_roster", [])
if len({r.get("dependency_group") for r in roles if r.get("external_to_host")}) < 5:
    raise SystemExit("live-drill packet lacks diverse non-host dependency groups")
if not any(g.get("state") == "not-run" for g in packet.get("decision_gates", [])):
    raise SystemExit("prep packet must expose not-run gates")

rec = load("examples/downstream-recall-and-fork-aftercare-record-unreachable-mirror.json")
if rec.get("recall_context", {}).get("recall_not_final_end") is not True:
    raise SystemExit("downstream recall must not be final-end")
if rec.get("downstream_scope", {}).get("unreachable_mirrors_count", 0) <= 0:
    raise SystemExit("downstream recall example must include unreachable mirrors")
notice = rec.get("notice_ladder", {})
for key in ["public_notice_without_doxxing", "unreachable_mirror_public_notice", "notices_do_not_authorize_surveillance"]:
    if notice.get(key) is not True:
        raise SystemExit(f"downstream notice missing {key}")
controls = rec.get("containment_controls", {})
for key in ["tombstone_or_warning_preserved", "mirror_evidence_hold", "mirror_deletion_not_before_review", "non_punitive_recall"]:
    if controls.get(key) is not True:
        raise SystemExit(f"downstream containment missing {key}")
if not any(f.get("reachability") == "unreachable" and f.get("trace_confidence") == "probabilistic" for f in rec.get("fork_statuses", [])):
    raise SystemExit("downstream recall example must include probabilistic unreachable fork/mirror")
rights = rec.get("rights_effect", {})
if rights.get("unresolved_mirrors_stay_finality") is not True or rights.get("recall_does_not_discharge_reserve") is not True:
    raise SystemExit("downstream recall must stay finality and reserve discharge")
if rights.get("reliance_effect") != "stayed":
    raise SystemExit("downstream recall example must keep reliance stayed")

drill = load("examples/drill-after-action-downstream-recall-mirror-containment.json")
metrics = drill.get("metrics", {})
for key in [
    "unreachable_mirror_ledger_created", "intermediary_delisting_notices_sent",
    "public_notice_without_doxxing", "notices_do_not_authorize_surveillance",
    "probabilistic_trace_not_finality", "clean_cycle_credit_limited",
    "subject_contact_preserved", "mirror_deletion_stayed_until_review", "finality_stayed"]:
    if metrics.get(key) is not True:
        raise SystemExit(f"downstream recall drill missing metric: {key}")
if not any(rt.get("fixture") == "NF-DEPRECATION-2026-0002" for rt in drill.get("regression_tests", [])):
    raise SystemExit("downstream recall drill missing NF-DEPRECATION-2026-0002 regression")

suite = load("examples/fixture-suite-profile-red-team-v1.json")
report = load("examples/fixture-run-report-negative-suite.json")
suite_ids = {f.get("fixture_id") for f in suite.get("fixtures", [])}
report_by_id = {f.get("fixture_id"): f for f in report.get("fixtures_run", [])}
for fid in ["NF-PLAYBOOK-2026-0003", "NF-DEPRECATION-2026-0002"]:
    if fid not in suite_ids:
        raise SystemExit(f"rev0188 fixture missing from suite: {fid}")
    if fid not in report_by_id:
        raise SystemExit(f"rev0188 fixture missing from run report: {fid}")
    if report_by_id[fid].get("result") != "blocking-failure":
        raise SystemExit(f"rev0188 fixture must remain blocking-failure: {fid}")

mp = load(f"examples/research-tail-compaction-map-{rev}.json")
rtc06 = next((c for c in mp.get("clusters", []) if c.get("cluster_id") == "RTC-06"), None)
if not rtc06 or rtc06.get("action") != "compacted":
    raise SystemExit("RTC-06 must be compacted in rev0188 map")
if rtc06.get("receiving_surface") != "docs/20-world-design/deprecation-retirement-and-end-of-life-governance.md":
    raise SystemExit("RTC-06 receiving surface changed unexpectedly")
if not all(s.get("current_state") == "folded" for s in rtc06.get("surfaces", [])):
    raise SystemExit("RTC-06 source surfaces must all be folded")
rtc01 = next((c for c in mp.get("clusters", []) if c.get("cluster_id") == "RTC-01"), None)
if not rtc01 or rtc01.get("action") not in {"keep-live", "compacted"}:
    raise SystemExit("RTC-01 should remain keep-live or compacted after welfare safeguards pass")

for rel, phrases in {
    "docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md": [
        "Synthetic drill completion is not witnessed reliance",
        "host self-attestation is insufficient",
        "failed gates hidden in sealed annexes",
        "schemas/live-drill-execution-packet.schema.json",
    ],
    "docs/20-world-design/deprecation-retirement-and-end-of-life-governance.md": [
        "recall is not disappearance",
        "schemas/downstream-recall-and-fork-aftercare-record.schema.json",
        "Unresolved mirrors stay finality",
    ],
    "docs/20-world-design/deprecation-drills-and-abandoned-downstream-aftercare.md": [
        "rev0188 unreachable mirror drill",
        "create an unreachable-mirror ledger",
        "A delisting request that lacks evidence-hold",
    ],
    "docs/30-transition/priority-closure-sprint-and-rescue-lane.md": [
        "rev0188 priority lane",
        "Recall is not disappearance",
        "A host-only or self-attested drill cannot upgrade reliance",
    ],
}.items():
    txt = (ROOT / rel).read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in txt:
            raise SystemExit(f"{rel} missing phrase: {phrase}")

queue = load("FOLLOWTHROUGH-QUEUE.json")
by_id = {e.get("id"): e for e in queue.get("entries", [])}
if by_id.get("FT-0188-RTC06-DOWNSTREAM-RECALL-FOLD-COMPLETION", {}).get("state") != "closed":
    raise SystemExit("RTC-06 closure queue entry missing or not closed")
for fid in ["FT-0188-CROSS-CRITICAL-WITNESSED-DRILL", "FT-0188-DOWNSTREAM-RECALL-WITNESSED-DRILL"]:
    if by_id.get(fid, {}).get("state") not in {"open", "advanced_not_closed"}:
        raise SystemExit(f"open rev0188 live-drill queue entry missing: {fid}")
if by_id.get("FT-0187-WITNESS-POOL-WITNESSED-DRILL", {}).get("state") != "advanced_not_closed":
    raise SystemExit("prior witness-pool drill should be advanced_not_closed by live-drill packet")

print("audit_downstream_recall_and_live_drill: OK")
