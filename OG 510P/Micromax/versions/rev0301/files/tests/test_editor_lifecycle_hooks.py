from __future__ import annotations

from pathlib import Path

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def test_on_change_hook_fires_and_is_stack_isolated_per_handler() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer('*scratch*', '')

    vm = ed.vm
    vm.eval(
        """
        variable n
        : h1 ( buf action -- ) 2drop ;
        : h2 ( buf action -- ) 2drop n @ 1 + n ! ;
        ' h1 hook-add ed.on-change
        ' h2 hook-add ed.on-change
        """,
        filename='<test>',
    )

    ed.input['text'] = 'x'
    assert ed.run_action('InsertText')

    vm.eval('n @', filename='<test>')
    assert vm.pop_int() == 1


def test_on_open_and_on_save_hooks(tmp_path: Path) -> None:
    p = tmp_path / 'note.md'
    p.write_text('# hi\n', encoding='utf-8')

    ed = Editor()
    install_editor_hostcalls(ed)

    vm = ed.vm
    vm.eval(
        """
        variable opens
        variable saves
        : hopen ( buf path ft -- ) drop drop drop opens @ 1 + opens ! ;
        : hsave ( buf path -- ) 2drop saves @ 1 + saves ! ;
        ' hopen hook-add ed.on-open
        ' hsave hook-add ed.on-save
        """,
        filename='<test>',
    )

    ed.open_file(str(p))

    # mutate and save
    ed.input['text'] = 'x'
    ed.run_action('InsertText')
    ed.save()

    vm.eval('opens @ saves @', filename='<test>')
    saves = vm.pop_int()
    opens = vm.pop_int()
    assert opens == 1
    assert saves == 1
