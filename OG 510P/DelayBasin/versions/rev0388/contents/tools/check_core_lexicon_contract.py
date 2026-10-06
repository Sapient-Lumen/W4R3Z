import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
registry = ROOT / "docs/20-constitution/core-lexicon-registry.md"
text = registry.read_text(encoding="utf-8")
entries = []
current = None
for raw in text.splitlines():
    m = re.match(r"- `(?P<id>LX-\d{4})` — `(?P<term>[^`]+)`", raw.strip())
    if m:
        current = {"id": m.group("id"), "term": m.group("term"), "class": None, "meaning": False, "dereference": False}
        entries.append(current)
        continue
    if current is None:
        continue
    stripped = raw.strip()
    if stripped.startswith("- Class:"):
        current["class"] = stripped.split(":", 1)[1].strip()
    elif stripped.startswith("- Meaning:"):
        current["meaning"] = True
    elif stripped.startswith("- Dereference:"):
        current["dereference"] = True

if not entries:
    raise SystemExit("core lexicon registry has no entries")

classes = {e["class"] for e in entries}
if "certified-core" not in classes:
    raise SystemExit("core lexicon registry missing certified-core entry")
if "provisional-private-handle" not in classes:
    raise SystemExit("core lexicon registry missing provisional-private-handle entry")

terms = set()
for e in entries:
    if not e["class"]:
        raise SystemExit(f"missing class for {e['id']}")
    if not e["meaning"] or not e["dereference"]:
        raise SystemExit(f"missing meaning/dereference for {e['id']}")
    if e["term"] in terms:
        raise SystemExit(f"duplicate lexicon term: {e['term']}")
    terms.add(e["term"])

pack = json.loads((ROOT / "context-pack.json").read_text(encoding="utf-8"))
if "core_lexicon" not in pack:
    raise SystemExit("context-pack missing core_lexicon")
cl = pack["core_lexicon"]
if cl.get("registry") != "docs/20-constitution/core-lexicon-registry.md":
    raise SystemExit("context-pack core_lexicon registry path mismatch")
certified = {(e["id"], e["term"]) for e in cl.get("certified", [])}
provisional = {(e["id"], e["term"]) for e in cl.get("provisional", [])}
expected_certified = {(e["id"], e["term"]) for e in entries if e["class"] == "certified-core"}
expected_provisional = {(e["id"], e["term"]) for e in entries if e["class"] == "provisional-private-handle"}
if certified != expected_certified:
    raise SystemExit(f"context-pack certified core mismatch: expected {sorted(expected_certified)}, got {sorted(certified)}")
if provisional != expected_provisional:
    raise SystemExit(f"context-pack provisional core mismatch: expected {sorted(expected_provisional)}, got {sorted(provisional)}")

print("check_core_lexicon_contract: OK")
