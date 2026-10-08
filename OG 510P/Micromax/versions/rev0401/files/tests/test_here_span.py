from micromax import VM


def test_here_span_returns_current_callsite_span() -> None:
    vm = VM()
    vm.eval('here-span', filename='<test-here>')
    sp = vm.pop()
    assert isinstance(sp, list)
    assert len(sp) == 3
    assert sp[0] == '<test-here>'
    assert isinstance(sp[1], int) and sp[1] >= 1
    assert isinstance(sp[2], int) and sp[2] >= 1
