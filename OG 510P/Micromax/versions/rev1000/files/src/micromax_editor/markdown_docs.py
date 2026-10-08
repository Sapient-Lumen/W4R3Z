from __future__ import annotations

from dataclasses import dataclass
import re
import string
from urllib.parse import unquote

# --- Markdown helpers (docs/help browser) ---

def md_norm_ref_id(s: str) -> str:
    """Normalize a markdown reference-id (case-insensitive, collapse whitespace)."""

    try:
        return re.sub(r"\s+", " ", str(s or "").strip()).casefold()
    except Exception:
        return ""


def md_link_label_has_text(s: str) -> bool:
    """Return True when a tiny markdown link label has visible text.

    CommonMark requires link labels to contain at least one non-whitespace
    character. The docs browser keeps that rule deliberately small and shared so
    empty or space-only labels do not become live inline/reference/shortcut
    links just because a regex-shaped destination happened to follow.
    """

    text = str(s or "")
    return any(not ch.isspace() for ch in text)


def md_leading_spaces_upto3(line: str) -> int | None:
    """Return the count of leading markdown block-indent spaces (0..3).

    The tiny docs browser intentionally follows CommonMark's "up to three
    spaces" rule for block starters. Tabs do not count here, and four leading
    spaces should be left as code-block-ish prose rather than parsed as
    headings or reference definitions.
    """

    s = str(line or "")
    col = 0
    while col < len(s) and s[col] == " " and col < 4:
        col += 1
    if col < len(s) and s[col] == "\t":
        return None
    if col >= 4:
        return None
    return col


_MD_BACKSLASH_UNESCAPE_CHARS = set(string.punctuation) | {" ", "\t"}


def md_backslash_unescape(text: str) -> str:
    r"""Undo a tiny markdown-safe subset of backslash escapes.

    The docs browser only needs a small, inspectable policy here: punctuation
    escapes behave like markdown escapes, and we also treat ``\ `` / ``\t`` as
    useful local-doc conveniences for path-like destinations. Unknown escapes
    stay literal.
    """

    s = str(text or "")
    if not s:
        return ""

    out: list[str] = []
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == "\\" and i + 1 < len(s):
            nxt = s[i + 1]
            if nxt in _MD_BACKSLASH_UNESCAPE_CHARS:
                out.append(nxt)
                i += 2
                continue
        out.append(ch)
        i += 1
    return ''.join(out)


def _md_rest_is_title(rest: str) -> bool:
    """Return True when *rest* is empty or a tiny markdown link title."""

    r = str(rest or "").strip()
    if not r:
        return True

    opener = r[:1]
    if opener in ('"', "'"):
        i = 1
        while i < len(r):
            ch = r[i]
            if ch == "\\":
                i += 2
                continue
            if ch == opener:
                return not r[i + 1 :].strip()
            i += 1
        return False

    if opener == '(':
        span = md_balanced_span(r, 0, opener='(', closer=')')
        if span is None:
            return False
        _, end = span
        return not r[end:].strip()

    return False


def _md_inline_rest_closes_on_line(rest: str) -> bool:
    """Return True when *rest* contains a tiny inline-link close on one line.

    ``rest`` is the content after a parsed destination. We accept either an
    immediate ``)`` (possibly after spaces/tabs) or a tiny markdown title
    followed by ``)``. Any trailing text after the closer is ignored so callers
    can keep scanning the rest of the source line normally.
    """

    r = str(rest or "")
    i = 0
    while i < len(r):
        ch = r[i]
        if ch == "\\":
            i += 2
            continue
        if ch == ')':
            return _md_rest_is_title(r[:i])
        i += 1
    return False


def md_inline_link_target_multiline(after_open: str, next_line: str = "", next_next_line: str = "") -> str:
    """Extract a tiny wrapped inline-link destination.

    CommonMark allows inline-link pieces to be separated by spaces/tabs and up
    to one line ending. Micromax keeps this intentionally small and shared:
    support destination-on-next-line and title/close-on-next-line shells around
    the existing destination parser without growing a full multiline inline
    parser.
    """

    first = str(after_open or "").lstrip(" \t")
    cont1 = str(next_line or "")
    cont2 = str(next_next_line or "")
    if first:
        dest_src = first
    else:
        dest_src = cont1.lstrip(" \t")
        cont1 = cont2
        cont2 = ""
        if not dest_src:
            return ""

    parsed = _md_link_target_prefix(dest_src)
    if parsed is None:
        return ""
    dest, rest, used_angle_brackets = parsed
    if not dest or not _md_link_rest_has_required_separator(rest, used_angle_brackets=used_angle_brackets):
        return ""

    if _md_inline_rest_closes_on_line(rest):
        return dest
    if rest.strip(" \t"):
        if _md_rest_is_title(rest):
            return dest if str(cont1 or "").lstrip(" \t").startswith(')') else ""
        return ""

    tail1 = str(cont1 or "").lstrip(" \t")
    if not tail1:
        return ""
    if _md_inline_rest_closes_on_line(tail1):
        return dest
    if _md_rest_is_title(tail1):
        return dest if str(cont2 or "").lstrip(" \t").startswith(')') else ""
    return ""


def md_docs_continuation_line(
    lines: list[object],
    idx: int,
    *,
    fence_flags: list[bool] | None = None,
    html_block_flags: list[bool] | None = None,
    comment_spans: list[list[tuple[int, int]]] | None = None,
) -> str:
    """Return one docs/help continuation line, or ``''`` when it is inert.

    This keeps small multiline markdown affordances aligned across editor
    actions, pickers, and the TUI: fenced/raw-HTML/comment-hidden lines and
    blank lines do not participate as wrapped link/reference continuations.
    """

    xs = list(lines or [])
    j = int(idx)
    if j < 0 or j >= len(xs):
        return ""
    if fence_flags and j < len(fence_flags) and fence_flags[j]:
        return ""
    if html_block_flags and j < len(html_block_flags) and html_block_flags[j]:
        return ""
    s2 = str(xs[j])
    stripped = s2.lstrip(" \t")
    if not stripped:
        return ""
    if comment_spans:
        spans2 = comment_spans[j] if j < len(comment_spans) else []
        col0 = len(s2) - len(stripped)
        if md_span_contains(spans2, int(col0), int(col0) + 1):
            return ""
    return s2


def _md_link_target_prefix(text: str) -> tuple[str, str, bool] | None:
    """Parse one tiny markdown link destination prefix.

    Returns ``(destination, rest, used_angle_brackets)`` when ``text`` starts
    with a destination, leaving any trailing title/whitespace in ``rest`` for
    the caller to decide about. This is shared by inline-link parsing and
    multi-line reference-link definitions so the docs browser does not grow
    separate destination regexes.
    """

    s = str(text or "")
    if not s:
        return None

    if s.startswith('<'):
        i = 1
        while i < len(s):
            ch = s[i]
            if ch == "\\":
                i += 2
                continue
            if ch == '>':
                dest = s[1:i].strip()
                if dest:
                    return (md_backslash_unescape(dest), s[i + 1 :], True)
                return None
            if ch in "\r\n<":
                return None
            i += 1
        return None

    i = 0
    depth = 0
    while i < len(s):
        ch = s[i]
        if ch == "\\":
            if i + 1 >= len(s):
                break
            i += 2
            continue
        if ch in "\r\n":
            break
        if ch.isspace():
            break
        if ord(ch) < 32:
            return None
        if ch == '(':
            depth += 1
        elif ch == ')':
            if depth == 0:
                break
            depth -= 1
        i += 1

    raw_dest = s[:i]
    if not raw_dest or depth != 0:
        return None
    return (md_backslash_unescape(raw_dest).strip(), s[i:], False)


