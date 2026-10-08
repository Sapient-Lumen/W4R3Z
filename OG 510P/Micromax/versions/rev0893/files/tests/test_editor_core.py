from __future__ import annotations

from pathlib import Path

from micromax_editor.buffer import Buffer, Cursor
from micromax_editor.editor import Editor
from micromax_editor.keymap import parse_action_chain
from micromax_editor.plugins import PluginManager


def test_buffer_insert_delete() -> None:
    b = Buffer("hello\nworld")
    cur = b.insert(Cursor(0, 5), "!")
    assert b.get_text() == "hello!\nworld"
    assert (cur.line, cur.col) == (0, 6)

    cur2 = b.insert(Cursor(0, 6), "\nX")
    assert b.get_text() == "hello!\nX\nworld"
    assert (cur2.line, cur2.col) == (1, 1)

    b.delete_range(Cursor(0, 0), Cursor(0, 6))
    assert b.get_text().startswith("\n")


def test_editor_insert_undo_redo() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "abc")
    ed.input["text"] = "XYZ"
    ed.run_action("InsertText")
    assert ed.cur().buf.get_text() == "XYZabc"

    ed.run_action("Undo")
    assert ed.cur().buf.get_text() == "abc"
    assert ed.status_model()["last_message"] == "undo: insert 3 -> *t* @ 1:0"

    ed.run_action("Redo")
    assert ed.cur().buf.get_text() == "XYZabc"
    assert ed.status_model()["last_message"] == "redo: insert 3 -> *t* @ 1:3"


def test_undo_redo_commands_report_feedback_and_empty_state() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "abc")

    assert ed.exec_command_line("undo") is False
    assert ed.status_model()["last_message"] == "undo: nothing to undo"

    ed.input["text"] = "Z"
    assert ed.run_action("InsertText") is True
    assert ed.exec_command_line("undo") is True
    assert ed.cur().buf.get_text() == "abc"
    assert ed.status_model()["last_message"] == "undo: insert 1 -> *t* @ 1:0"

    assert ed.exec_command_line("redo") is True
    assert ed.cur().buf.get_text() == "Zabc"
    assert ed.status_model()["last_message"] == "redo: insert 1 -> *t* @ 1:1"

    assert ed.exec_command_line("redo") is False
    assert ed.status_model()["last_message"] == "redo: nothing to redo"


def test_action_chain_semantics() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "")

    # Noop returns False
    assert ed.run_action_chain("Noop,Noop") is False

    # '|' aborts chain if previous action succeeded
    ed.input["text"] = "A"
    assert ed.run_action_chain("InsertText|Noop") is True
    assert ed.cur().buf.get_text() == "A"

    # '&' aborts chain if previous action failed
    assert ed.run_action_chain("Noop&InsertText") is False


def test_action_chain_parsing_respects_quotes_and_escapes() -> None:
    steps = parse_action_chain("command:replace 'a,b' 'c'|Noop")
    assert [s.action for s in steps] == ["command:replace 'a,b' 'c'", "Noop"]

    steps2 = parse_action_chain(r"Foo\,Bar,Noop")
    assert [s.action for s in steps2] == ["Foo,Bar", "Noop"]


def test_command_prefix_and_command_edit() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "")

    ok = ed.run_action_chain("command:pwd")
    assert ok is True
    assert ed.messages
    from pathlib import Path
    assert ed.messages[-1] == str(Path.cwd())

    ok2 = ed.run_action_chain("command-edit:help ")
    assert ok2 is True
    assert ed.prompt is not None
    assert ed.prompt.kind == "command"
    assert ed.prompt.text == "help "


def test_find_next_previous() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "one two one")

    ed.enter_prompt("find")
    assert ed.set_prompt_text("one") is True
    assert ed.submit_prompt() is True
    assert (ed.cur().cursors[0].line, ed.cur().cursors[0].col) == (0, 0)
    assert ed.status_model()["last_message"] == "find: *t* @ 1:0 (1/2)"

    assert ed.find_next() is True
    assert ed.cur().cursors[0].col == 8
    assert ed.status_model()["last_message"] == "findnext: *t* @ 1:8 (2/2)"

    assert ed.find_prev() is True
    assert ed.cur().cursors[0].col == 0
    assert ed.status_model()["last_message"] == "findprev: *t* @ 1:0 (1/2)"


def test_find_next_previous_fail_explicitly() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "one two")

    assert ed.find_next() is False
    assert ed.status_model()["last_message"] == "findnext: no active search"

    assert ed.find_prev() is False
    assert ed.status_model()["last_message"] == "findprev: no active search"

    assert ed.find("one") is True
    assert ed.find_next() is False
    assert ed.status_model()["last_message"] == "findnext: not found"
    assert ed.find_prev() is False
    assert ed.status_model()["last_message"] == "findprev: not found"


def test_options_set_show_toggle() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "")

    assert ed.exec_command_line("set hlsearch on") is True
    assert bool(ed.options.get("hlsearch")) is True

    assert ed.exec_command_line("toggle hlsearch") is True
    assert bool(ed.options.get("hlsearch")) is False


