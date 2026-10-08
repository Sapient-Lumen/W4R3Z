from pathlib import Path

from micromax.vm import VM
from micromax_editor.editor import Editor
from micromax_editor.plugins import PluginManager


def test_hook_groups_and_detail_rows_are_portable() -> None:
    vm = VM()
    vm.eval(
        '\n'.join(
            [
                'hook on-save',
                ': h1 1 ;',
                '"cfg" hook-group!',
                "' h1 hook-add on-save",
                'hook-detail on-save',
                'hook-groups on-save',
                'hook-group@',
                '0 hook-group!',
                'hook-group@',
            ]
        ),
        filename='hooks.mx',
    )

    cleared = vm.pop()
    current = vm.pop()
    groups = vm.pop_list()
    rows = vm.pop_list()

    assert cleared == 0
    assert current == 'cfg'
    assert groups == ['cfg']
    assert rows[0][0] == 'h1'
    assert rows[0][1] == 'cfg'
    assert rows[0][2][0] == 'hooks.mx'


def test_hook_rm_group_removes_only_matching_handlers() -> None:
    vm = VM()
    vm.eval(
        '\n'.join(
            [
                'hook on-save',
                ': h1 1 ;',
                ': h2 2 ;',
                '"g1" hook-group!',
                "' h1 hook-add on-save",
                '"g2" hook-group!',
                "' h2 hook-add on-save",
                '0 hook-group!',
                '"g1" hook-rm-group on-save',
                'hook-detail on-save',
            ]
        ),
        filename='hooks.mx',
    )

    rows = vm.pop_list()
    removed = vm.pop_int()

    assert removed == 1
    assert rows[0][0] == 'h2'
    assert rows[0][1] == 'g2'
    assert rows[0][2][0] == 'hooks.mx'


def test_plugin_reload_cleans_grouped_hook_handlers(tmp_path: Path) -> None:
    root = tmp_path / 'plugins'
    p = root / 'p1'
    p.mkdir(parents=True)
    (p / 'init.mx').write_text(
        '\n'.join(
            [
                ': on-pre 1 drop ;',
                ': init',
                "  ' on-pre hook-add ed.pre-action",
                ';',
            ]
        ),
        encoding='utf-8',
    )

    ed = Editor()
    pm = PluginManager(ed.vm)
    pm.load_tree(root)

    ed.vm.eval('hook-detail ed.pre-action', filename='<test>')
    rows1 = ed.vm.pop_list()
    assert len(rows1) == 1
    assert rows1[0][0] == 'on-pre'
    assert rows1[0][1] == 'plugin:p1'

    pm.reload('p1')
    ed.vm.eval('hook-detail ed.pre-action', filename='<test>')
    rows2 = ed.vm.pop_list()
    assert len(rows2) == 1
    assert rows2[0][1] == 'plugin:p1'

    pm.unload('p1')
    ed.vm.eval('hook-detail ed.pre-action', filename='<test>')
    assert ed.vm.pop_list() == []
