from __future__ import annotations

from micromax_editor.editor import Editor, MacroStep
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _new_editor() -> Editor:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')
    return ed


def test_script_origin_keybinding_replays_under_script_authority() -> None:
    ed = _new_editor()

    with ed.script_context():
        ed.vm.stack.append('F9')
        ed.vm.stack.append('command:set cap.fs-save true')
        ed.vm.stack.append('ed.bind')
        ed.vm.eval('hostcall')

    b = ed.resolve_key_binding('F9')
    assert b is not None
    assert b.script_context is True

    ed.messages.clear()
    assert ed.dispatch_key('F9') is False
    assert bool(ed.options.get('cap.fs-save')) is False
    assert any('script context cannot modify capability option: cap.fs-save' in msg for msg in ed.messages)


def test_interactive_keybinding_keeps_user_authority() -> None:
    ed = _new_editor()

    assert ed.exec_command_line('bind F9 "command:set cap.fs-save true"')
    b = ed.resolve_key_binding('F9')
    assert b is not None
    assert b.script_context is False

    assert ed.dispatch_key('F9') is True
    assert bool(ed.options.get('cap.fs-save')) is True


def test_script_context_command_bar_bind_captures_deferred_authority() -> None:
    ed = _new_editor()

    with ed.script_context():
        assert ed.exec_command_line('bind F8 "command:set cap.fs-open true"')

    b = ed.resolve_key_binding('F8')
    assert b is not None
    assert b.script_context is True

    ed.messages.clear()
    assert ed.dispatch_key('F8') is False
    assert bool(ed.options.get('cap.fs-open')) is False
    assert any('script context cannot modify capability option: cap.fs-open' in msg for msg in ed.messages)


def test_script_origin_macro_steps_replay_under_script_authority() -> None:
    ed = _new_editor()

    ed.set_macro(
        'evil',
        [
            MacroStep(
                kind='command',
                name='command',
                payload={'cmdline': 'set cap.fs-save true'},
                script_context=True,
            )
        ],
    )

    ed.messages.clear()
    assert ed.play_macro('evil') is False
    assert bool(ed.options.get('cap.fs-save')) is False
    assert any('script context cannot modify capability option: cap.fs-save' in msg for msg in ed.messages)


def test_macro_set_hostcall_marks_script_origin_steps() -> None:
    ed = _new_editor()

    with ed.script_context():
        ed.vm.stack.append([['c', 'set cap.fs-open true']])
        ed.vm.stack.append('evil')
        ed.vm.eval('"ed.macro-set" hostcall')

    steps = ed.get_macro('evil')
    assert steps and steps[0].script_context is True

    ed.messages.clear()
    assert ed.play_macro('evil') is False
    assert bool(ed.options.get('cap.fs-open')) is False
    assert any('script context cannot modify capability option: cap.fs-open' in msg for msg in ed.messages)


def test_macro_get_roundtrips_script_origin_marker() -> None:
    ed = _new_editor()
    ed.set_macro(
        'm',
        [
            MacroStep(
                kind='command',
                name='command',
                payload={'cmdline': 'noop'},
                script_context=True,
            )
        ],
    )

    ed.vm.eval('"m" "ed.macro-get" hostcall')
    assert ed.vm.pop_list() == [['c', 'noop', 'script']]


def test_script_macro_set_cannot_overwrite_trusted_macro() -> None:
    ed = _new_editor()
    ed.set_macro(
        'trusted',
        [MacroStep(kind='command', name='command', payload={'cmdline': 'noop'})],
    )

    with ed.script_context():
        try:
            ed.set_macro(
                'trusted',
                [MacroStep(kind='command', name='command', payload={'cmdline': 'set cap.fs-save true'})],
            )
        except RuntimeError as e:
            err = str(e)
        else:  # pragma: no cover - assertion path
            err = ''

    assert 'script context cannot modify macro: trusted' in err
    assert 'trusted registration' in err
    assert ed.get_macro('trusted')[0].payload == {'cmdline': 'noop'}


def test_script_macro_set_can_update_same_origin_but_not_other_script_origin() -> None:
    ed = _new_editor()

    with ed.script_context():
        ed.set_macro('owned', [MacroStep(kind='command', name='command', payload={'cmdline': 'first'})])
        first = ed.get_macro('owned')[0]
        assert first.script_context is True
        origin = first.script_origin_id
        assert origin

        ed.set_macro('owned', [MacroStep(kind='command', name='command', payload={'cmdline': 'second'})])
        updated = ed.get_macro('owned')[0]
        assert updated.payload == {'cmdline': 'second'}
        assert updated.script_origin_id == origin

    with ed.script_context():
        try:
            ed.set_macro('owned', [])
        except RuntimeError as e:
            err = str(e)
        else:  # pragma: no cover - assertion path
            err = ''

    assert 'script context cannot modify macro: owned' in err
    assert 'different script origin' in err
    assert ed.get_macro('owned')[0].payload == {'cmdline': 'second'}


def test_script_started_macro_recording_refuses_to_shadow_trusted_last() -> None:
    ed = _new_editor()
    ed.set_macro('last', [MacroStep(kind='command', name='command', payload={'cmdline': 'trusted'})])

    with ed.script_context():
        assert ed.start_macro('evil') is False

    assert ed.get_macro('last')[0].payload == {'cmdline': 'trusted'}
    assert ed.macro_recording is False
    assert 'macro record: script context cannot modify macro: last' in ed.messages[-1]


def test_script_started_macro_recording_stamps_later_user_actions_as_script_origin() -> None:
    ed = _new_editor()

    with ed.script_context():
        assert ed.start_macro('evil') is True
        origin = ed.current_script_origin_id()
        assert origin

    ed.input['text'] = 'X'
    assert ed.run_action('InsertText') is True
    assert ed.stop_macro() is True

    steps = ed.get_macro('evil')
    assert len(steps) == 1
    assert steps[0].kind == 'action'
    assert steps[0].script_context is True
    assert steps[0].script_origin_id == origin


def test_user_started_macro_recording_stamps_script_callbacks_as_script_origin() -> None:
    ed = _new_editor()
    assert ed.start_macro('last') is True

    with ed.script_context():
        origin = ed.current_script_origin_id()
        ed.input['text'] = 'Y'
        assert ed.run_action('InsertText') is True

    assert ed.stop_macro() is True
    steps = ed.get_macro('last')
    assert len(steps) == 1
    assert steps[0].script_context is True
    assert steps[0].script_origin_id == origin


def test_script_cannot_stop_or_cancel_trusted_macro_recording() -> None:
    ed = _new_editor()
    assert ed.start_macro('last') is True

    with ed.script_context():
        assert ed.stop_macro() is False
        assert 'macro stop: script context cannot modify macro recording' in ed.messages[-1]
        assert ed.cancel_macro() is False
        assert 'macro cancel: script context cannot modify macro recording' in ed.messages[-1]

    assert ed.macro_recording is True
    assert ed.cancel_macro() is True
