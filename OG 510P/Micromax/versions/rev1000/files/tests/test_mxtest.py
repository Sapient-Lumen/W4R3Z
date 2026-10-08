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
    for key in module.NATIVE_THREAD_LIMIT_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)

    env = module.isolated_pytest_env()

    assert env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] == "1"
    assert env["PYTHONDONTWRITEBYTECODE"] == "1"
    assert {key: env[key] for key in module.NATIVE_THREAD_LIMIT_ENV_KEYS} == {
        key: "1" for key in module.NATIVE_THREAD_LIMIT_ENV_KEYS
    }


def test_isolated_pytest_env_respects_explicit_native_thread_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_mxtest_module()
    monkeypatch.setenv("OPENBLAS_NUM_THREADS", "3")

    env = module.isolated_pytest_env()

    assert env["OPENBLAS_NUM_THREADS"] == "3"


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


def test_nodeid_batches_preserve_order_and_default_whole_group() -> None:
    module = _load_mxtest_module()
    nodeids = [f"tests/a.py::test_{index}" for index in range(5)]

    assert module.nodeid_batches(nodeids, batch_size=0) == [nodeids]
    assert module.nodeid_batches(nodeids, batch_size=99) == [nodeids]
    assert module.nodeid_batches(nodeids, batch_size=2) == [nodeids[:2], nodeids[2:4], nodeids[4:]]


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
        nodeids: list[str],
        pytest_args: list[str],
        *,
        durations: int,
        file_timeout: int | None,
        progress=None,
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


