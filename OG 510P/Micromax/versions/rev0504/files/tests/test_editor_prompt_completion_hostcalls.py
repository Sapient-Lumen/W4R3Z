import json
from pathlib import Path

from micromax.vm import Span

from micromax_editor.commandbar import Prompt
from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.plugins import PluginManager


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

    ed.enter_prompt('command', prefill='sst')
    assert ed.prompt is not None

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', 1)

    assert ed.prompt.text == 'showstatus '
    assert ed.prompt.suggestions == []
    assert ed.messages and ed.messages[-1] == 'fuzzy: showstatus'


def test_prompt_complete_fuzzy_sb_now_starts_binding_show_session() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.enter_prompt('command', prefill='sb')
    assert ed.prompt is not None

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', 1)

    assert ed.prompt.text == 'sb'
    assert ed.prompt.suggestions[:4] == ['showbuffer ', 'showbindings ', 'showbindingmodes ', 'showbuffergroups ']
    assert ed.messages and ed.messages[-1] == 'fuzzy matches: showbuffer, showbindings, showbindingmodes, showbuffergroups'


def test_prompt_complete_fuzzy_multiple_command_matches_start_session_and_cycle() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.enter_prompt('command', prefill='sk')
    assert ed.prompt is not None

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', 1)

    assert ed.prompt.suggestions[:3] == ['showkey ', 'showkeymode ', 'showkeymodes ']
    assert ed.messages and ed.messages[-1].startswith('fuzzy matches: ')

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', 1)
    assert ed.prompt.text == 'showkey '

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', 1)
    assert ed.prompt.text == 'showkeymode '


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


def test_prompt_complete_showkeymode_names() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')

    ed.vm.eval('"nav" "x" "command:help" "ed.bind-mode" hostcall', filename='<nav-bind>')
    ed.push_key_mode('prompt', once=True, capture=True)

    ed.enter_prompt('command', prefill='showkeymode p')
    assert ed.prompt is not None

    ed.prompt.set_cursor(len(ed.prompt.text))
    ed.prompt.clear_suggestions()

    _hostcall(ed, 'ed.prompt-complete', 1)
    assert ed.prompt.text == 'showkeymode prompt '
    assert ed.prompt.suggestions == []


def test_prompt_complete_showkeymode_uses_exact_keymode_metadata() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')

    ed.vm.eval('"nav" "x" "command:help" "ed.bind-mode" hostcall', filename='<nav-bind>')
    ed.vm.eval('"goto" "g" "command:showstatus" "ed.bind-mode" hostcall', filename='<goto-bind>')
    ed.push_key_mode('prompt', once=True, capture=True)

    ed.enter_prompt('command', prefill='showkeymode g')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'goto ')
    assert row[1] == 'keymode'
    assert row[2] == 'known bindings=1'
    assert row[3] == 'g->command:showstatus (show portable statusline summary)'

    row = ed._prompt_keymode_row('prompt ')
    assert row[1] == 'keymode'
    assert row[2].startswith('active internal bindings=')
    assert row[3]


def test_prompt_complete_showbindings_mode_uses_exact_keymode_metadata() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')

    ed.vm.eval('"nav" "x" "command:help" "ed.bind-mode" hostcall', filename='<nav-bind>')
    ed.vm.eval('"goto" "g" "command:showstatus" "ed.bind-mode" hostcall', filename='<goto-bind>')
    assert ed.exec_command_line('pushkeymode nav')

    ed.enter_prompt('command', prefill='showbindings g')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'goto ')
    assert row[1] == 'keymode'
    assert row[2] == 'known bindings=1'
    assert row[3] == 'g->command:showstatus (show portable statusline summary)'

def test_prompt_complete_showhook_names() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval(
        '\n'.join([
            'hook ed.test.alpha',
            '"cfg" hook-group!',
            ': h1 drop ;',
            "' h1 hook-add ed.test.alpha",
            '0 hook-group!',
            'hook ed.test.beta',
        ]),
        filename='<test>',
    )

    ed.enter_prompt('command', prefill='showhook ed.test.al')
    assert ed.prompt is not None

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', 1)

    assert ed.prompt.text == 'showhook ed.test.alpha '
    assert ed.prompt.suggestions == []

    ed.enter_prompt('command', prefill='showhook ')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'ed.test.alpha ')
    assert row[1] == 'hook'
    assert row[2] == '1 handler (e.g. h1#cfg)'
    assert row[3] == 'h1#cfg@<test>:4:6'


