import json
from pathlib import Path

from micromax.vm import Span

from micromax_editor.commandbar import Prompt
from micromax_editor.editor import Editor, MacroStep
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


def test_prompt_complete_showkeymode_command_previews_live_root_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')

    ed.vm.eval('"nav" "x" "command:help" "ed.bind-mode" hostcall', filename='<nav-bind>')
    ed.vm.eval('"goto" "g" "command:showstatus" "ed.bind-mode" hostcall', filename='<goto-bind>')
    assert ed.exec_command_line('pushkeymode nav')
    assert ed.exec_command_line('pushkeymode-once goto')

    ed.enter_prompt('command', prefill='showkeymode')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showkeymode ')
    assert row[1] == 'command'
    assert row[2] == 'showkeymode MODE - show exact keymode detail'
    assert row[3] == 'active goto!, nav · known=3 · goto g->command:showstatus'


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

def test_prompt_complete_showbindings_active_uses_live_binding_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')

    ed.vm.eval('"goto" "g" "command:showstatus" "ed.bind-mode" hostcall', filename='<goto-bind>')
    assert ed.exec_command_line('pushkeymode-once goto')

    rows = ed._prompt_suggestion_rows(
        cmd='showbindings',
        toks=['showbindings', 'active'],
        tok_i=1,
        candidates=['active '],
        path_mode=False,
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'active ')
    assert row[1] == 'special'
    assert row[2] == 'active bindings=1'
    assert row[3] == 'g@goto!->command:showstatus (show portable statusline summary)'



def test_prompt_complete_showbindings_preserves_unmatched_mode_as_zero_bindings() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    candidates, fuzzy = ed._prompt_command_token_candidates(
        cmd='showbindings',
        toks=['showbindings', 'ghost'],
        tok_i=1,
        prefix='ghost',
        at_eol=True,
    )
    assert candidates == ['ghost ']
    assert fuzzy is False

    rows = ed._prompt_suggestion_rows(
        cmd='showbindings',
        toks=['showbindings', 'ghost'],
        tok_i=1,
        candidates=['ghost '],
        path_mode=False,
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'ghost ')
    assert row == ['ghost ', 'keymode', '0 bindings', 'show bindings']

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


def test_prompt_complete_showhook_preserves_missing_typed_target() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval(
        '\n'.join([
            'hook ed.test.alpha',
            'hook ed.test.beta',
        ]),
        filename='<test>',
    )

    candidates, fuzzy = ed._prompt_command_token_candidates(
        cmd='showhook',
        toks=['showhook', 'ghost'],
        tok_i=1,
        prefix='ghost',
        at_eol=True,
    )
    assert ('ghost ',) == tuple(candidates[:1])
    assert fuzzy is False

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='showhook',
        toks=['showhook', 'ghost'],
        tok_i=1,
        candidates=candidates,
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'ghost ')
    assert row[1] == 'hook'
    assert row[2] == 'missing hook'
    assert row[3] == 'not a hook'

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
    # ed.prompt-complete is a script-origin hostcall. This test exercises the
    # completion row mechanics rather than the word-read policy itself.
    assert ed.exec_command_line('set cap.word-read true') is True

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
    assert ed.exec_command_line('set cap.word-read true') is True

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

    assert ed.submit_prompt() is True

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

    assert ed.submit_prompt() is True
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



def test_prompt_complete_showoption_command_previews_live_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')
    ed.exec_command_line('setlocal readonly true')

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='showoption',
        toks=['showoption'],
        tok_i=0,
        candidates=['showoption '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showoption ')
    assert row[1] == 'command'
    assert row[2] == 'showoption NAME - show exact option value/default/doc detail'
    inventory = ed.option_inventory_rows()
    target = next((item for item in inventory if int(item[4]) and str(item[1]) != str(item[2])), next((item for item in inventory if int(item[4])), inventory[0]))
    summary = f"{len(inventory)} options · {target[0]}={target[1]}" + (" (local)" if int(target[4]) else "")
    assert row[3] == summary


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




def test_prompt_complete_exact_plugin_info_rows_fallback_to_state_when_detail_is_blank(tmp_path: Path) -> None:
    root = tmp_path / 'plugins'
    root.mkdir()

    a = root / 'a'
    a.mkdir()
    (a / 'main.mx').write_text(': init ( -- ) ;\n', encoding='utf-8')
    (a / 'plugin.json').write_text(json.dumps({'entry': 'main.mx'}), encoding='utf-8')

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)

    show_rows = ed._prompt_suggestion_rows(
        cmd='showplugin',
        toks=['showplugin', 'a'],
        tok_i=1,
        candidates=['a '],
        path_mode=False,
    )
    show_row = next(r for r in show_rows if isinstance(r, list) and r and r[0] == 'a ')
    assert show_row[1] == 'plugin'
    assert show_row[2] == '[loaded]'
    assert show_row[3] == 'loaded plugin'

    info_rows = ed._prompt_suggestion_rows(
        cmd='plugin',
        toks=['plugin', 'info', 'a'],
        tok_i=2,
        candidates=['a '],
        path_mode=False,
    )
    info_row = next(r for r in info_rows if isinstance(r, list) and r and r[0] == 'a ')
    assert info_row[1] == 'plugin'
    assert info_row[2] == '[loaded]'
    assert info_row[3] == 'loaded plugin'




def test_prompt_complete_exact_plugin_rows_keep_multi_error_count_and_last_detail(tmp_path: Path) -> None:
    root = tmp_path / 'plugins'
    root.mkdir()

    b = root / 'b'
    b.mkdir()
    (b / 'main.mx').write_text(': init ( -- ) ;\n', encoding='utf-8')
    (b / 'plugin.json').write_text(json.dumps({'entry': 'main.mx', 'requires': ['missingdep']}), encoding='utf-8')

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)
    pm.load_errors.append(('b', 'secondary issue'))

    show_rows = ed._prompt_suggestion_rows(
        cmd='showplugin',
        toks=['showplugin', 'b'],
        tok_i=1,
        candidates=['b '],
        path_mode=False,
    )
    show_row = next(r for r in show_rows if isinstance(r, list) and r and r[0] == 'b ')
    assert show_row[1] == 'plugin'
    assert show_row[2] == '[error, deps:missingdep] errors=2'
    assert show_row[3] == '2 load errors · last: secondary issue'

    info_rows = ed._prompt_suggestion_rows(
        cmd='plugin',
        toks=['plugin', 'info', 'b'],
        tok_i=2,
        candidates=['b '],
        path_mode=False,
    )
    info_row = next(r for r in info_rows if isinstance(r, list) and r and r[0] == 'b ')
    assert info_row[1] == 'plugin'
    assert info_row[2] == '[error, deps:missingdep]'
    assert info_row[3] == '2 load errors · last: secondary issue'

    error_rows = ed._prompt_suggestion_rows(
        cmd='plugin',
        toks=['plugin', 'errors', 'b'],
        tok_i=2,
        candidates=['b '],
        path_mode=False,
    )
    error_row = next(r for r in error_rows if isinstance(r, list) and r and r[0] == 'b ')
    assert error_row[1] == 'plugin'
    assert error_row[2] == '[error, deps:missingdep]'
    assert error_row[3] == '2 load errors · last: secondary issue'

def test_prompt_complete_showplugin_preserves_missing_typed_target(tmp_path: Path) -> None:
    root = tmp_path / 'plugins'
    root.mkdir()

    a = root / 'a'
    a.mkdir()
    (a / 'main.mx').write_text(': init ( -- ) ;\n', encoding='utf-8')
    (a / 'plugin.json').write_text(json.dumps({'entry': 'main.mx'}), encoding='utf-8')

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)

    candidates, fuzzy = ed._prompt_command_token_candidates(cmd='showplugin', toks=['showplugin', 'ghost'], tok_i=1, prefix='ghost', at_eol=True)
    assert candidates == ['ghost ']
    assert fuzzy is False

    rows = ed._prompt_suggestion_rows(
        cmd='showplugin',
        toks=['showplugin', 'ghost'],
        tok_i=1,
        candidates=['ghost '],
        path_mode=False,
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'ghost ')
    assert row == ['ghost ', 'plugin', 'missing plugin', 'no such plugin']



def test_prompt_complete_showplugin_without_manager_previews_unavailable_manager() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    candidates, fuzzy = ed._prompt_command_token_candidates(cmd='showplugin', toks=['showplugin', 'ghost'], tok_i=1, prefix='ghost', at_eol=True)
    assert candidates == ['ghost ']
    assert fuzzy is False

    rows = ed._prompt_suggestion_rows(
        cmd='showplugin',
        toks=['showplugin', 'ghost'],
        tok_i=1,
        candidates=['ghost '],
        path_mode=False,
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'ghost ')
    assert row == ['ghost ', 'plugin', 'plugin manager', 'not available']


def test_prompt_complete_buffers_command_previews_live_inventory(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    p = tmp_path / 'proj' / 'demo.txt'
    p.parent.mkdir(parents=True)
    p.write_text('demo\nsecond\n', encoding='utf-8')
    ed.open_file(str(p))
    ed.cur().buf.dirty = True

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='',
        toks=[],
        tok_i=0,
        candidates=['buffers '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'buffers ')
    assert row[1] == 'command'
    assert row[2] == 'buffers - list open buffers'
    assert row[3] == ed._buffer_inventory_preview_summary()
    assert str(p) in row[3]
    assert '[active, dirty]' in row[3]


def test_prompt_complete_bufferpick_command_previews_empty_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='',
        toks=[],
        tok_i=0,
        candidates=['bufferpick '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'bufferpick ')
    assert row[1] == 'command'
    assert row[2] == 'bufferpick [QUERY] - open searchable buffer picker'
    assert row[3] == '0 section(s), 0 buffers'


def test_prompt_complete_bufferpick_command_previews_current_sections(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('help:guide', 'guide')
    ed.new_buffer('*notes*', 'notes')

    p = tmp_path / 'proj' / 'file.txt'
    p.parent.mkdir(parents=True)
    p.write_text('file', encoding='utf-8')
    ed.open_file(str(p))

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='',
        toks=[],
        tok_i=0,
        candidates=['bufferpick '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'bufferpick ')
    assert row[1] == 'command'
    assert row[2] == 'bufferpick [QUERY] - open searchable buffer picker'
    assert row[3] == '3 section(s), 3 buffers · Help: 1 | e.g. help:guide — 1 lines'


def test_prompt_complete_showbuffer_command_previews_live_inventory(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    p = tmp_path / 'proj' / 'demo.txt'
    p.parent.mkdir(parents=True)
    p.write_text('demo\nsecond\n', encoding='utf-8')
    ed.open_file(str(p))
    eb = ed.cur()
    eb.buf.dirty = True

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='',
        toks=[],
        tok_i=0,
        candidates=['showbuffer '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showbuffer ')
    assert row[1] == 'command'
    assert row[2] == 'showbuffer NAME - show exact buffer state without switching'
    assert row[3] == ed._buffer_inventory_preview_summary()
    assert str(p) in row[3]
    assert '[active, dirty]' in row[3]



def test_prompt_complete_buffer_command_previews_live_inventory(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    p = tmp_path / 'proj' / 'demo.txt'
    p.parent.mkdir(parents=True)
    p.write_text('demo\nsecond\n', encoding='utf-8')
    ed.open_file(str(p))
    eb = ed.cur()
    eb.buf.dirty = True

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='',
        toks=[],
        tok_i=0,
        candidates=['buffer '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'buffer ')
    assert row[1] == 'command'
    assert row[2] == 'buffer NAME - switch active buffer'
    assert row[3] == ed._buffer_inventory_preview_summary()
    assert str(p) in row[3]
    assert '[active, dirty]' in row[3]


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

def test_prompt_complete_showrecent_slot_reuses_exact_recent_metadata(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line('set cap.fs-list true')

    p = tmp_path / 'demo.txt'
    q = tmp_path / 'other.txt'
    p.write_text('demo\n', encoding='utf-8')
    q.write_text('other\n', encoding='utf-8')
    ed.open_file(str(p))
    ed.open_file(str(q))

    ed.enter_prompt('command', prefill='showrecent 2')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == 'showrecent 2 '

    ed.enter_prompt('command', prefill='showrecent ')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == '2 ')
    assert row[1] == 'recent'
    assert row[2] == f'#2 {tmp_path}'
    assert row[3] == 'existing file | switch buffer'


def test_prompt_complete_showrecent_hash_slot_reuses_exact_recent_metadata(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line('set cap.fs-list true')

    p = tmp_path / 'demo.txt'
    q = tmp_path / 'other.txt'
    p.write_text('demo\n', encoding='utf-8')
    q.write_text('other\n', encoding='utf-8')
    ed.open_file(str(p))
    ed.open_file(str(q))

    ed.enter_prompt('command', prefill='showrecent #')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == '#2 ')
    assert row[1] == 'recent'
    assert row[2] == f'#2 {tmp_path}'
    assert row[3] == 'existing file | switch buffer'


def test_prompt_complete_showrecent_top_level_file_omits_duplicate_section_echo(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line('set cap.fs-list true')

    (tmp_path / 'pyproject.toml').write_text('[project]\nname = "demo"\n', encoding='utf-8')
    root = tmp_path / 'root.md'
    other = tmp_path / 'other.md'
    root.write_text('root\n', encoding='utf-8')
    other.write_text('other\n', encoding='utf-8')
    ed.open_file(str(root))
    ed.open_file(str(other))

    ed.enter_prompt('command', prefill=f'showrecent {tmp_path}')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == f'{root} ')
    assert row[1] == 'recent'
    assert row[2] == f'#2 {tmp_path}'
    assert row[3] == 'existing file | switch buffer'


def test_prompt_complete_recent_reuses_inventory_truth(tmp_path: Path) -> None:
    existing = tmp_path / 'existing.txt'
    existing.write_text('E\n', encoding='utf-8')

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line('set cap.fs-list true')

    ed.open_file(str(existing))
    assert ed.exec_command_line('close') is True

    scratch = tmp_path / 'scratch.md'
    ed.open_file(str(scratch))
    ed.recent_files = [str(scratch), str(existing)]

    ed.enter_prompt('command', prefill='recent ')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows

    row1 = next(r for r in rows if isinstance(r, list) and r and r[0] == '1 ')
    assert row1[1] == 'recent'
    assert row1[2] == f'*{scratch} @ 1:0'
    assert row1[3] == 'new file | current buffer'

    row2 = next(r for r in rows if isinstance(r, list) and r and r[0] == '2 ')
    assert row2[1] == 'recent'
    assert row2[2] == str(existing)
    assert row2[3] == 'existing file'


def test_prompt_complete_recent_hash_slot_reuses_inventory_truth(tmp_path: Path) -> None:
    existing = tmp_path / 'existing.txt'
    existing.write_text('E\n', encoding='utf-8')

    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line('set cap.fs-list true')

    ed.open_file(str(existing))
    assert ed.exec_command_line('close') is True

    scratch = tmp_path / 'scratch.md'
    ed.open_file(str(scratch))
    ed.recent_files = [str(scratch), str(existing)]

    ed.enter_prompt('command', prefill='recent #')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows

    row2 = next(r for r in rows if isinstance(r, list) and r and r[0] == '#2 ')
    assert row2[1] == 'recent'
    assert row2[2] == str(existing)
    assert row2[3] == 'existing file'


def test_prompt_complete_recent_clear_row_is_explicit(tmp_path: Path) -> None:
    p = tmp_path / 'notes.txt'
    p.write_text('hi\n', encoding='utf-8')

    ed = Editor()
    install_editor_hostcalls(ed)
    ed.open_file(str(p))

    ed.enter_prompt('command', prefill='recent c')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == 'recent clear '

    ed.enter_prompt('command', prefill='recent ')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'clear ')
    assert row[1] == 'recent'
    assert row[2] == 'clear history'
    assert row[3] == 'forget 1 recent file'

def test_prompt_complete_recentpick_reuses_exact_recent_metadata(tmp_path: Path) -> None:
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

    ed.enter_prompt('command', prefill=f'recentpick {tmp_path / "proj" / "demo"}')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == f'recentpick {p} '

    ed.enter_prompt('command', prefill=f'recentpick {tmp_path / "proj" / "d"}')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == f'{p} ')
    assert row[1] == 'recent'
    assert row[2] == f'#2 {tmp_path}'
    assert row[3] == 'proj/demo.txt | existing file | switch buffer'




def test_prompt_complete_recentpick_slot_miss_stays_honest() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'one\n')
    rows = ed._prompt_suggestion_rows(
        cmd='recentpick',
        toks=['recentpick', '#9'],
        tok_i=1,
        candidates=['#9 '],
        path_mode=False,
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == '#9 ')
    assert row[1] == 'recent'
    assert row[3] == 'no such recent file'


def test_prompt_complete_recent_slot_miss_stays_honest() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'one\n')
    rows = ed._prompt_suggestion_rows(
        cmd='recent',
        toks=['recent', '#9'],
        tok_i=1,
        candidates=['#9 '],
        path_mode=False,
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == '#9 ')
    assert row[1] == 'recent'
    assert row[3] == 'no such recent file'



def test_prompt_complete_recentpick_query_miss_previews_zero_summary() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'one\n')
    rows = ed._prompt_suggestion_rows(
        cmd='recentpick',
        toks=['recentpick', 'zzz-no-such-recent-file'],
        tok_i=1,
        candidates=['zzz-no-such-recent-file '],
        path_mode=False,
    )
    row = next(
        r for r in rows if isinstance(r, list) and r and r[0] == 'zzz-no-such-recent-file '
    )
    assert row[1] == 'recent'
    assert row[2] == ''
    assert row[3] == '0 recent file(s)'


