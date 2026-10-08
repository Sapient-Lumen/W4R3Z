from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

PromptTokenSpan = tuple[str, int, int]
PromptRow = list[str]


@dataclass(frozen=True)
class PromptTokenContext:
    """Cursor-local command-prompt token state used by completion."""

    spans: tuple[PromptTokenSpan, ...]
    toks: tuple[str, ...]
    tok_i: int
    tok_start: int
    tok_end: int
    tok: str
    quote: str | None
    quote_closed: bool
    tok_inner: str
    tok_norm: str
    cmd: str
    prefix: str
    token_for_completion: int


@dataclass(frozen=True)
class PromptCompletionPlan:
    """Small editor-independent plan for applying command completion."""

    replacement_text: str | None = None
    cursor: int | None = None
    suggestions: tuple[str, ...] = ()
    suggestion_start: int = 0
    suggestion_end: int = 0
    message: str = ""


@dataclass(frozen=True)
class MergedCompletionCandidates:
    """Pure result of merging builtin/path candidates with plugin candidates."""

    candidates: tuple[str, ...]
    fuzzy_candidates: bool = False
    path_candidates: frozenset[str] = frozenset()

    @property
    def path_mode(self) -> bool:
        return bool(self.path_candidates)


def scan_prompt_tokens(s: str) -> list[PromptTokenSpan]:
    """Return ``[(token, start, end), ...]`` using forgiving shell-ish rules.

    This is for completion only, not command execution. It is quote-aware so
    whitespace inside quotes stays inside one token, and it treats a backslash
    outside single quotes as escaping the next character so the escaped character
    cannot accidentally terminate a quote while completion is locating the
    active token.
    """

    text = str(s or "")
    out: list[PromptTokenSpan] = []
    start: int | None = None
    in_single = False
    in_double = False

    i = 0
    while i < len(text):
        ch = text[i]

        if ch == "\\" and not in_single:
            if start is None:
                start = i
            i = i + 2 if (i + 1) < len(text) else i + 1
            continue

        if ch == "'" and not in_double:
            in_single = not in_single
            if start is None:
                start = i
            i += 1
            continue
        if ch == '"' and not in_single:
            in_double = not in_double
            if start is None:
                start = i
            i += 1
            continue

        if (not in_single) and (not in_double) and ch.isspace():
            if start is not None:
                out.append((text[start:i], start, i))
                start = None
            i += 1
            continue

        if start is None and not ch.isspace():
            start = i

        i += 1

    if start is not None:
        out.append((text[start : len(text)], start, len(text)))
    return out


def unescape_prompt_token_body(body: str, quote: str | None = None) -> str:
    """Return the command-parser value of a possibly escaped token body.

    Completion needs the filesystem prefix, not the command-line spelling. The
    renderer double-quotes paths containing ``\\`` or ``"`` and escapes those
    characters, so the next Tab must invert that tiny quoting layer before it
    asks the filesystem for children. Single-quoted bodies are literal.
    """

    raw = str(body or "")
    if quote == "'" or "\\" not in raw:
        return raw

    out: list[str] = []
    i = 0
    while i < len(raw):
        ch = raw[i]
        if ch == "\\" and (i + 1) < len(raw):
            out.append(raw[i + 1])
            i += 2
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def prompt_token_context(text: str, cursor: int) -> PromptTokenContext:
    """Return the token/completion prefix state at ``cursor``.

    The only command-specific rule here is the existing ``helpjump`` behavior:
    after the command word, all remaining text is treated as one jump target so
    headings containing spaces can complete as a single argument.
    """

    raw = str(text or "")
    cur = max(0, min(int(cursor), len(raw)))
    spans = scan_prompt_tokens(raw)
    toks = [t for t, _s, _e in spans]

    tok_i: int | None = None
    tok_start = tok_end = cur
    tok = ""
    for i, (t, start, end) in enumerate(spans):
        if start <= cur <= end:
            tok_i = i
            tok_start, tok_end = int(start), int(end)
            tok = str(t)
            break

    if tok_i is None:
        tok_i = 0
        for _t, _s, end in spans:
            if int(end) < cur:
                tok_i += 1
        tok_start = tok_end = cur
        tok = ""

    quote: str | None = None
    quote_closed = False
    tok_inner = tok
    tok_norm = tok
    if tok.startswith(("'", '"')):
        quote = tok[0]
        rest = tok[1:]
        if rest.endswith(quote):
            quote_closed = True
            rest = rest[:-1]
        tok_inner = unescape_prompt_token_body(rest, quote)
        tok_norm = quote + rest
    else:
        tok_inner = unescape_prompt_token_body(tok, quote)

    cmd = toks[0] if toks else ""
    prefix = tok_norm
    token_for_completion = int(tok_i)

    if cmd == "helpjump" and int(tok_i) >= 1:
        token_for_completion = 1
        if len(spans) >= 2:
            tok_start = int(spans[1][1])
        prefix = raw[tok_start:tok_end]

    return PromptTokenContext(
        spans=tuple(spans),
        toks=tuple(toks),
        tok_i=int(tok_i),
        tok_start=int(tok_start),
        tok_end=int(tok_end),
        tok=str(tok),
        quote=quote,
        quote_closed=bool(quote_closed),
        tok_inner=str(tok_inner),
        tok_norm=str(tok_norm),
        cmd=str(cmd),
        prefix=str(prefix),
        token_for_completion=int(token_for_completion),
    )


