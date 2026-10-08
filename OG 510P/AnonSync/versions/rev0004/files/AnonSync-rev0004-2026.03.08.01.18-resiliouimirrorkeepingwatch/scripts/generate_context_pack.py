#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main() -> int:
    state = json.loads((ROOT / "metadata" / "project-state.json").read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "metadata" / "archive-manifest.json").read_text(encoding="utf-8"))

    out = ROOT / "context-packs" / "anonsync-context-pack.md"
    lines: list[str] = []
    lines.append("# AnonSync Context Pack")
    lines.append("")
    lines.append("## Identity")
    lines.append(f"- project: {state['project_name']}")
    lines.append(f"- revision: {state['current_revision_label']}")
    lines.append(f"- archive: {manifest['archive_basename']}.zip")
    lines.append(f"- stage: {state['stage']}")
    lines.append("")
    lines.append("## Vision")
    lines.append(state["vision"])
    lines.append("")
    lines.append("## Invariants")
    for item in state["invariants"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Architecture choices")
    for key, value in state["architecture_choices"].items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("## Next priorities")
    for item in state["next_priorities"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Must reads")
    for item in state["top_level_must_reads"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Reminder")
    lines.append("Regenerate this file whenever project direction or canonical metadata changes.")

    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out.relative_to(ROOT)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
