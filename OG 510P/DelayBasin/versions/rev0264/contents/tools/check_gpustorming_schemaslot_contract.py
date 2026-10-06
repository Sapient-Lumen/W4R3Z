import pathlib

from gpustorming_contract_lib import trajectory_problem_phrase

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/operator-tokens-and-bootstrap-grammar.md"
ALIAS = ROOT / "docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
OPENQ = ROOT / "docs/20-constitution/open-question-registry.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
QUAR = ROOT / "docs/90-quarantine/wild-speculations-2026-03-08.md"
CHANGELOG = ROOT / "CHANGELOG.md"

for path in [DOC, ALIAS, TRAJ, OPENQ, PROMPTS, RUNBOOK, QUAR, CHANGELOG]:
    if not path.exists():
        raise SystemExit(f"missing required gpustorming-schemaslot surface: {path}")

checks = [
    (DOC, ["schema-scrubbed, field-key-swapped, enum-blanded, or type-neutral variant", "schema-slot privilege", "canonical-wire privilege"], "operator-token doc"),
    (ALIAS, ["schema-scrubbed, field-key-swapped, enum-blanded, or type-neutral variant", "field-key privilege", "typed-input privilege"], "alias doc"),
    (TRAJ, [trajectory_problem_phrase("schemaslot")], "trajectory map"),
    (OPENQ, ["schema-scrubbed/field-key-swapped/enum-blanded/type-neutral variant", "schema-slot privilege", "canonical-wire privilege"], "open-question registry"),
    (PROMPTS, ["schema-scrubbed, field-key-swapped, enum-blanded, or type-neutral variant worth checking", "typed-input privilege"], "prompt pairs"),
    (RUNBOOK, ["schema-scrubbed, field-key-swapped, enum-blanded, or type-neutral variant", "JSON keys, schema fields, enum labels, typed input lanes"], "runbook"),
    (QUAR, ["QWS-0152", "schema-slot carry or typed-contract scaffold"], "quarantine"),
    (CHANGELOG, ["schema-scrubbed / field-key-swapped / enum-blanded / type-neutral guard", "check_gpustorming_schemaslot_contract.py"], "changelog"),
]

for path, needles, label in checks:
    text = path.read_text(encoding="utf-8")
    missing = [needle for needle in needles if needle not in text]
    if missing:
        raise SystemExit(f"gpustorming-schemaslot contract missing from {label}: " + ", ".join(missing))

print("check_gpustorming_schemaslot_contract: OK")
