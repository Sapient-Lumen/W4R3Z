from __future__ import annotations

import json
from pathlib import Path

from micromax_editor.buffer import Cursor
from micromax_editor.editor import Editor
from micromax_editor.recovery_journal import RecoveryJournal
from micromax_editor.screen_consumer import validate_screen_contract_v1
from micromax_editor.startup import create_editor_runtime, open_initial_buffer


FIXTURE = (
    Path(__file__).parent
    / "fixtures"
    / "journeys"
    / "sustained-use-recovery-plugin-100x24.txt"
)


def _normalized(value: object, root: Path) -> str:
    return str(value).replace(str(root), "<TMP>")


def _visible_screen_step(ed: Editor, label: str, root: Path) -> str:
    contract = ed.screen_contract(24, 100)
    assert validate_screen_contract_v1(contract) == contract
    status = ed.status_model()
    statusline = ed.statusline_model(100, status=status)

    lines = [f"=== {label} ==="]
    lines.append(
        "state: "
        + json.dumps(
            {
                "active": _normalized(ed.active or "", root),
                "dirty": int(status["dirty"]),
                "last_message": _normalized(status["last_message"], root),
                "prompt": status["prompt_kind"],
                "recovery": status["recovery_summary"],
                "search": status["search_summary"],
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    for row in contract["rows"]:
        if row["text"]:
            text = row["text"]
            if row["kind"] == "infobar":
                # Record the complete message contract rather than a temporary
                # directory-dependent truncation of that message.
                text = status["last_message"]
            elif row["kind"] == "statusline":
                # The actual 100-column row is still validated above.  Persist
                # the logical segments so pytest's variable temp-root length
                # cannot make a journey fixture nondeterministic.
                text = (
                    f"{statusline['left_raw']} || {statusline['right_raw']}"
                )
            lines.append(
                f"{row['y']:02d} {row['kind']}: {_normalized(text, root)}"
            )
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


def _write_fragile_plugin(root: Path) -> None:
    plugin = root / "fragile"
    plugin.mkdir(parents=True)
    (plugin / "plugin.json").write_text(
        json.dumps(
            {
                "name": "fragile",
                "version": "1.0.0",
                "description": "sustained-use rollback probe",
                "entry": "init.mx",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (plugin / "init.mx").write_text(
        ': run drop "help" "ed.command-edit" hostcall 0 ;\n'
        '\' run "fragile" "open prompt then fail" "ed.cmd-add" hostcall drop\n',
        encoding="utf-8",
    )


def test_sustained_use_keeps_recovery_visible_and_plugin_failure_truthful(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("MICROMAX_INIT", str(tmp_path / "missing-init.mx"))

    project = tmp_path / "project"
    (project / ".git").mkdir(parents=True)
    (project / "src").mkdir()
    main = project / "src" / "main.mx"
    main.write_text(': greet "hello" ;\ngreet\n', encoding="utf-8")
    notes = project / "notes.txt"
    notes.write_text("alpha beta alpha\n", encoding="utf-8")
    draft = project / "draft.txt"
    draft.write_text("disk draft\n", encoding="utf-8")

    plugins = tmp_path / "plugins"
    plugins.mkdir()
    _write_fragile_plugin(plugins)

    journal = RecoveryJournal(tmp_path / "recovery")
    journal.checkpoint(draft, b"recovered draft\n", buffer_id="journey")

    runtime = create_editor_runtime(
        plugins_root=plugins,
        workspace_trust="trusted",
        recovery_root=journal.root,
    )
    ed = runtime.editor
    transcript = ""

    assert open_initial_buffer(ed, path=str(main)).ok is True
    assert ed.status_model()["recovery_summary"] == "recovery:1"
    assert "[recovery:1]" in ed.statusline_text(40)
    transcript += _visible_screen_step(ed, "startup-recovery-visible", tmp_path)

    assert ed.enter_file_prompt("notes") is True
    assert ed.prompt is not None
    assert ed.prompt.suggestion_rows[0][0] == "notes.txt"
    transcript += _visible_screen_step(ed, "project-file-movement", tmp_path)
    assert ed.submit_prompt() is True
    assert ed.cur().buf.path == str(notes)

    eb = ed.cur()
    eb.cursors[eb.primary] = Cursor(0, len(eb.buf.lines[0]))
    ed.input["text"] = "!"
    assert ed.run_action("InsertText") is True
    assert ed.find("alpha", literal=True, announce=True) is True
    assert ed.find_next() is True
    assert ed.exec_command_line("save") is True
    assert notes.read_text(encoding="utf-8") == "alpha beta alpha!\n"
    transcript += _visible_screen_step(ed, "edit-search-save", tmp_path)

    assert ed.exec_command_line("fragile") is False
    assert ed.prompt is None
    assert ed.messages[-1] == "command fragile: failed"
    assert ed.status_model()["recovery_summary"] == "recovery:1"
    assert "[recovery:1]" in ed.statusline_text(40)
    transcript += _visible_screen_step(ed, "plugin-failure-rolled-back", tmp_path)

    # Open the recovery target normally first.  This takes the riskier existing-
    # buffer path where recovery text, dirty state, codec metadata, and journal
    # authority must become one atomic history decision.
    assert ed.enter_file_prompt("draft") is True
    assert ed.submit_prompt() is True
    assert ed.cur().buf.path == str(draft)
    assert ed.cur().buf.get_text() == "disk draft\n"

    assert ed.exec_command_line("recover #1") is True
    assert ed.cur().buf.get_text() == "recovered draft\n"
    assert ed.cur().buf.dirty is True
    recovery_entry = ed.cur().interrupted_save_entry_id
    assert recovery_entry
    assert ed.status_model()["recovery_summary"] == "recovery:1"
    assert "[recovery:1]" in ed.statusline_text(40)
    transcript += _visible_screen_step(ed, "recovery-opened-dirty", tmp_path)

    # Undo must detach the disk generation from the recovery authority.  Saving
    # that clean generation must leave the crash record intact, and Redo must
    # reattach the exact still-live record before recovered text is visible.
    assert ed.undo_feedback() is True
    assert ed.cur().buf.get_text() == "disk draft\n"
    assert ed.cur().interrupted_save_entry_id is None
    assert ed.exec_command_line("save") is True
    assert draft.read_text(encoding="utf-8") == "disk draft\n"
    assert journal.entry_present(recovery_entry) is True
    assert ed.status_model()["recovery_summary"] == "recovery:1"
    transcript += _visible_screen_step(
        ed,
        "recovery-undone-save-keeps-record",
        tmp_path,
    )

    assert ed.redo_feedback() is True
    assert ed.cur().buf.get_text() == "recovered draft\n"
    assert ed.cur().buf.dirty is True
    assert ed.cur().interrupted_save_entry_id == recovery_entry
    assert journal.entry_present(recovery_entry) is True
    transcript += _visible_screen_step(ed, "recovery-redone-protected", tmp_path)

    assert ed.exec_command_line("save") is True
    assert draft.read_text(encoding="utf-8") == "recovered draft\n"
    assert RecoveryJournal(journal.root).presence().count == 0
    assert ed.status_model()["recovery_summary"] == ""
    assert "[recovery:" not in ed.statusline_text(100)
    transcript += _visible_screen_step(ed, "recovery-resolved", tmp_path)

    assert transcript == FIXTURE.read_text(encoding="utf-8")