def test_prompt_complete_showhooks_names() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval(
        '\n'.join([
            'hook ed.test.alpha',
            'hook ed.test.beta',
            '"cfg" hook-group!',
            ': h1 drop ;',
            "' h1 hook-add ed.test.alpha",
            '0 hook-group!',
        ]),
        filename='<test>',
    )

    ed.enter_prompt('command', prefill='showhooks ed.test.al')
    assert ed.prompt is not None

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', 1)

    assert ed.prompt.text == 'showhooks ed.test.alpha '
    assert ed.prompt.suggestions == []

    ed.enter_prompt('command', prefill='showhooks ')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'ed.test.alpha ')
    assert row[1] == 'hook'
    assert row[2] == '1 handler (e.g. h1#cfg)'
    assert row[3] == 'defined at <test>:1:1'


def test_prompt_complete_commandpick_topic_name_and_rows() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.enter_prompt('command', prefill='commandpick CommandP')
    assert ed.prompt is not None

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-complete', 1)

    assert ed.prompt.text == 'commandpick CommandPalette '
    assert ed.prompt.suggestions == []


def test_prompt_complete_commandpick_rows_keep_exact_command_metadata() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.command_dispatcher.register(
        'palette-demo',
        lambda _ed, _args: True,
        doc='demo palette command',
        group='demo',
        span=Span('<palette-command>', 1, 51),
    )
    ed.command_dispatcher.register(
        'palette-delta',
        lambda _ed, _args: True,
        doc='second palette command',
        group='demo',
        span=Span('<palette-command>', 2, 51),
    )

    ed.enter_prompt('command', prefill='commandpick palette-d')
    assert ed.prompt is not None
    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'palette-demo ')
    assert row[1] == 'command'
    assert row[2] == 'demo palette command'
    assert str(row[3]).startswith('command palette')
    assert 'group demo' in str(row[3])
    assert 'defined at <palette-command>:' in str(row[3])


def test_prompt_complete_commandpick_rows_keep_exact_action_metadata() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    def palette_action(_ed: Editor) -> bool:
        return True

    def palette_action_more(_ed: Editor) -> bool:
        return True

    ed.actions.register('PaletteActionDemo', palette_action, doc='demo palette action')
    ed.actions.register('PaletteActionDelta', palette_action_more, doc='second palette action')

    ed.enter_prompt('command', prefill='commandpick PaletteActionD')
    assert ed.prompt is not None
    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'PaletteActionDemo ')
    assert row[1] == 'action'
    assert row[2] == 'demo palette action'
    assert str(row[3]).startswith('command palette')
    assert 'defined at tests/test_editor_prompt_completion_hostcalls.py:' in str(row[3])


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
    assert 'defined at <test>:1:1' in str(row[3])


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
    assert 'defined at <test>:1:1' in str(row[3])
    assert str(row[3]).startswith('search topic · ')


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
    assert ed.vm.pop_str() == 'Commands'

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-current-preview')
    preview = ed.vm.pop_str()
    assert preview.startswith('Commands: showword')
    assert 'show visible micromax word' in preview



def test_topic_prompt_exposes_current_position_hostcall() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.enter_topic_prompt('visible micromax')
    assert ed.prompt is not None
    assert ed.prompt.suggestions

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-current-position')
    pos = ed.vm.pop_map()
    assert pos['index'] == 1
    assert pos['count'] >= 1
    assert pos['section'] == 'Commands'
    assert pos['section_index'] >= 1
    assert pos['section_count'] >= pos['section_index']
    assert str(pos['summary']).startswith('1/')
    assert 'Commands' in str(pos['summary'])




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
    assert chosen in ('show ', 'showbindings', 'showcmd', 'showhook', 'showkey', 'showkeymode', 'showkeymodes', 'showstatus', 'showword') or chosen.startswith('show')

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-submit')
    assert ed.prompt is None

    ed.enter_topic_prompt()
    assert ed.prompt is not None
    assert ed.run_action('PromptHistoryPrev') is True
    assert ed.prompt.text.startswith('show')



