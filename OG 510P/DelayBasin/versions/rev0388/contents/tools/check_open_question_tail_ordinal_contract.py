import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
text = (ROOT / "docs/20-constitution/open-question-registry.md").read_text(encoding="utf-8")
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
expected_latest_oq = receipt.get("next_open_question")
if not expected_latest_oq:
    raise SystemExit("REVISION-RECEIPT.json missing next_open_question for open-question tail guard")
heads = []
for m in re.finditer(r"^(\d+)\. Determine .*?$", text, re.M):
    after = text[m.end():]
    oq = re.search(r"- `(OQ-\d{4})` —", after)
    if oq:
        heads.append((int(m.group(1)), oq.group(1)))
if len(heads) < 2:
    raise SystemExit("open-question tail ordinal guard could not find enough headed OQ entries")
prev, latest = heads[-2], heads[-1]
if latest[0] != prev[0] + 1:
    raise SystemExit(f"open-question tail heading jump: {prev[0]} -> {latest[0]}")
if int(latest[1].split('-')[1]) != int(prev[1].split('-')[1]) + 1:
    raise SystemExit(f"open-question tail OQ jump: {prev[1]} -> {latest[1]}")
if latest[1] != expected_latest_oq:
    raise SystemExit(f"latest headed OQ should match receipt next_open_question {expected_latest_oq}, got {latest}")
print("check_open_question_tail_ordinal_contract: OK")
