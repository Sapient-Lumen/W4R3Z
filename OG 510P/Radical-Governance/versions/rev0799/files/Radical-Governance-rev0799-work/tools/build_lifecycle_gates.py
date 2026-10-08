#!/usr/bin/env python3
from __future__ import annotations

import json

from archive_meta import GENERATED, current_revision, generated_at_utc

CURRENT_REV = current_revision()

GATE_RULES = {
    "scoping-and-authority": {"administrative-law", "registration", "identity", "procurement", "oversight", "multilevel-governance"},
    "prelaunch-and-approval": {"evaluation", "testing", "lifecycle", "interoperability", "oversight", "transparency"},
    "live-operation": {"operations", "monitoring", "incident", "accessibility", "data-governance", "service-delivery-governance"},
    "change-and-release": {"change-management", "third-party", "interoperability", "monitoring", "data-governance"},
    "redress-and-review": {"appeals", "contestability", "evidence", "records-management", "disclosure", "public-records-governance"},
    "retirement-and-continuity": {"incident", "lifecycle", "procurement", "records-management", "monitoring"},
}


def main() -> None:
    data = json.loads((GENERATED / "ARCHIVE_INDEX.json").read_text(encoding="utf-8"))
    notes = data.get("notes", [])
    gates = {}
    for gate, tags in GATE_RULES.items():
        matched = []
        latest = None
        for note in notes:
            overlap = sorted(set(note.get("tags", [])) & tags)
            if overlap:
                entry = {"number": note.get("number"), "file": note.get("file"), "title": note.get("title"), "matched_tags": overlap}
                matched.append(entry)
                if latest is None or int(note.get("number", -1)) > int(latest.get("number", -1)):
                    latest = entry
        gates[gate] = {"count": len(matched), "latest": latest, "notes": matched}

    payload = {"revision": CURRENT_REV, "generated_at_utc": generated_at_utc(), "gates": gates}
    # This is a machine/debug surface; compact output keeps generated-route
    # mass from becoming a reader-facing control plane by accident.
    (GENERATED / "LIFECYCLE_GATES.json").write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print("OK: wrote generated/LIFECYCLE_GATES.json")


if __name__ == "__main__":
    main()
