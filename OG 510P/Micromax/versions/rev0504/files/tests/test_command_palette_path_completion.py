from __future__ import annotations

from micromax_editor.editor import Cursor, Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def test_command_palette_path_completions_and_drilldown(tmp_path, monkeypatch) -> None:
    # Work in a temporary directory so the palette completions are deterministic.
    monkeypatch.chdir(tmp_path)

    (tmp_path / "dir").mkdir()
    (tmp_path / "dir" / "a.txt").write_text("hi\n", encoding="utf-8")
    (tmp_path / "doc.txt").write_text("x\n", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)

    # Disabled by default: no directory suggestions should appear.
    rows = ed.command_palette_apropos_rows("./d", limit=40)
    openpaths = [r[0] for r in rows if str(r[1]) == "openpath"]
    assert "./dir/" not in openpaths

    # Enable filesystem listing.
    assert ed.exec_command_line("set cap.fs-list true")

    rows = ed.command_palette_apropos_rows("./d", limit=80)
    openpaths = [str(r[0]) for r in rows if str(r[1]) == "openpath"]
    assert "./dir/" in openpaths
    assert "./doc.txt" in openpaths

    rows = ed.command_palette_apropos_rows("dir/", limit=80)
    openpaths = [str(r[0]) for r in rows if str(r[1]) == "openpath"]
    assert "dir/a.txt" in openpaths

    # Drill-down UX: selecting a directory keeps the palette open and navigates.
    ed.enter_command_palette("./d")
    assert ed.prompt is not None
    assert ed.prompt.kind == "palette"
    assert "./dir/" in [str(x) for x in (ed.prompt.suggestions or [])]
    idx = [str(x) for x in ed.prompt.suggestions].index("./dir/")
    ed.prompt.suggest_index = idx

    assert ed.submit_prompt() is True
    assert ed.prompt is not None
    assert ed.prompt.kind == "palette"
    assert str(ed.prompt.text).startswith("./dir/")


def test_command_palette_path_completions_respect_cap_fs_root(tmp_path, monkeypatch) -> None:
    root = tmp_path / "root"
    root.mkdir()
    (root / "dir").mkdir()
    (root / "dir" / "a.txt").write_text("hi\n", encoding="utf-8")
    (root / "doc.txt").write_text("x\n", encoding="utf-8")

    outside = tmp_path / "outside"
    outside.mkdir()
    monkeypatch.chdir(outside)

    ed = Editor()
    install_editor_hostcalls(ed)

    # Enable listing + sandbox.
    assert ed.exec_command_line("set cap.fs-list true")
    assert ed.exec_command_line(f"set cap.fs-root {root}")

    rows = ed.command_palette_apropos_rows("./d", limit=80)
    openpaths = [str(r[0]) for r in rows if str(r[1]) == "openpath"]
    assert "./dir/" in openpaths
    assert "./doc.txt" in openpaths

    rows = ed.command_palette_apropos_rows("dir/", limit=80)
    openpaths = [str(r[0]) for r in rows if str(r[1]) == "openpath"]
    assert "dir/a.txt" in openpaths

    # Drill-down still works under the sandbox.
    ed.enter_command_palette("./d")
    assert ed.prompt is not None and ed.prompt.kind == "palette"
    idx = [str(x) for x in ed.prompt.suggestions].index("./dir/")
    ed.prompt.suggest_index = idx
    assert ed.submit_prompt() is True
    assert ed.prompt is not None and ed.prompt.kind == "palette"
    assert str(ed.prompt.text).startswith("./dir/")


