from __future__ import annotations

from pathlib import Path

import pytest

from micromax_editor.buffer import Cursor
from micromax_editor.buffer_names import BufferNameCollisionError, unique_buffer_name
from micromax_editor.editor import Editor, MacroStep
from micromax_editor.micromax_bridge import install_editor_hostcalls


def test_unique_buffer_name_is_deterministic_and_fills_first_hole() -> None:
    assert unique_buffer_name("notes", set()) == "notes"
    assert unique_buffer_name("notes", {"notes"}) == "notes<2>"
    assert unique_buffer_name("notes", {"notes", "notes<2>", "notes<4>"}) == "notes<3>"
    assert unique_buffer_name("*scratch*", {"*scratch*"}) == "*scratch-2*"
    assert (
        unique_buffer_name(
            "*scratch*",
            {"*scratch*", "*scratch-2*", "*scratch-4*"},
        )
        == "*scratch-3*"
    )
    with pytest.raises(ValueError, match="must not be empty"):
        unique_buffer_name("", set())


def test_strict_new_buffer_collision_is_side_effect_free() -> None:
    ed = Editor()
    ed.new_buffer("notes", "alpha")
    original = ed.cur()
    original.cursors[0] = Cursor(0, 2)
    assert ed.mark_set("anchor") is True
    original.buf.insert(Cursor(0, 5), "!")

    before_active = ed.active
    before_mru = list(ed._buffer_mru)
    before_authority = dict(ed._buffer_authority)
    before_marks = dict(ed.marks)
    before_mark_authority = dict(ed._mark_authority)
    before_next_cursor_id = ed._next_cursor_id

    with pytest.raises(BufferNameCollisionError, match="buffer already exists: notes"):
        ed.new_buffer("notes", "replacement")

    assert ed.buffers == {"notes": original}
    assert ed.cur() is original
    assert original.buf.get_text() == "alpha!"
    assert original.buf.dirty is True
    assert ed.active == before_active
    assert ed._buffer_mru == before_mru
    assert ed._buffer_authority == before_authority
    assert ed.marks == before_marks
    assert ed._mark_authority == before_mark_authority
    assert ed._next_cursor_id == before_next_cursor_id


def test_unique_creation_preserves_existing_buffer_and_mark_target() -> None:
    ed = Editor()
    ed.new_buffer("notes", "private draft")
    original = ed.cur()
    assert ed.mark_set("draft") is True

    actual = ed.new_buffer_unique("notes", "fresh")

    assert actual == "notes<2>"
    assert ed.active == "notes<2>"
    assert ed.buffers["notes"] is original
    assert ed.buffers["notes"].buf.get_text() == "private draft"
    assert ed.buffers["notes<2>"].buf.get_text() == "fresh"
    assert ed.marks["draft"][0] == "notes"


def test_open_file_disambiguates_pathless_same_name_buffer(tmp_path: Path) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("from disk\n", encoding="utf-8")

    ed = Editor()
    ed.new_buffer(str(path), "unsaved draft")
    original = ed.cur()
    original.buf.insert(Cursor(0, len("unsaved draft")), "!")
    assert ed.mark_set("draft") is True

    assert ed.open_file(str(path)) is True

    opened_name = f"{path}<2>"
    assert sorted(ed.buffers) == sorted([str(path), opened_name])
    assert ed.buffers[str(path)] is original
    assert original.buf.path is None
    assert original.buf.get_text() == "unsaved draft!"
    assert original.buf.dirty is True
    assert ed.marks["draft"][0] == str(path)
    assert ed.active == opened_name
    assert ed.cur().buf.path == str(path)
    assert ed.cur().buf.get_text() == "from disk\n"

    # The normalized path, not the display label, owns file identity. Reopening
    # switches to the path-backed buffer instead of allocating another name.
    assert ed.switch_buffer(str(path)) is True
    assert ed.open_file(str(path)) is True
    assert ed.active == opened_name
    assert len(ed.buffers) == 2


def test_help_open_disambiguates_pathless_same_name_buffer(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "01-guide.md").write_text("# Guide\n\nSafe help.\n", encoding="utf-8")
    monkeypatch.setenv("MICROMAX_DOCS", str(docs))

    ed = Editor()
    ed.new_buffer("help:guide", "personal notes")
    original = ed.cur()

    assert ed.open_help_doc("guide") is True
    assert ed.active == "help:guide<2>"
    assert ed.buffers["help:guide"] is original
    assert original.buf.path is None
    assert original.buf.get_text() == "personal notes"
    assert ed.cur().local_options["readonly"] is True
    assert ed.cur().local_options["help_doc"] == "guide"

    assert ed.switch_buffer("help:guide") is True
    assert ed.open_help_doc("guide") is True
    assert ed.active == "help:guide<2>"
    assert len(ed.buffers) == 2


