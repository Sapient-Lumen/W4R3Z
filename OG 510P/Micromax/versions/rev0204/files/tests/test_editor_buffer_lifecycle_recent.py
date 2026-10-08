from __future__ import annotations

from pathlib import Path

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


def test_open_does_not_overwrite_existing_dirty_buffer(tmp_path: Path) -> None:
    p = tmp_path / "a.txt"
    p.write_text("hello", encoding="utf-8")

    ed = Editor()
    ed.exec_command_line(f"open {p}")
    assert ed.cur().buf.get_text() == "hello"

    # Make buffer dirty without saving.
    ed.input["text"] = "!"
    ed.run_action("EndOfLine")
    ed.run_action("InsertText")
    assert ed.cur().buf.get_text() == "hello!"
    assert ed.cur().buf.dirty is True

    # Re-open same path should *not* clobber unsaved text.
    ed.exec_command_line(f"open {p}")
    assert ed.cur().buf.get_text() == "hello!"
    assert ed.cur().buf.dirty is True


def test_recent_tracks_open_and_save_and_picker_opens(tmp_path: Path) -> None:
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("A", encoding="utf-8")
    b.write_text("B", encoding="utf-8")

    ed = Editor()
    ed.exec_command_line(f"open {a}")
    ed.exec_command_line(f"open {b}")

    assert ed.recent_files[:2] == [str(b), str(a)]

    # Saving should bump path to MRU.
    ed.exec_command_line(f"open {a}")
    ed.input["text"] = "!"
    ed.run_action("EndOfLine")
    ed.run_action("InsertText")
    ed.exec_command_line("save")
    assert ed.recent_files[0] == str(a)

    # recentpick should open a prompt with suggestions.
    ed.exec_command_line("recentpick")
    assert ed.prompt is not None
    assert ed.prompt.kind == "recent"
    assert str(a) in ed.prompt.suggestions
    assert str(b) in ed.prompt.suggestions
    assert ed.prompt_current_section() == str(tmp_path)
    assert ed.prompt_current_preview().startswith(f"{tmp_path}: {a}")

    # Pick b -> opens/switches to it.
    ed.prompt.suggest_index = ed.prompt.suggestions.index(str(b))
    assert ed.submit_prompt() is True
    assert ed.cur().buf.path == str(b)


def test_close_buffer_dirty_guard_and_force(tmp_path: Path) -> None:
    p = tmp_path / "a.txt"
    p.write_text("hello", encoding="utf-8")

    ed = Editor()
    ed.exec_command_line(f"open {p}")
    assert str(p) in ed.buffers

    # Dirty buffer -> first close warns and does not close.
    ed.cur().buf.dirty = True
    ed.messages.clear()
    assert ed.exec_command_line("close") is False
    assert str(p) in ed.buffers
    assert ed.messages and "unsaved changes" in ed.messages[-1]

    # Second close closes.
    ed.messages.clear()
    assert ed.exec_command_line("close") is True
    assert str(p) not in ed.buffers

    # Force close skips the guard.
    q = tmp_path / "b.txt"
    q.write_text("x", encoding="utf-8")
    ed.exec_command_line(f"open {q}")
    ed.cur().buf.dirty = True
    assert ed.exec_command_line("close -f") is True
    assert str(q) not in ed.buffers


def test_recent_and_with_viewport_hostcalls(tmp_path: Path) -> None:
    p = tmp_path / "a.txt"
    p.write_text("hello", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)

    ed.exec_command_line(f"open {p}")

    xs = _hostcall(ed, 'ed.recent')
    assert isinstance(xs, list)
    assert str(p) in [str(x) for x in xs]

    # with-viewport should restore after mutation.
    ed.set_viewport(top_line=3, top_subline=2, left_col=1, height=10, width=20, follow_cursor=False)
    before = dict(ed.viewport_model())

    # Quotation: mutate viewport via hostcall.
    ed.vm.eval('[ 0 0 1 1 "ed.viewport!" hostcall ]', filename='<q>')
    q = ed.vm.stack.pop()

    ok = _hostcall(ed, 'ed.with-viewport', q)
    assert ok == 1
    after = dict(ed.viewport_model())
    assert after == before

