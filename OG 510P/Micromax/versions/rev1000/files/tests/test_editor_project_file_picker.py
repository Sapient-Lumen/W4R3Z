from __future__ import annotations

import copy
import multiprocessing
from pathlib import Path

import pytest

from micromax_editor.buffer import Cursor
from micromax_editor.editor import Editor
from micromax_editor.file_access import isolated_filesystem_worker_context
from micromax_editor.hostcall_boundary import (
    DEFAULT_PROJECT_FILE_MAX_DEPTH,
    DEFAULT_PROJECT_FILE_MAX_DIRS,
    DEFAULT_PROJECT_FILE_MAX_ENTRIES,
    DEFAULT_PROJECT_FILE_MAX_FILES,
    DEFAULT_PROJECT_FILE_MAX_PATH_BYTES,
    DEFAULT_PROJECT_FILE_TIMEOUT_SECONDS,
)
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.project_files import (
    ProjectFileScan,
    ProjectFileScanLimits,
    scan_project_files,
)


def _limits(**overrides: int | float) -> ProjectFileScanLimits:
    values: dict[str, int | float] = {
        "max_files": 64,
        "max_dirs": 64,
        "max_depth": 16,
        "max_entries": 256,
        "max_path_bytes": 8192,
        "timeout_seconds": 0,
    }
    values.update(overrides)
    return ProjectFileScanLimits(**values)  # type: ignore[arg-type]


def _direct_scan(root: Path, *, include_hidden: bool = False) -> ProjectFileScan:
    return scan_project_files(
        root,
        include_hidden=include_hidden,
        limits=_limits(),
    )


def _install_direct_editor_scan(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, object]]:
    import micromax_editor.editor as editor_module

    calls: list[dict[str, object]] = []

    def direct(root, *, containment_root=None, include_hidden=False, limits=None):  # type: ignore[no-untyped-def]
        calls.append(
            {
                "root": str(root),
                "containment_root": None if containment_root is None else str(containment_root),
                "include_hidden": bool(include_hidden),
                "limits": limits,
            }
        )
        active = limits or ProjectFileScanLimits()
        active = ProjectFileScanLimits(
            max_files=active.max_files,
            max_dirs=active.max_dirs,
            max_depth=active.max_depth,
            max_entries=active.max_entries,
            max_path_bytes=active.max_path_bytes,
            timeout_seconds=0,
        )
        return scan_project_files(
            root,
            containment_root=containment_root,
            include_hidden=include_hidden,
            limits=active,
        )

    monkeypatch.setattr(editor_module, "scan_project_files", direct)
    return calls


def _bind_key_via_hostcall(ed: Editor, key: str, action_spec: str) -> None:
    ed.vm.stack.extend([str(key), str(action_spec), "ed.bind"])
    ed.vm.eval("hostcall", filename="<project-picker-test>")


def test_scan_is_deterministic_hidden_aware_and_never_follows_symlinks(tmp_path: Path) -> None:
    root = tmp_path / "project"
    (root / "src").mkdir(parents=True)
    (root / ".git").mkdir()
    (root / "node_modules" / "pkg").mkdir(parents=True)
    (root / "B.txt").write_text("b", encoding="utf-8")
    (root / "a.txt").write_text("a", encoding="utf-8")
    (root / "src" / "main.py").write_text("print('ok')\n", encoding="utf-8")
    (root / ".env").write_text("secret=no\n", encoding="utf-8")
    (root / ".git" / "config").write_text("metadata\n", encoding="utf-8")
    (root / "node_modules" / "pkg" / "index.js").write_text("generated\n", encoding="utf-8")

    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.txt").write_text("secret\n", encoding="utf-8")
    try:
        (root / "linked-dir").symlink_to(outside, target_is_directory=True)
        (root / "linked-file").symlink_to(outside / "secret.txt")
    except (OSError, NotImplementedError):
        pass

    first = _direct_scan(root)
    second = _direct_scan(root)
    assert first.ok is True
    assert first.files == second.files
    assert first.files == ("a.txt", "B.txt", "src/main.py")

    hidden = _direct_scan(root, include_hidden=True)
    assert hidden.files == (".env", "a.txt", "B.txt", "src/main.py")
    assert not any(".git" in path or "node_modules" in path for path in hidden.files)
    assert not any("linked" in path or "secret" in path for path in hidden.files)


