from __future__ import annotations

from micromax import VM


def test_maps_basic_get_set_delete_and_predicate() -> None:
    vm = VM()

    # map? predicate
    vm.eval('map map?')
    assert vm.pop_int() == 1

    vm.eval('list map?')
    assert vm.pop_int() == 0

    # set + get
    vm.eval('1 "a" map m! "a" swap m@')
    assert vm.pop_int() == 1

    # missing -> 0
    vm.eval('map "missing" swap m@')
    assert vm.pop_int() == 0

    # has?
    vm.eval('1 "k" map m! "k" swap m?')
    assert vm.pop_int() == 1

    vm.eval('map "k" swap m?')
    assert vm.pop_int() == 0

    vm.eval('1 "a" map m! "missing" swap m?')
    assert vm.pop_int() == 0

    # delete
    vm.eval('1 "k" map m! "k" swap m-del "k" swap m?')
    assert vm.pop_int() == 0

    # overwriting an existing key updates its value
    vm.eval('1 "k" map m! 2 "k" rot m! "k" swap m@')
    assert vm.pop_int() == 2

    # deleting a missing key is a no-op for existing entries
    vm.eval('1 "a" map m! "missing" swap m-del "a" swap m@')
    assert vm.pop_int() == 1


def test_maps_keys_items_and_merge() -> None:
    vm = VM()

    vm.eval('1 "b" map m! 2 "a" rot m!')
    m = vm.pop_map()

    vm.stack.append(m)
    vm.eval('m-keys')
    keys = vm.pop_list()
    assert keys == ['a', 'b']

    vm.eval('map m-keys')
    assert vm.pop_list() == []

    vm.stack.append(m)
    vm.eval('m-items')
    items = vm.pop_list()
    assert items == [['a', 2], ['b', 1]]

    vm.eval('map m-items')
    assert vm.pop_list() == []

    # merge: src into dst (dst mutated and returned)
    vm.eval('1 "a" map m! 99 "c" rot m!')
    src = vm.pop_map()

    vm.eval('2 "a" map m!')
    dst = vm.pop_map()

    vm.stack.append(src)
    vm.stack.append(dst)
    vm.eval('m-merge')
    merged = vm.pop_map()

    # src overrides 'a' and adds 'c'
    assert merged == {'a': 1, 'c': 99}

    # empty source is a no-op
    vm.eval('map')
    src_empty = vm.pop_map()
    vm.eval('3 "z" map m!')
    dst2 = vm.pop_map()
    vm.stack.append(src_empty)
    vm.stack.append(dst2)
    vm.eval('m-merge')
    assert vm.pop_map() == {'z': 3}

    # empty destination adopts source pairs
    vm.eval('7 "q" map m!')
    src2 = vm.pop_map()
    vm.eval('map')
    dst_empty = vm.pop_map()
    vm.stack.append(src2)
    vm.stack.append(dst_empty)
    vm.eval('m-merge')
    assert vm.pop_map() == {'q': 7}
