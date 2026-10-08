from __future__ import annotations

import json
from pathlib import Path

import pytest

from micromax_editor.__main__ import main


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_main_help_describes_the_current_editor_product(capsys) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])

    assert exc_info.value.code == 0
    output = capsys.readouterr().out
    assert "calm, scriptable editor with explicit effects and headless truth" in output
    assert "reference curses TUI" in output
    assert "prototype" not in output.lower()


def test_main_headless_repl_unknown_command_is_typed(tmp_path, capsys, monkeypatch) -> None:
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.setenv('MICROMAX_INIT', str(tmp_path / 'missing-init.mx'))

    lines = iter([':bogus', ':q'])
    monkeypatch.setattr('builtins.input', lambda _prompt='': next(lines))

    rc = main(['--plugins', str(REPO_ROOT / 'plugins')])

    assert rc == 0
    out_lines = capsys.readouterr().out.splitlines()
    assert 'repl: no such command: :bogus' in out_lines


def test_main_dump_screen_opens_plain_file_and_prints_json(tmp_path, capsys, monkeypatch) -> None:
    sample = tmp_path / 'sample.txt'
    sample.write_text('alpha\nbeta\n', encoding='utf-8')
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.setenv('MICROMAX_INIT', str(tmp_path / 'missing-init.mx'))

    rc = main([
        str(sample),
        '--plugins', str(REPO_ROOT / 'plugins'),
        '--dump-screen', '8', '40',
    ])

    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data['schema'] == 'micromax.screen.v1'
    assert data['size'] == {'lines': 8, 'cols': 40}
    assert len(data['rows']) == 8
    assert data['rows'][0]['text'].startswith('alpha')
    assert data['rows'][0]['source']['line'] == 0
    assert data['cursor']['visible'] is True
    bottom_texts = [
        row['text']
        for row in data['rows']
        if row['kind'] in {'infobar', 'statusline', 'interaction', 'keymenu'}
    ]
    assert not any(text.startswith('plugin load failed:') for text in bottom_texts)
    assert not any(text.startswith('[core]') or text.startswith('[capdemo]') for text in bottom_texts)


def test_main_dump_screen_diagnostic_is_explicit(tmp_path, capsys, monkeypatch) -> None:
    sample = tmp_path / 'sample.txt'
    sample.write_text('alpha\nbeta\n', encoding='utf-8')
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.setenv('MICROMAX_INIT', str(tmp_path / 'missing-init.mx'))

    rc = main([
        str(sample),
        '--plugins', str(REPO_ROOT / 'plugins'),
        '--dump-screen', '8', '40',
        '--dump-screen-detail', 'diagnostic',
    ])

    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data['lines'] == 8
    assert data['cols'] == 40
    assert data['edit_window']['row_count'] >= 2
    assert data['edit_window']['rows'][0]['text'].startswith('alpha')
    assert data['cursor']['visible'] == 1
    assert 'docs_cues' in data




def test_main_dump_screen_surfaces_docs_link_metadata(tmp_path, capsys, monkeypatch) -> None:
    doc = tmp_path / '10-cli-docs-link-metadata.md'
    doc.write_text(
        '# Title\n\n'
        'See [local](#frag), [topic](other-topic#part), and <https://example.invalid/>.\n\n'
        '## Frag {#frag}\n',
        encoding='utf-8',
    )
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.setenv('MICROMAX_INIT', str(tmp_path / 'missing-init.mx'))

    rc = main([
        '--help-doc', str(doc),
        '--plugins', str(REPO_ROOT / 'plugins'),
        '--dump-screen', '12', '140',
        '--dump-screen-detail', 'diagnostic',
    ])

    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    docs_cues = dict(data['docs_cues'])
    assert docs_cues['link_entry_count'] == 3
    row = next(row for row in docs_cues['rows'] if row['link_count'] == 3)
    assert [entry['target_kind'] for entry in row['link_entries']] == [
        'fragment',
        'doc-fragment',
        'external',
    ]
    assert [entry['target_kind'] for entry in row['fragment_link_entries']] == [
        'fragment',
        'doc-fragment',
    ]
    assert [entry['target_kind'] for entry in row['local_doc_link_entries']] == ['doc-fragment']
    assert [entry['target_kind'] for entry in row['external_link_entries']] == ['external']
    assert row['footnote_link_entries'] == []
    assert row['fragment_link_count'] == 2
    assert row['local_doc_link_count'] == 1
    assert row['external_link_count'] == 1
    assert row['footnote_link_count'] == 0
    assert docs_cues['fragment_link_rows'] == 1
    assert docs_cues['local_doc_link_rows'] == 1
    assert docs_cues['external_link_rows'] == 1
    assert docs_cues['footnote_link_rows'] == 0


