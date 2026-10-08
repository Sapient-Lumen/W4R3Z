from __future__ import annotations

import json
from pathlib import Path

import pytest

from micromax_editor.__main__ import main, run_headless_repl
from micromax_editor.buffer import Cursor
from micromax_editor.editor import Editor
from micromax_editor.startup import open_initial_buffer


REPO_ROOT = Path(__file__).resolve().parents[1]


def _dirty(ed: Editor, name: str, text: str = "x") -> None:
    eb = ed.buffers[name]
    eb.buf.insert(Cursor(0, len(eb.buf.lines[0])), text)


def test_open_initial_buffer_without_target_creates_scratch() -> None:
    ed = Editor()
    result = open_initial_buffer(ed)
    assert result.ok is True
    assert result.kind == "scratch"
    assert result.active == "*scratch*"
    assert result.fallback_used is False
    assert ed.active == "*scratch*"
    assert list(ed.buffers) == ["*scratch*"]


def test_open_initial_buffer_directory_failure_is_renderable_and_explicit(tmp_path: Path) -> None:
    ed = Editor()
    result = open_initial_buffer(ed, path=str(tmp_path))
    assert result.ok is False
    assert result.kind == "path"
    assert result.requested == str(tmp_path)
    assert result.active == "*scratch*"
    assert result.fallback_used is True
    assert result.message == f"startup: could not open {tmp_path}; using *scratch*"
    assert ed.active == "*scratch*"
    assert ed.cur().buf.get_text() == ""
    assert ed.screen_model(lines=8, cols=40)["cursor"]["visible"] == 1
    assert ed.messages[-2:] == [
        f"open: is a directory: {tmp_path}",
        result.message,
    ]


def test_open_initial_buffer_catches_unexpected_open_failure(monkeypatch) -> None:
    ed = Editor()

    def fail(_path: str) -> bool:
        raise OSError("read boundary failed")

    monkeypatch.setattr(ed, "open_file", fail)
    result = open_initial_buffer(ed, path="broken.txt")
    assert result.ok is False
    assert result.active == "*scratch*"
    assert result.message == (
        "startup: could not open broken.txt: read boundary failed; using *scratch*"
    )
    assert ed.active == "*scratch*"


