import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
reg = ROOT / "docs/20-constitution/promotion-contract-registry.md"
pack = ROOT / "context-pack.json"

text = reg.read_text(encoding="utf-8")
contracts = re.findall(r"- `PC-\d{4}` — `[^`]+`", text)
if not contracts:
    print("promotion-contract registry has no PC entries")
    sys.exit(1)

data = json.loads(pack.read_text(encoding="utf-8"))
if data.get("promotion_surface") != "docs/20-constitution/promotion-contract-registry.md":
    print("context-pack missing promotion_surface")
    sys.exit(1)

print("check_promotion_contract: OK")
