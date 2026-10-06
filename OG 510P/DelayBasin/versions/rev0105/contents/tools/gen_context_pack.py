import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
out = ROOT / "context-pack.json"


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




def compress_open_question(item: str) -> str:
    m = re.match(r"(`OQ-\d{4}`) — (.*)", item)
    if not m:
        return item
    ident, body = m.groups()
    body = body.strip()
    if len(body) <= 96:
        return item
    body = body.rstrip()
    if body.endswith('?'):
        body = body[:-1]
    words = body.split()
    short = " ".join(words[:7]).rstrip(' ,;:.') + '?'
    return f"{ident} — {short}"

def parse_lexicon(path: pathlib.Path):
    text = path.read_text(encoding="utf-8")
    certified = []
    provisional = []
    current = None
    for raw in text.splitlines():
        m = re.match(r"- `(?P<id>LX-\d{4})` — `(?P<term>[^`]+)`", raw.strip())
        if m:
            current = {"id": m.group("id"), "term": m.group("term"), "class": None}
            continue
        if current is not None and raw.strip().startswith("- Class:"):
            current["class"] = raw.split(":", 1)[1].strip()
            target = certified if current["class"] == "certified-core" else provisional
            target.append({"id": current["id"], "term": current["term"]})
            current = None
    return certified, provisional


def parse_moves(path: pathlib.Path):
    text = path.read_text(encoding="utf-8")
    certified = []
    current = None
    for raw in text.splitlines():
        m = re.match(r"- `(?P<id>MV-\d{4})` — `(?P<term>[^`]+)`", raw.strip())
        if m:
            current = {"id": m.group("id"), "class": None}
            continue
        if current is not None and raw.strip().startswith("- Class:"):
            current["class"] = raw.split(":", 1)[1].strip()
            if current["class"] == "certified-move":
                certified.append(current["id"])
            current = None
    return certified


def parse_decay_watch(path: pathlib.Path):
    text = path.read_text(encoding="utf-8")
    entries = []
    current = None
    for raw in text.splitlines():
        m = re.match(r"- `(?P<id>DW-\d{4})` — `(?P<label>[^`]+)`", raw.strip())
        if m:
            if current:
                entries.append(current)
            current = {"id": m.group("id"), "label": m.group("label"), "horizon": None}
            continue
        if current is not None and raw.strip().startswith("- Review horizon:"):
            current["horizon"] = raw.split(":", 1)[1].strip()
    if current:
        entries.append(current)
    return entries[-3:]


changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
rev = re.search(r"(rev\d{4})", changelog).group(1)

start_here = (ROOT / "START_HERE.md").read_text(encoding="utf-8")
must_read = []
for line in start_here.splitlines():
    m = re.match(r"\d+\. `([^`]+)`", line.strip())
    if m:
        must_read.append(m.group(1))
if not must_read:
    raise SystemExit("could not derive must_read from START_HERE.md")
for rel in must_read:
    if not (ROOT / rel).exists():
        raise SystemExit(f"must_read path missing: {rel}")

open_questions = parse_markdown_bullets((ROOT / "docs/20-constitution/open-question-registry.md").read_text(encoding="utf-8"), "OQ-")
trajectory_text = (ROOT / "docs/00-meta/trajectory-map.md").read_text(encoding="utf-8")
hot_ids = []
for item in re.findall(r"OQ-\d{4}", trajectory_text):
    if item not in hot_ids:
        hot_ids.append(item)
if hot_ids:
    filtered = [q for q in open_questions if any(q.startswith(f"`{oid}`") for oid in hot_ids)]
    open_questions = filtered[-2:]
else:
    open_questions = open_questions[-2:]
open_questions = [compress_open_question(q) for q in open_questions]

certified, provisional = parse_lexicon(ROOT / "docs/20-constitution/core-lexicon-registry.md")
certified_moves = parse_moves(ROOT / "docs/20-constitution/move-registry.md")
decay_watch = parse_decay_watch(ROOT / "docs/20-constitution/decay-watch-registry.md")

pack = {
    "project": "DelayBasin",
    "revision": rev,
    "must_read": must_read,
    "open_questions": open_questions,
    "core_lexicon": {
        "registry": "docs/20-constitution/core-lexicon-registry.md",
        "certified": certified,
        "provisional": provisional,
    },
    "move_registry": {
        "registry": "docs/20-constitution/move-registry.md",
        "certified": certified_moves,
    },
    "promotion_surface": "docs/20-constitution/promotion-contract-registry.md",
    "decay_surface": "docs/20-constitution/decay-watch-registry.md",
    "decay_watch": decay_watch,
    "recovery": {
        "surface": "docs/20-constitution/recovery-kernel.md",
        "move": "MV-0010"
    },
    "revision_receipt": {
        "surface": "REVISION-RECEIPT.json",
        "contract": "docs/20-constitution/revision-receipt-contract.md",
        "move": "MV-0011"
    },
    "typed_reentry": {
        "workflow_surface": "docs/50-promptcraft/prompt-pairs.md",
        "state_surfaces": [
            "START_HERE.md",
            "SURFACE-STATUS.json",
            "RELEASE-MANIFEST.json",
            "context-pack.json",
            "REVISION-RECEIPT.json",
            "RETROSPECTIVE-QUEUE.json",
            "FIREBREAK-LEDGER.json",
            "ASSUMPTION-LEDGER.json",
            "FOREIGN-PRESSURE-LEDGER.json",
            "RESOLUTION-LEDGER.json",
            "docs/20-constitution/claim-registry.md",
            "docs/20-constitution/open-question-registry.md",
            "docs/20-constitution/core-lexicon-registry.md",
            "docs/20-constitution/move-registry.md",
        ],
        "check_surface": "make lint",
        "admission_moves": certified_moves,
        "quarantine_surface": "docs/90-quarantine/wild-speculations-2026-03-08.md",
    },
    "commands": {
        "lint": "make lint",
        "package_release": "make package-release STAMP=... SLUG=...",
    },
}
out.write_text(json.dumps(pack, ensure_ascii=False, separators=(",",":")) + "\n", encoding="utf-8")
print(f"wrote {out}")