def test_main_dump_screen_surfaces_docs_link_source_kind_metadata(tmp_path, capsys, monkeypatch) -> None:
    doc = tmp_path / '10-cli-docs-link-source-kind-metadata.md'
    doc.write_text(
        '# Title\n\n'
        'See [inline](#frag), [full][visionref], [collapsed][], [shortcut], <https://example.invalid/>, and [^note].\n\n'
        '## Frag {#frag}\n\n'
        '[visionref]: other-topic#part\n'
        '[collapsed]: collapse-topic#part\n'
        '[shortcut]: shortcut-topic#part\n'
        '[^note]: footnote body\n',
        encoding='utf-8',
    )
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.setenv('MICROMAX_INIT', str(tmp_path / 'missing-init.mx'))

    rc = main([
        '--help-doc', str(doc),
        '--plugins', str(REPO_ROOT / 'plugins'),
        '--dump-screen', '12', '160',
        '--dump-screen-detail', 'diagnostic',
    ])

    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    docs_cues = dict(data['docs_cues'])
    row = next(row for row in docs_cues['rows'] if row['link_count'] == 6)
    assert [entry['source_kind'] for entry in row['link_entries']] == [
        'inline',
        'reference',
        'reference',
        'reference',
        'autolink',
        'footnote',
    ]
    assert [entry['reference_form'] for entry in row['link_entries']] == [
        '',
        'full',
        'collapsed',
        'shortcut',
        '',
        '',
    ]
    assert [entry['display'] for entry in row['inline_link_entries']] == ['inline']
    assert [entry['display'] for entry in row['reference_link_entries']] == ['full', 'collapsed', 'shortcut']
    assert [entry['display'] for entry in row['full_reference_link_entries']] == ['full']
    assert [entry['display'] for entry in row['collapsed_reference_link_entries']] == ['collapsed']
    assert [entry['display'] for entry in row['shortcut_reference_link_entries']] == ['shortcut']
    assert [entry['display'] for entry in row['autolink_entries']] == ['https://example.invalid/']
    assert [entry['display'] for entry in row['footnote_ref_entries']] == ['[^note]']
    assert docs_cues['inline_link_rows'] == 1
    assert docs_cues['reference_link_rows'] == 1
    assert docs_cues['full_reference_link_rows'] == 1
    assert docs_cues['collapsed_reference_link_rows'] == 1
    assert docs_cues['shortcut_reference_link_rows'] == 1
    assert docs_cues['autolink_rows'] == 1
    assert docs_cues['footnote_ref_rows'] == 1
    assert docs_cues['inline_link_count'] == 1
    assert docs_cues['reference_link_count'] == 3
    assert docs_cues['full_reference_link_count'] == 1
    assert docs_cues['collapsed_reference_link_count'] == 1
    assert docs_cues['shortcut_reference_link_count'] == 1
    assert docs_cues['autolink_count'] == 1
    assert docs_cues['footnote_ref_count'] == 1


def test_main_dump_screen_surfaces_docs_list_metadata(tmp_path, capsys, monkeypatch) -> None:
    doc = tmp_path / '10-cli-docs-list-metadata.md'
    doc.write_text(
        '# Title\n\n'
        '- alpha\n'
        '2) beta\n',
        encoding='utf-8',
    )
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.setenv('MICROMAX_INIT', str(tmp_path / 'missing-init.mx'))

    rc = main([
        '--help-doc', str(doc),
        '--plugins', str(REPO_ROOT / 'plugins'),
        '--dump-screen', '10', '120',
        '--dump-screen-detail', 'diagnostic',
    ])

    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    docs_cues = dict(data['docs_cues'])
    bullet_row = next(row for row in docs_cues['rows'] if row['text'] == '- alpha')
    assert bullet_row['list_entries'][0]['list_kind'] == 'bullet'
    assert bullet_row['bullet_list_count'] == 1
    assert bullet_row['ordered_list_count'] == 0
    ordered_row = next(row for row in docs_cues['rows'] if row['text'] == '2) beta')
    assert ordered_row['list_entries'][0]['list_kind'] == 'ordered'
    assert ordered_row['bullet_list_count'] == 0
    assert ordered_row['ordered_list_count'] == 1
    assert docs_cues['list_rows'] == 2
    assert docs_cues['bullet_list_rows'] == 1
    assert docs_cues['ordered_list_rows'] == 1
    assert docs_cues['bullet_list_entry_count'] == 1
    assert docs_cues['ordered_list_entry_count'] == 1


