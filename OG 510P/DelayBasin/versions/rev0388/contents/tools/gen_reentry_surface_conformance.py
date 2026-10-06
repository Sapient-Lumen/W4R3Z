import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "REENTRY-CONTRACT.json"
OUT = ROOT / "REENTRY-SURFACE-CONFORMANCE.json"
START = (ROOT / "START_HERE.md").read_text(encoding="utf-8")
AGENTS = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
RUNBOOK = (ROOT / "docs/00-meta/llm-runbook.md").read_text(encoding="utf-8")
PACK = json.loads((ROOT / "context-pack.json").read_text(encoding="utf-8"))

contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
state_surfaces = set(PACK.get("typed_reentry", {}).get("state_surfaces", []))
reentry_contract = PACK.get("reentry_contract", {})

ordered = []
for item in contract["ordered_reads"]:
    path = item["path"]
    ordered.append({
        "path": path,
        "role": item["role"],
        "required": item["required"],
        "exists": (ROOT / path).exists(),
        "mentioned_in_start_here": path in START,
        "mentioned_in_agents": path in AGENTS,
        "mentioned_in_runbook": path in RUNBOOK,
        "listed_in_context_pack": path in state_surfaces or reentry_contract.get("surface") == path or reentry_contract.get("conformance") == path,
    })

commands = []
context_pack_commands = set(PACK.get("commands", {}).values())
for item in contract["commands"]:
    cmd = item["command"]
    commands.append({
        "name": item["name"],
        "command": cmd,
        "required": item["required"],
        "mentioned_in_agents": cmd in AGENTS,
        "mentioned_in_runbook": cmd in RUNBOOK,
        "listed_in_context_pack": cmd in context_pack_commands,
    })

payload = {
    "version": 1,
    "project": contract["project"],
    "contract_path": "REENTRY-CONTRACT.json",
    "profile_id": contract["profile_id"],
    "startup_surfaces": {
        "primary": "START_HERE.md",
        "derivative": "AGENTS.md",
        "runbook": "docs/00-meta/llm-runbook.md",
        "compact_packet": "context-pack.json",
    },
    "ordered_reads": ordered,
    "commands": commands,
    "status": "conformant",
}
OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
print(f"wrote {OUT}")
