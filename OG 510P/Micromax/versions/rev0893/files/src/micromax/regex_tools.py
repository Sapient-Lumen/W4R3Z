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
    """Convert a micro-ish replacement template to Python ``re`` syntax.

    The public template dialect is deliberately dollar-based: ``$1``,
    ``$name``, ``${name}``, and ``$$``.  Python's replacement strings also
    treat backslashes as escapes/backreferences, so raw user backslashes must be
    escaped while generated ``\\g<...>`` group references remain active.

    This is intentionally a single-pass parser rather than a sentinel-based
    rewrite: replacement templates are user text, and every byte/codepoint that
    is not part of the documented dollar dialect must round-trip literally.
    """

    def is_ascii_digit(ch: str) -> bool:
        return "0" <= ch <= "9"

    def is_ascii_name_start(ch: str) -> bool:
        return ch == "_" or "A" <= ch <= "Z" or "a" <= ch <= "z"

    def is_ascii_name_char(ch: str) -> bool:
        return is_ascii_name_start(ch) or is_ascii_digit(ch)

    def is_valid_numeric_group_token(raw: str) -> bool:
        # Python's ``\g<01>`` treats ``01`` as group 1, but Micromax's
        # visible dollar dialect should not silently normalize a different
        # token.  Keep non-canonical numeric spellings literal instead.
        return bool(raw) and all(is_ascii_digit(ch) for ch in raw) and (raw == "0" or raw[0] != "0")

    def is_valid_group_token(raw: str) -> bool:
        return bool(raw) and (
            is_valid_numeric_group_token(raw)
            or (is_ascii_name_start(raw[0]) and all(is_ascii_name_char(ch) for ch in raw))
        )

    def literal_segment(raw: str) -> str:
        # The returned string is consumed by Python's replacement parser, so raw
        # backslashes must still be protected even when a malformed `${...}`
        # sequence is kept literal.
        return raw.replace("\\", "\\\\")

    s = str(template)
    out: list[str] = []
    i = 0
    n = len(s)

    while i < n:
        ch = s[i]

        if ch == "\\":
            # Keep user-authored backslashes literal.  Only the references
            # generated from Micromax's dollar syntax should reach Python's
            # replacement parser as active ``\\g<...>`` escapes.
            out.append("\\\\")
            i += 1
            continue

        if ch != "$":
            out.append(ch)
            i += 1
            continue

        if i + 1 >= n:
            out.append("$")
            i += 1
            continue

        nxt = s[i + 1]
        if nxt == "$":
            out.append("$")
            i += 2
            continue

        if nxt == "{":
            end = s.find("}", i + 2)
            if end >= 0:
                raw = s[i + 2 : end]
                if is_valid_group_token(raw):
                    # Python's \g<...> accepts both numeric and named groups.
                    out.append(f"\\g<{raw}>")
                else:
                    # Keep malformed braced placeholders literal as one segment.
                    # In particular, do not allow `>` inside `${...}` to close
                    # Python's generated `\g<...>` early and accidentally turn
                    # nearby literal text into active replacement syntax.
                    out.append(literal_segment(s[i : end + 1]))
                i = end + 1
                continue
            # An unterminated `${...` sequence is malformed as a whole.  Preserve
            # the rest of the user template literally so nested `$1`-shaped text
            # cannot become an active reference merely because the closing brace
            # was omitted.
            out.append(literal_segment(s[i:]))
            break

        if is_ascii_digit(nxt):
            j = i + 2
            while j < n and is_ascii_digit(s[j]):
                j += 1
            raw = s[i + 1 : j]
            if is_valid_numeric_group_token(raw):
                out.append(f"\\g<{raw}>")
            else:
                out.append(literal_segment(s[i:j]))
            i = j
            continue

        if is_ascii_name_start(nxt):
            j = i + 2
            while j < n and is_ascii_name_char(s[j]):
                j += 1
            out.append(f"\\g<{s[i + 1:j]}>")
            i = j
            continue

        out.append("$")
        i += 1

    return "".join(out)


def format_replacement_template_error(exc: BaseException) -> str:
    """Return a stable one-line diagnostic for replacement-template errors."""

    msg = str(exc).strip()
    return msg or exc.__class__.__name__


def parse_re_flags(flags: object) -> int:
    """Parse the tiny public flag set used by regex hostcalls.

    Accepts:
    - ``0`` or ``""``: no flags
    - a string containing any of: ``i`` (ignorecase), ``m`` (multiline),
      ``s`` (dotall)

    Deliberately reject Python-only sentinel values and non-zero Python integer
    flags.  The public Micromax dialect is portable and side-effect-free;
    accepting raw host-engine flags would leak Python-only behavior such as
    ``re.DEBUG`` output through a VM boundary that is documented as tiny and
    cross-host.
    """

    if isinstance(flags, bool):
        raise TypeError(f"flags must be 0 or a string of ims flags, got boolean {flags!r}")
    if flags in (0, ""):
        return 0
    if flags is None:
        raise TypeError("flags must be 0 or a string of ims flags, got None")
    if isinstance(flags, int):
        raise ValueError(f"regex flags must be 0 or a string of ims flags, got integer {int(flags)}")
    if not isinstance(flags, str):
        raise TypeError("flags must be 0 or a string of ims flags")
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
