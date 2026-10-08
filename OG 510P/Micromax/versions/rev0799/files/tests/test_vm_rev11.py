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




def test_catch_restores_return_stack_depth_on_throw():
    vm = VM()
    vm.eval(': boom 1 >r 99 throw ; [ boom ] catch')
    assert vm.stack == [99]
    vm.eval('rdepth')
    assert vm.pop_int() == 0



def test_catch_preserves_outer_return_stack_value_on_throw():
    vm = VM()
    vm.eval('77 >r [ 1 >r 99 throw ] catch drop r>')
    assert vm.stack == [77]



def test_catch_preserves_outer_return_stack_order_on_throw():
    vm = VM()
    vm.eval('11 >r 22 >r [ 99 >r 77 throw ] catch drop r> r>')
    assert vm.stack == [22, 11]

def test_catch_success_preserves_outer_return_stack_order_and_values():
    vm = VM()
    vm.eval('11 >r 22 >r [ 99 >r rdrop ] catch drop r> r>')
    assert vm.stack == [22, 11]




def test_nested_catch_success_preserves_outer_return_stack_order_and_values():
    vm = VM()
    vm.eval('11 >r 22 >r [ [ 99 >r rdrop ] catch drop ] catch drop r> r>')
    assert vm.stack == [22, 11]



def test_nested_catch_throw_preserves_outer_return_stack_order_and_values():
    vm = VM()
    vm.eval('11 >r 22 >r [ [ 99 >r 77 throw ] catch drop ] catch drop r> r>')
    assert vm.stack == [22, 11]


def test_nested_catch_success_counts_only_outer_user_return_stack_items():
    vm = VM()
    vm.eval('77 >r [ [ rdepth ] catch drop ] catch drop r>')
    assert vm.stack == [1, 77]


def test_nested_catch_throw_counts_only_outer_user_return_stack_items():
    vm = VM()
    vm.eval('77 >r [ [ 99 throw ] catch drop rdepth ] catch drop r>')
    assert vm.stack == [1, 77]


def test_nested_catch_throw_preserves_outer_visible_return_stack_value():
    vm = VM()
    vm.eval('77 >r [ [ 99 throw ] catch drop r@ ] catch drop r>')
    assert vm.stack == [77, 77]

def test_nested_catch_success_preserves_outer_visible_return_stack_value():
    vm = VM()
    vm.eval('77 >r [ [ r@ ] catch drop ] catch drop r>')
    assert vm.stack == [77, 77]



def test_stack_helpers_pick_roll_depth_clear():
    vm = VM()
    vm.eval("10 20 30 depth")
    assert vm.pop_int() == 3

    vm.eval("0 pick")
    assert vm.stack == [10, 20, 30, 30]

    vm.eval("clear 10 20 30 1 pick")
    assert vm.stack == [10, 20, 30, 20]

    vm.eval("clear 10 20 30 2 pick")
    assert vm.stack == [10, 20, 30, 10]

    vm.eval("clear 10 20 30 40 3 pick")
    assert vm.stack == [10, 20, 30, 40, 10]

    vm.eval("clear 10 20 30 40 50 4 pick")
    assert vm.stack == [10, 20, 30, 40, 50, 10]

    vm.eval("clear 10 20 30 0 roll")
    assert vm.stack == [10, 20, 30]

    vm.eval("clear 10 20 30 2 roll")
    assert vm.stack == [20, 30, 10]

    vm.eval("clear 10 20 30 40 3 roll")
    assert vm.stack == [20, 30, 40, 10]

    vm.eval("clear 10 20 30 40 50 4 roll")
    assert vm.stack == [20, 30, 40, 50, 10]


def test_pick_roll_reject_negative_indices_and_too_shallow_stacks():
    vm = VM()

    for src, want in [
        ("10 -1 pick", "pick: u must be >= 0"),
        ("10 -1 roll", "roll: u must be >= 0"),
        ("10 20 2 pick", "Stack underflow"),
        ("10 20 2 roll", "Stack underflow"),
    ]:
        try:
            vm.eval(src)
            assert False, f"expected error for {src!r}"
        except MicromaxError as exc:
            assert want in str(exc)
        vm.stack.clear()


