from pathlib import Path

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


def test_mx_command_add_exec_help_and_remove() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    # Define a command implementation in micromax.
    ed.vm.eval(
        ': hi-cmd ( args -- ok ) drop "hi!" "ed.msg" hostcall 1 ;',
        filename='<test>',
    )

    # Register it as a command-bar command with documentation.
    ed.vm.eval("' hi-cmd \"hi\" \"say hi\" \"ed.cmd-add\" hostcall", filename='<test>')

    assert ed.exec_command_line('hi')
    assert ed.messages and ed.messages[-1] == 'hi!'

    # `help` should show doc + a best-effort provenance span.
    ed.messages.clear()
    assert ed.exec_command_line('help hi')
    assert ed.messages
    msg = ed.messages[-1]
    assert 'say hi' in msg
    assert '<test>:' in msg

    # The command should show up in the command list hostcall.
    ed.vm.stack.clear()
    _hostcall(ed, 'ed.cmds')
    names = ed.vm.pop_list()
    assert 'hi' in names

    # Remove it.
    ed.vm.stack.clear()
    _hostcall(ed, 'ed.cmd-rm', 'hi')
    assert ed.vm.pop_int() == 1

    ed.messages.clear()
    assert not ed.exec_command_line('hi')
    assert ed.messages == ['command: no such command: hi']


def test_command_dispatcher_reports_raising_command_with_name() -> None:
    ed = Editor()

    def _boom(_ed: Editor, _args: list[str]) -> bool:
        raise RuntimeError('boom')

    ed.command_dispatcher.register('boom', _boom, doc='explode for test')

    assert not ed.exec_command_line('boom')
    assert ed.messages == ['command boom: error: boom']


def test_command_bar_parse_error_is_user_visible_not_an_editor_crash() -> None:
    ed = Editor()

    assert not ed.exec_command_line("open 'unterminated")
    assert ed.messages == ['command: parse error: No closing quotation']


def test_command_bar_parse_error_submit_path_closes_prompt_cleanly() -> None:
    ed = Editor()

    ed.enter_prompt('command', prefill="replace 'old")
    assert ed.prompt is not None
    assert not ed.submit_prompt()
    assert ed.prompt is None
    assert ed.messages[-1] == 'command: parse error: No closing quotation'


def test_mx_command_reports_micromax_error_with_command_name() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval(
        ': bad-cmd ( args -- ok ) drop drop drop ;',
        filename='<mx-test>',
    )
    ed.vm.eval(
        "' bad-cmd \"bad\" \"bad cmd\" \"ed.cmd-add\" hostcall",
        filename='<mx-test>',
    )

    assert not ed.exec_command_line('bad')
    assert ed.messages
    msg = ed.messages[-1]
    assert msg.startswith('command bad: error: <mx-test>:1:36: Stack underflow')
    assert 'trace: bad-cmd' in msg


def test_mx_completion_hook_ed_complete_cmd_specific() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    # Provide a command-specific completion word.
    # Contract: ( cmd tok_i prefix toks -- cands mode ) where mode=2 means replace.
    ed.vm.eval(
        ': ed.complete.testcmd ( cmd tok_i prefix toks -- cands mode )\n'
        '  drop drop drop drop\n'
        '  "alpha " list push "beta " swap push\n'
        '  2\n'
        ';',
        filename='<test>',
    )

    ed.enter_prompt('command', prefill='testcmd ')
    assert ed.prompt is not None

    # First Tab starts a suggestion session (multiple candidates).
    assert ed.prompt_complete(direction=1)
    assert ed.prompt.suggestions
    assert ed.prompt.suggest_base == 'testcmd '

    # Next Tab applies the first suggestion.
    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == 'testcmd alpha '

    # Next Tab cycles.
    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == 'testcmd beta '

    # Shift-Tab cycles back.
    assert ed.prompt_complete(direction=-1)
    assert ed.prompt.text == 'testcmd alpha '


def test_mx_completion_hook_can_return_metadata_rows() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval(
        """\
: row1 ( -- row ) list "alpha " swap push "topic" swap push "alpha menu" swap push "alpha info" swap push ;
: row2 ( -- row ) list "beta " swap push "topic" swap push "beta menu" swap push "beta info" swap push ;
: rows-demo ( -- rows ) list row1 swap push row2 swap push ;
: ed.complete.rowcmd ( cmd tok_i prefix toks -- cands rows mode )
  drop drop drop drop
  "alpha " list push "beta " swap push
  rows-demo
  2
;
""",
        filename='<test>',
    )

    ed.enter_prompt('command', prefill='rowcmd ')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    assert ed.prompt.suggestions == ['alpha ', 'beta ']

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-suggestion-rows')
    rows = ed.vm.pop_list()
    row_by_insert = {str(r[0]): r for r in rows if isinstance(r, list) and len(r) >= 4}
    assert row_by_insert['alpha '][1] == 'topic'
    assert row_by_insert['alpha '][2] == 'alpha menu'
    assert row_by_insert['alpha '][3] == 'alpha info'
    assert row_by_insert['beta '][1] == 'topic'
    assert row_by_insert['beta '][2] == 'beta menu'


def test_mx_completion_hook_rows_can_overlay_builtin_metadata() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval(
        """\
: ed.complete ( cmd tok_i prefix toks -- cands rows mode )
  drop drop drop drop
  "showstatus " list push
  list list "showstatus " swap push "plugin-command" swap push "plugin menu" swap push "plugin info" swap push swap push
  1
;
""",
        filename='<test>',
    )

    ed.enter_prompt('command', prefill='s')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    assert ed.prompt.suggestions

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-suggestion-rows')
    rows = ed.vm.pop_list()
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showstatus ')
    assert row[1] == 'plugin-command'
    assert row[2] == 'plugin menu'
    assert row[3] == 'plugin info'


