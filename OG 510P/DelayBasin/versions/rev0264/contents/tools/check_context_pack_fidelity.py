import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
pack = json.loads((ROOT / "context-pack.json").read_text(encoding="utf-8"))

for rel in pack.get("must_read", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"context-pack must_read path missing: {rel}")

required_reentry_docs = {
    "docs/10-method/witness-vocabularies-state-families-and-comparability-budgets.md",
    "docs/10-method/transfer-ledgers-adopted-non-takes-and-repeat-argument-brakes.md",
    "docs/10-method/operational-heads-citation-heads-and-frozen-public-surfaces.md",
    "docs/10-method/gate-classes-future-trigger-kinds-and-bounded-reopen-rules.md",
}
missing_required = sorted(required_reentry_docs - set(pack.get("must_read", [])))
if missing_required:
    raise SystemExit(f"context-pack must_read missing compact control surfaces: {missing_required}")

registry_text = (ROOT / "docs/20-constitution/open-question-registry.md").read_text(encoding="utf-8")
trajectory_text = (ROOT / "docs/00-meta/trajectory-map.md").read_text(encoding="utf-8")
for item in pack.get("open_questions", []):
    if item["id"] not in registry_text:
        raise SystemExit(f"context-pack open_question id not found in registry: {item['id']}")
    if item["selection_source"] == "docs/00-meta/trajectory-map.md" and item["id"] not in trajectory_text:
        raise SystemExit(f"context-pack open_question hot id missing from trajectory map: {item['id']}")
    if item["text"].endswith(":"):
        raise SystemExit(f"context-pack open_question looks truncated: {item}")
    if "?" not in item["text"]:
        raise SystemExit(f"context-pack open_question missing question mark: {item}")

print("check_context_pack_fidelity: OK")
