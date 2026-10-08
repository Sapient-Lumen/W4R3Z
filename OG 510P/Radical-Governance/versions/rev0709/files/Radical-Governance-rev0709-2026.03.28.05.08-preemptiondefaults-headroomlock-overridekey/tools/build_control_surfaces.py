#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
from archive_meta import current_revision

CURRENT_REV = current_revision()

SURFACE_RULES = {
    "boundary-setting": {"registration", "oversight", "operations", "data-governance", "administrative-law"},
    "predeployment-evidence": {"testing", "evaluation", "lifecycle", "interoperability", "procurement", "administrative-law"},
    "live-operations": {"monitoring", "incident", "change-management", "operations", "records-management"},
    "user-interaction": {"transparency", "accessibility", "appeals", "contestability", "participation"},
    "evidence-and-redress": {"evidence", "appeals", "contestability", "monitoring", "records-management"},
    "supplier-and-ecosystem": {"third-party", "identity", "interoperability", "registration", "procurement"},
}


def main() -> None:
    data = json.loads((ROOT / "ARCHIVE_INDEX.json").read_text(encoding="utf-8"))
    notes = data.get("notes", [])
    surfaces = {}
    for surface, tags in SURFACE_RULES.items():
        matched = []
        latest = None
        for note in notes:
            note_tags = set(note.get("tags", []))
            if note_tags & tags:
                entry = {
                    "number": note.get("number"),
                    "file": note.get("file"),
                    "title": note.get("title"),
                    "matched_tags": sorted(note_tags & tags),
                }
                matched.append(entry)
                if latest is None or int(note.get("number", -1)) > int(latest.get("number", -1)):
                    latest = entry
        surfaces[surface] = {
            "count": len(matched),
            "latest": latest,
            "notes": matched,
        }

    payload = {
        "revision": CURRENT_REV,
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "surfaces": surfaces,
    }
    (ROOT / "CONTROL_SURFACES.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("OK: wrote CONTROL_SURFACES.json")


if __name__ == "__main__":
    main()
