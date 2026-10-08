from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load_mxdoctor_module():
    spec = importlib.util.spec_from_file_location("mxdoctor_test_module", ROOT / "tools" / "mxdoctor.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_mxdoctor_disables_pytest_plugin_autoload_by_default(monkeypatch) -> None:
    module = _load_mxdoctor_module()
    monkeypatch.delenv("PYTEST_DISABLE_PLUGIN_AUTOLOAD", raising=False)
    monkeypatch.delenv("PYTHONDONTWRITEBYTECODE", raising=False)

    env = module.isolated_pytest_env()

    assert env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] == "1"
    assert env["PYTHONDONTWRITEBYTECODE"] == "1"


def test_mxdoctor_respects_explicit_pytest_plugin_autoload_choice(monkeypatch) -> None:
    module = _load_mxdoctor_module()
    monkeypatch.setenv("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "0")

    env = module.isolated_pytest_env()

    assert env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] == "0"


def test_mxdoctor_default_preflight_command_is_bounded_risk_lane(monkeypatch) -> None:
    monkeypatch.delenv("MXDOCTOR_PREFLIGHT_GROUP_SIZE", raising=False)
    module = _load_mxdoctor_module()

    cmd = module.preflight_command()
    commands = module.preflight_commands()

    assert cmd[:7] == [module.sys.executable, "-m", "pytest", "-q", "-s", "-p", "no:cacheprovider"]
    selectors = cmd[7:]
    assert selectors == module.FAST_PYTEST_TARGETS
    assert len(selectors) <= 31
    assert module.preflight_group_size() == module.PREFLIGHT_GROUP_SIZE
    assert commands
    assert all(command[:7] == cmd[:7] for command in commands)
    grouped_selectors = [selector for command in commands for selector in command[7:]]
    assert grouped_selectors == selectors
    assert len(commands) < len(selectors)
    assert all(len(command[7:]) <= module.preflight_group_size() for command in commands)
    assert "tests/test_smoke.py" in selectors
    assert "tests/test_stdlib_startup.py" in selectors
    assert "tests/test_editor_fs_open_save.py" in selectors
    assert "tests/test_editor_fs_read.py" in selectors
    assert "tests/test_editor_fs_list.py" in selectors
    assert "tests/test_editor_fs_stat.py" in selectors
    assert "tests/test_editor_script_context_fs_caps.py" in selectors
    assert "tests/test_editor_macro_authority.py" in selectors
    assert "tests/test_editor_mark_access_authority.py" in selectors
    assert "tests/test_editor_palette_recent_authority.py" not in selectors
    assert "tests/test_editor_plugin_authority.py" in selectors
    assert "tests/test_editor_hook_authority.py" in selectors
    assert "tests/test_editor_timer_authority.py" in selectors
    assert "tests/test_editor_keybinding_authority.py" in selectors
    assert "tests/test_editor_keymode_authority.py" in selectors
    assert "tests/test_editor_action_authority.py" in selectors
    assert "tests/test_editor_search_authority.py" in selectors
    assert "tests/test_editor_message_log_authority.py" in selectors
    assert "tests/test_editor_word_authority.py" in selectors
    assert "tests/test_editor_action_authority.py" in selectors
    assert "tests/test_editor_prompt_authority.py" in selectors
    assert "tests/test_editor_hook_authority.py" in selectors
    assert "tests/test_editor_highlight_and_timers.py" not in selectors
    assert "tests/test_editor_persistence_cap_persist.py" in selectors
    assert "tests/test_editor_hostcall_state_argument_boundary.py" in selectors
    assert "tests/test_editor_with_undo_transaction.py" in selectors
    assert "tests/test_plugin_reload_recovery.py" in selectors
    assert "tests/test_plugin_containment_and_caps.py" in selectors
    assert "tests/test_editor_mx_commands_and_completion.py" not in selectors
    assert "tests/test_mxdoctor.py" in selectors
    assert not any(target.startswith("tests/test_mxtest.py::") for target in selectors)
    assert "tests/test_docs_index.py" not in selectors
    assert "tests/test_editor_help_docs_boundary.py" in selectors
    assert "tests/test_prompt_completion.py" not in selectors
    assert "tests/test_prompt_rank.py" not in selectors


