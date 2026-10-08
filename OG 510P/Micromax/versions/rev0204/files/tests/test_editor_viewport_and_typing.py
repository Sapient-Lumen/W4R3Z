from __future__ import annotations

from pathlib import Path

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.plugins import PluginManager


def _load_core_plugins(ed: Editor) -> None:
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    root = Path(__file__).resolve().parents[1] / 'plugins'
    pm.load_tree(root)


def test_viewport_tracks_primary_cursor() -> None:
    ed = Editor()
    ed.new_buffer('*t*', "\n".join([f"line {i}" for i in range(10)]))

    # Small viewport.
    ed.set_viewport(top_line=0, left_col=0, height=3, width=5)
    assert ed.viewport_model()["top_line"] == 0

    # Move down beyond the bottom.
    for _ in range(4):
        ed.run_action('CursorDown')
    st = ed.status_model()
    assert st['line'] == 4
    # With height 3, cursor line 4 should force top to 2.
    assert st['viewport_top_line'] == 2

    # Horizontal scrolling.
    ed.new_buffer('*w*', "0123456789")
    ed.set_viewport(top_line=0, left_col=0, height=3, width=5)
    for _ in range(10):
        ed.run_action('CursorRight')
    st = ed.status_model()
    assert st['col'] == 10
    assert st['viewport_left_col'] == 6


def test_scrollmargin_keeps_vertical_context_in_plain_viewport() -> None:
    ed = Editor()
    ed.new_buffer('*t*', "\n".join([f"line {i}" for i in range(12)]))
    ed.options.set('scrollmargin', '2')

    ed.set_viewport(top_line=0, left_col=0, height=5, width=12, follow_cursor=False)
    for _ in range(4):
        ed.run_action('CursorDown')

    st = ed.status_model()
    assert st['line'] == 4
    # With height 5 and scrollmargin 2, line 4 should already push the window
    # down so the cursor keeps two rows of context above when possible.
    assert st['viewport_top_line'] == 2


def test_dispatch_key_fallback_inserts_text_into_buffer() -> None:
    ed = Editor()
    ed.new_buffer('*t*', "")

    assert ed.dispatch_key('h') is True
    assert ed.dispatch_key('i') is True
    assert ed.cur().buf.get_text() == 'hi'


def test_prompt_mode_typing_and_backspace_do_not_touch_buffer() -> None:
    ed = Editor()
    _load_core_plugins(ed)
    ed.new_buffer('*t*', 'abc')

    # Enter command prompt.
    assert ed.run_action('CommandMode') is True
    assert ed.prompt is not None

    # Typing edits prompt, not buffer.
    assert ed.dispatch_key('x') is True
    assert ed.prompt is not None and ed.prompt.text == 'x'
    assert ed.cur().buf.get_text() == 'abc'

    # Backspace edits prompt.
    assert ed.dispatch_key('Backspace') is True
    assert ed.prompt is not None and ed.prompt.text == ''
    assert ed.cur().buf.get_text() == 'abc'

    # Escape closes prompt (binding exists in core plugin).
    assert ed.dispatch_key('Esc') is True
    assert ed.prompt is None
