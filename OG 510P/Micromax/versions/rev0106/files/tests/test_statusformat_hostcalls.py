from __future__ import annotations

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _hostcall(ed: Editor, name: str, *args: object) -> object:
    vm = ed.vm
    vm.stack.clear()
    for a in args:
        vm.stack.append(a)
    vm.stack.append(name)
    vm.eval('hostcall')
    assert vm.stack
    return vm.stack.pop()


def test_ed_statusfmt_and_statusline_text_hostcalls() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('t.mx', 'x', path='t.mx')

    out = _hostcall(ed, 'ed.statusfmt', '$(filename)')
    assert isinstance(out, str)
    assert 't.mx' in out

    s = _hostcall(ed, 'ed.statusline-text', 40)
    assert isinstance(s, str)
    assert len(s) <= 40


def test_ed_with_buffer_hostcall_restores_active_buffer() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'aaa\n')
    ed.new_buffer('b', 'bbb\n')
    assert ed.active == 'b'

    # Build a quotation that emits the active buffer name.
    ed.vm.eval('[ "ed.active-buffer" hostcall "ed.msg" hostcall ]', filename='<q>')
    q = ed.vm.stack.pop()

    ok = _hostcall(ed, 'ed.with-buffer', 'a', q)
    assert ok == 1
    assert ed.active == 'b'  # restored
    assert ed.messages and ed.messages[-1] == 'a'