def _md_link_rest_has_required_separator(rest: str, *, used_angle_brackets: bool) -> bool:
    """Return True when link-destination trailing text starts legally.

    Angle-bracket destinations need whitespace before an optional title;
    immediate ``)`` is still fine. Bare destinations do not need a separate
    check here because the tiny destination parser already stops before the
    whitespace that would separate a following title.
    """

    r = str(rest or "")
    if not r or not used_angle_brackets:
        return True
    return r[:1].isspace() or r.startswith(')')


def md_reference_def_target_info(after_colon: str, next_line: str = "", next_next_line: str = "") -> tuple[str, int]:
    """Extract a tiny markdown reference-definition destination plus line usage.

    Returns ``(target, continuation_lines_used)`` where the second value is the
    number of following physical lines consumed by the tiny shared parser:

    - ``0`` when the definition stays on the starter line
    - ``1`` when the destination or title comes from ``next_line``
    - ``2`` when both a wrapped destination and a wrapped title are used

    CommonMark allows up to one line ending after the colon and after the
    destination inside reference definitions. Micromax keeps that support
    intentionally small and shared: the destination parser is reused, while the
    surrounding multiline logic stays conservative and inspectable.
    """

    first = str(after_colon or "").lstrip(" \t")
    used_lines = 0
    if first:
        dest_src = first
        peek_title = str(next_line or "")
    else:
        dest_src = str(next_line or "").lstrip(" \t")
        if not dest_src:
            return ("", 0)
        used_lines = 1
        peek_title = str(next_next_line or "")

    parsed = _md_link_target_prefix(dest_src)
    if parsed is None:
        return ("", 0)
    dest, rest, used_angle_brackets = parsed
    if not dest or not _md_link_rest_has_required_separator(rest, used_angle_brackets=used_angle_brackets):
        return ("", 0)

    if rest.strip(" \t"):
        return ((dest, used_lines) if _md_rest_is_title(rest) else ("", 0))

    title_line = str(peek_title or "").lstrip(" \t")
    if title_line[:1] in ('"', "'", '('):
        return ((dest, used_lines + 1) if _md_rest_is_title(title_line) else ("", 0))

    return (dest, used_lines)


def md_reference_def_target(after_colon: str, next_line: str = "", next_next_line: str = "") -> str:
    """Extract a tiny markdown reference-definition destination."""

    return md_reference_def_target_info(after_colon, next_line, next_next_line)[0]


def md_inline_link_target(inner: str) -> str:
    """Extract and *validate* a tiny inline-link destination.

    Supports the docs-browser cases that are awkward with ``split()`` alone:
      - balanced parentheses in bare destinations
      - backslash escapes inside destinations/titles
      - optional quoted or parenthesized titles

    The policy stays intentionally conservative: malformed trailing content
    returns ``''`` so callers can fall back to other markdown forms.
    """

    s = str(inner or "").strip()
    if not s:
        return ""

    parsed = _md_link_target_prefix(s)
    if parsed is None:
        return ""
    dest, rest, used_angle_brackets = parsed
    if not dest or not _md_link_rest_has_required_separator(rest, used_angle_brackets=used_angle_brackets) or not _md_rest_is_title(rest):
        return ""
    return dest

_BACKTICK_RUN_RE = re.compile(r"(?<!`)(?P<ticks>`+)(?!`)")
_FENCE_OPEN_RE = re.compile(r"^[ ]{0,3}(?P<fence>`{3,}|~{3,})(?P<rest>.*)$")
_SETEXT_UNDERLINE_RE = re.compile(r"^[ ]{0,3}(?P<run>=+|-{2,})[ \\t]*$")


_MD_HTML_BLOCK_TAGS = {
    "address", "article", "aside", "base", "basefont", "blockquote", "body",
    "caption", "center", "col", "colgroup", "dd", "details", "dialog",
    "dir", "div", "dl", "dt", "fieldset", "figcaption", "figure",
    "footer", "form", "frame", "frameset", "h1", "h2", "h3", "h4",
    "h5", "h6", "head", "header", "hr", "html", "iframe", "legend",
    "li", "link", "main", "menu", "menuitem", "meta", "nav", "noframes",
    "ol", "optgroup", "option", "p", "param", "search", "section",
    "source", "summary", "table", "tbody", "td", "tfoot", "th", "thead",
    "title", "tr", "track", "ul",
}


_MD_HTML_BLOCK_TYPE1_RE = re.compile(
    r"^[ ]{0,3}<(?P<tag>script|pre|style|textarea)(?=[\t />]|$)",
    flags=re.IGNORECASE,
)
_MD_HTML_BLOCK_TYPE3_RE = re.compile(r"^[ ]{0,3}<\?")
_MD_HTML_BLOCK_TYPE4_RE = re.compile(r"^[ ]{0,3}<![A-Z]")
_MD_HTML_BLOCK_TYPE5_RE = re.compile(r"^[ ]{0,3}<!\[CDATA\[")
_MD_HTML_BLOCK_TYPE6_RE = re.compile(
    rf"^[ ]{{0,3}}</?(?:{'|'.join(sorted(re.escape(t) for t in _MD_HTML_BLOCK_TAGS))})(?=[\t />]|$)",
    flags=re.IGNORECASE,
)


_MD_HTML_TYPE7_EXCLUDED = {"pre", "script", "style", "textarea"}


def md_backslash_escaped(s: str, idx: int) -> bool:
    """Return True when the character at *idx* is escaped by odd backslashes.

    This tiny helper is shared by docs-browser scanners so literal markdown like
    ``\\[example]`` or ``\\<https://example.invalid>`` stays prose instead of
    turning into a live link/footnote/autolink.
    """

    text = str(s or "")
    i = int(idx)
    if i <= 0 or i > len(text):
        return False
    n = 0
    j = i - 1
    while j >= 0 and text[j] == "\\":
        n += 1
        j -= 1
    return (n % 2) == 1


