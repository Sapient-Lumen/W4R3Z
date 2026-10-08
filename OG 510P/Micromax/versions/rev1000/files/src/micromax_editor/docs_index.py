from __future__ import annotations

from dataclasses import dataclass
import multiprocessing
import os
from pathlib import Path
import re
import time
from typing import Callable, Iterable

from .file_access import (
    ContainedDirEntry,
    FilesystemOperationTimeoutError,
    list_dir_contained,
    read_file_prefix_contained,
    stat_path_contained,
)
from .resource_roots import default_docs_root
from .worker_process import (
    WorkerResultError,
    WorkerResultTimeoutError,
    collect_worker_result,
    create_one_shot_worker,
    isolated_worker_context,
)

HeadingScan = Callable[[list[object]], Iterable[tuple[int, int, int, str, str, int]]]
DocEntry = dict[str, str]
DocRow = list[str]
DetailRow = list[object]
DocsFingerprint = tuple[tuple[str, int, int], ...]
DocsCacheToken = tuple[str, DocsFingerprint]

_SETEXT_UNDERLINE_RE = re.compile(r"^[ ]{0,3}(?P<run>=+|-{2,})[ \t]*$")
_REVISION_BANNER_RE = re.compile(
    r"^(?:rev(?:ision)?\s*0*\d+\b|latest\b[^\n]*\brev\s*0*\d+\b)",
    re.IGNORECASE,
)

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
DOCS_SCAN_MAX_FILES = 2048
DOCS_SCAN_MAX_FILE_BYTES = 1024 * 1024
DOCS_SCAN_MAX_TOTAL_BYTES = 8 * 1024 * 1024
DOCS_SCAN_TIMEOUT_SECONDS = 5.0
_DOC_SCAN_CACHE: dict[str, tuple[DocsFingerprint, list[DocEntry], int]] = {}
_DOC_RECORD_CACHE: dict[str, tuple[DocsFingerprint, list["_DocScanRecord"], int]] = {}


@dataclass(frozen=True)
class DocPromptState:
    """Materialized docs picker rows plus exact detail lookup caches."""

    rows: list[DocRow]
    section_labels: dict[str, str]
    section_ranks: dict[str, int]
    detail_rows_by_topic: dict[str, DetailRow]
    detail_rows_by_norm_path: dict[str, DetailRow]


@dataclass(frozen=True)
class _DocScanRecord:
    path: str
    name: str
    mtime: int
    size: int
    text: str


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


def _docs_worker_context() -> multiprocessing.context.BaseContext:
    """Return a process context for killable docs-root inventory scans."""

    return isolated_worker_context()


def _docs_entry_is_markdown(entry: ContainedDirEntry) -> bool:
    name = Path(str(entry.path)).name
    return bool(name) and name.casefold().endswith(".md")


def _docs_scan_records_inline(
    root: Path,
    *,
    max_files: int = DOCS_SCAN_MAX_FILES,
    max_file_bytes: int = DOCS_SCAN_MAX_FILE_BYTES,
    max_total_bytes: int = DOCS_SCAN_MAX_TOTAL_BYTES,
) -> list[_DocScanRecord]:
    """Return top-level markdown docs through one bounded contained scan.

    Docs picker/help catalog construction is a hot surface.  Keep it to a
    direct-child inventory, cap rows and bytes, follow only contained symlinks,
    and read just a prefix from each file for title/summary extraction.
    """

    rootp = Path(root)
    limit = None if int(max_files) < 0 else int(max_files) + 1
    try:
        entries = list_dir_contained(rootp, containment_root=rootp, limit=limit)
    except Exception:
        return []

    candidates = [entry for entry in entries if _docs_entry_is_markdown(entry)]
    candidates.sort(key=lambda entry: Path(str(entry.path)).name.casefold())
    if int(max_files) >= 0 and len(candidates) > int(max_files):
        candidates = candidates[: int(max_files)]

    out: list[_DocScanRecord] = []
    total = 0
    for entry in candidates:
        path = Path(str(entry.path))
        try:
            st = stat_path_contained(path, containment_root=rootp)
            if not st.exists or st.kind != "file":
                continue
            data = read_file_prefix_contained(
                path,
                containment_root=rootp,
                max_bytes=max(0, int(max_file_bytes)),
            ).data
        except Exception:
            continue
        total += len(data)
        if int(max_total_bytes) >= 0 and total > int(max_total_bytes):
            break
        out.append(
            _DocScanRecord(
                path=str(path),
                name=str(path.name),
                mtime=int(st.mtime),
                size=int(st.size),
                text=data.decode("utf-8", "replace"),
            )
        )
    return out


