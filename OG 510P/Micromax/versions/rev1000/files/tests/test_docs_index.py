from __future__ import annotations

from pathlib import Path

from micromax_editor import docs_index
from micromax_editor.docs_index import (
    build_doc_prompt_state,
    build_docs_catalog,
    docs_root_from_env,
    scan_docs,
)


def _tiny_heading_scan(lines: list[object]) -> list[tuple[int, int, int, str, str, int]]:
    out: list[tuple[int, int, int, str, str, int]] = []
    for i, line in enumerate(lines):
        text = str(line)
        if text.startswith("# "):
            out.append((i, i + 1, 1, text[2:].strip(), "", 2))
    return out


def test_docs_root_from_env_keeps_relative_paths_repo_local(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)

    assert docs_root_from_env(None) == tmp_path / "docs"
    assert docs_root_from_env("alt-docs") == tmp_path / "alt-docs"


def test_scan_docs_extracts_title_summary_and_catalog_keys(tmp_path: Path) -> None:
    root = tmp_path / "docs"
    root.mkdir()
    doc = root / "704-risky-change.md"
    doc.write_text("# Risky Change\n\nFirst useful summary.\n", encoding="utf-8")

    rows = scan_docs(root, _tiny_heading_scan)
    catalog = build_docs_catalog(rows)

    assert rows == [
        {
            "topic": "risky-change",
            "path": str(doc),
            "title": "Risky Change",
            "summary": "First useful summary.",
        }
    ]
    assert catalog["risky-change"]["path"] == str(doc)
    assert catalog["704-risky-change.md"]["topic"] == "risky-change"
    assert catalog[str(doc).casefold()]["title"] == "Risky Change"


def test_build_doc_prompt_state_keeps_rows_and_lookup_caches(tmp_path: Path) -> None:
    path = tmp_path / "docs" / "704-risky-change.md"
    entries = [
        {
            "topic": "risky-change",
            "path": str(path),
            "title": "Risky Change",
            "summary": "First useful summary.",
        }
    ]

    state = build_doc_prompt_state(
        entries,
        section_info_for_path=lambda p: (700, "700+ Audit"),
        normalize_path=lambda p: f"norm:{p}",
    )

    assert state.rows == [["risky-change", "doc", "Risky Change", "First useful summary."]]
    assert state.section_labels == {"risky-change": "700+ Audit"}
    assert state.section_ranks == {"700+ Audit": 700}
    assert state.detail_rows_by_topic["risky-change"] == [
        "risky-change",
        "Risky Change",
        "First useful summary.",
        "700+ Audit",
        str(path),
    ]
    assert state.detail_rows_by_norm_path[f"norm:{path}"][0] == "risky-change"


