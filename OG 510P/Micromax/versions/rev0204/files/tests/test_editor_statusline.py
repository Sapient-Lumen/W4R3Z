from micromax_editor.buffer import Cursor
from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _hostcall(ed: Editor, name: str, *args: object) -> list[object]:
    vm = ed.vm
    for a in args:
        vm.stack.append(a)
    vm.stack.append(name)
    vm.eval('hostcall')
    return list(vm.stack)


def test_status_model_hostcall_reports_portable_editor_state() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('notes.txt', 'alpha\nbeta', path='/tmp/notes.txt')

    eb = ed.cur()
    eb.buf.dirty = True
    eb.cursors[0] = Cursor(1, 2)
    eb.sel_anchors[0] = Cursor(1, 0)
    ed.message('saved ok')
    ed.enter_prompt('command', prefill='open a')
    ed.macro_recording = True
    ed._macro_target = 'demo'

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.status')
    st = ed.vm.pop_map()

    assert st['mode'] == 'command'
    assert st['buffer_name'] == 'notes.txt'
    assert st['file_name'] == 'notes.txt'
    assert st['buffer_index'] == 1
    assert st['buffer_count'] == 1
    assert st['buffer_summary'] == '1/1'
    assert st['path'] == '/tmp/notes.txt'
    assert st['dirty'] == 1
    assert st['readonly'] == 0
    assert st['line'] == 1
    assert st['col'] == 2
    assert st['display_line'] == 2
    assert st['display_col'] == 3
    assert st['position'] == '2:3'
    assert st['line_count'] == 2
    assert st['cursor_count'] == 1
    assert st['primary_cursor_index'] == 0
    assert st['selection_count'] == 1
    assert st['primary_selection_chars'] == 2
    assert st['prompt_kind'] == 'command'
    assert st['prompt_text'] == 'open a'
    assert st['last_message'] == 'saved ok'
    assert st['macro_recording'] == 1
    assert st['macro_name'] == 'demo'



def test_showstatus_and_status_summary_hostcall_are_deterministic() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', 'abc')

    eb = ed.cur()
    eb.buf.dirty = True
    eb.cursors.append(Cursor(0, 1))
    eb.sel_anchors.append(None)
    eb.cursor_ids.append(ed._alloc_cursor_id())
    ed._normalize_cursor_lists(eb)
    ed.message('hello world')

    assert ed.exec_command_line('showstatus')
    msg = ed.messages[-1]
    assert "mode=normal" in msg
    assert "buffer='*scratch*'" in msg
    assert 'dirty=1' in msg
    assert 'pos=1:1' in msg
    assert 'cursors=1/2' in msg
    assert 'sels=0' in msg

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.status-summary')
    assert ed.vm.pop_str() == msg


def test_status_model_exposes_search_position_summary() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', 'alpha beta alpha\nsecond alpha\n')

    assert ed.find('ALPHA') is True

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.status')
    st = ed.vm.pop_map()

    assert st['search_query'] == 'ALPHA'
    assert st['search_literal'] == 1
    assert st['search_case_sensitive'] == 0
    assert st['search_match_index'] == 1
    assert st['search_match_count'] == 3
    assert st['search_summary'] == '1/3'

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.status-summary')
    summary = ed.vm.pop_str()
    assert "search_pos='1/3'" in summary


def test_statusline_templates_can_render_search_summary() -> None:
    ed = Editor()
    ed.new_buffer('*scratch*', 'alpha beta alpha\nsecond alpha\n')
    assert ed.find('alpha') is True

    ed.options.set('statusformatr', '$(search_summary)', local=ed.cur().local_options)
    assert ed.statusline_text(20).endswith('1/3')


def test_statusline_searchpos_directive_and_default_formatter_show_search_count() -> None:
    ed = Editor()
    ed.new_buffer('*scratch*', 'alpha beta alpha\nsecond alpha\n')
    assert ed.find('alpha') is True

    s = ed.statusline_text(120)
    assert '[1/3]' in s

    ed.options.set('statusformatr', '$(searchpos) $(position)', local=ed.cur().local_options)
    assert ed.statusline_text(40).endswith('[1/3] 1:1')