def test_option_commands_report_typed_feedback() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "")

    assert ed.exec_command_line("set hlsearch on") is True
    assert ed.status_model()["last_message"] == "set: hlsearch=True"

    assert ed.exec_command_line("toggle hlsearch") is True
    assert ed.status_model()["last_message"] == "toggle: hlsearch=False"

    assert ed.exec_command_line("setlocal readonly true") is True
    assert ed.status_model()["last_message"] == "setlocal: readonly(local)=True"

    assert ed.exec_command_line("togglelocal readonly") is True
    assert ed.status_model()["last_message"] == "togglelocal: readonly(local)=False"


def test_minimal_plugin_lifecycle(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    p = root / "p1"
    p.mkdir(parents=True)
    (p / "init.mx").write_text(
        """
        : init ( -- )
          123 constant plugin_loaded
        ;
        """.strip(),
        encoding="utf-8",
    )

    ed = Editor()
    pm = PluginManager(ed.vm)
    loaded = pm.load_tree(root)
    assert [pl.name for pl in loaded] == ["p1"]
    pl = loaded[0]
    w = ed.vm.find_word_in_wid(pl.wid, "plugin_loaded")
    assert w is not None


def test_selection_copy_cut_paste() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "hello world")

    # Select "hello" using SelectRight (shift-arrow semantics).
    for _ in range(5):
        ed.run_action("SelectRight")
    assert ed.selection_text() == "hello"

    assert ed.run_action("Copy") is True
    assert ed.clipboard_text() == "hello"
    assert ed.messages[-1] == "copied: 1 selection, 5 chars"

    # Move clears selection; paste appends at end.
    ed.run_action("EndOfLine")
    assert ed.run_action("Paste") is True
    assert ed.cur().buf.get_text() == "hello worldhello"
    assert ed.messages[-1] == "paste: 1 cursor, 5 chars -> *t* @ 1:16"

    # Cut a selection
    ed.cur().cursors[0] = Cursor(0, 0)
    for _ in range(5):
        ed.run_action("SelectRight")
    assert ed.run_action("Cut") is True
    assert ed.cur().buf.get_text().startswith(" world")
    assert ed.messages[-1] == "cut: 1 selection, 5 chars -> *t* @ 1:0"


def test_cutline_duplicate_and_indent() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "a\nb")

    assert ed.run_action("CutLine") is True
    assert ed.clipboard_text() == "a\n"
    assert ed.cur().buf.get_text() == "b"

    assert ed.run_action("DuplicateLine") is True
    assert ed.cur().buf.get_text() == "b\nb"

    ed.run_action("SelectAll")
    assert ed.run_action("IndentSelection") is True
    assert ed.cur().buf.get_text().startswith("    b")
    assert ed.run_action("UnindentSelection") is True
    assert ed.cur().buf.get_text() == "b\nb"


def test_replace_commands_literal_and_regex() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "one one")

    assert ed.exec_command_line("replace one X -l") is True
    assert ed.cur().buf.get_text() == "X one"
    assert ed.status_model()["last_message"] == "replace: replaced 1 occurrence from cursor"

    assert ed.exec_command_line("replaceall one Y -l") is True
    assert ed.cur().buf.get_text() == "X Y"
    assert ed.status_model()["last_message"] == "replaceall: replaced 1 occurrence"

    # ignorecase option (default True) applies to replace/replaceall, like find.
    ed.new_buffer("*t_ic*", "One oNe one")
    assert ed.exec_command_line("replace one X -l") is True
    # With ignorecase enabled, the first match from the cursor is "One".
    assert ed.cur().buf.get_text() == "X oNe one"
    assert ed.status_model()["last_message"] == "replace: replaced 1 occurrence from cursor"
    assert ed.exec_command_line("replaceall one Y -l") is True
    assert ed.cur().buf.get_text() == "X Y Y"
    assert ed.status_model()["last_message"] == "replaceall: replaced 2 occurrences"

    ed.new_buffer("*t_rx_ic*", "A1 a2")
    # Regex replace also respects ignorecase.
    assert ed.exec_command_line("replace 'a([0-9])' 'b$1' -a") is True
    assert ed.cur().buf.get_text() == "b1 b2"
    assert ed.status_model()["last_message"] == "replaceall: replaced 2 occurrences"


def test_replace_commands_report_not_found_without_mutating() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "alpha beta")

    assert ed.exec_command_line("replace gamma X -l") is False
    assert ed.cur().buf.get_text() == "alpha beta"
    assert ed.status_model()["last_message"] == "replace: not found"

    assert ed.exec_command_line("replaceall gamma X -l") is False
    assert ed.cur().buf.get_text() == "alpha beta"
    assert ed.status_model()["last_message"] == "replaceall: not found"


def test_replace_commands_reject_unknown_flags_without_mutating() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "one one")

    assert ed.exec_command_line("replace one X --literal") is False
    assert ed.cur().buf.get_text() == "one one"
    assert ed.status_model()["last_message"] == "replace: unknown flag: --literal"

    assert ed.exec_command_line("replace one X -a --literal") is False
    assert ed.cur().buf.get_text() == "one one"
    assert ed.status_model()["last_message"] == "replaceall: unknown flag: --literal"

    assert ed.exec_command_line("replaceall one X --literal") is False
    assert ed.cur().buf.get_text() == "one one"
    assert ed.status_model()["last_message"] == "replaceall: unknown flag: --literal"