def test_prompt_complete_recentdirpick_query_miss_previews_zero_summary() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'one\n')
    rows = ed._prompt_suggestion_rows(
        cmd='recentdirpick',
        toks=['recentdirpick', 'zzz-no-such-recent-file'],
        tok_i=1,
        candidates=['zzz-no-such-recent-file '],
        path_mode=False,
    )
    row = next(
        r for r in rows if isinstance(r, list) and r and r[0] == 'zzz-no-such-recent-file '
    )
    assert row[1] == 'recent'
    assert row[2] == ''
    assert row[3] == '0 recent file(s)'


def test_prompt_complete_recentdirpick_reuses_exact_recent_metadata(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line('set cap.fs-list true')

    (tmp_path / 'pyproject.toml').write_text('[project]\nname = "demo"\n', encoding='utf-8')
    root = tmp_path / 'root.md'
    other = tmp_path / 'other.md'
    root.write_text('root\n', encoding='utf-8')
    other.write_text('other\n', encoding='utf-8')
    ed.open_file(str(root))
    ed.open_file(str(other))

    ed.enter_prompt('command', prefill=f'recentdirpick {tmp_path}')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == f'{root} ')
    assert row[1] == 'recent'
    assert row[2] == f'#2 {tmp_path}'
    assert row[3] == 'existing file | switch buffer'


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


def test_prompt_complete_showrecent_path_miss_stays_honest(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line('set cap.fs-list true')

    p = tmp_path / 'a.txt'
    p.write_text('a\n', encoding='utf-8')
    ed.open_file(str(p))

    missing = '/definitely/not/a/recent/missing-path-987654321.txt'
    rows = ed._prompt_suggestion_rows(
        cmd='showrecent',
        toks=['showrecent', missing],
        tok_i=1,
        candidates=[f'{missing} '],
        path_mode=False,
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == f'{missing} ')
    assert row[1] == 'recent'
    assert row[2] == ''
    assert row[3] == 'no such recent file'

def test_prompt_complete_showrecentdir_slot_miss_stays_honest(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line('set cap.fs-list true')

    p = tmp_path / 'a.txt'
    p.write_text('a\n', encoding='utf-8')
    ed.open_file(str(p))

    rows = ed._prompt_suggestion_rows(
        cmd='showrecentdir',
        toks=['showrecentdir', '#9'],
        tok_i=1,
        candidates=['#9 '],
        path_mode=False,
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == '#9 ')
    assert row[1] == 'recentdir'
    assert row[2] == ''
    assert row[3] == 'no such recent directory'

def test_prompt_complete_showrecentdir_path_miss_stays_honest(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line('set cap.fs-list true')

    p = tmp_path / 'a.txt'
    p.write_text('a\n', encoding='utf-8')
    ed.open_file(str(p))

    missing = tmp_path / 'missing-dir'
    rows = ed._prompt_suggestion_rows(
        cmd='showrecentdir',
        toks=['showrecentdir', str(missing)],
        tok_i=1,
        candidates=[f'{missing} '],
        path_mode=False,
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == f'{missing} ')
    assert row[1] == 'recentdir'
    assert row[2] == ''
    assert row[3] == 'no such recent directory'

def test_prompt_complete_showrecentdir_hash_slot_reuses_exact_recent_directory_metadata(tmp_path: Path) -> None:
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

    ed.enter_prompt('command', prefill='showrecentdir #')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == '#1 ')
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


def test_prompt_complete_showbuffergroups_command_previews_current_sections(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('help:guide', 'guide')
    ed.new_buffer('*notes*', 'notes')

    p = tmp_path / 'proj' / 'file.txt'
    p.parent.mkdir(parents=True)
    p.write_text('file', encoding='utf-8')
    ed.open_file(str(p))

    ed.enter_prompt('command', prefill='showb')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showbuffergroups ')
    assert row[1] == 'command'
    assert row[2] == 'showbuffergroups [QUERY] - show count-aware buffer sections'
    assert row[3] == '3 section(s), 3 buffers · Help: 1 | e.g. help:guide — 1 lines'



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
    assert row[2] == '3 files (e.g. a.txt #4 [open] @ 1:0)'
    assert row[3] == 'proj/src/a.txt | switch buffer'

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
    assert row[2] == '2 files (e.g. b.txt #3 [open] @ 1:0)'
    assert row[3] == 'switch buffer'



def test_prompt_complete_showrecentgroups_project_root_bucket_omits_duplicate_filename_echo(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    (tmp_path / 'pyproject.toml').write_text('[project]\nname = "demo"\n', encoding='utf-8')
    other_root = tmp_path / 'otherroot'
    other_root.mkdir(parents=True)
    (other_root / 'pyproject.toml').write_text('[project]\nname = "other"\n', encoding='utf-8')
    root = tmp_path / 'root.md'
    other = other_root / 'other.md'
    root.write_text('root\n', encoding='utf-8')
    other.write_text('other\n', encoding='utf-8')
    ed.open_file(str(root))
    ed.open_file(str(other))

    ed.enter_prompt('command', prefill='showrecentgroups ')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == f'{tmp_path} ')
    assert row[1] == 'recent-group'
    assert row[2] == '1 file (e.g. root.md #2 [open] @ 1:0)'
    assert row[3] == 'switch buffer'

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


def test_prompt_complete_showplugins_command_previews_current_sections(tmp_path: Path) -> None:
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

    ed.enter_prompt('command', prefill='showpl')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showplugins ')
    assert row[1] == 'command'
    assert row[2] == 'showplugins [QUERY] - show count-aware plugin-state sections'
    assert row[3] == '2 section(s), 3 plugins · Errors: 1 | e.g. beta — missing dependency: missingdep'


def test_prompt_complete_showplugins_command_previews_empty_sections() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('a', 'one\n')
    ed.plugin_manager = PluginManager(ed.vm)

    ed.enter_prompt('command', prefill='showpl')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showplugins ')
    assert row[2] == 'showplugins [QUERY] - show count-aware plugin-state sections'
    assert row[3] == '0 section(s), 0 plugins'



def test_prompt_complete_showplugins_command_previews_unavailable_manager() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('a', 'one\n')

    ed.enter_prompt('command', prefill='showpl')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showplugins ')
    assert row[2] == 'showplugins [QUERY] - show count-aware plugin-state sections'
    assert row[3] == 'plugin manager not available'


def test_prompt_complete_showplugin_command_previews_live_inventory(tmp_path: Path) -> None:
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

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='showplugin',
        toks=['showplugin'],
        tok_i=0,
        candidates=['showplugin '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showplugin ')
    assert row[1] == 'command'
    assert row[2] == 'showplugin NAME - show exact plugin state without opening verbose detail'
    assert row[3] == '3 plugins · e.g. beta [error, deps:missingdep]'



def test_prompt_complete_showplugin_command_previews_empty_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.plugin_manager = PluginManager(ed.vm)

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='showplugin',
        toks=['showplugin'],
        tok_i=0,
        candidates=['showplugin '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showplugin ')
    assert row[1] == 'command'
    assert row[2] == 'showplugin NAME - show exact plugin state without opening verbose detail'
    assert row[3] == '0 plugins'



def test_prompt_complete_showplugin_command_previews_unavailable_manager() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='showplugin',
        toks=['showplugin'],
        tok_i=0,
        candidates=['showplugin '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showplugin ')
    assert row[1] == 'command'
    assert row[2] == 'showplugin NAME - show exact plugin state without opening verbose detail'
    assert row[3] == 'plugin manager not available'



def test_prompt_complete_plugin_root_command_previews_live_inventory(tmp_path: Path) -> None:
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

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='plugin',
        toks=['plugin'],
        tok_i=0,
        candidates=['plugin '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'plugin ')
    assert row[1] == 'command'
    assert row[2] == 'plugin list|load NAME|unload NAME|reload NAME|info NAME|errors [NAME]|cleanup [NAME]|grants|revoke NAME'
    assert row[3] == '3 plugins (1 error, 2 loaded) · e.g. beta [error, deps:missingdep]'



def test_prompt_complete_plugin_root_command_previews_empty_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.plugin_manager = PluginManager(ed.vm)

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='plugin',
        toks=['plugin'],
        tok_i=0,
        candidates=['plugin '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'plugin ')
    assert row[1] == 'command'
    assert row[2] == 'plugin list|load NAME|unload NAME|reload NAME|info NAME|errors [NAME]|cleanup [NAME]|grants|revoke NAME'
    assert row[3] == '0 plugins'



def test_prompt_complete_plugin_root_command_previews_unavailable_manager() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='plugin',
        toks=['plugin'],
        tok_i=0,
        candidates=['plugin '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'plugin ')
    assert row[1] == 'command'
    assert row[2] == 'plugin list|load NAME|unload NAME|reload NAME|info NAME|errors [NAME]|cleanup [NAME]|grants|revoke NAME'
    assert row[3] == 'plugin manager not available'


def test_prompt_complete_pluginpick_command_previews_live_sections(tmp_path: Path) -> None:
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

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='pluginpick',
        toks=['pluginpick'],
        tok_i=0,
        candidates=['pluginpick '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'pluginpick ')
    assert row[1] == 'command'
    assert row[2] == 'pluginpick [QUERY] - open searchable plugin picker'
    assert row[3] == '2 section(s), 3 plugins · Errors (1): e.g. beta — missing dependency: missingdep'


def test_prompt_complete_pluginpick_command_previews_empty_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.plugin_manager = PluginManager(ed.vm)

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='pluginpick',
        toks=['pluginpick'],
        tok_i=0,
        candidates=['pluginpick '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'pluginpick ')
    assert row[1] == 'command'
    assert row[2] == 'pluginpick [QUERY] - open searchable plugin picker'
    assert row[3] == '0 section(s), 0 plugins'


def test_prompt_complete_pluginpick_command_previews_unavailable_manager() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='pluginpick',
        toks=['pluginpick'],
        tok_i=0,
        candidates=['pluginpick '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'pluginpick ')
    assert row[1] == 'command'
    assert row[2] == 'pluginpick [QUERY] - open searchable plugin picker'
    assert row[3] == 'plugin manager not available'


def test_prompt_complete_plugin_list_command_previews_live_inventory(tmp_path: Path) -> None:
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

    ed.enter_prompt('command', prefill='plugin ')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'list ')
    assert row[1] == 'subcommand'
    assert row[2] == 'plugin list - show live plugin inventory'
    assert row[3] == '3 plugins (1 error, 2 loaded) · e.g. beta [error, deps:missingdep]'



def test_prompt_complete_plugin_list_command_previews_empty_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.plugin_manager = PluginManager(ed.vm)

    ed.enter_prompt('command', prefill='plugin ')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'list ')
    assert row[1] == 'subcommand'
    assert row[2] == 'plugin list - show live plugin inventory'
    assert row[3] == '0 plugins'



def test_prompt_complete_plugin_list_command_previews_unavailable_manager() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.enter_prompt('command', prefill='plugin ')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'list ')
    assert row[1] == 'subcommand'
    assert row[2] == 'plugin list - show live plugin inventory'
    assert row[3] == 'plugin manager not available'


def test_prompt_complete_plugin_subcommands_preview_live_inventory(tmp_path: Path) -> None:
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

    ed.enter_prompt('command', prefill='plugin ')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows

    reload_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'reload ')
    assert reload_row[1] == 'subcommand'
    assert reload_row[2] == 'plugin reload NAME - reload one loaded plugin'
    assert reload_row[3] == '2 loaded plugins · e.g. alpha [loaded]'

    info_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'info ')
    assert info_row[1] == 'subcommand'
    assert info_row[2] == 'plugin info NAME - show exact plugin state'
    assert info_row[3] == '3 plugins · e.g. beta [error, deps:missingdep]'

    errors_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'errors ')
    assert errors_row[1] == 'subcommand'
    assert errors_row[2] == 'plugin errors NAME - show plugin load errors'
    assert errors_row[3] == '1 plugin with errors · e.g. beta [error, deps:missingdep]'



def test_prompt_complete_plugin_subcommands_preview_empty_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.plugin_manager = PluginManager(ed.vm)

    ed.enter_prompt('command', prefill='plugin ')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows

    reload_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'reload ')
    assert reload_row[3] == '0 loaded plugins'

    info_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'info ')
    assert info_row[3] == '0 plugins'

    errors_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'errors ')
    assert errors_row[3] == '0 plugins with errors'



def test_prompt_complete_plugin_subcommands_preview_empty_loaded_subset_keeps_inventory_witness(tmp_path: Path) -> None:
    root = tmp_path / 'plugins'
    root.mkdir()

    broken = root / 'beta'
    broken.mkdir()
    (broken / 'main.mx').write_text(': init ( -- ) ;\n', encoding='utf-8')
    (broken / 'plugin.json').write_text(json.dumps({'entry': 'main.mx', 'requires': ['missingdep']}), encoding='utf-8')

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)

    ed.enter_prompt('command', prefill='plugin ')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows

    reload_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'reload ')
    assert reload_row[3] == '0 loaded plugins · 1 plugin total · e.g. beta [error, deps:missingdep]'



def test_prompt_complete_plugin_subcommands_preview_empty_error_subset_keeps_inventory_witness(tmp_path: Path) -> None:
    root = tmp_path / 'plugins'
    root.mkdir()

    alpha = root / 'alpha'
    alpha.mkdir()
    (alpha / 'main.mx').write_text(': init ( -- ) ;\n', encoding='utf-8')
    (alpha / 'plugin.json').write_text(json.dumps({'entry': 'main.mx'}), encoding='utf-8')

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)

    ed.enter_prompt('command', prefill='plugin ')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows

    errors_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'errors ')
    assert errors_row[3] == '0 plugins with errors · 1 plugin total · e.g. alpha [loaded]'



def test_prompt_complete_plugin_subcommands_preview_unavailable_manager() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.enter_prompt('command', prefill='plugin ')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows

    reload_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'reload ')
    assert reload_row[3] == 'plugin manager not available'

    info_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'info ')
    assert info_row[3] == 'plugin manager not available'

    errors_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'errors ')
    assert errors_row[3] == 'plugin manager not available'


def test_prompt_complete_plugin_target_candidates_preserve_exact_missing_and_unloaded_names(tmp_path: Path) -> None:
    root = tmp_path / 'plugins'
    root.mkdir()

    alpha = root / 'alpha'
    alpha.mkdir()
    (alpha / 'main.mx').write_text(': init ( -- ) ;\n', encoding='utf-8')
    (alpha / 'plugin.json').write_text(json.dumps({'entry': 'main.mx'}), encoding='utf-8')

    beta = root / 'beta'
    beta.mkdir()
    (beta / 'main.mx').write_text(': init ( -- ) ;\n', encoding='utf-8')
    (beta / 'plugin.json').write_text(json.dumps({'entry': 'main.mx', 'requires': ['missingdep']}), encoding='utf-8')

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)

    reload_candidates, reload_fuzzy = ed._prompt_command_token_candidates(
        cmd='plugin',
        toks=['plugin', 'reload', 'beta'],
        tok_i=2,
        prefix='beta',
        at_eol=True,
    )
    assert reload_candidates == ['beta ']
    assert reload_fuzzy is False

    missing_candidates, missing_fuzzy = ed._prompt_command_token_candidates(
        cmd='plugin',
        toks=['plugin', 'errors', 'ghost'],
        tok_i=2,
        prefix='ghost',
        at_eol=True,
    )
    assert missing_candidates == ['ghost ']
    assert missing_fuzzy is False


