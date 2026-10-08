from __future__ import annotations

from pathlib import Path

import pytest

from micromax.vm import MicromaxError
from micromax_editor.editor import Editor, MacroStep
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.plugins import PluginManager


def _editor_with_plugin_manager() -> tuple[Editor, PluginManager]:
    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    return ed, pm


def _write_plugin(plug: Path, value: str, extra_count: int = 0) -> None:
    lines = [f': aword "{value}" ;']
    for i in range(extra_count):
        lines.append(f': helper-{i} {i} ;')
    (plug / "init.mx").write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_successful_reload_retires_old_wordlists_without_live_growth(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    plug = root / "alpha"
    plug.mkdir(parents=True)
    _write_plugin(plug, "v0", extra_count=24)

    ed, pm = _editor_with_plugin_manager()
    assert [p.name for p in pm.load_tree(root)] == ["alpha"]
    base_count = len(ed.vm.wordlists)
    first_wid = pm.plugins["alpha"].wid
    assert first_wid in ed.vm.wordlists

    old_wids: list[int] = []
    for i in range(1, 6):
        old = pm.plugins["alpha"]
        old_wids.append(old.wid)
        _write_plugin(plug, f"v{i}", extra_count=24)
        reloaded = pm.reload("alpha")
        assert reloaded.wid != old.wid
        assert old.wid not in ed.vm.wordlists
        assert old.wid not in ed.vm.wordlist_names
        assert old.wid not in ed.vm.search_order
        assert ed._word_key(old.wid, "aword") not in ed._snapshot_word_authority()
        assert len(ed.vm.wordlists) == base_count

    ed.vm.eval("use alpha aword", filename="<test>")
    assert ed.vm.stack.pop() == "v5"

    rows = pm.retired_wordlist_rows("alpha")
    assert len(rows) == len(old_wids)
    assert [int(row[2]) for row in rows] == old_wids
    assert all(row[1] == "reload" for row in rows)
    assert all(int(row[4]) == 25 for row in rows)
    assert all("aword" in row[8] for row in rows)
    assert all(tombstone.words for tombstone in pm.retired_wordlists)
    assert all(not any(hasattr(item, "execute") for item in tombstone.words) for tombstone in pm.retired_wordlists)


def test_successful_unload_retires_live_wordlist_and_scrubs_authority(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    plug = root / "alpha"
    plug.mkdir(parents=True)
    _write_plugin(plug, "alive", extra_count=3)

    ed, pm = _editor_with_plugin_manager()
    assert [p.name for p in pm.load_tree(root)] == ["alpha"]
    plugin = pm.plugins["alpha"]
    live_wid = plugin.wid
    assert ed._word_key(live_wid, "aword") in ed._snapshot_word_authority()

    pm.unload("alpha")

    assert "alpha" not in pm.plugins
    assert "alpha" not in ed.vm.modules
    assert live_wid not in ed.vm.wordlists
    assert live_wid not in ed.vm.wordlist_names
    assert live_wid not in ed.vm.search_order
    assert ed._word_key(live_wid, "aword") not in ed._snapshot_word_authority()

    rows = pm.retired_wordlist_rows("alpha")
    assert len(rows) == 1
    row = rows[0]
    assert row[1] == "unload"
    assert int(row[2]) == live_wid
    assert int(row[4]) == 4
    assert "aword" in row[8]


def test_direct_xt_from_retired_wordlist_fails_after_reload(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    plug = root / "alpha"
    plug.mkdir(parents=True)
    _write_plugin(plug, "old")

    ed, pm = _editor_with_plugin_manager()
    assert [p.name for p in pm.load_tree(root)] == ["alpha"]
    ed.vm.eval("use alpha ' aword", filename="<test>")
    old_xt = ed.vm.stack.pop()

    _write_plugin(plug, "new")
    pm.reload("alpha")

    ed.vm.eval("use alpha aword", filename="<test>")
    assert ed.vm.stack.pop() == "new"

    ed.vm.stack.append(old_xt)
    with pytest.raises(MicromaxError, match="Retired execution token: aword"):
        ed.vm.eval("execute", filename="<test>")


def test_captured_keybinding_from_retired_generation_does_not_run_after_reload(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    plug = root / "alpha"
    plug.mkdir(parents=True)
    (plug / "init.mx").write_text(
        '"F20" "mx: \\"old-key-ran\\" \\"ed.msg\\" hostcall 1" "ed.bind" hostcall\n',
        encoding="utf-8",
    )

    ed, pm = _editor_with_plugin_manager()
    assert [p.name for p in pm.load_tree(root)] == ["alpha"]
    old_binding = ed.keymap.get_binding("F20")
    assert old_binding is not None
    assert old_binding.script_context is True
    assert int(old_binding.plugin_generation or 0) == int(pm.plugins["alpha"].generation)

    (plug / "init.mx").write_text(': fresh "new" ;\n', encoding="utf-8")
    pm.reload("alpha")

    ed.messages.clear()
    assert ed._run_key_binding(old_binding) is False
    assert "old-key-ran" not in ed.messages
    assert any("stale plugin callback: plugin alpha" in msg for msg in ed.messages)


def test_reinserted_hook_handler_from_retired_generation_does_not_run(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    plug = root / "alpha"
    plug.mkdir(parents=True)
    (plug / "init.mx").write_text(
        '[ "old-hook-ran" "ed.msg" hostcall ] hook-add ed.on-action\n',
        encoding="utf-8",
    )

    ed, pm = _editor_with_plugin_manager()
    assert [p.name for p in pm.load_tree(root)] == ["alpha"]
    hook_word = ed.vm.find_word("ed.on-action")
    assert hook_word is not None
    old_handler = list(getattr(hook_word, "handlers"))[-1]
    assert int(getattr(old_handler, "plugin_generation", 0) or 0) == int(pm.plugins["alpha"].generation)

    (plug / "init.mx").write_text(': fresh "new" ;\n', encoding="utf-8")
    pm.reload("alpha")

    hook_word = ed.vm.find_word("ed.on-action")
    assert hook_word is not None
    getattr(hook_word, "handlers").append(old_handler)
    ed.messages.clear()
    ed.vm.stack.extend(["manual", 1])
    ed.vm.eval("ed.on-action", filename="<stale-hook-test>")

    assert "old-hook-ran" not in ed.messages
    assert any("stale plugin callback: plugin alpha" in msg for msg in ed.messages)


def test_reinserted_timer_from_retired_generation_does_not_run(tmp_path: Path) -> None:
    import heapq

    root = tmp_path / "plugins"
    plug = root / "alpha"
    plug.mkdir(parents=True)
    (plug / "init.mx").write_text(
        '0 [ "old-timer-ran" "ed.msg" hostcall ] "ed.after" hostcall drop\n',
        encoding="utf-8",
    )

    ed, pm = _editor_with_plugin_manager()
    ed._now_fn = lambda: 0.0
    assert [p.name for p in pm.load_tree(root)] == ["alpha"]
    old_task_id = next(iter(ed.timers._tasks.keys()))
    old_task = ed.timers.get(old_task_id)
    assert old_task is not None
    assert int(getattr(old_task, "plugin_generation", 0) or 0) == int(pm.plugins["alpha"].generation)

    (plug / "init.mx").write_text(': fresh "new" ;\n', encoding="utf-8")
    pm.reload("alpha")

    old_task.canceled = False
    old_task.due = 0.0
    ed.timers._tasks[int(old_task.task_id)] = old_task
    heapq.heappush(ed.timers._heap, (0.0, int(old_task.task_id)))
    ed.messages.clear()
    assert ed.pump_timers() == 1

    assert "old-timer-ran" not in ed.messages
    assert any("stale plugin callback: plugin alpha" in msg for msg in ed.messages)


def test_reinserted_macro_from_retired_generation_is_pruned_on_play(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    plug = root / "alpha"
    plug.mkdir(parents=True)
    (plug / "init.mx").write_text(': fresh "old" ;\n', encoding="utf-8")

    ed, pm = _editor_with_plugin_manager()
    assert [p.name for p in pm.load_tree(root)] == ["alpha"]
    old_plugin = pm.plugins["alpha"]
    old_step = MacroStep(
        kind="command",
        name="old-macro-step",
        payload={"cmdline": "fresh"},
        script_context=True,
        plugin_load_root=str(old_plugin.root),
        plugin_generation=int(old_plugin.generation),
        script_origin_id="origin-alpha-old",
    )
    ed.macros["alpha-old"] = [old_step]

    (plug / "init.mx").write_text(': fresh "new" ;\n', encoding="utf-8")
    pm.reload("alpha")
    assert "alpha-old" not in ed.macros

    # Embedders/tests can still reinsert a captured stale macro row.  Playback
    # should refuse it before the command body runs and clear the dead slot so
    # future macro inventory does not keep advertising a non-runnable macro.
    ed.macros["alpha-old"] = [old_step]
    ed.messages.clear()
    assert ed.play_macro("alpha-old") is False

    assert "alpha-old" not in ed.macros
    assert "alpha-old" not in ed.macro_names()
    assert any("macro play: stale plugin macro: plugin alpha" in msg for msg in ed.messages)


def test_reinserted_prompt_from_retired_generation_does_not_submit(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    plug = root / "alpha"
    plug.mkdir(parents=True)
    (plug / "init.mx").write_text(
        ': init "showstatus" "ed.command-edit" hostcall ;\n',
        encoding="utf-8",
    )

    ed, pm = _editor_with_plugin_manager()
    assert [p.name for p in pm.load_tree(root)] == ["alpha"]
    old_prompt = ed.prompt
    assert old_prompt is not None
    assert old_prompt.kind == "command"
    assert old_prompt.text == "showstatus"
    assert int(getattr(old_prompt, "plugin_generation", 0) or 0) == int(pm.plugins["alpha"].generation)

    (plug / "init.mx").write_text(': fresh "new" ;\n', encoding="utf-8")
    pm.reload("alpha")
    assert ed.prompt is None

    ed.prompt = old_prompt
    ed.messages.clear()
    assert ed.submit_prompt() is False

    assert ed.prompt is None
    assert any("stale plugin prompt: plugin alpha" in msg for msg in ed.messages)


def test_reinserted_qreplace_from_retired_generation_does_not_apply(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    plug = root / "alpha"
    plug.mkdir(parents=True)
    (plug / "init.mx").write_text(
        ': init "qreplace one OLD -l" "ed.command" hostcall drop ;\n',
        encoding="utf-8",
    )

    ed, pm = _editor_with_plugin_manager()
    ed.new_buffer("main", "one one\n")
    assert [p.name for p in pm.load_tree(root)] == ["alpha"]
    old_session = ed.qreplace
    assert old_session is not None
    assert int(getattr(old_session.authority, "plugin_generation", 0) or 0) == int(pm.plugins["alpha"].generation)

    (plug / "init.mx").write_text(': fresh "new" ;\n', encoding="utf-8")
    pm.reload("alpha")
    assert ed.qreplace is None

    ed.qreplace = old_session
    ed.messages.clear()
    assert ed.qreplace_yes() is False

    assert ed.cur().buf.get_text() == "one one\n"
    assert ed.qreplace is None
    assert any("stale plugin qreplace: plugin alpha" in msg for msg in ed.messages)


def test_reinserted_open_url_confirmation_from_retired_generation_does_not_open(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    plug = root / "alpha"
    plug.mkdir(parents=True)
    (plug / "init.mx").write_text(
        ': init "urlopen https://alpha.invalid/old" "ed.command" hostcall drop ;\n',
        encoding="utf-8",
    )

    ed, pm = _editor_with_plugin_manager()
    ed.options.set("cap.open-url", "true")
    opened: list[str] = []
    ed._open_url_fn = lambda url, new=0: opened.append(str(url)) or True
    assert [p.name for p in pm.load_tree(root)] == ["alpha"]
    old_url = ed._pending_open_url
    old_source = ed._pending_open_url_source
    old_authority = ed._pending_open_url_authority
    assert old_url == "https://alpha.invalid/old"
    assert int(getattr(old_authority, "plugin_generation", 0) or 0) == int(pm.plugins["alpha"].generation)

    (plug / "init.mx").write_text(': fresh "new" ;\n', encoding="utf-8")
    pm.reload("alpha")
    assert ed._pending_open_url is None

    ed._pending_open_url = old_url
    ed._pending_open_url_source = old_source
    ed._pending_open_url_authority = old_authority
    ed.messages.clear()
    assert ed.open_url_confirm_yes() is False

    assert opened == []
    assert ed._pending_open_url is None
    assert any("stale plugin openurl: plugin alpha" in msg for msg in ed.messages)