def test_new_command_uses_collision_free_names_and_accepts_one_quoted_name() -> None:
    ed = Editor()

    assert ed.exec_command_line("new") is True
    assert ed.active == "*scratch*"
    assert ed.messages[-1] == "new: *scratch* @ 1:0"

    assert ed.exec_command_line("new") is True
    assert ed.active == "*scratch-2*"
    assert ed.exec_command_line('new "project notes"') is True
    assert ed.active == "project notes"
    assert ed.exec_command_line('new "project notes"') is True
    assert ed.active == "project notes<2>"
    assert list(ed.buffers) == [
        "*scratch*",
        "*scratch-2*",
        "project notes",
        "project notes<2>",
    ]

    before = list(ed.buffers)
    assert ed.exec_command_line("new too many") is False
    assert ed.messages[-1] == "usage: new [NAME]"
    assert list(ed.buffers) == before


def test_new_command_and_action_are_interactive_only() -> None:
    ed = Editor()
    assert ed.exec_command_line("new seed") is True
    before = list(ed.buffers)

    with ed.script_context(origin_id="plugin:untrusted"):
        assert ed.exec_command_line("new scripted") is False
        assert ed.run_action("NewBuffer") is False

    assert list(ed.buffers) == before
    assert any("interactive buffer creation only" in message for message in ed.messages)

    assert ed.run_action("NewBuffer") is True
    assert ed.active == "*scratch*"
    assert list(ed.buffers) == ["seed", "*scratch*"]


def test_script_origin_binding_cannot_launder_new_buffer_authority() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("seed", "")

    with ed.script_context(origin_id="plugin:demo"):
        ed.vm.stack.extend(["F12", "NewBuffer", "ed.bind"])
        ed.vm.eval("hostcall")

    binding = ed.resolve_key_binding("F12")
    assert binding is not None
    assert binding.script_context is True
    assert binding.script_origin_id == "plugin:demo"

    assert ed.dispatch_key("F12") is False
    assert list(ed.buffers) == ["seed"]
    assert ed.messages[-1] == "new: disabled for scripts (interactive buffer creation only)"


def test_failed_macro_creation_rollback_preserves_public_registry_identity() -> None:
    ed = Editor()
    ed.new_buffer("seed", "safe")
    original = ed.cur()
    assert ed.mark_set("home") is True
    buffers_registry = ed.buffers
    marks_registry = ed.marks

    ed.set_macro(
        "create-then-fail",
        [
            MacroStep(
                kind="command",
                name="command",
                payload={"cmdline": "new transient"},
            ),
            MacroStep(
                kind="command",
                name="command",
                payload={"cmdline": "definitely_missing"},
            ),
        ],
    )

    assert ed.play_macro("create-then-fail") is False
    assert ed.buffers is buffers_registry
    assert ed.marks is marks_registry
    assert ed.buffers == {"seed": original}
    assert ed.active == "seed"
    assert ed.marks["home"][0] == "seed"
    assert "transient" not in ed.buffers


def test_trusted_user_binding_can_invoke_new_buffer_action(tmp_path: Path) -> None:
    init_path = tmp_path / "init.mx"
    init_path.write_text(
        '"Ctrl-Alt-n" "NewBuffer" "ed.bind" hostcall\n',
        encoding="utf-8",
    )

    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("seed", "")
    assert ed.load_user_init(path=str(init_path)) is True

    binding = ed.resolve_key_binding("Ctrl-Alt-n")
    assert binding is not None
    assert binding.script_context is False
    assert ed.dispatch_key("Ctrl-Alt-n") is True
    assert ed.active == "*scratch*"


def test_buffer_transaction_undo_redo_preserves_public_registry_identity() -> None:
    ed = Editor()
    ed.new_buffer("seed", "safe")
    original = ed.cur()
    assert ed.mark_set("home") is True
    buffers_registry = ed.buffers
    marks_registry = ed.marks

    before = ed._buffer_transaction_snapshot()
    ed.new_buffer("created", "new")
    assert ed.mark_set("created-mark") is True
    created = ed.cur()
    after = ed._buffer_transaction_snapshot()
    ed._record_buffer_transaction_snapshot(before, after, "create buffer")

    assert ed.undo.undo() is True
    assert ed.buffers is buffers_registry
    assert ed.marks is marks_registry
    assert ed.buffers == {"seed": original}
    assert sorted(ed.marks) == ["home"]

    assert ed.undo.redo() is True
    assert ed.buffers is buffers_registry
    assert ed.marks is marks_registry
    assert ed.buffers == {"seed": original, "created": created}
    assert sorted(ed.marks) == ["created-mark", "home"]