def test_prompt_complete_plugin_target_rows_stay_truthful_for_reload_errors_and_missing(tmp_path: Path) -> None:
    root = tmp_path / 'plugins'
    root.mkdir()

    alpha = root / 'alpha'
    alpha.mkdir()
    (alpha / 'main.mx').write_text(': init ( -- ) ;\n', encoding='utf-8')
    (alpha / 'plugin.json').write_text(json.dumps({'entry': 'main.mx'}), encoding='utf-8')

    beta = root / 'beta'
    beta.mkdir()
    (beta / 'main.mx').write_text(': init ( -- ) ;\n', encoding='utf-8')
    (beta / 'plugin.json').write_text(json.dumps({'entry': 'main.mx', 'requires': ['missingdep']}), encoding='utf-8')

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)

    reload_rows = ed._prompt_suggestion_rows(
        cmd='plugin',
        toks=['plugin', 'reload', 'beta'],
        tok_i=2,
        candidates=['beta '],
        path_mode=False,
    )
    reload_row = next(r for r in reload_rows if isinstance(r, list) and r and r[0] == 'beta ')
    assert reload_row[1] == 'plugin'
    assert reload_row[2] == '[error, deps:missingdep]'
    assert reload_row[3] == 'missing dependency: missingdep · not loaded'

    clean_error_rows = ed._prompt_suggestion_rows(
        cmd='plugin',
        toks=['plugin', 'errors', 'alpha'],
        tok_i=2,
        candidates=['alpha '],
        path_mode=False,
    )
    clean_error_row = next(r for r in clean_error_rows if isinstance(r, list) and r and r[0] == 'alpha ')
    assert clean_error_row[1] == 'plugin'
    assert clean_error_row[2] == '[loaded]'
    assert clean_error_row[3] == '0 load errors · loaded plugin'

    missing_rows = ed._prompt_suggestion_rows(
        cmd='plugin',
        toks=['plugin', 'info', 'ghost'],
        tok_i=2,
        candidates=['ghost '],
        path_mode=False,
    )
    missing_row = next(r for r in missing_rows if isinstance(r, list) and r and r[0] == 'ghost ')
    assert missing_row[1] == 'plugin'
    assert missing_row[2] == 'missing plugin'
    assert missing_row[3] == 'no such plugin'


def test_prompt_complete_plugin_reload_available_target_keeps_state_witness(tmp_path: Path) -> None:
    root = tmp_path / 'plugins'
    root.mkdir()

    optional = root / 'optional'
    optional.mkdir()
    (optional / 'main.mx').write_text(': init ( -- ) ;\n', encoding='utf-8')
    (optional / 'plugin.json').write_text(json.dumps({'entry': 'main.mx', 'version': '0.2.0'}), encoding='utf-8')

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)
    pm.plugins.pop('optional', None)

    reload_rows = ed._prompt_suggestion_rows(
        cmd='plugin',
        toks=['plugin', 'reload', 'optional'],
        tok_i=2,
        candidates=['optional '],
        path_mode=False,
    )
    reload_row = next(r for r in reload_rows if isinstance(r, list) and r and r[0] == 'optional ')
    assert reload_row[1] == 'plugin'
    assert reload_row[2] == '[available, v0.2.0]'
    assert reload_row[3] == 'available plugin · not loaded'


def test_prompt_complete_plugin_errors_available_target_keeps_state_witness(tmp_path: Path) -> None:
    root = tmp_path / 'plugins'
    root.mkdir()

    optional = root / 'optional'
    optional.mkdir()
    (optional / 'main.mx').write_text(': init ( -- ) ;\n', encoding='utf-8')
    (optional / 'plugin.json').write_text(json.dumps({'entry': 'main.mx', 'version': '0.2.0'}), encoding='utf-8')

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)
    pm.plugins.pop('optional', None)

    error_rows = ed._prompt_suggestion_rows(
        cmd='plugin',
        toks=['plugin', 'errors', 'optional'],
        tok_i=2,
        candidates=['optional '],
        path_mode=False,
    )
    error_row = next(r for r in error_rows if isinstance(r, list) and r and r[0] == 'optional ')
    assert error_row[1] == 'plugin'
    assert error_row[2] == '[available, v0.2.0]'
    assert error_row[3] == '0 load errors · available plugin · not loaded'


def test_prompt_complete_showplugin_and_plugin_info_available_targets_keep_not_loaded_witness(tmp_path: Path) -> None:
    root = tmp_path / 'plugins'
    root.mkdir()

    optional = root / 'optional'
    optional.mkdir()
    (optional / 'main.mx').write_text(': init ( -- ) ;\n', encoding='utf-8')
    (optional / 'plugin.json').write_text(json.dumps({'entry': 'main.mx', 'version': '0.2.0'}), encoding='utf-8')

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)
    pm.plugins.pop('optional', None)

    info_rows = ed._prompt_suggestion_rows(
        cmd='plugin',
        toks=['plugin', 'info', 'optional'],
        tok_i=2,
        candidates=['optional '],
        path_mode=False,
    )
    info_row = next(r for r in info_rows if isinstance(r, list) and r and r[0] == 'optional ')
    assert info_row[1] == 'plugin'
    assert info_row[2] == '[available, v0.2.0]'
    assert info_row[3] == 'available plugin · not loaded'

    show_rows = ed._prompt_suggestion_rows(
        cmd='showplugin',
        toks=['showplugin', 'optional'],
        tok_i=1,
        candidates=['optional '],
        path_mode=False,
    )
    show_row = next(r for r in show_rows if isinstance(r, list) and r and r[0] == 'optional ')
    assert show_row[1] == 'plugin'
    assert show_row[2] == '[available, v0.2.0]'
    assert show_row[3] == 'available plugin · not loaded'


def test_prompt_complete_macro_root_command_previews_empty_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer(text='')

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='macro',
        toks=['macro'],
        tok_i=0,
        candidates=['macro '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'macro ')
    assert row[1] == 'command'
    assert row[2] == 'macro record/rec/start|stop/end|cancel/abort|play/run|list/ls|status/st - keyboard macros'
    assert row[3] == 'idle · default=last (0 steps) · 0 macros'



def test_prompt_complete_macro_list_and_status_preview_badge_last_when_it_is_the_only_sample() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer(text='')

    ed.set_macro('last', [MacroStep(kind='command', name='command', payload={'cmdline': 'noop'})])

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='macro',
        toks=['macro', 'list'],
        tok_i=1,
        candidates=['list ', 'status '],
    )
    list_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'list ')
    status_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'status ')

    assert list_row[3] == '1 macro · e.g. last (1 step) [default]'
    assert status_row[3] == 'idle · default=last (1 step) · 1 macro · e.g. last (1 step) [default]'


def test_prompt_complete_macro_root_command_previews_recording_and_saved_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer(text='')

    assert ed.exec_command_line('macro record demo')
    ed.input['text'] = 'z'
    assert ed.run_action('InsertText')

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='macro',
        toks=['macro'],
        tok_i=0,
        candidates=['macro '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'macro ')
    assert row[1] == 'command'
    assert row[2] == 'macro record/rec/start|stop/end|cancel/abort|play/run|list/ls|status/st - keyboard macros'
    assert row[3] == 'recording · demo (1 step) · stop to save, cancel to discard · 0 macros'

    assert ed.exec_command_line('macro stop')
    rows = ed._prompt_commandish_suggestion_rows(
        cmd='macro',
        toks=['macro'],
        tok_i=0,
        candidates=['macro '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'macro ')
    assert row[3] == 'idle · default=last (1 step) · 2 macros · e.g. demo (1 step)'

    ed._macro_playing = True
    ed._macro_play_name = 'demo'
    ed._macro_play_steps = 1
    rows = ed._prompt_commandish_suggestion_rows(
        cmd='macro',
        toks=['macro'],
        tok_i=0,
        candidates=['macro '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'macro ')
    assert row[3] == 'playing · demo (1 step) · wait for playback · 2 macros · e.g. last (1 step) [default]'



def test_prompt_complete_macro_subcommands_preview_empty_inventory_and_status() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer(text='')

    ed.enter_prompt('command', prefill='macro ')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    assert 'status ' in ed.prompt.suggestions
    rows = ed.prompt.suggestion_rows

    list_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'list ')
    assert list_row[1] == 'subcommand'
    assert list_row[2] == 'macro list - show saved macro inventory'
    assert list_row[3] == '0 macros'

    status_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'status ')
    assert status_row[1] == 'subcommand'
    assert status_row[2] == 'macro status - show live macro state'
    assert status_row[3] == 'idle · default=last (0 steps) · 0 macros'


def test_prompt_complete_macro_subcommands_preview_live_inventory_and_recording_state() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer(text='')

    assert ed.exec_command_line('macro record demo')
    ed.input['text'] = 'z'
    assert ed.run_action('InsertText')

    ed.enter_prompt('command', prefill='macro ')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows

    list_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'list ')
    assert list_row[3] == '0 macros'

    status_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'status ')
    assert status_row[3] == 'recording · demo (1 step) · 0 macros'

    assert ed.exec_command_line('macro stop')
    ed.enter_prompt('command', prefill='macro ')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows

    list_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'list ')
    assert list_row[3] == '2 macros · e.g. demo (1 step)'

    status_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'status ')
    assert status_row[3] == 'idle · default=last (1 step) · 2 macros · e.g. demo (1 step)'

    ed._macro_playing = True
    ed._macro_play_name = 'demo'
    ed._macro_play_steps = 1
    ed.enter_prompt('command', prefill='macro ')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    status_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'status ')
    assert status_row[3] == 'playing · demo (1 step) · 2 macros · e.g. last (1 step) [default]'


def test_prompt_complete_macro_subcommands_preview_action_rows_and_aliases_when_idle() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer(text='')

    ed.enter_prompt('command', prefill='macro ')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    assert 'rec ' in ed.prompt.suggestions
    assert 'start ' in ed.prompt.suggestions
    assert 'run ' in ed.prompt.suggestions
    assert 'ls ' in ed.prompt.suggestions
    assert 'st ' in ed.prompt.suggestions
    assert 'end ' in ed.prompt.suggestions
    assert 'abort ' in ed.prompt.suggestions
    rows = ed.prompt.suggestion_rows

    play_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'play ')
    assert play_row[1] == 'subcommand'
    assert play_row[2] == 'macro play [NAME] [COUNT] - play saved macro'
    assert play_row[3] == 'idle · default=last (0 steps) · default slot empty · 0 macros'

    record_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'record ')
    assert record_row[1] == 'subcommand'
    assert record_row[2] == 'macro record [NAME] - start recording macro'
    assert record_row[3] == 'idle · default=last (0 steps) · record default slot · 0 macros'

    rec_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'rec ')
    assert rec_row[1] == 'subcommand'
    assert rec_row[2] == 'macro rec [NAME] - start recording macro'
    assert rec_row[3] == 'idle · default=last (0 steps) · record default slot · 0 macros'

    start_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'start ')
    assert start_row[1] == 'subcommand'
    assert start_row[2] == 'macro start [NAME] - start recording macro'
    assert start_row[3] == 'idle · default=last (0 steps) · record default slot · 0 macros'

    run_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'run ')
    assert run_row[1] == 'subcommand'
    assert run_row[2] == 'macro run [NAME] [COUNT] - play saved macro'
    assert run_row[3] == 'idle · default=last (0 steps) · default slot empty · 0 macros'

    stop_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'stop ')
    assert stop_row[1] == 'subcommand'
    assert stop_row[2] == 'macro stop - stop recording and save'
    assert stop_row[3] == 'idle · not recording'

    end_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'end ')
    assert end_row[1] == 'subcommand'
    assert end_row[2] == 'macro end - stop recording and save'
    assert end_row[3] == 'idle · not recording'

    cancel_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'cancel ')
    assert cancel_row[1] == 'subcommand'
    assert cancel_row[2] == 'macro cancel - stop recording and discard'
    assert cancel_row[3] == 'idle · not recording'

    abort_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'abort ')
    assert abort_row[1] == 'subcommand'
    assert abort_row[2] == 'macro abort - stop recording and discard'
    assert abort_row[3] == 'idle · not recording'

    ls_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'ls ')
    assert ls_row[1] == 'subcommand'
    assert ls_row[2] == 'macro ls - show saved macro inventory'
    assert ls_row[3] == '0 macros'

    st_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'st ')
    assert st_row[1] == 'subcommand'
    assert st_row[2] == 'macro st - show live macro state'
    assert st_row[3] == 'idle · default=last (0 steps) · 0 macros'





def test_prompt_complete_macro_subcommands_preview_playback_blockers() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer(text='')

    assert ed.exec_command_line('macro record demo')
    ed.input['text'] = 'z'
    assert ed.run_action('InsertText')
    assert ed.exec_command_line('macro stop')

    ed._macro_playing = True
    ed._macro_play_name = 'demo'
    ed._macro_play_steps = 1

    assert ed._prompt_macro_command_row('play ', subcommand='play') == [
        'play ', 'subcommand', 'macro play [NAME] [COUNT] - play saved macro',
        'playing · demo (1 step) · wait for playback',
    ]
    assert ed._prompt_macro_command_row('run ', subcommand='run') == [
        'run ', 'subcommand', 'macro run [NAME] [COUNT] - play saved macro',
        'playing · demo (1 step) · wait for playback',
    ]
    assert ed._prompt_macro_command_row('stop ', subcommand='stop') == [
        'stop ', 'subcommand', 'macro stop - stop recording and save',
        'playing · demo (1 step) · wait for playback',
    ]
    assert ed._prompt_macro_command_row('end ', subcommand='end') == [
        'end ', 'subcommand', 'macro end - stop recording and save',
        'playing · demo (1 step) · wait for playback',
    ]
    assert ed._prompt_macro_command_row('cancel ', subcommand='cancel') == [
        'cancel ', 'subcommand', 'macro cancel - stop recording and discard',
        'playing · demo (1 step) · wait for playback',
    ]
    assert ed._prompt_macro_command_row('abort ', subcommand='abort') == [
        'abort ', 'subcommand', 'macro abort - stop recording and discard',
        'playing · demo (1 step) · wait for playback',
    ]

def test_prompt_complete_macro_subcommands_preview_action_rows_when_recording_and_after_save() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer(text='')

    assert ed.exec_command_line('macro record demo')
    ed.input['text'] = 'z'
    assert ed.run_action('InsertText')

    ed.enter_prompt('command', prefill='macro ')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows

    play_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'play ')
    assert play_row[3] == 'recording · demo (1 step) · stop or cancel first'

    run_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'run ')
    assert run_row[3] == 'recording · demo (1 step) · stop or cancel first'

    record_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'record ')
    assert record_row[3] == 'recording · demo (1 step) · stop or cancel first'

    stop_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'stop ')
    assert stop_row[3] == 'recording · demo (1 step) · save macro'

    end_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'end ')
    assert end_row[3] == 'recording · demo (1 step) · save macro'

    cancel_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'cancel ')
    assert cancel_row[3] == 'recording · demo (1 step) · discard macro'

    abort_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'abort ')
    assert abort_row[3] == 'recording · demo (1 step) · discard macro'

    assert ed.exec_command_line('macro stop')
    ed.enter_prompt('command', prefill='macro ')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows

    play_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'play ')
    assert play_row[3] == 'idle · default=last (1 step) · play default slot · 2 macros · e.g. demo (1 step)'

    run_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'run ')
    assert run_row[3] == 'idle · default=last (1 step) · play default slot · 2 macros · e.g. demo (1 step)'

    record_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'record ')
    assert record_row[3] == 'idle · default=last (1 step) · overwrite default slot on save · 2 macros · e.g. demo (1 step)'

    ls_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'ls ')
    assert ls_row[3] == '2 macros · e.g. demo (1 step)'

    st_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'st ')
    assert st_row[3] == 'idle · default=last (1 step) · 2 macros · e.g. demo (1 step)'

