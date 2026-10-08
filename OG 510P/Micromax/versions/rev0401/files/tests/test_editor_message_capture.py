from __future__ import annotations

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def test_ed_with_messages_restores_log() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.message("keep")
    ed.vm.eval('[ "temp" "ed.msg" hostcall ] "ed.with-messages" hostcall')
    ok = ed.vm.pop_int()
    assert ok == 1
    assert ed.messages == ["keep"]


def test_ed_capture_messages_returns_emitted_and_restores_log() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.message("keep")
    ed.vm.eval('[ "a" "ed.msg" hostcall  "b" "ed.msg" hostcall ] "ed.capture-messages" hostcall')
    ok = ed.vm.pop_int()
    msgs = ed.vm.pop_list()
    assert ok == 1
    assert msgs == ["a", "b"]
    # original log restored
    assert ed.messages == ["keep"]
