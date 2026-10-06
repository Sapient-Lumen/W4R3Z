import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
pack = json.loads((ROOT / "context-pack.json").read_text(encoding="utf-8"))

for rel in pack.get("must_read", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"context-pack must_read path missing: {rel}")

for item in pack.get("open_questions", []):
    if not item.startswith("`OQ-"):
        raise SystemExit(f"context-pack open_question missing OQ id: {item}")
    if item.endswith(":"):
        raise SystemExit(f"context-pack open_question looks truncated: {item}")
    if "?" not in item:
        raise SystemExit(f"context-pack open_question missing question mark: {item}")

print("check_context_pack_fidelity: OK")