def test_prompt_complete_macro_play_slots_preview_saved_inventory_and_omit_empty_last() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer(text='')

    ed.enter_prompt('command', prefill='macro play ')
    assert ed.prompt is not None
    assert ed.prompt_complete(direction=1) is False
    assert ed.prompt.suggestion_rows == []

    ed.enter_prompt('command', prefill='macro run ')
    assert ed.prompt is not None
    assert ed.prompt_complete(direction=1) is False
    assert ed.prompt.suggestion_rows == []

    empty_last_row = ed._prompt_macro_slot_row('last ', subcommand='play')
    assert empty_last_row == ['last ', 'macro', '0 steps [default]', 'default slot empty']

    empty_last_run_row = ed._prompt_macro_slot_row('last ', subcommand='run')
    assert empty_last_run_row == ['last ', 'macro', '0 steps [default]', 'default slot empty']

    missing_row = ed._prompt_macro_slot_row('ghost ', subcommand='play')
    assert missing_row == ['ghost ', 'macro', 'missing macro', 'no such macro']

    missing_run_row = ed._prompt_macro_slot_row('ghost ', subcommand='run')
    assert missing_run_row == ['ghost ', 'macro', 'missing macro', 'no such macro']

    assert ed.exec_command_line('macro record demo')
    ed.input['text'] = 'z'
    assert ed.run_action('InsertText')
    assert ed.exec_command_line('macro stop')

    ed.enter_prompt('command', prefill='macro play ')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows

    demo_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'demo ')
    assert demo_row[1] == 'macro'
    assert demo_row[2] == 'demo (1 step)'
    assert demo_row[3] == 'play macro'

    last_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'last ')
    assert last_row[1] == 'macro'
    assert last_row[2] == 'last (1 step) [default]'
    assert last_row[3] == 'play default slot'

    ed.enter_prompt('command', prefill='macro run ')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    run_rows = ed.prompt.suggestion_rows

    demo_run_row = next(r for r in run_rows if isinstance(r, list) and r and r[0] == 'demo ')
    assert demo_run_row[1] == 'macro'
    assert demo_run_row[2] == 'demo (1 step)'
    assert demo_run_row[3] == 'play macro'

    last_run_row = next(r for r in run_rows if isinstance(r, list) and r and r[0] == 'last ')
    assert last_run_row[1] == 'macro'
    assert last_run_row[2] == 'last (1 step) [default]'
    assert last_run_row[3] == 'play default slot'


def test_prompt_complete_macro_play_omits_zero_step_named_slots_from_saved_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer(text='')

    ed.set_macro('blank', [])

    ed.enter_prompt('command', prefill='macro play ')
    assert ed.prompt is not None
    assert ed.prompt_complete(direction=1) is False
    assert ed.prompt.suggestions == []
    assert ed.prompt.suggestion_rows == []

    missing_row = ed._prompt_macro_slot_row('blank ', subcommand='play')
    assert missing_row == ['blank ', 'macro', 'missing macro', 'no such macro']



def test_prompt_complete_macro_record_slots_preview_overwrite_and_new_targets() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer(text='')

    new_row = ed._prompt_macro_slot_row('demo ', subcommand='record')
    assert new_row == ['demo ', 'macro', 'new macro slot', 'record new macro']

    default_row = ed._prompt_macro_slot_row('last ', subcommand='record')
    assert default_row == ['last ', 'macro', 'last [default]', 'record default slot']

    assert ed.exec_command_line('macro record demo')
    ed.input['text'] = 'z'
    assert ed.run_action('InsertText')
    assert ed.exec_command_line('macro stop')

    ed.enter_prompt('command', prefill='macro record ')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows

    demo_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'demo ')
    assert demo_row[1] == 'macro'
    assert demo_row[2] == 'demo (1 step)'
    assert demo_row[3] == 'overwrite on save'

    last_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'last ')
    assert last_row[1] == 'macro'
    assert last_row[2] == 'last (1 step) [default]'
    assert last_row[3] == 'overwrite default slot on save'


def test_prompt_complete_macro_slot_rows_report_live_blockers() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer(text='')

    assert ed.exec_command_line('macro record demo')
    ed.input['text'] = 'z'
    assert ed.run_action('InsertText')

    record_row = ed._prompt_macro_slot_row('other ', subcommand='record')
    assert record_row == [
        'other ', 'macro', 'new macro slot',
        'recording · demo (1 step) · stop or cancel first',
    ]

    rec_row = ed._prompt_macro_slot_row('other ', subcommand='rec')
    assert rec_row == [
        'other ', 'macro', 'new macro slot',
        'recording · demo (1 step) · stop or cancel first',
    ]

    start_row = ed._prompt_macro_slot_row('last ', subcommand='start')
    assert start_row == [
        'last ', 'macro', 'last [default]',
        'recording · demo (1 step) · stop or cancel first',
    ]

    recording_play_row = ed._prompt_macro_slot_row('demo ', subcommand='play')
    assert recording_play_row == [
        'demo ', 'macro', 'missing macro',
        'recording · demo (1 step) · stop or cancel first',
    ]

    recording_run_row = ed._prompt_macro_slot_row('demo ', subcommand='run')
    assert recording_run_row == [
        'demo ', 'macro', 'missing macro',
        'recording · demo (1 step) · stop or cancel first',
    ]

    assert ed.exec_command_line('macro stop')
    ed._macro_playing = True
    ed._macro_play_name = 'demo'
    ed._macro_play_steps = 1

    play_row = ed._prompt_macro_slot_row('demo ', subcommand='play')
    assert play_row == [
        'demo ', 'macro', 'demo (1 step)',
        'playing · demo (1 step) · wait for playback',
    ]

    run_row = ed._prompt_macro_slot_row('demo ', subcommand='run')
    assert run_row == [
        'demo ', 'macro', 'demo (1 step)',
        'playing · demo (1 step) · wait for playback',
    ]

    playback_record_row = ed._prompt_macro_slot_row('other ', subcommand='record')
    assert playback_record_row == [
        'other ', 'macro', 'new macro slot',
        'playing · demo (1 step) · wait for playback',
    ]


def test_prompt_complete_macro_play_slot_suggestions_hide_blocked_slots_but_keep_exact_typed_slot() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer(text='')

    assert ed.exec_command_line('macro record demo')
    ed.input['text'] = 'z'
    assert ed.run_action('InsertText')
    assert ed.exec_command_line('macro stop')

    assert ed.exec_command_line('macro record live')
    ed.input['text'] = 'x'
    assert ed.run_action('InsertText')

    ed.enter_prompt('command', prefill='macro play ')
    assert ed.prompt is not None
    assert ed.prompt_complete(direction=1) is False
    assert ed.prompt.suggestions == []
    assert ed.prompt.suggestion_rows == []

    recording_candidates, recording_fuzzy = ed._prompt_command_token_candidates(
        cmd='macro',
        toks=['macro', 'run', 'demo'],
        tok_i=2,
        prefix='demo',
        at_eol=True,
    )
    assert recording_candidates == ['demo ']
    assert recording_fuzzy is False

    recording_rows = ed._prompt_commandish_suggestion_rows(
        cmd='macro',
        toks=['macro', 'run', 'demo'],
        tok_i=2,
        candidates=['demo '],
    )
    assert recording_rows == [[
        'demo ', 'macro', 'demo (1 step)',
        'recording · live (1 step) · stop or cancel first',
    ]]

    assert ed.exec_command_line('macro cancel')

    ed._macro_playing = True
    ed._macro_play_name = 'demo'
    ed._macro_play_steps = 1

    ed.enter_prompt('command', prefill='macro play ')
    assert ed.prompt is not None
    assert ed.prompt_complete(direction=1) is False
    assert ed.prompt.suggestions == []
    assert ed.prompt.suggestion_rows == []

    candidates, fuzzy = ed._prompt_command_token_candidates(
        cmd='macro',
        toks=['macro', 'run', 'demo'],
        tok_i=2,
        prefix='demo',
        at_eol=True,
    )
    assert candidates == ['demo ']
    assert fuzzy is False

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='macro',
        toks=['macro', 'run', 'demo'],
        tok_i=2,
        candidates=['demo '],
    )
    assert rows == [[
        'demo ', 'macro', 'demo (1 step)',
        'playing · demo (1 step) · wait for playback',
    ]]



def test_prompt_complete_macro_record_slot_suggestions_hide_blocked_slots_but_keep_exact_typed_slot() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer(text='')

    assert ed.exec_command_line('macro record demo')
    ed.input['text'] = 'z'
    assert ed.run_action('InsertText')

    ed.enter_prompt('command', prefill='macro record ')
    assert ed.prompt is not None
    assert ed.prompt_complete(direction=1) is False
    assert ed.prompt.suggestions == []
    assert ed.prompt.suggestion_rows == []

    candidates, fuzzy = ed._prompt_command_token_candidates(
        cmd='macro',
        toks=['macro', 'record', 'other'],
        tok_i=2,
        prefix='other',
        at_eol=True,
    )
    assert candidates == ['other ']
    assert fuzzy is False

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='macro',
        toks=['macro', 'record', 'other'],
        tok_i=2,
        candidates=['other '],
    )
    assert rows == [[
        'other ', 'macro', 'new macro slot',
        'recording · demo (1 step) · stop or cancel first',
    ]]



def test_prompt_complete_macro_count_rows_preview_repeat_validation_and_blockers() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer(text='')

    empty_last_row = ed._prompt_macro_count_row('2 ', subcommand='play', slot_name='last')
    assert empty_last_row == ['2 ', 'count', '0 steps [default]', 'default slot empty']

    empty_last_run_row = ed._prompt_macro_count_row('3 ', subcommand='run', slot_name='last')
    assert empty_last_run_row == ['3 ', 'count', '0 steps [default]', 'default slot empty']

    empty_last_bad_int = ed._prompt_macro_count_row('oops ', subcommand='play', slot_name='last')
    assert empty_last_bad_int == ['oops ', 'count', '0 steps [default]', 'count must be an int']

    missing_bad_int = ed._prompt_macro_count_row('oops ', subcommand='play', slot_name='ghost')
    assert missing_bad_int == ['oops ', 'count', 'missing macro', 'count must be an int']

    empty_last_zero = ed._prompt_macro_count_row('0 ', subcommand='run', slot_name='last')
    assert empty_last_zero == ['0 ', 'count', '0 steps [default]', 'count must be > 0']

    missing_zero = ed._prompt_macro_count_row('0 ', subcommand='run', slot_name='ghost')
    assert missing_zero == ['0 ', 'count', 'missing macro', 'count must be > 0']

    assert ed.exec_command_line('macro record demo')
    ed.input['text'] = 'z'
    assert ed.run_action('InsertText')
    assert ed.exec_command_line('macro stop')

    play_row = ed._prompt_macro_count_row('3 ', subcommand='play', slot_name='demo')
    assert play_row == ['3 ', 'count', 'demo (1 step)', 'play 3x']

    run_row = ed._prompt_macro_count_row('2 ', subcommand='run', slot_name='demo')
    assert run_row == ['2 ', 'count', 'demo (1 step)', 'play 2x']

    last_row = ed._prompt_macro_count_row('2 ', subcommand='play', slot_name='last')
    assert last_row == ['2 ', 'count', 'last (1 step) [default]', 'play default slot 2x']

    bad_int_row = ed._prompt_macro_count_row('oops ', subcommand='play', slot_name='demo')
    assert bad_int_row == ['oops ', 'count', 'demo (1 step)', 'count must be an int']

    zero_row = ed._prompt_macro_count_row('0 ', subcommand='play', slot_name='demo')
    assert zero_row == ['0 ', 'count', 'demo (1 step)', 'count must be > 0']

    missing_row = ed._prompt_macro_count_row('3 ', subcommand='play', slot_name='ghost')
    assert missing_row == ['3 ', 'count', 'missing macro', 'no such macro']

    assert ed.exec_command_line('macro record live')
    ed.input['text'] = 'x'
    assert ed.run_action('InsertText')
    recording_blocked_row = ed._prompt_macro_count_row('4 ', subcommand='run', slot_name='demo')
    assert recording_blocked_row == [
        '4 ', 'count', 'demo (1 step)',
        'recording · live (1 step) · stop or cancel first',
    ]
    recording_missing_row = ed._prompt_macro_count_row('4 ', subcommand='run', slot_name='ghost')
    assert recording_missing_row == [
        '4 ', 'count', 'missing macro',
        'recording · live (1 step) · stop or cancel first',
    ]
    assert ed.exec_command_line('macro cancel')

    ed._macro_playing = True
    ed._macro_play_name = 'demo'
    ed._macro_play_steps = 1
    blocked_row = ed._prompt_macro_count_row('4 ', subcommand='run', slot_name='demo')
    assert blocked_row == [
        '4 ', 'count', 'demo (1 step)',
        'playing · demo (1 step) · wait for playback',
    ]
    blocked_missing_row = ed._prompt_macro_count_row('4 ', subcommand='run', slot_name='ghost')
    assert blocked_missing_row == [
        '4 ', 'count', 'missing macro',
        'playing · demo (1 step) · wait for playback',
    ]



def test_prompt_complete_macro_play_count_suggestions_offer_common_counts_for_known_slots() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer(text='')

    assert ed.exec_command_line('macro record demo')
    ed.input['text'] = 'z'
    assert ed.run_action('InsertText')
    assert ed.exec_command_line('macro stop')

    ed.enter_prompt('command', prefill='macro play demo ')
    assert ed.prompt is not None
    assert ed.prompt_complete(direction=1)
    assert ed.prompt.suggestions[:5] == ['1 ', '2 ', '3 ', '5 ', '10 ']
    rows = ed.prompt.suggestion_rows
    one_row = next(r for r in rows if isinstance(r, list) and r and r[0] == '1 ')
    assert one_row == ['1 ', 'count', 'demo (1 step)', 'play 1x']
    ten_row = next(r for r in rows if isinstance(r, list) and r and r[0] == '10 ')
    assert ten_row == ['10 ', 'count', 'demo (1 step)', 'play 10x']

    ed.enter_prompt('command', prefill='macro run ghost ')
    assert ed.prompt is not None
    assert ed.prompt_complete(direction=1) is False
    assert ed.prompt.suggestion_rows == []


def test_prompt_complete_macro_play_count_suggestions_hide_blocked_repeats_but_keep_exact_typed_count() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer(text='')

    assert ed.exec_command_line('macro record demo')
    ed.input['text'] = 'z'
    assert ed.run_action('InsertText')
    assert ed.exec_command_line('macro stop')

    assert ed.exec_command_line('macro record live')
    ed.input['text'] = 'x'
    assert ed.run_action('InsertText')

    ed.enter_prompt('command', prefill='macro play demo ')
    assert ed.prompt is not None
    assert ed.prompt_complete(direction=1) is False
    assert ed.prompt.suggestions == []
    assert ed.prompt.suggestion_rows == []

    recording_candidates, recording_fuzzy = ed._prompt_command_token_candidates(
        cmd='macro',
        toks=['macro', 'run', 'demo', '2'],
        tok_i=3,
        prefix='2',
        at_eol=True,
    )
    assert recording_candidates == ['2 ']
    assert recording_fuzzy is False

    recording_rows = ed._prompt_commandish_suggestion_rows(
        cmd='macro',
        toks=['macro', 'run', 'demo', '2'],
        tok_i=3,
        candidates=['2 '],
    )
    assert recording_rows == [[
        '2 ', 'count', 'demo (1 step)',
        'recording · live (1 step) · stop or cancel first',
    ]]

    assert ed.exec_command_line('macro cancel')

    ed._macro_playing = True
    ed._macro_play_name = 'demo'
    ed._macro_play_steps = 1

    ed.enter_prompt('command', prefill='macro play demo ')
    assert ed.prompt is not None
    assert ed.prompt_complete(direction=1) is False
    assert ed.prompt.suggestions == []
    assert ed.prompt.suggestion_rows == []

    candidates, fuzzy = ed._prompt_command_token_candidates(
        cmd='macro',
        toks=['macro', 'run', 'demo', '2'],
        tok_i=3,
        prefix='2',
        at_eol=True,
    )
    assert candidates == ['2 ']
    assert fuzzy is False

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='macro',
        toks=['macro', 'run', 'demo', '2'],
        tok_i=3,
        candidates=['2 '],
    )
    assert rows == [[
        '2 ', 'count', 'demo (1 step)',
        'playing · demo (1 step) · wait for playback',
    ]]



