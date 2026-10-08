from __future__ import annotations

import ast
import json
import re
import time
from dataclasses import dataclass
from functools import lru_cache
from typing import Any


_VAR_PATTERN = re.compile(r"\$\{([^}]+)\}")


def _get_path(ctx: dict[str, Any], path: str) -> Any:
    cur: Any = ctx
    for part in path.split('.'):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            raise KeyError(path)
    return cur


def interpolate(text: str, ctx: dict[str, Any]) -> str:
    """Expand ${var} tokens using values from ctx.

    Supports dotted paths like ${user.name}.
    Unknown variables are left as-is.
    """

    def repl(m: re.Match[str]) -> str:
        key = m.group(1).strip()
        try:
            val = _get_path(ctx, key)
        except Exception:
            return m.group(0)
        return str(val)

    return _VAR_PATTERN.sub(repl, text)


@dataclass
class _Env:
    ctx: dict[str, Any]

    def name(self, n: str) -> Any:
        """Resolve a name from the expression environment.

        In addition to variables in ctx, VHK supports a few JSON-style
        lowercase constants for ergonomics in YAML-authored expressions:

        - true / false
        - null / none

        These are treated as reserved identifiers.
        """

        if n in {"true", "True"}:
            return True
        if n in {"false", "False"}:
            return False
        if n in {"null", "none", "None"}:
            return None
        if n in self.ctx:
            return self.ctx[n]
        raise NameError(n)


_ALLOWED_NODES = (
    ast.Expression,
    ast.BoolOp,
    ast.BinOp,
    ast.UnaryOp,
    ast.Compare,
    ast.Call,
    ast.Name,
    ast.Load,
    ast.Constant,
    ast.List,
    ast.Tuple,
    ast.Dict,
    ast.Subscript,
    ast.Slice,
    ast.Attribute,
    ast.And,
    ast.Or,
    ast.Not,
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
    ast.In,
    ast.NotIn,
    ast.Is,
    ast.IsNot,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.Mod,
    ast.Pow,
    ast.USub,
)


_SAFE_FUNCS: dict[str, Any] = {
    # Regex helpers.
    "re_search": lambda pattern, text, **kwargs: re.search(pattern, text, **kwargs) is not None,
    "re_match": lambda pattern, text, **kwargs: re.match(pattern, text, **kwargs) is not None,
    "re_findall": lambda pattern, text, **kwargs: re.findall(pattern, text, **kwargs),

    # Basic conversions / utilities.
    "len": lambda x: len(x),
    "int": lambda x, base=10: int(x, base) if isinstance(x, str) else int(x),
    "float": lambda x: float(x),
    "str": lambda x: str(x),
    "bool": lambda x: bool(x),
    "abs": lambda x: abs(x),
    "round": lambda x, ndigits=0: round(x, ndigits),
    "min": lambda *xs: min(*xs),
    "max": lambda *xs: max(*xs),
    "sum": lambda xs: sum(xs),

    # String helpers (method-call-free convenience).
    "lower": lambda s: str(s).lower(),
    "upper": lambda s: str(s).upper(),
    "strip": lambda s: str(s).strip(),
    "replace": lambda s, old, new, count=-1: str(s).replace(str(old), str(new), count),
    "split": lambda s, sep=None, maxsplit=-1: str(s).split(sep, maxsplit),
    "join": lambda sep, items: str(sep).join([str(x) for x in items]),
    "startswith": lambda s, prefix: str(s).startswith(str(prefix)),
    "endswith": lambda s, suffix: str(s).endswith(str(suffix)),
    "contains": lambda haystack, needle: needle in haystack,

    # Time helpers.
    #
    # These are handy for measuring durations (monotonic_*) and for
    # tracking external side effects like file mtimes (now_*).
    #
    # `monotonic_ms()` intentionally mirrors AutoHotkey's A_TickCount.
    "now_ns": lambda: int(getattr(time, "time_ns", lambda: int(time.time()*1e9))()),
    "now_ms": lambda: int(int(getattr(time, "time_ns", lambda: int(time.time()*1e9))())/1_000_000),
    "monotonic_ns": lambda: int(getattr(time, "monotonic_ns", lambda: int(time.monotonic()*1e9))()),
    "monotonic_ms": lambda: int(int(getattr(time, "monotonic_ns", lambda: int(time.monotonic()*1e9))())/1_000_000),

    # JSON helpers.
    "json_loads": lambda s: json.loads(s),
    "json_dumps": lambda obj, **kwargs: json.dumps(obj, **kwargs),
}