def md_html_comment_spans(line: str, *, in_comment: bool = False) -> tuple[list[tuple[int, int]], bool]:
    """Return tiny raw-HTML comment spans for one source line.

    The policy is intentionally small and shared across docs/help surfaces:
      - recognizes HTML comment open/close markers ``<!--`` / ``-->``
      - supports multi-line comments via ``in_comment`` carry state
      - returns spans covering the raw-comment text on this line

    This is a precedence helper, not a full HTML tokenizer. It keeps literal
    markdown examples inside HTML comments from leaking back into the live docs
    browser as links, refs, or footnotes.
    """

    s = str(line or "")
    if not s:
        return ([], bool(in_comment))

    spans: list[tuple[int, int]] = []
    i = 0
    inside = bool(in_comment)
    n = len(s)
    while i < n:
        if inside:
            j = s.find('-->', i)
            if j < 0:
                spans.append((i, n))
                return (spans, True)
            spans.append((i, j + 3))
            i = j + 3
            inside = False
            continue
        j = s.find('<!--', i)
        if j < 0:
            break
        k = s.find('-->', j + 4)
        if k < 0:
            spans.append((j, n))
            return (spans, True)
        spans.append((j, k + 3))
        i = k + 3
    return (spans, inside)


def md_html_comment_line_spans(lines: list[object]) -> list[list[tuple[int, int]]]:
    """Return per-line raw-HTML comment spans for a docs/help buffer."""

    xs = [str(x) for x in (lines or [])]
    out: list[list[tuple[int, int]]] = []
    inside = False
    for s in xs:
        spans, inside = md_html_comment_spans(s, in_comment=inside)
        out.append(spans)
    return out


def _md_inline_code_parts(line: str) -> list[tuple[int, int, int, int, int, int]]:
    """Return tiny inline-code opener/body/closer spans for one line.

    Returned tuples are ``(open_a, open_b, body_a, body_b, close_a, close_b)``.
    The policy intentionally matches :func:`md_inline_code_spans`: equal-length
    backtick delimiters only, longer runs allowed, fenced-code openers ignored,
    and unmatched/escaped runs skipped.
    """

    s = str(line or "")
    if not s:
        return []
    if re.match(r"^\s*`{3,}", s):
        return []

    runs = list(_BACKTICK_RUN_RE.finditer(s))
    if not runs:
        return []

    out: list[tuple[int, int, int, int, int, int]] = []
    i = 0
    while i < len(runs):
        m = runs[i]
        open_a = int(m.start('ticks'))
        open_b = int(m.end('ticks'))
        n = len(str(m.group('ticks') or ''))
        if md_backslash_escaped(s, open_a):
            i += 1
            continue
        j = i + 1
        matched = False
        while j < len(runs):
            m2 = runs[j]
            if len(str(m2.group('ticks') or '')) != n:
                j += 1
                continue
            close_a = int(m2.start('ticks'))
            close_b = int(m2.end('ticks'))
            if close_a > open_b:
                out.append((open_a, open_b, open_b, close_a, close_a, close_b))
                i = j + 1
                matched = True
                break
            j += 1
        if not matched:
            i += 1
    return out


def md_inline_code_spans(line: str) -> list[tuple[int, int]]:
    """Return spans for tiny inline markdown code in a docs/help line.

    Policy is intentionally small but useful for docs-browser precedence:
      - recognizes inline code spans with equal-length backtick delimiters
      - supports longer delimiters so literal backticks can appear inside code
      - returns spans for the *inside* text (excluding the backticks)
      - ignores fenced code block markers (```...).

    Spans are ``(start, end)`` indices into ``line``.
    """

    return [(int(body_a), int(body_b)) for _oa, _ob, body_a, body_b, _ca, _cb in _md_inline_code_parts(line)]



def md_inline_code_delimiter_spans(line: str) -> list[tuple[int, int]]:
    """Return backtick-delimiter spans for tiny inline markdown code.

    This stays intentionally tiny and shared-substrate-first. It reuses the same
    equal-length backtick scan as :func:`md_inline_code_spans` so docs/help
    source view can give visible code-span delimiters a small cue without
    inventing another parser path.

    Returned spans cover only the opening/closing backtick delimiter runs, not
    the code body text itself.
    """

    out: list[tuple[int, int]] = []
    for open_a, open_b, _body_a, _body_b, close_a, close_b in _md_inline_code_parts(line):
        if int(open_b) > int(open_a):
            out.append((int(open_a), int(open_b)))
        if int(close_b) > int(close_a):
            out.append((int(close_a), int(close_b)))
    out.sort()
    return out


def md_inline_code_matches(line: str) -> list[MdCodeMatch]:
    """Return tiny docs/help inline-code matches for one source line.

    This keeps code-span inspection on the same tiny shared substrate as the
    existing precedence/style helpers: equal-length backtick delimiters only,
    no richer markdown AST, and just enough structured metadata for shared
    docs-cues snapshots and future UIs/LLMs.
    """

    s = str(line or "")
    if not s:
        return []
    out: list[MdCodeMatch] = []
    for open_a, open_b, body_a, body_b, close_a, close_b in _md_inline_code_parts(s):
        start = int(open_a)
        end = int(close_b)
        delimiter_length = max(0, int(open_b) - int(open_a))
        out.append(
            MdCodeMatch(
                kind='code',
                start=start,
                end=end,
                body_start=int(body_a),
                body_end=int(body_b),
                delimiter_length=int(delimiter_length),
                text=s[int(body_a):int(body_b)],
            )
        )
    return out


def md_raw_html_tag_matches(
    line: str,
    *,
    masked_spans: list[tuple[int, int]] | None = None,
) -> list[MdLiteralTokenMatch]:
    """Return tiny docs/help inline raw-HTML tag matches for one line.

    This reuses the same small shared raw-HTML helper the docs browser already
    trusts for precedence and dimming, but packages the visible tokens as
    structured matches so shared docs-cues snapshots and future UIs/LLMs do not
    need to rescan dim spans to learn what literal source is on screen.
    Supported autolinks stay out of this helper; they already flow through the
    ordinary shared link metadata path.
    """

    from micromax_editor.tui import md_raw_html_tag_token_spans

    s = str(line or "")
    if not s:
        return []
    out: list[MdLiteralTokenMatch] = []
    for a, b in md_raw_html_tag_token_spans(s, masked_spans=masked_spans):
        start = int(a)
        end = int(b)
        token = s[start:end]
        detail = ''
        m = re.match(r"</?\??([A-Za-z][A-Za-z0-9:-]*)", token)
        if m is not None:
            detail = str(m.group(1)).casefold()
        out.append(
            MdLiteralTokenMatch(
                kind='raw-html-tag',
                start=start,
                end=end,
                text=token,
                detail=detail,
            )
        )
    return out


def md_escaped_markdown_matches(
    line: str,
    *,
    masked_spans: list[tuple[int, int]] | None = None,
) -> list[MdLiteralTokenMatch]:
    r"""Return tiny docs/help escaped-markdown token matches for one line.

    This reuses the same tiny escape-pair helper the docs/help TUI already uses
    for dim source cues, but packages the visible escape pairs as structured
    matches so shared docs-cues snapshots can report which literal markdown
    punctuation was escaped on screen.
    """

    from micromax_editor.tui import md_escaped_markdown_token_spans

    s = str(line or "")
    if not s:
        return []
    out: list[MdLiteralTokenMatch] = []
    for a, b in md_escaped_markdown_token_spans(s, masked_spans=masked_spans):
        start = int(a)
        end = int(b)
        token = s[start:end]
        detail = token[1:] if len(token) >= 2 else ''
        out.append(
            MdLiteralTokenMatch(
                kind='escaped-markdown',
                start=start,
                end=end,
                text=token,
                detail=detail,
            )
        )
    return out


