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

import re

from .regex_tools import convert_replacement_template, format_replacement_template_error, parse_re_flags
from .vm import VM, MicromaxError


def install_regex_hostcalls(vm: VM) -> None:
    """Install the reference regex hostcall set into `vm`."""

    vm.host_features.add("mx.regex")

    def _compile(pattern: str, flags: object) -> re.Pattern[str]:
        pat_s = str(pattern)
        if len(pat_s) > 10_000:
            raise MicromaxError("re: pattern too large")
        try:
            return re.compile(pat_s, flags=parse_re_flags(flags))
        except Exception as e:
            # Normalize Python's error surface into a stable VM error.
            raise MicromaxError(f"invalid regex: {e}") from e

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

    def _pop_search_args(v: VM) -> tuple[str, str, int, object]:
        # Pop the full public hostcall shape before validating the already-popped
        # start value.  Direct hostcall users then get the same explicit start
        # diagnostics without leaving stale hay/pattern arguments behind.
        flags = v.pop()
        start_raw = v.pop()
        pattern = v.pop_str()
        hay = v.pop_str()
        return hay, pattern, _checked_start_pos(start_raw), flags

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

    def _capture_value(value: str | None) -> str | int:
        # Python reports unmatched optional captures as None.  The VM's public
        # false/absent sentinel is 0, and surfacing the literal string "None"
        # makes absence indistinguishable from text that actually matched those
        # four characters.  Keep matched empty strings as "" so callers can
        # still distinguish "matched empty" from "did not participate".
        return 0 if value is None else str(value)

    def _match_to_map(m: re.Match[str]) -> dict:
        # Keep this tiny and JSON-ish.
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

    def hc_re_search(v: VM) -> None:
        hay, pattern, start, flags = _pop_search_args(v)

        pat = _compile(pattern, flags)
        if start > len(hay):
            # Python clamps an over-large ``pos`` to ``len(hay)`` for zero-width
            # patterns such as ``""`` or ``"$"``.  The Micromax contract treats
            # a positive out-of-range start as an ordinary empty search, so make
            # that boundary explicit before delegating to the host engine.
            v.stack.append(0)
            return
        try:
            m = pat.search(hay, pos=start)
        except Exception as e:
            raise MicromaxError(f"re.search: {e}") from e
        v.stack.append(0 if m is None else _match_to_map(m))

    def hc_re_findall(v: VM) -> None:
        hay, pattern, start, flags = _pop_search_args(v)
        pat = _compile(pattern, flags)
        if start > len(hay):
            v.stack.append([])
            return
        try:
            ms = [_match_to_map(m) for m in pat.finditer(hay, pos=start)]
        except Exception as e:
            raise MicromaxError(f"re.findall: {e}") from e
        v.stack.append(ms)

    def hc_re_sub(v: VM) -> None:
        flags = v.pop()
        repl = v.pop_str()
        pattern = v.pop_str()
        hay = v.pop_str()
        pat = _compile(pattern, flags)
        _reject_zero_width_sub_matches("re.sub", pat, hay)
        repl_py = convert_replacement_template(repl)
        try:
            out = pat.sub(repl_py, hay)
        except (re.error, IndexError) as e:
            raise MicromaxError(f"re.sub: invalid replacement: {format_replacement_template_error(e)}") from e
        except Exception as e:
            raise MicromaxError(f"re.sub: {e}") from e
        v.stack.append(out)

    def hc_re_subn(v: VM) -> None:
        flags = v.pop()
        repl = v.pop_str()
        pattern = v.pop_str()
        hay = v.pop_str()
        pat = _compile(pattern, flags)
        _reject_zero_width_sub_matches("re.subn", pat, hay)
        repl_py = convert_replacement_template(repl)
        try:
            out, n = pat.subn(repl_py, hay)
        except (re.error, IndexError) as e:
            raise MicromaxError(f"re.subn: invalid replacement: {format_replacement_template_error(e)}") from e
        except Exception as e:
            raise MicromaxError(f"re.subn: {e}") from e
        v.stack.append(out)
        v.stack.append(int(n))

    def hc_re_escape(v: VM) -> None:
        s = v.pop_str()
        v.stack.append(re.escape(s))

    vm.register_host("re.search", hc_re_search)
    vm.register_host("re.findall", hc_re_findall)
    vm.register_host("re.sub", hc_re_sub)
    vm.register_host("re.subn", hc_re_subn)
    vm.register_host("re.escape", hc_re_escape)