def test_replace_commands_reject_empty_search_without_mutating() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "abc")

    assert ed.exec_command_line("replace '' X -l") is False
    assert ed.cur().buf.get_text() == "abc"
    assert ed.status_model()["last_message"] == "replace: empty search"

    assert ed.exec_command_line("replace '' X -a -l") is False
    assert ed.cur().buf.get_text() == "abc"
    assert ed.status_model()["last_message"] == "replaceall: empty search"

    assert ed.exec_command_line("replaceall '' X -l") is False
    assert ed.cur().buf.get_text() == "abc"
    assert ed.status_model()["last_message"] == "replaceall: empty search"


def test_replace_commands_reject_zero_width_regex_without_mutating() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "abc")

    assert ed.exec_command_line("replace '$' X") is False
    assert ed.cur().buf.get_text() == "abc"
    assert ed.status_model()["last_message"] == "replace: zero-width matches are not supported"

    assert ed.exec_command_line("replace '$' X -a") is False
    assert ed.cur().buf.get_text() == "abc"
    assert ed.status_model()["last_message"] == "replaceall: zero-width matches are not supported"

    assert ed.exec_command_line("replaceall '$' X") is False
    assert ed.cur().buf.get_text() == "abc"
    assert ed.status_model()["last_message"] == "replaceall: zero-width matches are not supported"


def test_replaceall_rejects_regex_that_eventually_matches_zero_width_without_partial_edit() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "abc")

    assert ed.exec_command_line("replaceall 'abc|$' X") is False

    assert ed.cur().buf.get_text() == "abc"
    assert ed.status_model()["last_message"] == "replaceall: zero-width matches are not supported"


def test_replace_commands_keep_python_backslash_templates_literal() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "a1 a2")

    assert ed.exec_command_line(r"replace 'a([0-9])' '\1'") is True
    assert ed.cur().buf.get_text() == r"\1 a2"
    assert ed.status_model()["last_message"] == "replace: replaced 1 occurrence from cursor"

    ed = Editor()
    ed.new_buffer("*t*", "a1 a2")

    assert ed.exec_command_line(r"replaceall 'a([0-9])' '\q'") is True
    assert ed.cur().buf.get_text() == r"\q \q"
    assert ed.status_model()["last_message"] == "replaceall: replaced 2 occurrences"





def test_replace_commands_keep_leading_zero_numeric_templates_literal() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "ab ab")

    assert ed.exec_command_line("replace '(a)(b)' '$01'") is True
    assert ed.cur().buf.get_text() == "$01 ab"
    assert ed.status_model()["last_message"] == "replace: replaced 1 occurrence from cursor"

    assert ed.exec_command_line("replaceall '(a)(b)' '${01}'") is True
    assert ed.cur().buf.get_text() == "$01 ${01}"
    assert ed.status_model()["last_message"] == "replaceall: replaced 1 occurrence"


def test_replace_commands_keep_malformed_braced_templates_literal() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "a a")

    assert ed.exec_command_line("replace '(?P<x>a)' '${x>lit}'") is True
    assert ed.cur().buf.get_text() == "${x>lit} a"
    assert ed.status_model()["last_message"] == "replace: replaced 1 occurrence from cursor"

    assert ed.exec_command_line("replaceall '(?P<x>a)' '${$1}'") is True
    assert ed.cur().buf.get_text() == "${x>lit} ${$1}"
    assert ed.status_model()["last_message"] == "replaceall: replaced 1 occurrence"


def test_replace_commands_keep_unterminated_braced_templates_literal() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "a a")

    assert ed.exec_command_line("replace '(?P<x>a)' '${$1'") is True
    assert ed.cur().buf.get_text() == "${$1 a"
    assert ed.status_model()["last_message"] == "replace: replaced 1 occurrence from cursor"

    assert ed.exec_command_line("replaceall '(?P<x>a)' '${x$1'") is True
    assert ed.cur().buf.get_text() == "${$1 ${x$1"
    assert ed.status_model()["last_message"] == "replaceall: replaced 1 occurrence"


def test_replace_commands_reject_invalid_replacement_without_mutating() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "a1 a2")

    assert ed.exec_command_line("replace 'a([0-9])' '$2'") is False
    assert ed.cur().buf.get_text() == "a1 a2"
    assert ed.status_model()["last_message"].startswith("replace: invalid replacement: ")
    assert "invalid group reference 2" in ed.status_model()["last_message"]

    assert ed.exec_command_line("replaceall 'a([0-9])' '$2'") is False
    assert ed.cur().buf.get_text() == "a1 a2"
    assert ed.status_model()["last_message"].startswith("replaceall: invalid replacement: ")
    assert "invalid group reference 2" in ed.status_model()["last_message"]

    assert ed.exec_command_line("replaceall '(?P<num>[0-9])' '$missing'") is False
    assert ed.cur().buf.get_text() == "a1 a2"
    assert ed.status_model()["last_message"] == "replaceall: invalid replacement: unknown group name 'missing'"




