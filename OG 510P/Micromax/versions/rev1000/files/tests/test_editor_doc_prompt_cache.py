from __future__ import annotations

import os
from pathlib import Path

from micromax_editor.editor import Editor


def _help_query_with_many_doc_candidates(minimum: int = 10) -> str:
    """Return a live docs query that exercises a large doc completion batch.

    The old regression used ``help phn`` because that once produced many doc
    rows.  The docs corpus is intentionally changing every revision, so the
    test should prove the cache budget rather than depend on one stale token.
    """

    candidates = (
        'port',
        'plugin',
        'macro',
        'help',
        'doc',
        'show',
        'command',
        'mode',
        'buffer',
        'mxtest',
    )
    for query in candidates:
        ed = Editor()
        ed.enter_prompt('command', prefill=f'help {query}')
        assert ed.prompt is not None
        if not ed.prompt_complete(direction=1):
            continue
        doc_rows = [
            row
            for row in ed.prompt.suggestion_rows
            if len(row) >= 2 and row[1] == 'doc'
        ]
        if len(doc_rows) >= minimum:
            return query
    raise AssertionError(f'no docs completion query produced {minimum} rows')


def test_doc_prompt_rows_reuses_cached_rows_without_re_normalizing_paths(monkeypatch) -> None:
    ed = Editor()
    calls = 0
    original = ed._normalize_path

    def counted(path: str) -> str | None:
        nonlocal calls
        calls += 1
        return original(path)

    monkeypatch.setattr(ed, '_normalize_path', counted)

    first = ed.doc_prompt_rows()
    first_calls = calls
    calls = 0
    second = ed.doc_prompt_rows()

    assert first
    assert first == second
    assert first_calls >= len(first)
    assert calls == 0
    assert getattr(ed, '_doc_detail_rows_by_topic', {})


def test_scan_docs_reuses_process_cache_across_editor_instances(monkeypatch) -> None:
    first_editor = Editor()
    first = first_editor._scan_docs()
    assert first

    def fail_read_text(self: Path, *args, **kwargs) -> str:
        raise AssertionError(f'unexpected docs reread: {self}')

    monkeypatch.setattr(Path, 'read_text', fail_read_text)

    second_editor = Editor()
    second = second_editor._scan_docs()

    assert second == first


def test_doc_prompt_rows_invalidates_when_docs_file_changes(tmp_path, monkeypatch) -> None:
    doc = tmp_path / '01-alpha.md'
    doc.write_text('# Alpha\n\nfirst summary\n', encoding='utf-8')
    monkeypatch.setenv('MICROMAX_DOCS', str(tmp_path))

    ed = Editor()
    first = ed.doc_prompt_rows()
    assert first == [['alpha', 'doc', 'Alpha', 'first summary']]

    # Force a signature change even on filesystems with coarse timestamp
    # precision so the process-local docs cache must reread this root.
    old_mtime = doc.stat().st_mtime_ns
    doc.write_text('# Alpha Prime\n\nsecond summary\n', encoding='utf-8')
    os.utime(doc, ns=(old_mtime + 2_000_000_000, old_mtime + 2_000_000_000))

    second = ed.doc_prompt_rows()

    assert second == [['alpha', 'doc', 'Alpha Prime', 'second summary']]
    assert ed._help_doc_title_for_target('alpha') == 'Alpha Prime'


def test_scan_docs_invalidates_across_editor_instances_when_docs_file_changes(tmp_path, monkeypatch) -> None:
    doc = tmp_path / '10-topic.md'
    doc.write_text('# Topic\n\nold\n', encoding='utf-8')
    monkeypatch.setenv('MICROMAX_DOCS', str(tmp_path))

    first_editor = Editor()
    assert first_editor._scan_docs()[0]['summary'] == 'old'

    old_mtime = doc.stat().st_mtime_ns
    doc.write_text('# Topic\n\nnew\n', encoding='utf-8')
    os.utime(doc, ns=(old_mtime + 2_000_000_000, old_mtime + 2_000_000_000))

    second_editor = Editor()

    assert second_editor._scan_docs()[0]['summary'] == 'new'



def test_help_topic_completion_warms_doc_rows_once_for_many_doc_candidates(monkeypatch) -> None:
    ed = Editor()
    query = _help_query_with_many_doc_candidates()
    ed.enter_prompt('command', prefill=f'help {query}')
    assert ed.prompt is not None

    calls = 0
    original = ed.doc_prompt_rows

    def counted(*args, **kwargs):
        nonlocal calls
        calls += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(ed, 'doc_prompt_rows', counted)

    assert ed.prompt_complete(direction=1)
    assert ed.prompt is not None
    doc_rows = [row for row in ed.prompt.suggestion_rows if len(row) >= 2 and row[1] == 'doc']
    assert len(doc_rows) >= 10
    assert calls <= 1


def test_help_topic_completion_warms_doc_rows_once_for_row_batch(monkeypatch) -> None:
    ed = Editor()
    calls = 0
    original = ed.doc_prompt_rows

    def counted() -> list[list[str]]:
        nonlocal calls
        calls += 1
        return original()

    monkeypatch.setattr(ed, 'doc_prompt_rows', counted)

    query = _help_query_with_many_doc_candidates()
    ed.enter_prompt('command', prefill=f'help {query}')
    assert ed.prompt_complete(direction=1)

    assert calls == 1
    assert ed.prompt is not None
    doc_rows = [row for row in ed.prompt.suggestion_rows if len(row) >= 2 and row[1] == 'doc']
    assert len(doc_rows) >= 10
    assert ed.prompt.suggestions


def test_cd_clears_docs_root_and_display_path_caches(tmp_path, monkeypatch) -> None:
    first = tmp_path / 'first'
    second = tmp_path / 'second'
    first.mkdir()
    second.mkdir()
    monkeypatch.chdir(first)

    ed = Editor()
    assert ed.docs_root() == first / 'docs'
    assert ed._display_path(str(first / 'alpha.txt')) == 'alpha.txt'

    assert ed.exec_command_line(f'cd {second}')

    assert ed.docs_root() == second / 'docs'
    assert ed._display_path(str(second / 'beta.txt')) == 'beta.txt'