def test_mxdoctor_preflight_group_size_env_override(monkeypatch) -> None:
    module = _load_mxdoctor_module()
    monkeypatch.setenv("MXDOCTOR_PREFLIGHT_GROUP_SIZE", "2")

    commands = module.preflight_commands()

    assert module.preflight_group_size() == 2
    assert all(len(command[7:]) <= 2 for command in commands)
    assert [selector for command in commands for selector in command[7:]] == module.FAST_PYTEST_TARGETS


def test_mxdoctor_bad_preflight_group_size_env_falls_back(monkeypatch) -> None:
    module = _load_mxdoctor_module()
    monkeypatch.setenv("MXDOCTOR_PREFLIGHT_GROUP_SIZE", "not-an-int")

    assert module.preflight_group_size() == module.PREFLIGHT_GROUP_SIZE


def test_mxdoctor_full_pytest_command_keeps_unscoped_suite_lane() -> None:
    module = _load_mxdoctor_module()

    assert module.pytest_command(full=True) == [module.sys.executable, "-m", "pytest", "-q"]


def test_mxdoctor_chunked_command_uses_handoff_manifest_and_checkpointing(monkeypatch) -> None:
    module = _load_mxdoctor_module()
    monkeypatch.delenv("MXDOCTOR_CHUNKED_MAX_RUNTIME_SECONDS", raising=False)

    cmd = module.chunked_command(chunks=3)

    assert cmd[:3] == [module.sys.executable, "tools/mxtest.py", "--run-chunks"]
    assert "3" in cmd
    assert "--strategy" in cmd
    assert "segment" in cmd
    assert "--isolate-files" in cmd
    assert "--resume" in cmd
    assert "--checkpoint-tests" in cmd
    assert "--max-new-tests" in cmd
    assert str(module.DEFAULT_CHUNKED_MAX_NEW_TESTS) in cmd
    assert "--max-new-files" in cmd
    assert str(module.DEFAULT_CHUNKED_MAX_NEW_FILES) in cmd
    assert "--test-batch-size" in cmd
    assert str(module.DEFAULT_CHUNKED_TEST_BATCH_SIZE) in cmd
    assert "--file-timeout" in cmd
    assert str(module.DEFAULT_CHUNKED_FILE_TIMEOUT_SECONDS) in cmd
    assert module.DEFAULT_TEST_MANIFEST in cmd
    assert ".artifacts/mxtest-all.json" not in cmd
    assert "--max-runtime-seconds" in cmd
    assert str(module.DEFAULT_CHUNKED_MAX_RUNTIME_SECONDS) in cmd


def test_mxdoctor_chunked_command_accepts_manifest_runtime_and_budget_overrides() -> None:
    module = _load_mxdoctor_module()

    cmd = module.chunked_command(
        chunks=5,
        manifest=".artifacts/custom.json",
        max_runtime_seconds=12.5,
        max_new_tests=7,
        max_new_files=2,
        test_batch_size=1,
        file_timeout=33,
    )

    assert ".artifacts/custom.json" in cmd
    assert "--max-runtime-seconds" in cmd
    assert "12.5" in cmd
    assert cmd[cmd.index("--max-new-tests") + 1] == "7"
    assert cmd[cmd.index("--max-new-files") + 1] == "2"
    assert cmd[cmd.index("--test-batch-size") + 1] == "1"
    assert cmd[cmd.index("--file-timeout") + 1] == "33"