def _escape_double_quoted_path(s: str) -> str:
    return str(s).replace("\\", "\\\\").replace('"', '\\"')


def path_needs_completion_quotes(path: str) -> bool:
    """Return whether an unquoted completion would be unsafe for shlex parsing."""

    p = str(path or "")
    return any(ch.isspace() or ch in {'"', "'", "\\"} for ch in p)


def render_path_completion(
    path: str,
    *,
    is_dir: bool,
    at_eol: bool,
    quote: str | None = None,
    close_dirs: bool = False,
) -> str:
    """Render one path completion candidate using the command-bar quote policy."""

    q = quote
    if q == "'" and "'" in str(path):
        # A single quote cannot be escaped inside a POSIX single-quoted token.
        # We replace the whole active token during completion, so it is safe to
        # switch quote style and render a parseable command line.
        q = '"'
    if q is None and path_needs_completion_quotes(path):
        q = '"'

    trail = " " if (bool(at_eol) and (not bool(is_dir))) else ""
    if q is None:
        return str(path) + trail

    body = str(path)
    if q == '"':
        body = _escape_double_quoted_path(body)

    if bool(is_dir):
        return (q + body + q) if bool(close_dirs) else (q + body)
    return q + body + q + trail


def path_completion_candidates(
    unquoted_prefix: str,
    *,
    at_eol: bool,
    quote: str | None = None,
    close_dirs: bool = False,
    cwd: Path | None = None,
) -> list[str]:
    """Return filesystem path completion candidates for the command prompt.

    The function is intentionally small and source-archive friendly: no shell is
    invoked, hidden paths require a leading dot, directories sort before files,
    and candidates are rendered as command-bar insert text rather than stat-rich
    UI rows.
    """

    typed = str(unquoted_prefix or "")
    dirpart, namepart = os.path.split(typed)
    if dirpart != "" and not dirpart.endswith(os.sep):
        dirpart = dirpart + os.sep

    if typed == "~":
        dirpart, namepart = "~" + os.sep, ""

    base = Path(dirpart or ".").expanduser()
    if cwd is not None and not base.is_absolute():
        base = Path(cwd) / base
    try:
        if not base.exists() or not base.is_dir():
            return []
        raw_entries = list(base.iterdir())
    except OSError:
        return []

    show_hidden = namepart.startswith(".")
    matched: list[tuple[int, str, str, bool]] = []
    for child in raw_entries:
        nm = child.name
        if not show_hidden and nm.startswith("."):
            continue
        if not nm.startswith(namepart):
            continue
        try:
            is_dir = child.is_dir()
        except OSError:
            is_dir = False
        suffix = os.sep if is_dir else ""
        cand_path = f"{dirpart}{nm}{suffix}"
        matched.append((0 if is_dir else 1, nm, cand_path, bool(is_dir)))

    # Sort before limiting so a large directory does not return an arbitrary
    # prefix-dependent slice from the filesystem's iteration order.
    matched.sort(key=lambda item: (int(item[0]), str(item[1])))
    max_items = 60 if typed == "" else 200
    return [
        render_path_completion(
            cand_path,
            is_dir=is_dir,
            at_eol=bool(at_eol),
            quote=quote,
            close_dirs=bool(close_dirs),
        )
        for _kind, _nm, cand_path, is_dir in matched[:max_items]
    ]


def overlay_suggestion_rows(
    base_rows: list[PromptRow],
    candidates: list[str],
    extra_candidates: list[str],
    extra_rows: list[PromptRow],
) -> list[PromptRow]:
    """Overlay plugin-provided suggestion rows onto inferred row metadata."""

    if not base_rows or not extra_candidates or not extra_rows:
        return base_rows

    out = [list(r[:4]) + [""] * max(0, 4 - len(r[:4])) for r in base_rows]
    index_by_insert: dict[str, int] = {}
    for i, cand in enumerate(candidates):
        index_by_insert.setdefault(str(cand), int(i))

    for i, cand in enumerate(extra_candidates):
        if i >= len(extra_rows):
            continue
        dst_i = index_by_insert.get(str(cand))
        if dst_i is None or dst_i >= len(out):
            continue
        row = [str(x) for x in list(extra_rows[i])[:4]]
        while len(row) < 4:
            row.append("")
        row[0] = str(candidates[dst_i])
        for j in range(1, 4):
            if row[j] != "":
                out[dst_i][j] = row[j]
    return [r[:4] for r in out]


