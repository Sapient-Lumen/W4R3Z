import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
registry = ROOT / "docs/20-constitution/move-registry.md"
text = registry.read_text(encoding="utf-8")
entries = []
current = None
for raw in text.splitlines():
    m = re.match(r"- `(?P<id>MV-\d{4})` — `(?P<term>[^`]+)`", raw.strip())
    if m:
        current = {"id": m.group("id"), "class": None, "meaning": False, "admission": False, "dereference": False}
        entries.append(current)
        continue
    if current is None:
        continue
    stripped = raw.strip()
    if stripped.startswith("- Class:"):
        current["class"] = stripped.split(":", 1)[1].strip()
    elif stripped.startswith("- Meaning:"):
        current["meaning"] = True
    elif stripped.startswith("- Admission notes:"):
        current["admission"] = True
    elif stripped.startswith("- Dereference:"):
        current["dereference"] = True

if not entries:
    raise SystemExit("move registry has no entries")
for e in entries:
    if e["class"] != "certified-move":
        raise SystemExit(f"unexpected move class for {e['id']}: {e['class']}")
    if not e["meaning"] or not e["admission"] or not e["dereference"]:
        raise SystemExit(f"missing meaning/admission/dereference for {e['id']}")

pack = json.loads((ROOT / "context-pack.json").read_text(encoding="utf-8"))
mr = pack.get("move_registry")
if not mr:
    raise SystemExit("context-pack missing move_registry")
if mr.get("registry") != "docs/20-constitution/move-registry.md":
    raise SystemExit("context-pack move_registry registry path mismatch")
expected = [e["id"] for e in entries]
got = mr.get("certified", [])
if expected != got:
    raise SystemExit(f"context-pack move registry mismatch: expected {expected}, got {got}")
tr = pack.get("typed_reentry", {})
move_ids = tr.get("admission_moves")
if move_ids != expected:
    raise SystemExit(f"typed_reentry admission_moves mismatch: expected {expected}, got {move_ids}")

print("check_move_registry_contract: OK")
