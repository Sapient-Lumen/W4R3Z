from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re
import time
from typing import Callable, Iterable

from .resource_roots import default_docs_root

HeadingScan = Callable[[list[object]], Iterable[tuple[int, int, int, str, str, int]]]
DocEntry = dict[str, str]
DocRow = list[str]
DetailRow = list[object]
DocsFingerprint = tuple[tuple[str, int, int], ...]
DocsCacheToken = tuple[str, DocsFingerprint]

_SETEXT_UNDERLINE_RE = re.compile(r"^[ ]{0,3}(?P<run>=+|-{2,})[ \t]*$")

# Process-local docs catalog cache keyed by resolved docs root plus a cheap
# directory fingerprint. Long-lived editor/test processes get the fast path, but
# edits to docs files are visible without asking callers to clear a global cache.
#
# The repository docs tree is large enough that re-statting every Markdown file
# for every prompt probe recreates the completion stall this cache was meant to
# remove. Large roots therefore reuse a fresh fingerprint for a short window;
# small custom docs roots are checked every call, preserving immediate edit
# visibility for live docs tests and user-supplied docs directories.
_LARGE_ROOT_FILE_COUNT = 128
_LARGE_ROOT_FINGERPRINT_TTL_NS = 1_000_000_000
_DOC_SCAN_CACHE: dict[str, tuple[DocsFingerprint, list[DocEntry], int]] = {}


@dataclass(frozen=True)
class DocPromptState:
    """Materialized docs picker rows plus exact detail lookup caches."""

    rows: list[DocRow]
    section_labels: dict[str, str]
    section_ranks: dict[str, int]
    detail_rows_by_topic: dict[str, DetailRow]
    detail_rows_by_norm_path: dict[str, DetailRow]


def docs_root_from_env(raw: str | None = None, *, cwd: Path | None = None) -> Path:
    """Return a docs root using the repo/install-aware ``MICROMAX_DOCS`` convention.

    ``raw`` is intentionally explicit so editor code can pass the environment
    value it wants. When neither ``raw`` nor ``MICROMAX_DOCS`` is set, the
    default remains ``./docs`` when that directory exists, then falls back to an
    installed ``share/micromax/docs`` tree.
    """

    value = raw if raw is not None else os.environ.get("MICROMAX_DOCS")
    return default_docs_root(value, cwd=cwd)


def docs_root_key(root: Path) -> str:
    """Return a stable cache key for one docs root path."""

    try:
        return str(root.resolve())
    except Exception:
        return str(root)


def _doc_path_stays_inside_root(path: Path, root: Path) -> bool:
    """Return whether ``path`` resolves to a markdown file inside ``root``.

    The docs index is a documentation inventory, not a general filesystem
    browser.  Symlinks that point outside the docs root are intentionally
    excluded so catalog/topic lookups cannot become a read bypass for scripts
    through help buffers.
    """

    try:
        if path.suffix.casefold() != ".md":
            return False
        if not path.is_symlink():
            return bool(path.is_file())
        root_resolved = root.resolve(strict=False)
        resolved = path.resolve(strict=True)
        resolved.relative_to(root_resolved)
        return bool(resolved.is_file())
    except Exception:
        return False


def _docs_markdown_files(root: Path) -> list[Path]:
    try:
        if not root.exists() or root.is_dir() is False:
            return []
        return sorted(
            [p for p in root.glob("*.md") if _doc_path_stays_inside_root(p, root)],
            key=lambda p: p.name.casefold(),
        )
    except Exception:
        return []


def docs_root_fingerprint(root: Path) -> DocsFingerprint:
    """Return a cheap freshness signature for direct markdown docs children."""

    out: list[tuple[str, int, int]] = []
    for p in _docs_markdown_files(root):
        try:
            st = p.stat()
        except OSError:
            continue
        out.append(
            (
                str(p.name),
                int(getattr(st, "st_mtime_ns", 0)),
                int(getattr(st, "st_size", 0)),
            )
        )
    return tuple(out)


