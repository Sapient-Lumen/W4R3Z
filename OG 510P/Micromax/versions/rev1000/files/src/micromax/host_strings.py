"""Reference host-provided string helpers.

These are registered as allowlisted hostcalls rather than VM primitives so the
portable kernel stays small and embeddings may choose their own implementation.

The generic hostcall result budget remains a postcondition for every helper.
String operations with exact result geometry additionally preflight bytes/cells
*before* entering CPython's allocating ``join``, ``replace``, ``split``, or
concatenation paths.  ``s-format`` uses the same bounded value renderer as the
portable ``to-str`` word, so repeated references cannot amplify one modest
string/list into an enormous result during a single dispatch.

Hostcall names:
  s+ s-len s-slice s-index s-contains? s-split s-join s-replace s-trim s-upper s-lower s-format

Integer control slots reject Python booleans even though ``bool`` subclasses
``int``.  ``s-format %s`` keeps direct host-language boolean sentinels visibly
typed, including boolean map keys.  Existing argument-failure stack behavior is
preserved: split/join/replace requests are validated before consumption, while
format consumes its count/format control cells but leaves formatter data visible
until conversion succeeds.
"""

from __future__ import annotations

from .host_limits import (
    effective_hostcall_result_limits,
    hostcall_result_budget_violation_from_counts,
    utf8_size,
)
from .value_text import (
    BoundedTextBuilder,
    TextResultBudgetExceeded,
    append_value_repr,
)
from .vm import MicromaxError, VM


_STRING_SIZE_CACHE_MAX = 64


def _result_limits(vm: VM) -> tuple[int, int]:
    return effective_hostcall_result_limits(vm)


def _preflight_result(vm: VM, name: str, *, byte_count: int, cell_count: int) -> None:
    max_bytes, max_cells = _result_limits(vm)
    violation = hostcall_result_budget_violation_from_counts(
        name,
        byte_count=byte_count,
        cell_count=cell_count,
        max_bytes=max_bytes,
        max_cells=max_cells,
    )
    if violation is not None:
        raise MicromaxError(violation)


def _bounded_string_byte_sum(
    vm: VM,
    name: str,
    values: list[str],
    *,
    initial_bytes: int = 0,
) -> int:
    """Sum immutable string sizes, stopping at the first proven overrun.

    VM lists can cheaply contain many references to the same large string.
    Rescanning every alias after the result is already known to exceed its
    limit would turn a defensive preflight into a blocking hostcall.  Cache by
    identity in a fixed-size table and fail on the first proven overrun; the
    cache itself therefore cannot grow with caller data.
    """

    max_bytes, max_cells = _result_limits(vm)
    total = int(initial_bytes)
    if max_bytes > 0 and total > max_bytes:
        _preflight_result(vm, name, byte_count=total, cell_count=1)

    cached_sizes: dict[int, tuple[str, int]] = {}
    for value in values:
        identity = id(value)
        cached = cached_sizes.get(identity)
        if cached is not None and cached[0] is value:
            size = cached[1]
        else:
            remaining = None if max_bytes <= 0 else max_bytes - total
            size = utf8_size(value, stop_after=remaining)
            if len(cached_sizes) >= _STRING_SIZE_CACHE_MAX:
                cached_sizes.clear()
            cached_sizes[identity] = (value, size)
        total += size
        if max_bytes > 0 and total > max_bytes:
            violation = hostcall_result_budget_violation_from_counts(
                name,
                byte_count=total,
                cell_count=1,
                max_bytes=max_bytes,
                max_cells=max_cells,
            )
            raise MicromaxError(violation or f"{name}: result too large")
    return total


def _require_int_arg(value: object, *, action: str, slot: str) -> int:
    if isinstance(value, bool):
        raise MicromaxError(f"{action}: {slot} must be an integer, got boolean {value!r}")
    if not isinstance(value, int):
        raise MicromaxError(f"{action}: {slot} must be an integer, got {type(value).__name__}")
    return int(value)


def _norm_index(index: int, length: int) -> int:
    if index < 0:
        index = length + index
    return max(0, min(index, length))


