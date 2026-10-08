from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from micromax import VM
from micromax.host_limits import (
    DEFAULT_HOSTCALL_RESULT_MAX_BYTES,
    effective_hostcall_result_limits,
    estimate_host_value_budget,
    utf8_size,
)
from micromax import host_strings
from micromax.host_strings import install_string_hostcalls


ROOT = Path(__file__).resolve().parents[1]


def _vm() -> VM:
    vm = VM()
    install_string_hostcalls(vm)
    return vm


def _hostcall(vm: VM, name: str, *args: object) -> None:
    vm.stack.extend([*args, name])
    vm.eval("hostcall", filename="<test>")


def test_utf8_size_matches_replace_encoding_without_a_bytes_copy() -> None:
    samples = [
        "",
        "ascii",
        "é",
        "𝄞",
        "a\ud800b",
        'quote " slash \\ newline\n nul\x00',
    ]
    for sample in samples:
        expected = len(sample.encode("utf-8", errors="replace"))
        assert utf8_size(sample) == expected
        assert estimate_host_value_budget(sample).bytes == expected

    assert utf8_size("ééé", stop_after=3) == 4


def test_malformed_hostcall_result_limits_fail_to_finite_defaults() -> None:
    vm = _vm()
    vm.hostcall_result_max_bytes = False  # type: ignore[assignment]
    vm.hostcall_result_max_cells = 3.5  # type: ignore[assignment]
    assert effective_hostcall_result_limits(vm) == (
        DEFAULT_HOSTCALL_RESULT_MAX_BYTES,
        8192,
    )


def test_s_plus_preflights_exact_utf8_bytes_and_preserves_arguments() -> None:
    vm = _vm()
    vm.hostcall_result_max_bytes = 3
    left = "é"
    right = "ab"

    with pytest.raises(Exception, match=r"s\+: 4 bytes > 3"):
        _hostcall(vm, "s+", left, right)
    assert vm.stack == [left, right]

    vm.stack.clear()
    vm.hostcall_result_max_bytes = 4
    _hostcall(vm, "s+", left, right)
    assert vm.pop_str() == "éab"


def test_s_split_preflights_list_cells_before_materializing_parts() -> None:
    vm = _vm()
    vm.hostcall_result_max_bytes = 100
    vm.hostcall_result_max_cells = 3

    with pytest.raises(Exception, match=r"s-split: 4 cells > 3"):
        _hostcall(vm, "s-split", "a,b,c", ",")
    assert vm.stack == ["a,b,c", ","]

    vm.stack.clear()
    vm.hostcall_result_max_cells = 4
    _hostcall(vm, "s-split", "a,b,c", ",")
    assert vm.pop_list() == ["a", "b", "c"]

    vm.stack.clear()
    vm.hostcall_result_max_cells = 3
    with pytest.raises(Exception, match=r"s-split: 4 cells > 3"):
        _hostcall(vm, "s-split", "abc", "")
    assert vm.stack == ["abc", ""]


def test_s_join_preflights_bytes_without_duplicating_or_consuming_parts() -> None:
    vm = _vm()
    parts = ["é", "x"]
    vm.hostcall_result_max_bytes = 3

    with pytest.raises(Exception, match=r"s-join: 4 bytes > 3"):
        _hostcall(vm, "s-join", parts, "-")
    assert vm.stack == [parts, "-"]
    assert vm.stack[0] is parts

    vm.stack.clear()
    shared = "é" * 32  # 64 UTF-8 bytes, repeated by reference.
    repeated = [shared] * 8
    exact_bytes = (64 * 8) + 7
    vm.hostcall_result_max_bytes = exact_bytes
    _hostcall(vm, "s-join", repeated, "|")
    assert vm.pop_str() == "|".join(repeated)

    # Type validity still wins over size policy, preserving the established
    # inspectable malformed-list contract.
    vm.stack.clear()
    bad_parts: list[object] = ["oversized", 2]
    vm.hostcall_result_max_bytes = 1
    with pytest.raises(Exception, match="expected list of str, got int"):
        _hostcall(vm, "s-join", bad_parts, "-")
    assert vm.stack == [bad_parts, "-"]


