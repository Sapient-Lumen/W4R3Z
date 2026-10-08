from __future__ import annotations

import json
from pathlib import Path

from micromax_editor.__main__ import main


REPO_ROOT = Path(__file__).resolve().parents[1]


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
    assert data['lines'] == 8
    assert data['cols'] == 40
    assert data['edit_window']['row_count'] >= 2
    assert data['edit_window']['rows'][0]['text'].startswith('alpha')
    assert data['cursor']['visible'] == 1




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
    ])

    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    docs_cues = dict(data['docs_cues'])
    assert docs_cues['code_entry_count'] == 3
    row = next(row for row in docs_cues['rows'] if row['code_count'] == 3)
    assert [entry['delimiter_length'] for entry in row['code_entries']] == [1, 2, 1]
    assert row['code_entries'][1]['text'] == 'tick`inside'


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
    ])

    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    docs_cues = dict(data['docs_cues'])
    assert docs_cues['markup_entry_count'] == 4
    row = next(row for row in docs_cues['rows'] if row['markup_count'] == 4)
    assert [(entry['kind'], entry['delimiter']) for entry in row['markup_entries']] == [
        ('strong', '**'),
        ('emphasis', '*'),
        ('emphasis', '_'),
        ('strike', '~~'),
    ]


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
    ])

    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    docs_cues = dict(data['docs_cues'])
    assert docs_cues['literal_entry_count'] == 4
    row = next(row for row in docs_cues['rows'] if row['literal_count'] == 4)
    assert [(entry['kind'], entry['detail']) for entry in row['literal_entries']] == [
        ('raw-html-tag', 'kbd'),
        ('raw-html-tag', 'kbd'),
        ('escaped-markdown', '['),
        ('escaped-markdown', '<'),
    ]


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
    ])

    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    docs_cues = dict(data['docs_cues'])
    assert docs_cues['image_entry_count'] == 3
    row = next(row for row in docs_cues['rows'] if row['image_count'] == 3)
    assert [entry['target_kind'] for entry in row['image_entries']] == [
        'fragment',
        'doc-fragment',
        'external',
    ]


def test_main_dump_screen_surfaces_docs_table_metadata(tmp_path, capsys, monkeypatch) -> None:
    doc = tmp_path / '10-cli-docs-table-metadata.md'
    doc.write_text(
        '# Title\n\n'
        '| Key | Value | Count |\n'
        '| :--- | :---: | ---: |\n'
        '| one | alpha beta | 7 |\n',
        encoding='utf-8',
    )
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.setenv('MICROMAX_INIT', str(tmp_path / 'missing-init.mx'))

    rc = main([
        '--help-doc', str(doc),
        '--plugins', str(REPO_ROOT / 'plugins'),
        '--dump-screen', '12', '120',
    ])

    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    docs_cues = dict(data['docs_cues'])
    assert docs_cues['table_entry_count'] == 9
    header_row = next(row for row in docs_cues['rows'] if row['table_kind'] == 'header')
    assert [entry['text'] for entry in header_row['table_entries']] == ['Key', 'Value', 'Count']
    delim_row = next(row for row in docs_cues['rows'] if row['table_kind'] == 'delimiter')
    assert [entry['align'] for entry in delim_row['table_entries']] == ['left', 'center', 'right']


def test_main_dump_screen_surfaces_docs_heading_metadata(tmp_path, capsys, monkeypatch) -> None:
    doc = tmp_path / '10-cli-docs-heading-metadata.md'
    doc.write_text(
        '# Alpha Beta {#start-here}\n\n'
        'Setext topic\n'
        '-----\n',
        encoding='utf-8',
    )
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.setenv('MICROMAX_INIT', str(tmp_path / 'missing-init.mx'))

    rc = main([
        '--help-doc', str(doc),
        '--plugins', str(REPO_ROOT / 'plugins'),
        '--dump-screen', '10', '120',
    ])

    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    docs_cues = dict(data['docs_cues'])
    assert docs_cues['heading_entry_count'] == 3
    atx_row = next(row for row in docs_cues['rows'] if row['text'].startswith('# Alpha Beta'))
    assert atx_row['heading_entries'][0]['fragment'] == 'start-here'
    underline_row = next(row for row in docs_cues['rows'] if row['line_role'] == 'heading-underline')
    assert underline_row['heading_entries'][0]['fragment'] == 'setext-topic'
    assert underline_row['heading_entries'][0]['marker'] == '-'


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
    ])

    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    docs_cues = dict(data['docs_cues'])
    assert docs_cues['definition_entry_count'] == 4
    ref_row = next(row for row in docs_cues['rows'] if row['definition_role'] == 'reference')
    assert ref_row['definition_entries'][0]['target_kind'] == 'file-fragment'
    assert ref_row['definition_entries'][0]['target_doc'] == '00-vision.md'
    assert ref_row['definition_entries'][0]['target_fragment'] == 'intro'
    foot_row = next(row for row in docs_cues['rows'] if row['definition_role'] == 'footnote')
    assert foot_row['definition_entries'][0]['target_fragment'] == '^tiny'
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
    ])

    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    docs_cues = dict(data['docs_cues'])
    assert docs_cues['block_entry_count'] == 8
    opener_row = next(row for row in docs_cues['rows'] if row['text'].startswith('```python'))
    assert opener_row['block_entries'][0]['role'] == 'opener'
    assert opener_row['block_entries'][0]['info_string'] == 'python'
    assert opener_row['block_entries'][0]['language'] == 'python'
    html_row = next(row for row in docs_cues['rows'] if row['text'] == '<div>')
    assert html_row['block_entries'][0]['kind'] == 'html-block'
    indented_row = next(row for row in docs_cues['rows'] if row['text'] == '    indented one')
    assert indented_row['block_entries'][0]['kind'] == 'indented-code'
    assert docs_cues['fenced_code_opener_entry_count'] == 1
    assert docs_cues['fenced_code_body_entry_count'] == 1
    assert docs_cues['fenced_code_closer_entry_count'] == 1
    assert docs_cues['html_block_entry_count'] == 3
    assert docs_cues['indented_code_entry_count'] == 2