def test_with_viewport_restores_softwrap_and_top_subline(tmp_path: Path) -> None:
    p = tmp_path / "wrap.txt"
    p.write_text("    one two three four five six seven eight nine ten\n", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    ed.exec_command_line(f"open {p}")

    # Enable softwrap and set a viewport with a nonzero top_subline.
    ed.options.set("softwrap", "true", local=ed.cur().local_options)
    ed.set_viewport(top_line=0, top_subline=2, left_col=7, height=5, width=10, follow_cursor=False)
    before = dict(ed.viewport_model())
    # Under softwrap, left_col must be 0.
    assert before["left_col"] == 0

    # Quotation: mutate viewport in a way that would normally clamp/disable fields.
    ed.vm.eval('[ 0 0 0 3 "ed.viewport!" hostcall ]', filename='<q>')
    q = ed.vm.stack.pop()

    ok = _hostcall(ed, 'ed.with-viewport', q)
    assert ok == 1
    after = dict(ed.viewport_model())
    assert after == before


def test_recentpick_groups_rows_by_project_root_and_rewrites_details(tmp_path: Path) -> None:
    p1 = tmp_path / "proj1"
    p2 = tmp_path / "proj2"
    p1.mkdir()
    p2.mkdir()
    (p1 / 'pyproject.toml').write_text('[project]\nname = "p1"\n', encoding='utf-8')
    (p2 / 'pyproject.toml').write_text('[project]\nname = "p2"\n', encoding='utf-8')
    a = p1 / 'src' / 'a.txt'
    b = p2 / 'lib' / 'b.txt'
    c = p1 / 'tests' / 'c.txt'
    a.parent.mkdir(parents=True)
    b.parent.mkdir(parents=True)
    c.parent.mkdir(parents=True)
    a.write_text('A', encoding='utf-8')
    b.write_text('B', encoding='utf-8')
    c.write_text('C', encoding='utf-8')

    ed = Editor()
    ed.open_file(str(a))
    ed.open_file(str(b))
    ed.open_file(str(c))

    assert ed.exec_command_line('recentpick') is True
    assert ed.prompt is not None
    assert ed.prompt.kind == 'recent'

    rows = [[str(x) for x in row[:4]] for row in ed.prompt.suggestion_rows]
    labels = [ed.prompt_row_section_label(row, prompt_kind='recent') for row in rows]
    assert labels == [str(p1), str(p1), str(p2)]

    assert rows[0][0] == str(c)
    assert rows[0][2] == 'proj1'
    assert rows[0][3] == 'tests/c.txt'
    assert rows[1][0] == str(a)
    assert rows[1][2] == 'proj1'
    assert rows[1][3] == 'src/a.txt'
    assert rows[2][0] == str(b)
    assert rows[2][2] == 'proj2'
    assert rows[2][3] == 'lib/b.txt'


def test_recentpick_alt_up_down_jumps_between_project_sections(tmp_path: Path) -> None:
    p1 = tmp_path / "proj1"
    p2 = tmp_path / "proj2"
    p1.mkdir()
    p2.mkdir()
    (p1 / '.git').mkdir()
    (p2 / '.git').mkdir()
    a = p1 / 'a.txt'
    b = p1 / 'b.txt'
    c = p2 / 'c.txt'
    a.write_text('A', encoding='utf-8')
    b.write_text('B', encoding='utf-8')
    c.write_text('C', encoding='utf-8')

    ed = Editor()
    ed.open_file(str(a))
    ed.open_file(str(c))
    ed.open_file(str(b))

    assert ed.exec_command_line('recentpick') is True
    assert ed.prompt is not None
    assert ed.prompt.kind == 'recent'
    starts: list[int] = []
    last = None
    for i, row in enumerate(ed.prompt.suggestion_rows):
        lbl = ed.prompt_row_section_label([str(x) for x in row[:4]], prompt_kind='recent')
        if lbl != last:
            starts.append(i)
            last = lbl
    assert starts == [0, 2]

    ed.prompt.suggest_index = 1
    assert ed.dispatch_key('Alt-UpArrow') is True
    assert ed.prompt is not None
    assert int(ed.prompt.suggest_index) == 0

    assert ed.dispatch_key('Alt-DownArrow') is True
    assert ed.prompt is not None
    assert int(ed.prompt.suggest_index) == 2
