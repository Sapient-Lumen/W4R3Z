from __future__ import annotations

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def test_micromax_set_show_toggle_words_refresh_caps() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')

    # set parses tokens like an immediate word and returns the set value.
    ed.vm.eval('set cap.shell true', filename='<test>')
    assert int(ed.vm.stack.pop()) == 1

    # capability advertisement should refresh for cap.* changes.
    ed.vm.eval('"ed.shell" host.feature?', filename='<test>')
    assert int(ed.vm.stack.pop()) == 1

    # show reads the current value.
    ed.vm.eval('show cap.shell', filename='<test>')
    assert int(ed.vm.stack.pop()) == 1

    # toggle flips (bool only) and returns the new value.
    ed.vm.eval('toggle cap.shell', filename='<test>')
    assert int(ed.vm.stack.pop()) == 0
    ed.vm.eval('"ed.shell" host.feature?', filename='<test>')
    assert int(ed.vm.stack.pop()) == 0


def test_opt_bang_refreshes_caps_for_cap_dot_options() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')

    # stack-oriented path: opt! uses ed.opt-set hostcall.
    ed.vm.eval('"cap.shell" "true" opt!', filename='<test>')
    assert int(ed.vm.stack.pop()) == 1

    # should refresh host.feature? like set/toggle.
    ed.vm.eval('"ed.shell" host.feature?', filename='<test>')
    assert int(ed.vm.stack.pop()) == 1