def test_build_doc_prompt_state_preserves_editor_section_sort_order(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    entries = [
        {"topic": "zeta", "path": str(docs / "90-zeta.md"), "title": "Zeta", "summary": ""},
        {"topic": "beta", "path": str(docs / "10-beta.md"), "title": "Beta", "summary": ""},
        {"topic": "alpha", "path": str(docs / "10-alpha.md"), "title": "Alpha", "summary": ""},
    ]

    state = build_doc_prompt_state(entries, normalize_path=lambda p: p)

    assert [row[0] for row in state.rows] == ["alpha", "beta", "zeta"]
    assert state.section_labels["alpha"] == "10–19 Research"
    assert state.section_labels["zeta"] == "90–99 Advanced notes"


def test_scan_docs_fast_title_summary_handles_multiline_setext(tmp_path: Path) -> None:
    root = tmp_path / "docs"
    root.mkdir()
    doc = root / "106-multiline-setext-headings.md"
    doc.write_text(
        "Multi-line setext\nheading demo\n==================\n\nSummary after underline.\n",
        encoding="utf-8",
    )

    rows = scan_docs(root, _tiny_heading_scan)

    assert rows[0]["topic"] == "multiline-setext-headings"
    assert rows[0]["title"] == "Multi-line setext heading demo"
    assert rows[0]["summary"] == "Summary after underline."


def test_scan_docs_summary_skips_wrapped_revision_banner_paragraphs(tmp_path: Path) -> None:
    root = tmp_path / "docs"
    root.mkdir()
    doc = root / "00-vision.md"
    doc.write_text(
        "# Vision\n\n"
        "Rev0955 makes the current landing explicit and wraps onto\n"
        "another line. See\n"
        "`docs/913-current.md`.\n\n"
        "## Mission\n\n"
        "Stable mission sentence.\n",
        encoding="utf-8",
    )

    rows = scan_docs(root, _tiny_heading_scan)

    assert rows[0]["title"] == "Vision"
    assert rows[0]["summary"] == "Stable mission sentence."


def test_scan_docs_summary_skips_latest_landing_paragraph(tmp_path: Path) -> None:
    root = tmp_path / "docs"
    root.mkdir()
    doc = root / "01-guide.md"
    doc.write_text(
        "# Guide\n\n"
        "Latest tiny landing (rev955): transient archive bookkeeping.\n\n"
        "Durable guide summary.\n",
        encoding="utf-8",
    )

    rows = scan_docs(root, _tiny_heading_scan)

    assert rows[0]["summary"] == "Durable guide summary."


def test_scan_docs_summary_keeps_latest_text_without_revision_marker(tmp_path: Path) -> None:
    root = tmp_path / "docs"
    root.mkdir()
    doc = root / "02-latest.md"
    doc.write_text(
        "# Latest guidance\n\n"
        "Latest stable guidance for operators.\n",
        encoding="utf-8",
    )

    rows = scan_docs(root, _tiny_heading_scan)

    assert rows[0]["summary"] == "Latest stable guidance for operators."


def test_scan_docs_fast_title_summary_ignores_fenced_headings(tmp_path: Path) -> None:
    root = tmp_path / "docs"
    root.mkdir()
    doc = root / "999-fence.md"
    doc.write_text(
        "```\n# Not the title\n```\n\n# Real title\n\nReal summary.\n",
        encoding="utf-8",
    )

    rows = scan_docs(root, _tiny_heading_scan)

    assert rows[0]["title"] == "Real title"
    assert rows[0]["summary"] == "Real summary."


def test_docs_cache_token_checks_small_docs_roots_strictly(monkeypatch, tmp_path: Path) -> None:
    docs_index.clear_docs_scan_cache()
    root = tmp_path / "docs"
    root.mkdir()
    doc = root / "01-alpha.md"
    doc.write_text("# Alpha\n", encoding="utf-8")
    calls = 0
    original_fingerprint = docs_index.docs_root_fingerprint

    def counted_fingerprint(root_arg: Path):
        nonlocal calls
        calls += 1
        return original_fingerprint(root_arg)

    monkeypatch.setattr(docs_index, "docs_root_fingerprint", counted_fingerprint)
    monkeypatch.setattr(docs_index.time, "monotonic_ns", lambda: 100_000_000_000)

    docs_index.scan_docs(root, lambda _rows: [])
    calls = 0
    first = docs_index.docs_root_cache_token(root)
    doc.write_text("# Alpha Changed\n", encoding="utf-8")
    second = docs_index.docs_root_cache_token(root)

    assert calls == 2
    assert first != second


def test_docs_cache_token_uses_hot_cache_for_large_docs_root(monkeypatch, tmp_path: Path) -> None:
    docs_index.clear_docs_scan_cache()
    root = tmp_path / "docs"
    root.mkdir()
    records = [(f"{idx:03d}-doc.md", idx, 1000 + idx) for idx in range(133)]
    calls = 0
    now = 100_000_000_000

    def fake_fingerprint(root_arg: Path):
        nonlocal calls
        assert root_arg == root
        calls += 1
        return tuple(records)

    monkeypatch.setattr(docs_index, "docs_root_fingerprint", fake_fingerprint)
    monkeypatch.setattr(docs_index.time, "monotonic_ns", lambda: now)

    docs_index.scan_docs(root, lambda _rows: [])
    calls = 0
    first = docs_index.docs_root_cache_token(root)
    records.append(("999-late.md", 99, 9999))
    now = 100_010_000_000
    second = docs_index.docs_root_cache_token(root)
    now = 101_500_000_000
    third = docs_index.docs_root_cache_token(root)

    assert calls == 1
    assert first == second
    assert third != second


def test_scan_docs_avoids_direct_glob_and_read_text(monkeypatch, tmp_path: Path) -> None:
    docs_index.clear_docs_scan_cache()
    root = tmp_path / "docs"
    root.mkdir()
    doc = root / "02-bounded.md"
    doc.write_text("# Bounded Docs\n\nCatalog summary.\n", encoding="utf-8")

    def forbidden_glob(self: Path, pattern: str):  # type: ignore[no-untyped-def]
        raise AssertionError("docs catalog must not use Path.glob")

    def forbidden_read_text(self: Path, *args, **kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("docs catalog must not use Path.read_text")

    monkeypatch.setattr(Path, "glob", forbidden_glob)
    monkeypatch.setattr(Path, "read_text", forbidden_read_text)

    rows = scan_docs(root, _tiny_heading_scan)

    assert rows[0]["topic"] == "bounded"
    assert rows[0]["title"] == "Bounded Docs"
    assert rows[0]["summary"] == "Catalog summary."




def test_private_scan_doc_file_uses_contained_prefix_read(monkeypatch, tmp_path: Path) -> None:
    doc = tmp_path / "04-private-fallback.md"
    doc.write_text("# Private Fallback\n\nStill bounded.\n", encoding="utf-8")

    def forbidden_read_text(self: Path, *args, **kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("private docs fallback must not use Path.read_text")

    monkeypatch.setattr(Path, "read_text", forbidden_read_text)

    row = docs_index._scan_doc_file(doc, _tiny_heading_scan)

    assert row["topic"] == "private-fallback"
    assert row["title"] == "Private Fallback"
    assert row["summary"] == "Still bounded."


def test_scan_docs_uses_prefix_budget_without_dropping_large_docs(monkeypatch, tmp_path: Path) -> None:
    docs_index.clear_docs_scan_cache()
    root = tmp_path / "docs"
    root.mkdir()
    doc = root / "03-large.md"
    doc.write_text("# Large Doc\n\nSmall visible summary.\n" + ("x" * 4096), encoding="utf-8")
    monkeypatch.setattr(docs_index, "DOCS_SCAN_MAX_FILE_BYTES", 128)

    rows = scan_docs(root, _tiny_heading_scan)

    assert rows[0]["topic"] == "large"
    assert rows[0]["title"] == "Large Doc"
    assert rows[0]["summary"] == "Small visible summary."


def test_scan_docs_reuses_recent_large_scan_records_between_token_and_rows(monkeypatch, tmp_path: Path) -> None:
    docs_index.clear_docs_scan_cache()
    root = tmp_path / "docs"
    root.mkdir()
    for idx in range(3):
        (root / f"{idx:02d}-doc.md").write_text(f"# Doc {idx}\n\nSummary {idx}.\n", encoding="utf-8")

    calls = 0
    original_scan = docs_index._docs_scan_records_bounded

    def counted_scan(root_arg: Path):  # type: ignore[no-untyped-def]
        nonlocal calls
        calls += 1
        return original_scan(root_arg)

    monkeypatch.setattr(docs_index, "_LARGE_ROOT_FILE_COUNT", 2)
    monkeypatch.setattr(docs_index, "_LARGE_ROOT_FINGERPRINT_TTL_NS", 1_000_000_000)
    monkeypatch.setattr(docs_index, "_docs_scan_records_bounded", counted_scan)

    first = docs_index.docs_root_cache_token(root)
    rows = scan_docs(root, _tiny_heading_scan)
    second = docs_index.docs_root_cache_token(root)

    assert calls == 1
    assert first == second
    assert [row["topic"] for row in rows] == ["doc", "doc", "doc"]
