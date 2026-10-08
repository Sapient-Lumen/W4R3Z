from __future__ import annotations

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _hostcall(ed: Editor, name: str, *args: object) -> object:
    vm = ed.vm
    vm.stack.clear()
    for a in args:
        vm.stack.append(a)
    vm.stack.append(name)
    vm.eval('hostcall')
    assert vm.stack
    return vm.stack.pop()


def test_ed_statusfmt_and_statusline_text_hostcalls() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('t.mx', 'x', path='t.mx')

    out = _hostcall(ed, 'ed.statusfmt', '$(filename)')
    assert isinstance(out, str)
    assert 't.mx' in out

    s = _hostcall(ed, 'ed.statusline-text', 40)
    assert isinstance(s, str)
    assert len(s) <= 40

    model = _hostcall(ed, 'ed.statusline-model', 40)
    assert isinstance(model, dict)
    assert model['active'] == 1
    assert model['text'] == s
    assert model['width'] == 40


def test_ed_with_buffer_hostcall_restores_active_buffer() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'aaa\n')
    ed.new_buffer('b', 'bbb\n')
    assert ed.active == 'b'

    # Build a quotation that emits the active buffer name.
    ed.vm.eval('[ "ed.active-buffer" hostcall "ed.msg" hostcall ]', filename='<q>')
    q = ed.vm.stack.pop()

    ok = _hostcall(ed, 'ed.with-buffer', 'a', q)
    assert ok == 1
    assert ed.active == 'b'  # restored
    assert ed.messages and ed.messages[-1] == 'a'




def test_ed_interaction_model_hostcall_exposes_shared_prompt_row() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('t.mx', 'alpha\nbeta\n', path='t.mx')

    ed.enter_command_palette('status')

    model = _hostcall(ed, 'ed.interaction-model', 18)
    assert isinstance(model, dict)
    assert model['active'] == 1
    assert model['kind'] == 'palette'
    assert model['prefix'] == ':'
    assert model['raw_line'].startswith(':status')
    assert model['text'] == ed.interaction_model(18)['text']
    assert model['truncated'] == 1

def test_ed_keymenu_and_infobar_model_hostcalls() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('t.mx', 'alpha\nbeta\n', path='t.mx')
    eb = ed.cur()
    ed.options.set('keymenu', 'true', local=eb.local_options)
    ed.options.set('constantshow', 'true', local=eb.local_options)
    ed.message('saved ok')

    keymenu = _hostcall(ed, 'ed.keymenu-model', 80)
    assert isinstance(keymenu, dict)
    assert keymenu['active'] == 1
    assert keymenu['context'] == 'normal'
    assert keymenu['entries'][0]['key'] == '^Q'
    assert 'Quit' in keymenu['entries'][0]['label']

    infobar = _hostcall(ed, 'ed.infobar-model', 80)
    assert isinstance(infobar, dict)
    assert infobar['active'] == 1
    assert infobar['message_raw'] == 'saved ok'
    assert infobar['summary_raw'].startswith('Ln 1/3, Col 1')
    assert infobar['text'] == ed.infobar_text(80)


def test_ed_prompt_panel_hostcall_exposes_visible_picker_rows() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('t.mx', 'alpha\nbeta\n', path='t.mx')
    ed.enter_command_palette('status')

    model = _hostcall(ed, 'ed.prompt-panel', 12, 30)
    assert isinstance(model, dict)
    assert model['active'] == 1
    assert model['kind'] == 'palette'
    assert model['entries'][0]['type'] == 'header'
    assert model['entries'][1]['type'] == 'row'
    assert model['entries'][1]['text'].startswith('> ')


def test_ed_gutter_model_hostcall_exposes_visible_line_numbers_and_scrollbar() -> None:
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
    assert model['line_numbers'][0]['text'].strip() == '1'
    assert model['scrollbar_rows'][0]['text'] == ed.scrollbar_thumb_char()


def test_ed_edit_window_hostcall_exposes_shared_visible_rows() -> None:
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
    assert model['viewport_width'] == 4
    assert model['row_count'] >= 2
    assert model['rows'][0]['text'] == 'abcd'
    assert model['rows'][1]['continuation'] == 1
    assert model['rows'][1]['text'] == 'ef'
    assert model['cursor']['view_y'] == 1
    assert model['cursor']['view_x'] == 1
    assert model['cursor']['visible'] == 1




def test_ed_screen_rows_hostcall_exposes_flat_visible_plain_text_rows() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('t.mx', 'alpha\nbeta\ngamma\n', path='t.mx')
    eb = ed.cur()
    ed.options.set('keymenu', 'true', local=eb.local_options)
    ed.options.set('ruler', 'true', local=eb.local_options)
    ed.options.set('scrollbar', 'true', local=eb.local_options)
    ed.enter_command_palette('status')

    model = _hostcall(ed, 'ed.screen-rows', 10, 30)
    assert isinstance(model, dict)
    assert model['row_count'] == 10
    first_viewport = next(row for row in model['rows'] if row['kind'] == 'viewport')
    assert first_viewport['text'].startswith('1 alpha')
    assert first_viewport['line'] == 0
    prompt_row = next(row for row in model['rows'] if row['kind'] == 'interaction')
    assert prompt_row['text'].startswith(':status')
    assert prompt_row['cursor_here'] == 1

def test_ed_screen_model_hostcall_exposes_layout_window_and_bottom_rows() -> None:
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
    assert model['layout']['cols'] == 30
    assert model['edit_window']['viewport_width'] == model['layout']['viewport_width']
    assert model['gutter']['line_numbers_active'] == 1
    assert model['prompt_panel']['active'] == 1
    assert model['bottom_rows'][0]['kind'] == 'keymenu'
    assert model['cursor']['mode'] == 'prompt'

