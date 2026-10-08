import pytest

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def test_regex_hostcalls_are_advertised() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    vm = ed.vm
    vm.eval('"mx.regex" host.feature?', filename='<test>')
    assert vm.pop_int() == 1


def test_re_search_and_group_expansion() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')
    vm = ed.vm

    vm.eval('"abc123def" "([0-9]+)" 0 "" re-search', filename='<test>')
    m = vm.pop_map()
    assert m['start'] == 3
    assert m['end'] == 6
    assert m['group'] == '123'
    assert m['groups'] == ['123']

    # $1 template expansion via re-sub.
    vm.eval('"abc123def" "([0-9]+)" "[$1]" "" re-sub', filename='<test>')
    assert vm.pop_str() == 'abc[123]def'

    # Named groups: ${name}
    vm.eval('"x=42" "x=(?P<n>[0-9]+)" "${n}" "" re-sub', filename='<test>')
    assert vm.pop_str() == '42'

    # $$ is a literal '$'
    vm.eval('"x" "x" "$$" "" re-sub', filename='<test>')
    assert vm.pop_str() == '$'


def test_re_subn_returns_count() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')
    vm = ed.vm

    vm.eval('"a1a2a3" "a" "b" "" re-subn', filename='<test>')
    n = vm.pop_int()
    out = vm.pop_str()
    assert out == 'b1b2b3'
    assert n == 3


def test_re_invalid_pattern_raises() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')
    vm = ed.vm

    with pytest.raises(Exception):
        vm.eval('"abc" "(" 0 "" re-search', filename='<test>')
