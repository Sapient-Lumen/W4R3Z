from __future__ import annotations

import pytest

from micromax import MicromaxError
from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _editor() -> Editor:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*words*", "")
    return ed


def _hostcall(ed: Editor, name: str, *args: object) -> list[object]:
    ed.vm.stack[:] = list(args)
    ed.vm.stack.append(str(name))
    ed.vm.eval("hostcall", filename="<word-authority-test>")
    return list(ed.vm.stack)


def test_script_word_inventory_hides_trusted_dynamic_words_but_keeps_own_and_core_words() -> None:
    ed = _editor()
    ed.vm.eval(': trusted-secret ( -- n ) "trusted docs" 123 ;', filename="/secret/trusted.mx")

    with ed.script_context(origin_id="script-a"):
        ed.vm.eval(': own-word ( -- n ) "own docs" 42 ;', filename="/tmp/script-a.mx")
        names = set(ed.visible_vm_word_names())
        assert "+" in names
        assert "own-word" in names
        assert "trusted-secret" not in names
        own = ed.word_detail_row("own-word")
        assert own is not None
        assert own[0] == "own-word"
        assert ed.word_detail_row("trusted-secret") is None

    with ed.script_context(origin_id="script-b"):
        names = set(ed.visible_vm_word_names())
        assert "+" in names
        assert "own-word" not in names
        assert "trusted-secret" not in names


def test_word_read_capability_reveals_protected_dynamic_word_metadata() -> None:
    ed = _editor()
    ed.vm.eval(': trusted-secret ( -- n ) "trusted docs" 123 ;', filename="/secret/trusted.mx")
    assert ed.exec_command_line("set cap.word-read true") is True

    with ed.script_context(origin_id="script-a"):
        row = ed.word_detail_row("trusted-secret")
        names = set(ed.visible_vm_word_names())

    assert row is not None
    assert row[0] == "trusted-secret"
    assert row[2] == "( -- n )"
    assert row[5] == ["/secret/trusted.mx", 1, 1]
    assert "trusted-secret" in names


def test_word_detail_hostcall_denial_preserves_name_operand() -> None:
    ed = _editor()
    ed.vm.eval(': trusted-secret ( -- n ) "trusted docs" 123 ;', filename="/secret/trusted.mx")

    with ed.script_context(origin_id="script-a"):
        ed.vm.stack[:] = ["trusted-secret"]
        with pytest.raises(MicromaxError, match="cannot read word: trusted-secret"):
            ed.vm.stack.append("ed.word-detail-row")
            ed.vm.eval("hostcall", filename="<word-authority-test>")

    assert ed.vm.stack == ["trusted-secret"]


def test_help_and_prompt_word_rows_filter_protected_dynamic_words() -> None:
    ed = _editor()
    ed.vm.eval(': trusted-secret ( -- n ) "trusted docs" 123 ;', filename="/secret/trusted.mx")

    with ed.script_context(origin_id="script-a"):
        ed.vm.eval(': own-word ( -- n ) "own docs" 42 ;', filename="/tmp/script-a.mx")
        topics = {str(row[0]): row for row in ed.help_topic_rows()}
        assert "own-word" in topics
        assert "trusted-secret" not in topics
        assert any(str(row[0]).strip() == "own-word" for row in ed.apropos_rows("own-word"))
        assert not any(str(row[0]).strip() == "trusted-secret" for row in ed.apropos_rows("trusted-secret"))


def test_word_read_capability_is_advertised() -> None:
    ed = _editor()
    _hostcall(ed, "host.capabilities")
    rows = {str(row[0]): row for row in ed.vm.stack[-1]}
    assert rows["ed.word-read"][1] == "cap.word-read"
    assert rows["ed.word-read"][3] == 0

    assert ed.exec_command_line("set cap.word-read true") is True
    _hostcall(ed, "host.capabilities")
    rows = {str(row[0]): row for row in ed.vm.stack[-1]}
    assert rows["ed.word-read"][3] == 1
