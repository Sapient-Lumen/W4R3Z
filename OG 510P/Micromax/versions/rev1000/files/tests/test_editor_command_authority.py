from __future__ import annotations

import pytest

from micromax import MicromaxError
from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _editor() -> Editor:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*commands*", "")
    return ed


def _hostcall(ed: Editor, name: str, *args: object) -> list[object]:
    ed.vm.stack[:] = list(args)
    ed.vm.stack.append(str(name))
    ed.vm.eval("hostcall", filename="<command-authority-test>")
    return list(ed.vm.stack)


def _noop(_ed: Editor, _args: list[str]) -> bool:
    return True


def test_script_command_inventory_hides_trusted_commands_but_keeps_same_origin_commands() -> None:
    ed = _editor()
    ed.register_command_checked("trusted-secret", _noop, doc="trusted docs", group="trusted")

    with ed.script_context(origin_id="script-a"):
        ed.register_command_checked("own-public", _noop, doc="own docs", group="script-a")
        assert "own-public" in ed.command_names()
        assert "trusted-secret" not in ed.command_names()
        rows = {str(row[0]): row for row in ed.command_rows()}
        assert rows["own-public"][1] == "own docs"
        assert "trusted-secret" not in rows
        assert ed.command_detail_row("own-public") is not None
        assert ed.command_detail_row("trusted-secret") is None

    with ed.script_context(origin_id="script-b"):
        assert "trusted-secret" not in ed.command_names()
        assert "own-public" not in ed.command_names()


def test_command_read_capability_reveals_protected_command_metadata() -> None:
    ed = _editor()
    ed.register_command_checked("trusted-secret", _noop, doc="trusted docs", group="trusted")
    assert ed.exec_command_line("set cap.command-read true") is True

    with ed.script_context(origin_id="script-a"):
        row = ed.command_detail_row("trusted-secret")
        names = set(ed.command_names())

    assert row == ["trusted-secret", "trusted docs", "trusted", 0]
    assert "trusted-secret" in names


def test_command_inventory_hostcalls_use_read_authority_filters() -> None:
    ed = _editor()
    ed.register_command_checked("trusted-secret", _noop, doc="trusted docs", group="trusted")

    with ed.script_context(origin_id="script-a"):
        ed.register_command_checked("own-public", _noop, doc="own docs", group="script-a")
        names = set(_hostcall(ed, "ed.cmds")[-1])
        assert "help" in names
        assert "own-public" in names
        assert "trusted-secret" not in names
        row_map = {str(row[0]): row for row in _hostcall(ed, "ed.cmd-rows")[-1]}
        assert row_map["own-public"] == ["own-public", "own docs", "script-a", 0]
        assert "help" in row_map
        assert "trusted-secret" not in row_map
        palette = _hostcall(ed, "ed.command-palette-rows", "own")[-1]
        assert any(row[:3] == ["own-public", "command", "own docs"] for row in palette)
        leaked = _hostcall(ed, "ed.command-palette-rows", "trusted")[-1]
        assert not any(row and row[0] == "trusted-secret" for row in leaked)

    assert ed.exec_command_line("set cap.command-read true") is True
    with ed.script_context(origin_id="script-b"):
        assert {str(row[0]) for row in _hostcall(ed, "ed.cmd-rows")[-1]} >= {"trusted-secret", "own-public"}


def test_command_detail_hostcall_denial_preserves_name_operand() -> None:
    ed = _editor()
    ed.register_command_checked("trusted-secret", _noop, doc="trusted docs")

    with ed.script_context(origin_id="script-a"):
        ed.vm.stack[:] = ["trusted-secret"]
        with pytest.raises(MicromaxError, match="cannot read command: trusted-secret"):
            ed.vm.stack.append("ed.command-detail-row")
            ed.vm.eval("hostcall", filename="<command-authority-test>")

    assert ed.vm.stack == ["trusted-secret"]


def test_command_read_capability_is_advertised() -> None:
    ed = _editor()
    _hostcall(ed, "host.capabilities")
    rows = {str(row[0]): row for row in ed.vm.stack[-1]}
    assert rows["ed.command-read"][1] == "cap.command-read"
    assert rows["ed.command-read"][3] == 0

    assert ed.exec_command_line("set cap.command-read true") is True
    _hostcall(ed, "host.capabilities")
    rows = {str(row[0]): row for row in ed.vm.stack[-1]}
    assert rows["ed.command-read"][3] == 1