def test_main_dump_screen_surfaces_docs_task_list_kind_metadata(tmp_path, capsys, monkeypatch) -> None:
    doc = tmp_path / '10-cli-docs-task-kind-metadata.md'
    doc.write_text(
        '# Title\n\n'
        '- [x] done\n'
        '1. [ ] todo\n',
        encoding='utf-8',
    )
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.setenv('MICROMAX_INIT', str(tmp_path / 'missing-init.mx'))

    rc = main([
        '--help-doc', str(doc),
        '--plugins', str(REPO_ROOT / 'plugins'),
        '--dump-screen', '10', '120',
        '--dump-screen-detail', 'diagnostic',
    ])

    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    docs_cues = dict(data['docs_cues'])
    bullet_row = next(row for row in docs_cues['rows'] if row['text'] == '- [x] done')
    assert bullet_row['task_entries'][0]['list_kind'] == 'bullet'
    assert bullet_row['task_entries'][0]['list_marker'] == '-'
    assert bullet_row['checked_task_entries'] == bullet_row['task_entries']
    assert bullet_row['unchecked_task_entries'] == []
    assert bullet_row['bullet_task_entries'] == bullet_row['task_entries']
    assert bullet_row['ordered_task_entries'] == []
    assert bullet_row['bullet_task_count'] == 1
    assert bullet_row['ordered_task_count'] == 0
    ordered_row = next(row for row in docs_cues['rows'] if row['text'] == '1. [ ] todo')
    assert ordered_row['task_entries'][0]['list_kind'] == 'ordered'
    assert ordered_row['task_entries'][0]['list_marker'] == '1.'
    assert ordered_row['checked_task_entries'] == []
    assert ordered_row['unchecked_task_entries'] == ordered_row['task_entries']
    assert ordered_row['bullet_task_entries'] == []
    assert ordered_row['ordered_task_entries'] == ordered_row['task_entries']
    assert ordered_row['bullet_task_count'] == 0
    assert ordered_row['ordered_task_count'] == 1
    assert docs_cues['task_rows'] == 2
    assert docs_cues['checked_task_rows'] == 1
    assert docs_cues['unchecked_task_rows'] == 1
    assert docs_cues['bullet_task_rows'] == 1
    assert docs_cues['ordered_task_rows'] == 1
    assert docs_cues['checked_task_entry_count'] == 1
    assert docs_cues['unchecked_task_entry_count'] == 1
    assert docs_cues['bullet_task_entry_count'] == 1
    assert docs_cues['ordered_task_entry_count'] == 1


def test_main_dump_screen_surfaces_docs_blockquote_and_break_metadata(tmp_path, capsys, monkeypatch) -> None:
    doc = tmp_path / '10-cli-docs-blockquote-break-metadata.md'
    doc.write_text(
        '# Title\n\n'
        '> [!TIP] Keep this nearby\n'
        '***\n',
        encoding='utf-8',
    )
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.setenv('MICROMAX_INIT', str(tmp_path / 'missing-init.mx'))

    rc = main([
        '--help-doc', str(doc),
        '--plugins', str(REPO_ROOT / 'plugins'),
        '--dump-screen', '10', '120',
        '--dump-screen-detail', 'diagnostic',
    ])

    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    docs_cues = dict(data['docs_cues'])
    quote_row = next(row for row in docs_cues['rows'] if row['text'] == '> [!TIP] Keep this nearby')
    assert quote_row['blockquote_entries'][0]['depth'] == 1
    assert quote_row['blockquote_alert_entries'][0]['alert_kind'] == 'tip'
    assert quote_row['tip_blockquote_alert_entries'][0]['alert_kind'] == 'tip'
    assert quote_row['note_blockquote_alert_entries'] == []
    assert quote_row['blockquote_count'] == 1
    assert quote_row['blockquote_alert_count'] == 1
    assert quote_row['tip_blockquote_alert_count'] == 1
    break_row = next(row for row in docs_cues['rows'] if row['line_role'] == 'thematic-break')
    assert break_row['thematic_break_entries'][0]['marker'] == '*'
    assert break_row['thematic_break_count'] == 1
    assert docs_cues['blockquote_rows'] == 1
    assert docs_cues['blockquote_alert_rows'] == 1
    assert docs_cues['tip_blockquote_alert_rows'] == 1
    assert docs_cues['tip_blockquote_alert_entry_count'] == 1
    assert docs_cues['warning_blockquote_alert_rows'] == 0
    assert docs_cues['thematic_break_rows'] == 1


def test_main_dump_screen_surfaces_docs_code_metadata(tmp_path, capsys, monkeypatch) -> None:
    doc = tmp_path / '10-cli-docs-code-metadata.md'
    doc.write_text(
        '# Title\n\n'
        'Use `status`, ``tick`inside``, and `  padded  `.\n',
        encoding='utf-8',
    )
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.setenv('MICROMAX_INIT', str(tmp_path / 'missing-init.mx'))

    rc = main([
        '--help-doc', str(doc),
        '--plugins', str(REPO_ROOT / 'plugins'),
        '--dump-screen', '10', '120',
        '--dump-screen-detail', 'diagnostic',
    ])

    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    docs_cues = dict(data['docs_cues'])
    assert docs_cues['code_entry_count'] == 3
    assert docs_cues['single_backtick_code_rows'] == 1
    assert docs_cues['multi_backtick_code_rows'] == 1
    assert docs_cues['single_backtick_code_count'] == 2
    assert docs_cues['multi_backtick_code_count'] == 1
    row = next(row for row in docs_cues['rows'] if row['code_count'] == 3)
    assert [entry['delimiter_length'] for entry in row['code_entries']] == [1, 2, 1]
    assert [entry['delimiter_kind'] for entry in row['code_entries']] == ['single-backtick', 'multi-backtick', 'single-backtick']
    assert row['code_entries'][1]['text'] == 'tick`inside'
    assert [entry['text'] for entry in row['single_backtick_code_entries']] == ['status', '  padded  ']
    assert [entry['text'] for entry in row['multi_backtick_code_entries']] == ['tick`inside']


