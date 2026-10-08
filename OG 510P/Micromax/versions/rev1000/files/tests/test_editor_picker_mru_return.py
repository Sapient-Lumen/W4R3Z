from __future__ import annotations

from pathlib import Path

import pytest

from micromax_editor.editor import Editor


@pytest.mark.parametrize("command", ["recentpick", "recentdirpick"])
def test_empty_recent_picker_defaults_to_mru_other_file(
    tmp_path: Path,
    command: str,
) -> None:
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    first.write_text("first\n", encoding="utf-8")
    second.write_text("second\n", encoding="utf-8")

    ed = Editor()
    assert ed.exec_command_line("set cap.fs-list true") is True
    assert ed.open_file(str(first)) is True
    assert ed.open_file(str(second)) is True
    assert ed.cur().buf.path == str(second)

    assert ed.exec_command_line(command) is True
    assert ed.prompt is not None
    assert ed.prompt.suggestions[ed.prompt.suggest_index] == str(first)

    assert ed.submit_prompt() is True
    assert ed.cur().buf.path == str(first)


def test_empty_buffer_picker_defaults_to_mru_other_but_query_keeps_rank() -> None:
    ed = Editor()
    ed.new_buffer("alpha", "alpha\n")
    ed.new_buffer("beta", "beta\n")
    ed.new_buffer("gamma", "gamma\n")
    assert ed.active == "gamma"
    assert ed.previous_buffer_name() == "beta"

    ed.enter_buffer_prompt()
    assert ed.prompt is not None
    assert ed.prompt.suggestions[ed.prompt.suggest_index] == "beta"
    assert ed.submit_prompt() is True
    assert ed.active == "beta"

    ed.enter_buffer_prompt("alpha")
    assert ed.prompt is not None
    assert ed.prompt.suggestions[ed.prompt.suggest_index] == "alpha"
    assert ed.submit_prompt() is True
    assert ed.active == "alpha"


def test_recent_picker_rejects_selection_removed_after_prompt_open(tmp_path: Path) -> None:
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    first.write_text("first\n", encoding="utf-8")
    second.write_text("second\n", encoding="utf-8")

    ed = Editor()
    assert ed.exec_command_line("set cap.fs-list true") is True
    assert ed.open_file(str(first)) is True
    assert ed.open_file(str(second)) is True
    assert ed.exec_command_line("recentpick") is True
    prompt = ed.prompt
    assert prompt is not None
    assert prompt.suggestions[prompt.suggest_index] == str(first)

    ed.recent_files.clear()
    ed.recent_files_authority.clear()

    assert ed.submit_prompt() is False
    assert ed.prompt is prompt
    assert ed.cur().buf.path == str(second)
    assert ed.messages[-1] == "recentpick: 0 recent file(s)"


def test_project_context_does_not_canonicalize_every_snapshot_member(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    previous = root / "previous.py"
    active = root / "active.py"

    ed = Editor()
    ed.new_buffer("previous", "", path=str(previous))
    ed.new_buffer("active", "", path=str(active))
    ed.recent_files = [str(active), str(previous), str(root / "recent.py")]

    def fail_resolve(_path: str) -> str:
        raise AssertionError("project picker context must not resolve snapshot members")

    ed._normalize_path = fail_resolve  # type: ignore[method-assign]
    inventory = ["active.py", "previous.py", "recent.py"] + [
        f"src/generated-{index:04d}.py" for index in range(4096)
    ]

    context, statuses = ed._project_file_picker_context(str(root), inventory)

    assert context[:2] == ["previous.py", "recent.py"]
    assert statuses["active.py"] == "active"
    assert statuses["previous.py"] == "previous"
    assert statuses["recent.py"] == "recent"


def test_recent_return_target_planning_reads_visible_register_once(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    first.write_text("first\n", encoding="utf-8")
    second.write_text("second\n", encoding="utf-8")

    ed = Editor()
    assert ed.open_file(str(first)) is True
    assert ed.open_file(str(second)) is True
    ed.enter_prompt("recent")

    original = ed.visible_recent_files
    calls = 0

    def counted_visible_recent_files() -> list[str]:
        nonlocal calls
        calls += 1
        return original()

    monkeypatch.setattr(ed, "visible_recent_files", counted_visible_recent_files)
    preferred, avoided = ed._picker_browse_navigation_candidates("recent")

    assert calls == 1
    assert preferred == (str(first),)
    assert avoided == (str(second),)
