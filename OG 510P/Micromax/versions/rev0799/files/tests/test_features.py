from __future__ import annotations

import textwrap

import pytest

from micromax import VM, MicromaxError


def test_doc_capture_from_paren_comment() -> None:
    vm = VM()
    vm.eval(": inc ( n -- n ) ( add one ) 1 + ;")
    w = vm.find_word("inc")
    assert w is not None
    assert getattr(w, "effect", "") == "( n -- n )"
    assert getattr(w, "doc", "") == "add one"


def test_lists_basic() -> None:
    vm = VM()
    vm.eval("1 list push dup clone dup len")
    n = vm.pop_int()
    lst2 = vm.pop_list()
    lst1 = vm.pop_list()
    assert n == 1
    assert lst1 == [1]
    assert lst2 == [1]

    # pop from the cloned list
    vm.stack.append(lst1)
    vm.stack.append(lst2)
    vm.eval("pop")
    lst2_after = vm.pop_list()
    x = vm.pop()
    lst1_after = vm.pop_list()
    assert x == 1
    assert lst2_after == []
    assert lst1_after == [1]


def test_hooks_run_in_order() -> None:
    vm = VM()
    vm.eval(
        textwrap.dedent(
            """
            variable acc
            list acc !

            : h1 ( -- ) acc @ 1 swap push acc ! ;
            : h2 ( -- ) acc @ 2 swap push acc ! ;
            hook on-save
            ' h1 hook-add on-save
            ' h2 hook-add on-save
            on-save
            acc @
            """
        )
    )
    assert vm.pop_list() == [1, 2]


def test_modules_isolate_and_use() -> None:
    vm = VM()
    vm.eval("module foo : a 123 ; endmodule")
    with pytest.raises(MicromaxError):
        vm.eval("a")
    vm.eval("use foo a")
    assert vm.pop_int() == 123


def test_require_loads_once(tmp_path) -> None:
    vm = VM()
    vm.eval("variable loads 0 loads !")
    p = tmp_path / "once.mf"
    p.write_text("loads @ 1 + loads !\n", encoding="utf-8")
    vm.eval(f'"{p}" require')
    vm.eval(f'"{p}" require')
    vm.eval("loads @")
    assert vm.pop_int() == 1


def test_locals_sugar_and_shadowing() -> None:
    vm = VM()
    vm.eval("99 constant x")
    vm.eval(": add2 ( n -- n ) ->x x 2 + ;")
    vm.eval("5 add2")
    assert vm.pop_int() == 7

    # local shadows dictionary word
    vm.eval(": use_local ( -- n ) 1 ->x x ;")
    vm.eval("use_local")
    assert vm.pop_int() == 1


def test_session_locals_persist_and_can_be_cleared() -> None:
    vm = VM()
    vm.eval("123 ->a")
    vm.eval("a")
    assert vm.pop_int() == 123
    vm.eval("locals-clear")
    with pytest.raises(MicromaxError):
        vm.eval("a")


def test_send_and_dot_sugar() -> None:
    vm = VM()
    vm.eval("1 list push dup .len")  # .len => "len" send
    n = vm.pop_int()
    lst = vm.pop_list()
    assert n == 1
    assert lst == [1]

    with pytest.raises(MicromaxError):
        vm.eval('"nope" send')


def test_reload_and_unrequire(tmp_path) -> None:
    vm = VM()
    vm.eval("variable loads 0 loads !")
    p = tmp_path / "x.mf"
    p.write_text("loads @ 1 + loads !\n", encoding="utf-8")

    vm.eval(f'"{p}" require')
    vm.eval(f'"{p}" require')
    vm.eval("loads @")
    assert vm.pop_int() == 1

    vm.eval(f'"{p}" reload')
    vm.eval("loads @")
    assert vm.pop_int() == 2

    vm.eval(f'"{p}" unrequire')
    vm.eval(f'"{p}" require')
    vm.eval("loads @")
    assert vm.pop_int() == 3


