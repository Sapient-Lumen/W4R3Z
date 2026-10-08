from __future__ import annotations

"""Side-effect-free replace planning for editor replace-family commands.

The editor's bulk-edit trust boundary should be able to answer "what would
change?" before a buffer mutates.  This module keeps that planning logic small,
plain, and reusable by commands, hostcalls, and future prompt previews.
"""

from dataclasses import dataclass
import re

from micromax.regex_tools import convert_replacement_template, format_replacement_template_error


@dataclass(frozen=True)
class ReplaceMatch:
    """One planned replacement witness."""

    start: int
    end: int
    line: int
    col: int
    end_line: int
    end_col: int
    old: str
    new: str

    def row(self) -> list[object]:
        return [int(self.line), int(self.col), int(self.end_line), int(self.end_col), self.old, self.new]


@dataclass(frozen=True)
class ReplacePlan:
    """Plain-data result for a replace request.

    ``error`` is intentionally message text *without* a command prefix.  Callers
    decide whether the prefix is ``replace``, ``replaceall``, ``qreplace``, or a
    preview/hostcall surface.
    """

    ok: bool
    error: str = ""
    search: str = ""
    value: str = ""
    replace_all: bool = False
    literal: bool = False
    case_sensitive: bool = True
    start_index: int = 0
    count: int = 0
    matches: tuple[ReplaceMatch, ...] = ()
    new_text: str | None = None

    @property
    def changed(self) -> bool:
        return self.ok and self.new_text is not None and self.count > 0

    def rows(self) -> list[list[object]]:
        """Return compact sample rows for scripting surfaces."""

        return [m.row() for m in self.matches]

    def summary_row(self) -> list[object]:
        """Return a stable, script-friendly summary row.

        Shape: ``[ok count replace_all literal case_sensitive start_index error rows]``.
        Line/column coordinates in sample rows are zero-based, matching editor
        hostcall conventions.
        """

        return [
            1 if self.ok else 0,
            int(self.count),
            1 if self.replace_all else 0,
            1 if self.literal else 0,
            1 if self.case_sensitive else 0,
            int(self.start_index),
            str(self.error),
            self.rows(),
        ]


def _line_col(text: str, idx: int) -> tuple[int, int]:
    idx2 = max(0, min(int(idx), len(text)))
    line = text.count("\n", 0, idx2)
    last_nl = text.rfind("\n", 0, idx2)
    col = idx2 if last_nl < 0 else idx2 - last_nl - 1
    return int(line), int(col)


def _match(text: str, start: int, end: int, replacement: str) -> ReplaceMatch:
    line, col = _line_col(text, start)
    end_line, end_col = _line_col(text, end)
    return ReplaceMatch(
        start=int(start),
        end=int(end),
        line=line,
        col=col,
        end_line=end_line,
        end_col=end_col,
        old=text[start:end],
        new=str(replacement),
    )


def _apply(text: str, matches: list[ReplaceMatch]) -> str:
    pieces: list[str] = []
    pos = 0
    for m in matches:
        pieces.append(text[pos : m.start])
        pieces.append(m.new)
        pos = m.end
    pieces.append(text[pos:])
    return "".join(pieces)


def _template_error(exc: BaseException) -> str:
    return f"invalid replacement: {format_replacement_template_error(exc)}"


def plan_replace(
    text: str,
    search: str,
    value: str,
    *,
    start_index: int = 0,
    replace_all: bool = False,
    literal: bool = False,
    case_sensitive: bool = True,
    sample_limit: int = 3,
) -> ReplacePlan:
    """Return a side-effect-free replacement plan.

    The behavior mirrors the editor's existing replace/replaceall contract:
    empty searches are rejected; regex replacement templates are validated even
    when there are no matches; and zero-width regex matches are rejected before
    any mutation can occur.
    """

    text = str(text)
    search = str(search)
    value = str(value)
    start = 0 if replace_all else max(0, min(int(start_index), len(text)))
    samples = max(0, int(sample_limit))

    def fail(message: str) -> ReplacePlan:
        return ReplacePlan(
            ok=False,
            error=message,
            search=search,
            value=value,
            replace_all=bool(replace_all),
            literal=bool(literal),
            case_sensitive=bool(case_sensitive),
            start_index=start,
        )

    if search == "":
        return fail("empty search")

    matches: list[ReplaceMatch] = []

    if literal:
        haystack = text if case_sensitive else text.lower()
        needle = search if case_sensitive else search.lower()
        pos = start
        while True:
            idx = haystack.find(needle, pos)
            if idx < 0:
                break
            matches.append(_match(text, idx, idx + len(search), value))
            if not replace_all:
                break
            pos = idx + max(1, len(search))
    else:
        flags = 0 if case_sensitive else re.IGNORECASE
        try:
            pat = re.compile(search, flags)
        except re.error as exc:
            return fail(f"invalid regex: {exc}")
        repl_py = convert_replacement_template(value)
        for found in pat.finditer(text, pos=start):
            if found.start() == found.end():
                return fail("zero-width matches are not supported")
            try:
                replacement = found.expand(repl_py)
            except (re.error, IndexError) as exc:
                return fail(_template_error(exc))
            matches.append(_match(text, found.start(), found.end(), replacement))
            if not replace_all:
                break
        if not matches:
            try:
                pat.subn(repl_py, "", count=0)
            except (re.error, IndexError) as exc:
                return fail(_template_error(exc))

    if not matches:
        return fail("not found")

    new_text = _apply(text, matches)
    return ReplacePlan(
        ok=True,
        search=search,
        value=value,
        replace_all=bool(replace_all),
        literal=bool(literal),
        case_sensitive=bool(case_sensitive),
        start_index=start,
        count=len(matches),
        matches=tuple(matches[:samples]),
        new_text=new_text,
    )
