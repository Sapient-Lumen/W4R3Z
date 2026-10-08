import pytest

from micromax import VM, MicromaxError


def test_ensure_runs_cleanup_on_success_and_preserves_result_stack() -> None:
    vm = VM()
    # body leaves 1; cleanup adds 2 to it.
    vm.eval('[ 1 ] [ 2 + ] ensure')
    assert vm.pop_int() == 3


def test_ensure_runs_cleanup_on_failure_and_rethrows_original_error() -> None:
    vm = VM()
    # body fails; cleanup still runs and can see the pre-body stack.
    with pytest.raises(MicromaxError):
        vm.eval('123 [ drop drop ] [ 999 ] ensure')
    # cleanup ran before rethrow
    assert vm.pop_int() == 999
    assert vm.pop_int() == 123


def test_finally_is_alias_for_ensure() -> None:
    vm = VM()
    vm.eval('[ 5 ] [ 1 + ] finally')
    assert vm.pop_int() == 6
