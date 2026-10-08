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


def test_s_split_preflights_argument_shape_before_consuming_arguments() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*scratch*", "")
    vm = ed.vm

    vm.stack.clear()
    vm.stack.extend([123, ",", "s-split"])
    with pytest.raises(Exception) as excinfo:
        vm.eval("hostcall", filename="<test>")
    assert "s-split: source must be str, got int" in str(excinfo.value)
    assert vm.stack == [123, ","]

    vm.stack.clear()
    vm.stack.extend(["a,b", 1, "s-split"])
    with pytest.raises(Exception) as excinfo:
        vm.eval("hostcall", filename="<test>")
    assert "s-split: delimiter must be str, got int" in str(excinfo.value)
    assert vm.stack == ["a,b", 1]

    vm.stack.clear()
    vm.stack.extend(["only", "s-split"])
    with pytest.raises(Exception) as excinfo:
        vm.eval("hostcall", filename="<test>")
    assert "s-split: not enough arguments" in str(excinfo.value)
    assert vm.stack == ["only"]

    vm.stack.clear()
    vm.stack.extend(["a,b", ",", "s-split"])
    vm.eval("hostcall", filename="<test>")
    assert vm.pop_list() == ["a", "b"]

    vm.stack.clear()
    vm.stack.extend(["ab", "", "s-split"])
    vm.eval("hostcall", filename="<test>")
    assert vm.pop_list() == ["a", "b"]


def test_s_replace_rejects_empty_search_before_output() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*scratch*", "")
    vm = ed.vm

    with pytest.raises(Exception) as excinfo:
        vm.eval('"ab" "" "X" s-replace', filename='<test>')
    assert "s-replace: empty search" in str(excinfo.value)
    assert vm.stack == ["ab", "", "X"]

    # Positive-width replacement remains unchanged.
    vm.stack.clear()
    vm.eval('"abab" "a" "x" s-replace', filename='<test>')
    assert vm.pop_str() == 'xbxb'


def test_s_replace_preflights_argument_shape_before_consuming_arguments() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*scratch*", "")
    vm = ed.vm

    vm.stack.clear()
    vm.stack.extend([123, "a", "b", "s-replace"])
    with pytest.raises(Exception) as excinfo:
        vm.eval("hostcall", filename="<test>")
    assert "s-replace: source must be str, got int" in str(excinfo.value)
    assert vm.stack == [123, "a", "b"]

    vm.stack.clear()
    vm.stack.extend(["abc", 1, "b", "s-replace"])
    with pytest.raises(Exception) as excinfo:
        vm.eval("hostcall", filename="<test>")
    assert "s-replace: old must be str, got int" in str(excinfo.value)
    assert vm.stack == ["abc", 1, "b"]

    vm.stack.clear()
    vm.stack.extend(["abc", "a", 2, "s-replace"])
    with pytest.raises(Exception) as excinfo:
        vm.eval("hostcall", filename="<test>")
    assert "s-replace: new must be str, got int" in str(excinfo.value)
    assert vm.stack == ["abc", "a", 2]

    vm.stack.clear()
    vm.stack.extend(["abc", "", "X", "s-replace"])
    with pytest.raises(Exception) as excinfo:
        vm.eval("hostcall", filename="<test>")
    assert "s-replace: empty search" in str(excinfo.value)
    assert vm.stack == ["abc", "", "X"]

    vm.stack.clear()
    vm.stack.extend(["abc", "a", "X", "s-replace"])
    vm.eval("hostcall", filename="<test>")
    assert vm.pop_str() == "Xbc"


def test_s_join_preflights_list_contents_before_consuming_arguments() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*scratch*", "")
    vm = ed.vm

    vm.stack.clear()
    bad_parts = ["a", 2, "c"]
    vm.stack.extend([bad_parts, ",", "s-join"])
    with pytest.raises(Exception) as excinfo:
        vm.eval("hostcall", filename="<test>")
    assert "s-join: expected list of str, got int" in str(excinfo.value)
    assert vm.stack == [bad_parts, ","]

    vm.stack.clear()
    vm.stack.extend(["not-a-list", ",", "s-join"])
    with pytest.raises(Exception) as excinfo:
        vm.eval("hostcall", filename="<test>")
    assert "s-join: expected list of str, got str" in str(excinfo.value)
    assert vm.stack == ["not-a-list", ","]

    vm.stack.clear()
    vm.stack.extend([["a", "b"], 1, "s-join"])
    with pytest.raises(Exception) as excinfo:
        vm.eval("hostcall", filename="<test>")
    assert "s-join: delimiter must be str, got int" in str(excinfo.value)
    assert vm.stack == [["a", "b"], 1]

    vm.stack.clear()
    vm.stack.extend([["a", "b"], "-", "s-join"])
    vm.eval("hostcall", filename="<test>")
    assert vm.pop_str() == "a-b"

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