def docs_root_cache_token(root: Path) -> DocsCacheToken:
    """Return the root key plus freshness signature used by docs caches."""

    key = docs_root_key(root)
    cached = _DOC_SCAN_CACHE.get(key)
    now = time.monotonic_ns()
    if cached is not None:
        fingerprint, _rows, checked_ns = cached
        if (
            len(fingerprint) >= _LARGE_ROOT_FILE_COUNT
            and now - int(checked_ns) < _LARGE_ROOT_FINGERPRINT_TTL_NS
        ):
            return (key, fingerprint)

    fingerprint = docs_root_fingerprint(root)
    if cached is not None and cached[0] == fingerprint:
        _DOC_SCAN_CACHE[key] = (fingerprint, cached[1], now)
    return (key, fingerprint)


def clear_docs_scan_cache() -> None:
    """Clear process-local docs scan state; mostly useful for tests/tools."""

    _DOC_SCAN_CACHE.clear()


def _copy_doc_entries(rows: list[DocEntry]) -> list[DocEntry]:
    return [dict(row) for row in rows]


def _strip_inline_markup(text: str) -> str:
    """Best-effort inline cleanup for docs catalog titles."""

    out = str(text or "")
    if not out:
        return ""
    out = re.sub(
        r"!\[(?P<label>[^\]]*)\]\((?P<inner>[^)]*)\)",
        lambda m: str(m.group("label") or ""),
        out,
    )
    out = re.sub(
        r"\[(?P<label>[^\]]+)\]\((?P<inner>[^)]*)\)",
        lambda m: str(m.group("label") or ""),
        out,
    )
    out = re.sub(
        r"\[(?P<label>[^\]]+)\]\[(?P<id>[^\]]*)\]",
        lambda m: str(m.group("label") or ""),
        out,
    )
    out = re.sub(
        r"<(?P<url>(?:https?://|mailto:)[^ >]+)>",
        lambda m: str(m.group("url") or ""),
        out,
    )
    out = re.sub(r"`([^`]*)`", lambda m: str(m.group(1) or ""), out)
    out = re.sub(r"\*\*([^*]+)\*\*", lambda m: str(m.group(1) or ""), out)
    out = re.sub(r"__([^_]+)__", lambda m: str(m.group(1) or ""), out)
    out = re.sub(r"\*([^*]+)\*", lambda m: str(m.group(1) or ""), out)
    out = re.sub(r"_([^_]+)_", lambda m: str(m.group(1) or ""), out)
    out = re.sub(r"~~([^~]+)~~", lambda m: str(m.group(1) or ""), out)
    out = re.sub(r"<[^>]+>", "", out)
    out = out.replace("[", "").replace("]", "")
    out = out.replace("(", "").replace(")", "")
    return re.sub(r"\s+", " ", out).strip()


def _clean_heading_title(raw_title: str) -> str:
    title = str(raw_title or "").strip()
    attr_m = re.search(r"\s+(?P<attrs>\{(?::)?\s*[^{}]*\})\s*$", title)
    if attr_m is not None:
        title = title[: int(attr_m.start())].rstrip()
    return _strip_inline_markup(title) or title.strip()


def _atx_heading_title(line: str) -> tuple[int, str] | None:
    s = str(line or "")
    indent = len(s) - len(s.lstrip(" "))
    if indent > 3:
        return None
    m = re.match(r"[ ]{0,3}(?P<hashes>#{1,6})\s+(?P<title>.+?)\s*(?:#+\s*)?$", s)
    if m is None:
        return None
    title = _clean_heading_title(str(m.group("title") or ""))
    if not title:
        return None
    return (len(str(m.group("hashes") or "")), title)