def test_replace_commands_report_invalid_replacement_even_when_not_found() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "abc")

    assert ed.exec_command_line("replace 'z([0-9])' '$2'") is False
    assert ed.cur().buf.get_text() == "abc"
    assert ed.status_model()["last_message"].startswith("replace: invalid replacement: ")
    assert "invalid group reference 2" in ed.status_model()["last_message"]

    assert ed.exec_command_line("replaceall 'z([0-9])' '$2'") is False
    assert ed.cur().buf.get_text() == "abc"
    assert ed.status_model()["last_message"].startswith("replaceall: invalid replacement: ")
    assert "invalid group reference 2" in ed.status_model()["last_message"]

    assert ed.exec_command_line("replaceall '(?P<num>z)' '$missing'") is False
    assert ed.cur().buf.get_text() == "abc"
    assert ed.status_model()["last_message"] == "replaceall: invalid replacement: unknown group name 'missing'"

    # A valid replacement template with no matches remains an ordinary not-found
    # result; only actual template mistakes should win over `not found`.
    assert ed.exec_command_line("replaceall 'z([0-9])' '$1'") is False
    assert ed.cur().buf.get_text() == "abc"
    assert ed.status_model()["last_message"] == "replaceall: not found"


def test_replaceall_preserves_command_identity_for_regex_and_undo_feedback() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "one two one")

    assert ed.exec_command_line("replaceall '([)' X") is False
    assert ed.status_model()["last_message"].startswith("replaceall: invalid regex:")

    assert ed.exec_command_line("replaceall one X -l") is True
    assert ed.cur().buf.get_text() == "X two X"

    assert ed.exec_command_line("undo") is True
    assert ed.cur().buf.get_text() == "one two one"
    assert ed.status_model()["last_message"] == "undo: replaceall -> *t* @ 1:0"

    assert ed.exec_command_line("redo") is True
    assert ed.cur().buf.get_text() == "X two X"
    assert ed.status_model()["last_message"] == "redo: replaceall -> *t* @ 1:0"


def test_command_autocomplete() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "")
    ed.enter_prompt("command")
    assert ed.prompt is not None

    ed.prompt.set_text("replacea")
    ed.prompt.set_cursor(len(ed.prompt.text))
    assert ed.run_action("Autocomplete") is True
    assert ed.prompt.text == "replaceall "

def test_command_autocomplete_options() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "")
    ed.enter_prompt("command")
    assert ed.prompt is not None

    ed.prompt.set_text("set hls")
    ed.prompt.set_cursor(len(ed.prompt.text))
    assert ed.run_action("Autocomplete") is True
    assert ed.prompt.text == "set hlsearch "

def test_command_autocomplete_cycle_and_shift_tab() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "")
    ed.enter_prompt("command")
    assert ed.prompt is not None

    # 'tog' matches toggle and togglelocal -> expands to common prefix 'toggle'
    ed.prompt.set_text("tog")
    ed.prompt.set_cursor(len(ed.prompt.text))
    assert ed.run_action("Autocomplete") is True
    assert ed.prompt.text == "toggle"
    assert len(ed.prompt.suggestions) >= 2  # session started

    # Tab selects the first candidate
    assert ed.run_action("Autocomplete") is True
    assert ed.prompt.text in ("toggle ", "togglelocal ")

    # Shift-Tab (PromptCompletePrev) should move backwards.
    before = ed.prompt.text
    assert ed.run_action("PromptCompletePrev") is True
    assert ed.prompt.text != before

def test_paste_empty_clipboard_is_explicit() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "")
    ed.set_clipboard_items([], kind="items")

    assert ed.run_action("Paste") is False
    assert ed.messages[-1] == "paste: clipboard empty"


def test_cutline_accumulates_until_paste() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "a\nb\nc")

    assert ed.run_action("CutLine") is True
    assert ed.clipboard_text() == "a\n"
    assert ed.cur().buf.get_text() == "b\nc"

    assert ed.run_action("CutLine") is True
    assert ed.clipboard_text() == "a\nb\n"
    assert ed.cur().buf.get_text() == "c"

    # Paste resets the accumulation behavior.
    ed.run_action("EndOfLine")
    assert ed.run_action("Paste") is True
    assert ed.cur().buf.get_text() == "ca\nb\n"

    # CutLine now replaces (doesn't append).
    ed.cur().cursors[0] = Cursor(0, 0)
    assert ed.run_action("CutLine") is True
    assert ed.clipboard_text() == "ca\n"


def test_smartpaste_indents_unindented_multiline_block() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "    ")
    ed.cur().cursors[0] = Cursor(0, 4)
    ed.exec_command_line("set smartpaste true")
    ed.set_clipboard_items(["if x:\n    y\nz"], kind="items")

    assert ed.run_action("Paste") is True
    assert ed.cur().buf.get_text() == "    if x:\n        y\n    z"


