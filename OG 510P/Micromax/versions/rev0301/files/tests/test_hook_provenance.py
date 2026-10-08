from micromax.vm import VM


def test_hook_rows_and_xt_span_capture_provenance() -> None:
    vm = VM()
    vm.eval(
        ": h1 1 ; hook on-save ' h1 hook-add on-save ' on-save xt-span hook-rows on-save",
        filename="hooks.mx",
    )
    rows = vm.pop_list()
    sp = vm.pop()

    assert sp == ["hooks.mx", 1, 10]
    assert rows == [["h1", ["hooks.mx", 1, 28]]]


def test_hook_fetch_remains_plain_xt_list() -> None:
    vm = VM()
    vm.eval(": h1 1 ; hook on-save ' h1 hook-add on-save hook@ on-save", filename="hooks.mx")
    xs = vm.pop_list()
    assert len(xs) == 1
    assert getattr(xs[0], "name", "") == "h1"
