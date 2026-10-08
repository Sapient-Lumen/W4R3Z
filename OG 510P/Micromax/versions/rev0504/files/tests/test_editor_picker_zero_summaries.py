from __future__ import annotations

from pathlib import Path

from micromax_editor.editor import Editor


def test_bufferpick_zero_match_feedback_names_query() -> None:
    ed = Editor()

    assert ed.exec_command_line('bufferpick zzz-no-such-buffer') is True
    assert ed.prompt is not None
    assert ed.prompt.kind == 'buffer'
    assert ed.submit_prompt() is False
    assert ed.messages[-1] == 'bufferpick zzz-no-such-buffer: 0 buffer(s)'


def test_pluginpick_zero_match_feedback_names_query() -> None:
    ed = Editor()

    assert ed.exec_command_line('pluginpick zzz-no-such-plugin') is True
    assert ed.prompt is not None
    assert ed.prompt.kind == 'plugin'
    assert ed.submit_prompt() is False
    assert ed.messages[-1] == 'pluginpick zzz-no-such-plugin: 0 plugin(s)'


def test_recentpick_and_recentdirpick_zero_match_feedback_name_query(tmp_path: Path) -> None:
    p = tmp_path / 'a.txt'
    p.write_text('a\n', encoding='utf-8')

    ed = Editor()
    assert ed.exec_command_line(f'open {p}') is True

    assert ed.exec_command_line('recentpick zzz-no-such-file') is True
    assert ed.prompt is not None
    assert ed.prompt.kind == 'recent'
    assert ed.submit_prompt() is False
    assert ed.messages[-1] == 'recentpick zzz-no-such-file: 0 recent file(s)'

    assert ed.exec_command_line('recentdirpick zzz-no-such-file') is True
    assert ed.prompt is not None
    assert ed.prompt.kind == 'recentdir'
    assert ed.submit_prompt() is False
    assert ed.messages[-1] == 'recentdirpick zzz-no-such-file: 0 recent file(s)'


def test_helppick_zero_match_feedback_names_query() -> None:
    ed = Editor()

    assert ed.exec_command_line('helppick zzz-no-such-doc') is True
    assert ed.prompt is not None
    assert ed.prompt.kind == 'doc'
    assert ed.submit_prompt() is False
    assert ed.messages[-1] == 'docpick zzz-no-such-doc: 0 doc(s)'


def test_docs_navigation_picker_zero_match_feedback_names_query() -> None:
    ed = Editor()
    assert ed.open_help_doc('vision') is True

    assert ed.exec_command_line('helplinkpick zzz-no-such-link') is True
    assert ed.prompt is not None
    assert ed.prompt.kind == 'helplink'
    assert ed.submit_prompt() is False
    assert ed.messages[-1] == 'helplinkpick zzz-no-such-link: 0 link(s)'

    assert ed.exec_command_line('helpoutlinepick zzz-no-such-heading') is True
    assert ed.prompt is not None
    assert ed.prompt.kind == 'helpoutline'
    assert ed.submit_prompt() is False
    assert ed.messages[-1] == 'helpoutlinepick zzz-no-such-heading: 0 heading(s)'

    assert ed.exec_command_line('helpnavpick zzz-no-such-target') is True
    assert ed.prompt is not None
    assert ed.prompt.kind == 'helpnav'
    assert ed.submit_prompt() is False
    assert ed.messages[-1] == 'helpnavpick zzz-no-such-target: 0 help target(s)'


def test_markpick_and_jumppick_zero_match_feedback_name_query() -> None:
    ed = Editor()
    ed.new_buffer('a', 'one\n')

    assert ed.exec_command_line('markpick zzz-no-such-mark') is True
    assert ed.prompt is not None
    assert ed.prompt.kind == 'mark'
    assert ed.submit_prompt() is False
    assert ed.messages[-1] == 'markpick zzz-no-such-mark: 0 mark(s)'

    assert ed.exec_command_line('jumppick zzz-no-such-jump') is True
    assert ed.prompt is not None
    assert ed.prompt.kind == 'jump'
    assert ed.submit_prompt() is False
    assert ed.messages[-1] == 'jumppick zzz-no-such-jump: 0 jump(s)'
