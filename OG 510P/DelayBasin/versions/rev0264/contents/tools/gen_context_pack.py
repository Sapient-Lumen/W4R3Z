import json
import pathlib
import re

from open_question_selection_lib import select_context_open_questions

ROOT = pathlib.Path(__file__).resolve().parents[1]
out = ROOT / "context-pack.json"




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

open_questions = select_context_open_questions(ROOT)

certified, provisional = parse_lexicon(ROOT / "docs/20-constitution/core-lexicon-registry.md")
certified_moves = parse_moves(ROOT / "docs/20-constitution/move-registry.md")
decay_watch = parse_decay_watch(ROOT / "docs/20-constitution/decay-watch-registry.md")
status = json.loads((ROOT / "SURFACE-STATUS.json").read_text(encoding="utf-8"))
manifest = json.loads((ROOT / "RELEASE-MANIFEST.json").read_text(encoding="utf-8"))
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))

pack = {
    "project": "DelayBasin",
    "revision": rev,
    "must_read": must_read,
    "open_questions": open_questions,
    "frontier_ticket": {
        "surface": "frontier-ticket.json",
        "selected_focus_id": open_questions[-1]["id"],
    },
    "innovation_packet": {
        "surface": "innovation-packet.json",
        "anchor_revision": receipt["previous_revision"],
    },
    "validation": {
        "surface": "VALIDATION-INDEX.json",
        "guide": "docs/00-meta/validation-index.md",
    },
    "replay_capsule": {
        "surface": "replay-capsule.json"
    },
    "current_posture": {
        "operational_head": status["operational_head"]["surface"],
        "citation_head": status["citation_head"]["surface"],
        "decision_state": status["status_lanes"]["decision_state"],
        "execution_state": status["status_lanes"]["execution_state"],
        "public_state": status["status_lanes"]["public_state"],
        "state_class": status["state_class"],
    },
    "operator_warnings": [
        {"id": "OW-0001", "source": "docs/10-method/derivative-operator-contracts-low-entropy-reentry-wrappers-and-non-canon-read-first-surfaces.md", "text": "Derivative aids; canon wins"},
        {"id": "OW-0002", "source": "SURFACE-STATUS.json", "text": "Working tree is not citation head."},
        {"id": "OW-0003", "source": "DATACUBE-TRANSFER-LEDGER.json", "text": "Check transfer ledger before peer import."},
        {"id": "OW-0004", "source": "WITNESS-VOCABULARY.json", "text": "Use exact governed tokens."}
    ],
    "reentry_contract": {
        "surface": "REENTRY-CONTRACT.json",
        "conformance": "REENTRY-SURFACE-CONFORMANCE.json",
        "profile_id": "careful-revision-pass",
    },
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
    "compact_surface_bundle": {
        "surface": "compact-surface-bundle.json"
    },
    "typed_reentry": {
        "workflow_surface": "docs/50-promptcraft/prompt-pairs.md",
        "state_surfaces": [
            "START_HERE.md",
            "SURFACE-STATUS.json",
            "RELEASE-MANIFEST.json",
            "context-pack.json",
            "frontier-ticket.json",
            "innovation-packet.json",
            "VALIDATION-INDEX.json",
            "replay-capsule.json",
            "compact-surface-bundle.json",
            "docs/00-meta/validation-index.md",
            "REENTRY-CONTRACT.json",
            "REENTRY-SURFACE-CONFORMANCE.json",
            "REVISION-RECEIPT.json",
            "RETROSPECTIVE-QUEUE.json",
            "FIREBREAK-LEDGER.json",
            "ASSUMPTION-LEDGER.json",
            "OBLIGATION-LEDGER.json",
            "APPLICABILITY-LEDGER.json",
            "WITNESS-VOCABULARY.json",
            "FOREIGN-PRESSURE-LEDGER.json",
            "DATACUBE-TRANSFER-LEDGER.json",
            "RESOLUTION-LEDGER.json",
            "docs/20-constitution/open-question-registry.md",
        ],
        "check_surface": "make lint",
        "admission_moves": certified_moves,
        "quarantine_surface": "docs/90-quarantine/wild-speculations-2026-03-08.md",
    },
    "commands": {
        "lint": "make lint",
        "innovation_packet": "python3 tools/gen_innovation_packet.py",
        "replay_capsule": "python3 tools/gen_replay_capsule.py",
        "validation_index": "python3 tools/gen_validation_index.py",
        "compact_surface_bundle": "python3 tools/gen_compact_surface_bundle.py",
        "package_release": "make package-release STAMP=... SLUG=...",
    },
}
out.write_text(json.dumps(pack, ensure_ascii=False, separators=(",",":")) + "\n", encoding="utf-8")
print(f"wrote {out}")
