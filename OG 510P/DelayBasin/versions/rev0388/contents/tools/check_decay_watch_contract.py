import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
reg = ROOT / "docs/20-constitution/decay-watch-registry.md"
pack = ROOT / "context-pack.json"

text = reg.read_text(encoding="utf-8")
entries = re.findall(r"- `DW-\d{4}` — `[^`]+`", text)
if not entries:
    print("decay-watch registry has no DW entries")
    sys.exit(1)

data = json.loads(pack.read_text(encoding="utf-8"))
if data.get("decay_surface") != "docs/20-constitution/decay-watch-registry.md":
    print("context-pack missing decay_surface")
    sys.exit(1)
watch = data.get("decay_watch", [])
if not watch:
    print("context-pack missing decay_watch summary")
    sys.exit(1)
print("check_decay_watch_contract: OK")
