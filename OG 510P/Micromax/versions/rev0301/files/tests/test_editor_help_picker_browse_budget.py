from __future__ import annotations

from micromax_editor.editor import Editor


def _section_starts(ed: Editor) -> list[tuple[int, str]]:
    assert ed.prompt is not None
    starts: list[tuple[int, str]] = []
    last = None
    for i, row in enumerate(ed.prompt.suggestion_rows):
        label = ed.prompt_row_section_label([str(x) for x in list(row[:4])], prompt_kind=ed.prompt.kind)
        if label != last:
            starts.append((i, label))
            last = label
    return starts


def test_helplink_prompt_rows_empty_query_keep_file_and_external_sections_visible() -> None:
    ed = Editor()
    assert ed.open_help_doc('help-picker-sections') is True

    rows = ed._helplink_prompt_rows('', limit=5)
    starts: list[str] = []
    last = None
    for row in rows:
        label = ed.prompt_row_section_label([str(x) for x in list(row[:4])], prompt_kind='helplink')
        if label != last:
            starts.append(label)
            last = label

    assert starts[:3] == ['Docs', 'Files', 'External']
    names = [str(row[0]) for row in rows]
    assert 'Vision 1' in names
    assert 'Softwrap file' in names
    assert 'micro editor' in names


def test_helpnav_prompt_rows_empty_query_keep_headings_and_link_sections_visible() -> None:
    ed = Editor()
    assert ed.open_help_doc('help-picker-sections') is True

    rows = ed._helpnav_prompt_rows('', limit=5)
    starts: list[str] = []
    last = None
    for row in rows:
        label = ed.prompt_row_section_label([str(x) for x in list(row[:4])], prompt_kind='helpnav')
        if label != last:
            starts.append(label)
            last = label

    assert starts[:5] == ['Top', 'Help picker section browse budget', 'Docs', 'Files', 'External']
    names = [str(row[0]) for row in rows]
    assert 'Help picker section browse budget' in names
    assert 'Softwrap file' in names
    assert 'micro editor' in names




def test_helpoutline_prompt_rows_empty_query_keep_multiple_heading_sections_visible() -> None:
    ed = Editor()
    assert ed.open_help_doc('helpoutline-section-groups') is True

    rows = ed._helpoutline_prompt_rows('', limit=4)
    starts: list[str] = []
    last = None
    for row in rows:
        label = ed.prompt_row_section_label([str(x) for x in list(row[:4])], prompt_kind='helpoutline')
        if label != last:
            starts.append(label)
            last = label

    assert starts[:4] == [
        'Top',
        'Help outline section groups',
        'Help outline section groups › Guide',
        'Help outline section groups › Guide › Links',
    ]
    assert [str(row[0]) for row in rows] == [
        'Help outline section groups',
        'Guide',
        'Links',
        'Deep dive',
    ]

def test_helplinkpick_alt_down_jumps_between_budgeted_sections() -> None:
    ed = Editor()
    assert ed.open_help_doc('help-picker-sections') is True
    assert ed.exec_command_line('helplinkpick') is True
    assert ed.prompt is not None
    assert ed.prompt.kind == 'helplink'
    assert ed._refresh_helplink_prompt_suggestions(limit=5) is True

    starts = _section_starts(ed)
    assert [label for _i, label in starts][:3] == ['Docs', 'Files', 'External']

    ed.prompt.suggest_index = int(starts[0][0])
    assert ed.dispatch_key('Alt-DownArrow') is True
    assert ed.prompt is not None
    assert int(ed.prompt.suggest_index) == int(starts[1][0])

    assert ed.dispatch_key('Alt-DownArrow') is True
    assert ed.prompt is not None
    assert int(ed.prompt.suggest_index) == int(starts[2][0])





def test_helpoutlinepick_alt_down_jumps_between_budgeted_sections() -> None:
    ed = Editor()
    assert ed.open_help_doc('helpoutline-section-groups') is True
    assert ed.exec_command_line('helpoutlinepick') is True
    assert ed.prompt is not None
    assert ed.prompt.kind == 'helpoutline'
    assert ed._refresh_helpoutline_prompt_suggestions(limit=4) is True

    starts = _section_starts(ed)
    assert [label for _i, label in starts][:4] == [
        'Top',
        'Help outline section groups',
        'Help outline section groups › Guide',
        'Help outline section groups › Guide › Links',
    ]

    ed.prompt.suggest_index = int(starts[0][0])
    assert ed.dispatch_key('Alt-DownArrow') is True
    assert ed.prompt is not None
    assert int(ed.prompt.suggest_index) == int(starts[1][0])

    assert ed.dispatch_key('Alt-DownArrow') is True
    assert ed.prompt is not None
    assert int(ed.prompt.suggest_index) == int(starts[2][0])

    assert ed.dispatch_key('Alt-DownArrow') is True
    assert ed.prompt is not None
    assert int(ed.prompt.suggest_index) == int(starts[3][0])

def test_helpnavpick_alt_down_jumps_between_budgeted_sections() -> None:
    ed = Editor()
    assert ed.open_help_doc('help-picker-sections') is True
    assert ed.exec_command_line('helpnavpick') is True
    assert ed.prompt is not None
    assert ed.prompt.kind == 'helpnav'
    assert ed._refresh_helpnav_prompt_suggestions(limit=5) is True

    starts = _section_starts(ed)
    assert [label for _i, label in starts][:5] == [
        'Top',
        'Help picker section browse budget',
        'Docs',
        'Files',
        'External',
    ]

    ed.prompt.suggest_index = int(starts[0][0])
    assert ed.dispatch_key('Alt-DownArrow') is True
    assert ed.prompt is not None
    assert int(ed.prompt.suggest_index) == int(starts[1][0])

    assert ed.dispatch_key('Alt-DownArrow') is True
    assert ed.prompt is not None
    assert int(ed.prompt.suggest_index) == int(starts[2][0])

    assert ed.dispatch_key('Alt-DownArrow') is True
    assert ed.prompt is not None
    assert int(ed.prompt.suggest_index) == int(starts[3][0])