def test_dump_screen_failed_initial_path_returns_json_and_nonzero(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("MICROMAX_INIT", str(tmp_path / "missing-init.mx"))
    rc = main(
        [
            str(tmp_path),
            "--plugins",
            str(REPO_ROOT / "plugins"),
            "--dump-screen",
            "8",
            "40",
        ]
    )
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert rc == 1
    assert data["schema"] == "micromax.screen.v1"
    assert data["size"] == {"lines": 8, "cols": 40}
    assert len(data["rows"]) == 8
    assert data["cursor"]["visible"] is True
    assert "Traceback" not in captured.err
    assert f"startup: could not open {tmp_path}; using *scratch*" in captured.err
    assert any(
        str(row.get("text", "")).startswith("startup: could not open")
        for row in data["rows"]
    )


@pytest.mark.parametrize("operation", ["quit", "close", "closeall", "only"])
def test_discard_confirmation_rearms_when_target_text_changes(operation: str) -> None:
    ed = Editor()
    ed.new_buffer("discard", "one")
    if operation == "only":
        ed.new_buffer("keep", "two")
    _dirty(ed, "discard")

    assert ed.exec_command_line(operation) is False
    assert "unsaved changes" in ed.messages[-1]
    _dirty(ed, "discard", "!")
    assert ed.exec_command_line(operation) is False
    assert "discard scope or unsaved state changed" in ed.messages[-1]
    assert "confirmation refreshed" in ed.messages[-1]
    assert "discard" in ed.buffers
    assert ed.should_quit is False

    assert ed.exec_command_line(operation) is True
    if operation == "quit":
        assert ed.should_quit is True
        assert "discard" in ed.buffers
    else:
        assert "discard" not in ed.buffers


def test_quit_confirmation_rearms_when_open_buffer_set_changes() -> None:
    ed = Editor()
    ed.new_buffer("dirty", "one")
    _dirty(ed, "dirty")
    assert ed.exec_command_line("quit") is False
    ed.new_buffer("new-clean-buffer", "")
    assert ed.exec_command_line("quit") is False
    assert ed.should_quit is False
    assert "confirmation refreshed" in ed.messages[-1]
    assert ed.exec_command_line("quit") is True


def test_close_confirmation_rearms_for_same_name_buffer_replacement() -> None:
    ed = Editor()
    ed.new_buffer("dirty", "one")
    _dirty(ed, "dirty")
    assert ed.exec_command_line("close") is False

    # Strict creation now refuses this replacement. Deliberately remove the
    # mapping to retain a low-level identity regression for corrupted/legacy
    # state: only the live object distinguishes the replacement from the row
    # the user was warned about.
    old = ed.buffers.pop("dirty")
    ed._buffer_authority.pop("dirty", None)
    ed.new_buffer("dirty", "one")
    _dirty(ed, "dirty")
    assert old is not ed.buffers["dirty"]
    assert ed.exec_command_line("close") is False
    assert "confirmation refreshed" in ed.messages[-1]
    assert "dirty" in ed.buffers
    assert ed.exec_command_line("close") is True


def test_only_confirmation_rearms_for_same_name_keep_replacement() -> None:
    ed = Editor()
    ed.new_buffer("discard", "one")
    _dirty(ed, "discard")
    ed.new_buffer("keep", "two")
    assert ed.exec_command_line("only") is False

    # The retained context is not discarded, so its edits need not re-arm.
    # Simulate corrupted/legacy replacement state explicitly: public strict
    # creation cannot replace this live name anymore.
    old_keep = ed.buffers.pop("keep")
    ed._buffer_authority.pop("keep", None)
    ed.new_buffer("keep", "replacement")
    assert old_keep is not ed.buffers["keep"]
    assert ed.exec_command_line("only") is False
    assert "confirmation refreshed" in ed.messages[-1]
    assert sorted(ed.buffers) == ["discard", "keep"]
    assert ed.exec_command_line("only") is True
    assert list(ed.buffers) == ["keep"]


def test_close_confirmation_tracks_explicit_target_across_buffer_switch() -> None:
    ed = Editor()
    ed.new_buffer("dirty", "one")
    _dirty(ed, "dirty")
    ed.new_buffer("other", "two")
    assert ed.exec_command_line("close dirty") is False
    assert ed.active == "other"
    assert ed._close_armed is True
    assert ed._close_armed_name == "dirty"
    assert ed.exec_command_line("close dirty") is True
    assert "dirty" not in ed.buffers
    assert ed.active == "other"


def test_only_confirmation_rearms_when_keep_target_changes() -> None:
    ed = Editor()
    ed.new_buffer("dirty", "one")
    _dirty(ed, "dirty")
    ed.new_buffer("keep-a", "two")
    ed.new_buffer("keep-b", "three")
    assert ed.switch_buffer("keep-a") is True
    assert ed.exec_command_line("only") is False
    assert ed.switch_buffer("keep-b") is True
    assert ed.exec_command_line("only") is False
    assert "confirmation refreshed" in ed.messages[-1]
    assert sorted(ed.buffers) == ["dirty", "keep-a", "keep-b"]


def test_unrelated_command_disarms_bulk_discard_confirmation() -> None:
    ed = Editor()
    ed.new_buffer("dirty", "one")
    _dirty(ed, "dirty")
    assert ed.exec_command_line("closeall") is False
    assert ed._closeall_armed is True
    assert ed.exec_command_line("pwd") is True
    assert ed._closeall_armed is False
    assert ed.exec_command_line("closeall") is False
    assert "unsaved changes" in ed.messages[-1]
    assert "confirmation refreshed" not in ed.messages[-1]


def test_prompt_preview_drops_armed_state_after_a_new_edit() -> None:
    ed = Editor()
    ed.new_buffer("dirty", "one")
    _dirty(ed, "dirty")
    assert ed.exec_command_line("quit") is False
    assert "| armed" in ed._prompt_quit_command_preview(command="quit")
    _dirty(ed, "dirty", "!")
    assert "| armed" not in ed._prompt_quit_command_preview(command="quit")
    assert "run quit again" in ed._prompt_quit_command_preview(command="quit")


def test_headless_repl_safe_quit_requires_unchanged_second_request(capsys) -> None:
    ed = Editor()
    ed.new_buffer("dirty", "one")
    _dirty(ed, "dirty")
    calls = 0

    def read(_prompt: str) -> str:
        nonlocal calls
        calls += 1
        if calls == 1:
            return ":q"
        if calls == 2:
            _dirty(ed, "dirty", "!")
            return ":q"
        return ":q"

    rc = run_headless_repl(ed, input_fn=read, stdin_isatty=False)
    out = capsys.readouterr().out
    assert rc == 0
    assert calls == 3
    assert "unsaved changes in: dirty" in out
    assert "discard scope or unsaved state changed" in out
    assert ed.should_quit is True


def test_headless_repl_force_quit_is_explicit(capsys) -> None:
    ed = Editor()
    ed.new_buffer("dirty", "one")
    _dirty(ed, "dirty")
    rc = run_headless_repl(ed, input_fn=lambda _prompt: ":q!", stdin_isatty=False)
    assert rc == 0
    assert ed.should_quit is True
    assert "force quit" in capsys.readouterr().out


def test_headless_repl_noninteractive_eof_refuses_clean_success(capsys) -> None:
    ed = Editor()
    ed.new_buffer("dirty", "one")
    _dirty(ed, "dirty")

    def eof(_prompt: str) -> str:
        raise EOFError

    rc = run_headless_repl(ed, input_fn=eof, stdin_isatty=False)
    out = capsys.readouterr().out
    assert rc == 2
    assert ed.should_quit is False
    assert ed._quit_armed is False
    assert "unsaved changes in: dirty" in out
    assert "exiting with status 2" in out


def test_headless_repl_tty_eof_returns_to_prompt_without_arming(capsys) -> None:
    ed = Editor()
    ed.new_buffer("dirty", "one")
    _dirty(ed, "dirty")
    calls = 0

    def read(_prompt: str) -> str:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise EOFError
        return ":q!"

    rc = run_headless_repl(ed, input_fn=read, stdin_isatty=True)
    out = capsys.readouterr().out
    assert rc == 0
    assert calls == 2
    assert "EOF did not discard unsaved buffers" in out
    assert ed.should_quit is True


def test_headless_repl_clean_eof_uses_normal_quit(capsys) -> None:
    ed = Editor()
    ed.new_buffer("clean", "one")

    def eof(_prompt: str) -> str:
        raise EOFError

    rc = run_headless_repl(ed, input_fn=eof, stdin_isatty=False)
    assert rc == 0
    assert ed.should_quit is True
    assert "exiting with status 2" not in capsys.readouterr().out


def test_trusted_startup_edit_conflict_recovery_and_close_journey(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from micromax_editor.startup import create_editor_runtime

    plugins = tmp_path / "plugins"
    plugins.mkdir()
    path = tmp_path / "journey.txt"
    path.write_text("alpha\n", encoding="utf-8")
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("MICROMAX_INIT", str(tmp_path / "missing-init.mx"))

    runtime = create_editor_runtime(plugins_root=plugins, workspace_trust="trusted")
    ed = runtime.editor
    assert open_initial_buffer(ed, path=str(path)).ok is True

    ed.run_action("EndOfLine")
    ed.input["text"] = "!"
    assert ed.run_action("InsertText") is True
    assert ed.cur().buf.get_text() == "alpha!\n"
    assert ed.dispatch_key("Ctrl-z") is True
    assert ed.cur().buf.get_text() == "alpha\n"
    assert ed.dispatch_key("Ctrl-y") is True
    assert ed.dispatch_key("Ctrl-s") is True
    assert path.read_text(encoding="utf-8") == "alpha!\n"

    ed.input["text"] = " local"
    assert ed.run_action("InsertText") is True
    path.write_text("external\n", encoding="utf-8")
    assert ed.dispatch_key("Ctrl-s") is False
    assert "file changed on disk" in ed.messages[-1]
    assert ed.exec_command_line("diff") is True
    assert any(message.startswith("diff: ") for message in ed.messages[-8:])
    assert ed.exec_command_line("save!") is True
    assert path.read_text(encoding="utf-8") == ed.cur().buf.get_text()

    ed.input["text"] = "?"
    assert ed.run_action("InsertText") is True
    assert ed.exec_command_line("close") is False
    ed.input["text"] = "!"
    assert ed.run_action("InsertText") is True
    assert ed.exec_command_line("close") is False
    assert "confirmation refreshed" in ed.messages[-1]
    assert ed.exec_command_line("close") is True
    assert ed.active == "*scratch*"


def test_restricted_startup_keeps_host_defaults_and_user_file_flow(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from micromax_editor.startup import create_editor_runtime

    path = tmp_path / "restricted.txt"
    path.write_text("safe", encoding="utf-8")
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("MICROMAX_INIT", str(tmp_path / "would-load.mx"))
    (tmp_path / "would-load.mx").write_text(": should-not-load 1 ;\n", encoding="utf-8")

    runtime = create_editor_runtime(
        plugins_root=REPO_ROOT / "plugins",
        workspace_trust="restricted",
    )
    ed = runtime.editor
    assert runtime.trust_policy.state == "restricted"
    assert runtime.plugin_manager.candidates
    assert not runtime.plugin_manager.plugins
    assert any("plugins scanned but not loaded" in message for message in ed.messages)
    assert any("user init not loaded" in message for message in ed.messages)
    assert ed.vm.find_word("should-not-load") is None

    assert open_initial_buffer(ed, path=str(path)).ok is True
    assert ed.resolve_key_binding("Ctrl-s") is not None
    ed.run_action("EndOfLine")
    ed.input["text"] = "!"
    assert ed.run_action("InsertText") is True
    assert ed.dispatch_key("Ctrl-s") is True
    assert path.read_text(encoding="utf-8") == "safe!"
