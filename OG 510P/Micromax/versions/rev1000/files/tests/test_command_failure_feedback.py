from __future__ import annotations

from micromax_editor.editor import Editor


def _editor() -> Editor:
    ed = Editor()
    ed.new_buffer("*scratch*", "")
    return ed


def test_failed_command_without_feedback_replaces_stale_success_message() -> None:
    ed = _editor()
    ed.message("save: wrote prior.txt")
    ed.command_dispatcher.register("silent-fail", lambda _ed, _args: False)

    assert ed.exec_command_line("silent-fail") is False
    assert ed.messages[-1] == "command silent-fail: failed"


def test_failed_command_keeps_its_specific_feedback_without_generic_duplicate() -> None:
    ed = _editor()

    def explained_failure(editor: Editor, _args: list[str]) -> bool:
        editor.message("specific failure: review the selected target")
        return False

    ed.command_dispatcher.register("explained-fail", explained_failure)
    before = len(ed.messages)

    assert ed.exec_command_line("explained-fail") is False
    assert ed.messages[before:] == ["specific failure: review the selected target"]
