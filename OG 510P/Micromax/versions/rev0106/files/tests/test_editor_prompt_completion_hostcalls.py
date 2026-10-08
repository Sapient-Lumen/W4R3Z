from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _hostcall(ed: Editor, name: str, *args: object) -> list[object]:
    vm = ed.vm
    for a in args:
        vm.stack.append(a)
    vm.stack.append(name)
    vm.eval('hostcall')
    # return a shallow snapshot of the stack for convenience
    return list(vm.stack)


def test_prompt_complete_unique_match_inserts_and_no_session() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.enter_prompt('command', prefill='he')
    assert ed.prompt is not None

    # dir>=0 cycles forward
    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', 1)

    assert ed.prompt.text == 'help '
    assert ed.prompt.suggestions == []


def test_prompt_complete_multiple_matches_starts_session_and_cycles() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.enter_prompt('command', prefill='s')
    assert ed.prompt is not None

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', 1)

    # multiple matches should create a suggestion session
    assert len(ed.prompt.suggestions) >= 2
    assert ed.prompt.suggest_base == 's'

    # ask for the suggestions via hostcall
    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-suggestions')
    suggs = ed.vm.pop_list()
    assert isinstance(suggs, list)
    assert len(suggs) == len(ed.prompt.suggestions)

    # next tab applies first suggestion
    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', 1)
    assert ed.prompt.text == ed.prompt.suggestions[0]

    # next tab cycles to next
    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', 1)
    assert ed.prompt.text == ed.prompt.suggestions[1]

    # shift-tab cycles backwards
    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', -1)
    assert ed.prompt.text == ed.prompt.suggestions[0]

    # clear suggestions
    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-clear-suggestions')
    assert ed.prompt.suggestions == []


def test_prompt_complete_fuzzy_unique_command_match_inserts() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.enter_prompt('command', prefill='sb')
    assert ed.prompt is not None

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', 1)

    assert ed.prompt.text == 'showbindings '
    assert ed.prompt.suggestions == []
    assert ed.messages and ed.messages[-1] == 'fuzzy: showbindings'


def test_prompt_complete_fuzzy_multiple_command_matches_start_session_and_cycle() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.enter_prompt('command', prefill='sk')
    assert ed.prompt is not None

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', 1)

    assert ed.prompt.suggestions[:2] == ['showkey ', 'showkeymodes ']
    assert ed.messages and ed.messages[-1].startswith('fuzzy matches: ')

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', 1)
    assert ed.prompt.text == 'showkey '

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', 1)
    assert ed.prompt.text == 'showkeymodes '


def test_prompt_complete_fuzzy_help_topic_prefers_camel_boundary_match() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.enter_prompt('command', prefill='help phn')
    assert ed.prompt is not None

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', 1)

    assert ed.prompt.suggestions[:2] == ['PromptHistoryNext ', 'pushkeymode-once ']
    assert ed.messages and ed.messages[-1].startswith('fuzzy matches: ')

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', 1)
    assert ed.prompt.text == 'help PromptHistoryNext '
    assert ed.prompt.suggest_index == 0


def test_prompt_complete_option_value_enum_unique_match_inserts() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.enter_prompt('command', prefill='set clipboard ex')
    assert ed.prompt is not None

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', 1)

    assert ed.prompt.text == 'set clipboard external '
    assert ed.prompt.suggestions == []


def test_prompt_complete_option_value_bool_starts_session_and_cycles() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.enter_prompt('command', prefill='set ignorecase ')
    assert ed.prompt is not None

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', 1)

    assert ed.prompt.suggestions == ['false ', 'true ']
    assert ed.prompt.suggest_base == 'set ignorecase '

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', 1)
    assert ed.prompt.text == 'set ignorecase false '

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', 1)
    assert ed.prompt.text == 'set ignorecase true '


def test_prompt_complete_keymode_name_unique_match_inserts() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.keymap.bind('g', 'CursorLeft', mode='goto')
    ed.keymap.bind('n', 'CursorDown', mode='nav')

    ed.enter_prompt('command', prefill='pushkeymode go')
    assert ed.prompt is not None

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', 1)

    assert ed.prompt.text == 'pushkeymode goto '
    assert ed.prompt.suggestions == []


