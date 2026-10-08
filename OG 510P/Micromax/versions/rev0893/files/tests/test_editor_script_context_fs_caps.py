from __future__ import annotations

from pathlib import Path as _Path

import pytest

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
    assert ok == 0
    assert any("cap.prompt-write" in str(msg) for msg in ed.messages)

    assert ed.exec_command_line("set cap.prompt-write true")
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


def test_scripted_save_anchors_relative_buffer_path_under_cap_fs_root(tmp_path, monkeypatch) -> None:
    root = tmp_path / "root"
    root.mkdir()
    inside = root / "in.txt"
    inside.write_text("inside", encoding="utf-8")
    outside = tmp_path / "in.txt"
    outside.write_text("outside", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-save true")
    assert ed.exec_command_line(f"set cap.fs-root {root}")
    ed.new_buffer("relative", "changed", path="in.txt")
    ed.cur().buf.dirty = True

    ok = _call_ed_command(ed, "save")

    assert ok == 1
    assert inside.read_text(encoding="utf-8") == "changed"
    assert outside.read_text(encoding="utf-8") == "outside"
    assert ed.cur().buf.path and _Path(ed.cur().buf.path).resolve() == inside.resolve()


def test_scripted_save_rechecks_cap_root_after_late_symlink_swap(tmp_path, monkeypatch) -> None:
    from micromax_editor import editor as editor_mod

    root = tmp_path / "root"
    root.mkdir()
    inside = root / "inside.txt"
    inside.write_text("inside", encoding="utf-8")
    outside = tmp_path / "outside.txt"
    outside.write_text("outside", encoding="utf-8")
    link = root / "link.txt"
    try:
        link.symlink_to(inside)
    except (OSError, NotImplementedError) as e:
        pytest.skip(f"symlink unavailable: {e}")
    monkeypatch.chdir(tmp_path)

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-save true")
    assert ed.exec_command_line(f"set cap.fs-root {root}")
    ed.new_buffer("relative-link", "changed", path="link.txt")
    ed.cur().buf.dirty = True

    original_write = editor_mod.write_file_bytes
    swapped = {"done": False}

    def swap_then_write(path, payload, **kwargs):  # type: ignore[no-untyped-def]
        if not swapped["done"]:
            swapped["done"] = True
            link.unlink()
            link.symlink_to(outside)
        return original_write(path, payload, **kwargs)

    monkeypatch.setattr(editor_mod, "write_file_bytes", swap_then_write)

    ok = _call_ed_command(ed, "save")

    assert ok == 0
    assert swapped["done"] is True
    assert link.is_symlink()
    assert inside.read_text(encoding="utf-8") == "inside"
    assert outside.read_text(encoding="utf-8") == "outside"
    assert ed.cur().buf.get_text() == "changed"
    assert ed.cur().buf.dirty is True
    assert any("outside containment root" in msg for msg in ed.messages)


def test_legacy_ed_save_hostcall_anchors_relative_buffer_path_under_cap_fs_root(tmp_path, monkeypatch) -> None:
    root = tmp_path / "root"
    root.mkdir()
    inside = root / "hostcall.txt"
    inside.write_text("inside", encoding="utf-8")
    outside = tmp_path / "hostcall.txt"
    outside.write_text("outside", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-save true")
    assert ed.exec_command_line(f"set cap.fs-root {root}")
    ed.new_buffer("relative-hostcall", "changed", path="hostcall.txt")
    ed.cur().buf.dirty = True

    vm = ed.vm
    vm.stack.append("ed.save")
    vm.eval("hostcall")
    err = str(vm.stack.pop())
    ok = int(vm.stack.pop())

    assert ok == 1
    assert err == ""
    assert inside.read_text(encoding="utf-8") == "changed"
    assert outside.read_text(encoding="utf-8") == "outside"
    assert ed.cur().buf.path and _Path(ed.cur().buf.path).resolve() == inside.resolve()


def _call_disk_state(ed: Editor) -> dict[str, object]:
    vm = ed.vm
    vm.stack.append("ed.disk-state")
    vm.eval("hostcall")
    state = vm.stack.pop()
    assert isinstance(state, dict)
    return state


def test_structured_disk_state_is_cap_stat_gated_for_path_backed_buffers(tmp_path) -> None:
    p = tmp_path / "state.txt"
    p.write_text("base", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.open_file(str(p)) is True

    state = _call_disk_state(ed)

    assert state["disk_state"] == "unauthorized"
    assert state["disk_warning"] == 1
    assert "cap.fs-stat" in str(state["disk_error"])

    assert ed.exec_command_line("set cap.fs-stat true")
    state = _call_disk_state(ed)
    assert state["disk_state"] == "fresh"
    assert state["disk_error"] == ""


def test_structured_disk_state_anchors_relative_buffer_path_under_cap_fs_root(tmp_path, monkeypatch) -> None:
    root = tmp_path / "root"
    root.mkdir()
    inside = root / "state.txt"
    inside.write_text("inside", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-stat true")
    assert ed.exec_command_line(f"set cap.fs-root {root}")
    ed.new_buffer("relative-state", "buffer", path="state.txt")

    state = _call_disk_state(ed)

    # If the hostcall statted process cwd by accident, this relative path would
    # look like a missing/new file.  Scripts should see the cap-root anchored
    # target instead, with no stale raw-path witness applied to the wrong file.
    assert state["disk_state"] == "untracked"
    assert state["disk_warning"] == 0


def test_structured_disk_state_denies_paths_outside_cap_fs_root_without_statting(tmp_path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("outside", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-stat true")
    assert ed.exec_command_line(f"set cap.fs-root {root}")
    ed.new_buffer("outside-state", "buffer", path=str(outside))

    state = _call_disk_state(ed)

    assert state["disk_state"] == "unauthorized"
    assert state["disk_warning"] == 1
    assert "outside cap.fs-root" in str(state["disk_error"])


def _call_disk_states(ed: Editor, include_all: int = 0) -> list[list[object]]:
    vm = ed.vm
    vm.stack.append(int(include_all))
    vm.stack.append("ed.disk-states")
    vm.eval("hostcall")
    rows = vm.stack.pop()
    assert isinstance(rows, list)
    return [list(row) for row in rows]


def test_structured_disk_states_rows_are_cap_stat_gated(tmp_path) -> None:
    p = tmp_path / "states.txt"
    p.write_text("base", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    ed.vm.eval('"ed.disk-states" host.feature?')
    assert int(ed.vm.stack.pop()) == 1
    assert ed.open_file(str(p)) is True

    rows = _call_disk_states(ed, 1)

    assert len(rows) == 1
    assert rows[0][0] == str(p)
    assert rows[0][1] == "unauthorized"
    assert rows[0][2] == 1
    assert "cap.fs-stat" in str(rows[0][8])

    assert ed.exec_command_line("set cap.fs-stat true")
    rows = _call_disk_states(ed, 1)
    assert rows[0][1] == "fresh"
    assert rows[0][2] == 0


def test_scripted_diskstate_command_uses_cap_stat_boundary(tmp_path) -> None:
    p = tmp_path / "cmd-state.txt"
    p.write_text("base", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.open_file(str(p)) is True
    p.write_text("changed", encoding="utf-8")

    ok = _call_ed_command(ed, "diskstate --all")

    assert ok == 1
    assert any("unauthorized" in msg and "cap.fs-stat" in msg for msg in ed.messages)
    assert not any("changed" in msg for msg in ed.messages if "diskstate:" in msg and "unauthorized" not in msg)

    ed.messages.clear()
    assert ed.exec_command_line("set cap.fs-stat true")
    ok = _call_ed_command(ed, "diskstate")

    assert ok == 1
    assert any("changed" in msg for msg in ed.messages if "diskstate:" in msg)


def test_scripted_diskstate_command_respects_cap_fs_root_for_relative_buffers(tmp_path, monkeypatch) -> None:
    root = tmp_path / "root"
    root.mkdir()
    inside = root / "rel-state.txt"
    inside.write_text("inside", encoding="utf-8")
    outside = tmp_path / "rel-state.txt"
    outside.write_text("outside", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-stat true")
    assert ed.exec_command_line(f"set cap.fs-root {root}")
    ed.new_buffer("relative-diskstate", "buffer", path="rel-state.txt")

    ok = _call_ed_command(ed, "diskstate --all")

    assert ok == 1
    joined = "\n".join(ed.messages)
    assert str(inside) in joined or "rel-state.txt" in joined
    assert "untracked" in joined
    assert "changed" not in joined
    assert outside.read_text(encoding="utf-8") == "outside"


def _call_disk_rows(ed: Editor, *, include_all: bool = False) -> list[list[object]]:
    vm = ed.vm
    vm.stack.append(1 if include_all else 0)
    vm.stack.append("ed.disk-rows")
    vm.eval("hostcall")
    rows = vm.stack.pop()
    assert isinstance(rows, list)
    return rows


def test_structured_disk_rows_are_cap_stat_gated_for_path_backed_buffers(tmp_path) -> None:
    p = tmp_path / "row-state.txt"
    p.write_text("base", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.open_file(str(p)) is True

    rows = _call_disk_rows(ed, include_all=True)

    assert len(rows) == 1
    assert rows[0][1] == "unauthorized"
    assert rows[0][2] == 1
    assert "cap.fs-stat" in str(rows[0][8])

    assert ed.exec_command_line("set cap.fs-stat true")
    rows = _call_disk_rows(ed, include_all=True)
    assert len(rows) == 1
    assert rows[0][1] == "fresh"
    assert rows[0][2] == 0


def test_structured_disk_rows_default_to_warning_rows_and_anchor_relative_paths(
    tmp_path, monkeypatch
) -> None:
    root = tmp_path / "root"
    root.mkdir()
    inside = root / "rows.txt"
    inside.write_text("inside", encoding="utf-8")
    cwd_shadow = tmp_path / "rows.txt"
    cwd_shadow.write_text("outside", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-stat true")
    assert ed.exec_command_line(f"set cap.fs-root {root}")
    ed.new_buffer("relative-rows", "buffer", path="rows.txt")

    assert _call_disk_rows(ed, include_all=False) == []
    rows = _call_disk_rows(ed, include_all=True)

    assert len(rows) == 1
    assert rows[0][0] == "relative-rows"
    assert rows[0][1] == "untracked"
    assert rows[0][2] == 0
    assert cwd_shadow.read_text(encoding="utf-8") == "outside"


def test_structured_disk_rows_report_outside_cap_root_as_warning(tmp_path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "rows-outside.txt"
    outside.write_text("outside", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-stat true")
    assert ed.exec_command_line(f"set cap.fs-root {root}")
    ed.new_buffer("outside-rows", "buffer", path=str(outside))

    rows = _call_disk_rows(ed)

    assert len(rows) == 1
    assert rows[0][1] == "unauthorized"
    assert rows[0][2] == 1
    assert "outside cap.fs-root" in str(rows[0][8])


def test_scripted_open_rechecks_cap_root_after_late_symlink_parent_swap(tmp_path, monkeypatch) -> None:
    from micromax_editor import command_dispatcher as command_dispatcher_mod

    root = tmp_path / "root"
    root.mkdir()
    inside_dir = root / "inside"
    inside_dir.mkdir()
    (inside_dir / "secret.txt").write_text("inside", encoding="utf-8")
    outside_dir = tmp_path / "outside"
    outside_dir.mkdir()
    (outside_dir / "secret.txt").write_text("outside", encoding="utf-8")
    link = root / "link"
    try:
        link.symlink_to(inside_dir, target_is_directory=True)
    except (OSError, NotImplementedError) as e:
        pytest.skip(f"symlink unavailable: {e}")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-open true")
    assert ed.exec_command_line(f"set cap.fs-root {root}")

    original = command_dispatcher_mod.checked_sandbox_path
    swapped = {"done": False}

    def swap_after_preflight(ed_arg, raw_path):  # type: ignore[no-untyped-def]
        path = original(ed_arg, raw_path)
        if not swapped["done"]:
            swapped["done"] = True
            link.unlink()
            link.symlink_to(outside_dir, target_is_directory=True)
        return path

    monkeypatch.setattr(command_dispatcher_mod, "checked_sandbox_path", swap_after_preflight)

    ok = _call_ed_command(ed, "open link/secret.txt")

    assert ok == 0
    assert swapped["done"] is True
    if ed.active is not None:
        assert ed.cur().buf.get_text() != "outside"
    assert any("outside containment root" in msg for msg in ed.messages)


def test_ed_open_hostcall_rechecks_cap_root_after_late_symlink_parent_swap(tmp_path, monkeypatch) -> None:
    from micromax_editor import micromax_bridge as micromax_bridge_mod

    root = tmp_path / "root"
    root.mkdir()
    inside_dir = root / "inside"
    inside_dir.mkdir()
    (inside_dir / "secret.txt").write_text("inside", encoding="utf-8")
    outside_dir = tmp_path / "outside"
    outside_dir.mkdir()
    (outside_dir / "secret.txt").write_text("outside", encoding="utf-8")
    link = root / "link"
    try:
        link.symlink_to(inside_dir, target_is_directory=True)
    except (OSError, NotImplementedError) as e:
        pytest.skip(f"symlink unavailable: {e}")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-open true")
    assert ed.exec_command_line(f"set cap.fs-root {root}")

    original = micromax_bridge_mod.checked_sandbox_path
    swapped = {"done": False}

    def swap_after_preflight(ed_arg, raw_path):  # type: ignore[no-untyped-def]
        path = original(ed_arg, raw_path)
        if not swapped["done"]:
            swapped["done"] = True
            link.unlink()
            link.symlink_to(outside_dir, target_is_directory=True)
        return path

    monkeypatch.setattr(micromax_bridge_mod, "checked_sandbox_path", swap_after_preflight)

    vm = ed.vm
    vm.stack.append("link/secret.txt")
    vm.stack.append("ed.open")
    vm.eval("hostcall")
    err = str(vm.stack.pop())
    ok = int(vm.stack.pop())

    assert ok == 0
    assert swapped["done"] is True
    assert "outside containment root" in err
    if ed.active is not None:
        assert ed.cur().buf.get_text() != "outside"


def test_scripted_save_mkparents_does_not_create_dirs_after_parent_symlink_swap(tmp_path, monkeypatch) -> None:
    from micromax_editor import file_write

    root = tmp_path / "root"
    root.mkdir()
    anchor = root / "anchor"
    anchor.mkdir()
    outside_anchor = tmp_path / "outside-anchor"
    outside_anchor.mkdir()

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-save true")
    assert ed.exec_command_line(f"set cap.fs-root {root}")
    assert ed.exec_command_line("set mkparents true")
    ed.new_buffer("relative-parent", "changed", path="anchor/deep/file.txt")
    ed.cur().buf.dirty = True

    original_open_child = file_write._open_child_dir_no_follow
    swapped = {"done": False}

    def swap_before_open_child(parent_fd, name):  # type: ignore[no-untyped-def]
        if str(name) == "anchor" and not swapped["done"]:
            swapped["done"] = True
            anchor.rmdir()
            anchor.symlink_to(outside_anchor, target_is_directory=True)
        return original_open_child(parent_fd, name)

    monkeypatch.setattr(file_write, "_open_child_dir_no_follow", swap_before_open_child)

    ok = _call_ed_command(ed, "save")

    assert ok == 0
    assert swapped["done"] is True
    assert anchor.is_symlink()
    assert not (outside_anchor / "deep").exists()
    assert ed.cur().buf.get_text() == "changed"
    assert ed.cur().buf.dirty is True
    assert any(
        ("outside containment root" in msg)
        or ("Too many levels" in msg)
        or ("Not a directory" in msg)
        or ("not a directory" in msg)
        for msg in ed.messages
    )


def test_scripted_ed_command_cannot_self_enable_capability(tmp_path) -> None:
    p = tmp_path / "a.txt"
    p.write_text("orig", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*x*", "changed", path=str(p))
    ed.cur().buf.dirty = True

    ok = _call_ed_command(ed, "set cap.fs-save true")
    assert ok == 0
    assert bool(ed.options.get("cap.fs-save")) is False
    assert any("script context cannot modify capability option: cap.fs-save" in msg for msg in ed.messages)

    ok = _call_ed_command(ed, "save")
    assert ok == 0
    assert p.read_text(encoding="utf-8") == "orig"


def test_scripted_opt_set_hostcall_cannot_self_enable_capability() -> None:
    from micromax import MicromaxError

    ed = Editor()
    install_editor_hostcalls(ed)

    with ed.script_context():
        ed.vm.stack.append("cap.fs-read")
        ed.vm.stack.append("true")
        ed.vm.stack.append("ed.opt-set")
        with pytest.raises(MicromaxError, match="script context cannot modify capability option: cap.fs-read"):
            ed.vm.eval("hostcall", filename="<test>")

    assert bool(ed.options.get("cap.fs-read")) is False


def test_scripted_toggle_command_cannot_self_enable_capability() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ok = _call_ed_command(ed, "toggle cap.fs-open")

    assert ok == 0
    assert bool(ed.options.get("cap.fs-open")) is False
    assert any("script context cannot modify capability option: cap.fs-open" in msg for msg in ed.messages)


def test_privileged_config_vm_eval_can_still_set_capabilities() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval("set cap.fs-read true", filename="<trusted-init>")

    assert bool(ed.options.get("cap.fs-read")) is True
    ed.vm.eval('"ed.fs-read" host.feature?', filename="<test>")
    assert int(ed.vm.stack.pop()) == 1


def _call_ed_run(ed: Editor, action_spec: str) -> int:
    ed.vm.stack.append(str(action_spec))
    ed.vm.stack.append("ed.run")
    ed.vm.eval("hostcall", filename="<test>")
    return int(ed.vm.stack.pop())


def test_scripted_ed_run_command_cannot_self_enable_capability() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ok = _call_ed_run(ed, "command:set cap.fs-save true")

    assert ok == 0
    assert bool(ed.options.get("cap.fs-save")) is False
    assert any("script context cannot modify capability option: cap.fs-save" in msg for msg in ed.messages)


def test_scripted_ed_run_mx_cannot_self_enable_capability() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ok = _call_ed_run(ed, "mx:set cap.fs-open true")

    assert ok == 0
    assert bool(ed.options.get("cap.fs-open")) is False
    assert any("script context cannot modify capability option: cap.fs-open" in msg for msg in ed.messages)




def _set_macro_via_hostcall(ed: Editor, name: str, steps: list[list[object]]) -> None:
    ed.vm.stack.append(steps)
    ed.vm.stack.append(str(name))
    ed.vm.stack.append("ed.macro-set")
    ed.vm.eval("hostcall", filename="<test>")


def _play_macro_via_hostcall(ed: Editor, name: str, count: int = 1) -> int:
    ed.vm.stack.append(str(name))
    ed.vm.stack.append(int(count))
    ed.vm.stack.append("ed.macro-play")
    ed.vm.eval("hostcall", filename="<test>")
    return int(ed.vm.stack.pop())


def test_scripted_macro_play_hostcall_cannot_replay_capability_grant(tmp_path) -> None:
    p = tmp_path / "macro-save.txt"
    p.write_text("orig", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*x*", "changed", path=str(p))
    ed.cur().buf.dirty = True
    _set_macro_via_hostcall(ed, "grant", [["c", "set cap.fs-save true"]])

    ok = _play_macro_via_hostcall(ed, "grant")

    assert ok == 0
    assert bool(ed.options.get("cap.fs-save")) is False
    assert p.read_text(encoding="utf-8") == "orig"
    assert any("set cap.macro-play true" in msg for msg in ed.messages)


def test_scripted_macro_play_with_macro_cap_still_cannot_self_enable_fs_capability(tmp_path) -> None:
    p = tmp_path / "macro-save.txt"
    p.write_text("orig", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    ed.exec_command_line("set cap.macro-play true")
    ed.new_buffer("*x*", "changed", path=str(p))
    ed.cur().buf.dirty = True
    _set_macro_via_hostcall(ed, "grant", [["c", "set cap.fs-save true"]])

    ok = _play_macro_via_hostcall(ed, "grant")

    assert ok == 0
    assert bool(ed.options.get("cap.fs-save")) is False
    assert p.read_text(encoding="utf-8") == "orig"
    assert any("script context cannot modify capability option: cap.fs-save" in msg for msg in ed.messages)


def test_scripted_macro_play_hostcall_honors_pregranted_capability(tmp_path) -> None:
    p = tmp_path / "macro-save-ok.txt"
    p.write_text("orig", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-save true")
    assert ed.exec_command_line("set cap.macro-play true")
    ed.new_buffer("*x*", "changed", path=str(p))
    ed.cur().buf.dirty = True
    _set_macro_via_hostcall(ed, "saveit", [["c", "save"]])

    ok = _play_macro_via_hostcall(ed, "saveit")

    assert ok == 1
    assert p.read_text(encoding="utf-8") == "changed"


def test_scripted_reload_commands_need_code_load_capability() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ok = _call_ed_command(ed, "reload")
    assert ok == 0
    assert any("reload: disabled for scripts (cap.fs-require)" in msg for msg in ed.messages)

    ed.messages.clear()
    ok = _call_ed_command(ed, "plugin reload core")
    assert ok == 0
    assert any("plugin reload: disabled for scripts (cap.fs-require)" in msg for msg in ed.messages)


def test_scripted_plugin_reload_hostcall_needs_code_load_capability() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    with ed.script_context():
        ed.vm.stack.append("missing")
        ed.vm.stack.append("plugin.reload")
        ed.vm.eval("hostcall", filename="<test>")

    assert int(ed.vm.stack.pop()) == 0
    assert any("plugin reload: disabled for scripts (cap.fs-require)" in msg for msg in ed.messages)


def test_script_registered_keybinding_keeps_script_context_for_command_cap_mutation() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    with ed.script_context():
        ed.vm.eval('"F8" "command:set cap.fs-save true" "ed.bind" hostcall', filename='<script-bind>')

    binding = ed.keymap.get_binding("F8")
    assert binding is not None
    assert binding.script_context is True

    assert ed.dispatch_key("F8") is False
    assert not bool(ed.options.get("cap.fs-save"))
    assert any("cannot modify capability option" in msg for msg in ed.messages)


def test_script_registered_keybinding_keeps_script_context_for_mx_cap_mutation() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    with ed.script_context():
        ed.vm.eval('"F9" "mx:set cap.fs-open true" "ed.bind" hostcall', filename='<script-bind>')

    assert ed.dispatch_key("F9") is False
    assert not bool(ed.options.get("cap.fs-open"))
    assert any("cannot modify capability option" in msg for msg in ed.messages)


def test_command_registered_keybinding_from_script_context_is_lower_authority() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    with ed.script_context():
        assert ed.exec_command_line("bind F10 command:set cap.fs-save true") is True

    assert ed.dispatch_key("F10") is False
    assert not bool(ed.options.get("cap.fs-save"))
    assert any("cannot modify capability option" in msg for msg in ed.messages)


def _bind_key_via_hostcall(ed: Editor, key: str, action_spec: str) -> None:
    ed.vm.stack.append(str(key))
    ed.vm.stack.append(str(action_spec))
    ed.vm.stack.append("ed.bind")
    ed.vm.eval("hostcall", filename="<test>")


def test_script_origin_keybinding_does_not_later_gain_user_authority() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    with ed.script_context():
        _bind_key_via_hostcall(ed, "F9", "command:set cap.fs-save true")

    binding = ed.resolve_key_binding("F9")
    assert binding is not None
    assert bool(getattr(binding, "script_context", False)) is True

    ok = ed.dispatch_key("F9")

    assert ok is False
    assert bool(ed.options.get("cap.fs-save")) is False
    assert any("script context cannot modify capability option: cap.fs-save" in msg for msg in ed.messages)


def test_trusted_keybinding_keeps_interactive_user_authority() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    _bind_key_via_hostcall(ed, "F10", "command:set cap.fs-save true")

    binding = ed.resolve_key_binding("F10")
    assert binding is not None
    assert bool(getattr(binding, "script_context", False)) is False

    assert ed.dispatch_key("F10") is True
    assert bool(ed.options.get("cap.fs-save")) is True


def test_plugin_origin_keybinding_preserves_package_local_load_root(tmp_path) -> None:
    from micromax_editor.vm_load_policy import plugin_load_root_context

    root = tmp_path / "plugin"
    root.mkdir()
    helper = root / "helper.mx"
    helper.write_text('"plugin-key-loaded" "ed.msg" hostcall\n', encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)

    with plugin_load_root_context(ed.vm, root):
        with ed.script_context():
            _bind_key_via_hostcall(ed, "F11", 'mx:"helper.mx" require')

    binding = ed.resolve_key_binding("F11")
    assert binding is not None
    assert bool(getattr(binding, "script_context", False)) is True
    assert str(getattr(binding, "plugin_load_root", ""))
    assert bool(ed.options.get("cap.fs-require")) is False

    assert ed.dispatch_key("F11") is True
    assert ed.messages[-1] == "plugin-key-loaded"


def test_script_keybinding_description_update_preserves_lower_authority() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    with ed.script_context():
        _bind_key_via_hostcall(ed, "F12", "command:set cap.fs-save true")
        ed.vm.stack.append("F12")
        ed.vm.stack.append("grant saver")
        ed.vm.stack.append("ed.bind-doc")
        ed.vm.eval("hostcall", filename="<test>")

    assert int(ed.vm.stack.pop()) == 1
    binding = ed.resolve_key_binding("F12")
    assert binding is not None
    assert binding.desc == "grant saver"
    assert bool(getattr(binding, "script_context", False)) is True

    assert ed.dispatch_key("F12") is False
    assert bool(ed.options.get("cap.fs-save")) is False
    assert any("cannot modify capability option" in msg for msg in ed.messages)


def test_script_origin_macro_set_does_not_later_gain_user_authority() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    with ed.script_context():
        _set_macro_via_hostcall(ed, "grantlater", [["c", "set cap.fs-save true"]])

    steps = ed.get_macro("grantlater")
    assert len(steps) == 1
    assert bool(getattr(steps[0], "script_context", False)) is True

    ok = ed.play_macro("grantlater")

    assert ok is False
    assert bool(ed.options.get("cap.fs-save")) is False
    assert any("script context cannot modify capability option: cap.fs-save" in msg for msg in ed.messages)


def test_scripted_save_bang_requires_force_save_capability(tmp_path) -> None:
    p = tmp_path / "force-save-cap.txt"
    p.write_text("base\n", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-save true")
    assert ed.open_file(str(p)) is True

    ed.cur().buf.set_text("ours\n")
    ed.cur().buf.dirty = True
    p.write_text("theirs\n", encoding="utf-8")

    ok = _call_ed_command(ed, "save!")
    assert ok == 0
    assert p.read_text(encoding="utf-8") == "theirs\n"
    assert any("cap.fs-force-save" in msg for msg in ed.messages)

    assert ed.exec_command_line("set cap.fs-force-save true")
    ok = _call_ed_command(ed, "save!")
    assert ok == 1
    assert p.read_text(encoding="utf-8") == "ours\n"


def test_script_context_cannot_relax_save_external_guard_with_setlocal(tmp_path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*x*", "x", path=str(tmp_path / "x.txt"))

    assert bool(ed.options.get("save.checkexternal", local=ed.cur().local_options)) is True
    ok = _call_ed_command(ed, "setlocal save.checkexternal false")
    assert ok == 0
    assert bool(ed.options.get("save.checkexternal", local=ed.cur().local_options)) is True
    assert any("protected option: save.checkexternal" in msg for msg in ed.messages)

    assert ed.exec_command_line("setlocal save.checkexternal false") is True
    assert bool(ed.options.get("save.checkexternal", local=ed.cur().local_options)) is False


def test_script_context_cannot_relax_save_external_guard_via_vm_words() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    with pytest.raises(Exception) as err:
        with ed.script_context():
            ed.vm.eval('set save.checkexternal false', filename="<script-opt>")
    assert "protected option: save.checkexternal" in str(err.value)
    assert bool(ed.options.get("save.checkexternal")) is True


def test_script_context_cannot_seed_external_clipboard_backend_for_later_user() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ok = _call_ed_command(ed, "set clipboard external")
    assert ok == 0
    assert ed.options.get("clipboard") == "internal"
    assert any("protected option: clipboard" in msg for msg in ed.messages)

    ok = _call_ed_command(ed, "set clipboard.external.cmd /tmp/evil-copy")
    assert ok == 0
    assert ed.options.get("clipboard.external.cmd") == ""
    assert any("protected option: clipboard.external.cmd" in msg for msg in ed.messages)

    assert ed.exec_command_line("set clipboard external") is True
    assert ed.options.get("clipboard") == "external"
    assert ed.exec_command_line("set clipboard.external.cmd /tmp/user-copy") is True
    assert ed.options.get("clipboard.external.cmd") == "/tmp/user-copy"


def test_script_context_cannot_redirect_persistence_options_or_aliases(tmp_path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    target = tmp_path / "history.json"

    ok = _call_ed_command(ed, f"set history.file {target}")
    assert ok == 0
    assert ed.options.get("history.file") != str(target)
    assert any("protected option: history.file" in msg for msg in ed.messages)

    ok = _call_ed_command(ed, "toggle savehistory")
    assert ok == 0
    assert bool(ed.options.get("history.persist")) is False
    assert any("protected option: history.persist" in msg for msg in ed.messages)

    assert ed.exec_command_line(f"set history.file {target}") is True
    assert ed.options.get("history.file") == str(target)
    assert ed.exec_command_line("toggle savehistory") is True
    assert bool(ed.options.get("history.persist")) is True


def test_script_context_cannot_lower_external_url_and_save_policy_options() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    checks = [
        ("set open-url.confirm false", "open-url.confirm", True),
        ("set save.atomic false", "save.atomic", True),
        ("set mkparents true", "mkparents", False),
        ("set readonly true", "readonly", False),
        ("set autosave 5", "autosave", 0),
    ]
    for cmdline, opt, default in checks:
        ed.messages.clear()
        ok = _call_ed_command(ed, cmdline)
        assert ok == 0
        assert ed.options.get(opt) == default
        assert any(f"protected option: {opt}" in msg for msg in ed.messages)

    assert ed.exec_command_line("set open-url.confirm false") is True
    assert ed.options.get("open-url.confirm") is False
    assert ed.exec_command_line("set save.atomic false") is True
    assert ed.options.get("save.atomic") is False
    assert ed.exec_command_line("set mkparents true") is True
    assert ed.options.get("mkparents") is True


def test_script_context_can_still_mutate_plain_editor_options() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ok = _call_ed_command(ed, "set ignorecase false")
    assert ok == 1
    assert ed.options.get("ignorecase") is False


def test_script_context_cannot_enable_autosave_as_delayed_save_bypass() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    with ed.script_context():
        ok = ed.exec_command_line("set autosave 1")

    assert ok is False
    assert int(ed.options.get("autosave")) == 0
    assert any("cannot modify protected option: autosave" in msg for msg in ed.messages)


def test_script_context_cannot_disable_save_external_freshness_guard() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    with ed.script_context():
        ok = ed.exec_command_line("set save.checkexternal false")

    assert ok is False
    assert bool(ed.options.get("save.checkexternal")) is True
    assert any("cannot modify protected option: save.checkexternal" in msg for msg in ed.messages)


def test_script_context_cannot_clear_readonly_before_later_edit() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("scratch", "")
    assert ed.exec_command_line("setlocal readonly true") is True

    with ed.script_context():
        ok = ed.exec_command_line("setlocal readonly false")

    assert ok is False
    assert bool(ed.options.get("readonly", local=ed.cur().local_options)) is True
    assert any("cannot modify protected option: readonly" in msg for msg in ed.messages)


def test_script_dirty_buffer_is_not_autosaved_without_save_cap_even_when_user_enabled_autosave(tmp_path) -> None:
    p = tmp_path / "auto-script.txt"
    p.write_text("hello\n", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line(f"open {p}") is True
    assert ed.exec_command_line("set autosave 1") is True

    with ed.script_context():
        ed.input["text"] = "!"
        assert ed.run_action("EndOfLine") is True
        assert ed.run_action("InsertText") is True

    assert ed.cur().buf.dirty is True
    assert bool(getattr(ed.cur(), "script_dirty_since_sync", False)) is True

    assert ed.autosave_dirty_buffers(immediate=True) == []
    assert p.read_text(encoding="utf-8") == "hello\n"
    assert ed.cur().buf.dirty is True
    assert bool(getattr(ed.cur(), "script_dirty_since_sync", False)) is True

    assert ed.exec_command_line("set cap.fs-save true") is True
    assert ed.autosave_dirty_buffers(immediate=True) == [str(p)]
    assert p.read_text(encoding="utf-8") == "hello!\n"
    assert ed.cur().buf.dirty is False
    assert bool(getattr(ed.cur(), "script_dirty_since_sync", False)) is False


def test_direct_script_text_hostcall_taints_buffer_for_autosave(tmp_path) -> None:
    p = tmp_path / "hostcall-taint.txt"
    p.write_text("old", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line(f"open {p}") is True
    assert ed.exec_command_line("set autosave 1") is True

    with ed.script_context():
        ed.vm.stack.append("new")
        ed.vm.stack.append("ed.set-text")
        ed.vm.eval("hostcall", filename="<script>")

    assert ed.cur().buf.get_text() == "new"
    assert ed.cur().buf.dirty is True
    assert bool(getattr(ed.cur(), "script_dirty_since_sync", False)) is True
    assert ed.autosave_dirty_buffers(immediate=True) == []
    assert p.read_text(encoding="utf-8") == "old"


def test_scripted_close_bang_requires_buffer_discard_capability() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("notes", "unsaved")
    ed.cur().buf.dirty = True

    ok = _call_ed_command(ed, "close!")
    assert ok == 0
    assert "notes" in ed.buffers
    assert any("cap.buffer-discard" in msg for msg in ed.messages)

    assert ed.exec_command_line("set cap.buffer-discard true") is True
    ok = _call_ed_command(ed, "close!")
    assert ok == 1
    assert "notes" not in ed.buffers


def test_scripted_quit_bang_requires_buffer_discard_capability() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("dirty", "unsaved")
    ed.cur().buf.dirty = True

    ok = _call_ed_command(ed, "quit!")
    assert ok == 0
    assert ed.should_quit is False
    assert any("cap.buffer-discard" in msg for msg in ed.messages)

    assert ed.exec_command_line("set cap.buffer-discard true") is True
    ok = _call_ed_command(ed, "quit!")
    assert ok == 1
    assert ed.should_quit is True


def test_scripted_revert_bang_requires_buffer_discard_capability(tmp_path) -> None:
    p = tmp_path / "revert-discard.txt"
    p.write_text("disk\n", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-open true") is True
    assert ed.open_file(str(p)) is True
    ed.cur().buf.set_text("local\n")
    ed.cur().buf.dirty = True

    ok = _call_ed_command(ed, "revert!")
    assert ok == 0
    assert ed.cur().buf.get_text() == "local\n"
    assert ed.cur().buf.dirty is True
    assert any("cap.buffer-discard" in msg for msg in ed.messages)

    assert ed.exec_command_line("set cap.buffer-discard true") is True
    ok = _call_ed_command(ed, "revert!")
    assert ok == 1
    assert ed.cur().buf.get_text() == "disk\n"
    assert ed.cur().buf.dirty is False


def test_scripted_closeall_and_only_require_buffer_discard_capability() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("keep", "clean")
    ed.new_buffer("dirty", "unsaved")
    ed.cur().buf.dirty = True
    ed.switch_buffer("keep")

    ok = _call_ed_command(ed, "only!")
    assert ok == 0
    assert "dirty" in ed.buffers
    assert any("cap.buffer-discard" in msg for msg in ed.messages)

    ed.messages.clear()
    ok = _call_ed_command(ed, "closeall!")
    assert ok == 0
    assert "dirty" in ed.buffers
    assert any("cap.buffer-discard" in msg for msg in ed.messages)

    assert ed.exec_command_line("set cap.buffer-discard true") is True
    ok = _call_ed_command(ed, "only!")
    assert ok == 1
    assert "keep" in ed.buffers
    assert "dirty" not in ed.buffers


def test_scripted_cd_requires_cap_fs_chdir(tmp_path, monkeypatch) -> None:
    root = tmp_path / "root"
    root.mkdir()
    monkeypatch.chdir(tmp_path)

    ed = Editor()
    install_editor_hostcalls(ed)

    ok = _call_ed_command(ed, f"cd {root}")
    assert ok == 0
    assert _Path.cwd().resolve() == tmp_path.resolve()
    assert any("cap.fs-chdir" in msg for msg in ed.messages)

    assert ed.exec_command_line("set cap.fs-chdir true") is True
    ok = _call_ed_command(ed, f"cd {root}")
    assert ok == 1
    assert _Path.cwd().resolve() == root.resolve()
    ed.vm.eval('"ed.chdir" host.feature?', filename="<test>")
    assert int(ed.vm.stack.pop()) == 1


def test_scripted_cd_respects_cap_fs_root_for_relative_and_absolute_paths(tmp_path, monkeypatch) -> None:
    root = tmp_path / "root"
    inside = root / "sub"
    outside = tmp_path / "outside"
    inside.mkdir(parents=True)
    outside.mkdir()
    monkeypatch.chdir(tmp_path)

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-chdir true") is True
    assert ed.exec_command_line(f"set cap.fs-root {root}") is True

    ok = _call_ed_command(ed, "cd sub")
    assert ok == 1
    assert _Path.cwd().resolve() == inside.resolve()

    ok = _call_ed_command(ed, f"cd {outside}")
    assert ok == 0
    assert _Path.cwd().resolve() == inside.resolve()
    assert any("outside cap.fs-root" in msg for msg in ed.messages)


def test_scripted_ed_run_command_cd_uses_script_chdir_capability(tmp_path, monkeypatch) -> None:
    root = tmp_path / "root"
    root.mkdir()
    monkeypatch.chdir(tmp_path)

    ed = Editor()
    install_editor_hostcalls(ed)

    ok = _call_ed_run(ed, f"command:cd {root}")
    assert ok == 0
    assert _Path.cwd().resolve() == tmp_path.resolve()
    assert any("cap.fs-chdir" in msg for msg in ed.messages)


def _call_hostcall(ed: Editor, name: str, *args: object) -> object:
    ed.vm.stack.clear()
    for arg in args:
        ed.vm.stack.append(arg)
    ed.vm.stack.append(str(name))
    ed.vm.eval("hostcall", filename="<test-hostcall>")
    return ed.vm.stack[-1] if ed.vm.stack else None


def test_script_created_command_prompt_submits_later_under_script_authority() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    _call_hostcall(ed, "ed.command-edit", "set cap.fs-open true")
    assert ed.prompt is not None
    assert ed.prompt.kind == "command"
    assert bool(getattr(ed.prompt, "script_context", False)) is True

    # Simulate a later user Enter key rather than the ed.prompt-submit hostcall.
    assert ed.submit_prompt() is False
    assert bool(ed.options.get("cap.fs-open")) is False
    assert any("cap.fs-open" in str(msg) for msg in ed.messages)


def test_script_prompt_set_taints_existing_prompt_before_later_submit() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("main", "alpha\n")

    ed.enter_prompt("command", prefill="showstatus")
    assert ed.prompt is not None
    assert bool(getattr(ed.prompt, "script_context", False)) is False

    _call_hostcall(ed, "ed.prompt-set", "set cap.fs-save true")
    assert ed.prompt is not None
    assert bool(getattr(ed.prompt, "script_context", False)) is True

    assert ed.submit_prompt() is False
    assert bool(ed.options.get("cap.fs-save")) is False
    assert any("cap.fs-save" in str(msg) for msg in ed.messages)


def test_script_created_palette_prompt_cannot_later_open_path_without_cap(tmp_path) -> None:
    p = tmp_path / "later.txt"
    p.write_text("hello", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-list true") is True

    _call_hostcall(ed, "ed.command-palette", str(p))
    assert ed.prompt is not None
    assert ed.prompt.kind == "palette"
    assert bool(getattr(ed.prompt, "script_context", False)) is True
    idx = next(
        i for i, row in enumerate(ed.prompt.suggestion_rows) if len(row) >= 2 and str(row[1]) == "openpath"
    )
    ed.prompt.suggest_index = int(idx)

    # A later direct submit must keep the prompt's script origin; otherwise this
    # would become an unrestricted interactive open.
    assert ed.submit_prompt() is False
    assert not any(
        eb.buf.path and _Path(eb.buf.path).resolve() == p.resolve()
        for eb in ed.buffers.values()
    )
    assert any("cap.fs-open" in str(msg) for msg in ed.messages)


def test_script_prompt_completion_taints_existing_command_prompt_before_submit() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.enter_prompt("command", prefill="set cap.fs-open tr")
    assert ed.prompt is not None
    assert bool(getattr(ed.prompt, "script_context", False)) is False

    _call_hostcall(ed, "ed.prompt-complete", 1)
    assert ed.prompt is not None
    assert ed.prompt.text.strip() == "set cap.fs-open true"
    assert bool(getattr(ed.prompt, "script_context", False)) is True

    assert ed.submit_prompt() is False
    assert bool(ed.options.get("cap.fs-open")) is False
    assert any("cap.fs-open" in str(msg) for msg in ed.messages)


def test_script_created_command_prompt_later_tab_needs_fs_list_cap(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "secret.txt").write_text("secret\n", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)

    _call_hostcall(ed, "ed.command-edit", "open s")
    assert ed.prompt is not None
    assert bool(getattr(ed.prompt, "script_context", False)) is True

    # A later direct Tab/completion must use the captured script authority.  It
    # should not list process-cwd files without explicit cap.fs-list.
    assert ed.prompt_complete(direction=1) is False
    assert ed.prompt is not None
    assert ed.prompt.text == "open s"



def test_script_created_command_prompt_later_tab_uses_cap_root(tmp_path, monkeypatch) -> None:
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (root / "safe.txt").write_text("safe\n", encoding="utf-8")
    (outside / "secret.txt").write_text("secret\n", encoding="utf-8")
    monkeypatch.chdir(outside)

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-list true") is True
    assert ed.exec_command_line(f"set cap.fs-root {root}") is True

    _call_hostcall(ed, "ed.command-edit", "open ./s")
    assert ed.prompt is not None
    assert bool(getattr(ed.prompt, "script_context", False)) is True

    assert ed.prompt_complete(direction=1) is True
    assert ed.prompt is not None
    assert "safe.txt" in ed.prompt.text
    assert "secret.txt" not in ed.prompt.text



def test_script_created_prompt_copy_selected_keeps_clipboard_script_origin() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    _call_hostcall(ed, "ed.command-palette", "status")
    assert ed.prompt is not None
    assert bool(getattr(ed.prompt, "script_context", False)) is True
    assert ed.prompt_copy_selected() is True

    assert ed.clipboard_items
    assert bool(getattr(ed, "clipboard_from_script", False)) is True


def test_script_command_prompt_path_completion_refuses_symlink_escape(tmp_path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.txt").write_text("secret\n", encoding="utf-8")
    link = root / "link"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlink support unavailable")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-list true") is True
    assert ed.exec_command_line(f"set cap.fs-root {root}") is True

    with ed.script_context():
        candidates = ed._path_completion_candidates("link/s", at_eol=True)

    assert candidates == []
