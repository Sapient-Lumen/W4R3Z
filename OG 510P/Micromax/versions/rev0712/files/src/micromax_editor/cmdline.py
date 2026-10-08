from __future__ import annotations

import shlex
from dataclasses import dataclass


@dataclass(frozen=True)
class CommandLine:
    name: str
    args: list[str]


def parse_cmdline(s: str) -> CommandLine | None:
    """Parse a command-bar line.

    In micro, the command bar parser uses shell-like quoting rules
    (single/double quotes and backslash escaping). We use Python's `shlex` to
    get similar behavior.

    Returns None if the line is empty or only whitespace.
    """

    s = s.strip()
    if not s:
        return None

    parts = shlex.split(s, posix=True)
    if not parts:
        return None
    return CommandLine(name=parts[0], args=parts[1:])