def test_mxdoctor_chunked_command_can_disable_runtime_budget(monkeypatch) -> None:
    module = _load_mxdoctor_module()
    monkeypatch.setenv("MXDOCTOR_CHUNKED_MAX_RUNTIME_SECONDS", "9")

    cmd = module.chunked_command(max_runtime_seconds=0)

    assert "--max-runtime-seconds" not in cmd


def test_mxdoctor_chunked_runtime_budget_env_override(monkeypatch) -> None:
    module = _load_mxdoctor_module()
    monkeypatch.setenv("MXDOCTOR_CHUNKED_MAX_RUNTIME_SECONDS", "17.5")

    cmd = module.chunked_command()

    assert "--max-runtime-seconds" in cmd
    assert "17.5" in cmd


def test_mxdoctor_timeout_env_helpers(monkeypatch) -> None:
    module = _load_mxdoctor_module()
    monkeypatch.delenv("MXDOCTOR_PREFLIGHT_TIMEOUT_SECONDS", raising=False)

    assert module.preflight_timeout_seconds() == module.DEFAULT_PREFLIGHT_TIMEOUT_SECONDS


    signals: list[tuple[int, int]] = []

    class FakeProc:
        pid = 123

        def __init__(self) -> None:
            self.wait_calls = 0
            self.terminated = False
            self.killed = False

        def poll(self):
            return None

        def wait(self, timeout=None):
            self.wait_calls += 1
            if self.wait_calls == 1:
                raise module.subprocess.TimeoutExpired(["doctor-child"], timeout)
            return 0

        def terminate(self) -> None:
            self.terminated = True

        def kill(self) -> None:
            self.killed = True

    monkeypatch.setattr(module.os, "name", "posix")
    monkeypatch.setattr(module.os, "killpg", lambda pgid, sig: signals.append((pgid, sig)))
    confirmed_proc = FakeProc()

    module._terminate_process_group(confirmed_proc, pgid=123)

    assert signals == [(123, module.signal.SIGTERM), (123, module.signal.SIGKILL)]
    assert confirmed_proc.terminated is False
    assert confirmed_proc.killed is False

    signals.clear()
    monkeypatch.setattr(module.os, "getpgid", lambda pid: pid + 1)
    unconfirmed_proc = FakeProc()

    assert module._confirmed_child_process_group_id(unconfirmed_proc) is None
    module._terminate_process_group(unconfirmed_proc, pgid=None)

    assert signals == []
    assert unconfirmed_proc.terminated is True
    assert unconfirmed_proc.killed is True

    monkeypatch.setenv("MXDOCTOR_PREFLIGHT_TIMEOUT_SECONDS", "0")
    assert module.preflight_timeout_seconds() is None

    monkeypatch.setenv("MXDOCTOR_PREFLIGHT_TIMEOUT_SECONDS", "not-an-int")
    assert module.preflight_timeout_seconds() == module.DEFAULT_PREFLIGHT_TIMEOUT_SECONDS


def test_mxdoctor_default_runs_bounded_preflight(monkeypatch) -> None:
    module = _load_mxdoctor_module()
    calls: list[list[str]] = []

    monkeypatch.setattr(module, "check_stdlib_resource", lambda: 0)
    monkeypatch.setattr(module, "warn_about_transient_caches", lambda: None)
    monkeypatch.setattr(module, "report_optional_tools", lambda: None)
    monkeypatch.setattr(module.platform, "platform", lambda: "test-platform")

    def fake_run(cmd: list[str], *, env: dict[str, str] | None = None, timeout: int | None = None) -> int:
        calls.append(list(cmd))
        return 0

    monkeypatch.setattr(module, "run", fake_run)

    rc = module.main([])

    assert rc == 0
    assert calls[0] == [module.sys.executable, "tools/mxlint.py"]
    assert calls[1:] == module.preflight_commands()