def test_navigation_section_row_hostcalls_expose_mark_and_jump_groups() -> None:
    from micromax_editor.buffer import Cursor

    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'one\ntwo\n')
    ed.new_buffer('b', 'zzz\n')

    ed.switch_buffer('a')
    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    eb.cursors[eb.primary] = eb.buf.clamp(Cursor(0, 0))
    assert ed.mark_set('alpha')

    ed.switch_buffer('b')
    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    eb.cursors[eb.primary] = eb.buf.clamp(Cursor(0, 0))
    assert ed.mark_set('beta')

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.mark-section-rows', '')
    mark_sections = ed.vm.pop_list()
    assert [sec[0] for sec in mark_sections] == ['b', 'a']
    ed.vm.stack.clear()
    _hostcall(ed, 'ed.mark-section-summary-rows', '')
    mark_summaries = ed.vm.pop_list()
    assert mark_summaries == [
        ['b', 1, 'beta', 'zzz'],
        ['a', 1, 'alpha', 'one'],
    ]
    ed.vm.stack.clear()
    _hostcall(ed, 'ed.mark-inventory-rows')
    mark_inventory = ed.vm.pop_list()
    assert mark_inventory == [
        ['alpha', 'a', '1:0', 'one', 0, 0],
        ['beta', 'b', '1:0', 'zzz', 1, 1],
    ]

    assert ed.push_jump() is True
    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    eb.cursors[eb.primary] = eb.buf.clamp(Cursor(0, 1))
    assert ed.push_jump() is True
    eb.cursors[eb.primary] = eb.buf.clamp(Cursor(0, 2))
    assert ed.push_jump() is True
    assert ed.jump_to_index(1) is True

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.jump-section-rows', '')
    jump_sections = ed.vm.pop_list()
    assert [sec[0] for sec in jump_sections] == ['Current', 'Back', 'Forward']
    ed.vm.stack.clear()
    _hostcall(ed, 'ed.jump-history-rows')
    jump_history = ed.vm.pop_list()
    assert jump_history == [
        ['current', 0, 2, 'b', '1:1', 'zzz'],
        ['back', 1, 1, 'b', '1:0', 'zzz'],
        ['forward', 1, 3, 'b', '1:2', 'zzz'],
    ]



def test_palette_prompt_exposes_current_section_and_preview_hostcalls() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.enter_command_palette('status')
    assert ed.prompt is not None
    assert ed.prompt.suggestions

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-current-section')
    assert ed.vm.pop_str() == 'Commands'

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-current-preview')
    preview = ed.vm.pop_str()
    assert preview.startswith('Commands: showstatus')
    assert 'portable statusline summary' in preview


def test_palette_prompt_exposes_current_position_hostcall() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.enter_command_palette('status')
    assert ed.prompt is not None
    assert ed.prompt.suggestions

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-current-position')
    pos = ed.vm.pop_map()
    assert pos['index'] == 1
    assert pos['count'] >= 1
    assert pos['section'] == 'Commands'
    assert pos['section_index'] >= 1
    assert pos['section_count'] >= pos['section_index']
    assert str(pos['summary']).startswith('1/')
    assert 'Commands' in str(pos['summary'])


def test_prompt_window_hostcall_exposes_shared_picker_window_metadata() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    p = Prompt(kind="helplink")
    rows: list[list[str]] = []
    rows.append(["Docs link 1", "link", "help:vision", ""])
    rows.append(["Docs link 2", "link", "help:help-browser", ""])
    rows.append(["File link 1", "link", "docs/00-vision.md", ""])
    rows.append(["File link 2", "link", "docs/98-help-browser.md", ""])
    for i in range(20):
        rows.append([f"External {i}", "link", f"https://example.com/{i}", ""])
    p.suggestion_rows = rows
    p.suggestions = [r[0] for r in rows]
    p.suggest_index = 14
    ed.prompt = p

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-window', 5)
    win = ed.vm.pop_map()
    assert win['kind'] == 'helplink'
    assert win['max_lines'] == 5
    assert win['show_top'] == 1
    assert win['show_bottom'] == 1
    assert win['sticky_section'] == 'External'
    entries = win['entries']
    assert entries[0]['type'] == 'more'
    assert entries[0]['direction'] == 'up'
    assert entries[1]['type'] == 'sticky'
    assert entries[1]['label'] == 'External'
    assert any(ent.get('type') == 'row' and ent.get('selected') == 1 for ent in entries)


def test_prompt_display_hostcall_exposes_shared_rendered_rows() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.enter_command_palette('status')

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.prompt-display', 6, 80)
    rows = ed.vm.pop()

    assert isinstance(rows, list)
    assert rows
    assert rows[0]['type'] == 'header'
    assert rows[0]['section_label'] == 'Commands'
    row = next(r for r in rows if isinstance(r, dict) and r.get('type') == 'row')
    assert row['row_kind'] == 'command'
    assert row['section_label'] == 'Commands'
    assert row['text'].startswith('> ')
    assert row['row'][0] == 'showstatus'


def test_prompt_complete_showoption_uses_exact_option_metadata() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')
    ed.exec_command_line('setlocal readonly true')

    ed.enter_prompt('command', prefill='showoption saveh')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == 'showoption savehistory '

    ed.enter_prompt('command', prefill='showoption re')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'readonly ')
    assert row[1] == 'option'
    assert row[2] == 'bool value=true (local)'
    assert row[3] == 'disallow edits and saves in the current buffer unless locally overridden'