def test_smartpaste_skips_midline_paste_and_already_indented_blocks() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "x = ")
    ed.cur().cursors[0] = Cursor(0, 4)
    ed.exec_command_line("set smartpaste true")
    ed.set_clipboard_items(["a\nb"], kind="items")
    assert ed.run_action("Paste") is True
    assert ed.cur().buf.get_text() == "x = a\nb"

    ed2 = Editor()
    ed2.new_buffer("*t2*", "    ")
    ed2.cur().cursors[0] = Cursor(0, 4)
    ed2.exec_command_line("set smartpaste true")
    ed2.set_clipboard_items(["    if x:\n        y"], kind="items")
    assert ed2.run_action("Paste") is True
    assert ed2.cur().buf.get_text() == "        if x:\n        y"


def test_smartpaste_maps_per_cursor_items_independently() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "    \n\t")
    ed.exec_command_line("set smartpaste true")
    eb = ed.cur()
    eb.cursors = [Cursor(0, 4), Cursor(1, 1)]
    eb.sel_anchors = [None, None]
    eb.primary = 0
    ed.set_clipboard_items(["a\nb", "x\ny"], kind="items")

    assert ed.run_action("Paste") is True
    assert ed.cur().buf.get_text() == "    a\n    b\n\tx\n\ty"


def test_macro_record_and_playback() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "")

    assert ed.run_action("ToggleMacro") is True
    ed.input["text"] = "A"
    ed.run_action("InsertText")
    ed.input["text"] = "B"
    ed.run_action("InsertText")
    assert ed.run_action("ToggleMacro") is True

    # Reset buffer and replay
    ed.cur().buf.set_text("")
    ed.cur().cursors[0] = Cursor(0, 0)
    assert ed.run_action("PlayMacro") is True
    assert ed.cur().buf.get_text() == "AB"


def test_multicursor_select_and_cut() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "foo bar foo")

    # Alt-n behavior: select current word + add cursor for next match
    assert ed.run_action("SpawnMultiCursorSelect") is True
    assert len(ed.cur().cursors) == 2
    assert ed.selection_text(0) == "foo"
    assert ed.selection_text(1) == "foo"

    assert ed.run_action("Cut") is True
    assert ed.cur().buf.get_text() == " bar "
    assert ed.clipboard_text() == "foo\nfoo"


def test_multicursor_document_order_and_primary_index() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "a\nb\nc")

    # Put cursor on the middle line.
    ed.cur().cursors[0] = Cursor(1, 0)
    ed.cur().primary = 0

    # Spawn a cursor above; the cursor list should be document-ordered, but the
    # primary remains on the original line.
    assert ed.run_action("SpawnMultiCursorUp") is True
    eb = ed.cur()
    assert [(c.line, c.col) for c in eb.cursors] == [(0, 0), (1, 0)]
    assert eb.primary == 1
    assert (ed.primary_cursor().line, ed.primary_cursor().col) == (1, 0)


def test_remove_multicursor_removes_latest_added() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "a\nb\nc")
    ed.cur().cursors[0] = Cursor(1, 0)
    ed.cur().primary = 0

    # Add DOWN then UP; "latest" should be UP (even though it's first in doc order).
    assert ed.run_action("SpawnMultiCursorDown") is True
    assert ed.run_action("SpawnMultiCursorUp") is True

    eb = ed.cur()
    assert [(c.line, c.col) for c in eb.cursors] == [(0, 0), (1, 0), (2, 0)]
    assert eb.primary == 1

    assert ed.run_action("RemoveMultiCursor") is True
    eb2 = ed.cur()
    assert [(c.line, c.col) for c in eb2.cursors] == [(1, 0), (2, 0)]
    assert eb2.primary == 0


def test_editor_hostcalls_multicursor_and_replace_selections() -> None:
    from micromax_editor.micromax_bridge import install_editor_hostcalls

    ed = Editor()
    ed.new_buffer("*t*", "foo foo")
    install_editor_hostcalls(ed)

    # Create two selections (Alt-n style) and then replace them via hostcall.
    assert ed.run_action("SpawnMultiCursorSelect") is True
    assert len(ed.cur().cursors) == 2

    vm = ed.vm
    vm.stack.append(["X", "Y"])
    vm.stack.append("ed.replace-selections")
    vm.eval("hostcall")
    col = vm.pop_int()
    line = vm.pop_int()
    assert (line, col) == (0, 1)
    assert ed.cur().buf.get_text() == "X Y"

    # Cursor/primary introspection
    vm.stack.append("ed.cursors")
    vm.eval("hostcall")
    curs = vm.pop_list()
    assert curs == [[0, 1], [0, 3]]

    vm.stack.append("ed.primary")
    vm.eval("hostcall")
    assert vm.pop_int() == ed.cur().primary

    # Undo should restore original
    ed.run_action("Undo")
    assert ed.cur().buf.get_text() == "foo foo"


def test_prompt_history_prev_next() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "")

    # run a command to seed history
    assert ed.exec_command_line("pwd") is True

    ed.enter_prompt("command")
    assert ed.prompt is not None
    assert ed.run_action("PromptHistoryPrev") is True
    assert ed.prompt.text == "pwd"

    assert ed.run_action("PromptHistoryNext") is True
    assert ed.prompt.text == ""  # restored


