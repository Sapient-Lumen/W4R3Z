from micromax import VM


def test_type_predicates() -> None:
    vm = VM()

    vm.eval('123 int?', filename='<test>')
    assert vm.pop_int() == 1

    vm.eval('"x" int?', filename='<test>')
    assert vm.pop_int() == 0

    vm.eval('"x" str?', filename='<test>')
    assert vm.pop_int() == 1

    vm.eval('list list?', filename='<test>')
    assert vm.pop_int() == 1

    vm.eval('[ 1 2 ] quote?', filename='<test>')
    assert vm.pop_int() == 1

    vm.eval('\' dup xt?', filename='<test>')
    assert vm.pop_int() == 1


def test_conversions_and_string_comparisons() -> None:
    vm = VM()

    vm.eval('"42" to-int', filename='<test>')
    assert vm.pop_int() == 42

    vm.eval('42 to-int', filename='<test>')
    assert vm.pop_int() == 42

    vm.eval('123 to-str', filename='<test>')
    assert vm.pop_str() == '123'

    vm.eval('list "a" swap push 123 swap push to-str', filename='<test>')
    assert vm.pop_str() == '["a", 123]'

    vm.eval('"a" "a" s=', filename='<test>')
    assert vm.pop_int() == 1

    vm.eval('"a" "b" s<', filename='<test>')
    assert vm.pop_int() == 1