def test_prompt_complete_showplugin_uses_exact_plugin_metadata(tmp_path: Path) -> None:
    root = tmp_path / 'plugins'
    root.mkdir()

    a = root / 'a'
    a.mkdir()
    (a / 'main.mx').write_text(': init ( -- ) ;\n', encoding='utf-8')
    (a / 'plugin.json').write_text(
        json.dumps({'entry': 'main.mx', 'version': '1.0.0', 'description': 'demo plugin'}),
        encoding='utf-8',
    )

    b = root / 'b'
    b.mkdir()
    (b / 'main.mx').write_text(': init ( -- ) ;\n', encoding='utf-8')
    (b / 'plugin.json').write_text(json.dumps({'entry': 'main.mx', 'requires': ['missingdep']}), encoding='utf-8')

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)

    ed.enter_prompt('command', prefill='showplugin a')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == 'showplugin a '

    ed.enter_prompt('command', prefill='showplugin ')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'b ')
    assert row[1] == 'plugin'
    assert row[2] == '[error, deps:missingdep] errors=1'
    assert row[3] == 'missing dependency: missingdep'


def test_prompt_complete_showbuffer_uses_exact_buffer_metadata(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    p = tmp_path / 'proj' / 'demo.txt'
    q = tmp_path / 'proj' / 'delta.txt'
    p.parent.mkdir(parents=True)
    p.write_text('demo\nsecond\n', encoding='utf-8')
    q.write_text('delta\n', encoding='utf-8')
    ed.open_file(str(p))
    ed.open_file(str(q))

    ed.enter_prompt('command', prefill=f'showbuffer {tmp_path / "proj" / "demo"}')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == f'showbuffer {p} '

    ed.enter_prompt('command', prefill=f'showbuffer {tmp_path / "proj" / "d"}')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == f'{p} ')
    assert row[1] == 'buffer'
    assert row[2] == f'{tmp_path / "proj"} @ 1:0'
    assert row[3] == f'{p} | 3 lines'


def test_prompt_complete_buffer_uses_exact_buffer_metadata(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    p = tmp_path / 'proj' / 'demo.txt'
    q = tmp_path / 'proj' / 'delta.txt'
    p.parent.mkdir(parents=True)
    p.write_text('demo\nsecond\n', encoding='utf-8')
    q.write_text('delta\n', encoding='utf-8')
    ed.open_file(str(p))
    ed.open_file(str(q))
    ed.switch_buffer(str(p))
    ed.cur().buf.dirty = True

    ed.enter_prompt('command', prefill=f'buffer {tmp_path / "proj" / "d"}')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == f'{p} ')
    assert row[1] == 'buffer'
    assert row[2] == f'{tmp_path / "proj"} [active, dirty] @ 1:0'
    assert row[3] == f'{p} | 3 lines'


def test_prompt_complete_showrecent_uses_exact_recent_metadata(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line('set cap.fs-list true')

    (tmp_path / 'pyproject.toml').write_text('[project]\nname = "demo"\n', encoding='utf-8')
    p = tmp_path / 'proj' / 'demo.txt'
    q = tmp_path / 'proj' / 'delta.txt'
    p.parent.mkdir(parents=True)
    p.write_text('demo\n', encoding='utf-8')
    q.write_text('delta\n', encoding='utf-8')
    ed.open_file(str(p))
    ed.open_file(str(q))

    ed.enter_prompt('command', prefill=f'showrecent {tmp_path / "proj" / "demo"}')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == f'showrecent {p} '

    ed.enter_prompt('command', prefill=f'showrecent {tmp_path / "proj" / "d"}')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == f'{p} ')
    assert row[1] == 'recent'
    assert row[2] == f'#2 {tmp_path}'
    assert row[3] == 'proj/demo.txt | existing file | switch buffer'


def test_prompt_complete_showrecentdir_uses_exact_recent_directory_metadata(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line('set cap.fs-list true')

    a = tmp_path / 'proj' / 'src' / 'a.txt'
    b = tmp_path / 'proj' / 'tests' / 'b.txt'
    c = tmp_path / 'proj' / 'tests' / 'c.txt'
    a.parent.mkdir(parents=True)
    b.parent.mkdir(parents=True)
    a.write_text('a\n', encoding='utf-8')
    b.write_text('b\n', encoding='utf-8')
    c.write_text('c\n', encoding='utf-8')
    ed.open_file(str(a))
    ed.open_file(str(b))
    ed.open_file(str(c))

    ed.enter_prompt('command', prefill=f'showrecentdir {tmp_path / "proj" / "te"}')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == f'showrecentdir {b.parent} '

    ed.enter_prompt('command', prefill=f'showrecentdir {tmp_path / "proj"}')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == f'{b.parent} ')
    assert row[1] == 'recentdir'
    assert row[2] == '2 files [active, open=2]'
    assert row[3] == f'c.txt #1 [active] @ 1:0 | {b.parent} | existing file | current buffer'


