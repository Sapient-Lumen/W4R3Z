from __future__ import annotations

import pytest

from micromax import MicromaxError, VM
from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def test_vm_hostcall_result_budget_restores_stack_arguments() -> None:
    vm = VM(load_stdlib=False)

    def explode(v: VM) -> None:
        s = v.pop_str()
        v.stack.append(s + s)

    vm.register_host("explode", explode)
    vm.hostcall_result_max_bytes = 3
    vm.hostcall_result_max_cells = 100
    vm.stack.extend(["aa", "explode"])

    with pytest.raises(MicromaxError) as excinfo:
        vm.eval("hostcall", filename="<budget-test>")

    assert "hostcall result budget exceeded: explode" in str(excinfo.value)
    assert "bytes >" in str(excinfo.value)
    assert vm.stack == ["aa"]


def test_vm_hostcall_result_cell_budget_rejects_nested_result_payload() -> None:
    vm = VM(load_stdlib=False)

    def many_rows(v: VM) -> None:
        count = v.pop_int()
        v.stack.append([{"n": i, "label": f"row-{i}"} for i in range(count)])

    vm.register_host("many-rows", many_rows)
    vm.hostcall_result_max_bytes = 10_000
    vm.hostcall_result_max_cells = 8
    vm.stack.extend([4, "many-rows"])

    with pytest.raises(MicromaxError) as excinfo:
        vm.eval("hostcall", filename="<budget-test>")

    assert "hostcall result budget exceeded: many-rows" in str(excinfo.value)
    assert "cells >" in str(excinfo.value)
    assert vm.stack == [4]


def test_regex_helper_large_result_is_caught_by_shared_hostcall_budget() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*scratch*", "")
    vm = ed.vm
    vm.hostcall_result_max_bytes = 100_000
    vm.hostcall_result_max_cells = 5

    with pytest.raises(MicromaxError) as excinfo:
        vm.eval('"aaaa" "a" 0 "" re-findall', filename="<budget-test>")

    assert "hostcall result budget exceeded: re.findall" in str(excinfo.value)
    assert vm.stack == ["aaaa", "a", 0, ""]


def test_prospective_hostcall_result_budget_uses_standard_message() -> None:
    from micromax.host_limits import hostcall_result_budget_violation_from_counts

    assert (
        hostcall_result_budget_violation_from_counts(
            "prospective",
            byte_count=8,
            cell_count=2,
            max_bytes=8,
            max_cells=2,
        )
        is None
    )
    assert hostcall_result_budget_violation_from_counts(
        "prospective",
        byte_count=9,
        cell_count=2,
        max_bytes=8,
        max_cells=2,
    ) == "hostcall result budget exceeded: prospective: 9 bytes > 8"
    assert hostcall_result_budget_violation_from_counts(
        "prospective",
        byte_count=8,
        cell_count=3,
        max_bytes=8,
        max_cells=2,
    ) == "hostcall result budget exceeded: prospective: 3 cells > 2"


def test_hostcall_budget_estimates_giant_integer_without_decimal_conversion() -> None:
    vm = VM(load_stdlib=False)
    giant = 1 << 100_000

    def return_giant(v: VM) -> None:
        v.pop()
        v.stack.append(giant)

    vm.register_host("return-giant", return_giant)
    vm.hostcall_result_max_bytes = 32
    vm.hostcall_result_max_cells = 100
    vm.stack.extend(["sentinel", "return-giant"])

    with pytest.raises(MicromaxError) as excinfo:
        vm.eval("hostcall", filename="<giant-int-budget>")

    message = str(excinfo.value)
    assert "hostcall result budget exceeded: return-giant" in message
    assert "bytes > 32" in message
    assert vm.stack == ["sentinel"]