def test_basic_stack_helper_examples_match_portability_slice():
    vm = VM()
    vm.eval("clear 1 2 nip")
    assert vm.stack == [2]

    vm.eval("clear 1 2 tuck")
    assert vm.stack == [2, 1, 2]

    vm.eval("clear 1 2 2dup")
    assert vm.stack == [1, 2, 1, 2]

    vm.eval("clear 1 2 2drop")
    assert vm.stack == []


def test_keep_example_matches_portability_slice():
    vm = VM()
    vm.eval("clear 3 4 [ + ] keep")
    assert vm.stack == [7, 4]


def test_try_success_examples_match_portability_slice():
    vm = VM()
    vm.eval("clear [ 1 2 + ] try?")
    assert vm.stack == [3, 1]

    vm.eval("clear 1 [ 2 + ] [ drop drop 0 ] try")
    assert vm.stack == [3]


def test_rdrop_and_recover_success_examples_match_portability_slice():
    vm = VM()
    vm.eval("clear 1 >r rdrop rdepth")
    assert vm.stack == [0]

    vm.eval("clear 77 >r 99 >r rdrop r> rdepth")
    assert vm.stack == [77, 0]

    vm.eval("clear 1 [ 2 + ] [ drop drop 0 ] recover")
    assert vm.stack == [3]


def test_try_and_recover_handler_error_precedence_examples_match_portability_slice():
    vm = VM()
    try:
        vm.eval('clear 123 [ drop drop ] [ drop drop 999 "handler boom" error ] try')
        assert False, 'expected try handler failure'
    except MicromaxError as exc:
        assert 'handler boom' in str(exc)
    assert vm.stack == [123, 999]

    vm = VM()
    try:
        vm.eval('clear 123 [ drop drop ] [ drop drop 999 "handler boom" error ] recover')
        assert False, 'expected recover handler failure'
    except MicromaxError as exc:
        assert 'handler boom' in str(exc)
    assert vm.stack == [123, 999]


def test_ensure_and_finally_failure_examples_match_portability_slice():
    vm = VM()
    try:
        vm.eval("clear 123 [ drop drop ] [ 999 ] ensure")
        assert False, 'expected ensure failure'
    except MicromaxError as exc:
        assert 'Stack underflow' in str(exc)
    assert vm.stack == [123, 999]

    vm = VM()
    try:
        vm.eval("clear 123 [ drop drop ] [ 999 ] finally")
        assert False, 'expected finally failure'
    except MicromaxError as exc:
        assert 'Stack underflow' in str(exc)
    assert vm.stack == [123, 999]


def test_ensure_and_finally_cleanup_error_precedence_examples_match_portability_slice():
    vm = VM()
    try:
        vm.eval('clear [ 1 ] [ "cleanup boom" error ] ensure')
        assert False, 'expected ensure cleanup failure on success path'
    except MicromaxError as exc:
        assert 'cleanup boom' in str(exc)
    assert vm.stack == [1]

    vm = VM()
    try:
        vm.eval('clear 123 [ drop drop ] [ "cleanup boom" error ] ensure')
        assert False, 'expected ensure cleanup failure on failure path'
    except MicromaxError as exc:
        assert 'cleanup boom' in str(exc)
    assert vm.stack == [123]

    vm = VM()
    try:
        vm.eval('clear [ 1 ] [ "cleanup boom" error ] finally')
        assert False, 'expected finally cleanup failure on success path'
    except MicromaxError as exc:
        assert 'cleanup boom' in str(exc)
    assert vm.stack == [1]

    vm = VM()
    try:
        vm.eval('clear 123 [ drop drop ] [ "cleanup boom" error ] finally')
        assert False, 'expected finally cleanup failure on failure path'
    except MicromaxError as exc:
        assert 'cleanup boom' in str(exc)
    assert vm.stack == [123]