def _docs_scan_worker(
    root: str,
    max_files: int,
    max_file_bytes: int,
    max_total_bytes: int,
    queue: object,
) -> None:
    try:
        rows = [
            (rec.path, rec.name, int(rec.mtime), int(rec.size), rec.text)
            for rec in _docs_scan_records_inline(
                Path(root),
                max_files=int(max_files),
                max_file_bytes=int(max_file_bytes),
                max_total_bytes=int(max_total_bytes),
            )
        ]
        queue.put(("ok", rows))
    except BaseException as e:  # pragma: no cover - serialized to parent.
        queue.put(("err", f"{type(e).__name__}: {e}"))


def _docs_scan_records_bounded(
    root: Path,
    *,
    worker_context: multiprocessing.context.BaseContext | None = None,
) -> list[_DocScanRecord]:
    try:
        timeout = float(DOCS_SCAN_TIMEOUT_SECONDS)
    except Exception:
        timeout = 5.0
    max_files = int(DOCS_SCAN_MAX_FILES)
    max_file_bytes = int(DOCS_SCAN_MAX_FILE_BYTES)
    max_total_bytes = int(DOCS_SCAN_MAX_TOTAL_BYTES)
    if timeout <= 0:
        return _docs_scan_records_inline(
            Path(root),
            max_files=max_files,
            max_file_bytes=max_file_bytes,
            max_total_bytes=max_total_bytes,
        )

    ctx = worker_context or _docs_worker_context()
    result_budget = max(1024 * 1024, max_total_bytes * 4 + 1024 * 1024)
    proc, channel = create_one_shot_worker(
        ctx,
        target=_docs_scan_worker,
        args=(str(root), max_files, max_file_bytes, max_total_bytes),
        max_result_bytes=result_budget,
    )
    try:
        result = collect_worker_result(
            proc,
            channel,
            timeout_seconds=timeout,
            operation=f"docs catalog scan: {root}",
            require_clean_exit=True,
        )
    except WorkerResultTimeoutError as exc:
        raise FilesystemOperationTimeoutError(
            f"docs catalog scan timed out after {timeout:.3g}s: {root}"
        ) from exc
    except WorkerResultError:
        return []

    if not isinstance(result, tuple) or len(result) != 2:
        return []
    status, payload = result

    if status != "ok":
        return []
    out: list[_DocScanRecord] = []
    for row in list(payload or []):
        try:
            path, name, mtime, size, text = row
        except Exception:
            continue
        out.append(_DocScanRecord(str(path), str(name), int(mtime), int(size), str(text)))
    return out


def _fingerprint_for_records(records: list[_DocScanRecord]) -> DocsFingerprint:
    return tuple((str(rec.name), int(rec.mtime), int(rec.size)) for rec in records)


def docs_root_fingerprint(root: Path) -> DocsFingerprint:
    """Return a bounded freshness signature for direct markdown docs children."""

    key = docs_root_key(root)
    try:
        records = _docs_scan_records_bounded(root)
    except FilesystemOperationTimeoutError:
        records = []
    fingerprint = _fingerprint_for_records(records)
    _DOC_RECORD_CACHE[key] = (fingerprint, list(records), time.monotonic_ns())
    return fingerprint


def _doc_records_for_fingerprint(root: Path, fingerprint: DocsFingerprint) -> list[_DocScanRecord]:
    key = docs_root_key(root)
    cached = _DOC_RECORD_CACHE.get(key)
    if cached is not None and cached[0] == fingerprint:
        return list(cached[1])
    try:
        records = _docs_scan_records_bounded(root)
    except FilesystemOperationTimeoutError:
        records = []
    actual = _fingerprint_for_records(records)
    _DOC_RECORD_CACHE[key] = (actual, list(records), time.monotonic_ns())
    return list(records)


def _large_docs_fingerprint_is_fresh(fingerprint: DocsFingerprint, checked_ns: int, now_ns: int) -> bool:
    return bool(
        len(fingerprint) >= _LARGE_ROOT_FILE_COUNT
        and int(now_ns) - int(checked_ns) < _LARGE_ROOT_FINGERPRINT_TTL_NS
    )


