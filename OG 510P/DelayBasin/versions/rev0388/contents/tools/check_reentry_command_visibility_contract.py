import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "REENTRY-CONTRACT.json"
PACK = ROOT / "context-pack.json"
CONFORMANCE = ROOT / "REENTRY-SURFACE-CONFORMANCE.json"

contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
pack = json.loads(PACK.read_text(encoding="utf-8"))
conformance = json.loads(CONFORMANCE.read_text(encoding="utf-8"))

pack_commands = pack.get("commands", {})
if not isinstance(pack_commands, dict) or not pack_commands:
    raise SystemExit("context-pack commands must be a non-empty object")
pack_values = set(pack_commands.values())

required_named = {
    "context_pack": "make context-pack",
    "reentry_conformance": "python3 tools/gen_reentry_surface_conformance.py",
    "lint": "make lint",
    "validation_toolchain": "python3 tools/gen_validation_toolchain_manifest.py",
    "package_release": "make package-release STAMP=... SLUG=...",
}
for name, command in required_named.items():
    if pack_commands.get(name) != command:
        raise SystemExit(f"context-pack commands missing or drifted for {name}: {command}")

rows = {row.get("name"): row for row in conformance.get("commands", [])}
for item in contract.get("commands", []):
    name = item.get("name")
    command = item.get("command")
    row = rows.get(name)
    if row is None:
        raise SystemExit(f"REENTRY-SURFACE-CONFORMANCE missing command row: {name}")
    if row.get("command") != command:
        raise SystemExit(f"conformance command drift for {name}")
    expected = command in pack_values
    if row.get("listed_in_context_pack") != expected:
        raise SystemExit(f"conformance listed_in_context_pack mismatch for {name}")
    if item.get("required") and not (row.get("mentioned_in_agents") or row.get("mentioned_in_runbook") or row.get("listed_in_context_pack")):
        raise SystemExit(f"required reentry command has no visible startup cue: {name}")

print("check_reentry_command_visibility_contract: OK")