def test_assert_examples_match_portability_slice():
    vm = VM()
    vm.eval('clear 123 1 "ok" assert')
    assert vm.stack == [123]

    vm = VM()
    try:
        vm.eval('clear 123 0 "boom" assert')
        assert False, 'expected assert failure'
    except MicromaxError as exc:
        assert 'boom' in str(exc)
    assert vm.stack == [123]


def test_qdup_one_plus_one_minus_two_times_two_slash_zero_greater_zero_not_equals_not_equals_general_negate_zero_less_abs_min_max_tuck_nip_2dup_2drop_and_pair_return_stack_helpers():
    vm = VM()
    vm.eval("0 ?dup")
    assert vm.stack == [0]

    vm.eval("clear -1 ?dup")
    assert vm.stack == [-1, -1]

    vm.eval("clear 0 1+ -2 1+ 9 1+")
    assert vm.stack == [1, -1, 10]

    vm.eval("clear 2 1- 1 1- 0 1-")
    assert vm.stack == [1, 0, -1]

    vm.eval("clear 0 2* -3 2* 9 2*")
    assert vm.stack == [0, -6, 18]

    vm.eval("clear 0 2/ 1 2/ 8 2/ -3 2/")
    assert vm.stack == [0, 0, 4, -2]

    vm.eval("clear -1 0> 0 0> 5 0>")
    assert vm.stack == [0, 0, 1]

    vm.eval("clear 0 0<> -7 0<> 9 0<>")
    assert vm.stack == [0, 1, 1]

    vm.eval("clear 3 3 <> 3 4 <> \"a\" \"a\" <> \"a\" \"b\" <>")
    assert vm.stack == [0, 1, 0, 1]

    vm.eval("clear 0 negate")
    assert vm.stack == [0]

    vm.eval("clear 7 negate -3 negate")
    assert vm.stack == [-7, 3]

    vm.eval("clear -1 0< 0 0< 5 0<")
    assert vm.stack == [1, 0, 0]

    vm.eval("clear -7 abs 0 abs 9 abs")
    assert vm.stack == [7, 0, 9]

    vm.eval("clear 3 7 max 7 3 max -2 -5 max 4 4 max")
    assert vm.stack == [7, 7, -2, 4]

    vm.eval("clear 3 7 min 7 3 min -2 -5 min 4 4 min")
    assert vm.stack == [3, 3, -5, 4]

    vm.eval("clear 1 2 tuck")
    assert vm.stack == [2, 1, 2]
    vm.eval("nip")
    assert vm.stack == [2, 2]

    vm.eval("clear 1 2 2dup")
    assert vm.stack == [1, 2, 1, 2]
    vm.eval("2drop")
    assert vm.stack == [1, 2]

    vm.eval("clear 1 2 3 4 2nip")
    assert vm.stack == [3, 4]

    vm.eval("clear 1 2 3 4 2over")
    assert vm.stack == [1, 2, 3, 4, 1, 2]

    vm.eval("clear 1 2 3 4 2tuck")
    assert vm.stack == [3, 4, 1, 2, 3, 4]

    vm.eval("clear 1 2 3 4 2swap")
    assert vm.stack == [3, 4, 1, 2]

    vm.eval("clear 1 2 3 4 5 6 2rot")
    assert vm.stack == [3, 4, 5, 6, 1, 2]

    vm.eval("clear 1 2 2>r 2r>")
    assert vm.stack == [1, 2]

    vm.eval("clear 10 20 2>r 2r@ 2r>")
    assert vm.stack == [10, 20, 10, 20]

    vm.eval("clear 7 8 2>r 2r@ rdepth 2r> rdepth")
    assert vm.stack == [7, 8, 2, 7, 8, 0]

    vm.eval("clear 1 2 2>r 2rdrop rdepth")
    assert vm.stack == [0]

    vm.eval("clear 77 >r 1 2 2>r 2rdrop r> rdepth")
    assert vm.stack == [77, 0]


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


def test_catch_restores_mutable_stack_values_on_throw():
    vm = VM()
    vm.eval(
        'list "safe" swap push '
        '[ "evil" swap push drop 99 throw ] catch',
        filename="<test>",
    )

    assert vm.stack == [["safe"], 99]