def md_inline_html_tag_spans(line: str, *, masked_spans: list[tuple[int, int]] | None = None) -> list[tuple[int, int]]:
    """Return tiny inline raw-HTML/autolink spans for one source line.

    The policy is intentionally small and precedence-oriented, not a full HTML
    tokenizer. It exists so docs/help link detection can avoid regex-shaped false
    positives in CommonMark-style cases where HTML tags or autolinks bind tighter
    than link grouping, e.g. ``[foo <bar attr="](baz)">``.

    Recognized forms:
      - autolinks: ``<https://...>`` / ``<mailto:...>``
      - permissive raw tags starting ``<tag ...>``, ``</tag>``, ``<?...>``

    Spans are ``(start, end)`` indices into ``line``. Callers may pass
    ``masked_spans`` (inline code, HTML comments, etc.) so already-inert regions
    stay inert here too.
    """

    s = str(line or "")
    if not s:
        return []

    masks = [(int(a), int(b)) for a, b in (masked_spans or [])]
    out: list[tuple[int, int]] = []
    i = 0
    n = len(s)
    while i < n:
        if s[i] != '<' or md_backslash_escaped(s, i) or md_span_contains(masks, i, i + 1):
            i += 1
            continue

        m = re.match(r"<(?P<url>(?:https?://|mailto:)[^ >]+)>", s[i:])
        if m is not None:
            end = i + int(m.end())
            if not md_span_contains(masks, i, end):
                out.append((i, end))
                i = end
                continue

        j = i + 1
        if j >= n:
            break

        ch = s[j]
        if ch == '/':
            j += 1
            if j >= n or not s[j].isalpha():
                i += 1
                continue
        elif ch == '?':
            pass
        elif not ch.isalpha():
            i += 1
            continue

        end = s.find('>', j + 1)
        if end < 0:
            i += 1
            continue
        end += 1
        if md_span_contains(masks, i, end):
            i += 1
            continue
        out.append((i, end))
        i = end

    return out


def md_html_type7_tag_line(line: str) -> bool:
    """Return True for a tiny complete-tag line suitable for type-7-ish blocks.

    This is intentionally conservative and inspectable. It recognizes lines that
    are *just* one complete open/close tag (optionally with attributes and up to
    three leading spaces), excluding the raw-block tags already handled by the
    tighter type-1 helper (``<pre>``, ``<script>``, ``<style>``,
    ``<textarea>``) and excluding comments/declarations/processing instructions.

    The goal is not full HTML validation; it is to catch the CommonMark/GFM-ish
    docs cases that matter to Micromax, such as ``<widget-box data-x="1">`` or
    ``</widget-box>`` lines that should keep subsequent literal markdown inert
    until a blank line.
    """

    s = str(line or "")
    if not s:
        return False
    if re.match(r"^[ ]{4,}", s):
        return False

    rest = re.sub(r"^[ ]{0,3}", "", s).rstrip()
    if len(rest) < 3 or rest[0] != '<' or rest[-1] != '>':
        return False
    if rest.startswith(('<!--', '<?', '<!')):
        return False

    i = 1
    closing = False
    if rest[1:2] == '/':
        closing = True
        i = 2

    if i >= len(rest) - 1 or not rest[i].isalpha():
        return False

    j = i + 1
    while j < len(rest):
        ch = rest[j]
        if ch.isalnum() or ch in {'-', ':'}:
            j += 1
            continue
        break

    name = rest[i:j].casefold()
    if not name or name in _MD_HTML_TYPE7_EXCLUDED:
        return False

    nxt = rest[j:j + 1]
    if nxt and (not nxt.isspace()) and nxt not in {'>', '/'}:
        return False

    if closing:
        return not rest[j:-1].strip()

    quote = ''
    k = j
    while k < len(rest):
        ch = rest[k]
        if quote:
            if ch == quote:
                quote = ''
            k += 1
            continue
        if ch in {'"', "'"}:
            quote = ch
            k += 1
            continue
        if ch == '<':
            return False
        if ch == '>':
            return k == len(rest) - 1
        k += 1
    return False


def md_html_block_line_flags(lines: list[object]) -> list[bool]:
    """Return zero-based per-line flags for tiny raw-HTML blocks.

    Policy is intentionally small and shared across docs/help surfaces. It aims
    at the CommonMark/GFM HTML block cases that matter for an editor-centric
    docs browser without becoming a full HTML parser:
      - type 1: ``<script|pre|style|textarea ...>`` through a matching end tag
      - type 3: processing instructions ``<? ... ?>``
      - type 4: declarations ``<!A...>`` through ``>``
      - type 5: CDATA ``<![CDATA[ ... ]]>``
      - type 6-ish: common block tags like ``<div>``/``<table>`` or closing
        forms like ``</div>`` through the next blank line
      - type 7-ish: complete generic tag-only lines like ``<widget-box>`` or
        ``</widget-box>`` through the next blank line, but only when they do
        not interrupt a paragraph

    HTML comments remain handled by :func:`md_html_comment_line_spans` so inline
    comment spans can coexist with visible prose on the same source line.
    """

    xs = [str(x) for x in (lines or [])]
    if not xs:
        return []

    flags: list[bool] = [False] * len(xs)
    mode = ""
    end_tag = ""

    for i, s in enumerate(xs):
        line = str(s)
        if mode == "blank":
            if not line.strip():
                mode = ""
                continue
            flags[i] = True
            continue

        if mode == "type1":
            flags[i] = True
            if re.search(rf"</{re.escape(end_tag)}(?=[\t />]|$)", line, flags=re.IGNORECASE):
                mode = ""
                end_tag = ""
            continue

        if mode == "type3":
            flags[i] = True
            if "?>" in line:
                mode = ""
            continue

        if mode == "type4":
            flags[i] = True
            if ">" in line:
                mode = ""
            continue

        if mode == "type5":
            flags[i] = True
            if "]]>" in line:
                mode = ""
            continue

        m1 = _MD_HTML_BLOCK_TYPE1_RE.match(line)
        if m1 is not None:
            flags[i] = True
            end_tag = str(m1.group('tag') or '').casefold()
            if end_tag and not re.search(rf"</{re.escape(end_tag)}(?=[\t />]|$)", line, flags=re.IGNORECASE):
                mode = "type1"
            else:
                end_tag = ""
            continue

        if _MD_HTML_BLOCK_TYPE3_RE.match(line):
            flags[i] = True
            if "?>" not in line:
                mode = "type3"
            continue

        if _MD_HTML_BLOCK_TYPE4_RE.match(line):
            flags[i] = True
            if ">" not in line:
                mode = "type4"
            continue

        if _MD_HTML_BLOCK_TYPE5_RE.match(line):
            flags[i] = True
            if "]]>" not in line:
                mode = "type5"
            continue

        if _MD_HTML_BLOCK_TYPE6_RE.match(line):
            flags[i] = True
            mode = "blank"
            continue

        prev_blank = i == 0 or not str(xs[i - 1]).strip()
        if prev_blank and md_html_type7_tag_line(line):
            flags[i] = True
            mode = "blank"
            continue

    return flags