def test_prompt_complete_showtopics_uses_topic_section_summary_metadata() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.enter_prompt('command', prefill='showtopics Doc')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == 'showtopics Docs '

    ed.enter_prompt('command', prefill='showtopics ')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'Commands ')
    assert row[1] == 'topic-group'
    assert 'topic' in str(row[2]) and '(e.g. ' in str(row[2])
    assert str(row[3])


def test_prompt_complete_showoptiongroups_uses_option_section_summary_metadata() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')

    ed.enter_prompt('command', prefill='showoptiongroups Capa')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == 'showoptiongroups Capabilities '

    ed.enter_prompt('command', prefill='showoptiongroups ')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'Capabilities ')
    assert row[1] == 'option-group'
    assert 'option' in str(row[2]) and '(e.g. ' in str(row[2])
    assert str(row[3])


def test_prompt_complete_showbuffergroups_uses_buffer_section_summary_metadata(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('help:guide', 'guide')
    ed.new_buffer('*notes*', 'notes')

    p = tmp_path / 'proj' / 'file.txt'
    p.parent.mkdir(parents=True)
    p.write_text('file', encoding='utf-8')
    ed.open_file(str(p))

    ed.enter_prompt('command', prefill='showbuffergroups He')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == 'showbuffergroups Help '

    ed.enter_prompt('command', prefill='showbuffergroups ')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'Help ')
    assert row[1] == 'buffer-group'
    assert row[2] == '1 buffer (e.g. help:guide)'
    assert row[3] == '1 lines'



def test_prompt_complete_showrecentgroups_and_showrecentdirgroups_reuse_section_summary_metadata(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    (tmp_path / 'pyproject.toml').write_text('[project]\nname = "demo"\n', encoding='utf-8')
    other_root = tmp_path / 'otherroot'
    other_root.mkdir(parents=True)
    (other_root / 'pyproject.toml').write_text('[project]\nname = "other"\n', encoding='utf-8')
    a = tmp_path / 'proj' / 'src' / 'a.txt'
    b = tmp_path / 'proj' / 'tests' / 'b.txt'
    c = tmp_path / 'proj' / 'tests' / 'c.txt'
    d = other_root / 'docs' / 'd.txt'
    a.parent.mkdir(parents=True)
    b.parent.mkdir(parents=True)
    d.parent.mkdir(parents=True)
    a.write_text('a\n', encoding='utf-8')
    b.write_text('b\n', encoding='utf-8')
    c.write_text('c\n', encoding='utf-8')
    d.write_text('d\n', encoding='utf-8')
    ed.open_file(str(a))
    ed.open_file(str(b))
    ed.open_file(str(c))
    ed.open_file(str(d))

    ed.enter_prompt('command', prefill=f'showrecentgroups {str(other_root)[:-1]}')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == f'showrecentgroups {other_root} '

    ed.enter_prompt('command', prefill='showrecentgroups ')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == f'{tmp_path} ')
    assert row[1] == 'recent-group'
    assert row[2] == f'3 files (e.g. {a})'
    assert row[3] == 'proj/src/a.txt'

    ed.enter_prompt('command', prefill=f'showrecentdirgroups {tmp_path / "proj" / "te"}')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == f'showrecentdirgroups {b.parent} '

    ed.enter_prompt('command', prefill=f'showrecentdirgroups {tmp_path / "proj"}')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == f'{b.parent} ')
    assert row[1] == 'recentdir-group'
    assert row[2] == f'2 files (e.g. {b})'
    assert row[3] == str(b.parent)



def test_prompt_complete_showplugins_uses_plugin_section_summary_metadata(tmp_path: Path) -> None:
    root = tmp_path / 'plugins'
    root.mkdir()

    for name in ('alpha', 'amber'):
        d = root / name
        d.mkdir()
        (d / 'main.mx').write_text(': init ( -- ) ;\n', encoding='utf-8')
        (d / 'plugin.json').write_text(json.dumps({'entry': 'main.mx'}), encoding='utf-8')

    broken = root / 'beta'
    broken.mkdir()
    (broken / 'main.mx').write_text(': init ( -- ) ;\n', encoding='utf-8')
    (broken / 'plugin.json').write_text(json.dumps({'entry': 'main.mx', 'requires': ['missingdep']}), encoding='utf-8')

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)

    ed.enter_prompt('command', prefill='showplugins Loa')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == 'showplugins Loaded '

    ed.enter_prompt('command', prefill='showplugins ')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'Loaded ')
    assert row[1] == 'plugin-group'
    assert row[2] == '2 plugins (e.g. alpha)'
    assert row[3] == '[loaded]'


