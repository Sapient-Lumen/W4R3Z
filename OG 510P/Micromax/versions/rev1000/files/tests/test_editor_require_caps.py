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


def _call_host(ed: Editor, name: str) -> None:
    vm = ed.vm
    vm.stack.append(str(name))
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

def test_ed_require_rejects_oversized_source_before_consuming_path(tmp_path) -> None:
    src = tmp_path / "too-large.mx"
    src.write_text('"too-large" "ed.msg" hostcall\n', encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-require true")
    ed.vm.editor_source_load_max_bytes = 8

    vm = ed.vm
    vm.stack.append(str(src))
    vm.stack.append("ed.require")
    with pytest.raises(MicromaxError) as err:
        vm.eval("hostcall")

    assert "file too large" in str(err.value)
    assert vm.stack == [str(src)]
    assert "too-large" not in ed.messages


def test_ed_require_uses_source_eval_step_budget(tmp_path) -> None:
    src = tmp_path / "step-budget.mx"
    src.write_text('"loaded" "ed.msg" hostcall\n', encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-require true")
    ed.vm.editor_source_eval_step_budget = 2

    with pytest.raises(MicromaxError) as err:
        _call_ed_require(ed, str(src))

    assert "Execution budget exceeded" in str(err.value)
    assert "loaded" not in ed.messages


def test_core_include_in_script_context_uses_source_load_budget(tmp_path) -> None:
    src = tmp_path / "too-large-include.mx"
    src.write_text('"included" "ed.msg" hostcall\n', encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-require true")
    ed.vm.editor_source_load_max_bytes = 8

    with pytest.raises(MicromaxError) as err:
        with ed.script_context():
            ed.vm.eval(f'"{src}" include')

    assert "file too large" in str(err.value)
    assert "included" not in ed.messages


def test_core_require_in_script_context_uses_source_eval_step_budget(tmp_path) -> None:
    src = tmp_path / "core-step-budget.mx"
    src.write_text('"loaded" "ed.msg" hostcall\n', encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-require true")
    ed.vm.editor_source_eval_step_budget = 2

    with pytest.raises(MicromaxError) as err:
        with ed.script_context():
            ed.vm.eval(f'"{src}" require')

    assert "Execution budget exceeded" in str(err.value)
    assert "loaded" not in ed.messages
    assert str(src) not in ed.vm.loaded_paths

def test_query_budget_preserves_operand_and_skips_docs_section_scan() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.vm.editor_hostcall_query_max_bytes = 4
    called = False

    def doc_section_rows(query: str) -> list[object]:
        nonlocal called
        called = True
        return [["docs", query]]

    ed.doc_section_rows = doc_section_rows  # type: ignore[method-assign]
    ed.vm.stack[:] = ["abcde"]

    with pytest.raises(MicromaxError, match="ed.doc-section-rows: query 5 bytes exceeds editor query input budget 4"):
        _call_host(ed, "ed.doc-section-rows")

    assert called is False
    assert ed.vm.stack == ["abcde"]


def test_query_budget_blocks_prompt_opening_before_state_change() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.vm.editor_hostcall_query_max_bytes = 3
    ed.vm.stack[:] = ["query"]

    with pytest.raises(MicromaxError, match="ed.command-palette: query 5 bytes exceeds editor query input budget 3"):
        _call_host(ed, "ed.command-palette")

    assert ed.vm.stack == ["query"]
    assert ed.prompt is None


def test_disabled_query_budget_allows_embedding_owned_large_queries() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.vm.editor_hostcall_query_max_bytes = 0
    seen: list[str] = []

    def apropos_rows(query: str, *, limit: int | None = None) -> list[list[object]]:
        seen.append(query)
        assert limit is None or isinstance(limit, int)
        return [[query, "kind", "menu", "info"]]

    ed.apropos_rows = apropos_rows  # type: ignore[method-assign]
    ed.vm.stack[:] = ["x" * 32]

    _call_host(ed, "ed.apropos-rows")

    assert seen == ["x" * 32]
    assert ed.vm.stack == [[["x" * 32, "kind", "menu", "info"]]]

def test_ed_require_limits_nested_source_load_depth(tmp_path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    helper = root / "helper.mx"
    helper.write_text('"helper-ran" "ed.msg" hostcall\n', encoding="utf-8")
    main = root / "main.mx"
    main.write_text('"helper.mx" include\n', encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-require true")
    assert ed.exec_command_line(f"set cap.fs-root {root}")
    ed.vm.editor_source_load_max_depth = 1

    with pytest.raises(MicromaxError) as err:
        _call_ed_require(ed, "main.mx")

    assert "source load depth" in str(err.value)
    assert "source load graph budget 1" in str(err.value)
    assert "helper-ran" not in ed.messages


def test_ed_require_limits_cumulative_source_load_bytes(tmp_path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    helper = root / "helper.mx"
    helper.write_text('"helper-ran" "ed.msg" hostcall\n', encoding="utf-8")
    main = root / "main.mx"
    main.write_text('"helper.mx" include\n', encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-require true")
    assert ed.exec_command_line(f"set cap.fs-root {root}")
    ed.vm.editor_source_load_max_bytes = 10_000
    ed.vm.editor_source_load_max_total_bytes = main.stat().st_size + 1

    with pytest.raises(MicromaxError) as err:
        _call_ed_require(ed, "main.mx")

    assert "source load graph" in str(err.value)
    assert "bytes exceeds source load graph budget" in str(err.value)
    assert "helper-ran" not in ed.messages


def test_ed_require_graph_byte_failure_preserves_direct_path_operand(tmp_path) -> None:
    src = tmp_path / "root-too-large.mx"
    src.write_text('"root-ran" "ed.msg" hostcall\n', encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-require true")
    ed.vm.editor_source_load_max_bytes = 10_000
    ed.vm.editor_source_load_max_total_bytes = 1

    vm = ed.vm
    vm.stack.append(str(src))
    vm.stack.append("ed.require")
    with pytest.raises(MicromaxError) as err:
        vm.eval("hostcall")

    assert "source load graph" in str(err.value)
    assert vm.stack == [str(src)]
    assert "root-ran" not in ed.messages
