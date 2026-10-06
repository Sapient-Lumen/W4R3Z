import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
context = json.loads((ROOT / "context-pack.json").read_text(encoding="utf-8"))
frontier = json.loads((ROOT / "frontier-ticket.json").read_text(encoding="utf-8"))
registry_text = (ROOT / "docs/20-constitution/open-question-registry.md").read_text(encoding="utf-8")

registry_titles = {}
for raw in registry_text.splitlines():
    m = re.match(r"- `(OQ-\d{4})` — (.+)", raw)
    if m:
        registry_titles[m.group(1)] = " ".join(m.group(2).split())

frontier_id = receipt.get("next_open_question")
if frontier_id not in registry_titles:
    raise SystemExit(f"current frontier {frontier_id} missing from open-question registry")
expected = registry_titles[frontier_id]
ctx_focus = context.get("open_questions", [{}])[-1]
ft_focus = frontier.get("primary_focus", {})
for label, focus in [("context-pack", ctx_focus), ("frontier-ticket", ft_focus)]:
    if focus.get("id") != frontier_id:
        raise SystemExit(f"{label} frontier id {focus.get('id')} != {frontier_id}")
    if focus.get("text") != expected:
        raise SystemExit(f"{label} frontier title is not exact registry title: {focus.get('text')!r} != {expected!r}")
    if len(focus.get("text", "").split()) < max(7, len(expected.split()) - 2):
        raise SystemExit(f"{label} frontier title looks lossily compressed: {focus.get('text')!r}")
print("check_open_question_title_integrity: OK")
