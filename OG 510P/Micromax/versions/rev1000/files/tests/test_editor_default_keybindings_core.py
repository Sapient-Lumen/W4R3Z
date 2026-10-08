from __future__ import annotations

import re
from pathlib import Path

from micromax_editor.default_keybindings import (
    CORE_MIRRORED_KEY_BINDINGS,
    DEFAULT_KEY_BINDINGS,
)
from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.plugins import PluginManager
from micromax_editor.startup import create_editor_runtime


ROOT = Path(__file__).resolve().parents[1]


def _editor_with_product_defaults() -> Editor:
    ed = Editor()
    ed.install_default_keybindings()
    install_editor_hostcalls(ed)
    return ed


def _load_core_plugins(ed: Editor) -> PluginManager:
    # Match the product startup order: trusted defaults first, plugins second.
    ed.install_default_keybindings()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(ROOT / "plugins")
    return pm


def _core_plugin_binding_rows() -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    text = (ROOT / "plugins" / "core" / "init.mx").read_text(encoding="utf-8")
    for line in text.splitlines():
        global_match = re.fullmatch(
            r'\s*"([^"]+)"\s+"([^"]+)"\s+"ed\.bind" hostcall\s*',
            line,
        )
        if global_match is not None:
            rows.append(("global", global_match.group(1), global_match.group(2)))
            continue
        mode_match = re.fullmatch(
            r'\s*"([^"]+)"\s+"([^"]+)"\s+"([^"]+)"\s+'
            r'"ed\.bind-mode" hostcall\s*',
            line,
        )
        if mode_match is not None:
            rows.append(
                (mode_match.group(1), mode_match.group(2), mode_match.group(3))
            )
    return rows


def test_bare_embed_keeps_minimal_bootstrap_until_product_defaults_requested() -> None:
    ed = Editor()

    assert ed.resolve_key_binding("Ctrl-s") is None
    qreplace_yes = ed.keymap.get_binding_exact("y", mode="qreplace")
    assert qreplace_yes is not None
    assert qreplace_yes.action_spec == "QueryReplaceYes"
    assert qreplace_yes.script_context is False

    ed.install_default_keybindings()

    save = ed.resolve_key_binding("Ctrl-s")
    assert save is not None
    assert save.action_spec == "command:save"
    assert save.script_context is False


def test_reinstalling_product_defaults_does_not_clobber_trusted_customization() -> None:
    ed = Editor()
    ed.install_default_keybindings()
    ed.bind_key_checked("Ctrl-s", "command:help")

    customized = ed.resolve_key_binding("Ctrl-s")
    assert customized is not None
    assert customized.action_spec == "command:help"

    ed.install_default_keybindings()

    assert ed.resolve_key_binding("Ctrl-s") is customized


def test_repo_default_plugins_load_cleanly() -> None:
    ed = Editor()
    pm = _load_core_plugins(ed)

    assert pm.load_errors == []
    assert "core" in pm.plugins
    assert "capdemo" in pm.plugins


def test_default_keymap_rows_are_unique_and_core_mirror_cannot_drift() -> None:
    identities = [(row.mode, row.key) for row in DEFAULT_KEY_BINDINGS]
    assert len(identities) == len(set(identities))

    expected = [
        (row.mode, row.key, row.action_spec) for row in CORE_MIRRORED_KEY_BINDINGS
    ]
    assert _core_plugin_binding_rows() == expected


def test_core_default_keybindings_are_trusted_host_policy() -> None:
    ed = Editor()
    _load_core_plugins(ed)
    ed.new_buffer("*scratch*", "")

    expected = {
        "Ctrl-b": "command:bufferpick",
        "Ctrl-o": "FilePicker",
        "Ctrl-r": "command-edit:replace ",
        "Ctrl-Space": "CommandPalette",
        "Alt-g": "BindingPrompt",
        "Ctrl-s": "command:save",
        "Ctrl-z": "Undo",
        "Ctrl-x": "Cut",
        "Ctrl-v": "Paste",
    }
    for key, action_spec in expected.items():
        binding = ed.resolve_key_binding(key)
        assert binding is not None
        assert binding.action_spec == action_spec
        assert binding.script_context is False
        assert binding.plugin_load_root is None
        assert binding.plugin_generation is None
        assert binding.script_origin_id is None
        assert binding.group is None

    prompt_left = ed.keymap.get_binding_exact("LeftArrow", mode="prompt")
    assert prompt_left is not None
    assert prompt_left.action_spec == "PromptLeft"
    assert prompt_left.script_context is False

    qreplace_yes = ed.keymap.get_binding_exact("y", mode="qreplace")
    assert qreplace_yes is not None
    assert qreplace_yes.script_context is False