def test_status_model_exposes_buffer_position_summary_for_multiple_buffers() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('zeta.txt', 'z')
    ed.new_buffer('alpha.txt', 'a')

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.status')
    st = ed.vm.pop_map()

    # buffer_names() uses stable sorted order.
    assert st['buffer_index'] == 1
    assert st['buffer_count'] == 2
    assert st['buffer_summary'] == '1/2'

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.status-summary')
    summary = ed.vm.pop_str()
    assert "buf_pos='1/2'" in summary


def test_statusline_bufpos_directive_and_default_formatter_show_buffer_position() -> None:
    ed = Editor()
    ed.new_buffer('zeta.txt', 'z')
    ed.new_buffer('alpha.txt', 'a')

    s = ed.statusline_text(120)
    assert '[1/2]' in s

    ed.options.set('statusformatr', '$(bufpos) $(position)', local=ed.cur().local_options)
    assert ed.statusline_text(40).endswith('[1/2] 1:1')


def test_statusline_bufpos_is_hidden_for_single_buffer() -> None:
    ed = Editor()
    ed.new_buffer('solo.txt', 'x')
    ed.options.set('statusformatr', '$(bufpos)$(position)', local=ed.cur().local_options)
    assert ed.statusline_text(40).endswith('1:1')
    assert '[' not in ed.statusline_text(40)

def test_command_palette_status_model_exposes_current_preview() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', 'alpha')

    ed.enter_command_palette('status')

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.status')
    st = ed.vm.pop_map()

    assert st['mode'] == 'palette'
    assert st['prompt_kind'] == 'palette'
    assert st['prompt_text'] == 'status'
    assert st['prompt_current_insert'] == 'showstatus'
    assert st['prompt_current_kind'] == 'command'
    assert st['prompt_current_section'] == 'Commands'
    assert st['prompt_current_preview'].startswith('Commands: showstatus')
    assert 'portable statusline summary' in st['prompt_current_preview']

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.status-summary')
    summary = ed.vm.pop_str()
    assert "prompt='palette'" in summary
    assert 'prompt_item=' in summary


def test_command_palette_status_model_uses_recent_section_for_recent_item() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', 'alpha')

    assert ed.exec_command_line('commandpick status')
    assert ed.submit_prompt() is True
    assert ed.prompt is not None
    assert ed.prompt.kind == 'command'
    ed.cancel_prompt()

    ed.enter_command_palette('')

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.status')
    st = ed.vm.pop_map()

    assert st['mode'] == 'palette'
    assert st['prompt_current_insert'] == 'showstatus'
    assert st['prompt_current_section'] == 'Recent'
    assert 'Recent: showstatus' in st['prompt_current_preview']


def test_topic_prompt_status_model_exposes_current_preview() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', 'alpha')

    ed.enter_topic_prompt('visible micromax')

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.status')
    st = ed.vm.pop_map()

    assert st['mode'] == 'topic'
    assert st['prompt_kind'] == 'topic'
    assert st['prompt_text'] == 'visible micromax'
    assert st['prompt_current_insert'] == 'showword'
    assert st['prompt_current_kind'] == 'command'
    assert st['prompt_current_section'] == 'Commands'
    assert st['prompt_current_preview'].startswith('Commands: showword')
    assert 'show visible micromax word' in st['prompt_current_preview']

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.status-summary')
    summary = ed.vm.pop_str()
    assert "prompt='topic'" in summary
    assert 'prompt_item=' in summary


