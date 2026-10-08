from __future__ import annotations

import json
from pathlib import Path

from micromax_editor.editor import Editor
from micromax_editor.screen_consumer import validate_screen_contract_v1


FIXTURE = Path(__file__).parent / "fixtures" / "journeys" / "qreplace-generation-80x24.txt"


def _visible_screen_step(ed: Editor, label: str) -> str:
    contract = ed.screen_contract(24, 80)
    assert validate_screen_contract_v1(contract) == contract

    lines = [f"=== {label} ==="]
    for row in contract["rows"]:
        if row["text"]:
            lines.append(f"{row['y']:02d} {row['kind']}: {row['text']}")
    cues = ", ".join(
        f"{cue['kind']}@{cue['y']}:{cue['x']}-{cue['end']}"
        for cue in contract["cues"]
    )
    lines.append(f"cues: {cues or '-'}")
    lines.append(
        "cursor: "
        + json.dumps(contract["cursor"], sort_keys=True, separators=(",", ":"))
    )
    return "\n".join(lines) + "\n"


def test_qreplace_generation_guard_has_complete_80x24_headless_journey() -> None:
    ed = Editor()
    ed.new_buffer("journey.txt", "one two one\n")
    transcript = ""

    assert ed.exec_command_line("qreplace one X -l") is True
    transcript += _visible_screen_step(ed, "query-first")

    assert ed.qreplace_yes() is True
    transcript += _visible_screen_step(ed, "accepted-first")

    # This used to consume qreplace's selected range and leave stale match
    # coordinates live. It now closes qreplace, clears the mark, and starts a
    # separate edit transaction at the visible cursor.
    ed.input["text"] = "!"
    assert ed.run_action("InsertText") is True
    transcript += _visible_screen_step(ed, "external-edit")

    assert ed.run_action("Undo") is True
    transcript += _visible_screen_step(ed, "undo-external")

    assert ed.run_action("Undo") is True
    transcript += _visible_screen_step(ed, "undo-qreplace")

    assert transcript == FIXTURE.read_text(encoding="utf-8")