def test_s_join_alias_preflight_caches_sizes_and_stops_at_proven_overrun(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    vm = _vm()
    vm.hostcall_result_max_bytes = 30
    shared = "é" * 10  # 20 UTF-8 bytes, repeated by identity.
    parts = [shared] * 50_000
    calls: list[str] = []
    real_utf8_size = host_strings.utf8_size

    def counting_utf8_size(text: str, *, stop_after: int | None = None) -> int:
        calls.append(text)
        return real_utf8_size(text, stop_after=stop_after)

    monkeypatch.setattr(host_strings, "utf8_size", counting_utf8_size)
    with pytest.raises(Exception, match=r"s-join: 40 bytes > 30"):
        _hostcall(vm, "s-join", parts, "")

    # One delimiter scan plus one scan of the shared value is sufficient; the
    # second alias proves the overrun and the remaining 49,998 are untouched.
    assert calls == ["", shared]
    assert vm.stack == [parts, ""]


def test_s_replace_rejects_a_300_mb_projection_before_allocation() -> None:
    vm = _vm()
    source = "a" * 100_000
    old = "a"
    new = "b" * 3_000

    with pytest.raises(Exception, match=r"s-replace: 300000000 bytes > 1048576"):
        _hostcall(vm, "s-replace", source, old, new)
    assert vm.stack == [source, old, new]


def test_s_format_bounds_repeated_reference_amplification() -> None:
    vm = _vm()
    shared = "x" * 600_000
    value = [shared, shared]

    with pytest.raises(Exception, match=r"hostcall result budget exceeded: s-format"):
        _hostcall(vm, "s-format", value, "%s", 1)
    assert vm.stack == [value, "%s", 1]
    assert vm.stack[0] is value

    vm.stack.clear()
    vm.hostcall_result_max_bytes = 64
    _hostcall(vm, "s-format", [True, "é"], "%s", 1)
    assert vm.pop_str() == '[<bool True>, "é"]'


def test_to_str_uses_the_shared_bounded_renderer_and_keeps_source_on_denial() -> None:
    vm = _vm()
    shared = "x" * 600_000
    value = [shared, shared]
    vm.value_text_max_bytes = 1_000_000
    vm.stack.append(value)

    with pytest.raises(Exception, match=r"text result budget exceeded: to-str"):
        vm.eval("to-str", filename="<test>")
    assert vm.stack == [value]
    assert vm.stack[0] is value


def test_preallocation_survives_an_address_space_limit_that_cannot_fit_projection() -> None:
    if sys.platform != "linux" or not Path("/proc/self/statm").exists():
        pytest.skip("requires Linux RLIMIT_AS and /proc")

    script = r'''
import json
import os
import resource
from micromax import VM
from micromax import host_strings
from micromax.host_strings import install_string_hostcalls

vm = VM()
install_string_hostcalls(vm)
source = "a" * 100_000
old = "a"
new = "b" * 3_000
pages = int(open("/proc/self/statm", encoding="ascii").read().split()[0])
current_vms = pages * os.sysconf("SC_PAGE_SIZE")
soft, hard = resource.getrlimit(resource.RLIMIT_AS)
ceiling = current_vms + 128 * 1024 * 1024
if hard not in (-1, resource.RLIM_INFINITY):
    ceiling = min(ceiling, hard)
resource.setrlimit(resource.RLIMIT_AS, (ceiling, hard))
vm.stack.extend([source, old, new, "s-replace"])
try:
    vm.eval("hostcall", filename="<rlimit-probe>")
except Exception as exc:
    print(json.dumps({
        "type": type(exc).__name__,
        "message": str(exc),
        "stack_preserved": vm.stack == [source, old, new],
    }, sort_keys=True))
else:
    print(json.dumps({"type": "none", "message": "", "stack_preserved": False}))
'''
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src")
    proc = subprocess.run(
        [sys.executable, "-c", script],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=10,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload == {
        "message": (
            "hostcall result budget exceeded: s-replace: "
            "300000000 bytes > 1048576"
        ),
        "stack_preserved": True,
        "type": "MicromaxError",
    }