def test_main_dump_screen_surfaces_docs_inline_markup_metadata(tmp_path, capsys, monkeypatch) -> None:
    doc = tmp_path / '10-cli-docs-inline-markup-metadata.md'
    doc.write_text(
        '# Title\n\n'
        'Use **strong**, *soft*, _also_, and ~~gone~~ beside `*code*`.\n',
        encoding='utf-8',
    )
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.setenv('MICROMAX_INIT', str(tmp_path / 'missing-init.mx'))

    rc = main([
        '--help-doc', str(doc),
        '--plugins', str(REPO_ROOT / 'plugins'),
        '--dump-screen', '10', '140',
        '--dump-screen-detail', 'diagnostic',
    ])

    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    docs_cues = dict(data['docs_cues'])
    assert docs_cues['markup_entry_count'] == 4
    assert docs_cues['strong_markup_rows'] == 1
    assert docs_cues['emphasis_markup_rows'] == 1
    assert docs_cues['strike_markup_rows'] == 1
    assert docs_cues['asterisk_markup_rows'] == 1
    assert docs_cues['underscore_markup_rows'] == 1
    assert docs_cues['tilde_markup_rows'] == 1
    assert docs_cues['asterisk_markup_count'] == 2
    assert docs_cues['underscore_markup_count'] == 1
    assert docs_cues['tilde_markup_count'] == 1
    row = next(row for row in docs_cues['rows'] if row['markup_count'] == 4)
    assert [(entry['kind'], entry['delimiter'], entry['delimiter_kind']) for entry in row['markup_entries']] == [
        ('strong', '**', 'asterisk'),
        ('emphasis', '*', 'asterisk'),
        ('emphasis', '_', 'underscore'),
        ('strike', '~~', 'tilde'),
    ]
    assert [entry['text'] for entry in row['strong_markup_entries']] == ['strong']
    assert [entry['text'] for entry in row['emphasis_markup_entries']] == ['soft', 'also']
    assert [entry['text'] for entry in row['strike_markup_entries']] == ['gone']
    assert [entry['text'] for entry in row['asterisk_markup_entries']] == ['strong', 'soft']
    assert [entry['text'] for entry in row['underscore_markup_entries']] == ['also']
    assert [entry['text'] for entry in row['tilde_markup_entries']] == ['gone']


def test_main_dump_screen_surfaces_docs_literal_source_metadata(tmp_path, capsys, monkeypatch) -> None:
    doc = tmp_path / '10-cli-docs-literal-source-metadata.md'
    doc.write_text(
        '# Title\n\n'
        'Use <kbd>, </kbd>, \\[tag], and \\<https://example.invalid/escaped>.\n',
        encoding='utf-8',
    )
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.setenv('MICROMAX_INIT', str(tmp_path / 'missing-init.mx'))

    rc = main([
        '--help-doc', str(doc),
        '--plugins', str(REPO_ROOT / 'plugins'),
        '--dump-screen', '10', '160',
        '--dump-screen-detail', 'diagnostic',
    ])

    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    docs_cues = dict(data['docs_cues'])
    assert docs_cues['literal_entry_count'] == 4
    assert docs_cues['raw_html_rows'] == 1
    assert docs_cues['escaped_markdown_rows'] == 1
    row = next(row for row in docs_cues['rows'] if row['literal_count'] == 4)
    assert [(entry['kind'], entry['detail']) for entry in row['literal_entries']] == [
        ('raw-html-tag', 'kbd'),
        ('raw-html-tag', 'kbd'),
        ('escaped-markdown', '['),
        ('escaped-markdown', '<'),
    ]
    assert [entry['detail'] for entry in row['raw_html_literal_entries']] == ['kbd', 'kbd']
    assert [entry['detail'] for entry in row['escaped_markdown_entries']] == ['[', '<']
    assert row['raw_html_literal_count'] == 2
    assert row['escaped_markdown_count'] == 2


