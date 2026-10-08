#!/usr/bin/env python3
from __future__ import annotations

import json

from archive_meta import GENERATED, current_notes_from_index, current_revision, generated_at_utc

CURRENT_REV = current_revision()


def main() -> None:
    status = json.loads((GENERATED / "NOTE_STATUS.json").read_text(encoding="utf-8"))
    matrix = json.loads((GENERATED / "CASE_PACKET_MATRIX.json").read_text(encoding="utf-8"))
    audit = json.loads((GENERATED / "CROSS_BOUNDARY_CONSOLIDATION_AUDIT.json").read_text(encoding="utf-8"))
    index = json.loads((GENERATED / "ARCHIVE_INDEX.json").read_text(encoding="utf-8"))

    notes = status.get("notes", {})
    first_citations = [
        {"file": file, "number": meta.get("number"), "canon_role": meta.get("canon_role"), "note_class": meta.get("note_class")}
        for file, meta in sorted(notes.items(), key=lambda item: int(item[1].get("number") or 0))
        if meta.get("first_citation")
    ]
    active_via_dispatcher = [
        {"file": file, "number": meta.get("number"), "dispatcher": meta.get("dispatcher"), "canon_role": meta.get("canon_role")}
        for file, meta in sorted(notes.items(), key=lambda item: int(item[1].get("number") or 0))
        if meta.get("status") == "active_via_dispatcher"
    ]

    applied_cases = [
        {
            "case_id": case.get("case_id"),
            "file": case.get("file"),
            "form_verdict": case.get("form_verdict"),
            "thickness": case.get("thickness"),
            "live_chain_notes": case.get("live_chain_notes", []),
            "reserved_notes": case.get("reserved_notes", []),
        }
        for case in matrix.get("cases", [])
    ]

    by_number = {int(note.get("number")): note for note in index.get("notes", []) if note.get("number") is not None}
    dispatcher = by_number.get(848, {})
    data = {
        "revision": CURRENT_REV,
        "generated_at_utc": generated_at_utc(),
        "generated_from": ["generated/NOTE_STATUS.json", "generated/CASE_PACKET_MATRIX.json", "generated/CROSS_BOUNDARY_CONSOLIDATION_AUDIT.json", "generated/ARCHIVE_INDEX.json"],
        "current_revision_notes": current_notes_from_index(),
        "front_door": status.get("front_door", {}),
        "canonical_reading_order": [
            status.get("front_door", {}).get("pocket_answer"),
            status.get("front_door", {}).get("long_answer"),
            status.get("front_door", {}).get("operating_canon"),
            status.get("front_door", {}).get("cross_boundary_dispatcher"),
            status.get("front_door", {}).get("applied_thick_case"),
            status.get("front_door", {}).get("applied_thin_case"),
            status.get("front_door", {}).get("applied_middle_case"),
            status.get("front_door", {}).get("applied_asset_case"),
            status.get("front_door", {}).get("applied_contract_case"),
            status.get("front_door", {}).get("applied_regulatory_case"),
            status.get("front_door", {}).get("applied_treaty_global_case"),
            "generated/CASE_PACKET_MATRIX.json",
            status.get("front_door", {}).get("cross_boundary_consolidation_audit"),
        ],
        "first_citations": first_citations,
        "active_via_dispatcher": active_via_dispatcher,
        "dispatcher_graph": {
            "dispatcher_number": 848,
            "dispatcher_file": dispatcher.get("file"),
            "depends_on": dispatcher.get("depends_on", []),
            "applied_cases": applied_cases,
            "merge_guidance": matrix.get("merge_guidance", {}),
            "consolidation_audit": {
                "file": "generated/CROSS_BOUNDARY_CONSOLIDATION_AUDIT.json",
                "audit_holding": audit.get("audit_holding"),
                "consolidation_map": audit.get("consolidation_map", []),
            },
        },
        "status_counts": status.get("status_counts", {}),
        "class_counts": status.get("class_counts", {}),
    }
    (GENERATED / "CANON_MAP.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("OK: wrote generated/CANON_MAP.json")


if __name__ == "__main__":
    main()
