#!/usr/bin/env python3
"""scripts/check_drill_scenarios.py

Drift firewall for the drill scenario registry.

Validates:
- registry CSV exists and has required headers
- scenario_id uniqueness and basic format
- trigger_id references a known publication trigger
- public_notice_type matches the PublicNotice schema enum
- required_envelope_kinds exist in the envelope-kinds registry
- referenced checklist/playbook paths exist

This keeps tabletop/live drill planning aligned with the evidence + publication surfaces.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from _shared.registry import read_csv, require_headers, split_semicolon

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "artifacts" / "registries" / "drill-scenarios.csv"
ENVELOPE_KINDS = ROOT / "artifacts" / "registries" / "envelope-kinds.csv"
PUB_TRIGGERS = ROOT / "artifacts" / "registries" / "publication-triggers.csv"
PUBLIC_NOTICE_SCHEMA = ROOT / "schemas" / "PublicNotice.json"

RE_ID = re.compile(r"^[a-z0-9_]+$")


def main() -> int:
    if not REGISTRY.exists():
        print(f"ERROR: missing registry: {REGISTRY}", file=sys.stderr)
        return 2

    # Load known envelope kinds
    kinds_tbl = read_csv(ENVELOPE_KINDS)
    known_kinds = {r.get("kind", "").strip() for r in kinds_tbl.rows if r.get("kind")}

    # Load known publication triggers
    trig_tbl = read_csv(PUB_TRIGGERS)
    known_triggers = {r.get("trigger_id", "").strip() for r in trig_tbl.rows if r.get("trigger_id")}

    # Load PublicNotice.notice_type enum
    try:
        schema = json.loads(PUBLIC_NOTICE_SCHEMA.read_text(encoding="utf-8"))
        notice_enum = schema.get("properties", {}).get("notice_type", {}).get("enum", [])
        if not isinstance(notice_enum, list) or not notice_enum:
            raise ValueError("notice_type enum missing")
        notice_types = {str(x) for x in notice_enum}
    except Exception as e:
        print(f"ERROR: failed to load PublicNotice schema notice_type enum: {e}", file=sys.stderr)
        return 2

    tbl = read_csv(REGISTRY)
    required_headers = {
        "scenario_id",
        "title",
        "trigger_id",
        "public_notice_type",
        "required_envelope_kinds",
        "checklists",
        "playbooks",
        "notes",
    }

    missing = require_headers(tbl, required_headers)
    if missing:
        print(f"ERROR: {REGISTRY} missing headers: {missing}", file=sys.stderr)
        return 2

    seen_ids: set[str] = set()
    any_fail = False

    for i, r in enumerate(tbl.rows, start=2):  # header is line 1
        sid = r.get("scenario_id", "")
        if not sid or not RE_ID.match(sid):
            any_fail = True
            print(f"ERROR:{REGISTRY}:{i}: invalid scenario_id '{sid}'", file=sys.stderr)
        if sid in seen_ids:
            any_fail = True
            print(f"ERROR:{REGISTRY}:{i}: duplicate scenario_id '{sid}'", file=sys.stderr)
        seen_ids.add(sid)

        trig = r.get("trigger_id", "")
        if trig and trig not in known_triggers:
            any_fail = True
            print(
                f"ERROR:{REGISTRY}:{i}: unknown trigger_id '{trig}' (not in publication-triggers.csv)",
                file=sys.stderr,
            )

        nt = r.get("public_notice_type", "")
        if nt and nt not in notice_types:
            any_fail = True
            print(
                f"ERROR:{REGISTRY}:{i}: unknown public_notice_type '{nt}' (not in PublicNotice.notice_type enum)",
                file=sys.stderr,
            )

        for k in split_semicolon(r.get("required_envelope_kinds", "")):
            if k not in known_kinds:
                any_fail = True
                print(
                    f"ERROR:{REGISTRY}:{i}: required_envelope_kind '{k}' not in envelope-kinds.csv",
                    file=sys.stderr,
                )

        for p in split_semicolon(r.get("checklists", "")):
            path = ROOT / p
            if not path.exists():
                any_fail = True
                print(f"ERROR:{REGISTRY}:{i}: missing checklist path '{p}'", file=sys.stderr)

        for p in split_semicolon(r.get("playbooks", "")):
            path = ROOT / p
            if not path.exists():
                any_fail = True
                print(f"ERROR:{REGISTRY}:{i}: missing playbook path '{p}'", file=sys.stderr)

    if any_fail:
        return 2

    print("OK drill-scenarios registry")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