def test_prompt_complete_showbindings_mode_includes_active_and_known_modes() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.keymap.bind('g', 'CursorLeft', mode='goto')
    ed.push_key_mode('nav', once=True)

    ed.enter_prompt('command', prefill='showbindings a')
    assert ed.prompt is not None

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', 1)
    assert ed.prompt.text == 'showbindings active '

    ed.enter_prompt('command', prefill='showbindings n')
    assert ed.prompt is not None

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', 1)
    assert ed.prompt.text == 'showbindings nav '


def test_prompt_complete_showhook_names() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval('hook ed.test.alpha hook ed.test.beta', filename='<test>')

    ed.enter_prompt('command', prefill='showhook ed.test.al')
    assert ed.prompt is not None

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', 1)

    assert ed.prompt.text == 'showhook ed.test.alpha '
    assert ed.prompt.suggestions == []


def test_prompt_complete_commandpick_topic_name_and_rows() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.enter_prompt('command', prefill='commandpick CommandP')
    assert ed.prompt is not None

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', 1)

    assert ed.prompt.text == 'commandpick CommandPalette '
    assert ed.prompt.suggestions == []


def test_prompt_complete_showword_name_and_rows() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval(
        ': prompt-word-demo ( x -- x ) ( demo word for prompt completion ) ;\n'
        ': prompt-word-delta ( x -- x ) ( second demo word for prompt completion ) ;',
        filename='<test>',
    )

    ed.enter_prompt('command', prefill='showword prompt-word-demo')
    assert ed.prompt is not None

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', 1)

    assert ed.prompt.text == 'showword prompt-word-demo '
    assert ed.prompt.suggestions == []

    ed.enter_prompt('command', prefill='showword prompt-word-d')
    assert ed.prompt is not None

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', 1)

    assert ed.prompt is not None
    assert len(ed.prompt.suggestions) >= 2

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-suggestion-rows')
    rows = ed.vm.pop_list()
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'prompt-word-demo ')
    assert row[1] == 'word'
    assert 'colon' in str(row[2])
    assert '( x -- x )' in str(row[2])
    assert 'demo word for prompt completion' in str(row[3])


def test_prompt_complete_bind_action_name_unique_match_inserts() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.enter_prompt('command', prefill='bind Ctrl-x CursorL')
    assert ed.prompt is not None

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', 1)

    assert ed.prompt.text == 'bind Ctrl-x CursorLeft '
    assert ed.prompt.suggestions == []


def test_prompt_complete_bind_command_action_completes_command_name() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.enter_prompt('command', prefill='bind Ctrl-x command:shst')
    assert ed.prompt is not None

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', 1)

    assert ed.prompt.text == 'bind Ctrl-x command:showstatus '
    assert ed.prompt.suggestions == []
    assert ed.messages and ed.messages[-1] == 'fuzzy: command:showstatus'


def test_prompt_complete_bind_command_action_argument_uses_command_completion() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.keymap.bind('g', 'CursorLeft', mode='goto')
    ed.push_key_mode('nav', once=True)

    ed.enter_prompt('command', prefill='bind Ctrl-x command:showbindings a')
    assert ed.prompt is not None

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', 1)

    assert ed.prompt.text == 'bind Ctrl-x command:showbindings active '
    assert ed.prompt.suggestions == []


def test_prompt_complete_bindmode_command_edit_action_completes_command_name() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.enter_prompt('command', prefill='bindmode nav Ctrl-x command-edit:he')
    assert ed.prompt is not None

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', 1)

    assert ed.prompt.text == 'bindmode nav Ctrl-x command-edit:help '
    assert ed.prompt.suggestions == []


def test_prompt_suggestion_rows_expose_command_docs() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.enter_prompt('command', prefill='s')
    assert ed.prompt is not None

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', 1)

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-suggestion-rows')
    rows = ed.vm.pop_list()
    assert isinstance(rows, list)
    assert rows
    row_by_insert = {str(r[0]): r for r in rows if isinstance(r, list) and len(r) >= 4}
    assert 'showstatus ' in row_by_insert
    assert row_by_insert['showstatus '][1] == 'command'
    assert 'portable statusline summary' in str(row_by_insert['showstatus '][2])


