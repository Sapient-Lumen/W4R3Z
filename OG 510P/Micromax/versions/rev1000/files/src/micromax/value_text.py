"""Bounded deterministic rendering of Micromax-visible values.

Plugin dispatch fuel counts VM steps.  It cannot interrupt one Python string
allocation after a primitive has entered CPython.  This module therefore builds
representations under an embedding-owned UTF-8 byte ceiling and stops before a
shared object graph can amplify into an enormous result.

The representation intentionally matches the long-standing ``to-str`` and
``s-format %s`` surface: nested strings are JSON-quoted, lists/maps are stable,
and recursion deeper than six levels is shown as ``...``.  Host-only boolean
sentinels can either retain portable integer rendering or remain visibly typed.
"""

from __future__ import annotations

import io
import json
import operator
from typing import Any

from .host_limits import DEFAULT_VALUE_TEXT_MAX_BYTES, utf8_size


class TextResultBudgetExceeded(ValueError):
    """Raised before a value-to-text operation exceeds its byte ceiling."""

    def __init__(self, *, action: str, observed_bytes: int, max_bytes: int) -> None:
        self.action = str(action)
        self.observed_bytes = max(0, int(observed_bytes))
        self.max_bytes = max(0, int(max_bytes))
        super().__init__(
            f"text result budget exceeded: {self.action}: "
            f"{self.observed_bytes} bytes > {self.max_bytes}"
        )


def effective_value_text_max_bytes(vm: Any) -> int:
    """Return the embedding-tunable value-rendering ceiling.

    Missing or malformed settings fail to the safe default.  A finite
    nonpositive value is an explicit embedding opt-out.
    """

    raw = getattr(vm, "value_text_max_bytes", DEFAULT_VALUE_TEXT_MAX_BYTES)
    try:
        if isinstance(raw, bool):
            raise TypeError("bool is not a byte count")
        if isinstance(raw, str):
            value = int(raw.strip(), 10)
        else:
            value = operator.index(raw)
    except (TypeError, ValueError, OverflowError):
        value = int(DEFAULT_VALUE_TEXT_MAX_BYTES)
    return max(0, int(value))


def _json_string_utf8_size(text: str, *, stop_after: int | None = None) -> int:
    """Exact UTF-8 size of ``json.dumps(text, ensure_ascii=False)``."""

    limit = None if stop_after is None else max(-1, int(stop_after))
    total = 2  # surrounding quotes
    if limit is not None and total > limit:
        return total
    for char in text:
        codepoint = ord(char)
        if char in {'"', "\\"} or char in {"\b", "\f", "\n", "\r", "\t"}:
            total += 2
        elif codepoint < 0x20:
            total += 6  # \u00xx
        elif codepoint <= 0x7F or 0xD800 <= codepoint <= 0xDFFF:
            total += 1
        elif codepoint <= 0x7FF:
            total += 2
        elif codepoint <= 0xFFFF:
            total += 3
        else:
            total += 4
        if limit is not None and total > limit:
            return total
    return total