def test_scan_enforces_file_entry_path_byte_and_depth_budgets(tmp_path: Path) -> None:
    root = tmp_path / "project"
    (root / "deep" / "nested").mkdir(parents=True)
    for name in ("a.txt", "b.txt", "c.txt"):
        (root / name).write_text(name, encoding="utf-8")
    (root / "deep" / "nested" / "leaf.txt").write_text("leaf", encoding="utf-8")

    files = scan_project_files(root, limits=_limits(max_files=2))
    assert len(files.files) == 2
    assert files.truncated is True
    assert files.reason == "files"

    entries = scan_project_files(root, limits=_limits(max_entries=1))
    assert entries.truncated is True
    assert entries.reason == "entries"
    assert entries.entries_scanned == 1

    path_bytes = scan_project_files(root, limits=_limits(max_path_bytes=2))
    assert path_bytes.truncated is True
    assert path_bytes.reason == "path-bytes"
    assert path_bytes.path_bytes == 2

    depth = scan_project_files(root, limits=_limits(max_depth=0))
    assert set(depth.files) == {"a.txt", "b.txt", "c.txt"}
    assert depth.truncated is True
    assert depth.reason == "depth"


def test_depth_truncation_does_not_disable_a_later_terminal_entry_budget(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import micromax_editor.project_files as project_files_module

    root = tmp_path / "project"
    for name in ("a", "b", "c", "d"):
        (root / name).mkdir(parents=True)
    (root / "a" / "inner").mkdir()
    (root / "b" / "one.txt").write_text("1", encoding="utf-8")
    (root / "b" / "two.txt").write_text("2", encoding="utf-8")
    (root / "c" / "should-not-scan.txt").write_text("c", encoding="utf-8")
    (root / "d" / "should-not-scan.txt").write_text("d", encoding="utf-8")

    real_scandir = project_files_module.os.scandir
    scan_calls: list[object] = []

    def counted_scandir(path):  # type: ignore[no-untyped-def]
        scan_calls.append(path)
        return real_scandir(path)

    monkeypatch.setattr(project_files_module.os, "scandir", counted_scandir)
    result = scan_project_files(
        root,
        limits=_limits(max_depth=1, max_entries=6),
    )

    assert result.truncated is True
    assert result.reason == "entries"
    assert result.entries_scanned == 6
    # root, a, and b are scanned. The hard entry cap reached in b prevents c/d.
    assert len(scan_calls) == 3


def test_new_filesystem_worker_context_prefers_spawn_then_forkserver(monkeypatch: pytest.MonkeyPatch) -> None:
    requested: list[str] = []

    monkeypatch.setattr(
        multiprocessing,
        "get_all_start_methods",
        lambda: ["fork", "spawn", "forkserver"],
    )
    real_get_context = multiprocessing.get_context

    def tracked(method=None):  # type: ignore[no-untyped-def]
        requested.append(str(method))
        return real_get_context(method)

    monkeypatch.setattr(multiprocessing, "get_context", tracked)
    context = isolated_filesystem_worker_context()

    assert context.get_start_method() == "spawn"
    assert requested == ["spawn"]


def test_scan_timeout_is_transactional_and_leaves_no_partial_snapshot(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import micromax_editor.project_files as project_files_module

    events: list[str] = []
    process = object()
    channel = object()

    monkeypatch.setattr(
        project_files_module,
        "isolated_filesystem_worker_context",
        lambda: object(),
    )
    monkeypatch.setattr(
        project_files_module,
        "create_one_shot_worker",
        lambda *_args, **_kwargs: (events.append("create") or process, channel),
    )

    def timeout(*_args, **_kwargs):  # type: ignore[no-untyped-def]
        events.append("collect")
        raise project_files_module.WorkerResultTimeoutError("deadline")

    monkeypatch.setattr(project_files_module, "collect_worker_result", timeout)

    result = scan_project_files(tmp_path, limits=_limits(timeout_seconds=0.001))

    assert result.files == ()
    assert result.timed_out is True
    assert result.truncated is True
    assert result.reason == "timeout"
    assert "timed out" in result.error
    assert events == ["create", "collect"]


def test_target_ready_boundary_excludes_spawn_bootstrap_from_scan_timeout(
    tmp_path: Path,
) -> None:
    (tmp_path / "ready.txt").write_text("ready", encoding="utf-8")

    result = scan_project_files(
        tmp_path,
        limits=_limits(timeout_seconds=0.25),
    )

    assert result.ok is True
    assert result.files == ("ready.txt",)
    assert result.timed_out is False


def test_project_scan_ready_gate_classifies_child_exit_before_target_entry() -> None:
    import micromax_editor.project_files as project_files_module

    gate = project_files_module._ProjectFileWorkerReadyGate(timeout_seconds=0.1)
    gate.child_endpoint.close()
    try:
        with pytest.raises(
            project_files_module.WorkerResultStartError,
            match="closed before readiness",
        ):
            gate.wait_and_release(4242)
    finally:
        gate.close()


def test_scan_readiness_timeout_is_not_mislabeled_as_traversal_timeout(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    import micromax_editor.project_files as project_files_module

    process = object()
    channel = object()
    monkeypatch.setattr(
        project_files_module,
        "create_one_shot_worker",
        lambda *_args, **_kwargs: (process, channel),
    )

    def fail_readiness(proc, result_channel, **kwargs):  # type: ignore[no-untyped-def]
        assert proc is process
        assert result_channel is channel
        assert callable(kwargs["after_start"])
        raise project_files_module.WorkerResultStartTimeoutError(
            "project file scan worker readiness timed out after 5s"
        )

    monkeypatch.setattr(
        project_files_module,
        "collect_worker_result",
        fail_readiness,
    )

    result = scan_project_files(tmp_path, limits=_limits(timeout_seconds=0.25))

    assert result.ok is False
    assert result.timed_out is True
    assert result.truncated is True
    assert result.reason == "startup-timeout"
    assert result.error == "project file scan worker readiness timed out after 5s"


def test_scan_accepts_one_complete_framed_worker_snapshot(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import micromax_editor.project_files as project_files_module

    events: list[str] = []
    expected = ProjectFileScan(root=str(tmp_path.resolve()), files=("a.txt",))
    process = object()
    channel = object()

    monkeypatch.setattr(
        project_files_module,
        "isolated_filesystem_worker_context",
        lambda: object(),
    )
    monkeypatch.setattr(
        project_files_module,
        "create_one_shot_worker",
        lambda *_args, **_kwargs: (events.append("create") or process, channel),
    )

    def collect(proc, result_channel, **kwargs):  # type: ignore[no-untyped-def]
        assert proc is process
        assert result_channel is channel
        assert kwargs["require_clean_exit"] is True
        assert callable(kwargs["after_start"])
        events.append("collect")
        return ("ok", expected)

    monkeypatch.setattr(project_files_module, "collect_worker_result", collect)
    result = scan_project_files(tmp_path, limits=_limits(timeout_seconds=1))

    assert result == expected
    assert events == ["create", "collect"]

def test_picker_uses_nearest_marker_root_and_one_immutable_snapshot(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = _install_direct_editor_scan(monkeypatch)
    root = tmp_path / "project"
    nested = root / "src" / "nested"
    nested.mkdir(parents=True)
    (root / ".git").mkdir()
    seed = nested / "seed.py"
    seed.write_text("seed\n", encoding="utf-8")
    (root / "README.md").write_text("readme\n", encoding="utf-8")
    (root / "src" / "main.py").write_text("main\n", encoding="utf-8")
    (root / "tests").mkdir()
    (root / "tests" / "test_main.py").write_text("test\n", encoding="utf-8")

    ed = Editor()
    ed.open_file(str(seed))
    assert ed.enter_file_prompt() is True
    assert ed.prompt is not None
    assert ed.prompt.kind == "file"
    assert ed.prompt.picker_root == str(root.resolve())
    assert len(calls) == 1
    assert ed.prompt_current_section() == "Project root"

    assert ed.set_prompt_text("mnpy") is True
    assert len(calls) == 1
    assert ed.prompt is not None
    assert ed.prompt.suggestions[0] == "src/main.py"
    assert ed.prompt_current_section() == "Matches"

    (root / "after-scan.txt").write_text("new\n", encoding="utf-8")
    assert ed.set_prompt_text("after-scan") is True
    assert len(calls) == 1
    assert ed.prompt is not None
    assert "after-scan.txt" not in ed.prompt.picker_items
    assert ed.prompt.suggestions == []


def test_picker_reopens_on_previous_file_and_toggles_without_typing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_direct_editor_scan(monkeypatch)
    root = tmp_path / "project"
    root.mkdir()
    (root / ".git").mkdir()
    first = root / "first.py"
    second = root / "second.py"
    third = root / "third.py"
    for path in (first, second, third):
        path.write_text(f"{path.stem}\n", encoding="utf-8")

    ed = Editor()
    assert ed.open_file(str(first)) is True
    assert ed.open_file(str(second)) is True

    assert ed.enter_file_prompt() is True
    assert ed.prompt is not None
    rows = ed.project_file_prompt_rows(limit=40)
    assert rows[0] == ["first.py", "projectfile-context", "previous", "project root"]
    assert [row[0] for row in rows].count("first.py") == 1
    assert next(row for row in rows if row[0] == "second.py")[2] == "active"
    assert ed.prompt_current_section() == "Open and recent"
    status = ed.status_model()
    assert status["prompt_current_insert"] == "first.py"
    assert status["prompt_current_menu"] == "previous"
    assert status["prompt_current_section"] == "Open and recent"
    assert "first.py" in status["prompt_current_preview"]

    assert ed.submit_prompt() is True
    assert ed.cur().name == str(first.resolve())

    assert ed.enter_file_prompt() is True
    assert ed.prompt_current_row()[:3] == ["second.py", "projectfile-context", "previous"]
    assert ed.submit_prompt() is True
    assert ed.cur().name == str(second.resolve())


def test_picker_marks_dirty_previous_file_without_live_rescanning(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_direct_editor_scan(monkeypatch)
    root = tmp_path / "project"
    root.mkdir()
    (root / ".git").mkdir()
    first = root / "first.py"
    second = root / "second.py"
    first.write_text("first\n", encoding="utf-8")
    second.write_text("second\n", encoding="utf-8")

    ed = Editor()
    assert ed.open_file(str(first)) is True
    ed.cur().buf.insert(Cursor(0, 0), "changed ")
    assert ed.open_file(str(second)) is True
    assert ed.enter_file_prompt() is True
    assert ed.prompt_current_row()[:3] == [
        "first.py",
        "projectfile-context",
        "modified previous",
    ]

    # The prompt owns one captured truth. Later mutation does not rewrite the
    # visible row until the picker is deliberately reopened.
    ed.buffers[str(first.resolve())].buf.mark_clean()

    def unexpected_path_refresh(_path: str) -> str:
        raise AssertionError("project prompt refresh must not re-normalize live paths")

    monkeypatch.setattr(ed, "_normalize_path", unexpected_path_refresh)
    ed._refresh_file_prompt_suggestions()
    assert ed.prompt_current_row()[2] == "modified previous"


def test_script_picker_context_does_not_inventory_other_user_buffers(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_direct_editor_scan(monkeypatch)
    root = tmp_path / "project"
    root.mkdir()
    first = root / "first.py"
    second = root / "second.py"
    first.write_text("first\n", encoding="utf-8")
    second.write_text("second\n", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.open_file(str(first)) is True
    assert ed.open_file(str(second)) is True
    assert ed.exec_command_line(f"set cap.fs-root {root}") is True
    assert ed.exec_command_line("set cap.fs-list true") is True

    with ed.script_context():
        assert ed.enter_file_prompt() is True
        assert ed.prompt is not None
        assert ed.prompt.picker_meta["context_paths"] == []
        rows = ed.project_file_prompt_rows(limit=40)

    # Scripts retain ambient knowledge of the active buffer, but the hidden
    # previous user buffer is neither promoted nor labeled as open.
    assert next(row for row in rows if row[0] == "second.py")[2] == "active"
    assert next(row for row in rows if row[0] == "first.py")[2] == "file"


def test_picker_submit_opens_only_a_snapshot_member(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _install_direct_editor_scan(monkeypatch)
    root = tmp_path / "project"
    root.mkdir()
    (root / ".git").mkdir()
    seed = root / "seed.txt"
    target = root / "target.txt"
    outside = tmp_path / "outside.txt"
    seed.write_text("seed\n", encoding="utf-8")
    target.write_text("target\n", encoding="utf-8")
    outside.write_text("outside\n", encoding="utf-8")

    ed = Editor()
    ed.open_file(str(seed))
    assert ed.enter_file_prompt() is True
    assert ed.set_prompt_text(str(outside)) is True
    assert ed.submit_prompt() is False
    assert ed.cur().name == str(seed.resolve())
    assert any("0 project file(s)" in message for message in ed.messages)

    assert ed.enter_file_prompt() is True
    assert ed.set_prompt_text("target.txt") is True
    assert ed.submit_prompt() is True
    assert ed.cur().name == str(target.resolve())
    assert any("filepick: target.txt @" in message for message in ed.messages)


def test_picker_rejects_deleted_and_post_scan_symlink_swaps(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_direct_editor_scan(monkeypatch)
    root = tmp_path / "project"
    root.mkdir()
    (root / ".git").mkdir()
    seed = root / "seed.txt"
    stale = root / "stale.txt"
    seed.write_text("seed\n", encoding="utf-8")
    stale.write_text("stale\n", encoding="utf-8")

    ed = Editor()
    ed.open_file(str(seed))
    assert ed.enter_file_prompt() is True
    stale.unlink()
    assert ed.set_prompt_text("stale.txt") is True
    assert ed.submit_prompt() is False
    assert any("disappeared since scan" in message for message in ed.messages)

    outside = tmp_path / "secret.txt"
    outside.write_text("secret\n", encoding="utf-8")
    stale.write_text("safe\n", encoding="utf-8")
    assert ed.enter_file_prompt() is True
    stale.unlink()
    try:
        stale.symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks unavailable on this host")
    assert ed.set_prompt_text("stale.txt") is True
    assert ed.submit_prompt() is False
    assert ed.cur().name == str(seed.resolve())
    assert any("symlink" in message or "escaped project root" in message for message in ed.messages)


def test_hidden_option_reveals_dotfiles_but_never_vcs_metadata(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = _install_direct_editor_scan(monkeypatch)
    root = tmp_path / "project"
    root.mkdir()
    (root / ".git").mkdir()
    seed = root / "seed.txt"
    seed.write_text("seed\n", encoding="utf-8")
    (root / ".env").write_text("visible by option\n", encoding="utf-8")
    (root / ".git" / "config").write_text("never visible\n", encoding="utf-8")

    ed = Editor()
    ed.open_file(str(seed))
    assert ed.exec_command_line("set filepicker.hidden true") is True
    assert ed.enter_file_prompt() is True
    assert calls[-1]["include_hidden"] is True
    assert ed.prompt is not None
    assert ".env" in ed.prompt.picker_items
    assert not any(path.startswith(".git/") for path in ed.prompt.picker_items)


def test_script_picker_requires_list_then_preserves_delayed_open_authority(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_direct_editor_scan(monkeypatch)
    root = tmp_path / "project"
    root.mkdir()
    target = root / "target.txt"
    target.write_text("target\n", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line(f"set cap.fs-root {root}") is True
    with ed.script_context():
        assert ed.enter_file_prompt() is False
    assert any("cap.fs-list" in message for message in ed.messages)

    assert ed.exec_command_line("set cap.fs-list true") is True
    with ed.script_context():
        assert ed.enter_file_prompt() is True
    assert ed.prompt is not None
    assert ed.prompt.script_context is True
    assert ed.prompt.picker_root == str(root.resolve())
    assert ed.set_prompt_text("target.txt") is True
    assert ed.submit_prompt() is False
    assert any("cap.fs-open" in message for message in ed.messages)
    assert str(target.resolve()) not in ed.buffers


def test_script_bound_picker_cannot_borrow_later_interactive_open_authority(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_direct_editor_scan(monkeypatch)
    root = tmp_path / "project"
    root.mkdir()
    target = root / "target.txt"
    target.write_text("target\n", encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line(f"set cap.fs-root {root}") is True
    assert ed.exec_command_line("set cap.fs-list true") is True
    with ed.script_context():
        _bind_key_via_hostcall(ed, "F9", "FilePicker")

    assert ed.dispatch_key("F9") is True
    assert ed.prompt is not None
    assert ed.prompt.script_context is True
    assert ed.set_prompt_text("target.txt") is True
    assert ed.submit_prompt() is False
    assert str(target.resolve()) not in ed.buffers
    assert any("cap.fs-open" in message for message in ed.messages)


def test_prompt_lifecycle_snapshot_detaches_project_inventory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_direct_editor_scan(monkeypatch)
    root = tmp_path / "project"
    root.mkdir()
    (root / "one.txt").write_text("one\n", encoding="utf-8")

    ed = Editor()
    ed.new_buffer("seed", "", path=str(root / "seed.txt"))
    assert ed.enter_file_prompt() is True
    assert ed.prompt is not None
    original_root = ed.prompt.picker_root
    original_items = list(ed.prompt.picker_items)
    original_meta = copy.deepcopy(ed.prompt.picker_meta)
    original_context = list(ed.prompt.picker_meta.get("context_paths", []))
    original_status = dict(ed.prompt.picker_meta.get("status_by_path", {}))

    snapshot = ed.snapshot_prompt_group_state(None)
    ed.prompt.picker_root = "mutated"
    ed.prompt.picker_items.append("mutated.txt")
    ed.prompt.picker_meta["mutated"] = 1
    context = ed.prompt.picker_meta.get("context_paths")
    if isinstance(context, list):
        context.append("mutated.txt")
    statuses = ed.prompt.picker_meta.get("status_by_path")
    if isinstance(statuses, dict):
        statuses["mutated.txt"] = "previous"
    ed.restore_prompt_group_state(snapshot, None)

    assert ed.prompt is not None
    assert ed.prompt.picker_root == original_root
    assert ed.prompt.picker_items == original_items
    assert ed.prompt.picker_meta == original_meta
    assert ed.prompt.picker_meta.get("context_paths") == original_context
    assert ed.prompt.picker_meta.get("status_by_path") == original_status
    assert ed.prompt.picker_items is not snapshot.prompt.picker_items  # type: ignore[union-attr]
    assert ed.prompt.picker_meta is not snapshot.prompt.picker_meta  # type: ignore[union-attr]


def test_direct_scan_limits_reject_nonfinite_timeouts() -> None:
    assert ProjectFileScanLimits(timeout_seconds=float("nan")).normalized().timeout_seconds == 1.0
    assert ProjectFileScanLimits(timeout_seconds=float("inf")).normalized().timeout_seconds == 1.0
    assert ProjectFileScanLimits(timeout_seconds=0).normalized().timeout_seconds == 0.0


def test_vm_project_scan_limits_remain_finite_when_malformed_or_nonpositive() -> None:
    ed = Editor()
    ed.vm.editor_project_file_max_files = 0
    ed.vm.editor_project_file_max_dirs = -1
    ed.vm.editor_project_file_max_depth = "nope"
    ed.vm.editor_project_file_max_entries = None
    ed.vm.editor_project_file_max_path_bytes = 0
    ed.vm.editor_project_file_timeout_seconds = float("inf")

    limits = ed._project_file_scan_limits()
    assert limits.max_files == DEFAULT_PROJECT_FILE_MAX_FILES
    assert limits.max_dirs == DEFAULT_PROJECT_FILE_MAX_DIRS
    assert limits.max_depth == DEFAULT_PROJECT_FILE_MAX_DEPTH
    assert limits.max_entries == DEFAULT_PROJECT_FILE_MAX_ENTRIES
    assert limits.max_path_bytes == DEFAULT_PROJECT_FILE_MAX_PATH_BYTES
    assert limits.timeout_seconds == DEFAULT_PROJECT_FILE_TIMEOUT_SECONDS