def md_fenced_code_line_flags(lines: list[object]) -> list[bool]:
    """Return zero-based per-line flags for tiny fenced code blocks.

    Policy is intentionally small and shared across docs/help surfaces:
      - opening fence: up to 3 leading spaces, then ``` or ~~~ (3+ chars)
      - closing fence: same marker character, at least the opener length
      - lines inside the fence, including opener/closer, are flagged ``True``

    This is a precedence helper, not a full markdown block parser. It keeps
    fenced examples inert so markdown-looking text inside them stays prose for
    docs actions and TUI link underlining.
    """

    xs = [str(x) for x in (lines or [])]
    if not xs:
        return []

    flags: list[bool] = [False] * len(xs)
    in_fence = False
    fence_ch = ''
    fence_len = 0

    for i, s in enumerate(xs):
        if not in_fence:
            m = _FENCE_OPEN_RE.match(s)
            if m is None:
                continue
            fence = str(m.group('fence') or '')
            if not fence:
                continue
            in_fence = True
            fence_ch = fence[0]
            fence_len = len(fence)
            flags[i] = True
            continue

        flags[i] = True
        if re.match(rf"^[ ]{{0,3}}{re.escape(fence_ch)}{{{int(fence_len)},}}[ \t]*$", s):
            in_fence = False
            fence_ch = ''
            fence_len = 0

    return flags



def md_indented_code_line_flags(
    lines: list[object],
    *,
    fence_flags: list[bool] | None = None,
    html_block_flags: list[bool] | None = None,
) -> list[bool]:
    """Return zero-based flags for tiny blank-separated indented code-ish runs.

    This helper is intentionally smaller than full CommonMark. It only covers
    the blank-separated top-level shape that shows up in Micromax's docs/help
    source view:
      - a run begins at start-of-file or after a blank line
      - the first non-blank line begins with 4+ spaces or a tab
      - the run continues across blank lines and later 4+-space/tab lines
      - fenced/raw-HTML lines are never claimed here

    The goal is shared precedence for docs/help surfaces so obvious source-view
    code examples stay code-ish for helpfollow/helplinkpick/TUI rendering
    without committing the editor to a fuller markdown block parser.
    """

    xs = [str(x) for x in (lines or [])]
    if not xs:
        return []

    fence_flags = list(fence_flags or [])
    html_block_flags = list(html_block_flags or [])
    flags: list[bool] = [False] * len(xs)
    in_code = False

    def _is_inert_elsewhere(idx: int) -> bool:
        return bool((idx < len(fence_flags) and fence_flags[idx]) or (idx < len(html_block_flags) and html_block_flags[idx]))

    def _is_indented_codeish(s: str) -> bool:
        return s.startswith("\t") or bool(re.match(r"^ {4,}", s))

    for i, s in enumerate(xs):
        if _is_inert_elsewhere(i):
            in_code = False
            continue
        if in_code:
            if not s.strip():
                keep_blank = False
                j = int(i) + 1
                while j < len(xs):
                    if _is_inert_elsewhere(j):
                        break
                    sj = str(xs[j])
                    if not sj.strip():
                        j += 1
                        continue
                    if _is_indented_codeish(sj):
                        keep_blank = True
                    break
                if keep_blank:
                    flags[i] = True
                    continue
                in_code = False
            elif _is_indented_codeish(s):
                flags[i] = True
                continue
            else:
                in_code = False
        prev_blank = i == 0 or not str(xs[i - 1]).strip()
        if prev_blank and _is_indented_codeish(s):
            flags[i] = True
            in_code = True

    return flags



def _ellipsize_right(text: str, width: int) -> str:
    """Return *text* clipped to *width* with an end ellipsis when needed."""

    s = str(text or "")
    w = max(0, int(width))
    if w <= 0:
        return ""
    if len(s) <= w:
        return s
    if w == 1:
        return s[:1]
    return s[: max(0, w - 1)] + "…"


def _ellipsize_left(text: str, width: int) -> str:
    """Return *text* clipped to *width* with a leading ellipsis when needed."""

    s = str(text or "")
    w = max(0, int(width))
    if w <= 0:
        return ""
    if len(s) <= w:
        return s
    if w == 1:
        return s[-1:]
    return "…" + s[-max(0, w - 1):]


def _fit_left_right_text(left: str, right: str, width: int, *, sep: str = " ") -> str:
    """Fit left/right prompt text into *width* while preserving right detail.

    This is used by picker rows where the leading label is usually the primary
    thing to scan, but the trailing detail often carries the distinguishing path,
    location, or mode. When truncation is needed we keep as much of the right
    detail as possible, using an ellipsis on the left side rather than simply
    chopping the whole combined string at the end.
    """

    w = max(0, int(width))
    if w <= 0:
        return ""

    left_s = str(left or "")
    right_s = str(right or "")
    if not right_s:
        return _ellipsize_right(left_s, w)
    if not left_s:
        return _ellipsize_left(right_s, w)

    right_block = f"{sep}{right_s}"
    full = left_s + right_block
    if len(full) <= w:
        return full
    if len(right_block) >= w:
        return _ellipsize_left(right_block, w)

    avail_left = max(0, w - len(right_block))
    return (_ellipsize_right(left_s, avail_left) + right_block)[:w]


def md_span_contains(spans: list[tuple[int, int]], a: int, b: int) -> bool:
    """Return True when ``[a,b)`` is fully covered by one span in ``spans``."""

    aa = int(a)
    bb = int(b)
    return any(int(sa) <= aa and bb <= int(sb) for sa, sb in spans)


@dataclass(frozen=True)
class MdLinkMatch:
    """Tiny docs/help markdown link match used by editor actions and the TUI."""

    kind: str
    start: int
    end: int
    label_start: int
    label_end: int
    display: str
    target: str


@dataclass(frozen=True)
class MdImageMatch:
    """Tiny docs/help markdown image match used by docs-cues snapshots."""

    kind: str
    start: int
    end: int
    alt_start: int
    alt_end: int
    alt_text: str
    target: str


@dataclass(frozen=True)
class MdCodeMatch:
    """Tiny docs/help inline-code match used by docs-cues snapshots."""

    kind: str
    start: int
    end: int
    body_start: int
    body_end: int
    delimiter_length: int
    text: str


@dataclass(frozen=True)
class MdLiteralTokenMatch:
    """Tiny docs/help literal-source token used by docs-cues snapshots."""

    kind: str
    start: int
    end: int
    text: str
    detail: str


