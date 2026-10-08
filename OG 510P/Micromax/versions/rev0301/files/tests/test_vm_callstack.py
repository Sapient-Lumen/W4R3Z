from __future__ import annotations

from micromax import VM


def test_callstack_is_empty_at_top_level() -> None:
    vm = VM()
    vm.eval('callstack')
    xs = vm.pop_list()
    assert xs == []


def test_callstack_shows_nested_words_excluding_itself() -> None:
    vm = VM()
    vm.eval(': inner ( -- xs ) callstack ;')
    vm.eval(': outer ( -- xs ) inner ;')
    vm.eval('outer')
    xs = vm.pop_list()
    assert xs == ['outer', 'inner']


def test_trace_alias_matches_callstack() -> None:
    vm = VM()
    vm.eval(': inner ( -- xs ) trace ;')
    vm.eval(': outer ( -- xs ) inner ;')
    vm.eval('outer')
    xs = vm.pop_list()
    assert xs == ['outer', 'inner']
