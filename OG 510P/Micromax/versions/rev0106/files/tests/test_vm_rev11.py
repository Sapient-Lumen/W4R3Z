from micromax import VM, MicromaxError


def test_return_stack_words():
    vm = VM()
    vm.eval("1 2 >r 3 r>")
    assert vm.stack == [1, 3, 2]

    vm.eval("clear")
    vm.eval("99 >r r@")
    assert vm.stack == [99]
    vm.eval("rdepth")
    assert vm.pop_int() == 1
    vm.eval("rdrop")
    vm.eval("rdepth")
    assert vm.pop_int() == 0


def test_stack_helpers_pick_roll_depth_clear():
    vm = VM()
    vm.eval("10 20 30 depth")
    assert vm.pop_int() == 3

    vm.eval("0 pick")
    assert vm.stack == [10, 20, 30, 30]

    vm.eval("clear 10 20 30 1 pick")
    assert vm.stack == [10, 20, 30, 20]

    vm.eval("clear 10 20 30 2 roll")
    assert vm.stack == [20, 30, 10]


def test_tuck_nip_2dup_2drop():
    vm = VM()
    vm.eval("1 2 tuck")
    assert vm.stack == [2, 1, 2]
    vm.eval("nip")
    assert vm.stack == [2, 2]

    vm.eval("clear 1 2 2dup")
    assert vm.stack == [1, 2, 1, 2]
    vm.eval("2drop")
    assert vm.stack == [1, 2]


def test_dip_keep_2dip_2keep():
    vm = VM()
    vm.eval("4 [ 1 2 + ] dip")
    assert vm.stack == [3, 4]

    vm.eval("clear 3 4 [ + ] keep")
    assert vm.stack == [7, 4]

    vm.eval("clear 10 100 200 [ 1 + ] 2dip")
    assert vm.stack == [11, 100, 200]

    vm.eval("clear 100 200 [ + ] 2keep")
    assert vm.stack == [300, 100, 200]


def test_bi_and_tri():
    vm = VM()
    vm.eval("5 [ 1 + ] [ 2 * ] bi")
    assert vm.stack == [6, 10]

    vm.eval("clear 5 [ 1 + ] [ 2 * ] [ dup * ] tri")
    assert vm.stack == [6, 10, 25]


def test_format_error_includes_source_excerpt():
    vm = VM()
    try:
        vm.eval("1 drop drop", filename="t.mx")
        assert False, "expected error"
    except MicromaxError as e:
        s = vm.format_error(e)
        assert "t.mx" in s
        assert "1 drop drop" in s
        assert "^" in s

def test_find_word_by_string_name():
    vm = VM()
    vm.eval('"dup" find')
    xt = vm.pop()
    assert xt != 0
    assert getattr(xt, 'name', '') == 'dup'

    vm.eval('"nope" find')
    assert vm.pop() == 0


def test_compile_and_execute_quote():
    vm = VM()
    vm.eval('[ 1 2 + ] compile dup compiled? swap call')
    assert vm.stack == [1, 3]


def test_compile_rejects_parsing_words():
    vm = VM()
    try:
        vm.eval('[ module foo ] compile')
        assert False, 'expected error'
    except MicromaxError as e:
        assert 'requires token-stream parsing' in str(e) or 'compile:' in str(e)



def test_compiled_code_tracks_redefinition_via_dict_version():
    vm = VM()
    vm.eval(": a 1 ; : b a ;")
    # Compile b (tier-2)
    vm.eval("' b compile")
    # Call b
    vm.eval("b")
    assert vm.pop_int() == 1

    # Redefine a and ensure compiled b sees the new definition
    vm.eval(": a 2 ;")
    vm.eval("b")
    assert vm.pop_int() == 2