def test_command_palette_path_completion_sections_split_dirs_files_and_open_query(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    (tmp_path / "dir").mkdir()
    (tmp_path / "doc.txt").write_text("x\n", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-list true")

    sections = ed.command_palette_section_rows("./d", limit=80)
    labels = [str(sec[0]) for sec in sections]
    assert labels[:3] == ["Directories", "Files", "Open"]

    dirs = next(sec[1] for sec in sections if str(sec[0]) == "Directories")
    files = next(sec[1] for sec in sections if str(sec[0]) == "Files")
    openq = next(sec[1] for sec in sections if str(sec[0]) == "Open")

    assert any(isinstance(row, list) and row and str(row[0]) == "./dir/" and str(row[2]) == "dir" for row in dirs)
    assert any(isinstance(row, list) and row and str(row[0]) == "./doc.txt" and str(row[2]) == "file" for row in files)
    assert any(isinstance(row, list) and row and str(row[0]) == "./d" and str(row[2]) == "open" for row in openq)


def test_command_palette_path_completion_rows_keep_parent_and_recent_state(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    (tmp_path / "guide").mkdir()
    p = tmp_path / "guide" / "intro.md"
    r = tmp_path / "guide" / "notes.md"
    q = tmp_path / "draft.txt"
    p.write_text("intro\nnext\n", encoding="utf-8")
    r.write_text("notes\n", encoding="utf-8")
    q.write_text("draft\n", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-list true")

    ed.open_file(str(p))
    ed.open_file(str(r))
    assert ed.switch_buffer(str(p))
    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    eb.cursors[eb.primary] = eb.buf.clamp(Cursor(1, 1))
    eb.buf.dirty = True

    rows = ed.command_palette_apropos_rows("./d", limit=80)
    other_file = next(r for r in rows if str(r[1]) == "openpath" and str(r[0]) == "./draft.txt")
    assert other_file[2] == "file"
    assert other_file[3] == str(tmp_path)

    rows = ed.command_palette_apropos_rows("./g", limit=80)
    dir_row = next(r for r in rows if str(r[1]) == "openpath" and str(r[0]) == "./guide/")
    assert dir_row[2] == "dir"
    assert dir_row[3] == "recent dir: 2 files [active, open=2, dirty=1] | drill down"

    rows = ed.command_palette_apropos_rows("guide/i", limit=80)
    file_row = next(r for r in rows if str(r[1]) == "openpath" and str(r[0]) == "guide/intro.md")
    assert file_row[2] == "file"
    assert file_row[3] == "recent #2 [active, dirty] @ 2:1 | guide/intro.md | current buffer"

    rows = ed.command_palette_apropos_rows("guide/n", limit=80)
    sibling_row = next(r for r in rows if str(r[1]) == "openpath" and str(r[0]) == "guide/notes.md")
    assert sibling_row[2] == "file"
    assert sibling_row[3] == "recent #1 [open] @ 1:0 | guide/notes.md | switch buffer"



def test_command_palette_exact_open_rows_keep_target_context(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    (tmp_path / "guide").mkdir()
    p = tmp_path / "guide" / "intro.md"
    p.write_text("intro\nnext\n", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-list true")

    ed.open_file(str(p))
    assert ed.switch_buffer(str(p))
    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    eb.cursors[eb.primary] = eb.buf.clamp(Cursor(1, 1))
    eb.buf.dirty = True

    rows = ed.command_palette_apropos_rows("guide/intro.md", limit=80)
    file_open = next(r for r in rows if str(r[1]) == "openpath" and str(r[0]) == "guide/intro.md" and str(r[2]) == "open")
    assert file_open[3] == "recent #1 [active, dirty] @ 2:1 | guide/intro.md | existing file | current buffer"

    rows = ed.command_palette_apropos_rows("guide/", limit=80)
    dir_open = next(r for r in rows if str(r[1]) == "openpath" and str(r[0]) == "guide/" and str(r[2]) == "open")
    assert dir_open[3] == "recent dir: 1 file [active, open=1, dirty=1] | directory | drill down"

    rows = ed.command_palette_apropos_rows("draft.md", limit=80)
    new_open = next(r for r in rows if str(r[1]) == "openpath" and str(r[0]) == "draft.md" and str(r[2]) == "open")
    assert new_open[3] == f"new file | {tmp_path}"

    missing = tmp_path / "scratch.md"
    ed.open_file(str(missing))
    rows = ed.command_palette_apropos_rows("scratch.md", limit=80)
    unsaved_open = next(r for r in rows if str(r[1]) == "openpath" and str(r[0]) == "scratch.md" and str(r[2]) == "open")
    assert unsaved_open[3] == f"recent #1 [active] @ 1:0 | {tmp_path} | new file | current buffer"


def test_command_palette_parsecursor_existing_extensionless_targets_still_get_open_rows(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    guide = tmp_path / "guide"
    guide.mkdir()
    intro = tmp_path / "intro"
    intro.write_text("one\ntwo\n", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-list true")
    assert ed.exec_command_line("set parsecursor true")

    rows = ed.command_palette_apropos_rows("guide:2", limit=80)
    dir_open = next(r for r in rows if str(r[1]) == "openpath" and str(r[0]) == "guide:2" and str(r[2]) == "open")
    assert dir_open[3] == "directory | drill down"

    ed.enter_command_palette("guide:2")
    assert ed.prompt is not None and ed.prompt.kind == "palette"
    idx = next(
        i
        for i, row in enumerate(ed.prompt.suggestion_rows)
        if len(row) >= 3 and str(row[0]) == "guide:2" and str(row[1]) == "openpath" and str(row[2]) == "open"
    )
    ed.prompt.suggest_index = idx

    assert ed.submit_prompt() is True
    assert ed.prompt is not None and ed.prompt.kind == "palette"
    assert str(ed.prompt.text) == "guide/"

    rows = ed.command_palette_apropos_rows("intro:2", limit=80)
    file_open = next(r for r in rows if str(r[1]) == "openpath" and str(r[0]) == "intro:2" and str(r[2]) == "open")
    assert file_open[3] == f"existing file | {tmp_path} | cursor 2:0"

    ed.enter_command_palette("intro:2")
    assert ed.prompt is not None and ed.prompt.kind == "palette"
    idx = next(
        i
        for i, row in enumerate(ed.prompt.suggestion_rows)
        if len(row) >= 3 and str(row[0]) == "intro:2" and str(row[1]) == "openpath" and str(row[2]) == "open"
    )
    ed.prompt.suggest_index = idx

    assert ed.submit_prompt() is True
    assert ed.messages[-1].endswith("intro @ 2:0")
    assert ed.primary_cursor() == Cursor(1, 0)


def test_command_palette_parsecursor_partial_extensionless_queries_keep_completion_rows_visible(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    guide = tmp_path / "guide"
    guide.mkdir()
    intro = tmp_path / "intro"
    intro.write_text("one\ntwo\nthird\n", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-list true")
    assert ed.exec_command_line("set parsecursor true")

    rows = ed.command_palette_apropos_rows("gu:2", limit=80)
    dir_row = next(
        r for r in rows if str(r[1]) == "openpath" and str(r[0]) == "guide/:2" and str(r[2]) == "dir"
    )
    assert dir_row[3] == f"{tmp_path} | drill down"

    ed.enter_command_palette("gu:2")
    assert ed.prompt is not None and ed.prompt.kind == "palette"
    idx = next(
        i
        for i, row in enumerate(ed.prompt.suggestion_rows)
        if len(row) >= 3 and str(row[0]) == "guide/:2" and str(row[1]) == "openpath" and str(row[2]) == "dir"
    )
    ed.prompt.suggest_index = idx

    assert ed.submit_prompt() is True
    assert ed.prompt is not None and ed.prompt.kind == "palette"
    assert str(ed.prompt.text) == "guide/"

    rows = ed.command_palette_apropos_rows("intr:2", limit=80)
    file_row = next(
        r for r in rows if str(r[1]) == "openpath" and str(r[0]) == "intro:2" and str(r[2]) == "file"
    )
    assert file_row[3] == f"{tmp_path} | cursor 2:0"

    ed.enter_command_palette("intr:2")
    assert ed.prompt is not None and ed.prompt.kind == "palette"
    idx = next(
        i
        for i, row in enumerate(ed.prompt.suggestion_rows)
        if len(row) >= 3 and str(row[0]) == "intro:2" and str(row[1]) == "openpath" and str(row[2]) == "file"
    )
    ed.prompt.suggest_index = idx

    assert ed.submit_prompt() is True
    assert ed.messages[-1].endswith("intro @ 2:0")
    assert ed.primary_cursor() == Cursor(1, 0)


def test_command_palette_parsecursor_partial_unsaved_open_buffer_query_keeps_completion_row_visible(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-list true")
    assert ed.exec_command_line("set parsecursor true")

    scratch = tmp_path / "scratch.md"
    ed.open_file(str(scratch))

    rows = ed.command_palette_apropos_rows("scr:2", limit=80)
    file_row = next(
        r for r in rows if str(r[1]) == "openpath" and str(r[0]) == "scratch.md:2" and str(r[2]) == "file"
    )
    assert file_row[3] == f"recent #1 [active] @ 1:0 | {tmp_path} | new file | current buffer | goto 1:0"

    ed.enter_command_palette("scr:2")
    assert ed.prompt is not None and ed.prompt.kind == "palette"
    idx = next(
        i
        for i, row in enumerate(ed.prompt.suggestion_rows)
        if len(row) >= 3 and str(row[0]) == "scratch.md:2" and str(row[1]) == "openpath" and str(row[2]) == "file"
    )
    ed.prompt.suggest_index = idx

    assert ed.submit_prompt() is True
    assert ed.messages[-1].endswith("scratch.md @ 1:0")
    assert ed.primary_cursor() == Cursor(0, 0)




def test_command_palette_recent_file_row_keeps_live_buffer_action_truth_for_existing_files(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    guide = tmp_path / "guide"
    notes = tmp_path / "notes"
    guide.mkdir()
    notes.mkdir()
    intro = guide / "intro.md"
    daily = notes / "daily.txt"
    intro.write_text("intro\nnext\n", encoding="utf-8")
    daily.write_text("notes\n", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-list true")

    ed.open_file(str(intro))
    ed.open_file(str(daily))
    assert ed.switch_buffer(str(intro))
    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    eb.cursors[eb.primary] = eb.buf.clamp(Cursor(1, 1))
    eb.buf.dirty = True

    rows = ed.command_palette_apropos_rows("intro", limit=40)
    recent_row = next(
        r for r in rows if str(r[1]) == "recentfile" and str(r[0]) == str(intro)
    )
    assert recent_row[3] == f"section={tmp_path / "guide"} | {tmp_path / "guide"} | existing file | current buffer"

    rows = ed.command_palette_apropos_rows("daily", limit=40)
    recent_row = next(
        r for r in rows if str(r[1]) == "recentfile" and str(r[0]) == str(daily)
    )
    assert recent_row[3] == f"section={tmp_path / "notes"} | {tmp_path / "notes"} | existing file | switch buffer"


def test_command_palette_recent_file_row_keeps_existing_file_truth_for_closed_recent_file(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    old = tmp_path / "old.md"
    old.write_text("old\n", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-list true")

    ed.open_file(str(old))
    assert ed.exec_command_line("close")

    rows = ed.command_palette_apropos_rows("old", limit=40)
    recent_row = next(
        r for r in rows if str(r[1]) == "recentfile" and str(r[0]) == str(old)
    )
    assert recent_row[3] == f"section={tmp_path} | {tmp_path} | existing file"


def test_command_palette_recent_file_row_keeps_missing_file_truth_for_deleted_recent_file(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    old = tmp_path / "old.md"
    old.write_text("old\n", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-list true")

    ed.open_file(str(old))
    assert ed.exec_command_line("close")
    old.unlink()

    rows = ed.command_palette_apropos_rows("old", limit=40)
    recent_row = next(
        r for r in rows if str(r[1]) == "recentfile" and str(r[0]) == str(old)
    )
    assert recent_row[3] == f"section={tmp_path} | {tmp_path} | new file | empty buffer @ 1:0"



def test_command_palette_recent_file_row_keeps_missing_file_truth_for_unsaved_open_buffer(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-list true")

    scratch = tmp_path / "scratch.md"
    ed.open_file(str(scratch))

    rows = ed.command_palette_apropos_rows("scratch", limit=40)
    recent_row = next(
        r for r in rows if str(r[1]) == "recentfile" and str(r[0]) == str(scratch)
    )
    assert recent_row[3] == f"section={tmp_path} | {tmp_path} | new file | current buffer"



def test_command_palette_parsecursor_deleted_recent_file_completion_row_keeps_new_file_truth(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    old = tmp_path / "old.md"
    old.write_text("old\n", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-list true")
    assert ed.exec_command_line("set parsecursor true")

    ed.open_file(str(old))
    assert ed.exec_command_line("close")
    old.unlink()

    rows = ed.command_palette_apropos_rows("ol:3", limit=80)
    file_row = next(
        r for r in rows if str(r[1]) == "openpath" and str(r[0]) == "old.md:3" and str(r[2]) == "file"
    )
    assert file_row[3] == f"recent #1 | {tmp_path} | new file | empty buffer @ 1:0"

    ed.enter_command_palette("ol:3")
    assert ed.prompt is not None and ed.prompt.kind == "palette"
    idx = next(
        i
        for i, row in enumerate(ed.prompt.suggestion_rows)
        if len(row) >= 3 and str(row[0]) == "old.md:3" and str(row[1]) == "openpath" and str(row[2]) == "file"
    )
    ed.prompt.suggest_index = idx

    assert ed.submit_prompt() is True
    assert ed.messages[-1] == "opened: old.md @ 1:0"
    assert ed.primary_cursor() == Cursor(0, 0)


def test_command_palette_parsecursor_relative_file_query_still_gets_typed_open_row(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-list true")
    assert ed.exec_command_line("set parsecursor true")

    rows = ed.command_palette_apropos_rows("draft.md:3:7", limit=80)
    open_row = next(
        r for r in rows if str(r[1]) == "openpath" and str(r[0]) == "draft.md:3:7" and str(r[2]) == "open"
    )
    assert open_row[3] == f"new file | {tmp_path} | empty buffer @ 1:0"

    ed.enter_command_palette("draft.md:3:7")
    assert ed.prompt is not None and ed.prompt.kind == "palette"
    idx = next(
        i
        for i, row in enumerate(ed.prompt.suggestion_rows)
        if len(row) >= 3 and str(row[0]) == "draft.md:3:7" and str(row[1]) == "openpath" and str(row[2]) == "open"
    )
    ed.prompt.suggest_index = idx

    assert ed.submit_prompt() is True
    assert ed.messages[-1] == "opened: draft.md @ 1:0"
    assert ed.primary_cursor() == Cursor(0, 0)


def test_command_palette_parsecursor_path_completions_keep_cursor_suffix_and_submit_target(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    guide = tmp_path / "guide"
    guide.mkdir()
    intro = guide / "intro.md"
    intro.write_text("intro\nnext\nthird\n", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-list true")
    assert ed.exec_command_line("set parsecursor true")

    rows = ed.command_palette_apropos_rows("guide/i:2", limit=80)
    file_row = next(
        r for r in rows if str(r[1]) == "openpath" and str(r[0]) == "guide/intro.md:2" and str(r[2]) == "file"
    )
    assert file_row[3] == str(tmp_path / "guide") + " | cursor 2:0"

    rows = ed.command_palette_apropos_rows("guide/intro.md:2", limit=80)
    open_row = next(
        r for r in rows if str(r[1]) == "openpath" and str(r[0]) == "guide/intro.md:2" and str(r[2]) == "open"
    )
    assert open_row[3] == "existing file | " + str(tmp_path / "guide") + " | cursor 2:0"

    ed.enter_command_palette("guide/i:2")
    assert ed.prompt is not None and ed.prompt.kind == "palette"
    idx = next(
        i
        for i, row in enumerate(ed.prompt.suggestion_rows)
        if len(row) >= 3 and str(row[0]) == "guide/intro.md:2" and str(row[1]) == "openpath" and str(row[2]) == "file"
    )
    ed.prompt.suggest_index = idx

    assert ed.submit_prompt() is True
    assert ed.messages[-1].endswith("guide/intro.md @ 2:0")
    assert ed.primary_cursor() == Cursor(1, 0)


def test_command_palette_parsecursor_open_row_keeps_exact_goto_cue_for_open_buffer(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    guide = tmp_path / "guide"
    guide.mkdir()
    intro = guide / "intro.md"
    intro.write_text("intro\nnext\nthird\n", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-list true")
    assert ed.exec_command_line("set parsecursor true")

    ed.open_file(str(intro))
    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    eb.cursors[eb.primary] = eb.buf.clamp(Cursor(1, 1))
    eb.buf.dirty = True

    rows = ed.command_palette_apropos_rows("guide/intro.md:1:0", limit=80)
    open_row = next(
        r for r in rows if str(r[1]) == "openpath" and str(r[0]) == "guide/intro.md:1:0" and str(r[2]) == "open"
    )
    assert open_row[3] == "recent #1 [active, dirty] @ 2:1 | guide/intro.md | existing file | current buffer | goto 1:0"

    ed.enter_command_palette("guide/intro.md:1:0")
    assert ed.prompt is not None and ed.prompt.kind == "palette"
    idx = next(
        i
        for i, row in enumerate(ed.prompt.suggestion_rows)
        if len(row) >= 3 and str(row[0]) == "guide/intro.md:1:0" and str(row[1]) == "openpath" and str(row[2]) == "open"
    )
    ed.prompt.suggest_index = idx

    assert ed.submit_prompt() is True
    assert ed.messages[-1].endswith("guide/intro.md @ 1:0")


def test_command_palette_parsecursor_directory_open_row_still_drills_down(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    guide = tmp_path / "guide"
    guide.mkdir()
    (guide / "intro.md").write_text("intro\n", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-list true")
    assert ed.exec_command_line("set parsecursor true")

    rows = ed.command_palette_apropos_rows("guide/:2", limit=80)
    open_row = next(r for r in rows if str(r[1]) == "openpath" and str(r[0]) == "guide/:2" and str(r[2]) == "open")
    assert open_row[3] == "directory | drill down"

    ed.enter_command_palette("guide/:2")
    assert ed.prompt is not None and ed.prompt.kind == "palette"
    idx = next(
        i
        for i, row in enumerate(ed.prompt.suggestion_rows)
        if len(row) >= 3 and str(row[0]) == "guide/:2" and str(row[1]) == "openpath" and str(row[2]) == "open"
    )
    ed.prompt.suggest_index = idx

    assert ed.submit_prompt() is True
    assert ed.prompt is not None and ed.prompt.kind == "palette"
    assert str(ed.prompt.text) == "guide/"


def test_command_palette_parsecursor_partial_directory_query_keeps_completion_row_and_drills_down(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    guide = tmp_path / "guide"
    guide.mkdir()
    sub = guide / "sub"
    sub.mkdir()
    (sub / "note.md").write_text("note\n", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-list true")
    assert ed.exec_command_line("set parsecursor true")

    rows = ed.command_palette_apropos_rows("guide/s:2", limit=80)
    dir_row = next(
        r for r in rows if str(r[1]) == "openpath" and str(r[0]) == "guide/sub/:2" and str(r[2]) == "dir"
    )
    assert dir_row[3] == str(tmp_path / "guide") + " | drill down"

    ed.enter_command_palette("guide/s:2")
    assert ed.prompt is not None and ed.prompt.kind == "palette"
    idx = next(
        i
        for i, row in enumerate(ed.prompt.suggestion_rows)
        if len(row) >= 3 and str(row[0]) == "guide/sub/:2" and str(row[1]) == "openpath" and str(row[2]) == "dir"
    )
    ed.prompt.suggest_index = idx

    assert ed.submit_prompt() is True
    assert ed.prompt is not None and ed.prompt.kind == "palette"
    assert str(ed.prompt.text) == "guide/sub/"


def test_command_palette_openpath_submit_reports_landed_target(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    p = tmp_path / "doc.txt"
    p.write_text("x\n", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-list true")

    ed.enter_command_palette("./doc")
    assert ed.prompt is not None
    assert ed.prompt.kind == "palette"
    idx = next(
        i for i, row in enumerate(ed.prompt.suggestion_rows) if len(row) >= 2 and str(row[1]) == "openpath" and str(row[0]) == "./doc.txt"
    )
    ed.prompt.suggest_index = idx

    assert ed.submit_prompt() is True
    assert ed.cur().buf.path == 'doc.txt'
    assert ed.messages[-1] == 'opened: doc.txt @ 1:0'
