#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
from archive_meta import current_revision

CURRENT_REV = current_revision()

GATE_RULES = {
    "scoping-and-authority": {"administrative-law", "registration", "identity", "procurement", "oversight"},
    "prelaunch-and-approval": {"evaluation", "testing", "lifecycle", "interoperability", "oversight", "transparency"},
    "live-operation": {"operations", "monitoring", "incident", "accessibility", "data-governance"},
    "change-and-release": {"change-management", "third-party", "interoperability", "monitoring", "data-governance"},
    "redress-and-review": {"appeals", "contestability", "evidence", "records-management", "disclosure"},
    "retirement-and-continuity": {"incident", "lifecycle", "procurement", "records-management", "monitoring"},
}


def main() -> None:
    data = json.loads((ROOT / "ARCHIVE_INDEX.json").read_text(encoding="utf-8"))
    notes = data.get("notes", [])
    gates = {}
    for gate, tags in GATE_RULES.items():
        matched = []
        latest = None
        for note in notes:
            note_tags = set(note.get("tags", []))
            overlap = sorted(note_tags & tags)
            if overlap:
                entry = {
                    "number": note.get("number"),
                    "file": note.get("file"),
                    "title": note.get("title"),
                    "matched_tags": overlap,
                }
                matched.append(entry)
                if latest is None or int(note.get("number", -1)) > int(latest.get("number", -1)):
                    latest = entry
        gates[gate] = {"count": len(matched), "latest": latest, "notes": matched}

    payload = {
        "revision": CURRENT_REV,
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "gates": gates,
    }
    (ROOT / "LIFECYCLE_GATES.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("OK: wrote LIFECYCLE_GATES.json")


if __name__ == "__main__":
    main()