def test_host_api_version_and_feature_query() -> None:
    vm = VM()
    vm.eval("host.api-version")
    assert isinstance(vm.pop(), str)

    vm.host_features.add("jobs")
    vm.eval('"jobs" host.feature?')
    assert vm.pop_int() == 1
    vm.eval('"nope" host.feature?')
    assert vm.pop_int() == 0

def test_stdlib_assert_word() -> None:
    vm = VM()
    vm.eval('1 "ok" assert')
    assert vm.stack == []

    with pytest.raises(MicromaxError):
        vm.eval('0 "nope" assert')


def test_introspection_words_list_wid_words_wid_name() -> None:
    vm = VM()

    vm.eval('words-list')
    names = vm.pop_list()
    assert 'dup' in names
    assert 'words' in names

    # Create a fresh wordlist and define a word in it.
    vm.eval('wordlist dup ->w set-current : a 1 ; w wid-words')
    wnames = vm.pop_list()
    assert 'a' in wnames

    vm.eval('w wid-name')
    nm = vm.pop_str()
    assert nm.startswith('wl')


def test_xt_kind_doc_and_src() -> None:
    vm = VM()
    vm.eval(': foo ( -- ) ( add one literal ) 1 ;')

    vm.eval("' foo xt-kind")
    assert vm.pop_str() == "colon"

    vm.eval("' dup xt-kind")
    assert vm.pop_str() == "primitive"

    vm.eval("[ 1 ] xt-kind")
    assert vm.pop_str() == "quote"

    vm.eval("' foo xt-effect")
    assert vm.pop_str() == "( -- )"

    vm.eval("' foo xt-doc")
    assert vm.pop_str() == "add one literal"

    vm.eval("' cr xt-effect")
    assert vm.pop_str() == "( -- )"

    vm.eval("' cr xt-doc")
    assert vm.pop_str() == "newline"

    vm.eval("' foo xt-src")
    src = vm.pop_str()
    assert src.startswith(": foo")

    vm.eval("' foo xt-span")
    sp = vm.pop_list()
    assert sp[0] == "<input>"
    assert int(sp[1]) == 1
    assert int(sp[2]) == 1

    vm.eval("[ 1 ] xt-span")
    sp2 = vm.pop_list()
    assert sp2[0] == "<input>"

    vm.eval("' dup xt-span")
    assert vm.pop_int() == 0


def test_xt_src_rows_are_structured() -> None:
    vm = VM()
    vm.eval(': foo ( n -- n ) ( add one ) 1 + ;')
    vm.eval("' foo xt-src-rows")
    rows = vm.pop_list()
    assert isinstance(rows, list)
    assert rows, "expected at least one row"
    # first row is definition-ish, starts with colon def
    assert str(rows[0][0]).startswith(": foo")
    assert rows[0][1] == "def"
    # should include effect/doc metadata as separate rows
    kinds = [r[1] for r in rows]
    assert "effect" in kinds
    assert "doc" in kinds

def test_words_rows_and_help_show_effects(capsys) -> None:
    vm = VM()
    vm.eval(': inc ( n -- n ) ( add one ) 1 + ;')

    vm.eval('words-rows')
    rows = vm.pop_list()
    inc = next(row for row in rows if row[0] == 'inc')
    assert inc[1] == 'colon'
    assert inc[2] == '( n -- n )'
    assert inc[3] == 'add one'

    vm.eval('help inc')
    out = capsys.readouterr().out
    assert 'effect: ( n -- n )' in out
    assert 'add one' in out


def test_core_introspection_miss_feedback_is_plain(capsys) -> None:
    vm = VM()

    vm.eval('help nope-word')
    assert capsys.readouterr().out == 'help: no such word: nope-word\n'

    vm.eval('see nope-word')
    assert capsys.readouterr().out == 'see: no such word: nope-word\n'

    vm.eval('where nope-word')
    assert capsys.readouterr().out == 'where: no such word: nope-word\n'


def test_stdlib_effect_metadata_is_visible() -> None:
    vm = VM()
    vm.eval("' 2keep xt-effect")
    assert vm.pop_str() == '( x y q -- ... x y )'