def test_main_dump_screen_surfaces_docs_image_metadata(tmp_path, capsys, monkeypatch) -> None:
    doc = tmp_path / '10-cli-docs-image-metadata.md'
    doc.write_text(
        '# Title\n\n'
        'See ![local](#frag), ![topic](other-topic#part), and ![ext](https://example.invalid/img.png).\n\n'
        '## Frag {#frag}\n',
        encoding='utf-8',
    )
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.setenv('MICROMAX_INIT', str(tmp_path / 'missing-init.mx'))

    rc = main([
        '--help-doc', str(doc),
        '--plugins', str(REPO_ROOT / 'plugins'),
        '--dump-screen', '12', '160',
        '--dump-screen-detail', 'diagnostic',
    ])

    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    docs_cues = dict(data['docs_cues'])
    assert docs_cues['image_entry_count'] == 3
    assert docs_cues['local_doc_image_rows'] == 1
    assert docs_cues['fragment_image_rows'] == 1
    assert docs_cues['external_image_rows'] == 1
    assert docs_cues['footnote_image_rows'] == 0
    row = next(row for row in docs_cues['rows'] if row['image_count'] == 3)
    assert [entry['target_kind'] for entry in row['image_entries']] == [
        'fragment',
        'doc-fragment',
        'external',
    ]
    assert [entry['target_kind'] for entry in row['fragment_image_entries']] == [
        'fragment',
        'doc-fragment',
    ]
    assert [entry['target_kind'] for entry in row['local_doc_image_entries']] == ['doc-fragment']
    assert [entry['target_kind'] for entry in row['external_image_entries']] == ['external']
    assert row['footnote_image_entries'] == []




def test_main_dump_screen_surfaces_docs_footnote_image_target_slices(tmp_path, capsys, monkeypatch) -> None:
    doc = tmp_path / '10-cli-docs-image-footnote-metadata.md'
    doc.write_text(
        '# Title\n\n'
        'See ![note](#^fig-note).\n\n'
        '[^fig-note]: footnote target\n',
        encoding='utf-8',
    )
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.setenv('MICROMAX_INIT', str(tmp_path / 'missing-init.mx'))

    rc = main([
        '--help-doc', str(doc),
        '--plugins', str(REPO_ROOT / 'plugins'),
        '--dump-screen', '10', '120',
        '--dump-screen-detail', 'diagnostic',
    ])

    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    docs_cues = dict(data['docs_cues'])
    assert docs_cues['footnote_image_rows'] == 1
    assert docs_cues['footnote_image_count'] == 1
    row = next(row for row in docs_cues['rows'] if row['footnote_image_count'] == 1)
    assert [entry['target_kind'] for entry in row['footnote_image_entries']] == ['footnote']
    assert [entry['target_kind'] for entry in row['fragment_image_entries']] == ['footnote']


def test_main_dump_screen_surfaces_docs_image_source_kind_metadata(tmp_path, capsys, monkeypatch) -> None:
    doc = tmp_path / '10-cli-docs-image-source-kind-metadata.md'
    doc.write_text(
        '# Title\n\n'
        'See ![inline](#frag), ![full][shot], ![collapsed][], and ![shortcut].\n\n'
        '[shot]: other-topic#part\n'
        '[collapsed]: collapse.md#snap\n'
        '[shortcut]: other.md#snap\n'
        '## Frag {#frag}\n',
        encoding='utf-8',
    )
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.setenv('MICROMAX_INIT', str(tmp_path / 'missing-init.mx'))

    rc = main([
        '--help-doc', str(doc),
        '--plugins', str(REPO_ROOT / 'plugins'),
        '--dump-screen', '12', '180',
        '--dump-screen-detail', 'diagnostic',
    ])

    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    docs_cues = dict(data['docs_cues'])
    assert docs_cues['image_entry_count'] == 4
    assert docs_cues['inline_image_rows'] == 1
    assert docs_cues['reference_image_rows'] == 1
    assert docs_cues['full_reference_image_rows'] == 1
    assert docs_cues['collapsed_reference_image_rows'] == 1
    assert docs_cues['shortcut_reference_image_rows'] == 1
    assert docs_cues['inline_image_count'] == 1
    assert docs_cues['reference_image_count'] == 3
    assert docs_cues['full_reference_image_count'] == 1
    assert docs_cues['collapsed_reference_image_count'] == 1
    assert docs_cues['shortcut_reference_image_count'] == 1
    row = next(row for row in docs_cues['rows'] if row['image_count'] == 4)
    assert [entry['source_kind'] for entry in row['image_entries']] == ['inline', 'reference', 'reference', 'reference']
    assert [entry['reference_form'] for entry in row['image_entries']] == ['', 'full', 'collapsed', 'shortcut']
    assert [entry['alt_text'] for entry in row['inline_image_entries']] == ['inline']
    assert [entry['alt_text'] for entry in row['reference_image_entries']] == ['full', 'collapsed', 'shortcut']
    assert [entry['alt_text'] for entry in row['full_reference_image_entries']] == ['full']
    assert [entry['alt_text'] for entry in row['collapsed_reference_image_entries']] == ['collapsed']
    assert [entry['alt_text'] for entry in row['shortcut_reference_image_entries']] == ['shortcut']


