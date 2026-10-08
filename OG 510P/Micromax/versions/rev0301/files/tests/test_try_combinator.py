import pytest

from micromax import VM, MicromaxError


def test_try_question_mark_success_and_failure():
    vm = VM()
    vm.eval("[ 1 2 + ] try?")
    flag = vm.pop_int()
    val = vm.pop_int()
    assert val == 3
    assert flag == 1

    vm = VM()
    vm.eval("123 [ drop drop ] try?")
    flag = vm.pop_int()
    # On failure, stack is restored and flag is 0.
    assert flag == 0
    assert vm.pop_int() == 123


def test_try_runs_handler_on_failure_and_discards_on_success():
    vm = VM()
    # Success: handler is ignored; stack should contain just the result.
    vm.eval('1 [ 2 + ] [ drop drop 0 ] try')
    assert vm.pop_int() == 3

    vm = VM()
    # Failure: handler runs with (ior msg). It can see pre-try stack values.
    vm.eval('1 [ drop drop ] [ drop drop 999 ] try')
    # handler left original 1 plus 999
    assert vm.pop_int() == 999
    assert vm.pop_int() == 1


def test_try_and_recover_handler_error_replace_original_failure_and_keep_handler_stack_effects():
    vm = VM()
    with pytest.raises(MicromaxError, match='handler boom'):
        vm.eval('123 [ drop drop ] [ drop drop 999 "handler boom" error ] try')
    assert vm.stack == [123, 999]

    vm = VM()
    with pytest.raises(MicromaxError, match='handler boom'):
        vm.eval('123 [ drop drop ] [ drop drop 999 "handler boom" error ] recover')
    assert vm.stack == [123, 999]
