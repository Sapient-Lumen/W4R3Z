from __future__ import annotations

from pathlib import Path as _Path

from micromax_editor.buffer import Cursor
from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _call_ed_command(ed: Editor, cmdline: str) -> int:
    vm = ed.vm
    vm.stack.append(str(cmdline))
    vm.stack.append("ed.command")
    vm.eval("hostcall")
    return int(vm.stack.pop())


def _call_ed_prompt_submit(ed: Editor) -> int:
    vm = ed.vm
    vm.stack.append("ed.prompt-submit")
    vm.eval("hostcall")
    return int(vm.stack.pop())


def test_scripted_ed_command_cannot_bypass_cap_fs_open(tmp_path) -> None:
    p = tmp_path / "a.txt"
    p.write_text("hello\n", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)

    # Scripts can execute commands via `ed.command`, but filesystem authority
    # should still be capability-gated.
    ok = _call_ed_command(ed, f"open {p}")
    assert ok == 0

    assert ed.exec_command_line("set cap.fs-open true")
    ok = _call_ed_command(ed, f"open {p}")
    assert ok == 1
    assert ed.cur().buf.path and _Path(ed.cur().buf.path).resolve() == p.resolve()


def test_scripted_ed_command_open_respects_cap_fs_root(tmp_path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    inside = root / "in.txt"
    inside.write_text("in", encoding="utf-8")

    outside = tmp_path / "out.txt"
    outside.write_text("out", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-open true")
    assert ed.exec_command_line(f"set cap.fs-root {root}")

    ok = _call_ed_command(ed, "open in.txt")
    assert ok == 1

    ok = _call_ed_command(ed, f"open {outside}")
    assert ok == 0


def test_scripted_ed_command_save_is_capability_gated(tmp_path) -> None:
    p = tmp_path / "a.txt"
    p.write_text("orig", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*x*", "changed", path=str(p))
    ed.cur().buf.dirty = True

    ok = _call_ed_command(ed, "save")
    assert ok == 0
    assert p.read_text(encoding="utf-8") == "orig"

    assert ed.exec_command_line("set cap.fs-save true")
    ok = _call_ed_command(ed, "save")
    assert ok == 1
    assert p.read_text(encoding="utf-8") == "changed"


def test_scripted_prompt_submit_cannot_bypass_cap_fs_open(tmp_path) -> None:
    p = tmp_path / "a.txt"
    p.write_text("hello\n", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)

    ed.enter_prompt("command", prefill=f"open {p}")
    ok = _call_ed_prompt_submit(ed)
    assert ok == 0

    assert ed.exec_command_line("set cap.fs-open true")
    ed.enter_prompt("command", prefill=f"open {p}")
    ok = _call_ed_prompt_submit(ed)
    assert ok == 1


def _call_ed_command_palette(ed: Editor, query: str) -> None:
    vm = ed.vm
    vm.stack.append(str(query))
    vm.stack.append("ed.command-palette")
    vm.eval("hostcall")


def test_scripted_palette_submit_cannot_bypass_cap_fs_open(tmp_path) -> None:
    p = tmp_path / "a.txt"
    p.write_text("hello\n", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)

    _call_ed_command_palette(ed, str(p))
    assert ed.prompt is not None
    assert ed.prompt.kind == "palette"

    # Force selection to an openpath row for determinism.
    idx = next(
        i for i, row in enumerate(ed.prompt.suggestion_rows) if len(row) >= 2 and str(row[1]) == "openpath"
    )
    ed.prompt.suggest_index = int(idx)

    ok = _call_ed_prompt_submit(ed)
    assert ok == 0

    assert ed.exec_command_line("set cap.fs-open true")
    _call_ed_command_palette(ed, str(p))
    idx = next(
        i for i, row in enumerate(ed.prompt.suggestion_rows) if len(row) >= 2 and str(row[1]) == "openpath"
    )
    ed.prompt.suggest_index = int(idx)

    ok = _call_ed_prompt_submit(ed)
    assert ok == 1
    assert ed.cur().buf.path and _Path(ed.cur().buf.path).resolve() == p.resolve()


def test_scripted_palette_open_respects_cap_fs_root(tmp_path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    inside = root / "in.txt"
    inside.write_text("in", encoding="utf-8")

    outside = tmp_path / "out.txt"
    outside.write_text("out", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-open true")
    assert ed.exec_command_line(f"set cap.fs-root {root}")

    _call_ed_command_palette(ed, "./in.txt")
    idx = next(
        i for i, row in enumerate(ed.prompt.suggestion_rows) if len(row) >= 2 and str(row[1]) == "openpath"
    )
    ed.prompt.suggest_index = int(idx)
    ok = _call_ed_prompt_submit(ed)
    assert ok == 1

    _call_ed_command_palette(ed, str(outside))
    idx = next(
        i for i, row in enumerate(ed.prompt.suggestion_rows) if len(row) >= 2 and str(row[1]) == "openpath"
    )
    ed.prompt.suggest_index = int(idx)
    ok = _call_ed_prompt_submit(ed)
    assert ok == 0


def test_scripted_ed_command_open_preserves_parsecursor_suffix(tmp_path) -> None:
    p = tmp_path / 'a.txt'
    p.write_text('alpha\nbeta\ngamma\n', encoding='utf-8')

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line('set cap.fs-open true')
    assert ed.exec_command_line('set parsecursor true')

    ok = _call_ed_command(ed, f'open {p}:2:2')
    assert ok == 1
    assert ed.primary_cursor() == Cursor(1, 2)
    assert ed.status_model()['last_message'] == f'opened: {p} @ 2:2'
