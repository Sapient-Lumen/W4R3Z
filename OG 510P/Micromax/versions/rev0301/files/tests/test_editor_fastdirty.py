from __future__ import annotations

from pathlib import Path

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def test_fastdirty_default_tracks_return_to_clean_text_via_undo() -> None:
    ed = Editor()
    ed.new_buffer('t.txt', 'abc', path='t.txt')

    ed.input['text'] = 'x'
    assert ed.run_action('InsertText') is True
    assert ed.cur().buf.dirty is True

    assert ed.run_action('Undo') is True
    assert ed.cur().buf.get_text() == 'abc'
    assert ed.cur().buf.dirty is False


def test_fastdirty_true_keeps_dirty_after_undo_until_save(tmp_path: Path) -> None:
    p = tmp_path / 'note.txt'
    p.write_text('abc', encoding='utf-8')

    ed = Editor()
    ed.new_buffer(str(p), 'abc', path=str(p))
    assert ed.exec_command_line('set fastdirty true') is True

    ed.input['text'] = 'x'
    assert ed.run_action('InsertText') is True
    assert ed.cur().buf.dirty is True

    assert ed.run_action('Undo') is True
    assert ed.cur().buf.get_text() == 'abc'
    assert ed.cur().buf.dirty is True

    ed.save()
    assert ed.cur().buf.dirty is False
    assert p.read_text(encoding='utf-8') == 'abc'


def test_fastdirty_option_changes_sync_through_hostcalls_and_locals() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('one.txt', 'a', path='one.txt')
    ed.new_buffer('two.txt', 'b', path='two.txt')

    ed.switch_buffer('one.txt')
    ed.vm.eval('"fastdirty" "true" "ed.opt-set" hostcall', filename='<test>')
    assert int(ed.vm.stack.pop()) == 1
    assert ed.buffers['one.txt'].buf.fastdirty is True
    assert ed.buffers['two.txt'].buf.fastdirty is True

    ed.vm.eval('"fastdirty" "false" "ed.opt-set-local" hostcall', filename='<test>')
    assert int(ed.vm.stack.pop()) == 0
    assert ed.buffers['one.txt'].buf.fastdirty is False
    assert ed.buffers['two.txt'].buf.fastdirty is True
