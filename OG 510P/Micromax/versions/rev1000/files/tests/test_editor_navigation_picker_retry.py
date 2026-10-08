from __future__ import annotations

from pathlib import Path

import pytest

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.project_files import ProjectFileScanLimits, scan_project_files


def _install_direct_editor_scan(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Replace the isolated scan boundary with deterministic in-process evidence."""

    import micromax_editor.editor as editor_module

    calls: list[str] = []

    def direct(root, *, containment_root=None, include_hidden=False, limits=None):  # type: ignore[no-untyped-def]
        calls.append(str(Path(root).resolve()))
        active = limits or ProjectFileScanLimits()
        return scan_project_files(
            root,
            containment_root=containment_root,
            include_hidden=include_hidden,
            limits=ProjectFileScanLimits(
                max_files=active.max_files,
                max_dirs=active.max_dirs,
                max_depth=active.max_depth,
                max_entries=active.max_entries,
                max_path_bytes=active.max_path_bytes,
                timeout_seconds=0,
            ),
        )

    monkeypatch.setattr(editor_module, "scan_project_files", direct)
    return calls


def _assert_same_retryable_prompt(
    ed: Editor,
    prompt: object,
    *,
    kind: str,
    text: str,
    cursor: int,
) -> None:
    assert ed.prompt is prompt
    assert ed.prompt is not None
    assert ed.prompt.kind == kind
    assert ed.prompt.text == text
    assert ed.prompt.cursor == cursor
    assert ed.active_key_modes()[-1] == "prompt"
    assert ed.active_key_modes().count("prompt") == 1


def test_buffer_picker_failed_accept_keeps_query_then_success_closes() -> None:
    ed = Editor()
    ed.new_buffer("alpha", "alpha\n")
    ed.new_buffer("beta", "beta\n")
    assert ed.active == "beta"

    ed.enter_buffer_prompt()
    assert ed.set_prompt_text("no-such-buffer") is True
    prompt = ed.prompt
    assert prompt is not None
    cursor = prompt.cursor

    assert ed.submit_prompt() is False
    _assert_same_retryable_prompt(
        ed,
        prompt,
        kind="buffer",
        text="no-such-buffer",
        cursor=cursor,
    )
    assert ed.active == "beta"
    assert ed.messages[-1] == "bufferpick no-such-buffer: 0 buffer(s)"

    assert ed.set_prompt_text("alpha") is True
    assert ed.submit_prompt() is True
    assert ed.active == "alpha"
    assert ed.prompt is None
    assert "prompt" not in ed.active_key_modes()


@pytest.mark.parametrize(
    ("command", "kind", "label"),
    (("recentpick", "recent", "recentpick"), ("recentdirpick", "recentdir", "recentdirpick")),
)
def test_recent_picker_failed_accept_keeps_query_then_success_closes(
    tmp_path: Path,
    command: str,
    kind: str,
    label: str,
) -> None:
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    first.write_text("first\n", encoding="utf-8")
    second.write_text("second\n", encoding="utf-8")

    ed = Editor()
    assert ed.exec_command_line("set cap.fs-list true") is True
    assert ed.open_file(str(first)) is True
    assert ed.open_file(str(second)) is True
    assert ed.exec_command_line(command) is True
    assert ed.set_prompt_text("no-such-recent") is True
    prompt = ed.prompt
    assert prompt is not None
    cursor = prompt.cursor

    assert ed.submit_prompt() is False
    _assert_same_retryable_prompt(
        ed,
        prompt,
        kind=kind,
        text="no-such-recent",
        cursor=cursor,
    )
    assert ed.cur().buf.path == str(second)
    assert ed.messages[-1] == f"{label} no-such-recent: 0 recent file(s)"
    assert "no-such-recent" not in ed.buffers

    assert ed.set_prompt_text("first.txt") is True
    assert ed.submit_prompt() is True
    assert ed.cur().buf.path == str(first)
    assert ed.prompt is None
    assert "prompt" not in ed.active_key_modes()


def test_project_picker_stale_accept_retains_exact_snapshot_without_rescan(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = _install_direct_editor_scan(monkeypatch)
    root = tmp_path / "project"
    root.mkdir()
    (root / ".git").mkdir()
    seed = root / "seed.txt"
    stale = root / "stale.txt"
    survivor = root / "survivor.txt"
    seed.write_text("seed\n", encoding="utf-8")
    stale.write_text("stale\n", encoding="utf-8")
    survivor.write_text("survivor\n", encoding="utf-8")

    ed = Editor()
    assert ed.open_file(str(seed)) is True
    assert ed.enter_file_prompt() is True
    assert len(calls) == 1
    prompt = ed.prompt
    assert prompt is not None
    root_before = prompt.picker_root
    items_before = list(prompt.picker_items)
    meta_before = dict(prompt.picker_meta)

    stale.unlink()
    assert ed.set_prompt_text("stale.txt") is True
    cursor = prompt.cursor
    assert ed.submit_prompt() is False

    _assert_same_retryable_prompt(
        ed,
        prompt,
        kind="file",
        text="stale.txt",
        cursor=cursor,
    )
    assert len(calls) == 1
    assert prompt.picker_root == root_before
    assert prompt.picker_items == items_before
    assert prompt.picker_meta == meta_before
    assert ed.cur().buf.path == str(seed.resolve())
    assert ed.messages[-1] == "filepick: file disappeared since scan: stale.txt"

    assert ed.set_prompt_text("survivor.txt") is True
    assert ed.submit_prompt() is True
    assert len(calls) == 1
    assert ed.cur().buf.path == str(survivor.resolve())
    assert ed.prompt is None
    assert "prompt" not in ed.active_key_modes()


def test_script_project_picker_open_denial_retains_origin_and_snapshot(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = _install_direct_editor_scan(monkeypatch)
    root = tmp_path / "project"
    root.mkdir()
    target = root / "target.txt"
    target.write_text("target\n", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line(f"set cap.fs-root {root}") is True
    assert ed.exec_command_line("set cap.fs-list true") is True
    with ed.script_context(origin_id="picker-script"):
        assert ed.enter_file_prompt() is True

    prompt = ed.prompt
    assert prompt is not None
    assert prompt.script_context is True
    assert prompt.script_origin_id == "picker-script"
    items_before = list(prompt.picker_items)
    assert ed.set_prompt_text("target.txt") is True
    cursor = prompt.cursor

    assert ed.submit_prompt() is False
    _assert_same_retryable_prompt(
        ed,
        prompt,
        kind="file",
        text="target.txt",
        cursor=cursor,
    )
    assert prompt.script_context is True
    assert prompt.script_origin_id == "picker-script"
    assert prompt.picker_items == items_before
    assert len(calls) == 1
    assert str(target.resolve()) not in ed.buffers
    assert ed.messages[-1] == "filepick: disabled for scripts (cap.fs-open)"