def test_skip_multicursor_advances_selection() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "foo foo foo")

    assert ed.run_action("SpawnMultiCursorSelect") is True
    # now have two cursors (match 1 and 2)
    assert len(ed.cur().cursors) == 2

    # skip should move primary selection to the third match
    assert ed.run_action("SkipMultiCursor") is True
    assert ed.selection_text() == "foo"
    # primary selection should now start at col 8
    rng = ed.selection_range()
    assert rng is not None
    s, e = rng
    assert (s.line, s.col) == (0, 8)
    assert (e.line, e.col) == (0, 11)

def test_hostcall_replace_range_is_undoable() -> None:
    from micromax_editor.micromax_bridge import install_editor_hostcalls

    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', 'hello')

    # Replace 'hello' with 'yo' via hostcall (line0 col0..col5).
    ed.vm.eval('0 0 0 5 "yo" "ed.replace-range" hostcall')
    assert ed.cur().buf.get_text() == 'yo'
    assert ed.undo.can_undo()
    assert ed.undo.undo()
    assert ed.cur().buf.get_text() == 'hello'





def test_hostcall_set_text_is_undoable_and_clamps_cursor_state() -> None:
    from micromax_editor.micromax_bridge import install_editor_hostcalls

    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*t*", "abcdef")
    ed.cur().cursors[0] = Cursor(0, 6)

    ed.vm.eval('"xy" "ed.set-text" hostcall')

    assert ed.cur().buf.get_text() == "xy"
    assert (ed.cur().cursors[0].line, ed.cur().cursors[0].col) == (0, 2)
    assert ed.undo.can_undo()
    assert ed.undo.undo()
    assert ed.cur().buf.get_text() == "abcdef"
    assert (ed.cur().cursors[0].line, ed.cur().cursors[0].col) == (0, 6)

def test_hostcall_with_undo_groups_multiple_edits() -> None:
    from micromax_editor.micromax_bridge import install_editor_hostcalls

    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*t*", "abc")

    before_depth = ed.undo.depth()

    # Two inserts performed as one undo step.
    ed.vm.eval('"group" [ "X" "ed.insert" hostcall "Y" "ed.insert" hostcall ] "ed.with-undo" hostcall')
    assert ed.cur().buf.get_text() == "XYabc"
    assert ed.undo.depth() == before_depth + 1

    assert ed.undo.undo()
    assert ed.cur().buf.get_text() == "abc"


def test_hostcall_clipboard_roundtrip_items_and_lines() -> None:
    from micromax_editor.micromax_bridge import install_editor_hostcalls

    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*t*", "x")

    ed.vm.stack.clear()
    ed.vm.eval('list "a" swap push "b" swap push "lines" "ed.set-clipboard-items" hostcall')
    assert ed.clipboard_kind == "lines"
    assert ed.clipboard_text() == "a\nb\n"

    ed.vm.stack.clear()
    ed.vm.eval('"ed.clipboard-items" hostcall')
    kind = ed.vm.stack.pop()
    items = ed.vm.stack.pop()
    assert kind == "lines"
    assert items == ["a", "b"]

    ed.vm.stack.clear()
    ed.vm.eval('"hello" "ed.set-clipboard" hostcall "ed.clipboard" hostcall')
    assert ed.vm.stack.pop() == "hello"


def test_hostcall_selection_recovery_stack() -> None:
    from micromax_editor.micromax_bridge import install_editor_hostcalls

    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*t*", "hello")

    # Start with two cursors.
    ed.vm.eval('list list 0 swap push 0 swap push swap push list 0 swap push 1 swap push swap push "ed.set-cursors" hostcall')
    assert len(ed.cur().cursors) == 2

    # Save selections, change cursors, restore.
    ed.vm.eval('"ed.push-selections" hostcall')
    ed.vm.eval('list list 0 swap push 4 swap push swap push "ed.set-cursors" hostcall')
    assert len(ed.cur().cursors) == 1

    ed.vm.stack.clear()
    ed.vm.eval('"ed.pop-selections" hostcall')
    assert ed.vm.stack.pop() == 1
    assert len(ed.cur().cursors) == 2


def test_hostcalls_set_selections_and_selection_range_helpers() -> None:
    from micromax_editor.micromax_bridge import install_editor_hostcalls

    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*t*", "hello world")

    # Two cursors: start + after space.
    ed.vm.eval(
        'list '
        '  list 0 swap push 0 swap push swap push '
        '  list 0 swap push 6 swap push swap push '
        '"ed.set-cursors" hostcall'
    )
    assert len(ed.cur().cursors) == 2

    # Set a *reversed* directed selection for cursor 0: anchor at col5, cursor at col0.
    # Cursor 1 has no selection.
    ed.vm.stack.clear()
    ed.vm.eval(
        'list '
        '  list 0 swap push 5 swap push 0 swap push 0 swap push swap push '
        '  list swap push '
        '"ed.set-selections" hostcall'
    )

    # `ed.selection-range` is normalized/directionless.
    ed.vm.stack.clear()
    ed.vm.eval('"ed.selection-range" hostcall')
    assert ed.vm.stack.pop() == [0, 0, 0, 5]

    # EnsureSelectionsForward makes anchor <= cursor (cursor moves).
    assert ed.run_action("EnsureSelectionsForward") is True
    sel0 = ed.cur().sel_anchors[ed.cur().primary]
    cur0 = ed.primary_cursor()
    assert sel0 is not None
    assert (sel0.line, sel0.col) <= (cur0.line, cur0.col)

    # FlipSelections swaps endpoints again.
    assert ed.run_action("FlipSelections") is True
    sel1 = ed.cur().sel_anchors[ed.cur().primary]
    cur1 = ed.primary_cursor()
    assert sel1 is not None
    assert (cur1.line, cur1.col) < (sel1.line, sel1.col)

    # Range setter is clamping + normalizing.
    ed.vm.stack.clear()
    ed.vm.eval('0 11 0 6 "ed.set-selection-range" hostcall')
    ed.vm.eval('"ed.selection-range" hostcall')
    assert ed.vm.stack.pop() == [0, 6, 0, 11]


