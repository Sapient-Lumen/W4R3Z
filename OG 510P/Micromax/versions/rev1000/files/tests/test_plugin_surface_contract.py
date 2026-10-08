from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from micromax import VM
from micromax.vm import MicromaxError
from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.plugin_contract import (
    INTERNAL_PLUGIN_MODEL_HOSTCALLS,
    PLUGIN_SURFACE_STABILITIES,
    STABLE_PLUGIN_EDITOR_HOSTCALLS,
    STABLE_PLUGIN_LIFECYCLE_WORDS,
    plugin_editor_hostcall_stability,
)
from micromax_editor.editor_hostcall_registry import editor_hostcall_names
from micromax_editor.plugins import PluginManager
from micromax_editor.vm_load_policy import plugin_load_root_context


ROOT = Path(__file__).resolve().parents[1]


def _manager() -> tuple[Editor, PluginManager]:
    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    return ed, pm


def _plugin(root: Path, name: str, source: str, *, requires: tuple[str, ...] = ()) -> Path:
    path = root / name
    path.mkdir()
    (path / "init.mx").write_text(source, encoding="utf-8")
    if requires:
        (path / "plugin.json").write_text(
            json.dumps({"name": name, "entry": "init.mx", "requires": list(requires)}),
            encoding="utf-8",
        )
    return path


def test_plugin_namespace_scope_is_explicit_before_context_mutation(
    tmp_path: Path,
) -> None:
    vm = VM(load_stdlib=False)
    with pytest.raises(
        ValueError,
        match="plugin_name requires explicit readable_wids and writable_wids",
    ):
        with plugin_load_root_context(vm, tmp_path, plugin_name="partial"):
            pass

    assert not hasattr(vm, "current_plugin_load_root")
    assert not hasattr(vm, "current_plugin_name")
    assert vm.wordlist_access_scope is None


