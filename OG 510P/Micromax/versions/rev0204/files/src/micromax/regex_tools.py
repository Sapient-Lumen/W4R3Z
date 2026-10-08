"""micromax.regex_tools

Small shared helpers for regular-expression features.

Why a shared module?
- The editor's command-bar `replace`/`replaceall` commands and the VM's regex
  hostcalls should agree on replacement-template semantics.
- Keeping the conversion logic in one place avoids drift.

Replacement templates
---------------------

Micromax uses a micro-like template convention for replacement strings:

- ``$1`` / ``$2`` ... expand numbered capture groups.
- ``$name`` or ``${name}`` expand named capture groups.
- ``$$`` becomes a literal ``$``.

Python's ``re`` module uses ``\\g<name>`` syntax for group expansion, so we
convert templates into that form.
"""

from __future__ import annotations

import re


def convert_replacement_template(template: str) -> str:
    """Convert a micro-ish replacement template to Python ``re`` syntax."""

    sentinel = "\u0000DOLLAR\u0000"
    s = str(template)
    s = s.replace("$$", sentinel)

    def repl(m: re.Match[str]) -> str:
        raw = str(m.group(1))
        if raw.startswith("{") and raw.endswith("}"):
            raw = raw[1:-1]
        # Python's \g<...> accepts both numeric and named groups.
        return f"\\g<{raw}>"

    s = re.sub(r"\$(\{[^}]+\}|[A-Za-z_][A-Za-z0-9_]*|[0-9]+)", repl, s)
    return s.replace(sentinel, "$")


def parse_re_flags(flags: object) -> int:
    """Parse a tiny flag set used by regex hostcalls.

    Accepts:
    - ``0`` or ``""``: no flags
    - a string containing any of: ``i`` (ignorecase), ``m`` (multiline),
      ``s`` (dotall)
    """

    if flags in (0, None, ""):
        return 0
    if isinstance(flags, int):
        return int(flags)
    if not isinstance(flags, str):
        raise TypeError("flags must be 0, int, or str")
    out = 0
    for ch in flags:
        if ch == "i":
            out |= re.IGNORECASE
        elif ch == "m":
            out |= re.MULTILINE
        elif ch == "s":
            out |= re.DOTALL
        elif ch in (" ", "\t", "\n"):
            continue
        else:
            raise ValueError(f"unknown regex flag: {ch!r}")
    return out
