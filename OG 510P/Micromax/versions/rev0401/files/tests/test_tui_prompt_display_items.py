from __future__ import annotations

from micromax_editor.commandbar import Prompt
from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.tui import _prompt_display_items, _prompt_display_lines


def test_tui_prompt_display_items_preserves_row_kinds_and_text() -> None:
    ed = Editor()

    p = Prompt(kind="palette")
    rows: list[list[str]] = [
        ["./foo.txt", "openpath", "file", "/tmp"],
        ["/tmp/bar.txt", "recentfile", "bar.txt", "/tmp"],
        ["DoThing", "action", "do a thing", ""],
        ["save", "command", "save file", ""],
    ]
    p.suggestion_rows = rows
    p.suggestions = [r[0] for r in rows]
    p.suggest_index = 0
    ed.prompt = p

    items = _prompt_display_items(ed, max_lines=12, width=80)
    lines = _prompt_display_lines(ed, max_lines=20, width=80)

    assert lines == [it.text for it in items]

    row_items = [it for it in items if (not it.is_header and not it.is_more)]
    assert any(it.row_kind == "openpath" for it in row_items)
    assert any(it.row_kind == "recentfile" for it in row_items)
    assert any(it.row_kind == "action" for it in row_items)
    assert any(it.row_kind == "command" for it in row_items)



def test_tui_prompt_display_lines_show_jump_section_headers() -> None:
    ed = Editor()
    ed.new_buffer('a', 'one\ntwo\nthree\n')

    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    eb.cursors[eb.primary] = eb.buf.clamp(eb.cursors[eb.primary].__class__(0, 0))
    assert ed.push_jump() is True
    eb.cursors[eb.primary] = eb.buf.clamp(eb.cursors[eb.primary].__class__(1, 0))
    assert ed.push_jump() is True
    eb.cursors[eb.primary] = eb.buf.clamp(eb.cursors[eb.primary].__class__(2, 0))
    assert ed.push_jump() is True
    assert ed.jump_to_index(1) is True

    ed.enter_jump_prompt()
    assert ed.prompt is not None

    lines = _prompt_display_lines(ed, max_lines=8, width=80)
    assert any(line.startswith('-- Current (') for line in lines)
    assert any(line.startswith('-- Back (') for line in lines)
    assert any(line.startswith('-- Forward (') for line in lines)


def test_tui_prompt_display_lines_show_binding_mode_section_headers() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.vm.eval('"Ctrl-z" "command:help" "ed.bind" hostcall', filename='<global-bind>')
    ed.vm.eval('"nav" "Ctrl-x" "command:quit" "ed.bind-mode" hostcall', filename='<nav-bind>')
    ed.vm.eval('"prompt" "Ctrl-n" "command:showstatus" "ed.bind-mode" hostcall', filename='<prompt-bind>')
    ed.vm.eval('"nav" "ed.keymode-push" hostcall', filename='<push-nav>')

    ed.enter_binding_prompt()
    assert ed.prompt is not None

    lines = _prompt_display_lines(ed, max_lines=20, width=80)
    assert any(line.startswith('-- Prompt (') for line in lines)
    assert any(line.startswith('-- nav (') for line in lines)
    assert any(line.startswith('-- Global (') for line in lines)


def test_prompt_window_model_exposes_sticky_headers_and_more_markers() -> None:
    ed = Editor()

    p = Prompt(kind="helplink")
    rows: list[list[str]] = []
    rows.append(["Docs link 1", "link", "help:vision", ""])
    rows.append(["Docs link 2", "link", "help:help-browser", ""])
    rows.append(["File link 1", "link", "docs/00-vision.md", ""])
    rows.append(["File link 2", "link", "docs/98-help-browser.md", ""])
    for i in range(20):
        rows.append([f"External {i}", "link", f"https://example.com/{i}", ""])
    p.suggestion_rows = rows
    p.suggestions = [r[0] for r in rows]
    p.suggest_index = 14
    ed.prompt = p

    win = ed.prompt_window_model(max_lines=5)
    assert win['kind'] == 'helplink'
    assert win['show_top'] == 1
    assert win['show_bottom'] == 1
    assert win['sticky_section'] == 'External'
    entries = win['entries']
    assert entries[0]['type'] == 'more'
    assert entries[0]['direction'] == 'up'
    assert entries[1]['type'] == 'sticky'
    assert entries[1]['label'] == 'External'
    assert any(ent.get('type') == 'row' and ent.get('selected') == 1 for ent in entries)


def test_prompt_display_model_matches_tui_lines_and_metadata() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    p = Prompt(kind="helplink")
    rows: list[list[str]] = []
    rows.append(["Docs link 1", "link", "help:vision", ""])
    rows.append(["Docs link 2", "link", "help:help-browser", ""])
    rows.append(["File link 1", "link", "docs/00-vision.md", ""])
    rows.append(["File link 2", "link", "docs/98-help-browser.md", ""])
    for i in range(12):
        rows.append([f"External {i}", "link", f"https://example.com/{i}", ""])
    p.suggestion_rows = rows
    p.suggestions = [r[0] for r in rows]
    p.suggest_index = 10
    ed.prompt = p

    model = ed.prompt_display_model(max_lines=5, width=80)
    lines = _prompt_display_lines(ed, max_lines=5, width=80)

    assert [str(ent.get('text', '')) for ent in model] == lines
    assert model[0]['type'] == 'more'
    assert model[1]['type'] == 'sticky'
    assert model[1]['section_label'] == 'External'
    row = next(ent for ent in model if ent.get('type') == 'row' and int(ent.get('selected', 0)) == 1)
    assert row['row_kind'] == 'link'
    assert row['section_label'] == 'External'
    assert row['row'][0].startswith('External ')


def test_prompt_display_model_keeps_tail_detail_visible_when_rows_are_narrow() -> None:
    ed = Editor()

    p = Prompt(kind="palette")
    rows = [["VeryLongTopicName", "command", "docs/98-help-browser.md", ""]]
    p.suggestion_rows = rows
    p.suggestions = [r[0] for r in rows]
    p.suggest_index = 0
    ed.prompt = p

    model = ed.prompt_display_model(max_lines=3, width=22)
    row = next(ent for ent in model if ent.get("type") == "row")
    assert row["text"] == "> …/98-help-browser.md"


def test_prompt_display_model_preserves_detail_block_when_name_is_truncated() -> None:
    ed = Editor()

    p = Prompt(kind="palette")
    rows = [["VeryLongTopicName", "command", "docs/98-help-browser.md", ""]]
    p.suggestion_rows = rows
    p.suggestions = [r[0] for r in rows]
    p.suggest_index = 0
    ed.prompt = p

    model = ed.prompt_display_model(max_lines=3, width=30)
    row = next(ent for ent in model if ent.get("type") == "row")
    assert row["text"] == "> V… — docs/98-help-browser.md"


def test_prompt_display_model_headers_use_ellipsis_when_width_is_tiny() -> None:
    ed = Editor()

    p = Prompt(kind="palette")
    rows = [["save", "command", "save file", ""]]
    p.suggestion_rows = rows
    p.suggestions = [r[0] for r in rows]
    p.suggest_index = 0
    ed.prompt = p

    model = ed.prompt_display_model(max_lines=3, width=13)
    header = next(ent for ent in model if ent.get("type") == "header")
    assert header["text"] == "-- Commands …"
