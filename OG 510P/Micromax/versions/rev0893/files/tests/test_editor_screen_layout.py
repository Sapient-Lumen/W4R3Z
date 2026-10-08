from __future__ import annotations

import curses

from micromax_editor.commandbar import Prompt
from micromax_editor.docs_cues import DOCS_CUE_ZERO_METRIC_KEYS
from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.tui import _render


def _hostcall(ed: Editor, name: str, *args: object) -> object:
    vm = ed.vm
    vm.stack.clear()
    for a in args:
        vm.stack.append(a)
    vm.stack.append(name)
    vm.eval("hostcall")
    assert vm.stack
    return vm.stack.pop()


def test_screen_layout_model_tracks_viewport_suggestions_and_bottom_rows() -> None:
    ed = Editor()
    ed.new_buffer('t.mx', '\n'.join(f'line {i}' for i in range(12)) + '\n', path='t.mx')
    eb = ed.cur()
    ed.options.set('ruler', 'true', local=eb.local_options)
    ed.options.set('scrollbar', 'true', local=eb.local_options)
    ed.options.set('keymenu', 'true', local=eb.local_options)

    p = Prompt(kind='palette')
    rows = [
        ['open README.md', 'openpath', 'README.md', 'Files'],
        ['open TODO.md', 'openpath', 'TODO.md', 'Files'],
    ]
    p.suggestion_rows = rows
    p.suggestions = [r[0] for r in rows]
    p.suggest_index = 0
    p.text = 'open'
    ed.prompt = p

    model = ed.screen_layout_model(12, 40)
    assert model['viewport_x'] == 3
    assert model['gutter_left'] == 3
    assert model['gutter_right'] == 1
    assert model['viewport_width'] == 36
    assert model['suggestions_height'] == 3
    assert model['viewport_height'] == 6
    assert model['keymenu_y'] == 9
    assert model['prompt_y'] == 10
    assert model['status_y'] == 11
    assert model['bottom_rows_count'] == 3
    assert [row['kind'] for row in model['bottom_rows']] == ['keymenu', 'interaction', 'statusline']


def test_prompt_panel_model_tracks_visible_picker_rows_and_positions() -> None:
    ed = Editor()
    ed.new_buffer('t.mx', 'alpha\nbeta\ngamma\n', path='t.mx')

    p = Prompt(kind='palette')
    rows = [
        ['open README.md', 'openpath', 'README.md', 'Files'],
        ['open TODO.md', 'openpath', 'TODO.md', 'Files'],
    ]
    p.suggestion_rows = rows
    p.suggestions = [r[0] for r in rows]
    p.suggest_index = 0
    p.text = 'open'
    ed.prompt = p

    model = ed.prompt_panel_model(12, 40)
    assert model['active'] == 1
    assert model['kind'] == 'palette'
    assert model['y'] == 7
    assert model['height'] == 3
    assert model['width'] == 40
    assert model['row_count'] == 3
    assert model['entries'][0]['type'] == 'header'
    assert model['entries'][0]['text'].startswith('-- Open')
    assert model['entries'][1]['type'] == 'row'
    assert model['entries'][1]['screen_y'] == 8
    assert model['entries'][1]['selected'] == 1


def test_screen_layout_model_reclaims_rows_when_statusline_and_infobar_are_hidden() -> None:
    ed = Editor()
    ed.new_buffer('*scratch*', 'one\ntwo\nthree\nfour\n')
    eb = ed.cur()
    ed.options.set('statusline', 'false', local=eb.local_options)
    ed.options.set('infobar', 'false', local=eb.local_options)

    model = ed.screen_layout_model(8, 20)
    assert model['viewport_height'] == 8
    assert model['bottom_rows_count'] == 0
    assert model['prompt_y'] == -1
    assert model['status_y'] == -1




def test_viewport_rows_model_tracks_composed_visible_rows_and_gutters() -> None:
    ed = Editor()
    ed.new_buffer('t.mx', '\n'.join(f'line {i}' for i in range(20)) + '\n', path='t.mx')
    eb = ed.cur()
    ed.options.set('ruler', 'true', local=eb.local_options)
    ed.options.set('scrollbar', 'true', local=eb.local_options)
    ed.options.set('statusline', 'false', local=eb.local_options)
    ed.options.set('infobar', 'false', local=eb.local_options)

    model = ed.viewport_rows_model(4, 20)
    assert model['active'] == 1
    assert model['height'] == 4
    assert model['left_width'] == 3
    assert model['right_width'] == 1
    assert model['row_count'] == 4
    assert model['rows'][0]['left_text'].strip() == '1'
    assert model['rows'][0]['text'] == 'line 0'
    assert model['rows'][0]['text_x'] == 3
    assert model['rows'][0]['right_x'] == 19
    assert model['rows'][0]['combined_text'].startswith(model['rows'][0]['left_text'] + model['rows'][0]['text'])
    assert any(str(row.get('right_text', '') or '') == ed.scrollbar_thumb_char() for row in model['rows'])


def test_search_rows_model_tracks_visible_matches_and_current_match() -> None:
    ed = Editor()
    ed.new_buffer('t.txt', 'alpha beta alpha\nsecond alpha\n', path='t.txt')
    eb = ed.cur()
    ed.options.set('hlsearch', 'true', local=eb.local_options)

    assert ed.find('ALPHA') is True
    model = ed.search_rows_model(8, 30)
    assert model['active'] == 1
    assert model['enabled'] == 1
    assert model['query'] == 'ALPHA'
    assert model['match_rows'] == 2
    assert model['rows'][0]['spans'] == [[0, 5], [11, 16]]
    assert model['rows'][0]['current_spans'] == [[0, 5]]
    assert model['rows'][1]['spans'] == [[7, 12]]


def test_edit_window_model_tracks_visible_rows_and_cursor() -> None:
    ed = Editor()
    ed.new_buffer('t.mx', 'abcdef\nxyz\n', path='t.mx')
    eb = ed.cur()
    ed.options.set('statusline', 'false', local=eb.local_options)
    ed.options.set('infobar', 'false', local=eb.local_options)
    ed.options.set('softwrap', 'true', local=eb.local_options)
    c = ed.primary_cursor()
    c.line = 0
    c.col = 5

    model = ed.edit_window_model(4, 4)
    assert model['viewport_height'] == 4
    assert model['viewport_width'] == 4
    assert model['row_count'] == 4
    assert [row['text'] for row in model['rows'][:3]] == ['abcd', 'ef', 'xyz']
    assert model['rows'][3]['text'] == ''
    assert model['rows'][1]['continuation'] == 1
    assert model['cursor']['view_y'] == 1
    assert model['cursor']['view_x'] == 1
    assert model['cursor']['screen_y'] == 1
    assert model['cursor']['screen_x'] == 1
    assert model['cursor']['visible'] == 1
    assert model['viewport']['height'] == 4
    assert model['viewport']['width'] == 4


def test_ed_screen_layout_hostcall_exposes_shared_layout_model() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('t.mx', 'alpha\nbeta\n', path='t.mx')
    eb = ed.cur()
    ed.options.set('keymenu', 'true', local=eb.local_options)
    ed.enter_command_palette('status')

    model = _hostcall(ed, 'ed.screen-layout', 10, 30)
    assert isinstance(model, dict)
    assert model['cols'] == 30
    assert model['lines'] == 10
    assert model['bottom_rows_count'] == 3
    assert model['prompt_y'] == 8
    assert [row['kind'] for row in model['bottom_rows']] == ['keymenu', 'interaction', 'statusline']



def test_ed_edit_window_hostcall_exposes_shared_edit_rows_and_cursor() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('t.mx', 'abcdef\nxyz\n', path='t.mx')
    eb = ed.cur()
    ed.options.set('statusline', 'false', local=eb.local_options)
    ed.options.set('infobar', 'false', local=eb.local_options)
    ed.options.set('softwrap', 'true', local=eb.local_options)
    c = ed.primary_cursor()
    c.line = 0
    c.col = 5

    model = _hostcall(ed, 'ed.edit-window', 4, 4)
    assert isinstance(model, dict)
    assert model['rows'][0]['text'] == 'abcd'
    assert model['rows'][1]['text'] == 'ef'
    assert model['cursor']['screen_y'] == 1
    assert model['cursor']['screen_x'] == 1




def test_ed_viewport_rows_hostcall_exposes_shared_composed_visible_rows() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('t.mx', '\n'.join(f'line {i}' for i in range(20)) + '\n', path='t.mx')
    eb = ed.cur()
    ed.options.set('ruler', 'true', local=eb.local_options)
    ed.options.set('scrollbar', 'true', local=eb.local_options)
    ed.options.set('statusline', 'false', local=eb.local_options)
    ed.options.set('infobar', 'false', local=eb.local_options)

    model = _hostcall(ed, 'ed.viewport-rows', 4, 20)
    assert isinstance(model, dict)
    assert model['row_count'] == 4
    assert model['rows'][0]['left_text'].strip() == '1'
    assert model['rows'][0]['text'] == 'line 0'
    assert any(str(row.get('right_text', '') or '') == ed.scrollbar_thumb_char() for row in model['rows'])


def test_ed_search_rows_hostcall_exposes_shared_visible_search_spans() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('t.txt', 'alpha beta alpha\nsecond alpha\n', path='t.txt')
    eb = ed.cur()
    ed.options.set('hlsearch', 'true', local=eb.local_options)

    assert ed.find('ALPHA') is True
    model = _hostcall(ed, 'ed.search-rows', 8, 30)
    assert isinstance(model, dict)
    assert model['match_rows'] == 2
    assert model['rows'][0]['spans'] == [[0, 5], [11, 16]]
    assert model['rows'][0]['current_spans'] == [[0, 5]]


def test_showchars_rows_model_tracks_visible_replacements_and_spans() -> None:
    ed = Editor()
    ed.new_buffer('t.txt', '\t a\tb\n', path='t.txt')
    eb = ed.cur()
    ed.options.set('statusline', 'false', local=eb.local_options)
    ed.options.set('infobar', 'false', local=eb.local_options)
    ed.options.set('showchars', 'tab=>,space=.,itab=|>,ispace=:', local=eb.local_options)

    model = ed.showchars_rows_model(4, 10)
    assert model['active'] == 1
    assert model['enabled'] == 1
    assert model['spec'] == 'tab=>,space=.,itab=|>,ispace=:'
    assert model['changed_rows'] == 1
    assert model['rows'][0]['text'] == '\t a\tb'
    assert model['rows'][0]['display_text'] == '|:a>b'
    assert model['rows'][0]['spans'] == [[0, 1], [1, 2], [3, 4]]
    assert model['rows'][1]['display_text'] == ''