def test_help_falls_back_to_visible_micromax_word() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval(': word-doc-demo ( x -- x ) ( demo word for help fallback ) ;', filename='<word-help>')

    ed.messages.clear()
    assert ed.exec_command_line('help word-doc-demo')
    assert ed.messages
    msg = ed.messages[-1]
    assert 'word word-doc-demo' in msg
    assert '[colon]' in msg
    assert '( x -- x )' in msg
    assert 'demo word for help fallback' in msg
    assert '<word-help>:' in msg


def test_showword_root_reports_runtime_summary_then_usage() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval(': showword-root-demo ( n -- n ) ( demo root showword ) 1 + ;', filename='<showword-root>')

    ed.messages.clear()
    assert not ed.exec_command_line('showword')
    assert ed.messages == [
        f"showword: {ed._word_inventory_preview_summary()}",
        'usage: showword NAME',
    ]



def test_showword_reports_visible_micromax_word() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval(': word-show-demo ( n -- n ) ( demo word for showword ) 1 + ;', filename='<showword>')

    ed.messages.clear()
    assert ed.exec_command_line('showword word-show-demo')
    assert ed.messages
    msg = ed.messages[-1]
    assert 'word word-show-demo' in msg
    assert '[colon]' in msg
    assert '( n -- n )' in msg
    assert '[wl forth]' in msg
    assert 'demo word for showword' in msg
    assert '<showword>:' in msg


def test_showword_missing_word_fails_plainly() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.messages.clear()
    assert not ed.exec_command_line('showword no-such-word')
    assert ed.messages == ['showword: no such word: no-such-word']


def test_word_detail_row_hostcall_matches_showword_surface() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval(': word-detail-demo ( n -- n ) ( demo word detail row ) 1 + ;', filename='<word-detail>')

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.word-detail-row', 'word-detail-demo')
    row = ed.vm.pop()
    assert isinstance(row, list)
    assert row[:5] == ['word-detail-demo', 'colon', '( n -- n )', 'forth', 'demo word detail row']
    assert row[5] == ['<word-detail>', 1, 1]
    assert isinstance(row[6], str) and ': word-detail-demo 1 + ;' in row[6]
    assert '\\ effect ( n -- n )' in row[6]

    ed.messages.clear()
    assert ed.exec_command_line('showword word-detail-demo')
    assert ed.messages[-1].startswith('word word-detail-demo [colon] ( n -- n ) [wl forth]: demo word detail row')
    assert '<word-detail>:1:1' in ed.messages[-1]
    assert ': word-detail-demo 1 + ;' in ed.messages[-1]
    assert '\\ effect ( n -- n )' in ed.messages[-1]


def test_word_detail_row_hostcall_returns_zero_for_missing_word() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.word-detail-row', 'no-such-word')
    assert ed.vm.pop() == 0


def test_topic_detail_row_and_showtopic_follow_help_precedence_without_opening_docs() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval(': topic-detail-demo ( n -- n ) ( demo word for showtopic ) 1 + ;', filename='<topic-detail>')

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.topic-detail-row', 'showword')
    row = ed.vm.pop()
    assert isinstance(row, list)
    assert row[0] == 'showword'
    assert row[1] == 'command'
    assert isinstance(row[2], list)
    assert row[2][0] == 'showword'

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.topic-detail-row', 'topic-detail-demo')
    row = ed.vm.pop()
    assert isinstance(row, list)
    assert row[0] == 'topic-detail-demo'
    assert row[1] == 'word'
    assert row[2][:5] == ['topic-detail-demo', 'colon', '( n -- n )', 'forth', 'demo word for showtopic']

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.topic-detail-row', 'vision')
    row = ed.vm.pop()
    assert isinstance(row, list)
    assert row[0] == 'vision'
    assert row[1] == 'doc'
    assert row[2][:4] == ['vision', 'Vision', '**Micromax** is a small, embeddable, concatenative language intended to be a *sane* plugin/config/macro system.', '00–09 Project']

    ed.messages.clear()
    assert ed.exec_command_line('showtopic vision')
    assert ed.current_help_doc_topic() is None
    assert ed.messages[-1].startswith('doc vision: Vision [00–09 Project] — **Micromax** is a small, embeddable')

    ed.messages.clear()
    assert ed.exec_command_line('showtopic topic-detail-demo')
    assert ed.messages[-1].startswith('word topic-detail-demo [colon] ( n -- n ) [wl forth]: demo word for showtopic')


def test_topic_detail_row_and_showtopic_missing_topic_are_plain() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.topic-detail-row', 'no-such-topic')
    assert ed.vm.pop() == 0

    ed.messages.clear()
    assert not ed.exec_command_line('showtopic no-such-topic')
    assert ed.messages == ['showtopic: no such topic: no-such-topic']


def test_showtopic_root_reports_runtime_summary_then_usage() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    summary = ed._topic_inventory_preview_summary()
    assert 'topic' in summary
    assert 'vision' in summary
    assert '[doc]' in summary

    ed.messages.clear()
    assert ed.exec_command_line('showtopic') is False
    assert ed.messages == [
        f'showtopic: {summary}',
        'usage: showtopic NAME',
    ]


def test_apropos_reports_matching_micromax_word() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval(': apropos-word-demo ( x -- x ) ( demo word for apropos ) ;', filename='<apropos>')

    ed.messages.clear()
    assert ed.exec_command_line('apropos aproposwd')
    assert ed.messages
    msg = ed.messages[-1]
    assert msg.startswith('apropos aproposwd: ')
    assert ' topic(s), ' in msg
    assert 'apropos-word-demo [word]' in msg
    assert 'demo word for apropos' in msg


def test_apropos_empty_inventory_reports_zero_topics() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.messages.clear()
    assert not ed.exec_command_line('apropos zzz-no-such-topic')
    assert ed.messages == ['apropos zzz-no-such-topic: 0 topic(s)']


def test_apropos_can_match_topic_summary_text() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.messages.clear()
    assert ed.exec_command_line('apropos visible micromax')
    assert ed.messages
    msg = ed.messages[-1]
    assert 'apropos visible micromax:' in msg
    assert 'showword [command]' in msg
    assert 'show visible micromax word' in msg