def merge_completion_candidates(
    *,
    base_candidates: list[str],
    fuzzy_candidates: bool = False,
    path_mode: bool = False,
    extra_candidates: list[str] | None = None,
    extra_mode: int = 0,
) -> MergedCompletionCandidates:
    """Merge builtin/path candidates with Micromax plugin completion results.

    ``extra_mode`` follows the editor plugin contract: ``0`` means ignore, ``1``
    means add missing plugin candidates, and ``2`` means replace builtins.  The
    returned ``path_candidates`` set tracks provenance so plugin-added rows do
    not inherit filesystem metadata merely because the builtin side was doing
    path completion.
    """

    base = [str(c) for c in list(base_candidates or [])]
    extra = [str(c) for c in list(extra_candidates or [])]
    mode = int(extra_mode or 0)

    if mode == 2:
        return MergedCompletionCandidates(
            candidates=tuple(extra),
            fuzzy_candidates=False,
            path_candidates=frozenset(),
        )

    out = list(base)
    path_set = set(base) if bool(path_mode) else set()

    if mode == 1 and extra:
        seen = set(out)
        for cand in extra:
            if cand in seen:
                continue
            seen.add(cand)
            out.append(cand)

    return MergedCompletionCandidates(
        candidates=tuple(out),
        fuzzy_candidates=bool(fuzzy_candidates),
        path_candidates=frozenset(path_set),
    )


def should_prefer_exact_common_candidate(common: str, raw: list[str], *, cmd: str = "") -> bool:
    """Return whether a common prefix should snap to its exact candidate.

    This preserves the command-prompt heuristic that ``he`` should complete to
    ``help `` even though helper commands like ``helppick`` also match, without
    making broader command families like ``toggle`` snap too aggressively.
    """

    common_s = str(common or "")
    if not common_s or common_s not in raw:
        return False
    others = [str(r) for r in raw if str(r) != common_s]
    if not others:
        return False

    if common_s.endswith("help"):
        return True
    if str(cmd or "") == "helpjump" and all(r.startswith(common_s + " ") for r in others):
        return True

    def is_pick_variant(value: str) -> bool:
        if not value.startswith(common_s):
            return False
        suffix = value[len(common_s) :]
        return suffix.startswith("pick") or suffix.startswith("-pick") or suffix.startswith("_pick")

    return all(is_pick_variant(r) for r in others)


def raw_completion_insert(candidate: str) -> str:
    """Return the visible/debug spelling of a completion insert candidate."""

    c = str(candidate)
    return c[:-1] if c.endswith(" ") else c


def plan_prompt_completion_application(
    *,
    text: str,
    token_start: int,
    token_end: int,
    prefix: str,
    candidates: list[str],
    fuzzy_candidates: bool = False,
    cmd: str = "",
) -> PromptCompletionPlan | None:
    """Plan the final command-prompt completion edit/session.

    The editor supplies candidate discovery and row decoration; this pure helper
    owns the risky application policy: unique insertion, exact-common snapping,
    common-prefix insertion, and suggestion-session bounds.
    """

    if not candidates:
        return None

    prompt_text = str(text or "")
    start = max(0, min(int(token_start), len(prompt_text)))
    end = max(start, min(int(token_end), len(prompt_text)))
    inserts = [str(c) for c in candidates]
    raw = [raw_completion_insert(c) for c in inserts]

    if len(inserts) == 1:
        insert = inserts[0]
        new_text = prompt_text[:start] + insert + prompt_text[end:]
        message = "fuzzy: " + raw[0] if bool(fuzzy_candidates) else ""
        return PromptCompletionPlan(
            replacement_text=new_text,
            cursor=start + len(insert),
            message=message,
        )

    import os as _os

    common = _os.path.commonprefix(raw) if raw and (not bool(fuzzy_candidates)) else ""
    if common and len(common) > len(str(prefix or "")):
        if should_prefer_exact_common_candidate(common, raw, cmd=cmd):
            for insert in inserts:
                if raw_completion_insert(insert) == common:
                    new_text = prompt_text[:start] + insert + prompt_text[end:]
                    message = "fuzzy: " + common if bool(fuzzy_candidates) else ""
                    return PromptCompletionPlan(
                        replacement_text=new_text,
                        cursor=start + len(insert),
                        message=message,
                    )

        new_text = prompt_text[:start] + common + prompt_text[end:]
        return PromptCompletionPlan(
            replacement_text=new_text,
            cursor=start + len(common),
            suggestions=tuple(inserts),
            suggestion_start=start,
            suggestion_end=start + len(common),
            message="matches: " + ", ".join(raw),
        )

    return PromptCompletionPlan(
        suggestions=tuple(inserts),
        suggestion_start=start,
        suggestion_end=end,
        message=("fuzzy matches: " if bool(fuzzy_candidates) else "matches: ") + ", ".join(raw),
    )
