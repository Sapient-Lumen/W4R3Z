from __future__ import annotations

import shlex
from dataclasses import dataclass


class CommandLineParseError(ValueError):
    """A user-facing command-bar parse failure.

    Keep this tiny wrapper around ``shlex`` errors so callers can distinguish
    malformed command text from command dispatch/runtime failures without
    depending on the exact exception type raised by the parser implementation.
    """


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

    try:
        parts = shlex.split(s, posix=True)
    except ValueError as e:
        raise CommandLineParseError(str(e)) from e
    if not parts:
        return None
    return CommandLine(name=parts[0], args=parts[1:])
