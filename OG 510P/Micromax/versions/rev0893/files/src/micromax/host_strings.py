"""micromax.host_strings

Reference host-provided string helpers.

These are intentionally registered as *hostcalls* rather than VM primitives so:
- the portable kernel stays small (Rust/WASM can implement differently)
- embeddings can choose which helpers they want to expose

Editor embeddings (micromax-editor) install these by default and also define
small convenience words that call them.

Hostcall names:
  s+ s-len s-slice s-index s-contains? s-split s-join s-replace s-trim s-upper s-lower s-format

All operate on UTF-8 Python strings (unicode codepoints).  Integer control
slots such as `s-slice` indexes and the `s-format` argument count reject
Python booleans even though `bool` subclasses `int`; direct embeddings should
spell portable counts/indexes as real integers.  The `s-format` `%d` data
slot also rejects Python booleans so truth-value sentinels do not masquerade
as portable integer data.  The `s-format` `%s` representation path shows
Python booleans explicitly as host booleans instead of formatting them as
integer text, including boolean keys inside dictionary/map representations.
`s-format` now checks its declared argument count, format plan, and data
conversion validity before consuming formatter data, so arity/format/type
mistakes fail at the formatter boundary without partially eating the caller's
data stack.  `s-join` validates its delimiter and list contents before
consuming its public arguments, so a mixed list remains inspectable when the
join fails.

`s-split` validates its source/delimiter argument shape before consuming
anything, so direct hostcall type failures leave the split request visible for
inspection.  `s-replace` validates its source/old/new argument shape before
consuming anything and rejects an empty `old` needle.  Python treats an empty
needle as a request to insert between every codepoint and at both boundaries,
but Micromax keeps bulk rewrite helpers on visible, positive-width spans while
preserving the offending rewrite data for inspection.
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

    def _require_int_arg(value: object, *, action: str, slot: str) -> int:
        # Python booleans are integers, but they are embedding-only sentinels
        # here.  VM code can spell counts and indexes portably as `0`, `1`,
        # etc.; direct hostcall callers should not be able to smuggle truth
        # values into explicit numeric control slots.
        if isinstance(value, bool):
            raise MicromaxError(f"{action}: {slot} must be an integer, got boolean {value!r}")
        if not isinstance(value, int):
            raise MicromaxError(f"{action}: {slot} must be an integer, got {type(value).__name__}")
        return int(value)

    def _norm_index(i: int, n: int) -> int:
        if i < 0:
            i = n + i
        return max(0, min(i, n))

    def hc_s_slice(v: VM) -> None:
        end_raw = v.pop()
        start_raw = v.pop()
        s = v.pop_str()
        end = _require_int_arg(end_raw, action="s-slice", slot="end")
        start = _require_int_arg(start_raw, action="s-slice", slot="start")
        n = len(s)
        a = _norm_index(start, n)
        b = _norm_index(end, n)
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
        # Validate the split request before consuming it.  `s-split` is often
        # paired with `s-join`; both should leave malformed caller data visible
        # instead of reporting a generic pop_str() error after eating one side
        # of the request.
        if len(v.stack) < 2:
            raise MicromaxError("s-split: not enough arguments")
        s = v.stack[-2]
        delim = v.stack[-1]
        if not isinstance(s, str):
            raise MicromaxError(f"s-split: source must be str, got {type(s).__name__}")
        if not isinstance(delim, str):
            raise MicromaxError(f"s-split: delimiter must be str, got {type(delim).__name__}")
        del v.stack[-2:]
        if delim == "":
            v.stack.append([ch for ch in s])
            return
        v.stack.append(s.split(delim))

    def hc_s_join(v: VM) -> None:
        # Validate the whole public argument shape before consuming it.  A bad
        # list element is caller data, not a low-level stack accident; leaving
        # the list and delimiter visible makes direct hostcall failures much
        # easier to inspect and recover from.
        if len(v.stack) < 2:
            raise MicromaxError("s-join: not enough arguments")
        parts = v.stack[-2]
        delim = v.stack[-1]
        if not isinstance(delim, str):
            raise MicromaxError(f"s-join: delimiter must be str, got {type(delim).__name__}")
        if not isinstance(parts, list):
            raise MicromaxError(f"s-join: expected list of str, got {type(parts).__name__}")
        out: list[str] = []
        for x in parts:
            if not isinstance(x, str):
                raise MicromaxError(f"s-join: expected list of str, got {type(x).__name__}")
            out.append(x)
        del v.stack[-2:]
        v.stack.append(delim.join(out))

    def hc_s_replace(v: VM) -> None:
        # Keep the rewrite boundary inspectable: validate the full public
        # argument shape before consuming anything, so an empty needle or type
        # mistake leaves the source/old/new evidence visible to direct callers.
        if len(v.stack) < 3:
            raise MicromaxError("s-replace: not enough arguments")
        s = v.stack[-3]
        old = v.stack[-2]
        new = v.stack[-1]
        if not isinstance(s, str):
            raise MicromaxError(f"s-replace: source must be str, got {type(s).__name__}")
        if not isinstance(old, str):
            raise MicromaxError(f"s-replace: old must be str, got {type(old).__name__}")
        if not isinstance(new, str):
            raise MicromaxError(f"s-replace: new must be str, got {type(new).__name__}")
        if old == "":
            raise MicromaxError("s-replace: empty search")
        del v.stack[-3:]
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
        """Deterministic-ish representation for non-strings.

        This is duplicated here so hostcalls can format arbitrary values without
        depending on VM primitives.  It deliberately makes direct Python boolean
        sentinels explicit instead of inheriting Python's bool-as-int display.
        """
        import json
        from .vm import Cell, Quotation, Word

        if depth > 6:
            return "..."
        if isinstance(x, str):
            return json.dumps(x, ensure_ascii=False)
        if isinstance(x, bool):
            return f"<bool {x!r}>"
        if isinstance(x, int):
            return str(int(x))
        if isinstance(x, list):
            inner = ", ".join(_to_str_repr(v, depth=depth + 1) for v in x)
            return "[" + inner + "]"
        if isinstance(x, dict):
            items = []
            for k in sorted(x.keys(), key=lambda kk: str(kk)):
                if isinstance(k, bool):
                    # Keep direct host-language boolean sentinels visible even
                    # when they appear as map keys.  The generic key path uses
                    # stringified keys for JSON-ish readability, but
                    # ``str(True)`` / ``str(False)`` would hide the type witness
                    # that rev740 added for boolean values.
                    ks = json.dumps(f"<bool {k!r}>", ensure_ascii=False)
                else:
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

    def _format_specs(fmt: str) -> list[str]:
        specs: list[str] = []
        i = 0
        while i < len(fmt):
            ch = fmt[i]
            if ch != '%':
                i += 1
                continue
            if i + 1 >= len(fmt):
                raise MicromaxError('s-format: trailing %')
            spec = fmt[i + 1]
            i += 2
            if spec == '%':
                continue
            if spec in ('s', 'd'):
                specs.append(spec)
                continue
            raise MicromaxError(f's-format: unknown specifier %{spec}')
        return specs

    def hc_s_format(v: VM) -> None:
        """( ... fmt n -- s ) Minimal printf-ish formatter.

        Supports: %%s, %%d, and %%%%.

        `n` is the number of arguments consumed from the stack (below fmt).
        """
        n_raw = v.pop()
        fmt = v.pop_str()
        n = _require_int_arg(n_raw, action="s-format", slot="n")
        if n < 0:
            raise MicromaxError('s-format: n must be >= 0')
        if len(v.stack) < n:
            raise MicromaxError('s-format: not enough arguments')
        specs = _format_specs(fmt)
        if len(specs) > n:
            raise MicromaxError('s-format: not enough arguments')
        if len(specs) < n:
            raise MicromaxError('s-format: too many arguments')
        # Peek before formatting.  Formatter data should only be consumed once
        # the whole conversion pass is known to succeed; otherwise a type typo
        # such as `"abc" "%d" 1 s-format` loses the value the user needs to
        # inspect or recover.
        args = list(v.stack[-n:]) if n else []

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
                if isinstance(x, bool):
                    raise MicromaxError(f's-format: %d expects int, got boolean {x!r}')
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
        if n:
            del v.stack[-n:]
        v.stack.append(''.join(out))
    vm.register_host("s-lower", hc_s_lower)
    vm.register_host("s-format", hc_s_format)
