from __future__ import annotations

from micromax_editor.editor import Editor, MacroReplaySnapshot, MacroStep
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.undo import Edit


def _insert_step(text: str) -> MacroStep:
    return MacroStep(
        kind="action",
        name="InsertText",
        payload={"input": {"text": str(text)}},
    )


def _command_step(cmdline: str) -> MacroStep:
    return MacroStep(
        kind="command",
        name="command",
        payload={"cmdline": str(cmdline)},
    )


def test_repeated_macro_playback_is_one_undo_redo_transaction() -> None:
    ed = Editor()
    ed.new_buffer(text="")

    ed.input["text"] = "P"
    assert ed.run_action("InsertText") is True
    before_playback = ed._buffer_transaction_snapshot()
    before_depth = ed.undo.depth()

    ed.set_macro("stamp", [_insert_step("x")])
    assert ed.play_macro("stamp", count=3) is True

    assert ed.cur().buf.get_text() == "Pxxx"
    assert ed.undo.depth() == before_depth + 1
    aggregate = ed.undo.peek_undo()
    assert aggregate is not None
    assert aggregate.description == "macro stamp x3"

    assert ed.undo_feedback() is True
    assert ed.cur().buf.get_text() == "P"
    assert ed._buffer_transaction_changed(before_playback, ed._buffer_transaction_snapshot()) is False

    assert ed.undo_feedback() is True
    assert ed.cur().buf.get_text() == ""

    assert ed.redo_feedback() is True
    assert ed.cur().buf.get_text() == "P"
    assert ed.redo_feedback() is True
    assert ed.cur().buf.get_text() == "Pxxx"


def test_safe_repeated_macro_skips_per_step_history_and_full_undo_snapshots() -> None:
    ed = Editor()
    ed.new_buffer(text="")
    ed.set_macro("stamp", [_insert_step("x")])

    original_record = ed.undo.record
    observed: list[tuple[str, int, int, bool]] = []
    full_snapshot_calls = 0
    original_snapshot = ed._snapshot_buffer_state

    def snapshot(eb):
        nonlocal full_snapshot_calls
        full_snapshot_calls += 1
        return original_snapshot(eb)

    def record(edit: Edit) -> None:
        before_depth = ed.undo.depth()
        suppressed = ed.undo.is_suppressed()
        original_record(edit)
        observed.append((edit.description, before_depth, ed.undo.depth(), suppressed))

    ed.undo.record = record  # type: ignore[method-assign]
    ed._snapshot_buffer_state = snapshot  # type: ignore[method-assign]

    assert ed.play_macro("stamp", count=64) is True
    assert ed.cur().buf.get_text() == "x" * 64
    assert ed.undo.depth() == 1

    assert full_snapshot_calls == 0
    assert observed == [("macro stamp x64", 0, 1, False)]


def test_navigation_only_macro_preserves_existing_redo_history() -> None:
    ed = Editor()
    ed.new_buffer(text="abc")

    ed.input["text"] = "X"
    assert ed.run_action("InsertText") is True
    assert ed.undo_feedback() is True
    assert ed.undo.depth() == 0
    assert ed.undo.redo_depth() == 1

    ed.set_macro(
        "right",
        [MacroStep(kind="action", name="CursorRight", payload={"input": {}})],
    )
    assert ed.play_macro("right", count=2) is True

    assert ed.primary_cursor().col == 2
    assert ed.undo.depth() == 0
    assert ed.undo.redo_depth() == 1
    assert ed.redo_feedback() is True
    assert ed.cur().buf.get_text() == "Xabc"


def test_macro_containing_undo_uses_one_exact_aggregate_transaction() -> None:
    ed = Editor()
    ed.new_buffer(text="a")

    ed.input["text"] = "X"
    assert ed.run_action("InsertText") is True
    assert ed.cur().buf.get_text() == "Xa"

    ed.set_macro(
        "replace-prior",
        [
            MacroStep(kind="action", name="Undo", payload={"input": {}}),
            _insert_step("Y"),
        ],
    )
    assert ed.play_macro("replace-prior") is True

    assert ed.cur().buf.get_text() == "Ya"
    assert ed.undo.depth() == 2
    aggregate = ed.undo.peek_undo()
    assert aggregate is not None
    assert aggregate.description == "macro replace-prior x1"

    assert ed.undo_feedback() is True
    assert ed.cur().buf.get_text() == "Xa"
    assert ed.undo_feedback() is True
    assert ed.cur().buf.get_text() == "a"

    assert ed.redo_feedback() is True
    assert ed.cur().buf.get_text() == "Xa"
    assert ed.redo_feedback() is True
    assert ed.cur().buf.get_text() == "Ya"


def test_repeated_command_macro_collapses_intermediate_history() -> None:
    ed = Editor()
    ed.new_buffer(text="a")
    ed.set_macro("grow", [_command_step("replaceall a aa")])

    assert ed.play_macro("grow", count=2) is True
    assert ed.cur().buf.get_text() == "aaaa"
    assert ed.undo.depth() == 1

    assert ed.undo_feedback() is True
    assert ed.cur().buf.get_text() == "a"
    assert ed.redo_feedback() is True
    assert ed.cur().buf.get_text() == "aaaa"


def test_compound_macro_callbacks_do_not_retain_discarded_undo_history() -> None:
    ed = Editor()
    ed.new_buffer(text="a")
    ed.set_macro("grow", [_command_step("replaceall a aa")])

    assert ed.play_macro("grow", count=3) is True
    aggregate = ed.undo.peek_undo()
    assert aggregate is not None

    for callback in (aggregate.undo, aggregate.redo):
        closure = callback.__closure__ or ()
        snapshots = [
            cell.cell_contents
            for cell in closure
            if isinstance(cell.cell_contents, MacroReplaySnapshot)
        ]
        assert len(snapshots) == 1
        assert snapshots[0].input == {}
        assert snapshots[0].undo.undo == ()
        assert snapshots[0].undo.redo == ()


def test_macro_transaction_spans_multiple_open_buffers() -> None:
    ed = Editor()
    ed.new_buffer("a", "")
    ed.new_buffer("b", "")
    assert ed.exec_command_line("buffer a") is True

    ed.set_macro(
        "both",
        [
            _insert_step("A"),
            _command_step("buffer b"),
            _insert_step("B"),
        ],
    )
    assert ed.play_macro("both") is True

    assert ed.buffers["a"].buf.get_text() == "A"
    assert ed.buffers["b"].buf.get_text() == "B"
    assert ed.active == "b"
    assert ed.undo.depth() == 1

    assert ed.undo_feedback() is True
    assert ed.buffers["a"].buf.get_text() == ""
    assert ed.buffers["b"].buf.get_text() == ""
    assert ed.active == "a"

    assert ed.redo_feedback() is True
    assert ed.buffers["a"].buf.get_text() == "A"
    assert ed.buffers["b"].buf.get_text() == "B"
    assert ed.active == "b"


def test_script_started_macro_transaction_keeps_playback_caller_authority() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer(text="")

    with ed.script_context(origin_id="script-a"):
        ed.set_macro("own", [_insert_step("s")])
        assert ed.play_macro("own", count=2) is True
        aggregate = ed.undo.peek_undo()
        assert aggregate is not None
        authority = ed._undo_redo_entry_authority(aggregate)
        assert authority.script_context is True
        assert authority.script_origin_id == "script-a"
        assert ed.undo_feedback() is True

    assert ed.cur().buf.get_text() == ""
