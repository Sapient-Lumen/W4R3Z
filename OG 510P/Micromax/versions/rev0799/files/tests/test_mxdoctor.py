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


def test_mxdoctor_default_preflight_command_is_bounded_risk_lane() -> None:
    module = _load_mxdoctor_module()

    cmd = module.preflight_command()
    commands = module.preflight_commands()

    assert cmd[:7] == [module.sys.executable, "-m", "pytest", "-q", "-s", "-p", "no:cacheprovider"]
    selectors = cmd[7:]
    assert selectors == module.FAST_PYTEST_TARGETS
    assert len(selectors) <= 24
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
    assert "tests/test_editor_highlight_and_timers.py" in selectors
    assert "tests/test_editor_persistence_cap_persist.py" in selectors
    assert "tests/test_editor_hostcall_state_argument_boundary.py" in selectors
    assert "tests/test_editor_with_undo_transaction.py" in selectors
    assert "tests/test_plugin_reload_recovery.py" in selectors
    assert "tests/test_plugin_containment_and_caps.py" in selectors
    assert "tests/test_editor_mx_commands_and_completion.py" not in selectors
    assert "tests/test_mxdoctor.py" in selectors
    assert not any(target.startswith("tests/test_mxtest.py::") for target in selectors)
    assert "tests/test_docs_index.py" in selectors
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


def test_mxdoctor_chunked_command_uses_resumable_mxtest_manifest() -> None:
    module = _load_mxdoctor_module()

    cmd = module.chunked_command(chunks=3)

    assert cmd[:3] == [module.sys.executable, "tools/mxtest.py", "--run-chunks"]
    assert "3" in cmd
    assert "--strategy" in cmd
    assert "segment" in cmd
    assert "--isolate-files" in cmd
    assert "--resume" in cmd
    assert ".artifacts/mxtest-all.json" in cmd


def test_mxdoctor_default_runs_bounded_preflight(monkeypatch) -> None:
    module = _load_mxdoctor_module()
    calls: list[list[str]] = []

    monkeypatch.setattr(module, "check_stdlib_resource", lambda: 0)
    monkeypatch.setattr(module, "warn_about_transient_caches", lambda: None)
    monkeypatch.setattr(module, "report_optional_tools", lambda: None)
    monkeypatch.setattr(module.platform, "platform", lambda: "test-platform")

    def fake_run(cmd: list[str], *, env: dict[str, str] | None = None) -> int:
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

    def fake_run(cmd: list[str], *, env: dict[str, str] | None = None) -> int:
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

    def fake_run(cmd: list[str], *, env: dict[str, str] | None = None) -> int:
        calls.append(list(cmd))
        return 0

    monkeypatch.setattr(module, "run", fake_run)

    rc = module.main(["--chunked", "--chunks", "5"])

    assert rc == 0
    assert calls[1] == module.chunked_command(chunks=5)


def test_fast_targets_include_fs_save_boundary():
    from tools import mxdoctor
    assert "tests/test_editor_fs_open_save.py" in mxdoctor.FAST_PYTEST_TARGETS


def test_fast_targets_include_readonly_hostcall_boundary():
    from tools import mxdoctor
    assert "tests/test_editor_readonly_option.py" in mxdoctor.FAST_PYTEST_TARGETS
