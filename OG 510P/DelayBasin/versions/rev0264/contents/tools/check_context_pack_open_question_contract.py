import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
pack = json.loads((ROOT / "context-pack.json").read_text(encoding="utf-8"))
registry_text = (ROOT / "docs/20-constitution/open-question-registry.md").read_text(encoding="utf-8")
trajectory_text = (ROOT / "docs/00-meta/trajectory-map.md").read_text(encoding="utf-8")

def parse_registry_questions(text: str) -> dict[str, str]:
    items = {}
    current = None
    for raw in text.splitlines():
        if raw.startswith("- `OQ-"):
            if current is not None:
                m = re.match(r"`(?P<id>OQ-\d{4})` — (?P<body>.*)", current)
                if m:
                    items[m.group("id")] = m.group("body").strip()
            current = raw[2:].strip()
        elif current is not None:
            stripped = raw.strip()
            if not stripped:
                m = re.match(r"`(?P<id>OQ-\d{4})` — (?P<body>.*)", current)
                if m:
                    items[m.group("id")] = m.group("body").strip()
                current = None
            elif raw.startswith("- `"):
                m = re.match(r"`(?P<id>OQ-\d{4})` — (?P<body>.*)", current)
                if m:
                    items[m.group("id")] = m.group("body").strip()
                current = None
            elif raw.startswith("  - ") or raw.startswith("    "):
                continue
            else:
                current += " " + stripped
    if current is not None:
        m = re.match(r"`(?P<id>OQ-\d{4})` — (?P<body>.*)", current)
        if m:
            items[m.group("id")] = m.group("body").strip()
    return items

def compress_text(body: str) -> str:
    body = body.strip()
    if len(body) <= 96:
        return body
    body = body.rstrip()
    if body.endswith('?'):
        body = body[:-1]
    words = body.split()
    return " ".join(words[:6]).rstrip(' ,;:.') + '?'

registry = parse_registry_questions(registry_text)
questions = pack.get("open_questions", [])
if not questions:
    raise SystemExit("context-pack open_questions cannot be empty")

for item in questions:
    expected = compress_text(registry.get(item["id"], ""))
    if not expected:
        raise SystemExit(f"open question missing from registry: {item['id']}")
    if item["source"] != "docs/20-constitution/open-question-registry.md":
        raise SystemExit(f"open question source must stay on registry: {item['id']}")
    if item["text"] != expected:
        raise SystemExit(f"open question text drifted from registry compression for {item['id']}")
    if item["selection_source"] == "docs/00-meta/trajectory-map.md" and item["id"] not in trajectory_text:
        raise SystemExit(f"trajectory-selected open question missing from trajectory map: {item['id']}")

print("check_context_pack_open_question_contract: OK")