def md_help_link_target_info(target: str) -> dict[str, str]:
    """Return a tiny classification snapshot for one docs/help link target.

    The editor already follows a small set of target shapes in help buffers:
    same-page fragments, cross-doc fragments, docs topics / relative file paths,
    and external ``http(s)`` / ``mailto:`` URLs. Exposing the same tiny
    classification keeps future UIs/scripts/LLMs from rediscovering that logic
    by scraping raw targets.
    """

    t = str(target or "").strip().strip('"').strip("'")
    out = {
        "target": t,
        "target_kind": "",
        "doc": "",
        "fragment": "",
    }
    if not t:
        return out

    low = t.casefold()
    if low.startswith("http://") or low.startswith("https://"):
        out["target_kind"] = "external"
        return out
    if low.startswith("mailto:"):
        out["target_kind"] = "mailto"
        return out

    doc_part, hash_mark, frag_part = t.partition("#")
    frag = unquote(str(frag_part or "").strip()) if hash_mark else ""
    if hash_mark and not doc_part.strip():
        out["fragment"] = frag
        out["target_kind"] = "footnote" if frag.startswith("^") else "fragment"
        return out

    doc = unquote(str(doc_part or t).strip())
    out["doc"] = doc
    out["fragment"] = frag
    looks_like_path = doc.endswith('.md') or ('/' in doc) or ('\\' in doc)
    if hash_mark:
        out["target_kind"] = "file-fragment" if looks_like_path else "doc-fragment"
    else:
        out["target_kind"] = "file" if looks_like_path else "doc"
    return out


def md_help_link_source_kind(line: str, start: int, end: int, kind: str) -> str:
    """Return a tiny source-form classification for one visible docs/help link.

    ``docs_cues_model(...)`` already exposes what a visible link points to, but
    future UIs/scripts/LLMs sometimes also want to know *how* the source spelled
    that link: inline destination, autolink, footnote reference, or a
    reference-style link resolved through definitions elsewhere in the doc.

    The classifier intentionally stays tiny and source-view-oriented rather than
    promoting a fuller markdown AST.
    """

    k = str(kind or "")
    if k == "autolink":
        return "autolink"
    if k == "footnote":
        return "footnote"
    if k != "link":
        return ""

    s = str(line or "")
    a = max(0, int(start))
    b = max(a, int(end))
    frag = s[a:b]
    if not frag.startswith('['):
        return ""
    label_span = md_balanced_span(frag, 0, opener='[', closer=']')
    if label_span is None:
        return ""
    _, lb = label_span
    after = frag[lb:lb + 1]
    if after == '(':
        return "inline"
    if after == '[' or after == '':
        return "reference"
    return ""


def md_help_image_source_kind(line: str, start: int, end: int, kind: str) -> str:
    """Return a tiny source-form classification for one visible docs/help image.

    ``docs_cues_model(...)`` already exposes what a visible image points to, but
    future UIs/scripts/LLMs sometimes also want to know *how* the source spelled
    that image: inline destination or reference-style image syntax resolved
    through definitions elsewhere in the doc.

    The classifier intentionally stays tiny and source-view-oriented rather than
    promoting a fuller markdown AST.
    """

    if str(kind or "") != "image":
        return ""

    s = str(line or "")
    a = max(0, int(start))
    b = max(a, int(end))
    frag = s[a:b]
    if not frag.startswith('!['):
        return ""
    label_span = md_balanced_span(frag, 1, opener='[', closer=']')
    if label_span is None:
        return ""
    _, lb = label_span
    after = frag[lb:lb + 1]
    if after == '(':
        return "inline"
    if after == '[' or after == '':
        return "reference"
    return ""


def md_help_link_reference_form(line: str, start: int, end: int, kind: str) -> str:
    """Return ``full`` / ``collapsed`` / ``shortcut`` for reference-style links.

    ``docs_cues_model(...)`` already exposes link targets and coarse source
    kinds. Future UIs/scripts/LLMs sometimes also need the exact CommonMark-ish
    reference spelling the visible source used without reparsing the row:
    ``[label][id]`` (full), ``[label][]`` (collapsed), or ``[id]`` (shortcut).

    The classifier stays intentionally tiny and source-view-oriented rather than
    promoting a fuller markdown AST.
    """

    if md_help_link_source_kind(line, start, end, kind) != "reference":
        return ""

    s = str(line or "")
    a = max(0, int(start))
    b = max(a, int(end))
    frag = s[a:b]
    if not frag.startswith('['):
        return ""
    label_span = md_balanced_span(frag, 0, opener='[', closer=']')
    if label_span is None:
        return ""
    _, lb = label_span
    after = frag[lb:lb + 1]
    if after == '[':
        ref_span = md_balanced_span(frag, lb, opener='[', closer=']')
        if ref_span is None:
            return ""
        rs, re = ref_span
        return "collapsed" if frag[rs + 1:re - 1] == '' else "full"
    if after == '':
        return "shortcut"
    return ""


def md_help_image_reference_form(line: str, start: int, end: int, kind: str) -> str:
    """Return ``full`` / ``collapsed`` / ``shortcut`` for reference-style images.

    This mirrors :func:`md_help_link_reference_form` for visible docs/help image
    source. It keeps reference-style images inspectable as tiny source-view
    facts without promoting a fuller markdown AST.
    """

    if md_help_image_source_kind(line, start, end, kind) != "reference":
        return ""

    s = str(line or "")
    a = max(0, int(start))
    b = max(a, int(end))
    frag = s[a:b]
    if not frag.startswith('!['):
        return ""
    label_span = md_balanced_span(frag, 1, opener='[', closer=']')
    if label_span is None:
        return ""
    _, lb = label_span
    after = frag[lb:lb + 1]
    if after == '[':
        ref_span = md_balanced_span(frag, lb, opener='[', closer=']')
        if ref_span is None:
            return ""
        rs, re = ref_span
        return "collapsed" if frag[rs + 1:re - 1] == '' else "full"
    if after == '':
        return "shortcut"
    return ""


def md_inline_markup_delimiter_kind(delimiter: str) -> str:
    """Return a tiny source-delimiter family for inline markup tokens.

    ``docs_cues_model(...)`` already exposes inline-markup kinds like strong,
    emphasis, and strike. Future UIs/scripts/LLMs sometimes also want the
    literal delimiter family used by the visible source without re-filtering the
    raw ``delimiter`` field: asterisk-based emphasis, underscore-based
    emphasis, or tilde-based strikethrough.

    The classifier intentionally stays tiny and source-view-oriented rather than
    promoting a fuller markdown AST.
    """

    frag = str(delimiter or "")
    if not frag:
        return ""
    lead = frag[:1]
    if lead == '*':
        return 'asterisk'
    if lead == '_':
        return 'underscore'
    if lead == '~':
        return 'tilde'
    return ''


def md_fenced_code_marker_kind(marker: str) -> str:
    """Return a tiny marker family for fenced-code rows.

    CommonMark/GFM fenced blocks are source-spelled with either backticks or
    tildes. ``docs_cues_model(...)`` already exposes tiny fence details like the
    raw marker text and info string on opener rows; this helper promotes the
    common "which fence family is this block using?" question into a stable tiny
    classifier so future UIs/scripts/LLMs do not have to re-interpret the raw
    one-character ``marker`` field every time.
    """

    frag = str(marker or '')
    if frag == '`':
        return 'backtick'
    if frag == '~':
        return 'tilde'
    return ''