def test_hostcall_cursorstate_roundtrip() -> None:
    from micromax_editor.micromax_bridge import install_editor_hostcalls

    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*t*", "hello world")

    # Two cursors: start + after space.
    ed.vm.eval(
        'list '
        '  list 0 swap push 0 swap push swap push '
        '  list 0 swap push 6 swap push swap push '
        '"ed.set-cursors" hostcall'
    )
    assert len(ed.cur().cursors) == 2

    # Give primary (cursor 0) a selection.
    ed.vm.stack.clear()
    ed.vm.eval('0 0 0 5 "ed.set-selection-range" hostcall')
    assert ed.selection_text() == "hello"

    # Snapshot.
    ed.vm.stack.clear()
    ed.vm.eval('"ed.cursorstate" hostcall')
    state = ed.vm.pop_list()
    assert isinstance(state, list) and len(state) == 2
    primary = state[0]
    entries = state[1]
    assert primary == ed.cur().primary
    assert len(entries) == 2
    # Primary cursor is at the *end* of the selection range.
    assert entries[0][1:3] == [0, 5]
    assert entries[0][3:5] == [0, 0]
    assert entries[1][1:3] == [0, 6]

    # Mutate cursor state, then restore.
    ed.vm.stack.clear()
    ed.vm.eval('list list 0 swap push 10 swap push swap push "ed.set-cursors" hostcall')
    assert len(ed.cur().cursors) == 1

    ed.vm.stack.clear()
    ed.vm.stack.append(state)
    ed.vm.stack.append('ed.set-cursorstate')
    ed.vm.eval('hostcall')

    assert len(ed.cur().cursors) == 2
    assert ed.cur().primary == primary
    assert ed.selection_text() == "hello"


def test_hostcall_with_cursorstate_restores_cursors_and_selections() -> None:
    from micromax_editor.micromax_bridge import install_editor_hostcalls

    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*t*", "hello")

    # Ensure no selection initially.
    assert ed.has_primary_selection() is False
    assert (ed.primary_cursor().line, ed.primary_cursor().col) == (0, 0)

    ed.vm.stack.clear()
    ed.vm.eval('[ 0 5 "ed.set-cursor" hostcall 0 0 0 5 "ed.set-selection-range" hostcall ] "ed.with-cursorstate" hostcall')
    assert ed.vm.stack.pop() == 1

    # Cursor + selection restored.
    assert (ed.primary_cursor().line, ed.primary_cursor().col) == (0, 0)
    assert ed.has_primary_selection() is False


def test_jumplist_push_back_forward_and_truncate() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "a\nb\nc")
    eb = ed.cur()

    # Start at top, save position.
    eb.cursors[0] = Cursor(0, 0)
    assert ed.run_action("PushJump") is True

    # Move to bottom, save position.
    eb.cursors[0] = Cursor(2, 0)
    assert ed.run_action("PushJump") is True

    # Jump back and forward.
    assert ed.run_action("JumpBack") is True
    assert (ed.primary_cursor().line, ed.primary_cursor().col) == (0, 0)
    assert ed.run_action("JumpForward") is True
    assert (ed.primary_cursor().line, ed.primary_cursor().col) == (2, 0)

    # Jump back, then push a new destination: the forward tail is truncated.
    assert ed.run_action("JumpBack") is True
    eb.cursors[0] = Cursor(1, 0)
    assert ed.run_action("PushJump") is True

    idx, n = ed.jump_info()
    assert (idx, n) == (1, 2)
    assert ed.run_action("JumpForward") is False


def test_goto_and_jump_commands_auto_push_jumplist() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "a\nb\nc\nd")
    eb = ed.cur()
    eb.cursors[0] = Cursor(0, 0)

    # auto-push is enabled by default
    assert ed.exec_command_line("goto 4") is True
    assert (ed.primary_cursor().line, ed.primary_cursor().col) == (3, 0)
    assert ed.status_model()["last_message"] == "goto: *t* @ 4:0"
    assert ed.jump_back() is True
    assert (ed.primary_cursor().line, ed.primary_cursor().col) == (0, 0)
    assert ed.jump_forward() is True
    assert (ed.primary_cursor().line, ed.primary_cursor().col) == (3, 0)

    # Relative jump also records from/to.
    assert ed.exec_command_line("jump -2") is True
    assert (ed.primary_cursor().line, ed.primary_cursor().col) == (1, 0)
    assert ed.status_model()["last_message"] == "jump: *t* @ 2:0"
    assert ed.jump_back() is True
    assert (ed.primary_cursor().line, ed.primary_cursor().col) == (3, 0)