def test_apropos_can_match_topic_terms_out_of_order() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.messages.clear()
    assert ed.exec_command_line('apropos word show')
    assert ed.messages
    msg = ed.messages[-1]
    assert 'apropos word show:' in msg
    assert 'showword [command]' in msg


def test_help_unknown_topic_suggests_apropos_matches() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.messages.clear()
    assert not ed.exec_command_line('help shwrd')
    assert ed.messages
    msg = ed.messages[-1]
    assert 'help: no such topic: shwrd. Try:' in msg
    assert 'showword [command]' in msg


def test_help_unknown_topic_suggests_multi_term_apropos_matches() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.messages.clear()
    assert not ed.exec_command_line('help word show')
    assert ed.messages
    msg = ed.messages[-1]
    assert 'help: no such topic: word show. Try:' in msg
    assert 'showword [command]' in msg



def test_help_docs_unknown_topic_is_typed() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.messages.clear()
    assert not ed.exec_command_line('help docs zzz-no-such-doc')
    assert ed.messages == ['help docs: no such doc: zzz-no-such-doc']

def test_topic_rows_and_apropos_rows_hostcalls() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval(': topic-row-demo ( x -- x ) ( demo word for topic rows ) ;', filename='<topic-rows>')

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.topic-rows')
    rows = ed.vm.pop_list()

    showword_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showword')
    assert showword_row[1] == 'command'
    assert 'show visible micromax word' in str(showword_row[2])

    word_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'topic-row-demo')
    assert word_row[1] == 'word'
    assert 'colon' in str(word_row[2])
    assert '( x -- x )' in str(word_row[2])
    assert 'demo word for topic rows' in str(word_row[3])

    doc_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'vision')
    assert doc_row[1] == 'doc'
    assert doc_row[2] == 'Vision'
    assert '**Micromax** is a small, embeddable' in str(doc_row[3])

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.apropos-rows', 'trd')
    arows = ed.vm.pop_list()
    assert arows
    assert arows[0][0] == 'topic-row-demo'
    assert arows[0][1] == 'word'

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.apropos-rows', 'visible micromax')
    doc_rows = ed.vm.pop_list()
    assert doc_rows
    assert doc_rows[0][0] == 'showword'
    assert doc_rows[0][1] == 'command'

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.apropos-rows', 'vision')
    doc_rows = ed.vm.pop_list()
    assert doc_rows
    assert doc_rows[0][0] == 'vision'
    assert doc_rows[0][1] == 'doc'


def test_topic_section_rows_and_apropos_section_rows_hostcalls() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval(': topic-sections-demo ( x -- x ) ( demo word for topic sections ) ;', filename='<topic-sections>')

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.topic-section-rows')
    sections = ed.vm.pop_list()
    labels = [str(sec[0]) for sec in sections if isinstance(sec, list) and sec]
    assert labels[:4] == ['Commands', 'Actions', 'Words', 'Docs']

    commands = next(sec[1] for sec in sections if isinstance(sec, list) and sec and sec[0] == 'Commands')
    assert any(isinstance(row, list) and row and row[0] == 'showword' for row in commands)

    words = next(sec[1] for sec in sections if isinstance(sec, list) and sec and sec[0] == 'Words')
    assert any(isinstance(row, list) and row and row[0] == 'topic-sections-demo' for row in words)

    docs = next(sec[1] for sec in sections if isinstance(sec, list) and sec and sec[0] == 'Docs')
    assert any(isinstance(row, list) and row and row[0] == 'vision' for row in docs)

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.apropos-section-rows', 'visible micromax')
    asections = ed.vm.pop_list()
    assert asections
    assert asections[0][0] == 'Commands'
    assert any(isinstance(row, list) and row and row[0] == 'showword' for row in asections[0][1])


def test_topic_section_summary_rows_and_showtopics_stay_count_aware() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval(': topic-summary-demo ( x -- x ) ( demo word for topic summaries ) ;', filename='<topic-summary>')

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.topic-section-summary-rows')
    rows = ed.vm.pop_list()
    labels = [str(row[0]) for row in rows]
    assert labels[:4] == ['Commands', 'Actions', 'Words', 'Docs']
    assert all(int(row[1]) > 0 for row in rows[:4])
    assert all(str(row[2]) for row in rows[:4])
    assert all(str(row[3]) for row in rows[:4])
    words_row = next(row for row in rows if isinstance(row, list) and row and row[0] == 'Words')
    assert 'primitive wl=' in str(words_row[3])
    assert ' · ' in str(words_row[3])
    docs_row = next(row for row in rows if isinstance(row, list) and row and row[0] == 'Docs')
    assert ' · ' in str(docs_row[3])

    assert ed.exec_command_line('showtopics')
    assert ed.messages[0].startswith('showtopics: 4 section(s), ')
    assert ed.messages[1].startswith('Commands: ')
    assert any(msg.startswith('Words: ') for msg in ed.messages)
    assert any(msg.startswith('Docs: ') for msg in ed.messages)

    ed.messages.clear()
    assert ed.exec_command_line('showtopics Commands')
    assert ed.messages[0].startswith('showtopics Commands: 1 section(s), ')
    assert ed.messages[1].startswith('Commands: ')

    ed.messages.clear()
    assert ed.exec_command_line('showtopics Docs')
    assert ed.messages[0].startswith('showtopics Docs: 1 section(s), ')
    assert ed.messages[1].startswith('Docs: ')


