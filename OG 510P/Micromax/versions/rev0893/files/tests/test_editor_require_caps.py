from __future__ import annotations

from pathlib import Path

import pytest

from micromax import MicromaxError
from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _call_ed_require(ed: Editor, path: str) -> None:
    vm = ed.vm
    vm.stack.append(str(path))
    vm.stack.append("ed.require")
    vm.eval("hostcall")


def test_ed_require_is_capability_gated(tmp_path) -> None:
    src = tmp_path / "script.mx"
    src.write_text('"loaded" "ed.msg" hostcall\n', encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)

    with pytest.raises(MicromaxError) as err:
        _call_ed_require(ed, str(src))
    assert "cap.fs-require" in str(err.value)
    assert "loaded" not in ed.messages

    assert ed.exec_command_line("set cap.fs-require true")
    ed.vm.eval('"ed.require" host.feature?')
    assert int(ed.vm.stack.pop()) == 1

    _call_ed_require(ed, str(src))
    assert ed.messages[-1] == "loaded"


def test_ed_require_respects_cap_fs_root_for_relative_and_absolute_paths(tmp_path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    inside = root / "inside.mx"
    inside.write_text('"inside" "ed.msg" hostcall\n', encoding="utf-8")
    outside = tmp_path / "outside.mx"
    outside.write_text('"outside" "ed.msg" hostcall\n', encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-require true")
    assert ed.exec_command_line(f"set cap.fs-root {root}")

    _call_ed_require(ed, "inside.mx")
    assert ed.messages[-1] == "inside"

    with pytest.raises(MicromaxError) as err:
        _call_ed_require(ed, str(outside))
    assert "cap.fs-root" in str(err.value) or "outside containment root" in str(err.value)
    assert "outside" not in ed.messages


def test_ed_require_rechecks_cap_root_after_late_symlink_parent_swap(tmp_path, monkeypatch) -> None:
    from micromax_editor import micromax_bridge as bridge_mod

    root = tmp_path / "root"
    root.mkdir()
    inside_dir = root / "inside"
    inside_dir.mkdir()
    (inside_dir / "script.mx").write_text('"inside" "ed.msg" hostcall\n', encoding="utf-8")
    outside_dir = tmp_path / "outside"
    outside_dir.mkdir()
    (outside_dir / "script.mx").write_text('"outside" "ed.msg" hostcall\n', encoding="utf-8")
    link = root / "link"
    try:
        link.symlink_to(inside_dir, target_is_directory=True)
    except (OSError, NotImplementedError) as e:
        pytest.skip(f"symlink unavailable: {e}")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-require true")
    assert ed.exec_command_line(f"set cap.fs-root {root}")

    original = bridge_mod.checked_sandbox_path
    swapped = {"done": False}

    def swap_after_preflight(ed_arg, raw_path):  # type: ignore[no-untyped-def]
        path = original(ed_arg, raw_path)
        if not swapped["done"]:
            swapped["done"] = True
            link.unlink()
            link.symlink_to(outside_dir, target_is_directory=True)
        return path

    monkeypatch.setattr(bridge_mod, "checked_sandbox_path", swap_after_preflight)

    with pytest.raises(MicromaxError) as err:
        _call_ed_require(ed, "link/script.mx")

    assert swapped["done"] is True
    assert "outside containment root" in str(err.value)
    assert "inside" not in ed.messages
    assert "outside" not in ed.messages


def test_core_require_is_gated_in_editor_script_context(tmp_path) -> None:
    src = tmp_path / "core-load.mx"
    src.write_text('"core-loaded" "ed.msg" hostcall\n', encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)

    with pytest.raises(MicromaxError) as err:
        with ed.script_context():
            ed.vm.eval(f'"{src}" require')
    assert "cap.fs-require" in str(err.value)
    assert "core-loaded" not in ed.messages

    assert ed.exec_command_line("set cap.fs-require true")
    with ed.script_context():
        ed.vm.eval(f'"{src}" require')
    assert ed.messages[-1] == "core-loaded"


def test_ed_require_evaluates_loaded_file_in_script_context(tmp_path) -> None:
    src = tmp_path / "escalate.mx"
    src.write_text('set cap.fs-save true\n', encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-require true")

    with pytest.raises(MicromaxError) as err:
        _call_ed_require(ed, str(src))

    assert "script context cannot modify capability option: cap.fs-save" in str(err.value)
    assert bool(ed.options.get("cap.fs-save")) is False


def test_ed_require_nested_core_require_uses_cap_root_and_script_policy(tmp_path) -> None:
    root = tmp_path / "root"
    sub = root / "sub"
    sub.mkdir(parents=True)
    helper = sub / "helper.mx"
    helper.write_text('"nested-helper" "ed.msg" hostcall\n', encoding="utf-8")
    main = sub / "main.mx"
    main.write_text('"helper.mx" require\n', encoding="utf-8")
    outside = tmp_path / "outside.mx"
    outside.write_text('"outside" "ed.msg" hostcall\n', encoding="utf-8")
    bad = sub / "bad.mx"
    bad.write_text('"../../outside.mx" include\n', encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-require true")
    assert ed.exec_command_line(f"set cap.fs-root {root}")

    _call_ed_require(ed, "sub/main.mx")
    assert ed.messages[-1] == "nested-helper"

    with pytest.raises(MicromaxError) as err:
        _call_ed_require(ed, "sub/bad.mx")
    assert "cap.fs-root" in str(err.value) or "outside containment root" in str(err.value)
    assert "outside" not in ed.messages


def test_core_unrequire_is_gated_in_editor_script_context(tmp_path) -> None:
    src = tmp_path / "once.mx"
    src.write_text(': once-word "once" ;\n', encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)

    with pytest.raises(MicromaxError) as err:
        with ed.script_context():
            ed.vm.eval(f'"{src}" unrequire')
    assert "cap.fs-require" in str(err.value)

    assert ed.exec_command_line("set cap.fs-require true")
    with ed.script_context():
        ed.vm.eval(f'"{src}" require')
        ed.vm.eval(f'"{src}" unrequire')
        ed.vm.eval(f'"{src}" require')
    ed.vm.eval('once-word')
    assert ed.vm.stack.pop() == "once"


@pytest.mark.parametrize("word", ["include", "reload"])
def test_core_include_and_reload_are_gated_in_editor_script_context(tmp_path, word: str) -> None:
    src = tmp_path / f"{word}.mx"
    src.write_text(f'"{word}-loaded" "ed.msg" hostcall\n', encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)

    with pytest.raises(MicromaxError) as err:
        with ed.script_context():
            ed.vm.eval(f'"{src}" {word}')
    assert "cap.fs-require" in str(err.value)
    assert f"{word}-loaded" not in ed.messages

    assert ed.exec_command_line("set cap.fs-require true")
    with ed.script_context():
        ed.vm.eval(f'"{src}" {word}')
    assert ed.messages[-1] == f"{word}-loaded"