def test_prompt_complete_unknown_macro_subcommand_stays_visible_before_enter() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer(text='')

    assert ed._prompt_macro_command_row('nope ', subcommand='nope') == [
        'nope ', 'subcommand', 'missing subcommand', 'no such subcommand: nope'
    ]

    candidates, fuzzy = ed._prompt_command_token_candidates(
        cmd='macro',
        toks=['macro', 'nope'],
        tok_i=1,
        prefix='nope',
        at_eol=True,
    )
    assert candidates == ['nope ']
    assert fuzzy is False

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='macro',
        toks=['macro', 'nope'],
        tok_i=1,
        candidates=['nope '],
    )
    assert rows == [['nope ', 'subcommand', 'missing subcommand', 'no such subcommand: nope']]

    ed.enter_prompt('command', prefill='macro nope')
    assert ed.prompt is not None
    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == 'macro nope '
    assert ed.prompt.suggestions == []
    assert ed.prompt.suggestion_rows == []


def test_prompt_complete_macro_extra_arg_rows_show_arity_contracts() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer(text='')

    noarg_rows = ed._prompt_commandish_suggestion_rows(
        cmd='macro',
        toks=['macro', 'stop', 'now'],
        tok_i=2,
        candidates=['now '],
    )
    noarg_row = next(r for r in noarg_rows if isinstance(r, list) and r and r[0] == 'now ')
    assert noarg_row == ['now ', 'arg', 'macro stop', 'takes no args']

    record_rows = ed._prompt_commandish_suggestion_rows(
        cmd='macro',
        toks=['macro', 'record', 'demo', 'extra'],
        tok_i=3,
        candidates=['extra '],
    )
    record_row = next(r for r in record_rows if isinstance(r, list) and r and r[0] == 'extra ')
    assert record_row == ['extra ', 'arg', 'macro record [NAME]', 'takes at most 1 arg']

    run_rows = ed._prompt_commandish_suggestion_rows(
        cmd='macro',
        toks=['macro', 'run', 'demo', '2', 'extra'],
        tok_i=4,
        candidates=['extra '],
    )
    run_row = next(r for r in run_rows if isinstance(r, list) and r and r[0] == 'extra ')
    assert run_row == ['extra ', 'arg', 'macro run [NAME] [COUNT]', 'takes at most 2 args']


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
    assert '00-vision.md · ' in str(row[3])
    assert ':' in str(row[3])


def test_prompt_complete_showhelpnav_command_previews_live_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.open_help_doc('help-browser') is True

    rows = ed._prompt_suggestion_rows(
        cmd='',
        toks=['showhelpnav'],
        tok_i=0,
        candidates=['showhelpnav '],
        path_mode=False,
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showhelpnav ')
    assert row[1] == 'command'
    assert row[2] == 'showhelpnav [QUERY] - show count-aware current-doc navigation sections'
    assert row[3] == ed._showhelpnav_preview_summary()
    assert 'section(s), ' in row[3]
    assert 'help target' in row[3]
    assert 'Top: ' in row[3]



def test_prompt_complete_showhelpnav_command_previews_typed_blocker() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', 'plain text only\n')

    rows = ed._prompt_suggestion_rows(
        cmd='',
        toks=['showhelpnav'],
        tok_i=0,
        candidates=['showhelpnav '],
        path_mode=False,
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showhelpnav ')
    assert row[1] == 'command'
    assert row[2] == 'showhelpnav [QUERY] - show count-aware current-doc navigation sections'
    assert row[3] == 'not in a docs buffer'


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
    assert ' · ' in str(row[3])


def test_prompt_complete_showtopics_uses_richer_topic_section_summary_detail() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.enter_prompt('command', prefill='showtopics ')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'Words ')
    assert row[1] == 'topic-group'
    assert 'topic' in str(row[2]) and '(e.g. ' in str(row[2])
    assert 'primitive wl=' in str(row[3])
    assert ' · ' in str(row[3])


def test_prompt_complete_recent_group_commands_use_neutral_leading_section_previews(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    (tmp_path / 'pyproject.toml').write_text('[project]\nname = "demo"\n', encoding='utf-8')
    guide = tmp_path / 'guide' / 'intro.md'
    notes = tmp_path / 'notes' / 'daily.txt'
    guide.parent.mkdir(parents=True)
    notes.parent.mkdir(parents=True)
    guide.write_text('guide\n', encoding='utf-8')
    notes.write_text('notes\n', encoding='utf-8')
    ed.open_file(str(guide))
    ed.open_file(str(notes))

    ed.enter_prompt('command', prefill='showr')
    assert ed.prompt is not None
    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    recent_groups_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showrecentgroups ')
    assert recent_groups_row[1] == 'command'
    assert f'{tmp_path}: 2' in str(recent_groups_row[3])
    assert 'latest ' not in str(recent_groups_row[3])

    ed.enter_prompt('command', prefill='showrecentd')
    assert ed.prompt is not None
    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    recent_dir_groups_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showrecentdirgroups ')
    assert recent_dir_groups_row[1] == 'command'
    assert f'{notes.parent}: 1' in str(recent_dir_groups_row[3])
    assert 'latest ' not in str(recent_dir_groups_row[3])


def test_prompt_complete_group_summary_commands_use_neutral_leading_section_previews() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.enter_prompt('command', prefill='showt')
    assert ed.prompt is not None
    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    topic_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showtopics ')
    assert topic_row[1] == 'command'
    assert topic_row[3].startswith('4 section(s), ')
    command_count = len(list(ed.command_dispatcher.names()))
    assert f'Commands: {command_count}' in str(topic_row[3])
    assert 'latest ' not in str(topic_row[3])

    ed.enter_prompt('command', prefill='showd')
    assert ed.prompt is not None
    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    docs_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showdocs ')
    assert docs_row[1] == 'command'
    assert '00–09 Project: 3' in str(docs_row[3])
    assert 'latest ' not in str(docs_row[3])

    assert ed.open_help_doc('help-browser') is True
    ed.enter_prompt('command', prefill='showh')
    assert ed.prompt is not None
    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    helpnav_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showhelpnav ')
    assert helpnav_row[1] == 'command'
    assert 'Top: 1' in str(helpnav_row[3])
    assert 'latest ' not in str(helpnav_row[3])


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


def test_prompt_complete_showjumpgroups_uses_jump_section_summary_metadata() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('alpha', 'one\ntwo\nthree\n')
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

    ed.enter_prompt('command', prefill='showjumpgroups Cu')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == 'showjumpgroups Current '

    ed.enter_prompt('command', prefill='showjumpgroups ')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'Current ')
    assert row[1] == 'jump-group'
    assert row[2] == '1 jump (e.g. #2)'
    assert row[3] == 'alpha @ 2:1 — two'


def test_prompt_complete_markpick_command_previews_empty_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='',
        toks=[],
        tok_i=0,
        candidates=['markpick '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'markpick ')
    assert row[1] == 'command'
    assert row[2] == 'markpick [QUERY] - open searchable mark picker'
    assert row[3] == '0 section(s), 0 marks'


def test_prompt_complete_markpick_command_previews_current_sections() -> None:
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

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='',
        toks=[],
        tok_i=0,
        candidates=['markpick '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'markpick ')
    assert row[1] == 'command'
    assert row[2] == 'markpick [QUERY] - open searchable mark picker'
    assert row[3] == '2 section(s), 3 marks · beta: 1 | e.g. there — other'


def test_prompt_complete_marks_command_previews_live_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer("alpha", "zero\n  target  \n")
    ed._normalize_cursor_lists(ed.cur())
    ed.cur().cursors[ed.cur().primary].line = 1
    ed.cur().cursors[ed.cur().primary].col = 0
    assert ed.mark_set("here") is True

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='',
        toks=[],
        tok_i=0,
        candidates=['marks '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'marks ')
    assert row[1] == 'command'
    assert row[2] == 'marks - list marks'
    assert row[3] == ed._mark_inventory_preview_summary()
    assert 'here -> alpha [active, here] @ 2:0' in row[3]
    assert 'target' in row[3]


def test_prompt_complete_showmark_command_previews_live_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer("alpha", "zero\n  target  \n")
    ed._normalize_cursor_lists(ed.cur())
    ed.cur().cursors[ed.cur().primary].line = 1
    ed.cur().cursors[ed.cur().primary].col = 0
    assert ed.mark_set("here") is True

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='',
        toks=[],
        tok_i=0,
        candidates=['showmark '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showmark ')
    assert row[1] == 'command'
    assert row[2] == 'showmark NAME - show exact mark state without jumping'
    assert row[3] == ed._mark_inventory_preview_summary()
    assert 'here -> alpha [active, here] @ 2:0' in row[3]
    assert 'target' in row[3]



def test_prompt_complete_mark_and_markjump_commands_preview_live_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer("alpha", "zero\n  target  \n")
    ed._normalize_cursor_lists(ed.cur())
    ed.cur().cursors[ed.cur().primary].line = 1
    ed.cur().cursors[ed.cur().primary].col = 0
    assert ed.mark_set("here") is True

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='',
        toks=[],
        tok_i=0,
        candidates=['mark ', 'markjump '],
    )
    mark_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'mark ')
    assert mark_row[1] == 'command'
    assert mark_row[2] == 'mark NAME - set a named mark at the primary cursor'
    assert mark_row[3] == ed._mark_inventory_preview_summary()
    assert 'here -> alpha [active, here] @ 2:0' in mark_row[3]
    assert 'target' in mark_row[3]

    jump_row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'markjump ')
    assert jump_row[1] == 'command'
    assert jump_row[2] == 'markjump NAME - jump to a named mark'
    assert jump_row[3] == ed._mark_inventory_preview_summary()
    assert 'here -> alpha [active, here] @ 2:0' in jump_row[3]
    assert 'target' in jump_row[3]


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


def test_prompt_complete_showjump_hash_slot_uses_exact_jump_metadata() -> None:
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

    ed.enter_prompt('command', prefill='showjump #')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == '#1 ')
    assert row[1] == 'jump'
    assert row[2] == 'back 1 a @ 1:0'
    assert row[3] == 'one'



def test_prompt_complete_jumppick_uses_exact_jump_metadata() -> None:
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

    ed.enter_prompt('command', prefill='jumppick ')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == '1 ')
    assert row[1] == 'jump'
    assert row[2] == 'back 1 a @ 1:0'
    assert row[3] == 'one'


def test_prompt_complete_jumppick_hash_slot_uses_exact_jump_metadata() -> None:
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

    ed.enter_prompt('command', prefill='jumppick #')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == '#1 ')
    assert row[1] == 'jump'
    assert row[2] == 'back 1 a @ 1:0'
    assert row[3] == 'one'


def test_prompt_complete_jump_navigation_commands_preview_exact_next_jump_target() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'one\ntwo\nthree\nfour\nfive\n')
    ed._normalize_cursor_lists(ed.cur())
    ed.cur().cursors[ed.cur().primary].line = 0
    ed.cur().cursors[ed.cur().primary].col = 0
    assert ed.push_jump() is True
    ed.cur().cursors[ed.cur().primary].line = 1
    ed.cur().cursors[ed.cur().primary].col = 1
    assert ed.push_jump() is True
    ed.cur().cursors[ed.cur().primary].line = 4
    ed.cur().cursors[ed.cur().primary].col = 0
    assert ed.push_jump() is True
    assert ed.jump_to_index(1) is True

    ed.enter_prompt('command', prefill='jump')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    back = next(r for r in rows if isinstance(r, list) and r and r[0] == 'jumpback ')
    assert back[1] == 'command'
    assert back[2] == 'jumpback - jump to the previous jumplist entry'
    assert back[3] == 'next #1 [back 1] a @ 1:0'
    forward = next(r for r in rows if isinstance(r, list) and r and r[0] == 'jumpforward ')
    assert forward[1] == 'command'
    assert forward[2] == 'jumpforward - jump to the next jumplist entry'
    assert forward[3] == 'next #3 [forward 1] a @ 5:0'


def test_prompt_complete_jump_navigation_commands_preview_explicit_noop_state() -> None:
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
    assert ed.jump_to_index(0) is True

    ed.enter_prompt('command', prefill='jump')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    back = next(r for r in rows if isinstance(r, list) and r and r[0] == 'jumpback ')
    assert back[3] == 'no earlier jump'
    forward = next(r for r in rows if isinstance(r, list) and r and r[0] == 'jumpforward ')
    assert forward[3] == 'next #2 [forward 1] a @ 2:1'


def test_prompt_complete_jumppick_command_previews_current_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'one\ntwo\nthree\nfour\nfive\n')
    ed._normalize_cursor_lists(ed.cur())
    ed.cur().cursors[ed.cur().primary].line = 0
    ed.cur().cursors[ed.cur().primary].col = 0
    assert ed.push_jump() is True
    ed.cur().cursors[ed.cur().primary].line = 1
    ed.cur().cursors[ed.cur().primary].col = 1
    assert ed.push_jump() is True
    ed.cur().cursors[ed.cur().primary].line = 4
    ed.cur().cursors[ed.cur().primary].col = 0
    assert ed.push_jump() is True
    assert ed.jump_to_index(1) is True

    ed.enter_prompt('command', prefill='jum')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'jumppick ')
    assert row[1] == 'command'
    assert row[2] == 'jumppick [QUERY|N|#N] - open searchable jumplist picker or jump to visible slot'
    assert row[3] == '3 jumps · current #2 [current] a @ 2:1'



def test_prompt_complete_jumppick_command_previews_empty_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'one\n')
    ed.enter_prompt('command', prefill='jum')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'jumppick ')
    assert row[3] == '0 jumps'




def test_prompt_complete_recent_command_previews_current_inventory(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    a = tmp_path / 'a.txt'
    b = tmp_path / 'b.txt'
    a.write_text('A\n', encoding='utf-8')
    b.write_text('B\n', encoding='utf-8')
    ed.open_file(str(a))
    ed.open_file(str(b))

    ed.enter_prompt('command', prefill='recent')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'recent ')
    assert row[1] == 'command'
    assert row[2] == 'recent [N|#N|clear] - show/open recent files'
    assert row[3] == f'2 recent files · latest *{b} @ 1:0 | current buffer'



def test_prompt_complete_recent_command_previews_empty_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'one\n')
    ed.enter_prompt('command', prefill='recent')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'recent ')
    assert row[2] == 'recent [N|#N|clear] - show/open recent files'
    assert row[3] == '0 recent files'



def test_prompt_complete_recentpick_command_previews_current_inventory(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    (tmp_path / 'pyproject.toml').write_text('[project]\nname = "demo"\n', encoding='utf-8')
    guide = tmp_path / 'guide' / 'intro.md'
    notes = tmp_path / 'notes' / 'daily.txt'
    guide.parent.mkdir(parents=True)
    notes.parent.mkdir(parents=True)
    guide.write_text('guide\n', encoding='utf-8')
    notes.write_text('notes\n', encoding='utf-8')
    ed.open_file(str(guide))
    ed.open_file(str(notes))

    ed.enter_prompt('command', prefill='recent')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'recentpick ')
    assert row[1] == 'command'
    assert row[2] == 'recentpick [QUERY] - open searchable recent file picker'
    assert row[3] == f'2 recent files · latest {tmp_path.name} #1 [active] @ 1:0 — notes/daily.txt | current buffer'



def test_prompt_complete_recentpick_command_previews_empty_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'one\n')
    ed.enter_prompt('command', prefill='recent')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'recentpick ')
    assert row[2] == 'recentpick [QUERY] - open searchable recent file picker'
    assert row[3] == '0 recent files'



