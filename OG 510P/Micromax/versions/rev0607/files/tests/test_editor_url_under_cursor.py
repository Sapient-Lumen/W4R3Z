from __future__ import annotations

from pathlib import Path

from micromax_editor.editor import Editor
from micromax_editor.buffer import Cursor
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.plugins import PluginManager


def _set_cursor_on_substring(ed: Editor, needle: str) -> None:
    eb = ed.cur()
    for i, line in enumerate(eb.buf.lines):
        s = str(line)
        if needle in s:
            col = s.index(needle)
            eb.cursors[0] = Cursor(i, col)
            eb.primary = 0
            return
    raise AssertionError(f"needle not found: {needle}")


def _load_core_plugins(ed: Editor) -> None:
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    root = Path(__file__).resolve().parents[1] / 'plugins'
    pm.load_tree(root)


def test_urlcopy_under_cursor_copies_and_strips_punctuation() -> None:
    ed = Editor()
    ed.new_buffer('*scratch*', 'see https://example.com/hi, ok\n')
    _set_cursor_on_substring(ed, 'https://example.com/hi')

    assert ed.exec_command_line('urlcopy') is True
    assert ed.clipboard_text().strip() == 'https://example.com/hi'


def test_urlopen_under_cursor_requires_confirmation_when_enabled() -> None:
    ed = Editor()
    ed.new_buffer('*scratch*', 'link: https://example.com/x\n')
    _set_cursor_on_substring(ed, 'example.com')

    ed.options.set('cap.open-url', 'true')
    opened: list[str] = []

    def _opener(url: str, new: int = 0):
        opened.append(url)
        return True

    ed._open_url_fn = _opener

    # Starts confirm mode; does not open yet.
    assert ed.exec_command_line('urlopen') is True
    assert ed.current_key_mode() == 'openurl'
    assert opened == []

    # Cancel does not open.
    assert ed.dispatch_key('n') is True
    assert opened == []

    # Try again and accept.
    assert ed.exec_command_line('urlopen') is True
    assert ed.dispatch_key('y') is True
    assert opened == ['https://example.com/x']
    assert ed.messages[-1] == 'urlopen: https://example.com/x'


def test_urlopen_explicit_url_uses_confirmation_by_default() -> None:
    ed = Editor()
    ed.options.set('cap.open-url', 'true')

    opened: list[str] = []
    ed._open_url_fn = lambda url, new=0: opened.append(url) or True

    assert ed.exec_command_line('urlopen https://example.com/z') is True
    assert ed.current_key_mode() == 'openurl'

    assert ed.dispatch_key('c') is True
    assert opened == []
    assert ed.clipboard_text().strip() == 'https://example.com/z'
    assert ed.messages[-1] == 'urlcopy: https://example.com/z'


def test_urlopen_confirmation_mentions_cursor_or_command_source() -> None:
    ed = Editor()
    ed.new_buffer('*scratch*', 'link: https://example.com/x\n')
    _set_cursor_on_substring(ed, 'example.com')
    ed.options.set('cap.open-url', 'true')

    assert ed.exec_command_line('urlopen') is True
    msg1 = ed.messages[-1] if ed.messages else ''
    assert 'open external link under cursor?' in msg1
    assert ed.dispatch_key('n') is True

    assert ed.exec_command_line('urlopen https://example.com/z') is True
    msg2 = ed.messages[-1] if ed.messages else ''
    assert 'open external link from command?' in msg2


def test_core_default_keybindings_include_alt_o_for_urlopen() -> None:
    ed = Editor()
    _load_core_plugins(ed)
    ed.new_buffer('*scratch*', '')

    b_open = ed.resolve_key_binding('Alt-o')
    assert b_open is not None
    assert b_open.action_spec == 'OpenUrlUnderCursor'

    b_copy = ed.resolve_key_binding('Alt-y')
    assert b_copy is not None
    assert b_copy.action_spec == 'CopyUrlUnderCursor'


def test_urlcopy_reports_typed_success_feedback() -> None:
    ed = Editor()
    ed.new_buffer('*scratch*', 'see https://example.com/hi, ok\n')
    _set_cursor_on_substring(ed, 'https://example.com/hi')

    assert ed.exec_command_line('urlcopy') is True
    assert ed.messages[-1] == 'urlcopy: https://example.com/hi'


def test_urlopen_under_cursor_reports_typed_success_feedback_when_confirmation_off() -> None:
    ed = Editor()
    ed.new_buffer('*scratch*', 'link: https://example.com/x\n')
    _set_cursor_on_substring(ed, 'example.com')
    ed.options.set('cap.open-url', 'true')
    ed.options.set('open-url.confirm', 'false')

    opened: list[str] = []
    ed._open_url_fn = lambda url, new=0: opened.append(url) or True

    assert ed.exec_command_line('urlopen') is True
    assert opened == ['https://example.com/x']
    assert ed.messages[-1] == 'urlopen: https://example.com/x'


def test_urlopen_explicit_url_reports_typed_success_feedback_when_confirmation_off() -> None:
    ed = Editor()
    ed.options.set('cap.open-url', 'true')
    ed.options.set('open-url.confirm', 'false')

    opened: list[str] = []
    ed._open_url_fn = lambda url, new=0: opened.append(url) or True

    assert ed.exec_command_line('urlopen https://example.com/z') is True
    assert opened == ['https://example.com/z']
    assert ed.messages[-1] == 'urlopen: https://example.com/z'


def test_urlopen_under_cursor_missing_url_uses_command_name() -> None:
    ed = Editor()
    ed.new_buffer('*scratch*', 'plain text only\n')

    assert ed.exec_command_line('urlopen') is False
    assert ed.messages[-1] == 'urlopen: no url under cursor'
