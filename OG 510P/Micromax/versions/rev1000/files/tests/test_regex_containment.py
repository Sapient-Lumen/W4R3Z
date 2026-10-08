from __future__ import annotations

import json
import multiprocessing
import subprocess
import sys
import textwrap
import threading
import time
from pathlib import Path

import pytest

from micromax.regex_runtime import (
    RegexWorkerError,
    RegexWorkerOperationError,
    RegexWorkerStartupTimeoutError,
    RegexWorkerTimeoutError,
    run_regex_worker,
)
from micromax.regex_worker_child import PROTOCOL
from micromax_editor.editor import Editor
from micromax_editor.replace_plan import plan_replace


def _deeply_nested_pattern() -> str:
    """Return a byte-bounded pattern that exceeds CPython parser recursion."""

    return ("(" * 1000) + "a" + (")" * 1000)


def test_stdlib_regex_child_runs_without_site_or_package_imports() -> None:
    child = (
        Path(__file__).resolve().parents[1]
        / "src"
        / "micromax"
        / "regex_worker_child.py"
    )
    request = {
        "protocol": PROTOCOL,
        "action": "re.search",
        "haystack": "abc123",
        "pattern": r"([0-9]+)",
        "start": 0,
        "flags": "",
        "replacement": None,
        "max_matches": 1,
        "replace_all": True,
        "max_result_bytes": 4096,
    }
    result = subprocess.run(
        [sys.executable, "-I", "-S", str(child)],
        input=json.dumps(request),
        text=True,
        capture_output=True,
        check=False,
        timeout=2.0,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["protocol"] == PROTOCOL
    assert payload["ok"] is True
    assert payload["value"]["group"] == "123"
    assert payload["value"]["groups"] == ["123"]


def test_injected_multiprocessing_regex_adapter_uses_full_frame_channel() -> None:
    value = run_regex_worker(
        action="re.search",
        haystack="abc123",
        pattern=r"([0-9]+)",
        timeout_seconds=5.0,
        worker_context=multiprocessing.get_context("spawn"),
    )

    assert value["start"] == 3
    assert value["end"] == 6
    assert value["groups"] == ["123"]


def test_default_regex_match_deadline_begins_after_fast_child_ready() -> None:
    # The pattern is routed by VM hostcalls. The child gets a separate bounded
    # startup allowance, so scheduler pressure cannot consume the 250 ms match
    # clock before the stdlib-only interpreter is ready to read the request.
    value = run_regex_worker(
        action="re.search",
        haystack="aaaa",
        pattern=r"(a+)+$",
        timeout_seconds=0.25,
    )

    assert isinstance(value, dict)
    assert value["start"] == 0
    assert value["end"] == 4


def test_catastrophic_regex_is_killed_at_wall_clock_deadline() -> None:
    started = time.monotonic()
    with pytest.raises(RegexWorkerTimeoutError, match=r"timed out after 0\.05s"):
        run_regex_worker(
            action="re.search",
            haystack=("a" * 28) + "!",
            pattern=r"(a+)+$",
            timeout_seconds=0.05,
        )
    elapsed = time.monotonic() - started

    assert elapsed < 1.0


@pytest.mark.skipif(
    not sys.platform.startswith("linux") or not Path("/proc/self/statm").is_file(),
    reason="RLIMIT_AS headroom enforcement is a Linux worker boundary",
)
def test_default_worker_memory_headroom_stops_native_repeat_pressure() -> None:
    # This bounded-input pattern is not catastrophically slow: on an uncapped
    # CPython 3.13 worker it completes before the normal foreground deadline
    # while allocating hundreds of MiB of repeat/backtracking state.  The
    # child-owned RLIMIT_AS boundary must turn that pressure into an ordinary
    # operation failure instead of charging the editor process or container.
    count = 2_000_000
    with pytest.raises(RegexWorkerOperationError) as excinfo:
        run_regex_worker(
            action="re.search",
            haystack="a" * count,
            pattern=rf"(a?){{{count}}}$",
            timeout_seconds=3.0,
        )

    assert excinfo.value.kind == "memory-limit"
    assert str(excinfo.value) == "regex worker memory headroom exceeded"

    # The failed one-shot child owns its limit and allocation state.  A fresh
    # worker remains usable immediately afterward.
    recovered = run_regex_worker(
        action="re.search",
        haystack="abc",
        pattern="b",
        timeout_seconds=0.5,
    )
    assert recovered["group"] == "b"


def test_configured_worker_memory_headroom_fails_with_stable_kind() -> None:
    count = 300_000
    with pytest.raises(RegexWorkerOperationError) as excinfo:
        run_regex_worker(
            action="re.search",
            haystack="a" * count,
            pattern=rf"(a?){{{count}}}$",
            timeout_seconds=2.0,
            max_memory_headroom_bytes=16 * 1024 * 1024,
        )

    assert excinfo.value.kind == "memory-limit"
    assert str(excinfo.value) == "regex worker memory headroom exceeded"


def test_invalid_worker_memory_headroom_is_rejected_before_spawn() -> None:
    with pytest.raises(RegexWorkerError, match="invalid regex worker memory headroom"):
        run_regex_worker(
            action="re.search",
            haystack="a",
            pattern="a",
            timeout_seconds=0.5,
            max_memory_headroom_bytes=object(),  # type: ignore[arg-type]
        )


def test_boolean_worker_budgets_are_rejected_before_spawn() -> None:
    with pytest.raises(RegexWorkerError, match="invalid regex worker result budget"):
        run_regex_worker(
            action="re.search",
            haystack="a",
            pattern="a",
            timeout_seconds=0.5,
            max_result_bytes=True,
        )

    with pytest.raises(RegexWorkerError, match="invalid regex worker memory headroom"):
        run_regex_worker(
            action="re.search",
            haystack="a",
            pattern="a",
            timeout_seconds=0.5,
            max_memory_headroom_bytes=True,
        )


def test_worker_protocol_rejects_boolean_numeric_limits() -> None:
    import micromax.regex_worker_child as child

    request = {
        "protocol": PROTOCOL,
        "action": "re.search",
        "haystack": "a",
        "pattern": "a",
        "start": 0,
        "flags": "",
        "replacement": None,
        "max_matches": True,
        "replace_all": True,
        "max_result_bytes": 4096,
    }
    response = child.execute_request(request)

    assert response == {
        "protocol": PROTOCOL,
        "ok": False,
        "kind": "protocol",
        "message": "invalid regex worker limit",
    }


@pytest.mark.skipif(
    not sys.platform.startswith("linux"),
    reason="the regression protects the Linux child-only RLIMIT_AS seam",
)
def test_pure_executor_does_not_lower_calling_process_address_space_limit() -> None:
    import resource

    import micromax.regex_worker_child as child

    before = resource.getrlimit(resource.RLIMIT_AS)
    response = child.execute_request(
        {
            "protocol": PROTOCOL,
            "action": "re.search",
            "haystack": "a",
            "pattern": "a",
            "start": 0,
            "flags": "",
            "replacement": None,
            "max_matches": 1,
            "replace_all": True,
            "max_result_bytes": 4096,
            "max_memory_headroom_bytes": 1,
        }
    )

    assert response["ok"] is True
    assert resource.getrlimit(resource.RLIMIT_AS) == before


def test_worker_utf8_counter_matches_replacement_encoding_without_byte_copy() -> None:
    import micromax.regex_worker_child as child

    text = "Aé€😀\ud800"
    assert child._utf8_size_range(text, 0, len(text)) == len(
        text.encode("utf-8", errors="replace")
    )
    assert child._utf8_size_range(text, 0, len(text), stop_after=3) > 3


def test_worker_response_has_preallocated_memory_failure_envelope(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import micromax.regex_worker_child as child

    def fail_json_materialization(*args: object, **kwargs: object) -> str:
        raise MemoryError

    monkeypatch.setattr(child.json, "dumps", fail_json_materialization)
    encoded = child._encode_worker_response(
        {"protocol": PROTOCOL, "ok": True, "value": "unreachable"}
    )

    assert encoded is child._MEMORY_FAILURE_RESPONSE_BYTES
    assert child._MEMORY_FAILURE_RESPONSE == {
        "protocol": PROTOCOL,
        "ok": False,
        "kind": "memory-limit",
        "message": "regex worker memory headroom exceeded",
    }
    assert encoded == (
        b'{"protocol":"micromax.regex-worker.v1","ok":false,'
        b'"kind":"memory-limit",'
        b'"message":"regex worker memory headroom exceeded"}'
    )


def test_denied_substitution_preflights_before_source_slice_materialization() -> None:
    import micromax.regex_worker_child as child

    class SliceWitness(str):
        slice_calls = 0

        def __getitem__(self, key):  # type: ignore[no-untyped-def]
            if isinstance(key, slice):
                type(self).slice_calls += 1
            return super().__getitem__(key)

    haystack = SliceWitness("a" * 100)
    with pytest.raises(child.RegexOperationFailure, match="result budget exceeded"):
        child._apply_replacement_rows(
            haystack,
            [[90, 91, "x" * 100]],
            max_result_bytes=10,
        )

    assert SliceWitness.slice_calls == 0


def test_deep_pattern_compile_failure_is_classified_inside_worker() -> None:
    started = time.monotonic()
    with pytest.raises(RegexWorkerOperationError) as excinfo:
        run_regex_worker(
            action="re.search",
            haystack="a",
            pattern=_deeply_nested_pattern(),
            timeout_seconds=0.5,
        )

    assert excinfo.value.kind == "invalid-regex"
    assert str(excinfo.value) == (
        "invalid regex: pattern nesting exceeds engine limit"
    )
    assert time.monotonic() - started < 1.0


def test_complete_response_survives_slow_child_teardown(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    import micromax.regex_runtime as runtime

    child = tmp_path / "slow_exit_child.py"
    child.write_text(
        textwrap.dedent(
            f"""
            import json
            import sys
            import time

            sys.stdout.write(json.dumps({{
                "protocol": {PROTOCOL!r},
                "ready": True,
            }}, separators=(",", ":")) + "\\n")
            sys.stdout.flush()
            sys.stdin.buffer.read()
            sys.stdout.write(json.dumps({{
                "protocol": {PROTOCOL!r},
                "ok": True,
                "value": {{"start": 0, "end": 1, "group": "a", "groups": []}},
            }}, separators=(",", ":")))
            sys.stdout.flush()
            time.sleep(5)
            """
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        runtime,
        "_subprocess_worker_command",
        lambda: [sys.executable, "-I", "-S", str(child)],
    )

    started = time.monotonic()
    value = run_regex_worker(
        action="re.search",
        haystack="a",
        pattern="a",
        timeout_seconds=0.05,
    )

    assert value["group"] == "a"
    assert time.monotonic() - started < 1.0


def test_delayed_startup_does_not_consume_match_deadline(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    import micromax.regex_runtime as runtime

    child = tmp_path / "delayed_ready_child.py"
    child.write_text(
        textwrap.dedent(
            f"""
            import json
            import sys
            import time

            time.sleep(0.20)
            sys.stdout.write(json.dumps({{
                "protocol": {PROTOCOL!r},
                "ready": True,
            }}, separators=(",", ":")) + "\\n")
            sys.stdout.flush()
            sys.stdin.buffer.read()
            sys.stdout.write(json.dumps({{
                "protocol": {PROTOCOL!r},
                "ok": True,
                "value": {{"start": 0, "end": 1, "group": "a", "groups": []}},
            }}, separators=(",", ":")))
            sys.stdout.flush()
            """
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        runtime,
        "_subprocess_worker_command",
        lambda: [sys.executable, "-I", "-S", str(child)],
    )

    started = time.monotonic()
    value = run_regex_worker(
        action="re.search",
        haystack="a",
        pattern="a",
        timeout_seconds=0.05,
        startup_timeout_seconds=1.0,
    )
    elapsed = time.monotonic() - started

    assert value["group"] == "a"
    assert elapsed >= 0.15
    assert elapsed < 1.0


def test_startup_deadline_kills_child_that_never_becomes_ready(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    import micromax.regex_runtime as runtime

    child = tmp_path / "never_ready_child.py"
    child.write_text(
        "import time\ntime.sleep(5)\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        runtime,
        "_subprocess_worker_command",
        lambda: [sys.executable, "-I", "-S", str(child)],
    )

    started = time.monotonic()
    with pytest.raises(
        RegexWorkerStartupTimeoutError,
        match=r"startup timed out after 0\.05s",
    ):
        run_regex_worker(
            action="re.search",
            haystack="a",
            pattern="a",
            timeout_seconds=0.25,
            startup_timeout_seconds=0.05,
        )

    assert time.monotonic() - started < 1.0


def test_worker_enforces_match_budget_before_materializing_findall() -> None:
    with pytest.raises(RegexWorkerOperationError) as excinfo:
        run_regex_worker(
            action="re.findall",
            haystack="aaaa",
            pattern="a",
            timeout_seconds=0.5,
            max_matches=2,
        )

    assert excinfo.value.kind == "match-limit"
    assert str(excinfo.value) == "regex match limit exceeded: more than 2 matches"


def test_worker_enforces_result_budget_before_returning_expanded_substitution() -> None:
    with pytest.raises(RegexWorkerOperationError) as excinfo:
        run_regex_worker(
            action="re.sub",
            haystack="aaaa",
            pattern="a",
            replacement="x" * 300,
            timeout_seconds=0.5,
            max_matches=10,
            max_result_bytes=512,
        )

    assert excinfo.value.kind == "result-limit"
    assert "regex result budget exceeded" in str(excinfo.value)


def test_replace_plan_times_out_before_any_mutated_text_exists() -> None:
    source = ("a" * 28) + "!"
    started = time.monotonic()
    plan = plan_replace(
        source,
        r"(a+)+$",
        "X",
        replace_all=True,
        timeout_seconds=0.05,
    )

    assert plan.ok is False
    assert plan.new_text is None
    assert plan.error == "regex timed out after 0.05s"
    assert time.monotonic() - started < 1.0


def test_editor_search_and_replace_do_not_compile_deep_regex_in_foreground() -> None:
    from micromax_editor.buffer import Buffer
    from micromax_editor.search import SearchState, scan_buffer

    pattern = _deeply_nested_pattern()
    snapshot = scan_buffer(
        Buffer("alpha"),
        SearchState(query=pattern, literal=False, case_sensitive=True),
    )
    plan = plan_replace("alpha", pattern, "X", replace_all=True)

    assert snapshot.worker_routed is True
    assert snapshot.spans == ()
    assert snapshot.error == "invalid regex: pattern nesting exceeds engine limit"
    assert plan.ok is False
    assert plan.new_text is None
    assert plan.error == "invalid regex: pattern nesting exceeds engine limit"


def test_historical_highlight_helper_fails_closed_on_deep_regex_syntax() -> None:
    from micromax_editor.search import search_match_spans

    assert search_match_spans(
        "alpha",
        _deeply_nested_pattern(),
        literal=False,
        case_sensitive=True,
    ) == []


def test_case_insensitive_literal_replace_uses_original_unicode_coordinates() -> None:
    # U+0130 lowercases to two code points. Searching a lowercased copy used to
    # shift the later B from source index 2 to transformed index 3.
    plan = plan_replace(
        "AİB",
        "b",
        "Q",
        literal=True,
        case_sensitive=False,
    )

    assert plan.ok is True
    assert plan.matches[0].start == 2
    assert plan.matches[0].old == "B"
    assert plan.new_text == "AİQ"


def test_query_replace_plans_regex_once_and_never_rematches_mutated_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import micromax_editor.editor as editor_module

    original = editor_module.scan_regex_replacement_edits_lines
    calls = 0

    def counted(*args, **kwargs):  # type: ignore[no-untyped-def]
        nonlocal calls
        calls += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(
        editor_module,
        "scan_regex_replacement_edits_lines",
        counted,
    )

    ed = Editor()
    ed.new_buffer("planned.txt", "a1 a2 a3")
    assert ed.begin_query_replace(r"a([0-9])", "b$1") is True
    assert calls == 1

    assert ed.qreplace_yes() is True
    assert ed.qreplace_no() is True
    assert ed.qreplace_last() is True
    assert calls == 1
    assert ed.cur().buf.get_text() == "b1 a2 b3"


def test_query_replace_timeout_fails_before_capture_or_selection() -> None:
    ed = Editor()
    ed.new_buffer("risk.txt", ("a" * 28) + "!")
    ed.search_regex_timeout_seconds = 0.05
    before = ed.primary_cursor()

    assert ed.begin_query_replace(r"(a+)+$", "X") is False
    assert ed.qreplace is None
    assert ed.current_capture_key_mode() is None
    assert ed.primary_cursor() == before
    assert ed.messages[-1] == "qreplace: regex timed out after 0.05s"


def test_failed_search_candidate_preserves_previous_register_and_authority(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import micromax_editor.search as search_module

    ed = Editor()
    ed.new_buffer("search.txt", "alpha beta")
    assert ed.find("alpha", literal=True) is True
    prior_state = (
        ed.search.query,
        ed.search.literal,
        ed.search.case_sensitive,
        ed.search.last_match,
    )
    prior_authority = ed.search_authority
    prior_cursor = ed.primary_cursor()

    def timed_out(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise RegexWorkerTimeoutError("regex timed out after 0.25s")

    monkeypatch.setattr(search_module, "bounded_regex_spans", timed_out)
    assert ed.find(r"(a+)+$", literal=False) is False

    assert (
        ed.search.query,
        ed.search.literal,
        ed.search.case_sensitive,
        ed.search.last_match,
    ) == prior_state
    assert ed.search_authority == prior_authority
    assert ed.primary_cursor() == prior_cursor
    assert ed.messages[-1] == "find: regex timed out after 0.25s"


def test_query_replace_case_insensitive_literal_uses_source_coordinates() -> None:
    ed = Editor()
    ed.new_buffer("unicode.txt", "AİB")

    assert ed.begin_query_replace("b", "Q", literal=True) is True
    assert ed.selection_text() == "B"
    assert ed.qreplace_last() is True
    assert ed.cur().buf.get_text() == "AİQ"


def test_default_vm_regex_route_contains_simple_patterns_and_normalizes_nan(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import micromax.host_regex as host_regex

    original = host_regex.run_regex_worker
    calls: list[dict[str, object]] = []

    def observed(**kwargs):  # type: ignore[no-untyped-def]
        calls.append(dict(kwargs))
        return original(**kwargs)

    monkeypatch.setattr(host_regex, "run_regex_worker", observed)

    ed = Editor()
    from micromax_editor.micromax_bridge import install_editor_hostcalls

    install_editor_hostcalls(ed)
    ed.new_buffer("*scratch*", "")
    vm = ed.vm
    vm.hostcall_regex_timeout_seconds = float("nan")

    vm.eval('"abc" "a+" 0 "" re-search', filename="<test>")

    assert vm.pop_map()["group"] == "a"
    assert [call["action"] for call in calls] == ["re.search"]
    assert calls[0]["timeout_seconds"] == 0.25


def test_positive_timeout_vm_search_and_sub_skip_foreground_regex_compile(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import micromax.host_regex as host_regex
    from micromax_editor.micromax_bridge import install_editor_hostcalls

    compile_calls = 0
    original_compile = host_regex.re.compile

    def observed_compile(*args, **kwargs):  # type: ignore[no-untyped-def]
        nonlocal compile_calls
        compile_calls += 1
        return original_compile(*args, **kwargs)

    monkeypatch.setattr(host_regex.re, "compile", observed_compile)

    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*scratch*", "")
    vm = ed.vm
    vm.hostcall_regex_timeout_seconds = 0.5

    vm.eval('"abc" "a+" 0 "" re-search', filename="<test>")
    assert vm.pop_map()["group"] == "a"
    vm.eval('"abc" "b" "B" "" re-sub', filename="<test>")
    assert vm.pop_str() == "aBc"
    assert compile_calls == 0


def test_deep_vm_pattern_fails_closed_without_consuming_arguments() -> None:
    from micromax_editor.micromax_bridge import install_editor_hostcalls

    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*scratch*", "")
    vm = ed.vm
    vm.hostcall_regex_timeout_seconds = 0.5
    pattern = _deeply_nested_pattern()
    vm.stack.extend(["a", pattern, 0, "", "re.search"])

    with pytest.raises(Exception) as excinfo:
        vm.eval("hostcall", filename="<test>")

    assert "re.search: invalid regex: pattern nesting exceeds engine limit" in str(
        excinfo.value
    )
    assert vm.stack == ["a", pattern, 0, ""]


def test_vm_regex_explicit_zero_timeout_retains_local_embedding_escape_hatch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import micromax.host_regex as host_regex
    from micromax_editor.micromax_bridge import install_editor_hostcalls

    def forbidden(**kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError(f"unexpected worker route: {kwargs}")

    monkeypatch.setattr(host_regex, "run_regex_worker", forbidden)
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*scratch*", "")
    vm = ed.vm
    vm.hostcall_regex_timeout_seconds = 0

    vm.eval('"abc" "a+" 0 "" re-search', filename="<test>")

    assert vm.pop_map()["group"] == "a"


def test_findall_result_budget_stops_row_materialization_early(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import micromax.regex_worker_child as child

    original = child._match_to_map
    materialized = 0

    def counted(match):  # type: ignore[no-untyped-def]
        nonlocal materialized
        materialized += 1
        return original(match)

    monkeypatch.setattr(child, "_match_to_map", counted)
    response = child.execute_request(
        {
            "protocol": PROTOCOL,
            "action": "re.findall",
            "haystack": "a" * 1000,
            "pattern": "a",
            "start": 0,
            "flags": "",
            "replacement": None,
            "max_matches": 1000,
            "replace_all": True,
            "max_result_bytes": 256,
        }
    )

    assert response["ok"] is False
    assert response["kind"] == "result-limit"
    assert materialized < 10


def test_direct_search_scan_cannot_disable_containment_with_nonfinite_timeout() -> None:
    from micromax_editor.buffer import Buffer
    from micromax_editor.search import SearchState, scan_buffer

    snapshot = scan_buffer(
        Buffer("aaaa"),
        SearchState(query="a+", literal=False, case_sensitive=True),
        timeout_seconds=float("nan"),
    )

    assert snapshot.error == ""
    assert snapshot.worker_routed is True
    assert snapshot.spans == ((0, 4),)


def test_compatibility_match_helper_cannot_reenter_local_backtracking() -> None:
    from micromax_editor.search import match_spans

    started = time.monotonic()
    with pytest.raises(RegexWorkerTimeoutError, match=r"timed out after 0\.05s"):
        match_spans(
            ("a" * 28) + "!",
            query=r"(a+)+$",
            literal=False,
            case_sensitive=True,
            timeout_seconds=0.05,
        )

    assert time.monotonic() - started < 1.0


def test_literal_replace_expansion_budget_fails_before_new_text_materialization() -> None:
    plan = plan_replace(
        "aaaa",
        "a",
        "x" * 100,
        literal=True,
        replace_all=True,
        max_result_bytes=200,
    )

    assert plan.ok is False
    assert plan.new_text is None
    assert plan.error == "replace result budget exceeded: more than 200 bytes"


@pytest.mark.parametrize("literal", [False, True])
def test_oversized_replacement_is_rejected_before_scan_or_mutation(
    literal: bool,
) -> None:
    plan = plan_replace(
        "aaaa",
        "a",
        "x" * 257,
        literal=literal,
        replace_all=True,
        max_result_bytes=256,
    )

    assert plan.ok is False
    assert plan.new_text is None
    assert plan.error == "replacement too large: 257 bytes > 256"


def test_replace_plan_normalizes_malformed_embedding_limits() -> None:
    plan = plan_replace(
        "a a",
        "a",
        "x",
        literal=True,
        replace_all=False,
        start_index="not-an-index",  # type: ignore[arg-type]
        sample_limit="not-a-limit",  # type: ignore[arg-type]
    )

    assert plan.ok is True
    assert plan.start_index == 0
    assert plan.count == 1
    assert plan.new_text == "x a"


def test_regex_popen_constructor_timeout_returns_and_late_process_is_cleaned(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import micromax.regex_runtime as runtime

    constructor_entered = threading.Event()
    release_constructor = threading.Event()
    cleanup_finished = threading.Event()
    state = {"killed": False}

    class LateProcess:
        stdin = None
        stdout = None
        stderr = None
        returncode: int | None = None

        def kill(self) -> None:
            state["killed"] = True
            self.returncode = -9

        def communicate(
            self,
            input: bytes | None = None,
            timeout: float | None = None,
        ) -> tuple[bytes, bytes]:
            del input, timeout
            cleanup_finished.set()
            return (b"", b"")

        def wait(self, timeout: float | None = None) -> int:
            del timeout
            return int(self.returncode or 0)

    process = LateProcess()

    def blocked_popen(*_args: object, **_kwargs: object) -> LateProcess:
        constructor_entered.set()
        release_constructor.wait(timeout=5.0)
        return process

    monkeypatch.setattr(runtime.subprocess, "Popen", blocked_popen)

    started = time.monotonic()
    try:
        with pytest.raises(
            RegexWorkerStartupTimeoutError,
            match=r"startup timed out after 0\.05s",
        ):
            run_regex_worker(
                action="re.search",
                haystack="a",
                pattern="a",
                timeout_seconds=0.25,
                startup_timeout_seconds=0.05,
            )
        assert time.monotonic() - started < 0.5
        assert constructor_entered.wait(timeout=0.5)
        assert state == {"killed": False}
    finally:
        release_constructor.set()

    assert cleanup_finished.wait(timeout=1.0)
    assert state == {"killed": True}


def test_regex_constructor_and_ready_handshake_share_startup_deadline(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import micromax.regex_runtime as runtime

    ready_line = (
        json.dumps({"protocol": PROTOCOL, "ready": True}, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")

    class SlowReadyStream:
        def readline(self, _limit: int = -1) -> bytes:
            time.sleep(0.08)
            return ready_line

    class SlowReadyProcess:
        stdin = None
        stdout = SlowReadyStream()
        stderr = None
        returncode: int | None = None

        def kill(self) -> None:
            self.returncode = -9

        def communicate(
            self,
            input: bytes | None = None,
            timeout: float | None = None,
        ) -> tuple[bytes, bytes]:
            del input, timeout
            return (b"", b"")

        def wait(self, timeout: float | None = None) -> int:
            del timeout
            return int(self.returncode or 0)

    def delayed_popen(*_args: object, **_kwargs: object) -> SlowReadyProcess:
        time.sleep(0.06)
        return SlowReadyProcess()

    monkeypatch.setattr(runtime.subprocess, "Popen", delayed_popen)

    with pytest.raises(
        RegexWorkerStartupTimeoutError,
        match=r"startup timed out after 0\.1s",
    ):
        run_regex_worker(
            action="re.search",
            haystack="a",
            pattern="a",
            timeout_seconds=0.25,
            startup_timeout_seconds=0.10,
        )


def test_regex_ready_reader_start_interruption_reclaims_owned_process(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import micromax.regex_runtime as runtime

    events: list[str] = []

    class Process:
        stdout = object()

        def kill(self) -> None:
            events.append("kill")

        def communicate(
            self,
            input: bytes | None = None,
            timeout: float | None = None,
        ) -> tuple[bytes, bytes]:
            del input, timeout
            events.append("communicate")
            return (b"", b"")

        def wait(self, timeout: float | None = None) -> int:
            del timeout
            events.append("wait")
            return -9

    class InterruptedReader:
        def __init__(self, **_kwargs: object) -> None:
            pass

        def start(self) -> None:
            raise KeyboardInterrupt

        def join(self, timeout: float | None = None) -> None:
            del timeout
            raise RuntimeError("reader never started")

    monkeypatch.setattr(runtime.threading, "Thread", InterruptedReader)

    with pytest.raises(KeyboardInterrupt):
        runtime._wait_for_subprocess_ready(  # type: ignore[attr-defined]
            Process(),  # type: ignore[arg-type]
            startup_timeout=1.0,
            deadline=time.monotonic() + 1.0,
        )

    assert events == ["kill", "communicate"]


def test_regex_process_handoff_interruption_is_reclaimed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import micromax.regex_runtime as runtime

    process = object()
    cleaned: list[object] = []

    monkeypatch.setattr(
        runtime,
        "start_subprocess_with_deadline",
        lambda *_args, **_kwargs: process,
    )

    def interrupted_ready(*_args: object, **_kwargs: object) -> None:
        raise KeyboardInterrupt

    monkeypatch.setattr(runtime, "_wait_for_subprocess_ready", interrupted_ready)
    monkeypatch.setattr(
        runtime,
        "_kill_and_collect_subprocess",
        lambda value, **_kwargs: cleaned.append(value) or (b"", b""),
    )

    with pytest.raises(KeyboardInterrupt):
        runtime._run_stdlib_subprocess_worker(  # type: ignore[attr-defined]
            {"protocol": PROTOCOL},
            timeout=1.0,
            startup_timeout=1.0,
            max_result_bytes=1024,
        )

    assert cleaned == [process]
