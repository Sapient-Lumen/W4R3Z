import pytest

from micromax import VM, MicromaxError


def test_quote_effect_is_visible_via_xt_effect():
    vm = VM()
    vm.eval('[ ( x -- x x ) dup ] xt-effect')
    assert vm.pop_str() == '( x -- x x )'


def test_infer_effect_for_simple_colon_word():
    vm = VM()
    vm.eval(': twice ( n -- n ) dup + ;')
    vm.eval("' twice infer-effect")
    eff = vm.pop()
    assert eff != 0
    assert eff == '( x1 -- y1 )'


def test_check_effect_matches_declared_for_simple_colon_word():
    vm = VM()
    vm.eval(': foo ( x -- x x ) dup ;')
    vm.eval("' foo check-effect")
    assert vm.pop_int() == 1


def test_stackcheck_error_on_mismatch_at_definition_time():
    vm = VM()
    vm.eval('2 stackcheck!')
    with pytest.raises(MicromaxError):
        vm.eval(': bad ( x -- ) dup ;')


def test_stackcheck_error_on_mismatch_for_annotated_quote_runtime():
    vm = VM()
    vm.eval('2 stackcheck!')
    with pytest.raises(MicromaxError):
        vm.eval('5 [ ( x -- ) dup ] call')