def test_prompt_complete_showpalettegroups_uses_palette_section_summary_metadata() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    assert ed.exec_command_line('commandpick status') is True
    assert ed.submit_prompt() is True
    assert ed.prompt is not None
    assert ed.prompt.kind == 'command'
    ed.cancel_prompt()

    ed.enter_prompt('command', prefill='showpalettegroups Com')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == 'showpalettegroups Commands '

    ed.enter_prompt('command', prefill='showpalettegroups ')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'Commands ')
    assert row[1] == 'palette-group'
    assert 'item' in str(row[2]) and '(e.g. ' in str(row[2])
    assert str(row[3])


def test_prompt_complete_showhelpnav_uses_helpnav_section_summary_metadata() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    assert ed.open_help_doc('help-browser') is True

    ed.enter_prompt('command', prefill='showhelpnav Fi')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == 'showhelpnav Files '

    ed.enter_prompt('command', prefill='showhelpnav ')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'Files ')
    assert row[1] == 'helpnav-group'
    assert 'target' in str(row[2]) and '(e.g. ' in str(row[2])
    assert ':' in str(row[3])


def test_prompt_complete_showdocs_uses_doc_section_summary_metadata() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.enter_prompt('command', prefill='showdocs 100')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == 'showdocs 100+ Feature notes '

    ed.enter_prompt('command', prefill='showdocs ')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == '00–09 Project ')
    assert row[1] == 'doc-group'
    assert 'doc' in str(row[2]) and '(e.g. ' in str(row[2])
    assert str(row[3])


def test_prompt_complete_showbindingmodes_uses_binding_section_summary_metadata() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval('"Ctrl-z" "command:help" "ed.bind" hostcall', filename='<global-bind>')
    ed.vm.eval('"nav" "Ctrl-x" "command:quit" "ed.bind-mode" hostcall', filename='<nav-bind>')
    ed.vm.eval('"goto" "Ctrl-g" "command:showstatus" "ed.bind-mode" hostcall', filename='<goto-bind>')

    _hostcall(ed, 'ed.keymode-push', 'nav')
    _hostcall(ed, 'ed.keymode-push-once', 'goto')

    ed.enter_prompt('command', prefill='showbindingmodes Gl')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == 'showbindingmodes Global '

    ed.enter_prompt('command', prefill='showbindingmodes ')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'goto ')
    assert row[1] == 'bindingmode-group'
    assert row[2] == '1 binding (e.g. Ctrl-g)'
    assert row[3] == 'show portable statusline summary'


def test_prompt_complete_showmarkgroups_uses_mark_section_summary_metadata() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('alpha', 'zero\n  target  \n')
    ed._normalize_cursor_lists(ed.cur())
    ed.cur().cursors[ed.cur().primary].line = 1
    ed.cur().cursors[ed.cur().primary].col = 0
    assert ed.mark_set('here') is True
    assert ed.mark_set('home') is True

    ed.new_buffer('beta', 'other\n')
    ed._normalize_cursor_lists(ed.cur())
    ed.cur().cursors[ed.cur().primary].line = 0
    ed.cur().cursors[ed.cur().primary].col = 0
    assert ed.mark_set('there') is True

    ed.enter_prompt('command', prefill='showmarkgroups al')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == 'showmarkgroups alpha '

    ed.enter_prompt('command', prefill='showmarkgroups ')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'alpha ')
    assert row[1] == 'mark-group'
    assert row[2] == '2 marks (e.g. here)'
    assert row[3] == 'target'


def test_prompt_complete_showmark_uses_exact_mark_metadata() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer("alpha", "zero\n  target  \n")
    ed._normalize_cursor_lists(ed.cur())
    ed.cur().cursors[ed.cur().primary].line = 1
    ed.cur().cursors[ed.cur().primary].col = 0
    assert ed.mark_set("here") is True
    assert ed.mark_set("home") is True

    ed.enter_prompt('command', prefill='showmark he')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == 'showmark here '

    ed.enter_prompt('command', prefill='showmark h')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'here ')
    assert row[1] == 'mark'
    assert row[2] == 'alpha [active, here]'
    assert row[3] == 'target'


def test_prompt_complete_mark_and_markjump_reuse_exact_mark_metadata() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer("alpha", "zero\n  target  \n")
    ed._normalize_cursor_lists(ed.cur())
    ed.cur().cursors[ed.cur().primary].line = 1
    ed.cur().cursors[ed.cur().primary].col = 0
    assert ed.mark_set("here") is True
    assert ed.mark_set("home") is True

    ed.enter_prompt('command', prefill='markjump h')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'here ')
    assert row[1] == 'mark'
    assert row[2] == 'alpha [active, here]'
    assert row[3] == 'target'

    ed.enter_prompt('command', prefill='mark h')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'here ')
    assert row[1] == 'mark'
    assert row[2] == 'alpha [active, here]'
    assert row[3] == 'target'

