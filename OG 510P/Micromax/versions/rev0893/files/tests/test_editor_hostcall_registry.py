from __future__ import annotations

from collections import Counter

from micromax_editor.capabilities import CAPS
from micromax_editor.editor import Editor
from micromax_editor.editor_hostcall_registry import (
    EDITOR_HOSTCALL_REGISTRY,
    STATIC_EDITOR_HOST_FEATURES,
    editor_hostcall_names,
)
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _host_feature(ed: Editor, name: str) -> int:
    ed.vm.stack.append(str(name))
    ed.vm.eval("host.feature?", filename="<hostcall-registry-test>")
    return int(ed.vm.stack.pop())


def test_editor_hostcall_registry_names_are_unique() -> None:
    counts = Counter(editor_hostcall_names())
    assert [name for name, count in counts.items() if count != 1] == []


def test_static_editor_host_features_exclude_capability_controlled_features() -> None:
    assert set(STATIC_EDITOR_HOST_FEATURES).isdisjoint(CAPS.keys())


def test_editor_hostcall_registry_entries_are_registered() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    registered = set(ed.vm.host_fns.keys())
    assert set(editor_hostcall_names()).issubset(registered)
    assert len(EDITOR_HOSTCALL_REGISTRY) == len(editor_hostcall_names())


def test_capability_controlled_features_are_not_advertised_until_enabled() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    for feature in ("ed.hook-read", "ed.hook-fire", "ed.keymode-read"):
        assert _host_feature(ed, feature) == 0

    assert ed.exec_command_line("set cap.hook-read true") is True
    assert ed.exec_command_line("set cap.hook-fire true") is True
    assert ed.exec_command_line("set cap.keymode-read true") is True

    for feature in ("ed.hook-read", "ed.hook-fire", "ed.keymode-read"):
        assert _host_feature(ed, feature) == 1
