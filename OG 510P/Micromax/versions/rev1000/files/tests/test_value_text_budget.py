from __future__ import annotations

import json

import pytest

from micromax import MicromaxError, VM
from micromax.value_text import BoundedTextBuilder, TextResultBudgetExceeded


@pytest.mark.parametrize(
    "value",
    [
        "plain",
        "quote: \" and slash: \\",
        "line\nfeed\tand\x00control",
        "café 😀",
        "\ud800",
        "\u2028",
    ],
)
def test_json_string_builder_accounts_exact_utf8_bytes(value: str) -> None:
    expected = json.dumps(value, ensure_ascii=False)
    exact_bytes = len(expected.encode("utf-8", errors="replace"))

    builder = BoundedTextBuilder(action="json-test", max_bytes=exact_bytes)
    builder.append_json_string(value)
    assert builder.finish() == expected
    assert builder.bytes_used == exact_bytes

    with pytest.raises(TextResultBudgetExceeded):
        smaller = BoundedTextBuilder(action="json-test", max_bytes=exact_bytes - 1)
        smaller.append_json_string(value)


def test_large_integer_is_denied_before_decimal_rendering() -> None:
    builder = BoundedTextBuilder(action="integer-test", max_bytes=32)

    with pytest.raises(TextResultBudgetExceeded) as excinfo:
        builder.append_int(1 << 100_000)

    assert excinfo.value.observed_bytes > 32
    assert builder.finish() == ""


def test_to_str_bounds_shared_reference_amplification_and_preserves_operand() -> None:
    vm = VM()
    vm.value_text_max_bytes = 128
    shared = "x" * 64
    source = [shared] * 16
    vm.stack.append(source)

    with pytest.raises(MicromaxError, match=r"text result budget exceeded: to-str"):
        vm.eval("to-str", filename="<value-text-budget>")

    assert vm.stack == [source]
    assert vm.stack[0] is source

    vm.stack.clear()
    vm.eval("20 22 +", filename="<after-value-text-budget>")
    assert vm.pop_int() == 42


def test_to_str_keeps_stable_nested_representation_and_stops_cycles() -> None:
    vm = VM()
    source: list[object] = ["café", 7, {"b": "two", "a": 1}]
    source.append(source)
    vm.stack.append(source)

    vm.eval("to-str", filename="<value-text-shape>")
    rendered = vm.pop_str()

    assert rendered.startswith('["café", 7, {"a": 1, "b": "two"}, [')
    assert "..." in rendered
    assert len(rendered.encode("utf-8")) <= vm.value_text_max_bytes


def test_dot_and_dots_bound_debug_rendering_before_output_or_consumption(capsys) -> None:
    vm = VM()
    vm.value_text_max_bytes = 96
    shared = "z" * 48
    source = [shared] * 12
    vm.stack.append(source)

    with pytest.raises(MicromaxError, match=r"text result budget exceeded: \."):
        vm.eval(".", filename="<dot-budget>")
    assert vm.stack == [source]
    assert capsys.readouterr().out == ""

    with pytest.raises(MicromaxError, match=r"text result budget exceeded: \.s"):
        vm.eval(".s", filename="<dots-budget>")
    assert vm.stack == [source]
    assert capsys.readouterr().out == ""

    vm.stack.clear()
    vm.stack.append("hello")
    vm.eval(".", filename="<dot-compatible>")
    assert vm.stack == []
    assert capsys.readouterr().out == "hello"
