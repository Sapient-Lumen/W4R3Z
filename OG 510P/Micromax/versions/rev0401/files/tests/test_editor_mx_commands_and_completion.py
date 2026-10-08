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


def test_topic_section_rows_and_apropos_section_rows_hostcalls() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval(': topic-sections-demo ( x -- x ) ( demo word for topic sections ) ;', filename='<topic-sections>')

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.topic-section-rows')
    sections = ed.vm.pop_list()
    labels = [str(sec[0]) for sec in sections if isinstance(sec, list) and sec]
    assert labels[:3] == ['Commands', 'Actions', 'Words']

    commands = next(sec[1] for sec in sections if isinstance(sec, list) and sec and sec[0] == 'Commands')
    assert any(isinstance(row, list) and row and row[0] == 'showword' for row in commands)

    words = next(sec[1] for sec in sections if isinstance(sec, list) and sec and sec[0] == 'Words')
    assert any(isinstance(row, list) and row and row[0] == 'topic-sections-demo' for row in words)

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.apropos-section-rows', 'visible micromax')
    asections = ed.vm.pop_list()
    assert asections
    assert asections[0][0] == 'Commands'
    assert any(isinstance(row, list) and row and row[0] == 'showword' for row in asections[0][1])


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
