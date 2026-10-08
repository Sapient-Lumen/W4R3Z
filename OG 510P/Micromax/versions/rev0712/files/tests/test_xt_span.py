from micromax.vm import VM


def test_xt_span_for_colon_words_and_quotations() -> None:
    vm = VM()

    vm.eval(': foo 1 ;', filename='t.mx')
    vm.eval("' foo xt-span")
    sp = vm.pop()
    assert sp == ['t.mx', 1, 1]

    vm.eval('[ 1 ] xt-span', filename='q.mx')
    sp2 = vm.pop()
    assert sp2 == ['q.mx', 1, 1]


def test_xt_span_returns_0_for_primitives() -> None:
    vm = VM()
    vm.eval("' dup xt-span")
    assert vm.pop_int() == 0
