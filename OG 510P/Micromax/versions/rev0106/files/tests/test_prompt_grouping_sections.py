from __future__ import annotations

import json

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.plugins import PluginManager


def test_buffer_prompt_rows_group_help_and_scratch_first(tmp_path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    # scratch-like buffer
    ed.new_buffer("*scratch*", "x\n")

    # help buffer
    assert ed.open_help_doc("help-browser") is True

    # file-backed buffer
    p = tmp_path / "a.txt"
    p.write_text("hi\n", encoding="utf-8")
    ed.open_file(str(p))

    rows = ed.buffer_prompt_rows()
    labels = [ed._buffer_section_label(r) for r in rows]

    # At least one help row should appear before non-help rows.
    assert "Help" in labels
    first_help = labels.index("Help")
    # Non-help label should exist (directory or Buffers)
    non_help_positions = [i for i,l in enumerate(labels) if l not in ("Help", "Scratch")]
    assert non_help_positions
    assert first_help < min(non_help_positions)


def test_plugin_prompt_rows_group_errors_first(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    # Loaded plugin.
    a = root / "a"
    a.mkdir()
    (a / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (a / "plugin.json").write_text(json.dumps({"entry": "main.mx"}), encoding="utf-8")

    # Candidate plugin blocked by missing dep (will show ERROR).
    b = root / "b"
    b.mkdir()
    (b / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (b / "plugin.json").write_text(json.dumps({"entry": "main.mx", "requires": ["missingdep"]}), encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)

    rows = ed.plugin_prompt_rows()
    labels = [ed._plugin_section_label(r) for r in rows]

    assert "Errors" in labels
    assert labels[0] == "Errors"
