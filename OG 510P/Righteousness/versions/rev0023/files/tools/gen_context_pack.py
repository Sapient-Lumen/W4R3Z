import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]

start = (ROOT / "START_HERE.md").read_text(encoding="utf-8")
must_read = []
for line in start.splitlines():
    m = re.match(r"\d+\. `([^`]+)`", line.strip())
    if m:
        must_read.append(m.group(1))

for rel in must_read:
    if not (ROOT / rel).exists():
        raise SystemExit(f"missing must-read path: {rel}")

claims = json.loads((ROOT / "CLAIM_REGISTRY.json").read_text(encoding="utf-8"))["claims"]
questions = json.loads((ROOT / "OPEN_QUESTIONS.json").read_text(encoding="utf-8"))["questions"]
status = json.loads((ROOT / "SURFACE_STATUS.json").read_text(encoding="utf-8"))
manifest = json.loads((ROOT / "RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
receipt = json.loads((ROOT / "REVISION_RECEIPT.json").read_text(encoding="utf-8"))
revision = receipt["revision"]

state_rank = {"working-canon": 0, "admitted": 1, "provisional": 2}
def claim_num(claim):
    m = re.search(r"(\d+)$", claim["id"])
    return int(m.group(1)) if m else 0
selected_claims = sorted(
    claims,
    key=lambda c: (state_rank.get(c["state"], 9), -claim_num(c))
)[:6]
question_rank = {"high": 0, "medium": 1, "low": 2}
selected_questions = sorted(
    questions,
    key=lambda q: (question_rank.get(q["priority"], 9), q["id"])
)[:4]

pack = {
    "project": "Righteousness",
    "revision": revision,
    "must_read": must_read,
    "top_claims": [
        {"id": c["id"], "title": c["title"], "state": c["state"]}
        for c in selected_claims
    ],
    "open_questions": [
        {"id": q["id"], "question": q["question"], "priority": q["priority"]}
        for q in selected_questions
    ],
    "current_posture": {
        "operational_head": status["operational_head"]["surface"],
        "citation_head": status["citation_head"]["surface"],
        "decision_state": status["status_lanes"]["decision_state"],
        "execution_state": status["status_lanes"]["execution_state"],
        "public_state": status["status_lanes"]["public_state"],
        "state_class": status["state_class"],
    },
    "commands": {
        "lint": "make lint",
        "package_release": "make package-release STAMP=... SLUG=...",
    },
    "bundle": manifest["bundle"],
    "warnings": [
        "Canon is starter-scale, not exhaustive.",
        "Cross-tradition comparisons are compression aids, not identity claims.",
        "Quarantine is not canon.",
    ],
}

(ROOT / "context-pack.json").write_text(json.dumps(pack, indent=2) + "\n", encoding="utf-8")
print("wrote context-pack.json")