def test_s_slice_rejects_python_boolean_index_sentinels() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*scratch*", "")
    vm = ed.vm

    vm.stack.clear()
    vm.stack.extend(["abcdef", False, 4, "s-slice"])
    with pytest.raises(Exception) as excinfo:
        vm.eval("hostcall", filename="<test>")
    msg = str(excinfo.value)
    assert "s-slice: start must be an integer" in msg
    assert "boolean False" in msg
    assert vm.stack == []

    vm.stack.clear()
    vm.stack.extend(["abcdef", 1, True, "s-slice"])
    with pytest.raises(Exception) as excinfo:
        vm.eval("hostcall", filename="<test>")
    msg = str(excinfo.value)
    assert "s-slice: end must be an integer" in msg
    assert "boolean True" in msg
    assert vm.stack == []

    vm.eval('"abcdef" 0 1 s-slice', filename='<test>')
    assert vm.pop_str() == 'a'




def test_s_format_d_rejects_python_boolean_data_sentinels() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*scratch*", "")
    vm = ed.vm

    vm.stack.clear()
    vm.stack.extend([True, "%d", 1, "s-format"])
    with pytest.raises(Exception) as excinfo:
        vm.eval("hostcall", filename="<test>")
    msg = str(excinfo.value)
    assert "s-format: %d expects int" in msg
    assert "boolean True" in msg
    assert vm.stack == [True]

    vm.stack.clear()
    vm.stack.extend([False, "%d", 1, "s-format"])
    with pytest.raises(Exception) as excinfo:
        vm.eval("hostcall", filename="<test>")
    msg = str(excinfo.value)
    assert "s-format: %d expects int" in msg
    assert "boolean False" in msg
    assert vm.stack == [False]

    vm.eval('0 "%d" 1 s-format', filename='<test>')
    assert vm.pop_str() == '0'
    vm.eval('1 "%d" 1 s-format', filename='<test>')
    assert vm.pop_str() == '1'


def test_s_format_s_renders_python_boolean_data_sentinels_explicitly() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*scratch*", "")
    vm = ed.vm

    vm.stack.clear()
    vm.stack.extend([True, "%s", 1, "s-format"])
    vm.eval("hostcall", filename="<test>")
    assert vm.pop_str() == "<bool True>"

    vm.stack.clear()
    vm.stack.extend([False, "%s", 1, "s-format"])
    vm.eval("hostcall", filename="<test>")
    assert vm.pop_str() == "<bool False>"

    vm.stack.clear()
    vm.stack.extend([[True, False], "%s", 1, "s-format"])
    vm.eval("hostcall", filename="<test>")
    assert vm.pop_str() == "[<bool True>, <bool False>]"

    vm.eval('1 "%s" 1 s-format', filename='<test>')
    assert vm.pop_str() == '1'


def test_s_format_s_renders_python_boolean_map_keys_explicitly() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*scratch*", "")
    vm = ed.vm

    vm.stack.clear()
    vm.stack.extend([{True: "yes", False: "no"}, "%s", 1, "s-format"])
    vm.eval("hostcall", filename="<test>")
    assert vm.pop_str() == '{"<bool False>": "no", "<bool True>": "yes"}'

    # Ordinary non-boolean keys keep the existing JSON-ish stringified-key surface.
    vm.stack.clear()
    vm.stack.extend([{1: "one", "two": 2}, "%s", 1, "s-format"])
    vm.eval("hostcall", filename="<test>")
    assert vm.pop_str() == '{"1": "one", "two": 2}'