def _format_argument_count(fmt: str) -> int:
    """Validate one format plan without allocating a per-specifier list."""

    count = 0
    index = 0
    while index < len(fmt):
        char = fmt[index]
        if char != "%":
            index += 1
            continue
        if index + 1 >= len(fmt):
            raise MicromaxError("s-format: trailing %")
        spec = fmt[index + 1]
        index += 2
        if spec == "%":
            continue
        if spec in ("s", "d"):
            count += 1
            continue
        raise MicromaxError(f"s-format: unknown specifier %{spec}")
    return count


def install_string_hostcalls(vm: VM) -> None:
    """Install the reference string hostcall set into ``vm``."""

    vm.host_features.add("mx.strings")

    def hc_s_plus(v: VM) -> None:
        if len(v.stack) < 2:
            raise MicromaxError("s+: not enough arguments")
        left = v.stack[-2]
        right = v.stack[-1]
        if not isinstance(left, str):
            raise MicromaxError(f"s+: left must be str, got {type(left).__name__}")
        if not isinstance(right, str):
            raise MicromaxError(f"s+: right must be str, got {type(right).__name__}")
        result_bytes = utf8_size(left) + utf8_size(right)
        _preflight_result(v, "s+", byte_count=result_bytes, cell_count=1)
        result = str.__add__(left, right)
        del v.stack[-2:]
        v.stack.append(result)

    def hc_s_len(v: VM) -> None:
        source = v.pop_str()
        v.stack.append(len(source))

    def hc_s_slice(v: VM) -> None:
        end_raw = v.pop()
        start_raw = v.pop()
        source = v.pop_str()
        end = _require_int_arg(end_raw, action="s-slice", slot="end")
        start = _require_int_arg(start_raw, action="s-slice", slot="start")
        length = len(source)
        left = _norm_index(start, length)
        right = _norm_index(end, length)
        if right < left:
            left, right = right, left
        v.stack.append(source[left:right])

    def hc_s_index(v: VM) -> None:
        needle = v.pop_str()
        haystack = v.pop_str()
        v.stack.append(int(str.find(haystack, needle)))

    def hc_s_contains(v: VM) -> None:
        needle = v.pop_str()
        haystack = v.pop_str()
        v.stack.append(1 if needle in haystack else 0)

    def hc_s_split(v: VM) -> None:
        if len(v.stack) < 2:
            raise MicromaxError("s-split: not enough arguments")
        source = v.stack[-2]
        delimiter = v.stack[-1]
        if not isinstance(source, str):
            raise MicromaxError(f"s-split: source must be str, got {type(source).__name__}")
        if not isinstance(delimiter, str):
            raise MicromaxError(
                f"s-split: delimiter must be str, got {type(delimiter).__name__}"
            )

        source_bytes = utf8_size(source)
        if delimiter == "":
            piece_count = len(source)
            result_bytes = source_bytes
        else:
            match_count = str.count(source, delimiter)
            piece_count = match_count + 1
            result_bytes = source_bytes - (match_count * utf8_size(delimiter))
        _preflight_result(
            v,
            "s-split",
            byte_count=result_bytes,
            cell_count=1 + piece_count,
        )

        result = list(source) if delimiter == "" else str.split(source, delimiter)
        del v.stack[-2:]
        v.stack.append(result)

    def hc_s_join(v: VM) -> None:
        if len(v.stack) < 2:
            raise MicromaxError("s-join: not enough arguments")
        parts = v.stack[-2]
        delimiter = v.stack[-1]
        if not isinstance(delimiter, str):
            raise MicromaxError(
                f"s-join: delimiter must be str, got {type(delimiter).__name__}"
            )
        if not isinstance(parts, list):
            raise MicromaxError(f"s-join: expected list of str, got {type(parts).__name__}")

        # Preserve the existing type-error precedence: validate the complete
        # public list before deciding whether its otherwise-valid result fits.
        # Unlike the former implementation, this does not duplicate ``parts``.
        for part in parts:
            if not isinstance(part, str):
                raise MicromaxError(
                    f"s-join: expected list of str, got {type(part).__name__}"
                )

        delimiter_bytes = utf8_size(delimiter) * max(0, len(parts) - 1)
        total_bytes = _bounded_string_byte_sum(
            v,
            "s-join",
            parts,
            initial_bytes=delimiter_bytes,
        )
        _preflight_result(v, "s-join", byte_count=total_bytes, cell_count=1)

        result = str.join(delimiter, parts)
        del v.stack[-2:]
        v.stack.append(result)

    def hc_s_replace(v: VM) -> None:
        if len(v.stack) < 3:
            raise MicromaxError("s-replace: not enough arguments")
        source = v.stack[-3]
        old = v.stack[-2]
        new = v.stack[-1]
        if not isinstance(source, str):
            raise MicromaxError(f"s-replace: source must be str, got {type(source).__name__}")
        if not isinstance(old, str):
            raise MicromaxError(f"s-replace: old must be str, got {type(old).__name__}")
        if not isinstance(new, str):
            raise MicromaxError(f"s-replace: new must be str, got {type(new).__name__}")
        if old == "":
            raise MicromaxError("s-replace: empty search")

        match_count = str.count(source, old)
        source_bytes = utf8_size(source)
        old_bytes = utf8_size(old)
        new_bytes = utf8_size(new)
        result_bytes = source_bytes + match_count * (new_bytes - old_bytes)
        _preflight_result(v, "s-replace", byte_count=result_bytes, cell_count=1)

        result = str.replace(source, old, new)
        del v.stack[-3:]
        v.stack.append(result)

    def hc_s_trim(v: VM) -> None:
        source = v.pop_str()
        v.stack.append(str.strip(source))

    def hc_s_upper(v: VM) -> None:
        source = v.pop_str()
        v.stack.append(str.upper(source))

    def hc_s_lower(v: VM) -> None:
        source = v.pop_str()
        v.stack.append(str.lower(source))

    def hc_s_format(v: VM) -> None:
        """( ... fmt n -- s ) Minimal bounded printf-ish formatter."""

        n_raw = v.pop()
        fmt = v.pop_str()
        count = _require_int_arg(n_raw, action="s-format", slot="n")
        if count < 0:
            raise MicromaxError("s-format: n must be >= 0")
        if len(v.stack) < count:
            raise MicromaxError("s-format: not enough arguments")
        planned_count = _format_argument_count(fmt)
        if planned_count > count:
            raise MicromaxError("s-format: not enough arguments")
        if planned_count < count:
            raise MicromaxError("s-format: too many arguments")
        args_start = len(v.stack) - count

        max_bytes, max_cells = _result_limits(v)
        _preflight_result(v, "s-format", byte_count=0, cell_count=1)
        builder = BoundedTextBuilder(action="s-format", max_bytes=max_bytes)
        arg_index = 0
        index = 0
        try:
            while index < len(fmt):
                char = fmt[index]
                if char != "%":
                    builder.append(char)
                    index += 1
                    continue
                spec = fmt[index + 1]
                index += 2
                if spec == "%":
                    builder.append("%")
                    continue
                value = v.stack[args_start + arg_index]
                arg_index += 1
                if spec == "s":
                    if isinstance(value, str):
                        builder.append(value)
                    else:
                        append_value_repr(
                            builder,
                            value,
                            explicit_host_booleans=True,
                        )
                    continue
                if spec == "d":
                    if isinstance(value, bool):
                        raise MicromaxError(
                            f"s-format: %d expects int, got boolean {value!r}"
                        )
                    if isinstance(value, int):
                        builder.append_int(int(value))
                    elif isinstance(value, str):
                        try:
                            parsed = int(value.strip(), 10)
                        except Exception as exc:
                            raise MicromaxError("s-format: %d expects int") from exc
                        builder.append_int(parsed)
                    else:
                        raise MicromaxError("s-format: %d expects int")
                    continue
                raise MicromaxError(f"s-format: unknown specifier %{spec}")
        except TextResultBudgetExceeded as exc:
            # Result-budget denial is a precondition failure.  Restore the
            # formatter control cells so the caller retains the complete
            # inspectable request, matching split/join/replace preflights.
            v.stack.extend([fmt, n_raw])
            violation = hostcall_result_budget_violation_from_counts(
                "s-format",
                byte_count=exc.observed_bytes,
                cell_count=1,
                max_bytes=max_bytes,
                max_cells=max_cells,
            )
            raise MicromaxError(violation or str(exc)) from exc

        if arg_index != count:
            raise MicromaxError("s-format: too many arguments")
        result = builder.finish()
        if count:
            del v.stack[-count:]
        v.stack.append(result)

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
    vm.register_host("s-lower", hc_s_lower)
    vm.register_host("s-format", hc_s_format)
