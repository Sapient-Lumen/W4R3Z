from __future__ import annotations

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _editor() -> Editor:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*history*", "")
    return ed


def test_script_prompt_history_prev_cannot_replay_trusted_command_history() -> None:
    ed = _editor()
    ed.history["command"] = ["open secret.txt"]
    ed.history_authority["command"] = []  # legacy rows default to trusted/user-owned
    ed.enter_prompt("command")

    with ed.script_context(origin_id="script-a"):
        assert ed.prompt_history_prev() is False

    assert ed.prompt.text == ""
    assert ed.prompt.hist_index is None
    assert ed.history["command"] == ["open secret.txt"]


def test_delayed_script_prompt_cannot_later_replay_trusted_history() -> None:
    ed = _editor()
    ed.history["command"] = ["write private.txt"]
    with ed.script_context(origin_id="script-a"):
        ed.enter_prompt("command")

    # The physical/key-driven history action happens after script_context exits,
    # but the prompt still carries script provenance and must not regain user
    # authority just because time passed.
    assert ed.prompt_history_prev() is False
    assert ed.prompt.text == ""
    assert ed.prompt.hist_index is None


def test_script_prompt_history_navigation_skips_trusted_rows_and_replays_own_rows() -> None:
    ed = _editor()
    ed.history["command"] = ["trusted-old"]
    ed.history_authority["command"] = []
    with ed.script_context(origin_id="script-a"):
        ed._push_history("command", "script-owned")
        ed.enter_prompt("command")
        assert ed.prompt_history_prev() is True
        assert ed.prompt.text == "script-owned"
        assert ed.prompt_history_prev() is False
        assert ed.prompt.text == "script-owned"


def test_independent_script_prompt_history_cannot_replay_other_script_rows() -> None:
    ed = _editor()
    with ed.script_context(origin_id="script-a"):
        ed._push_history("find", "owned-search")
    with ed.script_context(origin_id="script-b"):
        ed.enter_prompt("find")
        assert ed.prompt_history_prev() is False
        assert ed.prompt.text == ""


def test_prompt_history_next_restores_saved_text_without_replaying_trusted_rows() -> None:
    ed = _editor()
    ed.history["command"] = ["trusted-old"]
    ed.history_authority["command"] = []
    with ed.script_context(origin_id="script-a"):
        ed._push_history("command", "script-owned")
        ed.enter_prompt("command", prefill="scratch")
        assert ed.prompt_history_prev() is True
        assert ed.prompt.text == "script-owned"
        assert ed.prompt_history_next() is True
        assert ed.prompt.text == "scratch"
        assert ed.prompt.hist_index is None


def test_script_prompt_history_append_does_not_evict_trusted_full_history() -> None:
    ed = _editor()
    ed.options.set("history.limit", "2")
    ed.history["command"] = ["trusted-1", "trusted-2"]
    ed.history_authority["command"] = []

    with ed.script_context(origin_id="script-a"):
        ed._push_history("command", "script-noise")

    assert ed.history["command"] == ["trusted-1", "trusted-2"]
    ed._normalize_prompt_history_authority("command")
    assert [auth.script_context for auth in ed.history_authority["command"]] == [False, False]


def test_history_clear_capability_does_not_grant_prompt_history_replay() -> None:
    ed = _editor()
    ed.history["command"] = ["trusted-danger"]
    ed.history_authority["command"] = []
    assert ed.exec_command_line("set cap.history-clear true") is True

    with ed.script_context(origin_id="script-a"):
        ed.enter_prompt("command")
        assert ed.prompt_history_prev() is False

    assert ed.prompt.text == ""


def test_persisted_prompt_history_is_not_recalled_by_script(tmp_path) -> None:
    root = tmp_path / "persist"
    root.mkdir()
    (root / "history.json").write_text('{"command": ["open persisted-secret.txt"]}\n', encoding="utf-8")

    ed = Editor()
    ed.new_buffer(text="")
    ed.options.set("cap.persist", "true")
    ed.options.set("cap.persist-root", str(root))
    ed.options.set("history.persist", "true")
    ed.options.set("history.file", "history.json")
    assert ed.load_prompt_history() is True

    auth = ed.history_authority["command"][0]
    assert auth.script_context is True
    assert str(auth.script_origin_id or "").startswith("persist:prompt-history:")

    ed.enter_prompt("command")
    assert ed.prompt is not None
    with ed.script_context(origin_id="script:a"):
        assert ed.prompt_history_prev() is False
    assert ed.prompt.text == ""

    # The trusted/interactive user path can still recall persisted history.
    assert ed.prompt_history_prev() is True
    assert ed.prompt.text == "open persisted-secret.txt"


def test_persisted_recent_rows_restore_as_lower_authority(tmp_path) -> None:
    root = tmp_path / "persist"
    root.mkdir()
    (root / "recent.json").write_text('["persisted.txt"]\n', encoding="utf-8")

    ed = Editor()
    ed.new_buffer(text="")
    ed.options.set("cap.persist", "true")
    ed.options.set("cap.persist-root", str(root))
    ed.options.set("recent.persist", "true")
    ed.options.set("recent.file", "recent.json")
    assert ed.load_recent_files() is True

    assert ed.recent_files == ["persisted.txt"]
    auth = ed.recent_files_authority[0]
    assert auth.script_context is True
    assert str(auth.script_origin_id or "").startswith("persist:recent:")

    with ed.script_context(origin_id="script:a"):
        try:
            ed.clear_recent_files()
        except PermissionError as e:
            assert "recent-file MRU" in str(e)
        else:  # pragma: no cover - defensive: policy must deny by default
            raise AssertionError("script cleared persisted recent row without capability")
    assert ed.recent_files == ["persisted.txt"]