def test_jumpback_and_jumpforward_actions_and_commands_report_orientation() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "a\nb\nc")
    eb = ed.cur()

    eb.cursors[0] = Cursor(0, 0)
    assert ed.run_action("PushJump") is True
    eb.cursors[0] = Cursor(2, 0)
    assert ed.run_action("PushJump") is True

    assert ed.run_action("JumpBack") is True
    assert ed.status_model()["last_message"] == "jumpback #1 [back 1] -> *t* @ 1:0"

    assert ed.run_action("JumpBack") is False
    assert ed.status_model()["last_message"] == "jumpback: no earlier jump"

    assert ed.run_action("JumpForward") is True
    assert ed.status_model()["last_message"] == "jumpforward #2 [forward 1] -> *t* @ 3:0"

    assert ed.exec_command_line("jumpback") is True
    assert ed.status_model()["last_message"] == "jumpback #1 [back 1] -> *t* @ 1:0"

    assert ed.exec_command_line("jumpforward") is True
    assert ed.status_model()["last_message"] == "jumpforward #2 [forward 1] -> *t* @ 3:0"

    assert ed.exec_command_line("jumpforward") is False
    assert ed.status_model()["last_message"] == "jumpforward: no later jump"

def test_editor_message_log_hostcalls() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "")

    # Install micromax hostcalls for the editor.
    from micromax_editor.micromax_bridge import install_editor_hostcalls

    install_editor_hostcalls(ed)

    ed.message("a")
    ed.message("b")

    ed.vm.eval('"ed.messages" hostcall')
    msgs = ed.vm.pop_list()
    assert msgs[-2:] == ["a", "b"]

    ed.vm.eval('"ed.last-message" hostcall')
    assert ed.vm.pop_str() == "b"

    ed.vm.eval('"ed.pop-message" hostcall')
    assert ed.vm.pop_str() == "a"

    ed.vm.eval('"ed.clear-messages" hostcall')
    assert ed.messages == []


def test_command_palette_action_opens_palette_prompt_with_suggestions() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "")

    assert ed.run_action("CommandPalette") is True
    assert ed.prompt is not None
    assert ed.prompt.kind == "palette"
    assert ed.prompt.suggestions
    assert ed.prompt.suggestion_rows
    assert ed.prompt.suggestion_rows[0][1] in ("command", "action")


def test_topic_prompt_action_opens_topic_prompt_with_suggestions() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "")

    assert ed.run_action("TopicPrompt") is True
    assert ed.prompt is not None
    assert ed.prompt.kind == "topic"
    assert ed.prompt.suggestions
    assert ed.prompt.suggestion_rows
    assert ed.prompt.suggestion_rows[0][1] in ("command", "action", "word")


def test_command_autocomplete_option_alias() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "")
    ed.enter_prompt("command")
    assert ed.prompt is not None

    ed.prompt.set_text("set saveh")
    ed.prompt.set_cursor(len(ed.prompt.text))
    assert ed.run_action("Autocomplete") is True
    assert ed.prompt.text == "set savehistory "


def test_replacepreview_reports_plan_without_mutating() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "one two one")

    assert ed.exec_command_line("replacepreview one X -a -l") is True

    assert ed.cur().buf.get_text() == "one two one"
    assert ed.status_model()["last_message"] == 'replacepreview: would replace 2 occurrences; first 1:0 "one" -> "X" (+1 more)'


def test_replacepreview_reports_invalid_template_without_mutating() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "abc")

    assert ed.exec_command_line("replacepreview 'z([0-9])' '$2'") is False

    assert ed.cur().buf.get_text() == "abc"
    assert ed.status_model()["last_message"].startswith("replacepreview: invalid replacement: ")


def test_hostcall_replace_preview_returns_plan_without_mutating() -> None:
    from micromax_editor.micromax_bridge import install_editor_hostcalls

    ed = Editor()
    ed.new_buffer("*t*", "one two one")
    install_editor_hostcalls(ed)

    ed.vm.eval('"one" "X" 1 1 "ed.replace-preview" hostcall')

    row = ed.vm.stack.pop()
    assert row[0:7] == [1, 2, 1, 1, 0, 0, ""]
    assert row[7][0] == [0, 0, 0, 3, "one", "X"]
    assert ed.cur().buf.get_text() == "one two one"


def test_hostcall_replace_preview_preflights_argument_types() -> None:
    from micromax.vm import MicromaxError
    from micromax_editor.micromax_bridge import install_editor_hostcalls

    ed = Editor()
    ed.new_buffer("*t*", "one")
    install_editor_hostcalls(ed)
    ed.vm.stack.extend(["one", "X", "not-int", 1, "ed.replace-preview"])

    try:
        ed.vm.eval("hostcall")
    except MicromaxError as exc:
        assert "expected replace_all int" in str(exc)
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("expected MicromaxError")

    assert ed.vm.stack[-4:] == ["one", "X", "not-int", 1]