def test_main_dump_screen_surfaces_docs_table_metadata(tmp_path, capsys, monkeypatch) -> None:
    doc = tmp_path / '10-cli-docs-table-metadata.md'
    doc.write_text(
        '# Title\n\n'
        '| Key | Value | Count | Note |\n'
        '| :--- | :---: | ---: | --- |\n'
        '| one | alpha beta | 7 | plain |\n',
        encoding='utf-8',
    )
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.setenv('MICROMAX_INIT', str(tmp_path / 'missing-init.mx'))

    rc = main([
        '--help-doc', str(doc),
        '--plugins', str(REPO_ROOT / 'plugins'),
        '--dump-screen', '12', '120',
        '--dump-screen-detail', 'diagnostic',
    ])

    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    docs_cues = dict(data['docs_cues'])
    assert docs_cues['table_entry_count'] == 12
    assert docs_cues['table_header_rows'] == 1
    assert docs_cues['table_body_rows'] == 1
    assert docs_cues['table_delimiter_rows'] == 1
    assert docs_cues['default_aligned_table_rows'] == 3
    assert docs_cues['left_aligned_table_rows'] == 3
    assert docs_cues['center_aligned_table_rows'] == 3
    assert docs_cues['right_aligned_table_rows'] == 3
    header_row = next(row for row in docs_cues['rows'] if row['table_kind'] == 'header')
    assert [(entry['text'], entry['align']) for entry in header_row['table_entries']] == [
        ('Key', 'left'),
        ('Value', 'center'),
        ('Count', 'right'),
        ('Note', 'default'),
    ]
    assert [entry['text'] for entry in header_row['left_aligned_table_entries']] == ['Key']
    assert [entry['text'] for entry in header_row['center_aligned_table_entries']] == ['Value']
    assert [entry['text'] for entry in header_row['right_aligned_table_entries']] == ['Count']
    assert [entry['text'] for entry in header_row['default_aligned_table_entries']] == ['Note']
    delim_row = next(row for row in docs_cues['rows'] if row['table_kind'] == 'delimiter')
    assert [entry['align'] for entry in delim_row['table_delimiter_entries']] == ['left', 'center', 'right', 'default']
    body_row = next(row for row in docs_cues['rows'] if row['table_kind'] == 'body')
    assert [(entry['text'], entry['align']) for entry in body_row['table_body_entries']] == [
        ('one', 'left'),
        ('alpha beta', 'center'),
        ('7', 'right'),
        ('plain', 'default'),
    ]


def test_main_dump_screen_surfaces_docs_heading_metadata(tmp_path, capsys, monkeypatch) -> None:
    doc = tmp_path / '10-cli-docs-heading-metadata.md'
    doc.write_text(
        '# Alpha Beta {#start-here}\n\n'
        'Setext topic\n'
        '-----\n\n'
        '### Gamma Level\n',
        encoding='utf-8',
    )
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.setenv('MICROMAX_INIT', str(tmp_path / 'missing-init.mx'))

    rc = main([
        '--help-doc', str(doc),
        '--plugins', str(REPO_ROOT / 'plugins'),
        '--dump-screen', '10', '120',
        '--dump-screen-detail', 'diagnostic',
    ])

    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    docs_cues = dict(data['docs_cues'])
    assert docs_cues['heading_entry_count'] == 4
    assert docs_cues['heading_title_rows'] == 3
    assert docs_cues['heading_underline_rows'] == 1
    assert docs_cues['atx_heading_rows'] == 2
    assert docs_cues['setext_heading_rows'] == 2
    assert docs_cues['h1_heading_rows'] == 1
    assert docs_cues['h2_heading_rows'] == 2
    assert docs_cues['h3_heading_rows'] == 1
    assert docs_cues['explicit_fragment_heading_rows'] == 1
    assert docs_cues['auto_fragment_heading_rows'] == 3
    atx_row = next(row for row in docs_cues['rows'] if row['text'].startswith('# Alpha Beta'))
    assert atx_row['heading_entries'][0]['fragment'] == 'start-here'
    assert atx_row['heading_title_entries'] == atx_row['heading_entries']
    assert atx_row['atx_heading_entries'] == atx_row['heading_entries']
    assert atx_row['h1_heading_entries'] == atx_row['heading_entries']
    assert atx_row['explicit_fragment_heading_entries'] == atx_row['heading_entries']
    underline_row = next(row for row in docs_cues['rows'] if row['line_role'] == 'heading-underline')
    assert underline_row['heading_entries'][0]['fragment'] == 'setext-topic'
    assert underline_row['heading_entries'][0]['marker'] == '-'
    assert underline_row['heading_underline_entries'] == underline_row['heading_entries']
    assert underline_row['setext_heading_entries'] == underline_row['heading_entries']
    assert underline_row['h2_heading_entries'] == underline_row['heading_entries']
    assert underline_row['auto_fragment_heading_entries'] == underline_row['heading_entries']
    h3_row = next(row for row in docs_cues['rows'] if row['text'] == '### Gamma Level')
    assert h3_row['h3_heading_entries'] == h3_row['heading_entries']
    assert h3_row['auto_fragment_heading_entries'] == h3_row['heading_entries']