def test_run_pytest_file_isolated_batches_nodeids_and_checkpoints(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_mxtest_module()
    nodeids = [
        "tests/a.py::test_one",
        "tests/a.py::test_two",
        "tests/a.py::test_three",
        "tests/b.py::test_four",
    ]
    calls: list[list[str]] = []
    progress: list[list[dict[str, object]]] = []

    def fake_run(selected, pytest_args, *, durations, timeout=None):  # type: ignore[no-untyped-def]
        calls.append(list(selected))
        return 0

    monkeypatch.setattr(module, "run_pytest", fake_run)

    rc, rows = module.run_pytest_file_isolated(
        nodeids,
        [],
        durations=0,
        file_timeout=None,
        progress=lambda seen: progress.append([dict(row) for row in seen]),
        test_batch_size=2,
    )

    assert rc == 0
    assert calls == [
        nodeids[:2],
        nodeids[2:3],
        nodeids[3:],
    ]
    assert [row["status"] for row in rows] == ["passed", "passed", "passed"]
    assert rows[0]["batch_index"] == 1
    assert rows[1]["batch_index"] == 2
    assert "batch_index" not in rows[2]
    assert progress[-1] == rows


def test_progress_jsonl_ok_prefix_requires_contiguous_ok_records(tmp_path: Path) -> None:
    module = _load_mxtest_module()
    progress = tmp_path / "progress.jsonl"
    selected = [
        "tests/a.py::test_one",
        "tests/a.py::test_two",
        "tests/a.py::test_three",
    ]
    progress.write_text(
        "{\"nodeid\": \"tests/a.py::test_one\", \"outcome\": \"passed\"}\n"
        "{\"nodeid\": \"tests/a.py::test_three\", \"outcome\": \"passed\"}\n",
        encoding="utf-8",
    )

    assert module.progress_jsonl_ok_prefix(progress, selected) == selected[:1]


def test_run_pytest_file_isolated_interrupt_uses_per_test_checkpoint_prefix(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_mxtest_module()
    nodeids = [f"tests/a.py::test_{index}" for index in range(4)]
    progress: list[list[dict[str, object]]] = []

    def fake_run(selected, pytest_args, *, durations, timeout=None, progress_jsonl=None):  # type: ignore[no-untyped-def]
        assert progress_jsonl is not None
        progress_jsonl.write_text(
            "\n".join(module.json.dumps({"nodeid": nodeid, "outcome": "passed"}) for nodeid in selected[:2])
            + "\n",
            encoding="utf-8",
        )
        raise module.MxtestInterrupted(module.signal.SIGTERM)

    monkeypatch.setattr(module, "run_pytest", fake_run)

    with pytest.raises(module.MxtestInterrupted):
        module.run_pytest_file_isolated(
            nodeids,
            [],
            durations=0,
            file_timeout=None,
            progress=lambda seen: progress.append([dict(row) for row in seen]),
            checkpoint_tests=True,
        )

    terminal = progress[-1]
    assert [row["status"] for row in terminal] == ["passed", "partial"]
    assert terminal[0]["checkpoint_reason"] == "pytest-test-progress"
    assert terminal[0]["selected"] == 2
    assert terminal[0]["returncode"] == 0
    assert terminal[0]["nodeids_digest"] == module.nodeids_digest(nodeids[:2])
    assert terminal[1]["selected"] == 2
    assert terminal[1]["nodeid_first"] == nodeids[2]
    assert terminal[1]["signal"] == "SIGTERM"


def test_run_pytest_file_isolated_timeout_uses_per_test_checkpoint_prefix(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_mxtest_module()
    nodeids = [f"tests/a.py::test_{index}" for index in range(4)]
    progress: list[list[dict[str, object]]] = []

    def fake_run(selected, pytest_args, *, durations, timeout=None, progress_jsonl=None):  # type: ignore[no-untyped-def]
        assert progress_jsonl is not None
        progress_jsonl.write_text(
            "\n".join(module.json.dumps({"nodeid": nodeid, "outcome": "passed"}) for nodeid in selected[:3])
            + "\n",
            encoding="utf-8",
        )
        return 124

    monkeypatch.setattr(module, "run_pytest", fake_run)

    rc, rows = module.run_pytest_file_isolated(
        nodeids,
        [],
        durations=0,
        file_timeout=5,
        progress=lambda seen: progress.append([dict(row) for row in seen]),
        checkpoint_tests=True,
    )

    assert rc == 124
    assert rows == progress[-1]
    assert [row["status"] for row in rows] == ["passed", "timed_out"]
    assert rows[0]["checkpoint_reason"] == "pytest-test-progress"
    assert rows[0]["selected"] == 3
    assert rows[1]["checkpoint_reason"] == "timeout-after-pytest-test-progress"
    assert rows[1]["selected"] == 1
    assert rows[1]["nodeid_first"] == nodeids[3]


def test_run_pytest_file_isolated_batch_interrupt_keeps_prior_passed_batch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_mxtest_module()
    nodeids = [f"tests/a.py::test_{index}" for index in range(4)]
    calls: list[list[str]] = []
    progress: list[list[dict[str, object]]] = []

    def fake_run(selected, pytest_args, *, durations, timeout=None):  # type: ignore[no-untyped-def]
        calls.append(list(selected))
        if len(calls) == 2:
            raise module.MxtestInterrupted(module.signal.SIGTERM)
        return 0

    monkeypatch.setattr(module, "run_pytest", fake_run)

    with pytest.raises(module.MxtestInterrupted):
        module.run_pytest_file_isolated(
            nodeids,
            [],
            durations=0,
            file_timeout=None,
            progress=lambda seen: progress.append([dict(row) for row in seen]),
            test_batch_size=2,
        )

    assert calls == [nodeids[:2], nodeids[2:]]
    assert [row["status"] for row in progress[-1]] == ["passed", "partial"]
    assert progress[-1][0]["nodeids_digest"] == module.nodeids_digest(nodeids[:2])
    assert progress[-1][1]["nodeid_first"] == nodeids[2]


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


def test_run_subprocess_with_heartbeat_success_reaps_residual_child_group(
    tmp_path: Path,
) -> None:
    module = _load_mxtest_module()
    if module.os.name != "posix":
        pytest.skip("successful-exit process-group cleanup is POSIX-specific")
    marker = tmp_path / "grandchild-lived-after-parent.txt"
    script = tmp_path / "exit_with_grandchild.py"
    script.write_text(
        "import subprocess, sys\n"
        f"marker = {str(marker)!r}\n"
        "subprocess.Popen([sys.executable, '-c', "
        "'import pathlib, time; time.sleep(1.2); pathlib.Path(%r).write_text(\"alive\")' % marker])\n",
        encoding="utf-8",
    )

    rc = module.run_subprocess_with_heartbeat(
        [module.sys.executable, str(script)], heartbeat_seconds=0
    )
    module.time.sleep(1.5)

    assert rc == 0
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
    monkeypatch.setattr(module, "_cleanup_residual_process_group", lambda pgid: None)

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


def test_mxtest_run_chunks_interrupt_marks_remaining_chunks_not_run(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_mxtest_module()
    manifest = tmp_path / "interrupted-with-remaining.json"
    source = _source_fixture(module)
    env = _environment_fixture(module)

    monkeypatch.setattr(
        module,
        "collect_nodeids",
        lambda pytest_args: ["tests/a.py::test_one", "tests/b.py::test_two"],
    )
    monkeypatch.setattr(module, "source_manifest_payload", lambda: dict(source))
    monkeypatch.setattr(module, "environment_manifest_payload", lambda: dict(env))

    def interrupt(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise module.MxtestInterrupted(int(module.signal.SIGTERM))

    monkeypatch.setattr(module, "run_pytest", interrupt)

    rc = module.main(["--run-chunks", "2", "--json", str(manifest), "--durations", "0"])

    payload = __import__("json").loads(manifest.read_text(encoding="utf-8"))
    records = payload["chunk_results"]
    assert rc == 128 + int(module.signal.SIGTERM)
    assert payload["status"] == "partial"
    assert payload["complete"] is False
    assert payload["interrupted"] is True
    assert payload["signal"] == "SIGTERM"
    assert payload["process_returncode"] == 128 + int(module.signal.SIGTERM)
    assert [record["status"] for record in records] == ["partial", "not_run"]
    assert records[0]["interrupted"] is True
    assert records[1]["skip_reason"] == "interrupted-SIGTERM"
    verify_rc, _lines, issues = module.verify_manifest_payload(payload)
    assert verify_rc == 1
    assert issues == []


def test_mxtest_run_chunks_isolated_interrupt_preserves_file_progress(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_mxtest_module()
    manifest = tmp_path / "isolated-interrupt.json"
    source = _source_fixture(module)
    env = _environment_fixture(module)
    calls: list[list[str]] = []

    monkeypatch.setattr(
        module,
        "collect_nodeids",
        lambda pytest_args: ["tests/a.py::test_one", "tests/b.py::test_two"],
    )
    monkeypatch.setattr(module, "source_manifest_payload", lambda: dict(source))
    monkeypatch.setattr(module, "environment_manifest_payload", lambda: dict(env))

    def fake_run(nodeids: list[str], pytest_args: list[str], *, durations: int, timeout: int | None = None) -> int:
        calls.append(list(nodeids))
        if nodeids[0].startswith("tests/b.py"):
            raise module.MxtestInterrupted(int(module.signal.SIGTERM))
        return 0

    monkeypatch.setattr(module, "run_pytest", fake_run)

    rc = module.main(["--run-chunks", "1", "--isolate-files", "--json", str(manifest), "--durations", "0"])

    payload = __import__("json").loads(manifest.read_text(encoding="utf-8"))
    files = payload["chunk_results"][0]["files"]
    assert rc == 128 + int(module.signal.SIGTERM)
    assert [row["file"] for row in files] == ["tests/a.py", "tests/b.py"]
    assert files[0]["status"] == "passed"
    assert files[1]["status"] == "partial"
    assert files[1]["interrupted"] is True
    assert files[1]["signal"] == "SIGTERM"
    assert calls == [["tests/a.py::test_one"], ["tests/b.py::test_two"]]


def test_mxtest_resume_reuses_passed_files_inside_partial_isolated_chunk(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_mxtest_module()
    manifest = tmp_path / "partial-file-resume.json"
    source = _source_fixture(module)
    env = _environment_fixture(module)
    nodeids = ["tests/a.py::test_one", "tests/b.py::test_two"]
    previous_record = module.chunk_selection_payload(
        selected=nodeids,
        index=1,
        total=1,
        strategy="node",
        duration_history={},
    )
    previous_record.update(
        {
            "returncode": None,
            "status": "partial",
            "duration_seconds": 7.5,
            "files": [
                {
                    "file": "tests/a.py",
                    "selected": 1,
                    "nodeids_digest": module.nodeids_digest(["tests/a.py::test_one"]),
                    "returncode": 0,
                    "duration_seconds": 1.25,
                    "timed_out": False,
                    "status": "passed",
                }
            ],
        }
    )
    manifest.write_text(
        __import__("json").dumps(
            {
                "source_digest": source["digest"],
                "source_manifest": source,
                "environment_digest": env["digest"],
                "environment_manifest": env,
                "chunk_results": [previous_record],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    calls: list[list[str]] = []

    monkeypatch.setattr(module, "collect_nodeids", lambda pytest_args: list(nodeids))
    monkeypatch.setattr(module, "source_manifest_payload", lambda: dict(source))
    monkeypatch.setattr(module, "environment_manifest_payload", lambda: dict(env))

    def fake_isolated(
        selected: list[str],
        pytest_args: list[str],
        *,
        durations: int,
        file_timeout: int | None,
        progress=None,
    ) -> tuple[int, list[dict[str, object]]]:
        calls.append(list(selected))
        return 0, [
            {
                "file": "tests/b.py",
                "selected": 1,
                "nodeids_digest": module.nodeids_digest(["tests/b.py::test_two"]),
                "returncode": 0,
                "duration_seconds": 0.5,
                "timed_out": False,
                "status": "passed",
            }
        ]

    monkeypatch.setattr(module, "run_pytest_file_isolated", fake_isolated)

    assert module.main(["--run-chunks", "1", "--isolate-files", "--resume", "--json", str(manifest), "--durations", "0"]) == 0

    payload = __import__("json").loads(manifest.read_text(encoding="utf-8"))
    record = payload["chunk_results"][0]
    assert payload["status"] == "passed"
    assert record["resumed"] is True
    assert record["skipped"] is False
    assert record["resumed_file_count"] == 1
    assert record["resumed_selected"] == 1
    assert [row["file"] for row in record["files"]] == ["tests/a.py", "tests/b.py"]
    assert record["files"][0]["resumed"] is True
    assert calls == [["tests/b.py::test_two"]]
    _rc, lines, summary = module.manifest_summary_payload(payload, slowest=2)
    assert summary["slowest_chunks"][0]["resumed_file_count"] == 1
    assert any("resumed_files=1" in line for line in lines)
    assert any("tests/a.py" in line and "resumed" in line and "skipped" not in line for line in lines)


def test_mxtest_resume_rejects_passed_file_with_mismatched_nodeids_digest(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_mxtest_module()
    manifest = tmp_path / "bad-file-resume.json"
    source = _source_fixture(module)
    env = _environment_fixture(module)
    nodeids = ["tests/a.py::test_one", "tests/b.py::test_two"]
    previous_record = module.chunk_selection_payload(
        selected=nodeids,
        index=1,
        total=1,
        strategy="node",
        duration_history={},
    )
    previous_record.update(
        {
            "returncode": None,
            "status": "partial",
            "duration_seconds": 7.5,
            "files": [
                {
                    "file": "tests/a.py",
                    "selected": 1,
                    "nodeids_digest": "0" * 64,
                    "returncode": 0,
                    "duration_seconds": 1.25,
                    "timed_out": False,
                    "status": "passed",
                }
            ],
        }
    )
    manifest.write_text(
        __import__("json").dumps(
            {
                "source_digest": source["digest"],
                "source_manifest": source,
                "environment_digest": env["digest"],
                "environment_manifest": env,
                "chunk_results": [previous_record],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    calls: list[list[str]] = []

    monkeypatch.setattr(module, "collect_nodeids", lambda pytest_args: list(nodeids))
    monkeypatch.setattr(module, "source_manifest_payload", lambda: dict(source))
    monkeypatch.setattr(module, "environment_manifest_payload", lambda: dict(env))

    def fake_isolated(
        selected: list[str],
        pytest_args: list[str],
        *,
        durations: int,
        file_timeout: int | None,
        progress=None,
    ) -> tuple[int, list[dict[str, object]]]:
        calls.append(list(selected))
        return 0, []

    monkeypatch.setattr(module, "run_pytest_file_isolated", fake_isolated)

    assert module.main(["--run-chunks", "1", "--isolate-files", "--resume", "--json", str(manifest), "--durations", "0"]) == 0

    payload = __import__("json").loads(manifest.read_text(encoding="utf-8"))
    record = payload["chunk_results"][0]
    assert "resumed_file_count" not in record
    assert calls == [nodeids]


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


def test_mxtest_run_chunks_prints_manifest_summary_by_default(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    module = _load_mxtest_module()
    manifest = tmp_path / "mxtest-all.json"
    fixed_source = _source_fixture(module)
    fixed_environment = _environment_fixture(module)

    monkeypatch.setattr(module, "source_manifest_payload", lambda: dict(fixed_source))
    monkeypatch.setattr(module, "environment_manifest_payload", lambda: dict(fixed_environment))
    monkeypatch.setattr(
        module,
        "collect_nodeids",
        lambda pytest_args: ["tests/a.py::test_one", "tests/b.py::test_two"],
    )

    def fake_run(nodeids: list[str], pytest_args: list[str], *, durations: int, timeout: int | None = None) -> int:
        return 0

    monkeypatch.setattr(module, "run_pytest", fake_run)

    assert (
        module.main(
            ["--run-chunks", "2", "--json", str(manifest), "--durations", "0", "--summary-limit", "1"]
        )
        == 0
    )

    out = capsys.readouterr().out
    assert "mxtest: manifest-first handoff summary" in out
    assert "mxtest manifest summary:" in out
    assert "slowest chunks (top 1):" in out
    assert str(manifest) in out


def test_mxtest_run_chunks_no_run_summary_suppresses_automatic_summary(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    module = _load_mxtest_module()
    manifest = tmp_path / "mxtest-all.json"

    monkeypatch.setattr(module, "collect_nodeids", lambda pytest_args: ["tests/a.py::test_one"])
    monkeypatch.setattr(module, "run_pytest", lambda nodeids, pytest_args, *, durations, timeout=None: 0)

    assert module.main(["--run-chunks", "1", "--json", str(manifest), "--durations", "0", "--no-run-summary"]) == 0

    out = capsys.readouterr().out
    assert "mxtest manifest summary:" not in out


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


def test_source_manifest_partitions_are_derived_from_paths() -> None:
    module = _load_mxtest_module()
    source = _source_from_paths(
        module,
        {
            "src/micromax/vm.py": "a",
            "tests/test_vm.py": "b",
            "docs/00-vision.md": "c",
            "tools/mxtest.py": "d",
            "pyproject.toml": "e",
        },
    )

    partitions = {row["name"]: row for row in source["partitions"]}

    assert source["partition_schema"] == module.SOURCE_MANIFEST_PARTITION_SCHEMA
    assert sorted(partitions) == ["docs", "runtime", "test-config", "tests", "tooling"]
    assert partitions["runtime"]["file_count"] == 1
    assert partitions["tooling"]["file_count"] == 1


def test_source_dependency_ignores_irrelevant_docs_partition_for_plain_tests() -> None:
    module = _load_mxtest_module()
    old_source = _source_from_paths(
        module,
        {
            "src/micromax/vm.py": "a",
            "tests/conftest.py": "b",
            "tests/test_plain.py": "c",
            "docs/00-vision.md": "d",
            "pyproject.toml": "e",
        },
    )
    new_source = _source_from_paths(
        module,
        {
            "src/micromax/vm.py": "a",
            "tests/conftest.py": "b",
            "tests/test_plain.py": "c",
            "docs/00-vision.md": "z",
            "pyproject.toml": "e",
        },
    )

    old_dependency = module.source_dependency_payload_for_nodeids(old_source, ["tests/test_plain.py::test_one"])
    new_dependency = module.source_dependency_payload_for_nodeids(new_source, ["tests/test_plain.py::test_one"])

    assert "docs" not in old_dependency["partitions"]
    assert old_dependency["digest"] == new_dependency["digest"]


def test_source_dependency_derives_file_partition_for_legacy_manifests() -> None:
    module = _load_mxtest_module()
    legacy = _source_from_paths(
        module,
        {
            "src/micromax/vm.py": "a",
            "tests/conftest.py": "b",
            "tests/test_plain.py": "c",
        },
    )
    current = _source_from_paths(
        module,
        {
            "src/micromax/vm.py": "a",
            "tests/conftest.py": "b",
            "tests/test_plain.py": "c",
        },
    )
    for entry in legacy["files"]:
        entry.pop("partition", None)
    legacy.pop("partitions", None)
    legacy.pop("partition_schema", None)

    old_dependency = module.source_dependency_payload_for_nodeids(legacy, ["tests/test_plain.py::test_one"])
    new_dependency = module.source_dependency_payload_for_nodeids(current, ["tests/test_plain.py::test_one"])

    assert old_dependency["digest"] == new_dependency["digest"]


def test_source_dependency_ignores_packaging_only_pyproject_change_for_plain_tests() -> None:
    module = _load_mxtest_module()
    old_source = _source_from_paths(
        module,
        {
            "src/micromax/vm.py": "a",
            "tests/conftest.py": "b",
            "tests/test_plain.py": "c",
            "pyproject.toml": "old-package-data",
        },
    )
    new_source = _source_from_paths(
        module,
        {
            "src/micromax/vm.py": "a",
            "tests/conftest.py": "b",
            "tests/test_plain.py": "c",
            "pyproject.toml": "new-package-data",
        },
    )

    old_dependency = module.source_dependency_payload_for_nodeids(old_source, ["tests/test_plain.py::test_one"])
    new_dependency = module.source_dependency_payload_for_nodeids(new_source, ["tests/test_plain.py::test_one"])

    assert "test-config" not in old_dependency["partitions"]
    assert "pyproject.toml" not in old_dependency["files"]
    assert old_dependency["digest"] == new_dependency["digest"]


def test_source_dependency_includes_docs_partition_for_docs_sensitive_tests() -> None:
    module = _load_mxtest_module()
    old_source = _source_from_paths(
        module,
        {
            "src/micromax/vm.py": "a",
            "tests/conftest.py": "b",
            "tests/test_docs_index.py": "c",
            "docs/00-vision.md": "d",
            "pyproject.toml": "e",
        },
    )
    new_source = _source_from_paths(
        module,
        {
            "src/micromax/vm.py": "a",
            "tests/conftest.py": "b",
            "tests/test_docs_index.py": "c",
            "docs/00-vision.md": "z",
            "pyproject.toml": "e",
        },
    )

    old_dependency = module.source_dependency_payload_for_nodeids(old_source, ["tests/test_docs_index.py::test_docs"])
    new_dependency = module.source_dependency_payload_for_nodeids(new_source, ["tests/test_docs_index.py::test_docs"])

    assert "docs" in old_dependency["partitions"]
    assert old_dependency["digest"] != new_dependency["digest"]



def test_source_dependency_includes_test_config_partition_for_packaging_config_tests() -> None:
    module = _load_mxtest_module()
    old_source = _source_from_paths(
        module,
        {
            "src/micromax/vm.py": "a",
            "tests/conftest.py": "b",
            "tests/test_installed_runtime_resources.py": "c",
            "pyproject.toml": "old-package-data",
            "docs/installed-help-manifest.txt": "manifest",
        },
    )
    new_source = _source_from_paths(
        module,
        {
            "src/micromax/vm.py": "a",
            "tests/conftest.py": "b",
            "tests/test_installed_runtime_resources.py": "c",
            "pyproject.toml": "new-package-data",
            "docs/installed-help-manifest.txt": "manifest",
        },
    )

    old_dependency = module.source_dependency_payload_for_nodeids(
        old_source, ["tests/test_installed_runtime_resources.py::test_pyproject_declares_bundled_runtime_resource_data_files"]
    )
    new_dependency = module.source_dependency_payload_for_nodeids(
        new_source, ["tests/test_installed_runtime_resources.py::test_pyproject_declares_bundled_runtime_resource_data_files"]
    )

    assert "test-config" in old_dependency["partitions"]
    assert old_dependency["digest"] != new_dependency["digest"]


def test_source_dependency_includes_workflow_partition_for_makefile_tests() -> None:
    module = _load_mxtest_module()
    old_source = _source_from_paths(
        module,
        {
            "src/micromax/vm.py": "a",
            "tests/conftest.py": "b",
            "tests/test_makefile_handoff_manifest.py": "c",
            "Makefile": "TEST_MANIFEST ?= .artifacts/mxtest-all-64.json",
        },
    )
    new_source = _source_from_paths(
        module,
        {
            "src/micromax/vm.py": "a",
            "tests/conftest.py": "b",
            "tests/test_makefile_handoff_manifest.py": "c",
            "Makefile": "TEST_MANIFEST ?= .artifacts/other.json",
        },
    )

    old_dependency = module.source_dependency_payload_for_nodeids(
        old_source, ["tests/test_makefile_handoff_manifest.py::test_makefile_defaults_to_handoff_manifest"]
    )
    new_dependency = module.source_dependency_payload_for_nodeids(
        new_source, ["tests/test_makefile_handoff_manifest.py::test_makefile_defaults_to_handoff_manifest"]
    )

    assert "workflow" in old_dependency["partitions"]
    assert old_dependency["digest"] != new_dependency["digest"]

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
        nodeids: list[str],
        pytest_args: list[str],
        *,
        durations: int,
        file_timeout: int | None,
        progress=None,
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


def test_run_chunks_resume_reuses_plain_chunk_when_only_docs_partition_changed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_mxtest_module()
    manifest = tmp_path / "mxtest-all.json"
    old_source = _source_from_paths(
        module,
        {
            "src/micromax/vm.py": "a",
            "tests/conftest.py": "b",
            "tests/test_plain.py": "c",
            "docs/00-vision.md": "d",
            "pyproject.toml": "e",
        },
    )
    current_source = _source_from_paths(
        module,
        {
            "src/micromax/vm.py": "a",
            "tests/conftest.py": "b",
            "tests/test_plain.py": "c",
            "docs/00-vision.md": "z",
            "pyproject.toml": "e",
        },
    )
    env = _environment_fixture(module)
    nodeids = ["tests/test_plain.py::test_one", "tests/test_later.py::test_two"]
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
                "source_digest": old_source["digest"],
                "source_manifest": old_source,
                "environment_digest": env["digest"],
                "environment_manifest": env,
                "chunk_results": [previous_record],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    calls: list[list[str]] = []

    monkeypatch.setattr(module, "collect_nodeids", lambda pytest_args: list(nodeids))
    monkeypatch.setattr(module, "source_manifest_payload", lambda: dict(current_source))
    monkeypatch.setattr(module, "environment_manifest_payload", lambda: dict(env))

    def fake_run(nodeids: list[str], pytest_args: list[str], *, durations: int, timeout: int | None = None) -> int:
        calls.append(list(nodeids))
        return 0

    monkeypatch.setattr(module, "run_pytest", fake_run)

    assert module.main(["--run-chunks", "2", "--resume", "--json", str(manifest), "--durations", "0"]) == 0

    payload = __import__("json").loads(manifest.read_text(encoding="utf-8"))
    assert payload["source_digest"] == current_source["digest"]
    assert payload["chunk_results"][0]["resumed"] is True
    assert payload["chunk_results"][0]["source_dependency_partitions"] == ["runtime"]
    assert calls == [["tests/test_later.py::test_two"]]


def test_run_chunks_resume_refuses_docs_sensitive_chunk_when_docs_partition_changed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_mxtest_module()
    manifest = tmp_path / "mxtest-all.json"
    old_source = _source_from_paths(
        module,
        {
            "src/micromax/vm.py": "a",
            "tests/conftest.py": "b",
            "tests/test_docs_index.py": "c",
            "docs/00-vision.md": "d",
            "pyproject.toml": "e",
        },
    )
    current_source = _source_from_paths(
        module,
        {
            "src/micromax/vm.py": "a",
            "tests/conftest.py": "b",
            "tests/test_docs_index.py": "c",
            "docs/00-vision.md": "z",
            "pyproject.toml": "e",
        },
    )
    env = _environment_fixture(module)
    nodeids = ["tests/test_docs_index.py::test_docs", "tests/test_later.py::test_two"]
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
                "source_digest": old_source["digest"],
                "source_manifest": old_source,
                "environment_digest": env["digest"],
                "environment_manifest": env,
                "chunk_results": [previous_record],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    calls: list[list[str]] = []

    monkeypatch.setattr(module, "collect_nodeids", lambda pytest_args: list(nodeids))
    monkeypatch.setattr(module, "source_manifest_payload", lambda: dict(current_source))
    monkeypatch.setattr(module, "environment_manifest_payload", lambda: dict(env))

    def fake_run(nodeids: list[str], pytest_args: list[str], *, durations: int, timeout: int | None = None) -> int:
        calls.append(list(nodeids))
        return 0

    monkeypatch.setattr(module, "run_pytest", fake_run)

    assert module.main(["--run-chunks", "2", "--resume", "--json", str(manifest), "--durations", "0"]) == 0

    assert calls == [["tests/test_docs_index.py::test_docs"], ["tests/test_later.py::test_two"]]


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


def _source_from_paths(module, path_tokens: dict[str, str]) -> dict[str, object]:
    files = []
    for path, token in sorted(path_tokens.items()):
        digest_seed = (token or path).encode("utf-8")
        sha = module.hashlib.sha256(digest_seed).hexdigest()
        files.append(
            {
                "path": path,
                "partition": module.source_manifest_partition_for_path(path),
                "size": len(token),
                "sha256": sha,
            }
        )
    return {
        "schema": module.SOURCE_MANIFEST_SCHEMA,
        "partition_schema": module.SOURCE_MANIFEST_PARTITION_SCHEMA,
        "algorithm": "sha256",
        "digest": module.source_manifest_digest(files),
        "file_count": len(files),
        "total_bytes": sum(int(row["size"]) for row in files),
        "partitions": module.source_manifest_partition_payload(files),
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


def test_aggregate_manifest_payload_records_selected_test_progress() -> None:
    module = _load_mxtest_module()
    passed = module.chunk_selection_payload(
        selected=["tests/a.py::test_one", "tests/a.py::test_two"],
        index=1,
        total=2,
        strategy="segment",
        duration_history={},
    )
    passed.update({"returncode": 0, "status": "passed", "duration_seconds": 0.1})
    partial = module.chunk_selection_payload(
        selected=["tests/b.py::test_three", "tests/b.py::test_four", "tests/b.py::test_five"],
        index=2,
        total=2,
        strategy="segment",
        duration_history={},
    )
    partial.update(
        {
            "returncode": None,
            "status": "partial",
            "duration_seconds": 0.2,
            "files": [
                {"file": "tests/b.py", "status": "passed", "selected": 1, "duration_seconds": 0.1},
                {"file": "tests/b.py", "status": "not_run", "selected": 2, "duration_seconds": 0.0},
            ],
        }
    )

    payload = module.aggregate_manifest_payload(
        base_payload={"collected": 5},
        total=2,
        chunks=[
            ["tests/a.py::test_one", "tests/a.py::test_two"],
            ["tests/b.py::test_three", "tests/b.py::test_four", "tests/b.py::test_five"],
        ],
        chunk_results=[passed, partial],
        started=0.0,
        complete=False,
    )

    assert payload["test_status_counts"]["passed"] == 3
    assert payload["test_status_counts"]["not_run"] == 2
    assert payload["passed_selected"] == 3
    assert payload["remaining_selected"] == 2


def test_verify_manifest_payload_rejects_stale_test_progress_counts() -> None:
    module = _load_mxtest_module()
    record = module.chunk_selection_payload(
        selected=["tests/a.py::test_one"],
        index=1,
        total=1,
        strategy="segment",
        duration_history={},
    )
    record.update({"returncode": 0, "status": "passed", "duration_seconds": 0.1})
    manifest = {
        "mode": "run-chunks",
        "run_chunks": 1,
        "selected": 1,
        "chunks": [1],
        "chunk_results": [record],
        "chunk_status_counts": {"passed": 1, "failed": 0, "timed_out": 0, "partial": 0, "not_run": 0},
        "test_status_counts": {"passed": 0, "failed": 0, "timed_out": 0, "partial": 0, "not_run": 1, "running": 0},
        "complete": True,
        "returncode": 0,
        "status": "passed",
    }

    rc, lines, issues = module.verify_manifest_payload(manifest)

    assert rc == 2
    assert any("test_status_counts" in issue for issue in issues)
    assert any(line.startswith("tests:") for line in lines)


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
    assert payload["test_status_counts"]["passed"] == 1
    assert payload["remaining_selected"] == 0
    assert "resume-safe: true" in lines
    assert any(line.startswith("test progress:") for line in lines)


def test_verify_current_manifest_payload_accepts_partial_resume_safe_manifest() -> None:
    module = _load_mxtest_module()
    source = _source_fixture(module)
    env = _environment_fixture(module)
    manifest = _passed_aggregate_manifest(module, source=source, environment=env)
    manifest["complete"] = False
    manifest["returncode"] = 1
    manifest["status"] = "partial"
    manifest["chunk_status_counts"] = {"passed": 0, "failed": 0, "timed_out": 0, "partial": 1, "not_run": 0}
    manifest["chunk_results"][0]["returncode"] = None
    manifest["chunk_results"][0]["status"] = "partial"

    rc, lines, payload = module.verify_current_manifest_payload(
        manifest,
        current_source=source,
        current_environment=env,
    )

    assert rc == 0
    assert payload["resume_safe"] is True
    assert payload["manifest_ok"] is True
    assert payload["manifest_passed"] is False
    assert payload["source_ok"] is True
    assert payload["environment_ok"] is True
    assert "manifest-passed: false" in lines
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
    assert payload["test_status_counts"]["passed"] == 2
    assert payload["remaining_selected"] == 0
    assert payload["manifest_issues"] == []
    assert any(line.startswith("test progress:") for line in lines)
    assert any(line.startswith("slowest chunks") for line in lines)
    assert any("tests/b.py" in line for line in lines)


def test_manifest_summary_payload_reports_next_incomplete_chunks() -> None:
    module = _load_mxtest_module()
    source = _source_fixture(module)
    env = _environment_fixture(module)
    first = module.chunk_selection_payload(
        selected=["tests/a.py::test_one"],
        index=1,
        total=3,
        strategy="segment",
        duration_history={},
    )
    first.update({"returncode": 0, "status": "passed", "duration_seconds": 0.5})
    second = module.chunk_selection_payload(
        selected=["tests/b.py::test_two", "tests/b.py::test_three"],
        index=2,
        total=3,
        strategy="segment",
        duration_history={},
    )
    second.update(
        {
            "returncode": None,
            "status": "partial",
            "duration_seconds": 1.0,
            "skip_reason": "max-new-tests-reached",
            "files": [
                {"file": "tests/b.py", "status": "passed", "selected": 1, "duration_seconds": 0.5},
                {"file": "tests/b.py", "status": "not_run", "selected": 1, "duration_seconds": 0.0},
            ],
        }
    )
    third = module.chunk_selection_payload(
        selected=["tests/c.py::test_four"],
        index=3,
        total=3,
        strategy="segment",
        duration_history={},
    )
    third.update(
        {
            "returncode": None,
            "status": "not_run",
            "duration_seconds": 0.0,
            "skip_reason": "max-new-tests-reached",
        }
    )
    manifest = _passed_aggregate_manifest(module, source=source, environment=env)
    manifest.update(
        {
            "run_chunks": 3,
            "selected": 4,
            "chunks": [1, 2, 1],
            "chunk_results": [first, second, third],
            "chunk_status_counts": {"passed": 1, "failed": 0, "timed_out": 0, "partial": 1, "not_run": 1},
            "test_status_counts": {"passed": 2, "failed": 0, "timed_out": 0, "partial": 0, "not_run": 2, "running": 0},
            "status": "partial",
            "complete": False,
            "returncode": 1,
        }
    )

    rc, lines, payload = module.manifest_summary_payload(manifest, slowest=2)

    assert rc == 0
    assert payload["next_incomplete_count"] == 2
    assert [row["index"] for row in payload["next_incomplete_chunks"]] == [2, 3]
    assert payload["next_incomplete_chunks"][0]["file_status_counts"] == {"passed": 1, "not_run": 1}
    assert any(line.startswith("next incomplete chunks (top 2 of 2):") for line in lines)
    assert any("chunk 2/3" in line and "files[passed=1 not_run=1]" in line for line in lines)


def test_manifest_summary_resumed_whole_chunk_is_not_labeled_skipped() -> None:
    module = _load_mxtest_module()
    source = _source_fixture(module)
    env = _environment_fixture(module)
    record = module.chunk_selection_payload(
        selected=["tests/a.py::test_one"],
        index=1,
        total=1,
        strategy="segment",
        duration_history={},
    )
    record.update(
        {
            "returncode": 0,
            "status": "passed",
            "duration_seconds": 1.0,
            "resumed": True,
            "skipped": True,
            "skip_reason": "previous-passed-matching-source-environment-and-chunk",
        }
    )
    manifest = _passed_aggregate_manifest(module, source=source, environment=env)
    manifest.update(
        {
            "run_chunks": 1,
            "selected": 1,
            "chunks": [1],
            "chunk_results": [record],
            "chunk_status_counts": {"passed": 1, "failed": 0, "timed_out": 0, "partial": 0, "not_run": 0},
            "strategy": "segment",
            "duration_seconds": 1.0,
        }
    )

    _rc, lines, _payload = module.manifest_summary_payload(manifest, slowest=1)

    chunk_line = next(line for line in lines if line.startswith("- chunk 1/1:"))
    assert "resumed" in chunk_line
    assert "skipped" not in chunk_line


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


def test_should_preserve_resumed_remainder_accepts_combined_budget_reasons() -> None:
    module = _load_mxtest_module()

    assert module.should_preserve_resumed_remainder(
        f"{module.RUNTIME_BUDGET_SKIP_REASON}+max-new-files-reached"
    )
    assert module.should_preserve_resumed_remainder(
        f"max-new-tests-reached+{module.interruption_skip_reason('SIGTERM')}"
    )
    assert not module.should_preserve_resumed_remainder(
        f"{module.RUNTIME_BUDGET_SKIP_REASON}+fail-fast-after-earlier-nonzero"
    )


def test_mxtest_budget_stop_preserves_later_matching_passed_chunks(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_mxtest_module()
    manifest = tmp_path / "limited-preserve-later.json"
    source = _source_from_paths(
        module,
        {
            "tests/conftest.py": "conf",
            "tests/a.py": "a",
            "tests/b.py": "b",
            "tests/c.py": "c",
        },
    )
    env = _environment_fixture(module)
    nodeids = [
        "tests/a.py::test_one",
        "tests/b.py::test_two",
        "tests/c.py::test_three",
    ]
    previous_record = module.chunk_selection_payload(
        selected=[nodeids[2]],
        index=3,
        total=3,
        strategy="node",
        duration_history={},
    )
    previous_record.update({"returncode": 0, "status": "passed", "duration_seconds": 0.1})
    manifest.write_text(
        __import__("json").dumps(
            {
                "source_digest": source["digest"],
                "source_manifest": source,
                "environment_digest": env["digest"],
                "environment_manifest": env,
                "chunk_results": [previous_record],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    calls: list[list[str]] = []

    monkeypatch.setattr(module, "collect_nodeids", lambda pytest_args: list(nodeids))
    monkeypatch.setattr(module, "source_manifest_payload", lambda: dict(source))
    monkeypatch.setattr(module, "environment_manifest_payload", lambda: dict(env))

    def fake_isolated(
        selected: list[str],
        pytest_args: list[str],
        *,
        durations: int,
        file_timeout: int | None,
        progress=None,
    ) -> tuple[int, list[dict[str, object]]]:
        calls.append(list(selected))
        return 0, [
            {
                "file": selected[0].split("::", 1)[0],
                "selected": len(selected),
                "nodeids_digest": module.nodeids_digest(selected),
                **module.nodeid_span_fields(selected),
                "returncode": 0,
                "duration_seconds": 0.1,
                "timed_out": False,
                "status": "passed",
            }
        ]

    monkeypatch.setattr(module, "run_pytest_file_isolated", fake_isolated)

    assert (
        module.main(
            [
                "--run-chunks",
                "3",
                "--strategy",
                "node",
                "--isolate-files",
                "--resume",
                "--max-new-tests",
                "1",
                "--json",
                str(manifest),
                "--durations",
                "0",
            ]
        )
        == 1
    )

    payload = __import__("json").loads(manifest.read_text(encoding="utf-8"))
    assert calls == [[nodeids[0]]]
    assert [record["status"] for record in payload["chunk_results"]] == ["passed", "not_run", "passed"]
    assert payload["chunk_results"][2]["resumed"] is True
    assert payload["chunk_results"][2]["skipped"] is True
    assert payload["chunk_results"][2]["skip_reason"] == "previous-passed-preserved-after-max-new-tests-reached"



def test_mxtest_interrupt_preserves_later_matching_passed_chunks(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_mxtest_module()
    manifest = tmp_path / "interrupt-preserve-later.json"
    source = _source_from_paths(
        module,
        {
            "tests/conftest.py": "conf",
            "tests/a.py": "a",
            "tests/b.py": "b",
            "tests/c.py": "c",
        },
    )
    env = _environment_fixture(module)
    nodeids = [
        "tests/a.py::test_one",
        "tests/b.py::test_two",
        "tests/c.py::test_three",
    ]
    previous_record = module.chunk_selection_payload(
        selected=[nodeids[2]],
        index=3,
        total=3,
        strategy="node",
        duration_history={},
    )
    previous_record.update({"returncode": 0, "status": "passed", "duration_seconds": 0.1})
    manifest.write_text(
        __import__("json").dumps(
            {
                "source_digest": source["digest"],
                "source_manifest": source,
                "environment_digest": env["digest"],
                "environment_manifest": env,
                "chunk_results": [previous_record],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    calls: list[list[str]] = []

    monkeypatch.setattr(module, "collect_nodeids", lambda pytest_args: list(nodeids))
    monkeypatch.setattr(module, "source_manifest_payload", lambda: dict(source))
    monkeypatch.setattr(module, "environment_manifest_payload", lambda: dict(env))

    def fake_run(nodeids: list[str], pytest_args: list[str], *, durations: int, timeout: int | None = None) -> int:
        calls.append(list(nodeids))
        raise module.MxtestInterrupted(int(module.signal.SIGTERM))

    monkeypatch.setattr(module, "run_pytest", fake_run)

    assert (
        module.main(
            [
                "--run-chunks",
                "3",
                "--strategy",
                "node",
                "--resume",
                "--json",
                str(manifest),
                "--durations",
                "0",
            ]
        )
        == 128 + int(module.signal.SIGTERM)
    )

    payload = __import__("json").loads(manifest.read_text(encoding="utf-8"))
    assert calls == [[nodeids[0]]]
    assert [record["status"] for record in payload["chunk_results"]] == ["partial", "not_run", "passed"]
    assert payload["chunk_results"][1]["skip_reason"] == "interrupted-SIGTERM"
    assert payload["chunk_results"][2]["resumed"] is True
    assert payload["chunk_results"][2]["skipped"] is True
    assert payload["chunk_results"][2]["skip_reason"] == "previous-passed-preserved-after-interrupted-SIGTERM"

def test_file_row_order_preserves_selection_order_after_resume_and_budget_skip() -> None:
    module = _load_mxtest_module()
    selected = [
        "tests/a.py::test_one",
        "tests/b.py::test_two",
        "tests/c.py::test_three",
    ]
    rows = [
        {"file": "tests/b.py", "status": "passed"},
        {"file": "tests/c.py", "status": "not_run"},
        {"file": "tests/a.py", "status": "passed"},
    ]

    ordered = module.order_file_rows_for_selected(selected, rows)

    assert [row["file"] for row in ordered] == ["tests/a.py", "tests/b.py", "tests/c.py"]


def test_mxtest_run_chunks_max_new_files_writes_resumeable_partial_manifest(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    module = _load_mxtest_module()
    manifest = tmp_path / "limited-files.json"
    nodeids = [
        "tests/a.py::test_one",
        "tests/a.py::test_two",
        "tests/b.py::test_three",
        "tests/c.py::test_four",
    ]
    calls: list[list[str]] = []

    monkeypatch.setattr(module, "collect_nodeids", lambda pytest_args: list(nodeids))

    def fake_isolated(
        selected: list[str],
        pytest_args: list[str],
        *,
        durations: int,
        file_timeout: int | None,
        progress=None,
    ) -> tuple[int, list[dict[str, object]]]:
        calls.append(list(selected))
        return 0, [
            {
                "file": "tests/a.py",
                "selected": 2,
                "nodeids_digest": module.nodeids_digest(["tests/a.py::test_one", "tests/a.py::test_two"]),
                "returncode": 0,
                "duration_seconds": 0.25,
                "timed_out": False,
                "status": "passed",
            }
        ]

    monkeypatch.setattr(module, "run_pytest_file_isolated", fake_isolated)

    assert (
        module.main(
            [
                "--run-chunks",
                "1",
                "--strategy",
                "file",
                "--isolate-files",
                "--max-new-files",
                "1",
                "--json",
                str(manifest),
                "--durations",
                "0",
                "--summary-limit",
                "3",
            ]
        )
        == 1
    )

    payload = __import__("json").loads(manifest.read_text(encoding="utf-8"))
    record = payload["chunk_results"][0]
    assert payload["status"] == "partial"
    assert payload["complete"] is False
    assert payload["max_new_files"] == 1
    assert record["status"] == "partial"
    assert record["returncode"] is None
    assert record["skipped_file_count"] == 2
    assert record["skipped_selected"] == 2
    assert calls == [["tests/a.py::test_one", "tests/a.py::test_two"]]
    assert [row["file"] for row in record["files"]] == ["tests/a.py", "tests/b.py", "tests/c.py"]
    assert [row["status"] for row in record["files"]] == ["passed", "not_run", "not_run"]
    assert record["files"][1]["skip_reason"] == "max-new-files-reached"
    out = capsys.readouterr().out
    assert "skipped_files=2" in out


def test_mxtest_max_new_files_resumes_then_spends_budget_on_remaining_files(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_mxtest_module()
    manifest = tmp_path / "limited-files-resume.json"
    source = _source_fixture(module)
    env = _environment_fixture(module)
    nodeids = [
        "tests/a.py::test_one",
        "tests/b.py::test_two",
        "tests/c.py::test_three",
    ]
    previous_record = module.chunk_selection_payload(
        selected=nodeids,
        index=1,
        total=1,
        strategy="file",
        duration_history={},
    )
    previous_record.update(
        {
            "returncode": None,
            "status": "partial",
            "duration_seconds": 1.0,
            "files": [
                {
                    "file": "tests/a.py",
                    "selected": 1,
                    "nodeids_digest": module.nodeids_digest(["tests/a.py::test_one"]),
                    "returncode": 0,
                    "duration_seconds": 0.1,
                    "timed_out": False,
                    "status": "passed",
                },
                {
                    "file": "tests/b.py",
                    "selected": 1,
                    "nodeids_digest": module.nodeids_digest(["tests/b.py::test_two"]),
                    "returncode": None,
                    "duration_seconds": 0.0,
                    "timed_out": False,
                    "status": "not_run",
                    "skipped": True,
                    "skip_reason": "max-new-files-reached",
                },
            ],
        }
    )
    manifest.write_text(
        __import__("json").dumps(
            {
                "source_digest": source["digest"],
                "source_manifest": source,
                "environment_digest": env["digest"],
                "environment_manifest": env,
                "chunk_results": [previous_record],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    calls: list[list[str]] = []

    monkeypatch.setattr(module, "collect_nodeids", lambda pytest_args: list(nodeids))
    monkeypatch.setattr(module, "source_manifest_payload", lambda: dict(source))
    monkeypatch.setattr(module, "environment_manifest_payload", lambda: dict(env))

    def fake_isolated(
        selected: list[str],
        pytest_args: list[str],
        *,
        durations: int,
        file_timeout: int | None,
        progress=None,
    ) -> tuple[int, list[dict[str, object]]]:
        calls.append(list(selected))
        return 0, [
            {
                "file": "tests/b.py",
                "selected": 1,
                "nodeids_digest": module.nodeids_digest(["tests/b.py::test_two"]),
                "returncode": 0,
                "duration_seconds": 0.2,
                "timed_out": False,
                "status": "passed",
            }
        ]

    monkeypatch.setattr(module, "run_pytest_file_isolated", fake_isolated)

    assert (
        module.main(
            [
                "--run-chunks",
                "1",
                "--strategy",
                "file",
                "--isolate-files",
                "--resume",
                "--max-new-files",
                "1",
                "--json",
                str(manifest),
                "--durations",
                "0",
            ]
        )
        == 1
    )

    payload = __import__("json").loads(manifest.read_text(encoding="utf-8"))
    record = payload["chunk_results"][0]
    assert calls == [["tests/b.py::test_two"]]
    assert record["resumed_file_count"] == 1
    assert record["skipped_file_count"] == 1
    assert [row["file"] for row in record["files"]] == ["tests/a.py", "tests/b.py", "tests/c.py"]
    assert [row["status"] for row in record["files"]] == ["passed", "passed", "not_run"]
    assert record["files"][0]["resumed"] is True
    assert record["files"][2]["skip_reason"] == "max-new-files-reached"


def test_mxtest_max_new_tests_can_checkpoint_inside_one_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_mxtest_module()
    manifest = tmp_path / "limited-tests.json"
    nodeids = [f"tests/big.py::test_{index}" for index in range(4)]
    calls: list[list[str]] = []

    monkeypatch.setattr(module, "collect_nodeids", lambda pytest_args: list(nodeids))

    def fake_isolated(
        selected: list[str],
        pytest_args: list[str],
        *,
        durations: int,
        file_timeout: int | None,
        progress=None,
    ) -> tuple[int, list[dict[str, object]]]:
        calls.append(list(selected))
        return 0, [
            {
                "file": "tests/big.py",
                "selected": len(selected),
                "nodeids_digest": module.nodeids_digest(selected),
                **module.nodeid_span_fields(selected),
                "returncode": 0,
                "duration_seconds": 0.2,
                "timed_out": False,
                "status": "passed",
            }
        ]

    monkeypatch.setattr(module, "run_pytest_file_isolated", fake_isolated)

    assert (
        module.main(
            [
                "--run-chunks",
                "1",
                "--isolate-files",
                "--max-new-tests",
                "2",
                "--json",
                str(manifest),
                "--durations",
                "0",
            ]
        )
        == 1
    )

    payload = __import__("json").loads(manifest.read_text(encoding="utf-8"))
    record = payload["chunk_results"][0]
    assert payload["max_new_tests"] == 2
    assert payload["status"] == "partial"
    assert calls == [nodeids[:2]]
    assert [row["file"] for row in record["files"]] == ["tests/big.py", "tests/big.py"]
    assert [row["selected"] for row in record["files"]] == [2, 2]
    assert [row["status"] for row in record["files"]] == ["passed", "not_run"]
    assert record["files"][0]["nodeid_first"] == nodeids[0]
    assert record["files"][1]["nodeid_first"] == nodeids[2]
    assert record["files"][1]["skip_reason"] == "max-new-tests-reached"


def test_mxtest_max_new_tests_resume_drops_only_passed_node_span_in_same_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_mxtest_module()
    manifest = tmp_path / "limited-tests-resume.json"
    source = _source_fixture(module)
    env = _environment_fixture(module)
    nodeids = [f"tests/big.py::test_{index}" for index in range(4)]
    previous_record = module.chunk_selection_payload(
        selected=nodeids,
        index=1,
        total=1,
        strategy="node",
        duration_history={},
    )
    previous_record.update(
        {
            "returncode": None,
            "status": "partial",
            "duration_seconds": 1.0,
            "files": [
                {
                    "file": "tests/big.py",
                    "selected": 2,
                    "nodeids_digest": module.nodeids_digest(nodeids[:2]),
                    **module.nodeid_span_fields(nodeids[:2]),
                    "returncode": 0,
                    "duration_seconds": 0.2,
                    "timed_out": False,
                    "status": "passed",
                },
                {
                    "file": "tests/big.py",
                    "selected": 2,
                    "nodeids_digest": module.nodeids_digest(nodeids[2:]),
                    **module.nodeid_span_fields(nodeids[2:]),
                    "returncode": None,
                    "duration_seconds": 0.0,
                    "timed_out": False,
                    "status": "not_run",
                    "skipped": True,
                    "skip_reason": "max-new-tests-reached",
                },
            ],
        }
    )
    manifest.write_text(
        __import__("json").dumps(
            {
                "source_digest": source["digest"],
                "source_manifest": source,
                "environment_digest": env["digest"],
                "environment_manifest": env,
                "chunk_results": [previous_record],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    calls: list[list[str]] = []

    monkeypatch.setattr(module, "collect_nodeids", lambda pytest_args: list(nodeids))
    monkeypatch.setattr(module, "source_manifest_payload", lambda: dict(source))
    monkeypatch.setattr(module, "environment_manifest_payload", lambda: dict(env))

    def fake_isolated(
        selected: list[str],
        pytest_args: list[str],
        *,
        durations: int,
        file_timeout: int | None,
        progress=None,
    ) -> tuple[int, list[dict[str, object]]]:
        calls.append(list(selected))
        return 0, [
            {
                "file": "tests/big.py",
                "selected": len(selected),
                "nodeids_digest": module.nodeids_digest(selected),
                **module.nodeid_span_fields(selected),
                "returncode": 0,
                "duration_seconds": 0.2,
                "timed_out": False,
                "status": "passed",
            }
        ]

    monkeypatch.setattr(module, "run_pytest_file_isolated", fake_isolated)

    assert (
        module.main(
            [
                "--run-chunks",
                "1",
                "--isolate-files",
                "--resume",
                "--max-new-tests",
                "2",
                "--json",
                str(manifest),
                "--durations",
                "0",
            ]
        )
        == 0
    )

    payload = __import__("json").loads(manifest.read_text(encoding="utf-8"))
    record = payload["chunk_results"][0]
    assert payload["status"] == "passed"
    assert calls == [nodeids[2:]]
    assert record["resumed_file_count"] == 1
    assert [row["selected"] for row in record["files"]] == [2, 2]
    assert [row["status"] for row in record["files"]] == ["passed", "passed"]
    assert record["files"][0]["resumed"] is True


def test_mxtest_max_new_files_requires_run_chunks_and_isolation() -> None:
    module = _load_mxtest_module()

    assert module.main(["--max-new-files", "1", "--isolate-files", "--durations", "0"]) == 2
    assert module.main(["--run-chunks", "1", "--max-new-files", "1", "--durations", "0"]) == 2
    assert module.main(["--run-chunks", "1", "--isolate-files", "--max-new-files", "-1", "--durations", "0"]) == 2


def test_mxtest_max_new_tests_requires_run_chunks_and_isolation() -> None:
    module = _load_mxtest_module()

    assert module.main(["--max-new-tests", "1", "--isolate-files", "--durations", "0"]) == 2
    assert module.main(["--run-chunks", "1", "--max-new-tests", "1", "--durations", "0"]) == 2
    assert module.main(["--run-chunks", "1", "--isolate-files", "--max-new-tests", "-1", "--durations", "0"]) == 2


def test_mxtest_max_runtime_seconds_marks_remaining_chunks_not_run(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_mxtest_module()
    manifest = tmp_path / "runtime-budget.json"
    source = _source_fixture(module)
    env = _environment_fixture(module)
    ticks = iter([100.0, 100.2, *([100.2] * 20)])

    monkeypatch.setattr(module.time, "monotonic", lambda: next(ticks))
    monkeypatch.setattr(module, "collect_nodeids", lambda pytest_args: ["tests/a.py::test_one", "tests/b.py::test_two"])
    monkeypatch.setattr(module, "source_manifest_payload", lambda: dict(source))
    monkeypatch.setattr(module, "environment_manifest_payload", lambda: dict(env))

    def fail_run(*args, **kwargs):  # noqa: ANN002, ANN003
        raise AssertionError("runtime budget should stop before pytest runs")

    monkeypatch.setattr(module, "run_pytest", fail_run)

    assert (
        module.main(
            [
                "--run-chunks",
                "2",
                "--max-runtime-seconds",
                "0.1",
                "--json",
                str(manifest),
                "--durations",
                "0",
            ]
        )
        == 1
    )

    payload = __import__("json").loads(manifest.read_text(encoding="utf-8"))
    assert payload["status"] == "partial"
    assert payload["max_runtime_seconds"] == 0.1
    assert [record["status"] for record in payload["chunk_results"]] == ["not_run", "not_run"]
    assert payload["chunk_results"][0]["skip_reason"] == module.RUNTIME_BUDGET_SKIP_REASON
    assert payload["chunk_results"][1]["skip_reason"] == module.RUNTIME_BUDGET_SKIP_REASON


def test_run_pytest_file_isolated_runtime_stop_keeps_prior_batch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_mxtest_module()
    nodeids = [f"tests/big.py::test_{index}" for index in range(5)]
    calls: list[list[str]] = []
    stop_checks = iter([False, True])

    def fake_run(nodeids_arg: list[str], pytest_args: list[str], *, durations: int, timeout: int | None = None) -> int:
        calls.append(list(nodeids_arg))
        return 0

    def stop_requested() -> bool:
        return next(stop_checks, True)

    monkeypatch.setattr(module, "run_pytest", fake_run)

    rc, rows = module.run_pytest_file_isolated(
        nodeids,
        [],
        durations=0,
        file_timeout=None,
        test_batch_size=2,
        stop_requested=stop_requested,
        stop_reason=module.RUNTIME_BUDGET_SKIP_REASON,
    )

    assert rc == 0
    assert calls == [nodeids[:2]]
    assert [row["status"] for row in rows] == ["passed", "not_run"]
    assert rows[0]["selected"] == 2
    assert rows[1]["selected"] == 3
    assert rows[1]["nodeid_first"] == nodeids[2]
    assert rows[1]["skip_reason"] == module.RUNTIME_BUDGET_SKIP_REASON


def test_run_pytest_file_isolated_runtime_child_timeout_is_budget_stop(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_mxtest_module()
    nodeids = [f"tests/a.py::test_{index}" for index in range(4)]
    progress: list[list[dict[str, object]]] = []

    def fake_run(selected, pytest_args, *, durations, timeout=None, progress_jsonl=None):  # type: ignore[no-untyped-def]
        assert timeout == 2
        assert progress_jsonl is not None
        progress_jsonl.write_text(
            "\n".join(module.json.dumps({"nodeid": nodeid, "outcome": "passed"}) for nodeid in selected[:2])
            + "\n",
            encoding="utf-8",
        )
        return 124

    monkeypatch.setattr(module, "run_pytest", fake_run)

    rc, rows = module.run_pytest_file_isolated(
        nodeids,
        [],
        durations=0,
        file_timeout=180,
        progress=lambda seen: progress.append([dict(row) for row in seen]),
        checkpoint_tests=True,
        stop_reason=module.RUNTIME_BUDGET_SKIP_REASON,
        child_timeout=lambda configured: 2,
    )

    assert rc == 0
    assert rows == progress[-1]
    assert [row["status"] for row in rows] == ["passed", "not_run"]
    assert rows[0]["selected"] == 2
    assert rows[0]["checkpoint_reason"] == "pytest-test-progress"
    assert rows[1]["selected"] == 2
    assert rows[1]["skip_reason"] == module.RUNTIME_BUDGET_SKIP_REASON
    assert rows[1]["timed_out"] is False
    assert rows[1]["checkpoint_reason"] == "runtime-budget-child-timeout"


def test_run_pytest_file_isolated_child_timeout_callback_caps_batch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_mxtest_module()
    nodeids = ["tests/a.py::test_one"]
    timeouts: list[int | None] = []

    def fake_run(nodeids_arg: list[str], pytest_args: list[str], *, durations: int, timeout: int | None = None) -> int:
        timeouts.append(timeout)
        return 0

    monkeypatch.setattr(module, "run_pytest", fake_run)

    rc, rows = module.run_pytest_file_isolated(
        nodeids,
        [],
        durations=0,
        file_timeout=180,
        child_timeout=lambda configured: min(int(configured or 999), 7),
    )

    assert rc == 0
    assert timeouts == [7]
    assert rows[0]["timeout_seconds"] == 7


def test_mxtest_max_runtime_seconds_requires_run_chunks() -> None:
    module = _load_mxtest_module()

    assert module.main(["--max-runtime-seconds", "1", "--durations", "0"]) == 2
    assert module.main(["--run-chunks", "1", "--max-runtime-seconds", "-1", "--durations", "0"]) == 2


def test_mxtest_test_batch_size_requires_isolation() -> None:
    module = _load_mxtest_module()

    assert module.main(["--test-batch-size", "2", "--durations", "0"]) == 2
    assert module.main(["--checkpoint-tests", "--durations", "0"]) == 2
    assert module.main(["--isolate-files", "--test-batch-size", "-1", "--durations", "0"]) == 2