class BoundedTextBuilder:
    """A small UTF-8-accounted text sink backed by ``io.StringIO``."""

    def __init__(self, *, action: str, max_bytes: int) -> None:
        self.action = str(action)
        self.max_bytes = max(0, int(max_bytes))
        self.bytes_used = 0
        self._out = io.StringIO()

    @property
    def remaining_bytes(self) -> int | None:
        if self.max_bytes <= 0:
            return None
        return max(0, self.max_bytes - self.bytes_used)

    def _reserve(self, byte_count: int) -> None:
        observed = self.bytes_used + max(0, int(byte_count))
        if self.max_bytes > 0 and observed > self.max_bytes:
            raise TextResultBudgetExceeded(
                action=self.action,
                observed_bytes=observed,
                max_bytes=self.max_bytes,
            )
        self.bytes_used = observed

    def append(self, text: str) -> None:
        if not isinstance(text, str):
            raise TypeError("BoundedTextBuilder.append expects str")
        remaining = self.remaining_bytes
        size = utf8_size(text, stop_after=remaining)
        self._reserve(size)
        self._out.write(text)

    def append_json_string(self, text: str) -> None:
        if not isinstance(text, str):
            raise TypeError("append_json_string expects str")
        remaining = self.remaining_bytes
        size = _json_string_utf8_size(text, stop_after=remaining)
        self._reserve(size)
        # The exact preflight above guarantees this materialized fragment fits
        # within the final ceiling before CPython creates it.
        self._out.write(json.dumps(text, ensure_ascii=False))

    def append_int(self, value: int) -> None:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError("append_int expects a non-boolean int")
        magnitude = abs(int(value))
        bits = magnitude.bit_length()
        sign = 1 if int(value) < 0 else 0
        # A conservative lower bound lets giant integers fail before decimal
        # conversion enters CPython's native big-int formatting loop.
        min_digits = 1 if bits == 0 else (((bits - 1) * 30102) // 100000) + 1
        minimum = sign + min_digits
        remaining = self.remaining_bytes
        if remaining is not None and minimum > remaining:
            self._reserve(minimum)
        self.append(str(int(value)))

    def finish(self) -> str:
        return self._out.getvalue()


def append_value_repr(
    builder: BoundedTextBuilder,
    value: Any,
    *,
    depth: int = 0,
    explicit_host_booleans: bool = False,
) -> None:
    """Append the stable nested representation of one value."""

    # Runtime imports avoid a module cycle while keeping exact type checks.
    from .vm import Cell, Quotation, Word

    if depth > 6:
        builder.append("...")
        return
    if isinstance(value, str):
        builder.append_json_string(value)
        return
    if isinstance(value, bool):
        if explicit_host_booleans:
            builder.append(f"<bool {value!r}>")
        else:
            builder.append_int(1 if value else 0)
        return
    if isinstance(value, int):
        builder.append_int(int(value))
        return
    if isinstance(value, list):
        builder.append("[")
        for index, item in enumerate(value):
            if index:
                builder.append(", ")
            append_value_repr(
                builder,
                item,
                depth=depth + 1,
                explicit_host_booleans=explicit_host_booleans,
            )
        builder.append("]")
        return
    if isinstance(value, dict):
        builder.append("{")
        for index, key in enumerate(sorted(value.keys(), key=lambda item: str(item))):
            if index:
                builder.append(", ")
            if explicit_host_booleans and isinstance(key, bool):
                builder.append_json_string(f"<bool {key!r}>")
            else:
                builder.append_json_string(str(key))
            builder.append(": ")
            append_value_repr(
                builder,
                value.get(key),
                depth=depth + 1,
                explicit_host_booleans=explicit_host_booleans,
            )
        builder.append("}")
        return
    if isinstance(value, Cell):
        builder.append("<cell ")
        append_value_repr(
            builder,
            value.value,
            depth=depth + 1,
            explicit_host_booleans=explicit_host_booleans,
        )
        builder.append(">")
        return
    if isinstance(value, Quotation):
        builder.append("<quote>")
        return
    if isinstance(value, Word):
        builder.append(f"<xt {getattr(value, 'name', '<xt>')}>")
        return
    builder.append(f"<{type(value).__name__}>")


def render_value_repr(
    value: Any,
    *,
    action: str,
    max_bytes: int,
    explicit_host_booleans: bool = False,
) -> str:
    """Return one bounded stable nested representation."""

    builder = BoundedTextBuilder(action=action, max_bytes=max_bytes)
    append_value_repr(
        builder,
        value,
        explicit_host_booleans=explicit_host_booleans,
    )
    return builder.finish()


def render_display_value(value: Any, *, action: str, max_bytes: int) -> str:
    """Return bounded text for the interactive ``.`` display surface.

    Top-level strings stay unquoted, preserving the long-standing Forth-like
    behavior of ``"hello" .``.  Structured values use the same deterministic
    renderer as ``to-str`` so repeated references are charged every time they
    would appear rather than handed to Python's unbounded ``repr`` machinery.
    Host-only booleans remain visibly typed instead of silently looking like the
    portable 0/1 values.
    """

    builder = BoundedTextBuilder(action=action, max_bytes=max_bytes)
    if isinstance(value, str):
        builder.append(value)
    else:
        append_value_repr(builder, value, explicit_host_booleans=True)
    return builder.finish()


__all__ = [
    "BoundedTextBuilder",
    "TextResultBudgetExceeded",
    "append_value_repr",
    "effective_value_text_max_bytes",
    "render_display_value",
    "render_value_repr",
]