def test_main_dump_screen_surfaces_docs_section_metadata(tmp_path, capsys, monkeypatch) -> None:
    doc = tmp_path / '10-cli-docs-section-metadata.md'
    doc.write_text(
        '# Guide\n\n'
        'Intro line\n\n'
        '## Links\n\n'
        'Section prose\n\n'
        '```python\n'
        'code line\n'
        '```\n\n'
        '### Deep Dive\n\n'
        'Nested prose\n',
        encoding='utf-8',
    )
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.setenv('MICROMAX_INIT', str(tmp_path / 'missing-init.mx'))

    rc = main([
        '--help-doc', str(doc),
        '--plugins', str(REPO_ROOT / 'plugins'),
        '--dump-screen', '20', '120',
        '--dump-screen-detail', 'diagnostic',
    ])

    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    docs_cues = dict(data['docs_cues'])
    assert docs_cues['section_distinct_count'] == 3
    intro_row = next(row for row in docs_cues['rows'] if row['text'] == 'Intro line')
    assert intro_row['section_entry']['path'] == 'Guide'
    code_row = next(row for row in docs_cues['rows'] if row['text'] == 'code line')
    assert code_row['section_entry']['path'] == 'Guide › Links'
    nested_row = next(row for row in docs_cues['rows'] if row['text'] == 'Nested prose')
    assert nested_row['section_entry']['path'] == 'Guide › Links › Deep Dive'
    assert nested_row['section_entry']['fragment'] == 'deep-dive'


def test_main_dump_screen_surfaces_docs_definition_metadata(tmp_path, capsys, monkeypatch) -> None:
    doc = tmp_path / '10-cli-docs-definition-metadata.md'
    doc.write_text(
        '# Title\n\n'
        '[visionref]:\n'
        '  00-vision.md#intro\n\n'
        'Paragraph with note[^tiny].\n\n'
        '[^tiny]: first line\n'
        '    second line\n',
        encoding='utf-8',
    )
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.setenv('MICROMAX_INIT', str(tmp_path / 'missing-init.mx'))

    rc = main([
        '--help-doc', str(doc),
        '--plugins', str(REPO_ROOT / 'plugins'),
        '--dump-screen', '12', '120',
        '--dump-screen-detail', 'diagnostic',
    ])

    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    docs_cues = dict(data['docs_cues'])
    assert docs_cues['definition_entry_count'] == 4
    ref_row = next(row for row in docs_cues['rows'] if row['definition_role'] == 'reference')
    assert ref_row['reference_definition_count'] == 1
    assert ref_row['reference_definition_entries'][0]['target_kind'] == 'file-fragment'
    assert ref_row['definition_entries'][0]['target_kind'] == 'file-fragment'
    assert ref_row['definition_entries'][0]['target_doc'] == '00-vision.md'
    assert ref_row['definition_entries'][0]['target_fragment'] == 'intro'
    foot_row = next(row for row in docs_cues['rows'] if row['definition_role'] == 'footnote')
    assert foot_row['footnote_definition_count'] == 1
    assert foot_row['footnote_definition_entries'][0]['target_fragment'] == '^tiny'
    assert foot_row['definition_entries'][0]['target_fragment'] == '^tiny'
    assert docs_cues['reference_definition_rows'] == 1
    assert docs_cues['reference_definition_cont_rows'] == 1
    assert docs_cues['footnote_definition_rows'] == 1
    assert docs_cues['footnote_definition_cont_rows'] == 1
    assert docs_cues['reference_definition_entry_count'] == 1
    assert docs_cues['reference_definition_cont_entry_count'] == 1
    assert docs_cues['footnote_definition_entry_count'] == 1
    assert docs_cues['footnote_definition_cont_entry_count'] == 1


def test_main_dump_screen_can_open_help_doc_and_surface_docs_cues(tmp_path, capsys, monkeypatch) -> None:
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.setenv('MICROMAX_INIT', str(tmp_path / 'missing-init.mx'))

    rc = main([
        '--help-doc', str(REPO_ROOT / 'docs' / '70-tutorial.md'),
        '--plugins', str(REPO_ROOT / 'plugins'),
        '--dump-screen', '12', '72',
        '--dump-screen-detail', 'diagnostic',
    ])

    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    docs_cues = dict(data['docs_cues'])
    assert docs_cues['enabled'] == 1
    assert docs_cues['active'] == 1
    assert docs_cues['help_doc'] == 'tutorial'
    assert docs_cues['row_count'] == data['layout']['viewport_height']
    assert any(str(row.get('line_role', '')).startswith('heading') for row in docs_cues['rows'])