def test_s_format_rejects_python_boolean_count_sentinels() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*scratch*", "")
    vm = ed.vm

    vm.stack.clear()
    vm.stack.extend(["hi", "%s", True, "s-format"])
    with pytest.raises(Exception) as excinfo:
        vm.eval("hostcall", filename="<test>")
    msg = str(excinfo.value)
    assert "s-format: n must be an integer" in msg
    assert "boolean True" in msg
    assert vm.stack == ["hi"]

    vm.stack.clear()
    vm.stack.extend(["%s", False, "s-format"])
    with pytest.raises(Exception) as excinfo:
        vm.eval("hostcall", filename="<test>")
    msg = str(excinfo.value)
    assert "s-format: n must be an integer" in msg
    assert "boolean False" in msg
    assert vm.stack == []

    vm.eval('"100%%" 0 s-format', filename='<test>')
    assert vm.pop_str() == '100%'




def test_s_format_preflights_format_plan_before_consuming_data() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*scratch*", "")
    vm = ed.vm

    with pytest.raises(Exception) as excinfo:
        vm.eval('1 "%q" 1 format', filename='<test>')
    assert "s-format: unknown specifier %q" in str(excinfo.value)
    assert vm.stack == [1]

    vm.stack.clear()
    with pytest.raises(Exception) as excinfo:
        vm.eval('1 "%" 1 format', filename='<test>')
    assert "s-format: trailing %" in str(excinfo.value)
    assert vm.stack == [1]

    vm.stack.clear()
    with pytest.raises(Exception) as excinfo:
        vm.eval('1 "%d %d" 1 format', filename='<test>')
    assert "s-format: not enough arguments" in str(excinfo.value)
    assert vm.stack == [1]

    vm.stack.clear()
    with pytest.raises(Exception) as excinfo:
        vm.eval('1 2 "%d" 2 format', filename='<test>')
    assert "s-format: too many arguments" in str(excinfo.value)
    assert vm.stack == [1, 2]

    vm.stack.clear()
    vm.stack.extend(["left", "%q", 1, "s-format"])
    with pytest.raises(Exception) as excinfo:
        vm.eval("hostcall", filename="<test>")
    assert "s-format: unknown specifier %q" in str(excinfo.value)
    assert vm.stack == ["left"]

    vm.eval('1 2 "%d %d" 2 s-format', filename='<test>')
    assert vm.pop_str() == '1 2'

def test_s_format_preflights_percent_d_data_before_consuming_data() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*scratch*", "")
    vm = ed.vm

    with pytest.raises(Exception) as excinfo:
        vm.eval('"not-an-int" "%d" 1 format', filename='<test>')
    assert "s-format: %d expects int" in str(excinfo.value)
    assert vm.stack == ["not-an-int"]

    vm.stack.clear()
    with pytest.raises(Exception) as excinfo:
        vm.eval('10 "bad" "%d %d" 2 format', filename='<test>')
    assert "s-format: %d expects int" in str(excinfo.value)
    assert vm.stack == [10, "bad"]

    vm.stack.clear()
    vm.stack.extend([object(), "%d", 1, "s-format"])
    bad = vm.stack[0]
    with pytest.raises(Exception) as excinfo:
        vm.eval("hostcall", filename="<test>")
    assert "s-format: %d expects int" in str(excinfo.value)
    assert vm.stack == [bad]

    vm.eval('"42" "%d" 1 s-format', filename='<test>')
    assert vm.pop_str() == '42'


def test_s_format_rejects_count_larger_than_available_data_cleanly() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*scratch*", "")
    vm = ed.vm

    with pytest.raises(Exception) as excinfo:
        vm.eval('1 "%d %d" 2 format', filename='<test>')
    assert "s-format: not enough arguments" in str(excinfo.value)
    assert "Stack underflow" not in str(excinfo.value)
    assert vm.stack == [1]

    vm.stack.clear()
    vm.stack.extend(["only", "%s %s", 2, "s-format"])
    with pytest.raises(Exception) as excinfo:
        vm.eval("hostcall", filename="<test>")
    assert "s-format: not enough arguments" in str(excinfo.value)
    assert vm.stack == ["only"]

    vm.eval('1 2 "%d %d" 2 s-format', filename='<test>')
    assert vm.pop_str() == '1 2'
