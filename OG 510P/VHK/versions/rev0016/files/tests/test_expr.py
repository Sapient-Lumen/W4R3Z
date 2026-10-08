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
