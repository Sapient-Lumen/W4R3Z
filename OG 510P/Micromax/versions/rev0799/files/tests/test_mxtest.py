from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load_mxtest_module():
    spec = importlib.util.spec_from_file_location("mxtest_test_module", ROOT / "tools" / "mxtest.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_parse_chunk_spec_accepts_one_based_index() -> None:
    module = _load_mxtest_module()

    assert module.parse_chunk_spec("1/8") == (1, 8)
    assert module.parse_chunk_spec(" 8 / 8 ") == (8, 8)


@pytest.mark.parametrize("spec", ["0/8", "9/8", "1/0", "one/eight", "1"])
def test_parse_chunk_spec_rejects_bad_chunks(spec: str) -> None:
    module = _load_mxtest_module()

    with pytest.raises(module.UsageError):
        module.parse_chunk_spec(spec)


def test_select_chunk_balances_contiguous_slices() -> None:
    module = _load_mxtest_module()
    items = [f"test_{i}" for i in range(10)]

    assert module.select_chunk(items, index=1, total=3) == ["test_0", "test_1", "test_2", "test_3"]
    assert module.select_chunk(items, index=2, total=3) == ["test_4", "test_5", "test_6"]
    assert module.select_chunk(items, index=3, total=3) == ["test_7", "test_8", "test_9"]
    assert module.chunk_counts(10, 3) == [4, 3, 3]


def test_isolated_pytest_env_disables_plugin_autoload_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_mxtest_module()
    monkeypatch.delenv("PYTEST_DISABLE_PLUGIN_AUTOLOAD", raising=False)
    monkeypatch.delenv("PYTHONDONTWRITEBYTECODE", raising=False)

    env = module.isolated_pytest_env()

    assert env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] == "1"
    assert env["PYTHONDONTWRITEBYTECODE"] == "1"


def test_group_nodeids_by_file_preserves_order() -> None:
    module = _load_mxtest_module()
    nodeids = [
        "tests/a.py::test_one",
        "tests/a.py::test_two",
        "tests/b.py::test_three",
        "tests/b.py::TestClass::test_four",
    ]

    assert module.group_nodeids_by_file(nodeids) == [
        ("tests/a.py", ["tests/a.py::test_one", "tests/a.py::test_two"]),
        ("tests/b.py", ["tests/b.py::test_three", "tests/b.py::TestClass::test_four"]),
    ]


def test_chunk_plan_records_resume_metadata() -> None:
    module = _load_mxtest_module()
    nodeids = [
        "tests/a.py::test_one",
        "tests/a.py::test_two",
        "tests/b.py::test_three",
    ]

    plan = module.chunk_plan(nodeids, 2)

    assert plan[0]["selected"] == 2
    assert plan[0]["file_count"] == 1
    assert plan[0]["first"] == "tests/a.py::test_one"
    assert plan[0]["last"] == "tests/a.py::test_two"
    assert plan[0]["command"] == "python tools/mxtest.py --chunk 1/2 --isolate-files"
    assert plan[1]["files"] == ["tests/b.py"]