def test_apropos_and_doc_section_summary_rows_and_showdocs() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.apropos-section-summary-rows', 'visible micromax')
    rows = ed.vm.pop_list()
    assert rows
    assert rows[0][0] == 'Commands'
    assert rows[0][2] == 'showword'
    assert 'show visible micromax word' in str(rows[0][3])

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.doc-section-summary-rows', '')
    drows = ed.vm.pop_list()
    assert drows
    assert drows[0][0] == '00–09 Project'
    assert int(drows[0][1]) > 0
    assert str(drows[0][2])
    assert str(drows[0][3])
    assert ' · ' in str(drows[0][3])

    assert ed.exec_command_line('showdocs')
    assert ed.messages[0].startswith('showdocs: ')
    assert 'section(s)' in ed.messages[0]
    assert 'doc(s)' in ed.messages[0]
    assert ed.messages[1].startswith('00–09 Project: ')
    assert '(e.g. ' in ed.messages[1]

    ed.messages.clear()
    assert ed.exec_command_line('showdocs 100+ Feature notes')
    assert ed.messages[0].startswith('showdocs 100+ Feature notes: 1 section(s), ')
    assert ed.messages[0].endswith(' doc(s)')
    assert ed.messages[1].startswith('100+ Feature notes: ')
    assert '(e.g. ' in ed.messages[1]


def test_command_palette_rows_hostcall_ranks_commands_and_actions() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.command-palette-rows', 'status')
    rows = ed.vm.pop_list()

    assert rows
    assert rows[0][0] == 'showstatus'
    assert rows[0][1] == 'command'
    assert 'portable statusline summary' in str(rows[0][2])


def test_command_palette_rows_hostcall_shows_recent_items_first_without_duplicates() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    assert ed.exec_command_line('commandpick status')
    assert ed.submit_prompt() is True
    assert ed.prompt is not None
    assert ed.prompt.kind == 'command'
    ed.cancel_prompt()

    assert ed.exec_command_line('commandpick command bar')
    assert ed.submit_prompt() is True
    assert ed.prompt is not None
    assert ed.prompt.kind == 'command'
    ed.cancel_prompt()

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.command-palette-rows', '')
    rows = ed.vm.pop_list()

    assert rows[:2]
    assert rows[0][0] == 'CommandMode'
    assert rows[0][1] == 'action'
    assert rows[1][0] == 'showstatus'
    assert rows[1][1] == 'command'
    assert sum(1 for row in rows if isinstance(row, list) and row and row[0] == 'showstatus') == 1
    assert sum(1 for row in rows if isinstance(row, list) and row and row[0] == 'CommandMode') == 1