def test_undeclared_sibling_import_is_denied_and_rolled_back(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(root, "base", ': shared "base" ;\n')
    _plugin(root, "thief", 'use base : stolen shared ;\n')

    ed, pm = _manager()
    loaded = pm.load_tree(root)

    assert [plugin.name for plugin in loaded] == ["base"]
    assert "thief" not in pm.plugins
    assert "thief" not in ed.vm.modules
    assert getattr(ed.vm, "current_plugin_name", None) is None
    assert ed.vm.wordlist_access_scope is None
    assert any(
        name == "thief" and "undeclared namespace read denied: use: module base" in err
        for name, err in pm.load_errors
    )
    ed.vm.eval("use base shared", filename="<declared-import-test>")
    assert ed.vm.stack.pop() == "base"


def test_declared_dependency_is_readable_but_not_writable(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(root, "base", ': shared "base" ;\n')
    _plugin(
        root,
        "writer",
        'in base : shared "writer" ;\n',
        requires=("base",),
    )

    ed, pm = _manager()
    loaded = pm.load_tree(root)

    assert [plugin.name for plugin in loaded] == ["base"]
    assert "writer" not in pm.plugins
    assert any(
        name == "writer" and "namespace write denied: in: module base" in err
        for name, err in pm.load_errors
    )
    ed.vm.eval("use base shared", filename="<dependency-write-test>")
    assert ed.vm.stack.pop() == "base"


@pytest.mark.parametrize(
    ("mutation", "operation"),
    [
        ("' own is switch", "namespace write denied: is switch"),
        ("' own ' switch defer!", "namespace write denied: defer! switch"),
    ],
)
def test_declared_dependency_deferred_behavior_is_not_writable(
    tmp_path: Path,
    mutation: str,
    operation: str,
) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(
        root,
        "base",
        'defer switch : original "base" ; \' original is switch\n',
    )
    _plugin(
        root,
        "writer",
        f': own "writer" ; {mutation}\n',
        requires=("base",),
    )

    ed, pm = _manager()
    assert [plugin.name for plugin in pm.load_tree(root)] == ["base"]
    assert any(
        name == "writer" and operation in err
        for name, err in pm.load_errors
    )
    ed.vm.eval("use base switch", filename="<dependency-defer-write-test>")
    assert ed.vm.stack.pop() == "base"


def test_plugin_cannot_create_an_ambient_module_surface(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(root, "creator", "module hidden : value 1 ; endmodule\n")

    _ed, pm = _manager()
    assert pm.load_tree(root) == []
    assert "creator" not in pm.plugins
    assert any(
        name == "creator" and "wordlist creation is internal: module hidden" in err
        for name, err in pm.load_errors
    )


def test_source_lifecycle_and_delayed_command_use_exact_dependency_order(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(root, "ambient", ': shared "ambient" ;\n')
    _plugin(root, "dep", ': shared "dep" ;\n')
    _plugin(
        root,
        "consumer",
        ': init shared "ed.msg" hostcall ;\n'
        ': run drop shared "ed.msg" hostcall 1 ;\n'
        "' run \"consumer-run\" \"dependency callback\" \"ed.cmd-add\" hostcall drop\n",
        requires=("dep",),
    )

    ed, pm = _manager()
    loaded = pm.load_tree(root)

    assert [plugin.name for plugin in loaded] == ["ambient", "dep", "consumer"]
    assert ed.messages == ["dep"]
    consumer = pm.plugins["consumer"]
    assert pm.plugin_execution_search_order(consumer) == [
        consumer.wid,
        pm.plugins["dep"].wid,
        ed.vm.forth_wid,
    ]

    # Contaminate trusted interactive lookup order.  A delayed plugin callback
    # must not inherit this ambient sibling even though it defines the same word.
    ed.vm.eval("use dep use ambient", filename="<ambient-order>")
    ambient_order = list(ed.vm.search_order)
    ed.messages.clear()

    assert ed.exec_command_line("consumer-run") is True
    assert ed.messages == ["dep"]
    assert ed.vm.search_order == ambient_order


def test_direct_dependencies_precede_transitive_implementation_words(
    tmp_path: Path,
) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(root, "base", ': shared "transitive" ;\n')
    _plugin(root, "mid", ': mid-value shared ;\n', requires=("base",))
    _plugin(root, "direct", ': shared "direct" ;\n')
    _plugin(
        root,
        "leaf",
        ': init shared "ed.msg" hostcall ;\n',
        requires=("mid", "direct"),
    )

    ed, pm = _manager()
    assert [plugin.name for plugin in pm.load_tree(root)] == [
        "base",
        "direct",
        "mid",
        "leaf",
    ]
    leaf = pm.plugins["leaf"]
    assert pm.plugin_execution_search_order(leaf) == [
        leaf.wid,
        pm.plugins["mid"].wid,
        pm.plugins["direct"].wid,
        pm.plugins["base"].wid,
        ed.vm.forth_wid,
    ]
    assert ed.messages == ["direct"]


def test_raw_set_current_cannot_switch_writes_into_a_dependency(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(root, "base", ': shared "base" ;\n')
    _plugin(
        root,
        "writer",
        'get-order drop drop set-current : shared "writer" ;\n',
        requires=("base",),
    )

    ed, pm = _manager()
    assert [plugin.name for plugin in pm.load_tree(root)] == ["base"]
    assert any(
        name == "writer" and "namespace write denied: set-current" in err
        for name, err in pm.load_errors
    )
    ed.vm.eval("use base shared", filename="<set-current-write-test>")
    assert ed.vm.stack.pop() == "base"


def test_dictionary_mutation_guard_is_authoritative_inside_plugin_scope(
    tmp_path: Path,
) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(root, "base", ': shared "base" ;\n')
    _plugin(root, "consumer", ': own "consumer" ;\n', requires=("base",))

    ed, pm = _manager()
    assert [plugin.name for plugin in pm.load_tree(root)] == ["base", "consumer"]
    consumer = pm.plugins["consumer"]
    base = pm.plugins["base"]

    with ed.plugin_callback_context(
        consumer.root,
        consumer.group,
        plugin_generation=consumer.generation,
    ):
        # Simulate a future core primitive that accidentally changes CURRENT
        # without preflighting.  The VM mutation point must still fail closed.
        ed.vm.current_wid = base.wid
        with pytest.raises(MicromaxError, match="namespace write denied: define stolen"):
            ed.vm.eval(': stolen "bad" ;', filename="<mutation-guard-test>")

    ed.vm.eval("use base shared", filename="<mutation-guard-check>")
    assert ed.vm.stack.pop() == "base"
    assert ed.vm.find_word_in_wid(base.wid, "stolen") is None


def test_wordlist_creation_guard_is_authoritative_at_the_vm_mutation_point(
    tmp_path: Path,
) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(root, "consumer", ': own "consumer" ;\n')

    ed, pm = _manager()
    assert [plugin.name for plugin in pm.load_tree(root)] == ["consumer"]
    consumer = pm.plugins["consumer"]
    before_next_wid = int(ed.vm._next_wid)
    before_wordlists = set(ed.vm.wordlists)
    before_names = dict(ed.vm.wordlist_names)

    with ed.plugin_callback_context(
        consumer.root,
        consumer.group,
        plugin_generation=consumer.generation,
    ):
        # Simulate a future primitive calling the VM allocator without the
        # source-level ``wordlist``/``module`` preflight.
        with pytest.raises(
            MicromaxError,
            match="wordlist creation is internal: new wordlist stolen",
        ):
            ed.vm.new_wordlist("stolen")

    assert ed.vm._next_wid == before_next_wid
    assert set(ed.vm.wordlists) == before_wordlists
    assert ed.vm.wordlist_names == before_names


def test_dependency_closure_supports_dependency_implementation_words(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(root, "base", ': base-value "base" ;\n')
    _plugin(root, "mid", ": mid-value base-value ;\n", requires=("base",))
    _plugin(
        root,
        "leaf",
        ': init mid-value "ed.msg" hostcall ;\n',
        requires=("mid",),
    )

    ed, pm = _manager()
    assert [plugin.name for plugin in pm.load_tree(root)] == ["base", "mid", "leaf"]
    leaf = pm.plugins["leaf"]
    assert pm.plugin_execution_search_order(leaf) == [
        leaf.wid,
        pm.plugins["mid"].wid,
        pm.plugins["base"].wid,
        ed.vm.forth_wid,
    ]
    assert ed.messages == ["base"]


def test_plugin_hook_inventory_does_not_leak_undeclared_wordlists(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(root, "ambient", "hook sibling-secret\n")
    _plugin(
        root,
        "consumer",
        "hook own-hook\n"
        ': list-hooks drop hooks 1 ;\n'
        "' list-hooks \"list-hooks\" \"list visible hooks\" \"ed.cmd-add\" hostcall drop\n",
    )

    ed, pm = _manager()
    assert [plugin.name for plugin in pm.load_tree(root)] == ["ambient", "consumer"]
    capsys.readouterr()
    assert ed.exec_command_line("list-hooks") is True
    rendered = capsys.readouterr().out
    assert "own-hook" in rendered
    assert "sibling-secret" not in rendered


def test_internal_models_are_hidden_and_denied_only_for_plugins(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(
        root,
        "probe",
        ': probe-model drop "ed.screen-model" host.feature? 0 =\n'
        '  [ "model-hidden" "ed.msg" hostcall 1 ]\n'
        '  [ "model-leaked" "ed.msg" hostcall 0 ] if ;\n'
        "' probe-model \"probe-model\" \"probe internal model\" \"ed.cmd-add\" hostcall drop\n",
    )
    _plugin(root, "badmodel", '2 20 "ed.screen-model" hostcall\n')

    ed, pm = _manager()
    loaded = pm.load_tree(root)

    assert [plugin.name for plugin in loaded] == ["probe"]
    assert any(
        name == "badmodel" and "internal editor hostcall denied: ed.screen-model" in err
        for name, err in pm.load_errors
    )
    assert ed.exec_command_line("probe-model") is True
    assert ed.messages[-1] == "model-hidden"

    probe = pm.plugins["probe"]
    with ed.plugin_callback_context(
        probe.root,
        probe.group,
        plugin_generation=probe.generation,
    ):
        ed.vm.eval("host.features", filename="<plugin-features>")
        features = ed.vm.stack.pop()
        for surface in ("ed.screen-model", "ed.docs-cues"):
            assert surface not in features
            denied_stack = [2, 20, surface]
            ed.vm.stack[:] = denied_stack
            with pytest.raises(
                MicromaxError,
                match=rf"internal editor hostcall denied: {re.escape(surface)}",
            ):
                ed.vm.eval("hostcall", filename="<plugin-model-denial>")
            assert ed.vm.stack == denied_stack
    ed.vm.stack.clear()

    # The same exact projection remains a trusted host/headless seam.
    ed.new_buffer("main", "hello")
    for surface in ("ed.screen-model", "ed.docs-cues"):
        ed.vm.stack.extend([2, 20, surface])
        ed.vm.eval("hostcall", filename="<trusted-model>")
        assert isinstance(ed.vm.stack.pop(), dict)


def test_plugin_surface_classification_is_total_and_small() -> None:
    names = set(editor_hostcall_names())
    assert INTERNAL_PLUGIN_MODEL_HOSTCALLS <= names
    assert STABLE_PLUGIN_EDITOR_HOSTCALLS <= names
    assert set(STABLE_PLUGIN_LIFECYCLE_WORDS) == {"preinit", "init", "postinit", "deinit"}
    assert {
        plugin_editor_hostcall_stability(name) for name in names
    } <= PLUGIN_SURFACE_STABILITIES
    assert all(
        plugin_editor_hostcall_stability(name) == "internal"
        for name in INTERNAL_PLUGIN_MODEL_HOSTCALLS
    )
    assert all(
        plugin_editor_hostcall_stability(name) == "stable"
        for name in STABLE_PLUGIN_EDITOR_HOSTCALLS
    )
    assert any(plugin_editor_hostcall_stability(name) == "experimental" for name in names)


def test_bundled_plugin_direct_hostcalls_are_in_the_stable_slice() -> None:
    consumers: dict[str, set[str]] = {}
    for path in sorted((ROOT / "plugins").rglob("*.mx")):
        source = path.read_text(encoding="utf-8")
        for name in re.findall(r'"([A-Za-z0-9_.!?-]+)"\s+hostcall', source):
            consumers.setdefault(name, set()).add(str(path.relative_to(ROOT)))

    assert consumers
    unstable = {
        name: sorted(paths)
        for name, paths in consumers.items()
        if plugin_editor_hostcall_stability(name) != "stable"
    }
    assert unstable == {}