def test_prompt_suggestion_rows_expose_option_metadata() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.options.set('ignorecase', 'false')
    ed.enter_prompt('command', prefill='set i')
    assert ed.prompt is not None

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', 1)

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-suggestion-rows')
    rows = ed.vm.pop_list()
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'ignorecase ')
    assert row[1] == 'option'
    assert 'bool' in str(row[2])
    assert 'current=false' in str(row[2])


def test_prompt_suggestion_rows_expose_binding_rhs_command_docs() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.enter_prompt('command', prefill='bind Ctrl-x command:sh')
    assert ed.prompt is not None

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', 1)

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-suggestion-rows')
    rows = ed.vm.pop_list()
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'command:showstatus ')
    assert row[1] == 'binding-command'
    assert 'portable statusline summary' in str(row[2])
    assert row[3] == 'command'


def test_prompt_complete_apropos_topic_and_rows() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval(': apropos-prompt-demo ( x -- x ) ( demo word for apropos prompt ) ;\n        : apropos-prompt-delta ( x -- x ) ( second apropos prompt demo ) ;', filename='<test>')

    ed.enter_prompt('command', prefill='apropos apropos-prompt-dem')
    assert ed.prompt is not None

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', 1)

    assert ed.prompt.text == 'apropos apropos-prompt-demo '
    assert ed.prompt.suggestions == []

    ed.enter_prompt('command', prefill='apropos apropos-prompt-d')
    assert ed.prompt is not None

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', 1)

    assert ed.prompt is not None
    assert ed.prompt.suggestions

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-suggestion-rows')
    rows = ed.vm.pop_list()
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'apropos-prompt-demo ')
    assert row[1] == 'word'
    assert 'demo word for apropos prompt' in str(row[3])


def test_topic_prompt_submit_opens_best_matching_help_topic() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.enter_topic_prompt('visible micromax')
    assert ed.prompt is not None
    assert ed.prompt.kind == 'topic'
    assert ed.prompt.suggestions
    assert ed.prompt.suggestions[0] == 'showword'

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-submit')

    assert ed.prompt is None
    assert ed.messages
    assert ed.messages[-1].startswith('showword: showword NAME - show visible micromax word')


def test_topic_prompt_live_refreshes_on_prompt_set_and_exposes_current_row() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.enter_topic_prompt('visible mic')
    assert ed.prompt is not None
    assert ed.prompt.suggestions
    assert ed.prompt.suggestions[0] == 'showword'

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-current-row')
    row = ed.vm.pop_list()
    assert row[0] == 'showword'
    assert row[1] == 'command'
    assert 'show visible micromax word' in str(row[2])

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-set', 'macro rec')
    assert ed.prompt is not None
    assert ed.prompt.text == 'macro rec'
    assert ed.prompt.suggestions
    assert ed.prompt.suggestions[0] == 'macro'

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-current-row')
    row = ed.vm.pop_list()
    assert row[0] == 'macro'
    assert row[1] == 'command'
    assert 'keyboard macros' in str(row[2])


def test_topic_prompt_exposes_current_section_and_preview_hostcalls() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.enter_topic_prompt('visible micromax')
    assert ed.prompt is not None
    assert ed.prompt.suggestions

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-current-section')
    assert ed.vm.pop_str() == 'Command'

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-current-preview')
    preview = ed.vm.pop_str()
    assert preview.startswith('Command: showword')
    assert 'show visible micromax word' in preview


def test_topic_prompt_tab_cycles_ranked_topics_and_history_roundtrips() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.enter_topic_prompt('sh')
    assert ed.prompt is not None

    ed.prompt.set_cursor(len(ed.prompt.text))
    ed.prompt.clear_suggestions()

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', 1)
    assert ed.prompt.suggestions
    assert ed.messages and ed.messages[-1].startswith('topics: ')

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', 1)
    chosen = ed.prompt.text
    assert chosen in ('show ', 'showbindings', 'showcmd', 'showhook', 'showkey', 'showkeymodes', 'showstatus', 'showword') or chosen.startswith('show')

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-submit')
    assert ed.prompt is None

    ed.enter_topic_prompt()
    assert ed.prompt is not None
    assert ed.run_action('PromptHistoryPrev') is True
    assert ed.prompt.text.startswith('show')