def test_prompt_complete_recentdirpick_command_previews_current_inventory(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    alpha = tmp_path / 'proj' / 'src' / 'alpha.txt'
    beta = tmp_path / 'proj' / 'tests' / 'beta.txt'
    gamma = tmp_path / 'proj' / 'tests' / 'gamma.txt'
    alpha.parent.mkdir(parents=True)
    beta.parent.mkdir(parents=True)
    alpha.write_text('alpha\n', encoding='utf-8')
    beta.write_text('beta\n', encoding='utf-8')
    gamma.write_text('gamma\n', encoding='utf-8')
    ed.open_file(str(alpha))
    ed.open_file(str(beta))
    ed.open_file(str(gamma))

    ed.enter_prompt('command', prefill='recent')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'recentdirpick ')
    assert row[1] == 'command'
    assert row[2] == 'recentdirpick [QUERY] - open searchable recent file picker grouped by directory'
    assert row[3] == f'3 recent files in 2 directories · latest gamma.txt #1 [active] @ 1:0 — {beta.parent} | current buffer'



def test_prompt_complete_recentdirpick_command_previews_empty_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'one\n')
    ed.enter_prompt('command', prefill='recent')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'recentdirpick ')
    assert row[2] == 'recentdirpick [QUERY] - open searchable recent file picker grouped by directory'
    assert row[3] == '0 recent files'



def test_prompt_complete_showrecent_command_previews_latest_visible_slot(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    p = tmp_path / 'demo.txt'
    q = tmp_path / 'other.txt'
    p.write_text('demo\n', encoding='utf-8')
    q.write_text('other\n', encoding='utf-8')
    ed.open_file(str(p))
    ed.open_file(str(q))

    ed.enter_prompt('command', prefill='showr')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showrecent ')
    assert row[1] == 'command'
    assert row[2] == 'showrecent PATH|N|#N - show exact recent-file state without opening'
    assert row[3] == f'{ed._recent_inventory_preview_summary()} · expects PATH|N|#N'



def test_prompt_complete_showrecent_command_previews_empty_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'one\n')
    ed.enter_prompt('command', prefill='showr')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showrecent ')
    assert row[2] == 'showrecent PATH|N|#N - show exact recent-file state without opening'
    assert row[3] == f'{ed._recent_inventory_preview_summary()} · expects PATH|N|#N'


def test_prompt_complete_showrecentdir_command_previews_latest_visible_bucket(tmp_path: Path) -> None:
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

    ed.enter_prompt('command', prefill='showr')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showrecentdir ')
    assert row[1] == 'command'
    assert row[2] == 'showrecentdir DIR|N|#N - show exact recent-directory bucket state without opening'
    assert row[3] == f'{ed._recent_dir_inventory_preview_summary()} · expects DIR|N|#N'



def test_prompt_complete_showrecentdir_command_previews_empty_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'one\n')
    ed.enter_prompt('command', prefill='showr')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showrecentdir ')
    assert row[2] == 'showrecentdir DIR|N|#N - show exact recent-directory bucket state without opening'
    assert row[3] == f'{ed._recent_dir_inventory_preview_summary()} · expects DIR|N|#N'



def test_prompt_complete_showrecentgroups_query_miss_previews_zero_summary() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'one\n')
    rows = ed._prompt_suggestion_rows(
        cmd='showrecentgroups',
        toks=['showrecentgroups', 'zzz-no-such-recent-file'],
        tok_i=1,
        candidates=['zzz-no-such-recent-file '],
        path_mode=False,
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'zzz-no-such-recent-file ')
    assert row[1] == 'recent-group'
    assert row[2] == ''
    assert row[3] == '0 section(s), 0 files'


def test_prompt_complete_showrecentgroups_command_previews_group_inventory(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    (tmp_path / 'pyproject.toml').write_text('[project]\nname = "demo"\n', encoding='utf-8')
    guide = tmp_path / 'guide' / 'intro.md'
    notes = tmp_path / 'notes' / 'daily.txt'
    guide.parent.mkdir(parents=True)
    notes.parent.mkdir(parents=True)
    guide.write_text('guide\n', encoding='utf-8')
    notes.write_text('notes\n', encoding='utf-8')
    ed.open_file(str(guide))
    ed.open_file(str(notes))

    ed.enter_prompt('command', prefill='showr')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showrecentgroups ')
    assert row[1] == 'command'
    assert row[2] == 'showrecentgroups [QUERY] - show count-aware recent file buckets'
    assert row[3] == f'1 section(s), 2 files · {tmp_path}: 2 | e.g. daily.txt #1 [active] @ 1:0 — notes/daily.txt | current buffer'
    assert 'latest ' not in str(row[3])



def test_prompt_complete_showrecentgroups_command_previews_empty_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'one\n')
    ed.enter_prompt('command', prefill='showr')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showrecentgroups ')
    assert row[2] == 'showrecentgroups [QUERY] - show count-aware recent file buckets'
    assert row[3] == '0 section(s), 0 files'
    assert 'latest ' not in str(row[3])


def test_prompt_complete_showrecentdirgroups_query_miss_previews_zero_summary() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'one\n')
    rows = ed._prompt_suggestion_rows(
        cmd='showrecentdirgroups',
        toks=['showrecentdirgroups', 'zzz-no-such-recent-file'],
        tok_i=1,
        candidates=['zzz-no-such-recent-file '],
        path_mode=False,
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'zzz-no-such-recent-file ')
    assert row[1] == 'recentdir-group'
    assert row[2] == ''
    assert row[3] == '0 section(s), 0 files'


def test_prompt_complete_showrecentdirgroups_command_previews_group_inventory(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    alpha = tmp_path / 'proj' / 'src' / 'alpha.txt'
    beta = tmp_path / 'proj' / 'tests' / 'beta.txt'
    gamma = tmp_path / 'proj' / 'tests' / 'gamma.txt'
    alpha.parent.mkdir(parents=True)
    beta.parent.mkdir(parents=True)
    alpha.write_text('alpha\n', encoding='utf-8')
    beta.write_text('beta\n', encoding='utf-8')
    gamma.write_text('gamma\n', encoding='utf-8')
    ed.open_file(str(alpha))
    ed.open_file(str(beta))
    ed.open_file(str(gamma))

    ed.enter_prompt('command', prefill='showr')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showrecentdirgroups ')
    assert row[1] == 'command'
    assert row[2] == 'showrecentdirgroups [QUERY] - show count-aware recent directory buckets'
    assert row[3] == f'2 section(s), 3 files · {beta.parent}: 2 | e.g. gamma.txt #1 [active] @ 1:0 — current buffer'
    assert 'latest ' not in str(row[3])



def test_prompt_complete_showrecentdirgroups_command_previews_empty_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'one\n')
    ed.enter_prompt('command', prefill='showr')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showrecentdirgroups ')
    assert row[2] == 'showrecentdirgroups [QUERY] - show count-aware recent directory buckets'
    assert row[3] == '0 section(s), 0 files'
    assert 'latest ' not in str(row[3])
    assert 'latest ' not in str(row[3])


def test_prompt_complete_showstatus_command_previews_portable_summary() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'one\n')
    ed.cur().buf.dirty = True
    ed.enter_prompt('command', prefill='show')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showstatus ')
    assert row[1] == 'command'
    assert row[2] == 'showstatus - show portable statusline summary'
    assert row[3] == "mode=normal buffer='a' dirty=1 readonly=0 pos=1:1 cursors=1/1 sels=0 selchars=0"
    assert 'prompt=' not in row[3]




def test_prompt_complete_urlopen_command_previews_capability_blocked_current_url() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('*scratch*', 'see https://example.com/blocked')
    buf = ed.cur()
    ed._normalize_cursor_lists(buf)
    buf.cursors[buf.primary].line = 0
    buf.cursors[buf.primary].col = 8

    ed.enter_prompt('command', prefill='url')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'urlopen ')
    assert row[1] == 'command'
    assert row[2] == 'urlopen [URL] - open URL under cursor (or explicit URL) [cap.open-url]'
    assert row[3] == 'disabled (cap.open-url) · https://example.com/blocked'



def test_prompt_complete_openurl_alias_previews_confirmed_current_url() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('*scratch*', 'see https://example.com/confirm')
    buf = ed.cur()
    ed._normalize_cursor_lists(buf)
    buf.cursors[buf.primary].line = 0
    buf.cursors[buf.primary].col = 8
    ed.options.set('cap.open-url', 'true')

    ed.enter_prompt('command', prefill='open')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'openurl ')
    assert row[1] == 'command'
    assert row[2] == 'openurl [URL] - alias for urlopen'
    assert row[3] == 'https://example.com/confirm [confirm]'



def test_prompt_complete_urlcopy_command_previews_current_url() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('*scratch*', 'see https://example.com/copy')
    buf = ed.cur()
    ed._normalize_cursor_lists(buf)
    buf.cursors[buf.primary].line = 0
    buf.cursors[buf.primary].col = 8

    ed.enter_prompt('command', prefill='url')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'urlcopy ')
    assert row[1] == 'command'
    assert row[2] == 'urlcopy [URL] - copy URL under cursor (or explicit URL)'
    assert row[3] == 'https://example.com/copy'



def test_prompt_complete_urlcopy_command_previews_typed_blocker() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('*scratch*', 'plain text only')
    ed.enter_prompt('command', prefill='url')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'urlcopy ')
    assert row[2] == 'urlcopy [URL] - copy URL under cursor (or explicit URL)'
    assert row[3] == 'no url under cursor'


def test_prompt_complete_showhelpheading_command_previews_current_heading() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    assert ed.open_help_doc('helpoutline-section-groups') is True
    eb = ed.cur()
    want_line = next(i for i, line in enumerate(eb.buf.lines) if 'inside one generic `Headings` bucket.' in line)
    ed._normalize_cursor_lists(eb)
    eb.cursors[eb.primary].line = want_line
    eb.cursors[eb.primary].col = 2

    ed.enter_prompt('command', prefill='showhelp')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showhelpheading ')
    assert row[1] == 'command'
    assert row[2] == 'showhelpheading - show current docs heading under cursor'
    assert row[3].startswith('Links @helpoutline-section-groups [h3] [section Help outline section groups › Guide] [#links] @ ')


def test_prompt_complete_showhelpheading_command_previews_typed_blocker() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('*scratch*', '')
    ed.enter_prompt('command', prefill='showhelp')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showhelpheading ')
    assert row[2] == 'showhelpheading - show current docs heading under cursor'
    assert row[3] == 'not in a docs buffer'


def test_prompt_complete_showhelplink_command_previews_current_link() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    assert ed.open_help_doc('help-browser') is True
    lines = ed.cur().buf.lines
    line_i = next(i for i, line in enumerate(lines) if 'micro editor' in line)
    col_i = lines[line_i].index('micro editor') + 2
    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    eb.cursors[eb.primary].line = line_i
    eb.cursors[eb.primary].col = col_i

    ed.enter_prompt('command', prefill='showhelp')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showhelplink ')
    assert row[1] == 'command'
    assert row[2] == 'showhelplink - show current docs-link target under cursor'
    assert row[3].startswith('micro editor @help-browser [external] [section External links] -> https://micro-editor.github.io/ @ ')


def test_prompt_complete_showhelplink_command_previews_typed_blocker() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('*scratch*', '')
    ed.enter_prompt('command', prefill='showhelp')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showhelplink ')
    assert row[2] == 'showhelplink - show current docs-link target under cursor'
    assert row[3] == 'not in a docs buffer'


def test_prompt_complete_helpfollow_command_previews_current_link() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    assert ed.open_help_doc('help-browser') is True
    lines = ed.cur().buf.lines
    line_i = next(i for i, line in enumerate(lines) if 'micro editor' in line)
    col_i = lines[line_i].index('micro editor') + 2
    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    eb.cursors[eb.primary].line = line_i
    eb.cursors[eb.primary].col = col_i

    ed.enter_prompt('command', prefill='helpfo')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'helpfollow ')
    assert row[1] == 'command'
    assert row[2] == 'helpfollow - follow a markdown link under cursor in docs help'
    assert row[3].startswith('micro editor @help-browser [external] [section External links] -> https://micro-editor.github.io/ @ ')


def test_prompt_complete_helpfollow_command_previews_typed_blocker() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('*scratch*', '')
    ed.enter_prompt('command', prefill='helpfo')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'helpfollow ')
    assert row[2] == 'helpfollow - follow a markdown link under cursor in docs help'
    assert row[3] == 'not in a docs buffer'


def test_prompt_complete_helplinkcopy_command_previews_current_link() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    assert ed.open_help_doc('help-browser') is True
    lines = ed.cur().buf.lines
    line_i = next(i for i, line in enumerate(lines) if 'micro editor' in line)
    col_i = lines[line_i].index('micro editor') + 2
    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    eb.cursors[eb.primary].line = line_i
    eb.cursors[eb.primary].col = col_i

    ed.enter_prompt('command', prefill='helpl')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'helplinkcopy ')
    assert row[1] == 'command'
    assert row[2] == 'helplinkcopy - copy markdown link target under cursor in docs help'
    assert row[3].startswith('micro editor @help-browser [external] [section External links] -> https://micro-editor.github.io/ @ ')



def test_prompt_complete_helplinkcopy_command_previews_typed_blocker() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('*scratch*', '')
    ed.enter_prompt('command', prefill='helpl')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'helplinkcopy ')
    assert row[2] == 'helplinkcopy - copy markdown link target under cursor in docs help'
    assert row[3] == 'not in a docs buffer'


def test_prompt_complete_helpcopylink_alias_previews_current_link() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    assert ed.open_help_doc('help-browser') is True
    lines = ed.cur().buf.lines
    line_i = next(i for i, line in enumerate(lines) if 'micro editor' in line)
    col_i = lines[line_i].index('micro editor') + 2
    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    eb.cursors[eb.primary].line = line_i
    eb.cursors[eb.primary].col = col_i

    ed.enter_prompt('command', prefill='help')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'helpcopylink ')
    assert row[1] == 'command'
    assert row[2] == 'helpcopylink - alias for helplinkcopy'
    assert row[3].startswith('micro editor @help-browser [external] [section External links] -> https://micro-editor.github.io/ @ ')



def test_prompt_complete_helpcopylink_alias_previews_typed_blocker() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('*scratch*', '')
    ed.enter_prompt('command', prefill='help')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'helpcopylink ')
    assert row[2] == 'helpcopylink - alias for helplinkcopy'
    assert row[3] == 'not in a docs buffer'


def test_prompt_complete_helpback_command_previews_next_history_target() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    assert ed.open_help_doc('help-browser') is True
    ed._normalize_cursor_lists(ed.cur())
    ed.cur().cursors[ed.cur().primary].line = 7
    ed.cur().cursors[ed.cur().primary].col = 3
    assert ed.open_help_doc('vision') is True

    ed.enter_prompt('command', prefill='help')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'helpback ')
    assert row[1] == 'command'
    assert row[2] == 'helpback - go back in docs help navigation'
    assert row[3] == 'next help-browser @ 8:3'


def test_prompt_complete_helpback_command_previews_empty_history() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.enter_prompt('command', prefill='help')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'helpback ')
    assert row[2] == 'helpback - go back in docs help navigation'
    assert row[3] == 'back stack empty'


def test_prompt_complete_helpforward_command_previews_next_history_target() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    assert ed.open_help_doc('help-browser') is True
    ed._normalize_cursor_lists(ed.cur())
    ed.cur().cursors[ed.cur().primary].line = 7
    ed.cur().cursors[ed.cur().primary].col = 3
    assert ed.open_help_doc('vision') is True
    assert ed.exec_command_line('helpback') is True

    ed.enter_prompt('command', prefill='helpf')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'helpforward ')
    assert row[1] == 'command'
    assert row[2] == 'helpforward - go forward in docs help navigation'
    assert row[3] == 'next vision @ 1:0'


def test_prompt_complete_helpforward_command_previews_empty_history() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.enter_prompt('command', prefill='helpf')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'helpforward ')
    assert row[2] == 'helpforward - go forward in docs help navigation'
    assert row[3] == 'forward stack empty'


def test_prompt_complete_helpresume_command_previews_dormant_target() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    assert ed.open_help_doc('help-browser') is True
    ed._normalize_cursor_lists(ed.cur())
    ed.cur().cursors[ed.cur().primary].line = 7
    ed.cur().cursors[ed.cur().primary].col = 3
    ed.new_buffer('*scratch*', '')

    ed.enter_prompt('command', prefill='help')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'helpresume ')
    assert row[1] == 'command'
    assert row[2] == 'helpresume - reopen the last dormant session-local docs help target'
    assert row[3] == 'resume help-browser @ 8:3'