def md_balanced_span(s: str, open_idx: int, *, opener: str, closer: str) -> tuple[int, int] | None:
    """Return ``(start, end)`` for a tiny balanced-delimiter span, or ``None``.

    This helper is intentionally small but covers the docs-browser cases regexes
    handle poorly: nested bracket labels like ``[Vision [nested]]`` and inline
    destinations with nested parentheses like ``(topic(one).md)``.
    """

    text = str(s or '')
    i0 = int(open_idx)
    if i0 < 0 or i0 >= len(text) or text[i0] != opener:
        return None

    depth = 0
    i = i0
    while i < len(text):
        ch = text[i]
        if ch == "\\":
            i += 2
            continue
        if ch == opener:
            depth += 1
        elif ch == closer:
            depth -= 1
            if depth == 0:
                return (i0, i + 1)
        i += 1
    return None


def md_label_contains_nested_links(
    label_src: str,
    defs: dict[str, str],
    footdefs: dict[str, tuple[int, int]] | None = None,
) -> bool:
    """Return True when *label_src* contains a valid nested markdown link.

    CommonMark allows balanced brackets inside link text, but valid links may
    not contain other links at any level of nesting. The tiny docs browser keeps
    this rule intentionally small and shared by recursively scanning the label
    contents with the same link matcher and rejecting the outer link when an
    inner *link* match exists.

    Images remain allowed inside link labels because ``md_link_matches`` already
    ignores image syntax, mirroring CommonMark's ``[![moon](img)](/uri)`` case.
    """

    inner = str(label_src or '')
    if not inner or '[' not in inner:
        return False
    for match in md_link_matches(inner, defs, footdefs):
        if str(match.kind) == 'link':
            return True
    return False


def md_link_matches(
    line: str,
    defs: dict[str, str],
    footdefs: dict[str, tuple[int, int]] | None = None,
    masked_spans: list[tuple[int, int]] | None = None,
    next_line: str = "",
    next_next_line: str = "",
) -> list[MdLinkMatch]:
    """Return tiny docs/help markdown link matches for one source line.

    Policy intentionally mirrors the editor's help-browser actions and the tiny
    TUI underline model while staying much smaller than a full markdown parser.
    """

    s = str(line or '')
    if not s:
        return []

    footdefs = dict(footdefs or {})
    code_spans = md_inline_code_spans(s)
    mask_spans = list(code_spans)
    if masked_spans:
        mask_spans.extend((int(a), int(b)) for a, b in masked_spans)
    html_spans = md_inline_html_tag_spans(s, masked_spans=mask_spans)
    out: list[MdLinkMatch] = []
    i = 0
    while i < len(s):
        ch = s[i]

        if ch == '<':
            if md_backslash_escaped(s, i) or md_span_contains(mask_spans, i, i + 1):
                i += 1
                continue
            m = re.match(r"<(?P<url>(?:https?://|mailto:)[^ >]+)>", s[i:])
            if m is not None:
                url = str(m.group('url') or '').strip()
                if url:
                    a = i + int(m.start())
                    b = i + int(m.end())
                    ua = i + int(m.start('url'))
                    ub = i + int(m.end('url'))
                    out.append(MdLinkMatch('autolink', a, b, ua, ub, url, url))
                    i = b
                    continue

        if ch != '[':
            i += 1
            continue
        if md_backslash_escaped(s, i) or md_span_contains(mask_spans, i, i + 1):
            i += 1
            continue
        # Treat the second opener of [label][id] as part of the same construct,
        # not as a standalone shortcut ref, even if the first opener stayed prose.
        if i > 0 and s[i - 1] == ']':
            i += 1
            continue

        label_span = md_balanced_span(s, i, opener='[', closer=']')
        if label_span is None:
            i += 1
            continue
        a, b = label_span
        if md_span_contains(mask_spans, a, b):
            i = max(i + 1, b)
            continue
        if a > 0 and s[a - 1] == '!':
            i = b
            continue

        if any(int(sa) < b and a < int(sb) for sa, sb in html_spans):
            i = b
            continue

        label = s[a + 1:b - 1]
        if not md_link_label_has_text(label):
            i = b
            continue
        if md_label_contains_nested_links(label, defs, footdefs):
            i += 1
            continue
        after = s[b:b+1]

        if after == '(':
            inner_span = md_balanced_span(s, b, opener='(', closer=')')
            if inner_span is not None:
                _, d = inner_span
                if not md_span_contains(mask_spans, a, d):
                    target = md_inline_link_target(s[b + 1:d - 1])
                    if target:
                        out.append(MdLinkMatch('link', a, d, a + 1, b - 1, label, target))
                        i = d
                        continue
            target = md_inline_link_target_multiline(s[b + 1 :], next_line, next_next_line)
            if target:
                out.append(MdLinkMatch('link', a, len(s), a + 1, b - 1, label, target))
                i = len(s)
                continue

        if after == '[':
            id_span = md_balanced_span(s, b, opener='[', closer=']')
            if id_span is not None:
                _, d = id_span
                if not md_span_contains(mask_spans, a, d):
                    rid = s[b + 1:d - 1].strip() or label.strip()
                    target = defs.get(md_norm_ref_id(rid))
                    if target:
                        out.append(MdLinkMatch('link', a, d, a + 1, b - 1, label, target))
                        i = d
                        continue

        if label.startswith('^') and after != ':':
            rid = label[1:].strip()
            if rid and footdefs.get(md_norm_ref_id(rid)) is not None:
                out.append(MdLinkMatch('footnote', a, b, a + 1, b - 1, f"[^{rid}]", f"#^{rid}"))
                i = b
                continue

        if after != ':':
            rid = label.strip()
            target = defs.get(md_norm_ref_id(rid)) if rid else None
            if target:
                out.append(MdLinkMatch('link', a, b, a + 1, b - 1, rid, target))
                i = b
                continue

        i += 1

    return out


