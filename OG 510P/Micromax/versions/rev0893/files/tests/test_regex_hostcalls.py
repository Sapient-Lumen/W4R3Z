import re

import pytest

from micromax.regex_tools import convert_replacement_template, parse_re_flags
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


def test_re_match_maps_mark_unmatched_captures_as_absent_not_text_none() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')
    vm = ed.vm

    vm.eval('"b" "(?P<a>a)?b(?P<c>c)?" 0 "" re-search', filename='<test>')
    m = vm.pop_map()
    assert m['group'] == 'b'
    assert m['groups'] == [0, 0]
    assert m['groupdict'] == {'a': 0, 'c': 0}

    # A capture that participates with an empty string is different from an
    # unmatched optional capture.  Keep that distinction visible to scripts.
    vm.eval('"b" "(?P<empty>a*)b(?P<miss>c)?" 0 "" re-search', filename='<test>')
    m = vm.pop_map()
    assert m['groups'] == ['', 0]
    assert m['groupdict'] == {'empty': '', 'miss': 0}

    vm.eval('"b ax" "(?P<a>a)?(?P<body>b|x)" 0 "" re-findall', filename='<test>')
    rows = vm.pop_list()
    assert rows[0]['groups'] == [0, 'b']
    assert rows[0]['groupdict'] == {'a': 0, 'body': 'b'}
    assert rows[1]['groups'] == ['a', 'x']
    assert rows[1]['groupdict'] == {'a': 'a', 'body': 'x'}




def test_re_search_and_findall_reject_negative_start_positions() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')
    vm = ed.vm

    with pytest.raises(Exception) as excinfo:
        vm.eval('"abc" "a" -1 "" re-search', filename='<test>')
    msg = str(excinfo.value)
    assert "re: start must be non-negative" in msg
    assert "-1" in msg

    with pytest.raises(Exception) as excinfo:
        vm.eval('"abc" "a" -2 "" re-findall', filename='<test>')
    msg = str(excinfo.value)
    assert "re: start must be non-negative" in msg
    assert "-2" in msg

    # Out-of-range positive starts are ordinary empty searches, not errors.
    vm.eval('"abc" "a" 99 "" re-search', filename='<test>')
    assert vm.pop_int() == 0
    vm.eval('"abc" "a" 99 "" re-findall', filename='<test>')
    assert vm.pop_list() == []

    # Python's engine clamps an over-large pos to len(hay) for zero-width
    # patterns.  Micromax keeps the visible start-index contract explicit: past
    # EOF means no search space even for empty / end-anchored patterns.
    vm.eval('"abc" "" 99 "" re-search', filename='<test>')
    assert vm.pop_int() == 0
    vm.eval('"abc" "$" 99 "" re-search', filename='<test>')
    assert vm.pop_int() == 0
    vm.eval('"abc" "(?=)" 99 "" re-findall', filename='<test>')
    assert vm.pop_list() == []


def test_re_search_and_findall_reject_boolean_start_sentinels() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')
    vm = ed.vm

    vm.stack.clear()
    vm.stack.extend(["abc", "a", False, "", "re.search"])
    with pytest.raises(Exception) as excinfo:
        vm.eval("hostcall", filename="<test>")
    msg = str(excinfo.value)
    assert "re: start must be an integer" in msg
    assert "boolean False" in msg
    assert vm.stack == []

    vm.stack.clear()
    vm.stack.extend(["abc", "a", True, "", "re.findall"])
    with pytest.raises(Exception) as excinfo:
        vm.eval("hostcall", filename="<test>")
    msg = str(excinfo.value)
    assert "re: start must be an integer" in msg
    assert "boolean True" in msg
    assert vm.stack == []

    # The portable VM-facing spelling for the beginning of the haystack remains
    # the integer 0.
    vm.eval('"abc" "a" 0 "" re-search', filename='<test>')
    assert vm.pop_map()["start"] == 0

