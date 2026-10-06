import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
VALIDATION = ROOT / "VALIDATION-INDEX.json"
GUIDE = ROOT / "docs/00-meta/validation-index.md"
RUN_LINT = ROOT / "tools/run_lint_suite.py"
START = ROOT / "START_HERE.md"
AGENTS = ROOT / "AGENTS.md"
README = ROOT / "README.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
METHOD = ROOT / "docs/10-method/method-overview.md"
PACK = ROOT / "context-pack.json"

for path in (VALIDATION, GUIDE, RUN_LINT, START, AGENTS, README, RUNBOOK, METHOD, PACK):
    if not path.exists():
        raise SystemExit(f"missing validation-index surface: {path}")

text = RUN_LINT.read_text(encoding="utf-8")
block = re.search(r"tools\s*=\s*\[(.*?)\]\n\nshadow_tools", text, re.S)
if not block:
    raise SystemExit("could not parse run_lint_suite.py tools list")
count = len(re.findall(r'"([^"]+\.py)"', block.group(1)))
count += len(sorted((ROOT / "tools").glob("check_shadow_*_contract.py")))

payload = json.loads(VALIDATION.read_text(encoding="utf-8"))
required_top = {"project", "revision", "surface", "guide_surface", "derivative_note", "tool_count", "commands", "generated_surfaces", "coverage_scope", "families"}
missing = sorted(required_top - set(payload))
if missing:
    raise SystemExit("VALIDATION-INDEX.json missing keys: " + ", ".join(missing))
if payload["project"] != "DelayBasin":
    raise SystemExit("VALIDATION-INDEX.json project must be DelayBasin")
if payload["surface"] != "VALIDATION-INDEX.json":
    raise SystemExit("VALIDATION-INDEX.json surface self-id drifted")
if payload["guide_surface"] != "docs/00-meta/validation-index.md":
    raise SystemExit("VALIDATION-INDEX.json guide_surface drifted")
if payload["tool_count"] != count:
    raise SystemExit(f"VALIDATION-INDEX.json tool_count {payload['tool_count']} != lint-suite count {count}")

required_commands = {
    "python3 tools/gen_context_pack.py",
    "python3 tools/gen_innovation_packet.py",
    "python3 tools/gen_frontier_ticket.py",
    "python3 tools/gen_replay_capsule.py",
    "python3 tools/gen_validation_index.py",
    "python3 tools/gen_compact_surface_bundle.py",
    "python3 tools/gen_reentry_surface_conformance.py",
    "make lint",
    "make package-release STAMP=... SLUG=...",
}
seen_commands = {row.get("command") for row in payload["commands"]}
if seen_commands != required_commands:
    raise SystemExit("VALIDATION-INDEX.json commands drifted from admitted command inventory")

required_surfaces = {
    "context-pack.json",
    "innovation-packet.json",
    "frontier-ticket.json",
    "replay-capsule.json",
    "VALIDATION-INDEX.json",
    "compact-surface-bundle.json",
    "docs/00-meta/validation-index.md",
    "REENTRY-SURFACE-CONFORMANCE.json",
    "RELEASE-MANIFEST.json",
}
seen_surfaces = {row.get("surface") for row in payload["generated_surfaces"]}
if seen_surfaces != required_surfaces:
    raise SystemExit("VALIDATION-INDEX.json generated_surfaces drifted from admitted validation inventory")

family_ids = [row.get("id") for row in payload["families"]]
expected_families = [
    "discovery_release_identity",
    "startup_derivative_packets",
    "receipt_basis_status",
    "governed_vocab_registries",
    "continuity_ledgers_transfer",
    "gpustorming_handle_family",
    "method_witness_families",
]
if family_ids != expected_families:
    raise SystemExit("VALIDATION-INDEX.json families drifted from admitted family inventory")

for row in payload["families"]:
    if not row.get("tools"):
        raise SystemExit(f"validation family missing tools: {row.get('id')}")
    if row.get("tool_count") != len(row["tools"]):
        raise SystemExit(f"validation family tool_count mismatch: {row.get('id')}")

for path in (START, AGENTS, README, RUNBOOK, METHOD):
    txt = path.read_text(encoding="utf-8")
    if "VALIDATION-INDEX.json" not in txt:
        raise SystemExit(f"{path.relative_to(ROOT)} missing VALIDATION-INDEX.json mention")
    if "validation-index.md" not in txt:
        raise SystemExit(f"{path.relative_to(ROOT)} missing validation-index.md mention")

pack = json.loads(PACK.read_text(encoding="utf-8"))
validation = pack.get("validation")
if validation != {"surface": "VALIDATION-INDEX.json", "guide": "docs/00-meta/validation-index.md"}:
    raise SystemExit("context-pack validation block drifted")
state_surfaces = set(pack.get("typed_reentry", {}).get("state_surfaces", []))
for rel in ("innovation-packet.json", "replay-capsule.json", "VALIDATION-INDEX.json", "docs/00-meta/validation-index.md", "compact-surface-bundle.json"):
    if rel not in state_surfaces:
        raise SystemExit(f"typed_reentry.state_surfaces missing {rel}")

print("check_validation_index_contract: OK")