def test_mxdoctor_full_runs_unbounded_pytest(monkeypatch) -> None:
    module = _load_mxdoctor_module()
    calls: list[list[str]] = []

    monkeypatch.setattr(module, "check_stdlib_resource", lambda: 0)
    monkeypatch.setattr(module, "warn_about_transient_caches", lambda: None)
    monkeypatch.setattr(module, "report_optional_tools", lambda: None)
    monkeypatch.setattr(module.platform, "platform", lambda: "test-platform")

    def fake_run(cmd: list[str], *, env: dict[str, str] | None = None, timeout: int | None = None) -> int:
        calls.append(list(cmd))
        return 0

    monkeypatch.setattr(module, "run", fake_run)

    rc = module.main(["--full"])

    assert rc == 0
    assert calls[1] == [module.sys.executable, "-m", "pytest", "-q"]


def test_mxdoctor_chunked_runs_mxtest_aggregate_lane(monkeypatch) -> None:
    module = _load_mxdoctor_module()
    calls: list[list[str]] = []

    monkeypatch.setattr(module, "check_stdlib_resource", lambda: 0)
    monkeypatch.setattr(module, "warn_about_transient_caches", lambda: None)
    monkeypatch.setattr(module, "report_optional_tools", lambda: None)
    monkeypatch.setattr(module.platform, "platform", lambda: "test-platform")

    def fake_run(cmd: list[str], *, env: dict[str, str] | None = None, timeout: int | None = None) -> int:
        calls.append(list(cmd))
        return 0

    monkeypatch.setattr(module, "run", fake_run)

    rc = module.main([
        "--chunked",
        "--chunks",
        "5",
        "--max-new-tests",
        "9",
        "--max-new-files",
        "3",
        "--test-batch-size",
        "1",
        "--file-timeout",
        "44",
    ])

    assert rc == 0
    assert calls[1] == module.chunked_command(
        chunks=5,
        max_new_tests=9,
        max_new_files=3,
        test_batch_size=1,
        file_timeout=44,
    )


def test_mxdoctor_main_passes_timeout_settings(monkeypatch) -> None:
    module = _load_mxdoctor_module()
    calls: list[tuple[list[str], int | None]] = []

    monkeypatch.setattr(module, "check_stdlib_resource", lambda: 0)
    monkeypatch.setattr(module, "warn_about_transient_caches", lambda: None)
    monkeypatch.setattr(module, "report_optional_tools", lambda: None)
    monkeypatch.setattr(module.platform, "platform", lambda: "test-platform")
    monkeypatch.setenv("MXDOCTOR_LINT_TIMEOUT_SECONDS", "11")
    monkeypatch.setenv("MXDOCTOR_PREFLIGHT_TIMEOUT_SECONDS", "22")

    def fake_run(cmd: list[str], *, env: dict[str, str] | None = None, timeout: int | None = None) -> int:
        calls.append((list(cmd), timeout))
        return 0

    monkeypatch.setattr(module, "run", fake_run)

    assert module.main([]) == 0

    assert calls[0] == ([module.sys.executable, "tools/mxlint.py"], 11)
    assert all(timeout == 22 for _cmd, timeout in calls[1:])



def test_mxdoctor_fast_targets_have_no_duplicates() -> None:
    module = _load_mxdoctor_module()

    assert len(module.FAST_PYTEST_TARGETS) == len(set(module.FAST_PYTEST_TARGETS))


def test_fast_targets_include_fs_save_boundary():
    module = _load_mxdoctor_module()

    assert "tests/test_editor_fs_open_save.py" in module.FAST_PYTEST_TARGETS


def test_fast_targets_include_readonly_hostcall_boundary():
    module = _load_mxdoctor_module()

    assert "tests/test_editor_readonly_option.py" in module.FAST_PYTEST_TARGETS


def test_fast_targets_include_plugin_runtime_read_authority():
    module = _load_mxdoctor_module()

    assert "tests/test_editor_plugin_authority.py" in module.FAST_PYTEST_TARGETS