def test_prompt_complete_helpresume_command_previews_active_target() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    assert ed.open_help_doc('help-browser') is True

    ed.enter_prompt('command', prefill='help')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'helpresume ')
    assert row[2] == 'helpresume - reopen the last dormant session-local docs help target'
    assert row[3] == 'already active: help-browser @ 1:0'


def test_prompt_complete_helpresume_command_previews_explicit_empty_state() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.enter_prompt('command', prefill='help')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'helpresume ')
    assert row[2] == 'helpresume - reopen the last dormant session-local docs help target'
    assert row[3] == 'no session help target'


def test_prompt_complete_helpresume_command_previews_missing_dormant_target() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed._help_session_entry = {'topic': 'zzz-no-such-session', 'line': 0, 'col': 0}

    ed.enter_prompt('command', prefill='help')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'helpresume ')
    assert row[2] == 'helpresume - reopen the last dormant session-local docs help target'
    assert row[3] == 'missing doc: zzz-no-such-session'



def test_prompt_complete_helphistory_command_previews_live_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.open_help_doc('help-browser') is True

    for i, line in enumerate(ed.cur().buf.lines):
        s = str(line)
        if 'Softwrap' in s:
            ed.cur().cursors[0].line = i
            ed.cur().cursors[0].col = s.index('Softwrap')
            break
    else:
        raise AssertionError('Softwrap link not found')

    back_pos = f"{ed.cur().cursors[0].line + 1}:{ed.cur().cursors[0].col}"
    assert ed.exec_command_line('helpfollow') is True

    ed.enter_prompt('command', prefill='help')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'helphistory ')
    assert row[1] == 'command'
    assert row[2] == 'helphistory - show the tiny docs help history register'
    assert row[3] == f'helphistory: 2 help target(s), [here] softwrap @ 1:0; [back 1] help-browser @ {back_pos}'


def test_prompt_complete_helphistory_command_previews_empty_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.enter_prompt('command', prefill='help')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'helphistory ')
    assert row[2] == 'helphistory - show the tiny docs help history register'
    assert row[3] == 'helphistory: 0 help target(s)'


def test_prompt_complete_helpoutlinepick_command_previews_live_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.open_help_doc('helpoutline-section-groups') is True

    rows = ed._prompt_suggestion_rows(
        cmd='',
        toks=['helpoutlinepick'],
        tok_i=0,
        candidates=['helpoutlinepick '],
        path_mode=False,
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'helpoutlinepick ')
    assert row[1] == 'command'
    assert row[2] == 'helpoutlinepick [QUERY] - pick a heading from the current docs page'
    assert row[3] == ed._helpoutlinepick_preview_summary()
    assert 'section(s), ' in row[3]
    assert 'heading' in row[3]
    assert 'Top: ' in row[3]


def test_prompt_complete_helpoutlinepick_command_previews_typed_blocker() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', 'plain text only\n')

    rows = ed._prompt_suggestion_rows(
        cmd='',
        toks=['helpoutlinepick'],
        tok_i=0,
        candidates=['helpoutlinepick '],
        path_mode=False,
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'helpoutlinepick ')
    assert row[1] == 'command'
    assert row[2] == 'helpoutlinepick [QUERY] - pick a heading from the current docs page'
    assert row[3] == 'not in a docs buffer'


def test_prompt_complete_helpnavpick_command_previews_live_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.open_help_doc('help-browser') is True

    rows = ed._prompt_suggestion_rows(
        cmd='',
        toks=['helpnavpick'],
        tok_i=0,
        candidates=['helpnavpick '],
        path_mode=False,
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'helpnavpick ')
    assert row[1] == 'command'
    assert row[2] == 'helpnavpick [QUERY] - pick a heading or link from the current docs page'
    assert row[3] == ed._helpnavpick_preview_summary()
    assert 'section(s), ' in row[3]
    assert 'help target' in row[3]
    assert 'Top: ' in row[3]


def test_prompt_complete_helpnavpick_command_previews_typed_blocker() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', 'plain text only\n')

    rows = ed._prompt_suggestion_rows(
        cmd='',
        toks=['helpnavpick'],
        tok_i=0,
        candidates=['helpnavpick '],
        path_mode=False,
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'helpnavpick ')
    assert row[1] == 'command'
    assert row[2] == 'helpnavpick [QUERY] - pick a heading or link from the current docs page'
    assert row[3] == 'not in a docs buffer'


def test_prompt_complete_helplinkpick_command_previews_live_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.open_help_doc('help-browser') is True

    rows = ed._prompt_suggestion_rows(
        cmd='',
        toks=['helplinkpick'],
        tok_i=0,
        candidates=['helplinkpick '],
        path_mode=False,
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'helplinkpick ')
    assert row[1] == 'command'
    assert row[2] == 'helplinkpick [QUERY] - pick a link from the current docs page'
    assert row[3] == ed._helplinkpick_preview_summary()
    assert 'section(s), ' in row[3]
    assert 'link' in row[3]
    assert 'e.g. ' in row[3]


def test_prompt_complete_helplinkpick_command_previews_typed_blocker() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', 'plain text only\n')

    rows = ed._prompt_suggestion_rows(
        cmd='',
        toks=['helplinkpick'],
        tok_i=0,
        candidates=['helplinkpick '],
        path_mode=False,
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'helplinkpick ')
    assert row[1] == 'command'
    assert row[2] == 'helplinkpick [QUERY] - pick a link from the current docs page'
    assert row[3] == 'not in a docs buffer'

def test_prompt_complete_helpprune_command_previews_pending_cleanup() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed._help_session_entry = {'topic': 'zzz-no-such-session', 'line': 0, 'col': 0}
    ed._help_stack = [
        ed._help_history_entry('vision', line=0, col=0),
        ed._help_history_entry('zzz-no-such-back', line=1, col=2),
    ]
    ed._help_forward_stack = [
        ed._help_history_entry('zzz-no-such-forward', line=2, col=1),
    ]

    ed.enter_prompt('command', prefill='help')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'helpprune ')
    assert row[1] == 'command'
    assert row[2] == 'helpprune - prune missing docs targets from local help history'
    assert row[3] == 'prune 3 missing help target(s) (session 1; back 1; forward 1)'


def test_prompt_complete_helpprune_command_previews_empty_state() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.enter_prompt('command', prefill='help')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'helpprune ')
    assert row[2] == 'helpprune - prune missing docs targets from local help history'
    assert row[3] == 'nothing to prune'


def test_prompt_complete_save_command_previews_current_target_and_dirty_state(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    p = tmp_path / 'demo.txt'
    p.write_text('demo\n', encoding='utf-8')
    ed.open_file(str(p))
    ed.cur().buf.dirty = True

    ed.enter_prompt('command', prefill='sav')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'save ')
    assert row[1] == 'command'
    assert row[2] == 'save [FILE] - save (optionally save as)'
    assert row[3] == f'target {p} | dirty'



def test_prompt_complete_save_command_previews_pathless_buffer_and_saveas_hint() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('draft', 'one\n')
    ed.cur().buf.dirty = True
    ed.enter_prompt('command', prefill='sav')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'save ')
    assert row[2] == 'save [FILE] - save (optionally save as)'
    assert row[3] == 'buffer has no path | dirty · use saveas FILE'



def test_prompt_complete_saveas_command_previews_current_path_and_expectation(tmp_path: Path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    p = tmp_path / 'demo.txt'
    p.write_text('demo\n', encoding='utf-8')
    ed.open_file(str(p))
    ed.cur().buf.dirty = True

    ed.enter_prompt('command', prefill='sav')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'saveas ')
    assert row[1] == 'command'
    assert row[2] == 'saveas FILE - save as'
    assert row[3] == f'current path {p} | dirty · expects FILE'



def test_prompt_complete_saveas_command_previews_pathless_buffer() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('draft', 'one\n')
    ed.cur().buf.dirty = True
    ed.enter_prompt('command', prefill='sav')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'saveas ')
    assert row[2] == 'saveas FILE - save as'
    assert row[3] == 'new file | dirty · expects FILE'



def test_prompt_complete_close_command_previews_dirty_guard_for_current_buffer() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('alpha', 'one\n')
    ed.new_buffer('beta', 'two\n')
    ed.cur().buf.dirty = True

    ed.enter_prompt('command', prefill='clo')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'close ')
    assert row[1] == 'command'
    assert row[2] == 'close [NAME] [-f] - close a buffer'
    assert row[3] == 'target beta @ 1:0 | dirty · run close again or close -f'



def test_prompt_complete_close_command_previews_next_buffer_when_clean() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('alpha', 'one\n')
    ed.new_buffer('beta', 'two\n')

    ed.enter_prompt('command', prefill='clo')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'close ')
    assert row[3] == 'target beta @ 1:0 · next alpha @ 1:0'



def test_prompt_complete_closeall_command_previews_dirty_count_and_guard() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('alpha', 'one\n')
    ed.new_buffer('beta', 'two\n')
    ed.new_buffer('gamma', 'three\n')
    ed.buffers['alpha'].buf.dirty = True

    ed.enter_prompt('command', prefill='closea')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'closeall ')
    assert row[1] == 'command'
    assert row[2] == 'closeall [-f] - close all buffers'
    assert row[3] == '3 buffers | dirty=1 · run closeall again or closeall -f'



def test_prompt_complete_only_command_previews_keep_target_and_dirty_other_count() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('alpha', 'one\n')
    ed.new_buffer('beta', 'two\n')
    ed.new_buffer('gamma', 'three\n')
    ed.buffers['alpha'].buf.dirty = True

    ed.enter_prompt('command', prefill='on')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'only ')
    assert row[1] == 'command'
    assert row[2] == 'only [-f] - close all other buffers'
    assert row[3] == 'keep gamma @ 1:0 · close 2 other buffers | dirty=1 · run only again or only -f'





def test_prompt_complete_force_close_command_previews_force_semantics() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('alpha', 'one\n')
    ed.new_buffer('beta', 'two\n')
    ed.buffers['beta'].buf.dirty = True

    ed.enter_prompt('command', prefill='close')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'close! ')
    assert row[1] == 'command'
    assert row[2] == 'close! - force close a buffer'
    assert row[3] == 'target beta @ 1:0 | dirty · force close · next alpha @ 1:0'



def test_prompt_complete_force_closeall_command_previews_force_semantics() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('alpha', 'one\n')
    ed.new_buffer('beta', 'two\n')
    ed.new_buffer('gamma', 'three\n')
    ed.buffers['alpha'].buf.dirty = True

    ed.enter_prompt('command', prefill='closea')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'closeall! ')
    assert row[1] == 'command'
    assert row[2] == 'closeall! - force close all buffers'
    assert row[3] == '3 buffers | dirty=1 · force close all · then *scratch* @ 1:0'



def test_prompt_complete_force_only_command_previews_force_semantics() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('alpha', 'one\n')
    ed.new_buffer('beta', 'two\n')
    ed.new_buffer('gamma', 'three\n')
    ed.buffers['alpha'].buf.dirty = True

    ed.enter_prompt('command', prefill='on')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'only! ')
    assert row[1] == 'command'
    assert row[2] == 'only! - force close other buffers'
    assert row[3] == 'keep gamma @ 1:0 · close 2 other buffers | dirty=1 · force close'



def test_prompt_complete_quit_command_previews_dirty_guard_and_armed_state() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('alpha', 'one\n')
    ed.new_buffer('beta', 'two\n')
    ed.new_buffer('gamma', 'three\n')
    ed.buffers['alpha'].buf.dirty = True

    ed.enter_prompt('command', prefill='qu')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'quit ')
    assert row[1] == 'command'
    assert row[2] == 'quit - request editor quit'
    assert row[3] == '3 buffers | dirty=1 · run quit again or quit -f'

    assert ed.exec_command_line('quit') is False

    ed.enter_prompt('command', prefill='qu')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'quit ')
    assert row[3] == '3 buffers | dirty=1 | armed · quit now'



def test_prompt_complete_force_quit_command_previews_force_semantics() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('alpha', 'one\n')
    ed.new_buffer('beta', 'two\n')
    ed.buffers['alpha'].buf.dirty = True

    ed.enter_prompt('command', prefill='qui')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'quit! ')
    assert row[1] == 'command'
    assert row[2] == 'quit! - force quit (no warning)'
    assert row[3] == '2 buffers | dirty=1 · force quit'


def test_prompt_complete_undo_command_previews_next_edit_target() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('*t*', '')
    ed.input['text'] = 'x'
    assert ed.run_action('InsertText') is True

    ed.enter_prompt('command', prefill='un')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'undo ')
    assert row[1] == 'command'
    assert row[2] == 'undo - undo the latest edit'
    assert row[3] == 'next insert 1 -> *t* @ 1:1'



def test_prompt_complete_undo_command_previews_empty_stack() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('*t*', '')

    ed.enter_prompt('command', prefill='un')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'undo ')
    assert row[3] == 'nothing to undo'



def test_prompt_complete_redo_command_previews_next_undone_edit_target() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('*t*', '')
    ed.input['text'] = 'x'
    assert ed.run_action('InsertText') is True
    assert ed.exec_command_line('undo') is True

    ed.enter_prompt('command', prefill='re')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'redo ')
    assert row[1] == 'command'
    assert row[2] == 'redo - redo the latest undone edit'
    assert row[3] == 'next insert 1 -> *t* @ 1:0'




def test_prompt_complete_showkeymodes_command_previews_active_and_known_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('*scratch*', '')
    ed.vm.eval('"nav" "x" "command:help" "ed.bind-mode" hostcall', filename='<nav-bind>')
    ed.vm.eval('"goto" "g" "command:showstatus" "ed.bind-mode" hostcall', filename='<goto-bind>')

    assert ed.exec_command_line('pushkeymode nav') is True
    assert ed.exec_command_line('pushkeymode-once goto') is True

    ed.enter_prompt('command', prefill='showkeymod')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showkeymodes ')
    assert row[1] == 'command'
    assert row[2] == 'showkeymodes - show active and known key modes'
    assert row[3] == 'active goto!, nav · known=3 · goto g->command:showstatus'



def test_prompt_complete_showkeymodes_command_previews_default_global_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('*scratch*', '')

    ed.enter_prompt('command', prefill='showkeymod')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showkeymodes ')
    assert row[3] == 'active global · known=1 · global bindings=0'



