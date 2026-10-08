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
(multiline), ``s`` (dotall).

Replacement templates use the shared `convert_replacement_template` helper.
"""

from __future__ import annotations

import re

from .regex_tools import convert_replacement_template, parse_re_flags
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

    def _match_to_map(m: re.Match[str]) -> dict:
        # Keep this tiny and JSON-ish.
        out: dict = {
            "start": int(m.start()),
            "end": int(m.end()),
            "group": str(m.group(0)),
            "groups": [str(x) for x in m.groups()],
        }
        gd = m.groupdict()
        if gd:
            out["groupdict"] = {str(k): str(v) for k, v in gd.items()}
        return out

    def hc_re_search(v: VM) -> None:
        flags = v.pop()
        start = v.pop_int()
        pattern = v.pop_str()
        hay = v.pop_str()

        pat = _compile(pattern, flags)
        try:
            m = pat.search(hay, pos=max(0, int(start)))
        except Exception as e:
            raise MicromaxError(f"re.search: {e}") from e
        v.stack.append(0 if m is None else _match_to_map(m))

    def hc_re_findall(v: VM) -> None:
        flags = v.pop()
        start = v.pop_int()
        pattern = v.pop_str()
        hay = v.pop_str()
        pat = _compile(pattern, flags)
        try:
            ms = [ _match_to_map(m) for m in pat.finditer(hay, pos=max(0, int(start))) ]
        except Exception as e:
            raise MicromaxError(f"re.findall: {e}") from e
        v.stack.append(ms)

    def hc_re_sub(v: VM) -> None:
        flags = v.pop()
        repl = v.pop_str()
        pattern = v.pop_str()
        hay = v.pop_str()
        pat = _compile(pattern, flags)
        repl_py = convert_replacement_template(repl)
        try:
            out = pat.sub(repl_py, hay)
        except Exception as e:
            raise MicromaxError(f"re.sub: {e}") from e
        v.stack.append(out)

    def hc_re_subn(v: VM) -> None:
        flags = v.pop()
        repl = v.pop_str()
        pattern = v.pop_str()
        hay = v.pop_str()
        pat = _compile(pattern, flags)
        repl_py = convert_replacement_template(repl)
        try:
            out, n = pat.subn(repl_py, hay)
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