def test_physical_default_open_save_and_undo_keep_user_authority(tmp_path: Path) -> None:
    ed = _editor_with_product_defaults()
    root = tmp_path / "project"
    root.mkdir()
    (root / ".git").mkdir()
    seed = root / "scratch.txt"
    seed.write_text("a", encoding="utf-8")
    ed.new_buffer(str(seed), "a", path=str(seed))

    assert ed.options.get("cap.fs-open") is False
    assert ed.options.get("cap.fs-save") is False
    assert ed.options.get("cap.undo-redo") is False

    assert ed.dispatch_key("x") is True
    assert ed.cur().buf.get_text() == "xa"
    assert ed.dispatch_key("Ctrl-z") is True
    assert ed.cur().buf.get_text() == "a"

    target = root / "opened.txt"
    target.write_text("old", encoding="utf-8")

    assert ed.dispatch_key("Ctrl-o") is True
    assert ed.prompt is not None
    assert ed.prompt.kind == "file"
    assert ed.prompt.picker_root == str(root.resolve())
    assert "opened.txt" in ed.prompt.picker_items
    assert ed.prompt.script_context is False

    ed.set_prompt_text("opened.txt")
    assert ed.submit_prompt() is True
    assert ed.cur().name == str(target.resolve())

    assert ed.dispatch_key("Z") is True
    assert ed.dispatch_key("Ctrl-s") is True
    assert target.read_text(encoding="utf-8") == "Zold"
    assert not any("disabled for scripts" in message for message in ed.messages)


def test_physical_clipboard_buffer_picker_and_palette_keep_user_authority() -> None:
    ed = _editor_with_product_defaults()
    ed.new_buffer("alpha", "hello")

    assert ed.options.get("cap.clipboard-read") is False
    assert ed.options.get("cap.clipboard-write") is False

    assert ed.dispatch_key("Ctrl-a") is True
    assert ed.dispatch_key("Ctrl-x") is True
    assert ed.cur().buf.get_text() == ""
    assert ed.dispatch_key("Ctrl-v") is True
    assert ed.cur().buf.get_text() == "hello"

    ed.new_buffer("beta", "world")
    assert ed.dispatch_key("Ctrl-b") is True
    assert ed.prompt is not None
    assert ed.prompt.kind == "buffer"
    assert ed.prompt.script_context is False
    ed.prompt.suggest_index = ed.prompt.suggestions.index("alpha")
    assert ed.submit_prompt() is True
    assert ed.active == "alpha"

    assert ed.dispatch_key("Ctrl-Space") is True
    assert ed.prompt is not None
    assert ed.prompt.kind == "palette"
    assert ed.prompt.script_context is False
    assert ed.prompt.suggestions


def test_arbitrary_plugin_binding_stays_capability_scoped(
    tmp_path: Path,
) -> None:
    target = tmp_path / "secret.txt"
    target.write_text("secret", encoding="utf-8")

    root = tmp_path / "plugins"
    plugin = root / "thirdparty"
    plugin.mkdir(parents=True)
    (plugin / "init.mx").write_text(
        "\n".join(
            [
                ": init",
                f'  "F12" "command:open {target}" "ed.bind" hostcall',
                ";",
            ]
        ),
        encoding="utf-8",
    )

    ed = _editor_with_product_defaults()
    ed.new_buffer("*scratch*", "")
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    assert [loaded.name for loaded in pm.load_tree(root)] == ["thirdparty"]

    binding = ed.resolve_key_binding("F12")
    assert binding is not None
    assert binding.script_context is True
    assert binding.plugin_load_root == str(plugin.resolve())

    assert ed.options.get("cap.fs-open") is False
    assert ed.dispatch_key("F12") is False
    assert str(target.resolve()) not in ed.buffers
    assert ed.messages[-1] == "open: disabled for scripts (cap.fs-open)"


def test_trusted_user_init_can_rebind_product_defaults(tmp_path: Path) -> None:
    init_path = tmp_path / "init.mx"
    init_path.write_text(
        '"Ctrl-s" "command:help" "ed.bind" hostcall\n',
        encoding="utf-8",
    )

    ed = _editor_with_product_defaults()
    assert ed.load_user_init(path=str(init_path)) is True

    binding = ed.resolve_key_binding("Ctrl-s")
    assert binding is not None
    assert binding.action_spec == "command:help"
    assert binding.script_context is False
    assert binding.span is not None
    assert binding.span.filename == str(init_path)


def test_runtime_reload_restores_trusted_defaults_before_plugin_reload() -> None:
    ed = Editor()
    _load_core_plugins(ed)

    assert ed.reload_runtime() is True

    binding = ed.resolve_key_binding("Ctrl-s")
    assert binding is not None
    assert binding.action_spec == "command:save"
    assert binding.script_context is False
    assert binding.plugin_load_root is None


def test_restricted_startup_keeps_product_keymap_without_loading_plugins(
    tmp_path: Path,
    monkeypatch,
) -> None:
    empty_plugins = tmp_path / "plugins"
    empty_plugins.mkdir()
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("MICROMAX_INIT", str(tmp_path / "missing-init.mx"))

    runtime = create_editor_runtime(
        plugins_root=empty_plugins,
        workspace_trust="restricted",
    )

    assert runtime.plugin_manager.plugins == {}
    binding = runtime.editor.resolve_key_binding("Ctrl-s")
    assert binding is not None
    assert binding.action_spec == "command:save"
    assert binding.script_context is False
