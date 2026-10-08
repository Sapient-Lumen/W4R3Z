from __future__ import annotations

import ast
import re
from dataclasses import dataclass
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


def eval_expr(expr: str, ctx: dict[str, Any]) -> Any:
    """Evaluate a small, safe expression language.

    This is intentionally limited (no attribute assignment, no imports, etc.).
    """

    tree = ast.parse(expr, mode="eval")
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_NODES):
            raise ValueError(f"Disallowed expression node: {type(node).__name__}")
        if isinstance(node, ast.Call):
            # Only allow calls to whitelisted helpers.
            if not isinstance(node.func, ast.Name):
                raise ValueError("Only simple function calls are allowed")

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
        if isinstance(node, ast.Attribute):
            base = _eval(node.value)
            if isinstance(base, dict):
                return base.get(node.attr)
            return getattr(base, node.attr)
        if isinstance(node, ast.Call):
            func_name = node.func.id  # type: ignore[attr-defined]
            args = [_eval(a) for a in node.args]
            kwargs = {kw.arg: _eval(kw.value) for kw in node.keywords if kw.arg}
            return _call(func_name, args, kwargs)
        raise ValueError(f"Unsupported expression node: {type(node).__name__}")

    return _eval(tree)


def _call(name: str, args: list[Any], kwargs: dict[str, Any]) -> Any:
    if name == "re_search":
        import re

        pattern, text = args[0], args[1]
        return re.search(pattern, text, **kwargs) is not None
    if name == "re_match":
        import re

        pattern, text = args[0], args[1]
        return re.match(pattern, text, **kwargs) is not None
    raise ValueError(f"Function not allowed: {name}")
