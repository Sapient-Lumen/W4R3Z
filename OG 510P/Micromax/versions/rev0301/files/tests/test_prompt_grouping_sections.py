from __future__ import annotations

import json

from micromax_editor.buffer import Cursor
from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.plugins import PluginManager


def _set_primary_cursor(ed: Editor, *, line: int, col: int) -> None:
    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    eb.cursors[eb.primary] = eb.buf.clamp(Cursor(int(line), int(col)))


def test_buffer_prompt_rows_group_help_and_scratch_first(tmp_path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer("*scratch*", "x\n")
    assert ed.open_help_doc("help-browser") is True

    p = tmp_path / "a.txt"
    p.write_text("hi\n", encoding="utf-8")
    ed.open_file(str(p))

    rows = ed.buffer_prompt_rows()
    labels = [ed._buffer_section_label(r) for r in rows]

    assert "Help" in labels
    first_help = labels.index("Help")
    non_help_positions = [i for i, l in enumerate(labels) if l not in ("Help", "Scratch")]
    assert non_help_positions
    assert first_help < min(non_help_positions)


def test_plugin_prompt_rows_group_errors_first(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    a = root / "a"
    a.mkdir()
    (a / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (a / "plugin.json").write_text(json.dumps({"entry": "main.mx"}), encoding="utf-8")

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


def test_binding_prompt_rows_empty_query_budget_across_sections() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    for i in range(3):
        ed.vm.eval(f'"nav" "Ctrl-{i}" "command:help" "ed.bind-mode" hostcall', filename="<nav-bind>")
    ed.vm.eval('"Ctrl-z" "command:quit" "ed.bind" hostcall', filename="<global-bind>")
    ed.push_key_mode("nav")

    rows = ed._binding_prompt_rows("", limit=2)
    labels = [ed.prompt_row_section_label(row, prompt_kind="binding") for row in rows]
    assert labels == ["nav", "Global"]


def test_buffer_prompt_rows_empty_query_budget_across_sections(tmp_path) -> None:
    ed = Editor()
    ed.new_buffer("*scratch*", "x\n")
    assert ed.open_help_doc("help-browser") is True
    assert ed.open_help_doc("vision") is True

    p = tmp_path / "notes.txt"
    p.write_text("hi\n", encoding="utf-8")
    ed.open_file(str(p))

    rows = ed._buffer_prompt_rows("", limit=3)
    labels = [ed.prompt_row_section_label(row, prompt_kind="buffer") for row in rows]
    assert labels == ["Help", "Scratch", str(tmp_path)]


def test_plugin_prompt_rows_empty_query_budget_across_sections(tmp_path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()

    for name in ("a", "b"):
        d = root / name
        d.mkdir()
        (d / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
        (d / "plugin.json").write_text(json.dumps({"entry": "main.mx", "requires": ["missingdep"]}), encoding="utf-8")

    good = root / "good"
    good.mkdir()
    (good / "main.mx").write_text(": init ( -- ) ;\n", encoding="utf-8")
    (good / "plugin.json").write_text(json.dumps({"entry": "main.mx"}), encoding="utf-8")

    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(root)

    rows = ed._plugin_prompt_rows("", limit=2)
    labels = [ed.prompt_row_section_label(row, prompt_kind="plugin") for row in rows]
    assert labels == ["Errors", "Loaded"]


def test_recent_prompt_rows_empty_query_budget_across_projects(tmp_path) -> None:
    ed = Editor()

    proj_a = tmp_path / "proj-a"
    (proj_a / ".git").mkdir(parents=True)
    a1 = proj_a / "src" / "one.py"
    a2 = proj_a / "src" / "two.py"
    a3 = proj_a / "src" / "three.py"
    for p in (a1, a2, a3):
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("print(1)\n", encoding="utf-8")

    proj_b = tmp_path / "proj-b"
    (proj_b / ".git").mkdir(parents=True)
    b1 = proj_b / "main.py"
    b1.write_text("print(2)\n", encoding="utf-8")

    ed.open_file(str(b1))
    ed.open_file(str(a1))
    ed.open_file(str(a2))
    ed.open_file(str(a3))

    rows = ed._recent_prompt_rows("", limit=2)
    labels = [ed.prompt_row_section_label(row, prompt_kind="recent") for row in rows]
    assert labels == [str(proj_a), str(proj_b)]


def test_doc_prompt_rows_empty_query_budget_across_numbered_families() -> None:
    ed = Editor()
    rows = ed._doc_prompt_rows("", limit=12)
    labels = [ed.prompt_row_section_label(row, prompt_kind="doc") for row in rows]
    seen: list[str] = []
    for label in labels:
        if label not in seen:
            seen.append(label)
    assert seen[:3] == ["00–09 Project", "10–19 Research", "20–29 Language + VM"]


def test_mark_and_jump_prompt_rows_empty_query_budget_across_sections() -> None:
    ed = Editor()
    ed.new_buffer("a", "one\n")
    ed.new_buffer("b", "two\nthree\nfour\n")

    ed.switch_buffer("b")
    _set_primary_cursor(ed, line=0, col=0)
    assert ed.mark_set("beta")
    _set_primary_cursor(ed, line=1, col=0)
    assert ed.mark_set("gamma")
    ed.switch_buffer("a")
    _set_primary_cursor(ed, line=0, col=0)
    assert ed.mark_set("alpha")

    mark_rows = ed._mark_prompt_rows("", limit=2)
    mark_labels = [ed.prompt_row_section_label(row, prompt_kind="mark") for row in mark_rows]
    assert mark_labels == ["a", "b"]

    ed.new_buffer("j", "one\ntwo\nthree\nfour\n")
    _set_primary_cursor(ed, line=0, col=0)
    assert ed.push_jump() is True
    _set_primary_cursor(ed, line=1, col=0)
    assert ed.push_jump() is True
    _set_primary_cursor(ed, line=2, col=0)
    assert ed.push_jump() is True
    _set_primary_cursor(ed, line=3, col=0)
    assert ed.push_jump() is True
    assert ed.jump_to_index(1) is True

    jump_rows = ed._jump_prompt_rows("", limit=3)
    jump_labels = [ed.prompt_row_section_label(row, prompt_kind="jump") for row in jump_rows]
    assert jump_labels == ["Current", "Back", "Forward"]
