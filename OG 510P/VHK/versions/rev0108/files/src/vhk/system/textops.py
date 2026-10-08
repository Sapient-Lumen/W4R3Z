from __future__ import annotations

import re
from typing import Iterable


def _flags(names: list[str]) -> int:
    out = 0
    for name in names:
        n = name.upper().strip()
        if not n:
            continue
        if n == "IGNORECASE":
            out |= re.IGNORECASE
        elif n == "MULTILINE":
            out |= re.MULTILINE
        elif n == "DOTALL":
            out |= re.DOTALL
        else:
            raise ValueError(f"Unknown regex flag: {name}")
    return out


def regex_replace(text: str, pattern: str, replacement: str, *, flags: list[str] | None = None, count: int = 0) -> str:
    return re.sub(pattern, replacement, text, count=max(0, int(count)), flags=_flags(flags or []))


def trim_text(text: str, *, chars: str | None = None, mode: str = "both") -> str:
    if mode == "both":
        return text.strip(chars)
    if mode == "left":
        return text.lstrip(chars)
    if mode == "right":
        return text.rstrip(chars)
    raise ValueError(f"Unknown trim mode: {mode}")


def split_text(text: str, *, sep: str | None = None, maxsplit: int = -1) -> list[str]:
    return text.split(sep, maxsplit)


def join_text(items: Iterable[object], *, sep: str = "") -> str:
    return str(sep).join(str(x) for x in items)
