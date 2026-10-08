from micromax_editor.editor import Editor


def test_status_model_includes_encoding_fileformat_and_percentage():
    ed = Editor()
    ed.new_buffer('test.mx', "\n".join(['a', 'b', 'c', 'd']), path='test.mx')
    st = ed.status_model()
    assert st['encoding'] == 'utf-8'
    assert st['fileformat'] == 'unix'
    assert st['filetype'] in ('micromax', 'mx', 'unknown')  # depends on filetypes table

    # top of file -> 0%
    assert st['percentage'] == 0

    # move to last line -> 100%
    for _ in range(3):
        ed.run_action('CursorDown')
    st = ed.status_model()
    assert st['display_line'] == 4
    assert st['percentage'] == 100


def test_statusline_text_contains_key_fields_and_respects_width():
    ed = Editor()
    ed.new_buffer('test.mx', "hello", path='test.mx')
    s = ed.statusline_text(120)
    assert 'ft:' in s
    assert 'enc:utf-8' in s
    assert 'cur:1/1' in s
    assert s.endswith('normal') or ' normal' in s

    s2 = ed.statusline_text(20)
    assert len(s2) == 20
