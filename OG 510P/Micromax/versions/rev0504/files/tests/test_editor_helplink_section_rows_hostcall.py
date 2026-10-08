from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _hostcall(ed: Editor, name: str, *args: object) -> list[object]:
    vm = ed.vm
    for a in args:
        vm.stack.append(a)
    vm.stack.append(name)
    vm.eval('hostcall')
    return list(vm.stack)


def test_helplink_section_rows_hostcall_groups_links() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    assert ed.open_help_doc('help-browser') is True

    ed.vm.stack.clear()
    _hostcall(ed, 'ed.helplink-section-rows', '')
    sections = ed.vm.pop_list()

    assert sections
    labels = [s[0] for s in sections if isinstance(s, list) and s]
    assert 'Files' in labels
    assert 'External' in labels

    files = next(s[1] for s in sections if isinstance(s, list) and s and s[0] == 'Files')
    ext = next(s[1] for s in sections if isinstance(s, list) and s and s[0] == 'External')

    assert any(isinstance(row, list) and row and row[0] == 'Softwrap' for row in files)
    assert any(isinstance(row, list) and row and row[0] == 'micro editor' for row in ext)