@lru_cache(maxsize=1024)
def _compile_expr(expr: str) -> ast.Expression:
    """Parse + validate an expression.

    Cached because waits/loops evaluate conditions frequently.
    """

    tree = ast.parse(expr, mode="eval")
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_NODES):
            raise ValueError(f"Disallowed expression node: {type(node).__name__}")
        if isinstance(node, ast.Call):
            # Only allow calls to whitelisted helpers.
            if not isinstance(node.func, ast.Name):
                raise ValueError("Only simple function calls are allowed")
            if node.func.id not in _SAFE_FUNCS:
                raise ValueError(f"Function not allowed: {node.func.id}")
        if isinstance(node, ast.Attribute):
            # No dunder/private attribute access.
            if node.attr.startswith("_"):
                raise ValueError("Private attributes are not allowed")
    return tree


def eval_expr(expr: str, ctx: dict[str, Any]) -> Any:
    """Evaluate a small, safe expression language.

    This is intentionally limited (no attribute assignment, no imports, etc.).
    """

    tree = _compile_expr(expr)
    env = _Env(ctx=ctx)

    def _eval(node: ast.AST) -> Any:
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Name):
            return env.name(node.id)
        if isinstance(node, ast.List):
            return [_eval(e) for e in node.elts]
        if isinstance(node, ast.Tuple):
            return tuple(_eval(e) for e in node.elts)
        if isinstance(node, ast.Dict):
            return {_eval(k): _eval(v) for k, v in zip(node.keys, node.values)}
        if isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                out = True
                for v in node.values:
                    out = bool(_eval(v))
                    if not out:
                        break
                return out
            if isinstance(node.op, ast.Or):
                out = False
                for v in node.values:
                    out = bool(_eval(v))
                    if out:
                        break
                return out
        if isinstance(node, ast.UnaryOp):
            v = _eval(node.operand)
            if isinstance(node.op, ast.Not):
                return not bool(v)
            if isinstance(node.op, ast.USub):
                return -v
        if isinstance(node, ast.BinOp):
            a = _eval(node.left)
            b = _eval(node.right)
            if isinstance(node.op, ast.Add):
                return a + b
            if isinstance(node.op, ast.Sub):
                return a - b
            if isinstance(node.op, ast.Mult):
                return a * b
            if isinstance(node.op, ast.Div):
                return a / b
            if isinstance(node.op, ast.Mod):
                return a % b
            if isinstance(node.op, ast.Pow):
                return a ** b
        if isinstance(node, ast.Compare):
            left = _eval(node.left)
            for op, comp in zip(node.ops, node.comparators):
                right = _eval(comp)
                ok = None
                if isinstance(op, ast.Eq):
                    ok = left == right
                elif isinstance(op, ast.NotEq):
                    ok = left != right
                elif isinstance(op, ast.Lt):
                    ok = left < right
                elif isinstance(op, ast.LtE):
                    ok = left <= right
                elif isinstance(op, ast.Gt):
                    ok = left > right
                elif isinstance(op, ast.GtE):
                    ok = left >= right
                elif isinstance(op, ast.In):
                    ok = left in right
                elif isinstance(op, ast.NotIn):
                    ok = left not in right
                elif isinstance(op, ast.Is):
                    ok = left is right
                elif isinstance(op, ast.IsNot):
                    ok = left is not right
                else:
                    raise ValueError(f"Unsupported compare op: {type(op).__name__}")
                if not ok:
                    return False
                left = right
            return True
        if isinstance(node, ast.Subscript):
            base = _eval(node.value)
            # Python 3.9+: slice is an expr
            key = _eval(node.slice)
            return base[key]
        if isinstance(node, ast.Slice):
            lower = _eval(node.lower) if node.lower is not None else None
            upper = _eval(node.upper) if node.upper is not None else None
            step = _eval(node.step) if node.step is not None else None
            return slice(lower, upper, step)
        if isinstance(node, ast.Attribute):
            base = _eval(node.value)
            if isinstance(base, dict):
                return base.get(node.attr)
            raise ValueError("Attribute access is only allowed on dict values")
        if isinstance(node, ast.Call):
            func_name = node.func.id  # type: ignore[attr-defined]
            args = [_eval(a) for a in node.args]
            kwargs = {kw.arg: _eval(kw.value) for kw in node.keywords if kw.arg}
            return _call(func_name, args, kwargs)
        raise ValueError(f"Unsupported expression node: {type(node).__name__}")

    return _eval(tree)


def validate_expr(expr: str) -> None:
    """Validate that an expression is syntactically valid for VHK.

    Notes
    -----
    At runtime, most expression fields are first interpolated (replacing
    ``${var}`` tokens) and then evaluated.

    For offline validation, we replace interpolation tokens with a placeholder
    identifier so the expression can be parsed without knowing the actual
    runtime values.
    """

    masked = _VAR_PATTERN.sub("x", expr or "")
    _compile_expr(masked)


def _call(name: str, args: list[Any], kwargs: dict[str, Any]) -> Any:
    try:
        fn = _SAFE_FUNCS[name]
    except KeyError as e:
        raise ValueError(f"Function not allowed: {name}") from e
    return fn(*args, **kwargs)
