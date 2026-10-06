import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/operator-tokens-and-bootstrap-grammar.md"
ALIAS = ROOT / "docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
QUAR = ROOT / "docs/90-quarantine/wild-speculations-2026-03-08.md"
CHANGELOG = ROOT / "CHANGELOG.md"

for path in (DOC, ALIAS, TRAJ, PROMPTS, RUNBOOK, QUAR, CHANGELOG):
    if not path.exists():
        raise SystemExit(f"missing required gpustorming surface: {path}")

doc_text = DOC.read_text(encoding="utf-8")
for needle in [
    "GPUstorming as handle-family / placement-and-density sweep",
    "active handle family",
    "one placement variant",
    "one density variant",
    "downstream divergence signature",
]:
    if needle not in doc_text:
        raise SystemExit(f"gpustorming contract missing from operator-token doc: {needle}")

alias_text = ALIAS.read_text(encoding="utf-8")
for needle in ["density variants that could steal or share the routing effect", "placement variant", "density variant"]:
    if needle not in alias_text:
        raise SystemExit(f"gpustorming contract missing from alias doc: {needle}")

traj_text = TRAJ.read_text(encoding="utf-8")
if "family plus placement/density problem" not in traj_text:
    raise SystemExit("gpustorming contract missing from trajectory map")

prompt_text = PROMPTS.read_text(encoding="utf-8")
for needle in ["placement variant worth checking", "density variant worth checking", "position/density privilege"]:
    if needle not in prompt_text:
        raise SystemExit(f"gpustorming contract missing from prompt pairs: {needle}")

runbook_text = RUNBOOK.read_text(encoding="utf-8")
for needle in ["do not certify an exact magic word from one sharp win", "placement variant", "density variant"]:
    if needle not in runbook_text:
        raise SystemExit(f"gpustorming contract missing from runbook: {needle}")

quar_text = QUAR.read_text(encoding="utf-8")
for needle in ["QWS-0134", "sparse routing scaffold", "handle family, placement, and density together"]:
    if needle not in quar_text:
        raise SystemExit(f"gpustorming contract missing from quarantine: {needle}")

change_text = CHANGELOG.read_text(encoding="utf-8")
for needle in ["handle-family / placement-and-density sweep", "check_gpustorming_contract.py"]:
    if needle not in change_text:
        raise SystemExit(f"gpustorming contract missing from changelog: {needle}")

print("check_gpustorming_contract: OK")