def test_viewport_cues_model_tracks_visible_overlay_spans() -> None:
    ed = Editor()
    ed.new_buffer('t.txt', 'a(b[c]d)e  \nsecond\n', path='t.txt')
    eb = ed.cur()
    ed.options.set('statusline', 'false', local=eb.local_options)
    ed.options.set('infobar', 'false', local=eb.local_options)
    ed.options.set('cursorline', 'true', local=eb.local_options)
    ed.options.set('hltrailingws', 'true', local=eb.local_options)
    ed.options.set('colorcolumn', '3', local=eb.local_options)
    ed.options.set('matchbrace', 'true', local=eb.local_options)
    eb.cursors[eb.primary].line = 0
    eb.cursors[eb.primary].col = 3
    assert ed.find('[') is True
    ed.options.set('hlsearch', 'true', local=eb.local_options)

    model = ed.viewport_cues_model(4, 20)
    assert model['active'] == 1
    assert model['cursorline_enabled'] == 1
    assert model['hlsearch_enabled'] == 1
    assert model['hltrailingws_enabled'] == 1
    assert model['colorcolumn'] == 3
    assert model['matchbrace_enabled'] == 1
    assert model['cue_rows'] >= 1
    row0 = model['rows'][0]
    assert row0['cursorline'] == 1
    assert row0['search_spans'] == [[3, 4]]
    assert row0['current_search_spans'] == [[3, 4]]
    assert row0['trailing_spans'] == [[9, 11]]
    assert row0['colorcolumn_spans'] == [[2, 3]]
    assert row0['brace_spans'] == [[3, 4], [5, 6]]



def test_ed_viewport_cues_hostcall_exposes_shared_visible_overlay_spans() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('t.txt', 'hi\n', path='t.txt')
    eb = ed.cur()
    ed.options.set('statusline', 'false', local=eb.local_options)
    ed.options.set('infobar', 'false', local=eb.local_options)
    ed.options.set('colorcolumn', '5', local=eb.local_options)

    model = _hostcall(ed, 'ed.viewport-cues', 4, 10)
    assert isinstance(model, dict)
    assert model['rows'][0]['colorcolumn_x'] == 4
    assert model['rows'][0]['colorcolumn_blank'] == 1






