from micromax_editor.editor import Editor


def test_statusformat_directives_and_escaping() -> None:
    ed = Editor()
    ed.new_buffer('t.mx', 'x', path='t.mx')

    # Make buffer dirty.
    ed.input['text'] = 'y'
    ed.run_action('InsertText')

    ed.options.set('statusformatl', '$(filename)$(modified)$$', local=ed.cur().local_options)
    s = ed.statusline_text(80)
    assert 't.mx*' in s
    assert '$' in s


def test_statusformat_opt_and_bind_directives() -> None:
    ed = Editor()
    ed.new_buffer('t.mx', 'hello', path='t.mx')

    ed.keymap.bind('Ctrl-k', 'MyAction')
    ed.options.set('tabsize', '8', local=ed.cur().local_options)

    ed.options.set('statusformatr', 'tab=$(opt:tabsize) key=$(bind:MyAction)', local=ed.cur().local_options)
    s = ed.statusline_text(120)
    assert 'tab=8' in s
    assert 'key=Ctrl-k' in s


def test_statusformat_sel_and_keymode_are_conditional() -> None:
    ed = Editor()
    ed.new_buffer('t.mx', 'abc', path='t.mx')

    ed.options.set('statusformatr', 'X$(sel)Y', local=ed.cur().local_options)
    assert 'XY' in ed.statusline_text(80)

    # Create a selection.
    ed.run_action('SelectRight')
    assert 'X sel:1Y' in ed.statusline_text(80)


def test_statusformat_if_directive_and_escaping() -> None:
    ed = Editor()
    ed.new_buffer('t.mx', 'x', path='t.mx')

    ed.options.set('statusformatl', 'X$(if:modified|YES|NO)Y', local=ed.cur().local_options)
    s0 = ed.statusline_text(80)
    assert 'XNOY' in s0

    # Make buffer dirty.
    ed.input['text'] = 'y'
    ed.run_action('InsertText')
    s1 = ed.statusline_text(80)
    assert 'XYESY' in s1

    # Escaped separators in THEN/ELSE.
    ed.options.set('statusformatl', '$(if:modified|a\\|b|c)', local=ed.cur().local_options)
    s2 = ed.statusline_text(80)
    assert 'a|b' in s2
