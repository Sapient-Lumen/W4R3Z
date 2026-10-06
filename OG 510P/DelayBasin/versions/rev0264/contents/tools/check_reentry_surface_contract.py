import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "REENTRY-CONTRACT.json"
CONFORMANCE = ROOT / "REENTRY-SURFACE-CONFORMANCE.json"
START = ROOT / "START_HERE.md"
AGENTS = ROOT / "AGENTS.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
PACK = ROOT / "context-pack.json"

for path in (CONTRACT, CONFORMANCE, START, AGENTS, RUNBOOK, PACK):
    if not path.exists():
        raise SystemExit(f"missing required reentry-contract surface: {path}")

contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
required_top = {"version", "project", "purpose", "profile_id", "ordered_reads", "commands", "non_authority_note"}
missing = sorted(required_top - set(contract))
if missing:
    raise SystemExit("REENTRY-CONTRACT.json missing keys: " + ", ".join(missing))
if contract["project"] != "DelayBasin":
    raise SystemExit("REENTRY-CONTRACT.json project must be DelayBasin")
if contract["profile_id"] != "careful-revision-pass":
    raise SystemExit("REENTRY-CONTRACT.json profile_id must be careful-revision-pass")

expected_reads = [
    ("START_HERE.md", "primary_landing"),
    ("AGENTS.md", "derivative_wrapper"),
    ("docs/00-meta/llm-runbook.md", "operator_runbook"),
    ("SURFACE-STATUS.json", "current_truth"),
    ("context-pack.json", "compact_reentry_packet"),
    ("REVISION-RECEIPT.json", "revision_summary"),
    ("DATACUBE-TRANSFER-LEDGER.json", "comparison_memory"),
    ("WITNESS-VOCABULARY.json", "controlled_tokens"),
    ("RELEASE-MANIFEST.json", "citation_identity"),
]
reads = contract["ordered_reads"]
if [(item.get("path"), item.get("role")) for item in reads] != expected_reads:
    raise SystemExit("REENTRY-CONTRACT.json ordered_reads drifted from admitted reentry contract")
for item in reads:
    if item.get("required") is not True:
        raise SystemExit("all ordered_reads must be required in REENTRY-CONTRACT.json")
    if not (ROOT / item["path"]).exists():
        raise SystemExit(f"REENTRY-CONTRACT ordered read missing: {item['path']}")

expected_commands = [
    ("context_pack", "python3 tools/gen_context_pack.py", True),
    ("reentry_conformance", "python3 tools/gen_reentry_surface_conformance.py", True),
    ("lint", "make lint", True),
    ("package_release", "make package-release STAMP=... SLUG=...", False),
]
commands = contract["commands"]
if [(item.get("name"), item.get("command"), item.get("required")) for item in commands] != expected_commands:
    raise SystemExit("REENTRY-CONTRACT.json commands drifted from admitted reentry contract")

pack = json.loads(PACK.read_text(encoding="utf-8"))
rc = pack.get("reentry_contract")
if rc != {
    "surface": "REENTRY-CONTRACT.json",
    "conformance": "REENTRY-SURFACE-CONFORMANCE.json",
    "profile_id": "careful-revision-pass",
}:
    raise SystemExit("context-pack reentry_contract block drifted from admitted contract")
tr = pack.get("typed_reentry", {})
for rel in ("REENTRY-CONTRACT.json", "REENTRY-SURFACE-CONFORMANCE.json"):
    if rel not in tr.get("state_surfaces", []):
        raise SystemExit(f"typed_reentry.state_surfaces missing {rel}")

start = START.read_text(encoding="utf-8")
agents = AGENTS.read_text(encoding="utf-8")
runbook = RUNBOOK.read_text(encoding="utf-8")
if "REENTRY-CONTRACT.json" not in start:
    raise SystemExit("START_HERE.md missing REENTRY-CONTRACT.json wiring")
if "REENTRY-CONTRACT.json" not in agents:
    raise SystemExit("AGENTS.md missing REENTRY-CONTRACT.json wiring")
if "REENTRY-SURFACE-CONFORMANCE.json" not in agents:
    raise SystemExit("AGENTS.md missing REENTRY-SURFACE-CONFORMANCE.json wiring")
if "REENTRY-CONTRACT.json" not in runbook or "REENTRY-SURFACE-CONFORMANCE.json" not in runbook:
    raise SystemExit("llm-runbook missing reentry contract/conformance guidance")
if "python3 tools/gen_reentry_surface_conformance.py" not in runbook:
    raise SystemExit("llm-runbook missing reentry conformance command guidance")

# Recompute expected conformance payload inline
state_surfaces = set(tr.get("state_surfaces", []))
ordered = []
for item in reads:
    path = item["path"]
    ordered.append({
        "path": path,
        "role": item["role"],
        "required": item["required"],
        "exists": (ROOT / path).exists(),
        "mentioned_in_start_here": path in start,
        "mentioned_in_agents": path in agents,
        "mentioned_in_runbook": path in runbook,
        "listed_in_context_pack": path in state_surfaces or rc.get("surface") == path or rc.get("conformance") == path,
    })
expected_payload = {
    "version": 1,
    "project": "DelayBasin",
    "contract_path": "REENTRY-CONTRACT.json",
    "profile_id": "careful-revision-pass",
    "startup_surfaces": {
        "primary": "START_HERE.md",
        "derivative": "AGENTS.md",
        "runbook": "docs/00-meta/llm-runbook.md",
        "compact_packet": "context-pack.json",
    },
    "ordered_reads": ordered,
    "commands": [
        {
            "name": item["name"],
            "command": item["command"],
            "required": item["required"],
            "mentioned_in_agents": item["command"] in agents,
            "mentioned_in_runbook": item["command"] in runbook,
            "listed_in_context_pack": pack.get("commands", {}).get("lint") == item["command"] or pack.get("commands", {}).get("package_release") == item["command"],
        }
        for item in commands
    ],
    "status": "conformant",
}
conformance = json.loads(CONFORMANCE.read_text(encoding="utf-8"))
if conformance != expected_payload:
    raise SystemExit("REENTRY-SURFACE-CONFORMANCE.json drifted from generated conformance payload")

for item in ordered:
    if not item["exists"]:
        raise SystemExit(f"reentry conformance reports missing required surface: {item['path']}")
    if not (item["mentioned_in_start_here"] or item["mentioned_in_agents"] or item["listed_in_context_pack"]):
        raise SystemExit(f"reentry conformance found no startup mention for required surface: {item['path']}")

print("check_reentry_surface_contract: OK")