def test_docs_cues_model_keeps_zero_viewport_metric_schema(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv('MICROMAX_DOCS', str(tmp_path))
    doc = tmp_path / '10-zero-schema.md'
    doc.write_text(
        '# Heading\n\n'
        '```python\n'
        'print(1)\n'
        '```\n\n'
        '<span>raw</span> and \\*escaped\\*\n',
        encoding='utf-8',
    )

    ed = Editor()
    assert ed.open_help_doc('zero-schema') is True

    active_model = ed.docs_cues_model(10, 80)
    zero_model = ed.docs_cues_model(0, 0)

    assert zero_model['active'] == 0
    assert zero_model['enabled'] == 1
    assert zero_model['rows'] == []
    assert set(zero_model) == set(active_model)
    for key in DOCS_CUE_ZERO_METRIC_KEYS:
        assert key in zero_model
        assert zero_model[key] == 0


def test_docs_cues_model_tracks_visible_help_buffer_scanability_spans(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv('MICROMAX_DOCS', str(tmp_path))
    doc = tmp_path / '10-scanability-demo.md'
    doc.write_text(
        '# Heading\n\n'
        '- [x] done item\n'
        '> [!NOTE] quoted\n'
        'A [link](other.md) and `code`\n'
        '| A | B |\n'
        '| --- | --- |\n',
        encoding='utf-8',
    )

    ed = Editor()
    assert ed.open_help_doc('scanability-demo') is True
    eb = ed.cur()
    ed.options.set('statusline', 'false', local=eb.local_options)
    ed.options.set('infobar', 'false', local=eb.local_options)

    model = ed.docs_cues_model(10, 60)
    assert model['active'] == 1
    assert model['enabled'] == 1
    assert model['help_doc'] == 'scanability-demo'
    assert model['row_count'] == model['height']
    assert model['rows'][0]['line_role'] == 'heading-title'
    task_row = next(row for row in model['rows'] if row['line'] == 2)
    assert task_row['bold_spans'] == [[0, 1], [2, 5]]
    assert task_row['dim_spans']
    quote_row = next(row for row in model['rows'] if row['line'] == 3)
    assert quote_row['bold_spans'] and quote_row['bold_spans'][0][0] == 0 and quote_row['bold_spans'][0][1] >= 2
    link_row = next(row for row in model['rows'] if row['link_count'] > 0)
    assert link_row['link_spans'] == [[3, 7]]
    assert link_row['dim_spans']
    table_delim = next(row for row in model['rows'] if row['line_role'] == 'table-delimiter')
    assert table_delim['line'] == 6





def test_docs_cues_model_exposes_row_local_link_metadata(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv('MICROMAX_DOCS', str(tmp_path))
    doc = tmp_path / '10-docs-link-metadata.md'
    doc.write_text(
        '# Title\n\n'
        'See [local](#frag), [topic](other-topic#part), [file](other.md#part), <https://example.invalid/>, and [^note].\n\n'
        '## Frag {#frag}\n\n'
        '[^note]: footnote body\n',
        encoding='utf-8',
    )

    ed = Editor()
    assert ed.open_help_doc('docs-link-metadata') is True
    eb = ed.cur()
    ed.options.set('statusline', 'false', local=eb.local_options)
    ed.options.set('infobar', 'false', local=eb.local_options)

    model = ed.docs_cues_model(12, 160)
    row = next(row for row in model['rows'] if row['link_count'] == 5)
    entries = list(row['link_entries'])
    assert [entry['target_kind'] for entry in entries] == [
        'fragment',
        'doc-fragment',
        'file-fragment',
        'external',
        'footnote',
    ]
    assert entries[0]['target_fragment'] == 'frag'
    assert entries[1]['target_doc'] == 'other-topic'
    assert entries[2]['target_doc'] == 'other.md'
    assert entries[3]['kind'] == 'autolink'
    assert entries[4]['target_fragment'] == '^note'
    assert [entry['target_kind'] for entry in row['local_doc_link_entries']] == [
        'doc-fragment',
        'file-fragment',
    ]
    assert [entry['target_kind'] for entry in row['fragment_link_entries']] == [
        'fragment',
        'doc-fragment',
        'file-fragment',
        'footnote',
    ]
    assert [entry['target_kind'] for entry in row['external_link_entries']] == ['external']
    assert [entry['target_kind'] for entry in row['footnote_link_entries']] == ['footnote']
    assert row['local_doc_link_count'] == 2
    assert row['fragment_link_count'] == 4
    assert row['external_link_count'] == 1
    assert row['footnote_link_count'] == 1
    assert model['link_rows'] >= 1
    assert model['link_entry_count'] == 5
    assert model['local_doc_link_rows'] == 1
    assert model['fragment_link_rows'] == 1
    assert model['external_link_rows'] == 1
    assert model['footnote_link_rows'] == 1
    assert model['local_doc_link_count'] == 2
    assert model['fragment_link_count'] == 4
    assert model['external_link_count'] == 1
    assert model['footnote_link_count'] == 1


def test_docs_cues_model_exposes_row_local_link_source_kind_metadata(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv('MICROMAX_DOCS', str(tmp_path))
    doc = tmp_path / '10-docs-link-source-kind-metadata.md'
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

    ed = Editor()
    assert ed.open_help_doc('docs-link-source-kind-metadata') is True
    eb = ed.cur()
    ed.options.set('statusline', 'false', local=eb.local_options)
    ed.options.set('infobar', 'false', local=eb.local_options)

    model = ed.docs_cues_model(12, 160)
    row = next(row for row in model['rows'] if row['link_count'] == 6)
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
    assert row['inline_link_count'] == 1
    assert row['reference_link_count'] == 3
    assert row['full_reference_link_count'] == 1
    assert row['collapsed_reference_link_count'] == 1
    assert row['shortcut_reference_link_count'] == 1
    assert row['autolink_count'] == 1
    assert row['footnote_ref_count'] == 1
    assert model['inline_link_rows'] == 1
    assert model['reference_link_rows'] == 1
    assert model['full_reference_link_rows'] == 1
    assert model['collapsed_reference_link_rows'] == 1
    assert model['shortcut_reference_link_rows'] == 1
    assert model['autolink_rows'] == 1
    assert model['footnote_ref_rows'] == 1
    assert model['inline_link_count'] == 1
    assert model['reference_link_count'] == 3
    assert model['full_reference_link_count'] == 1
    assert model['collapsed_reference_link_count'] == 1
    assert model['shortcut_reference_link_count'] == 1
    assert model['autolink_count'] == 1
    assert model['footnote_ref_count'] == 1


def test_docs_cues_model_exposes_row_local_code_metadata(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv('MICROMAX_DOCS', str(tmp_path))
    doc = tmp_path / '10-docs-code-metadata.md'
    doc.write_text(
        '# Title\n\n'
        'Use `status`, ``tick`inside``, and `  padded  `.\n',
        encoding='utf-8',
    )

    ed = Editor()
    assert ed.open_help_doc('docs-code-metadata') is True
    eb = ed.cur()
    ed.options.set('statusline', 'false', local=eb.local_options)
    ed.options.set('infobar', 'false', local=eb.local_options)

    model = ed.docs_cues_model(8, 120)
    row = next(row for row in model['rows'] if row['code_count'] == 3)
    entries = list(row['code_entries'])
    assert [entry['text'] for entry in entries] == [
        'status',
        'tick`inside',
        '  padded  ',
    ]
    assert [entry['delimiter_length'] for entry in entries] == [1, 2, 1]
    assert [entry['delimiter_kind'] for entry in entries] == [
        'single-backtick',
        'multi-backtick',
        'single-backtick',
    ]
    assert [entry['text'] for entry in row['single_backtick_code_entries']] == ['status', '  padded  ']
    assert [entry['text'] for entry in row['multi_backtick_code_entries']] == ['tick`inside']
    assert row['single_backtick_code_count'] == 2
    assert row['multi_backtick_code_count'] == 1
    assert entries[1]['start'] < entries[1]['body_start'] < entries[1]['body_end'] < entries[1]['end']
    assert model['code_rows'] >= 1
    assert model['code_entry_count'] == 3
    assert model['single_backtick_code_rows'] == 1
    assert model['multi_backtick_code_rows'] == 1
    assert model['single_backtick_code_count'] == 2
    assert model['multi_backtick_code_count'] == 1


def test_docs_cues_model_exposes_row_local_inline_markup_metadata(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv('MICROMAX_DOCS', str(tmp_path))
    doc = tmp_path / '10-docs-inline-markup-metadata.md'
    doc.write_text(
        '# Title\n\n'
        'Use **strong**, *soft*, _also_, and ~~gone~~ beside `*code*`.\n',
        encoding='utf-8',
    )

    ed = Editor()
    assert ed.open_help_doc('docs-inline-markup-metadata') is True
    eb = ed.cur()
    ed.options.set('statusline', 'false', local=eb.local_options)
    ed.options.set('infobar', 'false', local=eb.local_options)

    model = ed.docs_cues_model(8, 140)
    row = next(row for row in model['rows'] if row['markup_count'] == 4)
    entries = list(row['markup_entries'])
    assert [(entry['kind'], entry['delimiter'], entry['delimiter_kind'], entry['text']) for entry in entries] == [
        ('strong', '**', 'asterisk', 'strong'),
        ('emphasis', '*', 'asterisk', 'soft'),
        ('emphasis', '_', 'underscore', 'also'),
        ('strike', '~~', 'tilde', 'gone'),
    ]
    assert [entry['delimiter_length'] for entry in entries] == [2, 1, 1, 2]
    assert [entry['text'] for entry in row['strong_markup_entries']] == ['strong']
    assert [entry['text'] for entry in row['emphasis_markup_entries']] == ['soft', 'also']
    assert [entry['text'] for entry in row['strike_markup_entries']] == ['gone']
    assert [entry['text'] for entry in row['asterisk_markup_entries']] == ['strong', 'soft']
    assert [entry['text'] for entry in row['underscore_markup_entries']] == ['also']
    assert [entry['text'] for entry in row['tilde_markup_entries']] == ['gone']
    assert row['strong_markup_count'] == 1
    assert row['emphasis_markup_count'] == 2
    assert row['strike_markup_count'] == 1
    assert row['asterisk_markup_count'] == 2
    assert row['underscore_markup_count'] == 1
    assert row['tilde_markup_count'] == 1
    assert model['markup_rows'] >= 1
    assert model['markup_entry_count'] == 4
    assert model['strong_markup_rows'] == 1
    assert model['emphasis_markup_rows'] == 1
    assert model['strike_markup_rows'] == 1
    assert model['asterisk_markup_rows'] == 1
    assert model['underscore_markup_rows'] == 1
    assert model['tilde_markup_rows'] == 1
    assert model['strong_entry_count'] == 1
    assert model['emphasis_entry_count'] == 2
    assert model['strike_entry_count'] == 1
    assert model['asterisk_markup_count'] == 2
    assert model['underscore_markup_count'] == 1
    assert model['tilde_markup_count'] == 1


def test_docs_cues_model_exposes_row_local_literal_source_metadata(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv('MICROMAX_DOCS', str(tmp_path))
    doc = tmp_path / '10-docs-literal-source-metadata.md'
    doc.write_text(
        '# Title\n\n'
        'Use <kbd>, </kbd>, \\[tag], and \\<https://example.invalid/escaped>.\n',
        encoding='utf-8',
    )

    ed = Editor()
    assert ed.open_help_doc('docs-literal-source-metadata') is True
    eb = ed.cur()
    ed.options.set('statusline', 'false', local=eb.local_options)
    ed.options.set('infobar', 'false', local=eb.local_options)

    model = ed.docs_cues_model(8, 160)
    row = next(row for row in model['rows'] if row['literal_count'] == 4)
    entries = list(row['literal_entries'])
    assert [(entry['kind'], entry['text'], entry['detail']) for entry in entries] == [
        ('raw-html-tag', '<kbd>', 'kbd'),
        ('raw-html-tag', '</kbd>', 'kbd'),
        ('escaped-markdown', r'\[', '['),
        ('escaped-markdown', r'\<', '<'),
    ]
    assert [entry['text'] for entry in row['raw_html_literal_entries']] == ['<kbd>', '</kbd>']
    assert [entry['text'] for entry in row['escaped_markdown_entries']] == [r'\[', r'\<']
    assert row['raw_html_literal_count'] == 2
    assert row['escaped_markdown_count'] == 2
    assert model['literal_rows'] >= 1
    assert model['literal_entry_count'] == 4
    assert model['raw_html_rows'] == 1
    assert model['escaped_markdown_rows'] == 1
    assert model['raw_html_entry_count'] == 2
    assert model['escaped_markdown_entry_count'] == 2


def test_docs_cues_model_exposes_row_local_image_metadata(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv('MICROMAX_DOCS', str(tmp_path))
    doc = tmp_path / '10-docs-image-metadata.md'
    doc.write_text(
        '# Title\n\n'
        'See ![local](#frag), ![topic](other-topic#part), ![file](other.md#part), and ![ext](https://example.invalid/img.png).\n\n'
        '## Frag {#frag}\n',
        encoding='utf-8',
    )

    ed = Editor()
    assert ed.open_help_doc('docs-image-metadata') is True
    eb = ed.cur()
    ed.options.set('statusline', 'false', local=eb.local_options)
    ed.options.set('infobar', 'false', local=eb.local_options)

    model = ed.docs_cues_model(12, 180)
    row = next(row for row in model['rows'] if row['image_count'] == 4)
    entries = list(row['image_entries'])
    assert [entry['target_kind'] for entry in entries] == [
        'fragment',
        'doc-fragment',
        'file-fragment',
        'external',
    ]
    assert [entry['target_kind'] for entry in row['local_doc_image_entries']] == [
        'doc-fragment',
        'file-fragment',
    ]
    assert [entry['target_kind'] for entry in row['fragment_image_entries']] == [
        'fragment',
        'doc-fragment',
        'file-fragment',
    ]
    assert [entry['target_kind'] for entry in row['external_image_entries']] == ['external']
    assert row['footnote_image_entries'] == []
    assert row['local_doc_image_count'] == 2
    assert row['fragment_image_count'] == 3
    assert row['external_image_count'] == 1
    assert row['footnote_image_count'] == 0
    assert entries[0]['alt_text'] == 'local'
    assert entries[1]['target_doc'] == 'other-topic'
    assert entries[2]['target_doc'] == 'other.md'
    assert entries[3]['target'] == 'https://example.invalid/img.png'
    assert model['image_rows'] >= 1
    assert model['image_entry_count'] == 4
    assert model['local_doc_image_rows'] == 1
    assert model['fragment_image_rows'] == 1
    assert model['external_image_rows'] == 1
    assert model['footnote_image_rows'] == 0
    assert model['local_doc_image_count'] == 2
    assert model['fragment_image_count'] == 3
    assert model['external_image_count'] == 1
    assert model['footnote_image_count'] == 0




def test_docs_cues_model_exposes_row_local_image_target_slices_for_footnotes(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv('MICROMAX_DOCS', str(tmp_path))
    doc = tmp_path / '10-docs-image-footnote-metadata.md'
    doc.write_text(
        '# Title\n\n'
        'See ![note](#^fig-note).\n\n'
        '[^fig-note]: footnote target\n',
        encoding='utf-8',
    )

    ed = Editor()
    assert ed.open_help_doc('docs-image-footnote-metadata') is True
    eb = ed.cur()
    ed.options.set('statusline', 'false', local=eb.local_options)
    ed.options.set('infobar', 'false', local=eb.local_options)

    model = ed.docs_cues_model(10, 120)
    row = next(row for row in model['rows'] if row['footnote_image_count'] == 1)
    assert [entry['target_kind'] for entry in row['image_entries']] == ['footnote']
    assert [entry['target_kind'] for entry in row['fragment_image_entries']] == ['footnote']
    assert [entry['target_kind'] for entry in row['footnote_image_entries']] == ['footnote']
    assert row['local_doc_image_entries'] == []
    assert row['external_image_entries'] == []
    assert model['footnote_image_rows'] == 1
    assert model['footnote_image_count'] == 1
    assert model['fragment_image_rows'] == 1
    assert model['fragment_image_count'] == 1


def test_docs_cues_model_exposes_row_local_image_source_kind_metadata(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv('MICROMAX_DOCS', str(tmp_path))
    doc = tmp_path / '10-docs-image-source-kind-metadata.md'
    doc.write_text(
        '# Title\n\n'
        'See ![inline](#frag), ![full][shot], ![collapsed][], and ![shortcut].\n\n'
        '[shot]: other-topic#part\n'
        '[collapsed]: collapse.md#snap\n'
        '[shortcut]: other.md#snap\n'
        '## Frag {#frag}\n',
        encoding='utf-8',
    )

    ed = Editor()
    assert ed.open_help_doc('docs-image-source-kind-metadata') is True
    eb = ed.cur()
    ed.options.set('statusline', 'false', local=eb.local_options)
    ed.options.set('infobar', 'false', local=eb.local_options)

    model = ed.docs_cues_model(12, 180)
    row = next(row for row in model['rows'] if row['image_count'] == 4)
    assert [entry['source_kind'] for entry in row['image_entries']] == [
        'inline',
        'reference',
        'reference',
        'reference',
    ]
    assert [entry['reference_form'] for entry in row['image_entries']] == [
        '',
        'full',
        'collapsed',
        'shortcut',
    ]
    assert [entry['alt_text'] for entry in row['inline_image_entries']] == ['inline']
    assert [entry['alt_text'] for entry in row['reference_image_entries']] == ['full', 'collapsed', 'shortcut']
    assert [entry['alt_text'] for entry in row['full_reference_image_entries']] == ['full']
    assert [entry['alt_text'] for entry in row['collapsed_reference_image_entries']] == ['collapsed']
    assert [entry['alt_text'] for entry in row['shortcut_reference_image_entries']] == ['shortcut']
    assert row['inline_image_count'] == 1
    assert row['reference_image_count'] == 3
    assert row['full_reference_image_count'] == 1
    assert row['collapsed_reference_image_count'] == 1
    assert row['shortcut_reference_image_count'] == 1
    assert model['inline_image_rows'] == 1
    assert model['reference_image_rows'] == 1
    assert model['full_reference_image_rows'] == 1
    assert model['collapsed_reference_image_rows'] == 1
    assert model['shortcut_reference_image_rows'] == 1
    assert model['inline_image_count'] == 1
    assert model['reference_image_count'] == 3
    assert model['full_reference_image_count'] == 1
    assert model['collapsed_reference_image_count'] == 1
    assert model['shortcut_reference_image_count'] == 1


def test_docs_cues_model_exposes_row_local_structure_metadata(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv('MICROMAX_DOCS', str(tmp_path))
    doc = tmp_path / '10-docs-structure-metadata.md'
    doc.write_text(
        '# Title\n\n'
        '- [x] done item\n'
        '1. [ ] todo item\n'
        '> [!WARNING] careful now\n'
        '---\n',
        encoding='utf-8',
    )

    ed = Editor()
    assert ed.open_help_doc('docs-structure-metadata') is True
    eb = ed.cur()
    ed.options.set('statusline', 'false', local=eb.local_options)
    ed.options.set('infobar', 'false', local=eb.local_options)

    model = ed.docs_cues_model(10, 120)

    task_row = next(row for row in model['rows'] if row['text'] == '- [x] done item')
    assert [(entry['kind'], entry['text']) for entry in task_row['structure_entries']] == [
        ('list-marker', '-'),
        ('task-checkbox', '[x]'),
    ]
    assert task_row['structure_entries'][0]['list_kind'] == 'bullet'
    assert task_row['list_entries'] == [
        {
            'kind': 'list-marker',
            'start': 0,
            'end': 1,
            'text': '-',
            'list_kind': 'bullet',
            'marker': '-',
        },
    ]
    assert task_row['list_count'] == 1
    assert task_row['bullet_list_count'] == 1
    assert task_row['ordered_list_count'] == 0
    assert task_row['structure_entries'][1]['checked'] == 1
    assert task_row['structure_entries'][1]['body_start'] < task_row['structure_entries'][1]['body_end']
    assert task_row['task_entries'] == [
        {
            'kind': 'task-checkbox',
            'start': 2,
            'end': 5,
            'text': '[x]',
            'checked': 1,
            'list_kind': 'bullet',
            'list_marker': '-',
            'body_start': 6,
            'body_end': 15,
        },
    ]
    assert task_row['checked_task_entries'] == task_row['task_entries']
    assert task_row['unchecked_task_entries'] == []
    assert task_row['bullet_task_entries'] == task_row['task_entries']
    assert task_row['ordered_task_entries'] == []
    assert task_row['task_count'] == 1
    assert task_row['checked_task_count'] == 1
    assert task_row['unchecked_task_count'] == 0
    assert task_row['bullet_task_count'] == 1
    assert task_row['ordered_task_count'] == 0
    assert task_row['structure_count'] == 2

    ordered_row = next(row for row in model['rows'] if row['text'] == '1. [ ] todo item')
    assert [(entry['kind'], entry['text']) for entry in ordered_row['structure_entries']] == [
        ('list-marker', '1.'),
        ('task-checkbox', '[ ]'),
    ]
    assert ordered_row['structure_entries'][0]['list_kind'] == 'ordered'
    assert ordered_row['list_entries'] == [
        {
            'kind': 'list-marker',
            'start': 0,
            'end': 2,
            'text': '1.',
            'list_kind': 'ordered',
            'marker': '1.',
        },
    ]
    assert ordered_row['bullet_list_count'] == 0
    assert ordered_row['ordered_list_count'] == 1
    assert ordered_row['structure_entries'][1]['checked'] == 0
    assert ordered_row['task_entries'][0]['checked'] == 0
    assert ordered_row['task_entries'][0]['list_kind'] == 'ordered'
    assert ordered_row['task_entries'][0]['list_marker'] == '1.'
    assert ordered_row['checked_task_entries'] == []
    assert ordered_row['unchecked_task_entries'] == ordered_row['task_entries']
    assert ordered_row['bullet_task_entries'] == []
    assert ordered_row['ordered_task_entries'] == ordered_row['task_entries']
    assert ordered_row['task_count'] == 1
    assert ordered_row['checked_task_count'] == 0
    assert ordered_row['unchecked_task_count'] == 1
    assert ordered_row['bullet_task_count'] == 0
    assert ordered_row['ordered_task_count'] == 1
    assert model['checked_task_rows'] == 1
    assert model['unchecked_task_rows'] == 1
    assert model['checked_task_entry_count'] == 1
    assert model['unchecked_task_entry_count'] == 1

    quote_row = next(row for row in model['rows'] if row['text'] == '> [!WARNING] careful now')
    assert [(entry['kind'], entry['text']) for entry in quote_row['structure_entries']] == [
        ('blockquote-prefix', '> '),
        ('blockquote-alert', '[!WARNING]'),
    ]
    assert quote_row['structure_entries'][0]['depth'] == 1
    assert quote_row['structure_entries'][0]['body_start'] == 2
    assert quote_row['structure_entries'][1]['alert_kind'] == 'warning'
    assert quote_row['blockquote_entries'] == [
        {
            'kind': 'blockquote-prefix',
            'start': 0,
            'end': 2,
            'text': '> ',
            'depth': 1,
            'body_start': 2,
            'body_end': 24,
        },
    ]
    assert quote_row['blockquote_alert_entries'] == [
        {
            'kind': 'blockquote-alert',
            'start': 2,
            'end': 12,
            'text': '[!WARNING]',
            'alert_kind': 'warning',
        },
    ]
    assert quote_row['warning_blockquote_alert_entries'] == [
        {
            'kind': 'blockquote-alert',
            'start': 2,
            'end': 12,
            'text': '[!WARNING]',
            'alert_kind': 'warning',
        },
    ]
    assert quote_row['note_blockquote_alert_entries'] == []
    assert quote_row['tip_blockquote_alert_entries'] == []
    assert quote_row['important_blockquote_alert_entries'] == []
    assert quote_row['caution_blockquote_alert_entries'] == []
    assert quote_row['blockquote_count'] == 1
    assert quote_row['blockquote_alert_count'] == 1
    assert quote_row['warning_blockquote_alert_count'] == 1
    assert quote_row['note_blockquote_alert_count'] == 0
    assert quote_row['tip_blockquote_alert_count'] == 0
    assert quote_row['important_blockquote_alert_count'] == 0
    assert quote_row['caution_blockquote_alert_count'] == 0
    assert quote_row['thematic_break_count'] == 0

    break_row = next(row for row in model['rows'] if row['line_role'] == 'thematic-break')
    assert [(entry['kind'], entry['text']) for entry in break_row['structure_entries']] == [
        ('thematic-break', '---'),
    ]
    assert break_row['structure_entries'][0]['marker'] == '-'
    assert break_row['structure_entries'][0]['marker_count'] == 3
    assert break_row['thematic_break_entries'] == [
        {
            'kind': 'thematic-break',
            'start': 0,
            'end': 3,
            'text': '---',
            'marker': '-',
            'marker_count': 3,
        },
    ]
    assert break_row['blockquote_entries'] == []
    assert break_row['blockquote_alert_entries'] == []
    assert break_row['blockquote_count'] == 0
    assert break_row['blockquote_alert_count'] == 0
    assert break_row['thematic_break_count'] == 1

    assert model['structure_rows'] == 4
    assert model['structure_entry_count'] == 7
    assert model['list_rows'] == 2
    assert model['list_entry_count'] == 2
    assert model['bullet_list_rows'] == 1
    assert model['ordered_list_rows'] == 1
    assert model['bullet_list_entry_count'] == 1
    assert model['ordered_list_entry_count'] == 1
    assert model['task_rows'] == 2
    assert model['task_entry_count'] == 2
    assert model['checked_task_entry_count'] == 1
    assert model['unchecked_task_entry_count'] == 1
    assert model['bullet_task_rows'] == 1
    assert model['ordered_task_rows'] == 1
    assert model['bullet_task_entry_count'] == 1
    assert model['ordered_task_entry_count'] == 1
    assert model['blockquote_rows'] == 1
    assert model['blockquote_entry_count'] == 1
    assert model['blockquote_alert_rows'] == 1
    assert model['blockquote_alert_entry_count'] == 1
    assert model['warning_blockquote_alert_rows'] == 1
    assert model['warning_blockquote_alert_entry_count'] == 1
    assert model['note_blockquote_alert_rows'] == 0
    assert model['tip_blockquote_alert_rows'] == 0
    assert model['important_blockquote_alert_rows'] == 0
    assert model['caution_blockquote_alert_rows'] == 0
    assert model['thematic_break_rows'] == 1
    assert model['thematic_break_entry_count'] == 1


def test_docs_cues_model_exposes_row_local_table_metadata(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv('MICROMAX_DOCS', str(tmp_path))
    doc = tmp_path / '10-docs-table-metadata.md'
    doc.write_text(
        '# Title\n\n'
        '| Key | Value | Count | Note |\n'
        '| :--- | :---: | ---: | --- |\n'
        '| one | alpha beta | 7 | plain |\n',
        encoding='utf-8',
    )

    ed = Editor()
    assert ed.open_help_doc('docs-table-metadata') is True
    eb = ed.cur()
    ed.options.set('statusline', 'false', local=eb.local_options)
    ed.options.set('infobar', 'false', local=eb.local_options)

    model = ed.docs_cues_model(10, 120)

    header_row = next(row for row in model['rows'] if row['table_kind'] == 'header')
    assert [(entry['kind'], entry['column'], entry['text'], entry['align']) for entry in header_row['table_entries']] == [
        ('header-cell', 0, 'Key', 'left'),
        ('header-cell', 1, 'Value', 'center'),
        ('header-cell', 2, 'Count', 'right'),
        ('header-cell', 3, 'Note', 'default'),
    ]
    assert [(entry['kind'], entry['column'], entry['text']) for entry in header_row['table_header_entries']] == [
        ('header-cell', 0, 'Key'),
        ('header-cell', 1, 'Value'),
        ('header-cell', 2, 'Count'),
        ('header-cell', 3, 'Note'),
    ]
    assert header_row['table_body_entries'] == []
    assert header_row['table_delimiter_entries'] == []
    assert header_row['table_count'] == 4
    assert header_row['table_header_count'] == 4
    assert header_row['table_body_count'] == 0
    assert header_row['table_delimiter_count'] == 0
    assert [entry['text'] for entry in header_row['left_aligned_table_entries']] == ['Key']
    assert [entry['text'] for entry in header_row['center_aligned_table_entries']] == ['Value']
    assert [entry['text'] for entry in header_row['right_aligned_table_entries']] == ['Count']
    assert [entry['text'] for entry in header_row['default_aligned_table_entries']] == ['Note']

    delim_row = next(row for row in model['rows'] if row['table_kind'] == 'delimiter')
    assert [(entry['kind'], entry['column'], entry['align']) for entry in delim_row['table_entries']] == [
        ('delimiter-cell', 0, 'left'),
        ('delimiter-cell', 1, 'center'),
        ('delimiter-cell', 2, 'right'),
        ('delimiter-cell', 3, 'default'),
    ]
    assert [(entry['kind'], entry['column'], entry['align']) for entry in delim_row['table_delimiter_entries']] == [
        ('delimiter-cell', 0, 'left'),
        ('delimiter-cell', 1, 'center'),
        ('delimiter-cell', 2, 'right'),
        ('delimiter-cell', 3, 'default'),
    ]
    assert delim_row['table_header_entries'] == []
    assert delim_row['table_body_entries'] == []
    assert [entry['marker_count'] for entry in delim_row['table_entries']] == [3, 3, 3, 3]
    assert delim_row['table_header_count'] == 0
    assert delim_row['table_body_count'] == 0
    assert delim_row['table_delimiter_count'] == 4
    assert [entry['align'] for entry in delim_row['left_aligned_table_entries']] == ['left']
    assert [entry['align'] for entry in delim_row['center_aligned_table_entries']] == ['center']
    assert [entry['align'] for entry in delim_row['right_aligned_table_entries']] == ['right']
    assert [entry['align'] for entry in delim_row['default_aligned_table_entries']] == ['default']

    body_row = next(row for row in model['rows'] if row['table_kind'] == 'body')
    assert [(entry['kind'], entry['column'], entry['text'], entry['align']) for entry in body_row['table_entries']] == [
        ('body-cell', 0, 'one', 'left'),
        ('body-cell', 1, 'alpha beta', 'center'),
        ('body-cell', 2, '7', 'right'),
        ('body-cell', 3, 'plain', 'default'),
    ]
    assert [(entry['kind'], entry['column'], entry['text']) for entry in body_row['table_body_entries']] == [
        ('body-cell', 0, 'one'),
        ('body-cell', 1, 'alpha beta'),
        ('body-cell', 2, '7'),
        ('body-cell', 3, 'plain'),
    ]
    assert body_row['table_header_entries'] == []
    assert body_row['table_delimiter_entries'] == []
    assert body_row['table_header_count'] == 0
    assert body_row['table_body_count'] == 4
    assert body_row['table_delimiter_count'] == 0
    assert [entry['text'] for entry in body_row['left_aligned_table_entries']] == ['one']
    assert [entry['text'] for entry in body_row['center_aligned_table_entries']] == ['alpha beta']
    assert [entry['text'] for entry in body_row['right_aligned_table_entries']] == ['7']
    assert [entry['text'] for entry in body_row['default_aligned_table_entries']] == ['plain']

    assert model['table_rows'] == 3
    assert model['table_entry_count'] == 12
    assert model['table_header_rows'] == 1
    assert model['table_body_rows'] == 1
    assert model['table_delimiter_rows'] == 1
    assert model['default_aligned_table_rows'] == 3
    assert model['left_aligned_table_rows'] == 3
    assert model['center_aligned_table_rows'] == 3
    assert model['right_aligned_table_rows'] == 3
    assert model['table_header_cell_count'] == 4
    assert model['table_body_cell_count'] == 4
    assert model['table_delimiter_cell_count'] == 4
    assert model['default_aligned_table_entry_count'] == 3
    assert model['left_aligned_table_entry_count'] == 3
    assert model['center_aligned_table_entry_count'] == 3
    assert model['right_aligned_table_entry_count'] == 3


def test_docs_cues_model_exposes_row_local_heading_metadata(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv('MICROMAX_DOCS', str(tmp_path))
    doc = tmp_path / '10-docs-heading-metadata.md'
    doc.write_text(
        '# Alpha Beta {#start-here}\n\n'
        'Setext topic\n'
        '-----\n\n'
        '### Gamma Level\n',
        encoding='utf-8',
    )

    ed = Editor()
    assert ed.open_help_doc('docs-heading-metadata') is True
    eb = ed.cur()
    ed.options.set('statusline', 'false', local=eb.local_options)
    ed.options.set('infobar', 'false', local=eb.local_options)

    model = ed.docs_cues_model(8, 120)

    atx_row = next(row for row in model['rows'] if row['text'].startswith('# Alpha Beta'))
    assert atx_row['heading_count'] == 1
    assert atx_row['heading_entries'][0]['role'] == 'title'
    assert atx_row['heading_entries'][0]['source_kind'] == 'atx'
    assert atx_row['heading_entries'][0]['title'] == 'Alpha Beta'
    assert atx_row['heading_entries'][0]['fragment'] == 'start-here'
    assert atx_row['heading_entries'][0]['fragment_source'] == 'explicit'
    assert atx_row['heading_entries'][0]['text'] == '# Alpha Beta {#start-here}'
    assert atx_row['heading_title_entries'] == atx_row['heading_entries']
    assert atx_row['heading_underline_entries'] == []
    assert atx_row['atx_heading_entries'] == atx_row['heading_entries']
    assert atx_row['setext_heading_entries'] == []
    assert atx_row['h1_heading_entries'] == atx_row['heading_entries']
    assert atx_row['explicit_fragment_heading_entries'] == atx_row['heading_entries']
    assert atx_row['auto_fragment_heading_entries'] == []
    assert atx_row['h2_heading_entries'] == []
    assert atx_row['h3_heading_entries'] == []
    assert atx_row['heading_title_count'] == 1
    assert atx_row['heading_underline_count'] == 0
    assert atx_row['atx_heading_count'] == 1
    assert atx_row['setext_heading_count'] == 0
    assert atx_row['h1_heading_count'] == 1
    assert atx_row['h2_heading_count'] == 0
    assert atx_row['explicit_fragment_heading_count'] == 1
    assert atx_row['auto_fragment_heading_count'] == 0

    setext_title_row = next(row for row in model['rows'] if row['text'] == 'Setext topic')
    assert setext_title_row['heading_entries'][0]['role'] == 'title'
    assert setext_title_row['heading_entries'][0]['source_kind'] == 'setext'
    assert setext_title_row['heading_entries'][0]['title'] == 'Setext topic'
    assert setext_title_row['heading_entries'][0]['fragment'] == 'setext-topic'
    assert setext_title_row['heading_entries'][0]['fragment_source'] == 'auto'
    assert setext_title_row['heading_title_entries'] == setext_title_row['heading_entries']
    assert setext_title_row['heading_underline_entries'] == []
    assert setext_title_row['atx_heading_entries'] == []
    assert setext_title_row['setext_heading_entries'] == setext_title_row['heading_entries']
    assert setext_title_row['h2_heading_entries'] == setext_title_row['heading_entries']
    assert setext_title_row['h1_heading_entries'] == []
    assert setext_title_row['h3_heading_entries'] == []
    assert setext_title_row['explicit_fragment_heading_entries'] == []
    assert setext_title_row['auto_fragment_heading_entries'] == setext_title_row['heading_entries']

    underline_row = next(row for row in model['rows'] if row['line_role'] == 'heading-underline')
    assert underline_row['heading_count'] == 1
    assert underline_row['heading_entries'][0]['role'] == 'underline'
    assert underline_row['heading_entries'][0]['source_kind'] == 'setext'
    assert underline_row['heading_entries'][0]['fragment'] == 'setext-topic'
    assert underline_row['heading_entries'][0]['marker'] == '-'
    assert underline_row['heading_entries'][0]['marker_count'] == 5
    assert underline_row['heading_title_entries'] == []
    assert underline_row['heading_underline_entries'] == underline_row['heading_entries']
    assert underline_row['atx_heading_entries'] == []
    assert underline_row['setext_heading_entries'] == underline_row['heading_entries']
    assert underline_row['h2_heading_entries'] == underline_row['heading_entries']
    assert underline_row['explicit_fragment_heading_entries'] == []
    assert underline_row['auto_fragment_heading_entries'] == underline_row['heading_entries']

    h3_row = next(row for row in model['rows'] if row['text'] == '### Gamma Level')
    assert h3_row['heading_entries'][0]['level'] == 3
    assert h3_row['h1_heading_entries'] == []
    assert h3_row['h2_heading_entries'] == []
    assert h3_row['h3_heading_entries'] == h3_row['heading_entries']
    assert h3_row['explicit_fragment_heading_entries'] == []
    assert h3_row['auto_fragment_heading_entries'] == h3_row['heading_entries']
    assert h3_row['h3_heading_count'] == 1
    assert h3_row['auto_fragment_heading_count'] == 1

    assert model['heading_rows'] == 4
    assert model['heading_entry_count'] == 4
    assert model['heading_title_rows'] == 3
    assert model['heading_underline_rows'] == 1
    assert model['atx_heading_rows'] == 2
    assert model['setext_heading_rows'] == 2
    assert model['h1_heading_rows'] == 1
    assert model['h2_heading_rows'] == 2
    assert model['h3_heading_rows'] == 1
    assert model['h4_heading_rows'] == 0
    assert model['h5_heading_rows'] == 0
    assert model['h6_heading_rows'] == 0
    assert model['explicit_fragment_heading_rows'] == 1
    assert model['auto_fragment_heading_rows'] == 3
    assert model['heading_title_entry_count'] == 3
    assert model['heading_underline_entry_count'] == 1
    assert model['atx_heading_entry_count'] == 2
    assert model['setext_heading_entry_count'] == 2
    assert model['h1_heading_entry_count'] == 1
    assert model['h2_heading_entry_count'] == 2
    assert model['h3_heading_entry_count'] == 1
    assert model['h4_heading_entry_count'] == 0
    assert model['h5_heading_entry_count'] == 0
    assert model['h6_heading_entry_count'] == 0
    assert model['explicit_fragment_heading_entry_count'] == 1
    assert model['auto_fragment_heading_entry_count'] == 3


def test_docs_cues_model_exposes_row_local_section_metadata(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv('MICROMAX_DOCS', str(tmp_path))
    doc = tmp_path / '10-docs-section-metadata.md'
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

    ed = Editor()
    assert ed.open_help_doc('docs-section-metadata') is True
    eb = ed.cur()
    ed.options.set('statusline', 'false', local=eb.local_options)
    ed.options.set('infobar', 'false', local=eb.local_options)

    model = ed.docs_cues_model(16, 120)

    intro_row = next(row for row in model['rows'] if row['text'] == 'Intro line')
    assert intro_row['section_count'] == 1
    assert intro_row['section_entry']['title'] == 'Guide'
    assert intro_row['section_entry']['path'] == 'Guide'
    assert intro_row['section_entry']['path_titles'] == ['Guide']
    assert intro_row['section_entry']['fragment'] == 'guide'
    assert intro_row['section_entry']['level'] == 1
    assert intro_row['section_entry']['source_kind'] == 'atx'

    prose_row = next(row for row in model['rows'] if row['text'] == 'Section prose')
    assert prose_row['section_entry']['title'] == 'Links'
    assert prose_row['section_entry']['path'] == 'Guide › Links'
    assert prose_row['section_entry']['fragment'] == 'links'
    assert prose_row['section_entry']['heading_line'] == 4

    code_row = next(row for row in model['rows'] if row['text'] == 'code line')
    assert code_row['line_role'] == 'fenced-body'
    assert code_row['section_entry']['path'] == 'Guide › Links'

    nested_row = next(row for row in model['rows'] if row['text'] == 'Nested prose')
    assert nested_row['section_entry']['title'] == 'Deep Dive'
    assert nested_row['section_entry']['path'] == 'Guide › Links › Deep Dive'
    assert nested_row['section_entry']['fragment'] == 'deep-dive'
    assert nested_row['section_entry']['path_titles'] == ['Guide', 'Links', 'Deep Dive']

    assert model['section_distinct_count'] == 3
    assert model['section_rows'] >= 8


def test_ed_docs_cues_hostcall_exposes_shared_visible_help_buffer_spans(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv('MICROMAX_DOCS', str(tmp_path))
    doc = tmp_path / '10-docs-cues-hostcall.md'
    doc.write_text('# Title\n\nA [link](other.md)\n', encoding='utf-8')

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.open_help_doc('docs-cues-hostcall') is True

    model = _hostcall(ed, 'ed.docs-cues', 8, 40)
    assert isinstance(model, dict)
    assert model['help_doc'] == 'docs-cues-hostcall'
    assert model['rows'][0]['line_role'] == 'heading-title'
    assert next(row for row in model['rows'] if row['link_count'] > 0)['link_spans'] == [[3, 7]]


def test_ed_showchars_rows_hostcall_exposes_shared_visible_replacements() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('t.txt', '\t a\tb\n', path='t.txt')
    eb = ed.cur()
    ed.options.set('statusline', 'false', local=eb.local_options)
    ed.options.set('infobar', 'false', local=eb.local_options)
    ed.options.set('showchars', 'tab=>,space=.,itab=|>,ispace=:', local=eb.local_options)

    model = _hostcall(ed, 'ed.showchars-rows', 4, 10)
    assert isinstance(model, dict)
    assert model['changed_rows'] == 1
    assert model['rows'][0]['display_text'] == '|:a>b'
    assert model['rows'][0]['spans'] == [[0, 1], [1, 2], [3, 4]]


def test_display_rows_model_tracks_visible_showchars_and_overflow_text() -> None:
    ed = Editor()
    ed.new_buffer('t.txt', '\t a\tbcdefghij\n', path='t.txt')
    eb = ed.cur()
    ed.options.set('statusline', 'false', local=eb.local_options)
    ed.options.set('infobar', 'false', local=eb.local_options)
    ed.options.set('showchars', 'tab=>,space=.,itab=|>,ispace=:', local=eb.local_options)
    ed.options.set('overflowmarkers', 'true', local=eb.local_options)

    model = ed.display_rows_model(4, 6)
    row0 = next(row for row in model['rows'] if row['kind'] == 'viewport')
    assert row0['raw_text'] == '\t a\tbc'
    assert row0['viewport_text'] == '\t a\tbc'
    assert row0['viewport_display_text'] == '|:a>b>'
    assert row0['text'] == '|:a>b>'
    assert row0['display_changed'] == 1
    assert row0['overflow_cells'] == [[5, '>']]
    assert row0['overflow_left'] == 0
    assert row0['overflow_right'] == 1



def test_ed_display_rows_hostcall_exposes_shared_visible_display_text_rows() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('t.txt', 'abcdefghijklmno\n', path='t.txt')
    eb = ed.cur()
    ed.options.set('statusline', 'false', local=eb.local_options)
    ed.options.set('infobar', 'false', local=eb.local_options)
    ed.options.set('overflowmarkers', 'true', local=eb.local_options)
    eb.cursors[eb.primary].col = 6

    model = _hostcall(ed, 'ed.display-rows', 4, 6)
    assert isinstance(model, dict)
    row0 = next(row for row in model['rows'] if row['kind'] == 'viewport')
    assert row0['text'].startswith('<')
    assert row0['overflow_left'] == 1
    assert row0['overflow_right'] == 1
    assert row0['overflow_count'] == 2



def test_ed_prompt_panel_hostcall_exposes_shared_visible_picker_panel() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('t.mx', 'alpha\nbeta\n', path='t.mx')
    ed.enter_command_palette('status')

    model = _hostcall(ed, 'ed.prompt-panel', 12, 30)
    assert isinstance(model, dict)
    assert model['active'] == 1
    assert model['kind'] == 'palette'
    assert model['height'] == 3
    assert model['row_count'] == 3
    assert model['entries'][0]['type'] == 'header'
    assert model['entries'][1]['type'] == 'row'
    assert model['entries'][1]['screen_y'] == model['y'] + 1


def test_ed_gutter_model_hostcall_exposes_shared_visible_gutters() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('t.mx', '\n'.join(f'line {i}' for i in range(20)) + '\n', path='t.mx')
    eb = ed.cur()
    ed.options.set('ruler', 'true', local=eb.local_options)
    ed.options.set('scrollbar', 'true', local=eb.local_options)

    model = _hostcall(ed, 'ed.gutter-model', 8, 20)
    assert isinstance(model, dict)
    assert model['active'] == 1
    assert model['line_numbers_active'] == 1
    assert model['scrollbar_active'] == 1
    assert model['left_width'] == 3
    assert model['scrollbar_x'] == 19
    assert model['line_numbers'][0]['text'].strip() == '1'
    assert model['scrollbar_rows'][0]['kind'] == 'thumb'
    assert model['scrollbar_rows'][0]['screen_x'] == 19




def test_screen_rows_model_flattens_visible_screen_into_ordered_plain_text_rows() -> None:
    ed = Editor()
    ed.new_buffer('t.mx', 'alpha\nbeta\ngamma\n', path='t.mx')
    eb = ed.cur()
    ed.options.set('keymenu', 'true', local=eb.local_options)
    ed.options.set('ruler', 'true', local=eb.local_options)
    ed.options.set('scrollbar', 'true', local=eb.local_options)
    ed.enter_command_palette('status')

    model = ed.screen_rows_model(10, 30)
    assert model['active'] == 1
    assert model['row_count'] == 10
    first_viewport = next(row for row in model['rows'] if row['kind'] == 'viewport')
    assert first_viewport['text'].startswith('1 alpha')
    assert first_viewport['line'] == 0
    panel_row = next(row for row in model['rows'] if row['kind'] == 'prompt-panel')
    assert panel_row['text']
    prompt_row = next(row for row in model['rows'] if row['kind'] == 'interaction')
    assert prompt_row['text'].startswith(':status')
    assert prompt_row['cursor_here'] == 1
    assert prompt_row['cursor_x'] >= 1

def test_screen_model_composes_layout_window_bottom_rows_and_prompt_cursor() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('t.mx', 'alpha\nbeta\ngamma\n', path='t.mx')
    eb = ed.cur()
    ed.options.set('keymenu', 'true', local=eb.local_options)
    ed.enter_command_palette('status')

    model = ed.screen_model(10, 30)
    assert model['lines'] == 10
    assert model['cols'] == 30
    assert model['layout']['bottom_rows_count'] == 3
    assert model['gutter']['line_numbers_active'] == 0
    assert model['search_rows']['row_count'] == model['layout']['viewport_height']
    assert model['showchars_rows']['row_count'] == model['layout']['viewport_height']
    assert model['viewport_rows']['row_count'] == model['layout']['viewport_height']
    assert model['viewport_cues']['row_count'] == model['layout']['viewport_height']
    assert model['docs_cues']['row_count'] == model['layout']['viewport_height']
    assert model['display_rows']['row_count'] == model['lines']
    assert model['edit_window']['row_count'] >= 1
    assert model['prompt_panel']['active'] == 1
    assert model['prompt_panel']['row_count'] >= 1
    assert model['bottom_rows_count'] == 3
    assert [row['kind'] for row in model['bottom_rows']] == ['keymenu', 'interaction', 'statusline']
    assert model['bottom_rows'][1]['y'] == model['layout']['prompt_y']
    assert model['cursor']['mode'] == 'prompt'
    assert model['cursor']['screen_y'] == model['layout']['prompt_y']
    assert model['cursor']['screen_x'] >= 1




def test_ed_screen_model_hostcall_exposes_shared_visible_screen_snapshot() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('t.mx', 'alpha\nbeta\n', path='t.mx')
    eb = ed.cur()
    ed.options.set('keymenu', 'true', local=eb.local_options)
    ed.options.set('ruler', 'true', local=eb.local_options)
    ed.options.set('scrollbar', 'true', local=eb.local_options)
    ed.enter_command_palette('status')

    model = _hostcall(ed, 'ed.screen-model', 10, 30)
    assert isinstance(model, dict)
    assert model['layout']['bottom_rows_count'] == 3
    assert model['gutter']['line_numbers_active'] == 1
    assert model['search_rows']['row_count'] == model['layout']['viewport_height']
    assert model['viewport_cues']['row_count'] == model['layout']['viewport_height']
    assert model['docs_cues']['row_count'] == model['layout']['viewport_height']
    assert model['display_rows']['row_count'] == model['lines']
    assert model['prompt_panel']['active'] == 1
    assert model['bottom_rows'][0]['kind'] == 'keymenu'
    assert model['bottom_rows'][1]['slot'] == 'prompt'
    assert model['cursor']['mode'] == 'prompt'
    assert model['cursor']['screen_y'] == model['layout']['prompt_y']


def test_render_uses_shared_prompt_panel_model(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)

    class _FakeStdScr:
        def __init__(self) -> None:
            self.h = 10
            self.w = 30
            self.lines: dict[int, str] = {}
            self.cursor = (0, 0)

        def erase(self) -> None:
            self.lines = {}

        def getmaxyx(self) -> tuple[int, int]:
            return (self.h, self.w)

        def addnstr(self, y: int, x: int, s: str, n: int, *args) -> None:
            cur = self.lines.get(int(y), '')
            need = max(len(cur), int(x) + max(0, int(n)))
            buf = list(cur.ljust(need))
            txt = str(s)[: max(0, int(n))]
            for i, ch in enumerate(txt):
                pos = int(x) + i
                if pos >= len(buf):
                    buf.extend(' ' * (pos - len(buf) + 1))
                buf[pos] = ch
            self.lines[int(y)] = ''.join(buf).rstrip()

        def move(self, y: int, x: int) -> None:
            self.cursor = (int(y), int(x))

        def refresh(self) -> None:
            pass

    ed = Editor()
    ed.new_buffer('t.mx', 'alpha\nbeta\n', path='t.mx')
    ed.enter_command_palette('status')

    screen = ed.screen_model(10, 30)
    panel = dict(screen['prompt_panel'])
    fake = _FakeStdScr()
    _render(fake, ed)

    assert panel['active'] == 1
    assert fake.lines[panel['entries'][0]['screen_y']].startswith(panel['entries'][0]['text'])
    assert fake.lines[panel['entries'][1]['screen_y']].startswith(panel['entries'][1]['text'])


def test_render_uses_shared_viewport_cues_model(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)

    class _FakeStdScr:
        def __init__(self) -> None:
            self.h = 8
            self.w = 20
            self.lines: dict[int, str] = {}
            self.calls: list[tuple[int, int, str, int]] = []
            self.cursor = (0, 0)

        def erase(self) -> None:
            self.lines = {}
            self.calls = []

        def getmaxyx(self) -> tuple[int, int]:
            return (self.h, self.w)

        def addnstr(self, y: int, x: int, s: str, n: int, *args) -> None:
            attr = int(args[0]) if args else 0
            self.calls.append((int(y), int(x), str(s)[: max(0, int(n))], attr))
            cur = self.lines.get(int(y), '')
            need = max(len(cur), int(x) + max(0, int(n)))
            buf = list(cur.ljust(need))
            txt = str(s)[: max(0, int(n))]
            for i, ch in enumerate(txt):
                pos = int(x) + i
                if pos >= len(buf):
                    buf.extend(' ' * (pos - len(buf) + 1))
                buf[pos] = ch
            self.lines[int(y)] = ''.join(buf).rstrip()

        def move(self, y: int, x: int) -> None:
            self.cursor = (int(y), int(x))

        def refresh(self) -> None:
            pass

    ed = Editor()
    ed.new_buffer('*scratch*', 'hi\n')
    eb = ed.cur()
    ed.options.set('cursorline', 'false', local=eb.local_options)
    ed.options.set('colorcolumn', '5', local=eb.local_options)

    screen = ed.screen_model(8, 20)
    cues = dict(screen['viewport_cues'])
    row0 = cues['rows'][0]
    fake = _FakeStdScr()
    _render(fake, ed)

    assert row0['colorcolumn_blank'] == 1
    blank_calls = [attr for y, x, s, attr in fake.calls if y == row0['screen_y'] and x == row0['colorcolumn_x'] and s == ' ']
    assert blank_calls and any((attr & curses.A_REVERSE) and (attr & curses.A_DIM) for attr in blank_calls)




def test_render_uses_shared_docs_cues_model(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)
    monkeypatch.setenv('MICROMAX_DOCS', str(tmp_path))
    doc = tmp_path / '10-render-docs-cues.md'
    doc.write_text('# Title\n\nA [link](other.md)\n', encoding='utf-8')

    class _FakeStdScr:
        def __init__(self) -> None:
            self.h = 8
            self.w = 40
            self.lines: dict[int, str] = {}
            self.calls: list[tuple[int, int, str, int]] = []
            self.cursor = (0, 0)

        def erase(self) -> None:
            self.lines = {}
            self.calls = []

        def getmaxyx(self) -> tuple[int, int]:
            return (self.h, self.w)

        def addnstr(self, y: int, x: int, s: str, n: int, *args) -> None:
            attr = int(args[0]) if args else 0
            self.calls.append((int(y), int(x), str(s)[: max(0, int(n))], attr))
            cur = self.lines.get(int(y), '')
            need = max(len(cur), int(x) + max(0, int(n)))
            buf = list(cur.ljust(need))
            txt = str(s)[: max(0, int(n))]
            for i, ch in enumerate(txt):
                pos = int(x) + i
                if pos >= len(buf):
                    buf.extend(' ' * (pos - len(buf) + 1))
                buf[pos] = ch
            self.lines[int(y)] = ''.join(buf).rstrip()

        def move(self, y: int, x: int) -> None:
            self.cursor = (int(y), int(x))

        def refresh(self) -> None:
            pass

    ed = Editor()
    assert ed.open_help_doc('render-docs-cues') is True
    eb = ed.cur()
    ed.options.set('statusline', 'false', local=eb.local_options)
    ed.options.set('infobar', 'false', local=eb.local_options)

    screen = ed.screen_model(8, 40)
    docs_cues = dict(screen['docs_cues'])
    link_row = next(row for row in docs_cues['rows'] if row['link_count'] > 0)
    fake = _FakeStdScr()
    _render(fake, ed)

    underline_calls = [
        attr for y, _x, s, attr in fake.calls
        if y == link_row['screen_y'] and ('link' in s or s == 'link')
    ]
    assert underline_calls and any(attr & curses.A_UNDERLINE for attr in underline_calls)


def test_render_uses_shared_viewport_rows_model(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)

    class _FakeStdScr:
        def __init__(self) -> None:
            self.h = 8
            self.w = 20
            self.lines: dict[int, str] = {}
            self.cursor = (0, 0)

        def erase(self) -> None:
            self.lines = {}

        def getmaxyx(self) -> tuple[int, int]:
            return (self.h, self.w)

        def addnstr(self, y: int, x: int, s: str, n: int, *args) -> None:
            cur = self.lines.get(int(y), '')
            need = max(len(cur), int(x) + max(0, int(n)))
            buf = list(cur.ljust(need))
            txt = str(s)[: max(0, int(n))]
            for i, ch in enumerate(txt):
                pos = int(x) + i
                if pos >= len(buf):
                    buf.extend(' ' * (pos - len(buf) + 1))
                buf[pos] = ch
            self.lines[int(y)] = ''.join(buf).rstrip()

        def move(self, y: int, x: int) -> None:
            self.cursor = (int(y), int(x))

        def refresh(self) -> None:
            pass

    ed = Editor()
    ed.new_buffer('t.mx', '\n'.join(f'line {i}' for i in range(20)) + '\n', path='t.mx')
    eb = ed.cur()
    ed.options.set('ruler', 'true', local=eb.local_options)
    ed.options.set('scrollbar', 'true', local=eb.local_options)
    ed.options.set('cursorline', 'false', local=eb.local_options)

    screen = ed.screen_model(8, 20)
    rows = list(screen['viewport_rows']['rows'])
    fake = _FakeStdScr()
    _render(fake, ed)

    assert rows[0]['left_text'].strip() == '1'
    assert fake.lines[rows[0]['screen_y']].startswith(rows[0]['left_text'])
    assert rows[0]['text'] in fake.lines[rows[0]['screen_y']]
    thumb_row = next(row for row in rows if str(row.get('right_text', '') or ''))
    assert fake.lines[thumb_row['screen_y']][thumb_row['right_x']] == thumb_row['right_text']


def test_render_uses_shared_gutter_model(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)

    class _FakeStdScr:
        def __init__(self) -> None:
            self.h = 8
            self.w = 20
            self.lines: dict[int, str] = {}
            self.cursor = (0, 0)

        def erase(self) -> None:
            self.lines = {}

        def getmaxyx(self) -> tuple[int, int]:
            return (self.h, self.w)

        def addnstr(self, y: int, x: int, s: str, n: int, *args) -> None:
            cur = self.lines.get(int(y), '')
            need = max(len(cur), int(x) + max(0, int(n)))
            buf = list(cur.ljust(need))
            txt = str(s)[: max(0, int(n))]
            for i, ch in enumerate(txt):
                pos = int(x) + i
                if pos >= len(buf):
                    buf.extend(' ' * (pos - len(buf) + 1))
                buf[pos] = ch
            self.lines[int(y)] = ''.join(buf).rstrip()

        def move(self, y: int, x: int) -> None:
            self.cursor = (int(y), int(x))

        def refresh(self) -> None:
            pass

    ed = Editor()
    ed.new_buffer('t.mx', '\n'.join(f'line {i}' for i in range(20)) + '\n', path='t.mx')
    eb = ed.cur()
    ed.options.set('ruler', 'true', local=eb.local_options)
    ed.options.set('scrollbar', 'true', local=eb.local_options)
    ed.options.set('cursorline', 'false', local=eb.local_options)

    screen = ed.screen_model(8, 20)
    gutter = dict(screen['gutter'])
    fake = _FakeStdScr()
    _render(fake, ed)

    assert gutter['line_numbers_active'] == 1
    assert fake.lines[0].startswith(gutter['line_numbers'][0]['text'])
    thumb_y = gutter['scrollbar_rows'][0]['screen_y']
    thumb_x = gutter['scrollbar_rows'][0]['screen_x']
    assert fake.lines[thumb_y][thumb_x] == gutter['scrollbar_rows'][0]['text']


def test_render_uses_shared_screen_layout_model(monkeypatch) -> None:
    monkeypatch.setattr(curses, 'has_colors', lambda: False)

    class _FakeStdScr:
        def __init__(self) -> None:
            self.h = 8
            self.w = 40
            self.lines: dict[int, str] = {}
            self.cursor = (0, 0)

        def erase(self) -> None:
            self.lines = {}

        def getmaxyx(self) -> tuple[int, int]:
            return (self.h, self.w)

        def addnstr(self, y: int, x: int, s: str, n: int, *args) -> None:
            cur = self.lines.get(int(y), '')
            need = max(len(cur), int(x) + max(0, int(n)))
            buf = list(cur.ljust(need))
            txt = str(s)[: max(0, int(n))]
            for i, ch in enumerate(txt):
                pos = int(x) + i
                if pos >= len(buf):
                    buf.extend(' ' * (pos - len(buf) + 1))
                buf[pos] = ch
            self.lines[int(y)] = ''.join(buf).rstrip()

        def move(self, y: int, x: int) -> None:
            self.cursor = (int(y), int(x))

        def refresh(self) -> None:
            pass

    ed = Editor()
    ed.new_buffer('*scratch*', 'one\ntwo\nthree\nfour\n')
    eb = ed.cur()
    ed.options.set('cursorline', 'false', local=eb.local_options)
    ed.options.set('keymenu', 'true', local=eb.local_options)

    screen = ed.screen_model(8, 40)
    window = dict(screen['edit_window'])
    layout = dict(screen['layout'])
    fake = _FakeStdScr()
    _render(fake, ed)

    assert ed.viewport_model()['height'] == layout['viewport_height']
    assert fake.lines[layout['keymenu_y']].startswith('^Q Quit')
    assert fake.lines[layout['status_y']] == ed.statusline_text(40)
    assert fake.lines[0].startswith(window['rows'][0]['text'])
    assert fake.cursor == (window['cursor']['screen_y'], window['cursor']['screen_x'])



def test_docs_cues_model_exposes_row_local_definition_metadata(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv('MICROMAX_DOCS', str(tmp_path))
    doc = tmp_path / '10-docs-definition-metadata.md'
    doc.write_text(
        '# Title\n\n'
        '[visionref]:\n'
        '  00-vision.md#intro\n\n'
        'Paragraph with note[^tiny].\n\n'
        '[^tiny]: first line\n'
        '    second line\n',
        encoding='utf-8',
    )

    ed = Editor()
    assert ed.open_help_doc('docs-definition-metadata') is True
    eb = ed.cur()
    ed.options.set('statusline', 'false', local=eb.local_options)
    ed.options.set('infobar', 'false', local=eb.local_options)

    model = ed.docs_cues_model(12, 120)
    ref_row = next(row for row in model['rows'] if row['definition_role'] == 'reference')
    assert ref_row['definition_entries'] == [
        {
            'kind': 'reference-definition',
            'role': 'starter',
            'id': 'visionref',
            'start': 0,
            'end': 12,
            'text': '[visionref]:',
            'target': '00-vision.md#intro',
            'target_kind': 'file-fragment',
            'target_doc': '00-vision.md',
            'target_fragment': 'intro',
        }
    ]
    assert ref_row['reference_definition_entries'] == ref_row['definition_entries']
    assert ref_row['reference_definition_count'] == 1
    assert ref_row['reference_definition_cont_entries'] == []
    ref_cont_row = next(row for row in model['rows'] if row['definition_role'] == 'reference-cont')
    assert ref_cont_row['definition_entries'][0]['kind'] == 'reference-definition-cont'
    assert ref_cont_row['definition_entries'][0]['id'] == 'visionref'
    assert ref_cont_row['definition_entries'][0]['continuation_index'] == 1
    assert ref_cont_row['reference_definition_entries'] == []
    assert ref_cont_row['reference_definition_cont_entries'] == ref_cont_row['definition_entries']
    assert ref_cont_row['reference_definition_cont_count'] == 1
    foot_row = next(row for row in model['rows'] if row['definition_role'] == 'footnote')
    assert foot_row['definition_entries'] == [
        {
            'kind': 'footnote-definition',
            'role': 'starter',
            'id': 'tiny',
            'start': 0,
            'end': 8,
            'text': '[^tiny]:',
            'target': '#^tiny',
            'target_kind': 'footnote',
            'target_doc': '',
            'target_fragment': '^tiny',
        }
    ]
    assert foot_row['footnote_definition_entries'] == foot_row['definition_entries']
    assert foot_row['footnote_definition_count'] == 1
    assert foot_row['reference_definition_entries'] == []
    foot_cont_row = next(row for row in model['rows'] if row['definition_role'] == 'footnote-cont')
    assert foot_cont_row['definition_entries'][0]['kind'] == 'footnote-definition-cont'
    assert foot_cont_row['definition_entries'][0]['id'] == 'tiny'
    assert foot_cont_row['definition_entries'][0]['continuation_index'] == 1
    assert foot_cont_row['footnote_definition_entries'] == []
    assert foot_cont_row['footnote_definition_cont_entries'] == foot_cont_row['definition_entries']
    assert foot_cont_row['footnote_definition_cont_count'] == 1
    assert model['definition_rows'] == 4
    assert model['definition_entry_count'] == 4
    assert model['reference_definition_rows'] == 1
    assert model['reference_definition_cont_rows'] == 1
    assert model['footnote_definition_rows'] == 1
    assert model['footnote_definition_cont_rows'] == 1
    assert model['reference_definition_entry_count'] == 1
    assert model['reference_definition_cont_entry_count'] == 1
    assert model['footnote_definition_entry_count'] == 1
    assert model['footnote_definition_cont_entry_count'] == 1


def test_docs_cues_model_exposes_row_local_block_metadata(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv('MICROMAX_DOCS', str(tmp_path))
    doc = tmp_path / '10-docs-block-metadata.md'
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

    ed = Editor()
    assert ed.open_help_doc('docs-block-metadata') is True
    eb = ed.cur()
    ed.options.set('statusline', 'false', local=eb.local_options)
    ed.options.set('infobar', 'false', local=eb.local_options)

    model = ed.docs_cues_model(16, 120)
    opener_row = next(row for row in model['rows'] if row['line_role'] == 'fenced-fence' and row['text'].startswith('```python'))
    body_row = next(row for row in model['rows'] if row['line_role'] == 'fenced-body')
    closer_row = next(row for row in model['rows'] if row['line_role'] == 'fenced-fence' and row['text'] == '```')
    html_row = next(row for row in model['rows'] if row['line_role'] == 'html-block' and row['text'] == '<div>')
    indented_row = next(row for row in model['rows'] if row['line_role'] == 'indented-code' and row['text'] == '    indented one')

    assert opener_row['block_entries'] == [
        {
            'kind': 'fenced-code',
            'role': 'opener',
            'block_index': 1,
            'start': 0,
            'end': 3,
            'text': '```python',
            'marker': '`',
            'marker_kind': 'backtick',
            'marker_count': 3,
            'indent': 0,
            'info_string': 'python',
            'language': 'python',
            'has_language': 1,
        },
    ]
    assert opener_row['fenced_code_entries'] == opener_row['block_entries']
    assert opener_row['fenced_code_opener_entries'] == opener_row['block_entries']
    assert opener_row['fenced_code_body_entries'] == []
    assert opener_row['fenced_code_closer_entries'] == []
    assert opener_row['html_block_entries'] == []
    assert opener_row['indented_code_entries'] == []
    assert opener_row['fenced_code_count'] == 1
    assert opener_row['fenced_code_opener_count'] == 1
    assert body_row['block_entries'][0]['kind'] == 'fenced-code'
    assert body_row['block_entries'][0]['role'] == 'body'
    assert body_row['block_entries'][0]['block_index'] == 1
    assert body_row['fenced_code_entries'][0]['role'] == 'body'
    assert body_row['fenced_code_body_entries'][0]['role'] == 'body'
    assert body_row['fenced_code_opener_entries'] == []
    assert closer_row['block_entries'][0]['role'] == 'closer'
    assert closer_row['block_entries'][0]['marker_count'] == 3
    assert closer_row['fenced_code_closer_entries'][0]['role'] == 'closer'
    assert html_row['block_entries'][0] == {
        'kind': 'html-block',
        'role': 'line',
        'block_index': 1,
        'start': 0,
        'end': 5,
        'text': '<div>',
    }
    assert html_row['html_block_entries'][0]['kind'] == 'html-block'
    assert html_row['fenced_code_entries'] == []
    assert indented_row['block_entries'][0]['kind'] == 'indented-code'
    assert indented_row['block_entries'][0]['role'] == 'line'
    assert indented_row['block_entries'][0]['block_index'] == 1
    assert indented_row['block_entries'][0]['indent_text'] == '    '
    assert indented_row['block_entries'][0]['indent_width'] == 4
    assert indented_row['indented_code_entries'][0]['kind'] == 'indented-code'
    assert model['block_rows'] == 8
    assert model['block_entry_count'] == 8
    assert model['fenced_code_rows'] == 3
    assert model['fenced_code_opener_rows'] == 1
    assert model['fenced_code_body_rows'] == 1
    assert model['fenced_code_closer_rows'] == 1
    assert model['html_block_rows'] == 3
    assert model['indented_code_rows'] == 2
    assert model['fenced_code_entry_count'] == 3
    assert model['fenced_code_opener_entry_count'] == 1
    assert model['fenced_code_body_entry_count'] == 1
    assert model['fenced_code_closer_entry_count'] == 1
    assert model['html_block_entry_count'] == 3
    assert model['indented_code_entry_count'] == 2


def test_docs_cues_model_fenced_code_marker_and_language_metadata(tmp_path: Path, monkeypatch) -> None:
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
    # Rev791+ help/docs containment only opens explicit markdown paths inside
    # the configured docs root. Keep this docs-cue rendering fixture inside that
    # root instead of relying on arbitrary absolute help paths.
    monkeypatch.setenv('MICROMAX_DOCS', str(tmp_path))

    ed = Editor()
    assert ed.open_help_doc(str(doc)) is True
    eb = ed.cur()
    ed.options.set('statusline', 'false', local=eb.local_options)
    ed.options.set('infobar', 'false', local=eb.local_options)

    model = ed.docs_cues_model(12, 120)
    opener_backtick = next(
        row for row in model['rows']
        if row['fenced_code_opener_count'] == 1 and row['backtick_fenced_code_count'] == 1
    )
    body_backtick = next(
        row for row in model['rows']
        if row['text'] == 'print("hi")'
    )
    opener_tilde = next(
        row for row in model['rows']
        if row['fenced_code_opener_count'] == 1 and row['tilde_fenced_code_count'] == 1
    )
    body_tilde = next(row for row in model['rows'] if row['text'] == 'raw')

    assert opener_backtick['backtick_fenced_code_entries'][0]['marker_kind'] == 'backtick'
    assert opener_backtick['language_fenced_code_entries'][0]['language'] == 'python'
    assert opener_backtick['bare_fenced_code_entries'] == []
    assert body_backtick['backtick_fenced_code_entries'][0]['role'] == 'body'
    assert body_backtick['language_fenced_code_entries'][0]['language'] == 'python'
    assert body_backtick['language_fenced_code_count'] == 1
    assert opener_tilde['tilde_fenced_code_entries'][0]['marker_kind'] == 'tilde'
    assert opener_tilde['bare_fenced_code_entries'][0]['has_language'] == 0
    assert opener_tilde['language_fenced_code_entries'] == []
    assert body_tilde['tilde_fenced_code_entries'][0]['role'] == 'body'
    assert body_tilde['bare_fenced_code_entries'][0]['marker_kind'] == 'tilde'
    assert model['backtick_fenced_code_rows'] == 3
    assert model['tilde_fenced_code_rows'] == 3
    assert model['language_fenced_code_rows'] == 3
    assert model['bare_fenced_code_rows'] == 3
    assert model['backtick_fenced_code_count'] == 3
    assert model['tilde_fenced_code_count'] == 3
    assert model['language_fenced_code_count'] == 3
    assert model['bare_fenced_code_count'] == 3
