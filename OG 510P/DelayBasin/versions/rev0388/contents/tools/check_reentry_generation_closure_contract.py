import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
MAKEFILE = ROOT / "Makefile"
CONTRACT = ROOT / "REENTRY-CONTRACT.json"
PACK = ROOT / "context-pack.json"

for path in (MAKEFILE, CONTRACT, PACK):
    if not path.exists():
        raise SystemExit(f"missing reentry generation closure surface: {path}")

mk = MAKEFILE.read_text(encoding="utf-8")

def target_block(name: str) -> str:
    lines = mk.splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.strip() == f"{name}:":
            start = index
            break
    if start is None:
        raise SystemExit(f"Makefile missing target: {name}")
    block = [lines[start]]
    for line in lines[start + 1:]:
        if re.match(r"^[A-Za-z0-9_.-]+:", line):
            break
        block.append(line)
    return "\n".join(block)

context_block = target_block("context-pack")
if "tools/gen_all_generated_surfaces.py" not in context_block:
    raise SystemExit("context-pack target must run the all-generated-surfaces orchestrator")
for command in [
    "tools/gen_context_pack.py",
    "tools/gen_innovation_packet.py",
    "tools/gen_frontier_ticket.py",
    "tools/gen_replay_capsule.py",
    "tools/gen_compact_surface_bundle.py",
    "tools/gen_validation_index.py",
    "tools/gen_validation_toolchain_manifest.py",
    "tools/gen_schema_coverage_audit.py",
    "tools/gen_schema_conformance_audit.py",
    "tools/gen_archive_economy_audit.py",
    "tools/gen_reentry_surface_conformance.py",
]:
    if command not in (ROOT / "tools" / "generated_surface_lib.py").read_text(encoding="utf-8"):
        raise SystemExit(f"generated_surface_lib missing required generator: {command}")

handoff_block = target_block("handoff-release")
for needle in ["$(MAKE) context-pack", "$(MAKE) lint", "$(MAKE) package-release"]:
    if needle not in handoff_block:
        raise SystemExit(f"handoff-release target missing required step: {needle}")

contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
commands = {(item.get("name"), item.get("command"), item.get("required")) for item in contract.get("commands", [])}
if ("reentry_conformance", "python3 tools/gen_reentry_surface_conformance.py", True) not in commands:
    raise SystemExit("REENTRY-CONTRACT.json must require the reentry_conformance generator")

pack = json.loads(PACK.read_text(encoding="utf-8"))
if pack.get("commands", {}).get("context_pack") != "make context-pack":
    raise SystemExit("context-pack.json commands must name the context-pack target")
if pack.get("commands", {}).get("all_generated_surfaces") != "python3 tools/gen_all_generated_surfaces.py":
    raise SystemExit("context-pack.json commands must name the all-generated-surfaces orchestrator")
if pack.get("commands", {}).get("reentry_conformance") != "python3 tools/gen_reentry_surface_conformance.py":
    raise SystemExit("context-pack.json commands must name the reentry_conformance generator")
if pack.get("commands", {}).get("validation_toolchain") != "python3 tools/gen_validation_toolchain_manifest.py":
    raise SystemExit("context-pack.json commands must name the validation toolchain manifest generator")
if pack.get("commands", {}).get("schema_coverage_audit") != "python3 tools/gen_schema_coverage_audit.py":
    raise SystemExit("context-pack.json commands must name the schema coverage audit generator")
if pack.get("commands", {}).get("basis_provenance_audit") != "python3 tools/gen_basis_provenance_audit.py":
    raise SystemExit("context-pack.json commands must name the basis provenance audit generator")
if pack.get("commands", {}).get("schema_conformance_audit") != "python3 tools/gen_schema_conformance_audit.py":
    raise SystemExit("context-pack.json commands must name the schema conformance audit generator")
if pack.get("commands", {}).get("archive_economy_audit") != "python3 tools/gen_archive_economy_audit.py":
    raise SystemExit("context-pack.json commands must name the archive economy audit generator")

print("check_reentry_generation_closure_contract: OK")