def test_prompt_complete_showjump_uses_exact_jump_metadata() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'one\ntwo\nthree\n')
    ed._normalize_cursor_lists(ed.cur())
    ed.cur().cursors[ed.cur().primary].line = 0
    ed.cur().cursors[ed.cur().primary].col = 0
    assert ed.push_jump() is True
    ed.cur().cursors[ed.cur().primary].line = 1
    ed.cur().cursors[ed.cur().primary].col = 1
    assert ed.push_jump() is True
    ed.cur().cursors[ed.cur().primary].line = 2
    ed.cur().cursors[ed.cur().primary].col = 2
    assert ed.push_jump() is True
    assert ed.jump_to_index(1) is True

    ed.enter_prompt('command', prefill='showjump ')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == '1 ')
    assert row[1] == 'jump'
    assert row[2] == 'back 1 a @ 1:0'
    assert row[3] == 'one'


def test_prompt_complete_helpjump_uses_exact_heading_metadata() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.open_help_doc('helpoutline-section-groups') is True

    ed.enter_prompt('command', prefill='helpjump Guide L')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == 'helpjump Guide Links '

    ed_frag = Editor()
    install_editor_hostcalls(ed_frag)
    assert ed_frag.open_help_doc('help-browser') is True

    ed_frag.enter_prompt('command', prefill='helpjump custom-')
    assert ed_frag.prompt is not None

    assert ed_frag.prompt_complete(direction=1)
    assert ed_frag.prompt.text == 'helpjump custom-frag '

    ed_frag.enter_prompt('command', prefill='helpjump ')
    assert ed_frag.prompt is not None

    assert ed_frag.prompt_complete(direction=1)
    rows = ed_frag.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'custom-frag ')
    assert row[1] == 'heading'
    assert row[2] == 'Explicit fragment target [h2] [#custom-frag]'
    assert 'Help browser @ ' in row[3]


def test_prompt_complete_showkey_names() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.keymap.bind('Ctrl-g', 'command:showstatus')
    ed.keymap.bind('Ctrl-x', 'command:quit')

    ed.enter_prompt('command', prefill='showkey Ctrl-g')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == 'showkey Ctrl-g '


def test_prompt_complete_showkey_uses_exact_binding_metadata() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.keymap.bind('Ctrl-g', 'command:showstatus', group='nav')
    ed.keymap.bind('Ctrl-x', 'command:quit')

    ed.enter_prompt('command', prefill='showkey Ctrl-')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'Ctrl-g ')
    assert row[1] == 'binding'
    assert row[2] == '@global command:showstatus [group nav]'
    assert row[3] == 'show portable statusline summary'


def test_prompt_complete_showaction_uses_action_metadata() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    def demo_action(_ed: Editor) -> bool:
        return True

    def demo_action_more(_ed: Editor) -> bool:
        return True

    ed.actions.register('DemoAction', demo_action, doc='demo action')
    ed.actions.register('DemoActionMore', demo_action_more, doc='demo action sibling')

    ed.enter_prompt('command', prefill='showaction DemoA')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'DemoAction ')
    assert row[1] == 'action'
    assert row[2] == 'demo action'
    assert 'defined at tests/test_editor_prompt_completion_hostcalls.py:' in str(row[3])


def test_prompt_complete_help_showtopic_and_apropos_action_topics_keep_provenance() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    def topic_action(_ed: Editor) -> bool:
        return True

    def topic_action_more(_ed: Editor) -> bool:
        return True

    ed.actions.register('TopicActionDemo', topic_action, doc='demo topic action')
    ed.actions.register('TopicActionDelta', topic_action_more, doc='demo sibling action')

    ed.enter_prompt('command', prefill='help TopicActionD')
    assert ed.prompt is not None
    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'TopicActionDemo ')
    assert row[1] == 'action'
    assert row[2] == 'demo topic action'
    assert 'defined at tests/test_editor_prompt_completion_hostcalls.py:' in str(row[3])

    ed.enter_prompt('command', prefill='showtopic TopicActionD')
    assert ed.prompt is not None
    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'TopicActionDemo ')
    assert row[1] == 'action'
    assert row[2] == 'demo topic action'
    assert 'defined at tests/test_editor_prompt_completion_hostcalls.py:' in str(row[3])

    ed.enter_prompt('command', prefill='apropos TopicActionD')
    assert ed.prompt is not None
    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'TopicActionDemo ')
    assert row[1] == 'action'
    assert row[2] == 'demo topic action'
    assert str(row[3]).startswith('search topic')
    assert 'defined at tests/test_editor_prompt_completion_hostcalls.py:' in str(row[3])


