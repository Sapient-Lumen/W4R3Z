from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _hostcall(ed: Editor, name: str, *args: object) -> list[object]:
    vm = ed.vm
    for a in args:
        vm.stack.append(a)
    vm.stack.append(name)
    vm.eval('hostcall')
    return list(vm.stack)


def test_helplink_sections_can_group_by_heading() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    assert ed.open_help_doc('help-browser') is True

    # Switch to heading-based grouping.
    assert ed.exec_command_line('set help.linksections heading')

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.helplink-section-rows', '')
    sections = ed.vm.pop_list()

    assert sections
    labels = [s[0] for s in sections if isinstance(s, list) and s]
    # These headings exist in docs/98-help-browser.md.
    assert 'Links' in labels
    assert 'External links' in labels