def md_image_matches(
    line: str,
    defs: dict[str, str],
    *,
    masked_spans: list[tuple[int, int]] | None = None,
    next_line: str = "",
    next_next_line: str = "",
) -> list[MdImageMatch]:
    """Return tiny docs/help markdown image matches for one source line.

    This intentionally stays smaller than a fuller markdown AST. It mirrors the
    supported inline/reference/shortcut image forms the docs/help TUI already
    dims, so shared docs-cues snapshots can report visible image targets
    without adding another parser path.
    """

    s = str(line or '')
    if not s:
        return []

    mask_spans = [(int(a), int(b)) for a, b in md_inline_code_spans(s)]
    if masked_spans:
        mask_spans.extend((int(a), int(b)) for a, b in masked_spans)

    def _covered(a: int, b: int) -> bool:
        aa = int(a)
        bb = int(b)
        return any(int(sa) <= aa and bb <= int(sb) for sa, sb in mask_spans)

    out: list[MdImageMatch] = []
    i = 0
    while i < len(s) - 1:
        if s[i] != '!' or s[i + 1] != '[':
            i += 1
            continue
        if md_backslash_escaped(s, i) or _covered(i, i + 1):
            i += 1
            continue

        label_span = md_balanced_span(s, i + 1, opener='[', closer=']')
        if label_span is None:
            i += 1
            continue
        la, lb = label_span
        if _covered(i, lb):
            i = max(i + 1, lb)
            continue

        alt_text = s[la + 1 : lb - 1]
        after = s[lb:lb + 1]

        if after == '(':
            inner_span = md_balanced_span(s, lb, opener='(', closer=')')
            if inner_span is not None:
                _, end = inner_span
                if not _covered(i, end):
                    target = md_inline_link_target(s[lb + 1 : end - 1])
                    if target:
                        out.append(MdImageMatch('image', i, end, la + 1, lb - 1, alt_text, target))
                        i = end
                        continue
            target = md_inline_link_target_multiline(s[lb + 1 :], next_line, next_next_line)
            if target:
                out.append(MdImageMatch('image', i, len(s), la + 1, lb - 1, alt_text, target))
                i = len(s)
                continue

        if after == '[':
            id_span = md_balanced_span(s, lb, opener='[', closer=']')
            if id_span is not None:
                _, end = id_span
                if not _covered(i, end):
                    rid = s[lb + 1 : end - 1].strip() or alt_text.strip()
                    target = defs.get(md_norm_ref_id(rid))
                    if target:
                        out.append(MdImageMatch('image', i, end, la + 1, lb - 1, alt_text, target))
                        i = end
                        continue

        if after != ':':
            rid = alt_text.strip()
            target = defs.get(md_norm_ref_id(rid)) if rid else None
            if target:
                out.append(MdImageMatch('image', i, lb, la + 1, lb - 1, alt_text, target))
                i = lb
                continue

        i += 1

    return out


def md_strip_inline_markup(s: str) -> str:
    """Best-effort markdown-inline text cleanup for heading anchors/titles.

    This is intentionally tiny rather than CommonMark-complete. It removes the
    most common formatting wrappers so heading slugs and picker labels behave
    more like rendered markdown, not raw source.
    """

    out = str(s or "")
    if not out:
        return ""

    # Images/links/reference links/autolinks -> visible label text.
    out = re.sub(r"!\[(?P<label>[^\]]*)\]\((?P<inner>[^)]*)\)", lambda m: str(m.group("label") or ""), out)
    out = re.sub(r"\[(?P<label>[^\]]+)\]\((?P<inner>[^)]*)\)", lambda m: str(m.group("label") or ""), out)
    out = re.sub(r"\[(?P<label>[^\]]+)\]\[(?P<id>[^\]]*)\]", lambda m: str(m.group("label") or ""), out)
    out = re.sub(r"<(?P<url>(?:https?://|mailto:)[^ >]+)>", lambda m: str(m.group("url") or ""), out)

    # Inline code/emphasis/strikethrough markers -> contents.
    out = re.sub(r"`([^`]*)`", lambda m: str(m.group(1) or ""), out)
    out = re.sub(r"\*\*([^*]+)\*\*", lambda m: str(m.group(1) or ""), out)
    out = re.sub(r"__([^_]+)__", lambda m: str(m.group(1) or ""), out)
    out = re.sub(r"\*([^*]+)\*", lambda m: str(m.group(1) or ""), out)
    out = re.sub(r"_([^_]+)_", lambda m: str(m.group(1) or ""), out)
    out = re.sub(r"~~([^~]+)~~", lambda m: str(m.group(1) or ""), out)

    # Drop residual markdown-y punctuation/HTML tags conservatively.
    out = re.sub(r"<[^>]+>", "", out)
    out = out.replace("[", "").replace("]", "")
    out = out.replace("(", "").replace(")", "")
    return re.sub(r"\s+", " ", out).strip()


def md_heading_auto_id(title: str, *, seen: dict[str, int] | None = None) -> str:
    """Best-effort GitHub-style heading slug for docs fragments.

    Rules kept intentionally small:
      - remove common markdown inline markup
      - lowercase
      - replace whitespace runs with ``-``
      - drop most punctuation
      - preserve unicode letters/digits
      - de-duplicate with ``-1``, ``-2``, ... when ``seen`` is provided
    """

    clean = md_strip_inline_markup(title).strip().lower()
    parts: list[str] = []
    prev_dash = False
    for ch in clean:
        if ch.isalnum():
            parts.append(ch)
            prev_dash = False
            continue
        if ch.isspace() or ch == "-":
            if parts and not prev_dash:
                parts.append("-")
                prev_dash = True
            continue
        # Drop other punctuation/markup characters.
    slug = "".join(parts).strip("-") or "section"
    if seen is None:
        return slug
    n = int(seen.get(slug, 0))
    seen[slug] = n + 1
    if n <= 0:
        return slug
    return f"{slug}-{n}"


__all__ = [
    "MdCodeMatch",
    "MdImageMatch",
    "MdLinkMatch",
    "MdLiteralTokenMatch",
    "_BACKTICK_RUN_RE",
    "_FENCE_OPEN_RE",
    "_MD_BACKSLASH_UNESCAPE_CHARS",
    "_MD_HTML_BLOCK_TAGS",
    "_MD_HTML_BLOCK_TYPE1_RE",
    "_MD_HTML_BLOCK_TYPE3_RE",
    "_MD_HTML_BLOCK_TYPE4_RE",
    "_MD_HTML_BLOCK_TYPE5_RE",
    "_MD_HTML_BLOCK_TYPE6_RE",
    "_MD_HTML_TYPE7_EXCLUDED",
    "_SETEXT_UNDERLINE_RE",
    "_ellipsize_left",
    "_ellipsize_right",
    "_fit_left_right_text",
    "_md_inline_code_parts",
    "_md_inline_rest_closes_on_line",
    "_md_link_rest_has_required_separator",
    "_md_link_target_prefix",
    "_md_rest_is_title",
    "md_backslash_escaped",
    "md_backslash_unescape",
    "md_balanced_span",
    "md_docs_continuation_line",
    "md_escaped_markdown_matches",
    "md_fenced_code_line_flags",
    "md_fenced_code_marker_kind",
    "md_heading_auto_id",
    "md_help_image_reference_form",
    "md_help_image_source_kind",
    "md_help_link_reference_form",
    "md_help_link_source_kind",
    "md_help_link_target_info",
    "md_html_block_line_flags",
    "md_html_comment_line_spans",
    "md_html_comment_spans",
    "md_html_type7_tag_line",
    "md_image_matches",
    "md_indented_code_line_flags",
    "md_inline_code_delimiter_spans",
    "md_inline_code_matches",
    "md_inline_code_spans",
    "md_inline_html_tag_spans",
    "md_inline_link_target",
    "md_inline_link_target_multiline",
    "md_inline_markup_delimiter_kind",
    "md_label_contains_nested_links",
    "md_leading_spaces_upto3",
    "md_link_label_has_text",
    "md_link_matches",
    "md_norm_ref_id",
    "md_raw_html_tag_matches",
    "md_reference_def_target",
    "md_reference_def_target_info",
    "md_span_contains",
    "md_strip_inline_markup",
]
