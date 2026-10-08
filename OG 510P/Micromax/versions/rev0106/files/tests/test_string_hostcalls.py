import pytest
from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def test_string_hostcalls_words_exist_and_work() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*scratch*", "")

    vm = ed.vm

    vm.eval('"hi" "there" s+', filename='<test>')
    assert vm.pop_str() == 'hithere'

    vm.eval('"abcdef" 1 4 s-slice', filename='<test>')
    assert vm.pop_str() == 'bcd'

    vm.eval('"a,b,c" "," s-split', filename='<test>')
    assert vm.pop_list() == ['a', 'b', 'c']

    vm.eval('list "a" swap push "b" swap push "," s-join', filename='<test>')
    assert vm.pop_str() == 'a,b'

    vm.eval('"abab" "a" "x" s-replace', filename='<test>')
    assert vm.pop_str() == 'xbxb'

    vm.eval('"  Mixed  " s-trim s-upper', filename='<test>')
    assert vm.pop_str() == 'MIXED'


def test_string_hostcalls_are_advertised() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    vm = ed.vm
    vm.eval('"mx.strings" host.feature?', filename='<test>')
    assert vm.pop_int() == 1


def test_s_format_and_format_alias() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*scratch*", "")
    vm = ed.vm

    vm.eval('10 20 "%d lines, %d cols" 2 format', filename='<test>')
    assert vm.pop_str() == '10 lines, 20 cols'

    vm.eval('"hi" "%s!" 1 s-format', filename='<test>')
    assert vm.pop_str() == 'hi!'

    vm.eval('"100%%" 0 format', filename='<test>')
    assert vm.pop_str() == '100%'

    with pytest.raises(Exception):
        vm.eval('1 "%d %d" 2 format', filename='<test>')
