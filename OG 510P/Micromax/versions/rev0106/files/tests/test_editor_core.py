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

    ed.run_action("Redo")
    assert ed.cur().buf.get_text() == "XYZabc"


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

    assert ed.find("one") is True
    assert (ed.cur().cursors[0].line, ed.cur().cursors[0].col) == (0, 0)

    assert ed.find_next() is True
    assert ed.cur().cursors[0].col == 8

    assert ed.find_prev() is True
    assert ed.cur().cursors[0].col == 0


def test_options_set_show_toggle() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "")

    assert ed.exec_command_line("set hlsearch on") is True
    assert bool(ed.options.get("hlsearch")) is True

    assert ed.exec_command_line("toggle hlsearch") is True
    assert bool(ed.options.get("hlsearch")) is False


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

    # Move clears selection; paste appends at end.
    ed.run_action("EndOfLine")
    assert ed.run_action("Paste") is True
    assert ed.cur().buf.get_text() == "hello worldhello"

    # Cut a selection
    ed.cur().cursors[0] = Cursor(0, 0)
    for _ in range(5):
        ed.run_action("SelectRight")
    assert ed.run_action("Cut") is True
    assert ed.cur().buf.get_text().startswith(" world")


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

    assert ed.exec_command_line("replaceall one Y -l") is True
    assert ed.cur().buf.get_text() == "X Y"

    # ignorecase option (default True) applies to replace/replaceall, like find.
    ed.new_buffer("*t_ic*", "One oNe one")
    assert ed.exec_command_line("replace one X -l") is True
    # With ignorecase enabled, the first match from the cursor is "One".
    assert ed.cur().buf.get_text() == "X oNe one"
    assert ed.exec_command_line("replaceall one Y -l") is True
    assert ed.cur().buf.get_text() == "X Y Y"

    ed.new_buffer("*t_rx_ic*", "A1 a2")
    # Regex replace also respects ignorecase.
    assert ed.exec_command_line("replace 'a([0-9])' 'b$1' -a") is True
    assert ed.cur().buf.get_text() == "b1 b2"
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

    ed.prompt.set_text("set hl")
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
    assert ed.jump_back() is True
    assert (ed.primary_cursor().line, ed.primary_cursor().col) == (0, 0)
    assert ed.jump_forward() is True
    assert (ed.primary_cursor().line, ed.primary_cursor().col) == (3, 0)

    # Relative jump also records from/to.
    assert ed.exec_command_line("jump -2") is True
    assert (ed.primary_cursor().line, ed.primary_cursor().col) == (1, 0)
    assert ed.jump_back() is True
    assert (ed.primary_cursor().line, ed.primary_cursor().col) == (3, 0)


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