def docs_root_cache_token(root: Path) -> DocsCacheToken:
    """Return the root key plus freshness signature used by docs caches."""

    key = docs_root_key(root)
    cached = _DOC_SCAN_CACHE.get(key)
    now = time.monotonic_ns()
    if cached is not None:
        fingerprint, _rows, checked_ns = cached
        if _large_docs_fingerprint_is_fresh(fingerprint, int(checked_ns), now):
            return (key, fingerprint)

    # ``docs_root_cache_token`` is called both before ``scan_docs`` has built
    # rows and from hot render/status paths that only need the freshness token.
    # Reuse the bounded scan records cache for large roots during the same TTL;
    # otherwise a long help/status render can multiply safe-but-expensive worker
    # scans even though the previous process already observed the same docs root.
    record_cached = _DOC_RECORD_CACHE.get(key)
    if record_cached is not None:
        record_fingerprint, _records, record_checked_ns = record_cached
        if _large_docs_fingerprint_is_fresh(record_fingerprint, int(record_checked_ns), now):
            if cached is not None and cached[0] == record_fingerprint:
                _DOC_SCAN_CACHE[key] = (record_fingerprint, cached[1], int(record_checked_ns))
            return (key, record_fingerprint)

    fingerprint = docs_root_fingerprint(root)
    checked_after = time.monotonic_ns()
    cached = _DOC_SCAN_CACHE.get(key)
    if cached is not None and cached[0] == fingerprint:
        _DOC_SCAN_CACHE[key] = (fingerprint, cached[1], checked_after)
    return (key, fingerprint)


def clear_docs_scan_cache() -> None:
    """Clear process-local docs scan state; mostly useful for tests/tools."""

    _DOC_SCAN_CACHE.clear()
    _DOC_RECORD_CACHE.clear()


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
    """Return stable subject text rather than a leading revision breadcrumb.

    Living Micromax docs intentionally carry short ``Rev####`` / ``Latest ...
    (rev####)`` landing paragraphs near the primary heading. Those paragraphs
    are useful provenance but poor picker summaries: they churn every revision
    and can hide the document's durable subject. Once a banner starts, skip its
    whole Markdown paragraph, including wrapped continuation/link lines.
    """

    skip_revision_paragraph = False
    for i, line in enumerate(lines[int(start) :], int(start)):
        s = line.strip()
        if not s:
            skip_revision_paragraph = False
            continue
        if skip_revision_paragraph:
            continue
        if i in heading_line_idxs or _SETEXT_UNDERLINE_RE.match(s) is not None:
            continue
        if s.startswith("#"):
            continue
        if _REVISION_BANNER_RE.match(s) is not None:
            skip_revision_paragraph = True
            continue
        return s
    return ""


def _scan_doc_text(path: Path, text: str, heading_scan: HeadingScan) -> DocEntry:
    stem = path.stem
    slug = re.sub(r"^\d+\-", "", stem)
    topic = slug or stem
    title = ""
    summary = ""
    try:
        lines = str(text or "").splitlines()
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


def _scan_doc_record(record: _DocScanRecord, heading_scan: HeadingScan) -> DocEntry:
    return _scan_doc_text(Path(record.path), str(record.text), heading_scan)


def _scan_doc_file(path: Path, heading_scan: HeadingScan) -> DocEntry:
    # Compatibility fallback for older local experiments that imported this
    # private helper directly.  ``scan_docs`` uses bounded scan records instead;
    # keep the fallback on the same contained prefix-read seam rather than
    # reviving ambient ``Path.read_text`` in a private escape hatch.
    p = Path(path)
    try:
        data = read_file_prefix_contained(
            p,
            containment_root=p.parent,
            max_bytes=int(DOCS_SCAN_MAX_FILE_BYTES),
        ).data
        txt = data.decode("utf-8", "replace")
    except Exception:
        txt = ""
    return _scan_doc_text(p, txt, heading_scan)


def scan_docs(root: Path, heading_scan: HeadingScan) -> list[DocEntry]:
    """Return docs entries with process-cache reuse and freshness checks."""

    key, fingerprint = docs_root_cache_token(root)
    cached = _DOC_SCAN_CACHE.get(key)
    if cached is not None and cached[0] == fingerprint:
        return _copy_doc_entries(cached[1])

    records = _doc_records_for_fingerprint(root, fingerprint)
    out = [_scan_doc_record(record, heading_scan) for record in records]
    if records or fingerprint:
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
