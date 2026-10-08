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


def test_bounded_encoded_buffer_signature_matches_canonical_lf_text() -> None:
    import hashlib

    from micromax_editor.buffer import FASTDIRTY_AUTO_BYTES, Buffer

    text = (
        "αβ\n"
        + ("short row\n" * 9000)
        + ("x" * (FASTDIRTY_AUTO_BYTES + 17))
        + "\n"
        + "\ud800surrogate\n"
    )
    buf = Buffer(text)
    canonical = buf.get_text().encode("utf-8", errors="surrogatepass")
    expected = (
        len(canonical),
        hashlib.blake2b(canonical, digest_size=16).hexdigest(),
    )

    assert buf._current_signature() == expected
    assert buf._text_signature(buf.get_text()) == expected


def test_large_buffer_auto_fastdirty_is_visible_and_reversible() -> None:
    from micromax_editor.buffer import FASTDIRTY_AUTO_BYTES, Cursor

    text = "x" * FASTDIRTY_AUTO_BYTES
    ed = Editor()
    ed.new_buffer("large.txt", text, path="large.txt")
    eb = ed.cur()

    assert eb.local_options["fastdirty"] is True
    assert ed.options.get("fastdirty", local=eb.local_options) is True
    assert eb.buf.fastdirty is True

    assert ed.exec_command_line("setlocal fastdirty false") is True
    assert eb.local_options["fastdirty"] is False
    assert eb.buf.fastdirty is False

    end = eb.buf.insert(Cursor(0, len(text)), "!")
    assert eb.buf.dirty is True
    eb.buf.delete_range(Cursor(end.line, end.col - 1), end)
    assert eb.buf.get_text() == text
    assert eb.buf.dirty is False


def test_buffer_below_auto_fastdirty_threshold_remains_exact() -> None:
    from micromax_editor.buffer import FASTDIRTY_AUTO_BYTES

    ed = Editor()
    ed.new_buffer("ordinary.txt", "x" * (FASTDIRTY_AUTO_BYTES - 1))
    eb = ed.cur()

    assert "fastdirty" not in eb.local_options
    assert ed.options.get("fastdirty", local=eb.local_options) is False
    assert eb.buf.fastdirty is False