def test_command_palette_rows_hostcall_keeps_openpath_context_for_visible_file_and_dir_targets(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    p = tmp_path / 'guide' / 'intro.md'
    r = tmp_path / 'guide' / 'notes.md'
    q = tmp_path / 'draft.txt'
    p.parent.mkdir(parents=True)
    p.write_text('intro\nnext\n', encoding='utf-8')
    r.write_text('notes\n', encoding='utf-8')
    q.write_text('draft\n', encoding='utf-8')

    assert ed.exec_command_line('set cap.fs-list true')

    ed.open_file(str(p))
    ed.open_file(str(r))
    assert ed.switch_buffer(str(p))
    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    eb.cursors[eb.primary] = eb.buf.clamp(Cursor(1, 1))
    eb.buf.dirty = True

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.command-palette-rows', str(tmp_path / 'g'))
    rows = ed.vm.pop_list()

    row = next(r for r in rows if isinstance(r, list) and r and r[0] == str(tmp_path / 'guide') + '/')
    assert row[1] == 'openpath'
    assert row[2] == 'dir'
    assert row[3] == 'recent dir: 2 files [active, open=2, dirty=1] | drill down'

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.command-palette-rows', str(p))
    rows = ed.vm.pop_list()

    row = next(r for r in rows if isinstance(r, list) and r and r[0] == str(p))
    assert row[1] == 'openpath'
    assert row[2] == 'file'
    assert row[3] == f'recent #2 [active, dirty] @ 2:1 | {p} | current buffer'

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.command-palette-rows', str(q))
    rows = ed.vm.pop_list()

    row = next(r for r in rows if isinstance(r, list) and r and r[0] == str(q))
    assert row[1] == 'openpath'
    assert row[2] == 'file'
    assert row[3] == str(tmp_path)

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.command-palette-rows', str(r))
    rows = ed.vm.pop_list()

    row = next(row for row in rows if isinstance(row, list) and row and row[0] == str(r))
    assert row[1] == 'openpath'
    assert row[2] == 'file'
    assert row[3] == f'recent #1 [open] @ 1:0 | {r} | switch buffer'



def test_command_palette_rows_hostcall_keeps_exact_open_row_context(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    p = tmp_path / 'guide' / 'intro.md'
    p.parent.mkdir(parents=True)
    p.write_text('intro\nnext\n', encoding='utf-8')

    assert ed.exec_command_line('set cap.fs-list true')

    ed.open_file(str(p))
    assert ed.switch_buffer(str(p))
    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    eb.cursors[eb.primary] = eb.buf.clamp(Cursor(1, 1))
    eb.buf.dirty = True

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.command-palette-rows', str(p))
    rows = ed.vm.pop_list()

    row = next(r for r in rows if isinstance(r, list) and r and r[0] == str(p) and r[2] == 'open')
    assert row[1] == 'openpath'
    assert row[3] == f'recent #1 [active, dirty] @ 2:1 | {p} | existing file | current buffer'

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.command-palette-rows', str(p.parent) + '/')
    rows = ed.vm.pop_list()

    row = next(r for r in rows if isinstance(r, list) and r and r[0] == str(p.parent) + '/' and r[2] == 'open')
    assert row[1] == 'openpath'
    assert row[3] == 'recent dir: 1 file [active, open=1, dirty=1] | directory | drill down'

    missing = tmp_path / 'draft.md'
    ed.vm.stack.clear()
    _hostcall(ed, 'ed.command-palette-rows', str(missing))
    rows = ed.vm.pop_list()

    row = next(r for r in rows if isinstance(r, list) and r and r[0] == str(missing) and r[2] == 'open')
    assert row[1] == 'openpath'
    assert row[3] == f'new file | {tmp_path}'


    scratch = tmp_path / 'scratch.md'
    ed.open_file(str(scratch))
    ed.vm.stack.clear()
    _hostcall(ed, 'ed.command-palette-rows', str(scratch))
    rows = ed.vm.pop_list()

    row = next(r for r in rows if isinstance(r, list) and r and r[0] == str(scratch) and r[2] == 'open')
    assert row[1] == 'openpath'
    assert row[3] == f'recent #1 [active] @ 1:0 | {scratch} | new file | current buffer'


def test_command_palette_rows_hostcall_keeps_parsecursor_extensionless_targets_pathlike(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    guide = tmp_path / 'guide'
    guide.mkdir()
    intro = tmp_path / 'intro'
    intro.write_text('one\ntwo\n', encoding='utf-8')

    assert ed.exec_command_line('set cap.fs-list true')
    assert ed.exec_command_line('set parsecursor true')

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.command-palette-rows', str(guide) + ':2')
    rows = ed.vm.pop_list()

    row = next(r for r in rows if isinstance(r, list) and r and r[0] == str(guide) + ':2' and r[2] == 'open')
    assert row[1] == 'openpath'
    assert row[3] == 'directory | drill down'

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.command-palette-rows', str(intro) + ':2')
    rows = ed.vm.pop_list()

    row = next(r for r in rows if isinstance(r, list) and r and r[0] == str(intro) + ':2' and r[2] == 'open')
    assert row[1] == 'openpath'
    assert row[3] == f'existing file | {tmp_path} | cursor 2:0'


def test_command_palette_rows_hostcall_keeps_partial_extensionless_parsecursor_completion_rows_visible(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    ed = Editor()
    install_editor_hostcalls(ed)

    guide = tmp_path / 'guide'
    guide.mkdir()
    intro = tmp_path / 'intro'
    intro.write_text('one\ntwo\nthird\n', encoding='utf-8')

    assert ed.exec_command_line('set cap.fs-list true')
    assert ed.exec_command_line('set parsecursor true')

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.command-palette-rows', 'gu:2')
    rows = ed.vm.pop_list()

    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'guide/:2' and r[2] == 'dir')
    assert row[1] == 'openpath'
    assert row[3] == f'{tmp_path} | drill down'

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.command-palette-rows', 'intr:2')
    rows = ed.vm.pop_list()

    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'intro:2' and r[2] == 'file')
    assert row[1] == 'openpath'
    assert row[3] == f'{tmp_path} | cursor 2:0'


def test_command_palette_rows_hostcall_keeps_parsecursor_partial_unsaved_open_buffer_completion_visible(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-list true")
    assert ed.exec_command_line("set parsecursor true")

    scratch = tmp_path / "scratch.md"
    ed.open_file(str(scratch))

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.command-palette-rows', 'scr:2')
    rows = ed.vm.pop_list()

    row = next(
        r
        for r in rows
        if isinstance(r, list)
        and r
        and r[0] == 'scratch.md:2'
        and r[1] == 'openpath'
        and r[2] == 'file'
    )
    assert row[3] == f'recent #1 [active] @ 1:0 | {tmp_path} | new file | current buffer | goto 1:0'




def test_command_palette_rows_hostcall_keeps_recent_file_row_missing_file_truth_for_deleted_recent_file(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    ed = Editor()
    install_editor_hostcalls(ed)

    old = tmp_path / 'old.md'
    old.write_text('old\n', encoding='utf-8')

    assert ed.exec_command_line('set cap.fs-list true')

    ed.open_file(str(old))
    assert ed.exec_command_line('close')
    old.unlink()

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.command-palette-rows', 'old')
    rows = ed.vm.pop_list()

    row = next(
        r
        for r in rows
        if isinstance(r, list)
        and r
        and r[0] == str(old)
        and r[1] == 'recentfile'
    )
    assert row[3] == f'section={tmp_path} | new file | empty buffer @ 1:0'



def test_command_palette_rows_hostcall_keeps_recent_file_row_missing_file_truth_for_unsaved_open_buffer(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line('set cap.fs-list true')

    scratch = tmp_path / 'scratch.md'
    ed.open_file(str(scratch))

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.command-palette-rows', 'scratch')
    rows = ed.vm.pop_list()

    row = next(
        r
        for r in rows
        if isinstance(r, list)
        and r
        and r[0] == str(scratch)
        and r[1] == 'recentfile'
    )
    assert row[3] == f'section={tmp_path} | new file | current buffer'



def test_command_palette_rows_hostcall_keeps_parsecursor_deleted_recent_file_completion_new_file_truth(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    ed = Editor()
    install_editor_hostcalls(ed)

    old = tmp_path / 'old.md'
    old.write_text('old\n', encoding='utf-8')

    assert ed.exec_command_line('set cap.fs-list true')
    assert ed.exec_command_line('set parsecursor true')

    ed.open_file(str(old))
    assert ed.exec_command_line('close')
    old.unlink()

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.command-palette-rows', 'ol:3')
    rows = ed.vm.pop_list()

    row = next(
        r
        for r in rows
        if isinstance(r, list)
        and r
        and r[0] == 'old.md:3'
        and r[1] == 'openpath'
        and r[2] == 'file'
    )
    assert row[3] == f'recent #1 | {tmp_path} | new file | empty buffer @ 1:0'


def test_command_palette_rows_hostcall_keeps_parsecursor_relative_file_query_pathlike(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line('set cap.fs-list true')
    assert ed.exec_command_line('set parsecursor true')
    _hostcall(ed, 'ed.command-palette-rows', 'draft.md:3:7')

    rows = ed.vm.pop_list()
    row = next(
        r
        for r in rows
        if isinstance(r, list)
        and len(r) >= 4
        and str(r[0]) == 'draft.md:3:7'
        and str(r[1]) == 'openpath'
        and str(r[2]) == 'open'
    )
    assert row[3] == f'new file | {tmp_path} | empty buffer @ 1:0'


def test_command_palette_rows_hostcall_keeps_parsecursor_completion_rows_visible_with_cursor_suffix(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    guide = tmp_path / 'guide'
    guide.mkdir()
    intro = guide / 'intro.md'
    intro.write_text('intro\nnext\nthird\n', encoding='utf-8')

    assert ed.exec_command_line('set cap.fs-list true')
    assert ed.exec_command_line('set parsecursor true')

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.command-palette-rows', str(guide / 'i') + ':2')
    rows = ed.vm.pop_list()

    row = next(r for r in rows if isinstance(r, list) and r and r[0] == str(intro) + ':2' and r[2] == 'file')
    assert row[1] == 'openpath'
    assert row[3] == str(guide) + ' | cursor 2:0'

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.command-palette-rows', str(intro) + ':2')
    rows = ed.vm.pop_list()

    row = next(r for r in rows if isinstance(r, list) and r and r[0] == str(intro) + ':2' and r[2] == 'open')
    assert row[1] == 'openpath'
    assert row[3] == f'existing file | {guide} | cursor 2:0'


def test_command_palette_rows_hostcall_keeps_parsecursor_file_open_row_goto_cue_for_open_buffer(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    guide = tmp_path / 'guide'
    guide.mkdir()
    intro = guide / 'intro.md'
    intro.write_text('intro\nnext\nthird\n', encoding='utf-8')

    assert ed.exec_command_line('set cap.fs-list true')
    assert ed.exec_command_line('set parsecursor true')

    ed.open_file(str(intro))
    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    eb.cursors[eb.primary] = eb.buf.clamp(Cursor(1, 1))
    eb.buf.dirty = True

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.command-palette-rows', str(intro) + ':1:0')
    rows = ed.vm.pop_list()

    row = next(r for r in rows if isinstance(r, list) and r and r[0] == str(intro) + ':1:0' and r[2] == 'open')
    assert row[1] == 'openpath'
    assert row[3] == f'recent #1 [active, dirty] @ 2:1 | {intro} | existing file | current buffer | goto 1:0'


def test_command_palette_rows_hostcall_keeps_parsecursor_directory_open_row_honest(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    guide = tmp_path / 'guide'
    guide.mkdir()
    (guide / 'intro.md').write_text('intro\n', encoding='utf-8')

    assert ed.exec_command_line('set cap.fs-list true')
    assert ed.exec_command_line('set parsecursor true')

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.command-palette-rows', str(guide) + '/:2')
    rows = ed.vm.pop_list()

    row = next(r for r in rows if isinstance(r, list) and r and r[0] == str(guide) + '/:2' and r[2] == 'open')
    assert row[1] == 'openpath'
    assert row[3] == 'directory | drill down'


def test_command_palette_rows_hostcall_keeps_parsecursor_partial_directory_completion_rows_visible(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    guide = tmp_path / 'guide'
    guide.mkdir()
    sub = guide / 'sub'
    sub.mkdir()
    (sub / 'note.md').write_text('note\n', encoding='utf-8')

    assert ed.exec_command_line('set cap.fs-list true')
    assert ed.exec_command_line('set parsecursor true')

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.command-palette-rows', str(guide / 's') + ':2')
    rows = ed.vm.pop_list()

    row = next(r for r in rows if isinstance(r, list) and r and r[0] == str(sub) + '/:2' and r[2] == 'dir')
    assert row[1] == 'openpath'
    assert row[3] == f'{guide} | drill down'


def test_command_palette_rows_hostcall_keeps_exact_recent_file_metadata(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line('set cap.fs-list true')

    (tmp_path / 'pyproject.toml').write_text('[project]\nname = "demo"\n', encoding='utf-8')
    p = tmp_path / 'guide' / 'intro.md'
    q = tmp_path / 'notes' / 'daily.txt'
    p.parent.mkdir(parents=True)
    q.parent.mkdir(parents=True)
    p.write_text('intro\nnext\n', encoding='utf-8')
    q.write_text('notes\n', encoding='utf-8')

    ed.open_file(str(p))
    ed.open_file(str(q))
    assert ed.switch_buffer(str(p))
    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    eb.cursors[eb.primary] = eb.buf.clamp(Cursor(1, 1))
    eb.buf.dirty = True

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.command-palette-rows', 'intro')
    rows = ed.vm.pop_list()

    row = next(r for r in rows if isinstance(r, list) and r and r[0] == str(p))
    assert row[1] == 'recentfile'
    assert row[2] == 'intro.md #2 [active, dirty] @ 2:1'
    assert row[3] == f'section={tmp_path} | guide/intro.md | existing file | current buffer'

    row = next(r for r in rows if isinstance(r, list) and r and r[0] == str(q))
    assert row[1] == 'recentfile'
    assert row[2] == 'daily.txt #1 [open] @ 1:0'
    assert row[3] == f'section={tmp_path} | notes/daily.txt | existing file | switch buffer'



def test_command_palette_rows_hostcall_keeps_existing_file_truth_for_closed_recent_file(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line('set cap.fs-list true')

    old = tmp_path / 'old.md'
    old.write_text('old\n', encoding='utf-8')

    ed.open_file(str(old))
    assert ed.exec_command_line('close')

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.command-palette-rows', 'old')
    rows = ed.vm.pop_list()

    row = next(r for r in rows if isinstance(r, list) and r and r[0] == str(old))
    assert row[1] == 'recentfile'
    assert row[3] == f'section={tmp_path} | existing file'


def test_command_palette_section_rows_hostcall_includes_recent_section() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    assert ed.exec_command_line('commandpick status')
    assert ed.submit_prompt() is True
    assert ed.prompt is not None
    assert ed.prompt.kind == 'command'
    ed.cancel_prompt()

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.command-palette-section-rows', '')
    sections = ed.vm.pop_list()

    assert sections
    assert sections[0][0] == 'Recent'
    recent = sections[0][1]
    assert any(isinstance(row, list) and row and row[0] == 'showstatus' for row in recent)


def test_command_palette_section_summary_rows_and_showpalettegroups_are_count_aware() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    assert ed.exec_command_line('commandpick status')
    assert ed.submit_prompt() is True
    assert ed.prompt is not None
    assert ed.prompt.kind == 'command'
    ed.cancel_prompt()

    rows = ed.command_palette_section_summary_rows('portable statusline summary')
    assert rows
    assert rows[0][0] == 'Recent'
    assert rows[0][1] == 1
    assert rows[0][2] == 'showstatus'
    assert 'portable statusline summary' in str(rows[0][3])

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.command-palette-section-summary-rows', 'portable statusline summary')
    host_rows = ed.vm.pop_list()
    assert host_rows == rows

    ed.messages.clear()
    assert ed.exec_command_line('showpalettegroups portable statusline summary') is True
    assert ed.messages == [
        'showpalettegroups portable statusline summary: 1 section(s), 1 item(s)',
        'Recent: 1 (e.g. showstatus — showstatus - show portable statusline summary)',
    ]

    empty_rows = ed.command_palette_section_summary_rows('zzz-no-such-palette-item')
    assert empty_rows == []

    ed.messages.clear()
    assert ed.exec_command_line('showpalettegroups zzz-no-such-palette-item') is True
    assert ed.messages == ['showpalettegroups zzz-no-such-palette-item: 0 section(s), 0 item(s)']


def test_commandpick_command_opens_palette_prompt_with_ranked_rows() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    assert ed.exec_command_line('commandpick status')
    assert ed.prompt is not None
    assert ed.prompt.kind == 'palette'
    assert ed.prompt.text == 'status'
    assert ed.prompt.suggestions
    assert ed.prompt.suggestions[0] == 'showstatus'

    row = ed.prompt_suggestion_rows()[0]
    assert row[0] == 'showstatus'
    assert row[1] == 'command'
    assert 'portable statusline summary' in str(row[2])


def test_topicpick_command_opens_topic_prompt_with_ranked_rows() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    assert ed.exec_command_line('topicpick visible micromax')
    assert ed.prompt is not None
    assert ed.prompt.kind == 'topic'
    assert ed.prompt.text == 'visible micromax'
    assert ed.prompt.suggestions
    assert ed.prompt.suggestions[0] == 'showword'

    rows = ed.prompt_suggestion_rows()
    row = next(r for r in rows if r and r[0] == 'showword')
    assert row[1] == 'command'
    assert 'show visible micromax word' in str(row[2])


def test_ed_command_palette_hostcall_live_refresh_and_submit_action() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.command-palette', 'status')

    assert ed.prompt is not None
    assert ed.prompt.kind == 'palette'
    assert ed.prompt.suggestions
    assert ed.prompt.suggestions[0] == 'showstatus'

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-set', 'command bar')
    assert ed.prompt is not None
    assert ed.prompt.suggestions
    assert ed.prompt.suggestions[0] == 'CommandMode'

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-submit')
    assert ed.vm.pop_int() == 1
    assert ed.prompt is not None
    assert ed.prompt.kind == 'command'
    assert ed.prompt.text == ''


def test_ed_topic_prompt_hostcall_opens_topic_prompt() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.topic-prompt', 'shwrd')

    assert ed.prompt is not None
    assert ed.prompt.kind == 'topic'
    assert ed.prompt.text == 'shwrd'
    assert ed.prompt.suggestions
    assert ed.prompt.suggestions[0] == 'showword'


def test_commandpick_submit_on_command_opens_command_bar_with_prefill() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    assert ed.exec_command_line('commandpick status')
    assert ed.prompt is not None
    assert ed.prompt.kind == 'palette'

    assert ed.submit_prompt() is True
    assert ed.prompt is not None
    assert ed.prompt.kind == 'command'
    assert ed.prompt.text == 'showstatus '


def test_command_palette_apropos_rows_prefer_recent_match_on_tie() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.command_dispatcher.register('pal-a', lambda _ed, _args: True, doc='palette tie alpha')
    ed.command_dispatcher.register('pal-b', lambda _ed, _args: True, doc='palette tie beta')

    assert ed.exec_command_line('commandpick pal-b')
    assert ed.submit_prompt() is True
    assert ed.prompt is not None
    assert ed.prompt.kind == 'command'
    ed.cancel_prompt()

    rows = ed.command_palette_apropos_rows('pal')
    assert rows
    assert rows[0][0] == 'pal-b'
    assert rows[0][1] == 'command'


def test_binding_prompt_rows_hostcall_ranks_current_bindings_by_desc() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval('"Ctrl-z" "command:help" "ed.bind" hostcall', filename='<global-bind>')
    ed.vm.eval('"nav" "Ctrl-x" "command:quit" "ed.bind-mode" hostcall', filename='<nav-bind>')
    _hostcall(ed, 'ed.keymode-push', 'nav')

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.binding-prompt-rows', 'quit')
    rows = ed.vm.pop_list()

    assert rows
    assert rows[0][0] == 'Ctrl-x'
    assert rows[0][1] == 'binding'
    assert '@nav command:quit' in str(rows[0][2])
    assert 'request editor quit' in str(rows[0][3])


def test_binding_prompt_rows_hostcall_matches_multi_term_query_across_fields() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval('"Ctrl-z" "command:help" "ed.bind" hostcall', filename='<global-bind>')
    ed.vm.eval('"nav" "Ctrl-x" "command:quit" "ed.bind-mode" hostcall', filename='<nav-bind>')
    _hostcall(ed, 'ed.keymode-push', 'nav')

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.binding-prompt-rows', 'quit Ctrl')
    rows = ed.vm.pop_list()

    assert rows
    assert rows[0][0] == 'Ctrl-x'
    assert '@nav command:quit' in str(rows[0][2])


def test_binding_section_rows_hostcall_groups_by_winning_mode() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval('"Ctrl-z" "command:help" "ed.bind" hostcall', filename='<global-bind>')
    ed.vm.eval('"nav" "Ctrl-x" "command:quit" "ed.bind-mode" hostcall', filename='<nav-bind>')
    _hostcall(ed, 'ed.keymode-push', 'nav')

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.binding-section-rows', '')
    sections = ed.vm.pop_list()

    assert [sec[0] for sec in sections] == ['nav', 'Global']
    assert sections[0][1][0][0] == 'Ctrl-x'
    assert '@nav command:quit' in str(sections[0][1][0][2])


def test_bindingpick_command_opens_binding_prompt_with_ranked_rows() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval('"Ctrl-z" "command:help" "ed.bind" hostcall', filename='<global-bind>')
    ed.vm.eval('"nav" "Ctrl-x" "command:quit" "ed.bind-mode" hostcall', filename='<nav-bind>')
    _hostcall(ed, 'ed.keymode-push', 'nav')

    assert ed.exec_command_line('bindingpick quit')
    assert ed.prompt is not None
    assert ed.prompt.kind == 'binding'
    assert ed.prompt.text == 'quit'
    assert ed.prompt.suggestions
    assert ed.prompt.suggestions[0] == 'Ctrl-x'

    row = ed.prompt_suggestion_rows()[0]
    assert row[0] == 'Ctrl-x'
    assert row[1] == 'binding'
    assert '@nav command:quit' in str(row[2])
    assert 'request editor quit' in str(row[3])


def test_ed_binding_prompt_hostcall_live_refresh_and_submit() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval('"Ctrl-z" "command:help" "ed.bind" hostcall', filename='<global-bind>')
    ed.vm.eval('"nav" "Ctrl-x" "command:quit" "ed.bind-mode" hostcall', filename='<nav-bind>')
    _hostcall(ed, 'ed.keymode-push', 'nav')

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.binding-prompt', 'help')

    assert ed.prompt is not None
    assert ed.prompt.kind == 'binding'
    assert ed.prompt.suggestions
    assert ed.prompt.suggestions[0] == 'Ctrl-z'

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-set', 'quit')
    assert ed.prompt is not None
    assert ed.prompt.suggestions
    assert ed.prompt.suggestions[0] == 'Ctrl-x'

    ed.messages.clear()
    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-submit')
    assert ed.messages
    assert 'Ctrl-x -> command:quit' in ed.messages[-1]
    assert '[desc request editor quit]' in ed.messages[-1]


def test_command_palette_section_rows_hostcall_exposes_commands_and_actions_on_empty_query() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.command-palette-section-rows', '')
    sections = ed.vm.pop_list()

    labels = [sec[0] for sec in sections if isinstance(sec, list) and sec]
    assert labels[:2] == ['Commands', 'Actions']


def test_commandpick_empty_query_browse_exposes_action_section() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    assert ed.exec_command_line('commandpick') is True
    assert ed.prompt is not None
    assert ed.prompt.kind == 'palette'
    assert ed.prompt.suggestion_rows

    labels = []
    last = None
    for row in ed.prompt.suggestion_rows:
        label = ed.prompt_row_section_label([str(x) for x in list(row[:4])], prompt_kind='palette')
        if label != last:
            labels.append(label)
            last = label
    assert labels[:2] == ['Commands', 'Actions']


def test_commandpick_empty_submit_reports_zero_matches() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    assert ed.exec_command_line('commandpick zzz-no-such-command')
    assert ed.prompt is not None
    assert ed.prompt.kind == 'palette'
    assert ed.prompt.suggestions == []

    ed.messages.clear()
    assert ed.submit_prompt() is False
    assert ed.messages == ['commandpick zzz-no-such-command: 0 match(s)']


def test_topicpick_empty_submit_reports_zero_topics() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    assert ed.exec_command_line('topicpick zzz-no-such-topic')
    assert ed.prompt is not None
    assert ed.prompt.kind == 'topic'
    assert ed.prompt.suggestions == []

    ed.messages.clear()
    assert ed.submit_prompt() is False
    assert ed.messages == ['topicpick zzz-no-such-topic: 0 topic(s)']


def test_bindingpick_empty_submit_reports_zero_bindings() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    assert ed.exec_command_line('bindingpick zzz-no-such-binding')
    assert ed.prompt is not None
    assert ed.prompt.kind == 'binding'
    assert ed.prompt.suggestions == []

    ed.messages.clear()
    assert ed.submit_prompt() is False
    assert ed.messages == ['bindingpick zzz-no-such-binding: 0 binding(s)']



def test_mx_completion_added_candidate_does_not_inherit_path_row_metadata(tmp_path, monkeypatch) -> None:
    (tmp_path / 'alpha.txt').write_text('x', encoding='utf-8')
    monkeypatch.chdir(tmp_path)

    ed = Editor()
    install_editor_hostcalls(ed)
    ed.vm.eval(
        """
: ed.complete ( cmd tok_i prefix toks -- cands mode )
  drop drop drop drop
  "archive " list push
  1
;
""",
        filename='<test>',
    )

    ed.enter_prompt('command', prefill='open a')
    assert ed.prompt is not None
    assert ed.prompt_complete(direction=1)

    rows = ed.prompt_suggestion_rows()
    by_insert = {str(r[0]): r for r in rows if isinstance(r, list) and r}
    assert by_insert['alpha.txt '][1] == 'file'
    assert by_insert['archive '][1] == ''
    assert by_insert['archive '][2] == ''


def test_mx_completion_replace_mode_clears_path_row_metadata(tmp_path, monkeypatch) -> None:
    (tmp_path / 'alpha.txt').write_text('x', encoding='utf-8')
    monkeypatch.chdir(tmp_path)

    ed = Editor()
    install_editor_hostcalls(ed)
    ed.vm.eval(
        """
: ed.complete ( cmd tok_i prefix toks -- cands mode )
  drop drop drop drop
  "archive " list push
  2
;
""",
        filename='<test>',
    )

    ed.enter_prompt('command', prefill='open a')
    assert ed.prompt is not None
    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == 'open archive '
    assert ed.prompt_suggestion_rows() == []