def test_re_flags_stay_in_portable_zero_or_string_dialect(capsys) -> None:
    assert parse_re_flags(0) == 0
    assert parse_re_flags("") == 0
    assert parse_re_flags("i m s") == re.IGNORECASE | re.MULTILINE | re.DOTALL

    with pytest.raises(TypeError) as excinfo:
        parse_re_flags(None)
    assert "got None" in str(excinfo.value)

    with pytest.raises(TypeError) as excinfo:
        parse_re_flags(False)
    assert "boolean False" in str(excinfo.value)

    with pytest.raises(TypeError) as excinfo:
        parse_re_flags(True)
    assert "boolean True" in str(excinfo.value)

    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')
    vm = ed.vm

    with pytest.raises(Exception) as excinfo:
        vm.eval('"abc" "a" 0 128 re-search', filename='<test>')

    msg = str(excinfo.value)
    assert "invalid regex:" in msg
    assert "regex flags must be 0 or a string of ims flags" in msg
    assert "128" in msg
    captured = capsys.readouterr()
    assert captured.out == ""

    vm.stack.clear()
    vm.stack.extend(["abc", "a", 0, None, "re.search"])
    with pytest.raises(Exception) as excinfo:
        vm.eval("hostcall", filename="<test>")
    msg = str(excinfo.value)
    assert "invalid regex:" in msg
    assert "flags must be 0 or a string of ims flags" in msg
    assert "None" in msg
    assert vm.stack == []

    vm.stack.clear()
    vm.stack.extend(["abc", "a", 0, False, "re.search"])
    with pytest.raises(Exception) as excinfo:
        vm.eval("hostcall", filename="<test>")
    msg = str(excinfo.value)
    assert "invalid regex:" in msg
    assert "boolean False" in msg
    assert vm.stack == []


def test_re_flags_reject_unknown_string_flags() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')
    vm = ed.vm

    with pytest.raises(Exception) as excinfo:
        vm.eval('"abc" "a" 0 "x" re-search', filename='<test>')

    msg = str(excinfo.value)
    assert "invalid regex:" in msg
    assert "unknown regex flag: 'x'" in msg

def test_replacement_template_uses_dollar_dialect_not_python_backrefs() -> None:
    pat = re.compile(r"a([0-9])")

    assert pat.sub(convert_replacement_template(r"b$1"), "a1") == "b1"
    assert pat.sub(convert_replacement_template(r"\1"), "a1") == r"\1"
    assert pat.sub(convert_replacement_template(r"\q"), "a1") == r"\q"


def test_replacement_template_preserves_sentinel_like_user_text() -> None:
    pat = re.compile(r"a([0-9])")

    assert pat.sub(convert_replacement_template("\u0000DOLLAR\u0000"), "a1") == "\u0000DOLLAR\u0000"
    assert pat.sub(convert_replacement_template("\u0000REF0\u0000$1"), "a1") == "\u0000REF0\u00001"
    assert pat.sub(convert_replacement_template("$é$١"), "a1") == "$é$١"
    assert convert_replacement_template("$$") == "$"





def test_replacement_template_keeps_leading_zero_numeric_tokens_literal() -> None:
    pat = re.compile(r"(a)(b)")

    assert pat.sub(convert_replacement_template("$0"), "ab") == "ab"
    assert pat.sub(convert_replacement_template("$1"), "ab") == "a"
    assert pat.sub(convert_replacement_template("$01"), "ab") == "$01"
    assert pat.sub(convert_replacement_template("${01}"), "ab") == "${01}"


def test_malformed_braced_replacement_templates_stay_literal() -> None:
    pat = re.compile(r"(?P<x>a)")

    assert pat.sub(convert_replacement_template("${x>tail}"), "a") == "${x>tail}"
    assert pat.sub(convert_replacement_template("${$1}"), "a") == "${$1}"
    assert pat.sub(convert_replacement_template("${1abc}"), "a") == "${1abc}"
    assert pat.sub(convert_replacement_template(r"${x\y}"), "a") == r"${x\y}"
    assert pat.sub(convert_replacement_template("${x}"), "a") == "a"
    assert pat.sub(convert_replacement_template("${1}"), "a") == "a"