def test_mxtest_run_forwards_extra_pytest_args(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_mxtest_module()
    calls: list[tuple[list[str], list[str], int, int | None]] = []

    monkeypatch.setattr(
        module,
        "collect_nodeids",
        lambda pytest_args: ["tests/a.py::test_one", "tests/b.py::test_two"],
    )

    def fake_run(nodeids: list[str], pytest_args: list[str], *, durations: int, timeout: int | None = None) -> int:
        calls.append((nodeids, pytest_args, durations, timeout))
        return 0

    monkeypatch.setattr(module, "run_pytest", fake_run)

    assert module.main(["--chunk", "1/2", "--durations", "0", "--", "-k", "smoke"]) == 0

    assert calls == [(["tests/a.py::test_one"], ["-k", "smoke"], 0, None)]


def test_mxtest_isolated_run_forwards_extra_pytest_args(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_mxtest_module()
    calls: list[tuple[list[str], list[str], int, int | None]] = []

    monkeypatch.setattr(
        module,
        "collect_nodeids",
        lambda pytest_args: ["tests/a.py::test_one", "tests/a.py::test_two"],
    )

    def fake_run(
        nodeids: list[str], pytest_args: list[str], *, durations: int, file_timeout: int | None
    ) -> tuple[int, list[dict[str, object]]]:
        calls.append((nodeids, pytest_args, durations, file_timeout))
        return 0, []

    monkeypatch.setattr(module, "run_pytest_file_isolated", fake_run)

    assert module.main(["--isolate-files", "--file-timeout", "7", "--", "-k", "unit"]) == 0

    assert calls == [(["tests/a.py::test_one", "tests/a.py::test_two"], ["-k", "unit"], 10, 7)]


def test_status_for_returncode_is_stable() -> None:
    module = _load_mxtest_module()

    assert module.status_for_returncode(0) == "passed"
    assert module.status_for_returncode(124) == "timed_out"
    assert module.status_for_returncode(1) == "failed"


def test_build_chunks_file_strategy_keeps_files_whole_and_balances_large_files() -> None:
    module = _load_mxtest_module()
    nodeids = [
        *(f"tests/large.py::test_{i}" for i in range(5)),
        "tests/small_a.py::test_one",
        "tests/small_b.py::test_one",
        "tests/small_c.py::test_one",
    ]

    chunks = module.build_chunks(nodeids, 2, strategy="file")

    files_by_chunk = [
        {filename for filename, _group in module.group_nodeids_by_file(chunk)}
        for chunk in chunks
    ]
    assert files_by_chunk[0].isdisjoint(files_by_chunk[1])
    assert sorted(len(chunk) for chunk in chunks) == [3, 5]
    assert any(chunk == [f"tests/large.py::test_{i}" for i in range(5)] for chunk in chunks)


def test_load_duration_history_keeps_largest_observed_file_duration(tmp_path: Path) -> None:
    module = _load_mxtest_module()
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    first.write_text(
        '{"files":[{"file":"tests/a.py","duration_seconds":1.25},'
        '{"file":"tests/b.py","duration_seconds":2.0}]}\n',
        encoding="utf-8",
    )
    second.write_text(
        '{"files":[{"file":"tests/a.py","duration_seconds":3.5},'
        '{"file":"tests/c.py","duration_seconds":0.5}]}\n',
        encoding="utf-8",
    )

    history = module.load_duration_history([first, second])

    assert history == {"tests/a.py": 3.5, "tests/b.py": 2.0, "tests/c.py": 0.5}


def test_build_chunks_duration_strategy_uses_history_to_isolate_slow_file() -> None:
    module = _load_mxtest_module()
    nodeids = [
        "tests/slow.py::test_one",
        "tests/slow.py::test_two",
        "tests/fast_a.py::test_one",
        "tests/fast_b.py::test_one",
        "tests/fast_c.py::test_one",
    ]

    chunks = module.build_chunks(
        nodeids,
        2,
        strategy="duration",
        duration_history={"tests/slow.py": 60.0, "tests/fast_a.py": 1.0, "tests/fast_b.py": 1.0, "tests/fast_c.py": 1.0},
    )

    files_by_chunk = [
        {filename for filename, _group in module.group_nodeids_by_file(chunk)}
        for chunk in chunks
    ]
    assert {"tests/slow.py"} in files_by_chunk


def test_chunk_plan_records_strategy_weight_and_strategy_command() -> None:
    module = _load_mxtest_module()
    nodeids = [
        "tests/slow.py::test_one",
        "tests/slow.py::test_two",
        "tests/fast.py::test_one",
    ]

    plan = module.chunk_plan(
        nodeids,
        2,
        strategy="duration",
        duration_history={"tests/slow.py": 9.0, "tests/fast.py": 1.0},
        history_paths=[Path(".artifacts/history.json")],
        pytest_args=["-k", "smoke"],
    )

    assert plan[0]["strategy"] == "duration"
    assert plan[0]["strategy_weight_unit"] == "seconds-with-test-count-fallback"
    assert "--strategy duration" in plan[0]["command"]
    assert "--history .artifacts/history.json" in plan[0]["command"]
    assert "-- -k smoke" in plan[0]["command"]


def test_build_chunks_segment_strategy_splits_oversized_file_but_keeps_small_files_whole() -> None:
    module = _load_mxtest_module()
    nodeids = [
        *(f"tests/huge.py::test_{i}" for i in range(10)),
        "tests/small_a.py::test_one",
        "tests/small_b.py::test_one",
    ]

    chunks = module.build_chunks(nodeids, 3, strategy="segment")

    huge_chunk_counts = [sum(1 for nodeid in chunk if nodeid.startswith("tests/huge.py::")) for chunk in chunks]
    assert sorted(huge_chunk_counts) == [3, 3, 4]
    for small_file in ["tests/small_a.py", "tests/small_b.py"]:
        locations = [
            index
            for index, chunk in enumerate(chunks)
            if any(nodeid.startswith(f"{small_file}::") for nodeid in chunk)
        ]
        assert len(locations) == 1


def test_split_pytest_args_for_execution_drops_positional_selectors_but_keeps_options() -> None:
    module = _load_mxtest_module()

    execution, dropped = module.split_pytest_args_for_execution(
        ["tests/test_mxtest.py", "-k", "strategy or history", "--tb=short", "tests/test_other.py::test_x"]
    )

    assert execution == ["-k", "strategy or history", "--tb=short"]
    assert dropped == ["tests/test_mxtest.py", "tests/test_other.py::test_x"]




def test_split_pytest_args_for_collection_drops_output_flags_but_keeps_selectors() -> None:
    module = _load_mxtest_module()

    collection, dropped = module.split_pytest_args_for_collection(
        [
            "tests/test_mxtest.py",
            "-k",
            "manifest or chunk",
            "-vv",
            "--tb=short",
            "--durations",
            "5",
            "--color=yes",
        ]
    )

    assert collection == ["tests/test_mxtest.py", "-k", "manifest or chunk"]
    assert dropped == ["-vv", "--tb=short", "--durations", "5", "--color=yes"]


def test_collect_nodeids_ignores_verbosity_flags_for_stable_quiet_collection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_mxtest_module()
    calls: list[list[str]] = []

    class FakeProcess:
        returncode = 0
        stdout = "tests/a.py::test_one\n"

    def fake_run(cmd, **kwargs):  # type: ignore[no-untyped-def]
        calls.append(list(cmd))
        return FakeProcess()

    monkeypatch.setattr(module.subprocess, "run", fake_run)

    assert module.collect_nodeids(["tests/a.py", "-vv", "--tb=short"]) == ["tests/a.py::test_one"]

    assert calls == [[module.sys.executable, "-m", "pytest", "--collect-only", "-q", "tests/a.py"]]


def test_run_pytest_refuses_empty_nodeid_selection(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_mxtest_module()

    def fail_run(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("empty node-id runs must not invoke pytest")

    monkeypatch.setattr(module.subprocess, "run", fail_run)

    assert module.run_pytest([], [], durations=0) == 5


def test_run_pytest_file_isolated_refuses_empty_nodeid_selection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_mxtest_module()

    def fail_run(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("empty node-id runs must not invoke pytest")

    monkeypatch.setattr(module, "run_pytest", fail_run)

    assert module.run_pytest_file_isolated([], [], durations=0, file_timeout=None) == (5, [])


def test_mxtest_heartbeat_seconds_uses_env(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_mxtest_module()

    monkeypatch.delenv("MXTEST_HEARTBEAT_SECONDS", raising=False)
    assert module.mxtest_heartbeat_seconds() == module.DEFAULT_HEARTBEAT_SECONDS

    monkeypatch.setenv("MXTEST_HEARTBEAT_SECONDS", "0")
    assert module.mxtest_heartbeat_seconds() == 0

    monkeypatch.setenv("MXTEST_HEARTBEAT_SECONDS", "2")
    assert module.mxtest_heartbeat_seconds() == 2

    monkeypatch.setenv("MXTEST_HEARTBEAT_SECONDS", "not-a-number")
    assert module.mxtest_heartbeat_seconds() == module.DEFAULT_HEARTBEAT_SECONDS

    module.configure_mxtest_heartbeat(4)
    assert module.mxtest_heartbeat_seconds() == 4
    module.configure_mxtest_heartbeat(None)
    assert module.mxtest_heartbeat_seconds() == module.DEFAULT_HEARTBEAT_SECONDS


def test_mxtest_child_process_group_kwargs_are_separate_on_posix() -> None:
    module = _load_mxtest_module()

    kwargs = module._child_process_group_kwargs()

    if module.os.name == "posix":
        assert kwargs == {"start_new_session": True}
    else:
        assert "start_new_session" not in kwargs


def test_run_subprocess_with_heartbeat_emits_liveness(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    module = _load_mxtest_module()
    clock = {"now": 0.0}
    calls: list[list[str]] = []

    class FakePopen:
        def __init__(self, cmd, **kwargs):  # type: ignore[no-untyped-def]
            calls.append(list(cmd))

        def poll(self):  # type: ignore[no-untyped-def]
            return 0 if clock["now"] >= 1.2 else None

    def fake_monotonic() -> float:
        return clock["now"]

    def fake_sleep(seconds: float) -> None:
        clock["now"] += float(seconds)

    monkeypatch.setattr(module.subprocess, "Popen", FakePopen)
    monkeypatch.setattr(module.time, "monotonic", fake_monotonic)
    monkeypatch.setattr(module.time, "sleep", fake_sleep)

    rc = module.run_subprocess_with_heartbeat(["pytest"], label="test-child", heartbeat_seconds=1)

    assert rc == 0
    assert calls == [["pytest"]]
    assert "mxtest: still running test-child (1s elapsed)" in capsys.readouterr().err


def test_run_subprocess_with_heartbeat_timeout_kills_child_group(tmp_path: Path) -> None:
    module = _load_mxtest_module()
    if module.os.name != "posix":
        pytest.skip("process-group timeout regression is POSIX-specific")
    marker = tmp_path / "grandchild-lived.txt"
    script = tmp_path / "spawn_grandchild.py"
    script.write_text(
        "import subprocess, sys, time\n"
        f"marker = {str(marker)!r}\n"
        "subprocess.Popen([sys.executable, '-c', "
        "'import pathlib, time; time.sleep(1.5); pathlib.Path(%r).write_text(\"alive\")' % marker])\n"
        "time.sleep(10.0)\n",
        encoding="utf-8",
    )

    rc = module.run_subprocess_with_heartbeat([module.sys.executable, str(script)], timeout=1, heartbeat_seconds=0)
    module.time.sleep(1.8)

    assert rc == 124
    assert not marker.exists()


def test_run_subprocess_with_heartbeat_repolls_before_stale_liveness(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    module = _load_mxtest_module()
    clock = {"now": 0.0}

    class FakePopen:
        def __init__(self, cmd, **kwargs):  # type: ignore[no-untyped-def]
            self.polls = 0

        def poll(self):  # type: ignore[no-untyped-def]
            self.polls += 1
            # First loop sees a live child.  At the heartbeat boundary, the
            # defensive re-poll sees completion and must return without printing
            # a stale "still running" line.
            return None if self.polls == 1 else 0

    def fake_monotonic() -> float:
        return clock["now"]

    def fake_sleep(seconds: float) -> None:
        clock["now"] += float(seconds)

    monkeypatch.setattr(module.subprocess, "Popen", FakePopen)
    monkeypatch.setattr(module.time, "monotonic", fake_monotonic)
    monkeypatch.setattr(module.time, "sleep", fake_sleep)

    rc = module.run_subprocess_with_heartbeat(["pytest"], label="test-child", heartbeat_seconds=1)

    assert rc == 0
    assert "still running" not in capsys.readouterr().err


def test_run_subprocess_with_heartbeat_times_out_and_terminates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_mxtest_module()
    clock = {"now": 0.0}
    events: list[str] = []

    class FakePopen:
        def __init__(self, cmd, **kwargs):  # type: ignore[no-untyped-def]
            events.append("start")
            self.terminated = False
            self.killed = False

        def poll(self):  # type: ignore[no-untyped-def]
            if self.terminated or self.killed:
                return -15
            return None

        def terminate(self) -> None:
            events.append("terminate")
            self.terminated = True

        def kill(self) -> None:
            events.append("kill")
            self.killed = True

        def wait(self) -> None:
            events.append("wait")

    def fake_monotonic() -> float:
        return clock["now"]

    def fake_sleep(seconds: float) -> None:
        clock["now"] += float(seconds)

    monkeypatch.setattr(module.subprocess, "Popen", FakePopen)
    monkeypatch.setattr(module.time, "monotonic", fake_monotonic)
    monkeypatch.setattr(module.time, "sleep", fake_sleep)

    rc = module.run_subprocess_with_heartbeat(["pytest"], timeout=1, heartbeat_seconds=0)

    assert rc == 124
    assert events == ["start", "terminate"]


def test_run_subprocess_with_heartbeat_sigterm_cleans_child_before_exit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_mxtest_module()
    handlers: dict[int, object] = {}
    restored: list[int] = []
    terminated: list[tuple[object, int | None]] = []

    class FakePopen:
        pid = 12345

        def __init__(self, cmd, **kwargs):  # type: ignore[no-untyped-def]
            self.cmd = cmd

        def poll(self):  # type: ignore[no-untyped-def]
            handler = handlers[int(module.signal.SIGTERM)]
            handler(int(module.signal.SIGTERM), None)  # type: ignore[misc]
            raise AssertionError("signal handler should interrupt before poll returns")

    def fake_signal(signum, handler):  # type: ignore[no-untyped-def]
        signum = int(signum)
        if handler == "old-handler":
            restored.append(signum)
        else:
            handlers[signum] = handler
        return "old-handler"

    def fake_getsignal(signum):  # type: ignore[no-untyped-def]
        return "old-handler"

    def fake_terminate(proc, *, timeout=5.0, pgid=None):  # type: ignore[no-untyped-def]
        terminated.append((proc, pgid))

    monkeypatch.setattr(module.subprocess, "Popen", FakePopen)
    monkeypatch.setattr(module.signal, "signal", fake_signal)
    monkeypatch.setattr(module.signal, "getsignal", fake_getsignal)
    monkeypatch.setattr(module, "_confirmed_child_process_group_id", lambda proc: 12345)
    monkeypatch.setattr(module, "_terminate_process", fake_terminate)

    with pytest.raises(module.MxtestInterrupted) as excinfo:
        module.run_subprocess_with_heartbeat(["pytest"], heartbeat_seconds=0)

    assert excinfo.value.signum == int(module.signal.SIGTERM)
    assert terminated == [(terminated[0][0], 12345)]
    assert int(module.signal.SIGTERM) in restored


def test_mxtest_run_chunks_writes_partial_manifest_on_interrupt(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_mxtest_module()
    manifest = tmp_path / "interrupted.json"
    source = _source_fixture(module)
    env = _environment_fixture(module)

    monkeypatch.setattr(module, "collect_nodeids", lambda pytest_args: ["tests/a.py::test_one"])
    monkeypatch.setattr(module, "source_manifest_payload", lambda: dict(source))
    monkeypatch.setattr(module, "environment_manifest_payload", lambda: dict(env))

    def interrupt(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise module.MxtestInterrupted(int(module.signal.SIGTERM))

    monkeypatch.setattr(module, "run_pytest", interrupt)

    rc = module.main(["--run-chunks", "1", "--json", str(manifest), "--durations", "0"])

    payload = __import__("json").loads(manifest.read_text(encoding="utf-8"))
    assert rc == 128 + int(module.signal.SIGTERM)
    assert payload["status"] == "partial"
    assert payload["complete"] is False
    assert payload["returncode"] == 1
    assert payload["chunk_results"][0]["status"] == "partial"
    assert payload["chunk_results"][0]["interrupted"] is True
    assert payload["chunk_results"][0]["signal"] == "SIGTERM"


def test_mxtest_plan_records_heartbeat_seconds(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_mxtest_module()
    json_path = tmp_path / "plan.json"

    monkeypatch.setenv("MXTEST_HEARTBEAT_SECONDS", "3")
    monkeypatch.setattr(module, "collect_nodeids", lambda pytest_args: ["tests/a.py::test_one"])

    assert module.main(["--plan", "--json", str(json_path), "--durations", "0"]) == 0

    payload = __import__("json").loads(json_path.read_text(encoding="utf-8"))
    assert payload["heartbeat_seconds"] == 3


def test_write_json_summary_writes_complete_manifest_and_no_temp_file(tmp_path: Path) -> None:
    module = _load_mxtest_module()
    path = tmp_path / "summary.json"

    module.write_json_summary(path, {"ok": True, "items": [1, 2]})

    assert __import__("json").loads(path.read_text(encoding="utf-8")) == {"ok": True, "items": [1, 2]}
    assert list(tmp_path.glob(".summary.json.*.tmp")) == []


def test_write_json_summary_preserves_previous_manifest_when_replace_fails(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_mxtest_module()
    path = tmp_path / "summary.json"
    module.write_json_summary(path, {"old": True})
    original = path.read_text(encoding="utf-8")
    replace_calls: list[tuple[str, str]] = []

    def fail_replace(src: str, dst: str) -> None:
        replace_calls.append((src, dst))
        raise OSError("simulated replace failure")

    monkeypatch.setattr(module.os, "replace", fail_replace)

    with pytest.raises(OSError):
        module.write_json_summary(path, {"new": True})

    assert replace_calls
    assert path.read_text(encoding="utf-8") == original
    assert list(tmp_path.glob(".summary.json.*.tmp")) == []


def test_mxtest_run_drops_positional_selectors_after_collection(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_mxtest_module()
    collected_args: list[list[str]] = []
    run_calls: list[tuple[list[str], list[str], int, int | None]] = []

    def fake_collect(pytest_args: list[str]) -> list[str]:
        collected_args.append(pytest_args)
        return ["tests/a.py::test_one", "tests/a.py::test_two"]

    def fake_run(nodeids: list[str], pytest_args: list[str], *, durations: int, timeout: int | None = None) -> int:
        run_calls.append((nodeids, pytest_args, durations, timeout))
        return 0

    monkeypatch.setattr(module, "collect_nodeids", fake_collect)
    monkeypatch.setattr(module, "run_pytest", fake_run)

    assert module.main(["--chunk", "1/2", "--durations", "0", "--", "tests/a.py", "-k", "smoke"]) == 0

    assert collected_args == [["tests/a.py", "-k", "smoke"]]
    assert run_calls == [(["tests/a.py::test_one"], ["-k", "smoke"], 0, None)]




def test_mxtest_empty_chunk_skips_pytest_without_failing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_mxtest_module()
    json_path = tmp_path / "empty-chunk.json"

    monkeypatch.setattr(
        module,
        "collect_nodeids",
        lambda pytest_args: ["tests/a.py::test_one", "tests/a.py::test_two"],
    )

    def fail_run(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("empty chunks must not invoke pytest")

    monkeypatch.setattr(module, "run_pytest", fail_run)

    assert module.main(["--chunk", "4/8", "--json", str(json_path), "--durations", "0"]) == 0
    payload = __import__("json").loads(json_path.read_text(encoding="utf-8"))
    assert payload["selected"] == 0
    assert payload["status"] == "passed"
    assert payload["skipped"] is True
    assert payload["skip_reason"] == "empty-chunk-selection"


def test_mxtest_run_chunks_records_empty_chunks_as_skipped_passes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_mxtest_module()
    manifest = tmp_path / "mxtest-all.json"
    calls: list[list[str]] = []

    monkeypatch.setattr(
        module,
        "collect_nodeids",
        lambda pytest_args: ["tests/a.py::test_one", "tests/a.py::test_two"],
    )

    def fake_run(nodeids: list[str], pytest_args: list[str], *, durations: int, timeout: int | None = None) -> int:
        calls.append(list(nodeids))
        return 0

    monkeypatch.setattr(module, "run_pytest", fake_run)

    assert module.main(["--run-chunks", "4", "--json", str(manifest), "--durations", "0"]) == 0
    payload = __import__("json").loads(manifest.read_text(encoding="utf-8"))
    assert payload["status"] == "passed"
    assert payload["complete"] is True
    assert calls == [["tests/a.py::test_one"], ["tests/a.py::test_two"]]
    assert [record["selected"] for record in payload["chunk_results"]] == [1, 1, 0, 0]
    assert [record["skipped"] for record in payload["chunk_results"]] == [False, False, True, True]


def test_mxtest_cli_heartbeat_overrides_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    module = _load_mxtest_module()
    json_path = tmp_path / "heartbeat-cli-plan.json"

    monkeypatch.setenv("MXTEST_HEARTBEAT_SECONDS", "99")
    monkeypatch.setattr(module, "collect_nodeids", lambda pytest_args: ["tests/a.py::test_one"])

    assert module.main(["--plan", "--json", str(json_path), "--heartbeat", "5", "--durations", "0"]) == 0

    payload = __import__("json").loads(json_path.read_text(encoding="utf-8"))
    assert payload["heartbeat_seconds"] == 5



def test_mxtest_single_run_forwards_chunk_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_mxtest_module()
    calls: list[int | None] = []

    monkeypatch.setattr(module, "collect_nodeids", lambda pytest_args: ["tests/a.py::test_one"])

    def fake_run(nodeids: list[str], pytest_args: list[str], *, durations: int, timeout: int | None = None) -> int:
        calls.append(timeout)
        return 0

    monkeypatch.setattr(module, "run_pytest", fake_run)

    assert module.main(["--chunk-timeout", "9", "--durations", "0"]) == 0

    assert calls == [9]


def test_mxtest_run_chunks_forwards_chunk_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_mxtest_module()
    calls: list[int | None] = []

    monkeypatch.setattr(
        module,
        "collect_nodeids",
        lambda pytest_args: ["tests/a.py::test_one", "tests/b.py::test_two"],
    )

    def fake_run(nodeids: list[str], pytest_args: list[str], *, durations: int, timeout: int | None = None) -> int:
        calls.append(timeout)
        return 0

    monkeypatch.setattr(module, "run_pytest", fake_run)

    assert module.main(["--run-chunks", "2", "--chunk-timeout", "11", "--durations", "0"]) == 0

    assert calls == [11, 11]


def test_mxtest_plan_records_chunk_timeout(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    module = _load_mxtest_module()
    json_path = tmp_path / "timeout-plan.json"

    monkeypatch.setattr(module, "collect_nodeids", lambda pytest_args: ["tests/a.py::test_one"])

    assert module.main(["--plan", "--json", str(json_path), "--chunk-timeout", "13", "--durations", "0"]) == 0

    payload = __import__("json").loads(json_path.read_text(encoding="utf-8"))
    assert payload["chunk_timeout_seconds"] == 13
    assert payload["file_timeout_seconds"] is None



def test_mxtest_run_chunks_writes_running_checkpoint_before_pytest(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_mxtest_module()
    manifest = tmp_path / "mxtest-all.json"
    observed_statuses: list[str] = []

    monkeypatch.setattr(module, "collect_nodeids", lambda pytest_args: ["tests/a.py::test_one"])

    def fake_run(nodeids: list[str], pytest_args: list[str], *, durations: int, timeout: int | None = None) -> int:
        payload = __import__("json").loads(manifest.read_text(encoding="utf-8"))
        observed_statuses.append(str(payload["chunk_results"][0]["status"]))
        assert payload["chunk_results"][0]["checkpoint_reason"] == "chunk-started"
        assert payload["complete"] is False
        assert payload["status"] == "partial"
        return 0

    monkeypatch.setattr(module, "run_pytest", fake_run)

    assert module.main(["--run-chunks", "1", "--json", str(manifest), "--durations", "0"]) == 0

    assert observed_statuses == ["running"]
    final_payload = __import__("json").loads(manifest.read_text(encoding="utf-8"))
    assert final_payload["chunk_results"][0]["status"] == "passed"
    assert "checkpoint_reason" not in final_payload["chunk_results"][0]
    assert final_payload["complete"] is True



def test_verify_manifest_treats_running_checkpoint_as_incomplete() -> None:
    module = _load_mxtest_module()
    record = module.chunk_selection_payload(
        selected=["tests/a.py::test_one"],
        index=1,
        total=1,
        strategy="node",
        duration_history={},
    )
    record.update({"status": "running", "returncode": None})
    payload = {
        "mode": "run-chunks",
        "run_chunks": 1,
        "chunk_results": [record],
        "status": "partial",
        "complete": False,
    }

    rc, lines, issues = module.verify_manifest_payload(payload)

    assert rc == 1
    assert not issues
    assert "status: partial" in lines
    assert "complete: false" in lines




def test_verify_manifest_accepts_interrupted_prefix_checkpoint_as_partial() -> None:
    module = _load_mxtest_module()
    record = module.chunk_selection_payload(
        selected=["tests/a.py::test_one"],
        index=1,
        total=2,
        strategy="node",
        duration_history={},
    )
    record.update({"status": "running", "returncode": None})
    payload = {
        "mode": "run-chunks",
        "run_chunks": 2,
        "chunk_results": [record],
        "status": "partial",
        "complete": False,
    }

    rc, lines, issues = module.verify_manifest_payload(payload)

    assert rc == 1
    assert issues == []
    assert "status: partial" in lines
    assert "complete: false" in lines



def test_nodeids_digest_is_order_sensitive() -> None:
    module = _load_mxtest_module()

    assert module.nodeids_digest(["tests/a.py::test_one", "tests/b.py::test_two"]) == module.nodeids_digest(
        ["tests/a.py::test_one", "tests/b.py::test_two"]
    )
    assert module.nodeids_digest(["tests/a.py::test_one", "tests/b.py::test_two"]) != module.nodeids_digest(
        ["tests/b.py::test_two", "tests/a.py::test_one"]
    )


def test_chunk_plan_records_nodeid_digest() -> None:
    module = _load_mxtest_module()
    nodeids = ["tests/a.py::test_one", "tests/b.py::test_two"]

    plan = module.chunk_plan(nodeids, 2)

    assert plan[0]["nodeids_digest"] == module.nodeids_digest(["tests/a.py::test_one"])
    assert plan[1]["nodeids_digest"] == module.nodeids_digest(["tests/b.py::test_two"])


def test_source_manifest_digest_is_content_and_path_sensitive() -> None:
    module = _load_mxtest_module()
    first = [
        {"path": "tests/a.py", "size": 3, "sha256": "a" * 64},
        {"path": "src/micromax/vm.py", "size": 5, "sha256": "b" * 64},
    ]
    reordered = list(reversed(first))
    changed = [
        {"path": "tests/a.py", "size": 3, "sha256": "a" * 64},
        {"path": "src/micromax/vm.py", "size": 5, "sha256": "c" * 64},
    ]

    assert module.source_manifest_digest(first) == module.source_manifest_digest(reordered)
    assert module.source_manifest_digest(first) != module.source_manifest_digest(changed)


def test_source_manifest_issues_rejects_tampered_digest() -> None:
    module = _load_mxtest_module()
    files = [{"path": "tests/a.py", "size": 3, "sha256": "a" * 64}]
    payload = {
        "source_digest": "not-the-real-digest",
        "source_manifest": {
            "schema": module.SOURCE_MANIFEST_SCHEMA,
            "algorithm": "sha256",
            "digest": "not-the-real-digest",
            "file_count": 1,
            "total_bytes": 3,
            "files": files,
        },
    }

    issues = module.source_manifest_issues(payload)

    assert any("source_manifest digest" in issue for issue in issues)


def test_run_chunks_executes_all_chunks_and_writes_aggregate_manifest(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_mxtest_module()
    manifest = tmp_path / "mxtest-all.json"
    calls: list[list[str]] = []

    monkeypatch.setattr(
        module,
        "collect_nodeids",
        lambda pytest_args: [
            "tests/a.py::test_one",
            "tests/a.py::test_two",
            "tests/b.py::test_three",
            "tests/b.py::test_four",
        ],
    )

    def fake_run(
        nodeids: list[str], pytest_args: list[str], *, durations: int, file_timeout: int | None
    ) -> tuple[int, list[dict[str, object]]]:
        calls.append(list(nodeids))
        return 0, [
            {
                "file": nodeids[0].split("::", 1)[0],
                "selected": len(nodeids),
                "returncode": 0,
                "duration_seconds": 0.01,
                "timed_out": False,
                "status": "passed",
            }
        ]

    monkeypatch.setattr(module, "run_pytest_file_isolated", fake_run)

    assert module.main(["--run-chunks", "2", "--isolate-files", "--json", str(manifest), "--durations", "0"]) == 0

    payload = __import__("json").loads(manifest.read_text(encoding="utf-8"))
    assert payload["mode"] == "run-chunks"
    assert payload["status"] == "passed"
    assert payload["complete"] is True
    assert payload["chunks"] == [2, 2]
    assert [record["chunk"]["index"] for record in payload["chunk_results"]] == [1, 2]
    assert all(record["nodeids_digest"] for record in payload["chunk_results"])
    assert calls == [
        ["tests/a.py::test_one", "tests/a.py::test_two"],
        ["tests/b.py::test_three", "tests/b.py::test_four"],
    ]


def test_run_chunks_resume_skips_previously_passed_matching_chunk(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_mxtest_module()
    manifest = tmp_path / "mxtest-all.json"
    fixed_source = {
        "schema": module.SOURCE_MANIFEST_SCHEMA,
        "algorithm": "sha256",
        "digest": "source-digest",
        "file_count": 0,
        "total_bytes": 0,
        "files": [],
    }
    fixed_environment = _environment_fixture(module)
    monkeypatch.setattr(module, "source_manifest_payload", lambda: dict(fixed_source))
    monkeypatch.setattr(module, "environment_manifest_payload", lambda: dict(fixed_environment))
    nodeids = ["tests/a.py::test_one", "tests/b.py::test_two"]
    first_chunk = [nodeids[0]]
    previous_record = module.chunk_selection_payload(
        selected=first_chunk,
        index=1,
        total=2,
        strategy="node",
        duration_history={},
    )
    previous_record.update(
        {
            "returncode": 0,
            "status": "passed",
            "duration_seconds": 0.5,
            "resumed": False,
            "skipped": False,
        }
    )
    manifest.write_text(
        __import__("json").dumps(
            {
                "source_digest": "source-digest",
                "source_manifest": fixed_source,
                "environment_digest": fixed_environment["digest"],
                "environment_manifest": fixed_environment,
                "chunk_results": [previous_record],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    calls: list[list[str]] = []

    monkeypatch.setattr(module, "collect_nodeids", lambda pytest_args: list(nodeids))

    def fake_run(
        nodeids: list[str], pytest_args: list[str], *, durations: int, timeout: int | None = None
    ) -> int:
        calls.append(list(nodeids))
        return 0

    monkeypatch.setattr(module, "run_pytest", fake_run)

    assert module.main(["--run-chunks", "2", "--resume", "--json", str(manifest), "--durations", "0"]) == 0

    payload = __import__("json").loads(manifest.read_text(encoding="utf-8"))
    assert payload["status"] == "passed"
    assert payload["chunk_results"][0]["resumed"] is True
    assert payload["chunk_results"][0]["skipped"] is True
    assert payload["chunk_results"][1]["resumed"] is False
    assert calls == [["tests/b.py::test_two"]]


def test_run_chunks_resume_refuses_matching_chunk_when_source_digest_changed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_mxtest_module()
    manifest = tmp_path / "mxtest-all.json"
    current_source = {
        "schema": module.SOURCE_MANIFEST_SCHEMA,
        "algorithm": "sha256",
        "digest": "new-source",
        "file_count": 0,
        "total_bytes": 0,
        "files": [],
    }
    fixed_environment = _environment_fixture(module)
    monkeypatch.setattr(module, "source_manifest_payload", lambda: dict(current_source))
    monkeypatch.setattr(module, "environment_manifest_payload", lambda: dict(fixed_environment))
    nodeids = ["tests/a.py::test_one", "tests/b.py::test_two"]
    previous_record = module.chunk_selection_payload(
        selected=[nodeids[0]],
        index=1,
        total=2,
        strategy="node",
        duration_history={},
    )
    previous_record.update({"returncode": 0, "status": "passed", "duration_seconds": 0.5})
    manifest.write_text(
        __import__("json").dumps(
            {
                "source_digest": "old-source",
                "environment_digest": fixed_environment["digest"],
                "environment_manifest": fixed_environment,
                "chunk_results": [previous_record],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    calls: list[list[str]] = []

    monkeypatch.setattr(module, "collect_nodeids", lambda pytest_args: list(nodeids))

    def fake_run(nodeids: list[str], pytest_args: list[str], *, durations: int, timeout: int | None = None) -> int:
        calls.append(list(nodeids))
        return 0

    monkeypatch.setattr(module, "run_pytest", fake_run)

    assert module.main(["--run-chunks", "2", "--resume", "--json", str(manifest), "--durations", "0"]) == 0

    assert calls == [["tests/a.py::test_one"], ["tests/b.py::test_two"]]


def test_run_chunks_resume_refuses_matching_chunk_when_environment_digest_changed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_mxtest_module()
    manifest = tmp_path / "mxtest-all.json"
    fixed_source = {
        "schema": module.SOURCE_MANIFEST_SCHEMA,
        "algorithm": "sha256",
        "digest": "source-digest",
        "file_count": 0,
        "total_bytes": 0,
        "files": [],
    }
    old_environment = _environment_fixture(module, python_version="3.11.0")
    current_environment = _environment_fixture(module, python_version="3.12.0")
    monkeypatch.setattr(module, "source_manifest_payload", lambda: dict(fixed_source))
    monkeypatch.setattr(module, "environment_manifest_payload", lambda: dict(current_environment))
    nodeids = ["tests/a.py::test_one", "tests/b.py::test_two"]
    previous_record = module.chunk_selection_payload(
        selected=[nodeids[0]],
        index=1,
        total=2,
        strategy="node",
        duration_history={},
    )
    previous_record.update({"returncode": 0, "status": "passed", "duration_seconds": 0.5})
    manifest.write_text(
        __import__("json").dumps(
            {
                "source_digest": "source-digest",
                "source_manifest": fixed_source,
                "environment_digest": old_environment["digest"],
                "environment_manifest": old_environment,
                "chunk_results": [previous_record],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    calls: list[list[str]] = []

    monkeypatch.setattr(module, "collect_nodeids", lambda pytest_args: list(nodeids))

    def fake_run(nodeids: list[str], pytest_args: list[str], *, durations: int, timeout: int | None = None) -> int:
        calls.append(list(nodeids))
        return 0

    monkeypatch.setattr(module, "run_pytest", fake_run)

    assert module.main(["--run-chunks", "2", "--resume", "--json", str(manifest), "--durations", "0"]) == 0

    assert calls == [["tests/a.py::test_one"], ["tests/b.py::test_two"]]


def test_verify_manifest_payload_accepts_complete_passed_manifest() -> None:
    module = _load_mxtest_module()
    nodeids = ["tests/a.py::test_one", "tests/b.py::test_two"]
    records = []
    for index, selected in enumerate([[nodeids[0]], [nodeids[1]]], start=1):
        record = module.chunk_selection_payload(
            selected=selected,
            index=index,
            total=2,
            strategy="node",
            duration_history={},
        )
        record.update({"returncode": 0, "status": "passed", "duration_seconds": 0.1})
        records.append(record)

    rc, lines, issues = module.verify_manifest_payload(
        {
            "mode": "run-chunks",
            "run_chunks": 2,
            "chunk_results": records,
            "status": "passed",
            "complete": True,
        }
    )

    assert rc == 0
    assert issues == []
    assert "status: passed" in lines


def test_verify_manifest_payload_rejects_stale_status() -> None:
    module = _load_mxtest_module()
    record = module.chunk_selection_payload(
        selected=["tests/a.py::test_one"],
        index=1,
        total=1,
        strategy="node",
        duration_history={},
    )
    record.update({"returncode": 1, "status": "failed", "duration_seconds": 0.1})

    rc, lines, issues = module.verify_manifest_payload(
        {
            "mode": "run-chunks",
            "run_chunks": 1,
            "chunk_results": [record],
            "status": "passed",
            "complete": True,
        }
    )

    assert rc == 2
    assert any("does not match computed" in issue for issue in issues)
    assert "issues:" in lines


def test_verify_manifest_cli_does_not_collect_tests(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    module = _load_mxtest_module()
    manifest = tmp_path / "mxtest-all.json"
    record = module.chunk_selection_payload(
        selected=["tests/a.py::test_one"],
        index=1,
        total=1,
        strategy="node",
        duration_history={},
    )
    record.update({"returncode": 0, "status": "passed", "duration_seconds": 0.1})
    manifest.write_text(
        __import__("json").dumps(
            {
                "mode": "run-chunks",
                "run_chunks": 1,
                "chunk_results": [record],
                "status": "passed",
                "complete": True,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    def fail_collect(pytest_args: list[str]) -> list[str]:
        raise AssertionError("verify should not collect tests")

    monkeypatch.setattr(module, "collect_nodeids", fail_collect)

    assert module.main(["--verify-manifest", str(manifest)]) == 0


def test_load_duration_history_reads_all_chunks_aggregate_file_rows(tmp_path: Path) -> None:
    module = _load_mxtest_module()
    aggregate = tmp_path / "mxtest-all.json"
    aggregate.write_text(
        __import__("json").dumps(
            {
                "mode": "run-chunks",
                "chunk_results": [
                    {
                        "chunk": {"index": 1, "total": 2},
                        "files": [
                            {"file": "tests/a.py", "duration_seconds": 1.25},
                            {"file": "tests/b.py", "duration_seconds": 2.0},
                        ],
                    },
                    {
                        "chunk": {"index": 2, "total": 2},
                        "files": [
                            {"file": "tests/a.py", "duration_seconds": 1.75},
                            {"file": "tests/c.py", "duration_seconds": 0.5},
                        ],
                    },
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    history = module.load_duration_history([aggregate])

    assert history == {"tests/a.py": 1.75, "tests/b.py": 2.0, "tests/c.py": 0.5}


def test_diff_manifest_payload_reports_summary_and_chunk_digest_changes() -> None:
    module = _load_mxtest_module()
    old_record = module.chunk_selection_payload(
        selected=["tests/a.py::test_one"],
        index=1,
        total=1,
        strategy="node",
        duration_history={},
    )
    old_record.update({"returncode": 0, "status": "passed", "duration_seconds": 0.1})
    new_record = module.chunk_selection_payload(
        selected=["tests/a.py::test_one", "tests/b.py::test_two"],
        index=1,
        total=1,
        strategy="node",
        duration_history={},
    )
    new_record.update({"returncode": 0, "status": "passed", "duration_seconds": 0.2})

    rc, lines, payload = module.diff_manifest_payloads(
        {
            "mode": "run-chunks",
            "run_chunks": 1,
            "collected": 1,
            "selected": 1,
            "status": "passed",
            "complete": True,
            "nodeids_digest": module.nodeids_digest(["tests/a.py::test_one"]),
            "chunk_results": [old_record],
        },
        {
            "mode": "run-chunks",
            "run_chunks": 1,
            "collected": 2,
            "selected": 2,
            "status": "passed",
            "complete": True,
            "nodeids_digest": module.nodeids_digest(["tests/a.py::test_one", "tests/b.py::test_two"]),
            "chunk_results": [new_record],
        },
    )

    assert rc == 1
    assert payload["same"] is False
    assert payload["difference_count"] >= 3
    assert any(diff["field"] == "nodeids_digest" for diff in payload["differences"])
    assert any(diff["field"] == "chunk[1].nodeids_digest" for diff in payload["differences"])
    assert lines[0].startswith("mxtest manifest diff:")


def test_diff_manifest_payload_reports_source_file_changes() -> None:
    module = _load_mxtest_module()
    old_files = [
        {"path": "src/micromax/vm.py", "size": 3, "sha256": "a" * 64},
        {"path": "tests/old.py", "size": 1, "sha256": "b" * 64},
    ]
    new_files = [
        {"path": "src/micromax/vm.py", "size": 4, "sha256": "c" * 64},
        {"path": "tests/new.py", "size": 1, "sha256": "d" * 64},
    ]
    old_source = {"digest": module.source_manifest_digest(old_files), "files": old_files}
    new_source = {"digest": module.source_manifest_digest(new_files), "files": new_files}

    rc, lines, payload = module.diff_manifest_payloads(
        {
            "mode": "run-chunks",
            "run_chunks": 1,
            "source_digest": old_source["digest"],
            "source_manifest": old_source,
            "chunk_results": [],
        },
        {
            "mode": "run-chunks",
            "run_chunks": 1,
            "source_digest": new_source["digest"],
            "source_manifest": new_source,
            "chunk_results": [],
        },
    )

    assert rc == 1
    assert payload["source_differences"]["changed"] == ["src/micromax/vm.py"]
    assert payload["source_differences"]["added"] == ["tests/new.py"]
    assert payload["source_differences"]["removed"] == ["tests/old.py"]
    assert any(line.startswith("source files:") for line in lines)


def test_diff_manifest_cli_does_not_collect_tests(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    module = _load_mxtest_module()
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    payload = {
        "mode": "run-chunks",
        "run_chunks": 1,
        "collected": 1,
        "selected": 1,
        "status": "passed",
        "complete": True,
        "chunk_results": [],
    }
    first.write_text(__import__("json").dumps(payload) + "\n", encoding="utf-8")
    second.write_text(__import__("json").dumps(payload) + "\n", encoding="utf-8")

    def fail_collect(pytest_args: list[str]) -> list[str]:
        raise AssertionError("diff should not collect tests")

    monkeypatch.setattr(module, "collect_nodeids", fail_collect)

    assert module.main(["--diff-manifests", str(first), str(second)]) == 0


def test_recommend_chunks_payload_uses_file_history_and_duration_strategy() -> None:
    module = _load_mxtest_module()
    payload = {
        "mode": "run-chunks",
        "run_chunks": 2,
        "strategy": "segment",
        "status": "passed",
        "complete": True,
        "chunk_results": [
            {
                "chunk": {"index": 1, "total": 2},
                "status": "passed",
                "duration_seconds": 20.0,
                "files": [{"file": "tests/a.py", "duration_seconds": 20.0}],
            },
            {
                "chunk": {"index": 2, "total": 2},
                "status": "passed",
                "duration_seconds": 10.0,
                "files": [{"file": "tests/b.py", "duration_seconds": 10.0}],
            },
        ],
    }

    rc, lines, result = module.recommend_chunks_payload(
        payload,
        source_path=Path(".artifacts/mxtest-all.json"),
        target_seconds=10.0,
        min_chunks=1,
        max_chunks=8,
    )

    assert rc == 0
    assert result["recommended_chunks"] == 3
    assert result["recommended_strategy"] == "duration"
    assert result["history_file_count"] == 2
    assert "--strategy duration" in result["command"]
    assert "--history .artifacts/mxtest-all.json" in result["command"]
    assert any("per-file durations" in note for note in result["notes"])
    assert lines[0].startswith("mxtest recommendation:")


def test_recommend_chunks_cli_does_not_collect_tests(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    module = _load_mxtest_module()
    manifest = tmp_path / "mxtest-all.json"
    manifest.write_text(
        __import__("json").dumps(
            {
                "mode": "run-chunks",
                "run_chunks": 1,
                "strategy": "segment",
                "status": "passed",
                "complete": True,
                "chunk_results": [{"chunk": {"index": 1, "total": 1}, "status": "passed", "duration_seconds": 1.0}],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    def fail_collect(pytest_args: list[str]) -> list[str]:
        raise AssertionError("recommend should not collect tests")

    monkeypatch.setattr(module, "collect_nodeids", fail_collect)

    assert module.main(["--recommend-chunks", str(manifest), "--target-seconds", "1", "--max-chunks", "4"]) == 0


def test_verify_current_source_payload_accepts_matching_source_manifest() -> None:
    module = _load_mxtest_module()
    files = [{"path": "tests/a.py", "size": 3, "sha256": "a" * 64}]
    source = {
        "schema": module.SOURCE_MANIFEST_SCHEMA,
        "algorithm": "sha256",
        "digest": module.source_manifest_digest(files),
        "file_count": 1,
        "total_bytes": 3,
        "files": files,
    }
    manifest = {
        "source_digest": source["digest"],
        "source_file_count": source["file_count"],
        "source_total_bytes": source["total_bytes"],
        "source_manifest": source,
    }

    rc, lines, payload = module.verify_current_source_payload(manifest, current_source=source)

    assert rc == 0
    assert payload["matches_current_source"] is True
    assert payload["issues"] == []
    assert "matches: true" in lines


def test_verify_current_source_payload_reports_current_tree_drift() -> None:
    module = _load_mxtest_module()
    old_files = [
        {"path": "tests/a.py", "size": 3, "sha256": "a" * 64},
        {"path": "tests/old.py", "size": 1, "sha256": "b" * 64},
    ]
    new_files = [
        {"path": "tests/a.py", "size": 4, "sha256": "c" * 64},
        {"path": "tests/new.py", "size": 1, "sha256": "d" * 64},
    ]
    old_source = {
        "schema": module.SOURCE_MANIFEST_SCHEMA,
        "algorithm": "sha256",
        "digest": module.source_manifest_digest(old_files),
        "file_count": 2,
        "total_bytes": 4,
        "files": old_files,
    }
    current_source = {
        "schema": module.SOURCE_MANIFEST_SCHEMA,
        "algorithm": "sha256",
        "digest": module.source_manifest_digest(new_files),
        "file_count": 2,
        "total_bytes": 5,
        "files": new_files,
    }

    rc, lines, payload = module.verify_current_source_payload(
        {"source_digest": old_source["digest"], "source_manifest": old_source},
        current_source=current_source,
    )

    assert rc == 1
    assert payload["matches_current_source"] is False
    assert payload["source_differences"]["changed"] == ["tests/a.py"]
    assert payload["source_differences"]["added"] == ["tests/new.py"]
    assert payload["source_differences"]["removed"] == ["tests/old.py"]
    assert any("does not match current source" in issue for issue in payload["issues"])
    assert any(line.startswith("source files:") for line in lines)


def test_verify_current_source_cli_does_not_collect_tests(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_mxtest_module()
    manifest_path = tmp_path / "mxtest-all.json"
    json_path = tmp_path / "current-source.json"
    files = [{"path": "tests/a.py", "size": 3, "sha256": "a" * 64}]
    source = {
        "schema": module.SOURCE_MANIFEST_SCHEMA,
        "algorithm": "sha256",
        "digest": module.source_manifest_digest(files),
        "file_count": 1,
        "total_bytes": 3,
        "files": files,
    }
    manifest_path.write_text(
        __import__("json").dumps(
            {
                "mode": "run-chunks",
                "source_digest": source["digest"],
                "source_file_count": source["file_count"],
                "source_total_bytes": source["total_bytes"],
                "source_manifest": source,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    def fail_collect(pytest_args: list[str]) -> list[str]:
        raise AssertionError("current-source verification should not collect tests")

    monkeypatch.setattr(module, "collect_nodeids", fail_collect)
    monkeypatch.setattr(module, "source_manifest_payload", lambda: dict(source))

    assert module.main(["--verify-current-source", str(manifest_path), "--json", str(json_path)]) == 0
    payload = __import__("json").loads(json_path.read_text(encoding="utf-8"))
    assert payload["mode"] == "verify-current-source"
    assert payload["matches_current_source"] is True


def _environment_fixture(module, *, python_version: str = "3.11.0", pytest_version: str = "8.0.0") -> dict[str, object]:
    manifest: dict[str, object] = {
        "schema": module.ENVIRONMENT_MANIFEST_SCHEMA,
        "algorithm": "sha256-json",
        "python": {
            "implementation": "CPython",
            "version": python_version,
            "version_info": [3, 11, 0, "final", 0],
            "executable": "/usr/bin/python3",
        },
        "platform": {
            "system": "Linux",
            "release": "test-release",
            "version": "test-version",
            "machine": "x86_64",
            "processor": "x86_64",
        },
        "pytest": {
            "version": pytest_version,
            "disable_plugin_autoload": "1",
        },
        "packages": [{"name": "pytest", "version": pytest_version}],
        "env": {"PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1", "PYTHONDONTWRITEBYTECODE": "1"},
    }
    manifest["digest"] = module.environment_manifest_digest(manifest)
    return manifest


def test_environment_manifest_digest_changes_when_environment_changes() -> None:
    module = _load_mxtest_module()
    first = _environment_fixture(module, python_version="3.11.0")
    second = _environment_fixture(module, python_version="3.12.0")

    assert first["digest"] != second["digest"]
    diff = module.environment_manifest_differences(first, second)
    assert diff["changed"] == ["python.version"]


def test_environment_manifest_issues_report_tampering() -> None:
    module = _load_mxtest_module()
    env = _environment_fixture(module)
    tampered = __import__("copy").deepcopy(env)
    tampered["pytest"]["version"] = "999.0"  # type: ignore[index]

    issues = module.environment_manifest_issues(
        {"environment_digest": env["digest"], "environment_manifest": tampered}
    )

    assert any("environment_manifest digest" in issue for issue in issues)


def test_verify_current_environment_payload_accepts_matching_environment() -> None:
    module = _load_mxtest_module()
    env = _environment_fixture(module)

    rc, lines, payload = module.verify_current_environment_payload(
        {"environment_digest": env["digest"], "environment_manifest": env},
        current_environment=env,
    )

    assert rc == 0
    assert payload["matches_current_environment"] is True
    assert payload["issues"] == []
    assert "matches: true" in lines


def test_verify_current_environment_payload_reports_environment_drift() -> None:
    module = _load_mxtest_module()
    old_env = _environment_fixture(module, python_version="3.11.0", pytest_version="8.0.0")
    current_env = _environment_fixture(module, python_version="3.12.0", pytest_version="8.1.0")

    rc, lines, payload = module.verify_current_environment_payload(
        {"environment_digest": old_env["digest"], "environment_manifest": old_env},
        current_environment=current_env,
    )

    assert rc == 1
    assert payload["matches_current_environment"] is False
    assert "python.version" in payload["environment_differences"]["changed"]
    assert "pytest.version" in payload["environment_differences"]["changed"]
    assert any("does not match current environment" in issue for issue in payload["issues"])
    assert any(line.startswith("environment fields:") for line in lines)


def test_verify_current_environment_cli_does_not_collect_tests(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_mxtest_module()
    manifest_path = tmp_path / "mxtest-all.json"
    json_path = tmp_path / "current-environment.json"
    env = _environment_fixture(module)
    manifest_path.write_text(
        __import__("json").dumps(
            {
                "mode": "run-chunks",
                "environment_digest": env["digest"],
                "environment_manifest": env,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    def fail_collect(pytest_args: list[str]) -> list[str]:
        raise AssertionError("current-environment verification should not collect tests")

    monkeypatch.setattr(module, "collect_nodeids", fail_collect)
    monkeypatch.setattr(module, "environment_manifest_payload", lambda: dict(env))

    assert module.main(["--verify-current-environment", str(manifest_path), "--json", str(json_path)]) == 0
    payload = __import__("json").loads(json_path.read_text(encoding="utf-8"))
    assert payload["mode"] == "verify-current-environment"
    assert payload["matches_current_environment"] is True


def test_diff_manifest_payload_reports_environment_drift() -> None:
    module = _load_mxtest_module()
    old_env = _environment_fixture(module, python_version="3.11.0")
    new_env = _environment_fixture(module, python_version="3.12.0")

    rc, lines, payload = module.diff_manifest_payloads(
        {
            "mode": "run-chunks",
            "run_chunks": 1,
            "environment_digest": old_env["digest"],
            "environment_manifest": old_env,
            "chunk_results": [],
        },
        {
            "mode": "run-chunks",
            "run_chunks": 1,
            "environment_digest": new_env["digest"],
            "environment_manifest": new_env,
            "chunk_results": [],
        },
    )

    assert rc == 1
    assert payload["environment_differences"]["changed"] == ["python.version"]
    assert any(line.startswith("environment fields:") for line in lines)


def test_plan_json_embeds_environment_attestation(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    module = _load_mxtest_module()
    env = _environment_fixture(module)
    source = {"digest": "a" * 64, "file_count": 0, "total_bytes": 0, "files": []}
    json_path = tmp_path / "plan.json"

    monkeypatch.setattr(module, "collect_nodeids", lambda pytest_args: ["tests/a.py::test_one"])
    monkeypatch.setattr(module, "source_manifest_payload", lambda: dict(source))
    monkeypatch.setattr(module, "environment_manifest_payload", lambda: dict(env))

    assert module.main(["--plan", "--json", str(json_path)]) == 0
    payload = __import__("json").loads(json_path.read_text(encoding="utf-8"))
    assert payload["environment_digest"] == env["digest"]
    assert payload["environment_manifest"]["schema"] == module.ENVIRONMENT_MANIFEST_SCHEMA


def _source_fixture(module, *, sha: str = "a") -> dict[str, object]:
    files = [{"path": "tests/a.py", "size": 3, "sha256": sha * 64}]
    return {
        "schema": module.SOURCE_MANIFEST_SCHEMA,
        "algorithm": "sha256",
        "digest": module.source_manifest_digest(files),
        "file_count": 1,
        "total_bytes": 3,
        "files": files,
    }


def _passed_aggregate_manifest(module, *, source: dict[str, object], environment: dict[str, object]) -> dict[str, object]:
    record = module.chunk_selection_payload(
        selected=["tests/a.py::test_one"],
        index=1,
        total=1,
        strategy="node",
        duration_history={},
    )
    record.update({"returncode": 0, "status": "passed", "duration_seconds": 0.1})
    return {
        "mode": "run-chunks",
        "run_chunks": 1,
        "collected": 1,
        "selected": 1,
        "chunks": [1],
        "chunk_results": [record],
        "chunk_status_counts": {"passed": 1, "failed": 0, "timed_out": 0, "partial": 0, "not_run": 0},
        "complete": True,
        "returncode": 0,
        "status": "passed",
        "source_digest": source["digest"],
        "source_file_count": source["file_count"],
        "source_total_bytes": source["total_bytes"],
        "source_manifest": source,
        "environment_digest": environment["digest"],
        "environment_manifest": environment,
    }


def test_verify_current_manifest_payload_accepts_passed_current_manifest() -> None:
    module = _load_mxtest_module()
    source = _source_fixture(module)
    env = _environment_fixture(module)
    manifest = _passed_aggregate_manifest(module, source=source, environment=env)

    rc, lines, payload = module.verify_current_manifest_payload(
        manifest,
        current_source=source,
        current_environment=env,
    )

    assert rc == 0
    assert payload["resume_safe"] is True
    assert payload["manifest_ok"] is True
    assert payload["source_ok"] is True
    assert payload["environment_ok"] is True
    assert payload["issues"] == []
    assert "resume-safe: true" in lines


def test_verify_current_manifest_payload_reports_source_and_environment_drift() -> None:
    module = _load_mxtest_module()
    old_source = _source_fixture(module, sha="a")
    current_source = _source_fixture(module, sha="b")
    old_env = _environment_fixture(module, python_version="3.11.0")
    current_env = _environment_fixture(module, python_version="3.12.0")
    manifest = _passed_aggregate_manifest(module, source=old_source, environment=old_env)

    rc, lines, payload = module.verify_current_manifest_payload(
        manifest,
        current_source=current_source,
        current_environment=current_env,
    )

    assert rc == 1
    assert payload["resume_safe"] is False
    assert payload["manifest_ok"] is True
    assert payload["source_ok"] is False
    assert payload["environment_ok"] is False
    assert payload["source_differences"]["changed"] == ["tests/a.py"]
    assert "python.version" in payload["environment_differences"]["changed"]
    assert any("source:" in issue for issue in payload["issues"])
    assert any("environment:" in issue for issue in payload["issues"])
    assert "resume-safe: false" in lines


def test_verify_current_manifest_payload_returns_structural_issue_for_bad_manifest() -> None:
    module = _load_mxtest_module()
    env = _environment_fixture(module)
    source = _source_fixture(module)

    rc, lines, payload = module.verify_current_manifest_payload(
        {"mode": "run-chunks", "run_chunks": 1, "chunk_results": [], "status": "passed", "complete": True},
        current_source=source,
        current_environment=env,
    )

    assert rc == 2
    assert payload["resume_safe"] is False
    assert payload["manifest_ok"] is False
    assert any("manifest:" in issue for issue in payload["issues"])
    assert any("source:" in issue for issue in payload["issues"])
    assert any("environment:" in issue for issue in payload["issues"])
    assert "issues:" in lines


def test_verify_current_cli_does_not_collect_tests(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    module = _load_mxtest_module()
    manifest_path = tmp_path / "mxtest-all.json"
    json_path = tmp_path / "current.json"
    source = _source_fixture(module)
    env = _environment_fixture(module)
    manifest = _passed_aggregate_manifest(module, source=source, environment=env)
    manifest_path.write_text(__import__("json").dumps(manifest) + "\n", encoding="utf-8")

    def fail_collect(pytest_args: list[str]) -> list[str]:
        raise AssertionError("current manifest verification should not collect tests")

    monkeypatch.setattr(module, "collect_nodeids", fail_collect)
    monkeypatch.setattr(module, "source_manifest_payload", lambda: dict(source))
    monkeypatch.setattr(module, "environment_manifest_payload", lambda: dict(env))

    assert module.main(["--verify-current", str(manifest_path), "--json", str(json_path)]) == 0
    payload = __import__("json").loads(json_path.read_text(encoding="utf-8"))
    assert payload["mode"] == "verify-current"
    assert payload["resume_safe"] is True


def test_manifest_summary_payload_reports_digests_and_slowest_rows() -> None:
    module = _load_mxtest_module()
    source = _source_fixture(module)
    env = _environment_fixture(module)
    first = module.chunk_selection_payload(
        selected=["tests/a.py::test_one"],
        index=1,
        total=2,
        strategy="segment",
        duration_history={},
    )
    first.update(
        {
            "returncode": 0,
            "status": "passed",
            "duration_seconds": 0.5,
            "files": [
                {
                    "file": "tests/a.py",
                    "selected": 1,
                    "returncode": 0,
                    "duration_seconds": 0.5,
                    "timed_out": False,
                    "status": "passed",
                }
            ],
        }
    )
    second = module.chunk_selection_payload(
        selected=["tests/b.py::test_two"],
        index=2,
        total=2,
        strategy="segment",
        duration_history={},
    )
    second.update(
        {
            "returncode": 0,
            "status": "passed",
            "duration_seconds": 2.0,
            "files": [
                {
                    "file": "tests/b.py",
                    "selected": 1,
                    "returncode": 0,
                    "duration_seconds": 2.0,
                    "timed_out": False,
                    "status": "passed",
                }
            ],
        }
    )
    manifest = _passed_aggregate_manifest(module, source=source, environment=env)
    manifest.update(
        {
            "run_chunks": 2,
            "selected": 2,
            "chunks": [1, 1],
            "chunk_results": [first, second],
            "chunk_status_counts": {"passed": 2, "failed": 0, "timed_out": 0, "partial": 0, "not_run": 0},
            "strategy": "segment",
            "duration_seconds": 2.5,
        }
    )

    rc, lines, payload = module.manifest_summary_payload(manifest, slowest=1)

    assert rc == 0
    assert payload["mode"] == "manifest-summary"
    assert payload["status"] == "passed"
    assert payload["source_digest_short"] == source["digest"][:12]
    assert payload["environment_digest_short"] == env["digest"][:12]
    assert payload["slowest_chunks"][0]["index"] == 2
    assert payload["slowest_files"][0]["file"] == "tests/b.py"
    assert payload["manifest_issues"] == []
    assert any(line.startswith("slowest chunks") for line in lines)
    assert any("tests/b.py" in line for line in lines)


def test_manifest_summary_cli_does_not_collect_tests(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    module = _load_mxtest_module()
    source = _source_fixture(module)
    env = _environment_fixture(module)
    manifest_path = tmp_path / "mxtest-all.json"
    json_path = tmp_path / "summary.json"
    manifest_path.write_text(
        __import__("json").dumps(_passed_aggregate_manifest(module, source=source, environment=env)) + "\n",
        encoding="utf-8",
    )

    def fail_collect(pytest_args: list[str]) -> list[str]:
        raise AssertionError("manifest summary should not collect tests")

    monkeypatch.setattr(module, "collect_nodeids", fail_collect)

    assert module.main(["--manifest-summary", str(manifest_path), "--summary-limit", "1", "--json", str(json_path)]) == 0
    payload = __import__("json").loads(json_path.read_text(encoding="utf-8"))
    assert payload["mode"] == "manifest-summary"
    assert payload["slowest_limit"] == 1
    assert payload["status"] == "passed"


def test_mxtest_run_chunks_max_new_chunks_writes_partial_manifest(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_mxtest_module()
    manifest = tmp_path / "limited.json"
    calls: list[list[str]] = []

    monkeypatch.setattr(
        module,
        "collect_nodeids",
        lambda pytest_args: ["tests/a.py::test_one", "tests/b.py::test_two", "tests/c.py::test_three"],
    )

    def fake_run(nodeids: list[str], pytest_args: list[str], *, durations: int, timeout: int | None = None) -> int:
        calls.append(list(nodeids))
        return 0

    monkeypatch.setattr(module, "run_pytest", fake_run)

    assert module.main(["--run-chunks", "3", "--max-new-chunks", "1", "--json", str(manifest), "--durations", "0"]) == 1

    payload = __import__("json").loads(manifest.read_text(encoding="utf-8"))
    assert payload["status"] == "partial"
    assert payload["complete"] is False
    assert payload["max_new_chunks"] == 1
    assert calls == [["tests/a.py::test_one"]]
    assert [record["status"] for record in payload["chunk_results"]] == ["passed", "not_run", "not_run"]
    assert payload["chunk_results"][1]["skip_reason"] == "max-new-chunks-reached"
    assert payload["chunk_results"][2]["skip_reason"] == "max-new-chunks-reached"


def test_mxtest_max_new_chunks_requires_run_chunks() -> None:
    module = _load_mxtest_module()

    assert module.main(["--max-new-chunks", "1", "--durations", "0"]) == 2