def test_prompt_complete_help_and_showtopic_command_topics_use_exact_command_metadata() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.command_dispatcher.register(
        'topic-demo',
        lambda _ed, _args: True,
        doc='demo topic command',
        group='demo',
        span=Span('<topic-help>', 1, 51),
    )
    ed.command_dispatcher.register(
        'topic-demo-more',
        lambda _ed, _args: True,
        doc='demo sibling command',
        group='demo',
        span=Span('<topic-help>', 2, 51),
    )

    ed.enter_prompt('command', prefill='help topic-demo')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'topic-demo ')
    assert row[1] == 'command'
    assert row[2] == 'demo topic command'
    assert 'group demo' in str(row[3])
    assert 'defined at <topic-help>:' in str(row[3])

    ed.enter_prompt('command', prefill='showtopic topic-demo')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'topic-demo ')
    assert row[1] == 'command'
    assert row[2] == 'demo topic command'
    assert 'group demo' in str(row[3])
    assert 'defined at <topic-help>:' in str(row[3])


def test_prompt_complete_apropos_command_topics_keep_exact_command_metadata() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.command_dispatcher.register(
        'apropos-cmd-demo',
        lambda _ed, _args: True,
        doc='demo apropos command',
        group='demo',
        span=Span('<apropos-help>', 1, 51),
    )
    ed.command_dispatcher.register(
        'apropos-cmd-delta',
        lambda _ed, _args: True,
        doc='second apropos command',
        group='demo',
        span=Span('<apropos-help>', 2, 51),
    )

    ed.enter_prompt('command', prefill='apropos apropos-cmd-d')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'apropos-cmd-demo ')
    assert row[1] == 'command'
    assert row[2] == 'demo apropos command'
    assert str(row[3]).startswith('search topic')
    assert 'group demo' in str(row[3])
    assert 'defined at <apropos-help>:' in str(row[3])


def test_prompt_complete_showcmd_uses_exact_command_metadata() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval(': demo-showcmd ( args -- ok ) drop 1 ;', filename='<showcmd-test>')
    ed.vm.eval(': demo-showcmd-more ( args -- ok ) drop 1 ;', filename='<showcmd-test>')
    ed.vm.eval("' demo-showcmd \"demo\" \"demo command\" \"ed.cmd-add\" hostcall", filename='<showcmd-test>')
    ed.vm.eval("' demo-showcmd-more \"demonstrate\" \"demo sibling command\" \"ed.cmd-add\" hostcall", filename='<showcmd-test>')

    ed.enter_prompt('command', prefill='showcmd demo')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'demo ')
    assert row[1] == 'command'
    assert row[2] == 'demo command'
    assert 'group' not in str(row[2])
    assert 'defined at <showcmd-test>:' in str(row[3])


def test_prompt_complete_showdoc_and_help_docs_use_doc_metadata() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.enter_prompt('command', prefill='showdoc visi')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == 'showdoc vision '

    ed.enter_prompt('command', prefill='help docs visi')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == 'help docs vision '

    ed.enter_prompt('command', prefill='showdoc m')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[1] == 'doc')
    assert row[2]
    assert ':' in str(row[3])
    assert 'docs/' in str(row[3])
    assert 'inspect doc' not in str(row[3])


def test_prompt_complete_showtopic_uses_generic_topic_metadata() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval(
        ': prompt-topic-demo ( x -- x ) ( demo word for showtopic completion ) ;\n'
        ': prompt-topic-delta ( x -- x ) ( second demo word for showtopic completion ) ;',
        filename='<prompt-topic>',
    )

    ed.enter_prompt('command', prefill='showtopic visi')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == 'showtopic vision '

    ed.enter_prompt('command', prefill='showtopic prompt-topic-d')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    assert ed.prompt is not None
    assert len(ed.prompt.suggestions) >= 2

    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'prompt-topic-demo ')
    assert row[1] == 'word'
    assert '( x -- x )' in str(row[2])
    assert 'showtopic completion' in str(row[3])
    assert 'defined at <prompt-topic>:1:1' in str(row[3])


def test_prompt_complete_help_and_apropos_include_doc_topics() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.enter_prompt('command', prefill='help v')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    row = next(r for r in ed.prompt.suggestion_rows if isinstance(r, list) and r and r[0] == 'vision ')
    assert row[1] == 'doc'
    assert row[2] == 'Vision'
    assert str(row[3]).startswith('00–09 Project: **Micromax** is a small, embeddable')
    assert 'docs/00-vision.md' in str(row[3])

    ed.enter_prompt('command', prefill='apropos v')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    row = next(r for r in ed.prompt.suggestion_rows if isinstance(r, list) and r and r[0] == 'vision ')
    assert row[1] == 'doc'
    assert row[2] == 'Vision'
    assert str(row[3]).startswith('search topic · 00–09 Project: **Micromax** is a small, embeddable')
    assert 'docs/00-vision.md' in str(row[3])