def test_binding_prompt_status_model_exposes_current_preview() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', 'alpha')

    ed.vm.eval('"Ctrl-z" "command:help" "ed.bind" hostcall', filename='<global-bind>')
    ed.vm.eval('"nav" "Ctrl-x" "command:quit" "ed.bind-mode" hostcall', filename='<nav-bind>')
    ed.vm.eval('"prompt" "Ctrl-n" "command:showstatus" "ed.bind-mode" hostcall', filename='<prompt-bind>')
    _hostcall(ed, 'ed.keymode-push', 'nav')
    ed.enter_binding_prompt('quit')

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.status')
    st = ed.vm.pop_map()

    assert st['mode'] == 'binding'
    assert st['prompt_kind'] == 'binding'
    assert st['prompt_text'] == 'quit'
    assert st['prompt_current_insert'] == 'Ctrl-x'
    assert st['prompt_current_kind'] == 'binding'
    assert st['prompt_current_section'] == 'nav'
    assert '@nav command:quit' in st['prompt_current_menu']
    assert st['prompt_current_preview'].startswith('nav: Ctrl-x')
    assert 'request editor quit' in st['prompt_current_preview']

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.status-summary')
    summary = ed.vm.pop_str()
    assert "prompt='binding'" in summary
    assert 'prompt_item=' in summary