def test_prompt_complete_showbindings_command_previews_default_active_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('*scratch*', '')
    ed.vm.eval('"goto" "g" "command:showstatus" "ed.bind-mode" hostcall', filename='<goto-bind>')
    assert ed.exec_command_line('pushkeymode-once goto') is True

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='',
        toks=[],
        tok_i=0,
        candidates=['showbindings '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showbindings ')
    assert row[1] == 'command'
    assert row[2] == 'showbindings [MODE|active] - show discoverable bindings'
    assert row[3] == 'default=active bindings=1 · g@goto!->command:showstatus (show portable statusline summary)'



def test_prompt_complete_showbindings_command_previews_empty_active_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='',
        toks=[],
        tok_i=0,
        candidates=['showbindings '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showbindings ')
    assert row[3] == 'default=active bindings=0 · global bindings=0'



def test_prompt_complete_whichkey_command_previews_live_active_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('*scratch*', '')
    ed.vm.eval('"goto" "g" "command:showstatus" "ed.bind-mode" hostcall', filename='<goto-bind>')
    assert ed.exec_command_line('pushkeymode-once goto') is True

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='',
        toks=[],
        tok_i=0,
        candidates=['whichkey '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'whichkey ')
    assert row[1] == 'command'
    assert row[2] == 'whichkey - show currently available bindings with descriptions'
    assert row[3] == 'active bindings=1 · g@goto!->command:showstatus (show portable statusline summary)'



def test_prompt_complete_whichkey_command_previews_empty_active_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='',
        toks=[],
        tok_i=0,
        candidates=['whichkey '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'whichkey ')
    assert row[3] == 'active bindings=0 · global bindings=0'



def test_prompt_complete_showhook_command_previews_live_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('*scratch*', '')
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

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='showhook',
        toks=['showhook'],
        tok_i=0,
        candidates=['showhook '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showhook ')
    assert row[1] == 'command'
    assert row[2] == 'showhook NAME - show installed hook handlers'
    assert row[3] == '7 hooks · 1 with handlers · ed.test.alpha: 1 handler (e.g. h1#cfg)'



def test_prompt_complete_showhook_command_previews_empty_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='showhook',
        toks=['showhook'],
        tok_i=0,
        candidates=['showhook '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showhook ')
    assert row[1] == 'command'
    assert row[2] == 'showhook NAME - show installed hook handlers'
    assert row[3] == '5 hooks · 0 with handlers · ed.on-action: 0 handlers'



def test_prompt_complete_showhooks_command_previews_live_hook_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('*scratch*', '')
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

    ed.enter_prompt('command', prefill='showhook')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showhooks ')
    assert row[1] == 'command'
    assert row[2] == 'showhooks [QUERY] - show count-aware live hook summary'
    assert row[3] == '7 hooks · 1 with handlers · ed.test.alpha: 1 handler (e.g. h1#cfg)'



def test_prompt_complete_showhooks_command_previews_empty_hook_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('*scratch*', '')

    ed.enter_prompt('command', prefill='showhook')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showhooks ')
    assert row[3] == '5 hooks · 0 with handlers · ed.on-action: 0 handlers'



def test_prompt_complete_jumps_command_previews_current_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'one\ntwo\nthree\nfour\nfive\n')
    ed._normalize_cursor_lists(ed.cur())
    ed.cur().cursors[ed.cur().primary].line = 0
    ed.cur().cursors[ed.cur().primary].col = 0
    assert ed.push_jump() is True
    ed.cur().cursors[ed.cur().primary].line = 1
    ed.cur().cursors[ed.cur().primary].col = 1
    assert ed.push_jump() is True
    ed.cur().cursors[ed.cur().primary].line = 4
    ed.cur().cursors[ed.cur().primary].col = 0
    assert ed.push_jump() is True
    assert ed.jump_to_index(1) is True

    ed.enter_prompt('command', prefill='jum')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'jumps ')
    assert row[1] == 'command'
    assert row[2] == 'jumps - show the current jumplist register'
    assert row[3] == '3 jumps · #2 [current] a @ 2:1 <- #1 [back 1] a @ 1:0 (+1) -> #3 [forward 1] a @ 5:0 (+1)'


def test_prompt_complete_jumps_command_previews_empty_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'one\n')
    ed.enter_prompt('command', prefill='jum')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'jumps ')
    assert row[3] == '0 jumps'


def test_prompt_complete_showjump_command_previews_current_slot() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'one\ntwo\nthree\nfour\nfive\n')
    ed._normalize_cursor_lists(ed.cur())
    ed.cur().cursors[ed.cur().primary].line = 0
    ed.cur().cursors[ed.cur().primary].col = 0
    assert ed.push_jump() is True
    ed.cur().cursors[ed.cur().primary].line = 1
    ed.cur().cursors[ed.cur().primary].col = 1
    assert ed.push_jump() is True
    ed.cur().cursors[ed.cur().primary].line = 4
    ed.cur().cursors[ed.cur().primary].col = 0
    assert ed.push_jump() is True
    assert ed.jump_to_index(1) is True

    ed.enter_prompt('command', prefill='showjump')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showjump ')
    assert row[1] == 'command'
    assert row[2] == 'showjump INDEX|#N - show exact jumplist entry without jumping'
    assert row[3] == '3 jumps · #2 [current] a @ 2:1 — two · expects INDEX|#N'


def test_prompt_complete_showjump_command_previews_empty_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'one\n')
    ed.enter_prompt('command', prefill='showjump')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showjump ')
    assert row[3] == '0 jumps · expects INDEX|#N'


def test_prompt_complete_showjumpgroups_command_previews_group_inventory() -> None:
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

    ed.enter_prompt('command', prefill='showjump')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showjumpgroups ')
    assert row[1] == 'command'
    assert row[2] == 'showjumpgroups [QUERY] - show count-aware jumplist sections'
    assert row[3] == '3 section(s), 3 jumps · Current: 1 | e.g. #2 — a @ 2:1 — two'
    assert 'latest ' not in str(row[3])



def test_prompt_complete_showjumpgroups_command_previews_empty_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer('a', 'one\n')
    ed.enter_prompt('command', prefill='showjump')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt.suggestion_rows
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showjumpgroups ')
    assert row[3] == '0 section(s), 0 jumps'


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


def test_prompt_complete_helpjump_command_previews_live_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.open_help_doc('helpoutline-section-groups') is True

    rows = ed._prompt_suggestion_rows(
        cmd='',
        toks=['helpjump'],
        tok_i=0,
        candidates=['helpjump '],
        path_mode=False,
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'helpjump ')
    assert row[1] == 'command'
    assert row[2] == 'helpjump [QUERY] - jump to a heading on the current docs page'
    assert row[3] == ed._helpjump_preview_summary()
    assert 'section(s), ' in row[3]
    assert 'heading' in row[3]
    assert 'Top: ' in row[3]



def test_prompt_complete_helpjump_command_previews_typed_blocker() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', 'plain text only\n')

    rows = ed._prompt_suggestion_rows(
        cmd='',
        toks=['helpjump'],
        tok_i=0,
        candidates=['helpjump '],
        path_mode=False,
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'helpjump ')
    assert row[1] == 'command'
    assert row[2] == 'helpjump [QUERY] - jump to a heading on the current docs page'
    assert row[3] == 'not in a docs buffer'


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


def test_prompt_complete_exact_inspection_commands_preserve_missing_typed_targets() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    cases = [
        ('showcmd', 'ghostcmd', ['ghostcmd ', 'command', 'missing command', 'no such command']),
        ('showaction', 'ghostaction', ['ghostaction ', 'action', 'missing action', 'no such action']),
        ('showword', 'ghostword', ['ghostword ', 'word', 'missing word', 'no such word']),
        ('showdoc', 'ghostdoc', ['ghostdoc ', 'doc', 'missing doc', 'no such doc']),
        ('showtopic', 'ghosttopic', ['ghosttopic ', 'topic', 'missing topic', 'no such topic']),
    ]

    for cmd, typed, expected in cases:
        candidates, fuzzy = ed._prompt_command_token_candidates(
            cmd=cmd,
            toks=[cmd, typed],
            tok_i=1,
            prefix=typed,
            at_eol=True,
        )
        assert candidates == [typed + ' ']
        assert fuzzy is False

        rows = ed._prompt_suggestion_rows(
            cmd=cmd,
            toks=[cmd, typed],
            tok_i=1,
            candidates=candidates,
            path_mode=False,
        )
        row = next(r for r in rows if isinstance(r, list) and r and r[0] == typed + ' ')
        assert row == expected



def test_prompt_complete_exact_editor_state_commands_preserve_missing_typed_targets() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')

    cases = [
        ('showoption', 'ghostopt', ['ghostopt ', 'option', 'missing option', 'no such option']),
        ('showbuffer', 'ghostbuf', ['ghostbuf ', 'buffer', 'missing buffer', 'no such buffer']),
        ('showmark', 'ghostmark', ['ghostmark ', 'mark', 'missing mark', 'no such mark']),
        ('showjump', '99', ['99 ', 'jump', 'missing jump', 'no such jump']),
        ('showkeymode', 'ghostmode', ['ghostmode ', 'keymode', 'missing keymode', 'no such keymode']),
        ('showkey', 'Ctrl-?', ['Ctrl-? ', 'binding', 'missing binding', 'no such binding']),
    ]

    for cmd, typed, expected in cases:
        candidates, fuzzy = ed._prompt_command_token_candidates(
            cmd=cmd,
            toks=[cmd, typed],
            tok_i=1,
            prefix=typed,
            at_eol=True,
        )
        assert candidates == [typed + ' ']
        assert fuzzy is False

        rows = ed._prompt_suggestion_rows(
            cmd=cmd,
            toks=[cmd, typed],
            tok_i=1,
            candidates=candidates,
            path_mode=False,
        )
        row = next(r for r in rows if isinstance(r, list) and r and r[0] == typed + ' ')
        assert row == expected



def test_prompt_complete_showkey_command_previews_live_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.keymap.bind('Ctrl-g', 'command:showkeymodes', mode='nav')
    ed.keymap.set_desc('Ctrl-g', 'enter goto map', mode='nav')
    ed.push_key_mode('nav')

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='',
        toks=[],
        tok_i=0,
        candidates=['showkey '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showkey ')
    assert row[1] == 'command'
    assert row[2] == 'showkey KEY - show resolved binding for key'
    assert row[3] == ed._binding_inventory_preview_summary()
    assert 'Ctrl-g@nav->command:showkeymodes' in row[3]
    assert 'enter goto map' in row[3]



def test_prompt_complete_showcmd_command_previews_live_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval(': demo-showcmd ( args -- ok ) drop 1 ;', filename='<showcmd-root>')
    ed.vm.stack.clear()
    ed.vm.stack.append('cfg')
    ed.vm.stack.append('ed.group!')
    ed.vm.eval('hostcall')
    ed.vm.eval('\' demo-showcmd "demo" "demo command" "ed.cmd-add" hostcall', filename="<showcmd-root>")
    ed.vm.stack.clear()
    ed.vm.stack.append(0)
    ed.vm.stack.append('ed.group!')
    ed.vm.eval('hostcall')

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='',
        toks=[],
        tok_i=0,
        candidates=['showcmd '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showcmd ')
    assert row[1] == 'command'
    assert row[2] == 'show command docs/provenance'
    assert row[3] == ed._command_inventory_preview_summary()
    assert row[3].endswith('demo [group cfg]: demo command')


def test_prompt_complete_showaction_command_previews_live_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    def demo_action(_ed: Editor) -> bool:
        return True

    ed.actions.register('DemoAction', demo_action, doc='demo action')

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='',
        toks=[],
        tok_i=0,
        candidates=['showaction '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showaction ')
    assert row[1] == 'command'
    assert row[2].endswith('show editor action docs')
    assert row[3] == ed._action_inventory_preview_summary()
    assert row[3].endswith('DemoAction: demo action')


def test_prompt_complete_showword_command_previews_live_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.eval(': demo-showword-root ( n -- n ) ( demo root word ) 1 + ;', filename='<showword-root>')

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='',
        toks=[],
        tok_i=0,
        candidates=['showword '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showword ')
    assert row[1] == 'command'
    assert 'show visible micromax word' in str(row[2])
    assert row[3] == ed._word_inventory_preview_summary()
    assert row[3].endswith('demo-showword-root [colon] ( n -- n ): demo root word')



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


def test_prompt_complete_showdoc_command_previews_live_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='showdoc',
        toks=['showdoc'],
        tok_i=0,
        candidates=['showdoc '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showdoc ')
    assert row[1] == 'command'
    assert row[2] == 'showdoc TOPIC - show resolved docs title/section/summary/path'
    assert row[3] == ed._doc_inventory_preview_summary()
    assert 'vision' in str(row[3])
    assert '[00–09 Project]' in str(row[3])


def test_prompt_complete_showtopic_command_previews_live_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='showtopic',
        toks=['showtopic'],
        tok_i=0,
        candidates=['showtopic '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showtopic ')
    assert row[1] == 'command'
    assert row[2] == 'showtopic NAME - show exact help topic detail without reopening docs'
    assert row[3] == ed._topic_inventory_preview_summary()
    assert 'vision' in str(row[3])
    assert '[doc]' in str(row[3])


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


def test_prompt_complete_showmacro_command_previews_live_inventory() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer(text='')

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='',
        toks=[],
        tok_i=0,
        candidates=['showmacro '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showmacro ')
    assert row[1] == 'command'
    assert row[2] == 'showmacro NAME - show exact macro state without replaying'
    assert row[3] == 'idle · default=last (0 steps) · 0 macros'

    assert ed.exec_command_line('macro record demo')
    ed.input['text'] = 'z'
    assert ed.run_action('InsertText')
    rows = ed._prompt_commandish_suggestion_rows(
        cmd='',
        toks=[],
        tok_i=0,
        candidates=['showmacro '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showmacro ')
    assert row[3] == 'recording · demo (1 step) · stop to save, cancel to discard · 0 macros'

    assert ed.exec_command_line('macro stop')
    ed._macro_playing = True
    ed._macro_play_name = 'demo'
    ed._macro_play_steps = 1
    rows = ed._prompt_commandish_suggestion_rows(
        cmd='',
        toks=[],
        tok_i=0,
        candidates=['showmacro '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showmacro ')
    assert row[3] == 'playing · demo (1 step) · wait for playback · 2 macros · e.g. last (1 step) [default]'


def test_prompt_complete_showmacro_command_prefers_default_last_while_idle() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer(text='')

    ed.set_macro('last', [MacroStep(kind='command', name='command', payload={'cmdline': 'noop'})])
    ed.set_macro('demo', [
        MacroStep(kind='command', name='command', payload={'cmdline': 'noop'}),
        MacroStep(kind='command', name='command', payload={'cmdline': 'noop 2'}),
    ])

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='',
        toks=[],
        tok_i=0,
        candidates=['showmacro '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'showmacro ')
    assert row[3] == 'idle · default=last (1 step) · 2 macros · e.g. demo (2 steps)'

def test_prompt_complete_showmacro_surfaces_empty_default_last_slot() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer(text='')

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='showmacro',
        toks=['showmacro', 'l'],
        tok_i=1,
        candidates=['last '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'last ')
    assert row == ['last ', 'macro', '0 steps [default]', 'default replay slot']

    ed.enter_prompt('command', prefill='showmacro l')
    assert ed.prompt is not None
    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == 'showmacro last '


def test_showmacro_completion_candidates_put_last_first() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer(text='')

    ed.set_macro('last', [MacroStep(kind='command', name='command', payload={'cmdline': 'noop'})])
    ed.set_macro('demo', [
        MacroStep(kind='command', name='command', payload={'cmdline': 'noop'}),
        MacroStep(kind='command', name='command', payload={'cmdline': 'noop 2'}),
    ])

    candidates, fuzzy = ed._prompt_command_token_candidates(
        cmd='showmacro',
        toks=['showmacro', ''],
        tok_i=1,
        prefix='',
        at_eol=True,
    )
    assert candidates[:2] == ['last ', 'demo ']
    assert fuzzy is False


def test_macro_slot_completion_candidates_prefer_last_when_default_matters() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer(text='')

    fresh_record_candidates, fresh_record_fuzzy = ed._prompt_command_token_candidates(
        cmd='macro',
        toks=['macro', 'record', ''],
        tok_i=2,
        prefix='',
        at_eol=True,
    )
    assert fresh_record_candidates == ['last ']
    assert fresh_record_fuzzy is False

    ed.set_macro('last', [MacroStep(kind='command', name='command', payload={'cmdline': 'noop'})])
    ed.set_macro('demo', [
        MacroStep(kind='command', name='command', payload={'cmdline': 'noop'}),
        MacroStep(kind='command', name='command', payload={'cmdline': 'noop 2'}),
    ])

    play_candidates, play_fuzzy = ed._prompt_command_token_candidates(
        cmd='macro',
        toks=['macro', 'play', ''],
        tok_i=2,
        prefix='',
        at_eol=True,
    )
    assert play_candidates[:2] == ['last ', 'demo ']
    assert play_fuzzy is False

    record_candidates, record_fuzzy = ed._prompt_command_token_candidates(
        cmd='macro',
        toks=['macro', 'record', ''],
        tok_i=2,
        prefix='',
        at_eol=True,
    )
    assert record_candidates[:2] == ['last ', 'demo ']
    assert record_fuzzy is False


def test_prompt_complete_showmacro_uses_exact_macro_metadata() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer(text='')

    assert ed.exec_command_line('macro record demo')
    ed.input['text'] = 'z'
    assert ed.run_action('InsertText')

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='showmacro',
        toks=['showmacro', 'd'],
        tok_i=1,
        candidates=['demo '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'demo ')
    assert row == ['demo ', 'macro', '1 live step [recording]', 'stop to save, cancel to discard']

    ed.enter_prompt('command', prefill='showmacro d')
    assert ed.prompt is not None
    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == 'showmacro demo '

    rows = ed._prompt_commandish_suggestion_rows(
        cmd='showmacro',
        toks=['showmacro', 'g'],
        tok_i=1,
        candidates=['g '],
    )
    row = next(r for r in rows if isinstance(r, list) and r and r[0] == 'g ')
    assert row == ['g ', 'macro', 'missing macro', 'no such macro']