def test_unterminated_braced_replacement_templates_stay_literal() -> None:
    pat = re.compile(r"(?P<x>a)")

    assert pat.sub(convert_replacement_template("${$1"), "a") == "${$1"
    assert pat.sub(convert_replacement_template("${x$1"), "a") == "${x$1"
    assert pat.sub(convert_replacement_template(r"${x\$1"), "a") == r"${x\$1"
    assert pat.sub(convert_replacement_template("before ${x"), "a") == "before ${x"


def test_re_sub_keeps_malformed_braced_templates_literal() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')
    vm = ed.vm

    vm.eval('"a" "(?P<x>a)" "${x>tail}" "" re-sub', filename='<test>')
    assert vm.pop_str() == '${x>tail}'

    vm.eval('"a" "(?P<x>a)" "${$1}" "" re-sub', filename='<test>')
    assert vm.pop_str() == '${$1}'


def test_re_sub_keeps_python_backslash_templates_literal() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')
    vm = ed.vm

    vm.eval(r'"abc123def" "([0-9]+)" "[\\1]" "" re-sub', filename='<test>')
    assert vm.pop_str() == r"abc[\1]def"

    vm.eval(r'"abc123def" "([0-9]+)" "[\\q]" "" re-sub', filename='<test>')
    assert vm.pop_str() == r"abc[\q]def"



def test_re_sub_and_subn_reject_zero_width_matches_before_output() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')
    vm = ed.vm

    with pytest.raises(Exception) as excinfo:
        vm.eval('"abc" "" "X" "" re-sub', filename='<test>')
    assert "re.sub: zero-width matches are not supported" in str(excinfo.value)

    with pytest.raises(Exception) as excinfo:
        vm.eval('"abc" "^" "X" "" re-subn', filename='<test>')
    assert "re.subn: zero-width matches are not supported" in str(excinfo.value)

    with pytest.raises(Exception) as excinfo:
        vm.eval('"abc" "(?=b)" "X" "" re-sub', filename='<test>')
    assert "re.sub: zero-width matches are not supported" in str(excinfo.value)

    # A zero-width-capable pattern that has no match is still an ordinary no-op.
    vm.eval('"abc" "(?=z)" "X" "" re-sub', filename='<test>')
    assert vm.pop_str() == 'abc'

    # Positive-width substitutions continue to work.
    vm.eval('"abc" "a+" "X" "" re-subn', filename='<test>')
    n = vm.pop_int()
    out = vm.pop_str()
    assert (out, n) == ('Xbc', 1)


def test_re_sub_and_subn_report_invalid_replacements_explicitly() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')
    vm = ed.vm

    with pytest.raises(Exception) as excinfo:
        vm.eval('"abc" "(a)" "$2" "" re-sub', filename='<test>')
    msg = str(excinfo.value)
    assert "re.sub: invalid replacement:" in msg
    assert "invalid group reference 2" in msg
    assert vm.stack == []

    with pytest.raises(Exception) as excinfo:
        vm.eval('"abc" "(?P<x>a)" "$missing" "" re-subn', filename='<test>')
    msg = str(excinfo.value)
    assert "re.subn: invalid replacement:" in msg
    assert "unknown group name 'missing'" in msg
    assert vm.stack == []

    # Replacement-template mistakes should stay visible even when the pattern
    # has no matches; otherwise a typo could be hidden as an ordinary no-op.
    with pytest.raises(Exception) as excinfo:
        vm.eval('"abc" "(z)" "$2" "" re-sub', filename='<test>')
    msg = str(excinfo.value)
    assert "re.sub: invalid replacement:" in msg
    assert "invalid group reference 2" in msg
    assert vm.stack == []


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
