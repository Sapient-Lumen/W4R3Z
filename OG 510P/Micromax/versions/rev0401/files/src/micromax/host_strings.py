"""micromax.host_strings

Reference host-provided string helpers.

These are intentionally registered as *hostcalls* rather than VM primitives so:
- the portable kernel stays small (Rust/WASM can implement differently)
- embeddings can choose which helpers they want to expose

Editor embeddings (micromax-editor) install these by default and also define
small convenience words that call them.

Hostcall names:
  s+ s-len s-slice s-index s-contains? s-split s-join s-replace s-trim s-upper s-lower s-format

All operate on UTF-8 Python strings (unicode codepoints).
"""

from __future__ import annotations

from typing import Callable

from .vm import VM, MicromaxError


def install_string_hostcalls(vm: VM) -> None:
    """Install the reference string hostcall set into `vm`.

    This function only registers host functions (allowlisted via `hostcall`).
    It does not add VM primitives.
    """

    vm.host_features.add("mx.strings")

    def hc_s_plus(v: VM) -> None:
        b = v.pop_str()
        a = v.pop_str()
        v.stack.append(a + b)

    def hc_s_len(v: VM) -> None:
        s = v.pop_str()
        v.stack.append(len(s))

    def _norm_index(i: int, n: int) -> int:
        if i < 0:
            i = n + i
        return max(0, min(i, n))

    def hc_s_slice(v: VM) -> None:
        end = v.pop_int()
        start = v.pop_int()
        s = v.pop_str()
        n = len(s)
        a = _norm_index(int(start), n)
        b = _norm_index(int(end), n)
        if b < a:
            a, b = b, a
        v.stack.append(s[a:b])

    def hc_s_index(v: VM) -> None:
        needle = v.pop_str()
        hay = v.pop_str()
        v.stack.append(int(hay.find(needle)))

    def hc_s_contains(v: VM) -> None:
        needle = v.pop_str()
        hay = v.pop_str()
        v.stack.append(1 if needle in hay else 0)

    def hc_s_split(v: VM) -> None:
        delim = v.pop_str()
        s = v.pop_str()
        if delim == "":
            v.stack.append([ch for ch in s])
            return
        v.stack.append(s.split(delim))

    def hc_s_join(v: VM) -> None:
        delim = v.pop_str()
        parts = v.pop_list()
        out: list[str] = []
        for x in parts:
            if not isinstance(x, str):
                raise MicromaxError(f"s-join: expected list of str, got {type(x).__name__}")
            out.append(x)
        v.stack.append(delim.join(out))

    def hc_s_replace(v: VM) -> None:
        new = v.pop_str()
        old = v.pop_str()
        s = v.pop_str()
        v.stack.append(s.replace(old, new))

    def hc_s_trim(v: VM) -> None:
        s = v.pop_str()
        v.stack.append(s.strip())

    def hc_s_upper(v: VM) -> None:
        s = v.pop_str()
        v.stack.append(s.upper())

    def hc_s_lower(v: VM) -> None:
        s = v.pop_str()
        v.stack.append(s.lower())

    vm.register_host("s+", hc_s_plus)
    vm.register_host("s-len", hc_s_len)
    vm.register_host("s-slice", hc_s_slice)
    vm.register_host("s-index", hc_s_index)
    vm.register_host("s-contains?", hc_s_contains)
    vm.register_host("s-split", hc_s_split)
    vm.register_host("s-join", hc_s_join)
    vm.register_host("s-replace", hc_s_replace)
    vm.register_host("s-trim", hc_s_trim)
    vm.register_host("s-upper", hc_s_upper)


    def _to_str_repr(x: object, *, depth: int = 0) -> str:
        """Deterministic-ish representation matching `to-str` for non-strings.

        This is duplicated here so hostcalls can format arbitrary values without
        depending on VM primitives.
        """
        import json
        from .vm import Cell, Quotation, Word

        if depth > 6:
            return "..."
        if isinstance(x, str):
            return json.dumps(x, ensure_ascii=False)
        if isinstance(x, int):
            return str(int(x))
        if isinstance(x, list):
            inner = ", ".join(_to_str_repr(v, depth=depth + 1) for v in x)
            return "[" + inner + "]"
        if isinstance(x, dict):
            items = []
            for k in sorted(x.keys(), key=lambda kk: str(kk)):
                ks = json.dumps(str(k), ensure_ascii=False)
                vs = _to_str_repr(x.get(k), depth=depth + 1)
                items.append(f"{ks}: {vs}")
            return "{" + ", ".join(items) + "}"
        if isinstance(x, Cell):
            return f"<cell { _to_str_repr(x.value, depth=depth + 1) }>"
        if isinstance(x, Quotation):
            return "<quote>"
        if isinstance(x, Word):
            nm = getattr(x, "name", "<xt>")
            return f"<xt {nm}>"
        return f"<{type(x).__name__}>"

    def _as_str(x: object) -> str:
        return x if isinstance(x, str) else _to_str_repr(x)

    def hc_s_format(v: VM) -> None:
        """( ... fmt n -- s ) Minimal printf-ish formatter.

        Supports: %%s, %%d, and %%%%.

        `n` is the number of arguments consumed from the stack (below fmt).
        """
        n = v.pop_int()
        fmt = v.pop_str()
        if n < 0:
            raise MicromaxError('s-format: n must be >= 0')
        args = [v.pop() for _ in range(int(n))][::-1]

        out: list[str] = []
        ai = 0
        i = 0
        while i < len(fmt):
            ch = fmt[i]
            if ch != '%':
                out.append(ch)
                i += 1
                continue
            if i + 1 >= len(fmt):
                raise MicromaxError('s-format: trailing %')
            spec = fmt[i + 1]
            i += 2
            if spec == '%':
                out.append('%')
                continue
            if ai >= len(args):
                raise MicromaxError('s-format: not enough arguments')
            x = args[ai]
            ai += 1
            if spec == 's':
                out.append(_as_str(x) if not isinstance(x, str) else x)
                continue
            if spec == 'd':
                if isinstance(x, int):
                    out.append(str(int(x)))
                elif isinstance(x, str):
                    try:
                        out.append(str(int(x.strip(), 10)))
                    except Exception as e:
                        raise MicromaxError('s-format: %d expects int') from e
                else:
                    raise MicromaxError('s-format: %d expects int')
                continue
            raise MicromaxError(f's-format: unknown specifier %{spec}')

        if ai != len(args):
            raise MicromaxError('s-format: too many arguments')
        v.stack.append(''.join(out))
    vm.register_host("s-lower", hc_s_lower)
    vm.register_host("s-format", hc_s_format)
