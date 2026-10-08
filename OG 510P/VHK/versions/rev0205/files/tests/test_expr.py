from vhk.core.expr import eval_expr, interpolate


def test_interpolate_simple():
    assert interpolate("hi ${name}", {"name": "alice"}) == "hi alice"


def test_interpolate_dotted():
    assert interpolate("${user.name}", {"user": {"name": "bob"}}) == "bob"


def test_eval_expr_arith_bool():
    ctx = {"a": 2, "b": 3}
    assert eval_expr("a + b * 2 == 8", ctx) is True


def test_eval_expr_regex_helper():
    ctx = {"txt": "hello world"}
    assert eval_expr("re_search('world$', txt)", ctx) is True


def test_eval_expr_string_helpers_and_slice():
    ctx = {"s": "  Hello ", "xs": [0, 1, 2, 3, 4]}
    assert eval_expr("lower(strip(s)) == 'hello'", ctx) is True
    assert eval_expr("join('-', split('a,b,c', ','))", ctx) == "a-b-c"
    assert eval_expr("xs[1:4]", ctx) == [1, 2, 3]


def test_eval_expr_disallow_object_attribute_access():
    class Obj:
        def __init__(self):
            self.x = 1

    ctx = {"o": Obj()}
    try:
        eval_expr("o.x", ctx)
        assert False, "expected attribute access to be disallowed"
    except ValueError as e:
        assert "Attribute access" in str(e)

def test_eval_expr_json_style_constants():
    assert eval_expr('true and not false', {}) is True
    assert eval_expr('null is None', {}) is True
    assert eval_expr('none == null', {}) is True

def test_eval_expr_attribute_named_true_is_not_constant():
    ctx = {'d': {'true': 1, 'false': 0}}
    assert eval_expr('d.true == 1 and d.false == 0', ctx) is True

def test_eval_expr_time_helpers_are_ints_and_increasing():
    import time
    t0 = eval_expr("now_ns()", {})
    assert isinstance(t0, int)
    # Should be close to wall-clock epoch time.
    assert abs(t0 - time.time_ns()) < 2_000_000_000

    m0 = eval_expr("monotonic_ms()", {})
    time.sleep(0.01)
    m1 = eval_expr("monotonic_ms()", {})
    assert isinstance(m0, int)
    assert m1 >= m0
