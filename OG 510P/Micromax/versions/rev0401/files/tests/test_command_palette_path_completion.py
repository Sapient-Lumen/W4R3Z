from __future__ import annotations

from micromax_editor.editor import Editor
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
