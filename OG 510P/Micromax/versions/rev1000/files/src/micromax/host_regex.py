"""micromax.host_regex

Reference host-provided regex helpers.

These are registered as hostcalls (allowlisted via `hostcall`) so different
embeddings can choose whether to expose them.

Hostcall names:
  re.search   ( hay pattern start flags -- m|0 )
  re.findall  ( hay pattern start flags -- ms )
  re.sub      ( hay pattern repl flags -- out )
  re.subn     ( hay pattern repl flags -- out n )
  re.escape   ( s -- s2 )

`flags` is ``0`` or a string containing any of: ``i`` (ignorecase), ``m``
(multiline), ``s`` (dotall).  Python ``None``, booleans, and non-zero Python
integer flags are rejected so embedding-only sentinel values and host-specific
side effects such as ``re.DEBUG`` cannot leak through this tiny portable
dialect.

`start` positions for search-style hostcalls must be integer indexes.
Python booleans are rejected even though `bool` subclasses `int`, negative
starts are rejected instead of being silently clamped to the beginning of the
haystack, and starts beyond the haystack are treated as empty searches instead
of being host-clamped to the final zero-width position.

Regex hostcalls now preflight public argument shape and byte budgets before
consuming arguments.  The defaults are deliberately hostcall-specific and
embedding-tunable on the VM (`hostcall_regex_max_haystack_bytes`,
`hostcall_regex_max_pattern_bytes`, and
`hostcall_regex_max_replacement_bytes`).  In addition, every caller-authored
regex operation is routed through a minimal subprocess worker while
`hostcall_regex_timeout_seconds` is positive, so both known and unrecognized
catastrophic-backtracking shapes can be killed without wedging the editor host.
Embeddings that deliberately set the timeout to zero retain the legacy
local-engine escape hatch.

`re.sub` / `re.subn` reject zero-width matches before substitution so
invisible-match bulk rewrites stay aligned with editor replace/replaceall.
Replacement-template expansion failures are reported as explicit
``invalid replacement`` errors, matching editor replace surfaces.

Replacement templates use the shared `convert_replacement_template` helper:
`$0`/`$1`/`$name`/`${name}` are active, `$$` is literal `$`, raw
backslashes stay literal, and leading-zero numeric tokens such as `$01`
stay literal instead of being normalized by Python's replacement parser.

Match maps report unmatched optional captures as the VM absent sentinel `0`,
while captures that participate with an empty string remain `""`.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Callable

from .regex_tools import (
    convert_replacement_template,
    format_replacement_template_error,
    parse_re_flags,
)
from .host_limits import (
    DEFAULT_HOSTCALL_RESULT_MAX_BYTES,
    DEFAULT_HOSTCALL_RESULT_MAX_CELLS,
    utf8_size,
)
from .regex_runtime import (
    DEFAULT_REGEX_WORKER_RESULT_MAX_BYTES,
    RegexWorkerError,
    regex_pattern_needs_containment,
    run_regex_worker,
)
from .vm import VM, MicromaxError


DEFAULT_REGEX_HAYSTACK_MAX_BYTES = 262_144
DEFAULT_REGEX_PATTERN_MAX_BYTES = 10_000
DEFAULT_REGEX_REPLACEMENT_MAX_BYTES = 262_144
DEFAULT_REGEX_TIMEOUT_SECONDS = 0.25
DEFAULT_REGEX_WORKER_MAX_MATCHES = 100_000


@dataclass(frozen=True)
class _SearchArgs:
    hay: str
    pattern: str
    start: int
    flags: object
    compiled: re.Pattern[str] | None


@dataclass(frozen=True)
class _SubArgs:
    hay: str
    pattern: str
    repl: str
    flags: object
    compiled: re.Pattern[str] | None
    repl_py: str


def _limit(v: VM, attr: str, default: int) -> int:
    try:
        return int(getattr(v, attr, default))
    except Exception:
        return int(default)


def _check_bytes(v: VM, *, field: str, value: str, attr: str, default: int) -> None:
    max_bytes = _limit(v, attr, default)
    if max_bytes <= 0:
        return
    size = utf8_size(value, stop_after=max_bytes)
    if size > max_bytes:
        raise MicromaxError(f"re: {field} too large: {size} bytes > {max_bytes}")


def _capture_value(value: str | None) -> str | int:
    # Python reports unmatched optional captures as None.  The VM's public
    # false/absent sentinel is 0, and surfacing the literal string "None"
    # makes absence indistinguishable from text that actually matched those
    # four characters.  Keep matched empty strings as "" so callers can
    # still distinguish "matched empty" from "did not participate".
    return 0 if value is None else str(value)


def _match_to_map(m: re.Match[str]) -> dict:
    # Keep this tiny and JSON-ish so it can also cross the regex worker
    # containment pipe without returning host-owned Match objects.
    out: dict = {
        "start": int(m.start()),
        "end": int(m.end()),
        "group": str(m.group(0)),
        "groups": [_capture_value(x) for x in m.groups()],
    }
    gd = m.groupdict()
    if gd:
        out["groupdict"] = {str(k): _capture_value(v) for k, v in gd.items()}
    return out


def _timeout_seconds(v: VM) -> float:
    try:
        timeout = float(
            getattr(v, "hostcall_regex_timeout_seconds", DEFAULT_REGEX_TIMEOUT_SECONDS)
        )
    except Exception:
        return float(DEFAULT_REGEX_TIMEOUT_SECONDS)
    # NaN previously made ``timeout > 0`` false and silently revived the
    # unbounded local engine.  Non-finite configuration is invalid rather than
    # an intentional opt-out; keep the explicit finite ``<= 0`` escape hatch.
    if not math.isfinite(timeout):
        return float(DEFAULT_REGEX_TIMEOUT_SECONDS)
    return float(timeout)


def _worker_result_byte_limit(v: VM) -> int:
    """Return a finite child-output cap aligned with the VM result budget.

    A non-positive VM budget means the shared hostcall checker is disabled, not
    that an owned child may emit without bound.  Keep the worker's independent
    16 MiB ceiling in that case.
    """

    configured = _limit(
        v,
        "hostcall_result_max_bytes",
        DEFAULT_HOSTCALL_RESULT_MAX_BYTES,
    )
    if configured <= 0:
        return DEFAULT_REGEX_WORKER_RESULT_MAX_BYTES
    return min(DEFAULT_REGEX_WORKER_RESULT_MAX_BYTES, configured)


def _worker_match_limit(v: VM) -> int:
    """Return a conservative pre-materialization cap for list results."""

    configured = _limit(
        v,
        "hostcall_result_max_cells",
        DEFAULT_HOSTCALL_RESULT_MAX_CELLS,
    )
    if configured <= 0:
        return DEFAULT_REGEX_WORKER_MAX_MATCHES
    # Every match map consumes at least one result cell.  The VM's recursive
    # checker remains authoritative after return; this earlier cap only avoids
    # constructing an obviously impossible payload in the child.
    return min(DEFAULT_REGEX_WORKER_MAX_MATCHES, configured)


# Compatibility spelling retained for focused tests and old embeddings.
_regex_pattern_needs_containment = regex_pattern_needs_containment


def _contained_regex_value(
    v: VM,
    *,
    action: str,
    hay: str,
    pattern: str,
    start: int = 0,
    flags: object,
    repl_py: str | None = None,
    max_matches: int | None = None,
    fallback: Callable[[], object],
) -> object:
    timeout = _timeout_seconds(v)
    if timeout > 0:
        try:
            return run_regex_worker(
                action=action,
                haystack=hay,
                pattern=pattern,
                start=start,
                flags=flags,
                replacement=repl_py,
                timeout_seconds=timeout,
                max_matches=max_matches,
                max_result_bytes=_worker_result_byte_limit(v),
            )
        except RegexWorkerError as exc:
            raise MicromaxError(f"{action}: {exc}") from exc
    return fallback()


def install_regex_hostcalls(vm: VM) -> None:
    """Install the reference regex hostcall set into `vm`."""

    vm.host_features.add("mx.regex")

    def _prepare_pattern(
        v: VM,
        pattern: str,
        flags: object,
    ) -> re.Pattern[str] | None:
        """Validate cheap public shape and compile only for the local escape hatch.

        With a positive timeout, the isolated child owns both regex parsing and
        matching.  CPython's parser can itself exhaust recursion on a deeply
        nested, byte-bounded pattern, so compiling here would leave a foreground
        failure path even though matching was nominally contained.
        """

        _check_bytes(
            v,
            field="pattern",
            value=pattern,
            attr="hostcall_regex_max_pattern_bytes",
            default=DEFAULT_REGEX_PATTERN_MAX_BYTES,
        )
        try:
            parsed_flags = parse_re_flags(flags)
        except Exception as e:
            # Keep the portable flag dialect and its stable error surface local;
            # parsing these three flag letters cannot enter the regex engine.
            raise MicromaxError(f"invalid regex: {e}") from e
        if _timeout_seconds(v) > 0:
            return None
        try:
            return re.compile(pattern, flags=parsed_flags)
        except Exception as e:
            # Explicit finite nonpositive timeout is the documented embedding
            # opt-out.  Its local compile still normalizes parser recursion and
            # syntax failures instead of leaking raw host exceptions.
            raise MicromaxError(f"invalid regex: {e}") from e

    def _local_pattern(pattern: re.Pattern[str] | None) -> re.Pattern[str]:
        if pattern is None:
            raise MicromaxError("regex local engine unavailable")
        return pattern

    def _local_search_value(args: _SearchArgs) -> object:
        if args.start > len(args.hay):
            return 0
        match = _local_pattern(args.compiled).search(args.hay, pos=args.start)
        return 0 if match is None else _match_to_map(match)

    def _local_findall_value(args: _SearchArgs) -> list[dict]:
        if args.start > len(args.hay):
            return []
        return [
            _match_to_map(match)
            for match in _local_pattern(args.compiled).finditer(
                args.hay,
                pos=args.start,
            )
        ]

    def _require_str_arg(value: object, *, action: str, slot: str) -> str:
        if not isinstance(value, str):
            raise MicromaxError(f"{action}: {slot} must be str, got {type(value).__name__}")
        return value

    def _checked_start_pos(start: object) -> int:
        # Python's regex engine tolerates negative ``pos`` values by effectively
        # searching from the beginning.  The Micromax hostcall boundary should
        # not hide caller bugs that way: ``start`` is a visible index argument,
        # so negative values fail before the regex engine sees the request.
        # Also reject Python booleans explicitly.  ``bool`` is an ``int``
        # subclass in Python, but it is an embedding-only sentinel here, not a
        # portable VM-facing index spelling.
        if isinstance(start, bool):
            raise MicromaxError(f"re: start must be an integer, got boolean {start!r}")
        if not isinstance(start, int):
            raise MicromaxError(f"re: start must be an integer, got {type(start).__name__}")
        if start < 0:
            raise MicromaxError(f"re: start must be non-negative, got {start}")
        return int(start)

    def _preflight_search_args(v: VM, *, action: str) -> _SearchArgs:
        # Validate the whole public argument shape before consuming anything.
        # This keeps direct hostcall failures inspectable and prevents giant
        # caller-controlled payloads from reaching the host regex engine before
        # the boundary has named the budget violation.
        if len(v.stack) < 4:
            raise MicromaxError(f"{action}: not enough arguments")
        hay = _require_str_arg(v.stack[-4], action=action, slot="haystack")
        pattern = _require_str_arg(v.stack[-3], action=action, slot="pattern")
        start = _checked_start_pos(v.stack[-2])
        flags = v.stack[-1]
        _check_bytes(
            v,
            field="haystack",
            value=hay,
            attr="hostcall_regex_max_haystack_bytes",
            default=DEFAULT_REGEX_HAYSTACK_MAX_BYTES,
        )
        pat = _prepare_pattern(v, pattern, flags)
        return _SearchArgs(hay=hay, pattern=pattern, start=start, flags=flags, compiled=pat)

    def _preflight_sub_args(v: VM, *, action: str) -> _SubArgs:
        if len(v.stack) < 4:
            raise MicromaxError(f"{action}: not enough arguments")
        hay = _require_str_arg(v.stack[-4], action=action, slot="haystack")
        pattern = _require_str_arg(v.stack[-3], action=action, slot="pattern")
        repl = _require_str_arg(v.stack[-2], action=action, slot="replacement")
        flags = v.stack[-1]
        _check_bytes(
            v,
            field="haystack",
            value=hay,
            attr="hostcall_regex_max_haystack_bytes",
            default=DEFAULT_REGEX_HAYSTACK_MAX_BYTES,
        )
        _check_bytes(
            v,
            field="replacement",
            value=repl,
            attr="hostcall_regex_max_replacement_bytes",
            default=DEFAULT_REGEX_REPLACEMENT_MAX_BYTES,
        )
        pat = _prepare_pattern(v, pattern, flags)
        repl_py = convert_replacement_template(repl)
        if pat is not None:
            _reject_zero_width_sub_matches(action, pat, hay)
            try:
                # The explicit local-engine escape hatch keeps legacy eager
                # template validation.  Positive-timeout calls validate in the
                # same child that owns pattern compilation and matching.
                pat.sub(repl_py, "", count=0)
            except (re.error, IndexError) as e:
                raise MicromaxError(
                    f"{action}: invalid replacement: {format_replacement_template_error(e)}"
                ) from e
            except Exception as e:
                raise MicromaxError(f"{action}: {e}") from e
        return _SubArgs(
            hay=hay, pattern=pattern, repl=repl, flags=flags, compiled=pat, repl_py=repl_py
        )

    def _reject_zero_width_sub_matches(action: str, pat: re.Pattern[str], hay: str) -> None:
        # The regex hostcalls are documented as aligned with editor
        # replace/replaceall behavior.  Editor bulk replace rejects zero-width
        # matches before mutation because they describe invisible insertion
        # points rather than visible text spans.  Keep the VM substitution
        # helpers on the same trust boundary: scan before producing output so
        # no partial replacement result is returned for a pattern such as ``^``,
        # ``$``, ``(?=x)``, or the empty regex.
        try:
            for m in pat.finditer(hay):
                if m.start() == m.end():
                    raise MicromaxError(f"{action}: zero-width matches are not supported")
        except MicromaxError:
            raise
        except Exception as e:
            raise MicromaxError(f"{action}: {e}") from e

    def hc_re_search(v: VM) -> None:
        args = _preflight_search_args(v, action="re.search")
        try:
            result = _contained_regex_value(
                v,
                action="re.search",
                hay=args.hay,
                pattern=args.pattern,
                start=args.start,
                flags=args.flags,
                fallback=lambda: _local_search_value(args),
            )
        except MicromaxError:
            raise
        except Exception as e:
            raise MicromaxError(f"re.search: {e}") from e
        if args.start > len(args.hay):
            # Python clamps an over-large ``pos`` to ``len(hay)`` for zero-width
            # patterns.  Keep Micromax's empty-search contract, but only after
            # the worker has validated the pattern inside containment.
            result = 0
        del v.stack[-4:]
        v.stack.append(result)

    def hc_re_findall(v: VM) -> None:
        args = _preflight_search_args(v, action="re.findall")
        try:
            result = _contained_regex_value(
                v,
                action="re.findall",
                hay=args.hay,
                pattern=args.pattern,
                start=args.start,
                flags=args.flags,
                max_matches=_worker_match_limit(v),
                fallback=lambda: _local_findall_value(args),
            )
        except MicromaxError:
            raise
        except Exception as e:
            raise MicromaxError(f"re.findall: {e}") from e
        if args.start > len(args.hay):
            result = []
        del v.stack[-4:]
        v.stack.append(result)

    def hc_re_sub(v: VM) -> None:
        args = _preflight_sub_args(v, action="re.sub")
        try:
            result = _contained_regex_value(
                v,
                action="re.sub",
                hay=args.hay,
                pattern=args.pattern,
                flags=args.flags,
                repl_py=args.repl_py,
                max_matches=DEFAULT_REGEX_WORKER_MAX_MATCHES,
                fallback=lambda: _local_pattern(args.compiled).sub(
                    args.repl_py,
                    args.hay,
                ),
            )
        except MicromaxError:
            raise
        except (re.error, IndexError) as e:
            raise MicromaxError(f"re.sub: invalid replacement: {format_replacement_template_error(e)}") from e
        except Exception as e:
            raise MicromaxError(f"re.sub: {e}") from e
        del v.stack[-4:]
        v.stack.append(result)

    def hc_re_subn(v: VM) -> None:
        args = _preflight_sub_args(v, action="re.subn")
        try:
            result = _contained_regex_value(
                v,
                action="re.subn",
                hay=args.hay,
                pattern=args.pattern,
                flags=args.flags,
                repl_py=args.repl_py,
                max_matches=DEFAULT_REGEX_WORKER_MAX_MATCHES,
                fallback=lambda: list(
                    _local_pattern(args.compiled).subn(args.repl_py, args.hay)
                ),
            )
        except MicromaxError:
            raise
        except (re.error, IndexError) as e:
            raise MicromaxError(f"re.subn: invalid replacement: {format_replacement_template_error(e)}") from e
        except Exception as e:
            raise MicromaxError(f"re.subn: {e}") from e
        if not isinstance(result, list) or len(result) != 2:
            raise MicromaxError("re.subn: regex worker returned malformed result")
        del v.stack[-4:]
        v.stack.append(str(result[0]))
        v.stack.append(int(result[1]))

    def hc_re_escape(v: VM) -> None:
        if not v.stack:
            raise MicromaxError("re.escape: not enough arguments")
        s = _require_str_arg(v.stack[-1], action="re.escape", slot="input")
        _check_bytes(
            v,
            field="input",
            value=s,
            attr="hostcall_regex_max_haystack_bytes",
            default=DEFAULT_REGEX_HAYSTACK_MAX_BYTES,
        )
        del v.stack[-1:]
        v.stack.append(re.escape(s))

    vm.register_host("re.search", hc_re_search)
    vm.register_host("re.findall", hc_re_findall)
    vm.register_host("re.sub", hc_re_sub)
    vm.register_host("re.subn", hc_re_subn)
    vm.register_host("re.escape", hc_re_escape)
