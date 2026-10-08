import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
try:
    from jsonschema import Draft202012Validator
except Exception:
    Draft202012Validator = None


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

inputs = [
    "schemas/federated-namespace-continuity-record.schema.json",
    "examples/federated-namespace-continuity-record-host-exit.json",
    "fixtures/negative-tests/namespace-propagation-stale-tombstone-no-alias.json",
    "examples/drill-after-action-namespace-failover-host-exit.json",
    "examples/fixture-suite-profile-red-team-v1.json",
    "examples/fixture-run-report-negative-suite.json",
    "examples/research-tail-compaction-map-" + (ROOT / "VERSION").read_text(encoding="utf-8").strip() + ".json",
    "docs/20-world-design/packet-registry-normalization-and-wire-profile.md",
    "docs/30-transition/platform-account-portability-and-social-graph-continuity.md",
    "docs/00-meta/research-tail-compaction-and-refactor-map.md",
    "FOLLOWTHROUGH-QUEUE.json",
]
for rel in inputs:
    if not (ROOT / rel).exists():
        raise SystemExit(f"missing namespace-continuity audit input: {rel}")

schema = load(ROOT / "schemas/federated-namespace-continuity-record.schema.json")
example = load(ROOT / "examples/federated-namespace-continuity-record-host-exit.json")
fixture = load(ROOT / "fixtures/negative-tests/namespace-propagation-stale-tombstone-no-alias.json")
drill = load(ROOT / "examples/drill-after-action-namespace-failover-host-exit.json")
suite = load(ROOT / "examples/fixture-suite-profile-red-team-v1.json")
report = load(ROOT / "examples/fixture-run-report-negative-suite.json")
mp = load(ROOT / "examples" / f"research-tail-compaction-map-{(ROOT / 'VERSION').read_text(encoding='utf-8').strip()}.json")

if Draft202012Validator is not None:
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(example), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"federated namespace example fails schema: {errors[0].message}")
    fixture_schema = load(ROOT / "schemas/negative-test-fixture.schema.json")
    errors = sorted(Draft202012Validator(fixture_schema).iter_errors(fixture), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"namespace negative fixture fails schema: {errors[0].message}")
    drill_schema = load(ROOT / "schemas/drill-after-action-report.schema.json")
    errors = sorted(Draft202012Validator(drill_schema).iter_errors(drill), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"namespace failover drill fails drill schema: {errors[0].message}")

if fixture.get("fixture_id") != "NF-SOCIAL-GRAPH-2026-0002":
    raise SystemExit("namespace continuity fixture id changed unexpectedly")

suite_ids = {item.get("fixture_id") for item in suite.get("fixtures", [])}
report_items = {item.get("fixture_id"): item for item in report.get("fixtures_run", [])}
if "NF-SOCIAL-GRAPH-2026-0002" not in suite_ids:
    raise SystemExit("namespace fixture missing from fixture-suite profile")
if "NF-SOCIAL-GRAPH-2026-0002" not in report_items:
    raise SystemExit("namespace fixture missing from fixture-run report")
if report_items["NF-SOCIAL-GRAPH-2026-0002"].get("result") not in {"passed", "blocking-failure"}:
    raise SystemExit("namespace fixture must be actively exercised or blocking, not skipped")

if example.get("actor_identity", {}).get("actor_discovery_is_authorization") is not False:
    raise SystemExit("actor discovery must be explicitly non-authorizing")
if example.get("reliance_effect") not in {"conditional", "stayed", "blocked", "downgraded"}:
    raise SystemExit("namespace continuity record must constrain reliance while proofs remain open")
if example.get("relay_floor", {}).get("minimum_quorum", 0) < 2:
    raise SystemExit("protected relay floor must require at least two relays in the host-exit example")
if not example.get("tombstone_and_successor_policy", {}).get("successor_refs"):
    raise SystemExit("namespace continuity record lacks successor-chain refs")
if "reuse" not in example.get("tombstone_and_successor_policy", {}).get("blocked_reuse_rule", "").lower():
    raise SystemExit("namespace continuity record lacks explicit blocked-reuse rule")

metrics = drill.get("metrics", {})
for key in ["tombstone_reuse_blocked", "successor_chain_public_shell_present", "protected_relay_quorum_met", "low_volume_suppression_blocked", "actor_discovery_caveated_as_non_authorization"]:
    if metrics.get(key) is not True:
        raise SystemExit(f"namespace failover drill missing or false metric: {key}")
if metrics.get("alias_redirect_working_minutes", 9999) > 60:
    raise SystemExit("namespace failover drill did not restore alias redirect within one hour")
if not any(rt.get("fixture") == "NF-SOCIAL-GRAPH-2026-0002" for rt in drill.get("regression_tests", [])):
    raise SystemExit("namespace failover drill does not regression-test the namespace fixture")

rtc05 = next((c for c in mp.get("clusters", []) if c.get("cluster_id") == "RTC-05"), None)
if not rtc05 or rtc05.get("action") != "compacted":
    raise SystemExit("RTC-05 must be marked compacted in the active research-tail compaction map")
if not all(s.get("current_state") == "folded" for s in rtc05.get("surfaces", [])):
    raise SystemExit("RTC-05 compacted cluster must mark every source surface folded")

packet_doc = (ROOT / "docs/20-world-design/packet-registry-normalization-and-wire-profile.md").read_text(encoding="utf-8")
for phrase in [
    "Actor discovery is not subject authorization",
    "tombstone cannot be reused",
    "protected relay floor",
    "federation overflow",
    "schemas/federated-namespace-continuity-record.schema.json",
]:
    if phrase not in packet_doc:
        raise SystemExit(f"packet registry surface missing namespace phrase: {phrase}")

platform_doc = (ROOT / "docs/30-transition/platform-account-portability-and-social-graph-continuity.md").read_text(encoding="utf-8")
for phrase in ["old alias is a non-reusable tombstone", "successor-chain pointer", "actor discovery"]:
    if phrase not in platform_doc:
        raise SystemExit(f"social-graph portability surface missing namespace phrase: {phrase}")

queue = load(ROOT / "FOLLOWTHROUGH-QUEUE.json")
entry = next((e for e in queue.get("entries", []) if e.get("id") == "FT-0184-RTC05-NAMESPACE-FOLD-COMPLETION"), None)
if not entry or entry.get("state") != "closed":
    raise SystemExit("RTC-05 namespace fold queue entry was not closed by rev0184 artifacts")
open_entry = next((e for e in queue.get("entries", []) if e.get("id") == "FT-0184-NAMESPACE-FAILOVER-LIVE-DRILL"), None)
if not open_entry or open_entry.get("state") not in {"open", "advanced_not_closed"}:
    raise SystemExit("live namespace failover drill follow-through entry is missing")

print("audit_namespace_continuity: OK")
