import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))

PATTERN = re.compile(r"([A-Z-]+\.json)#([A-Z]{2}-\d{4})")

def walk(x):
    if isinstance(x, dict):
        for v in x.values():
            yield from walk(v)
    elif isinstance(x, list):
        for v in x:
            yield from walk(v)
    elif isinstance(x, str):
        yield x

cache = {}
for s in walk(receipt):
    m = PATTERN.search(s)
    if not m:
        continue
    file_name, item_id = m.groups()
    path = ROOT / file_name
    if not path.exists():
        raise SystemExit(f"receipt pointer targets missing file: {file_name}")
    if file_name not in cache:
        data = json.loads(path.read_text(encoding="utf-8"))
        cache[file_name] = {item.get("id") for item in data.get("items", [])}
    if item_id not in cache[file_name]:
        raise SystemExit(f"receipt pointer targets missing id: {file_name}#{item_id}")

print("check_revision_receipt_pointer_integrity: OK")