def test_main_dump_screen_surfaces_docs_block_metadata(tmp_path, capsys, monkeypatch) -> None:
    doc = tmp_path / '10-cli-docs-block-metadata.md'
    doc.write_text(
        '# Title\n\n'
        '```python\n'
        'print(1)\n'
        '```\n\n'
        '<div>\n'
        'raw html\n'
        '</div>\n\n'
        '    indented one\n'
        '    indented two\n',
        encoding='utf-8',
    )
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.setenv('MICROMAX_INIT', str(tmp_path / 'missing-init.mx'))

    rc = main([
        '--help-doc', str(doc),
        '--plugins', str(REPO_ROOT / 'plugins'),
        '--dump-screen', '16', '120',
        '--dump-screen-detail', 'diagnostic',
    ])

    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    docs_cues = dict(data['docs_cues'])
    assert docs_cues['block_entry_count'] == 8
    opener_row = next(row for row in docs_cues['rows'] if row['text'].startswith('```python'))
    assert opener_row['block_entries'][0]['role'] == 'opener'
    assert opener_row['block_entries'][0]['info_string'] == 'python'
    assert opener_row['block_entries'][0]['language'] == 'python'
    assert opener_row['fenced_code_entries'][0]['role'] == 'opener'
    assert opener_row['fenced_code_opener_entries'][0]['role'] == 'opener'
    html_row = next(row for row in docs_cues['rows'] if row['text'] == '<div>')
    assert html_row['block_entries'][0]['kind'] == 'html-block'
    assert html_row['html_block_entries'][0]['kind'] == 'html-block'
    indented_row = next(row for row in docs_cues['rows'] if row['text'] == '    indented one')
    assert indented_row['block_entries'][0]['kind'] == 'indented-code'
    assert indented_row['indented_code_entries'][0]['kind'] == 'indented-code'
    assert docs_cues['fenced_code_rows'] == 3
    assert docs_cues['fenced_code_opener_rows'] == 1
    assert docs_cues['fenced_code_body_rows'] == 1
    assert docs_cues['fenced_code_closer_rows'] == 1
    assert docs_cues['html_block_rows'] == 3
    assert docs_cues['indented_code_rows'] == 2
    assert docs_cues['fenced_code_opener_entry_count'] == 1
    assert docs_cues['fenced_code_body_entry_count'] == 1
    assert docs_cues['fenced_code_closer_entry_count'] == 1
    assert docs_cues['html_block_entry_count'] == 3
    assert docs_cues['indented_code_entry_count'] == 2



def test_main_dump_screen_reports_fenced_code_marker_and_language_metadata(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    doc = tmp_path / 'docs-fenced-source-kinds.md'
    doc.write_text(
        '# Fence source kinds\n\n'
        '```python\n'
        'print("hi")\n'
        '```\n\n'
        '~~~\n'
        'raw\n'
        '~~~\n',
        encoding='utf-8',
    )
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.setenv('MICROMAX_INIT', str(tmp_path / 'missing-init.mx'))

    rc = main([
        '--help-doc', str(doc),
        '--plugins', str(REPO_ROOT / 'plugins'),
        '--dump-screen', '12', '120',
        '--dump-screen-detail', 'diagnostic',
    ])

    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    docs_cues = dict(data['docs_cues'])
    opener_backtick = next(
        row for row in docs_cues['rows']
        if row['fenced_code_opener_count'] == 1 and row['backtick_fenced_code_count'] == 1
    )
    opener_tilde = next(
        row for row in docs_cues['rows']
        if row['fenced_code_opener_count'] == 1 and row['tilde_fenced_code_count'] == 1
    )
    body_tilde = next(row for row in docs_cues['rows'] if row['text'] == 'raw')
    assert opener_backtick['backtick_fenced_code_entries'][0]['language'] == 'python'
    assert opener_backtick['language_fenced_code_entries'][0]['marker_kind'] == 'backtick'
    assert opener_tilde['tilde_fenced_code_entries'][0]['marker_kind'] == 'tilde'
    assert opener_tilde['bare_fenced_code_entries'][0]['has_language'] == 0
    assert body_tilde['bare_fenced_code_entries'][0]['role'] == 'body'
    assert docs_cues['backtick_fenced_code_rows'] == 3
    assert docs_cues['tilde_fenced_code_rows'] == 3
    assert docs_cues['language_fenced_code_rows'] == 3
    assert docs_cues['bare_fenced_code_rows'] == 3
    assert docs_cues['backtick_fenced_code_count'] == 3
    assert docs_cues['tilde_fenced_code_count'] == 3
    assert docs_cues['language_fenced_code_count'] == 3
    assert docs_cues['bare_fenced_code_count'] == 3