def _looks_like_setext_title_line(line: str) -> bool:
    s = str(line or "")
    stripped = s.strip()
    if not stripped:
        return False
    if _atx_heading_title(s) is not None:
        return False
    if re.match(r"^[ ]{0,3}(?:>|[*+-]\s|\d+[.)]\s)", s):
        return False
    if re.match(r"^\s{4,}", s):
        return False
    if re.match(r"^[ ]{0,3}(`{3,}|~{3,})", s):
        return False
    if _SETEXT_UNDERLINE_RE.match(stripped) is not None:
        return False
    return True


def _fast_title_summary(lines: list[str]) -> tuple[str, str]:
    """Return the first docs title/summary without full markdown metadata scans."""

    title = ""
    summary = ""
    heading_start = -1
    heading_end = -1
    in_fence = False
    fence = ""

    for i, line in enumerate(lines):
        s = str(line or "")
        fence_m = re.match(r"^[ ]{0,3}(?P<fence>`{3,}|~{3,})", s)
        if fence_m is not None:
            token = str(fence_m.group("fence") or "")
            if not in_fence:
                in_fence = True
                fence = token[0]
            elif token.startswith(fence * 3):
                in_fence = False
                fence = ""
            continue
        if in_fence:
            continue

        atx = _atx_heading_title(s)
        if atx is not None:
            title = atx[1]
            heading_start = i
            heading_end = i + 1
            break

        if i > 0 and _SETEXT_UNDERLINE_RE.match(s.strip()) is not None:
            parts_rev: list[str] = []
            start = i
            for j in range(i - 1, -1, -1):
                prev = str(lines[j] or "")
                if not _looks_like_setext_title_line(prev):
                    break
                start = j
                parts_rev.append(prev.strip())
            if parts_rev:
                title = _clean_heading_title(" ".join(reversed(parts_rev)))
                heading_start = start
                heading_end = i + 1
                break

    start = heading_end if heading_end >= 0 else 0
    heading_lines = set(range(heading_start, heading_end)) if heading_start >= 0 else set()
    summary = _first_summary_line(lines, start, heading_lines)
    if not summary and start != 0:
        summary = _first_summary_line(lines, 0, heading_lines)
    return title, summary


def _first_summary_line(lines: list[str], start: int, heading_line_idxs: set[int]) -> str:
    for i, line in enumerate(lines[int(start) :], int(start)):
        s = line.strip()
        if not s:
            continue
        if i in heading_line_idxs or _SETEXT_UNDERLINE_RE.match(s) is not None:
            continue
        if s.startswith("#"):
            continue
        return s
    return ""


def _scan_doc_file(path: Path, heading_scan: HeadingScan) -> DocEntry:
    stem = path.stem
    slug = re.sub(r"^\d+\-", "", stem)
    topic = slug or stem
    title = ""
    summary = ""
    try:
        txt = path.read_text(encoding="utf-8")
        lines = txt.splitlines()
        title, summary = _fast_title_summary(lines)
        if not title:
            headings = list(heading_scan(list(lines)))
            heading_line_idxs = {
                int(k)
                for line0, line1, _level, _title, _frag, _col0 in headings
                for k in range(int(line0), int(line1))
            }
            summary_start = 0
            if headings:
                _line0, summary_start, _level, title0, _frag0, _col0 = headings[0]
                title = str(title0 or "")
            if summary_start:
                summary = _first_summary_line(lines, int(summary_start), heading_line_idxs)
            if not summary:
                summary = _first_summary_line(lines, 0, heading_line_idxs)
    except Exception:
        pass
    return {
        "topic": str(topic),
        "path": str(path),
        "title": str(title),
        "summary": str(summary),
    }


def scan_docs(root: Path, heading_scan: HeadingScan) -> list[DocEntry]:
    """Return docs entries with process-cache reuse and freshness checks."""

    key, fingerprint = docs_root_cache_token(root)
    cached = _DOC_SCAN_CACHE.get(key)
    if cached is not None and cached[0] == fingerprint:
        return _copy_doc_entries(cached[1])

    files = _docs_markdown_files(root)
    out = [_scan_doc_file(p, heading_scan) for p in files]
    if files or root.exists():
        _DOC_SCAN_CACHE[key] = (fingerprint, _copy_doc_entries(out), time.monotonic_ns())
    else:
        _DOC_SCAN_CACHE.pop(key, None)
    return _copy_doc_entries(out)


