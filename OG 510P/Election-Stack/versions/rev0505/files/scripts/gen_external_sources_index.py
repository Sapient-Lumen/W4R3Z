#!/usr/bin/env python3
"""scripts/gen_external_sources_index.py

Generate compact, no-URL views of external sources pinned in:
  evidence/lock/external-sources.toml

Outputs:
- docs/214-external-sources-index.md
  Flat table of all lockfile IDs (generated; no URLs).

- docs/230-external-sources-by-primary-tag.md
  The same sources grouped by *primary tag* (the first tag in each entry).
  Each source appears exactly once to avoid archive bloat.

- docs/EXTERNAL_SOURCE_REVIEW_QUEUE.md
  A tiny, actionable queue of *unpinned* entries sorted by review_by date,
  with lightweight "load-bearing" signals (in-repo citation counts + top
  referencing docs). This is a maintainer aid; it does not change policy.

Rationale:
- keep the archive size-disciplined (do not bundle third-party artifacts)
- reduce citation friction (surface lockfile IDs + brief notes)
- prevent silent drift in hand-maintained "citation map" docs

This generator is intentionally small and uses stdlib-only TOML parsing.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from _shared.md_scan import iter_markdown_files

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "evidence" / "lock" / "external-sources.toml"
OUT_FLAT = ROOT / "docs" / "214-external-sources-index.md"
OUT_TAG = ROOT / "docs" / "230-external-sources-by-primary-tag.md"
OUT_QUEUE = ROOT / "docs" / "EXTERNAL_SOURCE_REVIEW_QUEUE.md"
REVIEW_QUEUE_MAX_ROWS = 3

CITE_RE = re.compile(r"\b(?:source|xref):\s*([A-Za-z0-9_]+)\b")


def load_lockfile() -> list[dict]:
    if not LOCK.exists():
        print(f"ERROR: missing lockfile: {LOCK}", file=sys.stderr)
        raise SystemExit(2)

    try:
        import tomllib  # py3.11+
    except Exception as e:  # pragma: no cover
        print(f"ERROR: tomllib unavailable: {e}", file=sys.stderr)
        raise SystemExit(2)

    data = tomllib.loads(LOCK.read_text(encoding="utf-8"))
    sources = data.get("source", [])
    if not isinstance(sources, list):
        print("ERROR: lockfile parse: expected [[source]] list", file=sys.stderr)
        raise SystemExit(2)
    return sources


def iter_citation_files() -> list[Path]:
    return iter_markdown_files(ROOT)


def citation_counts() -> dict[str, int]:
    """Count lockfile citation occurrences across markdown.

    Purpose: when prioritizing *unpinned* sources, citations are a lightweight
    proxy for "load-bearing" usage.
    """

    counts: dict[str, int] = {}
    for p in iter_citation_files():
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            continue
        for m in CITE_RE.finditer(text):
            sid = m.group(1)
            counts[sid] = counts.get(sid, 0) + 1
    return counts


def citation_files_index() -> dict[str, set[str]]:
    """Return sid -> set(relpath) for markdown files referencing that sid."""

    idx: dict[str, set[str]] = {}
    for p in iter_citation_files():
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            continue
        rel = ""
        try:
            rel = p.relative_to(ROOT).as_posix()
        except Exception:
            continue
        for m in CITE_RE.finditer(text):
            sid = m.group(1)
            idx.setdefault(sid, set()).add(rel)
    return idx


def norm_tags(tags) -> str:
    if not tags:
        return ""
    if isinstance(tags, list):
        return ",".join([str(x).strip() for x in tags if str(x).strip()])
    return str(tags).strip()


def brief_note(note: str, limit: int = 12) -> str:
    note = (note or '').strip().replace("\n", ' ')
    if len(note) <= limit:
        return note
    if limit <= 1:
        return note[:limit]
    return note[: limit - 1].rstrip() + '…'


PRIORITY_WEIGHTS: dict[str, int] = {
    # Higher = pin sooner (normative/authority first).
    "law": 6,
    "regulation": 6,
    "vvsg": 6,
    "eac": 6,
    "cdf": 5,
    "nist": 5,
    "rfc": 5,
    "cisa": 4,
    "audit": 4,
    "rla": 4,
    "supply_chain": 3,
    "slsa": 3,
    "provenance": 2,
    "disinformation": 2,
    "comms": 1,
    "operations": 1,
    "randomness": 1,
    "beacon": 1,
}


def score_source(tags: str, note: str) -> int:
    """Heuristic priority score for unpinned sources.

    Goal: keep the generated index *tight* but still highlight which unpinned
    sources matter most to pin for drift-resistance.

    Note: final ranking also considers in-repo citation counts.
    """

    tset = {t.strip() for t in (tags or "").split(",") if t.strip()}
    score = sum(PRIORITY_WEIGHTS.get(t, 0) for t in tset)
    n = (note or "").lower()
    if "authoritative" in n or "normative" in n:
        score += 2
    if "statut" in n or "binding" in n:
        score += 2
    return score


def combined_priority(base_score: int, cite_count: int) -> int:
    """Combine tag-based scoring with citation-based load-bearing signal."""

    # Tag score dominates; citations break ties.
    return base_score * 10 + min(cite_count, 20)


def write_flat_index(rows: list[tuple[str, str, str, str, str, str, str]], cites: dict[str, int]) -> None:
    rows = sorted(rows, key=lambda r: r[0])

    lines: list[str] = []
    lines.append("# 214. External sources index (lockfile IDs, no URLs)")
    lines.append("")
    lines.append("**Track:** Shared")
    lines.append("")
    lines.append("")
    lines.append(
        "Generated from `evidence/lock/external-sources.toml`. This index is intentionally **no‑URL** to reduce link rot and avoid bundling third‑party artifacts."
    )
    lines.append("")
    lines.append(
        "How to cite in docs: `source: <id>`. The **canonical exhaustive list** lives in `evidence/lock/external-sources.toml`; this page is the intentionally compact reading/triage view."
    )
    lines.append("")

    pinned_count = sum(1 for _, pinned, _, _, _, _, _ in rows if pinned == "yes")
    unpinned_count = len(rows) - pinned_count

    tag_counts: dict[str, int] = {}
    for _sid, _pinned, _retrieved, _exemption, _review_by, tags, _note in rows:
        primary = "untagged"
        if tags:
            primary = tags.split(",", 1)[0].strip() or "untagged"
        tag_counts[primary] = tag_counts.get(primary, 0) + 1
    top_tags = sorted(tag_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:10]

    pin_first: list[tuple[int, int, str, str, str, str]] = []
    for sid, pinned, retrieved, exemption, review_by, tags, note in rows:
        if pinned == "no":
            base = score_source(tags, note)
            cc = cites.get(sid, 0)
            pr = combined_priority(base, cc)
            if pr > 0:
                pin_first.append((pr, cc, sid, retrieved, review_by, tags))
    pin_first.sort(key=lambda x: (-x[0], -x[1], x[2]))

    recent = sorted(rows, key=lambda r: (r[2], r[0]), reverse=True)[:8]

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total sources: {len(rows)} (pinned: {pinned_count}; unpinned: {unpinned_count}).")
    lines.append("- Exhaustive lookup lives in `evidence/lock/external-sources.toml`; use this page for quick maintainer orientation only.")
    lines.append("- Maintainer queue (generated): see `docs/EXTERNAL_SOURCE_REVIEW_QUEUE.md`.")
    if top_tags:
        lines.append("- Largest primary-tag groups: " + ", ".join([f"`{tag}`={count}" for tag, count in top_tags]) + ".")
    lines.append("")

    if pin_first:
        lines.append("## Pin-first candidates (highest leverage unpinned IDs)")
        lines.append("")
        lines.append("| id | retrieved | review_by | refs | tags |")
        lines.append("|---|---|---|---:|---|")
        for _pr, cc, sid, retrieved, review_by, tags in pin_first[:10]:
            lines.append(f"| `{sid}` | {retrieved} | {review_by} | {cc} | {tags} |")
        lines.append("")

    lines.append("## Recent source additions / touchpoints")
    lines.append("")
    lines.append("| id | pinned | retrieved | review_by | tags |")
    lines.append("|---|---|---|---|---|")
    for sid, pinned, retrieved, _exemption, review_by, tags, _note in recent:
        lines.append(f"| `{sid}` | {pinned} | {retrieved} | {review_by} | {tags} |")
    lines.append("")
    lines.append("For full per-ID details (including URLs, notes, and hashes), use `evidence/lock/external-sources.toml` directly.")

    OUT_FLAT.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_primary_tag_index(rows: list[dict]) -> None:
    """Write a compact primary-tag summary.

    The canonical exhaustive per-ID list lives in the lockfile and the compact
    `docs/214` view; this page is a bounded triage summary to keep archive size
    under control.
    """

    groups: dict[str, list[tuple[str, str, str]]] = {}
    for s in rows:
        sid = str(s.get("id", "")).strip()
        if not sid:
            continue
        sha = str(s.get("sha256", "")).strip()
        pinned = "yes" if sha else "no"
        review_by = str(s.get("review_by", "")).strip()

        tags = s.get("tags")
        primary = "untagged"
        if isinstance(tags, list) and tags:
            primary = str(tags[0]).strip() or "untagged"
        elif isinstance(tags, str) and tags.strip():
            primary = tags.strip().split(",", 1)[0].strip() or "untagged"

        groups.setdefault(primary, []).append((sid, pinned, review_by))

    lines: list[str] = []
    lines.append("# 230. External sources by primary tag (lockfile IDs, no URLs)")
    lines.append("")
    lines.append("**Track:** Shared")
    lines.append("")
    lines.append("")
    lines.append(
        "Generated from `evidence/lock/external-sources.toml`. Primary tag = the first element of each entry's `tags[]` list."
    )
    lines.append("")
    lines.append(
        "Purpose: bounded tag-grouped triage without duplicating the full lockfile. Exhaustive per-ID lookup lives in `evidence/lock/external-sources.toml`; the compact flat view lives in `docs/214`."
    )
    lines.append("")
    lines.append("| primary tag | total | pinned | unpinned | next review_by | example ids |")
    lines.append("|---|---:|---:|---:|---|---|")

    def _rb_key(v: str) -> str:
        return v if re.fullmatch(r"\d{4}-\d{2}-\d{2}", v or "") else "9999-12-31"

    for tag in sorted(groups.keys()):
        items = sorted(groups[tag], key=lambda r: r[0])
        pinned_count = sum(1 for _sid, p, _rb in items if p == "yes")
        unpinned = len(items) - pinned_count
        review_dates = [_rb for _sid, _p, _rb in items if _rb_key(_rb) != "9999-12-31"]
        next_review = sorted(review_dates)[0] if review_dates else ""
        examples = ", ".join([f"`{sid}`" for sid, _p, _rb in items[:3]])
        if len(items) > 3:
            examples += f"; (+{len(items)-3} more)"
        lines.append(f"| {tag} | {len(items)} | {pinned_count} | {unpinned} | {next_review} | {examples} |")

    OUT_TAG.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


DOC_BASENAME_RE = re.compile(r"^(\d{1,3})[-_].*\.md$")


def _sort_doc_refs(refs: list[str]) -> list[str]:
    def key(rel: str):
        base = rel.rsplit("/", 1)[-1]
        m = DOC_BASENAME_RE.match(base)
        if m:
            return (0, int(m.group(1)), rel)
        return (1, 9999, rel)

    return sorted(refs, key=key)


def write_review_queue(sources: list[dict], cites: dict[str, int], file_index: dict[str, set[str]]) -> None:
    """Write a small, actionable queue of unpinned entries.

    This is intentionally *non-policy*: it helps maintainers triage what to pin
    or re-review, but does not introduce new requirements.
    """

    rows: list[tuple[str, str, str, str, str, int, int, list[str], int]] = []
    # tuple: (review_by, sid, exemption, retrieved, tags, priority, cite_count, top_doc_refs, other_files)

    for s in sources:
        if not isinstance(s, dict):
            continue
        sid = str(s.get("id", "")).strip()
        if not sid:
            continue
        sha = str(s.get("sha256", "")).strip()
        if sha:
            continue  # pinned entries are not in the queue

        retrieved = str(s.get("retrieved", "")).strip()
        exemption = str(s.get("pin_exemption", "")).strip()
        review_by = str(s.get("review_by", "")).strip()
        tags = norm_tags(s.get("tags"))
        note = str(s.get("note", "")).strip()

        base = score_source(tags, note)
        cc = cites.get(sid, 0)
        pr = combined_priority(base, cc)

        files = sorted(file_index.get(sid, set()))
        doc_refs = [f for f in files if f.startswith("docs/") and DOC_BASENAME_RE.match(f.rsplit("/", 1)[-1] or "")]
        other = len(files) - len(doc_refs)
        doc_refs = _sort_doc_refs(doc_refs)
        top_docs = doc_refs[:6]

        rb_sort = review_by if re.fullmatch(r"\d{4}-\d{2}-\d{2}", review_by or "") else "9999-12-31"
        rows.append((rb_sort, sid, exemption, retrieved, tags, pr, cc, top_docs, other))

    # Sort by review date first, then priority (descending), then id.
    rows.sort(key=lambda r: (r[0], -r[5], -r[6], r[1]))

    lines: list[str] = []
    lines.append("# External source review queue (generated; no URLs)")
    lines.append("")
    lines.append("**Track:** Shared")
    lines.append("")
    lines.append("")
    lines.append("Generated from `evidence/lock/external-sources.toml`.")
    lines.append("")
    lines.append("Purpose: keep unpinned-source drift risk **visible and bounded** without expanding the archive.")
    lines.append("")
    lines.append("Notes:")
    lines.append("- Sorted by `review_by` (earliest first), then by a small heuristic priority score.")
    lines.append("- `refs` counts total `source:` + `xref:` occurrences across in-repo markdown.")
    lines.append("- `docs` shows up to 6 numbered docs that reference the ID.")
    lines.append(f"- Output is intentionally capped to the first {REVIEW_QUEUE_MAX_ROWS} actionable rows to keep the archive size-disciplined; use the lockfile directly for exhaustive triage.")
    lines.append("")

    if not rows:
        lines.append("No unpinned entries found.")
        OUT_QUEUE.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
        return

    lines.append(f"Unpinned entries: {len(rows)}")
    lines.append("")

    visible = rows[:REVIEW_QUEUE_MAX_ROWS]
    hidden = rows[REVIEW_QUEUE_MAX_ROWS:]
    if hidden:
        by_exemption: dict[str, int] = {}
        for _review_by, _sid, exemption, *_rest in hidden:
            by_exemption[exemption or "unspecified"] = by_exemption.get(exemption or "unspecified", 0) + 1
        parts = [f"{k}={by_exemption[k]}" for k in sorted(by_exemption)]
        lines.append(f"Visible rows: {len(visible)} (remaining summarized: {len(hidden)}; {'; '.join(parts)})")
        lines.append("")

    lines.append("| review_by | id | exemption | retrieved | refs | tags | docs (top) |")
    lines.append("|---|---|---|---|---:|---|---|")

    for review_by, sid, exemption, retrieved, tags, _pr, cc, top_docs, other in visible:
        rb = "" if review_by == "9999-12-31" else review_by
        docs = ", ".join([f"`DOC:{d}`" for d in top_docs]) if top_docs else ""
        if other:
            docs = (docs + ("; " if docs else "") + f"(+{other} other)")
        lines.append(f"| {rb} | `{sid}` | {exemption} | {retrieved} | {cc} | {tags} | {docs} |")

    OUT_QUEUE.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    sources = load_lockfile()
    cites = citation_counts()
    idx = citation_files_index()

    # Flat rows (for docs/214).
    flat_rows: list[tuple[str, str, str, str, str, str, str]] = []
    for s in sources:
        if not isinstance(s, dict):
            continue
        sid = str(s.get("id", "")).strip()
        if not sid:
            continue
        sha = str(s.get("sha256", "")).strip()
        pinned = "yes" if sha else "no"
        retrieved = str(s.get("retrieved", "")).strip()
        note = str(s.get("note", "")).strip().replace("\n", " ")
        tags = norm_tags(s.get("tags")).replace("\n", " ")
        exemption = str(s.get("pin_exemption", "")).strip()
        review_by = str(s.get("review_by", "")).strip()
        flat_rows.append((sid, pinned, retrieved, exemption, review_by, tags, note))

    write_flat_index(flat_rows, cites)
    write_primary_tag_index(sources)
    write_review_queue(sources, cites, idx)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
