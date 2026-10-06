import json
import pathlib
import re


def parse_markdown_bullets(text: str, prefix: str) -> list[str]:
    items = []
    current = None
    for raw in text.splitlines():
        if raw.startswith(f"- `{prefix}"):
            if current is not None:
                items.append(" ".join(current.split()))
            current = raw[2:].strip()
        elif current is not None:
            stripped = raw.strip()
            if not stripped:
                items.append(" ".join(current.split()))
                current = None
            elif raw.startswith("- `"):
                items.append(" ".join(current.split()))
                current = None
            elif raw.startswith("  - ") or raw.startswith("    "):
                continue
            else:
                current += " " + stripped
    if current is not None:
        items.append(" ".join(current.split()))
    return items


def compress_open_question_text(body: str) -> str:
    body = body.strip()
    if len(body) <= 96:
        return body
    body = body.rstrip()
    if body.endswith('?'):
        body = body[:-1]
    words = body.split()
    return " ".join(words[:6]).rstrip(' ,;:.') + '?'


def resolved_open_question_ids(path: pathlib.Path) -> set[str]:
    ledger = json.loads(path.read_text(encoding="utf-8"))
    ids = set()
    for item in ledger.get("items", []):
        if item.get("closure_state") == "resolved":
            for oid in item.get("resolved_objects", []):
                if re.fullmatch(r"OQ-\d{4}", oid):
                    ids.add(oid)
    return ids


def structured_open_question(item: str, selection_source: str) -> dict:
    m = re.match(r"`(?P<id>OQ-\d{4})` — (?P<body>.*)", item)
    if not m:
        return {
            "id": "OQ-UNKNOWN",
            "source": "docs/20-constitution/open-question-registry.md",
            "selection_source": selection_source,
            "text": compress_open_question_text(item),
        }
    return {
        "id": m.group("id"),
        "source": "docs/20-constitution/open-question-registry.md",
        "selection_source": selection_source,
        "text": compress_open_question_text(m.group("body")),
    }


def select_context_open_questions(root: pathlib.Path) -> list[dict]:
    open_questions = parse_markdown_bullets((root / "docs/20-constitution/open-question-registry.md").read_text(encoding="utf-8"), "OQ-")
    resolved_oqs = resolved_open_question_ids(root / "RESOLUTION-LEDGER.json")
    open_questions = [q for q in open_questions if not any(q.startswith(f"`{oid}`") for oid in resolved_oqs)]
    if not open_questions:
        raise SystemExit("no unresolved open questions remain for context-pack selection")
    trajectory_text = (root / "docs/00-meta/trajectory-map.md").read_text(encoding="utf-8")
    hot_ids = []
    for item in re.findall(r"OQ-\d{4}", trajectory_text):
        if item not in hot_ids:
            hot_ids.append(item)
    selection_source = "docs/20-constitution/open-question-registry.md"
    if hot_ids:
        filtered = [q for q in open_questions if any(q.startswith(f"`{oid}`") for oid in hot_ids)]
        if filtered:
            open_questions = filtered[-1:]
            selection_source = "docs/00-meta/trajectory-map.md"
        else:
            open_questions = open_questions[-1:]
    else:
        open_questions = open_questions[-1:]
    return [structured_open_question(q, selection_source) for q in open_questions]