def test_bufferpick_status_summary_exposes_grouped_preview(tmp_path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', 'alpha')
    assert ed.open_help_doc('help-browser') is True

    p = tmp_path / 'notes.txt'
    p.write_text('hi\n', encoding='utf-8')
    ed.open_file(str(p))

    assert ed.exec_command_line('bufferpick') is True

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.status')
    st = ed.vm.pop_map()
    assert st['prompt_kind'] == 'buffer'
    assert st['prompt_current_section'] == 'Help'
    assert st['prompt_current_preview'].startswith('Help: help:help-browser')

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.status-summary')
    summary = ed.vm.pop_str()
    assert "prompt='buffer'" in summary
    assert 'prompt_item=' in summary


def test_docpick_status_summary_exposes_grouped_preview() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', 'alpha')

    assert ed.exec_command_line('helppick vision') is True

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.status')
    st = ed.vm.pop_map()
    assert st['prompt_kind'] == 'doc'
    assert st['prompt_current_section'] == '00–09 Project'
    assert st['prompt_current_preview'].startswith('00–09 Project: Vision')

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.status-summary')
    summary = ed.vm.pop_str()
    assert "prompt='doc'" in summary
    assert 'prompt_item=' in summary


def test_recentpick_status_summary_exposes_grouped_preview(tmp_path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    proj = tmp_path / 'proj'
    (proj / '.git').mkdir(parents=True)
    p = proj / 'src' / 'main.py'
    q = proj / 'tests' / 'test_main.py'
    p.parent.mkdir(parents=True)
    q.parent.mkdir(parents=True)
    p.write_text('print(1)\n', encoding='utf-8')
    q.write_text('assert True\n', encoding='utf-8')
    ed.open_file(str(p))
    ed.open_file(str(q))

    assert ed.exec_command_line('recentpick') is True

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.status')
    st = ed.vm.pop_map()
    assert st['prompt_kind'] == 'recent'
    assert st['prompt_current_section'] == str(proj)
    assert st['prompt_current_menu'] == 'proj'
    assert st['prompt_current_info'] == 'tests/test_main.py'
    assert st['prompt_current_preview'].startswith(f'{proj}: {q}')
    assert st['prompt_index'] == 1
    assert st['prompt_count'] == 2
    assert st['prompt_section_index'] == 1
    assert st['prompt_section_count'] == 2
    assert st['prompt_position_summary'] == f'1/2 • {proj} 1/2'

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.status-summary')
    summary = ed.vm.pop_str()
    assert "prompt='recent'" in summary
    assert 'prompt_pos=' in summary
    assert 'prompt_item=' in summary


def test_helplinkpick_status_uses_visible_section_labels() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.open_help_doc('help-browser') is True

    assert ed.exec_command_line('helplinkpick') is True
    assert ed.prompt is not None
    idx = next(i for i, row in enumerate(ed.prompt.suggestion_rows) if str(row[0]) == 'Softwrap')
    ed.prompt.suggest_index = idx

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.status')
    st = ed.vm.pop_map()
    assert st['prompt_kind'] == 'helplink'
    assert st['prompt_current_section'] == 'Files'
    assert st['prompt_current_preview'].startswith('Files: Softwrap')


def test_helpnavpick_status_uses_visible_heading_section_label() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.open_help_doc('help-browser') is True

    assert ed.exec_command_line('helpnavpick') is True
    assert ed.prompt is not None
    idx = next(i for i, row in enumerate(ed.prompt.suggestion_rows) if str(row[0]) == 'Links' and str(row[1]) == 'heading')
    ed.prompt.suggest_index = idx

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.status')
    st = ed.vm.pop_map()
    assert st['prompt_kind'] == 'helpnav'
    assert st['prompt_current_section'] == 'Headings'
    assert st['prompt_current_preview'].startswith('Headings: Links')


def test_helpoutlinepick_status_uses_visible_heading_section_label() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.open_help_doc('help-browser') is True

    assert ed.exec_command_line('helpoutlinepick Links') is True
    assert ed.prompt is not None

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.status')
    st = ed.vm.pop_map()
    assert st['prompt_kind'] == 'helpoutline'
    assert st['prompt_current_section'] == 'Headings'
    assert st['prompt_current_preview'].startswith('Headings: Links')



def test_status_model_reports_effective_fileformat_option() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('notes.txt', 'alpha\n', path='/tmp/notes.txt')

    assert ed.exec_command_line('setlocal fileformat dos')

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.status')
    st = ed.vm.pop_map()

    assert st['fileformat'] == 'dos'


def test_statusline_opt_fileformat_uses_effective_buffer_option() -> None:
    ed = Editor()
    ed.new_buffer('notes.txt', 'alpha\n', path='/tmp/notes.txt')
    assert ed.exec_command_line('setlocal fileformat dos')
    ed.options.set('statusformatr', '$(opt:fileformat) $(position)', local=ed.cur().local_options)

    assert ed.statusline_text(40).endswith('dos 1:1')


def test_statusline_opt_encoding_uses_effective_buffer_option() -> None:
    ed = Editor()
    ed.new_buffer('notes.txt', 'caf\u00e9\n', path='/tmp/notes.txt')
    assert ed.exec_command_line('setlocal encoding latin-1')
    ed.options.set('statusformatr', '$(opt:encoding) $(position)', local=ed.cur().local_options)

    assert ed.statusline_text(40).endswith('latin-1 1:1')


def test_status_model_exposes_display_name_and_raw_file_name() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('notes.txt', 'alpha', path='/tmp/demo/notes.txt')

    st = ed.status_model()
    assert st['file_name'] == 'notes.txt'
    assert st['display_name'] == '/tmp/demo/notes.txt'

    ed.options.set('basename', 'true', local=ed.cur().local_options)
    st2 = ed.status_model()
    assert st2['file_name'] == 'notes.txt'
    assert st2['display_name'] == 'notes.txt'


def test_statusline_filename_honors_basename_option() -> None:
    ed = Editor()
    ed.new_buffer('notes.txt', 'alpha', path='/tmp/demo/notes.txt')
    ed.options.set('statusformatl', '$(filename)', local=ed.cur().local_options)
    ed.options.set('statusformatr', '', local=ed.cur().local_options)

    assert ed.statusline_text(80).startswith('/tmp/demo/notes.txt')

    ed.options.set('basename', 'true', local=ed.cur().local_options)
    assert ed.statusline_text(80).startswith('notes.txt')


def test_showstatus_prefers_effective_display_name() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('notes.txt', 'alpha', path='/tmp/demo/notes.txt')

    assert ed.exec_command_line('showstatus')
    assert "buffer='/tmp/demo/notes.txt'" in ed.messages[-1]

    ed.options.set('basename', 'true', local=ed.cur().local_options)
    assert ed.exec_command_line('showstatus')
    assert "buffer='notes.txt'" in ed.messages[-1]
