from __future__ import annotations

"""Best-effort parsing of GLib/GVariant text output.

VHK intentionally avoids heavy DBus bindings (PyGObject, dbus-python) so it can
run in minimal automation environments.

Some tooling we want to interrogate (notably GNOME's Mutter DisplayConfig
interface) is easiest to reach via `gdbus call`, which returns a compact
GVariant pretty-printed representation.

This module implements a *small*, conservative adapter that converts common
`gdbus call` output into Python primitives via ``ast.literal_eval``.

Supported patterns (best effort):
  - typed integers like ``uint32 7`` and ``<uint32 2>``
  - booleans like ``<true>`` / ``<false>``
  - typed dict annotations like ``@a{sv} {}``
  - variant wrappers like ``<'xrandr'>`` or ``<(16384, 16384)>``

This is not a general-purpose GVariant parser; it exists to support a handful
of stable portal / compositor probes.
"""

import ast
import re


_TYPED_INT = re.compile(r"\b(?:u?int(?:8|16|32|64))\s+(-?\d+)\b")
_TYPED_INT_IN_ANGLE = re.compile(r"<\s*(?:u?int(?:8|16|32|64))\s+(-?\d+)\s*>")


def _strip_angle_brackets_outside_quotes(text: str) -> str:
    """Remove ``<`` and ``>`` used by gdbus to denote variants.

    We only strip these outside of string literals.
    """

    out: list[str] = []
    in_quote = False
    escape = False
    for ch in text:
        if in_quote:
            out.append(ch)
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == "'":
                in_quote = False
            continue

        if ch == "'":
            in_quote = True
            out.append(ch)
            continue

        if ch in "<>":
            # Variant marker - drop.
            continue
        out.append(ch)
    return "".join(out)


def _replace_bare_bools_outside_quotes(text: str) -> str:
    """Replace bare `true`/`false` tokens with Python booleans."""

    out: list[str] = []
    token: list[str] = []
    in_quote = False
    escape = False

    def flush_token() -> None:
        if not token:
            return
        t = "".join(token)
        token.clear()
        if t == "true":
            out.append("True")
        elif t == "false":
            out.append("False")
        else:
            out.append(t)

    for ch in text:
        if in_quote:
            out.append(ch)
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == "'":
                in_quote = False
            continue

        if ch == "'":
            flush_token()
            in_quote = True
            out.append(ch)
            continue

        if ch.isalnum() or ch == "_":
            token.append(ch)
            continue

        flush_token()
        out.append(ch)

    flush_token()
    return "".join(out)


def gdbus_call_output_to_python(text: str) -> object:
    """Parse `gdbus call` output into Python primitives.

    Parameters
    ----------
    text:
        Raw stdout from a `gdbus call` invocation.

    Returns
    -------
    Parsed Python object.
    """

    src = (text or "").strip()
    if not src:
        raise ValueError("Empty gdbus output")

    # Normalize common gdbus markers.
    src = src.replace("<true>", "True").replace("<false>", "False")
    src = _replace_bare_bools_outside_quotes(src)
    src = _TYPED_INT_IN_ANGLE.sub(r"\1", src)
    src = _TYPED_INT.sub(r"\1", src)

    # Strip the most common dict annotation used by gdbus when printing variants.
    src = src.replace("@a{sv} ", "")

    # Remaining angle brackets are usually just variant wrappers like <'xrandr'>.
    src = _strip_angle_brackets_outside_quotes(src)

    try:
        return ast.literal_eval(src)
    except Exception as exc:
        raise ValueError(f"Failed to parse gdbus output as a Python literal: {exc}") from exc