def build_docs_catalog(entries: list[DocEntry]) -> dict[str, DocEntry]:
    """Return docs entries keyed by common target spellings."""

    out: dict[str, DocEntry] = {}
    for ent in entries:
        topic = str(ent.get("topic", "") or "").strip()
        path = str(ent.get("path", "") or "").strip()
        title = str(ent.get("title", "") or "").strip()
        if not path:
            continue
        stem = Path(path).stem
        slug = re.sub(r"^\d+\-", "", stem) or stem
        entry = {"path": path, "title": title, "topic": topic or slug}
        keys = {topic, path, Path(path).name, stem, slug}
        for key in keys:
            k = str(key or "").strip().casefold()
            if k:
                out.setdefault(k, dict(entry))
    return dict(out)


def doc_section_info_for_path(path: str) -> tuple[int, str]:
    """Best-effort visible section label for a docs path."""

    stem = Path(str(path or "")).stem
    m = re.match(r"^(\d+)(?:-|$)", stem)
    if m is None:
        return (999, "Docs")
    n = int(m.group(1), 10)
    if n < 10:
        return (0, "00–09 Project")
    if n < 20:
        return (10, "10–19 Research")
    if n < 30:
        return (20, "20–29 Language + VM")
    if n < 40:
        return (30, "30–39 Host + integration")
    if n < 50:
        return (40, "40–49 Planning")
    if n < 60:
        return (50, "50–59 Editor core")
    if n < 70:
        return (60, "60–69 Editor + host")
    if n < 80:
        return (70, "70–79 Tutorials + discovery")
    if n < 90:
        return (80, "80–89 Config + plugins")
    if n < 100:
        return (90, "90–99 Advanced notes")
    return (100, "100+ Feature notes")


def build_doc_prompt_state(
    entries: list[DocEntry],
    *,
    section_info_for_path: Callable[[str], tuple[int, str]] = doc_section_info_for_path,
    normalize_path: Callable[[str], str | None],
) -> DocPromptState:
    """Build docs picker rows plus the small lookup caches the editor needs."""

    rows: list[DocRow] = []
    section_labels: dict[str, str] = {}
    section_ranks: dict[str, int] = {}
    detail_rows: dict[str, DetailRow] = {}
    detail_rows_by_norm_path: dict[str, DetailRow] = {}

    for ent in entries:
        topic = str(ent.get("topic", ""))
        path = str(ent.get("path", ""))
        title = str(ent.get("title", ""))
        summary = str(ent.get("summary", ""))
        menu = title or Path(path).name
        rank, section = section_info_for_path(path)
        section_labels[topic] = section
        section_ranks.setdefault(section, int(rank))
        detail = [topic, title, summary, section, path]
        detail_rows[topic] = list(detail)
        norm_path = normalize_path(path) or str(path)
        if norm_path:
            detail_rows_by_norm_path[norm_path] = list(detail)
        rows.append([topic, "doc", menu, summary])

    rows.sort(
        key=lambda row: (
            int(section_ranks.get(section_labels.get(str(row[0]), ""), 999)),
            str(row[0]).casefold(),
            str(row[2]).casefold(),
        )
    )

    return DocPromptState(
        rows=[list(row) for row in rows],
        section_labels=dict(section_labels),
        section_ranks=dict(section_ranks),
        detail_rows_by_topic={key: list(value) for key, value in detail_rows.items()},
        detail_rows_by_norm_path={
            key: list(value) for key, value in detail_rows_by_norm_path.items()
        },
    )


# Compatibility aliases for older local experiments/imports.
docs_catalog = build_docs_catalog
build_doc_prompt_model = build_doc_prompt_state
