#!/usr/bin/env python3
from __future__ import annotations

import json

from archive_meta import GENERATED, current_revision, generated_at_utc

CURRENT_REV = current_revision()

SURFACE_RULES = {
    "boundary-setting": {"registration", "oversight", "operations", "data-governance", "administrative-law", "multilevel-governance"},
    "predeployment-evidence": {"testing", "evaluation", "lifecycle", "interoperability", "procurement", "administrative-law"},
    "live-operations": {"monitoring", "incident", "change-management", "operations", "records-management", "service-delivery-governance"},
    "user-interaction": {"transparency", "accessibility", "appeals", "contestability", "participation", "service-delivery-governance"},
    "evidence-and-redress": {"evidence", "appeals", "contestability", "monitoring", "records-management", "public-records-governance"},
    "supplier-and-ecosystem": {"third-party", "identity", "interoperability", "registration", "procurement", "agency-governance"},
}


def main() -> None:
    data = json.loads((GENERATED / "ARCHIVE_INDEX.json").read_text(encoding="utf-8"))
    notes = data.get("notes", [])
    surfaces = {}
    for surface, tags in SURFACE_RULES.items():
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
        surfaces[surface] = {"count": len(matched), "latest": latest, "notes": matched}

    payload = {
        "revision": CURRENT_REV,
        "generated_at_utc": generated_at_utc(),
        "surfaces": surfaces,
    }
    # This is a machine/debug surface; compact output keeps generated-route
    # mass from becoming a reader-facing control plane by accident.
    (GENERATED / "CONTROL_SURFACES.json").write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print("OK: wrote generated/CONTROL_SURFACES.json")


if __name__ == "__main__":
    main()
